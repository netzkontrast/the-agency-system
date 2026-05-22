---
name: agency
description: Central router. Surveys workflow, explains the system, dispatches to domain skills. Use at session start or when lost.
skill_kind: orchestrator
domain: agentic
allowed-tools: [Read, Bash, mcp__agency-mcp__agency_tool_search, mcp__agency-mcp__agency_skill_search, mcp__agency-mcp__agency_skill_dispatch]
prerequisites: []
---

# Agency — central router

## What

`/agency` is the single entry point into the agency-system. It surveys the
workflow map, names the recommended next step, and dispatches to the matching
domain skill on demand. Skill bodies are loaded lazily — this router carries
only the routing graph (`references/routing.md`) and the canonical chains
(`references/workflows.md`), keeping cold context under ~3k tokens.

## When to use

- At session start — to load `health-check` + `session-load` baseline.
- When the user asks "what next?", "where am I?", or "what's left?".
- When intent is known but the correct skill is not (route via `agency_skill_search`).
- When crossing domains (music → jules, novel → agentic) — `related:` is the only legal bridge.
- When a skill announces `prefers_codemode: true` and you need to surface the nudge.
- When recovering from a stale state cache, missing prerequisite, or unclear handoff.

## How to use

1. **Resolve intent.** Call `agency_skill_search "<intent>"` to surface candidate skills with their domain + one-line summary. Do not guess skill names.
2. **Inspect before dispatch.** Call `agency_skill_describe <name>` to read the frontmatter + references list without loading the body. Verify `prerequisites:` are satisfied.
3. **Dispatch.** Call `agency_skill_dispatch <name> "<args>"` to load the full SKILL.md and run it. The body enters context only at this point.
4. **Reminder at handoff.** After the dispatched skill completes, emit a one-line "Next step (optional): `/agency:<next-skill>` would …" naming the recommended downstream skill from the `prerequisites:` graph (see `references/workflows.md`).
5. **Cross-domain handoff.** Only follow `related:` frontmatter edges. Never cross domains on a hunch.
6. **Code Mode nudge.** If a candidate skill's frontmatter carries `prefers_codemode: true`, emit one line before dispatch: *"This skill prefers code-mode — wrap calls in a single script for token efficiency."* Do not auto-rewrite.

## References

- [`references/routing.md`](references/routing.md) — workflow map and routing decision tree (Graphviz)
- [`references/workflows.md`](references/workflows.md) — canonical chains per domain (music pre-gen, music pre-release, novel structural, jules orchestration)
- [`references/domains.md`](references/domains.md) — the 5 domains + plug-in contract (`Domain(ABC)`, `manifest.toml`)
- [`references/meta-loop.md`](references/meta-loop.md) — lessons + ADRs + briefs + sessions (`Plan/_*` scaffolds)
- [`references/troubleshooting.md`](references/troubleshooting.md) — common failure modes (stale cache, missing prereqs, silent fails, override drift)

## Compatibility

- Claude Code (CLI, desktop, web) — invoked as `/agency` or `/agency-system:agency`.
- Codex / other harnesses — skill bodies are plain markdown; any tool that resolves `mcp__agency-mcp__*` and reads `SKILL.md` files can drive the same flow.
- L1 / L3 parity — the `agency_skill_*` triad ships on both the in-process harness and the L3 sidecar daemon (`bin/agency`).
