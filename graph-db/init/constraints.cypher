// @golden-thread FEAT-SCAFFOLD-001, BR-CORE-001, CF-ANALYZE-GRAPH-001, TC-CORE-001, V-CORE-001

CREATE CONSTRAINT codeunit_id_unique IF NOT EXISTS
FOR (node:CodeUnit)
REQUIRE node.id IS UNIQUE;

CREATE CONSTRAINT file_path_unique IF NOT EXISTS
FOR (node:File)
REQUIRE node.path IS UNIQUE;

CREATE CONSTRAINT interface_id_unique IF NOT EXISTS
FOR (node:Interface)
REQUIRE node.id IS UNIQUE;

CREATE CONSTRAINT objective_id_unique IF NOT EXISTS
FOR (node:Objective)
REQUIRE node.id IS UNIQUE;

CREATE INDEX codeunit_name_index IF NOT EXISTS
FOR (node:CodeUnit)
ON (node.name);

CREATE INDEX interface_name_index IF NOT EXISTS
FOR (node:Interface)
ON (node.name);

CREATE INDEX objective_name_index IF NOT EXISTS
FOR (node:Objective)
ON (node.name);
