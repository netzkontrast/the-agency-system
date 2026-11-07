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
  - netzkontrast/ClaudeAnimationBase
  - netzkontrast/higgsfield-video-engineer
estimated_jules_sessions: 0
domain: video
wave: C
spec_kind: research_epic
---

> **Noch kein Jules-Auftrag.** Dieser Spec ist ein Planungsdokument. Er wird erst in
> Jules-taugliche Teil-Specs (140a …) zerlegt, nachdem der Pilot (§8, Phase P0) gelaufen
> ist und die offenen Entscheidungen (§10) getroffen sind.

# Spec 140 — Video-Domain: Musikvideo-Pipeline pro Song (analog zu bitwize)

## Warum

Die Musik-Domain bringt einen Song von der Idee bis zum Release: eine feste Skill-Kette,
Gates an den Übergängen, Status-Felder in der Track-Datei, MCP-Tools als Setter. Für
Videos gibt es nichts Vergleichbares. Diese Lücke soll eine Video-Domain füllen, die
denselben Mustern folgt und auf einer bestehenden Animations-Engine aufsetzt.

Erstes Zielalbum: *Lass mich, lass mich atmen* — Konzept in
`artists/the-agency-system/albums/dystopian-future-synth/lass-mich-lass-mich-atmen/VIDEO-CONCEPT.md`.

## 1. Engine-Wahl

| | `ClaudeAnimationBase` (**gewählt**) | `higgsfield-video-engineer` |
|---|---|---|
| Technik | p5.js + p5.brush, flaches 2D, gemalt; Headless Chrome | eigener WebGPU-Path-Tracer, 3D |
| Look | Pinsel, Aquarell, Kohle-Schraffur, kochende Tuschelinien, Papierkorn | physikalisch korrektes Licht, Filz/Papier/Ton als 3D-Material |
| Kosten pro Bild | Sekunden ohne GPU (gemessen hier: 26–32 s mit Software-WebGL, 4 CPU-Kerne, kein GPU — schlechtester Fall); mit GPU deutlich weniger (noch nicht gemessen) | 20–43 s mit GPU (laut README) |
| Länge | volle Songs machbar; paralleles, fortsetzbares Rendern | ausgelegt auf 15–30 s |
| Passt zur Agency-Ästhetik | direkt (Visual-Language-Guide: Tusche, Kohle, Papier, Zitterlinie) | nur über Umwege (Papier-Diorama) |
| Review-Werkzeuge | `studio.html` zum Scrubben; Contact Sheets, Frame-Strips, Crops per CLI | Proof-Renders, Animatic |
| Regelwerk | `ANIMATION_GUIDE.md`: Storyboard zuerst, Reads/Timing, Übergänge, Animationsprinzipien | 12-Phasen-Produktionskarte, Light-Standard, QA |

**Entscheidung:** ClaudeAnimationBase ist die Engine. Aus `higgsfield-video-engineer`
übernehmen wir **Werkzeuge und Prozess, nicht den Renderer**:
- `tools/beatmap.py` (Bar-Map: BPM, Downbeats, Abschnitte, Drop, Hits, Stopps)
- die QA-Disziplin (`references/qa.md`: Maschinen-Pass, Fresh-Eyes-Reviewer, feste Gates)
- das Sub-Agenten-Briefing (`references/briefing-agents.md`)
- den Lautheits-/Encode-Standard (−14 LUFS, −1 dBTP)

Der Path-Tracer bleibt optional für Standbilder (Cover, Eckpfeiler-Bilder), wenn ein
fotorealistischer Look gewünscht ist.

## 2. Ablage auf der Platte

**Ein Kit pro Album**, alle Tracks darin. So teilen sich alle Videos Palette, Bibliothek
und Engine-Version.

