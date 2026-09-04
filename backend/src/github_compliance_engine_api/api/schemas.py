from typing import Any, Literal

from pydantic import BaseModel, HttpUrl, field_validator

from github_compliance_engine_api.github_urls import validate_public_github_repo_url as validate_github_repo_url


class AnalyzeRequest(BaseModel):
    repo_url: HttpUrl

    @field_validator("repo_url")
    @classmethod
    def validate_public_github_repo_url(cls, value: HttpUrl) -> HttpUrl:
        return validate_github_repo_url(value)


class AnalyzeResponse(BaseModel):
    analysis_id: str
    status: Literal["accepted"]
    repo_url: str
    clone_status: Literal["cloned"]


class AnalysisResultsResponse(BaseModel):
    analysis_id: str
    status: Literal["complete"]
    graph: dict[str, Any]
    objective_mappings: list[dict[str, Any]]
    orphaned_code_units: list[dict[str, Any]]
    traceability_score: float
