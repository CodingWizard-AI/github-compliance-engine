from typing import Any, Literal

from pydantic import BaseModel, HttpUrl


class AnalyzeRequest(BaseModel):
    repo_url: HttpUrl


class AnalyzeResponse(BaseModel):
    analysis_id: str
    status: Literal["accepted"]
    repo_url: str


class AnalysisResultsResponse(BaseModel):
    analysis_id: str
    status: Literal["complete"]
    graph: dict[str, Any]
    objective_mappings: list[dict[str, Any]]
    orphaned_code_units: list[dict[str, Any]]
    traceability_score: float
