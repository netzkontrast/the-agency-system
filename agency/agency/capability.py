"""Capability — the craft (the open concept). Verbs are capability-defined and
role-tagged: act (craft write) · transform (stateless compute) · effect
(external side-effect). Invoking a capability records an Invocation in Memory,
edged SERVES->intent (and BY->agent / PRODUCES->artefact when relevant).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from .memory import Memory


@dataclass
class Capability:
    name: str
    home: str                       # which concept it primarily is
    verbs: dict[str, dict]          # verb -> {"role": str, "fn": callable}

    def role(self, verb: str) -> str:
        return self.verbs[verb]["role"]


class Registry:
    def __init__(self) -> None:
        self._caps: dict[str, Capability] = {}

    def register(self, cap: Capability) -> None:
        self._caps[cap.name] = cap

    def get(self, name: str) -> Capability:
        return self._caps[name]

    def names(self) -> list[str]:
        return sorted(self._caps)

    def invoke(self, memory: Memory, intent_id: str, cap_name: str, verb: str,
               agent_id: Optional[str] = None, **args) -> tuple[Any, str]:
        cap = self._caps[cap_name]
        spec = cap.verbs[verb]
        result = spec["fn"](**args)
        inv = memory.record("Invocation", {
            "capability": cap_name, "verb": verb, "role": spec["role"],
        })
        memory.link(inv, intent_id, "SERVES")
        if agent_id:
            memory.link(inv, agent_id, "PERFORMED_BY")  # 'BY' is a Cypher reserved word
        if isinstance(result, dict) and result.get("artefact"):
            art = memory.record("Artefact", dict(result["artefact"]))
            memory.link(inv, art, "PRODUCES")
        return result, inv