```
artists/<artist>/albums/<genre>/<album>/
  VIDEO-CONCEPT.md                 # Album-Ebene: Look, Formate, harte Regeln (Gate)
  video/
    package.json                   # p5, p5.brush, puppeteer-core (Versionen gepinnt)
    studio.html                    # aus dem Kit; ?track=02 wählt den Track
    render.mjs                     # aus dem Kit, + --track, + Dedupe für onTwos
    engine/                        # core.js, timeline.js aus dem Kit (ohne clawd.js)
    lib/                           # Album-Bibliothek: room, door, pillow, breath, glitch, palette, beat …
    tracks/<NN-slug>/
      config.js                    # Dauer, Audio-Pfad, Bar-Map-Pfad
      STORYBOARD.md                # Reads pro Einstellung (Guide-Workflow §1)
      beatmap.json                 # aus beatmap.py
      scenes/*.js                  # shots([...]) für diesen Track
      review/                      # Contact Sheets, QA-Berichte (klein halten)
    out/                           # Frames — gitignored
    exports/                       # Final-mp4s über Git LFS
```

## 3. Zustand in der Track-Datei

Neue Sektion `## Video` in jeder Track-Datei. Die Felder werden über
`update_track_field` gesetzt (Tools-Regel aus CLAUDE.md: kein Handeditieren).

| Feld | Werte |
|---|---|
| `video_format` | `none` / `video` / `canvas` / `teaser` (Liste) |
| `video_status` | siehe Leiter |
| `video_audio_source` | `suno-preview` / `mastered` (Final nur mit `mastered`) |
| `video_flash_test` | `pending` / `pass` / `fail` |
| `video_url` | Plattform-Links nach Release |

**Status-Leiter** (vom MCP erzwungen):

```
Concept → Storyboarded → Beatmapped → Built → Reviewed (edit lock)
→ Rendered → QA Passed → Released
```

## 4. Die Skill-Kette

Gleiche Logik wie in der Musik-Domain: Jeder Skill deklariert `prerequisites:`. Die
Schritte sind empfohlen. Gates mit **(hartes Gate)** blockieren, wenn der Skill läuft.

```
[Album-Ebene]
video-conceptualizer   Look, Palette, Formate, harte Regeln, Raum-Zustände pro Track
  ↓                    (hartes Gate: Phase-7-Bestätigung, wie album-conceptualizer)
video-library          gemalte Album-Bibliothek in video/lib/ + Loop-Sheets zum Prüfen
                       (wie die Modell-Sheets des Kits: ?loop=room, ?loop=pillow …)

[Pro Track]
video-storyboard       Reads pro Einstellung, Übergänge, Kontinuität zum Nachbar-Track
  ↓                    (liest Lyrics/Concept/Voice Lead/Yellow image aus der Track-Datei;
                        hartes Gate: Lead bestätigt das Storyboard vor jedem Code —
                        Guide-Regel 7)
video-beatmap          beatmap.py auf das importierte Audio → beatmap.json
  ↓                    + Abgleich mit der Songstruktur
video-build            scenes/*.js Einstellung für Einstellung; Sub-Agent pro Einstellung
  ↓                    möglich (Lead besitzt timeline + Storyboard)
video-review           Contact Sheet (ganze Form), Strips (jede Bewegung), Crops (Details),
  ↓                    Scrubben in studio.html mit Ton; Fresh-Eyes-Agent
                       (hartes Gate: Edit-Lock durch den Lead)
video-render           --frames --workers=N, fortsetzbar; --encode mit Master-Audio
  ↓
video-qa               Blitz-Test, name_exposure, Text-Ausnahmen geprüft, CW-Tafel,
  ↓                    Darstellungsregeln, Lautheit, Länge Bild == Länge Audio
                       (hartes Gate)
video-release          YouTube/Canvas-Metadaten, CW-Text, Altersfreigabe, video_url setzen
```

Die Kette ist kürzer als im Higgsfield-Plan. Styleframes, Asset-Proofs, Animatic und
Look-Pass fallen zusammen, weil Rendern billig ist und `studio.html` Echtzeit-Scrubbing
erlaubt. Der Review-Loop des Kits (Sheet → Strip → Crop) übernimmt diese Rolle.

