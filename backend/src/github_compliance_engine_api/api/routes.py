from fastapi import APIRouter, HTTPException, status

from github_compliance_engine_api.api.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    AnalysisResultsResponse,
)
from github_compliance_engine_api.ingestion import (
    CloneRequest,
    CloneTimeoutError,
    RepositoryUnavailableError,
    WorkspaceError,
    clone_repository,
)
from github_compliance_engine_api.objective_mapping import anchor_public_interfaces
from github_compliance_engine_api.settings import get_settings


ANALYSIS_ID = "analysis-placeholder-001"
WORKSPACE_ERROR_MESSAGE = "Analysis workspace could not be prepared."


# @golden-thread FEAT-SCAFFOLD-001, FEAT-ING-001, FR-ING-001, REST-ANALYZE-001, CF-ANALYZE-INGEST-001, TC-ING-001, V-ING-001
# @golden-thread FEAT-SCAFFOLD-001, FR-OBJ-001, REST-RESULTS-001, TC-OBJ-001, V-OBJ-001
router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze", response_model=AnalyzeResponse, status_code=status.HTTP_202_ACCEPTED)
def analyze_repo(payload: AnalyzeRequest) -> AnalyzeResponse:
    settings = get_settings()
    clone_request = CloneRequest(
        analysis_id=ANALYSIS_ID,
        repo_url=payload.repo_url,
        workspace_root=settings.ingestion_workspace_root,
        clone_depth=settings.ingestion_clone_depth,
        clone_timeout_seconds=settings.ingestion_clone_timeout_seconds,
    )
    try:
        clone_result = clone_repository(clone_request)
    except RepositoryUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.safe_message) from exc
    except CloneTimeoutError as exc:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=exc.safe_message) from exc
    except WorkspaceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=WORKSPACE_ERROR_MESSAGE) from exc

    return AnalyzeResponse(
        analysis_id=clone_result.analysis_id,
        status="accepted",
        repo_url=clone_result.repo_url,
        clone_status=clone_result.clone_status,
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
