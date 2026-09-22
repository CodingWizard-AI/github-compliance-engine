import re
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from github_compliance_engine_api.analysis_store import clear_analysis_store, get_analysis
from github_compliance_engine_api.ingestion import (
    CloneResult,
    CloneTimeoutError,
    FileTreeNode,
    MetadataExtractionError,
    RepositoryUnavailableError,
    RepoMetadata,
    WorkspaceError,
)
from github_compliance_engine_api.main import create_app


@pytest.fixture(autouse=True)
def reset_analysis_store() -> None:
    clear_analysis_store()


def mock_ingestion_settings(tmp_path: Path) -> SimpleNamespace:
    return SimpleNamespace(
        ingestion_workspace_root=tmp_path,
        ingestion_clone_depth=1,
        ingestion_clone_timeout_seconds=60,
        ingestion_metadata_timeout_seconds=30,
        ingestion_file_tree_max_depth=20,
        ingestion_file_tree_max_files=5000,
        ingestion_max_text_file_bytes=1048576,
        github_token=None,
    )


# Scaffold acceptance coverage: TC-ING-001, TC-OBJ-001, TC-CORE-001, V-ING-001, V-OBJ-001, V-CORE-001
# @golden-thread FEAT-SCAFFOLD-001, FEAT-ING-001, FR-ING-001, REST-ANALYZE-001, CF-ANALYZE-INGEST-001, TC-ING-001, V-ING-001
def test_analyze_accepts_public_github_repo_url(tmp_path: Path, monkeypatch) -> None:
    def clone_success(request):
        return CloneResult(
            analysis_id=request.analysis_id,
            repo_url=str(request.repo_url),
            local_clone_path=tmp_path / request.analysis_id / "repo",
            clone_status="cloned",
            commit_sha="abc123",
        )

    clone_repository = Mock(side_effect=clone_success)
    extract_repo_metadata = Mock(return_value=RepoMetadata(file_tree=FileTreeNode(path=".", name=".", type="dir")))
    monkeypatch.setattr("github_compliance_engine_api.api.routes.clone_repository", clone_repository)
    monkeypatch.setattr("github_compliance_engine_api.api.routes.extract_repo_metadata", extract_repo_metadata)
    monkeypatch.setattr("github_compliance_engine_api.api.routes.get_settings", lambda: mock_ingestion_settings(tmp_path))
    client = TestClient(create_app())

    response = client.post(
        "/api/analyze",
        json={"repo_url": "https://github.com/octocat/Hello-World"},
    )

    assert response.status_code == 202
    body = response.json()
    assert re.fullmatch(r"analysis-[0-9a-f]{32}", body["analysis_id"])
    assert body["status"] == "accepted"
    assert body["repo_url"] == "https://github.com/octocat/Hello-World"
    assert body["clone_status"] == "cloned"
    clone_request = clone_repository.call_args.args[0]
    assert clone_request.analysis_id == body["analysis_id"]
    assert str(clone_request.repo_url) == "https://github.com/octocat/Hello-World"
    assert clone_request.workspace_root == tmp_path
    assert clone_request.clone_depth == 1
    assert clone_request.clone_timeout_seconds == 60
    metadata_request = extract_repo_metadata.call_args.args[0]
    assert metadata_request.analysis_id == body["analysis_id"]
    assert metadata_request.repo_url == "https://github.com/octocat/Hello-World"
    assert metadata_request.local_clone_path == tmp_path / body["analysis_id"] / "repo"
    assert metadata_request.timeout_seconds == 30
    assert metadata_request.max_tree_depth == 20
    assert metadata_request.max_file_count == 5000
    assert metadata_request.max_text_file_bytes == 1048576
    assert metadata_request.github_token is None
    analysis = get_analysis(body["analysis_id"])
    assert analysis is not None
    assert analysis.status == "metadata_extracted"
    assert analysis.clone_result == clone_repository.return_value or analysis.clone_result.analysis_id == body["analysis_id"]
    assert analysis.repo_metadata == extract_repo_metadata.return_value


