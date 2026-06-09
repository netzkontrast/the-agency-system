---
title: "Umschalten"
release_date: ""  # YYYY-MM-DD (fill in when releasing)
genres: ["dystopian-future-synth"]
tags: ["ep", "agency-system", "did", "arousal-states", "switching-arc", "german", "integration"]
explicit: false
streaming:
  soundcloud: ""    # Fill in when released
  spotify: ""       # Fill in when released
  apple_music: ""   # Fill in when released
  youtube_music: "" # Fill in when released
  amazon_music: ""  # Fill in when released
sheet_music:
  songbook: ""
---

# Umschalten

## Album Details

<!-- NOTE: When releasing, set Status: Released and fill in release_date in frontmatter. Albums stay in place. -->

| Attribute | Detail |
|-----------|--------|
| **Artist** | [the-agency-system](../../../README.md) |
| **Album** | Umschalten (EP) |
| **Genre** | [Dystopian Future Synth](/genres/dystopian-future-synth/README.md) |
| **Tracks** | 5 (concept EP — one switching-arc through arousal states S0→S4) |
| **Status** | In Progress — all 5 tracks lyrics + Style Box drafted |
| **Explicit** | No |
| **Concept** | A switching-arc through the arousal states S0→S4 — the lived experience of involuntary switching between parts, earning toward integration |

## Concept

*Umschalten* ("switching over") is a five-track concept EP that walks one continuous arc through the arousal-state axis S0→S4 — the lived experience of involuntary switching between parts of a DID system, earning its way toward integration rather than being granted it.

It opens at S0 (Homöostase) inside a maintained surface-normal facade, drops into S1 (Latenz/Freeze) where the system stalls and watches itself from behind glass, spikes at S2 (Alert/Konflikt) as an intrusion fires every warning system and two parts collide over how to answer it, tips past holding into S3 (Kollaps-Peak) where one voice carries the unbearable so nothing else ruptures, and finally arrives at S4 (Repair/Integration) — not a smooth fusion but a seam filled with gold, every voice still audible inside the whole.

The recurring refrain **"Wer atmet, wenn ich schlafe?"** threads all five tracks. It is filed-and-not-opened at S0, muffled and trailing off at S1, spat as a challenge at S2, and answered by no one — a flatline — at S3. At S4 the closing we-voice finally answers it in the plural: **"wir atmen."** The question that haunted a single "Ich" across the EP is resolved only when there is a "Wir" to answer it.

## Structure

Five movements on one unbroken state-arc. The EP is built around two shared motifs that bind the tracks into a single switching-experience: the breath motif (a counted "ein, aus" that becomes the question "Wer atmet, wenn ich schlafe?", distorts to a flatline at S3, and returns as a shared choral breath at S4) and the relay-click / modular-pulse rhythm (clinical at S0, slowed and submerged at S1, weaponized as an alarm at S2, broken down into a sine flatline at S3, warm and steady at S4).

| State | Track | Switching-experience |
|---|---|---|
| S0 Homöostase | Tagschicht | maintained surface-normal facade; the question filed, not opened |
| S1 Latenz/Freeze | Unter Glas | the system stalls, watches itself from behind glass; first crack in the surface |
| S2 Alert/Konflikt | Alarmstufe | intrusion fires every alarm; two parts collide over how to answer |
| S3 Kollaps-Peak | Nulllinie | overload tips past holding; the unbearable carried until the breath flatlines |
| S4 Repair/Integration | Naht aus Gold | seams filled with gold; each voice audible inside the Wir; "wir atmen" |

## Voice Architecture

All voices are referenced by **function/role only** — never by personal name (the `name_exposure` rule for music outputs). Each track is led by the function-voice(s) whose part the active arousal-state recruits:

| State | Lead function(s) | Vocal descriptor (Suno) |
|---|---|---|
| S0 | host + rationalist (the two ANP voices) | weary mid-baritone (dry close-mic, flat affect) trading with a cold clear tenor (sibilant precision, no vibrato) |
| S1 | child_freeze + collapsed | fragile child-like breathy head-voice near-whisper, and a very deep gravelly near-spoken sub-bass |
| S2 | fighter + protector | female belt-alto with growl, clipped staccato, against a low male baritone barking three-word commands |
| S3 | collapsed | androgynous very-deep near-spoken lead, gravelly, breath-heavy, cracking under saturation |
| S4 | integrator + Wir-Stimme | lead mezzo-alto opening the room, blooming into a layered choral we-voice in warm close harmony |

Voices are kept distinct in Suno via descriptive Style-Box deskriptors and same-gender parenthesis discipline — never named in lyrics, metatags, or any public-facing field.

## Sonic Palette

- **Beats**: relay-click / modular-synth pulse and a counted-breath motif, transformed per state — clinical and even at S0, slowed and widely-spaced at S1, hammering four-on-the-floor at S2, distorting into a sine flatline at S3, warm and steady around 70 BPM at S4
- **Samples**: counted breath ("ein, aus") as the EP's structural spine; relay clicks as the switching-marker
- **Vocals**: function-keyed registers (see Voice Architecture) — ANP duo, child-freeze + collapsed, fighter-belt + protector-baritone, androgynous collapse-lead, integrator mezzo + choral we-voice
- **Mood**: cold dystopian-future-synth that travels from clinical dissociative calm, through submerged freeze and peak-arousal confrontation, into terminal collapse, and out the far side into earned, tender, kintsugi-gold integration

## Tracklist

| # | Title | State | Lead Function(s) | Status |
|---|-------|-------|------------------|--------|
| 01 | [Tagschicht](tracks/01-tagschicht.md) | S0 Homöostase | host + rationalist | In Progress |
| 02 | [Unter Glas](tracks/02-unter-glas.md) | S1 Latenz/Freeze | child_freeze + collapsed | In Progress |
| 03 | [Alarmstufe](tracks/03-alarmstufe.md) | S2 Alert/Konflikt | fighter + protector | In Progress |
| 04 | [Nulllinie](tracks/04-nulllinie.md) | S3 Kollaps-Peak | collapsed | In Progress |
| 05 | [Naht aus Gold](tracks/05-naht-aus-gold.md) | S4 Repair/Integration | integrator + Wir-Stimme | In Progress |

## Production Notes

<!-- SERVICE: suno -->
**Suno Settings**:
- **Target Duration**: 3:00–5:00 per track
- Per-track Style Box, Exclude Styles, and Lyrics Box noted in individual track files
- Vocal consistency: function-keyed registers held distinct via Style-Box deskriptors + same-gender parenthesis discipline; voices never named in metatags
- Production continuity: shared breath motif + relay-click/modular-pulse rhythm transformed across the S0→S4 arc

**Style Prompt Base** (per-track variations override this):
```
dystopian future synth, cold modular-synth pulse, relay-click rhythm, counted-breath motif, German vocals, function-keyed vocal registers held distinct, claustrophobic forward-dystopia, no retro 80s coding
```
<!-- /SERVICE: suno -->

## Distributor Genres

| Attribute | Selection |
|-----------|-----------|
| **Primary Genre** | Electronic |
| **Secondary Genre** | Alternative |
| **Electronic Subgenre** | Electronica/Downtempo |

*Avoid surfacing "dystopian-future-synth" to distributors — not a recognized aggregator genre. Use established adjacent tags.*
