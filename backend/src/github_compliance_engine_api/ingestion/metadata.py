import json
import tomllib
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
from pathspec import PathSpec

from github_compliance_engine_api.ingestion.contracts import (
    AnalysisError,
    FileTreeNode,
    LanguageMixEntry,
    ManifestDescriptor,
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
LANGUAGE_EXTENSIONS = {
    ".cjs": "JavaScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".mjs": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".py": "Python",
    ".java": "Java",
}
UNSUPPORTED_LANGUAGE_EXTENSIONS = {
    ".css": "CSS",
    ".go": "Go",
    ".html": "HTML",
    ".json": "JSON",
    ".md": "Markdown",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".sh": "Shell",
    ".xml": "XML",
    ".yaml": "YAML",
    ".yml": "YAML",
}
MANIFEST_FILENAMES = {
    "package.json": "package_json",
    "requirements.txt": "requirements_txt",
    "pyproject.toml": "pyproject_toml",
    "pom.xml": "pom_xml",
    "build.gradle": "build_gradle",
}
FRAMEWORK_RULESETS = {
    "express": ("javascript_typescript", "FEAT-RULE-003"),
    "fastapi": ("python", "FEAT-RULE-004"),
    "flask": ("python", "FEAT-RULE-004"),
    "spring": ("java", "FEAT-RULE-005"),
}
FRAMEWORK_PRIORITY = ("fastapi", "flask", "express", "spring")


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
    manifests = _extract_manifests(clone_path, file_tree, request, state)
    language_mix = _extract_language_mix(request, file_tree, manifests, state)

    return RepoMetadata(
        readme=readme,
        file_tree=file_tree,
        language_mix=language_mix,
        manifests=manifests,
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


def _extract_language_mix(
    request: MetadataExtractionRequest,
    file_tree: FileTreeNode,
    manifests: list[ManifestDescriptor],
    state: _ExtractionState,
) -> list[LanguageMixEntry]:
    entries = _github_language_mix(request, state)
    if not entries:
        entries = _fallback_language_mix(file_tree)
    return _apply_framework_hints(entries, manifests)


def _github_language_mix(
    request: MetadataExtractionRequest,
    state: _ExtractionState,
) -> list[LanguageMixEntry]:
    api_url = _github_languages_api_url(request.repo_url)
    if api_url is None:
        state.errors.append(_metadata_warning("GITHUB_LANGUAGES_SKIPPED", "GitHub language metadata could not be requested."))
        return []

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if request.github_token:
        headers["Authorization"] = f"Bearer {request.github_token}"

    try:
        response = httpx.get(api_url, headers=headers, timeout=request.timeout_seconds)
        if response.status_code != 200:
            state.errors.append(_metadata_warning("GITHUB_LANGUAGES_UNAVAILABLE", "GitHub language metadata is unavailable."))
            return []
        payload = response.json()
    except Exception:
        state.errors.append(_metadata_warning("GITHUB_LANGUAGES_UNAVAILABLE", "GitHub language metadata is unavailable."))
        return []

    if not isinstance(payload, dict):
        state.errors.append(_metadata_warning("GITHUB_LANGUAGES_INVALID", "GitHub language metadata could not be parsed."))
        return []

    language_bytes: dict[str, int] = {}
    for language, byte_count in payload.items():
        if isinstance(language, str) and isinstance(byte_count, int) and byte_count > 0:
            language_bytes[language] = byte_count

    if not language_bytes:
        state.errors.append(_metadata_warning("GITHUB_LANGUAGES_INVALID", "GitHub language metadata could not be parsed."))
        return []

    return _language_entries(language_bytes, "github_languages_api")


def _github_languages_api_url(repo_url: str) -> str | None:
    parsed = urlparse(repo_url)
    if parsed.scheme != "https" or parsed.hostname != "github.com":
        return None
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1].removesuffix(".git")
    return f"https://api.github.com/repos/{owner}/{repo}/languages"


def _fallback_language_mix(file_tree: FileTreeNode) -> list[LanguageMixEntry]:
    language_bytes: dict[str, int] = {}
    for node in _file_nodes(file_tree):
        language = _language_from_path(node.path)
        if language is None:
            continue
        byte_count = node.size_bytes if node.size_bytes and node.size_bytes > 0 else 1
        language_bytes[language] = language_bytes.get(language, 0) + byte_count
    return _language_entries(language_bytes, "file_extension_heuristic")


def _language_from_path(path: str) -> str | None:
    path_obj = Path(path)
    suffix = path_obj.suffix.lower()
    if suffix in LANGUAGE_EXTENSIONS:
        return LANGUAGE_EXTENSIONS[suffix]
    if suffix in UNSUPPORTED_LANGUAGE_EXTENSIONS:
        return UNSUPPORTED_LANGUAGE_EXTENSIONS[suffix]
    if path_obj.name.lower() == "dockerfile":
        return "Dockerfile"
    return None


def _language_entries(language_bytes: dict[str, int], detection_source: str) -> list[LanguageMixEntry]:
    total_bytes = sum(language_bytes.values())
    if total_bytes <= 0:
        return []

    return [
        LanguageMixEntry(
            language=language,
            normalized_language=_normalized_language(language),
            bytes=byte_count,
            coverage_pct=round((byte_count / total_bytes) * 100, 2),
            framework="unknown",
            ruleset_applicable=False,
            detection_source=detection_source,
        )
        for language, byte_count in sorted(language_bytes.items(), key=lambda item: (-item[1], item[0].lower()))
    ]


def _normalized_language(language: str) -> str:
    normalized = language.strip().lower()
    if normalized in {"javascript", "typescript"}:
        return "javascript_typescript"
    if normalized == "python":
        return "python"
    if normalized == "java":
        return "java"
    return "unsupported"


def _apply_framework_hints(
    entries: list[LanguageMixEntry],
    manifests: list[ManifestDescriptor],
) -> list[LanguageMixEntry]:
    hints: dict[str, dict[str, set[str]]] = {}
    for manifest in manifests:
        for framework in manifest.detected_frameworks:
            normalized_language, ruleset_id = FRAMEWORK_RULESETS[framework]
            hint = hints.setdefault(normalized_language, {"frameworks": set(), "manifests": set(), "rulesets": set()})
            hint["frameworks"].add(framework)
            hint["manifests"].add(manifest.path)
            hint["rulesets"].add(ruleset_id)

    by_language = {entry.normalized_language: entry for entry in entries}
    for normalized_language, hint in hints.items():
        entry = by_language.get(normalized_language)
        framework = _preferred_framework(hint["frameworks"])
        if entry is None:
            entry = LanguageMixEntry(
                language=_display_language(normalized_language),
                normalized_language=normalized_language,
                bytes=None,
                coverage_pct=0.0,
                framework=framework,
                manifest_files_detected=sorted(hint["manifests"]),
                ruleset_applicable=True,
                ruleset_ids=sorted(hint["rulesets"]),
                detection_source="manifest",
            )
            entries.append(entry)
            by_language[normalized_language] = entry
            continue

        entry.framework = framework
        entry.manifest_files_detected = sorted(set(entry.manifest_files_detected).union(hint["manifests"]))
        entry.ruleset_applicable = True
        entry.ruleset_ids = sorted(set(entry.ruleset_ids).union(hint["rulesets"]))

    return sorted(entries, key=lambda entry: (-(entry.bytes or 0), entry.language.lower()))


def _preferred_framework(frameworks: set[str]) -> str:
    for framework in FRAMEWORK_PRIORITY:
        if framework in frameworks:
            return framework
    return "unknown"


def _display_language(normalized_language: str) -> str:
    return {
        "javascript_typescript": "JavaScript/TypeScript",
        "python": "Python",
        "java": "Java",
    }.get(normalized_language, "Unsupported")


def _extract_manifests(
    clone_path: Path,
    file_tree: FileTreeNode,
    request: MetadataExtractionRequest,
    state: _ExtractionState,
) -> list[ManifestDescriptor]:
    manifests: list[ManifestDescriptor] = []
    for node in _file_nodes(file_tree):
        manifest_type = MANIFEST_FILENAMES.get(Path(node.path).name)
        if manifest_type is None:
            continue
        manifests.append(_parse_manifest(clone_path, node.path, manifest_type, request, state))
    return sorted(manifests, key=lambda manifest: manifest.path)


def _file_nodes(node: FileTreeNode) -> list[FileTreeNode]:
    if node.type == "file":
        return [node]
    nodes: list[FileTreeNode] = []
    for child in node.children:
        nodes.extend(_file_nodes(child))
    return nodes


def _parse_manifest(
    clone_path: Path,
    relative_path: str,
    manifest_type: str,
    request: MetadataExtractionRequest,
    state: _ExtractionState,
) -> ManifestDescriptor:
    manifest_path = clone_path / relative_path
    base_descriptor = ManifestDescriptor(
        path=relative_path,
        manifest_type=manifest_type,
        package_manager=_package_manager(manifest_type),
        parse_status="parsed",
    )

    try:
        size_bytes = manifest_path.stat().st_size
        if size_bytes > request.max_text_file_bytes:
            return base_descriptor.model_copy(update={"parse_status": "skipped"})
        content = manifest_path.read_text(encoding="utf-8")
    except Exception:
        error = _metadata_warning("MANIFEST_READ_FAILED", "A repository manifest could not be read.")
        state.errors.append(error)
        return base_descriptor.model_copy(update={"parse_status": "malformed", "parse_error": error})

    try:
        frameworks = _detect_manifest_frameworks(manifest_type, content)
    except Exception:
        error = _metadata_warning("MANIFEST_PARSE_FAILED", "A repository manifest could not be parsed.")
        state.errors.append(error)
        return base_descriptor.model_copy(update={"parse_status": "malformed", "parse_error": error})

    return base_descriptor.model_copy(update={"detected_frameworks": frameworks})


def _package_manager(manifest_type: str) -> str | None:
    return {
        "package_json": "npm",
        "requirements_txt": "pip",
        "pyproject_toml": "python",
        "pom_xml": "maven",
        "build_gradle": "gradle",
    }.get(manifest_type)


def _detect_manifest_frameworks(manifest_type: str, content: str) -> list[str]:
    if manifest_type == "package_json":
        return _detect_package_json_frameworks(content)
    if manifest_type == "requirements_txt":
        return _detect_python_requirement_frameworks(content.splitlines())
    if manifest_type == "pyproject_toml":
        return _detect_pyproject_frameworks(content)
    if manifest_type == "pom_xml":
        return _detect_pom_frameworks(content)
    if manifest_type == "build_gradle":
        return _detect_gradle_frameworks(content)
    return []


def _detect_package_json_frameworks(content: str) -> list[str]:
    payload = json.loads(content)
    if not isinstance(payload, dict):
        return []
    dependencies: set[str] = set()
    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        value = payload.get(key)
        if isinstance(value, dict):
            dependencies.update(package.lower() for package in value if isinstance(package, str))
    return ["express"] if "express" in dependencies else []


def _detect_python_requirement_frameworks(lines: list[str]) -> list[str]:
    packages = {_python_package_name(line) for line in lines}
    packages.discard("")
    return _python_frameworks(packages)


def _detect_pyproject_frameworks(content: str) -> list[str]:
    payload = tomllib.loads(content)
    packages: set[str] = set()
    packages.update(_dependencies_from_list(payload.get("project", {}).get("dependencies")))
    optional_dependencies = payload.get("project", {}).get("optional-dependencies")
    if isinstance(optional_dependencies, dict):
        for dependency_group in optional_dependencies.values():
            packages.update(_dependencies_from_list(dependency_group))

    poetry_dependencies = payload.get("tool", {}).get("poetry", {}).get("dependencies")
    if isinstance(poetry_dependencies, dict):
        packages.update(package.lower() for package in poetry_dependencies if isinstance(package, str))

    return _python_frameworks(packages)


def _dependencies_from_list(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {_python_package_name(dependency) for dependency in value if isinstance(dependency, str)}


def _python_package_name(dependency: str) -> str:
    stripped = dependency.split("#", 1)[0].strip().lower()
    if not stripped or stripped.startswith("-"):
        return ""
    for separator in ("[", "==", ">=", "<=", "~=", "!=", ">", "<", "="):
        stripped = stripped.split(separator, 1)[0]
    return stripped.strip().replace("_", "-")


def _python_frameworks(packages: set[str]) -> list[str]:
    frameworks: list[str] = []
    if "fastapi" in packages:
        frameworks.append("fastapi")
    if "flask" in packages:
        frameworks.append("flask")
    return frameworks


def _detect_pom_frameworks(content: str) -> list[str]:
    root = ET.fromstring(content)
    dependency_text = " ".join(element.text or "" for element in root.iter()).lower()
    if "spring-boot" in dependency_text or "springframework" in dependency_text:
        return ["spring"]
    return []


def _detect_gradle_frameworks(content: str) -> list[str]:
    normalized = content.lower()
    if "spring-boot" in normalized or "org.springframework" in normalized:
        return ["spring"]
    return []
