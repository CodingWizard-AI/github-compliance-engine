"""Repo ingestion boundary for FR-ING-001."""

from github_compliance_engine_api.ingestion.contracts import (
    AnalysisError,
    CloneRequest,
    CloneResult,
    CloneTimeoutError,
    FileTreeNode,
    IngestionError,
    LanguageMixEntry,
    ManifestDescriptor,
    MetadataExtractionError,
    MetadataExtractionRequest,
    RepositoryUnavailableError,
    ReadmeObject,
    RepoMetadata,
    WorkspaceError,
)
from github_compliance_engine_api.ingestion.clone import clone_repository
from github_compliance_engine_api.ingestion.metadata import extract_repo_metadata
from github_compliance_engine_api.ingestion.workspace import (
    analysis_workspace_path,
    cleanup_analysis_workspace,
    ensure_analysis_workspace,
)

__all__ = [
    "AnalysisError",
    "CloneRequest",
    "CloneResult",
    "CloneTimeoutError",
    "FileTreeNode",
    "IngestionError",
    "LanguageMixEntry",
    "ManifestDescriptor",
    "MetadataExtractionError",
    "MetadataExtractionRequest",
    "RepositoryUnavailableError",
    "ReadmeObject",
    "RepoMetadata",
    "WorkspaceError",
    "analysis_workspace_path",
    "clone_repository",
    "cleanup_analysis_workspace",
    "ensure_analysis_workspace",
    "extract_repo_metadata",
]
