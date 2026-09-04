"""Repo ingestion boundary for FR-ING-001."""

from github_compliance_engine_api.ingestion.contracts import (
    CloneRequest,
    CloneResult,
    CloneTimeoutError,
    IngestionError,
    RepositoryUnavailableError,
    WorkspaceError,
)
from github_compliance_engine_api.ingestion.clone import clone_repository
from github_compliance_engine_api.ingestion.workspace import (
    analysis_workspace_path,
    cleanup_analysis_workspace,
    ensure_analysis_workspace,
)

__all__ = [
    "CloneRequest",
    "CloneResult",
    "CloneTimeoutError",
    "IngestionError",
    "RepositoryUnavailableError",
    "WorkspaceError",
    "analysis_workspace_path",
    "clone_repository",
    "cleanup_analysis_workspace",
    "ensure_analysis_workspace",
]
