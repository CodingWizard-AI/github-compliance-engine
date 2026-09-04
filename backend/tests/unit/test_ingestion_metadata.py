from pathlib import Path

import pytest

from github_compliance_engine_api.ingestion import MetadataExtractionRequest, extract_repo_metadata


def metadata_request(
    clone_path: Path,
    *,
    max_tree_depth: int = 20,
    max_file_count: int = 5000,
    max_text_file_bytes: int = 1048576,
) -> MetadataExtractionRequest:
    return MetadataExtractionRequest(
        analysis_id="analysis-001",
        repo_url="https://github.com/octocat/Hello-World",
        local_clone_path=clone_path,
        max_tree_depth=max_tree_depth,
        max_file_count=max_file_count,
        max_text_file_bytes=max_text_file_bytes,
    )


def tree_paths(node) -> set[str]:
    paths = {node.path}
    for child in node.children:
        paths.update(tree_paths(child))
    return paths


def find_node(node, path: str):
    if node.path == path:
        return node
    for child in node.children:
        found = find_node(child, path)
        if found is not None:
            return found
    return None


# @golden-thread FEAT-ING-002, FR-ING-002, CF-ANALYZE-INGEST-001, TC-ING-002, V-ING-002
def test_extract_repo_metadata_reads_root_readme(tmp_path: Path) -> None:
    clone_path = tmp_path / "repo"
    clone_path.mkdir()
    readme = clone_path / "README.md"
    readme.write_text("# Project\n", encoding="utf-8")

    metadata = extract_repo_metadata(metadata_request(clone_path))

    assert metadata.readme is not None
    assert metadata.readme.raw_text == "# Project\n"
    assert metadata.readme.source_path == "README.md"
    assert metadata.readme.format == "md"
    assert metadata.readme.size_bytes == len("# Project\n")
    assert metadata.readme.truncated is False


def test_extract_repo_metadata_prefers_supported_readme_order(tmp_path: Path) -> None:
    clone_path = tmp_path / "repo"
    clone_path.mkdir()
    (clone_path / "README.txt").write_text("text", encoding="utf-8")
    (clone_path / "readme.rst").write_text("rst", encoding="utf-8")
    (clone_path / "ReadMe.md").write_text("markdown", encoding="utf-8")

    metadata = extract_repo_metadata(metadata_request(clone_path))

    assert metadata.readme is not None
    assert metadata.readme.source_path == "ReadMe.md"
    assert metadata.readme.raw_text == "markdown"


def test_extract_repo_metadata_allows_missing_readme(tmp_path: Path) -> None:
    clone_path = tmp_path / "repo"
    clone_path.mkdir()

    metadata = extract_repo_metadata(metadata_request(clone_path))

    assert metadata.readme is None
    assert metadata.extraction_errors == []


def test_extract_repo_metadata_records_safe_error_for_large_readme(tmp_path: Path) -> None:
    clone_path = tmp_path / "repo"
    clone_path.mkdir()
    (clone_path / "README.md").write_text("too large", encoding="utf-8")

    metadata = extract_repo_metadata(metadata_request(clone_path, max_text_file_bytes=4))

    assert metadata.readme is None
    assert [error.code for error in metadata.extraction_errors] == ["README_TOO_LARGE"]
    assert "README.md" not in metadata.extraction_errors[0].message


def test_extract_repo_metadata_records_safe_error_for_binary_or_undecodable_readme(tmp_path: Path) -> None:
    clone_path = tmp_path / "repo"
    clone_path.mkdir()
    (clone_path / "README.md").write_bytes(b"\xff\xfe\x00")

    metadata = extract_repo_metadata(metadata_request(clone_path))

    assert metadata.readme is None
    assert metadata.extraction_errors[0].code in {"README_BINARY", "README_DECODE_FAILED"}
    assert str(clone_path) not in metadata.extraction_errors[0].message


def test_file_tree_includes_files_dirs_and_symlinks_without_following_symlinks(tmp_path: Path) -> None:
    clone_path = tmp_path / "repo"
    src_path = clone_path / "src"
    src_path.mkdir(parents=True)
    (src_path / "app.py").write_text("print('hello')", encoding="utf-8")
    target_path = tmp_path / "outside"
    target_path.mkdir()
    (target_path / "secret.txt").write_text("secret", encoding="utf-8")
    (clone_path / "outside-link").symlink_to(target_path)

    metadata = extract_repo_metadata(metadata_request(clone_path))

    assert metadata.file_tree is not None
    assert tree_paths(metadata.file_tree) == {".", "outside-link", "src", "src/app.py"}
    assert find_node(metadata.file_tree, "outside-link").type == "symlink"
    assert find_node(metadata.file_tree, "outside-link").children == []


