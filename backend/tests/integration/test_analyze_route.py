from fastapi.testclient import TestClient

from github_compliance_engine_api.main import create_app


# Scaffold acceptance coverage: TC-ING-001, TC-OBJ-001, TC-CORE-001, V-ING-001, V-OBJ-001, V-CORE-001
# @golden-thread FEAT-SCAFFOLD-001, FR-ING-001, REST-ANALYZE-001, TC-ING-001, V-ING-001
def test_analyze_accepts_public_github_repo_url() -> None:
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


def test_analyze_rejects_invalid_repo_url() -> None:
    client = TestClient(create_app())

    response = client.post("/api/analyze", json={"repo_url": "not-a-url"})

    assert response.status_code == 422
