from pathlib import Path

from github_compliance_engine_api.settings import Settings


# @golden-thread FEAT-ING-001, FR-ING-001, CF-ANALYZE-INGEST-001, TC-ING-001, V-ING-001
def test_ingestion_settings_use_safe_defaults() -> None:
    settings = Settings(NEO4J_PASSWORD="local-dev-password")

    assert settings.ingestion_workspace_root == Path("/tmp/github-compliance-engine/analyses")
    assert settings.ingestion_clone_depth == 1
    assert settings.ingestion_clone_timeout_seconds == 60


def test_ingestion_settings_accept_env_overrides(monkeypatch) -> None:
    monkeypatch.setenv("NEO4J_PASSWORD", "local-dev-password")
    monkeypatch.setenv("INGESTION_WORKSPACE_ROOT", "/tmp/custom-ingestion")
    monkeypatch.setenv("INGESTION_CLONE_DEPTH", "2")
    monkeypatch.setenv("INGESTION_CLONE_TIMEOUT_SECONDS", "30")

    settings = Settings()

    assert settings.ingestion_workspace_root == Path("/tmp/custom-ingestion")
    assert settings.ingestion_clone_depth == 2
    assert settings.ingestion_clone_timeout_seconds == 30
