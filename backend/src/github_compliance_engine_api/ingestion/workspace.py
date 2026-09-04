import re
import shutil
from pathlib import Path

from github_compliance_engine_api.ingestion.contracts import WorkspaceError


ANALYSIS_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


# @golden-thread FEAT-ING-001, FR-ING-001, CF-ANALYZE-INGEST-001, TC-ING-001, V-ING-001
def analysis_workspace_path(workspace_root: Path, analysis_id: str) -> Path:
    if not analysis_id or not ANALYSIS_ID_PATTERN.fullmatch(analysis_id):
        raise WorkspaceError("Analysis workspace ID is invalid.")

    try:
        workspace_root = workspace_root.expanduser().resolve()
        workspace_path = (workspace_root / analysis_id).resolve()
        if workspace_root != workspace_path and workspace_root not in workspace_path.parents:
            raise WorkspaceError("Analysis workspace must be under the configured workspace root.")
    except WorkspaceError:
        raise
    except OSError as exc:
        raise WorkspaceError("Analysis workspace could not be resolved.") from exc

    return workspace_path


def ensure_analysis_workspace(workspace_root: Path, analysis_id: str) -> Path:
    workspace_path = analysis_workspace_path(workspace_root, analysis_id)
    try:
        workspace_path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise WorkspaceError("Analysis workspace could not be created.") from exc
    return workspace_path


def cleanup_analysis_workspace(workspace_path: Path) -> None:
    try:
        if workspace_path.exists():
            shutil.rmtree(workspace_path)
    except OSError as exc:
        raise WorkspaceError("Analysis workspace could not be cleaned up.") from exc
