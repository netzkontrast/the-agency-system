# spec 08 §4. PostToolUse hook
import json
import os
import jsonschema
from typing import Dict, Any

from .._store.sqlite import Store
from .._drivers.fs import FSArtefactDriver

def ingest(tool_name: str, envelope: Dict[str, Any]) -> None:
    store = Store()
    store.boot()
    store.log_tool_call(tool_name, envelope)

    if not envelope.get("ok"):
        return

    data = envelope.get("data", {})
    artefact_metadata = data.get("artefact_metadata") # Artefact metadata inline

    if artefact_metadata and isinstance(artefact_metadata, dict):
        schema_path = os.path.join(os.path.dirname(__file__), '..', '_shared', 'schemas', 'artefact-node.schema.json')
        is_valid = False
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema = json.load(f)
            try:
                jsonschema.validate(instance=artefact_metadata, schema=schema)
                is_valid = True
            except jsonschema.ValidationError:
                pass

        if is_valid:
            row = "unknown"
            produced_by = artefact_metadata.get("produced_by", {})
            skill = produced_by.get("skill", "")
            if "-" in skill:
                row = skill.split("-")[0]
            elif "artefact_path" in artefact_metadata:
                path = artefact_metadata["artefact_path"]
                if "/" in path:
                    parts = path.split("/")
                    if "result" in parts:
                        idx = parts.index("result")
                        if idx + 1 < len(parts):
                            row = parts[idx + 1]

            sha256 = artefact_metadata.get("sha256", "")
            node_id = f"{row}/Artefact/{sha256}"

            store.upsert_node(node_id, artefact_metadata, label="Artefact")

            # Wire up FSArtefactDriver
            # The driver checks if bytes are there if needed
            driver = FSArtefactDriver()
            if "artefact_path" in artefact_metadata and "raw_bytes" in artefact_metadata:
                 driver.put_bytes(artefact_metadata, artefact_metadata["raw_bytes"])
                 del artefact_metadata["raw_bytes"] # Remove from metadata payload

            for entry in artefact_metadata.get("derived_from", []):
                # GraphQLite silently drops edges whose target node does
                # not yet exist (it falls back to a self-loop). Upsert a
                # placeholder ExternalRef so the edge lands intact; the
                # placeholder is overwritten in-place once the real node
                # is ingested through its own channel.
                _ensure_node(store, entry, label="ExternalRef")
                store.upsert_edge(node_id, entry, rel_type="DERIVED_FROM")

            satisfies_phase = artefact_metadata.get("satisfies_phase")
            if satisfies_phase:
                target = f"phase:{row}/{satisfies_phase}"
                _ensure_node(store, target, label="Phase")
                store.upsert_edge(node_id, target, rel_type="SATISFIES_PHASE")

    emitted_edges = data.get("emitted_edges")
    if emitted_edges and isinstance(emitted_edges, list):
        for edge in emitted_edges:
            if isinstance(edge, dict):
                 type_ = edge.get("type")
                 from_node = edge.get("from")
                 to_node = edge.get("to")
                 if type_ and from_node and to_node:
                     # Same placeholder-target rule as above — emitted_edges
                     # references nodes by id, and GraphQLite needs both
                     # endpoints to exist before the edge will land.
                     _ensure_node(store, from_node, label="ExternalRef")
                     _ensure_node(store, to_node, label="ExternalRef")
                     store.upsert_edge(from_node, to_node, rel_type=type_)


def _ensure_node(store, node_id: str, *, label: str) -> None:
    """Upsert an empty placeholder if no node with this id exists yet.

    Idempotent: the GraphQLite ``upsert_node`` is a write-or-replace,
    so calling this on an already-ingested node overwrites the payload
    with ``{}``. To avoid clobbering, we probe first via a Cypher
    lookup and only upsert when the node is absent.
    """
    rows = store.query(
        "MATCH (n {id: $id}) RETURN n",
        params={"id": node_id},
    )
    if rows:
        return
    store.upsert_node(node_id, {"id": node_id}, label=label)
