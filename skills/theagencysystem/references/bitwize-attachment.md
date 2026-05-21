# Bitwize Attachment Map

Routing table for the **the-agency-system** gate skill. Tells the gate
*exactly* where, inside each live bitwize-music workflow skill, to inject the
artist's DNA snippets — and under which privacy constraint.

This map was built by introspecting the live skills in
`skills/music/<name>/SKILL.md`. Hook points use each skill's own wording
(phase names, field names, checklist labels) so the gate can target them
without re-reading the skill body.

## DNA reference files (load by name)

| Ref | What it carries |
|-----|-----------------|
| `references/resolver.yaml` | function ↔ name ↔ visual, class, blend, `name_exposure` |
| `references/matrix-index.yaml` | (function × state) → inline snippet + pointers |
| `references/state-axis.md` | S0–S4 state ladder |
| `references/entities/<function>.md` | per-entity 3-layer fingerprint (voice / music / visual) |
| `references/entities/_modes/{narrator,we-voice}.md` | non-alter narration modes |
| `references/states/s0..s4.md` | per-state expression (loudness, color, syntax) |
| `references/cross-cutting/{glitch-typology,color-thermodynamics,semiotic-symbols,composition-rules,hard-rules,collision-matrix,specd-formula}.md` | shared design + privacy guardrails |

Available entity functions on disk: `ambivalent, caregiver, child-freeze,
collapsed, fighter, host, integrator, protector, rationalist,
sexualized-override, witness` (+ `_ext/` extended cast, `_modes/`).

## `name_exposure` rule (critical)

- **novel layer** → alter NAME allowed (forward-looking; see last section).
- **music + design layers** → FUNCTION / ROLE ONLY, never the personal name.
  Enforce `name_exposure=function` from `resolver.yaml`. Suno metatags may use
  descriptive form (`[male mid-baritone, weary, dry close-mic]`) but never the
  character/name form (`[Container]`). See `cross-cutting/hard-rules.md`
  NO-LABELS section.

Every music/design row below states the constraint explicitly.

---

## album-conceptualizer

Roster/cast and per-track state assignment happen during the 7 planning
phases. Attach before Phase 1 (override-load slot) so the cast is in context.

