<!--
Imported from https://github.com/netzkontrast/agency/blob/867453e/skills/suno-lyric-writer/craft-reference.md
Source commit: 867453e
Edit upstream and re-import, or edit here and document the divergence.
-->

# Lyric Writer Craft Reference

Detailed tables and reference data for the lyric writer skill.

---

## Rhyme Techniques

### Rhyme Types (use variety)
| Type | Description | Example |
|------|-------------|---------|
| Perfect | Exact match | love/dove |
| Slant/Near | Similar but not exact | love/move |
| Consonance | Same ending consonants | blank/think |
| Assonance | Same vowel sounds | lake/fate |
| Internal | Rhymes within a line | "fire and desire higher" |

### Rhyme Scheme Patterns
| Pattern | Effect |
|---------|--------|
| AABB | Stable, immediate resolution |
| ABAB | Classic, delayed resolution |
| ABCB | Lighter, less pressure |
| AAAX | Strong setup, surprise ending |

### Rhyme Schemes by Genre

| Genre Family | Default Scheme | Strictness | Key Difference |
|---|---|---|---|
| **Hip-Hop / Rap** | AABB (couplet) | High — multisyllabic + internal mandatory | Rhyme density throughout the bar |
| **Pop** | XAXA (conversational) | Low — near rhymes preferred | If it sounds "crafted," it fails |
| **Rock** | XAXA or ABAB | Low — meaning > rhyme | Imagery and energy over technique |
| **Punk** | AABB (loose) | Low — half-rhymes authentic | Shoutable at 150+ BPM |
| **Metal / Industrial** | Optional | Very low | Concrete imagery, riff alignment |
| **Country / Folk** | ABCB (ballad stanza) | Moderate | Lines 2 & 4 rhyme, 1 & 3 free |
| **Electronic / EDM / Synthwave** | Repetition > rhyme | Minimal | Single phrases looped |
| **Darkwave / Goth / Post-Punk** | XAXA or free | Low | Atmospheric, moody — meaning first |
| **Ambient / Lo-Fi** | None | None | Vocals are texture |
| **Trip-Hop** | XAXA (loose) | Low | Abstract, moody |
| **R&B / Soul** | Flexible | Low — emotion first | Space for melisma |
| **Ballad (any)** | ABCB or ABAB | Moderate | Emotion serves the story |

### Rhyme Quality Standards (Universal)

- **Forced rhymes** never acceptable
- **No self-rhymes**
- **No lazy repeats** (mind/mind, time/time)
- **Meaning over rhyme** — near rhyme > unnatural perfect rhyme
- **Consistency** — maintain chosen scheme through each section

### Common Anti-Patterns

- ❌ Wrong scheme for genre
- ❌ Filler lines to set up quotes
- ❌ Clichés: "cold as ice," "broke my heart," "by my side," "set me free"
- ❌ Telling instead of showing
- ❌ Generic abstractions when specificity serves better

---

## Song Length

### Default Target: 3:30–5:00 minutes

### Duration → Word Count

| Target Duration | Non-Hip-Hop | Hip-Hop |
|-----------------|-------------|---------|
| 2:00–2:30 | 120–180 | 200–300 |
| 2:30–3:30 | 150–250 | 250–400 |
| 3:30–5:00 | 220–400 | 400–600 |
| 5:00–7:00 | 350–500 | 550–750 |

### Word Count Targets by Genre (Suno)

| Genre | Duration | Word Count | Structure |
|-------|----------|------------|-----------|
| Electronic / Synthwave / Darkwave | 3:30–5:00 | 220–300 | 3V + pre-chorus + chorus + bridge + break |
| Pop / Synth-Pop | 3:30–4:30 | 250–350 | 2–3V + pre-chorus + chorus + bridge |
| Rock / Alt-Rock / Post-Punk | 3:30–5:00 | 250–400 | 2–3V + chorus + bridge |
| Goth / Post-Punk | 3:30–5:00 | 200–300 | 2–3V + chorus + bridge + atmospheric break |
| Hip-Hop / Rap | 3:30–5:00 | 400–600 | 3V + hook + bridge |
| Folk / Country | 3:30–5:00 | 250–400 | 3V + chorus + bridge |
| Ballad (any) | 3:30–5:00 | 200–300 | 2–3V + chorus + bridge |
| Punk | 2:30–3:30 | 150–250 | 2V + chorus + bridge |

### Structure Defaults

- **Default**: 2–3 verses + chorus + bridge
- **Chorus**: 4–6 lines, repeated verbatim
- **Bridge**: 2–4 lines
- **Pre-chorus**: 2–4 lines
- **Instrumental breaks**: Add ~20–40 seconds runtime each

### How to Hit Duration Targets

**Add more sections, not longer sections.**
- Add a 3rd verse
- Add a pre-chorus before each chorus
- Add an instrumental break
- Do NOT write 10-line verses or 8-line choruses

---

## Section Length Limits by Genre

### Electronic / Synthwave / Darkwave / Goth / Industrial

| Section | Max Lines | Notes |
|---------|-----------|-------|
| Verse | 4–6 | Vocals sparse — less is more |
| Chorus / Hook | 2–4 | Often a repeated phrase |
| Bridge | 2–4 | |
| Drop / Break | 0 | Use `[Drop]` or `[Synth Solo]` tag |

