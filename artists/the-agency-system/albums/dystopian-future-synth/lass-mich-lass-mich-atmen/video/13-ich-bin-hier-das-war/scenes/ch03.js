// ch03.js: shots 16-21 (100-138 s). The second refrain with new pictures, the room emptying to paper, one light joins,
// the opening view returns, the pulse slows, and the page goes blank.
(() => {
  const WIDE = [960, 540, 1.0];
  const WALL16 = [2450, 470, 1.25];
  const WALL17 = [2600, 470, .95];
  const DOOR18 = [320, 480, 1.1];
  const CORNER = [1650, 340, 1.5];

  // 16  100.4-108.4  A light travels across the seam and the gold takes it; the room mirrored faintly in the paper.
  const tWar = stress(14), tHier = stress(13);
  const s16 = defShot(16, {
    cam: lt => [WALL16[0] + 3 * lt, WALL16[1], WALL16[2] + .003 * lt],
    world: t => {
      const travel = ease(seg(t, tHier - .3, tWar - .1));
      const takes = ease(seg(t, tWar - .7, tWar + .2));
      const lvl = .6 + .32 * takes * (1 - .25 * ease(seg(t, tWar + .4, 108.4)));
      room(t, {
        ghost: ease(seg(t, 100.4, 102.4)), seamLvl: lvl,
        glint: { s: .5, k: 0 },
        shafts: [[2060, 430, 2440, 450, 0, 0]],
        wallLight: 0,
        mist: null,
      });
      // the travelling light: a soft point of day that crosses the paper to the seam
      boilSeed('travel');
      const x = lerp(2020, 2440, travel), k = ease(seg(t, tHier - .5, tHier + .3));
      glow(x, 440 + 10 * Math.sin(t * .5), 190 + 70 * takes, C.glowY, .62 * k);
      glow(x, 440, 90, C.glowPale, .5 * k);
    },
    out: { type: 'wash', dur: .6 },
  });

  // 17  108.4-116.4  The light spreads over the wall, warm, held at 60 %, no flare.
  const tWar2 = stress(15);
  const s17 = defShot(17, {
    cam: lt => [WALL17[0] + 4 * lt, WALL17[1], WALL17[2] + .002 * lt],
    world: t => room(t, { ghost: 1, seamLvl: lerp(.92, .6, ease(seg(t, 108.4, 110.4))), wallLight: ease(seg(t, 109.0, tWar2)) }),
    out: { type: 'wash', dur: .7 },
  });

  // 18  116.4-122.4  Back at the door frame; the room empties of detail until only paper, ink and a door are left.
  const s18 = defShot(18, {
    cam: lt => [DOOR18[0] + 4 * Math.sin(lt * .25), DOOR18[1], DOOR18[2] + .004 * lt],
    world: t => room(t),
    out: { type: 'wash', dur: .7 },
  });

  // 19  122.4-128.4  Everything gone but one thing: the Clean Ping appears once on "auch" and stays. One more layer on the wall, bright.
  const tAuch = stress(17);
  const s19 = defShot(19, {
    cam: lt => [CORNER[0] + 3 * Math.sin(lt * .2), CORNER[1], CORNER[2] + .004 * lt],
    world: t => {
      const S = worldState(t), e = S.empty;
      room(t);
      // the corner of a window frame: two ink lines, so the point has a place
      const ca = e;
      boilSeed('corner');
      if (ca > .02) {
        inkLine([[1560, 191], [1648, 190], [1730, 190]], 2.2, fadeCol(C.ink, ca, C.paper), 'ink', .1);
        inkLine([[1730, 190], [1731, 280], [1730, 380]], 2.2, fadeCol(C.ink, ca, C.paper), 'ink', .1);
      }
      // the wall layers: one soft shadow, and after "auch" one more, bright
      const L1 = ease(seg(t, 122.8, 124.0)) * e;
      boilSeed('layer1');
      if (L1 > .02) paint([[1560, 300], [1790, 262], [1900, 700], [1660, 760]], { wash: C.graphiteLt, washOp: 42 * L1, ink: null });
      const L2 = ease(seg(t, tAuch + .1, tAuch + 1.6)) * e;
      boilSeed('layer2');
      if (L2 > .02) {
        paint([[1470, 330], [1690, 292], [1790, 720], [1570, 770]], { wash: C.day, washOp: 150 * L2, ink: null });
        glow(1630, 520, 320, C.glowY, .5 * L2);
      }
    },
    out: { type: 'slide', to: 20, dur: 1.6 },
  });

  // 20  128.4-131.1  The opening view returns: the door open, the point beside the frame.
  const s20 = defShot(20, {
    cam: () => WIDE,
    world: t => room(t),
    out: { type: 'cont' },
  });

  // 21  131.1-138  The lamp's pulse slows (every 2 s, then 4 s), one last breath fog, then the picture goes to paper.
  const s21 = defShot(21, {
    cam: lt => [960, 540, 1.0 + .002 * lt],
    world: t => {
      if (t >= 135.3) return;                                   // blank paper from here on (the declared hold starts at 136)
      const k = ease(seg(t, 131.6, 132.9)) * (1 - ease(seg(t, 133.4, 134.8)));
      room(t, { mist: { x: 1010, y: 520, k } });
    },
    over: t => {
      if (t < 135.3) paperWash(ease(seg(t, 133.6, 135.2)));
      else paperWash(1 - ease(seg(t, 135.3, 135.9)));          // flat paper settles into the grain of bare paper: no pop
    },
    out: { type: 'cont' },
  });

  shots([[100.4, s16], [108.4, s17], [116.4, s18], [122.4, s19], [128.4, s20], [131.1, s21]]);
})();
