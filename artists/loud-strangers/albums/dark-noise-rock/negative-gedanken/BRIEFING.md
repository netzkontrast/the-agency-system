# BRIEFING — Loud Strangers · „Negative Gedanken"

**Stand:** 2026-05-20, Ende Session 1 (Brainstorming + Spec + Audit)
**Branch:** `claude/loud-strangers-album-ZY1Bv`
**Artist-Folder:** `artists/loud-strangers/albums/dark-noise-rock/negative-gedanken/`

> Dieses Dokument ist die **Übergabe-Notiz für die nächste Session**. Wenn du
> hier landest, lies dieses File ZUERST komplett und folge dann der Sektion
> „Nächste konkrete Aktionen". Mit `SESSION-START-PROMPT.md` im gleichen
> Ordner kannst du eine neue Session in genau diesem Zustand starten.

---

## 1. Was wurde in Session 1 entschieden?

### 1.1 Album-Identität
- **Artist:** Loud Strangers (NEUE Identität, teilt KEINE DNA mit
  `children-of-agatha` oder `the-agency-system`).
- **Album-Konzept:** Mini-Album mit 7 Tracks zum Erleben intrusiver negativer
  Stimmen, Panik, Dissoziation und Wiedersturz. Der Artistname IST der
  Antagonist — die lauten Stimmen im Kopf.
- **Working Slug:** `negative-gedanken`
- **Genre-Folder:** `dark-noise-rock`
- **Frame:** **fiktional / Konzept-Album** (KEIN Documentary-Frame, KEINE
  Source-Verifikations-Pflicht, `sources_verified = N/A` für alle Tracks ok).

### 1.2 Artistische Foundation (LOCKED, via AskUserQuestion)
| Dimension | Entscheidung |
|---|---|
| Identität | Konzept-Projekt ohne fixe Persona, variable Erzähler-Aspekte je Track |
| Sprache | track-für-track (Conceptualizer Phase 3.5 entscheidet pro Track) |
| Frame | fiktional / Konzept-Album |
| Narrativer Bogen | **vorsichtiger Funke** — Track 7 = leise Anerkennung (nicht Heilung, nicht Triumph), kombiniert mit Loop-Twist (siehe §1.4) |

