# Coding Agent Reference Index: Notion Golden Thread

This index points implementation agents to the active Notion registries used by the GitHub Compliance Engine Golden Thread mapping.

## Root Trace

- Feature: `FEAT-SCAFFOLD-001`
- Business requirement: `BR-CORE-001`
- User requirements: `UR-USER-001`, `UR-USER-002`
- Functional requirements: `FR-ING-001`, `FR-OBJ-001`
- Test cases: `TC-ING-001`, `TC-OBJ-001`, `TC-CORE-001`
- Verifications: `V-ING-001`, `V-OBJ-001`, `V-CORE-001`

## Active Notion Database Mapping

| Prefix | Database | ID |
| --- | --- | --- |
| `BR` | Business Requirements | `49a94bf8-d508-8245-8003-011237bcc220` |
| `UR` | User Requirements | `7c494bf8-d508-82a9-b052-81082a95ca3f` |
| `FR` | Functional Requirements | `c1294bf8-d508-8238-ac98-81e7f433a2c1` |
| `TSR` | Technical & System Requirements | `b2f94bf8-d508-8313-8d2d-019b04ee5734` |
| `NFR` | Non-Functional Requirements | `14f94bf8-d508-8319-bdb3-814b98b9309e` |
| `TCR` | Transitional & Compliance Requirements | `7fa94bf8-d508-838c-b8e0-8123efa13f9c` |
| `FEAT` | Feature Registry | `e3c94bf8-d508-8264-bc9d-81a9ee014a16` |
| `IF` | Interface Registry | `e1d94bf8-d508-8393-a520-81280aea811a` |
| `CF` | Call Flow Registry | `f1b94bf8-d508-83cf-a592-8173ad7791ee` |
| `TC` | Test Case Registry | `93694bf8-d508-8294-ae22-81e8be266e47` |
| `V` | Verification Matrix | `e8e94bf8-d508-834c-8104-019a31391058` |
| `EA` | Evidence Artifact Registry | `60794bf8-d508-82d1-9471-01955334352a` |
| `REST` | REST Endpoints | `aed94bf8-d508-836f-bb09-01af55b2c928` |
| `SERVICES` | Services Matrix | `d9d94bf8-d508-827c-ae6f-81c297afc79e` |
| `DB` | Database Components | `3cf94bf8-d508-8035-8409-d9b764e3fddf` |

## Intentional Gaps

- `RPC` is intentionally blank: gRPC methods are not part of the current active matrix.
- `GQL` is intentionally blank: GraphQL operations are not part of the current active matrix.
- `EVT` is not configured for this scaffold: event registries are not part of the current active matrix.

## Agent Usage

Use `.golden-thread.config.yaml` as the local source of truth for database IDs. Use `.golden-thread/manifest.yaml` for the root scaffold trace and each future service manifest for layer-specific traceability.
