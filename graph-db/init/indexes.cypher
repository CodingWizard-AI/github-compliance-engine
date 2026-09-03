// @golden-thread FEAT-SCAFFOLD-001, BR-CORE-001, CF-ANALYZE-GRAPH-001, TC-CORE-001, V-CORE-001

CREATE FULLTEXT INDEX code_text_fulltext IF NOT EXISTS
FOR (node:CodeUnit|File)
ON EACH [node.docstring, node.readme];

CREATE VECTOR INDEX codeunit_embedding_vector IF NOT EXISTS
FOR (node:CodeUnit)
ON (node.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};
