from pathlib import Path

import pytest

from github_compliance_engine_api.analysis_store import (
    GoldenThreadAnalysis,
    clear_analysis_store,
    get_analysis,
    save_analysis,
)
from github_compliance_engine_api.ingestion import CloneResult, FileTreeNode, RepoMetadata


@pytest.fixture(autouse=True)
def reset_analysis_store() -> None:
    clear_analysis_store()


# @golden-thread FEAT-ING-002, FR-ING-002, CF-ANALYZE-INGEST-001, TC-ING-002, V-ING-002
def test_analysis_store_saves_and_retrieves_analysis() -> None:
    metadata = RepoMetadata(file_tree=FileTreeNode(path=".", name=".", type="dir"))
    analysis = GoldenThreadAnalysis(
        analysis_id="analysis-001",
        repo_url="https://github.com/octocat/Hello-World",
        status="metadata_extracted",
        clone_result=CloneResult(
            analysis_id="analysis-001",
            repo_url="https://github.com/octocat/Hello-World",
            local_clone_path=Path("/tmp/github-compliance-engine/analyses/analysis-001/repo"),
            clone_status="cloned",
        ),
        repo_metadata=metadata,
    )

    save_analysis(analysis)

    stored_analysis = get_analysis("analysis-001")
    assert stored_analysis == analysis
    assert stored_analysis.repo_metadata == metadata


def test_analysis_store_returns_none_for_missing_analysis() -> None:
    assert get_analysis("analysis-missing") is None


def test_analysis_store_returns_copy() -> None:
    analysis = GoldenThreadAnalysis(
        analysis_id="analysis-001",
        repo_url="https://github.com/octocat/Hello-World",
        status="metadata_extracted",
        repo_metadata=RepoMetadata(),
    )
    save_analysis(analysis)

    stored_analysis = get_analysis("analysis-001")
    assert stored_analysis is not None
    stored_analysis.status = "failed"

    assert get_analysis("analysis-001").status == "metadata_extracted"
