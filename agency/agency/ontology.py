"""Strict ontology + schemata for the agency graph.

The typed backbone that lets skills/tools be real, atomic, micro-steps. Every
node type has a STRICT required-field schema; every edge type is enumerated.
`Memory.record`/`Memory.link` enforce these — an out-of-schema node or an unknown
edge raises, so the graph cannot drift. Token-efficient: schemas list only the
*required* fields (extra fields are allowed but not mandated), and a skill
discloses one phase's schema at a time.
"""
from __future__ import annotations

# --- node types: label -> strict required fields ---------------------------
NODE_SCHEMAS: dict[str, list[str]] = {
    "Intent":     ["purpose", "deliverable", "acceptance", "status"],
    "Invocation": ["capability", "verb", "role"],
    "Lifecycle":  ["state", "phase"],
    "Agent":      ["runtime"],
    "Gate":       ["name", "passed"],
    "Artefact":   ["kind"],
    "Schema":     ["name", "required"],
    "Template":   ["name", "body"],
    # micro-step skills & tools:
    "Skill":      ["name", "kind"],                 # a skill = an ordered Lifecycle of Phases
    "Phase":      ["skill", "index", "name", "produces"],   # one atomic step; `produces` = its required outputs
    "Tool":       ["name", "input", "output"],      # a typed tool (input/output schema refs)
    # plugin-development (ported from superpowers writing-skills + plugin authoring):
    "Plugin":     ["name", "version", "description"],       # a Claude Code plugin manifest
    "Command":    ["name", "description"],                  # a slash command
}

# --- closed enums ----------------------------------------------------------
ROLES = {"act", "transform", "effect"}              # how-verb roles
LIFECYCLE_STATES = {                                # A2A-aligned task states
    "submitted", "working", "input-required", "auth-required",
    "completed", "failed", "canceled",
}

# --- edge types (enumerated; link() rejects anything else) -----------------
EDGE_TYPES = {
    "SERVES", "PERFORMED_BY", "PRODUCES", "PASSED", "BLOCKED_ON",
    "DERIVED_FROM", "VALIDATES_AGAINST", "SUPERSEDED_BY",
    "DISPATCHED_TO", "DRIVES", "PRECEDES", "NEXT", "HAS_PHASE",
}


# closed-enum constraints on specific (label, field) pairs — ENFORCED, not decorative
FIELD_ENUMS = {
    ("Invocation", "role"): ROLES,
    ("Lifecycle", "state"): LIFECYCLE_STATES,
}


def missing_required(label: str, props: dict) -> list[str]:
    """Required fields absent (None/empty) for a known label; [] if label unknown
    (unknown labels are permitted — the ontology is strict, not closed-world)."""
    return [f for f in NODE_SCHEMAS.get(label, []) if props.get(f) in (None, "")]


def violations(label: str, props: dict) -> list[str]:
    """All ontology violations for a node: missing required fields AND values that
    break a closed enum. This is what makes the schemata genuinely *strict*."""
    out = [f"missing required {f!r}" for f in missing_required(label, props)]
    for (lbl, field), allowed in FIELD_ENUMS.items():
        if lbl == label and field in props and props[field] not in allowed:
            out.append(f"{field}={props[field]!r} not in {sorted(allowed)}")
    return out


def is_known_edge(rel: str) -> bool:
    return rel in EDGE_TYPES


# --- a strict skill schema, ported from the REAL bitwize album-conceptualizer
# (its 7-phase gated workflow). This is the template for a micro-step skill:
# a Lifecycle of ordered Phases, each declaring only its required outputs, ending
# in a hard gate (Phase 7) that `elicit`s the human. The engine walks one phase at
# a time (progressive disclosure) — never the whole skill at once.
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

# album types as a closed enum (the conceptualizer's type choice)
ALBUM_TYPES = {"documentary", "narrative", "thematic", "character-study",
               "collection", "ost"}

# --- ported COMPLETELY from superpowers `writing-skills` (the skill creator).
# The Iron Law — "NO SKILL WITHOUT A FAILING TEST FIRST" — is ENFORCED by the
# phase ordering itself: the walker advances one phase at a time and validates
# each phase's required outputs, so GREEN (authoring) is structurally
# unreachable until RED (the baseline observation) has produced its outputs.
# RED → GREEN → lint(CSO) → REFACTOR → deploy(hard gate). The GREEN + lint phases
# are bound to REAL capability verbs (author_skill / lint_skill).
SKILL_CREATION_SKILL = {
    "name": "skill-creation",
    "kind": "authoring",
    "phases": [
        {"index": 1, "name": "red-baseline",
         "produces": ["baseline", "rationalizations"]},
        {"index": 2, "name": "green-author", "produces": ["skill_md"],
         "invoke": {"capability": "plugin", "verb": "author_skill"},
         "inputs": ["name", "description", "body"]},
        {"index": 3, "name": "lint", "produces": ["lint"],
         "invoke": {"capability": "plugin", "verb": "lint_skill"},
         "inputs": ["name", "description"]},
        {"index": 4, "name": "refactor",
         "produces": ["rationalization_table", "red_flags"]},
        {"index": 5, "name": "deploy", "produces": ["user_confirmed"], "gate": "hard"},
    ],
}

# --- the complete plugin-authoring chain: each phase emits a prestructured
# document (the bitwize "resulting document of each step" pattern, made strict +
# provenance-recorded). manifest → skill → command → marketplace entry → confirm.
PLUGIN_DEV_SKILL = {
    "name": "plugin-dev",
    "kind": "authoring",
    "phases": [
        {"index": 1, "name": "manifest", "produces": ["manifest"],
         "invoke": {"capability": "plugin", "verb": "scaffold"},
         "inputs": ["name", "version", "description"]},
        {"index": 2, "name": "skill", "produces": ["skill_md"],
         "invoke": {"capability": "plugin", "verb": "author_skill"},
         "inputs": ["name", "description", "body"]},
        {"index": 3, "name": "command", "produces": ["command_md"],
         "invoke": {"capability": "plugin", "verb": "author_command"},
         "inputs": ["name", "description", "body"]},
        {"index": 4, "name": "marketplace", "produces": ["entry"],
         "invoke": {"capability": "plugin", "verb": "marketplace_entry"},
         "inputs": ["name", "version", "description", "source"]},
        {"index": 5, "name": "confirm", "produces": ["user_confirmed"], "gate": "hard"},
    ],
}
