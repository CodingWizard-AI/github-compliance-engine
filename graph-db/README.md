# Neo4j Graph Store

Neo4j stores the GitHub Compliance Engine lexical graph: code units, files, interfaces, inferred objectives, structural relationships, text-search indexes, and vector-search indexes.

## Golden Thread

- Feature: `FEAT-SCAFFOLD-001`
- Business requirement: `BR-CORE-001`
- Call flow: `CF-ANALYZE-GRAPH-001`
- Test case: `TC-CORE-001`
- Verification: `V-CORE-001`

## Docker Ports

- Neo4j Browser: `http://localhost:7474`
- Bolt driver: `bolt://localhost:7687`

## Environment

The root Compose file supplies these values:

```sh
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=local-dev-password
NEO4J_HTTP_PORT=7474
NEO4J_BOLT_PORT=7687
```

Do not commit real database credentials.

For graph-store Docker commands, export the full local configuration in the same terminal before running Compose:

```sh
export NEXT_PUBLIC_BACKEND_BASE_URL=http://localhost:8000
export FRONTEND_HOSTNAME=0.0.0.0
export FRONTEND_PORT=3000
export BACKEND_HOST=0.0.0.0
export BACKEND_PORT=8000
export BACKEND_CORS_ORIGINS=http://localhost:3000
export NEO4J_URI=bolt://neo4j:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=local-dev-password
export NEO4J_HTTP_PORT=7474
export NEO4J_BOLT_PORT=7687
```

## Docker Commands

Run these commands from the repository root in the same terminal where the configuration variables are exported.

`neo4j-init` is intentionally separate from the long-running `neo4j` service. Neo4j does not auto-run mounted Cypher files from a generic init directory, so the scaffold uses a one-shot service to wait for Bolt readiness, apply `constraints.cypher` and `indexes.cypher`, then exit. The backend depends on successful `neo4j-init` completion so application services start after the graph schema baseline exists.

Validate Compose interpolation and graph-store mounts:

```sh
docker compose config
```

Start only the graph store:

```sh
docker compose up -d neo4j
```

Start Neo4j and apply constraints/indexes through the one-shot init service:

```sh
docker compose up --build -d neo4j neo4j-init
```

Verify constraints:

```sh
docker compose exec -T neo4j /var/lib/neo4j/bin/cypher-shell \
  -u "$NEO4J_USER" \
  -p "$NEO4J_PASSWORD" \
  "SHOW CONSTRAINTS YIELD name RETURN collect(name) AS constraints;"
```

Verify indexes:

```sh
docker compose exec -T neo4j /var/lib/neo4j/bin/cypher-shell \
  -u "$NEO4J_USER" \
  -p "$NEO4J_PASSWORD" \
  "SHOW INDEXES YIELD name, type RETURN name, type ORDER BY name;"
```

Reset the local graph store volume:

```sh
docker compose down -v
```

## Apply Init Scripts

The root Compose stack runs a one-shot `neo4j-init` service that applies `constraints.cypher` and `indexes.cypher` after Neo4j accepts Bolt connections.

To apply the scripts manually instead, start the Neo4j service:

```sh
docker compose up neo4j
```

Apply constraints and indexes from another terminal:

```sh
cat graph-db/init/constraints.cypher | docker compose exec -T neo4j /var/lib/neo4j/bin/cypher-shell \
  -u "$NEO4J_USER" \
  -p "$NEO4J_PASSWORD"

cat graph-db/init/indexes.cypher | docker compose exec -T neo4j /var/lib/neo4j/bin/cypher-shell \
  -u "$NEO4J_USER" \
  -p "$NEO4J_PASSWORD"
```

The Cypher scripts use `IF NOT EXISTS` and are safe to rerun.

## Schema

See `schema/node-labels-and-relationships.md` for required labels, relationships, and index intent.