### Vorbilder

| Video-Skill | Vorbild in bitwize | Vorbild in den Engine-Repos |
|---|---|---|
| `video-conceptualizer` | `album-conceptualizer` | Guide-Regel 7 „Ein Stück“ |
| `video-library` | — | `clawd.js` + Modell-Sheets (`sheets.js`) als Muster |
| `video-storyboard` | `lyric-writer` (pro Track, liest Album-DNA) | Guide-Workflow §1 |
| `video-beatmap` | `import-audio` | Higgsfield `tools/beatmap.py` |
| `video-build` | — | Guide-Workflow §2, Higgsfield `briefing-agents.md` |
| `video-review` | `lyric-reviewer` | Guide-Workflow §3, Higgsfield `qa.md` |
| `video-render` | `mastering-engineer` | `render.mjs --frames/--encode` |
| `video-qa` | `pre-generation-check` + `release-director` | Higgsfield `qa.md` |
| `video-release` | `release-director`, `promo-writer` | — |

### Anschluss an die Musik-Kette

```
lyric-writer … pre-generation-check → [Suno] → import-audio ─┬→ mix/mastering → release-director
                                                             │
video-storyboard (darf vor Suno laufen) ─────────────────────┴→ video-beatmap
                                                               (Suno-Preview reicht zum Bauen,
                                                                wenn Mastering die Länge nicht ändert)
                                                               video-render --encode mit Master-Audio
```

- `release-director` bekommt eine optionale Domäne „Video“, die `video_status` und
  `video_flash_test` prüft. Sie blockiert nur, wenn für den Track ein Video angekündigt ist.
- `next-step` und `resume` werden um den Video-Zweig ergänzt.

## 5. Änderungen am Kit

Sie liegen im Album-Kit oder als PRs an `ClaudeAnimationBase`, wenn sie allgemein nützlich
sind. Die ersten beiden sind beim Test in diesem Container aufgefallen:

1. **Chrome-Erkennung:** `render.mjs` nimmt den ersten existierenden Pfad. In Umgebungen,
   in denen `/usr/bin/google-chrome` nur ein Wrapper ist, schlägt das Laden fehl. Lösung:
   Playwright-Chromium (`/opt/pw-browsers/...`) mit in die Suchliste aufnehmen, oder ein
   Probe-Start vor der Auswahl.
2. **Navigations-Timeout:** Mit Software-WebGL dauert der Seitenstart länger als die festen
   30 s/60 s (`page.goto`, `waitForFunction`). Lösung: den Timeout als Flag konfigurierbar
   machen.
3. **Bar-Map statt fester BPM:** `PROJECT.bpm` + `offset` kann keine Tempo-Rampen (T01:
   60→90). `lib/beat.js` liest `beatmap.json` und ersetzt `bpOf`/`pulse`/`beatN`.
4. **Mehrere Tracks in einem Kit:** `?track=NN` lädt die `config.js` und die Szenen des
   Tracks; `render.mjs --track=NN`.
5. **Dedupe auf Zweiern:** Wenn eine Einstellung `onTwos` nutzt, wird jedes zweite Bild
   kopiert statt gerendert.
6. **Format:** `W`/`H` sind fest 1920×1080. Für Canvas-Loops wird 1080×1920 als Option
   gebraucht.
7. **Clawd entfernen:** `clawd.js` wird für dieses Album nicht geladen (kein Maskottchen).

## 6. MCP-Handler (`handlers/video/`)

Nach dem Vier-Verben-Vertrag aus `Plan/harness/VOCABULARY.md`, Anker-Triade
`video_search` / `video_describe` / `video_invoke`. Darunter:

