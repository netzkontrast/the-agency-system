# Loop Navigation Map — Chapter Zero

Shared briefing for every agent in the design loop (Design Agent, Fidelity
Critic, Feasibility Critic, Arbiter). Read this **first** so you adjudicate from
exact lines instead of grepping, and so you never confuse the section numbering
with the track numbering.

All paths are relative to the album root:
`artists/the-agency-system/albums/dystopian-future-synth/chapter-zero/`

---

## Ground-truth hierarchy (who wins a dispute)

1. **KOH value / tier / state / which-voice-first-appears** → `SOURCE/section-meta.md` — **WINS.**
2. **Verbatim prose / exact lines / what is or isn't said** → `SOURCE/kapitel-0.md`.
3. **Design law** (palette, 5%-rule, tiers, glitch grammar, prompt syntax) → `SOURCE/ASDLS.md`.
4. **Voice texture / idiolect** → `SOURCE/Sprachdns.md`.
5. **Code ↔ function ↔ name** → `SOURCE/cast.md` (+ `skills/theagencysystem/references/resolver.yaml`).

**Do NOT read `SOURCE/kapitel-0.html` (≈1 MB raw).** Everything you need is in the decoded `.md` files.

---

## The artifact under review — `DESIGN.md` (album root)

Read **§0 Revision log first** on any round after v1 — it maps each prior
critique item → what changed and where, so you verify deltas instead of
re-deriving the whole design. Sections:

- §0 Revision log (v(n-1) → v(n))
- §1 Concept & Logline
- §2 Source-Fidelity Map (the section→track table)
- §3 Tracklist (per-track table)
- §4 Sonic Direction (KOH spine, ASDLS→sonic gestures, per-voice fingerprints)
- §5 Voice Treatment
- §6 Album-Art / ASDLS Visual Direction
- §7 Source-Mapping Appendix — **INTERNAL ONLY** (personal names live here and ONLY here)
- §8 Production Plan (post shot-list, Persona plan, pronunciation/bracket plan, etc.)

---

## section ↔ track crosswalk (numbering differs!)

`section-meta.md` numbers **14 sections**; the album folds 2 narrator
connectives into intros → **13 tracks**. When you cite a KOH/tier, name **both**
the section id and the track #.

| §  | section id   | → Track |
|----|--------------|---------|
| 01 | `vorwort`    | T1 (intro) |
| 02 | `rauschen`   | T1 |
| 03 | `herz`       | T2 |
| 04 | `kontakte`   | T3 |
| 05 | `sog`        | T4 |
| 06 | `kampf`      | T5 |
| 07 | `wandel`     | T6 |
| 08 | `dazwischen` | T7 (intro) |
| 09 | `wacht`      | T7 |
| 10 | `perturbation` | T8 |
| 11 | `schrecken`  | T9 |
| 12 | `kaskade`    | T10 |
| 13 | `kollaps`    | T11 |
| 14 | `trennung`   | T12 (partition) + T13 (coda / host wakes) |

---

## `SOURCE/section-meta.md` — THE ARC GROUND TRUTH

- L16–22 tier → state → HUD colour key.
- L29–44 the 14 sections in narrative order (`# · id · Heading · KOH · Tier·State · colour · annotation`). Exact rows:

| line | id | KOH | Tier · State | annotation gist |
|---|---|---|---|---|
| L31 | vorwort | 0.998 | 0 · HOMÖOSTASE | narrator essay; the Nichts |
| L32 | rauschen | 0.94 | 1 · LATENZ | first self-perception; **MOROS-echo creeps in**, Stilebene 1 w/ fracture points |
| L33 | herz | 0.91 | 1 · LATENZ | KIKO pure child-fear |
| L34 | kontakte | 0.86 | 1 · LATENZ | **RHYS first; LIA ambivalence — NO Lex here** |
| L35 | sog | 0.82 | **2 · ALERT** | **LEX first hypotactic logic; ARGUS meta-observation first appears** |
| L36 | kampf | 0.74 | 2 · ALERT | NYX staccato; LEX "It is not loss" |
| L37 | wandel | 0.58 | **3 · KERNEL PANIC** | THE CHANGE / Click; first AEGIS axiom |
| L38 | dazwischen | 0.61 | 1 · LATENZ | narrator returns; a question hangs |
| L39 | wacht | 0.998 | 0 · HOMÖOSTASE | AEGIS full op; residual echoes = irrelevant variance |
| L40 | perturbation | 0.991 | 2 · ALERT | JUNA-signature strikes; first real threat |
| L41 | schrecken | **0.21** | **2 · ALERT** | PARADOX of misaligned coherence; **SILAS first echo** |
| L42 | kaskade | 0.21 | **3 · KERNEL PANIC** | all echoes roar; KIKO·LIA·MOROS·SILAS max polyphony |
| L43 | kollaps | 0.18 | 3 · KERNEL PANIC | autopoiesis fails |
| L44 | trennung | 0.00→1.00 | 3 · KERNEL PANIC | KOH_1.0; OBLIVION sweeps; NYX refuses; SILAS fades; KAEL wakes (2,304 tiles) |

