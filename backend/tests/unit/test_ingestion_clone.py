import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest

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


def completed_clone() -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=["git", "clone"], returncode=0)


# @golden-thread FEAT-ING-001, FR-ING-001, CF-ANALYZE-INGEST-001, TC-ING-001, V-ING-001
def test_clone_repository_uses_depth_one_by_default(tmp_path: Path, monkeypatch) -> None:
    run = Mock(return_value=completed_clone())
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.subprocess.run", run)
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.Repo", Mock(return_value=git_repo()))

    clone_repository(clone_request(tmp_path))

    assert run.call_count == 1
    assert run.call_args.args[0] == [
        "git",
        "clone",
        "--depth",
        "1",
        "--single-branch",
        "--",
        "https://github.com/octocat/Hello-World",
        str(tmp_path / "analysis-001" / "repo"),
    ]
    assert run.call_args.kwargs["check"] is True
    assert run.call_args.kwargs["capture_output"] is True
    assert run.call_args.kwargs["text"] is True
    assert run.call_args.kwargs["timeout"] == 60
    assert run.call_args.kwargs["env"]["GIT_TERMINAL_PROMPT"] == "0"


def test_clone_repository_uses_configured_git_executable(tmp_path: Path, monkeypatch) -> None:
    run = Mock(return_value=completed_clone())
    monkeypatch.setenv("GIT_PYTHON_GIT_EXECUTABLE", "/custom/git")
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.subprocess.run", run)
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.Repo", Mock(return_value=git_repo()))

    clone_repository(clone_request(tmp_path))

    assert run.call_args.args[0][0] == "/custom/git"


def test_clone_repository_opens_cloned_repo_for_commit_metadata(tmp_path: Path, monkeypatch) -> None:
    repo_factory = Mock(return_value=git_repo())
    monkeypatch.setattr(
        "github_compliance_engine_api.ingestion.clone.subprocess.run",
        Mock(return_value=completed_clone()),
    )
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.Repo", repo_factory)

    clone_repository(clone_request(tmp_path))

    repo_factory.assert_called_once_with(tmp_path / "analysis-001" / "repo")


def test_clone_repository_passes_canonical_repo_url_to_git(tmp_path: Path, monkeypatch) -> None:
    request = CloneRequest(
        analysis_id="analysis-001",
        repo_url="https://github.com:443/octocat/Hello-World",
        workspace_root=tmp_path,
    )
    run = Mock(return_value=completed_clone())
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.subprocess.run", run)
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.Repo", Mock(return_value=git_repo()))

    result = clone_repository(request)

    assert result.repo_url == "https://github.com/octocat/Hello-World"
    assert run.call_args.args[0][6] == "https://github.com/octocat/Hello-World"


def test_clone_repository_creates_isolated_workspace_and_returns_result(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "github_compliance_engine_api.ingestion.clone.subprocess.run",
        Mock(return_value=completed_clone()),
    )
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.Repo", Mock(return_value=git_repo("def456")))

    result = clone_repository(clone_request(tmp_path))

    assert (tmp_path / "analysis-001").exists()
    assert result.analysis_id == "analysis-001"
    assert result.repo_url == "https://github.com/octocat/Hello-World"
    assert result.local_clone_path == tmp_path / "analysis-001" / "repo"
    assert result.clone_status == "cloned"
    assert result.commit_sha == "def456"


def test_clone_repository_cleans_pre_existing_clone_target(tmp_path: Path, monkeypatch) -> None:
    workspace_path = tmp_path / "analysis-001"
    clone_path = workspace_path / "repo"
    clone_path.mkdir(parents=True)
    (clone_path / "stale.txt").write_text("stale clone", encoding="utf-8")
    run = Mock(return_value=completed_clone())
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.subprocess.run", run)
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.Repo", Mock(return_value=git_repo()))

    result = clone_repository(clone_request(tmp_path))

    assert not (clone_path / "stale.txt").exists()
    assert result.local_clone_path == clone_path
    assert run.call_args.args[0][-1] == str(clone_path)


def test_clone_repository_maps_pre_existing_cleanup_failure(tmp_path: Path, monkeypatch) -> None:
    clone_path = tmp_path / "analysis-001" / "repo"
    clone_path.mkdir(parents=True)
    run = Mock()
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.subprocess.run", run)
    monkeypatch.setattr(
        "github_compliance_engine_api.ingestion.clone.cleanup_analysis_workspace",
        Mock(side_effect=OSError("raw cleanup failure")),
    )

    with pytest.raises(WorkspaceError) as exc_info:
        clone_repository(clone_request(tmp_path))

    assert exc_info.value.safe_message == "Analysis workspace could not be prepared."
    run.assert_not_called()


