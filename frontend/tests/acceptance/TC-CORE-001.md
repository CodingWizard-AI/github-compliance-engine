# TC-CORE-001 Acceptance Placeholder

<!-- @golden-thread FEAT-SCAFFOLD-001, BR-CORE-001, UR-USER-001, UR-USER-002, TC-CORE-001, V-CORE-001 -->

## Scenario

End-to-end POC journey: submit a public GitHub repository URL, run the analysis pipeline, and review the Golden Thread traceability report.

## Steps

1. Start the local stack with Docker Compose after frontend, backend, and graph-db scaffolds are available.
2. Open the frontend at `http://localhost:3000`.
3. Submit `https://github.com/octocat/Hello-World`.
4. Confirm the frontend displays an accepted analysis ID.
5. Confirm the frontend renders graph nodes, graph edges, objective mappings, orphaned code units, and traceability score from the backend response.

## Expected Result

A first-time user can complete the full journey unaided and review a coherent placeholder Golden Thread report.
