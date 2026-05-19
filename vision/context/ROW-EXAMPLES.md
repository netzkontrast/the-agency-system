# The Context Column: Row Examples

This document demonstrates the canonical `context` cell shape applied to three different rows: `music`, `novel`, and `jules`. It shows how the structure accommodates different domains while maintaining strict isomorphism.

## 1. `context/music`

The music row generates audio assets, lyrics, and metadata. This design collapses existing scattered references into the structured matrix form.

### Manifest (`context/music/manifest.toml`)
```toml
[cell]
row = "music"
version = "1.0.0"

[ontology]
node_types = ["Track", "Album", "LyricSheet", "StylePrompt"]

[templates]
"lyric_sheet" = { path = "templates/lyric_sheet.md.jinja", inputs = ["title", "genre", "theme", "structure"] }
"style_prompt" = { path = "templates/style_prompt.txt.jinja", inputs = ["bpm", "genre_tags", "vibe"] }

[schemas]
"track_meta" = { path = "schemas/track.schema.json", type = "json-schema-2020-12" }

[search_anchors]
"suno_guide" = { path = "references/suno_prompt_guide.md", summary = "Official Suno v3 prompting techniques." }
```

### Template Example (`context/music/templates/lyric_sheet.md.jinja`)
```jinja
---
type: template
slug: lyric_sheet
summary: "Standard structure for a generated song lyric sheet."
render_formats: [md, txt]
output_path: "agentic/music/lyrics/{{ slug }}.md"
required_vars: [title, genre, theme, structure]
---
# {{ title }}

**Genre:** {{ genre }}
**Theme:** {{ theme }}

## Structure
{{ structure }}

## Lyrics
...
```

### Schema Example (`context/music/schemas/track.schema.json`)
**Name:** `tag:agency-system.local,2026:schema:music/track_meta`
**Purpose:** Validates the metadata payload returned by the track generation tool before it is written to the graph. Ensures required fields like `duration`, `bpm`, and `stem_paths` are present.

---

## 2. `context/novel`

The novel row coordinates long-form fiction writing, managing characters, plots, and world-building.

### Manifest (`context/novel/manifest.toml`)
```toml
[cell]
row = "novel"
version = "1.0.0"

[ontology]
node_types = ["Outline", "Chapter", "Scene", "Character", "Location"]

[templates]
"chapter" = { path = "templates/chapter.md.jinja", inputs = ["chapter_number", "pov_character", "summary"] }
"character_profile" = { path = "templates/character.md.jinja", inputs = ["name", "role", "arc_summary"] }

[schemas]
"plot_beat" = { path = "schemas/plot_beat.schema.json", type = "json-schema-2020-12" }

[search_anchors]
"world_bible" = { path = "references/world_bible.md", summary = "Core rules and magic system for the universe." }
```

### Template Example (`context/novel/templates/chapter.md.jinja`)
```jinja
---
type: template
slug: chapter
summary: "Scaffolding for a new novel chapter."
render_formats: [md, epub, pdf]
output_path: "agentic/novel/chapters/{{ chapter_number | pad(3) }}-{{ slug }}.md"
required_vars: [chapter_number, pov_character, summary]
---
# Chapter {{ chapter_number }}

> **POV:** {{ pov_character }}
> **Summary:** {{ summary }}

...
```

### Schema Example (`context/novel/schemas/plot_beat.schema.json`)
**Name:** `tag:agency-system.local,2026:schema:novel/plot_beat`
**Purpose:** Validates the structure of a single plot event, ensuring it contains `catalyst`, `action`, and `resolution_state` fields to maintain continuity across chapters.

---

## 3. `context/jules`

The jules row manages the orchestration and recursive workflow control. Its context cell is minimal, focusing on state and verification.

### Manifest (`context/jules/manifest.toml`)
```toml
[cell]
row = "jules"
version = "1.0.0"

[ontology]
node_types = ["SessionState", "Evidence", "FrictionLog"]

[templates]
"friction_log" = { path = "templates/friction_log.md.jinja", inputs = ["session_id", "blocker_description", "tier"] }

[schemas]
"confidence_evidence" = { path = "schemas/confidence_evidence.schema.json", type = "json-schema-2020-12" }

[search_anchors]
"jules_protocol" = { path = "references/JULES_PROTOCOL.md", summary = "Discipline and gate requirements." }
```

### Template Example (`context/jules/templates/friction_log.md.jinja`)
```jinja
---
type: template
slug: friction_log
summary: "Template for recording a workflow friction event."
render_formats: [md]
output_path: "Plan/_friction/{{ session_id }}-{{ slug }}.md"
required_vars: [session_id, blocker_description, tier]
---
# Friction Log: {{ session_id }}

**Tier:** {{ tier }}

## Blocker Description
{{ blocker_description }}
```

### Schema Example (`context/jules/schemas/confidence_evidence.schema.json`)
**Name:** `tag:agency-system.local,2026:schema:jules/confidence_evidence`
**Purpose:** Validates the data structure required to pass Gate-1 of the `JULES_PROTOCOL`. It enforces that the payload includes a `confidence_score` (>= 0.90) and an `evidence_citations` array containing valid file/line references.
