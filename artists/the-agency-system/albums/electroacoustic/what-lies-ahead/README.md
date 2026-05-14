---
title: "What Lies Ahead"
release_date: ""  # YYYY-MM-DD (fill in when releasing)
genres: ["electroacoustic", "thematic"]
tags: ["cptsd", "did", "trauma-recovery", "plurality", "documentary-edge"]
explicit: true  # locked Phase 6 — artist's decision; trauma subject matter + abuse acknowledgment + sexualized-override alter render warrant the flag
streaming:
  soundcloud: ""
  spotify: ""
  apple_music: ""
  youtube_music: ""
  amazon_music: ""
sheet_music:
  songbook: ""
---

# What Lies Ahead

## Album Details

| Attribute | Detail |
|-----------|--------|
| **Artist** | the-agency-system |
| **Album** | What Lies Ahead |
| **Genre** | electroacoustic *(umbrella — per-track sonic DNA varies widely; see Sonic Palette)* |
| **Tracks** | 13 *(11 alter-led tracks + 1 worldview + 1 partner-view; Witness annotates across all, no dedicated track)* |
| **Status** | Phase 6 complete — ready for Phase 7 (track scaffolds) |
| **Explicit** | Yes (locked Phase 6) |
| **Concept** | An album that lets every alter speak in their own voice, on their own terms, and be heard. cPTSD listeners meet the inner *Strömungen*; DID listeners recognize the form. |

## Phase Overview

| Phase | Title | Status |
|-------|-------|--------|
| 1 | Concept & Thesis | ✓ Locked |
| 2 | Listener Takeaways & Research Direction | ✓ Locked |
| 3 | Research Synthesis & Craft Principles | ✓ Locked |
| 4 | Track Sequencing & Production Mapping | ✓ Locked |
| 5 | Album Art Concept & Visual Direction | ✓ Locked *(execution pending — see `ALBUM-ART.md`)* |
| 6 | Practical Details (Title, Explicit, Research Scope) | ✓ Locked |
| 7 | Confirmation & Finalization (Track Scaffold Files) | ⧗ In progress |

**Phase 6 decisions (locked):**
- **Title**: "What Lies Ahead" — approved as final title
- **Research scope**: Signed off as complete (6 reports, 100+ sources, 10 anti-patterns, creative license documented)
- **Explicit flag**: `explicit: true` — artist's call; trauma subject matter, abuse acknowledgment, sexualized-override alter rendering warrant the flag

**Current position**: Phases 1–6 complete. Ready for Phase 7 — track scaffold creation (13 skeleton track files in `tracks/`).

## Frontmatter Reference

### mastering (optional)

Per-album mastering settings. Currently supports:

- `adm_validation_enabled: true` — opt in to Apple Digital Masters
  inter-sample peak validation. **Defaults to OFF** even when
  global `config.yaml::mastering.adm_validation_enabled` is `true`.
  ADM runs the AAC encode/decode check on every mastered file and
  can add 3-5 min/track to the pipeline. Only enable when the
  album's source material is spectrally viable (well-balanced
  highs) AND you're submitting the album for Apple Digital Masters
  certification. For most Suno-generated albums, leave this off.

Example (opt in for this album only):

```yaml
mastering:
  adm_validation_enabled: true
```

Omit the block entirely to use the default (ADM off).

## Concept

### The Engine

**An album that lets every alter speak in their own voice, on their own terms, and be heard.**

This is the primary thesis. Not "trauma recovery album," not "concept album about cPTSD/DID" — those are *descriptions* of the album from outside. From inside, the album is a way for the artist's system to be heard, as itself, in art. Audience-facing benefit (listeners with DID feeling seen, listeners with cPTSD feeling met) is the byproduct of doing that with full integrity, not the design target.

### Listener Takeaways

**For cPTSD listeners:**
- Recovery is **cyclic**, not linear. Relapses don't erase gains.
- **The worst is survived.** You are *here*, on the other side of what should have killed you.
- There are inner **Strömungen** (currents, tides, undertows) — trauma states that move through you. Knowing them is part of safety.

**For DID listeners:**
- *(Deferred — open question pending research. The takeaway must be named truthfully or not at all. Returning to this after research is the correct sequence, not a delay. See RESEARCH.md.)*

