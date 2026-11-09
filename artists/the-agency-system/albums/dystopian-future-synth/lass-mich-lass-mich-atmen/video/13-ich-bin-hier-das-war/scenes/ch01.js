// ch01.js: shots 1-7 (0 - 44.6 s). The room wakes: a pulse, the door and the cloth, light in the cloth, a bare pillow, a breath, the whole room.
// All times come from the song map (TS = shot boundaries, stress(i) = stressed syllable of line i's key word).
(() => {
  const WIDE = [960, 540, 1.0];
  const END2 = [985, 535, 1.07];                 // where the slow push of shot 2 ends
  const DOORV = [400, 480, 1.35], MIDV = [1250, 470, 1.45];
  const CURT = [1400, 470, 1.7];                 // shot 4 start
  const PILL = [940, 850, 1.8];                  // shot 5 start
  const MID = [900, 570, 1.3];                   // shot 6 / shot 7 start

  // 1  Fade up from blank paper onto the threshold; the lamp breathes on every beat.
  const s1 = defShot(1, {
    cam: lt => [960, 540, 1.0 + .003 * lt],
    world: t => room(t),
    over: (t, lt) => paperWash(1 - ease(seg(lt, 1.5, TS.s2))),   // blank paper under the notice, then the room fades up as it leaves
    out: { type: 'cont' },
  });

  // 2  Very slow push in. On "meiner" the pulse is larger and the paper wash breathes once (worldState.big).
  const s2 = defShot(2, {
    cam: (lt, t, dur) => { const k = ease(seg(lt, 0, dur - .8)), z0 = 1.0 + .003 * TS.s2; return [lerp(960, END2[0], k), lerp(540, END2[1], k), lerp(z0, END2[2], k)]; },
    world: t => room(t),
    out: { type: 'cont' },
  });

  // 3  Instrumental, 13 s. The camera slides from the door across to the curtain (first half); then the light strip widens like an inhale.
  const s3 = defShot(3, {
    cam: (lt, t, dur) => {
      const h = dur / 2;
      return kf(lt, [[0, END2], [2.4, DOORV], [3.8, DOORV], [h - .4, MIDV], [dur, CURT]]);
    },
    world: t => room(t),
    out: { type: 'cont' },
  });

  // 4  Close on the curtain folds, yellow behind them. On "Licht" the pulse stops: plain daylight.
  const s4 = defShot(4, {
    cam: lt => [CURT[0] + 6 * lt, CURT[1] + 3 * Math.sin(lt * .3), CURT[2] + .006 * lt],
    world: t => room(t),
    out: { type: 'wash', dur: .5 },
  });

  // 5  Close on the pillow, smooth; a yellowed thread lies beside it. On "Druck" the thread slides out of the frame.
  const s5 = defShot(5, {
    cam: lt => [PILL[0] + 5 * Math.sin(lt * .25), PILL[1] - 2 * lt, PILL[2] + .004 * lt],
    world: t => room(t),
    out: { type: 'wash', dur: .5 },
  });

  // 6  A breath fog opens on "ein" and closes on "aus". One light, one shadow.
  const tEin = wordT(3, /^ein/i, 33.4), tAus = stress(3);
  const six = lt => [MID[0] + 4 * Math.sin(lt * .2), MID[1], MID[2] + .004 * lt];
  const s6 = defShot(6, {
    cam: six,
    world: t => {
      const k = ease(seg(t, tEin - .5, tEin + .6)) * (1 - ease(seg(t, tAus - .9, tAus + .15)));
      room(t, { mist: { x: 1000, y: 600, k } });
    },
    out: { type: 'cont' },
  });

  // 7  Pull back to the whole room; the move slows to a stop exactly as "hier" lands.
  const tHier = stress(4);
  const s7 = defShot(7, {
    cam: (lt, t, dur) => {
      const k = easeOut(seg(lt, .2, tHier - TS.s7));
      const m = six(TS.s7 - TS.s6);
      return [lerp(m[0], WIDE[0], k), lerp(m[1], WIDE[1], k), lerp(m[2], WIDE[2], k)];
    },
    world: t => room(t),
    out: { type: 'cont' },
  });

  shots([[0, s1], [TS.s2, s2], [TS.s3, s3], [TS.s4, s4], [TS.s5, s5], [TS.s6, s6], [TS.s7, s7]]);
})();
