# Jules' Native Toolset & DSL — what tools Jules actually has

This reference is the *inside* view of Jules: what tools Jules can call once a
session is running on its VM. The rest of `SKILL.md` describes the *outside*
view (the MCP tools the orchestrator uses to dispatch and monitor sessions).
Use this file when writing the prompt body that Jules will execute, so you can
cite tool names Jules actually has and Jules picks them naturally.

The authoritative long-form reference for everything below lives at
[`reference/jules-architecture.md`](../../../../reference/jules-architecture.md)
in this repo. This file is the orchestrator-facing tight summary.

---

## 1. Environment cheatsheet

Each Jules session runs on a fresh, ephemeral **Ubuntu VM** with explicitly
pinned modern toolchains. Useful when writing prompts that depend on a specific
runtime — you do not have to ask Jules to "install Python", it is already there.

| Stack | Pinned default | Notes |
|---|---|---|
| Python | 3.12.11 | 3.10.18 also available via `pyenv` |
| Python tools | `pip`, `pipx`, `poetry`, `uv`, `black`, `mypy`, `pytest`, `ruff` | All pinned |
| Node.js | 22.16.0 | 18.20.8 and 20.19.2 via `nvm` |
| Node tools | `npm`, `yarn`, `pnpm`, `eslint`, `prettier`, `chromedriver` | For frontend verification |
| Java | OpenJDK 21.0.7 | 64-bit Server VM |
| Other | Go, Rust, Bun | Native on `PATH` |
| Unix | `git`, `grep`, `rg`, `jq`, `yq`, `make`, `tar`, `gzip`, `sed`, `tmux` | All pre-installed |

**Environment snapshots:** when a repo has a `setup.sh` (or Jules infers setup
from `README.md`/`AGENTS.md`), Jules **caches a VM snapshot** after the first
successful run. Later sessions hydrate from the snapshot, skipping cold-start
dependency resolution. *Always point Jules at `setup.sh` if the repo has one.*

**Env vars are locked at session start.** Repository-level secrets are injected
once and become immutable for the session — Jules cannot pick up new values
mid-session.

---

## 2. AGENTS.md scoping

Jules treats every `AGENTS.md` file in the repo as a **system-prompt overlay**.
Rules:

- An `AGENTS.md` applies to the **entire subtree** rooted at its directory.
- **Deepest file wins.** Nested `AGENTS.md` files override parent directives,
  so monorepo packages can each enforce their own conventions.
- Jules is instructed to read and obey `AGENTS.md` *before* finalising its plan.

**Canonical project pattern in this repo:** the top-level `AGENTS.md` (or the
prompt body) points Jules at [`Plan/JULES_PROTOCOL.md`](../../../../Plan/JULES_PROTOCOL.md)
as the binding rules document. When writing a Jules prompt, mention this path
explicitly so Jules loads it during exploration.

---

## 3. Standard Tools (Python-syntax)

Standard Tools are invoked with `tool_name(arg="value")` syntax — same as
ordinary Python function calls. Group by purpose:

### Filesystem I/O

| Tool | Behaviour |
|---|---|
| `list_files(path="")` | Lists files/dirs (`ls -a -1F --group-directories-first`); dirs end in `/`. Defaults to repo root. |
| `read_file(filepath)` | Loads file content into context. Hard errors on missing path — prevents hallucinated contents. |
| `write_file(filepath, content)` | Creates or fully overwrites a file. Replaces the legacy `create_file_with_block` and `overwrite_file_with_block`. |
| `delete_file(filepath)` | Removes a file. Errors if path invalid. |
| `rename_file(filepath, new_filepath)` | Move/rename. Blocks if source missing, target exists, or parent dir missing. |
| `restore_file(filepath)` | Reverts a single file to its cloned state. |
| `reset_all()` | Global rollback — entire repo back to clone state. Use when the plan is fundamentally wrong. |

### Planning / state machine

| Tool | Behaviour |
|---|---|
| `set_plan(plan)` | Registers the numbered-Markdown plan. Recursively callable to revise. |
| `request_plan_review(plan)` | **Mandatory before first `set_plan`** — human approves the plan. |
| `record_user_approval_for_plan()` | Locks approval state internally. |
| `plan_step_complete(message)` | Advances the state machine. Jules MUST verify with `read_file`/`list_files` before calling this. |
| `done(summary)` | Terminates a sub-agent and returns a summary payload. |

### CI / testing / submission