### Pop / Synth-Pop

| Section | Max Lines |
|---------|-----------|
| Verse | 6–8 |
| Chorus | 4–6 |
| Bridge | 4 |
| Pre-Chorus | 2–4 |

### Rock / Alt-Rock / Post-Punk / Indie

| Section | Max Lines |
|---------|-----------|
| Verse | 6–8 |
| Chorus | 4–6 |
| Bridge | 4 |

### Punk / Hardcore

| Section | Max Lines |
|---------|-----------|
| Verse | 4–6 |
| Chorus | 2–4 |
| Bridge | 2–4 |

### Metal / Industrial / Doom

| Section | Max Lines |
|---------|-----------|
| Verse | 4–8 |
| Chorus | 4–6 |
| Breakdown | 2–4 |

### Hip-Hop / Rap

| Section | Max Lines |
|---------|-----------|
| Verse | 8 |
| Hook | 4–6 |
| Bridge | 4–6 |

### Folk / Country / Singer-Songwriter

| Section | Max Lines |
|---------|-----------|
| Verse | 4–8 |
| Chorus | 4–6 |
| Bridge | 2–4 |

### Ambient / Trip-Hop / Lo-Fi

| Section | Max Lines |
|---------|-----------|
| Verse | 2–4 |
| Chorus | 2–4 |
| Bridge | 2 |

### Enforcement Rules

1. Count lines per section. Compare against table.
2. Exceeds max → trim. Cut weakest lines, keep hook and opening.
3. Any chorus over 6 lines → trim.
4. Electronic verse over 6 lines → cut.
5. Long sections cause Suno to rush, compress, or skip.

---

## Lyric Density & Pacing (Suno)

### Suno Verse Length Defaults

| Genre Family | Default Lines | Max Safe | Topics/Verse |
|---|---|---|---|
| Hip-Hop / Rap | 8 | 8 | 2-3 |
| Pop | 4 | 6-8 | 1-2 |
| Rock | 6 | 8 | 2 |
| Punk | 4 | 4 | 1 |
| Metal | 6-8 | 10 | 2-3 |
| Doom Metal | 4 | 6 | 1 |
| Electronic / Synthwave / Darkwave | 2-4 | 4 | 1 |
| Ambient | 0-2 | 4 | 1 |
| R&B / Soul | 6 | 8 | 1-2 |
| Singer-Songwriter | 6-8 | 8 | 2-3 |
| Progressive | 8-10 | 12 | 3-4 |

### BPM-Aware Limits (Universal Fallback)

| BPM Range | Max Lines/Verse | Topics | Feel |
|-----------|----------------|--------|------|
| < 80 | 4 | 1-2 | Slow, heavy |
| 80-94 | 4-6 | 1-2 | Laid back |
| 94-110 | 6 | 2-3 | Energetic |
| 110-140 | 6-8 | 2-3 | Standard |
| 140+ | 4 | 1 | Fast — short |

### Red Flags

- 8-line verse at BPM under 100
- Verse reads like a Wikipedia list
- "Laid back" concept with wall-to-wall syllables
- 3+ proper nouns in a single verse
- Every verse dense with no breathing room

---

## Line Length by Genre

| Genre | Syllables/Line | Tolerance |
|-------|----------------|-----------|
| Pop/Folk/Punk | 6-8 | ±2 |
| Rock/Indie/Goth | 8-10 | ±2 |
| Hip-Hop/Rap | 10-13+ | ±3 |
| Metal/Electronic | Varies | Flexible |

**Critical**: V1 line lengths must match V2 line lengths (±2 syllables).

---

## Refinement Pass Reference

### Pass 1: Tighten

| Pattern | Before | After | Why |
|---------|--------|-------|-----|
| Filler phrases | "He stood up and spoke the words" | "He said" | Padding |
| Redundant modifiers | "completely destroyed" | "destroyed" | Absolutes need no intensifiers |
| Passive voice | "The door was opened by her" | "She opened the door" | Active = singable |
| Double-saying | "alone and by myself" | "alone" | One expression per idea |
| Throat-clearing | "Well, I think that maybe" | Direct statement | Cut hedging |

### Pass 2: Strengthen

| Pattern | Before | After | Why |
|---------|--------|-------|-----|
| Generic imagery | "The city at night" | "Neon bleeding on wet asphalt" | Specific sticks |
| Abstract emotion | "I felt so lost" | "Couldn't find my keys, my name, my street" | Concrete |
| Clichés | "Cold as ice" | "Cold as a landlord's smile" | Fresh comparisons |
| Single-sense | "The room was dark" | "Dark — just the hum of pipes and mildew air" | Multi-sensory |
| Weak verbs | "He went across" | "He cut across" | Strong verbs |

### Pass 3: Flow & Ear

| Pattern | Before | After | Why |
|---------|--------|-------|-----|
| Consonant clusters | "Sixth street's strict structures" | "Sixth Street's sharp edges" | Tongue-trippers |
| Missing breath points | 12 syllables, no pause | Split at caesura | Singers need air |
| Stress misalignment | "into the DARK-ness" on weak beat | "the DARKness CALLS" on strong | Downbeat stress |
| Syllable mismatch | V1: 8, V2: 13 | Match within ±2 | Same melodic phrase |
