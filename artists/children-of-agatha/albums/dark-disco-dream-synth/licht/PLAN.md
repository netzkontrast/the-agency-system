# „Licht" (Schwester-Single) — Umsetzungsplan

> **Spiegel-Plan zu Unlicht.** Gleiche Struktur, thematisch invertiert. Research bereits erledigt; alle folgenden Tasks autonom.

**Goal:** Spiegel-Single zu „Unlicht" — gleicher Künstler-Kosmos, gleiches Crossover, gleiches Genre, gleiche 4 Stimmprofile; thematisch invertiert (das Dunkel enthält das Licht; das Leben als schwerere Liebe; das *zweite* Ja nach Kierkegaard).

**Architecture:** Sequenzielle Content-Phasen analog Unlicht: Research (✓) → volles Konzept → Lyrics → Suno-Cleanup → Review → Commit/PR. Jede Phase im Single-Verzeichnis `licht/`, Verifikation per Grep/Read.

**Tech Stack:** bitwize-music-Skills (album-conceptualizer/lyric-writer/suno-engineer/lyric-reviewer/voice-checker), Git/GitHub. Quelle: `SPEC.md` und `RESEARCH.md` im selben Verzeichnis.

**Constraints (gelten in JEDEM Task):** echte Umlaute überall · name_exposure · deskriptive Metatags, keine [Section]-Tags · Würde-Linie (das zweite Ja, niemals naiv) · **Inversions-Regel: Lichts Bejahung steht *neben* Unlichts Wunde, niemals darüber** · 4 frei alternierende m/w-Stimmprofile.

**Pfade:**
- Single-Verzeichnis: `artists/children-of-agatha/albums/dark-disco-dream-synth/licht/`
- Track (neu): `…/licht/Single-licht.md` · Spec: `…/licht/SPEC.md` · Research: `…/licht/RESEARCH.md`
- Schwester: `../unlicht/Single-unlicht.md`
- Branch: `claude/children-agatha-single-EytDs` · PR #178

---

### Task 1: Research (bereits erledigt)

- [x] `licht/RESEARCH.md` geschrieben (36 Zitate, P1–P5, Ton-Leitplanken, Bild-Lexikon). ✓

---

### Task 2: Vollständiges Konzept (Single-licht.md) mit allen Templates

**Files:**
- Create: `artists/children-of-agatha/albums/dark-disco-dream-synth/licht/Single-licht.md`

- [ ] **Step 1: Template-Sektionen abdecken** — Frontmatter (status: In Progress), Track Details, Concept, Stimm-Architektur, Mood & Imagery, Musical Direction, Suno Inputs (Style Box / Exclude / Settings / Lyrics Box), Streaming Lyrics, Art Direction, Production Notes, Pronunciation Notes, Phonetic Review Checklist, Generation Log. Plus **Cross-References zu Unlicht** (gleiche Sektion).

- [ ] **Step 2: Concept aus SPEC §3–§4 + RESEARCH P1–P5 schreiben.** Lichtwesen nach Durchquerung des Abgrunds; Inversions-Mechanismus; das *zweite* Ja; Würde-Linie; Inversions-Regel verbindlich.

- [ ] **Step 3: Stimm-Architektur-Tabelle** mit der gespiegelten Mythos-Spalte (Maske=das gesehene Licht, Inneres=Abgrund als Boden, Riss=zurück-lassende Schwelle, Das-Licht=Wendung). 4 Stimmen identisch wie Unlicht.

- [ ] **Step 4: Mood & Imagery aus Bild-Lexikon** — Abgrund-als-Boden, das Dunkle das hält, der Stein-der-dich-ansieht (Rilkes Torso), die stille Wüste (Eckhart), Haus/Brücke/Brunnen/Tor (Rilke 9. Elegie), unbesiegbarer Sommer (Camus).

