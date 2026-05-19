# spec 08 §2. Cypher-compatible query subset
import re
from typing import Tuple, List, Dict, Any, Optional

def translate(cypher: str, params: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Any]]:
    if params is None:
        params = {}

    # 1. MATCH (a:A {prop: $val})-[:EDGE_TYPE]->(b:B) RETURN a, b [LIMIT N]
    match1 = re.match(r'^MATCH\s+\((?P<a>\w+):(?P<a_type>\w+)\s*\{\s*(?P<prop>\w+)\s*:\s*\$(?P<val>\w+)\s*\}\)-\[:(?P<e_type>\w+)\]->\((?P<b>\w+):(?P<b_type>\w+)\)\s+RETURN\s+\w+,\s*\w+(?:\s+LIMIT\s+(?P<limit>\d+))?$', cypher.strip())
    if match1:
        sql = """SELECT a.id AS a_id, a.type AS a_type, a.payload AS a_payload,
       b.id AS b_id, b.type AS b_type, b.payload AS b_payload
FROM edges e
JOIN nodes a ON a.id = e.from_node
JOIN nodes b ON b.id = e.to_node
WHERE e.type = ? AND a.type = ? AND json_extract(a.payload, '$.' || ?) = ? AND b.type = ?"""
        sql_params = [match1.group('e_type'), match1.group('a_type'), match1.group('prop'), params.get(match1.group('val')), match1.group('b_type')]
        if match1.group('limit'):
            sql += " LIMIT ?"
            sql_params.append(int(match1.group('limit')))
        return sql, sql_params

    # 2. MATCH (a:A)-[:EDGE_TYPE]->(b) RETURN a, b [LIMIT N]
    match2 = re.match(r'^MATCH\s+\((?P<a>\w+):(?P<a_type>\w+)\)-\[:(?P<e_type>\w+)\]->\((?P<b>\w+)\)\s+RETURN\s+\w+,\s*\w+(?:\s+LIMIT\s+(?P<limit>\d+))?$', cypher.strip())
    if match2:
        sql = """SELECT a.id AS a_id, a.type AS a_type, a.payload AS a_payload,
       b.id AS b_id, b.type AS b_type, b.payload AS b_payload
FROM edges e
JOIN nodes a ON a.id = e.from_node
JOIN nodes b ON b.id = e.to_node
WHERE e.type = ? AND a.type = ?"""
        sql_params = [match2.group('e_type'), match2.group('a_type')]
        if match2.group('limit'):
            sql += " LIMIT ?"
            sql_params.append(int(match2.group('limit')))
        return sql, sql_params

    # 3. MATCH (a)-[:EDGE_TYPE]->(b) RETURN a, b [LIMIT N]
    match3 = re.match(r'^MATCH\s+\((?P<a>\w+)\)-\[:(?P<e_type>\w+)\]->\((?P<b>\w+)\)\s+RETURN\s+\w+,\s*\w+(?:\s+LIMIT\s+(?P<limit>\d+))?$', cypher.strip())
    if match3:
        sql = """SELECT a.id AS a_id, a.type AS a_type, a.payload AS a_payload,
       b.id AS b_id, b.type AS b_type, b.payload AS b_payload
FROM edges e
JOIN nodes a ON a.id = e.from_node
JOIN nodes b ON b.id = e.to_node
WHERE e.type = ?"""
        sql_params = [match3.group('e_type')]
        if match3.group('limit'):
            sql += " LIMIT ?"
            sql_params.append(int(match3.group('limit')))
        return sql, sql_params

    # 4. MATCH (n:NodeType {prop: $val}) RETURN n [LIMIT N]
    match4 = re.match(r'^MATCH\s+\((?P<n>\w+):(?P<n_type>\w+)\s*\{\s*(?P<prop>\w+)\s*:\s*\$(?P<val>\w+)\s*\}\)\s+RETURN\s+\w+(?:\s+LIMIT\s+(?P<limit>\d+))?$', cypher.strip())
    if match4:
        sql = """SELECT id, type, payload FROM nodes
WHERE type = ? AND json_extract(payload, '$.' || ?) = ?"""
        sql_params = [match4.group('n_type'), match4.group('prop'), params.get(match4.group('val'))]
        if match4.group('limit'):
            sql += " LIMIT ?"
            sql_params.append(int(match4.group('limit')))
        return sql, sql_params

    # 5. MATCH (n:NodeType) RETURN n [LIMIT N]
    match5 = re.match(r'^MATCH\s+\((?P<n>\w+):(?P<n_type>\w+)\)\s+RETURN\s+\w+(?:\s+LIMIT\s+(?P<limit>\d+))?$', cypher.strip())
    if match5:
        sql = "SELECT id, type, payload FROM nodes WHERE type = ?"
        sql_params = [match5.group('n_type')]
        if match5.group('limit'):
            sql += " LIMIT ?"
            sql_params.append(int(match5.group('limit')))
        return sql, sql_params

    if "*" in cypher:
        raise NotImplementedError("variable-length path not supported")

    raise NotImplementedError(f"Cypher query not supported: {cypher}")
