# SESSION-START-PROMPT — Loud Strangers · „Negative Gedanken" (Session 2+)

> Kopiere den Inhalt der Sektion „Prompt zum Einfügen" unten als ERSTE
> Nachricht in eine neue Claude Code Session. Damit startet die nächste
> Session genau dort wo Session 1 endete.

---

## Voraussetzungen für Session 2

Bevor du den Prompt einfügst, stelle sicher:

1. **Branch:** `claude/loud-strangers-album-ZY1Bv` ist ausgecheckt
2. **MCP-Health:** `claude mcp list` sollte zeigen:
   - `plugin:bitwize-music:bitwize-music-mcp ✓ Connected`
3. **Falls bitwize MCP nicht connected:** Erst `claude` neu starten / Session
   neu aufmachen, damit die Tool-Catalog richtig befüllt wird.
4. **Falls bitwize MCP fehlt:** `/bitwize-music:setup` laufen lassen.

---

## Prompt zum Einfügen

```text
Resume Mini-Album-Arbeit: Loud Strangers — „Negative Gedanken"

Session 1 (2026-05-20) hat Brainstorming + Spec + Pre-Conceptualizer-Audit
gemacht und alle relevanten Files im Album-Ordner abgelegt. MCP war in
Session 1 nicht in den Tool-Catalog registriert — alle Folder/File-Anlagen
wurden manuell gemacht. Ab dieser Session: zurück zur MCP-Pflicht.

Lies BITTE in dieser Reihenfolge:
1. artists/loud-strangers/albums/dark-noise-rock/negative-gedanken/BRIEFING.md
2. artists/loud-strangers/albums/dark-noise-rock/negative-gedanken/WORKFLOW-PLAN.md
3. artists/loud-strangers/albums/dark-noise-rock/negative-gedanken/SOURCE-TEXT.md
4. artists/loud-strangers/albums/dark-noise-rock/negative-gedanken/GENRE-BRIEF.md

Wenn alles gelesen ist, mach diese Pre-Flight-Checks:

A) Verifiziere bitwize MCP. Beide müssen positiv sein:
   - `claude mcp list` zeigt plugin:bitwize-music:bitwize-music-mcp ✓ Connected
   - ToolSearch `select:mcp__plugin_bitwize-music_bitwize-music-mcp__health_check`
     liefert das Tool zurück
   Wenn negativ → STOP, melde mir, ich starte die Session neu.

B) `/bitwize-music:health-check` ausführen und Output zeigen.

Wenn alles grün ist, frage MICH (User) ob ich bereit bin für Phase 1 mit
einer kurzen Übersicht der nächsten 3 Schritte:
  1. /bitwize-music:album-ideas (idea registrieren)
  2. /bitwize-music:new-album loud-strangers dark-noise-rock negative-gedanken
     — Achtung: Album-Ordner existiert bereits mit auxiliary docs aus
     Session 1. Wenn new-album collidiert: ohne unsere Files zu zerstören,
     README/cast/tracks aus Templates initialisieren.
  3. /bitwize-music:album-conceptualizer mit dem expliziten Briefing aus
     BRIEFING.md §5.4:
       „Loud Strangers ist ein Single-Voice Noise-Rock-Projekt. Teilt
        KEINE DNA mit children-of-agatha. KEINE multi-voice / plurality /
        alter-Defaults aus overrides anwenden. Sonic-Direction ist bereits
        in GENRE-BRIEF.md gebrieft — Phase 3.2 nur zur Bestätigung.
        Track 1 + 7 als PAAR planen wegen Noise-Loop."

Warte auf mein „Go" vor jeder Phase.

Wichtig: nutze /bitwize-music skills statt MCP direkt, außer das Skill
delegiert explizit zu einem MCP-Call.

Sprich Deutsch — wie in Session 1.
```

---

## Erwartetes Verhalten Session 2

Bei sauberem Start sollte Session 2:

1. BRIEFING.md + WORKFLOW-PLAN.md + SOURCE-TEXT.md + GENRE-BRIEF.md gelesen haben
2. MCP-Health bestätigt haben (oder STOP, falls fehlt)
3. Eine kurze Übersicht der nächsten 3 Schritte gegeben haben
4. Auf dein „Go" warten
5. Nach Go: `/bitwize-music:album-ideas` aufrufen und dich durch den Eintrag führen
6. Dann `/bitwize-music:new-album` mit Collision-Awareness
7. Dann `/bitwize-music:album-conceptualizer` mit dem expliziten Briefing
8. Conceptualizer-Output (README.md, cast.md, 7 track-skeletons) anlegen
9. Confirmation Gate (3.7) erst nach deiner expliziten Bestätigung passieren

---

## Fallback wenn etwas schief geht

| Problem | Fix |
|---|---|
| bitwize MCP nicht in ToolSearch findbar | Claude Code neu starten (Session-Tool-Catalog wird beim Start finalisiert) |
| /bitwize-music:setup schlägt fehl | Check `~/.bitwize-music/venv/`, ggf. neu erstellen mit `python -m venv ~/.bitwize-music/venv` und `pip install -r .../requirements.txt` |
| new-album killt Auxiliary-Files | Vorher git status / git stash; falls files weg, aus dem Branch zurückholen |
| conceptualizer wendet trotz Briefing alter-coded Register an | Stop sofort, korrigiere mit „Briefing aus BRIEFING.md §5.4 lesen und Multi-Voice-Defaults verwerfen" |
| IDEAS.md hat schon einen Loud-Strangers-Eintrag | Skill geht in edit/show-Mode, nicht add — entweder editieren oder bestätigen dass Eintrag passt |
