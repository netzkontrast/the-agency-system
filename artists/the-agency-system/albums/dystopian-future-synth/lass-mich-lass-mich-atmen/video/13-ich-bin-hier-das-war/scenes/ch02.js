// ch02.js: shots 8-15 (44-100 s). The refrain: here, and what was. The seam takes the light once; the glass clears; no turning round.
(() => {
  const WIDE = [960, 540, 1.0];
  const WALLC = [2450, 470, 1.3];       // the seam, centred
  const BOTH = [1500, 500, .8];         // room on the left, wall on the right
  const CLOSE = [960, 540, 1.15];       // the room again, closer
  const WINC = [1550, 420, 1.5];        // the window
  const WIN2 = [1550, 430, 1.35];       // the window, open
  const DOORC = [320, 470, 1.3];        // the threshold from the front

  // 8  44.4-48.4  Wide, level with the threshold. A slow glow breath on "hier". No push, no move.
  const s8 = defShot(8, {
    cam: () => WIDE,
    world: t => room(t),
    out: { type: 'slide', to: 9, dur: 1.4, wash: .35 },
  });

  // 9  48.4-52.4  The paper wall with its gold seam. On "war" the seam takes the light once: a glint runs along it and fades.
  const tWar = stress(6);
  const glint = t => ({ s: seg(t, tWar - .9, tWar + .9), k: Math.sin(Math.PI * seg(t, tWar - 1.0, tWar + 1.3)) * .95 });
  const s9 = defShot(9, {
    cam: lt => [WALLC[0] + 4 * lt, WALLC[1], WALLC[2] + .004 * lt],
    world: t => room(t, { glint: glint(t) }),
    out: { type: 'slide', to: 10, dur: 1.2 },
  });

  // 10  52.4-60.4  Room and wall in one frame. The light strip crosses from the room onto the wall. No flare; the seam stays at 60 %.
  const tWar2 = stress(7);
  const s10 = defShot(10, {
    cam: lt => [BOTH[0] + 8 * Math.sin(lt * .25), BOTH[1], BOTH[2]],
    world: t => {
      const head = ease(seg(t, 53.4, tWar2));
      room(t, { shafts: [[1745, 410, 2430, 440, head, .9 + .08 * Math.sin(t * .6)]], seamLvl: .6 });
    },
    out: { type: 'slide', to: 11, dur: 1.2, wash: .35 },
  });

  // 11  60.4-68.4  Back to the room, closer than shot 8; held. The glow breathes on "hier".
  const s11 = defShot(11, {
    cam: () => CLOSE,
    world: t => room(t),
    out: { type: 'wash', dur: .6 },
  });

  // 12  68.4-76.4  The window pane with breath fog on the glass. On "verlangt" a brush wipe clears it; nothing is demanded.
  const tVer = stress(9);
  const wipeP = t => seg(t, tVer - .25, tVer + .9);
  const s12 = defShot(12, {
    cam: lt => [WINC[0] + 3 * Math.sin(lt * .3), WINC[1], WINC[2] + .003 * lt],
    world: t => room(t, { fog: { k: .8 + .2 * seg(t, 68.4, tVer - .3), wipe: wipeP(t) } }),
    out: { type: 'slide', to: 13, dur: 2.2 },
  });

  // 13  76.4-84.4  The window is open; the curtain moves. On "da" it lifts once and settles.
  const tDa = stress(10);
  const s13 = defShot(13, {
    cam: lt => [WIN2[0] + 5 * Math.sin(lt * .25), WIN2[1], WIN2[2]],
    world: t => {
      const open = ease(seg(t, 76.9, 79.6));
      const lift = ease(seg(t, tDa - .4, tDa)) * (1 - ease(seg(t, tDa, tDa + 1.0)));
      room(t, { open, sway: 1 + 1.5 * open, lift, fog: { k: .9, wipe: 1 } });
    },
    out: { type: 'slide', to: 14, dur: 1.3, wash: .3 },
  });

  // 14  84.4-92.4  The seam again; the camera drifts sideways and the seam slides out of frame, left, behind the view.
  const tMir = stress(11);
  const s14 = defShot(14, {
    cam: lt => [WALLC[0] + 1150 * ease(seg(lt, .4, tMir - 84.4 + .2)) + 4 * lt, WALLC[1], WALLC[2]],
    world: t => room(t),
    out: { type: 'shoji', dur: 1.2 },
  });

  // 15  92.4-100.4  The threshold from the front. The camera does not turn around; on "hier" it settles.
  const tHier = stress(12);
  const s15 = defShot(15, {
    cam: lt => [DOORC[0] + 5 * Math.sin(lt * .22), DOORC[1], DOORC[2] + .09 * ease(seg(lt, .3, tHier - 92.4))],
    world: t => room(t),
    out: { type: 'wash', dur: .7 },
  });

  shots([[44.4, s8], [48.4, s9], [52.4, s10], [60.4, s11], [68.4, s12], [76.4, s13], [84.4, s14], [92.4, s15]]);
})();
