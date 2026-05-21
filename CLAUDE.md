# the-agency-system — Claude Code instructions

Working tree for **the-agency-system** music projects and for the
[bitwize-music](https://github.com/bitwize-music-studio/claude-ai-music-skills)
plugin that produces them.

## MANDATORY: Use subagents for independent or context-heavy work

**Default to subagents when a task is independent, parallelizable, or
context-heavy.** They protect the main session's attention budget and
return only a focused summary.

When to delegate:

- **Parallel research** (multiple topics, multiple research runs, multiple
  source dumps) → spawn one `general-purpose` subagent per topic in a
  single message; they run concurrently.
- **Locating code or content** ("where is X defined", "which files
  reference Y", "find all overrides that mention Z") → use the `Explore`
  subagent. Read-only, fast, optimised for grep-style lookups.
- **Long-form file analysis** (read 5+ files, compare, summarise) →
  delegate to a subagent so the raw content doesn't fill the main context.
- **Independent draft work** (drafting lyrics for unrelated tracks in
  parallel, generating multiple Style Box variants) → one subagent per
  draft, single message, parallel execution.
- **Audits / surveys** ("which overrides still reference project X",
  "which tracks are missing pronunciation entries") → subagent.

When to stay in main context:

- **Sequential work** where each step depends on the previous one.
- **Stateful decisions** that need the user in the loop.
- **Single file edits** with a clear target.
- **Anything the user is actively reviewing turn-by-turn.**

Brief the subagent like a colleague: state goal, list what to check, cap
the response length ("under 200 words"). Trust but verify — when an
agent edits files, check the diff before reporting work as done.

## MANDATORY: Tools always win over handcrafting

**If a tool exists for the operation, use the tool — never edit by hand.**
This applies to every layer:

- **Status / explicit / field changes** → use `update_track_field` MCP,
  not Edit on the Track Details table.
- **Creating tracks** → `create_track` MCP, not `Write` of a hand-rolled
  scaffold.
- **Cache out of sync (`track not found`)** → run `rebuild_state` MCP
  *first*, then retry the proper tool. Do not fall back to Edit.
- **Loading overrides** → `load_override` MCP, not bare `Read`.
- **Album coherence / validation / pre-generation gates** → the
  matching MCP tool, not a manual checklist.

Hand-editing is only acceptable when the tool surface genuinely doesn't
cover the operation (e.g. drafting prose inside the Concept section,
where there is no setter). Whenever you reach for `Edit` on a track or
album file, first ask: **"Is there a tool that owns this field?"** If
yes, use it.

This is mandatory and overrides any habit of "just fix it inline."

## MANDATORY: Skills before MCP

**Always prefer invoking a `/bitwize-music:<skill>` slash command (or the
`Skill` tool with the same name) over calling the underlying
`mcp__plugin_bitwize-music_*` tools directly.** Skills carry the full
workflow, the guard rails, and the project's craft conventions. MCP
tools are the low-level primitives the skills are built on — use them
directly only when:

1. A skill explicitly delegates to a specific MCP call (e.g.
   `update_track_field` for a status flip), or
2. No skill covers the operation (rare — check `/bitwize-music:help`
   first), or
3. A skill has been invoked and it has explicitly asked you to perform
   the MCP call as part of its own workflow.

If you find yourself reaching for an MCP tool, first ask: **"Which
skill should be driving this?"** That question almost always has an
answer. Document the skill choice in your reasoning before invoking
the MCP tool — that record is the evidence the right path was taken.

## RECOMMENDED: Follow the canonical workflow chains (and remind the user before skipping)

**Albums and tracks advance through fixed phase chains. Each downstream
skill's `prerequisites:` frontmatter declares which skills the chain
*expects* to have run first. The chains below are the recommended path
— the route that protects each skill's invariants.**

**The chain steps are optional, not mandatory.** The user may choose to
skip any link (e.g., generate on Suno without running lyric-reviewer
first, or release without running plagiarism-checker). Skipping is the
user's call, not Claude's.

**Claude's job at every handoff:** name the recommended next step,
explain in one sentence what it would check, and ask whether to run
it or move on. Surface — don't enforce. The reminder is mandatory; the
step is not.

**Hard gates are explicitly marked below and remain binding when the
corresponding skill is invoked.** Example: if the user runs
`pre-generation-check`, its 6 BLOCKING gates still block. Choosing not
to invoke it is allowed; running it and bypassing its results is not.

The single source of truth for routing is the resume / next-step
decision trees in the plugin (`skills/resume/SKILL.md`,
`skills/next-step/SKILL.md`). Don't paraphrase them in conversation —
invoke them when the user asks "what's next?". When the user gives a
direct instruction (e.g., "generate on Suno now"), honor it after
delivering the one-sentence reminder.

### Pre-generation chain (recommended path for every vocal track)

Steps marked **(optional)** can be skipped at the user's discretion;
Claude must remind before skipping. Steps marked **(hard gate when
invoked)** still block when the skill is run.

```
lyric-writer                  (drafts lyrics; auto-invokes suno-engineer at end)
  ↓
pronunciation-specialist      (optional — resolves homographs, proper nouns, tech terms)
  ↓
lyric-reviewer                (optional — 14-point QC; auto-applies phonetic fixes)
  ↓
voice-checker                 (optional, advisory — AI-pattern flags; never blocks even when run)
  ↓
pre-generation-check          (optional to invoke — but hard gate when invoked:
                               6 BLOCKING gates on sources, lyrics, pronunciation,
                               explicit, style box, artist names)
  ↓
[Generate on Suno]
```

- **lyric-writer auto-invokes suno-engineer** at the end of its
  workflow — do not double-call suno-engineer after lyric-writer.
- **The lyric-writer's internal 13-point check is self-review** — it
  does NOT substitute for invoking `/bitwize-music:lyric-reviewer`.
  Lyric-reviewer is the recommended follow-up; if the user opts to
  skip it, remind that the 14-point QC and auto-phonetic-fix pass
  will not run.
- **Instrumental tracks** skip lyric-writer, pronunciation-specialist,
  lyric-reviewer, and voice-checker — they enter the chain at
  suno-engineer. pre-generation-check gates 2/3/4 auto-skip;
  gates 1/5/6 still run.
- **voice-checker is advisory only** — never gate on it. Surface its
  Warning/Info flags to the user; don't auto-rewrite based on them.
- **explicit-checker** and **plagiarism-checker** can run earlier than
  the release chain — call them whenever explicit-content or
  borrowed-phrase risk surfaces during writing.

### Pre-release chain (recommended path for every album)

Steps marked **(optional)** can be skipped at the user's discretion;
Claude must remind before skipping. Steps marked **(hard gate when
invoked)** still block when the skill is run.

```
import-audio
  ↓
mix-engineer                  (optional stems polish; hands off to mastering)
  ↓
mastering-engineer            (optional — but recommended before release:
                               [qc_audio "" → master_album → qc_audio "mastered"])
  ↓
album-art-director + import-art   (optional — final artwork in place, ≥3000×3000)
  ↓
validate-album                (optional — structural integrity, required files, path layout)
  ↓
plagiarism-checker            (optional — distinctive-phrase scan vs existing songs)
  ↓
explicit-checker              (optional — final flag verification for distributor metadata)
  ↓
check_streaming_lyrics MCP    (optional — distributor lyric format validation)
  ↓
release-director              (optional to invoke — but hard gate when invoked:
                               9-domain QA gate; blocks until all pass)
  ↓
update_streaming_url + verify_streaming_urls
```

- release-director's 9 QA domains: Audio Quality, Metadata, Source
  Verification, Lyrics Accuracy, Artwork Quality, File Organization,
  Documentation, Explicit Content, Promo Copy (optional). Override
  `overrides/release-preferences.md` may *add* checks; it may NOT skip
  critical ones.
- **Streaming lyrics vs Suno lyrics**: distributor metadata, plagiarism
  scans, and promo content pull from *streaming* lyrics only (standard
  English, no phonetics). Never paste Suno-phonetic lyrics into
  public-facing fields.

### Concept phase gate (hard gate — preserved)

`album-conceptualizer` Phase 7 (Confirmation) is a **hard gate** and
remains binding. Lyric writing does not begin until the user has
explicitly confirmed the seven planning phases. Partial agreement
triggers a revision pass, not a forward pass. This gate is enforced
by the `album-conceptualizer` skill itself when invoked, and Claude
should not start lyric-writer for an album whose phases have not been
confirmed.

### Sources gate (hard gate for documentary albums — preserved)

`sources_verified = N/A` is acceptable for non-documentary albums —
do not gate non-docs on source verification. **Documentary albums
must** reach `Verified (date)` on every track before lyric-writer
runs. This is a hard gate for documentary work; Claude should refuse
to draft documentary lyrics on unverified sources and remind the user
to run source verification first.

### When in doubt — invoke the routing skill

`/bitwize-music:resume <album>` or `/bitwize-music:next-step` returns
the recommended next action with skill name and track. If you can't
tell which step is next, invoke the routing skill rather than guessing.
The user can still choose to skip the recommended step — but invoke
routing to know what's being skipped.

### Reminder behavior at handoffs (mandatory)

After any skill completes, Claude must end its reply with a short
**"Next step (optional)"** line naming the recommended next skill
and what it would check. Example:

> *Next step (optional): `/bitwize-music:lyric-reviewer` would run the
> 14-point QC on the lyrics and auto-apply any phonetic fixes. Run it,
> or proceed straight to Suno generation?*

The user decides whether to run it. Claude does not auto-invoke
optional chain steps without being asked. The reminder is the
guarantee that nothing is silently skipped.

## MANDATORY: Overrides are cross-project — albums hold album content

**Overrides (`overrides/*.md` and `overrides/*.yaml`) hold cross-project
preferences only.** Album-specific content — alter names, character
names, narrative DNA, per-track pronunciations, specific BPM identities,
named track titles — lives in the album folder, never in `overrides/`.

If an override file starts mentioning a specific album, character, or
genre identity, that's a signal it should be migrated:

- **Voice DNA / alter fingerprints** → `<album>/the-eleven.md`,
  `<album>/cast.md`, or whatever the project's convention is.
- **Project narrative / sequence / arcs** → `<album>/README.md`.
- **Track-specific pronunciations** → the track file's
  Pronunciation Notes table.
- **Album-specific research / sources** → `<album>/RESEARCH.md`,
  `<album>/SOURCES.md`.

What lives in `overrides/`: cross-project taste, lexicon avoidances,
genre→Suno mappings, vocal-register defaults, mastering presets for
genres the artist actually uses, documentary source-priority standards,
recurring German/foreign-language terms, the no-labels rule and
descriptive-only metatag conventions.

If a session inherits overrides from a previous project (HTML header
citing a different commit / repo), audit them before using the skills
that load them — obsolete project DNA will silently steer skills toward
the wrong aesthetic.

## Arbeit an the Agency System (Musik / Novel / Design)

**the Agency System** is a single DID-system concept expressed across three
layers — music, a novel, and a visual design language — that share one cast
and one world. When work starts (or continues) on this artist/project, invoke
the gate skill **`skills/theagencysystem/`** *before* the bitwize chain (or a
novel writing phase) so the right DNA is in context.

- **Gate first.** The skill asks "Artist/Projekt = the Agency System?" — on
  *No* it exits silently and loads nothing. On *Yes* it loads only the snippets
  the active `(function × state × layer)` needs. Do not bulk-read the snippet
  tree.
- **One cast, keyed by function.** Design + Music reference voices by
  **function/role**; the Novel references them by **name**. The bidirectional
  name↔function map lives in
  [`skills/theagencysystem/references/resolver.yaml`](skills/theagencysystem/references/resolver.yaml).
  Classification (CONFIRMED): ANP = {host, rationalist}; Meta = {integrator
  (ISH), witness}; the remaining seven are EP.
- **The 2D matrix.** `(function × state)` → 1-line essence + exact pointers:
  [`skills/theagencysystem/references/matrix-index.yaml`](skills/theagencysystem/references/matrix-index.yaml).
  The S0–S4 state axis is
  [`skills/theagencysystem/references/state-axis.md`](skills/theagencysystem/references/state-axis.md).
- **name_exposure (hard rule).** In **music** and **design** outputs use
  function/role only — a personal name (Kael, Nyx, Selene, …) must never reach
  a lyric, Suno metatag, promo field, or art prompt. Only the **novel** layer
  may use names. This extends `overrides/voice-craft-principles.md`.
- **Where DNA attaches to bitwize.**
  [`skills/theagencysystem/references/bitwize-attachment.md`](skills/theagencysystem/references/bitwize-attachment.md)
  routes each bitwize skill's own phase/field to the refs it should load.
- **Source overrides** (cross-project DNA the snippets were distilled from):
  `overrides/visual-language-guide.md`, `overrides/image-style-spec.md`,
  `overrides/kohaerenz-protokoll-sprach-dna.md`, `overrides/the-eleven.md`.

## Workflow patterns to remember

### Session-start audit (fresh session, especially after switching projects)

1. Run `/bitwize-music:health-check` — confirm the workflow stack is ready.
2. Run `/bitwize-music:help` if you need to find a skill — don't grep the
   filesystem.
3. Spot-check active overrides for project-specific content not matching
   the current album. If found, flag and offer cleanup before invoking
   skills that load those overrides.

### Common pitfalls (codified from prior misses)

- **State cache stale after bulk `create_track`**: run `rebuild_state`
  MCP before `update_track_field` on freshly-created tracks, or the
  field updates will return `track not found`.
- **`Write` requires prior `Read`**: the harness blocks `Write` until
  `Read` has been called on the target path in this session. For partial
  changes, use `Edit` (no Read requirement when targeting unique strings).
- **Track frontmatter validation fires on `Write`, not `Edit`**: the
  PostToolUse hook validates frontmatter only when a full file body is
  written. If you `Write` a track file, the frontmatter must include
  `status:` or the hook blocks the operation. `Edit` modifications are
  exempt.
- **Status transitions are MCP-enforced**: `update_track_field` rejects
  illegal transitions (e.g., `In Progress → In Progress`). Use `force=true`
  only when recovering from a cache mismatch, not to bypass workflow rules.
- **Don't name alters in Suno metatags**: the descriptive form
  `[male mid-baritone, weary, dry close-mic]` is permitted; the character
  form `[Container]` is forbidden by `voice-craft-principles.md`.

## Jules orchestration plugin

The Jules orchestrator allows for multi-agent asynchronous coding sessions.
It bundles an MCP server (with 16 lifecycle/patch/bulk tools), a slimmed `SKILL.md` (with `/references/`), and helpers (`lib/` utilities, `bin/jules-bulk`).
For details, see the [refactor design spec](docs/superpowers/specs/2026-05-16-jules-suite-refactor-design.md).

- **Local dev install:** `claude --plugin-dir ./jules-plugin`
- **Marketplace install:** `/plugin install jules-orchestrator@netzkontrast`

### Driving the CLI helpers outside Claude Code

When you run `bin/jules-bulk` (fanout / dashboard / approve-awaiting) from a
fresh shell — for example, from a Claude Code agent that has not yet loaded
the plugin — `fastmcp[code-mode]` is not on the Python path and the script
fails preflight. Bootstrap with:

```bash
./jules-plugin/bin/jules-dev-install      # idempotent: installs fastmcp[code-mode], httpx, PyYAML
export JULES_API_KEY=…
export CLAUDE_PLUGIN_ROOT=$(pwd)/jules-plugin
./jules-plugin/bin/jules-bulk dashboard   # smoke
```

`bin/jules-dev-install` verifies the imports the helpers need
(`FastMCP`, `CodeMode`, `jules_create`, `create_mcp`) and pre-creates the
session-registry directory at `${CLAUDE_PLUGIN_DATA:-$HOME/.jules}`. Re-running
is a no-op once the deps are present.

### Jules session state semantics (silent-fail recovery)

**`state=COMPLETED` does NOT mean "done, success".** It means *"session
is idle, waiting for input"*. A `COMPLETED` session can be resumed by
sending `jules_message(sid, ...)` — it transitions back to `IN_PROGRESS`
and continues working. Sessions persist indefinitely in `COMPLETED`;
only `AWAITING_PLAN_APPROVAL` has a timeout risk.

**Always verify the branch on remote before trusting `COMPLETED`.**
The state field flips even when Jules paused before pushing — the work
sits in the patch but never lands on `origin`. Use
`mcp__github__list_branches` and look for a branch matching the
session's work. If none is present, the session is in a recoverable
silent-fail state, not a terminal one.

**Recovery flow (JULES_PROTOCOL §8):**

1. Verify branch on remote → if missing, do NOT trust `COMPLETED`.
2. Extract the patch:
   `PYTHONPATH=jules-plugin/mcp-server/src python3 tools/jules-patch-extract.py <sid>`
   (writes to `/tmp/jules-patches/<sid>-out0.patch`, emits stats only —
   never `cat`/`head`/`grep` patches > 2 KB).
3. **Probe Jules first** — one focused message: "your state is
   COMPLETED but no branch on origin — please push and reply with PR
   URL". Jules normally answers within ~5 minutes; if it pushes, you're
   done.
4. After 2-3 probes with still no branch, switch to a **local
   subagent** that applies the extracted patch via
   `mcp__github__create_branch` + `mcp__github__create_or_update_file`
   (signed `web-flow` commits) + `mcp__github__create_pull_request`.
   **Never re-dispatch a fresh Jules session for the same work** — the
   patch is already in the API and a respawn wastes a slot and risks
   divergent output.

**Common silent-fail variants:**

| Symptom | Cause | Action |
|---|---|---|
| `COMPLETED` + non-empty patch + no branch | Jules paused on the "open PR?" UI gate | Probe via `jules_message`. If still nothing, apply patch locally. |
| `COMPLETED` + empty patch (0 files) | Jules completed without doing the work | Probe: tell Jules to actually produce the artifact. If still empty after 2 probes, dispatch a fresh session ONLY because there's no patch to recover from. |
| `COMPLETED` + patch contains files outside the spec `affects:` allow-list | Scope creep | First check whether the extra changes are legitimate (e.g. align with a parallel spec). If yes, keep them. If no, probe Jules to drop the out-of-scope diffs before pushing. |

The `tools/jules-patch-extract.py` script and `mcp__github__*` paths
are the only context-safe routes — bash `git apply` + `git push` of
extracted patches breaks signed commits because the local
CODESIGN_MCP backend currently returns HTTP 400.

## Most important commands & skills

Invoke as slash commands: `/bitwize-music:<name>`.

| Command | Purpose |
|---|---|
| `/bitwize-music:health-check` | Verify plugin + MCP server status |
| `/bitwize-music:configure` | Show / edit active config |
| `/bitwize-music:help` | List all plugin skills |
| `/bitwize-music:about` | Plugin overview |
| `/bitwize-music:tutorial` | Guided walkthrough |
| `/bitwize-music:new-album` | Start a new album |
| `/bitwize-music:album-conceptualizer` | Develop album concept |
| `/bitwize-music:lyric-writer` | Write lyrics |
| `/bitwize-music:suno-engineer` | Craft Suno prompts |
| `/bitwize-music:mastering-engineer` | Master audio |
| `/bitwize-music:release-director` | Coordinate release |

### Where to find more

- **Full skill list:** `/bitwize-music:help`
- **What a specific skill does:** `/bitwize-music:about <skill-name>` or
  `get_skill` MCP tool with the skill name.
- **Canonical naming for the unified `agency-system` plugin** (three-layer
  harness ladder L1/L2/L3, four-verb contract, five handler-bearing
  domains + agentic skill-only, Path A vs. Path B disambiguation, frontmatter
  conventions, repair-authority tiers, content tiers): see
  [`Plan/harness/VOCABULARY.md`](Plan/harness/VOCABULARY.md). When a phase
  document, sub-spec, ADR, or skill needs to cite a cross-cutting term,
  link to VOCABULARY rather than re-deriving the canon.
- **Architecture decisions (ADRs, MADR 4.0.0):**
  [`Plan/decisions/readme.md`](Plan/decisions/readme.md).
- **Cross-project preferences (lyric craft, Suno mappings, research
  standards, vocal registers, mastering presets, voice-craft principles):**
  `overrides/lyric-writing-guide.md`,
  `overrides/suno-preferences.md`,
  `overrides/research-preferences.md`,
  `overrides/pronunciation-guide.md`,
  `overrides/voice-craft-principles.md`,
  `overrides/promotion-preferences.md`,
  `overrides/mastering-presets.yaml`
- **Album-specific content** (voice DNA, narrative, sources, art direction)
  lives inside each album folder, never in `overrides/`.

## Repository essentials

- `artists/<artist>/albums/<genre>/<slug>/` — album content (READMEs, research, tracks, art direction)
- `overrides/` — cross-project preferences loaded automatically at session start
- `audio/`, `documents/` — Git LFS (run `git lfs install` once per machine)
- **Default branch: `Master`** (capitalised). All PRs target `Master`, not `main`. An `origin/main` branch exists but is not the merge target — passing `base: main` to `mcp__github__create_pull_request` returns `422 Validation Failed`.
