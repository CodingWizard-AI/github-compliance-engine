from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi.testclient import TestClient

from github_compliance_engine_api.ingestion import (
    CloneResult,
    CloneTimeoutError,
    RepositoryUnavailableError,
    WorkspaceError,
)
from github_compliance_engine_api.main import create_app


def mock_ingestion_settings(tmp_path: Path) -> SimpleNamespace:
    return SimpleNamespace(
        ingestion_workspace_root=tmp_path,
        ingestion_clone_depth=1,
        ingestion_clone_timeout_seconds=60,
    )


# Scaffold acceptance coverage: TC-ING-001, TC-OBJ-001, TC-CORE-001, V-ING-001, V-OBJ-001, V-CORE-001
# @golden-thread FEAT-SCAFFOLD-001, FEAT-ING-001, FR-ING-001, REST-ANALYZE-001, CF-ANALYZE-INGEST-001, TC-ING-001, V-ING-001
def test_analyze_accepts_public_github_repo_url(tmp_path: Path, monkeypatch) -> None:
    clone_repository = Mock(
        return_value=CloneResult(
            analysis_id="analysis-placeholder-001",
            repo_url="https://github.com/octocat/Hello-World",
            local_clone_path=tmp_path / "analysis-placeholder-001" / "repo",
            clone_status="cloned",
            commit_sha="abc123",
        )
    )
    monkeypatch.setattr("github_compliance_engine_api.api.routes.clone_repository", clone_repository)
    monkeypatch.setattr("github_compliance_engine_api.api.routes.get_settings", lambda: mock_ingestion_settings(tmp_path))
    client = TestClient(create_app())

    response = client.post(
        "/api/analyze",
        json={"repo_url": "https://github.com/octocat/Hello-World"},
    )

    assert response.status_code == 202
    body = response.json()
    assert body["analysis_id"] == "analysis-placeholder-001"
    assert body["status"] == "accepted"
    assert body["repo_url"] == "https://github.com/octocat/Hello-World"
    assert body["clone_status"] == "cloned"
    clone_request = clone_repository.call_args.args[0]
    assert clone_request.analysis_id == "analysis-placeholder-001"
    assert str(clone_request.repo_url) == "https://github.com/octocat/Hello-World"
    assert clone_request.workspace_root == tmp_path
    assert clone_request.clone_depth == 1
    assert clone_request.clone_timeout_seconds == 60


def test_analyze_rejects_invalid_repo_url(monkeypatch) -> None:
    clone_repository = Mock()
    monkeypatch.setattr("github_compliance_engine_api.api.routes.clone_repository", clone_repository)
    client = TestClient(create_app())

    response = client.post("/api/analyze", json={"repo_url": "not-a-url"})

    assert response.status_code == 422
    clone_repository.assert_not_called()


def test_analyze_rejects_non_github_repo_url(monkeypatch) -> None:
    clone_repository = Mock()
    monkeypatch.setattr("github_compliance_engine_api.api.routes.clone_repository", clone_repository)
    client = TestClient(create_app())

    response = client.post(
        "/api/analyze",
        json={"repo_url": "https://example.com/octocat/Hello-World"},
    )

    assert response.status_code == 422
    clone_repository.assert_not_called()


def test_analyze_rejects_missing_repo_path(monkeypatch) -> None:
    clone_repository = Mock()
    monkeypatch.setattr("github_compliance_engine_api.api.routes.clone_repository", clone_repository)
    client = TestClient(create_app())

    response = client.post(
        "/api/analyze",
        json={"repo_url": "https://github.com/octocat"},
    )

    assert response.status_code == 422
    clone_repository.assert_not_called()


def test_analyze_maps_repository_unavailable_to_safe_error(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "github_compliance_engine_api.api.routes.clone_repository",
        Mock(side_effect=RepositoryUnavailableError("Repository could not be cloned.")),
    )
    monkeypatch.setattr("github_compliance_engine_api.api.routes.get_settings", lambda: mock_ingestion_settings(tmp_path))
    client = TestClient(create_app())

    response = client.post(
        "/api/analyze",
        json={"repo_url": "https://github.com/octocat/Hello-World"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Repository could not be cloned."}


def test_analyze_maps_timeout_to_safe_error(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "github_compliance_engine_api.api.routes.clone_repository",
        Mock(side_effect=CloneTimeoutError("Repository clone timed out.")),
    )
    monkeypatch.setattr("github_compliance_engine_api.api.routes.get_settings", lambda: mock_ingestion_settings(tmp_path))
    client = TestClient(create_app())

    response = client.post(
        "/api/analyze",
        json={"repo_url": "https://github.com/octocat/Hello-World"},
    )

    assert response.status_code == 504
    assert response.json() == {"detail": "Repository clone timed out."}


def test_analyze_maps_workspace_error_to_generic_message(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "github_compliance_engine_api.api.routes.clone_repository",
        Mock(side_effect=WorkspaceError("raw /tmp/private/path detail")),
    )
    monkeypatch.setattr("github_compliance_engine_api.api.routes.get_settings", lambda: mock_ingestion_settings(tmp_path))
    client = TestClient(create_app())

    response = client.post(
        "/api/analyze",
        json={"repo_url": "https://github.com/octocat/Hello-World"},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Analysis workspace could not be prepared."}
