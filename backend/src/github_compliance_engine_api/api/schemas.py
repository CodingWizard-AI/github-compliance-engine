from typing import Any, Literal

from pydantic import BaseModel, HttpUrl, field_validator


class AnalyzeRequest(BaseModel):
    repo_url: HttpUrl

    @field_validator("repo_url")
    @classmethod
    def validate_public_github_repo_url(cls, value: HttpUrl) -> HttpUrl:
        path_segments = [segment for segment in value.path.split("/") if segment]
        if value.scheme != "https" or value.host != "github.com" or len(path_segments) != 2:
            raise ValueError("repo_url must be an HTTPS GitHub repository URL: https://github.com/{owner}/{repo}")

        return value


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
