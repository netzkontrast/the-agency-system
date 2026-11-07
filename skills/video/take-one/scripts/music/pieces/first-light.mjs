// "First Light", a gentle bed in G for piano and strings. Original composition for the
// take-one code music engine (the engine is adapted from anidoodle, Apache-2.0).
//
// THE HOOK is a slow rise of a third that settles by step: G4 A4 B4, answered a chord later.
// It opens the theme, climbs through Em and C in the build to a B5 over Am (the 9th, the piece's
// one bright ache), and comes home through a borrowed Cm (the Eb) in the coda.
//
//   bar 0       intro   G                        left hand alone, p, melody pickup on beat 3
//   bars 1-8    theme   G  D/F#  Em  C  G/B  Am  D7  G     stepwise line, strings join at bar 5
//   bars 9-12   build   Em  C  Am  D7            eighth-note left hand, melody in the high octave
//   bars 13-16  coda    C  Cm  D7  G             hush (a breath before it), the Eb ache, home
import { line } from "../plan.mjs";

const BPB = 3;
const mel = (t, s, v = 0.7, pickup) => line(t, s, { role: "melody", v, bpb: BPB, pickup });
const bass = (t, s, v = 0.7) => line(t, s, { role: "bass", v, bpb: BPB, roll: 0.03 });
const lh = (t, s, v = 0.7) => line(t, s, { role: "accomp", v, bpb: BPB, roll: 0.035 });
const str = (t, s, v = 0.45) => line(t, s, { role: "inner", v, bpb: BPB, roll: 0.02 });
const H = (xs) => xs.map(([t, name]) => ({ t, name }));

