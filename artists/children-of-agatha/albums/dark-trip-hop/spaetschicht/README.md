---
title: "Spätschicht"
release_date: ""  # YYYY-MM-DD (fill in when releasing)
genres: ["dark-trip-hop"]
tags: ["night-shift", "psychiatry", "medication", "dissociation", "cinematic-bass", "trip-hop", "collection", "dark-comic"]
explicit: false  # true or false  # TBD — drug/psychiatric content may push some tracks explicit
# anchor_track: null  # Optional: 1-based track number to anchor album mastering (issue #290). Empty = auto-select by composite score.
streaming:
  soundcloud: ""    # Fill in when released
  spotify: ""       # Fill in when released
  apple_music: ""   # Fill in when released
  youtube_music: "" # Fill in when released
  amazon_music: ""  # Fill in when released
sheet_music:
  songbook: ""
# mastering:  # Optional - per-album mastering settings
#   adm_validation_enabled: true
# slug: ""  # Optional - only uncomment if you need to override auto-generated slug
---

# Spätschicht

## Album Details

<!-- NOTE: When releasing, set Status: Released and fill in release_date in frontmatter. Albums stay in place. -->

| Attribute | Detail |
|-----------|--------|
| **Artist** | [Children of Agatha](../../../README.md) |
| **Album** | Spätschicht |
| **Genre** | Dark Trip Hop / Cinematic Bass |
| **Album Type** | Collection |
| **Tracks** | TBD |
| **Status** | Concept |
| **Explicit** | TBD |
| **Concept** | Party in der Psychiatrie. Während die Spätschicht des Personals schläft, machen die Patient:innen der Agatha-Klinik nachts ihre eigene Feier — Medikamentenwagen als Bar, Neonlicht als Stroboskop, „Tabletten für jeden". Eine Collection bass-getragener, benebelter Stücke über medikamentöse Euphorie, Dissoziation und die dunkle Komik des Ausgeliefertseins. Gleicher Ort wie *The Long Corridor* (St. Agatha), entgegengesetzter Ton: sardonisch, transgressiv, hypnotisch. |

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

*Spätschicht* spielt nachts auf Station der St.-Agatha-Klinik. Während die Spätschicht des Personals schläft oder wegsieht, machen die Patient:innen ihre eigene Feier — der Medikamentenwagen als Bar, das Neonlicht als Stroboskop, „Tabletten für jeden". Es ist eine echte Euphorie und gleichzeitig eine hohle: Dark Trip Hop mit Cinematic Bass als Soundtrack einer medikamentösen Nacht.

Erzählt wird durchgehend aus einem **kollektiven „Wir"**. Das ist keine Stilfigur, sondern der eigentliche Stoff des Albums: Die Medikation löst auf, wer die Einzelnen sind, und das „Ich" zerfließt auf dem Dancefloor zu einem einzigen Organismus. „Children of Agatha" ist hier kein Bandname, sondern ein wörtlicher Zustand — ein Wir, das nur existiert, weil das Ich verschwunden ist. Niemand weiß mehr, welches Gefühl wem gehört, welche Fröhlichkeit echt ist und welche Nebenwirkung.

Der Ton ist dokumentarisch kühl und urteilt nicht. Die Platte feiert nicht mit und mahnt nicht — sie hält die Euphorie und den Riss darunter im selben Bild. Gleicher Ort wie *The Long Corridor* (St. Agatha), entgegengesetzter Ton: dort elegisch und heilend, hier sardonisch, transgressiv, hypnotisch.

## Structure

Collection — eigenständige Stücke, lose verbunden über Ort (Station, nachts), Stimme (das kollektive Wir) und Sound (verschwimmender Cinematic Bass). Kein erzwungener Handlungsbogen, aber ein loser Nachtverlauf von der ersten Tablettenrunde bis zur Morgenvisite ist als Sequenzierungs-Idee verfügbar (siehe Tracklist, Phase 4).

## Themes

- **Auflösung des Ich** — das Selbst zerfließt zu einem kollektiven Wir
- **Medikamentöse Euphorie** — Rausch als Befreiung und Käfig zugleich
- **Verordnete vs. echte Gefühle** — kein Weg, Chemie von Empfindung zu trennen
- **Dokumentarische Kühle** — Beobachtung ohne Urteil, Feier und Hohlheit im selben Bild
- **Dunkle Komik** — das Sardonische des Ausgeliefertseins

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

- **Beats**: Fragmentierter, nächtlicher Trip Hop — verschleppt, körperlos, mit Lücken (Burial-/FKA-twigs-Schule). Kein Vier-zu-Boden-Club; eher zerbrochene Breaks, die wie aus der Ferne kommen.
- **Bass**: **Sub-Herzschlag** — tiefer, langsamer, fast körperlicher Sub-Bass, der wie ein gemeinsamer Puls wummert. Wenig Bewegung, maximale Schwere. Das „eine Wir" als hörbarer Herzschlag des kollektiven Körpers.
- **Texturen**: Sakral-dunkle Schicht (von Hausswolff / Chelsea Wolfe) — Orgel-Drones, gotischer Hall, Klinik-Raumklang. Vinyl-/Tonband-Knistern, ferne Stations-Geräusche (Medikamentenwagen, Neonlicht-Brummen).
- **Vocals**: Ein klar gesungenes, sehnsüchtiges **„Wir"** — die menschliche Konstante über dem benebelten Bass. Geschichtete/übereinandergelegte Stimmen, die zu einer verschmelzen (viele werden eins). Deutsch.
- **Sprache**: Deutsch durchgehend.
- **Mood**: Benebelte Euphorie mit Riss — dokumentarisch kühl, sardonisch, hypnotisch. Würdevoll trotz Verfall.

**Referenz-Anker**: Burial, FKA twigs, Anna von Hausswolff, Chelsea Wolfe; Bass-Schwere von Massive Attack (Mezzanine).

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
