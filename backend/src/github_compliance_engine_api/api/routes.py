import logging
from uuid import uuid4

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


WORKSPACE_ERROR_MESSAGE = "Analysis workspace could not be prepared."
logger = logging.getLogger(__name__)


# @golden-thread FEAT-SCAFFOLD-001, FEAT-ING-001, FR-ING-001, REST-ANALYZE-001, CF-ANALYZE-INGEST-001, TC-ING-001, V-ING-001
# @golden-thread FEAT-SCAFFOLD-001, FR-OBJ-001, REST-RESULTS-001, TC-OBJ-001, V-OBJ-001
router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze", response_model=AnalyzeResponse, status_code=status.HTTP_202_ACCEPTED)
def analyze_repo(payload: AnalyzeRequest) -> AnalyzeResponse:
    settings = get_settings()
    analysis_id = generate_analysis_id()
    clone_request = CloneRequest(
        analysis_id=analysis_id,
        repo_url=payload.repo_url,
        workspace_root=settings.ingestion_workspace_root,
        clone_depth=settings.ingestion_clone_depth,
        clone_timeout_seconds=settings.ingestion_clone_timeout_seconds,
    )
    try:
        clone_result = clone_repository(clone_request)
    except RepositoryUnavailableError as exc:
        log_ingestion_error(analysis_id, status.HTTP_400_BAD_REQUEST, exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.safe_message) from exc
    except CloneTimeoutError as exc:
        log_ingestion_error(analysis_id, status.HTTP_504_GATEWAY_TIMEOUT, exc)
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=exc.safe_message) from exc
    except WorkspaceError as exc:
        log_ingestion_error(analysis_id, status.HTTP_500_INTERNAL_SERVER_ERROR, exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=WORKSPACE_ERROR_MESSAGE) from exc

    return AnalyzeResponse(
        analysis_id=clone_result.analysis_id,
        status="accepted",
        repo_url=clone_result.repo_url,
        clone_status=clone_result.clone_status,
    )


def generate_analysis_id() -> str:
    return f"analysis-{uuid4().hex}"


def log_ingestion_error(analysis_id: str, http_status: int, exc: Exception) -> None:
    logger.warning(
        "Mapped ingestion error",
        extra={
            "analysis_id": analysis_id,
            "http_status": http_status,
            "error_type": type(exc).__name__,
        },
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
