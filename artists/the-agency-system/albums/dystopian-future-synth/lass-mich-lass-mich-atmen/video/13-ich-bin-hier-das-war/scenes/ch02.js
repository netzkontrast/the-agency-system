// ch02.js: shots 8-15 (44.6 - 78.6 s). The refrain: here, and what was. The seam takes the light once; the glass clears; no turning round.
(() => {
  const WIDE = [960, 540, 1.0];
  const WALLC = [2450, 460, 1.2];       // the seam, centred
  const BOTH = [1480, 480, .67];         // room on the left, wall on the right
  const CLOSE = [960, 540, 1.15];       // the room again, closer
  const WINC = [1550, 420, 1.5];        // the window
  const WIN2 = [1550, 430, 1.35];       // the window, open
  const DOORC = [320, 470, 1.3];        // the threshold from the front

  // 8  Wide, level with the threshold. A slow glow breath on "hier". No push, no move; the pan to the wall starts as the word has landed.
  const s8 = defShot(8, {
    cam: () => WIDE,
    world: t => room(t),
    out: { type: 'wash', dur: .5 },
  });

  // 9  The paper wall with its gold seam. On "war" the seam takes the light once: a glint runs along it and fades.
  const tWar = stress(6);
  const glint = t => ({ s: seg(t, tWar - .6, tWar + .5), k: Math.sin(Math.PI * seg(t, tWar - .65, tWar + .7)) * .95 });
  const s9 = defShot(9, {
    cam: lt => [WALLC[0] + 4 * lt, WALLC[1], WALLC[2] + .004 * lt],
    world: t => room(t, { glint: glint(t) }),
    out: { type: 'wash', dur: .5 },
  });

  // 10  Room and wall in one frame. The light strip crosses from the room onto the wall. No flare; the seam stays at 60 %.
  const tWar2 = stress(7);
  const s10 = defShot(10, {
    cam: lt => [BOTH[0] + 8 * Math.sin(lt * .25), BOTH[1], BOTH[2]],
    world: t => {
      const head = ease(seg(t, TS.s10 + 1.0, tWar2));
      room(t, { shafts: [[1745, 410, 2430, 440, head, .9 + .08 * Math.sin(t * .6)]], seamLvl: .6 });
    },
    out: { type: 'wash', dur: .5 },
  });

  // 11  Back to the room, closer than shot 8; held. The glow breathes on "hier".
  const s11 = defShot(11, {
    cam: lt => [CLOSE[0] + 3 * Math.sin(lt * .3), CLOSE[1], CLOSE[2]],
    world: t => room(t),
    out: { type: 'wash', dur: .5 },
  });

  // 12  The window pane with breath fog on the glass. On "verlangt" a brush wipe clears it; nothing is demanded.
  const tVer = stress(9);
  const wipeP = t => seg(t, tVer - .25, tVer + .9);
  const s12 = defShot(12, {
    cam: lt => [WINC[0] + 3 * Math.sin(lt * .3), WINC[1], WINC[2] + .003 * lt],
    world: t => room(t, { fog: { k: .8 + .2 * seg(t, TS.s12, tVer - .3), wipe: wipeP(t) } }),
    out: { type: 'slide', to: 13, dur: 1.2 },
  });

  // 13  The window is open; the curtain moves. On "da" it lifts once and settles.
  const tDa = stress(10);
  const s13 = defShot(13, {
    cam: lt => [WIN2[0] + 5 * Math.sin(lt * .25), WIN2[1], WIN2[2]],
    world: t => {
      const open = ease(seg(t, TS.s13 + .5, TS.s13 + 2.8));
      const lift = ease(seg(t, tDa - .4, tDa)) * (1 - ease(seg(t, tDa, tDa + 1.0)));
      room(t, { open, sway: 1 + 1.5 * open, lift, fog: { k: .9, wipe: 1 } });
    },
    out: { type: 'wash', dur: .45 },
  });

  // 14  The seam again; the camera drifts sideways and the seam slides out of frame, left, behind the view.
  const tMir = stress(11);
  const s14 = defShot(14, {
    cam: lt => [WALLC[0] + 1150 * ease(seg(lt, .3, tMir - TS.s14 - .35)) + 4 * lt, WALLC[1], WALLC[2]],
    world: t => room(t),
    out: { type: 'shoji', dur: .5 },
  });

  // 15  The threshold from the front. The camera does not turn around; on "hier" it settles.
  const tHier = stress(12);
  const s15 = defShot(15, {
    cam: lt => [DOORC[0] + 5 * Math.sin(lt * .22), DOORC[1], DOORC[2] + .09 * ease(seg(lt, .3, tHier - TS.s15))],
    world: t => room(t),
    out: { type: 'wash', dur: .5 },
  });

  shots([[TS.s8, s8], [TS.s9, s9], [TS.s10, s10], [TS.s11, s11], [TS.s12, s12], [TS.s13, s13], [TS.s14, s14], [TS.s15, s15]]);
})();
