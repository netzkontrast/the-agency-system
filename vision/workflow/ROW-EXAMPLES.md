# Row Examples

This document demonstrates how specific rows map into the `workflow/<row>` canonical shape.

## 1. `workflow/music`

*Reifying the MVP chain (`lyric-writer → suno-engineer → mastering → release-director`) into strict phases.*

**Manifest (`workflow/music/manifest.toml`):**
```toml
[workflow]
row = "music"
entry_verbs = ["create_track", "continue_track"]

[[phases]]
id = "phase-lyric"
path = "phases/01-lyric.md"

[[phases]]
id = "phase-suno"
path = "phases/02-suno.md"

[[phases]]
id = "phase-mastering"
path = "phases/03-mastering.md"

[[phases]]
id = "phase-release"
path = "phases/04-release.md"

[[gates]]
id = "gate-lyric-review"
path = "gates/lyric-review.md"
blocks = "phase-suno"
```

**Example Phase (`workflow/music/phases/01-lyric.md`):**
```markdown
---
id: phase-lyric
name: Lyric Writer
driven_by_skill: agentic/music/skills/lyric-writer.md
outputs:
  - workflow/music/handoffs/envelope.yaml (contains lyric data)
---
Generates the lyrical content based on user prompt and requested genre.
```

## 2. `workflow/novel`

*A pipeline for writing a book.*

**Manifest (`workflow/novel/manifest.toml`):**
```toml
[workflow]
row = "novel"
entry_verbs = ["start_book", "draft_chapter"]

[[phases]]
id = "phase-outline"
path = "phases/01-outline.md"

[[phases]]
id = "phase-chapter"
path = "phases/02-chapter.md"

[[phases]]
id = "phase-scene"
path = "phases/03-scene.md"

[[phases]]
id = "phase-revision"
path = "phases/04-revision.md"

[[phases]]
id = "phase-publish"
path = "phases/05-publish.md"

[[gates]]
id = "gate-outline-approved"
path = "gates/outline-approval.md"
blocks = "phase-chapter"
```

**Example Phase (`workflow/novel/phases/02-chapter.md`):**
```markdown
---
id: phase-chapter
name: Chapter Drafting
driven_by_skill: agentic/novel/skills/chapter-drafter.md
inputs:
  - workflow/novel/handoffs/envelope.yaml (contains outline)
outputs:
  - workflow/novel/handoffs/envelope.yaml (contains chapter drafts)
---
Drafts chapters strictly adhering to the approved outline.
```

## 3. `workflow/jules`

*The discipline pipeline enforcing the `JULES_PROTOCOL`.*

**Manifest (`workflow/jules/manifest.toml`):**
```toml
[workflow]
row = "jules"
entry_verbs = ["solve_issue", "refactor"]

[[phases]]
id = "phase-confidence"
path = "phases/01-confidence.md"

[[phases]]
id = "phase-tdd"
path = "phases/02-tdd.md"

[[phases]]
id = "phase-verification"
path = "phases/03-verification.md"

[[phases]]
id = "phase-review"
path = "phases/04-review.md"

[[phases]]
id = "phase-submit"
path = "phases/05-submit.md"

[[gates]]
id = "gate-confidence-check"
path = "gates/confidence-90.md"
blocks = "phase-tdd"
```

**Example Phase (`workflow/jules/phases/01-confidence.md`):**
```markdown
---
id: phase-confidence
name: Confidence Check
driven_by_skill: agentic/jules/skills/researcher.md
outputs:
  - workflow/jules/handoffs/envelope.yaml (contains confidence score)
---
Analyzes the task and codebase to ensure a 0.90 confidence score before proceeding to TDD.
```
