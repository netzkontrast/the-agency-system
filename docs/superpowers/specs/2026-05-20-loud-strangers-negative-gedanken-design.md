# Loud Strangers — „Negative Gedanken" Mini-Album Workflow

**Type:** Music album production workflow plan (nicht Software-Spec)
**Date:** 2026-05-20
**Branch:** `claude/loud-strangers-album-ZY1Bv`
**Status:** Draft for user review
**Artist:** Loud Strangers (Konzept-Projekt ohne fixe Persona)
**Working Slug:** `negative-gedanken`
**Genre-Folder:** `dark-noise-rock`
**Path:** `artists/loud-strangers/albums/dark-noise-rock/negative-gedanken/`

---

## 1. Album Overview

Mini-Album mit 7 Tracks, das die psychische Erfahrung von intrusiven negativen
Stimmen, Panik, Dissoziation und Wiedersturz vertont. Der Artistname „Loud
Strangers" verkörpert die Antagonisten — die fremden, lauten Stimmen im Kopf
der Erzählerin. Das Album ist als Endlosschleife konstruiert: Track 7 mündet
per Noise-Loop nahtlos in Track 1. Form spiegelt These — die Krankheit IST
der Kreislauf.

Frame: **fiktional / Konzept-Album** (keine Source-Verifikation nötig). Basistext
(4 datierte Textteile vom 5. November 2021) dient als Inspirationsquelle, nicht
als Verifikations-Quellmaterial.

## 2. Source Material

- **Basistext „Negative Gedanken":** 4 Teile, alle datiert Freitag 5. November 2021.
  Inhalt wird vom User in Conceptualizer-Phasen direkt zugeführt — nicht ins
  Repo verschoben (kein RESEARCH.md, kein SOURCES.md — fiktionaler Frame).
- **Genre-Konzeption „Systemischer Kollaps":** Vom User bereitgestellter
  Sonic-Brief. Post-Grunge × Dark Shoegaze × Industrial Ambient. Alle 7 Tracks
  haben spezifizierte sonic profiles (siehe Konversations-Transkript).

## 3. Locked Foundation

| Dimension | Wert | Quelle |
|---|---|---|
| Artist | Loud Strangers | User |
| Identität | Konzept-Projekt ohne fixe Persona, variable Erzähler-Aspekte | AskUser #1 |
| Sprache | track-für-track (Conceptualizer Phase 3.5) | AskUser #1 |
| Frame | fiktional / Konzept | AskUser #1 |
| Narrativer Bogen | vorsichtiger Funke (Track 7 = leise Anerkennung, nicht Triumph) | AskUser #1 |
| Sonic Direction | Post-Grunge × Dark Shoegaze × Industrial Ambient | User Brief |
| Per-Track Sonics | alle 7 spezifiziert | User Brief |
| Working Slug | `negative-gedanken` | AskUser #2 |
| Genre-Folder | `dark-noise-rock` | AskUser #3 |
| Phase 1 Pfad | `album-ideas` zuerst, dann `new-album` | AskUser #2 |
| DNA-Guard | README-Note + Pre-Conceptualizer-Audit + Exclude agency-system overrides | AskUser #3 |

## 4. Cross-Cutting Structural Constraints

### 4.1 DNA-Isolation
Loud Strangers teilt **keine DNA** mit anderen Artists im Repo:
- `children-of-agatha` (atmospheric-dark-folk, dark-trip-hop) → null Übernahme
- `the-agency-system` (Dev-Projekt-Bleed) → null Übernahme

Operationalisiert als:
- README-Note im Album: „No DNA inheritance from other artists. No agency-system overrides."
- Pre-Conceptualizer-Audit (Phase 2.5, siehe §5): aktive Overrides + Verzeichnisse auf children-of-agatha- und agency-system-Bleed prüfen, jeden Fund flaggen, vor Conceptualizer-Lauf klären

### 4.2 Album = Endlosschleife
Track 7 endet in präzisem Noise-Loop, der nahtlos in Track 1 mündet.
Workflow-Konsequenzen:
- **Track 1 + 7 als Paar planen** (Conceptualizer Phase 3.5)
- **Suno-Engineer:** abgestimmte Style-Box (gemeinsamer Noise-Layer)
- **Lyric-Writer:** Track 1 darf kein Cold-Open
- **Mix-Engineer:** Outro/Intro-Crossfade gemeinsam designen
- **Mastering-Engineer:** Crossfade-Spec dokumentieren
- **Release-Director / Distributor:** Gapless-Playback erzwingen

## 5. Workflow Phases

### Phase 1 — Idee registrieren (5 min)
- **Skill:** `/bitwize-music:album-ideas`
- **Action:** Eintrag in `IDEAS.md` mit Foundation-Zusammenfassung, Status=Promoted
- **Output:** IDEAS.md (neu, falls nicht existent)

### Phase 2 — Album-Struktur (5 min)
- **Skill:** `/bitwize-music:new-album`
- **Args:** artist=`loud-strangers`, genre=`dark-noise-rock`, slug=`negative-gedanken`
- **Output:** `artists/loud-strangers/albums/dark-noise-rock/negative-gedanken/`
  mit Skeleton-Dateien