def test_analyze_passes_metadata_settings_and_github_token(tmp_path: Path, monkeypatch) -> None:
    def clone_success(request):
        return CloneResult(
            analysis_id=request.analysis_id,
            repo_url=str(request.repo_url),
            local_clone_path=tmp_path / request.analysis_id / "repo",
            clone_status="cloned",
        )

    settings = mock_ingestion_settings(tmp_path)
    settings.ingestion_metadata_timeout_seconds = 15
    settings.ingestion_file_tree_max_depth = 10
    settings.ingestion_file_tree_max_files = 250
    settings.ingestion_max_text_file_bytes = 2048
    settings.github_token = "local-token"
    extract_repo_metadata = Mock(return_value=RepoMetadata())
    monkeypatch.setattr("github_compliance_engine_api.api.routes.clone_repository", Mock(side_effect=clone_success))
    monkeypatch.setattr("github_compliance_engine_api.api.routes.extract_repo_metadata", extract_repo_metadata)
    monkeypatch.setattr("github_compliance_engine_api.api.routes.get_settings", lambda: settings)
    client = TestClient(create_app())

    response = client.post("/api/analyze", json={"repo_url": "https://github.com/octocat/Hello-World"})

    assert response.status_code == 202
    metadata_request = extract_repo_metadata.call_args.args[0]
    assert metadata_request.timeout_seconds == 15
    assert metadata_request.max_tree_depth == 10
    assert metadata_request.max_file_count == 250
    assert metadata_request.max_text_file_bytes == 2048
    assert metadata_request.github_token == "local-token"


def test_analyze_generates_unique_analysis_ids(tmp_path: Path, monkeypatch) -> None:
    def clone_success(request):
        return CloneResult(
            analysis_id=request.analysis_id,
            repo_url=str(request.repo_url),
            local_clone_path=tmp_path / request.analysis_id / "repo",
            clone_status="cloned",
        )

    clone_repository = Mock(side_effect=clone_success)
    extract_repo_metadata = Mock(return_value=RepoMetadata())
    monkeypatch.setattr("github_compliance_engine_api.api.routes.clone_repository", clone_repository)
    monkeypatch.setattr("github_compliance_engine_api.api.routes.extract_repo_metadata", extract_repo_metadata)
    monkeypatch.setattr("github_compliance_engine_api.api.routes.get_settings", lambda: mock_ingestion_settings(tmp_path))
    client = TestClient(create_app())

    first = client.post("/api/analyze", json={"repo_url": "https://github.com/octocat/Hello-World"})
    second = client.post("/api/analyze", json={"repo_url": "https://github.com/octocat/Hello-World"})

    assert first.status_code == 202
    assert second.status_code == 202
    assert first.json()["analysis_id"] != second.json()["analysis_id"]
    clone_requests = [call.args[0] for call in clone_repository.call_args_list]
    assert clone_requests[0].analysis_id == first.json()["analysis_id"]
    assert clone_requests[1].analysis_id == second.json()["analysis_id"]
    assert clone_requests[0].analysis_id != clone_requests[1].analysis_id
    assert extract_repo_metadata.call_count == 2
    assert get_analysis(first.json()["analysis_id"]) is not None
    assert get_analysis(second.json()["analysis_id"]) is not None


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


def test_analyze_rejects_credential_bearing_repo_url(monkeypatch) -> None:
    clone_repository = Mock()
    monkeypatch.setattr("github_compliance_engine_api.api.routes.clone_repository", clone_repository)
    username = "review-user"
    password = "review-secret"
    repo_url = f"https://{username}:{password}@github.com/octocat/Hello-World"
    client = TestClient(create_app())

    response = client.post(
        "/api/analyze",
        json={"repo_url": repo_url},
    )

    assert response.status_code == 422
    response_text = response.text
    assert username not in response_text
    assert password not in response_text
    assert repo_url not in response_text
    assert "input" not in response.json()["detail"][0]
    assert "ctx" not in response.json()["detail"][0]
    clone_repository.assert_not_called()


@pytest.mark.parametrize(
    "repo_url",
    [
        "https://github.com:444/octocat/Hello-World",
        "https://github.com/octocat/Hello-World?decorated=value",
        "https://github.com/octocat/Hello-World#fragment",
    ],
)
def test_analyze_rejects_decorated_repo_urls(repo_url: str, monkeypatch) -> None:
    clone_repository = Mock()
    monkeypatch.setattr("github_compliance_engine_api.api.routes.clone_repository", clone_repository)
    client = TestClient(create_app())

    response = client.post("/api/analyze", json={"repo_url": repo_url})

    assert response.status_code == 422
    clone_repository.assert_not_called()


