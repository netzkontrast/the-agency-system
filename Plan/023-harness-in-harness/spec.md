---
spec_id: 023
slug: harness-in-harness
status: superseded
superseded_by: [vision/specs/10-harness-ladder.md §5, vision/specs/14-progressive-disclosure-roadmap.md]
owner: jules
depends_on: [008, 022]
affects:
  - bin/agency
  - servers/agency-mcp/src/agency_mcp/lib/devmode/__init__.py
  - servers/agency-mcp/src/agency_mcp/lib/devmode/server.py
  - servers/agency-mcp/src/agency_mcp/lib/devmode/discovery.py
  - servers/agency-mcp/src/agency_mcp/lib/devmode/progressive_skill.py
  - docs/architecture/harness-in-harness.md
  - tests/integration/test_devmode_server.py
  - tests/integration/test_devmode_progressive_disclosure.py
  - Plan/_research/023-harness-in-harness-epic-plan.md
source-repos: []
estimated_jules_sessions: 3
domain: agentic
wave: B
spec_kind: research_epic
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `Master`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 023 — Harness in a Harness (research epic)

## Why

The `agency-system` plugin works inside Claude Code via the standard MCP transport, but **any other agent without MCP integration is locked out** — Jules sandboxes, Cursor, Codex CLI, Continue, raw bash-only LLM harnesses. These agents can run scripts but cannot natively load MCP tools or auto-discover skills.

Yet they all share the same lowest-common-denominator surface: a bash tool. If we expose the plugin's full functionality through a single binary CLI that adopts the same token-efficiency disciplines we built into the plugin itself — Code Mode (defer schemas, discover via `search` → `describe` → `execute`) and Context Mode (defer document bodies, progressively disclose) — then **any agent with shell access becomes a first-class consumer of the agency-system plugin** without any plugin-specific integration code on their side.

That is the "harness in a harness" insight: build a tiny CLI harness (`bin/agency`, single binary with `git`/`docker`-style subcommands) that wraps the MCP daemon + skills tree, exposes a minimal anchor surface (a few discovery commands), and lets agents pull schemas/bodies on demand at the granularity they actually need. This collapses the "agents who can use the plugin" set from "agents with native MCP" to "agents with bash" — roughly a 5× audience expansion overnight.

This is a **research-epic spec**: instead of prescribing every implementation detail up front, it commissions a focused research pass (Approach §1-§3) to produce a concrete sub-spec breakdown under `Plan/_research/023-harness-in-harness-epic-plan.md`. The implementation (§4-§9) ships the foundational MVP — daemon + single-binary CLI + first discovery layer — leaving the deeper progressive-disclosure design open for the research output to refine.

## Done When