- [ ] **Step 5: Musical Direction** — gleiche Sonic Palette wie Unlicht (Dark Disco Dream Synth, ~120 BPM, Dream-Pads, Reese-Sub), aber **Drop-Funktion gespiegelt**: Wendungs-Drops statt Down-Drops; das *Ankommen* statt Verlierens; Outro mit Dur-Mode-Tendenz / aufgehelltem Arpeggio.

- [ ] **Step 6: Verifizieren.**
  Run: `grep -cE '^## (Track Details|Concept|Cross-References|Stimm-Architektur|Mood & Imagery|Musical Direction|Suno Inputs|Streaming Lyrics|Art Direction|Production Notes|Pronunciation Notes|Generation Log)' …/Single-licht.md`
  Expected: `>= 10`
  Run: `grep -ciE 'Inversion|Abgrund|zweite[s]? Ja|Wendung' …/Single-licht.md`
  Expected: `>= 4`

- [ ] **Step 7: Commit.**
```bash
git add artists/children-of-agatha/albums/dark-disco-dream-synth/licht/Single-licht.md
git commit -m "Add Licht single concept (sister of Unlicht, full templates)"
```

---

### Task 3: Lyrics (lyric-writer-Pass mit Inversions-Hook)

**Files:**
- Modify: `…/licht/Single-licht.md` (Suno Lyrics Box + Streaming Lyrics)

- [ ] **Step 1: Inversions-Hook + Gegenpol-Zeile aus SPEC §4 setzen:**
  - Haupt-Hook: **„Du sagst, du siehst kein Licht — ich seh, du *bist* es."**
  - Gegenpol/Breakdown: **„Der Abgrund ist der Boden, der mich hält."**

- [ ] **Step 2: Lyrics in 4 Stimmen schreiben.** Affekt-Differenz zu Unlicht: das Lichtwesen spricht jetzt aus dem Boden, nicht aus dem performten Schein. Bild-Lexikon nutzen (zweites Ja, Wunde-als-Tür, Funke, Haus/Brücke/Brunnen/Tor, unbesiegbarer Sommer). Echte Umlaute in BEIDEN Lyric-Blöcken.

- [ ] **Step 3: Würde-Gate manuell:** Bejahung als *Wahl*, niemals als „Sei dankbar"; Unlichts Schwere bleibt sichtbar (mindestens 1 Zeile, die das Wissen aus Unlicht honoriert, z. B. eine versteckte Anspielung auf „Schwelle"/„noch"/„Unlicht").

- [ ] **Step 4: 13-Punkt-Check** (lyric-writer-Logik). Fixe Verstöße. Verse→Chorus-Echo prüfen.

- [ ] **Step 5: Verifizieren.**
  Run (Inversions-Hook in beiden Blöcken): `grep -c "du bist es" …/Single-licht.md`
  Expected: `>= 2`
  Run (Gegenpol-Zeile): `grep -c "Abgrund ist der Boden" …/Single-licht.md`
  Expected: `>= 2`
  Run (echte Umlaute Marker): `grep -cE 'ä|ö|ü|ß' …/Single-licht.md`
  Expected: `>= 10`
  Run (keine alten Umlaut-Konversionen): `grep -cE '\b(fuer|haelt|spuer|ueber|waer|haende|laecheln)\b' …/Single-licht.md`
  Expected: `0`
  Run (Unlicht-Verbindung): `grep -c "Unlicht\|Schwelle\|noch" …/Single-licht.md`
  Expected: `>= 1`
  Run (name_exposure): `grep -rwniE 'Kael|Nyx|Selene|Lex|Alex|Rhys|Kiko|Lia|Isabelle|Moros|Argus' …/Single-licht.md`
  Expected: keine Treffer.

- [ ] **Step 6: Commit.**
```bash
git add artists/children-of-agatha/albums/dark-disco-dream-synth/licht/Single-licht.md
git commit -m "Add Licht lyrics: inversion hook, second yes, real umlauts"
```

---

### Task 4: Suno-Inputs (suno-engineer)

**Files:**
- Modify: `…/licht/Single-licht.md`

