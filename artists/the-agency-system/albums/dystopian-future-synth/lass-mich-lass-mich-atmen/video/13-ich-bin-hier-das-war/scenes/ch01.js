// ch01.js: chapter 1. Each shot fn(t, lt, dur) paints the WHOLE frame and is a pure function of t.
// Read <studio>/references/paint-medium.md before drawing (rules, workflow, full API).
(() => {
  shots([
    [0, (t, lt, dur) => {
      boilSeed('ground');
      paint(rectPts(-60, H * .62, W + 120, H * .5), { wash: PAL.clay, fill: PAL.clayDk, fillOp: 70, bleed: .1, ink: null });
      boilSeed('sun');
      const r = 90 + 12 * SONG.pulse(t);
      paint(ellPts(W / 2, H * .42, r, r, 28, 2), { wash: PAL.ochre, ink: PAL.ink, sw: 1 });
      glow(W / 2, H * .42, r * 2.4, '#FFC766', .8);
      if (lt < .3) brushWipe(.5 + lt / .6);
      // the last shot ends on a hold or a fade, not a wipe the film's end cuts in half (the gate flags that as a pop)
    }],
  ]);
})();
