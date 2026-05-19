# Row Examples: agentic/<row>

This document provides concrete examples of how the `agentic` canonical shape is applied across three distinct rows: `music`, `novel`, and `jules`.

## 1. `agentic/music` (Redesigning the MVP)

**Context:** The existing `bitwize-music` plugin is bloated. It has ~54 skills with 200–515 line bodies and 18 tools stuffed into a single `core.py`. We collapse this into the canonical shape by pushing logic down to handlers and pipelines into `workflow/music`.

### Layout
```
agentic/music/
├── manifest.toml
├── handlers/
│   ├── __init__.py
│   ├── analysis.py
│   ├── synthesis.py
│   └── review.py
└── skills/
    ├── music-producer/
    │   └── SKILL.md
    └── music-master/
        └── SKILL.md
```

### `manifest.toml`
```toml
[cell]
row = "music"
column = "agentic"

[routing]
namespace_prefix = "music_"

[skills]
exports = ["music-producer", "music-master"]

[tools]
exports = ["analysis", "synthesis", "review"]
```

### Example Skill (`skills/music-producer/SKILL.md`)
```markdown
---
name: music-producer
description: Analyzes stems and synthesizes reference tracks.
argument-hint: <action> [args...]
prefers_codemode: true
allowed-tools:
  - mcp__music_analyze_stems
  - mcp__music_synthesize_track
---

## Your Task
You are the Music Producer agent. You analyze raw stems and synthesize initial tracks.
Use `mcp__music_analyze_stems` to build the context.
If the structure is complex, use `dispatch_skill` to invoke `workflow/music` phase 2.
```

### Example Handler Signatures (`handlers/analysis.py`)
```python
@mcp.tool(tags={"domain:music"})
def analyze_stems(stem_paths: list[str]) -> ToolResult: ...

def register_music_analysis(mcp: FastMCP) -> None:
    # Registers analyze_stems
    pass
```

## 2. `agentic/novel` (Greenfield)

**Context:** Designed from scratch for a chapter/scene pipeline.

### Layout
```
agentic/novel/
├── manifest.toml
├── handlers/
│   ├── __init__.py
│   ├── drafting.py
│   └── revision.py
└── skills/
    └── novel-author/
        └── SKILL.md
```

### `manifest.toml`
```toml
[cell]
row = "novel"
column = "agentic"

[routing]
namespace_prefix = "novel_"

[skills]
exports = ["novel-author"]

[tools]
exports = ["drafting", "revision"]
```

### Example Skill (`skills/novel-author/SKILL.md`)
```markdown
---
name: novel-author
description: Drafts and revises novel chapters and scenes.
argument-hint: <chapter_id> <action>
prefers_codemode: true
allowed-tools:
  - mcp__novel_draft_scene
  - mcp__novel_revise_chapter
---

## Your Task
You are the Novel Author. Draft scenes using `mcp__novel_draft_scene`. When a chapter is complete, invoke `mcp__novel_revise_chapter` to apply structural edits. Read character sheets via context graph before drafting.
```

### Example Handler Signatures (`handlers/drafting.py`)
```python
@mcp.tool(tags={"domain:novel"})
def draft_scene(scene_id: str, context_refs: list[str]) -> ToolResult: ...

def register_novel_drafting(mcp: FastMCP) -> None:
    pass
```

## 3. `agentic/jules` (Slimming the Orchestrator)

**Context:** The existing `jules-plugin` has a good floor (85-line `SKILL.md` + 9 references). We align its 16-tool surface to the explicit matrix shape.

### Layout
```
agentic/jules/
├── manifest.toml
├── handlers/
│   ├── __init__.py
│   ├── session.py
│   └── patch.py
└── skills/
    └── jules-orchestrator/
        ├── SKILL.md
        └── references/
            ├── state-machine.md
            └── parallel-orchestration.md
```

### `manifest.toml`
```toml
[cell]
row = "jules"
column = "agentic"

[routing]
namespace_prefix = "jules_"

[skills]
exports = ["jules-orchestrator"]

[tools]
exports = ["session", "patch"]
```

### Example Skill (`skills/jules-orchestrator/SKILL.md`)
```markdown
---
name: jules
description: Delegates asynchronous coding tasks to the Jules agent.
argument-hint: <action> [args...]
prefers_codemode: false
allowed-tools:
  - mcp__jules_create
  - mcp__jules_get
  - mcp__jules_patch_apply
---

## Your Task
You are the orchestrator for the remote Jules agent. Start sessions with `mcp__jules_create`. Check state using `mcp__jules_get`.
For state transitions, see `references/state-machine.md`.
```

### Example Handler Signatures (`handlers/session.py`)
```python
@mcp.tool(tags={"domain:jules"})
def create(prompt: str, title: str = None) -> ToolResult: ...

@mcp.tool(tags={"domain:jules"})
def get(session_id: str) -> ToolResult: ...

def register_jules_session(mcp: FastMCP) -> None:
    pass
```
