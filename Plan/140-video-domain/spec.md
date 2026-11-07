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
Videos gibt es nichts Vergleichbares. Das zweite Repo,
`netzkontrast/higgsfield-video-engineer` (Skill `code-based-films`), liefert dafür die
**Produktionsmaschine**: einen eigenen WebGPU-Path-Tracer, ein Bar-Map-Werkzeug
(`tools/beatmap.py`), einen 12-Phasen-Ablauf mit Gates und einen Encoder. Es fehlt die
**Brücke**: wie ein Track aus `artists/<artist>/albums/…` mit Lyrics, Style Box, Audio
und Album-DNA in ein Video-Projekt übergeht, wer welchen Status setzt und wo die
Album-DNA (Gelb-Protokoll, name_exposure, Content-Warnungen) als Gate greift.

Erstes Zielalbum: *Lass mich, lass mich atmen* — Konzept in
`artists/the-agency-system/albums/dystopian-future-synth/lass-mich-lass-mich-atmen/VIDEO-CONCEPT.md`.

## 1. Was die Engine kann und wo sie nicht passt

| Engine (`code-based-films`) | Folge für die Video-Domain |
|---|---|
| Ausgelegt auf **15–30-s-Filme** | Songs dauern 3–5,5 min. → Format-Stufen A/B/C/V (siehe Album-Konzept §2); volle Länge nur „auf Zweiern“ (12 fps) oder als Visualizer aus Plates + 2D-Post. |
| ~20 s/Frame (RTX 4090), ~43 s (M4 Max) bei Final-Qualität | Render-Budget wird pro Track geplant und als Gate geprüft, bevor die Final-Phase startet. |
| **Musik zuerst, Timing an der Bar-Map** | Passt genau: Audio kommt aus der Musik-Kette (`import-audio`). |
| Generierte Bilder **nur als Ziel** (`refs/`), nie im Bild | Passt zum Album-Art-Workflow: `album-art-director` liefert schon Prompts im Album-Look. |
| Eigener Code im Bild, OFL-Schriften, keine fremden Assets | Wird übernommen. Suno-Audio gilt als eigene Musik. |
| Lead besitzt Story, Schnitt, Abnahme; Sub-Agenten bekommen enge Aufgaben | Entspricht der CLAUDE.md-Regel „Subagenten für unabhängige Arbeit“. |
| Kein Begriff von Lyrics, Stimmen, Content-Warnung, Album-Kontinuität | **Das ergänzt die Video-Domain.** |

**Entscheidung:** Die Engine bleibt im eigenen Repo und wird als Abhängigkeit genutzt
(`npx skills add …` bzw. Symlink `engine/` in das Projekt, wie in `SKILL.md` vorgesehen).
Die Video-Domain im Agency-Plugin enthält nur Orchestrierung, Zustand und Gates — keinen
Renderer-Code.

## 2. Ablage auf der Platte

```
artists/<artist>/albums/<genre>/<album>/
  VIDEO-CONCEPT.md                 # Album-Ebene: Look-Bibel, Formate, harte Regeln (Gate)
  video/
    lib/                           # gemeinsame Assets des Albums (Set, Requisiten, FX, Post)
      set/  prop/  fx/  post/  fonts/
    <NN-track-slug>/               # ein Engine-Projekt pro Track (Struktur wie felt-good-morning)
      TREATMENT.md
      BEATS.md                     # Beat Sheet, nur der Lead editiert
      music/beatmap.json           # aus tools/beatmap.py
      refs/                        # Styleframes (Ziel, nie im Bild)
      shots/  story.mjs  film.mjs  render_job.mjs
      assets/<x>/GAPS.md
      review/                      # QA-Berichte
      out/                         # Frames — gitignored
    exports/                       # nur Final-mp4s, über Git LFS
```

Frames und Zwischenbilder landen **nie** in Git (`.gitignore`: `video/*/out/`). Finale
Videos gehen über Git LFS, wie `audio/`.

## 3. Zustand in der Track-Datei

Neue Sektion `## Video` in jeder Track-Datei, Felder über `update_track_field`
(Tools-Regel aus CLAUDE.md: kein Handeditieren):

| Feld | Werte |
|---|---|
| `video_tier` | `none` / `A` / `B` / `C` / `V` (mehrere erlaubt, z. B. `A,B,C`) |
| `video_status` | siehe Leiter unten |
| `video_project` | relativer Pfad zu `video/<NN-slug>/` |
| `video_audio_source` | `suno-preview` / `mastered` (Final nur mit `mastered`) |
| `video_render_budget` | geschätzte GPU-Stunden |
| `video_flash_test` | `pending` / `pass` / `fail` |
| `video_url` | Plattform-Links nach Release |

**Status-Leiter** (vom MCP erzwungen, wie bei den Musik-Status):

```
Concept → Treatment → Beatmapped → Boarded → Styleframes Approved → Assets Ready
→ Animatic Locked → Look Approved → Rendered → QA Passed → Released
```

