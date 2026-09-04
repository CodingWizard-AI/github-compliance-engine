from github_compliance_engine_api.ingestion.contracts import (
    MetadataExtractionError,
    MetadataExtractionRequest,
    RepoMetadata,
)


CLONE_PATH_UNAVAILABLE_MESSAGE = "Repository metadata could not be extracted from the clone workspace."


# @golden-thread FEAT-ING-002, FR-ING-002, CF-ANALYZE-INGEST-001, TC-ING-002, V-ING-002
def extract_repo_metadata(request: MetadataExtractionRequest) -> RepoMetadata:
    try:
        clone_path_exists = request.local_clone_path.exists()
        clone_path_is_dir = request.local_clone_path.is_dir()
    except OSError as exc:
        raise MetadataExtractionError(CLONE_PATH_UNAVAILABLE_MESSAGE) from exc

    if not clone_path_exists or not clone_path_is_dir:
        raise MetadataExtractionError(CLONE_PATH_UNAVAILABLE_MESSAGE)

    return RepoMetadata()
