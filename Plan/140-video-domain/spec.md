---
spec_id: 140
slug: video-domain
status: draft
owner: lead
depends_on: [004, 005]
affects:
  - skills/video/
  - servers/agency-mcp/src/agency_mcp/handlers/video/
  - templates/video/
  - Plan/decisions/
source-repos:
  - netzkontrast/take-one
  - netzkontrast/ClaudeAnimationBase
  - netzkontrast/higgsfield-video-engineer
estimated_jules_sessions: 0
domain: video
wave: C
spec_kind: research_epic
---

> **Noch kein Jules-Auftrag.** Dieser Spec ist ein Planungsdokument. Er wird erst in
> Jules-taugliche Teil-Specs (140a …) zerlegt, nachdem der Pilot (§9, Phase P0) gelaufen
> ist und die offenen Entscheidungen (§11) getroffen sind.

# Spec 140 — Video-Domain: Musikvideo-Pipeline pro Song (analog zu bitwize)

## Warum

Die Musik-Domain bringt einen Song von der Idee bis zum Release: eine feste Skill-Kette,
Gates an den Übergängen, Status-Felder in der Track-Datei, MCP-Tools als Setter. Für
Videos gibt es nichts Vergleichbares. Diese Lücke soll eine Video-Domain füllen, die
denselben Mustern folgt und auf drei bestehenden Repos aufsetzt.

Erstes Zielalbum: *Lass mich, lass mich atmen* — Konzept in
`artists/the-agency-system/albums/dystopian-future-synth/lass-mich-lass-mich-atmen/VIDEO-CONCEPT.md`.

## 1. Drei Repos, drei Schichten

**Stand 2026-11-07 — Video Studio:** Die drei Repos sind zu einer eigenen Suite
zusammengeführt und ersetzt: [`skills/video/studio/`](../../skills/video/studio/SKILL.md),
Skill `video-studio`. Sie enthält:
- **Pipeline** (Phasen 0–11 mit harten Gates)
- **12 Subagenten-Briefs** (`agents/`)
- **13 Playbooks** (`playbooks/`)
- **Einen Film-Vertrag für alle Medien** (`references/film-contract.md`)
- **Einen Renderer** (`tools/render.mjs`) und einen Browser-Starter (`tools/lib/browser.mjs`)
- **Song-Map für jedes Medium** (`engine/lib/beat.js`)
- **Audio-Werkzeuge:** Lyrics-Alignment (`tools/audio/align_lyrics.py`, stable-ts) und beat_this
- **Untertitel** (`tools/audio/srt.py`) und Blitz-Gate (`tools/flash_test.py`)
- **CLI** (`bin/studio`)

Herkunft und Lizenzen stehen in `skills/video/studio/THIRD_PARTY.md`. Die Rollen-, Gate- und
Skill-Namen in §4–§5 unten sind der ursprüngliche Plan. Die umgesetzte Fassung steht in
`SKILL.md` (Phasen) und `agents/` (Rollen). Pfade in diesem Spec, die mit einem Repo-Namen
beginnen, meinen jetzt die entsprechenden Ordner der Suite.

| Schicht | Repo | Was wir davon nehmen |
|---|---|---|
| **Prozess & Qualität** | `netzkontrast/take-one` | das Studio mit 12 Jobs; der Fall „Song → Musikvideo“ (`references/music-video.md`) mit Studio-Prozess für lange Filme (Director → Critic → Animatoren pro Kapitel → Integrator); Song-Map aus dem Vocal-Stem (demucs + whisper, Wort-Zeiten, betonte Silben, Tempo-Drift); frischer Reviewer pro Runde mit Bewertungsraster und 10-Sekunden-Karte (`reviewer-brief.md`, `quality-checklist.md`); Review-Raum mit Notizen an Frames (`review-room.md`); Prüfwerkzeuge (`gate.mjs`, `text-audit.mjs`, `plate-audit.mjs`, `audio-check.mjs`, `songmap.py`, `render-parallel.sh`); Stil-Referenzen *Ink wash*, *Sketchbook*, *Pencil test*, *Watercolor* |
| **Medium / Engine** | `netzkontrast/ClaudeAnimationBase` | p5.js + p5.brush: flaches 2D, Tusche, Kohle-Schraffur, Aquarell, kochende Linien, Papierkorn, `glow()`; reine Funktion der Zeit; `studio.html` zum Scrubben; `render.mjs` (Contact Sheets, Strips, Crops, paralleles fortsetzbares Rendern, Encode mit Audio); `ANIMATION_GUIDE.md` (Timing für den Zuschauer, Übergänge, Animationsprinzipien) |
| **Takt-Analyse, optional Standbilder** | `netzkontrast/higgsfield-video-engineer` | `tools/beatmap.py` (BPM, Downbeats, Abschnitte, Drop, Stopps, Hits als Frame-Tabelle); optional der Path-Tracer für fotorealistische Standbilder (Cover, Eckpfeiler-Bilder) |
| **Album-DNA & Zustand** | `the-agency-system` (dieses Repo) | Video-Domain: Skill-Kette, harte Gates, Felder in der Track-Datei, MCP-Handler. Der Gate-Skill `skills/theagencysystem/` übernimmt die Rolle, die Take One „The owner's taste“ nennt (`TASTE.md`). |