## 4. Die Skill-Kette

Gleiche Logik wie in der Musik-Domain: jeder Skill deklariert `prerequisites:`; die
Schritte sind empfohlen, Gates mit **(hartes Gate)** blockieren, wenn der Skill läuft.

```
[Album-Ebene]
video-conceptualizer        Look-Bibel, Formate, harte Regeln, Track-Zustände
  ↓                         (hartes Gate: Phase-7-Bestätigung, wie album-conceptualizer)
video-asset-library         gemeinsame Album-Assets in Code + Proof-Renders + GAPS.md

[Pro Track]
video-treatment             Logline, Kernbild, Endbild, Raum-Zustand, Stimmen → Licht-Mapping
  ↓                         (liest Lyrics/Concept/Voice Lead/Yellow image aus der Track-Datei)
video-beatmap               tools/beatmap.py auf das importierte Audio → music/beatmap.json
  ↓                         + Abgleich mit Songstruktur (Verse/Refrain aus der Lyrics Box)
video-storyboard            BEATS.md: eine Zeile pro Einstellung, Events auf Downbeats
  ↓
video-styleframes           Styleframe pro Einstellung (refs/), Prompts aus image-style-spec
  ↓                         (hartes Gate: Lead-Abnahme als Ziel; name_exposure-Prüfung)
video-shot-builder          story.mjs / film.mjs; Sub-Agent pro Asset oder Einstellung
  ↓
video-animatic              Vorschau 640×480, 32–64 spp, mit Audio encodiert
  ↓                         (hartes Gate: Edit-Lock durch den Lead)
video-look-pass             2–3 Testbilder pro Einstellung gegen den Styleframe
  ↓
video-render                Final in Chunks, lokal oder Runpod, fortsetzbar
  ↓                         (Gate: Budget-Check gegen video_render_budget vor Start)
video-post                  analog-glitch-Pass, Titel/CW-Tafel/Lyrics (OFL), Encode mit Master-Audio
  ↓
video-qa                    Maschinen-Pass, ein Bild pro Einstellung per Auge, Fresh-Eyes-Agent
  ↓                         (hartes Gate: Blitz-Test, name_exposure, Lyrics-Quelle, CW-Tafel,
                             Darstellungsregeln des Albums, Lautheit −14 LUFS / −1 dBTP)
video-release               YouTube/Canvas-Metadaten, CW-Text, Altersfreigabe, video_url setzen
```

### Woher die Skills kommen

| Video-Skill | Vorbild in bitwize | Vorbild in Higgsfield |
|---|---|---|
| `video-conceptualizer` | `album-conceptualizer` (7 Phasen, Bestätigungs-Gate) | Phase 0 „Research and bar“ |
| `video-treatment` | `lyric-writer` (pro Track, liest Album-DNA) | Phase 1 „Story“ |
| `video-beatmap` | `import-audio` (Audio-Pfade) | `tools/beatmap.py`, Phase 2 |
| `video-storyboard` | — | Phase 3 `BEATS.md` |
| `video-styleframes` | `album-art-director` | Phase 4 |
| `video-asset-library`, `video-shot-builder` | — | Phase 5 + `briefing-agents.md` |
| `video-animatic`, `video-look-pass`, `video-render` | — | Phasen 6–9, `rendering.md` |
| `video-post` | `mastering-engineer` (Qualitäts-Endstufe) | Phase 10, `tools/encode.sh` |
| `video-qa` | `pre-generation-check` + `release-director` | Phase 11, `qa.md` |
| `video-release` | `release-director`, `promo-writer` | Phase 12 |

### Anschluss an die Musik-Kette

```
lyric-writer … pre-generation-check → [Suno] → import-audio ─┬→ mix/mastering → release-director
                                                             │
video-treatment (darf schon vor Suno laufen) ────────────────┴→ video-beatmap (Suno-Preview reicht
                                                                 für Animatic, wenn Mastering die
                                                                 Länge nicht ändert)
                                                               video-post encodiert mit Master-Audio
```

- `video-treatment`, `video-styleframes` und `video-asset-library` brauchen kein Audio
  und können sofort beginnen.
- `video-beatmap` braucht Audio. Wenn der Master später anders getrimmt wird, muss die
  Bar-Map neu laufen (QA prüft: Länge Master == Länge Bar-Map ± 1 Frame).
- `release-director` bekommt eine optionale zehnte Domäne „Video“, die `video_status`
  und `video_flash_test` prüft. Sie blockiert nur, wenn für den Track ein Video
  angekündigt ist.
- `/bitwize-music:next-step` bzw. `resume` werden um den Video-Zweig ergänzt, damit
  „Was kommt als Nächstes?“ auch Videoschritte nennt.

## 5. MCP-Handler (`handlers/video/`)

Nach dem Vier-Verben-Vertrag aus `Plan/harness/VOCABULARY.md`, Anker-Triade
`video_search` / `video_describe` / `video_invoke`. Darunter:

