from pathlib import Path

import pytest
from pydantic import ValidationError

from github_compliance_engine_api.ingestion import (
    FileTreeNode,
    LanguageMixEntry,
    MetadataExtractionError,
    MetadataExtractionRequest,
    RepoMetadata,
    extract_repo_metadata,
)


# @golden-thread FEAT-ING-002, FR-ING-002, CF-ANALYZE-INGEST-001, TC-ING-002, V-ING-002
def test_metadata_extraction_request_accepts_valid_defaults(tmp_path: Path) -> None:
    request = MetadataExtractionRequest(
        analysis_id="analysis-001",
        repo_url="https://github.com/octocat/Hello-World",
        local_clone_path=tmp_path,
    )

    assert request.timeout_seconds == 30
    assert request.max_tree_depth == 20
    assert request.max_file_count == 5000
    assert request.max_text_file_bytes == 1048576
    assert request.github_token is None


@pytest.mark.parametrize(
    "field",
    [
        "timeout_seconds",
        "max_tree_depth",
        "max_file_count",
        "max_text_file_bytes",
    ],
)
def test_metadata_extraction_request_rejects_invalid_limits(tmp_path: Path, field: str) -> None:
    payload = {
        "analysis_id": "analysis-001",
        "repo_url": "https://github.com/octocat/Hello-World",
        "local_clone_path": tmp_path,
        field: 0,
    }

    with pytest.raises(ValidationError):
        MetadataExtractionRequest(**payload)


def test_repo_metadata_defaults_empty_lists() -> None:
    metadata = RepoMetadata()

    assert metadata.readme is None
    assert metadata.file_tree is None
    assert metadata.language_mix == []
    assert metadata.manifests == []
    assert metadata.extraction_errors == []


def test_file_tree_node_supports_nested_children() -> None:
    tree = FileTreeNode(
        path=".",
        name=".",
        type="dir",
        children=[
            FileTreeNode(
                path="src/app.py",
                name="app.py",
                type="file",
                size_bytes=128,
            )
        ],
    )

    assert tree.path == "."
    assert tree.children[0].path == "src/app.py"
    assert tree.children[0].type == "file"


@pytest.mark.parametrize("coverage_pct", [-0.01, 100.01])
def test_language_mix_entry_validates_coverage_bounds(coverage_pct: float) -> None:
    with pytest.raises(ValidationError):
        LanguageMixEntry(
            language="Python",
            normalized_language="python",
            coverage_pct=coverage_pct,
            ruleset_applicable=True,
            detection_source="github_languages_api",
        )


def test_metadata_extraction_error_uses_safe_message() -> None:
    raw_detail = "RAW" + "_PATH"
    error = MetadataExtractionError("Repository metadata could not be extracted.")
    error.__cause__ = OSError(raw_detail)

    assert error.safe_message == "Repository metadata could not be extracted."
    assert raw_detail not in error.safe_message


def test_extract_repo_metadata_returns_empty_metadata_for_clone_directory(tmp_path: Path) -> None:
    clone_path = tmp_path / "repo"
    clone_path.mkdir()
    request = MetadataExtractionRequest(
        analysis_id="analysis-001",
        repo_url="https://github.com/octocat/Hello-World",
        local_clone_path=clone_path,
    )

    metadata = extract_repo_metadata(request)

    assert metadata == RepoMetadata()


@pytest.mark.parametrize("path_name", ["missing-repo", "repo-file"])
def test_extract_repo_metadata_raises_safe_error_for_invalid_clone_path(tmp_path: Path, path_name: str) -> None:
    clone_path = tmp_path / path_name
    if path_name == "repo-file":
        clone_path.write_text("not a directory", encoding="utf-8")
    request = MetadataExtractionRequest(
        analysis_id="analysis-001",
        repo_url="https://github.com/octocat/Hello-World",
        local_clone_path=clone_path,
    )

    with pytest.raises(MetadataExtractionError) as exc_info:
        extract_repo_metadata(request)

    assert exc_info.value.safe_message == "Repository metadata could not be extracted from the clone workspace."
    assert str(clone_path) not in exc_info.value.safe_message
