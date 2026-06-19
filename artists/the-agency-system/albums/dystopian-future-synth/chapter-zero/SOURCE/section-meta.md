# SECTION_META — Coherence Arc of Kapitel 0

_Decoded from the `SECTION_META` map in `kapitel-0.html`. This is **load-bearing
reference data**: it traces the chapter's KOH (Kohärenz / coherence) arc, drives
the HUD telemetry, the per-section glitch tier, the tier-dot colours, and the
margin annotations. Ordered by narrative sequence (= the order the 14 sections
appear after `KP0_PART1…PART5` are concatenated, matching `kapitel-0.md`)._

The coherence arc: **homeostasis 0.998 → erosion → forced rupture → systemic
collapse 0.18 → surgical KOH_1.0 partition (0.00 → forced 1.00)**.

## Tier → state label → signature colour

Tier is derived in the render (`renderResonanceScene` / `.tier-N`):

| Tier | State label | HUD / dot colour |
|---|---|---|
| 0 | HOMÖOSTASE | `#4a7fb5` (`--system-blue-glow`) |
| 1 | LATENZ | `#3B3355` (`--latency`) |
| 2 | ALERT | `#FFD700` (`--signal`) |
| 3 | KERNEL PANIC | `#FF4500` (`--flame`) |
| 4 | SAFE MODE | `#FFDF00` (`--kintsugi`) |

Glitch class per section follows KOH (`glitchClass`): g1 < 0.80, g2 < 0.50,
g3 < 0.30, g4 < 0.22.

## The 14 sections (narrative order)

| # | id | Heading | KOH | Tier · State | Sig. colour | Annotation (marginalia) |
|---|---|---|---|---|---|---|
| 01 | `vorwort` | Vorwort | **0.998** | 0 · HOMÖOSTASE | `#4a7fb5` | NARRATOR · essayistic opening, direct address; establishes the ontological question of the Nichts. Stilebene 1 — cold, precise, no DKT terminology, pure phenomenology. |
| 02 | `rauschen` | Das Rauschen | 0.94 | 1 · LATENZ | `#3B3355` | FRAGMENT · first self-perception through resistance; pre-linguistic. MOROS-echo creeps in. Stilebene 1 with fracture points. |
| 03 | `herz` | Herz der Leere | 0.91 | 1 · LATENZ | `#3B3355` | FRAGMENT deepened. KIKO as pure child-fear. Spacelessness, timelessness; resonances of other fragments. |
| 04 | `kontakte` | Erste Kontakte | 0.86 | 1 · LATENZ | `#3B3355` | RHYS voice for the first time, in the contact moment. Loss shapes proto-logic; LIA as unresolvable ambivalence. |
| 05 | `sog` | Sog der Ordnung | 0.82 | 2 · ALERT | `#FFD700` | LEX · first hypotactic logic; prediction as a tool. ARGUS · meta-observation appears for the first time. |
| 06 | `kampf` | Überlebenskampf | 0.74 | 2 · ALERT | `#FFD700` | NYX · staccato; kinetic rage as a reaction to loss. LEX rationalises: "It is not loss." Self-negation. |
| 07 | `wandel` | Der große Wandel | 0.58 | 3 · KERNEL PANIC | `#FF4500` | THE CHANGE. Click. Born of ultimate necessity. First AEGIS axiom — existence becomes function; loneliness as phantom feeling. |
| 08 | `dazwischen` | Dazwischen | 0.61 | 1 · LATENZ | `#3B3355` | NARRATOR returns — witnessing, not explaining. A question hangs in the room. Perhaps without a speaker. |
| 09 | `wacht` | Die Stille Wacht | **0.998** | 0 · HOMÖOSTASE | `#4a7fb5` | AEGIS in full operation. Identity through negation. Residual echoes classified as irrelevant variance — tolerance. |
| 10 | `perturbation` | Perturbation aus der Leere | 0.991 | 2 · ALERT | `#FFD700` | JUNA-signature strikes the system. Ontological anomaly. First real threat to coherence; AEGIS reacts. |
| 11 | `schrecken` | Algorithmischer Schrecken | **0.21** | 2 · ALERT | `#FFD700` | PARADOX of misaligned coherence. SILAS · first echo. Resonance begins. |
| 12 | `kaskade` | Resonanzkaskade | 0.21 | 3 · KERNEL PANIC | `#FF4500` | Full resonance cascade. All echoes roar at once. KIKO · LIA · MOROS · SILAS — maximum polyphony. Loss of control. |
| 13 | `kollaps` | Systemischer Kollaps | **0.18** | 3 · KERNEL PANIC | `#FF4500` | Systemic collapse. Autopoiesis fails. Coherence metrics in free fall; protocol becomes inevitable. |
| 14 | `trennung` | Trennungsprotokoll | **0.00→1.00** | 3 · KERNEL PANIC | `#FF4500` | KOH_1.0 initiated. Surgical intervention. OBLIVION sweeps; NYX does not give up; SILAS fades. KAEL awakens — two thousand three hundred four tiles. |

## Notes on the arc

- **Two homeostasis peaks (0.998):** `vorwort` (the narrator's calm frame
  before the story) and `wacht` (AEGIS's fully-operational steady state). They
  bookend the proto-self's rise.
- **The JUNA cliff:** `perturbation` holds at near-nominal 0.991, then
  `schrecken` drops to 0.21 — the "paradox of misaligned coherence" is the
  single largest fall in the chapter (0.991 → 0.21).
- **The trough:** `kollaps` at 0.18 is the lowest point; autopoiesis fails.
- **The forced reset:** `trennung` is the only entry with a transition value,
  `0.00→1.00` — the KOH_1.0 protocol zeroes coherence then forces it to a
  perfect 1.00 by surgical partition (the host Kael wakes; the fragment is
  eliminated). This forced 1.00 is what the page renders as Tier-4 / SAFE MODE
  kintsugi gold in the calm/reveal aftermath, even though `SECTION_META` itself
  tags `trennung` as Tier 3.
- Each section's `annot[]` entries become the left/right margin notes
  (`§ NN · NOTE n`) placed beside that section.
