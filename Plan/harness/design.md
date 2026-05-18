---
slug: harness-in-harness-test
status: draft
owner: claude
depends_on: [022, 008, 112]
related: [023, 131, 105, 104]
phase: 1
affects:
  - Plan/harness/design.md
  - Plan/harness/_research/01-fastmcp-in-memory.md
  - Plan/harness/_research/02-claude-bare-plugin-dir.md
  - Plan/harness/_research/03-test-coverage-baseline.md
  - tests/_harness/__init__.py
  - tests/_harness/mcp.py
  - tests/_harness/skills.py
  - tests/conftest.py
  - tests/smoke/test_dev_install.py
  - tests/smoke/test_nested_claude.py
source-repos: []
estimated_jules_sessions: 2
domain: agentic
wave: B
spec_kind: design
---

> **Status:** draft 2026-05-18 by orchestrator session (Claude Code).
> **Working branch:** `claude/fix-pr-merge-issues-sn1CS`
> **Reference PR:** [#115](https://github.com/netzkontrast/the-agency-system/pull/115) — coordination point for all parallel sessions working on this.
> **Cross-link:** [PR #111](https://github.com/netzkontrast/the-agency-system/pull/111) (`Plan/000-overview.md` v2) places this design's deliverables in Phase 1 alongside specs 131, 105, 104, 107, 130.

# Harness in a Harness — Test-fidelity ladder for the agency-system plugin

## 1. Why

The `agency-system` plugin works inside a fresh Claude Code session via `claude --plugin-dir /home/user/the-agency-system`. But **any agent currently iterating on the plugin** — including the orchestrator sessions writing Phase 1 specs — has no way to dogfood the plugin's MCP tools and skills *from inside their own session*. `--plugin-dir` is a startup-only flag; in-flight sessions cannot hot-reload it. The result is a slow loop: edit handler → exit session → restart Claude Code with `--plugin-dir` → verify → repeat.

This same gap shows up in CI. `tests/smoke/test_dev_install.py` was the first attempt at a smoke test (Spec 022.1 anchor). Its initial `claude --plugin-dir <repo> /help` probe was non-deterministic — `/help` invokes the chat surface, so the returned text depends on whichever plugin responds first in the active session. PR #115's interim fix swapped it for `claude plugin validate`, which is deterministic but only validates the *manifest schema* — it does not exercise the real boot path. The Codex P1 critique on PR #115 names this gap explicitly ([discussion_r3262361939](https://github.com/netzkontrast/the-agency-system/pull/115#discussion_r3262361939)).

Plan/000-v2 (PR #111) commissions the next two Phase 1 smoke tests — `tests/smoke/test_boot_budget.py` (Spec 131) and `tests/smoke/test_toon_gate.py` (Spec 105) — but does not name the *shared harness* those tests will boot from. Every test that wants to instantiate `create_mcp()` and probe its 114-tool surface today re-implements the boilerplate; existing examples ([`tests/integration/test_context_anchor_triad.py:1-49`](../../tests/integration/test_context_anchor_triad.py), [`tests/unit/jules/test_handlers_smoke.py:1-26`](../../tests/unit/jules/test_handlers_smoke.py)) show three different invocation patterns for what should be one. No `tests/conftest.py` exists.

This design closes that gap with a single layered abstraction.

## 2. North star — three layers, one shared mental model

| Layer | Audience | Boots via | Cost / call | What it proves |
|---|---|---|---|---|
| **L1 In-process harness** | Pytest, Phase 1 spec tests, devs (human or agent) iterating in-session | `create_mcp()` Python import + FastMCP in-memory transport ([fastmcp.Client](https://gofastmcp.com/clients/transports#in-memory-transport)) | ms | Tools register, schemas valid, handlers callable, skills parseable, anchor-triad output well-formed |
| **L2 Subprocess probe** | CI smoke, PR-115 follow-up, real-boot regression coverage | `subprocess.run(["claude", "--bare", "--plugin-dir", repo, "-p", ...])` | seconds + API tokens | The actual `claude` CLI loads the plugin end-to-end via the real `--plugin-dir` path; manifest + MCP wiring + skill auto-discovery all hold together |
| **L3 Sidecar daemon** ([Plan/023](../023-harness-in-harness/spec.md)) | External agents (Cursor, Codex CLI, Jules sandbox, bash-only LLM harnesses) | `bin/agency server start` → JSON-RPC over Streamable HTTP | seconds, networked | Plugin is reachable from *any* shell-equipped harness, not just Claude Code |

**The contract all three layers share:** *list tools, call a tool, list skills, dispatch a skill.* That four-verb surface is the test-fidelity ladder's invariant. L1 fakes the transport; L2 fakes nothing but charges per call; L3 makes the running plugin reachable from outside Claude Code entirely. Each layer is independently shippable; this design covers L1 and L2 only. **L3 is unchanged and remains owned by Plan/023.**

## 3. L1 — In-process harness module

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

## 4. L2 — Subprocess probe

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

## 5. Out of scope

- **L3 sidecar daemon.** Owned by [Plan/023](../023-harness-in-harness/spec.md); no changes to that spec. L1 + L2 are sufficient for the immediate "dev iterates on plugin in-session" use case; L3 unlocks the *external-agent* use case which is Phase 8 work.
- **Skill execution semantics.** `dispatch_skill` proves routing (name → file → frontmatter + body) but does not interpret skills — skills are LLM instructions, not executable code. A "skill simulator" that runs a skill's process inside the harness is a future extension if anyone needs it.
- **Hot-reload of `--plugin-dir` into an already-running Claude Code session.** Not possible per the CLI's architecture; L1 is the workaround (use pytest to dogfood without restarting Claude Code).
- **Spec 131 (`test_boot_budget.py`)** and **Spec 105 (`test_toon_gate.py`)** *use* this harness but are not authored here — they remain Phase 1 tickets owned by their respective specs.
- **Whether the L2 probe runs in default CI** — left for the CI config PR. Default expectation: opt-in via `pytest -m smoke_slow`.

## 6. Done When

- [ ] `tests/_harness/__init__.py`, `tests/_harness/mcp.py`, `tests/_harness/skills.py` exist with the four-verb API (`list_tools`, `call_tool`, `list_skills`, `dispatch_skill`) plus `harness_mcp()` and `REPO_ROOT`.
- [ ] `tests/conftest.py` exposes the four verbs as pytest fixtures (`tool`, `tools`, `skill`, `mcp`).
- [ ] `tests/smoke/test_dev_install.py` is refactored to use `harness_mcp()`; both Codex P2 critiques (r3262361932 + r3262361935) resolved by removing the `0.`-prefix gate and the `"passed"` substring gate; the Codex P1 critique (r3262361939) resolved by asserting `len(tools) >= 113` via the L1 harness.
- [ ] `tests/smoke/test_nested_claude.py` exists with the `--bare --plugin-dir <repo> --debug plugins -p exit` probe, marked `@pytest.mark.smoke_slow`, gracefully skipping when `claude` is not on PATH.
- [ ] `pytest tests/smoke/ -v` runs cleanly inside a fresh `bin/agency-dev-install` env, with the L1 tests in the fast group and the L2 test in `smoke_slow`.
- [ ] `Plan/harness/_research/01-fastmcp-in-memory.md`, `_research/02-claude-bare-plugin-dir.md`, `_research/03-test-coverage-baseline.md` exist as evidence files (≤200 lines each).
- [ ] Reference PR #115 description is updated to reflect L1 + L2 scope (or this work splits cleanly to a new PR — orchestrator's choice).
- [ ] Plan/000-overview.md §2.1 lists this design under Phase 1 with PR reference once merged.

## 7. Acceptance scenarios (Gherkin)

```gherkin
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
```

## 8. Evidence (cited)

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

## 9. Out-of-tree references

- [FastMCP Client transports — in-memory](https://gofastmcp.com/clients/transports#in-memory-transport)
- [Claude Code Plugins Reference](https://code.claude.com/docs/en/plugins-reference) — `--plugin-dir` semantics
- [Claude Code Plugins docs](https://code.claude.com/docs/en/plugins) — `--bare` and `--debug` flags
- [`Plan/JULES_PROTOCOL.md`](../JULES_PROTOCOL.md) §3 (branch/PR discipline), §8 (silent-fail recovery)
- [`Plan/JULES-REVIEW-LOOP.md`](../JULES-REVIEW-LOOP.md) §4.1 — review prompt template used for the first review pass on this design

## 10. First review pass

The first review pass on this design uses the JULES-REVIEW-LOOP §4.1 template with `phase=1`, `spec=harness-design`, `spec_path=Plan/harness/design.md`. PR #115 is the working branch; the design doc + research files land there; a `@jules` review request posts in the PR thread. See the orchestrator's coordination comment on [PR #111](https://github.com/netzkontrast/the-agency-system/pull/111#issuecomment-4482634644).