**Warum diese Engine:** Die Kosten pro Bild sind mit Path-Tracing für 3–5-Minuten-Songs zu
hoch (laut README 20–43 s pro Bild). Take One hat p5.brush in echten Produktionen
gemessen:
- „1080p24 etwa 1,5 s pro Frame mit 11 Workern auf einem 12-Kern-Mac; 98 s Film ≈ 1 h“
- „3–4-Minuten-Song ≈ 30–60 min Rendern auf einer GPU“

Hier im Cloud-Container ohne GPU waren es 26–32 s pro Bild (Software-WebGL). Die Ästhetik
(Tusche, Kohle, Papier, Zitterlinie) deckt sich direkt mit dem Visual-Language-Guide.

**Route:** nur Code. Take One bietet bezahlte Bild-/Video-Modelle (Higgsfield, Seedance,
Kling) als Option an. Für dieses Album entfällt das (Darstellungsregeln, §8). Suno ist die
einzige externe Quelle, und deren Audio kommt ohnehin aus der Musik-Kette.

## 2. Ablage auf der Platte

**Ein Kit pro Album**, alle Tracks darin. So teilen sich alle Videos Palette, Bibliothek
und Engine-Version.

```
artists/<artist>/albums/<genre>/<album>/
  VIDEO-CONCEPT.md                 # Album-Ebene: Look, Formate, harte Regeln (Gate)
  video/
    package.json                   # p5, p5.brush, puppeteer-core (gepinnt)
    film.html                      # aus skills/video/studio/engine/paint/ (tools/new-project.sh)
    (render: skills/video/studio/tools/render.mjs, nicht kopiert)
    engine/                        # core.js, timeline.js aus dem Kit (ohne clawd.js)
    shim/take-one.js               # renderFrame(t)/READY-Vertrag für die Take-One-Prüfwerkzeuge
    lib/                           # Album-Bibliothek: room, door, pillow, breath, glitch, palette, beat …
    BUILD_NOTES.md                 # gebaute APIs + jede Anweisung des Leads während des Baus (Take One)
    tracks/<NN-slug>/
      config.js                    # Dauer, Audio, Song-Map
      STORYBOARD.md                # Abschnitt für Abschnitt: Bild, Schlüsselwort, Reads, Übergänge
      songmap/                     # beatmap.json (Takte) + words.json (Wort-Zeiten aus dem Vocal-Stem)
      chapters/chNN_*.js           # ein Kapitel pro Abschnittsgruppe, je ein Animator
      review/                      # Contact Sheets, Reviewer-Packs, QA-Berichte (klein halten)
    cuts/                          # exportierte Schnitte für den Review-Raum (gitignored)
      review-notes/                # notes.json, shots/, sent.log (aus dem Review-Raum)
    out/                           # Frames (gitignored)
    exports/                       # Final-mp4s + .srt über Git LFS
```

## 3. Zustand in der Track-Datei

Neue Sektion `## Video` in jeder Track-Datei. Die Felder werden über
`update_track_field` gesetzt (Tools-Regel aus CLAUDE.md: kein Handeditieren).

