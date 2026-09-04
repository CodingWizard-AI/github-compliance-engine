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


def test_analysis_workspace_path_maps_resolution_failure(monkeypatch) -> None:
    raw_detail = "RAW" + "_PATH"
    original_resolve = Path.resolve

    def resolve(path: Path, *args, **kwargs):
        if path.name == "workspace-root":
            raise OSError(raw_detail)
        return original_resolve(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", resolve)

    with pytest.raises(WorkspaceError) as exc_info:
        analysis_workspace_path(Path("/tmp/workspace-root"), "analysis-001")

    assert exc_info.value.safe_message == "Analysis workspace could not be resolved."
    assert raw_detail not in exc_info.value.safe_message


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


def test_cleanup_analysis_workspace_maps_exists_failure(tmp_path: Path, monkeypatch) -> None:
    workspace_path = tmp_path / "analysis-001"
    raw_detail = "RAW" + "_EXISTS"
    original_exists = Path.exists

    def exists(path: Path) -> bool:
        if path == workspace_path:
            raise OSError(raw_detail)
        return original_exists(path)

    monkeypatch.setattr(Path, "exists", exists)

    with pytest.raises(WorkspaceError) as exc_info:
        cleanup_analysis_workspace(workspace_path)

    assert exc_info.value.safe_message == "Analysis workspace could not be cleaned up."
    assert raw_detail not in exc_info.value.safe_message


def test_cleanup_analysis_workspace_maps_rmtree_failure(tmp_path: Path, monkeypatch) -> None:
    workspace_path = ensure_analysis_workspace(tmp_path, "analysis-001")
    raw_detail = "RAW" + "_RMTREE"
    monkeypatch.setattr(
        "github_compliance_engine_api.ingestion.workspace.shutil.rmtree",
        lambda path: (_ for _ in ()).throw(OSError(raw_detail)),
    )

    with pytest.raises(WorkspaceError) as exc_info:
        cleanup_analysis_workspace(workspace_path)

    assert exc_info.value.safe_message == "Analysis workspace could not be cleaned up."
    assert raw_detail not in exc_info.value.safe_message
