<!--
Sources, top to bottom:
  1. https://github.com/netzkontrast/agency/blob/867453e/skills/the-agency-system-architect/quality_gate_audit.md
  2. https://github.com/netzkontrast/agency/blob/867453e/skills/suno-lyric-writer/documentary-standards.md
Source commit: 867453e
Edit upstream and re-import, or edit here and document the divergence.
-->

# Research / Quality Preferences

## Part 1 — The Agency System 13-point quality audit

*Binary PASS/FAIL audit gates for every track produced under the trilogy. Use these before any track is marked Final.*

# Quality Gate — 13-Punkt-Audit

Referenz für den **Quality Auditor**. Binäre Prüfung. Keine Ermessensspielräume.

---

## Prüfregel

Jeder Punkt wird mit **PASS** oder **FAIL** bewertet. Ergebnis:

- **13× PASS** → Gesamturteil `PASS`, Output geht zum Orchestrator.
- **≥ 1× FAIL** → Gesamturteil `REJECT`, benannte Rolle wird zurückgerufen.

Bei mehrdeutigem Fall: FAIL. Der Audit ist adversariell, nicht wohlwollend.

---

## Die 13 Punkte

### Gruppe A — Narrative Integrität (Architect-Output)

1. **Phase-Klarheit.** Genau eine dominante Phase. Nicht zwei, nicht keine.
2. **Cluster-Klarheit.** Genau ein dominanter Cluster. Schatten-Cluster optional, aber benannt.
3. **Metaphern-Budget.** Genau zwei Leit-Metaphern aus der erlaubten Liste (`narrative_bible.md`).

### Gruppe B — Sprachliche DNA (Lyricist-Output)

4. **Register-Reinheit.** Innerhalb einer Section nur ein Register (Agency ODER Kern). Wechsel nur an Section-Grenzen.
5. **POV-Konsistenz mit Blueprint.** Die in `VOICES (IFS)` benannten Stimmen sprechen — keine, die nicht benannt sind. **Ausnahme:** wenn der Draft einen POV-Shift enthält, der *nicht* im Blueprint steht → **FLAG for USER**, nicht automatisch FAIL (Kern-Invariante 5).
6. **Keine Emotions-Adjektive.** Null Vorkommen von traurig/einsam/verzweifelt/wütend/glücklich/stolz/leer (Liste in `sprachliche_abbildung.md`).
7. **Keine Lexikon-Ausschlüsse.** Null Vorkommen der Verbotsliste (Pop-Liebes-Vokabular, generische Schatten-Tropen, freie Religion, Diminutive).
8. **Prosodie-Symmetrie.** Parallele Verses haben Silbenzahl ±1. `scripts/validate_prosody.py` liefert Zahlen.
9. **Reimschema konstant pro Section.** AABB oder ABAB innerhalb einer Section nicht gemischt.

### Gruppe C — Sonische DNA (Engineer-Output)

10. **Style Prompt ≤ 110 Zeichen.** Harte Grenze.
11. **Control by Reduction.** Genau 1 Primärgenre + 1 Supporting-Texture + 1 Signature im Style Prompt. Zählbar.
12. **120-BPM-Deklaration.** Das Grid ist entweder im Style Prompt oder im `[Intro]`-Tag explizit benannt. Bei Abweichung: alternatives BPM explizit.
13. **Projekt-Tag-Budget.** Maximal 3 Agency-spezifische Tags aus `suno_prompt_engineering.md`. Standard-Suno-Tags unbegrenzt.

---

## Report-Format des Auditors

```
AUDIT REPORT — Track: <name>
Phase×Cluster: <X × Y>

Group A (Narrative)   — 1:[✓/✗]  2:[✓/✗]  3:[✓/✗]
Group B (Sprache)     — 4:[✓/✗]  5:[✓/✗/FLAG]  6:[✓/✗]  7:[✓/✗]  8:[✓/✗]  9:[✓/✗]
Group C (Sonik)       — 10:[✓/✗] 11:[✓/✗] 12:[✓/✗] 13:[✓/✗]

VERDICT: PASS | REJECT
Return to: <Architect | Lyricist | Engineer | USER for FLAG>
Violations: <präzise Benennung mit Section-Referenz>
```

---

## Beispiele

### Beispiel 1 — REJECT auf Punkt 6

```
Violation: Punkt 6 — "Emotions-Adjektiv" in [Chorus] Zeile 2:
  "Ich bin so einsam im Firewall-Schatten."
→ Return to Lyricist.
→ Hinweis: Ersetze "einsam" durch objective correlative
  (z.B. Zustand des Firewalls selbst).
```