- **Post-Action (User-Request 2026-05-20):** Diese Spec in den Album-Ordner
  kopieren als `WORKFLOW-PLAN.md` (Local-Reference im Album, Original bleibt
  in `docs/superpowers/specs/`)

### Phase 2.5 — Pre-Conceptualizer-Audit ✅ DONE (2026-05-20)
**Auditiert:** alle 7 overrides + mastering-presets.yaml
**Ergebnis:** 0 BLOCKING, 3 CAUTION, 0 dev-project-bleed

**Findings:**
- **Other-artist bleed (CAUTION):**
  - `lyric-writing-guide.md` — Multi-voice Tradition als Default → relativieren
  - `voice-craft-principles.md` — Plurality/Witness-Layer als Cross-Projekt → ignorieren für Loud Strangers
  - `suno-preferences.md` — alter-coded Vocal-Register-Tabelle → ignorieren für Loud Strangers
- **Mastering-Presets:** nur `dark-ambient` vorhanden; FEHLEN: `post-grunge`,
  `doomgaze`, `shoegaze`, `industrial-rock`, `dream-pop`, `noise-rock`, `post-rock`

**Konsequenzen für nachfolgende Phasen:**
- **Phase 3 Conceptualizer-Briefing** muss explizit enthalten:
  „Loud Strangers ist ein Single-Voice Noise-Rock-Projekt. Teilt KEINE DNA mit
  children-of-agatha. Alter-coded Vocal-Register aus suno-preferences ignorieren.
  Multi-Voice-Default aus lyric-writing-guide/voice-craft-principles NICHT auf
  dieses Album anwenden — wir können tracks-weise Mehrstimmigkeit nutzen, aber
  nur wenn der Track-Charakter es verlangt, nicht als Default."
- **Phase 6 Mastering** muss albumspezifische Presets erstellen (NICHT overrides/)
  für: post-grunge, doomgaze, shoegaze, industrial-rock, dream-pop, noise-rock,
  post-rock. Closest existing analogs als Startpunkt: `dark-electro-rock`,
  `gothic-rock`, `alternative-rock` (-12 bis -13 LUFS), `dark-ambient`/`drone`.