- [ ] **Step 1: Style Box** analog Unlicht (vocals-first, 2 Genre-Tags, ~120 BPM, Dark Disco Dream Synth) — aber Affekt-Bezeichner gespiegelt: „danceable affirmation from inside the abyss", „mystical staying", „brighter pad bloom toward the outro".

- [ ] **Step 2: Exclude Styles** — analog Unlicht-Set (no autotune, no retro outrun synthwave, no happy major-key eurodance, no Schlager). Bewusst KEIN „no sad" oder ähnliches, das die Inversion banalisieren würde.

- [ ] **Step 3: Suno Settings** — V5/V5.5, Instrumental Off, Weirdness ~35, Style Influence ~75, Target 5:00–7:00, echte Umlaute, Surface-Tags wie Unlicht (darkwave / nu-disco / dark synth-pop / italo-disco).

- [ ] **Step 4: Pronunciation Notes** — schlank: nur Risikowörter („Licht" Betonungsnotiz, „Abgrund"). Echte Umlaute überall.

- [ ] **Step 5: Verifizieren.**
  Run: `grep -A2 '### Style Box' …/Single-licht.md` — vocals-first und Affekt-Inversion sichtbar.
  Run: `grep -A2 '### Suno Settings' …/Single-licht.md` — Echte-Umlaute-Hinweis vorhanden.

- [ ] **Step 6: Commit.**
```bash
git add artists/children-of-agatha/albums/dark-disco-dream-synth/licht/Single-licht.md
git commit -m "Add Licht Suno inputs (mirror of Unlicht, inverted affect)"
```

---

### Task 5: Review (lyric-reviewer + voice-checker + Inversions-Gate)

**Files:**
- Modify (nur bei Fixes): `…/licht/Single-licht.md`

- [ ] **Step 1: lyric-reviewer-Logik (14-Punkt)** — manuell durchgehen. Pronunciation-Fixes anwenden. Kritische Issues = 0 sicherstellen.

- [ ] **Step 2: voice-checker-Logik (advisory)** — AI-Pattern-Check, besonders auf „Sei dankbar"/Klischee-Eskalation achten.

- [ ] **Step 3: Inversions-Gate manuell** — Bejahung steht *neben* Unlichts Wunde (nicht darüber); zweites Ja erkennbar; Würde-Linie gewahrt; Cross-Reference zu Unlicht vorhanden.

- [ ] **Step 4: Verifizieren.** Track-Datei strukturell vollständig; alle Hard-Constraints aus SPEC §7 erfüllt.

- [ ] **Step 5: Commit (falls Fixes).**
```bash
git add artists/children-of-agatha/albums/dark-disco-dream-synth/licht/Single-licht.md
git commit -m "Apply review fixes to Licht"
```

---

### Task 6: Push & PR-Update (final, beide Singles)

- [ ] **Step 1: Push (mit Retry).**
```bash
git push origin claude/children-agatha-single-EytDs
```

- [ ] **Step 2: PR #178 Beschreibung aktualisieren** — beide Singles (Unlicht vertieft + Licht als Spiegel) erwähnen, RESEARCH-Anker, Inversions-Architektur.

- [ ] **Step 3: Verifizieren.** PR zeigt alle neuen Commits; Branch sauber.

---

## Self-Review (Plan gegen Spec)

**Spec-Abdeckung:** §8 Research → Task 1 ✓ · §9.2 volles Konzept → Task 2 ✓ · §9.3 Lyrics → Task 3 ✓ · §9.4 Suno → Task 4 ✓ · §10.5 Review → Task 5 ✓ · §10.6 Commit/PR → Task 1–6 ✓ · Constraints (Inversions-Regel, Würde-Linie, name_exposure) → in Tasks 2/3/5 verifiziert ✓.

**Placeholder-Scan:** keine TBD/TODO; alle Greps und Commit-Messages konkret. ✓

**Konsistenz:** Pfade/Sektionsnamen über alle Tasks identisch. ✓
