---
slug: vision-harness-ladder
type: spec
status: ready
owner: claude
created: 2026-05-20
updated: 2026-05-20
summary: The three-layer harness ladder (L1 in-memory FastMCP, L2 subprocess probe, L3 sidecar daemon + bin/agency CLI). Defines the four-verb contract surface at every layer, the cross-layer equivalence invariant, the bootstrap path, the token-budget invariants (boot <500 tokens, tools/list <4 KB, per-result ≤4 KB), and the Path-A levers (L-α/β/γ) that are active in the implementation tag. Path B (full domain isomorphism) is vision-only (see spec 13); the deferred levers L-δ/ε/ζ/η + progressive disclosure are roadmap (see spec 14).
depends_on:
  - vision/specs/02-tool-result-envelope.md
  - vision/specs/06-agentic-base.md
  - vision/specs/09-crossover-matrix.md
  - vision/specs/11-four-verb-canon.md
  - vision/specs/12-vocabulary.md
referenced_by:
  - vision/specs/09-crossover-matrix.md
  - vision/specs/13-domain-isomorphism.md
  - vision/specs/14-progressive-disclosure-roadmap.md
supersedes:
  - Plan/harness/design.md
---

## 1. Motivation

The `agency-system` plugin has one supported access path today: a fresh Claude Code session launched with `claude --plugin-dir /home/user/the-agency-system` (or, post-marketplace, an installed plugin). Three distinct audiences hit that single path as a wall:

1. **Devs (human or agent) iterating on the plugin** can't dogfood it from inside their own session. `--plugin-dir` is a startup-only flag; in-flight Claude Code sessions cannot hot-reload it. The loop today is: edit handler → exit session → restart Claude Code with `--plugin-dir` → verify → repeat. **L1 closes this.**

2. **CI and the dev-install regression coverage** had a smoke test that *tried* to assert "the plugin loads via `--plugin-dir`" but used `/help` as the probe — `/help` invokes the chat surface, so the returned text depends on whichever plugin responds first. PR #115's interim fix swapped it for `claude plugin validate`, which is deterministic but only validates the *manifest schema* — it does not exercise the real boot path. The Codex P1 critique on PR #115 names this gap explicitly ([discussion_r3262361939](https://github.com/netzkontrast/the-agency-system/pull/115#discussion_r3262361939)). **L2 closes this.**

3. **Any agent without native MCP integration is locked out entirely.** Jules sandboxes, Cursor, Codex CLI, Continue, raw bash-only LLM harnesses — they can all run scripts, but cannot natively load MCP tools or auto-discover skills. Yet they all share one lowest-common-denominator surface: a bash shell. **L3 closes this** — a tiny CLI binary + daemon makes the plugin reachable from any shell-equipped harness, roughly a 5× audience expansion. Plan/023 names this insight; this design absorbs Plan/023's MVP scope into the unified ladder so all three layers ship under one coherent contract.

