# the-agency-system DNA Skill — Spec & Jules Brief

**Status:** v1 — requirements locked (brainstorm). Layout + resolver schema
finalize in `/sc:design`. State-axis confirmed. Build via Jules (J1) +
local subagents (J2) + assembly (me).

**Goal.** A gate-skill in the in-repo `agency-system` plugin that, when work
starts on *the Agency System* (music **and** novel), asks whether the
artist/project really is the Agency System, then token-efficiently loads the
right DNA snippets into the relevant bitwize / writing process — via a unified
**2D matrix `Alter × State`** that fully integrates the Design, Novel, and
Music layers.

**Source overrides (the four docs):** `overrides/visual-language-guide.md`,
`overrides/image-style-spec.md`, `overrides/kohaerenz-protokoll-sprach-dna.md`,
`overrides/the-eleven.md`.

---

## 1. Locked decisions
- Home: in-repo `agency-system` plugin. Gate is skill-driven: `AskUserQuestion`
  "Artist/Projekt = the Agency System?" → context (Music/Novel/Design) →
  targeted snippet load. Optional SessionStart reminder-hook.
- Unified 2D matrix `Alter × State`, all three layers fully integrated.
  Design+Music reference by **function/role**; Novel by **name**; joined by a
  **bidirectional name↔function resolver**.
- Matrix cell = short inline essence **+ pointer** to atomic snippets.
- Map target = external bitwize repo (Jules clones in build). Scope = music
  **and** novel now.
- Decomposition = atomic snippet units + index.

## 2. Entity model (resolver — key = function)
Canonical key = **function/archetype**; names are layer aliases.

| function | class | novel/visual name | the-eleven label | layers | tier |
|---|---|---|---|---|---|
| host | ANP | Kael | The Container (Host) | all | core |
| rationalist | ANP | Lex | The Rationalist | all | core |
| protector | EP | Alex | The Protector | all | core |
| caregiver | EP | Rhys | The Caregiver | all | core |
| integrator | Meta | Selene | The Integrator (ISH) | all | core |
| fighter | EP | Nyx | The Fighter | all | core |
| child_freeze | EP | Kiko | The Child-Freeze | all | core |
| ambivalent | EP | Lia | The Ambivalent | all | core |
| sexualized_override | EP | Isabelle | The Sexualized-Override | all | core |
| collapsed | EP | Moros | The Collapsed One | all | core |
| witness | Meta | Argus | Witness-of-Witnesses | all | core |
| mirror_juna | — | Silas | — | visual/novel | mirror |
| mirror_aegis | — | Oblivion | — | visual/novel | mirror |
| sys_aegis, sys_mnemosyne, sys_erasure, sys_juna | — | (names) | — | novel | system |
| mode_narrator, mode_we | — | Erzähler / Wir-Stimme | — | novel | mode |

- **Blend support:** composites via `blend_of: [caregiver, protector]` (e.g.
  lyric "Ich" in *Lass mich*).
- **name_exposure rule:** `novel → name allowed`; `music|design → function/role
  only` (enforces voice-craft "no labels").

## 3. State axis (CONFIRMED)
| State | ASDLS Tier | Novel Stilebene/Mode | Yellow-type | Lead function(s) |
|---|---|---|---|---|
| S0 Homöostase | T0 | Stilebene 1 / ANP-control | — | host, rationalist |
| S1 Latenz/Freeze | T1 | Hypoarousal (1→2) | Latency Violet | child_freeze, collapsed |
| S2 Alert/Konflikt | T2 | Stilebene 2 / KW3 | Signal Yellow | fighter, protector |
| S3 Kollaps-Peak | T3 | Vortex 1 | Flame/Corrupted | collapsed (peak) |
| S4 Repair/Integration | T4 | Stilebene 3 + Coda | Kintsugi Gold | integrator, mode_we |

Orthogonal sub-tags: `conflict_with:[alter]`, `kernwelt_class:[P|paraconsistent|NP-hard|generative]`, `yellow_type` (design).

## 4. Matrix cell contract
Lookup `(function|name, state, layer[, bitwize_context])` →
`{ inline: "1–2 line essence", pointers: [snippet files] }`.

## 5. Snippet layout (PROPOSED — finalize in /sc:design)
```
skills/the-agency-system/
  SKILL.md                       # gate flow + when/how to load
  references/
    resolver.yaml                # function↔name↔visual, class, blend, tier, name_exposure
    matrix-index.yaml            # (function × state) → {inline, pointers} + bitwize-attachment
    state-axis.md                # S0–S4 + per-layer alias mapping
    bitwize-attachment.md        # entity/cross-cutting → bitwize skill
    entities/  host.md … witness.md   _ext/ silas.md oblivion.md aegis.md mnemosyne.md erasure-pol.md juna.md   _modes/ narrator.md we-voice.md
    states/    s0.md … s4.md
    cross-cutting/  glitch-typology.md color-thermodynamics.md semiotic-symbols.md composition-rules.md hard-rules.md collision-matrix.md specd-formula.md
```

## 6. Gate flow
1. Skill invoked (manual, or SessionStart reminder-hook nudges Claude).
2. `AskUserQuestion`: "Artist/Projekt = the Agency System?" → No = exit silently.
3. Yes → determine context (Music/Novel/Design; auto from active album/file else ask).
4. Load resolver + state-axis; per task, lookup `(alter, state)` → inline + only the needed pointer snippets.
5. **name_exposure gate** per layer (music/design = function; novel = name).

## 7. bitwize integration points
album-conceptualizer (roster/yellow/arcs) · lyric-writer (voice-fingerprint + hard-rules + state→alter) · lyric-reviewer (distinguishability) · voice-checker (consistency anchors) · suno-engineer (metatags + function-form, **no names**) · album-art-director (full Visual+ASDLS: hex/symbols/tier/SPECD/lens/negatives) · mastering-engineer (state→LUFS) · release-director (no-labels compliance). Novel: writing phases pull `voice.*` + `akt-stilebenen` + `collision-matrix`.

## 8. CLAUDE.md reference plan
New section "Arbeit an the Agency System (Musik/Novel)" linking the skill + the
4 overrides + `matrix-index.yaml`, plus the gate reminder.

## 9. Acceptance / stories
- Token-efficient: never load more than the snippets needed for (alter, state, context).
- Privacy hard gate: no alter names in music/design outputs.
- Resolver = single source; crosswalk 1:1 core-11 + extension tiers.
- Story: "As lyric-writer for *Lass mich* T07 (state S3, fighter+child_freeze blend), I get function descriptors + pointers, no names."

---

## 10. Jules / subagent build plan
- **J1 (Jules, external repos):** clone Anthropic `skill-creator` → conventions
  checklist (SKILL.md format, frontmatter, references/ pattern, scripts). Clone
  bitwize-music (`github.com/bitwize-music-studio/claude-ai-music-skills`) →
  precise per-skill field/phase map (refines §7). Return as md artifacts.
- **J2 (local subagents):** cut the 4 overrides into atomic `entities/`,
  `states/`, `cross-cutting/` snippets; build `resolver.yaml` + `matrix-index.yaml`.
  Depends on /sc:design (layout/resolver) + J1 field map.
- **J3 (me + subagents):** `SKILL.md` (gate flow), `bitwize-attachment.md`,
  validate against skill-creator checklist, add CLAUDE.md reference.
- **Split:** Jules = clone/research/bitwize field-map (context-heavy).
  Subagents = local doc decomposition + resolver/index. Me = state-axis, gate
  UX, assembly + review.