**Precision note (load-bearing):** Track 9 (`schrecken`, L41) is **S2 / Tier 2 / ALERT at KOH 0.21** — *not* "S2→S3". The KOH crashes to 0.21 but the telemetry tier stays ALERT; Tier 3 / KERNEL PANIC only begins at Track 10 (`kaskade`, L42). The system is still in hyperarousal/fighting during the turn-inward and only tips into collapse at the cascade.

---

## `SOURCE/kapitel-0.md` — decoded prose (find verbatim lines here)

Section heading → line: L6 Vorwort · L28 Das Rauschen · L36 Herz der Leere ·
L50 Erste Kontakte · L76 Sog der Ordnung · L90 Überlebenskampf ·
L106 Der große Wandel · L146 Dazwischen · L160 Die Stille Wacht ·
L185 Perturbation aus der Leere · L207 Algorithmischer Schrecken ·
L244 Resonanzkaskade · L270 Systemischer Kollaps · L292 Trennungsprotokoll.

Verbatim anchors to cite:
- **Founding axiom** → §Der große Wandel (L106–145): *"Es ist, was es verhindert, dass es nicht ist."* Also here: the **2nd movement** (Wendung nach innen / Binnen-Physik / "the tool that simulates worlds could become a world").
- **Denial + prediction-failure** → §Überlebenskampf (L90–105): *"Dies ist nicht Verlust, sondern Strukturoptimierung. Es ist nicht Verlust. Es ist nicht. Verlust."* + *"Sektor zwei-acht-null erwartet, kam bei sechs-neun-zwei"* + sixteen bindings removed.
- **Moros echo** → §Das Rauschen (L28–35): *"Es ist sinnlos. Es war immer schon sinnlos…"*; full return §Resonanzkaskade (L244–269).
- **Coda** → §Trennungsprotokoll (L292+): *"Zweitausenddreihundertvier Kacheln. Einundzwanzig Grad. … Der Korridor ist leer. Ich bin pünktlich."*

---

## `SOURCE/Sprachdns.md` — voice DNA (headings use NAMES → internal; map via cast.md)

Pull §4 fingerprint texture from the right block:
L13 Narrator · L25 AEGIS (=the system/the watch) · L49 Erasure-Pol (≈the sweep) ·
L61 Juna (=the signal) · L73 Kael (=host) · L85 Lex (=logic-voice) ·
L109 Rhys (=warm-voice) · L133 Argus (=annotating/witness) · L145 Nyx (=kinetic) ·
L157 Kiko (=small-voice) · L169 Lia (=reaching) · L193 Moros (=heavy-voice) ·
L205 Silas (=mirror-echo) · L217 Oblivion (=sweep-voice).
**ABSENT in Ch.0 — do not introduce:** Alex/protector L97, Selene/integrator L121,
Isabelle/sexualized L181, We-Voice L229.

---

## `SOURCE/ASDLS.md` — design law (for §6)

§2 palette + 5%-rule + chromatic grammar L34–75 · §3 materiality/glitch-as-clinical L76–106 ·
§4 symbol vocabulary L107–148 · §5 composition + camera-lens prompting L149–174 ·
**§6 the Tier 0–4 state machine** — T0 L179, T1 L186, T2 L193, T3 L200, T4 L207 ·
§7 SPECD prompt formula + keyword library + Tier-2 example L214–265 · §8 master checklist L266+.

## `SOURCE/masterkonzept.md` — analog visual grammar (German; §4 = 13 per-alter grammars, NAMED → internal)

§2 glitch-as-somatic-symptom table L15 · §3 colour thermodynamics L30 ·
§4 per-alter L40–186 (Kael L44, Lex L55, Alex L66, Rhys L77, Selene L88, Nyx L99,
Kiko L110, Lia L121, Isabelle L132, Moros L143, Argus L154, Silas L165, Oblivion L176) ·
§5 composition rules L187 · §6 master synthesis L198.

## `SOURCE/asdls-design.md` — CSS-derived (L49 coherence→tier→colour; L133 voice-block styling).
## `SOURCE/dynamics.md` — behaviours (L21 boot/KOH-ignition; L95 glitch state machine; L127 kintsugi shatter — **Ch.0 has NO kintsugi**, mechanism only).
## `SOURCE/cast.md` — code↔function↔name table L18–30; verbatim fingerprints L34–92.

---

## HARD RULE — name_exposure

Music + design outputs (lyrics, Suno metatags, Style Boxes, promo, art prompts)
use **function/role only**. Personal names — Kael, Nyx, Lex, Rhys, Kiko, Lia,
Moros, Argus, Silas, Juna, AEGIS, Oblivion — appear **ONLY** in `DESIGN.md §7`
(internal) and in these SOURCE files. A name leaking into any public/output
field is a **CRITICAL** defect.

---

## Loop archive convention

Each round's agent outputs are committed under `SOURCE/loop<n>/`:
`design.md` (the DESIGN.md state that round), `fidelity.md`, `feasibility.md`,
and (if used) `arbiter.md`. The living working copy of the design stays at the
album root as `DESIGN.md`.