### 1.3 Sonic Direction (LOCKED, vom User in Session 1 gebriefed)
- **Obergenre:** Post-Grunge × Dark Shoegaze × Industrial Ambient
  („Systemischer Kollaps")
- **Alle 7 Tracks haben spezifizierte Sound-Profiles** — siehe `GENRE-BRIEF.md`
  im gleichen Ordner.

### 1.4 Cross-Cutting Constraints
- **DNA-Isolation (Workflow-Guardrail):** Loud Strangers darf KEINE Voice DNA,
  Narrative oder Charaktere von `children-of-agatha` (atmospheric-dark-folk,
  dark-trip-hop) erben. Auch keine Themen aus `the-agency-system`
  (Dev-Projekt-Bleed).
- **Album = Endlosschleife:** Track 7 endet in präzisem Noise-Loop, der
  nahtlos in Track 1 überleitet. Track 1 darf keinen Cold-Open haben.
  Mastering + Distributor müssen Gapless-Playback erzwingen.

---

## 2. Pre-Conceptualizer-Audit (DONE in Session 1)

Auditiert: alle 7 overrides + `mastering-presets.yaml`.

**Ergebnis:** 0 BLOCKING, 3 CAUTION, 0 dev-project-bleed.

### 2.1 CAUTION Findings — Wichtig fürs Conceptualizer-Briefing
- `lyric-writing-guide.md` postuliert Multi-Voice/Plurality als Default
  → **NICHT auf Loud Strangers anwenden.**
- `voice-craft-principles.md` rahmt Plurality, Witness-Layer, Ensemble-Polyphony
  als Cross-Projekt-Default → **für Loud Strangers ignorieren.**
- `suno-preferences.md` enthält alter-coded Vocal-Register-Tabelle
  (Override / control, Collapsed / submit, etc.) → **für Loud Strangers ignorieren.**

### 2.2 Mastering-Presets — Gap zu schließen
- **Vorhanden:** `dark-ambient` (passt für Track 4)
- **FEHLEN:** `post-grunge`, `noise-rock`, `doomgaze`, `sludge`, `dream-pop`,
  `shoegaze`, `industrial-rock`, `post-punk`, `post-rock`
- **Vorgehen:** mastering-engineer-Phase legt diese **albumspezifisch** ab
  (im Album-Ordner), NICHT in `overrides/` (per CLAUDE.md MANDATORY).

---

## 3. Datei-Inventar in diesem Album-Ordner

| File | Zweck | Status |
|---|---|---|
| `WORKFLOW-PLAN.md` | Kompletter 9-Phasen-Workflow-Plan (Kopie des superpowers-Specs) | Final für Session 1 |
| `SOURCE-TEXT.md` | Der „Negative Gedanken"-Basistext (4 Teile, 5.11.2021) | Final |
| `GENRE-BRIEF.md` | Sonic-Direction + Per-Track Sound-Profile | Final |
| `BRIEFING.md` | Diese Datei | Final für Session 1 |
| `SESSION-START-PROMPT.md` | Copy-Paste-fertiger Prompt für nächste Session | Final |

**Spec-Quelle:** `docs/superpowers/specs/2026-05-20-loud-strangers-negative-gedanken-design.md`
(Original — identisch zum hier liegenden `WORKFLOW-PLAN.md`).

**Was NICHT existiert (kommt in Session 2 via bitwize MCP):**
- `README.md` (Album-Master, wird von `new-album` + `album-conceptualizer` befüllt)
- `cast.md` (Erzähler-Aspekte, wird von `album-conceptualizer` Phase 3.3 befüllt)
- `art-direction.md` (wird von `album-art-director` befüllt)
- `tracks/` (7 Track-Files, werden von `new-album` + lyric-writer befüllt)

---

## 4. Warum wurde MCP in Session 1 umgangen?

Der bitwize-music MCP-Server war im Session-State „still connecting" und
wurde nicht in den Tool-Catalog der laufenden Session aufgenommen.
`claude mcp list` meldete `Connected`, aber `ToolSearch` fand keine Tools.

Konsequenz: `/bitwize-music:album-ideas` und `/bitwize-music:new-album`
waren NICHT korrekt ausführbar in Session 1.

**Entscheidung des Users (siehe Konversations-Log):**
„Commit alles… und schreibe ein ausführliches Briefing… und einen Session
Start prompt für mich - damit wir nahtlos weitermachen können… lege den
ordner schon mal an… manuell.. und speichere alles darin… umgehe dafür
mcp erst mal"

→ Ein **einmaliger** Bruch der „Skills before MCP"-Regel war autorisiert.
In Session 2 zurück zur MCP-Pflicht.

---

## 5. Nächste konkrete Aktionen (Session 2)

### 5.1 Pre-Flight Checks
1. **MCP-Health verifizieren** — diesmal MUSS bitwize MCP angedockt sein:
   - `claude mcp list` → bitwize-music-mcp = ✓ Connected
   - `ToolSearch` query `select:mcp__plugin_bitwize-music_bitwize-music-mcp__health_check`
     muss das Tool zurückgeben
   - Falls nicht: `/bitwize-music:setup` laufen lassen, dann Session neu starten

2. **Spec lesen:** `WORKFLOW-PLAN.md` in diesem Ordner

### 5.2 Phase 1 — Idee registrieren
```
/bitwize-music:album-ideas
```
- Mode: add
- Title: `negative-gedanken` (oder finaler Titel falls schon entschieden)
- Genre: rock (primary category — dark-noise-rock ist Sub-Genre)
- Type: Thematic
- Concept: 7-Track Mini-Album zur psychischen Erfahrung von intrusiven
  negativen Stimmen, Panik, Dissoziation und Wiedersturz. Endlosschleife durch
  Track-7-zu-Track-1-Noise-Loop. Inspiration: 4-teiliger Basistext vom 5.11.2021.
- Status: pending (wird in Phase 2 zu in-progress)

### 5.3 Phase 2 — Album-Struktur via bitwize
```
/bitwize-music:new-album loud-strangers dark-noise-rock negative-gedanken
```

**Collision-Risk:** Der Album-Ordner existiert bereits (Session 1 hat ihn
mit unseren auxiliary docs angelegt). new-album könnte:
- **Skip / Fail** mit „folder exists" → in diesem Fall die existierenden
  files lassen, README.md / cast.md / tracks/ manuell aus Templates initialisieren
- **Append** zur existierenden Struktur → wahrscheinlich der Fall, dann
  einfach weiter

→ Prüfen, wie sich new-album verhält. Auxiliary docs (WORKFLOW-PLAN.md,
SOURCE-TEXT.md, GENRE-BRIEF.md, BRIEFING.md, SESSION-START-PROMPT.md) NICHT
verlieren.

### 5.4 Phase 3 — Album-Conceptualizer mit explizitem Briefing
```
/bitwize-music:album-conceptualizer
```

**WICHTIG — Briefing vor Start an die Skill übergeben:**

> Loud Strangers ist ein Single-Voice Noise-Rock-Projekt. Teilt KEINE DNA mit
> children-of-agatha. Wende KEINE multi-voice / plurality / alter-Defaults aus
> overrides/lyric-writing-guide.md, overrides/voice-craft-principles.md oder
> overrides/suno-preferences.md an. Mehrstimmigkeit kann tracks-weise eingesetzt
> werden wenn der Track es verlangt, aber niemals als Default-Strategie.
>
> Sonic-Direction ist BEREITS gebrieft via GENRE-BRIEF.md im Album-Ordner —
> Phase 3.2 nur zur Bestätigung durchgehen.
>
> Track 1 und Track 7 müssen als PAAR geplant werden wegen Noise-Loop-
> Constraint (Track 7 Outro → Track 1 Intro nahtlos).

**Was der Conceptualizer in 7 Sub-Phasen entscheidet:**
- 3.1 Subject Matter (was JENSEITS „Depression"?)
- 3.2 Sonic Direction (vorausgefüllt aus GENRE-BRIEF.md, bestätigen)
- 3.3 Voice / Narrator Identity (Erzähler-Aspekte für variables Konzept)
- 3.4 Tracklist Architecture (7 Titel)
- 3.5 Per-Track Concepts (lyric + sprache + voice — Sound steht schon)
- 3.6 Visual Direction (Art-Brief)
- 3.7 Confirmation Gate (HARD GATE — explizite User-Bestätigung)

### 5.5 Mein Vorschlag aus Session 1 für Tracklist-Architektur

Conceptualizer-Phase 3.4 kann dies als Ausgangspunkt nehmen:

| # | Sound (locked) | Vorgeschlagener inhaltlicher Anker |
|---|---|---|
| 1 | Deceptive Soft-Grunge | Intro / die Stille vor den Stimmen |
| 2 | Classic 90s Grunge / Noise-Rock | Titeltrack „Loud Strangers" — die Übernahme (Teil 1 des Basistexts) |
| 3 | Heavy Doomgaze / Sludge | Schwarzes Meer / Kein Atem (Teil 2) |
| 4 | Dark Ambient / Spoken Word | Wahres Gesicht / Albtraum (Teil 3) |
| 5 | Melancholic Dream-Pop / Shoegaze | Bridge — Lichtstelle / Erinnerung |
| 6 | Driving Post-Punk / Industrial | Dauerschleife — die Erkenntnis ohne Kraft (Teil 4) |
| 7 | Epic Post-Rock / Noise-Loop | Coda — vorsichtiger Funke + Loop zurück zu Track 1 |

### 5.6 Sprachen-Vorschlag (Conceptualizer Phase 3.5 entscheidet)
- Tracks 2, 3, 4, 6: **Deutsch** (Treue zum Basistext, Intimität)
- Track 5 (Bridge): **Englisch** oder mixed (Distanz vom Quelltext, Reset)
- Track 7 (Coda): **Deutsch** mit englischem Anker-Phrase „loud strangers"
- Track 1 (Intro): vorsprachlich / gemurmelt / spoken word — Conceptualizer entscheidet

---

## 6. Phasen 4–8 (Übersicht — siehe WORKFLOW-PLAN.md für Details)

| Phase | Skill | Wann |
|---|---|---|
| 4 | `/bitwize-music:album-art-director` (Vorab-Skizze) | parallel zu Phase 5 |
| 5 | Track-Loop ×7: lyric-writer → pronunciation → lyric-reviewer → voice-checker → pre-generation-check → Suno | nach Conceptualizer-Confirmation |
| 6 | `/bitwize-music:import-audio` → `mix-engineer` → `mastering-engineer` (+ albumspezifische Genre-Presets!) | nach Suno-Generation aller 7 |
| 7 | art-director (final) → `validate-album` → `plagiarism-checker` → `explicit-checker` | nach Mastering |
| 8 | `/bitwize-music:release-director` (9-Domain-QA + Gapless-Flag) | nach Pre-Release-Checks |

---

## 7. Risiken zum Auge behalten

| Risk | Mitigation |
|---|---|
| `new-album` skill collidiert mit pre-existing Ordner | Auxiliary files NICHT verlieren; ggf. README/cast/tracks aus Templates manuell |
| Conceptualizer ignoriert das Briefing und fällt auf overrides-Defaults zurück | Bei Multi-Voice-Vorschlag des Skills → STOP, explizit korrigieren |
| Suno performt deutsche Lyrics schlechter als englische | pronunciation-specialist-Pass pro DE-Track, phonetische Spellings in Suno-Lyrics-Feld |
| Track 7 → Track 1 Crossfade misslingt | Track 1 + 7 in Phase 3.5 als Paar planen; Mix-Engineer + Mastering dokumentieren Spec; Gapless im Distributor |
| Streaming-Plattform handhabt Gapless inkonsistent | release-director prüft pro Plattform; Distributor-Metadata enthält explizite Gapless-Flag |

---

## 8. Definition of Done (Album-Level)

Album „Negative Gedanken" gilt als finalisiert wenn:

- [ ] Phase 1: IDEAS.md hat Entry, Status = in-progress nach Phase 2
- [ ] Phase 2: bitwize hat `new-album` ausgeführt, Ordnerstruktur konsistent
- [ ] Phase 3: alle 7 Sub-Phasen + Confirmation Gate passed
- [ ] Phase 4: `art-direction.md` mit Konzept-Skizze
- [ ] Phase 5: alle 7 Tracks Status = Final (Lyric-Loop + Suno + Import durch)
- [ ] Phase 6: Mastered Audio bei -14 LUFS / -1.0 dBTP, Crossfade T7→T1 dokumentiert,
      albumspezifische Genre-Presets im Album-Ordner gespeichert
- [ ] Phase 7: validate-album / plagiarism / explicit alle grün
- [ ] Phase 8: release-director-9-Domain-QA passed, Distributor-Upload mit
      Gapless-Flag, Streaming-URLs verifiziert

---

## 9. Konversations-Quellen für Vollständigkeit

Diese Entscheidungen wurden in Session 1 explizit via AskUserQuestion abgefragt
und vom User bestätigt:

1. **Artist-Identität** → Konzept-Projekt ohne fixe Persona
2. **Sprache** → track-für-track
3. **Frame** → fiktional / Konzept-Album
4. **Narrativer Bogen** → vorsichtiger Funke
5. **Phase 1 Start** → IDEAS.md first
6. **Working Title** → `negative-gedanken`
7. **Genre-Folder** → `dark-noise-rock`
8. **DNA-Guard** → README + Pre-Conceptualizer-Audit + Exclude agency-system
9. **Conceptualizer-Mode** → voll interaktiv mit Vor-Brief
10. **Spec-Workflow** → Phase 1+2 abwarten, dann alles zusammen committen

Plus zwei direkte User-Briefings:
- Genre-Konzeption „Systemischer Kollaps" (kopiert in GENRE-BRIEF.md)
- Basistext „Negative Gedanken" (kopiert in SOURCE-TEXT.md)
- DNA-Trennung: „Das Projekt teilt keine dna mit den anderen Künstlern"
- MCP-Bypass-Autorisation für Session 1 only
