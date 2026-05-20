"""Cross-column error-code catalogue.

Every site that produces an envelope with ``data.error.code`` MUST pull
its code from this module. Centralising makes the contract greppable and
prevents drift when new codes are needed.

Codes are ``UPPER_SNAKE_CASE`` strings; the constant name matches the
string value, so ``HANDLER_NOT_FOUND == "HANDLER_NOT_FOUND"``.

When you need a new code:

1. Add it here in the right section (validation / runner / handler /
   resume).
2. Use the constant — never inline the string.
3. If the new code crosses column boundaries, add a brief one-liner to
   the section comment so the next contributor can find it.

Sections mirror the four-verb contract's natural producers:

* **Validation** — schema / envelope contract failures.
* **Tool dispatch** — `mcp__call_tool` and `mcp__dispatch_skill`.
* **Cell loader** — handler discovery / import failures.
* **Workflow runner** — `_walk_phase` and the resume loop.
"""


# Validation -----------------------------------------------------------

ENVELOPE_INVALID = "ENVELOPE_INVALID"
"""Tool result did not validate against tool_result.schema.json."""


# Tool dispatch --------------------------------------------------------

TOOL_ERROR = "TOOL_ERROR"
"""Generic exception escaped from a tool handler."""

SKILL_ERROR = "SKILL_ERROR"
"""Generic exception escaped from a skill dispatcher."""


# Cell loader (handler discovery) --------------------------------------

HANDLER_NOT_FOUND = "HANDLER_NOT_FOUND"
"""No handler module / no registered MCP tool by the derived name.

Produced by both the cell loader (import-time discovery) and the
workflow walker (registry lookup at dispatch time)."""

HANDLER_MISSING_METHOD = "HANDLER_MISSING_METHOD"
"""Handler module loaded but does not define ``handle(**kwargs)``."""


# Workflow runner (walker + handler invocation) ------------------------

PHASE_BODY_MISSING = "PHASE_BODY_MISSING"
"""``workflow/<row>/<body_ref>`` referenced by a Phase node does not
exist on disk."""

HANDLER_BAD_SIGNATURE = "HANDLER_BAD_SIGNATURE"
"""Handler rejected the inputs (TypeError on call)."""

HANDLER_EXCEPTION = "HANDLER_EXCEPTION"
"""Handler raised a non-TypeError exception during execution."""

HANDLER_BAD_RETURN = "HANDLER_BAD_RETURN"
"""Handler returned a value that is not a tool_result envelope."""


# Workflow runner (resume contract) ------------------------------------

RESUME_EXPIRED = "RESUME_EXPIRED"
"""No Continuation node matches (session_id, phase_id) — TTL swept it
or the session never persisted one."""

RESUME_TERMINAL = "RESUME_TERMINAL"
"""Hydrated envelope was already in a terminal status (``completed`` or
``failed``); cannot resume."""

RESUME_PHASE_GONE = "RESUME_PHASE_GONE"
"""Continuation hydrated cleanly but the Phase node it points at no
longer exists in the graph."""


# Jules orchestration (jules-row handlers) -----------------------------

JULES_SOURCE_UNRESOLVED = "JULES_SOURCE_UNRESOLVED"
"""``jules_resolve_source(owner, repo)`` returned no matching source —
the GitHub repo is not connected to the Jules account."""

JULES_DISPATCH_FAILED = "JULES_DISPATCH_FAILED"
"""``jules_create`` returned an error response or raised before the
session id was minted."""

JULES_API_ERROR = "JULES_API_ERROR"
"""Any other failure surfaced by the jules_mcp lifecycle calls
(``jules_get``, ``jules_approve``, ``jules_message``)."""

SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
"""Handler was given a ``session_id`` with no matching JulesSession node
in the ontology graph."""

SESSION_STATE_INVALID = "SESSION_STATE_INVALID"
"""Handler refused to transition the session because the current state
violates the state-machine contract (e.g. await_plan called on a
DISPATCHED session that never reached AWAITING_PLAN_APPROVAL)."""

PATCH_UNAVAILABLE = "PATCH_UNAVAILABLE"
"""``jules_patch_summary`` returned an error — patch endpoint failed
or session has produced no diff yet."""

PATCH_APPLY_FAILED = "PATCH_APPLY_FAILED"
"""``jules_patch_apply`` reported ``applied=false`` (typically a
git-apply conflict captured in ``git_stderr``)."""
