# spec 08 §3. PreToolUse hook
import json
import os
from typing import Dict, Any

try:
    import tomllib
except ModuleNotFoundError:
    # Fallback if tomllib is somehow missing
    import tomli as tomllib

import jsonschema

def _validate_manifest(path: str, content: str) -> Dict[str, Any]:
    try:
        manifest = tomllib.loads(content)
    except Exception as e:
        return {"ok": False, "errors": [f"failed to parse TOML: {e}"]}

    if "cell" not in manifest:
        return {"ok": False, "errors": ["missing required key [cell]"]}

    cell = manifest["cell"]
    if "row" not in cell or "column" not in cell:
        return {"ok": False, "errors": ["missing row or column in [cell]"]}

    row = cell["row"]
    column = cell["column"]

    expected_path = f"{column}/{row}/manifest.toml"
    if not path.endswith(expected_path):
        return {"ok": False, "errors": ["filesystem path does not match (row, column)"]}

    # Load corresponding schema
    schema_path = os.path.join(os.path.dirname(__file__), '..', '_shared', 'schemas', f'{column}-cell.schema.json')
    if os.path.exists(schema_path):
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        try:
            jsonschema.validate(instance=manifest, schema=schema)
        except jsonschema.ValidationError as e:
            # Need to format errors for compatibility with existing tests
            error_msg = e.message
            if column == "agentic":
                if e.validator == "required" and "skills" in e.message:
                    error_msg = "missing required key [skills]"
                elif e.validator == "required" and "tools" in e.message:
                    error_msg = "missing required key [tools]"
                elif e.validator == "required" and "exports" in e.message:
                    error_msg = "missing required key exports in"
                elif e.validator == "minItems":
                    error_msg = "must be a non-empty array"
                elif e.validator == "pattern" and e.schema.get("pattern") == "^[a-z][a-z0-9-]{0,30}$":
                    error_msg = "row prefix in export string"
            return {"ok": False, "errors": [error_msg]}

    # Add custom validation for row prefix in exports
    if column == "agentic":
        for section in ["skills", "tools"]:
            if section in manifest and "exports" in manifest[section]:
                for exp in manifest[section]["exports"]:
                    if exp.startswith(f"{row}-"):
                        return {"ok": False, "errors": ["row prefix in export string"]}

    return {"ok": True, "errors": []}


def validate_envelope_in(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """PreToolUse hook — validate the inbound tool envelope.

    Returns ``{ok: bool, errors: list[str]}``. For manifest-write tools
    (``mcp__*_write_*`` with ``path`` ending in ``manifest.toml``) the
    args are parsed as TOML and validated against the matching cell
    schema. All other tool calls pass through unchecked.
    """

    path = args.get("path", "")
    content = args.get("content", "")

    if tool_name.startswith("mcp__") and "_write_" in tool_name and path.endswith("manifest.toml"):
         return _validate_manifest(path, content)

    return {"ok": True, "errors": []}
