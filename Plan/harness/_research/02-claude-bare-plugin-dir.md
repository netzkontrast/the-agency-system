# Research 02 — `claude --bare --plugin-dir <path>` boot path

> **Question.** Is there a deterministic way for `tests/smoke/test_nested_claude.py` to assert "the agency-system plugin loaded" without depending on chat / model output?
> **Answer.** Yes — combine `--bare` (skip default plugin sync) with `--debug plugins` (deterministic plugin-load events on stderr) and a trivial `-p exit` prompt.

## 1. The flags we rely on

From `claude --help` (Claude Code CLI in this sandbox):

```
--bare                  Minimal mode: skip hooks, LSP, plugin sync, attribution,
                        auto-memory, background prefetches, keychain reads, and
                        CLAUDE.md auto-discovery. Sets CLAUDE_CODE_SIMPLE=1. […]
                        Skills still resolve via /skill-name. Explicitly provide
                        context via: --system-prompt[-file], --append-system-prompt[-file],
                        --add-dir (CLAUDE.md dirs), --mcp-config, --settings, --agents,
                        --plugin-dir.

-d, --debug [filter]    Enable debug mode with optional category filtering
                        (e.g., "api,hooks" or "!1p,!file")

--plugin-dir <path>     Load a plugin from a directory or .zip for this session only
                        (repeatable: --plugin-dir A --plugin-dir B.zip)

-p, --print             Print response and exit (useful for pipes). [...]
```

`--bare` explicitly skips "plugin sync" — defaults won't compete for `/help` routing. `--plugin-dir` then introduces the one plugin we care about. `--debug plugins` filters debug output to the plugin-load events (the `[filter]` parameter takes a category, per the help text).

## 2. Why the original `/help` probe was flaky

The pre-PR-115 test (`tests/smoke/test_dev_install.py`):

```python
result = subprocess.run(
    ["claude", "--plugin-dir", str(repo_root), "/help"],
    capture_output=True, text=True, timeout=30,
)
assert "agency-system" in result.stdout or "agency-system" in result.stderr
```

PR #115's debugging captured the actual failing stdout:

```
I've loaded the complete bitwize-music plugin help for you. This shows all
available skills organized by category:
- Album & Track Creation (new albums, concepts, lyrics, Suno prompts)
- [...]
```

The model responded about a *different* plugin's help because:

1. `/help` is interpreted as a chat / slash-command prompt, not a CLI subcommand.
2. The session had `bitwize-music` enabled globally; its help routing fired first.
3. The probe relied on the chat surface mentioning "agency-system" — a behaviour, not a contract.

This is the gap the Codex P1 critique on PR #115 ([discussion_r3262361939](https://github.com/netzkontrast/the-agency-system/pull/115#discussion_r3262361939)) accurately calls out — `claude plugin validate` (the PR #115 interim fix) avoids the flakiness but no longer exercises the real boot path. L2 closes both gaps.

## 3. The deterministic probe

```bash
claude --bare \
       --plugin-dir /home/user/the-agency-system \
       --disable-slash-commands \
       --debug plugins \
       -p exit
```

- `--bare` → no default plugin competition.
- `--disable-slash-commands` → the `-p exit` prompt is not interpreted as a slash command, eliminating residual chat-routing variance.
- `--debug plugins` → plugin-load events land on stderr regardless of which model responds.
- `-p exit` → non-interactive; gives the model the smallest possible prompt so we don't pay for a meaningful chat round-trip. Token cost is dominated by the system prompt; the assistant turn is trivially short.

The L2 assertion grepping `"agency-system"` runs against `stdout + stderr` combined; the debug log emits the plugin name when loading.

## 4. Cost envelope

A trivial `-p` call to Claude Code:

- Cold boot of the binary: ~1-3s.
- Plugin load + manifest parse for `agency-system`: <1s (114 tools, 58 skills — all metadata, no handler execution).
- Single API call for the "exit" prompt: 1-3s + a few hundred tokens.

Total typical runtime: 3-8 seconds. Wallclock budget in test: 60s timeout (generous for cold caches in CI).

## 5. Why we don't use `claude plugin validate` as the L2 probe

`claude plugin validate <repo>` is a static manifest check — it parses `.claude-plugin/plugin.json` and walks the skill tree. It does NOT:

- Spawn the MCP server (`servers/agency-mcp/run.py` is never imported).
- Exercise `--plugin-dir`'s runtime loader.
- Surface handler-registration errors.

L2 needs to exercise the real `--plugin-dir` path that the Spec 022.1 anchor explicitly names. `validate` stays as a fast manifest test (kept in `test_dev_install.py`); L2 is the runtime backstop on top of it.

## 6. CI considerations

- **`claude` not on PATH** → graceful skip (already coded into the design § 4.1). CI runners without the CLI installed stay green.
- **Authentication** → `--bare` strictly uses `ANTHROPIC_API_KEY` or `apiKeyHelper via --settings`. The L2 test must run in an env with one of these set; CI configures it as a secret.
- **Rate limits** → L2 fires one trivial prompt per test run. The marker `@pytest.mark.smoke_slow` lets devs exclude it from inner-loop runs.
- **Cost** → Trivial prompt → trivial response. Single-digit cents per run in the worst case.

## 7. Alternative considered: `claude plugin details <name>` + `--plugin-dir`

`claude plugin details agency-system` would in principle print the plugin's component inventory. But the `details` subcommand operates on **installed** plugins (those registered via `claude plugin install`); it does not accept `--plugin-dir` to point at a dev-mode plugin. Excluded.

## References

- `claude --help` (CLI doc, this sandbox)
- [Claude Code Plugins Reference](https://code.claude.com/docs/en/plugins-reference) — `--plugin-dir` semantics
- `tests/smoke/test_dev_install.py` pre-PR-115 (probe history)
- PR #115 [discussion_r3262361939](https://github.com/netzkontrast/the-agency-system/pull/115#discussion_r3262361939) — Codex P1 critique
