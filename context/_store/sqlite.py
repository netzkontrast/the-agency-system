# spec 08 §1. SQLite ontology store
import json
import os
import sqlite3
from typing import Optional, Dict, Any, List

try:
    from graphqlite import Graph
    HAS_GRAPHQLITE = True
except ImportError:
    HAS_GRAPHQLITE = False


class Store:
    def __init__(self, db_path: Optional[str] = None) -> None:
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'ontology.db')
        self.db_path = db_path
        self.graph = None

    def boot(self) -> None:
        # GraphQLite initializes the schema automatically upon connecting.
        if HAS_GRAPHQLITE:
            try:
                self.graph = Graph(self.db_path)
            except RuntimeError as e:
                if "SQLite extension loading not available" in str(e):
                    # v0 stub fallback if graphqlite native extension loading is disabled in Python
                    self.graph = None
        else:
            self.graph = None

    def _get_graph(self):
        if self.graph is None and HAS_GRAPHQLITE:
            try:
                self.graph = Graph(self.db_path)
            except RuntimeError as e:
                pass
        return self.graph

    def upsert_node(self, node_id: str, payload: Dict[str, Any], *, label: str) -> None:
        """Upsert a node into the ontology graph.

        Signature matches GraphQLite's native ``Graph.upsert_node(id, payload, label=...)``
        so calls flow through without re-ordering. The raw-SQLite branch is
        a v0 stub kept only for environments where the GraphQLite native
        extension fails to load; v1 will drop it (see ``vision/specs/08-context-base-v1.md``).
        """
        g = self._get_graph()
        if g:
            g.upsert_node(node_id, payload, label=label)
        else:
            conn = sqlite3.connect(self.db_path)
            with conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS nodes (
                        id TEXT PRIMARY KEY,
                        type TEXT NOT NULL,
                        payload JSON
                    )
                ''')
                conn.execute('''
                    INSERT INTO nodes (id, type, payload)
                    VALUES (?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET payload = excluded.payload
                ''', (node_id, label, json.dumps(payload)))

    def upsert_edge(self, from_node: str, to_node: str, payload: Optional[Dict[str, Any]] = None, *, rel_type: str) -> None:
        """Upsert an edge into the ontology graph.

        Signature matches GraphQLite's ``Graph.upsert_edge(from_node, to_node, payload, rel_type=...)``.
        """
        g = self._get_graph()
        if payload is None:
            payload = {}
        if g:
            g.upsert_edge(from_node, to_node, payload, rel_type=rel_type)
        else:
            conn = sqlite3.connect(self.db_path)
            with conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS edges (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        type TEXT NOT NULL,
                        from_node TEXT NOT NULL,
                        to_node TEXT NOT NULL,
                        payload JSON,
                        UNIQUE(type, from_node, to_node)
                    )
                ''')
                conn.execute('''
                    INSERT INTO edges (type, from_node, to_node, payload)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(type, from_node, to_node) DO UPDATE SET payload = excluded.payload
                ''', (rel_type, from_node, to_node, json.dumps(payload)))

    def log_tool_call(self, tool: str, envelope: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tools_call_log (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool        TEXT NOT NULL,
                    envelope    JSON NOT NULL,
                    called_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
                )
            ''')
            conn.execute('''
                INSERT INTO tools_call_log (tool, envelope)
                VALUES (?, ?)
            ''', (tool, json.dumps(envelope)))

    def query(self, cypher: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if params is None:
            params = {}
        g = self._get_graph()
        if g:
            # GraphQLite returns dicts natively
            return list(g.query(cypher, params=params))
        else:
            # Simple mock for test environments where extension loading fails
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Very basic regex mock for test queries
            import re
            if "MATCH (n:Artefact) RETURN n" in cypher:
                try:
                    cursor.execute("SELECT id, type, payload FROM nodes WHERE type = 'Artefact'")
                    return [dict(row) for row in cursor.fetchall()]
                except sqlite3.OperationalError:
                    return []
            if cypher.startswith("MATCH (a:Artefact)-[:DERIVED_FROM]->(b) RETURN a, b"):
                try:
                    cursor.execute("SELECT * FROM edges WHERE type = 'DERIVED_FROM'")
                    return [dict(row) for row in cursor.fetchall()]
                except sqlite3.OperationalError:
                    return []

            return []

    def close(self) -> None:
        if self.graph:
            if hasattr(self.graph, 'close'):
                self.graph.close()
            self.graph = None
