from dataclasses import dataclass, field
from pathlib import Path

from pathspec import PathSpec

from github_compliance_engine_api.ingestion.contracts import (
    AnalysisError,
    FileTreeNode,
    MetadataExtractionError,
    MetadataExtractionRequest,
    ReadmeObject,
    RepoMetadata,
)


CLONE_PATH_UNAVAILABLE_MESSAGE = "Repository metadata could not be extracted from the clone workspace."
README_FILENAMES = ("readme.md", "readme.rst", "readme.txt")
FALLBACK_IGNORE_PATTERNS = (
    ".git/",
    "node_modules/",
    "__pycache__/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    ".venv/",
    "venv/",
    "dist/",
    "build/",
    ".next/",
    "coverage/",
    ".DS_Store",
)
TYPE_SORT_ORDER = {"dir": 0, "file": 1, "symlink": 2, "other": 3}


@dataclass
class _ExtractionState:
    file_count: int = 0
    truncated: bool = False
    errors: list[AnalysisError] = field(default_factory=list)


# @golden-thread FEAT-ING-002, FR-ING-002, CF-ANALYZE-INGEST-001, TC-ING-002, V-ING-002
def extract_repo_metadata(request: MetadataExtractionRequest) -> RepoMetadata:
    clone_path = _validated_clone_path(request.local_clone_path)
    state = _ExtractionState()
    ignore_spec = _ignore_spec(clone_path, state)
    readme = _extract_readme(clone_path, request, state)
    file_tree = _build_file_tree(clone_path, clone_path, request, ignore_spec, state, depth=0)
    file_tree.truncated = file_tree.truncated or state.truncated

    return RepoMetadata(
        readme=readme,
        file_tree=file_tree,
        extraction_errors=state.errors,
    )


def _validated_clone_path(local_clone_path: Path) -> Path:
    try:
        clone_path = local_clone_path.resolve()
        clone_path_exists = clone_path.exists()
        clone_path_is_dir = clone_path.is_dir()
    except OSError as exc:
        raise MetadataExtractionError(CLONE_PATH_UNAVAILABLE_MESSAGE) from exc

    if not clone_path_exists or not clone_path_is_dir:
        raise MetadataExtractionError(CLONE_PATH_UNAVAILABLE_MESSAGE)

    return clone_path


def _extract_readme(
    clone_path: Path,
    request: MetadataExtractionRequest,
    state: _ExtractionState,
) -> ReadmeObject | None:
    readme_path = _find_readme(clone_path)
    if readme_path is None:
        return None

    try:
        size_bytes = readme_path.stat().st_size
    except OSError:
        state.errors.append(_metadata_warning("README_STAT_FAILED", "README metadata could not be read."))
        return None

    if size_bytes > request.max_text_file_bytes:
        state.errors.append(_metadata_warning("README_TOO_LARGE", "README exceeds the configured metadata text size limit."))
        return None

    try:
        raw_bytes = readme_path.read_bytes()
    except OSError:
        state.errors.append(_metadata_warning("README_READ_FAILED", "README content could not be read."))
        return None

    if b"\x00" in raw_bytes:
        state.errors.append(_metadata_warning("README_BINARY", "README content is not supported text."))
        return None

    try:
        raw_text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        state.errors.append(_metadata_warning("README_DECODE_FAILED", "README content could not be decoded as UTF-8."))
        return None

    return ReadmeObject(
        raw_text=raw_text,
        source_path=_repo_relative_path(clone_path, readme_path),
        format=readme_path.suffix.lstrip(".").lower() or None,
        size_bytes=size_bytes,
        truncated=False,
    )


def _find_readme(clone_path: Path) -> Path | None:
    try:
        entries = sorted(clone_path.iterdir(), key=lambda path: path.name.lower())
    except OSError:
        return None

    by_lower_name = {
        entry.name.lower(): entry
        for entry in entries
        if not entry.is_symlink() and entry.is_file()
    }
    for filename in README_FILENAMES:
        if filename in by_lower_name:
            return by_lower_name[filename]
    return None


def _ignore_spec(clone_path: Path, state: _ExtractionState) -> PathSpec:
    patterns = list(FALLBACK_IGNORE_PATTERNS)
    gitignore_path = clone_path / ".gitignore"
    try:
        if gitignore_path.exists():
            patterns.extend(gitignore_path.read_text(encoding="utf-8").splitlines())
    except Exception:
        state.errors.append(_metadata_warning("GITIGNORE_READ_FAILED", "Repository ignore rules could not be read."))

    return PathSpec.from_lines("gitwildmatch", patterns)


def _build_file_tree(
    root_path: Path,
    current_path: Path,
    request: MetadataExtractionRequest,
    ignore_spec: PathSpec,
    state: _ExtractionState,
    depth: int,
) -> FileTreeNode:
    node = FileTreeNode(
        path=_repo_relative_path(root_path, current_path),
        name=current_path.name if current_path != root_path else ".",
        type=_node_type(current_path),
        size_bytes=_safe_size(current_path, state),
    )

    if node.type != "dir":
        return node

    if depth >= request.max_tree_depth:
        if _has_children(current_path):
            node.truncated = True
            state.truncated = True
        return node

    for child_path in _safe_iterdir(current_path, state):
        relative_path = _repo_relative_path(root_path, child_path)
        child_type = _node_type(child_path)
        if _is_ignored(ignore_spec, relative_path, child_type):
            continue
        if state.file_count >= request.max_file_count:
            node.truncated = True
            state.truncated = True
            break

        if child_type != "dir":
            state.file_count += 1

        child_node = _build_file_tree(root_path, child_path, request, ignore_spec, state, depth + 1)
        node.children.append(child_node)

    node.children.sort(key=lambda child: (TYPE_SORT_ORDER[child.type], child.path))
    return node


def _is_ignored(ignore_spec: PathSpec, relative_path: str, node_type: str) -> bool:
    return ignore_spec.match_file(relative_path) or (node_type == "dir" and ignore_spec.match_file(f"{relative_path}/"))


def _node_type(path: Path) -> str:
    try:
        if path.is_symlink():
            return "symlink"
        if path.is_dir():
            return "dir"
        if path.is_file():
            return "file"
    except OSError:
        return "other"
    return "other"


def _safe_size(path: Path, state: _ExtractionState) -> int | None:
    if _node_type(path) == "dir":
        return None
    try:
        return path.lstat().st_size
    except OSError:
        state.errors.append(_metadata_warning("FILE_STAT_FAILED", "A repository path could not be inspected."))
        return None


def _safe_iterdir(path: Path, state: _ExtractionState) -> list[Path]:
    try:
        return sorted(path.iterdir(), key=lambda child: (TYPE_SORT_ORDER[_node_type(child)], child.name.lower()))
    except OSError:
        state.errors.append(_metadata_warning("TREE_READ_FAILED", "A repository directory could not be read."))
        return []


def _has_children(path: Path) -> bool:
    try:
        next(path.iterdir())
        return True
    except (OSError, StopIteration):
        return False


def _repo_relative_path(root_path: Path, path: Path) -> str:
    if path == root_path:
        return "."
    return path.relative_to(root_path).as_posix()


def _metadata_warning(code: str, message: str) -> AnalysisError:
    return AnalysisError(
        code=code,
        message=message,
        severity="warning",
        stage="metadata",
        safe=True,
        retryable=False,
    )
