"""reflect — durable cross-session memory (the `reflect` cluster from the panel,
ported as a CONCEPT from the private-journal plugin).

Scope-tagged insight nodes written into the one graph, with recency + keyword
retrieval. This capability is the demonstration that **adding a capability is
adding a file**: it self-registers (reflection), it OWNS its ontology fragment (a
`Reflection` node type + a closed `scope` enum + the `OBSERVED_DURING` edge), and
the engine INJECTS `memory`/`intent_id` so its verbs can read/write the graph.
"""
from __future__ import annotations

from ..capability import Capability
from ..ontology import OntologyExtension

REFLECT_SCOPES = {"observation", "reflection", "project", "technical", "user", "world"}


def note(scope: str, text: str, memory=None, intent_id=None) -> dict:
    "Write a scope-tagged insight node (act); edged OBSERVED_DURING the intent."
    rid = memory.record("Reflection", {"scope": scope, "text": text})
    memory.link(rid, intent_id, "OBSERVED_DURING")
    return {"result": rid}


def recall(memory=None, scope: str = "") -> dict:
    "Retrieve reflections (transform), newest first, optionally filtered by scope."
    rows = sorted(memory.find("Reflection"), key=lambda p: p["vfrom"], reverse=True)
    out = [{"scope": r["scope"], "text": r["text"]}
           for r in rows if not scope or r.get("scope") == scope]
    return {"result": out}


def search(query: str, memory=None) -> dict:
    "Keyword search over reflection text (transform); deterministic substring match."
    q = (query or "").lower()
    out = [{"scope": r["scope"], "text": r["text"]}
           for r in memory.find("Reflection") if q in r["text"].lower()]
    return {"result": out}


reflect_ontology = OntologyExtension(
    nodes={"Reflection": ["scope", "text"]},
    enums={("Reflection", "scope"): REFLECT_SCOPES},
    edges={"OBSERVED_DURING", "INFORMS"},
)

reflect_capability = Capability(
    name="reflect",
    home="memory",
    verbs={
        "note":   {"role": "act", "fn": note, "inject": ["memory", "intent_id"]},
        "recall": {"role": "transform", "fn": recall, "inject": ["memory"]},
        "search": {"role": "transform", "fn": search, "inject": ["memory"]},
    },
    ontology=reflect_ontology,
)