| Tool | Was es tut |
|---|---|
| `create_video_kit` | legt `video/` für ein Album aus `templates/video/` an (Kit-Kopie, gepinnte Versionen) |
| `create_video_track` | legt `tracks/<NN-slug>/` an, verlinkt Audio und Lyrics |
| `run_beatmap` | `beatmap.py` mit `python -I`, schreibt `beatmap.json`, setzt `Beatmapped` |
| `render_status` | fehlende/fertige Frames, ms/Frame aus dem Log, ETA |
| `flash_test` | Luminanz-/Rot-Flash-Analyse über alle Frames, setzt `video_flash_test` |
| `check_video_text` | name_exposure und Text-Ausnahmen gegen Szenen-Code und Metadaten |
| `update_track_field` | (vorhanden) um die Video-Felder und die Leiter erweitert |

## 7. Album-DNA als Gates

Der Gate-Skill `skills/theagencysystem/` lädt vor jeder Video-Phase die passenden
Snippets. Neue Anknüpfungen in `references/bitwize-attachment.md`:

- `video-storyboard` → `matrix-index.yaml` (Funktion × Zustand) + `state-axis.md`
- `video-library` / `video-build` → `overrides/visual-language-guide.md`,
  `overrides/image-style-spec.md`
- `video-qa` → name_exposure (Design-Ebene: nur Funktion/Rolle, nie Namen)

## 8. Rollout

| Phase | Inhalt | Ergebnis |
|---|---|---|
| **P0 — Pilot von Hand** | Kit ins Album kopieren. Bibliothek-Minimum: Raum, Kissen, Atem, Palette, `beat.js`. T02, erste ~45 s. Renderzeit auf der Zielmaschine messen. | Clip + Erfahrungsbericht `Plan/_lessons-learned/140-pilot.md` |
| **P1 — Skills ohne Handler** | `skills/video/*` als Prompt-Skills; Zustand vorerst in `STORYBOARD.md` | Kette läuft |
| **P2 — Handler + Status-Leiter** | `handlers/video/`, Felder in `update_track_field`, Templates | Tools-Regel gilt auch für Video |
| **P3 — Album** | 13 Musikvideos + Canvas-Loops + Teaser | Release-fähiges Video-Paket |
| **P4 — Upstream** | Kit-Änderungen aus §5 als PRs an `ClaudeAnimationBase` | allgemein nutzbar |

Vor P2 eine ADR: „Video als siebte Domain“ (Bezug: `Plan/decisions/0004-five-handler-domains.md`).

## 9. Risiken

- **Renderzeit ohne GPU.** In Cloud-Containern ohne GPU (wie diesem) dauert ein Bild bis zu
  30 s. Volle Songs rendern deshalb auf einer Maschine mit GPU (lokal oder gemietet).
  Bauen und Reviewen mit Contact Sheets geht auch ohne GPU.
- **„Kein Text“ vs. Album-Inhalt.** Die Lyrics tragen viel. Der Guide verlangt, Bedeutung
  zu spielen statt sie zu schreiben. Das ist richtig für das Album, aber schwer. Die zwei
  Ausnahmen (T12, CW-Tafel) sind festgelegt, mehr nicht.
- **Kein Charakter.** Das Kit ist um eine Figur gebaut, die Lebendigkeit trägt. Ohne Figur
  müssen Objekte und Licht „spielen“. Der Pilot zeigt, ob das trägt.
- **Belastung beim Review.** Das Album behandelt sexualisierte Gewalt. Reviews werden
  getaktet.
- **Plattformen.** CW-Text und ggf. Altersfreigabe gehören in `video-release`.
- **Agent kann nicht hören.** Messen, und eine Person schaut vor der Abnahme.

## 10. Offene Entscheidungen

1. Zielmaschine mit GPU für das Rendern.
2. Kit-Änderungen (§5) als Fork im Album oder als PRs ans Kit-Repo.
3. Ob die Video-Skills ins Agency-Plugin gehören (Empfehlung) oder als eigenes Plugin
   neben dem Kit leben.
