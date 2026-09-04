from pathlib import Path

import pytest
from pydantic import ValidationError

from github_compliance_engine_api.ingestion import CloneRequest, CloneResult


# @golden-thread FEAT-ING-001, FR-ING-001, CF-ANALYZE-INGEST-001, TC-ING-001, V-ING-001
def test_clone_request_accepts_github_repo_url() -> None:
    request = CloneRequest(
        analysis_id="analysis-001",
        repo_url="https://github.com/octocat/Hello-World",
        workspace_root=Path("/tmp/github-compliance-engine/analyses"),
    )

    assert str(request.repo_url) == "https://github.com/octocat/Hello-World"
    assert request.clone_depth == 1
    assert request.clone_timeout_seconds == 60


def test_clone_request_rejects_non_github_repo_url() -> None:
    with pytest.raises(ValidationError):
        CloneRequest(
            analysis_id="analysis-001",
            repo_url="https://example.com/octocat/Hello-World",
            workspace_root=Path("/tmp/github-compliance-engine/analyses"),
        )


def test_clone_request_rejects_non_https_github_url() -> None:
    with pytest.raises(ValidationError):
        CloneRequest(
            analysis_id="analysis-001",
            repo_url="http://github.com/octocat/Hello-World",
            workspace_root=Path("/tmp/github-compliance-engine/analyses"),
        )


def test_clone_request_rejects_missing_repo_path() -> None:
    with pytest.raises(ValidationError):
        CloneRequest(
            analysis_id="analysis-001",
            repo_url="https://github.com/octocat",
            workspace_root=Path("/tmp/github-compliance-engine/analyses"),
        )


def test_clone_result_represents_completed_clone() -> None:
    result = CloneResult(
        analysis_id="analysis-001",
        repo_url="https://github.com/octocat/Hello-World",
        local_clone_path=Path("/tmp/github-compliance-engine/analyses/analysis-001/repo"),
        clone_status="cloned",
        commit_sha="abc123",
    )

    assert result.clone_status == "cloned"
    assert result.commit_sha == "abc123"
