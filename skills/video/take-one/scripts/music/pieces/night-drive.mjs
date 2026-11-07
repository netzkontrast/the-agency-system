// "Night Drive", a 120 bpm half-time lofi groove loop, 8 bars of 4/4 = exactly 16.000 s.
// Original composition for the take-one code music engine (engine adapted from anidoodle,
// Apache-2.0). A seamless loop: plan.loop is set, so renderLoop folds the reverb/delay tail back
// onto bar 1 and the CLI renders it loop-ready. The last bar ends on E (the v), not a cadence,
// so the loop pulls back to Am forever.
//
//   chords, one per bar, twice around:  Am9  Fmaj9  Cmaj9  Em7
//   drums: half-time (snare on 3), swung eighth hats, kick ducks the pad and keys (the pump)
//   voices: warm detuned-saw pad (rootless voicings), soft pluck lead through a dotted-eighth
//           ping-pong delay, FM e-piano offbeat stabs, sine sub on the roots, vinyl crackle
import { line } from "../plan.mjs";

const BPB = 4;
const L = (t, s, role, v = 0.7, extra = {}) => line(t, s, { role, v, bpb: BPB, ...extra });
const BPM = 120, BARS = 8, DOTTED_EIGHTH = (60 / BPM) * 0.75;

// one part written a bar at a time: fn(bar, chord index 0..3) -> notation or null
const byBar = (role, v, fn, extra = {}) => {
  const out = [];
  for (let b = 0; b < BARS; b++) { const s = fn(b, b % 4); if (s) out.push(...L(b * 4, s, role, v, extra)); }
  return out;
};

const PAD = ["[E3 A3 C4 E4]", "[A3 C4 E4 G4]", "[E3 G3 B3 D4]", "[G3 B3 D4 E4]"]; // Am, Fmaj9 (rootless), Cmaj9, Em7
const SUB = ["A1:3 r:.5 E2:.5", "F1:3 r:.5 C2:.5", "C2:3 r:.5 G1:.5", "E2:3 r:.5 E1:.5"];
const STAB = ["r:1.5 [C4 E4 A4]:1 r:1.5", "r:2.5 [C4 E4 G4]:1 r:.5", "r:1.5 [D4 E4 G4]:1 r:1.5", "r:2.5 [B3 D4 G4]:1 r:.5"];
const LEAD = [
  null, //                                              1  the pad establishes
  "r:2.5 E5:.5 G5:.5 A5:.5", //                         2  pickup run
  "B5:1.5 A5:.5 G5:.5 E5:1 r:.5", //                    3  the hook, high
  "G5:.5 E5:.5 D5:1 E5:1.5 r:.5", //                    4
  "r:.5 A4:.5 C5:.5 E5:1 D5:.5 C5:1", //                5  the answer, low
  "A4:1 C5:.5 A4:.5 G4:2", //                           6
  "r:.5 E5:.5 G5:.5 B5:1 A5:.5 G5:1", //                7  hook variant
  "E5:1 D5:.5 B4:.5 D5:1 A4:1", //                      8  ends hanging on the 11th: the loop pulls home
];

export default () => {
  const pad = byBar("accomp", 0.6, (b, c) => `${PAD[c]}:4`, { roll: 0.025 });
  const keys = byBar("inner", 0.62, (b, c) => (b === 0 ? null : STAB[c]), { roll: 0.02 });
  const lead = byBar("melody", 0.72, (b) => LEAD[b]);
  const subL = byBar("bass", 0.8, (b, c) => (b === 7 ? "E2:2 D2:1 E2:1" : SUB[c]));
  const kick = byBar("drum", 0.85, (b) => (b % 2 ? "C4:1 r:1.5 C4:.5@.7 r:.5 C4:.5@.85" : "C4:1 r:1.75 C4:1.25@.8"));
  const snare = byBar("drum", 0.7, () => "r:2 C4:2");
  const ghost = byBar("drum", 0.5, (b) => (b % 2 ? "r:3.75 C4:.25@.5" : null));
  const hats = byBar("drum", 0.5, () => "C4:.5@.85 C4:.5@.4 C4:.5@.65 C4:.5@.4 C4:.5@.85 C4:.5@.4 C4:.5@.65 C4:.5@.45");
  const crackle = [{ t: 0, d: BARS * 4, p: 60, v: 0.5, role: "color" }];
  const harmony = Array.from({ length: BARS }, (_, b) => ({ t: b * 4, name: ["Am9", "Fmaj9", "Cmaj9", "Em7"][b % 4] }));
  return {
    title: "Night Drive (lofi loop, 120)", seed: 3117, tail: 2.4, harmony,
    plan: {
      style: "lofi", tempo: BPM, meter: "4/4", swing: 0.57, loop: true, phraseBars: 4,
      sections: [{ id: "loop", bars: BARS, mood: "nostalgic", key: "A", mode: "aeolian", melody: ["hook"], dyn: [0.6, 0.66], repeatable: true }],
    },
    parts: [
      { id: "pad", inst: "warmPad", role: "accomp", notes: pad, gainDb: -4, opts: { cut: 2100, attack: 0.4, release: 1.2, spread: 0.7 }, send: 0.35 },
      { id: "keys", inst: "ePiano", role: "inner", notes: keys, gainDb: 0, opts: { width: 0.4 }, send: 0.3 },
      { id: "lead", inst: "softPluck", role: "melody", notes: lead, gainDb: 4, opts: { decay: 0.45, bright: 5400, delay: DOTTED_EIGHTH, feedback: 0.28, delayMix: 0.26 }, send: 0.25 },
      { id: "sub", inst: "sub", role: "bass", notes: subL, gainDb: -7, opts: { cut: 150 } },
      { id: "kick", inst: "kick", role: "drum", notes: kick, gainDb: 0.5, send: 0.08 },
      { id: "snare", inst: "snare", role: "drum", notes: snare, gainDb: 6, send: 0.3 },
      { id: "ghost", inst: "snare", role: "drum", notes: ghost, opts: { rim: true }, gainDb: 3, send: 0.2 },
      { id: "hat", inst: "hat", role: "drum", notes: hats, opts: { pan: 0.25 }, gainDb: 18, send: 0.1 },
      { id: "vinyl", inst: "vinyl", role: "color", notes: crackle, gainDb: -10 },
    ],
    fx: { duck: { by: "kick", parts: ["pad", "keys"], depth: 0.35, release: 0.24 }, tape: { wowCents: 5, wowHz: 0.375, flutterCents: 1.2, flutterHz: 6, drive: 1.15 } },
    stemTargets: { kick: -14, snare: -21, hat: -28, sub: -18, pad: -21, lead: -17, keys: -23 },
  };
};