### Lyric Seed (Anchor Line)

> *„Alles, was da ist, ist okay und darf bleiben."*
> *(Therapist's line. Possible album epigraph, worldview-track anchor, or recurring lyrical motif. To be placed when its right home becomes obvious.)*

### Voice Craft Reference

Multi-voice rendering follows the principles in `../../../../../overrides/voice-craft-principles.md`.
Core rule: **voices are never labeled.** The listener recognizes each alter through
diktion, rhythm, vocabulary, and pause structure — never through headers, name-adlibs,
or `[Section]` labels. For per-alter verbal signatures and prosodic anchors, see
`the-eleven.md` in this album folder.

**Duet / voice-switch preference:** The artist favors **duets that switch between voices mid-song** —
not call-and-response between two singers performing the same character, but genuine
alter-to-alter dialogue inside a single track. This is a distinguishing structural device for the
album and a natural fit for DID representation: alters in conversation, recognized by *how*
they speak rather than by any tag.

### Author's Named Fear (as Creative Material)

The artist named — and gave permission to use as material — a specific fear:
losing control, beginning to understand why memory fails, what role they play in
suppressing alters. The album does **not** need to resolve this. Some tracks can
sit inside the fear without offering exit. The album bears witness; it is not a
recovery manual.

## Structure

13 tracks total. Locked architecture:

- **11 alter-led tracks** — 6 solos + 5 alter-to-alter duets covering 10 of **The Eleven** (5 ANP + 5 EP). Witness, the 11th alter, has no dedicated track — he annotates across all 13. Each track carries its own sonic DNA. No alter is labeled in lyrics or section headers; identity is carried by syntax, vocabulary, rhythm, pause structure. See `the-eleven.md` for full archetype profiles, phobia/alliance networks, and lyrical hooks.
- **1 worldview track** (track 12) — most fractured. All eleven voices simultaneously, in incompatible registers. The album's central artistic refusal of the "system speaks as one" climax.
- **1 partner-view track** (track 13) — outside / song-like. Container + Partner duet — the only fully-resolved perspective. The witness from beyond the system.

**The Eleven — Quick Reference**

| # | Archetype | Class | Production World | Arc |
|---|-----------|-------|------------------|-----|
| 1 | Container (Host) | ANP | Mixed — container of all registers | → Fractality |
| 2 | Rationalist | ANP | Orchestral electronic (cold strings) | → Intuition |
| 3 | Protector | ANP | Band-driven dark electro rock | → Growth |
| 4 | Caregiver | ANP | Orchestral electronic (warm) | → Acceptance → Kudzu (Act II danger) |
| 5 | Integrator (ISH) | ANP | Spacious electroacoustic, reverbed | → Mediator |
| 6 | Fighter | EP (Fight) | Band-driven dark electro rock | → Constructive protection |
| 7 | Child-Freeze | EP (Freeze) | Piano-and-voice intimate | → Trust |
| 8 | Ambivalent | EP (Approach/Withdraw) | Piano-intimate, microtonal | → Leave superposition |
| 9 | Sexualized-Override | EP (Fight-via-control) | Low-register electronic, controlled | → Vulnerability |
| 10 | Collapsed One | EP (Submit/Collapse) | Sub-tempo drone / near-spoken | → Dragon-fight |
| — | Witness-of-Witnesses | Meta | **Annotative across all tracks** (no dedicated track) | → Constructive critique |
| W | Worldview | — | Most fractured (all eleven at once) | The album's structural refusal of forced integration |
| P | Partner-view | — | Outside / song-like | The album's stable horizon |

### Album Architecture — LOCKED

**13 tracks. 13 voices.** The Witness has no dedicated track — he lives across all of them as annotative voice. The album's content density is in *dialogue* — explicit alter-to-alter conversation is the central structural move.

**Locked track content (provisional sequencing — see Pending Research):**

| Type | Count | Tracks |
|---|---|---|
| **Solos** | 6 | Container, Rationalist, Caregiver, Fighter, Sexualized-Override, Collapsed One |
| **Alter-alter duets** | 5 | Container+Integrator · Protector+Fighter · Child-Freeze+Ambivalent · Caregiver+Sexualized-Override · Collapsed One+Integrator |
| **Worldview** | 1 | All voices simultaneously, most fractured (form: pending research) |
| **Partner-view** | 1 | Container + Partner duet (outside the system, locked) |

Alter appearance counts: Container 2, Rationalist 1, Protector 1 (duet only), Caregiver 2, Integrator 2 (duets only — no solo), Fighter 2, Child-Freeze 1 (duet only), Ambivalent 1 (duet only), Sexualized-Override 2, Collapsed One 2. **Witness annotates across all 13 tracks.**

### Research Synthesis

Six research runs completed (clinical TSDP/ISH/Gatekeeper, DID community preferences, DID-in-music, trauma-album sequencing, cPTSD broad, cPTSD craft-deep). Findings consolidated in **`RESEARCH.md`** — that file is the new working reference for craft decisions. Key headlines:

- **The hinge insight:** *"a 'part' without amnesia is a current."* Strömungen sits exactly at Peter Levine's vortex theory ↔ cPTSD ego-states. Single most powerful audience-bridge concept.
- **Worldview-as-most-fractured serves both audiences differently** — DID listeners hear "my system is not a problem"; cPTSD listeners hear "my recovery is not a line." The album does not need to explain which reading is correct. Depth segments the audience.
- **97% community preference for functional multiplicity** validates the locked refusal-of-fusion structure.
- **The DID-concept-album slot is functionally unoccupied.** Nat Puff has the songs; nobody has the album. The user can credibly occupy this position.
- **New craft principle: deliberate bleed.** Voices distinct *but porous* — passive influence, partial co-fronting, unattributable lines. Otherwise per-alter voice metatags risk reading as vocal cosplay (the Shyamalan / Slim-Shady pattern).
- **The Witness has three registers across the album:** helper observation (tracks 1–3, transition at 4) → outer-critic attack (5–9) → inner-critic re-voiced (10–12) → departs entirely (13). The shift IS the inner critic's mechanism per Pete Walker.
- **Emotional flashbacks as production callback:** late track quotes early-track motif at 6–8 BPM slower. Same notes, different body.
- **Partner-view as Container + Partner duet** (the partner as external memory of the system) — research recommends this strongly.

### Locked Sequence (v3 — research-grounded, post-synthesis)

| # | Track | Function | Witness register |
|---|---|---|---|
| 1 | Container (solo) | Voiced-thesis opener. Wound as ground from downbeat 1. | Helper / observation |
| 2 | Container + Integrator (duet) | The closed loop — collusion that believes itself to be care | Helper / observation |
| 3 | Rationalist (solo) | Fury early — cold logic almost succeeding before it gives | Helper / observation |
| 4 | Protector + Fighter (duet) | Method conflict, kinetic. **Outer-critic flip lives here** — Protector self-blames, Fighter attacks outward. The duet IS Walker's vacillation. | Helper → outer-critic transition |
| 5 | Fighter (solo) | Rage alone — what she is when no one needs protecting | Outer-critic attack |
| 6 | Caregiver (solo) | Warmth interior, attachment betrayal somatically (Ethel Cain template). **Fawn moment lives here** — throat-tight yes, body-site per verse. | Outer-critic attack |
| 7 | Collapsed One (solo) | **Structural axis** — Black Lake / Fourth of July position. Longest, most stripped. The album's gravity. | Outer-critic attack |
| 8 | Collapsed One + Integrator (duet) | Sufjan license. Integrator arrives *in* the wreckage, not as rescue. | Outer-critic attack |
| 9 | Child-Freeze + Ambivalent (duet) | **Recovery valley — genuinely soft.** Silent recognition across an impossible gap. Earned by everything before it. | Outer-critic attack → softening |
| 10 | Sexualized-Override (solo) | Performance reasserts. The system can't stay in vulnerability. Control returns. | Inner-critic re-voiced begins |
| 11 | Caregiver + Sexualized-Override (duet) | Climbing tension. The Caregiver's Kudzu surfaces as the Override resists. **Production callback lives here — track 6's Caregiver motif returns at 6–8 BPM slower, suppressed under the Override's refusal.** | Inner-critic re-voiced |
| 12 | **Worldview** (most fractured) | Penultimate fracture. All voices at once. Accumulated self-attack at maximum. | Inner-critic re-voiced |
| 13 | **Partner-view** (Container + Partner) | Benediction outward. **The only track with no Witness presence** — partner outside the system, the system drops its self-watching and simply IS. | None — Witness departs |

**Witness register-shift summary:** helper observation (1–3) → transition (4) → outer-critic attack (5–9) → inner-critic re-voiced (10–12) → Witness departs entirely (13). The Witness's *departure* in track 13 is part of the structural argument: when the partner sees you whole from outside, the system stops needing to watch itself.

**Three sub-decisions resolved by v3 locking:**
- **Outer-critic flip placement**: track 4 (Protector + Fighter duet enacts the inner/outer-critic vacillation structurally).
- **Fawn moment placement**: track 6 (Caregiver solo — her caregiving is fawn-coded; throat-tight yes lives in her attachment-betrayal lyric).
- **Production callback / emotional flashback**: track 11 quotes track 6 phrase at 6–8 BPM slower. Same melodic phrase, different body. The Kudzu's first surfacing as somatic memory.

### Phase 4 Sub-Decisions — Resolved by v3 Sequence Lock

See `RESEARCH.md` §5 for full context. All decisions below are locked into the Locked Sequence (v3) above:

- **Caregiver Kudzu rendering** — somatically in her solo (#6), surfacing in duet (#11) as the Override resists.
- **Partner-view form** — Container + Partner duet (track 13).
- **Witness register-shift across album** — helper (1–3), transition (4), outer-critic (5–9), inner-critic re-voiced (10–12), departs at 13.
- **Fawn moment placement** — track 6 (Caregiver solo).
- **Outer-critic flip placement** — track 4 (Protector + Fighter duet).
- **Production callback / emotional flashback** — track 11 quotes track 6 phrase at 6–8 BPM slower.

### Open (still pending)

- **Optional Truddi Chase reference** — a track that explicitly names the refusal of fusion as a love song from the system to itself. Decision deferred to the lyric-writing phase, where it will become obvious whether the line belongs in the worldview track (#12), the partner-view track (#13), Witness annotation, or declined entirely.

### Resolved Decisions Recap

- **Genre umbrella:** electroacoustic
- **Album type:** thematic with documentary edge
- **13-voice architecture:** 11 alters + worldview + partner-view (= novel-side "Mirror-Voices" reframed)
- **The Witness:** annotative across all tracks, no dedicated song
- **Integrator = Gatekeeper too.** Co-responsible (with the Container's avoidance) for the system's forgetting. Curatorial patience, not passive. (See `the-eleven.md` profile.)
- **Suno Voice Metatags:** specific gender/register/texture assigned per alter for vocal differentiation. (See `the-eleven.md`.)
- **Worldview = most fractured** (not most integrated). The album's central refusal of forced integration.
- **Partner-view = Container + Partner duet** (outside the system; locked in v3 sequence).
- **Duet preference:** alters in genuine dialogue mid-song, recognized by syntax not labels.
- **Five alter-alter duets** (above).

Structure may yield to the album's wishes. Pattern is target, not cage.

## Themes

- **Plurality as survival**, not pathology — alters as the architecture that kept the system alive
- **Cyclic progress** — recovery without linearity; relapses do not erase what's been gained
- **The worst is survived** — present-tense safety as the album's quiet ground
- **Strömungen** — inner currents, trauma states felt as moving water
- **Being heard** — what happens to an alter when their voice is rendered, not muted
- **Hope without resolution** — *„What Lies Ahead"* as an open horizon, not a promised destination
- **Fear, named** — the active fear of control loss, memory gaps, and the role of suppression — as witness, not problem to solve

## Motifs & Threads

*(Remove this section if not a concept/narrative/thematic album)*

### Lyrical Motifs

| Motif | Description | First Appears | Recurrences |
|-------|-------------|---------------|-------------|
| [phrase/image] | [what it represents] | Track XX | Track XX (context), Track XX (context) |

### Character Threads

| Character/Voice | Arc Summary | Tracks |
|-----------------|-------------|--------|
| [name/voice] | [how they develop across the album] | XX, XX, XX |

### Thematic Progression

| Track | Theme Focus | Advances From | Sets Up |
|-------|-------------|---------------|---------|
| 01 | [theme] | — | [what it establishes for later] |
| 02 | [theme] | Track 01's [element] | [what it sets up] |

*Seeded by album-conceptualizer during Phase 4. Updated by lyric-writer as tracks are written.*

<!-- OST: Include this section for OST albums (video game, film, TV, anime, etc.). Remove if not an OST. -->

## World / Setting

| Attribute | Detail |
|-----------|--------|
| **Media Type** | [Video Game / Film / TV Series / Anime / Theater / Podcast] |
| **Title** | [Fictional property name] |
| **Genre** | [Platformer / RPG / Noir / Sci-fi / Slice-of-life / etc.] |
| **Setting** | [Fantasy / Sci-fi / Post-apocalyptic / Modern / Historical / etc.] |
| **Era/Aesthetic** | [8-bit retro / Cinematic / Noir / Cel-shaded / etc.] |

### Locations & Scenes

| # | Location/Scene | Mood | Track(s) |
|---|---------------|------|----------|
| 1 | [Location or scene name] | [Mood description] | XX |

### Leitmotif Plan

| Theme | Represents | First Appears | Variations |
|-------|-----------|---------------|------------|
| [Main theme melody] | [What it represents] | Track XX | Track XX (minor key), Track XX (orchestral) |

*Leitmotifs are tracked here AND in the Motifs & Threads section. This table focuses on musical themes; Motifs & Threads tracks lyrical/textual callbacks.*

<!-- END OST -->

## Sonic Palette

### Reference Triangle

| Reference | Brings | Territory it opens for this album |
|---|---|---|
| **Björk — *Vulnicura*** (2015) | Orchestral strings woven through electronics; voice raw and central; trauma as chronological documentation; dark beauty without prettification | Orchestral-electronic tracks. Strings as grief, not decoration. Microtonal vocal phrasing for integrator-style alters. |
| **Secret Cameras — *Our Love*** (2026) | Full-band dark electro rock with post-punk lineage (Depeche Mode / Interpol / Placebo / The National / Radiohead); voice with built-in "darkness quality" | Band-driven tracks. Protector/fighter alters live here. Guitar/bass/drums/synths anchored, not just electronic. |
| **Left at London — *Will My Alters Go to Heaven?*** | Piano-and-voice intimacy; bedroom-pop production; lyrically unflinching about DID; treats plurality as self-evident (not metaphor) | Sparse tracks. Vulnerable alters (child alters, freeze, collapse). The lyrical permission to be direct rather than gestural. |

### Production Spectrum (held together, not fragmented)

The three references form a coherent *spectrum*, not three competing aesthetics. The album can run:

> **piano-and-voice intimate** ↔ **orchestral electronic with strings** ↔ **full dark electro rock band**

…held together by:

- **Voice-forward production** — always. The voice carries meaning; production serves it.
- **Dark electro / post-punk aesthetic** as connective tissue across the spectrum.
- **Songcraft anchoring** — even the most experimental tracks remain *songs*, not soundscapes.
- **Lyrical directness** — willing to name, not just gesture (Left at London permission).
- **Trauma rendered, not aestheticized** — strings as grief, not decoration (*Vulnicura* permission).

### Adjacent Influences (likely to surface)

Carrying the Secret Cameras post-punk lineage forward: **Depeche Mode** (*Violator*, *Ultra*), **NIN** (*The Fragile* — quieter side especially), **Massive Attack** (*Mezzanine*), **Portishead** (*Third*), **Radiohead** (*In Rainbows*, *A Moon Shaped Pool*), **Placebo**. For the more vulnerable / piano-led territory: adjacent to **Mitski**, **Phoebe Bridgers**, and Left at London's broader catalog.

### Mood / Palette Notes

- **Beats / Rhythm** — varied. Some tracks band-driven (live drums + electronics), some pulse-led electronic, some no rhythm at all (piano-only or drone).
- **Vocals** — central. Plural. *Never labeled* (per voice-DNA protocol). Recognized through diktion, vocabulary, rhythm, pause structure. Microtonal phrasing welcome.
- **Duets** — alter-to-alter dialogue inside single tracks. Not call-and-response between performers; genuine internal dialogue rendered as song.
- **Mood** — dark but never theatrical; intimate even at maximum density; songcraft over soundscape; honest over beautiful (when forced to choose).
- **Strömungen** — the album's tonal undertow. Some tracks *are* the current. Some tracks resist it. Some tracks ride it.

### Per-Alter Production Mapping

Archetype-to-production map as a **starting point**, with exceptions documented as the system reveals them. The map is a scaffold for Phase 4 sequencing, not a constraint.

**Baseline map (archetype → production world):**

- **Protector / Fighter alters** → band-driven dark electro rock (Secret Cameras territory)
- **Caregiver / Host / Integrator** → orchestral electronic (*Vulnicura* territory)
- **Child / Freeze / Collapse alters** → sparse piano-and-voice intimate (Left at London territory)

**Exceptions:** *(To be filled in per-alter — alters whose production world contradicts their archetype. Surface them as they emerge.)*

### Worldview Track — Most Fractured

**Locked-in artistic choice.** The worldview track is the album's most fractured production, not its most integrated. The system's view of the world is **not a single reconciled view** — it is all voices held simultaneously, in their incompatible registers, without resolution.

This is the album's central artistic refusal: most trauma-recovery albums place a "system speaks as one" moment as the climax. *What Lies Ahead* refuses that. Worldview as polyphonic chaos says: **plurality is not a wound to integrate. The worldview IS the plurality**. The track holds chorus without becoming monolith — every voice remains distinguishable inside the simultaneity. All voices, all styles, all Strömungen at once.

Production direction: maximum simultaneity. Multiple vocal layers in incompatible styles co-existing. No alter is named; recognition is carried by syntactic and timbral fingerprint alone.

### Partner-View Track — Outside / Song-Like

**Locked-in artistic choice.** The partner-view track sits *outside* the system. Cleanest production on the album. The only track that fully resolves.

This is the album's stable horizon — the only fully-resolved perspective the album allows itself. Everything else either stays inside the system or stays inside the current. The partner is the witness who sees the system whole, from beyond. Likely the album's emotional gut-punch track.

Production direction: cleanest, most "song-like" rendering. Vocal-forward. Likely sparser instrumentation. Could be the most "Vulnicura *Stonemilker*-ish" production on the record — but with the partner's voice as the carrier, not the system's.

## Tracklist

Working titles — final lyric titles emerge during the lyric-writing phase. Status reflects current track state.

| # | Title | POV | Concept | Status |
|---|-------|-----|---------|--------|
| 01 | [Where I Begin](tracks/01-where-i-begin.md) | Container (solo) | Voiced-thesis opener. Wound as ground from downbeat 1. | In Progress |
| 02 | [The Closed Loop](tracks/02-the-closed-loop.md) | Container + Integrator (duet) | The closed loop — collusion that believes itself to be care. | Not Started |
| 03 | [Cold Engine](tracks/03-cold-engine.md) | Rationalist (solo) | Fury early — cold logic almost succeeding before it gives. | Not Started |
| 04 | [Method Conflict](tracks/04-method-conflict.md) | Protector + Fighter (duet) | Method conflict, kinetic. Outer-critic flip enacted structurally. | In Progress |
| 05 | [Nothing Left to Protect](tracks/05-nothing-left-to-protect.md) | Fighter (solo) | Rage alone — what she is when no one needs protecting. | Not Started |
| 06 | [Throat-Tight Yes](tracks/06-throat-tight-yes.md) | Caregiver (solo) | Warmth interior, attachment betrayal somatically. Fawn moment lives here. | Not Started |
| 07 | [Where the Ground Was](tracks/07-where-the-ground-was.md) | Collapsed One (solo) | Structural axis — longest, most stripped. The album's gravity. | Not Started |
| 08 | [In the Wreckage](tracks/08-in-the-wreckage.md) | Collapsed One + Integrator (duet) | Sufjan license. Integrator arrives *in* the wreckage, not as rescue. | Not Started |
| 09 | [Across the Gap](tracks/09-across-the-gap.md) | Child-Freeze + Ambivalent (duet) | Recovery valley — genuinely soft. Silent recognition across an impossible gap. | Not Started |
| 10 | [Performance Returns](tracks/10-performance-returns.md) | Sexualized-Override (solo) | Performance reasserts. The system can't stay in vulnerability. Control returns. | Not Started |
| 11 | [Kudzu Surfaces](tracks/11-kudzu-surfaces.md) | Caregiver + Sexualized-Override (duet) | Climbing tension. Caregiver's Kudzu surfaces; production callback to track 6 at −6–8 BPM. | Not Started |
| 12 | [All Voices at Once](tracks/12-all-voices-at-once.md) | Worldview (all 11 voices) | Penultimate fracture. All voices simultaneously. Accumulated self-attack at maximum. | Not Started |
| 13 | [From Outside](tracks/13-from-outside.md) | Container + Partner (duet) | Benediction outward. The only track with no Witness presence — partner outside the system. | Not Started |

## Key Characters

*(Remove this section if not a narrative album)*

### [Character Group 1]
- **Name** - Role and description

### [Character Group 2]
- **Name** - Role and description

## Production Notes

<!-- SERVICE: suno -->
**Suno Persona** (optional):
| Attribute | Value |
|-----------|-------|
| **Persona Name** | [Name in Suno] |
| **Persona Link** | [Suno persona URL] |

**Suno Settings**:
- **Target Duration**: [3:30–5:00]
- Per-track overrides noted in individual track files
- [Vocal consistency notes]
- [Production continuity notes]

**Style Prompt Base**:
```
[Base style prompt to use across all tracks, modified per track as needed]
```
<!-- /SERVICE: suno -->

## Source Material

*(Remove this section if not based on real events)*

- [Source 1](URL)
- [Source 2](URL)

<!-- DOCUMENTARY/TRUE STORY ALBUMS: Include this section for albums based on real people/events. Delete if purely fictional. -->

## Documentary Standards

### Album Classification

| Attribute | Selection |
|-----------|-----------|
| **Album Type** | ☐ True Crime/Documentary / ☐ Dramatized Story / ☐ Inspired By / ☐ Fictional |
| **Real People Featured** | ☐ Yes / ☐ No |
| **Legal Sensitivity** | ☐ High / ☐ Medium / ☐ Low |

### Narrative Approach

| Principle | Approach |
|-----------|----------|
| **Primary Voice** | [e.g., Third-person narrator throughout] |
| **Perspective on Subjects** | [e.g., External observation, not impersonation] |
| **Quote Handling** | [e.g., Paraphrased and attributed, or narrator describes what was said] |
| **Artistic License** | [e.g., Dialogue smoothed for flow, timelines compressed] |

### Real People Depicted

| Person | Role in Album | Depicted How | Sensitivity |
|--------|---------------|--------------|-------------|
| [Name] | [Protagonist/Subject/etc.] | [Narrator describes / Quotes attributed / etc.] | [High/Med/Low] |

### Legal Safeguards

- [ ] **No defamation**: All negative claims are documented facts from public sources
- [ ] **No fabricated statements**: Real people's words are sourced, paraphrased, or described (not invented)
- [ ] **Fair use/commentary**: Album constitutes commentary on matters of public interest
- [ ] **Public figures doctrine**: Subjects are public figures or involved in newsworthy events
- [ ] **No private facts**: Private information only included if already public or newsworthy
- [ ] **Narrator voice**: Tracks maintain storyteller perspective, not impersonation

### Source Verification Status

Source verification is tracked per-track in each track file's `Sources Verified` field (single source of truth). Use `/bitwize-music:resume` or `/bitwize-music:validate-album` to see verification status across all tracks.

### Legal Notes

[Album-level legal considerations, potential sensitivities, and mitigations]

### Disclaimer Text

*(Optional: Include in album description/liner notes)*

```
[e.g., "This album is a dramatic interpretation of documented events.
All factual claims are based on publicly available sources including [source names].
Dialogue and internal thoughts are dramatized for artistic purposes."]
```

<!-- END DOCUMENTARY SECTIONS -->

## Album Art

### Phase 5 — Art Direction (LOCKED)

**Platform**: DALL-E 3 (via ChatGPT)

**Visual Concept**: The system as a single body experiencing multiple currents simultaneously—not multiple people, but one body as a landscape of inner movement. The image holds darkness and forward motion without resolution.

**Core Metaphors**:
- **Water as Strömungen** — Multiple pressures moving through a single substance; the logic of water guides layered translucence and undertow
- **The Body as Landscape** — Plurality rendered as terrain (spine, shoulders, collapse) seen from inside; somatic, not objective
- **Forward Motion Without Destination** — Movement toward the frame's edge with no arrival visible; dark dignity in unknowing

**See `ALBUM-ART.md` for full direction, DALL-E 3 craft notes, refinement anchors, iteration plan, and upscaling guidance.**

### Image Prompt (DALL-E 3 — v1)

Paste directly into ChatGPT. The "I NEED to use the exact prompt below" prefix often (not always) prevents DALL-E 3 from silently rewriting:

```
I NEED to use the exact prompt below without rewriting:

A single human form suspended in deep mineral water, photographed from within the water itself. 
The figure is seen from behind and slightly above, abstracted—no facial features visible, no recognizable identity. 
The body reads as terrain: the curve of the back like a ridge of stone, shoulders like the slope of dark hills, 
the spine traced as a single line of pressure. Layered translucent currents move through and around the form simultaneously, 
each current flowing in a different direction, none cancelling the others. 
The water is opaque, heavy, mineral-rich—dark slate, dark mercury, dark iron. No bright reflection, no ripples on the surface. 
The composition flows toward the right edge of the frame, suggesting motion that continues beyond the image. 
The light source is diffuse, ambient, ungenerous—neither sunlit nor shadowed-noir, but the soft uniform light of overcast depth. 
Quiet color palette: charcoal, deep teal, slate grey, hints of unsaturated bronze in the deepest currents. 
The aesthetic is contemporary fine-art photography meets generative abstraction—restrained, somatic, unsentimental, 
the visual language of a documentary rather than a fantasy. Texture forward, drama withheld.
Square 1:1 aspect ratio. 
Bottom right corner: the text "the-agency-system" in clean modern serif font, small and unobtrusive, integrated with the composition.
```

**Practical notes:**
- DALL-E 3 does **not** support negative prompts — direction is given through positive descriptions
- DALL-E 3 outputs at 1024x1024px; upscale to ≥3000x3000px before distribution (Upscayl recommended)
- If DALL-E 3 mangles the in-image artist name (frequent), regenerate without the text and add the name in post-editing

**Note**: Artist name should always appear in the bottom right. Preserve the artist's preferred casing/spelling.

### File Naming Convention

Save generated album art using `/bitwize-music:import-art` or manually to these locations:
- **Audio directory**: `{audio_root}/artists/{artist}/albums/{genre}/{album}/album.png` (used by promo videos, SoundCloud)
- **Content directory**: `{content_root}/artists/{artist}/albums/{genre}/{album}/album-art.png` (tracked in git)

Format: PNG preferred, JPEG acceptable. Resolution: at least 3000x3000 for distribution, 1500x1500 minimum.

## SoundCloud

### Description
*Copy this into SoundCloud's description field:*

```
[Album description with concept, themes, credits]
```

### Genre
```
[SoundCloud genre dropdown selection]
```

### Tags
```
[tag1, tag2, tag3, tag4, tag5]
```

## Distributor Genres

| Attribute | Selection |
|-----------|-----------|
| **Primary Genre** | [e.g., Hip-Hop/Rap, Electronic, Rock, Pop] |
| **Secondary Genre** | [e.g., Electronic, R&B/Soul, or "None"] |
| **Electronic Subgenre** | [Required if Primary or Secondary is Electronic] |

*Common primary genres: Hip-Hop/Rap, Electronic, Pop, Rock, R&B/Soul, Alternative, Metal, Folk, Country, Jazz, Classical, Soundtrack, Spoken Word*

*Electronic subgenres: Electronica/Downtempo, House, Deep House, Techno, Drum & Bass, Dubstep, Trance, Chill Out, Big Room, Breaks, Electro House, Glitch Hop, Minimal/Deep Tech, Progressive House, Psy-Trance, Tech House*

---

## Release Info

*(Fill in this section when album is complete and released)*

| Attribute | Detail |
|-----------|--------|
| **Released** | [Month Year] |

### Track Listing

| # | Title | Duration | Listen |
|---|-------|----------|--------|
| 01 | [Track Name] | 0:00 | [SoundCloud](URL) |
