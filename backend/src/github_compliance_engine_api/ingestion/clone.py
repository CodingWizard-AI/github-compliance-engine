import os
from pathlib import Path

from git import Git, GitCommandError, Repo
from git.exc import GitError

from github_compliance_engine_api.github_urls import canonical_github_repo_url
from github_compliance_engine_api.ingestion.contracts import (
    CloneRequest,
    CloneResult,
    CloneTimeoutError,
    RepositoryUnavailableError,
    WorkspaceError,
)
from github_compliance_engine_api.ingestion.workspace import (
    cleanup_analysis_workspace,
    ensure_analysis_workspace,
)


REPOSITORY_UNAVAILABLE_MESSAGE = "Repository could not be cloned. Confirm the repository is public and reachable."
CLONE_TIMEOUT_MESSAGE = "Repository clone timed out. Try again later or use a smaller public repository."


# @golden-thread FEAT-ING-001, FR-ING-001, CF-ANALYZE-INGEST-001, TC-ING-001, V-ING-001
def clone_repository(request: CloneRequest) -> CloneResult:
    workspace_path = ensure_analysis_workspace(request.workspace_root, request.analysis_id)
    clone_path = _prepare_clone_path(workspace_path, request)
    repo_url = canonical_github_repo_url(request.repo_url)

    try:
        _run_git_clone(repo_url, clone_path, request)
        repo = Repo(clone_path)
    except WorkspaceError:
        raise
    except GitCommandError as exc:
        _cleanup_workspace_or_raise(workspace_path)
        if _is_timeout_error(exc):
            raise CloneTimeoutError(CLONE_TIMEOUT_MESSAGE) from exc
        raise RepositoryUnavailableError(REPOSITORY_UNAVAILABLE_MESSAGE) from exc
    except GitError as exc:
        _cleanup_workspace_or_raise(workspace_path)
        raise RepositoryUnavailableError(REPOSITORY_UNAVAILABLE_MESSAGE) from exc
    except OSError as exc:
        _cleanup_workspace_or_raise(workspace_path)
        raise RepositoryUnavailableError(REPOSITORY_UNAVAILABLE_MESSAGE) from exc

    return CloneResult(
        analysis_id=request.analysis_id,
        repo_url=repo_url,
        local_clone_path=Path(clone_path),
        clone_status="cloned",
        commit_sha=_commit_sha(repo),
    )


def _prepare_clone_path(workspace_path: Path, request: CloneRequest) -> Path:
    clone_path = workspace_path / "repo"
    try:
        if not clone_path.exists():
            return clone_path
    except OSError as exc:
        raise WorkspaceError("Analysis workspace could not be prepared.") from exc

    try:
        cleanup_analysis_workspace(workspace_path)
        workspace_path = ensure_analysis_workspace(request.workspace_root, request.analysis_id)
    except WorkspaceError:
        raise
    except OSError as exc:
        raise WorkspaceError("Analysis workspace could not be prepared.") from exc

    return workspace_path / "repo"


def _run_git_clone(repo_url: str, clone_path: Path, request: CloneRequest) -> None:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    git = Git(os.getcwd())
    git.clone(
        "--depth",
        str(request.clone_depth),
        "--single-branch",
        "--",
        repo_url,
        os.fspath(clone_path),
        env=env,
        with_extended_output=True,
        kill_after_timeout=request.clone_timeout_seconds,
    )


def _cleanup_workspace_or_raise(workspace_path: Path) -> None:
    try:
        cleanup_analysis_workspace(workspace_path)
    except WorkspaceError:
        raise
    except OSError as exc:
        raise WorkspaceError("Analysis workspace could not be prepared.") from exc


def _is_timeout_error(exc: GitCommandError) -> bool:
    error_text = f"{exc}".lower()
    return "timeout" in error_text or "timed out" in error_text


def _commit_sha(repo: Repo) -> str | None:
    try:
        return str(repo.head.commit.hexsha)
    except (AttributeError, TypeError, ValueError):
        return None
