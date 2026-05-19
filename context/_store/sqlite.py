# spec 08 §1. SQLite ontology store
import sqlite3
import json
import os
from typing import Optional, Dict, Any, List

from . import cypher_adapter

class Store:
    def __init__(self, db_path: Optional[str] = None) -> None:
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'ontology.db')
        self.db_path = db_path
        self.conn = None

    def _get_conn(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def boot(self) -> None:
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            schema = f.read()
        conn = self._get_conn()
        with conn:
            conn.executescript(schema)

    def upsert_node(self, node_id: str, node_type: str, payload: Dict[str, Any]) -> None:
        conn = self._get_conn()
        with conn:
            conn.execute('''
                INSERT INTO nodes (id, type, payload)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    payload = excluded.payload,
                    updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
            ''', (node_id, node_type, json.dumps(payload)))

    def upsert_edge(self, edge_type: str, from_node: str, to_node: str, payload: Optional[Dict[str, Any]] = None) -> int:
        conn = self._get_conn()
        payload_json = json.dumps(payload) if payload is not None else None
        with conn:
            cursor = conn.execute('''
                INSERT INTO edges (type, from_node, to_node, payload)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(type, from_node, to_node) DO UPDATE SET
                    payload = excluded.payload
            ''', (edge_type, from_node, to_node, payload_json))
            # If it was an update, lastrowid might be 0, so we need to select it
            if cursor.lastrowid:
                return cursor.lastrowid
            else:
                cursor = conn.execute('SELECT id FROM edges WHERE type = ? AND from_node = ? AND to_node = ?', (edge_type, from_node, to_node))
                return cursor.fetchone()['id']

    def log_tool_call(self, tool: str, envelope: Dict[str, Any]) -> None:
        conn = self._get_conn()
        with conn:
            conn.execute('''
                INSERT INTO tools_call_log (tool, envelope)
                VALUES (?, ?)
            ''', (tool, json.dumps(envelope)))

    def query(self, cypher: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        sql, sql_params = cypher_adapter.translate(cypher, params)
        conn = self._get_conn()
        cursor = conn.execute(sql, sql_params)

        results = []
        for row in cursor:
            d = dict(row)
            # Parse JSON payloads
            for k in list(d.keys()):
                if k.endswith('payload') and d[k] is not None:
                    try:
                        d[k] = json.loads(d[k])
                    except json.JSONDecodeError:
                        pass
            results.append(d)
        return results

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None