| Feld | Werte |
|---|---|
| `video_format` | `none` / `video` / `canvas` / `teaser` (Liste) |
| `video_status` | siehe Leiter |
| `video_audio_source` | `suno-preview` / `mastered` (Final nur mit `mastered`) |
| `video_review_score` | letzter Score des frischen Reviewers (1–10) + Runde |
| `video_flash_test` | `pending` / `pass` / `fail` |
| `video_url` | Plattform-Links nach Release |

**Status-Leiter** (vom MCP erzwungen):

```
Concept → Song-Mapped → Storyboarded → Critiqued → Test-Section Approved
→ Built → Gate Passed → Reviewed (PASS oder 3 Runden) → Notes Closed → Mastered-Render
→ QA Passed → Released
```

## 4. Rollen (Take-One-Jobs, auf ein Album übertragen)

Wie bei Take One sind das Jobs, nicht zwölf Agenten. Jeder Job postet nach getaner Arbeit
eine Zeile („Storyboard: …“), damit der Lead den Film entstehen sieht und eingreifen kann.

| Take-One-Job | Hier | Wird vom Album übersprungen? |
|---|---|---|
| Strategist | Album-Kontext, Plattformen, CW-Lage | — |
| Creative director | die eine Idee pro Track, auf dem Album-Bogen | — |
| Writer | Wörter auf dem Bild: fast keine (§8.4); dafür die `.srt`-Untertitel aus den Streaming Lyrics | — |
| Voice director | — | ja (Song bringt die Stimmen) |
| Art director | Album-Look aus `VIDEO-CONCEPT.md`, Visual-Language-Guide, Take-One-Stil *Ink wash* als Nachbar | — |
| Storyboard artist | Storyboard Abschnitt für Abschnitt | — |
| Cinematographer | Kapitel bauen (Animatoren) | — |
| Composer | — | ja (Musik kommt aus der Musik-Kette) |
| Sound designer | — | in der Regel ja: die Musik ist der Ton. Ausnahme: CW-Tafel-Stille |
| Editor | Schnitt auf Takt und Wort-Zeiten, Master-Encode | — |
| Reviewer | frischer Agent pro Runde, max. 3 Runden | — |
| Social copywriter | Plattform-Texte mit CW, über `promo-writer` aus der Musik-Domain | — |

**Die Album-DNA ist der „Owner's taste“.** Take One holt einen Taste-File an drei Stellen
in den Raum: vor dem Pitch, bei den Wörtern und beim Review. Hier ist das der Gate-Skill
`skills/theagencysystem/` mit den passenden Snippets (Funktion × Zustand, Visual-Language,
name_exposure). Wo er einer allgemeinen Take-One-Regel widerspricht, gewinnt er. Wo der
Lead widerspricht, gewinnt der Lead.

## 5. Die Skill-Kette

Gleiche Logik wie in der Musik-Domain: Jeder Skill deklariert `prerequisites:`. Die
Schritte sind empfohlen. Gates mit **(hartes Gate)** blockieren, wenn der Skill läuft.

