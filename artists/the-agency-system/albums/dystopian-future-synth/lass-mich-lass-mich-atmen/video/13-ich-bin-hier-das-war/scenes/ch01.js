// ch01.js: shots 1-7 (0-44 s). The room wakes: a pulse, the light in the cloth, a bare pillow, a breath, the whole room.
// Every time below comes from the song map (stress(i) = the stressed syllable of line i's key word).
(() => {
  const WIDE = [960, 540, 1.0];
  const END2 = [985, 535, 1.07];                 // where the slow push of shot 2 ends; shot 3 holds here, then travels to the curtain
  const CURT = [1400, 470, 1.7];                 // shot 4 start
  const PILL = [940, 850, 1.8];                  // shot 5 start
  const MID = [900, 570, 1.3];                   // shot 6 / shot 7 start

  // 1  0-2.4  Fade up from blank paper onto the threshold; the lamp breathes on every beat.
  const s1 = defShot(1, {
    cam: lt => [960, 540, 1.0 + .003 * lt],
    world: t => room(t),
    over: (t, lt) => paperWash(1 - ease(seg(lt, 0, 2.2))),
    out: { type: 'cont' },
  });

  // 2  2.4-8.0  Very slow push in. On "meiner" the pulse is larger and the paper wash breathes once (worldState.big).
  const s2 = defShot(2, {
    cam: lt => { const k = ease(seg(lt, 0, 5.6)); return [lerp(960.0, END2[0], k), lerp(540.0, END2[1], k), lerp(1.0075, END2[2], k)]; },
    world: t => room(t),
    out: { type: 'cont' },
  });

  // 3  8.0-12.4  The light strip beside the curtain widens (an inhale); the camera drifts toward the curtain.
  const s3 = defShot(3, {
    cam: () => END2,
    world: t => room(t),
    out: { type: 'slide', to: 4, dur: 3.8 },
  });

  // 4  12.4-20.4  Close on the curtain folds, yellow behind them. On "Licht" the pulse stops: plain daylight.
  const s4 = defShot(4, {
    cam: lt => [CURT[0] + 6 * lt, CURT[1] + 3 * Math.sin(lt * .3), CURT[2] + .006 * lt],
    world: t => room(t),
    out: { type: 'wash', dur: .6 },
  });

  // 5  20.4-28.4  Close on the pillow, smooth; a yellowed thread lies beside it. On "Druck" the thread slides out of the frame.
  const s5 = defShot(5, {
    cam: lt => [PILL[0] + 5 * Math.sin(lt * .25), PILL[1] - 2 * lt, PILL[2] + .004 * lt],
    world: t => room(t),
    out: { type: 'wash', dur: .6 },
  });

  // 6  28.4-36.4  A breath fog opens on "ein" and closes on "aus". One light, one shadow.
  const tEin = wordT(3, /^ein/i, 29.7), tAus = stress(3);
  const six = lt => [MID[0] + 4 * Math.sin(lt * .2), MID[1], MID[2] + .004 * lt];
  const s6 = defShot(6, {
    cam: six,
    world: t => {
      const k = ease(seg(t, tEin - .5, tEin + .6)) * (1 - ease(seg(t, tAus - .9, tAus + .15)));
      room(t, { mist: { x: 1000, y: 600, k } });
    },
    out: { type: 'cont' },
  });

  // 7  36.4-44.4  Pull back to the whole room and stop; on "hier" the move settles and holds.
  const tHier = stress(4);
  const s7 = defShot(7, {
    cam: lt => {
      const k = easeOut(seg(lt, .2, tHier - 36.4));
      const m = six(8.0);
      return [lerp(m[0], WIDE[0], k), lerp(m[1], WIDE[1], k), lerp(m[2], WIDE[2], k)];
    },
    world: t => room(t),
    out: { type: 'cont' },
  });

  shots([[0, s1], [2.4, s2], [8.0, s3], [12.4, s4], [20.4, s5], [28.4, s6], [36.4, s7]]);
})();
