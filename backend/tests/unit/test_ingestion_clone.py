from pathlib import Path
from unittest.mock import Mock

import pytest
from git import GitCommandError

from github_compliance_engine_api.ingestion import (
    CloneRequest,
    CloneTimeoutError,
    RepositoryUnavailableError,
    WorkspaceError,
    clone_repository,
)


def clone_request(tmp_path: Path, analysis_id: str = "analysis-001") -> CloneRequest:
    return CloneRequest(
        analysis_id=analysis_id,
        repo_url="https://github.com/octocat/Hello-World",
        workspace_root=tmp_path,
    )


def git_repo(commit_sha: str = "abc123") -> Mock:
    repo = Mock()
    repo.head.commit.hexsha = commit_sha
    return repo


# @golden-thread FEAT-ING-001, FR-ING-001, CF-ANALYZE-INGEST-001, TC-ING-001, V-ING-001
def test_clone_repository_uses_depth_one_by_default(tmp_path: Path, monkeypatch) -> None:
    clone_from = Mock(return_value=git_repo())
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.Repo.clone_from", clone_from)

    clone_repository(clone_request(tmp_path))

    clone_from.assert_called_once_with(
        "https://github.com/octocat/Hello-World",
        tmp_path / "analysis-001" / "repo",
        depth=1,
        single_branch=True,
        kill_after_timeout=60,
    )


def test_clone_repository_creates_isolated_workspace_and_returns_result(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "github_compliance_engine_api.ingestion.clone.Repo.clone_from",
        Mock(return_value=git_repo("def456")),
    )

    result = clone_repository(clone_request(tmp_path))

    assert (tmp_path / "analysis-001").exists()
    assert result.analysis_id == "analysis-001"
    assert result.repo_url == "https://github.com/octocat/Hello-World"
    assert result.local_clone_path == tmp_path / "analysis-001" / "repo"
    assert result.clone_status == "cloned"
    assert result.commit_sha == "def456"


def test_clone_repository_maps_git_errors_to_safe_exception(tmp_path: Path, monkeypatch) -> None:
    clone_from = Mock(side_effect=GitCommandError("clone", "fatal: token TOKEN_REDACTED leaked"))
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.Repo.clone_from", clone_from)

    with pytest.raises(RepositoryUnavailableError) as exc_info:
        clone_repository(clone_request(tmp_path))

    assert exc_info.value.safe_message == "Repository could not be cloned. Confirm the repository is public and reachable."
    assert "TOKEN_REDACTED" not in exc_info.value.safe_message
    assert not (tmp_path / "analysis-001").exists()


def test_clone_repository_maps_timeout_and_cleans_partial_workspace(tmp_path: Path, monkeypatch) -> None:
    workspace_path = tmp_path / "analysis-001"
    workspace_path.mkdir()
    (workspace_path / "partial.txt").write_text("partial clone", encoding="utf-8")
    clone_from = Mock(side_effect=GitCommandError("clone", "kill_after_timeout reached"))
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.Repo.clone_from", clone_from)

    with pytest.raises(CloneTimeoutError) as exc_info:
        clone_repository(clone_request(tmp_path))

    assert exc_info.value.safe_message == "Repository clone timed out. Try again later or use a smaller public repository."
    assert not workspace_path.exists()


def test_clone_repository_surfaces_workspace_errors_without_clone(tmp_path: Path, monkeypatch) -> None:
    clone_from = Mock()
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.Repo.clone_from", clone_from)

    with pytest.raises(WorkspaceError):
        clone_repository(clone_request(tmp_path, analysis_id="../outside"))

    clone_from.assert_not_called()
