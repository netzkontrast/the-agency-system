# spec 08 §4. PostToolUse hook
import json
import os
import jsonschema
from typing import Dict, Any

from .._store.sqlite import Store

def ingest(tool_name: str, envelope: Dict[str, Any]) -> None:
    store = Store()
    store.boot()
    store.log_tool_call(tool_name, envelope)

    if not envelope.get("ok"):
        return

    data = envelope.get("data", {})
    artefact_ref = data.get("artefact_ref")

    if artefact_ref:
        if os.path.exists(artefact_ref):
             with open(artefact_ref, 'r') as f:
                 sidecar = json.load(f)

             schema_path = os.path.join(os.path.dirname(__file__), '..', '_shared', 'schemas', 'sidecar.schema.json')
             is_valid = False
             if os.path.exists(schema_path):
                 with open(schema_path, 'r') as f:
                     schema = json.load(f)
                 try:
                     jsonschema.validate(instance=sidecar, schema=schema)
                     is_valid = True
                 except jsonschema.ValidationError:
                     pass

             if is_valid:
                 row = "unknown"
                 produced_by = sidecar.get("produced_by", {})
                 skill = produced_by.get("skill", "")
                 if "-" in skill:
                     row = skill.split("-")[0]
                 elif "/" in artefact_ref:
                     parts = artefact_ref.split("/")
                     if "result" in parts:
                         idx = parts.index("result")
                         if idx + 1 < len(parts):
                             row = parts[idx + 1]

                 sha256 = sidecar.get("sha256", "")
                 node_id = f"{row}/Artefact/{sha256}"

                 store.upsert_node(node_id, "Artefact", sidecar)

                 for entry in sidecar.get("derived_from", []):
                     store.upsert_edge("DERIVED_FROM", node_id, entry)

                 satisfies_phase = sidecar.get("satisfies_phase")
                 if satisfies_phase:
                     store.upsert_edge("SATISFIES_PHASE", node_id, f"phase:{row}/{satisfies_phase}")

    emitted_edges = data.get("emitted_edges")
    if emitted_edges and isinstance(emitted_edges, list):
        for edge in emitted_edges:
            if isinstance(edge, dict):
                 type_ = edge.get("type")
                 from_node = edge.get("from")
                 to_node = edge.get("to")
                 if type_ and from_node and to_node:
                     store.upsert_edge(type_, from_node, to_node)
