import tomli
from pathlib import Path
import importlib
import sys
from agentic._harness.name_deriver import (
    ManifestLintError,
    skill_name,
    mcp_tool_name,
    skill_md_path,
    handler_module,
)
from agentic._harness.codemode import wrap_for_codemode
from context._shared import error_codes


class CellRegistry:
    def __init__(self):
        self.skills = {}
        self.tools = {}
        self.codemode_set = set()

    def get_all_tool_names(self):
        return list(self.tools.keys())

    def get_all_skill_names(self):
        return list(self.skills.keys())

    def call_tool(self, name: str, args: dict):
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found.")
        return self.tools[name](**args)

    def dispatch_skill(self, name: str, args: dict):
        if name not in self.skills:
            raise ValueError(f"Skill {name} not found.")
        # For dispatch_skill, we return the content of SKILL.md or an envelope
        # as expected. Real implementation might evaluate or pass back.
        # But for this spec we just mock evaluating or pass it to some runner.
        return self.skills[name](**args)


def discover(root: Path = Path(".")) -> CellRegistry:
    """Glob-scan all three columns for manifest.toml and build the registry."""
    registry = CellRegistry()

    # We need to make sure root is in sys.path so dynamic imports of agentic.* work
    root_str = str(root.absolute())
    if root_str not in sys.path:
        sys.path.insert(0, root_str)

    # In a real context column PreToolUse hook, there would be JSON schema validation.
    # For now, we simulate parsing the toml and applying the derivation rules.
    for column in ["agentic", "workflow", "context"]:
        col_dir = root / column
        if not col_dir.exists():
            continue

        for row_dir in col_dir.iterdir():
            if not row_dir.is_dir() or row_dir.name.startswith("_"):
                continue

            manifest_path = row_dir / "manifest.toml"
            if not manifest_path.exists():
                continue

            with open(manifest_path, "rb") as f:
                try:
                    data = tomli.load(f)
                except tomli.TOMLDecodeError:
                    continue

            cell_data = data.get("cell", {})
            row = cell_data.get("row")
            manifest_col = cell_data.get("column")

            if row != row_dir.name or manifest_col != column:
                # Path mismatch, skip
                continue

            if column == "agentic":
                try:
                    _register_agentic(registry, row, data, root)
                except ManifestLintError as e:
                    # In a real app we'd log this. Boot continues.
                    pass

    return registry


def _register_agentic(registry: CellRegistry, row: str, data: dict, root: Path):
    skills_exports = data.get("skills", {}).get("exports", [])
    for export in skills_exports:
        s_name = "/" + skill_name(row, export)  # mcp__list_skills returns with slash
        s_path = skill_md_path(row, export)

        # We define a function that handles the skill execution.
        def skill_handler(_s_name=s_name, _s_path=s_path, **kwargs):
            return {
                "ok": True,
                "data": {"message": f"Dispatched {_s_name} at {_s_path}"},
                "warnings": [],
                "next_suggested_tools": [],
            }

        registry.skills[s_name] = skill_handler

    tools_exports = data.get("tools", {}).get("exports", [])
    for export in tools_exports:
        t_name = mcp_tool_name(row, export)
        mod_name = handler_module(row, export)

        def tool_wrapper(_mod_name=mod_name, **kwargs):
            # Dynamically import the module when the tool is called
            try:
                importlib.invalidate_caches()
                mod = importlib.import_module(_mod_name)
                # Assume standard pattern is to have a handle() function
                return mod.handle(**kwargs)
            except ImportError as e:
                # Print to stderr for debug
                import traceback

                print(f"ImportError: {e}", file=sys.stderr)
                return {
                    "ok": False,
                    "data": {
                        "error": {
                            "code": error_codes.HANDLER_NOT_FOUND,
                            "message": f"Could not import {_mod_name}",
                            "fix_hint": "Create the handler module.",
                        }
                    },
                    "warnings": [],
                    "next_suggested_tools": [],
                }
            except AttributeError:
                return {
                    "ok": False,
                    "data": {
                        "error": {
                            "code": error_codes.HANDLER_MISSING_METHOD,
                            "message": f"Module {_mod_name} does not define 'handle'",
                            "fix_hint": "Define a 'handle(**kwargs)' method.",
                        }
                    },
                    "warnings": [],
                    "next_suggested_tools": [],
                }

        registry.tools[t_name] = tool_wrapper

    codemode_prefers = data.get("codemode", {}).get("prefers", [])
    for export in codemode_prefers:
        t_name = mcp_tool_name(row, export)
        registry.codemode_set.add(t_name)
        if t_name in registry.tools:
            registry.tools[t_name] = wrap_for_codemode(
                registry.tools[t_name], t_name, registry.codemode_set
            )
