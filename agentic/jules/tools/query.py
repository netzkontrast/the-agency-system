"""`mcp__jules_query` — placeholder query tool for the jules agentic cell.

Given a `topic` keyword argument, returns a `tool_result` envelope
containing a single synthetic finding. The v0.1 implementation exists to
exercise the cell-loader / hook / ontology wiring end-to-end; real
retrieval comes in a later phase.
"""


def handle(**kwargs) -> dict:
    """Return a `tool_result` envelope for the given `topic`.

    Args:
        topic: Subject of the placeholder query. Defaults to "" when
            omitted so the envelope shape stays stable for callers that
            probe the tool without arguments.

    Returns:
        A dict matching `context/_shared/schemas/tool_result.schema.json`.
    """
    topic = kwargs.get("topic", "")
    return {
        "ok": True,
        "data": {
            "topic": topic,
            "findings": [f"placeholder finding for {topic}"],
        },
        "warnings": [],
        "next_suggested_tools": [],
    }