const firstLight = () => {
  const melody = [
    ...mel(2, "D4:1", 0.64, 1), // the pickup, in the intro bar
    ...mel(3, [
      "G4:1.5 A4:.5 B4:1", //          1 G      the hook: a slow rise
      "A4:2 F#4:1", //                 2 D/F#
      "B4:1.5 C5:.5 E5:1", //          3 Em     the rise again, leaping onto E
      "D5:2 C5:1", //                  4 C
      "B4:1.5 A4:.5 G4:1", //          5 G/B    falling home (strings enter)
      "A4:1 C5:1 E5:1", //             6 Am     climbing
      "D5:1.5 C5:.5 A4:.5 F#4:.5", //  7 D7
      "G4:2 B4:1", //                  8 G      cadence; B4 lifts into the build
      "B4:1 E5:1@1.02 G5:1@1.02", // 9 Em     the rise, an octave wide
      "A5:2@0.95 G5:.5@1.02 E5:.5@1.02", // 10 C      near the top
      "B5:1.5@0.8 A5:.5 G5:.5 F#5:.5", // 11 Am   CLIMAX: the 9th over Am, then down by step
      "E5:1@1.08 D5:1@1.05 C5:1", //  12 D7     falling into the hush
      "B4:2 A4:1", //                 13 C      coda, pianissimo
      "G4:1 Eb4:1 D4:1", //           14 Cm     the borrowed iv: Eb is the ache
      "A4:1.5 G4:.5 F#4:1", //        15 D7
      "G4:3", //                      16 G      home
    ].join(" | ")),
  ];
  // climax chord: a rolled E5-A5 under the B5 (bar 11 = beat 33), so the loudness holds and the peak drops
  const climaxChord = line(33, "[E5 A5]:1.5 r:1.5", { role: "inner", v: 0.55, bpb: BPB, roll: 0.045 });
  const bassLine = bass(0, [
    "G2:3", //                        0 intro
    "G2:3", "F#2:3", "E2:3", "C2:3", "B1:3", "A1:3", "D2:3", "G1:1.5 D2:1.5", // 1-8
    "r:.5 E2:2.5", "r:.5 C2:2.5", "r:.5 A1:2.5", "r:.5 D2:2.5", // 9-12 staggered: the bass answers after each downbeat
    "C2:3", "C2:3", "D2:3", "[G1 D2 G2 D3 G3]:3", //                             13-16 rolled home
  ].join(" | "), 0.62);
  const accomp = lh(0, [
    "r:1 D3:1 B3:1", //               0 intro
    "r:1 D3:1 B3:1", "r:1 D3:1 A3:1", "r:1 E3:1 G3:1", "r:1 E3:1 G3:1", //  1-4
    "r:1 D3:1 G3:1", "r:1 E3:1 C4:1", "r:1 F#3:1 C4:1", "r:1 D3:1 B3:1", // 5-8
    "r:.5 E3:.5 G3:.5 B3:.5 G3:.5 E3:.5", //   9 Em  the pulse quickens
    "r:.5 E3:.5 G3:.5 C4:.5 G3:.5 E3:.5", //  10 C
    "r:.5 E3:.5 A3:.5 C4:.5 A3:.5 E3:.5", //  11 Am
    "r:.5 F#3:.5 A3:.5 C4:.5 A3:.5 F#3:.5", // 12 D7
    "r:2 G3:1", "r:2 G3:1", "r:2 F#3:1", "r:3", //  13-16 the hush, single notes
  ].join(" | "), 0.62);
  // strings: a quiet sustained choir from bar 5, swelling with the build, thinning in the coda
  const stringsPart = str(15, [
    "[G3 D4]:3", "[A3 E4]:3", "[A3 D4]:3", "[G3 B3]:3", //          5-8
    "[E3 G3 B3]:3", "[E3 G3 C4]:3", "[E3 A3 C4]:3", "[F#3 A3 C4]:3", // 9-12 build
    "[E3 G3 C4]:3", "[Eb3 G3 C4]:3", "[D3 F#3 C4]:3", "[D3 G3 B3]:3", // 13-16 coda (the Eb)
  ].join(" | "), 0.4);
  const harmony = H([[0, "G"], [3, "G"], [6, "D/F#"], [9, "Em"], [12, "C"], [15, "G/B"], [18, "Am"], [21, "D7"], [24, "G"],
    [27, "Em"], [30, "C"], [33, "Am"], [36, "D7"], [39, "C"], [42, "Cm"], [45, "D7"], [48, "G"]]);
  return {
    title: "First Light (bed in G)", seed: 4207, tail: 1.8, harmony, shortForm: firstLightShort,
    plan: {
      style: "nocturne", tempo: 64, meter: "3/4", phraseBars: 4,
      sections: [
        { id: "intro", bars: 1, mood: "tender", key: "G", mode: "major", melody: ["stepwise"], dyn: [0.35, 0.38], optional: true },
        { id: "theme", bars: 8, mood: "tender", key: "G", mode: "major", melody: ["hook", "stepwise"], dyn: [0.4, 0.6], repeatable: true, pickup: 1, variations: ["octaveDouble", "octaveUp"] },
        { id: "build", bars: 4, mood: ["tender", "hopeful", 0.5], key: "G", mode: "major", melody: ["hook", "sequence"], dyn: [0.65, 0.88], repeatable: true, pickup: 1 },
        { id: "coda", bars: 4, mood: ["tender", "melancholy", 0.4], key: "G", mode: "major", melody: ["themeTransformation"], dyn: [0.38, 0.26], ending: "tail" },
      ],
    },
    parts: [
      { id: "rh", inst: "piano", role: "melody", notes: [...melody, ...climaxChord] },
      { id: "lh", inst: "piano", role: "accomp", notes: [...bassLine, ...accomp] },
      { id: "str", inst: "strings", role: "inner", notes: stringsPart, gainDb: -10, opts: { attack: 0.85, release: 1.3, bright: 0.55, width: 0.6 }, send: 1.2 },
    ],
  };
};

/** The short form, for films under ~40 s: intro + theme, closing on the bar-8 cadence (the B4 lift
 *  into the build becomes a held G). The theme repeats with its variations when the film needs it. */
const firstLightShort = () => {
  const full = firstLight(), END = 27;
  const parts = full.parts.map((pt) => ({ ...pt, notes: pt.notes.filter((n) => n.t < END && !(n.role === "melody" && n.t >= 24)) }));
  parts[0].notes.push(...line(24, "G4:3", { role: "melody", v: 0.66, bpb: BPB }));
  parts[1].notes = parts[1].notes.filter((n) => !(n.role === "bass" && n.t >= 24)).concat(bass(24, "[G1 D2 G2 D3 G3]:3", 0.62));
  const sections = full.plan.sections.slice(0, 2).map((x) => (x.id === "theme" ? { ...x, dyn: [0.4, 0.5], ending: "tail" } : x));
  return { ...full, title: "First Light (short form)", shortForm: undefined, parts, harmony: full.harmony.filter((c) => c.t < END), plan: { ...full.plan, ritard: 0.7, sections } };
};

export default firstLight;
export { firstLightShort };