def test_clone_repository_maps_clone_target_exists_failure(tmp_path: Path, monkeypatch) -> None:
    run = Mock()
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.subprocess.run", run)
    original_exists = Path.exists

    def exists(path: Path) -> bool:
        if path.name == "repo":
            raise OSError("raw exists failure")
        return original_exists(path)

    monkeypatch.setattr(Path, "exists", exists)

    with pytest.raises(WorkspaceError) as exc_info:
        clone_repository(clone_request(tmp_path))

    assert exc_info.value.safe_message == "Analysis workspace could not be prepared."
    run.assert_not_called()


def test_clone_repository_maps_git_error_cleanup_failure(tmp_path: Path, monkeypatch) -> None:
    run = Mock(side_effect=subprocess.CalledProcessError(128, ["git", "clone"], stderr="fatal unavailable"))
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.subprocess.run", run)
    cleanup_error = "CLEANUP" + "_DETAIL"
    monkeypatch.setattr(
        "github_compliance_engine_api.ingestion.clone.cleanup_analysis_workspace",
        Mock(side_effect=OSError(cleanup_error)),
    )

    with pytest.raises(WorkspaceError) as exc_info:
        clone_repository(clone_request(tmp_path))

    assert exc_info.value.safe_message == "Analysis workspace could not be prepared."
    assert cleanup_error not in exc_info.value.safe_message


def test_clone_repository_maps_timeout_cleanup_failure(tmp_path: Path, monkeypatch) -> None:
    run = Mock(side_effect=subprocess.TimeoutExpired(["git", "clone"], 60, stderr="fatal unavailable"))
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.subprocess.run", run)
    cleanup_error = "CLEANUP" + "_DETAIL"
    monkeypatch.setattr(
        "github_compliance_engine_api.ingestion.clone.cleanup_analysis_workspace",
        Mock(side_effect=OSError(cleanup_error)),
    )

    with pytest.raises(WorkspaceError) as exc_info:
        clone_repository(clone_request(tmp_path))

    assert exc_info.value.safe_message == "Analysis workspace could not be prepared."
    assert cleanup_error not in exc_info.value.safe_message


def test_clone_repository_maps_git_errors_to_safe_exception(tmp_path: Path, monkeypatch) -> None:
    run = Mock(side_effect=subprocess.CalledProcessError(128, ["git", "clone"], stderr="fatal: token TOKEN_REDACTED leaked"))
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.subprocess.run", run)

    with pytest.raises(RepositoryUnavailableError) as exc_info:
        clone_repository(clone_request(tmp_path))

    assert exc_info.value.safe_message == "Repository could not be cloned. Confirm the repository is public and reachable."
    assert "TOKEN_REDACTED" not in exc_info.value.safe_message
    assert not (tmp_path / "analysis-001").exists()


def test_clone_repository_maps_timeout_and_cleans_partial_workspace(tmp_path: Path, monkeypatch) -> None:
    workspace_path = tmp_path / "analysis-001"
    workspace_path.mkdir()
    (workspace_path / "partial.txt").write_text("partial clone", encoding="utf-8")
    run = Mock(side_effect=subprocess.TimeoutExpired(["git", "clone"], 60, stderr="fatal: remote hung up"))
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.subprocess.run", run)

    with pytest.raises(CloneTimeoutError) as exc_info:
        clone_repository(clone_request(tmp_path))

    assert exc_info.value.safe_message == "Repository clone timed out. Try again later or use a smaller public repository."
    assert not workspace_path.exists()


def test_clone_repository_timeout_does_not_depend_on_error_text(tmp_path: Path, monkeypatch) -> None:
    run = Mock(side_effect=subprocess.TimeoutExpired(["git", "clone"], 60, stderr="fatal: remote hung up"))
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.subprocess.run", run)

    with pytest.raises(CloneTimeoutError) as exc_info:
        clone_repository(clone_request(tmp_path))

    assert exc_info.value.safe_message == "Repository clone timed out. Try again later or use a smaller public repository."
    assert not (tmp_path / "analysis-001").exists()


def test_clone_repository_surfaces_workspace_errors_without_clone(tmp_path: Path, monkeypatch) -> None:
    run = Mock()
    monkeypatch.setattr("github_compliance_engine_api.ingestion.clone.subprocess.run", run)

    with pytest.raises(WorkspaceError):
        clone_repository(clone_request(tmp_path, analysis_id="../outside"))

    run.assert_not_called()
