# Neo4j Graph Schema

This schema supports `CF-ANALYZE-GRAPH-001`: building a structural and lexical graph for analyzed public GitHub repositories.

## Golden Thread

- Feature: `FEAT-SCAFFOLD-001`
- Business requirement: `BR-CORE-001`
- Call flow: `CF-ANALYZE-GRAPH-001`
- Test case: `TC-CORE-001`
- Verification: `V-CORE-001`

## Node Labels

| Label | Purpose | Minimal properties |
| --- | --- | --- |
| `CodeUnit` | Function, class, method, component, module, or other parsed code unit. | `id`, `name`, `kind`, `path`, `language`, `start_line`, `end_line`, `docstring`, `embedding` |
| `File` | Repository file containing code, docs, or configuration. | `path`, `language`, `readme`, `size_bytes` |
| `Interface` | Externally-facing REST route, CLI command, UI entry, webhook, or comparable boundary. | `id`, `name`, `type`, `path`, `method`, `public` |
| `Objective` | Inferred business objective anchored to public interfaces. | `id`, `name`, `description`, `confidence` |

## Relationships

| Relationship | Direction | Purpose | Minimal properties |
| --- | --- | --- | --- |
| `IMPORTS` | `CodeUnit -> CodeUnit` or `File -> File` | Captures import/module dependency edges. | `source`, `confidence` |
| `CALLS` | `CodeUnit -> CodeUnit` or `Interface -> CodeUnit` | Captures call and route handler flow. | `source`, `confidence` |
| `EXTENDS` | `CodeUnit -> CodeUnit` | Captures inheritance, implementation, and extension relationships. | `source`, `confidence` |
| `MENTIONS` | `File -> CodeUnit` or `CodeUnit -> Objective` | Captures textual references from docs, README content, comments, or code. | `source`, `confidence` |
| `SERVES_OBJECTIVE` | `CodeUnit -> Objective` or `Interface -> Objective` | Connects code and public interfaces to inferred business objectives. | `source`, `confidence` |

## Indexes

- Unique constraints: `CodeUnit.id`, `File.path`, `Interface.id`, `Objective.id`.
- Lookup indexes: `CodeUnit.name`, `Interface.name`, `Objective.name`.
- Full-text index: `CodeUnit.docstring` and `File.readme`.
- Vector index: `CodeUnit.embedding` for semantic retrieval.

## Runtime Data

Runtime data is local state and must not be committed. The repository ignores `neo4j-data/`, `graph-db/data/`, `graph-db/logs/`, `graph-db/import/`, and `graph-db/plugins/`.
