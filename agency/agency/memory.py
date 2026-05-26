"""Memory — the moat. One bi-temporal, append-only graph on real GraphQLite.

Every node (Intent, Invocation, Lifecycle, Agent, Artefact, Gate) and every edge
(SERVES, BY, PRODUCES, DISPATCHED_TO, PASSED, SUPERSEDED_BY) lives here. Reads go
through `project()` (ranked, budget-capped). Cross-concern provenance is a single
Cypher traversal from an Intent — the one thing a flat SDK+memory-tool stack
cannot answer in one hop.
"""
from __future__ import annotations

import threading
import uuid
from typing import Any, Optional

from graphqlite import Graph, connect

from . import ontology

OPEN = 10 ** 12  # sentinel valid_to for the currently-valid version


class Memory:
    def __init__(self, path: str, ont: Optional["ontology.Ontology"] = None):
        # Build the Graph with a thread-safe SQLite connection: FastMCP and the
        # code-mode (Monty) sandbox run tools in worker threads, and the seed is
        # logically single-threaded, so check_same_thread=False is safe here.
        self.g = Graph.__new__(Graph)
        self.g._conn = connect(str(path), check_same_thread=False)
        self.g.namespace = "default"
        # the EFFECTIVE ontology (core + capability extensions), injected by the
        # engine. A standalone Memory falls back to the bare core.
        self.ont = ont if ont is not None else ontology.Ontology.core()
        # the logical clock is shared across worker threads (check_same_thread=False);
        # serialize it, and seed it from persisted state so ticks stay monotonic
        # across reopens (the bash CLI opens a fresh Engine per call).
        self._lock = threading.Lock()
        self._tick = self._max_persisted_tick()

    def _max_persisted_tick(self) -> int:
        try:
            rows = self.g.query("MATCH (n) RETURN n")
        except Exception:
            return 0
        mx = 0
        for r in rows:
            p = r.get("n", {}).get("properties", {})
            for k in ("vfrom", "vto"):
                v = p.get(k, 0)
                if isinstance(v, int) and v != OPEN and v > mx:
                    mx = v
        return mx

    def _now(self) -> int:
        with self._lock:
            self._tick += 1
            return self._tick

    # --- write axis: record · link · supersede -------------------------------
    def record(self, label: str, props: dict[str, Any], node_id: Optional[str] = None) -> str:
        bad = self.ont.violations(label, props)
        if bad:
            raise ValueError(f"{label} record violates ontology: {bad}")
        nid = node_id or f"{label.lower()}:{uuid.uuid4().hex[:8]}"
        data = {**props, "vfrom": self._now(), "vto": OPEN}
        self.g.upsert_node(nid, data, label=label)
        return nid

    def link(self, src: str, dst: str, rel: str, props: Optional[dict] = None) -> None:
        if not self.ont.is_known_edge(rel):
            raise ValueError(f"unknown edge type {rel!r}; not in the effective ontology's edge set")
        self.g.upsert_edge(src, dst, {**(props or {}), "vfrom": self._now()}, rel_type=rel)

    def update(self, node_id: str, changes: dict[str, Any]) -> None:
        """In-place mutation (keeps id + edges stable). For mutable state like a
        Lifecycle's current phase; use `supersede` for append-only entities."""
        node = self.g.get_node(node_id)
        if node is None:
            raise KeyError(node_id)
        label = node["labels"][0] if node.get("labels") else "Entity"
        merged = {**node["properties"], **changes}
        bad = self.ont.violations(label, {k: v for k, v in merged.items()
                                          if k not in ("vfrom", "vto", "id")})
        if bad:
            raise ValueError(f"{label} update violates ontology: {bad}")
        self.g.upsert_node(node_id, merged, label=label)

    def supersede(self, node_id: str, changes: dict[str, Any]) -> str:
        node = self.g.get_node(node_id)
        if node is None:
            raise KeyError(node_id)
        old = dict(node["properties"])
        label = node["labels"][0] if node.get("labels") else "Entity"
        now = self._now()
        # close the old version (append-only: it keeps its valid window)
        self.g.upsert_node(node_id, {**old, "vto": now}, label=label)
        new_id = f"{node_id}#{now}"
        new_props = {k: v for k, v in old.items() if k not in ("vfrom", "vto", "id")}
        new_props.update(changes)
        bad = self.ont.violations(label, new_props)            # supersede stays strict too
        if bad:
            raise ValueError(f"{label} supersede violates ontology: {bad}")
        new_props.update({"vfrom": now, "vto": OPEN})
        self.g.upsert_node(new_id, new_props, label=label)
        self.link(node_id, new_id, "SUPERSEDED_BY")
        return new_id

    # --- read axis: recall · find · validate ---------------------------------
    def recall(self, node_id: str, as_of: Optional[int] = None) -> Optional[dict]:
        node = self.g.get_node(node_id)
        if node is None:
            return None
        props = node["properties"]
        if as_of is not None and not (props["vfrom"] <= as_of < props["vto"]):
            return None
        return props

    def find(self, label: str, as_of: Optional[int] = None) -> list[dict]:
        rows = self.g.query(f"MATCH (n:{label}) RETURN n")
        out = []
        for r in rows:
            p = r["n"]["properties"]
            if as_of is None:
                if p["vto"] == OPEN:
                    out.append(p)
            elif p["vfrom"] <= as_of < p["vto"]:
                out.append(p)
        return out

    def validate(self, node_id: str, predicate) -> bool:
        props = self.recall(node_id)
        return bool(props) and bool(predicate(props))

    def validate_schema(self, node_id: str, schema_id: str) -> bool:
        """Check a node against a Schema node's `required` fields (comma-joined).
        The typed layer: a Schema powers `validate`; pairs with a Template that
        powers `act` (generate). Both are ordinary nodes in the one graph."""
        node = self.recall(node_id)
        schema = self.recall(schema_id)
        if not node or not schema:
            return False
        required = [f.strip() for f in str(schema.get("required", "")).split(",") if f.strip()]
        return all(node.get(f) not in (None, "") for f in required)

    def project(self, label: str, budget: int, as_of: Optional[int] = None) -> list[dict]:
        """Ranked, budget-capped deltas — never raw history. Recency rank here."""
        rows = self.find(label, as_of=as_of)
        rows.sort(key=lambda p: p["vfrom"], reverse=True)
        return rows[:budget]

    # --- the moat: cross-concern provenance in one traversal -----------------
    def provenance(self, intent_id: str) -> dict[str, list[dict]]:
        def q(cypher: str) -> list[dict]:
            return self.g.query(cypher, {"iid": intent_id})

        serves = [r["x"]["properties"]
                  for r in q("MATCH (i:Intent)<-[:SERVES]-(x) WHERE i.id = $iid RETURN x")]
        agents = [r["a"]["properties"]
                  for r in q("MATCH (i:Intent)<-[:SERVES]-(x)-[:PERFORMED_BY]->(a:Agent) "
                             "WHERE i.id = $iid RETURN DISTINCT a")]
        artefacts = [r["p"]["properties"]
                     for r in q("MATCH (i:Intent)<-[:SERVES]-(x)-[:PRODUCES]->(p:Artefact) "
                                "WHERE i.id = $iid RETURN p")]
        gates = [r["g"]["properties"]
                 for r in q("MATCH (i:Intent)<-[:SERVES]-(:Lifecycle)-[:PASSED]->(g:Gate) "
                            "WHERE i.id = $iid RETURN g")]
        return {"serves": serves, "agents": agents, "artefacts": artefacts, "gates": gates}

    def close(self) -> None:
        self.g.close()
