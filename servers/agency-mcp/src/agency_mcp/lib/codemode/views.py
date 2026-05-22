from enum import StrEnum

class View(StrEnum):
    """View tier for token efficiency on read tools.

    - id: only the primary key.
    - summary: id + name + state.
    - preview: summary + truncated body + `truncated_marker`.
    - full: all fields.
    """
    id = "id"
    summary = "summary"
    preview = "preview"
    full = "full"

BODY_PREVIEW_CHARS = 400