```
[Album-Ebene]
video-conceptualizer   Look, Palette, Formate, harte Regeln, Raum-Zustände pro Track,
  ↓                    Bogen über das Album (Take One: „one arc“, Ende reimt sich auf Anfang)
                       (hartes Gate: Phase-7-Bestätigung, wie album-conceptualizer)
video-library          gemalte Album-Bibliothek in video/lib/ + Loop-Sheets zum Prüfen
                       (wie die Modell-Sheets des Kits: ?loop=room, ?loop=pillow …)

[Pro Track]
video-songmap          Vocal-Stem (demucs), Wort-Zeiten (whisper) gegen die Streaming Lyrics,
  ↓                    betonte Silben, Tempo-Drift-Check, beatmap.py für Takte/Abschnitte/Drop
                       → songmap/beatmap.json + songmap/words.json
video-storyboard       Abschnitt für Abschnitt: Bild, Schlüsselwort jeder Zeile mit Zeit, Reads,
  ↓                    Übergänge, erstes/letztes Bild jedes Kapitels, Steigerung der Refrains,
                       Anschluss an Nachbar-Tracks (Director-Job)
video-critique         unabhängiger Critic-Agent prüft das Storyboard gegen timing.md und die
  ↓                    Quality-Checklist, bevor animiert wird (tote Einstellungen, zwei Reads
                       zugleich, Refrains ohne Steigerung, fehlende Payoffs, Kapitel-Nähte)
                       (hartes Gate: Lead bestätigt das Storyboard)
video-test-section     die ersten ~30–45 s fertig bauen; wird Stil-Bibel für alle Animatoren
  ↓                    (hartes Gate: Lead nimmt den Look ab)
video-build            ein Animator pro Kapitel, höchstens zwei schwere Agenten gleichzeitig;
  ↓                    jeder rendert sein Kapitel mit --clip --range in eigene Dateien,
                       prüft Contact Sheets und Strips an jedem Schlüsselwort;
                       Integrator prüft jede Kapitelnaht Frame für Frame
video-gate             gate.mjs (Determinismus, Vertrag, tote Luft), text-audit.mjs
  ↓                    (nur CW-Tafel und T12 erlaubt), Blitz-Test
                       (hartes Gate)
video-review           Reviewer-Pack bauen, frischer Reviewer-Agent: Score pro Achse,
  ↓                    10-Sekunden-Karte, drei schlimmste Probleme mit Zeitstempel;
                       PASS bei 8+ auf allen Achsen, sonst zurück; max. 3 Runden
video-notes            Schnitt in den Review-Raum; Lead pinnt Notizen an Frames;
  ↓                    jede Notizrunde wird der nächste Take
                       (hartes Gate: Edit-Lock durch den Lead)
video-render           Master-Render mit Master-Audio (render-parallel / --frames --workers),
  ↓                    audio-check (−14 LUFS, −1 dBTP), Länge Bild == Länge Audio,
                       .srt aus words.json + Streaming Lyrics
video-release          YouTube/Canvas-Metadaten, CW-Text, Altersfreigabe, Untertitel-Upload,
                       video_url setzen
```

### Vorbilder

| Video-Skill | bitwize | Take One | ClaudeAnimationBase / Higgsfield |
|---|---|---|---|
| `video-conceptualizer` | `album-conceptualizer` | Pitch (SKILL.md §3), music-video.md §4 | Guide-Regel 7 |
| `video-library` | — | Character department (§3b) | `clawd.js` + `sheets.js` als Muster |
| `video-songmap` | `import-audio` | audio.md: Vocal-Timing, Tempo-Drift, `songmap.py` | Higgsfield `beatmap.py` |
| `video-storyboard` | `lyric-writer` | music-video.md §5, „Storytelling with the lyrics“ | Guide-Workflow §1 |
| `video-critique` | `lyric-reviewer` | „Critic agent“ (Studio-Prozess) | — |
| `video-test-section` | — | „approved test section as style bible“ | — |
| `video-build` | — | „Running the parallel build“ | Guide-Workflow §2–3, `render.mjs` |
| `video-gate` | `pre-generation-check` | `gate.mjs`, `text-audit.mjs`, `plate-audit.mjs` | — |
| `video-review` | — | `reviewer-brief.md`, `quality-checklist.md`, `review-pack.sh` | Higgsfield `qa.md` |
| `video-notes` | — | `review-room.md` | — |
| `video-render` | `mastering-engineer` | `render-parallel.sh`, `audio-check.mjs`, `export.mjs` | `render.mjs --frames/--encode` |
| `video-release` | `release-director`, `promo-writer` | `captions.md` | — |

### Anschluss an die Musik-Kette

```
lyric-writer … pre-generation-check → [Suno] → import-audio ─┬→ mix/mastering → release-director
                                                             │
video-conceptualizer (darf vor Suno laufen) ─────────────────┴→ video-songmap
                                                               (Suno-Preview reicht zum Bauen,
                                                                wenn Mastering die Länge nicht ändert;
                                                                Song-Map nach dem Master neu prüfen)
                                                               video-render mit Master-Audio
```

- Die Song-Map nutzt die **Streaming Lyrics** als Text (whisper liefert nur die Zeiten).
  Das ist dieselbe Regel wie in der Musik-Domain: nie phonetische Suno-Lyrics nach außen.
- `release-director` bekommt eine optionale Domäne „Video“, die `video_status`,
  `video_flash_test` und `video_review_score` prüft. Sie blockiert nur, wenn für den Track
  ein Video angekündigt ist.