def test_file_tree_respects_fallback_ignore_rules(tmp_path: Path) -> None:
    clone_path = tmp_path / "repo"
    clone_path.mkdir()
    (clone_path / "app.py").write_text("", encoding="utf-8")
    ignored_path = clone_path / "node_modules"
    ignored_path.mkdir()
    (ignored_path / "package.js").write_text("", encoding="utf-8")

    metadata = extract_repo_metadata(metadata_request(clone_path))

    assert metadata.file_tree is not None
    assert tree_paths(metadata.file_tree) == {".", "app.py"}


def test_file_tree_respects_root_gitignore(tmp_path: Path) -> None:
    clone_path = tmp_path / "repo"
    clone_path.mkdir()
    (clone_path / ".gitignore").write_text("ignored.log\nnested/\n", encoding="utf-8")
    (clone_path / "kept.py").write_text("", encoding="utf-8")
    (clone_path / "ignored.log").write_text("", encoding="utf-8")
    nested_path = clone_path / "nested"
    nested_path.mkdir()
    (nested_path / "ignored.py").write_text("", encoding="utf-8")

    metadata = extract_repo_metadata(metadata_request(clone_path))

    assert metadata.file_tree is not None
    assert tree_paths(metadata.file_tree) == {".", ".gitignore", "kept.py"}


def test_file_tree_uses_fallback_when_gitignore_is_unreadable(tmp_path: Path, monkeypatch) -> None:
    clone_path = tmp_path / "repo"
    clone_path.mkdir()
    gitignore_path = clone_path / ".gitignore"
    gitignore_path.write_text("ignored.log\n", encoding="utf-8")
    (clone_path / "kept.py").write_text("", encoding="utf-8")
    original_read_text = Path.read_text

    def read_text(path: Path, *args, **kwargs) -> str:
        if path == gitignore_path:
            raise OSError("raw local path detail")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read_text)

    metadata = extract_repo_metadata(metadata_request(clone_path))

    assert metadata.file_tree is not None
    assert "kept.py" in tree_paths(metadata.file_tree)
    assert [error.code for error in metadata.extraction_errors] == ["GITIGNORE_READ_FAILED"]
    assert str(gitignore_path) not in metadata.extraction_errors[0].message


def test_file_tree_sets_truncated_when_file_limit_hit(tmp_path: Path) -> None:
    clone_path = tmp_path / "repo"
    clone_path.mkdir()
    (clone_path / "a.py").write_text("", encoding="utf-8")
    (clone_path / "b.py").write_text("", encoding="utf-8")

    metadata = extract_repo_metadata(metadata_request(clone_path, max_file_count=1))

    assert metadata.file_tree is not None
    assert metadata.file_tree.truncated is True
    assert len([path for path in tree_paths(metadata.file_tree) if path.endswith(".py")]) == 1


def test_file_tree_sets_truncated_when_depth_limit_hit(tmp_path: Path) -> None:
    clone_path = tmp_path / "repo"
    nested_path = clone_path / "src" / "package"
    nested_path.mkdir(parents=True)
    (nested_path / "module.py").write_text("", encoding="utf-8")

    metadata = extract_repo_metadata(metadata_request(clone_path, max_tree_depth=1))

    assert metadata.file_tree is not None
    assert metadata.file_tree.truncated is True
    assert tree_paths(metadata.file_tree) == {".", "src"}
    assert find_node(metadata.file_tree, "src").truncated is True


def test_extract_repo_metadata_returns_partial_results_on_nonfatal_filesystem_errors(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clone_path = tmp_path / "repo"
    unreadable_path = clone_path / "unreadable"
    clone_path.mkdir()
    unreadable_path.mkdir()
    (clone_path / "kept.py").write_text("", encoding="utf-8")
    original_iterdir = Path.iterdir

    def iterdir(path: Path):
        if path == unreadable_path:
            raise OSError("raw local path detail")
        return original_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", iterdir)

    metadata = extract_repo_metadata(metadata_request(clone_path))

    assert metadata.file_tree is not None
    assert "kept.py" in tree_paths(metadata.file_tree)
    assert "unreadable" in tree_paths(metadata.file_tree)
    assert "TREE_READ_FAILED" in [error.code for error in metadata.extraction_errors]


def test_extract_repo_metadata_does_not_leak_absolute_paths_or_raw_exception_details(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clone_path = tmp_path / "repo"
    clone_path.mkdir()
    (clone_path / "README.md").write_text("content", encoding="utf-8")
    raw_detail = "RAW" + "_EXCEPTION_DETAIL"
    original_read_bytes = Path.read_bytes

    def read_bytes(path: Path) -> bytes:
        if path.name == "README.md":
            raise OSError(raw_detail)
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", read_bytes)

    metadata = extract_repo_metadata(metadata_request(clone_path))
    error_text = " ".join(error.message for error in metadata.extraction_errors)

    assert metadata.file_tree is not None
    assert raw_detail not in error_text
    assert str(clone_path) not in error_text
