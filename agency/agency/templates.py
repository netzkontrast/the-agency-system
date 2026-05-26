"""Templates — the prestructure for the resulting document of each step of a chain.

The agency analog of the bitwize plugin's `templates/` directory: each is a
*living document* skeleton a Capability `act` fills in. A Template pairs with a
strict Schema (`REQUIRED`) — the generate/validate layer from CORE: a Capability
generates an Artefact `DERIVED_FROM` a Template that `VALIDATES_AGAINST` its
Schema. Markdown docs use `string.Template` (`$field`, brace-safe for bodies
that contain `{}`); the JSON plugin manifest is generated structurally
(`manifest_obj`) so it is always valid JSON.
"""
from __future__ import annotations

from string import Template

# A Claude Code SKILL.md — frontmatter + body. This is what the *skill creator*
# emits; it is the unit a plugin ships.
SKILL_MD = Template(
    "---\n"
    "name: $name\n"
    "description: $description\n"
    "allowed-tools:\n"
    "$allowed_tools\n"
    "---\n"
    "\n"
    "# $title\n"
    "\n"
    "$body\n"
)

# A Claude Code slash command — frontmatter (description) + the prompt body.
COMMAND_MD = Template(
    "---\n"
    "description: $description\n"
    "---\n"
    "\n"
    "$body\n"
)

# The prestructured *step document*: one chain step's result as a living doc
# (inputs it consumed, the output it produced, notes) — the bitwize album.md /
# track.md pattern, generalized to any chain step.
STEP_DOC = Template(
    "---\n"
    "step: $step\n"
    "status: $status\n"
    "---\n"
    "\n"
    "# $step\n"
    "\n"
    "## Inputs\n"
    "$inputs\n"
    "\n"
    "## Output\n"
    "$output\n"
    "\n"
    "## Notes\n"
    "$notes\n"
)

# Strict required-field schema per template kind (the validate side of the
# generate/validate pair). Recorded as a Schema node powers `validate_schema`.
REQUIRED: dict[str, list[str]] = {
    "plugin-manifest": ["name", "version", "description"],
    "skill-md": ["name", "description", "body"],
    "command-md": ["name", "description", "body"],
    "marketplace-entry": ["name", "version", "description", "source"],
    "step-doc": ["step", "output"],
}


def manifest_obj(name: str, version: str, description: str) -> dict:
    """The canonical `.claude-plugin/plugin.json` shape (Claude Code install
    descriptor). Generated structurally so the artefact is always valid JSON.
    Per the plugin spec: `author` is an OBJECT, `keywords` an ARRAY, and component
    paths are relative and start with `./`."""
    return {
        "name": name,
        "version": version,
        "description": description,
        "author": {"name": "agency"},
        "keywords": ["agency", "code-mode", "capabilities"],
        "skills": "./skills/",
        "commands": "./commands/",
    }


def marketplace_obj(name: str, version: str, description: str, source: str) -> dict:
    """One entry of a Claude Code `marketplace.json` `plugins` array. Per the
    marketplace schema `source` is EITHER a relative path string OR a github
    object — a bare `owner/name` is normalised to `{source: github, repo}`."""
    src = ({"source": "github", "repo": source}
           if "/" in source and not source.startswith(".") else source)
    return {"name": name, "version": version, "description": description, "source": src}