- `next-step` und `resume` werden um den Video-Zweig ergänzt.

## 6. Klebstoff zwischen den Repos

1. **Vertrags-Shim.** Die Take-One-Werkzeuge (`gate.mjs`, `frames.mjs`, `text-audit.mjs`)
   erwarten `window.renderFrame(t)` und `window.READY`. ClaudeAnimationBase bietet
   `window.renderAt(t)` und `window.ready`. `shim/take-one.js` verbindet beides. Der
   Contract-Scan von `gate.mjs` verbietet `Math.random`/`Date.now` im Zeichenpfad. Das Kit
   nutzt p5s geseedetes `random()`. Prüfen, ob p5 intern `Math.random` aufruft; falls ja,
   Ausnahme dokumentieren.
2. **Song-Map → Kit.** `lib/beat.js` liest `beatmap.json` und `words.json` und ersetzt
   `bpOf`/`pulse`/`beatN` des Kits (feste BPM können die Tempo-Rampe von T01, 60→90, nicht).
   Dazu kommt `wordAt(t)` bzw. `keyword(lineId)` für Aktionen auf Schlüsselwörtern.
3. **Kit-Änderungen.** Einige sind beim Test-Render in diesem Container aufgefallen:
   - Chrome-Erkennung: `/usr/bin/google-chrome` war nur ein Wrapper. Playwright-Chromium
     in die Suchliste aufnehmen oder vorher einen Probe-Start machen.
   - Navigations-Timeout als Flag (Software-WebGL braucht länger als 30 s/60 s).
   - `?track=NN` und `--track=NN` für mehrere Tracks in einem Kit.
   - Dedupe auf Zweiern (jedes zweite Bild kopieren).
   - 9:16 für Canvas-Loops (`W`/`H` sind fest 1920×1080).
   - `clawd.js` nicht laden.
4. **Take One läuft bisher nur auf macOS** (README: „not tried yet: a computer that is not
   a Mac“). `frames.mjs` startet `channel: 'chrome'`. Auf Linux muss Playwright-Chromium
   gehen; das gehört in den Pilot.

## 7. MCP-Handler (`handlers/video/`)

Nach dem Vier-Verben-Vertrag aus `Plan/harness/VOCABULARY.md`, Anker-Triade
`video_search` / `video_describe` / `video_invoke`. Darunter:

| Tool | Was es tut |
|---|---|
| `create_video_kit` | legt `video/` für ein Album aus `templates/video/` an (Kit + Shim, gepinnte Versionen) |
| `create_video_track` | legt `tracks/<NN-slug>/` an, verlinkt Audio und Streaming Lyrics |
| `run_songmap` | demucs + whisper + beatmap.py, schreibt `songmap/*.json`, setzt `Song-Mapped` |
| `render_status` | fehlende/fertige Frames pro Kapitel, ms/Frame, ETA |
| `run_gate` | `gate.mjs` + `text-audit.mjs` + Blitz-Test, setzt `video_flash_test` |
| `build_review_pack` | `review-pack.sh`-Äquivalent: Sheets, Strips, WORDS-AND-SOUND.md mit Messwerten |
| `review_notes` | liest `cuts/review-notes/notes.json`, offene/erledigte Notizen pro Schnitt |
| `export_subtitles` | `.srt` aus `words.json` + Streaming Lyrics |
| `check_video_text` | name_exposure und Text-Ausnahmen gegen Kapitel-Code und Metadaten |
| `update_track_field` | (vorhanden) um die Video-Felder und die Leiter erweitert |

## 8. Album-DNA als Gates

Der Gate-Skill `skills/theagencysystem/` lädt vor jeder Video-Phase die passenden
Snippets. Neue Anknüpfungen in `references/bitwize-attachment.md`:

- `video-storyboard` / `video-critique` → `matrix-index.yaml` (Funktion × Zustand) +
  `state-axis.md`
- `video-library` / `video-build` → `overrides/visual-language-guide.md`,
  `overrides/image-style-spec.md`
- `video-review` → im Reviewer-Brief unter „What is locked“: Darstellungsregeln, kein Text,
  keine Figuren. Sonst verbraucht der Reviewer seine drei Probleme auf Dinge, die per
  Konzept so sein müssen.
