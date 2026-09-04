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