### Phase 3 — Album-Conceptualizer (HARD GATE, 30–45 min)
- **Skill:** `/bitwize-music:album-conceptualizer`
- **Mode:** voll interaktiv, mit Vor-Brief
- **7 Sub-Phasen:**
  - **3.1 Subject Matter** — Thematik präzisieren (was JENSEITS „Depression"?)
  - **3.2 Sonic Direction** — vorausgefüllt aus User-Brief, zur Bestätigung
  - **3.3 Voice / Narrator Identity** — Erzähler-Aspekte für Konzept-Projekt definieren
  - **3.4 Tracklist Architecture** — 7 Titel + Reihenfolge
  - **3.5 Per-Track Concepts** — Lyrik-Konzept + Sprache + Voice pro Track
    (Sonic vorausgefüllt). **Track 1 + 7 als Paar planen wegen Loop-Constraint.**
  - **3.6 Visual Direction** — Art-Brief
  - **3.7 Confirmation Gate** — explizite User-Bestätigung aller Sub-Phasen
- **Output:**
  - `<album>/README.md` (Album-Concept-Master)
  - `<album>/cast.md` (Erzähler-Aspekte)
  - 7 Track-Skeletons (`tracks/01-*.md` bis `tracks/07-*.md`)

### Phase 4 — Art-Direction Vorab-Skizze (parallel zu Phase 6, 30 min)
- **Skill:** `/bitwize-music:album-art-director`
- **Mode:** Konzept-Vorschau, kein Final-Artwork
- **Output:** `<album>/art-direction.md` mit Bildkonzept + AI-Prompts

### Phase 5 — Track Production Loop (×7) — Hauptarbeit
**Pro Track in dieser Reihenfolge:**

```
lyric-writer
  → pronunciation-specialist  (besonders bei DE-Tracks)
  → lyric-reviewer            (14-Punkt-QC, auto-phonetic-fix)
  → voice-checker             (AI-Pattern-Scan, advisory)
  → pre-generation-check      (6 BLOCKING gates)
  → Suno-Generation extern
  → import-audio + import-track
```

**Reminder-Pflicht (per CLAUDE.md):** Nach jedem Skill den nächsten optionalen
Schritt benennen mit „Next step (optional)"-Hinweis.

**Track-Status-Flow:** Not Started → In Progress → Generated → Final

**Sprache pro Track:** in Phase 3.5 festgelegt. Pronunciation-specialist
besonders wichtig bei deutschen Tracks (Suno-DE-Performance).

### Phase 6 — Audio-Polish-Kette (nach allen 7 Tracks „Generated")
```
import-audio
  → mix-engineer       (Stem-Politur)
  → mastering-engineer (-14 LUFS, -1.0 dBTP, +Crossfade-Spec T7→T1)
```

### Phase 7 — Album-Art Final + Pre-Release-Checks
```
album-art-director (final, ≥3000×3000)
  → import-art
  → validate-album
  → plagiarism-checker
  → explicit-checker
  → check_streaming_lyrics MCP
```

### Phase 8 — Release
- **Skill:** `/bitwize-music:release-director`
- **9-Domain-QA-Gate** (binding wenn invoked)
- **Special:** Gapless-Playback im Distributor-Metadata erzwingen
- **Skill:** `update_streaming_url` + `verify_streaming_urls` nach Veröffentlichung

## 6. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Bleed von children-of-agatha Voice DNA | Phase 2.5 Pre-Conceptualizer-Audit ✅ done; 3 CAUTIONS dokumentiert |
| Bleed von agency-system-Themen in Overrides | Phase 2.5 Audit ✅ done; 0 Findings |
| Multi-Voice-Override-Prior bleed in Conceptualizer | Explizites Conceptualizer-Briefing (siehe Phase 3) |
| Mastering-Presets für 7 Tracks fehlen | Phase 6 erstellt albumspezifische Presets |
| Suno performt Deutsch schwächer als Englisch | Pronunciation-specialist-Pass pro DE-Track, ggf. phonetische Spelling in Suno-Lyrics |
| Track 7 → Track 1 Crossfade misslingt | Track 1 + 7 als Paar in Phase 3.5 planen, Mastering-Engineer dokumentiert Spec |
| Streaming-Plattformen handhaben Gapless unterschiedlich | Release-Director prüft pro Plattform, Distributor-Metadata enthält Hinweis |
| Lyric-Reviewer auto-applies phonetic fixes die Bedeutung verschieben | User reviewt Lyric-Reviewer-Output vor Suno-Generation (kein blindes Durchwinken) |
| AI-Pattern-Drift bei deutschsprachiger Vertonung schwerer Themen | Voice-checker advisory, User entscheidet pro Flag |
| Pre-Generation-Check blockt wegen `sources_verified` | Fiktionaler Frame → `sources_verified = N/A` in Track-Frontmatter setzen |

## 7. Open Questions for Conceptualizer (Phase 3)

Diese Punkte sind **bewusst offen gelassen** und werden vom Conceptualizer
interaktiv mit dem User gelöst:

- **3.1:** Was sagt das Album JENSEITS „Depression"? (z.B. „die Sprache, die
  Krankheit uns aufzwingt", „der Unterschied zwischen Beobachter und Subjekt",
  „die soziale Komparsen-Rolle")
- **3.3:** Welche Erzähler-Aspekte? Vorschlag (Brainstorm): „die Hülle",
  „die Stimmen selbst (Chor)", „der Beobachter", „das verlorene Ich",
  „die Frohnatur (Memoria)" — Conceptualizer entscheidet
- **3.4:** 7 Track-Titel. Mein Mapping-Vorschlag aus Konversation als
  Ausgangspunkt: 1=Intro/Anker, 2=Titeltrack („Loud Strangers"), 3=schwarzes
  Meer, 4=wahres Gesicht/Albtraum, 5=Bridge/Lichtstelle, 6=Dauerschleife,
  7=Coda/Funke+Noise-Loop
- **3.5:** Sprache pro Track. Vorschlag: DE-Kerntext-Tracks (2,3,4,6), EN
  für Bridge (5), DE für Coda (7) mit EN-Phrase „loud strangers" als Anker.
  Intro (1) sprachlos oder gemurmelt — Conceptualizer entscheidet
- **3.6:** Visual — sonic-Stichworte (Static, Wall-of-Sound, schwarzes Meer,
  Vakuum) als Eingaben für art-director

## 8. Definition of Done

Album gilt als finalisiert wenn:
- [ ] Phase 1 (album-ideas) eingetragen
- [ ] Phase 2 (new-album) Struktur vorhanden
- [ ] Phase 2.5 Audit gelaufen, alle Bleed-Findings geklärt
- [ ] Phase 3 Conceptualizer 7-Phasen confirmation gate passiert (HARD GATE)
- [ ] Phase 4 Art-Direction-Skizze in `art-direction.md`
- [ ] Phase 5 alle 7 Tracks Status=Final (Suno-Generation + import erledigt)
- [ ] Phase 6 Mastered Audio ≥-14 LUFS, ≤-1.0 dBTP, Crossfade-Spec dokumentiert
- [ ] Phase 7 alle Pre-Release-Checks grün
- [ ] Phase 8 Release-Director-9-Domain-QA passiert, Distributor-Upload mit
  Gapless-Flag, streaming-URLs verifiziert

## 9. References

- Konversations-Transkript: Brainstorming-Phase mit AskUser-Antworten
- Basistext „Negative Gedanken" (User-Provided, im Transkript)
- Genre-Konzeption „Systemischer Kollaps" (User-Provided, im Transkript)
- Project CLAUDE.md: §„MANDATORY: Skills before MCP",
  §„MANDATORY: Overrides are cross-project — albums hold album content",
  §„RECOMMENDED: Follow the canonical workflow chains"
- bitwize-music plugin v0.91.0: skills/album-conceptualizer/SKILL.md,
  skills/help/SKILL.md