def test_analyze_maps_repository_unavailable_to_safe_error(tmp_path: Path, monkeypatch, caplog) -> None:
    unsafe_detail = "UNSAFE" + "_DETAIL"
    ingestion_error = RepositoryUnavailableError("Repository could not be cloned.")
    ingestion_error.__cause__ = RuntimeError(unsafe_detail)
    monkeypatch.setattr(
        "github_compliance_engine_api.api.routes.clone_repository",
        Mock(side_effect=ingestion_error),
    )
    extract_repo_metadata = Mock()
    monkeypatch.setattr("github_compliance_engine_api.api.routes.extract_repo_metadata", extract_repo_metadata)
    monkeypatch.setattr("github_compliance_engine_api.api.routes.get_settings", lambda: mock_ingestion_settings(tmp_path))
    client = TestClient(create_app())

    response = client.post(
        "/api/analyze",
        json={"repo_url": "https://github.com/octocat/Hello-World"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Repository could not be cloned."}
    assert "RepositoryUnavailableError" in [getattr(record, "error_type", "") for record in caplog.records]
    assert unsafe_detail not in caplog.text
    extract_repo_metadata.assert_not_called()


def test_analyze_maps_timeout_to_safe_error(tmp_path: Path, monkeypatch, caplog) -> None:
    unsafe_detail = "UNSAFE" + "_DETAIL"
    ingestion_error = CloneTimeoutError("Repository clone timed out.")
    ingestion_error.__cause__ = RuntimeError(unsafe_detail)
    monkeypatch.setattr(
        "github_compliance_engine_api.api.routes.clone_repository",
        Mock(side_effect=ingestion_error),
    )
    extract_repo_metadata = Mock()
    monkeypatch.setattr("github_compliance_engine_api.api.routes.extract_repo_metadata", extract_repo_metadata)
    monkeypatch.setattr("github_compliance_engine_api.api.routes.get_settings", lambda: mock_ingestion_settings(tmp_path))
    client = TestClient(create_app())

    response = client.post(
        "/api/analyze",
        json={"repo_url": "https://github.com/octocat/Hello-World"},
    )

    assert response.status_code == 504
    assert response.json() == {"detail": "Repository clone timed out."}
    assert "CloneTimeoutError" in [getattr(record, "error_type", "") for record in caplog.records]
    assert unsafe_detail not in caplog.text
    extract_repo_metadata.assert_not_called()


def test_analyze_maps_workspace_error_to_generic_message(tmp_path: Path, monkeypatch, caplog) -> None:
    unsafe_detail = "UNSAFE" + "_DETAIL"
    monkeypatch.setattr(
        "github_compliance_engine_api.api.routes.clone_repository",
        Mock(side_effect=WorkspaceError(f"raw filesystem path {unsafe_detail}")),
    )
    extract_repo_metadata = Mock()
    monkeypatch.setattr("github_compliance_engine_api.api.routes.extract_repo_metadata", extract_repo_metadata)
    monkeypatch.setattr("github_compliance_engine_api.api.routes.get_settings", lambda: mock_ingestion_settings(tmp_path))
    client = TestClient(create_app())

    response = client.post(
        "/api/analyze",
        json={"repo_url": "https://github.com/octocat/Hello-World"},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Analysis workspace could not be prepared."}
    assert "WorkspaceError" in [getattr(record, "error_type", "") for record in caplog.records]
    assert unsafe_detail not in caplog.text
    extract_repo_metadata.assert_not_called()


def test_analyze_maps_metadata_extraction_error_to_safe_error(tmp_path: Path, monkeypatch, caplog) -> None:
    unsafe_detail = "UNSAFE" + "_METADATA_DETAIL"

    def clone_success(request):
        return CloneResult(
            analysis_id=request.analysis_id,
            repo_url=str(request.repo_url),
            local_clone_path=tmp_path / request.analysis_id / "repo",
            clone_status="cloned",
        )

    metadata_error = MetadataExtractionError(f"raw filesystem path {unsafe_detail}")
    metadata_error.__cause__ = RuntimeError(unsafe_detail)
    monkeypatch.setattr("github_compliance_engine_api.api.routes.clone_repository", Mock(side_effect=clone_success))
    monkeypatch.setattr(
        "github_compliance_engine_api.api.routes.extract_repo_metadata",
        Mock(side_effect=metadata_error),
    )
    monkeypatch.setattr("github_compliance_engine_api.api.routes.get_settings", lambda: mock_ingestion_settings(tmp_path))
    client = TestClient(create_app())

    response = client.post(
        "/api/analyze",
        json={"repo_url": "https://github.com/octocat/Hello-World"},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Repository metadata could not be extracted."}
    assert "MetadataExtractionError" in [getattr(record, "error_type", "") for record in caplog.records]
    assert unsafe_detail not in caplog.text
