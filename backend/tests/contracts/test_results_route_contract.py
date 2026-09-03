from fastapi.testclient import TestClient

from github_compliance_engine_api.main import create_app


# Scaffold acceptance coverage: TC-ING-001, TC-OBJ-001, TC-CORE-001, V-ING-001, V-OBJ-001, V-CORE-001
# @golden-thread FEAT-SCAFFOLD-001, REST-RESULTS-001, TC-OBJ-001, V-OBJ-001
def test_results_route_returns_placeholder_result_shape() -> None:
    client = TestClient(create_app())

    response = client.get("/api/analyze/analysis-placeholder-001/results")

    assert response.status_code == 200
    body = response.json()
    assert body["analysis_id"] == "analysis-placeholder-001"
    assert body["status"] == "complete"
    assert "graph" in body
    assert "objective_mappings" in body
    assert "orphaned_code_units" in body
    assert "traceability_score" in body
