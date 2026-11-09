// ch03.js: shots 16-23 (78.6 - 138 s). The second refrain with new pictures, the room emptying to paper, one light joins and stays,
// the opening view returns, a long exhale, the threshold again, the pulse slows, and the page goes blank.
(() => {
  const WIDE = [960, 540, 1.0];
  const WALL16 = [2450, 470, 1.25];
  const WALL17 = [2600, 470, .95];
  const DOOR18 = [320, 480, 1.1];
  const CORNER = [1650, 340, 1.5];
  const DOORC = [320, 470, 1.38];       // the threshold from the front (as shot 15)

  // 16  A light travels across the seam and the gold takes it; the room mirrored faintly in the paper.
  const tWar = stress(14), tHier = stress(13);
  const s16 = defShot(16, {
    cam: lt => [WALL16[0] + 3 * lt, WALL16[1], WALL16[2] + .003 * lt],
    world: t => {
      const travel = ease(seg(t, tHier - .3, tWar - .1));
      const takes = ease(seg(t, tWar - .7, tWar + .2));
      const lvl = .6 + .32 * takes * (1 - .25 * ease(seg(t, tWar + .4, TS.s17)));
      room(t, { ghost: ease(seg(t, TS.s16, TS.s16 + 1.6)), seamLvl: lvl });
      boilSeed('travel');
      const x = lerp(2020, 2440, travel), k = ease(seg(t, tHier - .5, tHier + .3));
      glow(x, 440 + 10 * Math.sin(t * .5), 190 + 70 * takes, C.glowY, .62 * k);
      glow(x, 440, 90, C.glowPale, .5 * k);
    },
    out: { type: 'wash', dur: .5 },
  });

  // 17  The light spreads over the wall, warm, held at 60 %, no flare.
  const tWar2 = stress(15);
  const s17 = defShot(17, {
    cam: lt => [WALL17[0] + 4 * lt, WALL17[1], WALL17[2] + .002 * lt],
    world: t => room(t, { ghost: 1, seamLvl: lerp(.92, .6, ease(seg(t, TS.s17, TS.s17 + 2))), wallLight: ease(seg(t, TS.s17 + .6, tWar2)) }),
    out: { type: 'wash', dur: .45 },
  });

  // 18  Back at the door frame; the room empties of detail until only paper, ink and a door are left.
  const s18 = defShot(18, {
    cam: lt => [DOOR18[0] + 4 * Math.sin(lt * .25), DOOR18[1], DOOR18[2] + .004 * lt],
    world: t => room(t),
    out: { type: 'wash', dur: .5 },
  });

  // 19  Everything gone but one thing: the Clean Ping appears once on "auch" and stays alone on the paper through the quiet 7 s after.
  const tAuch = stress(17);
  const s19 = defShot(19, {
    cam: lt => [CORNER[0] + 3 * Math.sin(lt * .2) + 4 * lt, CORNER[1] + 1.5 * lt, CORNER[2] + .006 * lt],
    world: t => {
      const S = worldState(t), e = S.empty, la = t - TS.s19, dk = darkK(t);
      room(t);
      boilSeed('corner');
      if (e > .02) {   // the corner of a window frame: two ink lines, so the point has a place
        inkLine([[1560, 191], [1648, 190], [1730, 190]], 2.2, mixCol(fadeCol(C.ink, e, C.paper), C.paper, dk), 'ink', .1);
        inkLine([[1730, 190], [1731, 280], [1730, 380]], 2.2, mixCol(fadeCol(C.ink, e, C.paper), C.paper, dk), 'ink', .1);
      }
      const L1 = ease(seg(t, TS.s19 + .3, TS.s19 + 1.5)) * e;     // the wall: one soft shadow, then, after "auch", one more, bright
      boilSeed('layer1');
      if (L1 > .02) paint([[1560, 300], [1790, 262], [1900, 700], [1660, 760]], { wash: mixCol(C.graphiteLt, '#4A3F55', dk), washOp: (42 + 60 * dk) * L1, ink: null });
      const L2 = ease(seg(t, tAuch + .1, tAuch + 1.6)) * e, dx = 55 * Math.sin(la * .22), br = .85 + .15 * Math.sin(la * .5);
      boilSeed('layer2');
      if (L2 > .02) {
        paint([[1470 + dx, 330], [1690 + dx, 292], [1790 + dx, 720], [1570 + dx, 770]], { wash: C.day, washOp: 150 * L2, ink: null });
        glow(1630 + dx, 520, 320, C.glowY, .5 * L2 * br);
      }
      const L3 = ease(seg(t, TS.s19 + 5, TS.s20 - 2)) * e;           // in the quiet seven seconds the light slowly lies further across the paper
      boilSeed('layer3');
      if (L3 > .02) glow(1900 + 40 * Math.sin(la * .2), 560, 380, C.glowPale, .35 * L3);
    },
    out: { type: 'slide', to: 20, dur: 1.8 },
  });

  // 20  The opening view returns: the door open, the point beside the frame; the glow pulses on the beat.
  const s20 = defShot(20, {
    cam: () => WIDE,
    world: t => room(t),
    out: { type: 'cont' },
  });

  // 21  Instrumental, 16.7 s: the long exhale. Light lies on the wall and the floor, the curtain breathes twice, the camera backs away.
  const s21 = defShot(21, {
    cam: (lt, t, dur) => { const k = ease(seg(lt, 0, dur - 3)); return [lerp(960, 1010, k), 540, lerp(1.0, .84, k)]; },
    world: t => {
      const a = t - TS.s21;
      const lift = .55 * bump(t, TS.s21 + 5.5, 1.6, 2.6) + .55 * bump(t, TS.s21 + 11.5, 1.6, 2.6);
      room(t, { roomLight: ease(seg(t, TS.s21 + 1, TS.s21 + 9)), lift, sway: 1.4 + .3 * Math.sin(a * .4) });
    },
    out: { type: 'slide', to: 22, dur: 3.0 },
  });

  // 22  The threshold again, from the front. On "hier" the point brightens a little and holds; on "war" the room is paper-quiet.
  const s22 = defShot(22, {
    cam: lt => [DOORC[0] + 4 * Math.sin(lt * .2), DOORC[1], DOORC[2] + .004 * lt],
    world: t => room(t, { roomLight: 1 - ease(seg(t, TS.s23 - .9, TS.s23)) }),
    out: { type: 'slide', to: 23, dur: .9 },
  });

  // 23  Stille: the pulse slows (every 2 s, then 4 s), one last breath fog, then the picture goes to paper (blank from DUR - 2: a declared hold).
  const s23 = defShot(23, {
    cam: lt => [960, 540, 1.0 + .002 * lt],
    world: t => {
      if (t >= DUR - 1.4) return;
      const k = ease(seg(t, DUR - 4.0, DUR - 2.7)) * (1 - ease(seg(t, DUR - 2.6, DUR - 1.6)));   // blooms with the sub-bass swell, 134-136 s
      room(t, { mist: { x: 1010, y: 520, k } });
    },
    over: t => {
      if (t < DUR - 1.4) paperWash(ease(seg(t, DUR - 3.6, DUR - 1.6)));
      else paperWash(1 - ease(seg(t, DUR - 1.4, DUR - 1.0)));   // flat paper settles into the grain of bare paper: no pop
    },
    out: { type: 'cont' },
  });

  shots([[TS.s16, s16], [TS.s17, s17], [TS.s18, s18], [TS.s19, s19], [TS.s20, s20], [TS.s21, s21], [TS.s22, s22], [TS.s23, s23]]);
})();
