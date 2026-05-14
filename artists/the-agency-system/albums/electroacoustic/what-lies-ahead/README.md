---
title: "What Lies Ahead"
release_date: ""  # YYYY-MM-DD (fill in when releasing)
genres: ["electroacoustic", "thematic"]
tags: ["cptsd", "did", "trauma-recovery", "plurality", "documentary-edge"]
explicit: false  # tentative — revisit in Phase 6 once tracks take shape
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
| **Album** | What Lies Ahead *(working title)* |
| **Genre** | electroacoustic *(umbrella — per-track sonic DNA varies widely; see Sonic Palette)* |
| **Tracks** | 13 *(structural target: 11 alter tracks + 1 worldview + 1 partner-view, with permission to break the pattern where the album wants to)* |
| **Status** | Concept — in planning |
| **Explicit** | TBD (Phase 6) |
| **Concept** | An album that lets every alter speak in their own voice, on their own terms, and be heard. cPTSD listeners meet the inner *Strömungen*; DID listeners recognize the form. |

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

Multi-voice rendering follows the **Voice DNA Protocol** (`overrides/voice-dna-protocol.md`).
Core rule that transfers from novel to lyrics: **voices are never labeled**. The listener
recognizes each alter through diktion, rhythm, vocabulary, and pause structure — never
through headers, name-adlibs, or `[Section]` labels.

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

13 tracks. Working target:

- **11 alter tracks** — one per alter (artist + 10 co-alters). Each carries its own sonic DNA per the Voice DNA Protocol's per-voice rules: syntax, vocabulary, rhythm. No alter is labeled.
- **1 worldview track** — the system's outer-facing view on the world. Likely candidate home for the *„Alles, was da ist…"* anchor line.
- **1 partner-view track** — perspective from the artist's partner. The album's external mirror.

Structure may yield to the album's wishes. Pattern is target, not cage. Detailed sequencing in Phase 4.

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

- **Beats**: [Production style description]
- **Samples**: [Sample sources/types if applicable]
- **Vocals**: [Vocal style and delivery]
- **Mood**: [Overall emotional tone]

## Tracklist

| # | Title | POV | Concept | Status |
|---|-------|-----|---------|--------|
| 01 | [Track Name](tracks/01-track-name.md) | [POV] | [Brief concept] | Not Started |
| 02 | [Track Name](tracks/02-track-name.md) | [POV] | [Brief concept] | Not Started |

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

### AI Art Platform
<!-- Set your platform: Midjourney, Leonardo.ai, DALL-E, Stable Diffusion -->
**Platform**: [Not selected]

### Image Prompt
*Generated by `/bitwize-music:album-art-director`. Platform-specific format.*

```
[Prompt will be generated in the format matching your selected platform.
Run /bitwize-music:album-art-director to create a visual concept and prompt.]
```

### Negative Prompt
<!-- Leonardo.ai / Stable Diffusion only. Remove this section if using Midjourney or DALL-E. -->
```
[Elements to exclude — only applicable for Leonardo.ai and Stable Diffusion]
```

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
