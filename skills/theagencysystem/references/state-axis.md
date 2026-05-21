# State axis — S0–S4 (the second dimension of the matrix)

The matrix is `function × state`. This file is the index for the **state**
axis; per-state detail lives in `states/s0.md … s4.md`. States map 1:1 across
all three layers (music / novel / design).

| State | Name | ASDLS tier | Novel Stilebene / Mode | Yellow-type (design) | Lead function(s) |
|---|---|---|---|---|---|
| S0 | Homöostase | T0 | Stilebene 1 / ANP-control | — (System Blue) | host, rationalist |
| S1 | Latenz / Freeze | T1 | Hypoarousal (1→2) | Latency Violet | child_freeze, collapsed |
| S2 | Alert / Konflikt | T2 | Stilebene 2 / KW3 | Signal Yellow | fighter, protector |
| S3 | Kollaps-Peak | T3 | Vortex 1 | Flame / Corrupted | collapsed (peak) |
| S4 | Repair / Integration | T4 | Stilebene 3 + Coda | Kintsugi Gold | integrator, mode_we |

## Per-layer alias of the same state
- **Music:** energy / arrangement / vocal-delivery + mastering loudness tendency.
- **Novel:** Stilebene + Kernwelt class (KW) + syntax register.
- **Design:** ASDLS tier (T0–T4) + signature hex + glitch intensity.

## Orthogonal sub-tags (attach to any cell)
- `conflict_with:[function …]` — which other functions this state pulls into friction.
- `kernwelt_class:[P | paraconsistent | NP-hard | generative]` — novel computational class.
- `yellow_type:<…>` — the design color-thermodynamics band (see `cross-cutting/color-thermodynamics.md`).

## Notes
- ANP = {host, rationalist}; integrator is Meta/ISH; `mode_we` = Wir-Stimme.
- A state is never loaded alone: pair it with the active `entities/<function>.md`
  via `matrix-index.yaml`. S3/S2 conflict cells should also pull
  `cross-cutting/collision-matrix.md`; S4 integration cells pull `entities/_modes/we-voice.md`.
