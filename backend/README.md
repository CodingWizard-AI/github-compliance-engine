# Python Analysis Backend

FastAPI scaffold for the GitHub Compliance Engine analysis service.

## Golden Thread

- Feature: `FEAT-SCAFFOLD-001`
- Business requirement: `BR-CORE-001`
- Functional requirements: `FR-ING-001`, `FR-OBJ-001`
- REST endpoints: `REST-ANALYZE-001`, `REST-RESULTS-001`
- Test cases: `TC-ING-001`, `TC-OBJ-001`
- Verifications: `V-ING-001`, `V-OBJ-001`

## Environment

```sh
BACKEND_CORS_ORIGINS=http://localhost:3000
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=local-dev-password
```

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

`POST /api/analyze` accepts a public GitHub repository URL and returns a deterministic placeholder analysis ID until the real ingestion pipeline is implemented.

`GET /api/analyze/{analysis_id}/results` returns a deterministic placeholder result shape for graph, objective mapping, orphan detection, and traceability score consumers.
