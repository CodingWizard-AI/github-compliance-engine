from threading import RLock
from typing import Literal

from pydantic import BaseModel, Field

from github_compliance_engine_api.ingestion import AnalysisError, CloneResult, RepoMetadata


AnalysisStatus = Literal["ingesting", "metadata_extracted", "failed"]


# @golden-thread FEAT-ING-002, FR-ING-002, CF-ANALYZE-INGEST-001, TC-ING-002, V-ING-002
class GoldenThreadAnalysis(BaseModel):
    analysis_id: str
    repo_url: str
    status: AnalysisStatus
    clone_result: CloneResult | None = None
    repo_metadata: RepoMetadata | None = None
    errors: list[AnalysisError] = Field(default_factory=list)


_analysis_store: dict[str, GoldenThreadAnalysis] = {}
_analysis_store_lock = RLock()


def save_analysis(analysis: GoldenThreadAnalysis) -> None:
    with _analysis_store_lock:
        _analysis_store[analysis.analysis_id] = analysis.model_copy(deep=True)


def get_analysis(analysis_id: str) -> GoldenThreadAnalysis | None:
    with _analysis_store_lock:
        analysis = _analysis_store.get(analysis_id)
        return analysis.model_copy(deep=True) if analysis is not None else None


def clear_analysis_store() -> None:
    with _analysis_store_lock:
        _analysis_store.clear()
