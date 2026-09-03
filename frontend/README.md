# Next.js Frontend

Next.js App Router scaffold for submitting GitHub repository URLs and rendering placeholder Golden Thread analysis results.

## Golden Thread

- Feature: `FEAT-SCAFFOLD-001`
- Business requirement: `BR-CORE-001`
- User requirements: `UR-USER-001`, `UR-USER-002`
- REST endpoints: `REST-ANALYZE-001`, `REST-RESULTS-001`
- Call flows: `CF-ANALYZE-001`, `CF-RESULTS-001`
- Test case: `TC-CORE-001`
- Verification: `V-CORE-001`

## Environment

```sh
NEXT_PUBLIC_BACKEND_BASE_URL=http://localhost:8000
```

## Local Development

Install dependencies:

```sh
npm install
```

Run the frontend:

```sh
npm run dev
```

Run validation:

```sh
npm run lint
npm run build
```

The app expects the Python backend scaffold to expose `POST /api/analyze` and `GET /api/analyze/{analysis_id}/results`.
