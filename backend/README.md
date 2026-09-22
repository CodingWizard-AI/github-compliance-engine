# Python Analysis Backend

FastAPI backend for the GitHub Compliance Engine analysis service.

## Golden Thread

- Features: `FEAT-SCAFFOLD-001`, `FEAT-ING-001`, `FEAT-ING-002`
- Business requirement: `BR-CORE-001`
- Functional requirements: `FR-ING-001`, `FR-ING-002`, `FR-OBJ-001`
- REST endpoints: `REST-ANALYZE-001`, `REST-RESULTS-001`
- Call flow: `CF-ANALYZE-INGEST-001`
- Test cases: `TC-ING-001`, `TC-ING-002`, `TC-OBJ-001`
- Verifications: `V-ING-001`, `V-ING-002`, `V-OBJ-001`

## Environment

```sh
BACKEND_CORS_ORIGINS=http://localhost:3000
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
INGESTION_WORKSPACE_ROOT=/tmp/github-compliance-engine/analyses
INGESTION_CLONE_DEPTH=1
INGESTION_CLONE_TIMEOUT_SECONDS=60
INGESTION_METADATA_TIMEOUT_SECONDS=30
INGESTION_FILE_TREE_MAX_DEPTH=20
INGESTION_FILE_TREE_MAX_FILES=5000
INGESTION_MAX_TEXT_FILE_BYTES=1048576
GITHUB_TOKEN=
GIT_PYTHON_GIT_EXECUTABLE=/usr/bin/git
```

The ingestion runtime uses an ephemeral per-analysis workspace under
`INGESTION_WORKSPACE_ROOT`. `POST /api/analyze` performs a real shallow clone
with `INGESTION_CLONE_DEPTH` and stops clone execution after
`INGESTION_CLONE_TIMEOUT_SECONDS`. Docker sets
`GIT_PYTHON_GIT_EXECUTABLE=/usr/bin/git` because GitPython requires a `git`
binary at import time.

`FEAT-ING-002` synchronously extracts a root README, bounded file tree, language
mix, supported manifests, and framework/ruleset hints after cloning. The tree
respects root `.gitignore` rules and fallback exclusions. Extraction time, tree
depth, file count, and text reads are bounded by the settings above. Nonfatal
failures are retained as safe structured warnings on the in-memory analysis.

The GitHub Languages API is preferred for language byte counts. `GITHUB_TOKEN`
is optional and should stay empty for unauthenticated local development; API
failures fall back to deterministic file-extension detection. MongoDB Atlas is
the planned persistence platform, but this feature adds no database driver,
connection requirement, or durable writes.

## Local Development

Install the backend with test dependencies:

```sh
python -m pip install -e ".[dev]"
```

Run the API:

```sh
python -m uvicorn github_compliance_engine_api.main:create_app --factory --reload --host 0.0.0.0 --port 8000
```

Run tests:

```sh
python -m pytest
```

## Route Contracts

`POST /api/analyze` accepts only HTTPS GitHub repository URLs shaped as
`https://github.com/{owner}/{repo}`. A successful request performs a shallow
clone and metadata extraction, stores the result in process memory, and returns
the unchanged `analysis_id`, `status="accepted"`, `repo_url`, and
`clone_status="cloned"` fields.

Malformed URLs, non-GitHub hosts, non-HTTPS URLs, and missing owner/repo paths
return FastAPI validation errors. Private, missing, unreachable, or timed-out
repositories return safe API errors without raw Git output, local filesystem
paths, stack traces, or credentials.

`GET /api/analyze/{analysis_id}/results` returns a deterministic placeholder result shape for graph, objective mapping, orphan detection, and traceability score consumers.

## Ingestion Verification

Default tests mock GitPython so the suite does not require network access:

```sh
python -m pytest
```

Optional live verification can be run with the stack started and network access
available:

```sh
curl -s -X POST http://localhost:8000/api/analyze \
  -H 'Content-Type: application/json' \
  -d '{"repo_url":"https://github.com/octocat/Hello-World"}'
```

The response should include `clone_status="cloned"`. Local workspaces are
temporary analysis inputs; do not commit `.env`, cloned repositories, tokens, or
runtime workspace contents.

PR acceptance coverage: `FEAT-ING-001`, `FEAT-ING-002`, `BR-CORE-001`,
`UR-USER-001`, `FR-ING-001`, `FR-ING-002`, `REST-ANALYZE-001`,
`CF-ANALYZE-INGEST-001`, `TC-ING-001`, `TC-ING-002`, `V-ING-001`, and
`V-ING-002`.
