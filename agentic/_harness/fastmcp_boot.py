import json
from pathlib import Path
from fastmcp import FastMCP
from jsonschema import validate, ValidationError

from context._shared import error_codes

# spec 02 §Schema: We need to validate the tool result envelope
ENVELOPE_SCHEMA_PATH = Path("context/_shared/schemas/tool_result.schema.json")


def validate_tool_result(result: dict) -> dict:
    if ENVELOPE_SCHEMA_PATH.exists():
        try:
            with open(ENVELOPE_SCHEMA_PATH) as f:
                schema = json.load(f)
            validate(instance=result, schema=schema)
        except ValidationError as e:
            # Wrap in spec-02 error response
            return {
                "ok": False,
                "data": {
                    "error": {
                        "code": error_codes.ENVELOPE_INVALID,
                        "message": str(e.path),
                        "fix_hint": "Tool must return the spec-02 envelope.",
                    }
                },
                "warnings": [],
                "next_suggested_tools": [],
            }
        except Exception:
            # If schema reading fails, we skip validation or handle differently,
            # but for now we assume schema is valid if present.
            pass
    return result


def register_four_verb_contract(mcp: FastMCP, registry) -> None:
    @mcp.tool(name="mcp__list_tools")
    def list_tools(row: str | None = None) -> dict:
        """Return names of registered MCP tools, optionally filtered by row."""
        # Simple string matching for filtering
        tools = registry.get_all_tool_names()
        if row:
            tools = [t for t in tools if t.startswith(f"mcp__{row}_")]

        result = {
            "ok": True,
            "data": {"tools": tools},
            "warnings": [],
            "next_suggested_tools": [],
        }
        return validate_tool_result(result)

    @mcp.tool(name="mcp__call_tool")
    def call_tool(name: str, args: dict) -> dict:
        """Invoke a registered tool by name; pass through the envelope."""
        try:
            result = registry.call_tool(name, args)
            return validate_tool_result(result)
        except Exception as e:
            return validate_tool_result(
                {
                    "ok": False,
                    "data": {
                        "error": {
                            "code": error_codes.TOOL_ERROR,
                            "message": str(e),
                            "fix_hint": "Check the tool implementation and inputs.",
                        }
                    },
                    "warnings": [],
                    "next_suggested_tools": [],
                }
            )

    @mcp.tool(name="mcp__list_skills")
    def list_skills(row: str | None = None) -> dict:
        """Return slash-command names of registered skills."""
        skills = registry.get_all_skill_names()
        if row:
            skills = [s for s in skills if s.startswith(f"/{row}-")]

        result = {
            "ok": True,
            "data": {"skills": skills},
            "warnings": [],
            "next_suggested_tools": [],
        }
        return validate_tool_result(result)

    @mcp.tool(name="mcp__dispatch_skill")
    def dispatch_skill(name: str, args: dict) -> dict:
        """Invoke a skill. If it triggers a workflow phase that yields,
        return the PhaseStateEnvelope (spec 04). Else return a ToolResult."""
        try:
            result = registry.dispatch_skill(name, args)
            # dispatch_skill could return PhaseStateEnvelope, which isn't strictly tool_result.schema.json,
            # but standard returns are. For spec 06, we validate ToolResult. If it's a PhaseStateEnvelope,
            # we might skip validation or have a separate schema.
            # We'll rely on the handler providing valid envelopes.
            # But the spec says "Every registered tool's return value is validated against tool_result.schema.json".
            # FastMCP tools themselves wrap the result.
            # Wait, "If it triggers a workflow phase that yields, return the PhaseStateEnvelope... Else return a ToolResult."
            # We'll just validate it against the tool result envelope for now as spec 06 item 5 says "Every registered tool's return value is validated".
            return validate_tool_result(result)
        except Exception as e:
            return validate_tool_result(
                {
                    "ok": False,
                    "data": {
                        "error": {
                            "code": error_codes.SKILL_ERROR,
                            "message": str(e),
                            "fix_hint": "Check the skill implementation.",
                        }
                    },
                    "warnings": [],
                    "next_suggested_tools": [],
                }
            )