| Tool | Behaviour |
|---|---|
| `pre_commit_instructions()` | **MUST be called before `submit`.** Returns the dynamic checklist of tests/format/lint validations Jules has to satisfy. |
| `submit(branch_name, commit_message, title, description)` | Commits and pushes; triggers PR creation. |
| `request_code_review()` | Invokes the **Jules Critic** — a parallel review LLM that hunts edge cases & untested assumptions before the human sees the PR. |
| `frontend_verification_instructions()` | Returns sandbox-specific Playwright boilerplate for UI checks. |
| `frontend_verification_complete(screenshot_path, additional_media_paths=[])` | Attaches Playwright screenshots/media to the session for visual review. |
| `start_live_preview_instructions()` | Binds a local web server (Vite/Next.js) to a sandbox port for live preview. |

### Multimodal / web

| Tool | Behaviour |
|---|---|
| `google_search(query)` | Live web search — bypasses LLM training cutoff. |
| `view_text_website(url)` | Headless scrape, DOM → plaintext. Requires sandbox internet. |
| `knowledgebase_lookup(query)` | Google's internal proprietary dev knowledgebase — use proactively for framework-specific guidance (`django`, `npm`, etc.). |
| `view_image(url)` | Multimodal: ingest image at URL. |
| `read_image_file(filepath)` | Read local image from VM filesystem. |
| `read_media_file(filepath)` | Same plus video (`webm`) — used to "watch" Playwright recordings. |

### Human-in-the-loop

| Tool | Behaviour |
|---|---|
| `message_user(message, continue_working)` | Async status update. `continue_working=True` keeps going; `False` blocks. **Forbidden for asking questions.** |
| `request_user_input(message)` | The blocking ask-the-human tool. Use when ambiguous or scope shifted. |
| `read_pr_comments()` | Ingests pending reviewer comments from the GitHub PR. |
| `reply_to_pr_comments(replies)` | Posts replies. `replies` is a JSON string of `[{comment_id, reply}]`. |
| `initiate_memory_recording()` | Records salient decisions/quirks for long-term recall in future sessions on the same repo. |

---

## 4. Special Tools (custom DSL — NOT Python, NOT JSON)

Two tools use a custom DSL because their arguments are raw, multi-line,
unescaped text. The tool name appears alone on line 1; arguments follow.

### `run_in_bash_session`

Persistent bash shell. **State (cwd, env vars, sourced venvs) is shared across
calls.** Use this — not separate shell tools — for everything from
`pip install` to `pytest -x` to running a dev server.

Operational patterns Jules already knows:

- **Background processes:**
  `npm start > npm_output.log 2>&1 &` — then `read_file("npm_output.log")` to
  diagnose startup crashes.
- **Port collision cleanup:**
  `kill $(lsof -t -i :<PORT>) 2>/dev/null || true`
- **Orphan hunting:**
  `pgrep -af <pattern>` then `kill <PID>`.
- **Use `rg`/`grep` directly** — the old `grep(...)` standard tool was
  deprecated in favour of native ripgrep.

### `replace_with_git_merge_diff`

Surgical edits using exact-line search/replace markers. Preferred over
`write_file` for targeted changes — saves tokens and reduces hallucination.

```
replace_with_git_merge_diff
path/to/target/file.py
<<<<<<< SEARCH
[exact original lines, including indentation]
=======
[new replacement lines]
>>>>>>> REPLACE
```

The `SEARCH` block must match the file **byte-for-byte**, including leading
whitespace.

---

## 5. Prompt-writing cheatsheet for orchestrators

When you write the prompt body Jules will execute, lean on this list:

- **Name the tools Jules has.** If you say "use `replace_with_git_merge_diff`
  for the edit", "run the test via `run_in_bash_session`", "call
  `pre_commit_instructions()` before `submit`", "use `request_code_review()`
  after the test is green", Jules picks those tools naturally rather than
  reinventing the wheel.
- **Anchor on the rules document.** Tell Jules where the canonical
  `AGENTS.md` and/or `Plan/JULES_PROTOCOL.md` live so it loads them during
  exploration.
- **Multi-file tasks:** explicitly request `list_files` + `read_file` for the
  affected modules before any edits — Jules's spatial awareness is far better
  after a deliberate exploration pass.
- **UI tasks:** instruct Jules to call `frontend_verification_instructions()`,
  drive the change through Playwright, and attach a screenshot via
  `frontend_verification_complete(...)`.
- **Dependency setup:** point Jules at `setup.sh` — it snapshots the VM after
  the first successful run, so later sessions are much faster.
- **Verification before completion:** require Jules to call
  `pre_commit_instructions()` and `request_code_review()` before `submit`.
  This is the cheapest way to lift PR quality.
- **Do not ask Jules to "cancel" or "stop".** Those actions are unsupported
  (see [`caveats.md`](caveats.md) — `jules_stop` is not in the upstream API).
  If a session needs to die, let it idle into `COMPLETED` and stop sending
  messages.
- **Trust persistence.** Successive `run_in_bash_session` calls share state —
  you can split a long script across multiple tool calls without re-sourcing
  venvs or re-exporting env vars.
