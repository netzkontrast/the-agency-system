"""Strict, EXTENSIBLE ontology for the agency graph.

The **core** defines the irreducible base: every node type's required-field
schema, the enumerated edge set, and the closed enums. But the core is not
closed — **each capability extends it** with its own node types, edges, enums,
skill schemas, and template-schemas (`Capability.ontology`, an
`OntologyExtension`). The engine merges every discovered extension onto the core
into one effective `Ontology` (strictly: an extension may not redefine a core
node with different fields), and injects it into `Memory`, which enforces it on
`record`/`link`/`update` — so the graph cannot drift and capability schemata are
owned by the capability, not hard-wired centrally.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# --- the CORE: base node types (label -> strict required fields) ------------
NODE_SCHEMAS: dict[str, list[str]] = {
    "Intent":     ["purpose", "deliverable", "acceptance", "status"],
    "Invocation": ["capability", "verb", "role"],
    "Lifecycle":  ["state", "phase"],
    "Agent":      ["runtime"],
    "Gate":       ["name", "passed"],
    "Artefact":   ["kind"],
    "Schema":     ["name", "required"],
    "Template":   ["name", "body"],
    # micro-step skills & tools (generic):
    "Skill":      ["name", "kind"],                 # a skill = an ordered Lifecycle of Phases
    "Phase":      ["skill", "index", "name", "produces"],   # one atomic step
    "Tool":       ["name", "input", "output"],      # a typed tool (input/output schema refs)
}

# --- core closed enums ------------------------------------------------------
ROLES = {"act", "transform", "effect"}              # how-verb roles
LIFECYCLE_STATES = {                                # A2A-aligned task states
    "submitted", "working", "input-required", "auth-required",
    "completed", "failed", "canceled",
}

# --- core edge types (enumerated; link() rejects anything else) -------------
EDGE_TYPES = {
    "SERVES", "PERFORMED_BY", "PRODUCES", "PASSED", "BLOCKED_ON",
    "DERIVED_FROM", "VALIDATES_AGAINST", "SUPERSEDED_BY",
    "DISPATCHED_TO", "DRIVES", "PRECEDES", "NEXT", "HAS_PHASE",
}

# closed-enum constraints on specific (label, field) pairs — ENFORCED
FIELD_ENUMS: dict[tuple[str, str], set] = {
    ("Invocation", "role"): ROLES,
    ("Lifecycle", "state"): LIFECYCLE_STATES,
}

# --- a strict skill schema kept in the CORE as the canonical micro-step shape:
# the bitwize album-conceptualizer (7 gated phases, progressive disclosure, a
# Phase-7 hard gate). Capabilities contribute their OWN skills the same way.
ALBUM_CONCEPT_SKILL = {
    "name": "album-concept",
    "kind": "conceptualizer",
    "phases": [
        {"index": 1, "name": "foundation",
         "produces": ["artist", "genre", "type", "scale", "theme", "true_story"]},
        {"index": 2, "name": "concept",
         "produces": ["key_subjects", "emotional_core", "why"]},
        {"index": 3, "name": "sonic",
         "produces": ["references", "production_style", "vocal_approach",
                      "instrumentation", "mood", "target_duration"]},
        {"index": 4, "name": "structure",
         "produces": ["tracklist", "sequencing", "energy_map"]},
        {"index": 5, "name": "art",
         "produces": ["visual_concept", "palette", "symbols"]},
        {"index": 6, "name": "practical",
         "produces": ["album_title", "track_titles", "research_needs",
                      "explicit", "distributor_genres"]},
        {"index": 7, "name": "confirmation",
         "produces": ["user_confirmed"], "gate": "hard"},
    ],
}

ALBUM_TYPES = {"documentary", "narrative", "thematic", "character-study",
               "collection", "ost"}

CORE_SKILLS = {"album-concept": ALBUM_CONCEPT_SKILL}


@dataclass
class OntologyExtension:
    """What a capability contributes to the ontology. All optional — a capability
    that uses only core types contributes nothing. Merged onto the core strictly."""
    nodes: dict[str, list[str]] = field(default_factory=dict)        # label -> required fields
    edges: set = field(default_factory=set)                         # additional edge types
    enums: dict = field(default_factory=dict)                       # (label, field) -> allowed set
    skills: dict = field(default_factory=dict)                      # skill-name -> skill schema
    schemas: dict = field(default_factory=dict)                     # artefact/template name -> required fields
    templates: dict = field(default_factory=dict)                   # template name -> body


class Ontology:
    """The effective ontology: the core, plus every capability's extension."""

    def __init__(self) -> None:
        self.nodes = {k: list(v) for k, v in NODE_SCHEMAS.items()}
        self.edges = set(EDGE_TYPES)
        self.enums = {k: set(v) for k, v in FIELD_ENUMS.items()}
        self.skills = dict(CORE_SKILLS)
        self.schemas: dict[str, list[str]] = {}
        self.templates: dict[str, str] = {}

    @classmethod
    def core(cls) -> "Ontology":
        return cls()

    def extend(self, ext: OntologyExtension, owner: str = "?") -> "Ontology":
        for label, req in ext.nodes.items():
            if label in self.nodes and list(self.nodes[label]) != list(req):
                raise ValueError(
                    f"ontology extension by {owner!r}: node {label!r} redefines an "
                    f"existing schema {self.nodes[label]} with {list(req)}")
            self.nodes[label] = list(req)
        self.edges |= set(ext.edges)
        for key, allowed in ext.enums.items():
            self.enums.setdefault(key, set()).update(allowed)     # enums widen, never clobber
        for name, sk in ext.skills.items():
            if name in self.skills:
                raise ValueError(f"{owner!r}: skill {name!r} already defined")
            self.skills[name] = sk
        for name, req in ext.schemas.items():
            if name in self.schemas:
                raise ValueError(f"{owner!r}: schema {name!r} already defined")
            self.schemas[name] = list(req)
        for name, body in ext.templates.items():
            if name in self.templates:
                raise ValueError(f"{owner!r}: template {name!r} already defined")
            self.templates[name] = body
        return self

    # --- enforcement (used by Memory) --------------------------------------
    def missing_required(self, label: str, props: dict) -> list[str]:
        return [f for f in self.nodes.get(label, []) if props.get(f) in (None, "")]

    def violations(self, label: str, props: dict) -> list[str]:
        out = [f"missing required {f!r}" for f in self.missing_required(label, props)]
        for (lbl, fld), allowed in self.enums.items():
            if lbl == label and fld in props and props[fld] not in allowed:
                out.append(f"{fld}={props[fld]!r} not in {sorted(allowed)}")
        return out

    def is_known_edge(self, rel: str) -> bool:
        return rel in self.edges

    def skill(self, name: str) -> dict:
        return self.skills[name]
