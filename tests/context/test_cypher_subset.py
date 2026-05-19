import pytest
from context._store import cypher_adapter

def test_cypher_single_hop_translates_to_sql():
    # Scenario: Cypher single-hop translates to SQL
    # Given the query `MATCH (a:Artefact)-[:DERIVED_FROM]->(b) RETURN a, b`
    query = "MATCH (a:Artefact)-[:DERIVED_FROM]->(b) RETURN a, b"

    # When `cypher_adapter.translate` runs
    sql, params = cypher_adapter.translate(query)

    # Then the emitted SQL joins `edges` with `nodes` twice
    assert "JOIN nodes a" in sql
    assert "JOIN nodes b" in sql

    # And the parameter list contains `["DERIVED_FROM", "Artefact"]`
    assert params == ["DERIVED_FROM", "Artefact"]

def test_unsupported_cypher_raises_clear_error():
    # Scenario: Unsupported Cypher raises a clear error
    # Given the query `MATCH (a)-[:E*1..3]->(b) RETURN a`
    query = "MATCH (a)-[:E*1..3]->(b) RETURN a"

    # When `cypher_adapter.translate` runs
    with pytest.raises(NotImplementedError) as excinfo:
        cypher_adapter.translate(query)

    # Then it raises `NotImplementedError` mentioning "variable-length path"
    assert "variable-length path" in str(excinfo.value)
