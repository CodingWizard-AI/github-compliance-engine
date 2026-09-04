from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator

from github_compliance_engine_api.github_urls import validate_public_github_repo_url


# @golden-thread FEAT-ING-001, FR-ING-001, CF-ANALYZE-INGEST-001, TC-ING-001, V-ING-001
class CloneRequest(BaseModel):
    analysis_id: str = Field(min_length=1)
    repo_url: HttpUrl
    workspace_root: Path
    clone_depth: int = Field(default=1, ge=1)
    clone_timeout_seconds: int = Field(default=60, ge=1)

    @field_validator("repo_url")
    @classmethod
    def validate_github_repo_url(cls, value: HttpUrl) -> HttpUrl:
        return validate_public_github_repo_url(value)


class CloneResult(BaseModel):
    analysis_id: str
    repo_url: str
    local_clone_path: Path
    clone_status: Literal["cloned"]
    commit_sha: str | None = None


ErrorSeverity = Literal["info", "warning", "error", "fatal"]
AnalysisStage = Literal[
    "clone",
    "metadata",
    "endpoint_extraction",
    "ruleset",
    "graph",
    "objective_mapping",
    "orphan_detection",
    "scoring",
    "api_serialization",
    "ui",
]
FileTreeNodeType = Literal["file", "dir", "symlink", "other"]
NormalizedLanguage = Literal["javascript_typescript", "python", "java", "unsupported"]
FrameworkName = Literal["express", "fastapi", "flask", "spring", "unknown"]
DetectionSource = Literal["github_languages_api", "file_extension_heuristic", "manifest", "manual"]
ManifestType = Literal["package_json", "requirements_txt", "pyproject_toml", "pom_xml", "build_gradle", "unknown"]
ParseStatus = Literal["parsed", "missing", "malformed", "skipped"]


# @golden-thread FEAT-ING-002, FR-ING-002, CF-ANALYZE-INGEST-001, TC-ING-002, V-ING-002
class MetadataExtractionRequest(BaseModel):
    analysis_id: str = Field(min_length=1)
    repo_url: str = Field(min_length=1)
    local_clone_path: Path
    timeout_seconds: int = Field(default=30, ge=1)
    max_tree_depth: int = Field(default=20, ge=1)
    max_file_count: int = Field(default=5000, ge=1)
    max_text_file_bytes: int = Field(default=1048576, ge=1)
    github_token: str | None = None


class AnalysisError(BaseModel):
    code: str
    message: str
    severity: ErrorSeverity
    stage: AnalysisStage
    safe: bool = True
    retryable: bool = False
    evidence_id: str | None = None


class ReadmeObject(BaseModel):
    raw_text: str
    source_path: str
    format: str | None = None
    size_bytes: int = Field(ge=0)
    truncated: bool = False


class FileTreeNode(BaseModel):
    path: str
    name: str
    type: FileTreeNodeType
    size_bytes: int | None = Field(default=None, ge=0)
    truncated: bool = False
    ignored: bool = False
    children: list["FileTreeNode"] = Field(default_factory=list)
    content_hash: str | None = None


class LanguageMixEntry(BaseModel):
    language: str
    normalized_language: NormalizedLanguage
    bytes: int | None = Field(default=None, ge=0)
    coverage_pct: float = Field(ge=0.0, le=100.0)
    framework: FrameworkName | None = None
    manifest_files_detected: list[str] = Field(default_factory=list)
    ruleset_applicable: bool
    ruleset_ids: list[str] = Field(default_factory=list)
    detection_source: DetectionSource


class ManifestDescriptor(BaseModel):
    path: str
    manifest_type: ManifestType
    package_manager: str | None = None
    detected_frameworks: list[FrameworkName] = Field(default_factory=list)
    parse_status: ParseStatus
    parse_error: AnalysisError | None = None


class RepoMetadata(BaseModel):
    readme: ReadmeObject | None = None
    file_tree: FileTreeNode | None = None
    language_mix: list[LanguageMixEntry] = Field(default_factory=list)
    manifests: list[ManifestDescriptor] = Field(default_factory=list)
    extraction_errors: list[AnalysisError] = Field(default_factory=list)


class IngestionError(Exception):
    def __init__(self, safe_message: str) -> None:
        self.safe_message = safe_message
        super().__init__(safe_message)


class RepositoryUnavailableError(IngestionError):
    pass


class CloneTimeoutError(IngestionError):
    pass


class WorkspaceError(IngestionError):
    pass


class MetadataExtractionError(IngestionError):
    pass