- `video-gate` / `video-release` → name_exposure (Design-Ebene: nur Funktion/Rolle, nie Namen)

## 9. Rollout

| Phase | Inhalt | Ergebnis |
|---|---|---|
| **P−1 — Port** ✅ | Die drei Repos nach `skills/video/` übernommen; Domain `video` in `shared_list_skills`/`plugin_help` | erledigt (2026-11-07) |
| **P1 — Skill-Suite** ✅ | Video Studio: Skill + Subagenten-Briefs + Playbooks + Werkzeuge, ersetzt die drei Ports | erledigt (2026-11-07), Tests in `tests/unit/video/` |
| **P0 — Pilot von Hand** | Kit + Shim ins Album, Bibliothek-Minimum (Raum, Kissen, Atem, Palette, `beat.js`). T02: Song-Map, Storyboard, Critic, Test-Section (~45 s). Take-One-Tools auf Linux/Mac zum Laufen bringen, Renderzeit und Token-Verbrauch messen. | Clip + Erfahrungsbericht `Plan/_lessons-learned/140-pilot.md` |
| **P1 — Skills ohne Handler** | `skills/video/*` als Prompt-Skills, die die Take-One-Referenzen laden | Kette läuft |
| **P2 — Handler + Status-Leiter** | `handlers/video/`, Felder in `update_track_field`, Templates | Tools-Regel gilt auch für Video |
| **P3 — Album** | 13 Musikvideos + Canvas-Loops + Teaser, zwei Tracks parallel | Release-fähiges Video-Paket |
| **P4 — Upstream** | Kit-Änderungen (§6.3) als PRs an `ClaudeAnimationBase`, Linux-Fixes an `take-one` | allgemein nutzbar |

Vor P2 eine ADR: „Video als siebte Domain“ (Bezug: `Plan/decisions/0004-five-handler-domains.md`).

## 10. Risiken

- **Token-Verbrauch.** Take One schätzt 0,4–0,7 Mio. Tokens für 30 s Film in einer Session
  und einen Mehrfachen davon, wenn der Bau auf Agenten verteilt wird. Linear hochgerechnet
  (ungeprüft) wären das für einen 4-Minuten-Track mehrere Millionen Tokens, für das Album
  ein Vielfaches. Der Pilot misst das. Take-One-Lektion: höchstens zwei schwere Agenten
  gleichzeitig, kleine Fixes an ein leichteres Modell.
- **Renderzeit ohne GPU.** In Cloud-Containern ohne GPU (wie diesem) dauert ein Bild bis zu
  30 s. Volle Songs rendern auf einer Maschine mit GPU. Bauen und Reviewen mit Contact
  Sheets geht auch ohne.
- **„Kein Text“ vs. stumme Zuschauer.** Take One hat gelernt, dass ein stummer Zuschauer
  ohne Wörter einem gesprochenen Musikvideo nicht folgen kann. Für dieses Album gilt trotzdem
  „spielen statt schreiben“. Die Lösung sind Untertitel als `.srt` (vom Zuschauer
  zuschaltbar) statt eingebrannter Lyrics. Entscheidung beim Lead (§11).
- **Kein Charakter.** Take One sagt, Filme ohne Figur oder Gesicht stoppen das Scrollen
  seltener. Hier tragen Objekte und Licht. Der Pilot zeigt, ob das reicht.
- **Belastung beim Review.** Das Album behandelt sexualisierte Gewalt. Reviews werden
  getaktet, der Review-Raum erlaubt Pausen zwischen Notizrunden.
- **Agent kann nicht hören.** Take One: messen, und der frische Reviewer bekommt die
  Messwerte statt des Tons. Eine Person hört vor der Abnahme.

## 11. Offene Entscheidungen

1. Zielmaschine mit GPU für das Rendern.
2. Lyrics: nur `.srt`-Untertitel (empfohlen) oder dezent eingebrannt?
3. Kit-Änderungen als Fork im Album oder als PRs an `ClaudeAnimationBase` / `take-one`.
4. Arbeitsweise pro Track: „Run“ bis zum ersten fertigen Take oder „in Stages“ (Take One
   fragt das jedes Mal).
5. Ob die Video-Skills ins Agency-Plugin gehören (Empfehlung) oder als eigenes Plugin
   neben den drei Repos leben.
