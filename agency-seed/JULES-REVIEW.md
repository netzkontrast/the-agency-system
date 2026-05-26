# JULES-REVIEW — bash-only validation of the agency engine

> Outcome record of a live Jules review session (a real bash-only agent
> dogfooding `AGENTS.md`). Session `16448793329314054168`
> (https://jules.google.com/session/16448793329314054168), branch
> `claude/extract-agency-plugin-o4JRc`. Jules reached `COMPLETED` but paused
> before pushing its branch (the known "open PR?" gate), so this record is
> reconstructed from the session activities + the actions taken in response.

## What Jules validated (the harness-in-harness claim)

A bash-only agent — no MCP client, no Skill loader — set the engine up and drove
it **purely via the documented bash CLI** (`search` / `get-schema` / `execute`):

- Followed `AGENTS.md` setup, ran the suite → **all tests passed** (7 passed at
  the commit it cloned, pre-dating the schemas/templates test).
- Used the code-mode contract over the shell to discover a tool, read its schema,
  and `execute` a tool call. No engine/seed code modified.

This is the harness-in-harness / `AGENTS.md` claim confirmed by an actual
shell-only agent.

## Finding (a real gap) — and the fix

Jules hit setup friction: the code-mode sandbox (`execute`) needs
**`pydantic-monty`**, which `pip install fastmcp` does **not** pull — only
`fastmcp[code-mode]` does. `requirements.txt` previously pinned plain `fastmcp`,
so a fresh agent's documented setup would fail the `execute`-path tests.

**Resolved:** `requirements.txt` now pins `fastmcp[code-mode]>=3.3.0`. Proven by
a clean-room install (fresh venv, `pip install -r requirements.txt` only) →
`pydantic-monty` present → **8/8 tests pass**.

## Net

The bash-only contract works as documented; the one gap a real shell-only agent
would hit is closed and proven. `AGENTS.md` is accurate for setup once the
`[code-mode]` extra is pulled (now the default via `requirements.txt`).
