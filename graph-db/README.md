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

## Apply Init Scripts

Start the Neo4j service:

```sh
docker compose up neo4j
```

Apply constraints and indexes from another terminal:

```sh
cat graph-db/init/constraints.cypher | docker compose exec -T neo4j cypher-shell -u neo4j -p local-dev-password
cat graph-db/init/indexes.cypher | docker compose exec -T neo4j cypher-shell -u neo4j -p local-dev-password
```

The Cypher scripts use `IF NOT EXISTS` and are safe to rerun.

## Schema

See `schema/node-labels-and-relationships.md` for required labels, relationships, and index intent.