Plan/000-v2 (PR #111) commissions the next two Phase 1 smoke tests — `tests/smoke/test_boot_budget.py` (Spec 131) and `tests/smoke/test_toon_gate.py` (Spec 105) — but does not name the *shared harness* those tests will boot from. Every test that wants to instantiate `create_mcp()` and probe its 114-tool surface today re-implements the boilerplate; existing examples ([`tests/integration/test_context_anchor_triad.py:1-49`](../../tests/integration/test_context_anchor_triad.py), [`tests/unit/jules/test_handlers_smoke.py:1-26`](../../tests/unit/jules/test_handlers_smoke.py)) show three different invocation patterns for what should be one. No `tests/conftest.py` exists.

This design closes all three gaps with a single layered abstraction: **one four-verb contract** (*list tools, call tool, list skills, dispatch skill*) exposed via three transports at three fidelity tiers.

## 2. North-star table

**Spec 09 r2 reconciliation with the promoted Harness-in-Harness — stated plainly:**

Spec 09 and the promoted Harness ladder describe **the same isomorphism viewed from two different axes**.
- Spec 09 r2's axis: **caller-column × callee-column**, 9 cells, one MCP server, one envelope, four verbs at every cell boundary.
- Harness ladder's axis: **transport fidelity**, 3 layers, one MCP server, one envelope, four verbs at every layer boundary.

The single-MCP-server / single-envelope / single-four-verb invariants are **literally the same statements**. Neither supersedes the other. Wave 0's promotion makes the cross-axis citation explicit: spec 09 §3 bullets 1-2 cite `vision/specs/10-harness-ladder.md` §2 for the layer-fidelity axis, and 10-harness-ladder §2 cites `vision/specs/09-crossover-matrix.md` §2 for the matrix-cell axis.

| Layer | Audience | Boots via | Cost / call | What it proves |
|---|---|---|---|---|
| **L1 In-process harness** | Pytest, Phase 1 spec tests, devs (human or agent) iterating in-session | `create_mcp()` Python import + FastMCP in-memory transport ([fastmcp.Client](https://gofastmcp.com/clients/transports#in-memory-transport)) | ms | Tools register, schemas valid, handlers callable, skills parseable, anchor-triad output well-formed |
| **L2 Subprocess probe** | CI smoke, PR-115 follow-up, real-boot regression coverage | `subprocess.run(["claude", "--bare", "--plugin-dir", repo, "-p", ...])` | seconds + API tokens | The actual `claude` CLI loads the plugin end-to-end via the real `--plugin-dir` path; manifest + MCP wiring + skill auto-discovery all hold together |
| **L3 Sidecar daemon + CLI** | External agents (Cursor, Codex CLI, Jules sandbox, bash-only LLM harnesses), in-session bash dogfooding | `bin/agency server start` → JSON-RPC over Streamable HTTP (transport choice locked in [Plan/023](../023-harness-in-harness/spec.md) §Approach pre-research) | ~100 ms p50 (localhost), networked | The running plugin is reachable from *any* shell-equipped harness, including the active Claude Code session via `Bash` |

**The contract all three layers share:** *list tools, call a tool, list skills, dispatch a skill.* That four-verb surface is the ladder's invariant. L1 fakes the transport; L2 fakes nothing but pays per call; L3 makes the running plugin reachable from outside Claude Code entirely. Each layer is **independently shippable**. This design covers all three.

**Relationship to Plan/023.** Plan/023 was structured as a *research-epic* — its Done-When item 1 commissions a ≥1500-word epic plan with ≥6 sources before MVP code lands. This design absorbs Plan/023's MVP scope (items 2, 3, 5, 6, 7, 8-basic — daemon lifecycle, single-binary CLI, MCP wire pass-through, bootstrap self-doc, smoke tests, basic docs) into the unified ladder so it can ship in parallel with L1+L2. **The research-epic items (1, 4 — prior-art survey + progressive-disclosure ladder design) are explicitly deferred** to a follow-up sub-spec `Plan/harness/L3-progressive-disclosure.md` that will resume the research subagents A/B/C. Plan/023's transport decision (Streamable HTTP, UDS fallback) is preserved verbatim; this design does not re-research transport.

**Token caps**: Boot context < 500 tokens, tools/list < 4 KB, per-tool result ≤ 4 KB.

## 3. L1 — in-memory FastMCP

### 3.1 Module layout

```
tests/
├── _harness/
│   ├── __init__.py        # re-exports: harness_mcp, call_tool, list_tools, load_skill, dispatch_skill, REPO_ROOT
│   ├── mcp.py             # FastMCP in-memory plumbing
│   └── skills.py          # SKILL.md parsing + dispatch resolver
└── conftest.py            # pytest fixtures wrapping _harness
```

The `tests/_harness/` package is **not** part of the plugin; it lives under `tests/` because it is test infrastructure. The plugin's `agency-mcp` server is its *subject under test*, not a dependency.

### 3.2 Public API (the four-verb contract)

The four verbs are the same conceptual surface the L2 probe and the L3 daemon expose. The L1 form is async because FastMCP's transport is async:

```python
# tests/_harness/mcp.py

import asyncio
from functools import lru_cache
from agency_mcp.server import create_mcp


@lru_cache(maxsize=1)
def harness_mcp():
    """Return the singleton FastMCP instance, booted once per pytest session.

    Cached because create_mcp() registers 114 tools + the ContextWatcher
    thread; booting per-test would dominate runtime and risk watcher
    race conditions across tests.
    """
    return create_mcp()


async def list_tools(*, domain: str | None = None) -> list[dict]:
    """L1 verb 1 — list tool stubs.

    Domain filter (e.g. 'music', 'novel', 'jules', 'context', 'shared')
    matches the same `domain:<x>` tag the existing handler-smoke tests use
    (tests/unit/jules/test_handlers_smoke.py:11-15).
    """
    tools = await harness_mcp().list_tools()
    if domain is None:
        return [{"name": t.name, "tags": list(t.tags or [])} for t in tools]
    needle = f"domain:{domain}"
    return [
        {"name": t.name, "tags": list(t.tags or [])}
        for t in tools
        if needle in (t.tags or set())
    ]


async def call_tool(name: str, **kwargs) -> dict:
    """L1 verb 2 — invoke a tool through FastMCP's in-memory transport.

    Returns the parsed JSON body (the test in
    tests/integration/test_context_anchor_triad.py:21 documents the
    ToolResult.content[0].text wire-format we unwrap here).

    Raises HarnessError if the tool isn't registered, the call raises
    inside the handler, or the response is not JSON-parseable.
    """
    import json
    result = await harness_mcp().call_tool(name, kwargs)
    # ToolResult envelope (see test_context_anchor_triad.py:21)
    try:
        return json.loads(result.content[0].text)
    except (AttributeError, IndexError, json.JSONDecodeError) as exc:
        raise HarnessError(f"call_tool({name}) returned non-JSON: {exc}") from exc
```

```python
# tests/_harness/skills.py

import re
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_ROOT = REPO_ROOT / "skills"


def list_skills(*, domain: str | None = None) -> list[dict]:
    """L1 verb 3 — list skill stubs."""
    out = []
    for skill_md in SKILLS_ROOT.rglob("SKILL.md"):
        meta = _frontmatter(skill_md)
        if domain is not None and not meta.get("name", "").startswith(f"{domain}-"):
            continue
        out.append({"path": str(skill_md.relative_to(REPO_ROOT)), "name": meta.get("name"), "description": meta.get("description")})
    return out


def dispatch_skill(name: str) -> dict:
    """L1 verb 4 — resolve a skill name to its SKILL.md path + body.

    Does NOT execute the skill (skills are instructions for an LLM, not
    executable code). It proves *routing*: that the name resolves to a
    real file with a parseable frontmatter and a non-empty body.
    """
    for skill_md in SKILLS_ROOT.rglob("SKILL.md"):
        meta = _frontmatter(skill_md)
        if meta.get("name") == name:
            body = skill_md.read_text().split("---", 2)[-1].lstrip()
            return {"name": name, "path": str(skill_md.relative_to(REPO_ROOT)), "frontmatter": meta, "body": body}
    raise HarnessError(f"skill '{name}' not found under {SKILLS_ROOT}")


_FM_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
def _frontmatter(path: Path) -> dict:
    m = _FM_RE.match(path.read_text())
    return yaml.safe_load(m.group(1)) if m else {}
```

### 3.3 Pytest fixtures (the on-ramp)

```python
# tests/conftest.py

import pytest
import pytest_asyncio
from tests._harness.mcp import harness_mcp, list_tools, call_tool
from tests._harness.skills import list_skills, dispatch_skill, REPO_ROOT


@pytest.fixture(scope="session")
def mcp():
    """Boot create_mcp() once for the whole pytest run."""
    return harness_mcp()


@pytest_asyncio.fixture
async def tool():
    """Inject the call_tool verb — `await tool("music_find_album", title="X")`."""
    return call_tool


@pytest_asyncio.fixture
async def tools():
    """Inject the list_tools verb — `await tools(domain="music")`."""
    return list_tools


@pytest.fixture
def skill():
    """Inject the dispatch_skill verb."""
    return dispatch_skill
```

### 3.4 First user — retrofit PR #115's smoke test

After L1 lands, `tests/smoke/test_dev_install.py` reduces to (replacing the brittle `claude plugin validate` stdout grep):

```python
import json
from tests._harness.mcp import harness_mcp
from tests._harness.skills import REPO_ROOT


def test_manifest_is_agency_system():
    manifest = json.loads((REPO_ROOT / ".claude-plugin" / "plugin.json").read_text())
    assert manifest["name"] == "agency-system"
    assert "version" in manifest  # loosened per Codex P2 r3262361932 — no version-prefix gate


@pytest.mark.asyncio
async def test_plugin_boots_114_tools():
    """Closes Codex P1 r3262361939 — actually exercises boot, not just schema."""
    mcp = harness_mcp()
    tools = await mcp.list_tools()
    assert len(tools) >= 113, f"expected ≥113 tools, got {len(tools)}"
```

Both Codex critiques on PR #115 resolve in one step.

### 3.5 Why an L1 harness is the right abstraction (not a one-off helper)

- **Repeated 3× already.** [`test_context_anchor_triad.py:7`](../../tests/integration/test_context_anchor_triad.py), [`test_handlers_smoke.py:7-10`](../../tests/unit/jules/test_handlers_smoke.py), and [`test_boot.py`](../../tests/smoke/test_boot.py) each open with the same boot boilerplate via three different patterns.
- **Phase 1's next two smoke tests will do it again.** Spec 131 (`test_boot_budget.py`) needs the same boot to assert `tools/list` < 4 KB; Spec 105 (`test_toon_gate.py`) needs the same boot to assert TOON gating on homogeneous list returns.
- **In-session dogfooding.** A dev or agent editing a handler in this very session can `python -m pytest tests/smoke/<spec> -x` and exercise the plugin's real tool surface — without restarting Claude Code.

### 3.6 Resource and ContextWatcher considerations

`create_mcp()` starts a daemon thread (`ContextWatcher`, [`lib/codemode/context_watcher.py:17-168`](../../servers/agency-mcp/src/agency_mcp/lib/codemode/context_watcher.py)) that polls Plan/_lessons-learned/_overrides/_reference paths every 5 seconds. Booting per-pytest-session (the `harness_mcp` lru-cache) means **one** watcher per run, not one per test. A `pytest-finalize` hook in `conftest.py` calls `watcher.stop()` to keep CI clean.

If the watcher's poll loop interferes with tests that mutate Plan/_lessons-learned/ files (none today), a future `harness_mcp(watcher=False)` knob can be added — out of scope for L1 v1.

**Cold-boot vs warm-singleton.** Spec 131's `tests/smoke/test_boot_budget.py` measures `tools/list` payload at cold boot. The harness's lru-cache singleton returns a warm instance after the first call, which may differ from cold (FastMCP may lazy-load schemas on first list). Two mitigations land with L1:

1. `harness_mcp.cache_clear()` exposed as a helper so cold-boot tests can force a fresh boot — `Spec 131` runs `cache_clear()` then `harness_mcp()` to measure cold.
2. A `cold_mcp()` fixture (separate from `mcp`) that always returns a fresh instance, for tests that need repeated cold measurements.

If both prove insufficient, the L2 subprocess probe (§4) is the fallback — that's the strict cold-boot oracle (`subprocess.run([sys.executable, "-c", "from agency_mcp.server import create_mcp; ..."])`).

### 3.7 Isomorphism across the five domains

The codebase has five domains (music, novel, jules, context, shared) plus an `agentic` skill-only domain. A 2026-05-18 audit (`_research/05-domain-isomorphism.md`) scored their cross-domain uniformity at **6/10** today, identifying five concrete strains the four-verb contract has to handle. L1 closes them with two normalisation passes plus three documented conventions; the deeper "restructure for native isomorphism" question — and which parts to land before this design's tag — is treated in §11 below.

| Strain (audit §3) | L1 response |
|---|---|
| Strain 1 — Complex parameter expressions (`music_master_album` has 6+ kwargs) | L1's `call_tool(name, **kwargs)` is naturally typed via Python. No special handling needed. (L3's CLI handles via `--json '{...}'` escape hatch — see §5.) |
| Strain 2 — Non-JSON binary returns (`music_transcribe_audio` returns a path) | `call_tool` returns the JSON envelope verbatim — the path string is the body. Callers that need the binary fetch separately. Documented in §6 "Out of scope". |
| Strain 3 — Skill-schema divergence (music has `model`/`allowed-tools`, jules doesn't) | `dispatch_skill(name)` returns the full parsed frontmatter dict. Callers tolerate optional fields being absent (use `frontmatter.get("model")`, not `frontmatter["model"]`). A future Phase 1 sibling spec `test_skill_schema.py` enforces required-field contract across all 58 SKILL.md files. |
| Strain 4 — Session-state dependency chains (`music_update_track_field` requires cache warmth) | `harness_warm(domain)` helper added to L1's public API — triggers domain-specific cache bootstrap (e.g. `music_list_albums()` for music). Tests document required call sequences. For L3, the daemon's process lifetime preserves cache across CLI invocations until `agency server stop`. |
| Strain 5 — Domain-classifier divergence (context tagged `domain:cross`; novel has 56 handlers but **zero manifest entries**; shared has tag-less `@mcp.tool`) | **Two normalisation passes shipped in `tests/_harness/normalisation.py`:**<br>① `list_tools(domain="X")` queries `mcp.list_tools()` (the FastMCP authoritative source) and filters by tag — `domain:novel` returns the 56 handlers even though manifest.json is empty for novel. A no-tag tool falls back to `domain:shared`.<br>② `dispatch_skill` returns the full parsed frontmatter so callers can tolerate optional fields explicitly. |

**Why `mcp.list_tools()` is the source of truth.** Every registered tool — including bare `@mcp.tool` decorators and `mcp.tool(...)(fn)` post-wraps — appears in `mcp.list_tools()`. The manifest.json file is the *CodeMode anchor/deferred classification cache*, not the registration ledger. Treating it as the registration ledger is what produces the novel "phantom domain" effect. The harness consults manifest only for the boolean "is this an eager anchor?" question, never for "which tools exist?"

**Module location.** The two normalisation passes live in `tests/_harness/normalisation.py` (≤80 lines): `resolve_domain(tool)`, `tools_by_domain(mcp, domain)`, `parse_skill_frontmatter(path)`. L1's `list_tools` / `dispatch_skill` verbs delegate to these helpers.

**Post-design uniformity score.** With L1's two normalisations in place and §11's low-cost restructures landed, the score lifts from 6/10 to 9/10. The remaining 1/10 (full schema enforcement + binary-envelope standardisation) is named in §11 as follow-up work.

## 4. L2 — subprocess probe

### 4.1 The probe

```python
# tests/smoke/test_nested_claude.py

import subprocess
import pytest
from tests._harness.skills import REPO_ROOT


@pytest.fixture
def claude_on_path():
    if subprocess.run(["which", "claude"], capture_output=True).returncode != 0:
        pytest.skip("claude CLI not on PATH — L2 probe is opt-in for CI with claude installed")


def test_nested_claude_loads_plugin(claude_on_path):
    """L2 — the real `claude --plugin-dir <repo>` boot path closes Spec 022.1.

    Uses `--bare` to skip default plugin loading + auto-memory, ensuring the
    only plugin in scope is the one we explicitly pass via --plugin-dir.
    `-p` makes the call non-interactive; the prompt is intentionally trivial
    because we are testing PLUGIN LOAD, not chat behaviour.
    """
    result = subprocess.run(
        [
            "claude", "--bare",
            "--plugin-dir", str(REPO_ROOT),
            "--disable-slash-commands",  # eliminates the /help → chat-routing flake from the old test
            "--debug", "plugins",         # surfaces plugin load events to stderr deterministically
            "-p", "exit",
        ],
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, f"claude exited {result.returncode}\nstderr:\n{result.stderr[-2000:]}"
    # Plugin name appears in the debug-plugin log emitted at startup; this is
    # deterministic regardless of which model responds to the trivial prompt.
    combined = result.stdout + "\n" + result.stderr
    assert "agency-system" in combined, (
        "agency-system plugin did not load via --plugin-dir\n"
        f"stdout: {result.stdout[-500:]}\n"
        f"stderr: {result.stderr[-500:]}"
    )
```

### 4.2 Why `--bare` + `--debug plugins` instead of `/help`

The original test used `claude --plugin-dir <repo> /help` and grepped for `"agency-system"`. PR #115's investigation surfaced two failure modes:

1. **`/help` is a chat prompt, not a CLI command.** It triggers the model to respond, and the response depends on whatever default plugin's help routing handles `/help` first. In a session with `bitwize-music` enabled, the response described that plugin instead of the agency-system one.
2. **No deterministic "did the plugin load" signal in chat output.** The model may or may not name plugins in its response.

`--bare` skips defaults (and explicitly mentions plugin sync in its docs: *"Minimal mode: skip hooks, LSP, plugin sync, attribution, auto-memory..."*). Combined with `--debug plugins` (per `claude --help`: *"Enable debug mode with optional category filtering"*), the plugin-load events land on stderr deterministically, and `--plugin-dir` is the only thing introducing plugins into the run. The probe checks the load event, not the chat output.

### 4.3 Cost and runtime guard

The probe spawns a real Claude session and consumes API tokens for the trivial prompt. Three controls:

1. **`@pytest.mark.smoke_slow`** marker so the L2 test can be excluded from the fast loop with `pytest -m "not smoke_slow"`.
2. **Skip gracefully** when `claude` is not on PATH (CI without the CLI installed stays green).
3. **Cap at 60 s timeout** — generous for cold model load + the `exit` prompt round-trip.

In CI with the `claude` CLI installed, the probe adds one nested session per run. The L1 in-process harness is the fast path; L2 is the boot-fidelity backstop.

## 5. L3 — sidecar daemon + bin/agency CLI

### 5.1 Why daemon + CLI (and not just "MCP server in subprocess")

External agents (Jules sandbox, Cursor, Codex CLI, raw bash + LLM) need three things at once:

1. A **long-lived** plugin endpoint — spawning the MCP server per call has cold-boot cost (∼3-5 s for `create_mcp()` to register 114 tools and start the watcher thread, see `_research/01-fastmcp-in-memory.md` §3).
2. A **shell-friendly** invocation surface — agents talk to bash, not to JSON-RPC libraries. The CLI translates `agency tool execute <name> --param x=y` into the JSON-RPC call.
3. A **discoverable** entry point — `agency --bootstrap` prints ≤60 lines of self-documenting usage so a first-touch agent can use the plugin without prior knowledge.

The daemon (a FastMCP server in Streamable-HTTP transport mode) and the CLI (a Python `argparse`-based binary) are the answer to all three. They reuse `agency_mcp.server.create_mcp()` — the same factory L1 imports — so the tool surface stays identical across all three layers.

### 5.2 Module layout

```
bin/
└── agency                                # single-binary CLI (executable, Python, argparse)

servers/agency-mcp/src/agency_mcp/lib/devmode/
├── __init__.py                           # re-exports: run_dev_transport, lifecycle helpers
├── server.py                             # run_dev_transport(transport, host, port) — wraps create_mcp().run()
├── lifecycle.py                          # PID file + log rotation + graceful shutdown
└── discovery.py                          # tool search/describe/execute (anchor-surface mirror of Spec 104)

docs/architecture/
└── harness-in-harness.md                 # ≤300 lines — describes all three layers, security boundary, transport rationale

tests/integration/
└── test_devmode_server.py                # daemon lifecycle + tool execute round-trip
```

**Same `create_mcp()` factory, three transports on top of it** (design.md:393).
The daemon lives **inside the existing MCP server package** (`servers/agency-mcp/src/agency_mcp/lib/devmode/`) rather than as a sibling — this preserves the single-source-of-truth invariant (one `create_mcp()` factory, three transports on top of it). The CLI binary at `bin/agency` is the only new top-level entry point.

### 5.3 The four-verb contract over HTTP JSON-RPC

L3 exposes the same four verbs as L1, mapped onto FastMCP's Streamable HTTP transport. The CLI subcommands are thin wrappers over the JSON-RPC calls:

| Verb (L1) | L3 CLI | L3 wire (MCP JSON-RPC) |
|---|---|---|
| `list_tools(domain=None)` | `agency tool search [--domain X]` | `tools/list` (filtered server-side by tag) |
| `call_tool(name, **kwargs)` | `agency tool execute <name> [--param k=v ...]` | `tools/call` |
| `list_skills(domain=None)` | `agency skill list [--domain X]` | `tools/call agency_skill_list {domain}` (a meta-tool registered in `lib/devmode/discovery.py`) |
| `dispatch_skill(name)` | `agency skill describe <name>` | `tools/call agency_skill_describe {name}` |

`tools/list` and `tools/call` are the standard MCP JSON-RPC methods — any third-party MCP client (Cursor, Continue, Cline) can connect to the daemon and use the same surface. The CLI is a thin transport-layer convenience, not a custom protocol.

### 5.4 Daemon lifecycle

`bin/agency server` exposes four subcommands:

```bash
agency server start        # spawns the FastMCP HTTP server in the background.
                           # writes PID to ~/.agency-system/dev-server.pid
                           # writes logs to ~/.agency-system/dev-server.log
                           # binds 127.0.0.1:7777 (configurable via --port)
                           # idempotent: a second `start` while running prints
                           #   "already running, PID <int>" and exits 0.

agency server stop         # sends SIGTERM to the PID, waits ≤10s for clean
                           # shutdown, removes the PID file. Exits 0 on success,
                           # 1 on PID-not-found or shutdown timeout.

agency server status       # exit 0 + JSON {running, pid, port, uptime_seconds}
                           # if alive; exit 1 + JSON {running: false} otherwise.

agency server logs [-f]    # tails ~/.agency-system/dev-server.log; -f follows.
```

The daemon is **localhost-only** (binds 127.0.0.1, not 0.0.0.0) and **single-user** (no auth). The PID file at `~/.agency-system/dev-server.pid` is the lock — `agency server start` refuses to spawn a second daemon if it sees a live PID. Stale PIDs (process gone) are cleaned up and the start proceeds.

### 5.5 Bootstrap self-doc

`agency` (zero args) or `agency --bootstrap` prints ≤60 lines of self-documenting usage. This is **the contract** for any first-touch agent — a Jules session reading the output should be able to use the plugin without prior knowledge:

```
agency — agency-system plugin CLI

  agency server start | stop | status | logs [-f]
      Run the agency-system MCP daemon. localhost:7777, single-user.

  agency tool search [--domain music|novel|jules|context|shared]
      List tools by domain. Output: JSON list of {name, summary, tags}.

  agency tool describe <name>
      Full schema for one tool. Output: JSON {name, description, inputSchema}.

  agency tool execute <name> [--param key=value ...] [--json '{...}']
      Invoke a tool. Output: JSON result body.

  agency skill list [--domain music|novel|jules|agentic]
      List skills (name + summary).

  agency skill describe <name>
      Full frontmatter + body of a skill (parseable for downstream agents).

Examples:
  agency server start && agency tool search --domain music
  agency tool execute health_check
  agency tool execute music_find_album --param title="Black Mirror"
  agency skill describe music-lyric-writer

Docs: docs/architecture/harness-in-harness.md
```

### 5.6 MVP scope (what ships, what defers)

The L3 MVP under this design ships **Plan/023 Done-When items 2, 3, 5, 6, 7, 8-basic**:

| Plan/023 item | L3 status | Notes |
|---|---|---|
| 1. Research output (epic plan ≥1500 words) | **Deferred** to `Plan/harness/L3-progressive-disclosure.md` (follow-up sub-spec) | Plan/023's Subagents A (prior art) and B (anchor surface) re-run there. Subagent D (transport) result locked verbatim into §2 above. |
| 2. MVP daemon (`agency server start/stop/status/logs`) | **Ships** | §5.4 above |
| 3. Single-binary CLI (`bin/agency`) | **Ships** | §5.2-5.3 above |
| 4. Progressive disclosure for skills (4-tier ladder) | **Deferred** to `Plan/harness/L3-progressive-disclosure.md` | Initial `agency skill list/describe` provides a 2-tier baseline; 4-tier requires Subagent C output |
| 5. MCP wire-format pass-through | **Ships** | Built-in via FastMCP HTTP transport — Cursor / Continue / Cline can connect directly |
| 6. Bootstrap self-doc | **Ships** | §5.5 above |
| 7. Smoke tests (`tests/integration/test_devmode_server.py`) | **Ships** | Daemon lifecycle + one tool execute round-trip |
| 8. `docs/architecture/harness-in-harness.md` | **Ships (basic)** | Architectural overview + transport + security boundary. Progressive-disclosure section deferred. |

The deferred items (1, 4) are pure additions — they will not require rework of the MVP. The 2-tier baseline (`list` returns `{name, summary}`; `describe` returns frontmatter + body) is forward-compatible with a 4-tier expansion (`--tier N` flag added later).

### 5.7 Security boundary

| Concern | Decision | Rationale |
|---|---|---|
| Network reach | `127.0.0.1` only (loopback) | External-agent use case is local-only; remote access is a follow-up spec |
| Authentication | None | Single-user. Daemon trusts anything that can connect to 127.0.0.1:7777 |
| Process lifetime | Tied to parent shell via PID file + atexit hook | A killed parent leaves a stale PID file; `agency server start` cleans it up |
| Tool-call audit | Logs every invocation to `~/.agency-system/dev-server.log` | Sufficient for dev / dogfooding; production-grade audit is out of scope |
| Untrusted-input handlers | Same trust boundary as the in-Claude-Code plugin (i.e., trusted) | The plugin handlers were authored against MCP-trusted input; L3 inherits that assumption. Adding untrusted-input gates is a follow-up spec, not this one. |

### 5.8 Isomorphism across the five domains (L3 side)

L3's CLI mirrors L1's normalisation passes (§3.7):

- `agency tool search [--domain X]` walks `mcp.list_tools()` server-side and filters by tag — returns novel's 56 tools regardless of manifest.json gaps.
- `agency tool execute <name> [--param k=v ...] [--json '{...}']` handles complex parameter expressions via the `--json` escape hatch (Strain 1).
- Binary returns (Strain 2): the CLI prints the JSON path/metadata; a follow-up `agency file get <path>` verb (deferred to L3 progressive-disclosure sub-spec) serves the binary.
- `agency skill describe <name>` returns the full parsed frontmatter as JSON; callers tolerate optional fields. Same convention as L1 (Strain 3).
- Session state (Strain 4): the daemon's process lifetime preserves the StateCache across CLI calls. `agency tool execute <domain>_warm` is the explicit warm verb where needed.

### 5.9 In-session bash dogfooding (the orchestrator's own use case)

Once L3 is running, the **orchestrator session itself** (this one — a Claude Code session with the `Bash` tool) can invoke the plugin's tools via the CLI:

```bash
# In any Bash tool call:
agency server start
agency tool execute health_check
agency tool execute music_find_album --param title="X"
agency skill describe music-lyric-writer
```

This means the dev / agent iterating on the plugin **doesn't need to restart Claude Code at all** to verify their changes — L3 + a `agency server stop && agency server start` reload-cycle is faster than `--plugin-dir` restart, and works inside the existing session. This is the highest-leverage cross-layer win: **L3 makes L1's "dev-iteration loop" work even for non-pytest verification.**

## 6. Out-of-scope

- **Skill execution semantics.** `dispatch_skill` (L1) and `agency skill describe` (L3) prove routing (name → file → frontmatter + body) but do not interpret skills — skills are LLM instructions, not executable code. A "skill simulator" that runs a skill's process inside the harness is a future extension.
- **Hot-reload of `--plugin-dir` into an already-running Claude Code session.** Not possible per the CLI's architecture; L1 + L3 are the workarounds.
- **Spec 131 (`test_boot_budget.py`)** and **Spec 105 (`test_toon_gate.py`)** *use* this harness but are not authored here — they remain Phase 1 tickets owned by their respective specs.
- **Whether the L2 probe runs in default CI** — left for the CI config PR. Default expectation: opt-in via `pytest -m smoke_slow`.
- **L3 progressive-disclosure 4-tier ladder for skills.** Deferred to `Plan/harness/L3-progressive-disclosure.md`. The MVP exposes a 2-tier baseline (`list` + `describe`) that's forward-compatible.
- **Authentication / multi-tenant access for L3.** Daemon is localhost-only, single-user. Auth is a follow-up spec only if remote access is ever desired.
- **Windows compatibility for L3.** POSIX-only (Linux + macOS). Windows uses WSL. (Same exclusion Plan/023 took.)
- **Cross-machine federation of L3 daemons.** Out of scope. The daemon owns one repo's plugin instance only.

## 7. Done-When (acceptance criteria)

### L1 — In-process harness

- [ ] `tests/_harness/__init__.py`, `tests/_harness/mcp.py`, `tests/_harness/skills.py` exist with the four-verb API (`list_tools`, `call_tool`, `list_skills`, `dispatch_skill`) plus `harness_mcp()` and `REPO_ROOT`.
- [ ] `tests/conftest.py` exposes the four verbs as pytest fixtures (`tool`, `tools`, `skill`, `mcp`).
- [ ] `tests/smoke/test_dev_install.py` is refactored to use `harness_mcp()`; both Codex P2 critiques (r3262361932 + r3262361935) resolved by removing the `0.`-prefix gate and the `"passed"` substring gate; the Codex P1 critique (r3262361939) resolved by asserting `len(tools) >= 113` via the L1 harness.
- [ ] `pytest tests/smoke/ -v` runs cleanly inside a fresh `bin/agency-dev-install` env, with the L1 tests in the fast group.

### L2 — Subprocess probe

- [ ] `tests/smoke/test_nested_claude.py` exists with the `--bare --plugin-dir <repo> --debug plugins -p exit` probe, marked `@pytest.mark.smoke_slow`, gracefully skipping when `claude` is not on PATH.

### L3 — Sidecar daemon + CLI

- [ ] `bin/agency` is an executable Python script (`#!/usr/bin/env python3` + argparse) implementing the subcommands in §5.5: `server start|stop|status|logs`, `tool search|describe|execute`, `skill list|describe`, and zero-arg / `--bootstrap` self-doc.
- [ ] `servers/agency-mcp/src/agency_mcp/lib/devmode/server.py` exposes `run_dev_transport(transport: str = "http", host: str = "127.0.0.1", port: int = 7777)` that calls `create_mcp().run(transport=..., host=..., port=...)`. Same `create_mcp()` factory L1 uses — no fork.
- [ ] `servers/agency-mcp/src/agency_mcp/lib/devmode/lifecycle.py` provides PID-file management (`~/.agency-system/dev-server.pid`), log file management (`~/.agency-system/dev-server.log` with size-based rotation at 10 MB), and the `start_idempotent` / `stop_graceful` / `status` helpers `bin/agency server` wraps.
- [ ] `agency server start` is idempotent: a second start while running prints `already running, PID <int>` and exits 0. Stale PID file (no live process) is cleaned and start proceeds.
- [ ] `agency server stop` sends SIGTERM, waits ≤10s for clean shutdown, then SIGKILL if needed. Removes PID file on success.
- [ ] `agency server status` exits 0 + JSON `{running, pid, port, uptime_seconds}` when alive, exits 1 + JSON `{running: false}` otherwise. JSON shape is the contract for downstream agents parsing the output.
- [ ] `agency tool execute health_check` round-trips via the daemon and returns the same JSON body `harness_mcp().call_tool("health_check")` returns (L1 ↔ L3 equivalence). Tested in `tests/integration/test_devmode_server.py`.
- [ ] `agency --bootstrap` prints ≤60 lines, names every subcommand, includes one runnable example per subcommand, references `docs/architecture/harness-in-harness.md`.
- [ ] `tests/integration/test_devmode_server.py` covers: idempotent start, graceful stop, status JSON shape, one tool execute round-trip. Uses `tmp_path` for PID/log paths to avoid stomping on a real dev daemon.
- [ ] `docs/architecture/harness-in-harness.md` exists (≤300 lines): all three layers, security boundary, transport rationale (linking Plan/023 §Approach pre-research), in-session bash dogfooding cookbook (§5.8 above), example invocations for each subcommand.
- [ ] **Forward-compatibility evidence:** `agency skill list` returns `[{name, summary}]`; `agency skill describe <name>` returns frontmatter + body. The deferred 4-tier expansion adds `--tier N`; existing call sites without `--tier` get tier-2 (current default). No breaking change.

### Cross-layer

- [ ] `Plan/harness/_research/{01-fastmcp-in-memory, 02-claude-bare-plugin-dir, 03-test-coverage-baseline, 04-fastmcp-http-transport}.md` all exist (≤200 lines each).
- [ ] PR #115 description reflects all three layers (or work splits cleanly across PRs at the orchestrator's discretion).
- [ ] Plan/000-overview.md §2.1 lists this design with PR references once merged. The reference points to L1+L2 under Phase 1 and L3 under Phase 8.
- [ ] Plan/023-harness-in-harness/spec.md is updated with a `superseded_by: Plan/harness/design.md` marker for items 2-3-5-6-7-8 and a `defers_to: Plan/harness/L3-progressive-disclosure.md` marker for items 1-4.

## 8. Gherkin acceptance anchors

```gherkin

# anchor: harness.matrix.iso
Scenario: L1 vs L3 returns identical payloads for the same verb
  Given the same tool and parameters
  When an L1 mcp__call_tool against mcp__<row>_start is executed
  And an L3 daemon `agency tool execute mcp__<row>_start` is executed
  Then they return the exact same body payload
# anchor: harness.L1.1
Scenario: In-process harness boots create_mcp() once per pytest session
  Given a pytest session starts in tests/
  When two tests each request the `mcp` fixture
  Then both receive the same FastMCP instance
  And create_mcp() was called exactly once
  And the ContextWatcher daemon thread is started exactly once

# anchor: harness.L1.2
Scenario: call_tool invokes the real handler through FastMCP's in-memory transport
  Given the harness is booted
  When a test calls `await tool("context_search", query="dramatica", limit=5)`
  Then the response is the parsed JSON list from context_search's handler
  And the call did NOT spawn an stdio subprocess
  And the response shape matches what tests/integration/test_context_anchor_triad.py asserts

# anchor: harness.L1.3
Scenario: dispatch_skill resolves a name to a real SKILL.md
  Given the skills tree at /home/user/the-agency-system/skills/
  When a test calls `skill("music-session-start")`
  Then the response is {name, path, frontmatter, body}
  And the path resolves to skills/music/session-start/SKILL.md
  And the frontmatter contains a non-empty `description:` field

# anchor: harness.L1.4
Scenario: PR #115's smoke test resolves with the harness
  Given tests/smoke/test_dev_install.py is refactored to use harness_mcp()
  When `pytest tests/smoke/test_dev_install.py -v` runs
  Then the manifest test does not depend on version-prefix
  And the boot test asserts ≥113 tools via list_tools(), not via stdout grep
  And all three Codex critiques on PR #115 are resolved

# anchor: harness.L2.1
Scenario: Nested claude probe loads the plugin via --plugin-dir
  Given `claude` is on PATH in CI
  When the probe runs `claude --bare --plugin-dir <repo> --debug plugins -p exit`
  Then the subprocess exits 0 within 60s
  And the combined stdout+stderr contains "agency-system"
  And the test passes deterministically across runs

# anchor: harness.L2.2
Scenario: Nested claude probe is skipped when claude is not on PATH
  Given `claude` is NOT on PATH
  When the probe runs
  Then pytest records the test as skipped
  And the CI build stays green

# anchor: harness.L3.1
Scenario: L3 daemon lifecycle is idempotent
  Given the daemon is not running
  When the operator runs `agency server start`
  Then exit 0 and a PID file appears at ~/.agency-system/dev-server.pid
  And `agency server status` returns exit 0 + JSON {running: true, pid: <int>, port: 7777, uptime_seconds: <int>}
  When the operator runs `agency server start` again
  Then exit 0 and stderr contains "already running, PID <int>"
  And no second process is spawned
  When the operator runs `agency server stop`
  Then exit 0 and the PID file is removed
  And `agency server status` returns exit 1 + JSON {running: false}

# anchor: harness.L3.2
Scenario: L3 tool execute round-trips against the daemon
  Given the daemon is running
  When the operator runs `agency tool execute health_check`
  Then exit 0 and stdout is the JSON body returned by the health_check handler
  And the same call via `harness_mcp().call_tool("health_check")` returns the same body (L1 ↔ L3 equivalence)

# anchor: harness.L3.3
Scenario: L3 is reachable from external MCP clients
  Given the daemon is running on 127.0.0.1:7777 with Streamable HTTP transport
  When an external MCP client (e.g. Cursor, Continue, Cline) connects and sends a `tools/list` JSON-RPC request
  Then the daemon responds with the full registered tool surface
  And a subsequent `tools/call` for `health_check` returns the same body `agency tool execute health_check` would produce

# anchor: harness.L3.4
Scenario: L3 bootstrap self-doc is the contract for new agents
  Given a first-touch agent has shell access and `bin/agency` on PATH but no prior knowledge of agency-system
  When the agent runs `agency --bootstrap` (or `agency` with no args)
  Then the output is ≤ 60 lines
  And the output names every subcommand from §5.5 above
  And the output includes one runnable example per subcommand
  And the output references docs/architecture/harness-in-harness.md
  And the agent can use the plugin's tools/skills using only the output as documentation

# anchor: harness.L3.5
Scenario: L3 makes in-session dogfooding possible without restarting Claude Code
  Given a Claude Code session is running with the Bash tool available
  And the operator has edited a handler under servers/agency-mcp/src/agency_mcp/handlers/
  When the operator runs `agency server stop && agency server start` in a Bash tool call
  And then runs `agency tool execute <the-edited-tool> --param ...`
  Then the response reflects the edited handler's new behaviour
  And no Claude Code restart was required
```

## 9. Evidence and references

| Claim | Source |
|---|---|
| `create_mcp()` returns a FastMCP instance named "agency-system" | `servers/agency-mcp/src/agency_mcp/server.py:99-106` |
| 114 tools registered | `servers/agency-mcp/src/agency_mcp/codemode/manifest.json` (`jq '.tools \| length'`) |
| FastMCP's in-memory invocation is `await mcp.call_tool(name, params)` returning `ToolResult.content[0].text` | `tests/integration/test_context_anchor_triad.py:7-21` |
| Handler-isolated smoke pattern (FastMCP + `register_<domain>_handlers`) | `tests/unit/jules/test_handlers_smoke.py:7-10` |
| ContextWatcher is a daemon thread polling every 5s | `servers/agency-mcp/src/agency_mcp/lib/codemode/context_watcher.py:17-75` |
| 58 SKILL.md files; namespace prefix is auto-prepended by Claude Code (not by `name:`) | parallel-agent audit, this PR (see §1 of `_research/03-test-coverage-baseline.md`) |
| `claude --bare` skips default plugin sync | `claude --help` output: *"Minimal mode: skip hooks, LSP, plugin sync, attribution, auto-memory..."* |
| `claude --debug plugins` filters debug output to the plugins category | `claude --help`: `-d, --debug [filter]   Enable debug mode with optional category filtering (e.g., "api,hooks" or "!1p,!file")` |
| Existing smoke test uses non-deterministic `/help` chat probe | `tests/smoke/test_dev_install.py` pre-PR-115 + PR #115 investigation comment |
| Plan/000-v2 places this work in Phase 1 | `Plan/000-overview.md` §4 + §9 Phase 1 dispatch matrix |
| FastMCP supports Streamable HTTP transport with `mcp.run(transport="http", host=..., port=...)` | FastMCP docs (cited in `_research/04-fastmcp-http-transport.md`) + Plan/023 §Approach pre-research |
| Transport choice locked: Streamable HTTP default, UDS fallback | `Plan/023-harness-in-harness/spec.md` §Approach "Pre-research finding (locked 2026-05-18)" |
| External MCP clients (Cursor, Continue, Cline) speak MCP JSON-RPC over HTTP | MCP 2025-06-18 spec — cited in Plan/023 |

## 10. Migration notes

- [FastMCP Client transports — in-memory](https://gofastmcp.com/clients/transports#in-memory-transport)
- [FastMCP Server transports](https://gofastmcp.com/servers/transports) — Streamable HTTP for L3
- [FastMCP deployment](https://gofastmcp.com/deployment/running-server)
- [MCP 2025-06-18 spec — transports](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)
- [Claude Code Plugins Reference](https://code.claude.com/docs/en/plugins-reference) — `--plugin-dir` semantics
- [Claude Code Plugins docs](https://code.claude.com/docs/en/plugins) — `--bare` and `--debug` flags
- [`Plan/JULES_PROTOCOL.md`](../JULES_PROTOCOL.md) §3 (branch/PR discipline), §8 (silent-fail recovery)
- [`Plan/JULES-REVIEW-LOOP.md`](../JULES-REVIEW-LOOP.md) §4.1 — review prompt template used for the first review pass on this design
- [`Plan/023-harness-in-harness/spec.md`](../023-harness-in-harness/spec.md) — origin of L3 design; this design absorbs items 2-3-5-6-7-8 and defers items 1-4

## 11. Path-A levers (active)

- **L-α** Unified `register(mcp)` per row. Status: active. Single entry point per domain. Anchor: `Plan/harness/design.md:861`.
- **L-β** `@domain_tool` decorator. Status: active. Standardised decorator macro. Anchor: `Plan/harness/design.md:841`.
- **L-γ** Manifest auto-sync at boot. Status: active. Regenerates manifest JSON at boot. Anchor: `Plan/harness/design.md:873`.

Path B (target tree, Domain base class) and deferred levers L-δ/ε/ζ/η + progressive disclosure 4-tier ladder are explicitly OUT of this spec. See `vision/specs/13-domain-isomorphism.md` for Path B and `vision/specs/14-progressive-disclosure-roadmap.md` for deferred levers.
