from pathlib import Path

import pytest

from github_compliance_engine_api.ingestion import (
    WorkspaceError,
    analysis_workspace_path,
    cleanup_analysis_workspace,
    ensure_analysis_workspace,
)


# @golden-thread FEAT-ING-001, FR-ING-001, CF-ANALYZE-INGEST-001, TC-ING-001, V-ING-001
def test_analysis_workspace_path_is_under_root(tmp_path: Path) -> None:
    workspace_path = analysis_workspace_path(tmp_path, "analysis-001")

    assert workspace_path == tmp_path.resolve() / "analysis-001"


def test_ensure_analysis_workspace_creates_directory(tmp_path: Path) -> None:
    workspace_path = ensure_analysis_workspace(tmp_path, "analysis-001")

    assert workspace_path.exists()
    assert workspace_path.is_dir()


@pytest.mark.parametrize("analysis_id", ["", "../outside", "nested/path", "analysis 001"])
def test_analysis_workspace_path_rejects_invalid_ids(tmp_path: Path, analysis_id: str) -> None:
    with pytest.raises(WorkspaceError):
        analysis_workspace_path(tmp_path, analysis_id)


def test_cleanup_analysis_workspace_removes_directory(tmp_path: Path) -> None:
    workspace_path = ensure_analysis_workspace(tmp_path, "analysis-001")
    marker = workspace_path / "repo.txt"
    marker.write_text("placeholder", encoding="utf-8")

    cleanup_analysis_workspace(workspace_path)

    assert not workspace_path.exists()