| hook point (skill's own phase/field) | load these refs | layer | name_exposure |
|---|---|---|---|
| Phase 1 (Foundation) — Artist / Theme-Story | `resolver.yaml` | music (planning) | FUNCTION ONLY |
| Phase 2 (Concept Deep Dive) — "key characters/subjects" | `resolver.yaml` + `entities/_modes/{narrator,we-voice}.md` | music (planning) | FUNCTION ONLY |
| Phase 3 (Sonic Direction) — "Vocal approach (Narrator, character voices…)" | `matrix-index.yaml` + `state-axis.md` | music (planning) | FUNCTION ONLY |
| Phase 4 (Structure Planning) — per-track focus + Motifs & Threads / Character Threads table | `matrix-index.yaml` + `state-axis.md` | music (planning) | FUNCTION ONLY (Character Threads = function labels) |
| Phase 5 (Album Art) — visual concept discussion | `cross-cutting/{color-thermodynamics,semiotic-symbols}.md` + `state-axis.md` | design (planning) | FUNCTION ONLY |

---

## lyric-writer

Voice fingerprint per POV function + state lookup. Attach at the override-load
slot (before drafting line 1) and feed the 13-point check's POV/voice items.

| hook point (skill's own phase/field) | load these refs | layer | name_exposure |
|---|---|---|---|
| Workflow step 1.5 (Load album context) / override-load slot | `resolver.yaml` (state→function map) | music | FUNCTION ONLY |
| Drafting per POV section | `entities/<fn>.md` (voice layer) + `states/<sN>.md` | music | FUNCTION ONLY |
| 13-point check #4 (POV/Tense) — voice distinguishability per function | `entities/<fn>.md` + `cross-cutting/collision-matrix.md` | music | FUNCTION ONLY |
| Voice-switch handling (no headers/labels) | `cross-cutting/hard-rules.md` (NO-LABELS) | music | FUNCTION ONLY — never mark a switch, never name an alter |
| "We"-voice / narrator passages | `entities/_modes/{we-voice,narrator}.md` | music | FUNCTION ONLY |

---

## lyric-reviewer

QC gate. Attach for the voice-DISTINGUISHABILITY check across functions —
verify each POV part is recognizable by syntax/vocab alone, no name leaks.

| hook point (skill's own phase/field) | load these refs | layer | name_exposure |
|---|---|---|---|
| 14-point check #4 (POV/Tense) + #5 (Structure) — cross-function distinguishability | `resolver.yaml` + `entities/<fn>.md` (relevant functions) | music | FUNCTION ONLY |
| 14-point check #14 (Artist Name) — extend to alter-name leak scan | `cross-cutting/hard-rules.md` (NO-LABELS) | music | FUNCTION ONLY — flag any personal name in lyrics OR style box as Critical |
| Quality Bar gate (before "Ready for Suno") | `cross-cutting/collision-matrix.md` | music | FUNCTION ONLY |

---

## voice-checker

Advisory only (Warning/Info, never blocks). Attach consistency anchors per
function so AI-pattern flags are judged against the intended voice.

| hook point (skill's own phase/field) | load these refs | layer | name_exposure |
|---|---|---|---|
| Class 4 (Missing Idiosyncrasy) — per-function texture anchors | `entities/<fn>.md` (voice layer) | music | FUNCTION ONLY |
| Class 6 (Perfect Grammar) + Class 7 (Parallel Structure) — function-specific syntax norms | `entities/<fn>.md` | music | FUNCTION ONLY |
| Album-level scan (lyrics mode) — cross-function consistency | `resolver.yaml` | music | FUNCTION ONLY (advisory; never auto-rewrite) |

---

## suno-engineer

Metatags + Style Box. Strict: function-form descriptors only, NO NAMES.

| hook point (skill's own phase/field) | load these refs | layer | name_exposure |
|---|---|---|---|
| Style Prompt (Style of Music Box) — "[Vocal description] FIRST" | `entities/<fn>.md` (music/vocal layer) | music | FUNCTION ONLY — descriptive register only, e.g. `[male mid-baritone, weary, dry close-mic]` |
| Lyrics Box section tags (`[Intro]`, `[Verse]`…) | `cross-cutting/hard-rules.md` (NO-LABELS) | music | FUNCTION ONLY — NEVER character/name tags (`[Container]` forbidden); no name-adlibs |
| Artist/Band Name Warning + Quality Standards gate | `cross-cutting/hard-rules.md` | music | FUNCTION ONLY — enforce `name_exposure=function` from `resolver.yaml` |
| Voice Switching (dialogue/duets) | `entities/<fn>.md` (music layer) | music | FUNCTION ONLY — describe register contrast, not names |

---

## album-art-director

Full Visual + ASDLS direction: hex / symbols / tier / SPECD / lens / negatives.
Attach across the 6-step AI Art Generation Workflow. Sibling refs
(`visual-styles.md`, `prompt-examples.md`, `album-types.md`) supply
genre-visual-language and per-platform prompt formats — the DNA refs override
their color/symbol/composition choices.

| hook point (skill's own phase/field) | load these refs | layer | name_exposure |
|---|---|---|---|
| Step 1 (Concept Development) — color palette / imagery | `states/<sN>.md` + `cross-cutting/color-thermodynamics.md` | design | FUNCTION ONLY |
| Step 4 (Composition Planning) — layout / focal / depth | `cross-cutting/composition-rules.md` + `cross-cutting/specd-formula.md` | design | FUNCTION ONLY |
| Step 5 (Prompt Construction) — Subject / Style / Color / Composition | `entities/<fn>.md` (visual layer) + `cross-cutting/{semiotic-symbols,glitch-typology}.md` | design | FUNCTION ONLY |
| Step 5 negative-prompt field (Leonardo/SD/Midjourney) | `cross-cutting/hard-rules.md` (Negative-prompt list + ASDLS bans) | design | FUNCTION ONLY |
| Quality Standards gate (before finalizing) | `cross-cutting/hard-rules.md` (5% rule, one symbol/one tier) + `cross-cutting/collision-matrix.md` | design | FUNCTION ONLY |

ASDLS reminders to enforce here: ≤5% state color over ≥95% Terminal Black /
Deep Charcoal; one core symbol + one tier per image; hard-edge state-color
boundaries (no gradients); no daylight/retro-futurism/analog artifacts.

---

## mastering-engineer

State → loudness/LUFS tendency. Attach at the override-load + genre-confirm
step so per-state dynamic intent informs target LUFS within streaming bounds.

| hook point (skill's own phase/field) | load these refs | layer | name_exposure |
|---|---|---|---|
| Step 1.5 (Confirm Genre Settings) — per-track variations | `states/<sN>.md` (loudness/dynamics tendency) | music (audio) | FUNCTION ONLY (states map to tracks, not names) |
| Step 3 (Choose Settings) — `target_lufs` / dynamics per track | `states/<sN>.md` | music (audio) | FUNCTION ONLY |

Note: state tendencies steer *within* the -14 LUFS streaming standard and
genre presets — they do not override platform targets.

---

## release-director

NO-LABELS compliance gate. Attach to the 9-domain pre-release QA so no personal
name reaches distributor metadata, lyrics, art, or promo copy.

| hook point (skill's own phase/field) | load these refs | layer | name_exposure |
|---|---|---|---|
| Step 2 Pre-Release QA — domain 2 (Metadata), 4 (Lyrics Accuracy), 5 (Artwork), 9 (Promo Copy) | `cross-cutting/hard-rules.md` (NO-LABELS) | music + design (release) | FUNCTION ONLY — fail QA on any alter personal name in public-facing fields |
| Step 3 Distribution Prep — Streaming Lyrics validation | `cross-cutting/hard-rules.md` | music (release) | FUNCTION ONLY — streaming lyrics carry no name + no phonetics |
| Quality Standards gate (Before Any Upload) | `resolver.yaml` (`name_exposure` audit) | music + design (release) | FUNCTION ONLY |

---

## pronunciation-specialist

Pronunciation safety. DNA attaches only as function-keyed entries so phonetics
for cast terms are resolved without exposing personal names in lyrics.

| hook point (skill's own phase/field) | load these refs | layer | name_exposure |
|---|---|---|---|
| Step 1 (Automated Scan) — Names & Proper Nouns category | `resolver.yaml` (function-keyed pronunciation hints) | music | FUNCTION ONLY — phonetic spellings keyed to role/term, never a printed personal name in the Lyrics Box |

Note: if a cast member's name surfaces as a pronunciation risk, resolve it as a
function-keyed override entry; the Lyrics Box still ships function/descriptive
forms only.

---

## Novel (forward-looking)

`skills/novel/` is currently **EMPTY** (only `.gitkeep`). These are stub
attachments for when novel/prose skills land. The novel layer is the **only**
layer where the alter NAME is allowed.

| hook point (future novel skill) | load these refs | layer | name_exposure |
|---|---|---|---|
| Writing phases — character POV / interiority | `entities/<fn>.md` (full 3-layer) + `entities/_modes/{narrator,we-voice}.md` | novel | NAME ALLOWED |
| Scene-state / mood mapping | `state-axis.md` + `states/<sN>.md` | novel | NAME ALLOWED |
| Multi-alter scene staging / collisions | `cross-cutting/collision-matrix.md` + `resolver.yaml` | novel | NAME ALLOWED |

When novel skills are authored, refine these against the skills' own phase
names (this section is a placeholder, not introspected).
