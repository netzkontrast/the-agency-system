# „Unlicht" (Vertiefung) — Umsetzungsplan

> **Für agentische Worker:** REQUIRED SUB-SKILL: `superpowers:subagent-driven-development` (empfohlen) oder `superpowers:executing-plans`, um diesen Plan Task für Task umzusetzen. Schritte nutzen Checkbox-Syntax (`- [ ]`).

**Goal:** Die bestehende Single „Unlicht" in-place zum Lied eines Lichtwesens vertiefen — recherchiert geerdet, mit veiled-mystischem Tod-als-Liebe-Kern, echten Umlauten überall.

**Architecture:** Sequenzielle Content-Phasen: Research → vollständiges Konzept (Templates) → Lyric-Überarbeitung → Umlaut-/Suno-Cleanup → Review → Commit/PR. Jede Phase mutiert Dateien im Single-Verzeichnis und wird per Grep/Read verifiziert (kein Code/TDD).

**Tech Stack:** bitwize-music-Skills (album-conceptualizer, lyric-writer, suno-engineer, lyric-reviewer, voice-checker), `deep-research`-Harness, Git/GitHub (PR #178). Quelle: `SPEC.md` im selben Verzeichnis.

**Constraints (gelten in JEDEM Task):** echte Umlaute überall (auch Suno-Box) · name_exposure (keine Personennamen) · deskriptive Metatags, keine [Section]-Tags · Würde-Linie (mystisch, nie instruktiv; „noch"-Tether Pflicht) · 4 frei alternierende m/w-Stimmprofile.

**Pfade:**
- Single-Verzeichnis: `artists/children-of-agatha/albums/dark-disco-dream-synth/unlicht/`
- Track: `…/unlicht/Single-unlicht.md` · Spec: `…/unlicht/SPEC.md` · Research (neu): `…/unlicht/RESEARCH.md`
- Branch: `claude/children-agatha-single-EytDs` · PR #178

---

### Task 1: Research R1–R5 → RESEARCH.md

**Files:**
- Create: `artists/children-of-agatha/albums/dark-disco-dream-synth/unlicht/RESEARCH.md`

- [ ] **Step 1: SPEC lesen** — `SPEC.md` §8 (Research-Plan) als verbindliche Cluster-/Anker-Liste.

- [ ] **Step 2: deep-research für R2–R5 fahren (fan-out, zitiert).** Genau diese vier Fragen stellen:
  - R2 Lichtwesen: „Lichtbringer- und 'wounded healer'-Archetyp in Mythologie/Tiefenpsychologie — Bildmotive des Trägers, der vom eigenen Licht verzehrt wird."
  - R3 Orakel: „Pythia/Delphi und der Seher-Archetyp — die Kosten der Schau, prophetische Last, der/die Sehende, der/die fremde Wahrheit trägt."
  - R4 Tod-als-Liebe: „Tod als Geliebte/Erlösung in Mystik & Dichtung — Novalis 'Hymnen an die Nacht', Rilke 'eigener Tod'/Duineser Elegien, Rumi/Sufi-Liebestod, apophatische Mystik. Abgrenzung mystische Todessehnsucht ↔ klinische Suizidalität."
  - R5 Licht-enthält-Dunkel: „C. G. Jung Schatten/enantiodromia; Johannes vom Kreuz 'dunkle Nacht der Seele'; die Idee, dass Überfülle an Licht blendet/zur Last wird."

- [ ] **Step 3: Klinischer Pass R1 (eigene gezielte Recherche).** Anker: Bessel van der Kolk (Körper/Trauma), Janina Fisher (parts work / strukturelle Dissoziation), Elaine Aron (HSP/Hochsensibilität), Viktor Frankl + posttraumatic growth (Rolle des Leid). Ziel: psychisch korrekte Erdung, damit der Stoff nicht romantisiert wird (CoA-Würde).

- [ ] **Step 4: RESEARCH.md schreiben** mit genau diesen Abschnitten (echte Umlaute):
  - Kopf: Zweck (Ton-/Bild-Referenz, **keine** faktischen Claims; `Sources Verified = N/A`).
  - `## R1 — Klinische Erdung` · `## R2 — Lichtwesen` · `## R3 — Orakel` · `## R4 — Tod als Liebe` · `## R5 — Licht enthält Dunkel`.
  - Je Cluster: 3–6 Stichpunkte mit konkreten Bildern/Begriffen + zitierten Quellen (Titel/Autor/Jahr, Link wo möglich).
  - `## Ton-Leitplanken`: 4–6 Sätze, die aus R4/R1 die Würde-Linie ableiten (mystische Erlösungs-Sehnsucht ja, Suizid-Instruktion/Verklärung nein; „noch"-Tether als Pflicht).
  - `## Bild-Lexikon für die Lyrics`: 8–12 konkrete, kitschfreie Bilder (z. B. „Schwelle, die sich nicht schließt", „den Schein für andere halten", „Nacht als Heimat des Lichts" — aus Novalis), die der lyric-writer verwenden darf.

- [ ] **Step 5: Verifizieren.**
  Run: `grep -cE '^## (R[1-5] —|Ton-Leitplanken|Bild-Lexikon)' artists/children-of-agatha/albums/dark-disco-dream-synth/unlicht/RESEARCH.md`
  Expected: `7`
  Run: `grep -ciE 'Novalis|Rilke|Rumi|Jung|Aron|van der Kolk|Fisher|Frankl|Johannes vom Kreuz|Pythia' …/RESEARCH.md`
  Expected: `>= 8` (Anker präsent)

- [ ] **Step 6: Commit.**
```bash
git add artists/children-of-agatha/albums/dark-disco-dream-synth/unlicht/RESEARCH.md
git commit -m "Add RESEARCH.md tone reference for Unlicht (R1-R5)"
```

---

### Task 2: Vollständiges Konzept mit allen bitwize-Track-Templates

**Files:**
- Modify: `artists/children-of-agatha/albums/dark-disco-dream-synth/unlicht/Single-unlicht.md`
- Read: `/root/.claude/plugins/cache/bitwize-music/bitwize-music/0.91.0/templates/` (Track-Template als Sektions-Referenz)

- [ ] **Step 1: Template-Sektionen abgleichen.** Track-Template lesen; sicherstellen, dass `Single-unlicht.md` JEDE Template-Sektion enthält: Frontmatter, Track Details, Concept, Mood & Imagery, Musical Direction, Stimm-Architektur, Suno Inputs (Style Box / Exclude Styles / Suno Settings / Lyrics Box), Streaming Lyrics, Art Direction, Production Notes, Pronunciation Notes, Phonetic Review Checklist, Generation Log. Fehlende ergänzen (per `Edit`, nicht Voll-`Write` — Frontmatter-Hook-Schonung).

- [ ] **Step 2: Concept auf die Lichtwesen-Figur umschreiben** (aus SPEC §3–§6 + RESEARCH-Bild-Lexikon): Lichtwesen/Empath/Orakel; Licht-als-Last; C-PTSD als Ätiologie; Tod-als-Liebe als veiled Kern; „noch"-Tether. Echte Umlaute.

- [ ] **Step 3: Mood & Imagery + Musical Direction** mit dem RESEARCH-Bild-Lexikon anreichern (Schwelle, Nacht-als-Heimat-des-Lichts, der Schein für andere). Tanzbarkeit/BPM/Hooks unverändert.

- [ ] **Step 4: Stimm-Architektur-Tabelle** auf die Mythos-Überlagerung aktualisieren (Maske=performter Schein, Inneres=Gewicht des Lichts, Riss=Schwelle, Das Licht=Orakel/Zeuge) — SPEC §5.

- [ ] **Step 5: Verifizieren.**
  Run: `grep -cE '^## (Concept|Mood & Imagery|Musical Direction|Stimm-Architektur|Suno Inputs|Streaming Lyrics|Art Direction|Production Notes|Pronunciation Notes|Generation Log)' …/Single-unlicht.md`
  Expected: `>= 9` (Suno Inputs ist `##`, Style Box etc. `###`)
  Run: `grep -ciE 'Lichtwesen|Orakel|Empath|Schwelle' …/Single-unlicht.md`
  Expected: `>= 4`

- [ ] **Step 6: Commit.**
```bash
git add artists/children-of-agatha/albums/dark-disco-dream-synth/unlicht/Single-unlicht.md
git commit -m "Rewrite Unlicht concept around the light-being (full templates)"
```

---

### Task 3: Lyric-Überarbeitung (veiled mystischer Kern, echte Umlaute)

**Files:**
- Modify: `…/unlicht/Single-unlicht.md` (Suno Lyrics Box + Streaming Lyrics)

- [ ] **Step 1: lyric-writer-Skill anwenden** mit RESEARCH-Bild-Lexikon + SPEC §4/§7. Beibehalten: Hook „Du siehst mein Licht — ich seh nur Unlicht", 4 Stimmen, Bogen, Tanzbarkeit. Einarbeiten: Licht-als-Last, der neue Gegenpol „Das Licht ist zu schwer, um dich frei zu lassen", die veiled Tod-als-Liebe-Sehnsucht (Novalis-Nacht-Register), „noch"-Tether bleibt.

- [ ] **Step 2: Echte Umlaute in BEIDEN Lyric-Blöcken.** Jede deutsche Zeile mit ä/ö/ü/ß statt ae/oe/ue/ss — auch in der Suno-Box.

- [ ] **Step 3: 13-Punkt-Check** (lyric-writer) auf die neue Fassung; Verstöße fixen. Würde-Linie prüfen: keine instruktive/verklärende Suizid-Aussage; „noch"-Tether vorhanden.

- [ ] **Step 4: Refinement-Log** in der Track-Datei um die Vertiefungs-Änderungen ergänzen.

- [ ] **Step 5: Verifizieren.**
  Run (Suno-Box darf KEINE Konvertierungen mehr enthalten): `grep -cE 'fuer|Laecheln|haelt|spuer|glaenz|Schluessel|Tuer|waer|dringt zu mir' …/Single-unlicht.md`
  Expected: `0` außerhalb des Refinement-Logs — falls >0, prüfen, ob nur „Vorher"-Zitat im Log; sonst fixen.
  Run (Tether vorhanden): `grep -c 'noch' …/Single-unlicht.md`
  Expected: `>= 1`
  Run (name_exposure): `grep -rwniE 'Kael|Nyx|Selene|Lex|Alex|Rhys|Kiko|Lia|Isabelle|Moros|Argus' …/Single-unlicht.md`
  Expected: keine Treffer.

- [ ] **Step 6: Commit.**
```bash
git add artists/children-of-agatha/albums/dark-disco-dream-synth/unlicht/Single-unlicht.md
git commit -m "Revise Unlicht lyrics: veiled mystical core, real umlauts"
```

---

### Task 4: Umlaut-/Suno-Cleanup (Style Box + Settings)

**Files:**
- Modify: `…/unlicht/Single-unlicht.md` (Style Box, Exclude Styles, Suno Settings, Pronunciation Notes)

- [ ] **Step 1: suno-engineer-Skill anwenden.** Style Box bleibt vocals-first, 2 Genre-Tags, avoidance-konform; Suno-Box-Lyrics nutzen jetzt echte Umlaute → Style-Box/Settings konsistent halten.

- [ ] **Step 2: Pronunciation-Table schlanken.** Reine Umlaut-Umschreib-Zeilen (für→fuer etc.) entfernen — gelten nicht mehr (echte Umlaute). Nur echte Risikowörter behalten (z. B. „Unlicht" = Betonungsnotiz UN-licht).

- [ ] **Step 3: Hinweis ergänzen** in Suno Settings: V5.5 mit echten Umlauten; falls Fehlartikulation auftritt, A/B-Generierung gegen konvertierte Variante.

- [ ] **Step 4: Verifizieren.**
  Run: `grep -A3 '### Suno Settings' …/Single-unlicht.md` — enthält Umlaut-Hinweis.
  Run: `grep -c 'ue → \|ä → ae\|ö → oe' …/Single-unlicht.md` (alte Umschreib-Zeilen)
  Expected: `0`

- [ ] **Step 5: Commit.**
```bash
git add artists/children-of-agatha/albums/dark-disco-dream-synth/unlicht/Single-unlicht.md
git commit -m "Cleanup Unlicht Suno inputs for real umlauts; slim pronunciation table"
```

---

### Task 5: Review (lyric-reviewer + voice-checker)

**Files:**
- Modify (nur bei Fixes): `…/unlicht/Single-unlicht.md`

- [ ] **Step 1: lyric-reviewer (14-Punkt)** auf die Track-Datei. Pronunciation-Auto-Fixes anwenden; kritische Issues = 0 sicherstellen.

- [ ] **Step 2: voice-checker (advisory)** für AI-Muster/Authentizität; Warnungen sichten, nur bei echtem Mehrwert anpassen (nicht auto-umschreiben).

- [ ] **Step 3: Würde-Gate manuell** prüfen: Tod-als-Liebe bleibt mystisch/veiled, „noch"-Tether vorhanden, keine instruktive Lesart.

- [ ] **Step 4: Verifizieren.** Review-Report zeigt „Ready for Suno" (0 kritische Issues). Falls Fixes nötig → anwenden, Schritt 1 wiederholen.

- [ ] **Step 5: Commit (falls Fixes).**
```bash
git add artists/children-of-agatha/albums/dark-disco-dream-synth/unlicht/Single-unlicht.md
git commit -m "Apply lyric-reviewer/voice-checker fixes to Unlicht"
```

---

### Task 6: Push & PR-Update

- [ ] **Step 1: Push (mit Retry).**
```bash
git push origin claude/children-agatha-single-EytDs
```

- [ ] **Step 2: PR #178 Beschreibung aktualisieren** (mcp__github__update_pull_request) — Vertiefung, RESEARCH.md, Lichtwesen-Figur, echte Umlaute kurz vermerken.

- [ ] **Step 3: Verifizieren.** `git status` sauber; PR zeigt neue Commits.

---

## Self-Review (Plan gegen Spec)

**Spec-Abdeckung:** §8 Research → Task 1 ✓ · §9.2 volles Konzept/Templates → Task 2 ✓ · §9.3 Lyric-Überarbeitung → Task 3 ✓ · §2/§9.4 echte Umlaute + Suno-Cleanup → Task 3+4 ✓ · §10.5 Review → Task 5 ✓ · §10.6 Commit/PR → Task 1–6 + Task 6 ✓ · Constraints (name_exposure, Metatags, Würde-Linie, 4 Stimmen) → in Tasks 2/3/5 verifiziert ✓.

**Placeholder-Scan:** keine „TBD/TODO"; alle Research-Queries, Umlaut-Listen, Verifikations-Greps und Commit-Messages konkret ausgeschrieben. ✓

**Konsistenz:** Dateipfade und Sektionsnamen identisch über alle Tasks; Verifikations-Greps treffen die in früheren Tasks geschriebenen Marker. ✓
