from pathlib import Path

from github_compliance_engine_api.settings import Settings


# @golden-thread FEAT-ING-001, FR-ING-001, CF-ANALYZE-INGEST-001, TC-ING-001, V-ING-001
def test_ingestion_settings_use_safe_defaults() -> None:
    settings = Settings(NEO4J_PASSWORD="local-dev-password")

    assert settings.ingestion_workspace_root == Path("/tmp/github-compliance-engine/analyses")
    assert settings.ingestion_clone_depth == 1
    assert settings.ingestion_clone_timeout_seconds == 60
    assert settings.ingestion_metadata_timeout_seconds == 30
    assert settings.ingestion_file_tree_max_depth == 20
    assert settings.ingestion_file_tree_max_files == 5000
    assert settings.ingestion_max_text_file_bytes == 1048576
    assert settings.github_token is None


def test_ingestion_settings_accept_env_overrides(monkeypatch) -> None:
    monkeypatch.setenv("NEO4J_PASSWORD", "local-dev-password")
    monkeypatch.setenv("INGESTION_WORKSPACE_ROOT", "/tmp/custom-ingestion")
    monkeypatch.setenv("INGESTION_CLONE_DEPTH", "2")
    monkeypatch.setenv("INGESTION_CLONE_TIMEOUT_SECONDS", "30")
    monkeypatch.setenv("INGESTION_METADATA_TIMEOUT_SECONDS", "15")
    monkeypatch.setenv("INGESTION_FILE_TREE_MAX_DEPTH", "10")
    monkeypatch.setenv("INGESTION_FILE_TREE_MAX_FILES", "250")
    monkeypatch.setenv("INGESTION_MAX_TEXT_FILE_BYTES", "2048")
    monkeypatch.setenv("GITHUB_TOKEN", "local-token")

    settings = Settings()

    assert settings.ingestion_workspace_root == Path("/tmp/custom-ingestion")
    assert settings.ingestion_clone_depth == 2
    assert settings.ingestion_clone_timeout_seconds == 30
    assert settings.ingestion_metadata_timeout_seconds == 15
    assert settings.ingestion_file_tree_max_depth == 10
    assert settings.ingestion_file_tree_max_files == 250
    assert settings.ingestion_max_text_file_bytes == 2048
    assert settings.github_token == "local-token"


def test_empty_github_token_is_none(monkeypatch) -> None:
    monkeypatch.setenv("NEO4J_PASSWORD", "local-dev-password")
    monkeypatch.setenv("GITHUB_TOKEN", "")

    settings = Settings()

    assert settings.github_token is None
