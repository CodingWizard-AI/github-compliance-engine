from fastapi import APIRouter, status

from github_compliance_engine_api.api.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    AnalysisResultsResponse,
)
from github_compliance_engine_api.objective_mapping import anchor_public_interfaces


# @golden-thread FEAT-SCAFFOLD-001, FR-ING-001, REST-ANALYZE-001, TC-ING-001, V-ING-001
# @golden-thread FEAT-SCAFFOLD-001, FR-OBJ-001, REST-RESULTS-001, TC-OBJ-001, V-OBJ-001
router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze", response_model=AnalyzeResponse, status_code=status.HTTP_202_ACCEPTED)
def analyze_repo(payload: AnalyzeRequest) -> AnalyzeResponse:
    return AnalyzeResponse(
        analysis_id="analysis-placeholder-001",
        status="accepted",
        repo_url=str(payload.repo_url),
    )


@router.get("/analyze/{analysis_id}/results", response_model=AnalysisResultsResponse)
def get_analysis_results(analysis_id: str) -> AnalysisResultsResponse:
    public_interfaces = [
        {"name": "POST /api/analyze", "public": True},
        {"name": "internal.clone_repo", "public": False},
    ]
    return AnalysisResultsResponse(
        analysis_id=analysis_id,
        status="complete",
        graph={
            "nodes": [
                {"id": "frontend", "label": "Next.js Frontend", "type": "Interface"},
                {"id": "backend", "label": "Python Analysis Backend", "type": "CodeUnit"},
            ],
            "edges": [{"source": "frontend", "target": "backend", "type": "CALLS"}],
        },
        objective_mappings=anchor_public_interfaces(public_interfaces),
        orphaned_code_units=[],
        traceability_score=1.0,
    )