- [ ] **Research output:** `Plan/_research/023-harness-in-harness-epic-plan.md` exists, ≥1500 words, citing ≥6 sources. It enumerates: (a) prior-art harnesses (mcp-cli, fastmcp dev, Continue's MCP bridge, smol-tool, Cursor's MCP layer, etc.), (b) the canonical anchor-command surface (≤5 commands), (c) the progressive-disclosure ladder for skills (e.g. 4-tier: name → summary → frontmatter → full body), (d) at least 3 candidate sub-specs (one per major sub-feature) with their `depends_on`, `affects`, and `estimated_jules_sessions`, (e) a token-economy analysis comparing this approach to a naive `--list-all` CLI, (f) security/permission boundary recommendations (local-only, no auth → when to add what), (g) **transport-layer choice** between HTTP + JSON-RPC (MCP-standard) vs ZeroMQ / Unix-domain-socket / stdio-multiplexed alternatives, with a measured latency + throughput comparison (or cited numbers) and a tradeoff matrix.
- [ ] **MVP daemon:** `bin/agency server start` spawns the agency FastMCP server (transport per the research output's recommendation; HTTP on `127.0.0.1:7777` as the default until the comparison says otherwise), writes a PID file at `~/.agency-system/dev-server.pid`, logs to `~/.agency-system/dev-server.log`, and returns 0 on success. `agency server stop` sends SIGTERM to the PID and waits for clean shutdown. `agency server status` returns 0 + JSON `{running, pid, port, uptime_seconds}` or 1 + `{running: false}`. `agency server logs` tails the log file.
- [ ] **Single-binary CLI:** `bin/agency` is executable and implements all subcommands: `agency server …` (lifecycle), `agency tool …` (search/describe/execute, the anchor surface), `agency skill …` (list/describe/read, the disclosure surface), and `agency --bootstrap` (the self-doc). Pretty-prints JSON results (or `--raw` for piping). Auto-starts the daemon if not running (override via `--no-autostart`).
- [ ] **Progressive disclosure for skills:** `agency skill list [--domain X]` returns `[{slug, summary}]` only (no body). `agency skill describe <slug>` returns frontmatter + summary + heading list. `agency skill read <slug> [--section X]` returns the full body or a single section. Three explicit token-cost tiers; the lightest tier MUST stay ≤500 tokens for the full music-skill set (54 skills).
- [ ] **MCP wire-format pass-through:** the CLI's `agency tool execute` translates into a real MCP JSON-RPC call (`tools/call`) against the daemon's transport endpoint. Other MCP clients (Cursor, Continue, Cline) can connect to the daemon and use the same surface — i.e. `bin/agency` is a real MCP server with a thin CLI on top, not a custom protocol. (If the research output picks a non-standard transport, document the MCP-compatibility bridge.)
- [ ] **Bootstrap self-doc:** `agency --bootstrap` (zero args) prints ≤60 lines of self-documenting usage, including the 3-5 anchor commands, one example per command, and a pointer to `docs/architecture/harness-in-harness.md`. The output is the contract — any agent (Jules, Codex, GPT-5, etc.) reading it should be able to use the plugin without further context.
- [ ] **Smoke tests:** `tests/integration/test_devmode_server.py` covers daemon lifecycle + tool execute round-trip. `tests/integration/test_devmode_progressive_disclosure.py` asserts the 4-tier skill ladder respects its token budgets (use tiktoken). Both pass.
- [ ] **Documentation:** `docs/architecture/harness-in-harness.md` (≤300 lines) describes the architectural model, the discovery surface, the progressive-disclosure ladder, the token-economy comparison, the chosen transport (with rationale), and the security boundary (localhost-only, no auth, kill-on-parent-exit).

## Source clones (run first)

```bash
# No external clones required — this spec works on the existing tree.
# Reference reading lists go in the research output (Approach §1-§3).
```

## Files

- **Create**:
  - `bin/agency` — single CLI binary (Python with `argparse` subcommands, `httpx` for HTTP transport or `pyzmq` if the research output picks ZeroMQ).
  - `servers/agency-mcp/src/agency_mcp/lib/devmode/__init__.py`.
  - `servers/agency-mcp/src/agency_mcp/lib/devmode/server.py` — adds a `run_dev_transport(transport, host, port)` entry point that the daemon spawns.
  - `servers/agency-mcp/src/agency_mcp/lib/devmode/discovery.py` — the search/describe/execute anchor surface, mirroring Spec 104's anchor-triad pattern but at the CLI layer.
  - `servers/agency-mcp/src/agency_mcp/lib/devmode/progressive_skill.py` — the 4-tier skill disclosure ladder.
  - `docs/architecture/harness-in-harness.md` — the architectural overview.
  - `tests/integration/test_devmode_server.py`, `tests/integration/test_devmode_progressive_disclosure.py`.
  - `Plan/_research/023-harness-in-harness-epic-plan.md` — the research output.
- **Modify**: none (no changes to existing handlers/skills/specs).
- **Move / Delete**: none.

## Approach

### Pre-research finding (locked 2026-05-18) — transport layer

A focused research pass on ZeroMQ vs HTTP vs UDS vs stdio for the local MCP daemon transport concluded: **stay on Streamable HTTP as the default; fall back to Unix domain socket only if profiling later shows wire-time matters.** Reasons:

- MCP 2025-06-18 spec names only `stdio` and `Streamable HTTP` as standard transports. Custom transports are *permitted* but no third-party MCP client (Cursor / Continue / Cline) will negotiate them. ZeroMQ is *legal* but isolated.
- FastMCP exposes `stdio`, `http`, and (deprecated) `sse`. No ZeroMQ, no UDS adapter — both would require a custom bridge against `mcp.server.lowlevel`.
- Latency numbers favour ZeroMQ marginally (≤200 μs vs ~0.5-1 ms HTTP loopback p50), but our token-budget bottleneck is FastMCP/Python work, not the wire. 100 ms p99 is 20-200× the latency floor of *any* of these transports.
- Zero prior art for "MCP over ZeroMQ" on GitHub (verified 2026-05-18 search).
- UDS captures most of the speed-up (~30-50% over TCP loopback) without breaking JSON-RPC framing — that is the right escape valve if Spec 023's MVP shows wire-time pressure.

**Implication for Subagent D below:** transport is no longer an open question — drop it from the research kickoff. The research-epic now focuses on the three remaining unknowns (prior art, anchor surface, progressive disclosure). Document the transport decision in the epic plan's "Decisions locked pre-implementation" section, but do not re-research it.

Sources: [MCP spec — transports](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports), [FastMCP deployment](https://gofastmcp.com/deployment/running-server), [pyzmq performance](https://deepwiki.com/zeromq/pyzmq/7-performance-considerations), [UDS vs TCP loopback (Myhro 2017)](https://blog.myhro.info/2017/01/benchmarking-ip-and-unix-domain-sockets-for-real), [Baeldung IPC perf](https://www.baeldung.com/linux/ipc-performance-comparison).

---

1. **Gate 1 — Confidence + research kickoff.** Verify Spec 008 (CodeMode-registry) + Spec 022 (dev-mode-install) are merged on Master. Cite both PR shas. Then **spawn ≥3 parallel research subagents** (Subagent A/B/C below; D is already locked above) — they produce the inputs for the epic plan.

   - **Subagent A — Prior art:** Survey existing tools that expose an MCP daemon over a transport + a thin CLI for external agents. Targets: `mcp dev`, `fastmcp dev`, the official `mcp-cli` npm package, Continue's MCP bridge, Cursor's MCP integration source, Cline's MCP plumbing, smol-tool, any community projects on GitHub. For each: architecture diagram, daemon-vs-stateless choice, transport (stdio/HTTP/SSE/WebSocket/ZeroMQ), CLI ergonomics, license. Output: 5-row comparison table + recommendations for our case. Cap research at 8 fetches.

   - **Subagent B — Anchor surface design:** Given Spec 104's tool-anchor-triad and Spec 008's CodeMode classification, design the minimum CLI surface that matches the same token discipline. Output: a numbered command list (≤5 commands), with cost estimates per command (in tokens of CLI output) and a Gherkin trace of "agent X uses tool Y" via the surface. Bonus: propose how `--bootstrap` should chain into the discovery commands so any first-touch agent can self-onboard.

   - **Subagent C — Progressive disclosure for skills:** Research how other ecosystems do progressive disclosure of skill / persona / prompt content. Targets: Anthropic Skills, Anthropic Personas, OpenAI's Custom GPTs description vs body, Cursor's `.cursorrules`/AGENTS.md split, Continue's persona system, the original `skill-creator` SKILL.md 5-mandatory-sections convention. Output: a recommended 4-tier ladder (name → summary → frontmatter+heading-list → full body), token-budget per tier, the API shape (`--tier N` or `--section X` or both?), and how to handle composes_with chains (Spec 021 prompt-builders depend on each other).

   *(Subagent D — Transport-layer comparison was completed 2026-05-18 ahead of dispatch; finding locked above. Do not re-spawn.)*

2. **Synthesize the epic plan.** Combine the three subagent outputs (A/B/C) into `Plan/_research/023-harness-in-harness-epic-plan.md`. The synthesis MUST: confirm the locked transport choice (Streamable HTTP default, UDS as documented fallback), lock the anchor command list, lock the progressive-disclosure ladder, and **propose ≥3 sub-specs** (e.g. `023a-base-mvp`, `023b-progressive-disclosure-skills`, `023c-multi-client-validation`) with concrete `affects:` lists.

3. **PR-comment the epic plan + sleep.** Open a draft PR labelled `[REVIEW: research-output]` with the epic plan rendered in the body. WAIT for human review before proceeding to implementation. The research output is the deliverable; the MVP code below ships in a follow-up commit after the human approves the synthesis.

4. **MVP daemon.** Implement `agency server start/stop/status/logs` per the Done-When section. PID file + log rotation + graceful shutdown.

5. **MVP CLI baseline.** Implement `agency tool search/describe/execute` against the daemon's chosen transport. Auto-start logic. JSON output by default, pretty-printed.

6. **Progressive-disclosure for skills.** Implement the 4-tier ladder per the research output's recommendation. Enforce token budgets via tiktoken in the test.

7. **Bootstrap self-doc.** Write `agency --bootstrap` — the contract for first-touch agents.

8. **TDD — Gate 2.** Tests for: daemon lifecycle (start/status/stop idempotent), tool execute round-trip (call a known tool, assert response shape), skill disclosure tiers (each tier's output is ≤ its budget), MCP-wire compatibility (raw transport call works for external clients).

9. **Gate 3 + Gate 4 — Evidence + Self-Review.** Paste the test outputs + the bootstrap output (≤60 lines). Self-review the open questions deferred to the sub-specs (these become the next-session backlog).

## Acceptance (Gherkin)

```gherkin
# anchor: 023.1
Scenario: Research output produces a synthesised epic plan
  Given the four research subagents have run to completion
  When the operator reads Plan/_research/023-harness-in-harness-epic-plan.md
  Then the file is ≥1500 words
  And it cites ≥6 sources with URLs
  And it proposes ≥3 sub-specs with concrete affects and depends_on
  And it locks the transport-layer choice with a measured rationale

# anchor: 023.2
Scenario: Daemon lifecycle is idempotent and discoverable
  Given `agency server start` has been called once successfully
  When the operator runs `agency server status`
  Then the response is JSON {running: true, pid: <int>, port: 7777, uptime_seconds: <int>}
  When the operator runs `agency server start` a second time
  Then exit code is 0 and stderr says "already running, PID <int>"
  When the operator runs `agency server stop`
  Then the daemon process is gone and the PID file is removed

# anchor: 023.3
Scenario: Anchor-command discovery surface stays under token budget
  Given the daemon is running with all 113 tools registered
  When the operator runs `agency tool search music`
  Then the response is a JSON list of tool stubs (id, name, summary)
  And the total response is ≤ 1500 tokens (measured by tiktoken)
  When the operator runs `agency tool describe music_list_albums`
  Then the response includes the full schema for that one tool only

# anchor: 023.4
Scenario: Progressive disclosure for skills respects token tiers
  Given the daemon is running with all 54 music skills + jules skills loaded
  When the operator runs `agency skill list --domain music`
  Then the response is ≤ 500 tokens (54 stubs, name+summary only)
  When the operator runs `agency skill describe music-lyric-writer`
  Then the response is ≤ 1500 tokens (frontmatter + heading list + summary)
  When the operator runs `agency skill read music-lyric-writer --section "## Process"`
  Then the response is the body of that one section only

# anchor: 023.5
Scenario: Real MCP clients can connect to the daemon (transport-dependent)
  Given the daemon is running with the research-locked transport
  When an external MCP client (e.g. Cursor, Continue) sends a tools/call JSON-RPC
  Then the daemon responds with valid MCP JSON-RPC (over HTTP transport, OR via a documented MCP-bridge if the research picks a non-standard transport)
  And the response is identical to what `agency tool execute` would produce for the same call

# anchor: 023.6
Scenario: Bootstrap self-doc is the contract for new agents
  Given a first-touch agent has shell access but no prior knowledge of agency-system
  When the agent runs `agency --bootstrap`
  Then the output is ≤ 60 lines
  And the output names the ≤5 anchor commands (server/tool/skill/--bootstrap)
  And the output includes one runnable example per command
  And the output references docs/architecture/harness-in-harness.md
```

## Out of scope

- **Authentication / multi-tenant access.** Daemon is localhost-only, single-user. Auth is a follow-up spec only if remote access is ever desired.
- **Plugin hot-reload on file change.** The daemon must be restarted to pick up new skills/tools. A watcher-based hot-reload is a future spec.
- **Marketplace publication of `agency` as a standalone tool.** This ships only as part of the agency-system repo for now.
- **Stdio fallback transport.** HTTP (or research-chosen) is sufficient for the harness-in-harness use case. Stdio support remains via the existing `run.py` for Claude Code's `--plugin-dir` flow (Spec 022).
- **Cross-platform daemon management.** POSIX only (bash/Python on Linux + macOS). Windows uses WSL.
- **The deep "Context Mode" wiring (Spec 108 / 111-113).** Those specs handle Claude-Code-side context deferral. This spec handles CLI-side disclosure. They share a philosophy but ship independently — the research output should explicitly note the boundary.

## References

- `Plan/JULES_PROTOCOL.md` §3 (branch/PR discipline), §8 (silent-fail recovery)
- `Plan/000-overview.md` §2.1 (FastMCP conventions, anchor-triad rule), §4 (DAG — this spec sits at Wave B, parallel to 014/015/021)
- `Plan/022-dev-mode-install/spec.md` — the predecessor that makes `claude --plugin-dir` work natively; this spec extends the dev-mode story to non-Claude-Code agents
- `Plan/008-codemode-registry/spec.md` — the schema-deferral pattern this spec mirrors at the CLI layer
- `Plan/104-tool-search-anchor-triad/spec.md` — the in-FastMCP anchor-triad design; the CLI surface should be lexically aligned
- `Plan/108-context-mode-integration/spec.md` — the at-the-hook-layer Context Mode work (mksglu plugin adoption); explicit boundary in this spec's research output
- `Plan/_lessons-learned/14-token-consumption-postmortem.md` — the cost analysis that motivates the discovery + disclosure discipline
- [FastMCP HTTP transport docs](https://gofastmcp.com/servers/transports)
- [MCP spec — transports](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)
- [mcp-cli (npm)](https://www.npmjs.com/package/@modelcontextprotocol/cli)
- [Anthropic Skills documentation](https://platform.claude.com/docs/en/agents-and-tools/skills) — for progressive-disclosure prior art
- [pyzmq](https://pyzmq.readthedocs.io/) + [ZeroMQ guide](https://zguide.zeromq.org/) — for the Subagent D transport comparison