### Beispiel 2 — FLAG auf Punkt 5

```
Status: Punkt 5 — FLAG (nicht FAIL).
Blueprint benennt VOICES = "Core (Manager)".
[Bridge] Zeile 3 enthält 1. Sg. in Exile-Duktus
  ("Leiser. Ich halte nur noch den Namen.").
→ Question to USER: War der POV-Shift in die
  Exile-Stimme beabsichtigt? Wenn ja, Blueprint nachträglich
  erweitern. Wenn nein, Lyricist korrigieren.
```

### Beispiel 3 — REJECT auf Punkt 11

```
Violation: Punkt 11 — Style Prompt enthält 4 Genres:
  "industrial darkwave, minimal techno, dark ambient,
   post-rock, clinical mood, sub-bass, FM arps, baritone"
→ Return to Engineer.
→ Hinweis: Reduziere auf 1 Primär + 1 Support + 1 Signature.
```

---

## Eskalation

Bei **3 aufeinanderfolgenden REJECTs** am selben Track:

1. Auditor gibt `ESCALATE` zurück.
2. Orchestrator pausiert die DAG.
3. Strukturierter Problem-Report an den User:
   - Track-Name, Phase×Cluster
   - Welche Punkte in jedem Durchlauf versagt haben
   - Hypothese: liegt die Blockade im Blueprint, der sprachlichen Umsetzung oder der sonischen Übersetzung?
   - Vorschlag: Blueprint überdenken oder Invariante temporär lockern (User-Entscheidung).

---

## Part 2 — Documentary research standards

*Source/citation standards for lyrics referencing real people or events. Adapted from suno-lyric-writer.*


# Documentary & True Crime Legal Standards

Legal guidelines for writing lyrics about real people and events.

---

## When to Apply

Apply these standards for:
- True crime albums (criminal cases, trials, investigations)
- Documentary storytelling (real events, real people)
- Biographical work (real people's lives)
- Historical narratives (factual events)
- Any work citing real sources

---

## The Five Rules

1. **No impersonation** — Third-person narrator only, never speak AS the person
2. **No fabricated quotes** — Never put words in quotes unless documented in sources
3. **No internal state claims** — Never claim to know what someone thought, felt, or believed
4. **No speculative actions** — Stick to documented events only
5. **No negative factual claims** — Don't claim "nobody saw" or "nobody heard" (can't prove negatives)

---

## What to AVOID (High Risk)

### Internal State Claims
- ❌ "She was afraid" / "He felt angry" / "She believed him"
- ❌ "He knew it was wrong" / "Living in fear" / "Tried to disappear"

### Fabricated Quotes
- ❌ "I need help," she cried
- ❌ Direct speech without documented source

### Speculative Actions
- ❌ "She finally made the call" (unless documented HOW)
- ❌ "Goes to sleep that night" (private undocumented action)

### Negative Factual Claims
- ❌ "Nobody heard her scream" / "No one knew the truth"

---

## Safe Alternatives

### Pattern-Based Language
- ✅ "The pattern started" / "The cycle repeated"
- ✅ "Years of documented abuse"

### Observable Behavior
- ✅ "She called 911" (documented action)
- ✅ "Court records show" / "Testimony revealed"

### Documented Medical/Psychiatric States
- ✅ "Brief reactive psychosis" (if diagnosed)
- ✅ "Testimony says she lost her mind" (attributed)

### Narrator Description vs. Internal Claims
- ✅ "She asked for protection" → ❌ "She felt desperate"
- ✅ "Four years of violence" → ❌ "Four years of hiding"

---

## Before/After Examples

| Bad (risky) | Good (safe) |
|-------------|-------------|
| "She was living in dread" | "Years of documented abuse, the pattern escalating" |
| "'I need protection,' she begged" | "She asked for protection, asked to get away" |
| "She finally made the call, hiding in the bathroom" | "She reached out for help, contacted the authorities" |
| "Nobody heard her scream" | "The walls kept her screams in, the world couldn't see within" |

---

## The Standard

For EVERY line, ask:
1. Can I cite this to a specific source?
2. Am I claiming internal knowledge I can't have?
3. Am I inventing quotes?
4. Am I speculating about undocumented actions?
5. Am I making negative claims I can't prove?

**If any answer is problematic, rewrite the line.**

If you can't cite it, don't write it. If you can't prove it, don't claim it. If it's internal, don't assume it.