| Tool | Was es tut |
|---|---|
| `create_video_project` | legt `video/<NN-slug>/` aus `templates/video/` an, verlinkt Engine und `lib/` |
| `run_beatmap` | ruft `beatmap.py` mit `python -I` auf, schreibt `music/beatmap.json`, setzt `Beatmapped` |
| `render_status` | fehlende/fertige Frames pro Einstellung, ETA aus den Frame-Zeiten |
| `estimate_render_budget` | Frames × spp × gemessene s/Frame → GPU-Stunden |
| `flash_test` | Luminanz-/Rot-Flash-Analyse über alle Frames (numpy), schreibt `video_flash_test` |
| `check_video_text` | name_exposure-Liste und Lyrics-Quelle (Streaming Lyrics) gegen Titel, Untertitel, Beschreibungen |
| `update_track_field` | (vorhanden) um die Video-Felder erweitert, mit Status-Leiter |

## 6. Album-DNA als Gates (gilt für jedes Agency-System-Album)

Der Gate-Skill `skills/theagencysystem/` lädt vor jeder Video-Phase die passenden
Snippets. Neue Anknüpfungen in `references/bitwize-attachment.md`:

- `video-treatment` → `matrix-index.yaml` (Funktion × Zustand) + `state-axis.md`
- `video-styleframes` → `overrides/visual-language-guide.md`, `overrides/image-style-spec.md`
- `video-qa` → name_exposure (Design-Ebene: nur Funktion/Rolle, nie Namen)

## 7. Änderungen an der Engine (Upstream, `higgsfield-video-engineer`)

Klein halten. Nur was die Video-Domain wirklich braucht:

1. **Hold-Frames / „auf Zweiern“:** Render-Treiber kann jedes n-te Frame rendern und beim
   Encode halten (`--hold 2`).
2. **16:9 und 9:16 als Presets** neben 4:3 (`--aspect`).
3. **Lange Laufzeiten:** `FRAMES` aus der Audiolänge statt als Konstante; Chunk-Pläne für
   5 000+ Frames.
4. **Post-Hook:** definierter Platz für einen projekteigenen 2D-Pass zwischen Render und
   Encode (heute nur `glow.py` im Beispiel).
5. **Loop-Export** für Stufe A (Crossfade-freier Loop: letzter Frame == erster Frame).

Jede Änderung als eigener PR im Engine-Repo, mit Proof-Render und bestehender CI.

## 8. Rollout

| Phase | Inhalt | Ergebnis |
|---|---|---|
| **P0 — Pilot von Hand** | T02 (*Lass mich, lass mich atmen*), Stufe B, 20 s. Higgsfield-Ablauf direkt nutzen, Album-Konzept als Vorgabe. Zeiten und Reibungen notieren. | Clip + Erfahrungsbericht `Plan/_lessons-learned/140-pilot.md` |
| **P1 — Skills ohne Handler** | `skills/video/*` als Prompt-Skills, Zustand vorerst in `TREATMENT.md`/`BEATS.md` | Kette mit 13 Skills läuft |
| **P2 — Handler + Status-Leiter** | `handlers/video/`, Felder in `update_track_field`, Templates | Tools-Regel gilt auch für Video |
| **P3 — Album** | Stufe A+B für alle 13, Stufe C für T02/T07/T13 | Release-fähiges Video-Paket |
| **P4 — Upstream** | Engine-Änderungen aus §7, soweit P0–P3 sie gebraucht haben | PRs im Engine-Repo |

Vor P2 eine ADR: „Video als siebte Domain“ (Bezug: `Plan/decisions/0004-five-handler-domains.md`).

## 9. Risiken

- **Rechenzeit.** Volle Songs path-traced sind teuer. Gegenmittel: Stufen, 12 fps,
  Plates + 2D-Post, Budget-Gate vor dem Final-Render.
- **Belastung beim Review.** Das Album behandelt sexualisierte Gewalt. Reviews werden
  getaktet (eine Session pro schwerem Track), nichts wird in einem Rutsch abgenommen.
- **Plattformen.** YouTube-Richtlinien zu Suizid/Selbstverletzung/Missbrauch: die
  Darstellungsregeln (Objekt statt Körper) senken das Risiko; CW-Text und ggf.
  Altersfreigabe gehören in `video-release`.
- **Agent kann nicht hören und sieht nur Stichproben.** Wie im Higgsfield-Leitfaden:
  messen, und eine Person schaut vor der Abnahme.

## 10. Offene Entscheidungen

1. Hardware: lokale GPU? Runpod-Konto?
2. Formatprioritäten: Stufe C für drei Tracks oder zuerst A+B für alle?
3. Ob die Video-Skills ins Agency-Plugin gehören (Empfehlung) oder als eigenes Plugin
   neben der Engine leben.
4. Hausschrift (OFL) für Titel, CW-Tafel und Lyrics.
