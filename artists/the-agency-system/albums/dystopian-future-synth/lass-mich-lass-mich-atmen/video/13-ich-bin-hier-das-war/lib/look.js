// look.js: the shared look of "Ich bin hier / Das war". One room, painted once, seen by every chapter.
// Objects and light only (no bodies, no faces, no names). Every helper is a pure function of t and calls boilSeed(key)
// with a constant key before each element, so the line boil stays stable.
// World space: the room spans x -600..2060, the paper wall x 2040..3900; floor line at y 780. Chapters set a camera with
// camSet() and call room(t, extras) inside it; transitions (slide / wash / shoji) are handled by defShot().

// ---------- palette ----------
const C = {
  paper: '#F3EBDC', ink: '#2B2233', yellow: '#F2C14E', gold: '#FFDF00', ping: '#FCEE0C',
  wall: '#E6DBC4', wall2: '#D6C8AC', floor: '#D2C3A4', graphite: '#6E6670', graphiteLt: '#A59DA6',
  cloth: '#EBDBA4', clothDk: '#CDB677', day: '#F7E5A6', leaf: '#C4B597', fog: '#D3D8D5', pillow: '#E9DFD9',
  shade: '#EBDAA8', thread: '#C9A33F', goldDk: '#9C8440', glowY: '#FFC766', glowPale: '#FFE7A0', cream: '#FFF5E2',
};
const fadeCol = (col, a, bg) => mixCol(col, bg, 1 - clamp(a));

// ---------- the song map: stressed syllables (read from SONG, storyboard times only as fallback) ----------
const _FALL = [7.39, 17.56, 23.71, 31.13, 41.50, 46.51, 50.29, 57.70, 62.51, 73.38, 81.77, 89.70, 97.56, 102.51, 106.29, 113.70, 118.51, 123.93, 130.85];
const stress = i => { const l = SONG.line(i); return (l && l.key && l.key.stress != null) ? l.key.stress : _FALL[i]; };
function wordT(line, re, fb) {
  const ws = (SONG.map && SONG.map.words) || [];
  for (const w of ws) if (w.line === line && re.test(w.w)) return w.stress != null ? w.stress : w.t;
  return fb;
}
// shot boundaries, computed from the measured song map (never hard-coded; a re-measured map retimes the film)
const _lt = i => { const l = SONG.line(i); return l ? l.t : null; }, _le = i => { const l = SONG.line(i); return l ? l.end : null; };
const _instr = (SONG.map && SONG.map.sections || []).filter(x => /instrumental/i.test(x.name));
const TS = {
  s2: SONG.beatTime(Math.ceil(SONG.beatAt(2.35))), s3: _instr[0] ? _instr[0].t : 8.62, s4: _instr[0] ? _instr[0].end : 21.5, s5: _lt(2) - .34, s6: _le(2), s7: _lt(4),
  s8: _lt(5), s9: _lt(6), s10: _lt(7), s11: _le(7), s12: _lt(9), s13: _le(9), s14: _le(10), s15: _lt(12), s16: _lt(13),
  s17: _le(14), s18: _le(15), s19: _le(16), s20: _lt(18), s21: _le(19), s22: _lt(20), s23: _le(21),
};
// smooth bump peaking at t0 (rises over `rise` s before it, falls over `fall` s after)
const bump = (t, t0, rise, fall) => ease(seg(t, t0 - rise, t0)) * (1 - ease(seg(t, t0, t0 + fall)));

// dark paper of the bridge (shot 19): painted night paper; same eased window the lyric layer uses for its paper-coloured ink
function darkK(t) { return ease(seg(t, TS.s19, TS.s19 + 1.2)) * (1 - ease(seg(t, TS.s20 - 1.0, TS.s20))); }
// ---------- the heartbeat: 1 beat = 1 s, soft attack; slows to nothing in the outro ----------
function softBeat(t, tb, a = .12, k = 5) {
  const x = t - tb; if (x < 0) return 0;
  const u = Math.min(1, x / a), rise = u * u * (3 - 2 * u);
  return rise * Math.exp(-Math.max(0, x - a) * k);
}
const FIRST_BEAT = SONG.beatTime(Math.ceil(SONG.beatAt(2.35)));   // the audio is silent until 2.35 s: no pulse before the first beat after it
function heart(t) {
  if (t < FIRST_BEAT) return 0;
  const tc = TS.s23 - .2;
  if (t < tc) return SONG.pulseSoft(t, .12, 5);
  const i = Math.floor(SONG.beatAt(tc)), b0 = SONG.beatTime(i);   // the beat that is sounding as the outro begins
  return softBeat(t, b0) + softBeat(t, b0 + 1) + .85 * softBeat(t, b0 + 3) + .7 * softBeat(t, b0 + 7);   // every 1 s, then 2 s, then 4 s
}

// ---------- global world state: every default is a pure function of t, so neighbouring shots always match ----------
function worldState(t) {
  const tMein = stress(0), tLicht = stress(1), tDruck = stress(2);
  const on = (1 - ease(seg(t, tLicht - .3, tLicht + .15))) + ease(seg(t, TS.s7 - .4, TS.s7 + 1.2));   // heartbeat on / off / on again
  const pulseOn = clamp(on);
  const hb = heart(t);
  let big = .38 * bump(t, tMein, .3, .9);                       // "meiner": a larger pulse
  for (const [i, g] of [[4, .16], [5, .2], [8, .16], [12, .16], [13, .2], [16, .16], [18, .16], [20, .16]]) big += g * bump(t, stress(i), .3, 1.2);
  const fade21 = 1 - ease(seg(t, DUR - 3.6, DUR - 1.9));
  const swell = ease(seg(t, TS.s21 + 1, TS.s21 + 9)) * (1 - ease(seg(t, TS.s22 - 1, TS.s22 + .5)));   // the loud instrumental: the film's biggest light
  const level = clamp((lerp(.72, .5, pulseOn) + .36 * pulseOn * hb + big + .22 * swell) * fade21 + .02 * Math.sin(t * .6));
  const strip = .36 + .4 * ease(seg(t, (TS.s3 + TS.s4) / 2, TS.s4)) + .02 * Math.sin(t * .5);
  const daylight = ease(seg(t, tLicht - .2, tLicht + .5));
  const thread = ease(seg(t, tDruck - .1, tDruck + .7));
  const pingK = ease(seg(t, stress(17) - .15, stress(17) + .45)) * (1 - ease(seg(t, DUR - 4.2, DUR - 2.8)));
  const empty = ease(seg(t, TS.s18 + .1, TS.s19 + .6)) * (1 - ease(seg(t, TS.s20 - 1.4, TS.s20 + .4)));
  const doorGone = ease(seg(t, TS.s19 + .8, TS.s19 + 2.4)) * (1 - ease(seg(t, TS.s20 - 1.8, TS.s20 - .2)));
  const pk = ease(seg(t, TS.s21 + 1.5, TS.s22 - .5)), pingPos = { x: lerp(1754, 548, pk), y: lerp(170, 128, pk) };
  const pingBoost = .5 * bump(t, stress(20), .3, 2.5) + .55 * bump(t, stress(19) + .15, .3, 1.8) + .55 * bump(t, stress(21) + .15, .3, 1.8) + .12 * hb * ease(seg(t, TS.s20, TS.s20 + 2));
  return { level, hb, pulseOn, big, strip, daylight, thread, pingK, pingPos, pingBoost, empty, doorGone, breath: .5 + .5 * Math.sin(t * .45) };
}

// ---------- camera with a visible-rect, so props out of view cost nothing ----------
let VIEW = [0, 0, W, H];
// the layout is drawn in 1920x1080 world units; the camera scales it to whatever frame size the renderer asks for
const SC = W / 1920;
function camSet(cx, cy, z) { camBegin(cx, cy, z * SC); const hw = 960 / z + 160, hh = 540 / z + 160; VIEW = [cx - hw, cy - hh, cx + hw, cy + hh]; }
const seen = (x0, x1, y0 = -1e9, y1 = 1e9) => x1 >= VIEW[0] && x0 <= VIEW[2] && y1 >= VIEW[1] && y0 <= VIEW[3];

// ---------- backdrop: wall and floor ----------
function backdrop(t, S, e) {
  const x0 = Math.max(-640, VIEW[0]), x1 = Math.min(4200, VIEW[2]); if (x1 <= x0) return;
  const warm = .05 * S.big;
  const wall = mixCol(mixCol(C.wall, C.day, warm + .1 * S.daylight), C.paper, e), floor = mixCol(C.floor, C.paper, e);
  boilSeed('wall');
  paint(rectPts(x0, -420, x1 - x0, 1200), { wash: wall, ink: null });
  boilSeed('floor');
  paint(rectPts(x0, 780, x1 - x0, 820), { wash: floor, ink: null });
  if (e < .98) {
    boilSeed('wall-shade');
    paint(rectPts(x0, 520, x1 - x0, 260), { wash: C.wall2, washOp: 70 * (1 - e), ink: null });
    boilSeed('floor-shade');
    paint(rectPts(x0, 1000, x1 - x0, 400), { wash: C.wall2, washOp: 60 * (1 - e), ink: null });
  }
  const line = mixCol(C.ink, wall, .12 + .88 * e * .0);
  for (let x = x0; x < x1; x += 1500) {
    const xe = Math.min(x1, x + 1500);
    boilSeed('base' + Math.round(x / 1500));
    inkLine([[x, 781], [(x + xe) / 2, 783], [xe, 781]], 1.5, line, 'ink', .2);
    if (e < .98) for (const [k, yy] of [[0, 850], [1, 940], [2, 1040]]) {
      boilSeed('board' + k + '_' + Math.round(x / 1500));
      inkLine([[x, yy], [(x + xe) / 2, yy + 2], [xe, yy]], .7, fadeCol(mixCol(C.floor, C.ink, .2), 1 - e, wall), 'inkfine', .2);
    }
  }
}

// ---------- motes: slow dust in the light ----------
function motes(t, x0, y0, x1, y1, n, a, key) {
  if (a <= .02) return;
  for (let i = 0; i < n; i++) {
    const h = hash(i * 3.7 + n), x = lerp(x0, x1, h) + 20 * Math.sin(t * .35 + i * 2.1);
    const hh = y1 - y0, y = y0 + (((hash(i + 50) * hh - t * (9 + 7 * hash(i + 9))) % hh) + hh) % hh;
    boilSeed(key + i);
    paint(ellPts(x, y, 2 + 2.5 * hash(i + 21), 2 + 2 * hash(i + 22), 8, .4), { wash: C.cream, washOp: 190 * a, ink: null });
  }
}

// ---------- the door: open, daylight beyond; threshold ----------
const DOOR = { x0: 130, x1: 500, y0: 160, y1: 780 };
function door(t, o = {}) {
  const a = 1 - (o.gone ?? 0); if (a < .02 || !seen(0, 720)) return;
  const { x0, x1, y0, y1 } = DOOR, bg = o.bg || C.wall, day = o.day ?? 0;
  const dayC = fadeCol(C.day, a, bg);
  boilSeed('door-sky');
  paint(rectPts(x0, y0, x1 - x0, y1 - y0), { wash: dayC, ink: null });
  boilSeed('door-sky2');
  paint(ellPts((x0 + x1) / 2, y0 + 110, 150, 90, 16, 6), { wash: fadeCol('#CFE0D8', a, bg), washOp: 60 * a, ink: null });
  boilSeed('door-ground');
  paint(rectPts(x0, y0 + 430, x1 - x0, y1 - y0 - 430), { wash: fadeCol('#EBDB95', a, bg), ink: null });
  boilSeed('door-horizon');
  inkLine([[x0 + 6, y0 + 428], [(x0 + x1) / 2, y0 + 424], [x1 - 6, y0 + 428]], .7, fadeCol(mixCol(C.ink, C.day, .55), a, bg), 'inkfine', .3);
  for (let i = 0; i < 7; i++) {   // grass strokes outside, swaying
    boilSeed('door-grass' + i);
    const gx = x0 + 40 + i * 48 + 10 * hash(i), gy = y0 + 470 + 60 * hash(i + 5), sw = 4 * Math.sin(t * .6 + i);
    inkLine([[gx, gy], [gx + sw * .5, gy - 30], [gx + sw, gy - 56]], .8, fadeCol(mixCol('#9DAE62', C.ink, .15), a, bg), 'inkfine', .5);
  }
  glow(315, 470, 440 + 20 * Math.sin(t * .4), C.glowY, (.5 + .08 * Math.sin(t * .4) + .1 * day) * a);
  const sway = 4 * Math.sin(t * .33);
  boilSeed('door-frame');
  inkLine([[x0, y1], [x0 - 2, y0 + 3], [x1 + 2, y0 - 4], [x1, y1]], 2.4, fadeCol(C.ink, a, bg), 'ink', .15);
  inkLine([[x0 - 28, y1 + 4], [x0 - 26, y0 - 26], [x1 + 26, y0 - 30], [x1 + 24, y1 + 4]], 1.5, fadeCol(C.ink, a, bg), 'ink', .15);
  boilSeed('door-leaf');   // the leaf, swung into the room: a narrow, tall trapezoid on the hinge side
  const fx = 118 + sway;
  paint([[x1, y0], [x1 + fx, y0 - 52], [x1 + fx, y1 + 62], [x1, y1]], { wash: fadeCol(C.leaf, a, bg), ink: fadeCol(C.ink, a, bg), sw: 1.5 });
  boilSeed('door-leaf-panel');
  inkLine([[x1 + 22, y0 + 40], [x1 + fx - 20, y0 - 2], [x1 + fx - 20, y0 + 250], [x1 + 22, y0 + 290], [x1 + 22, y0 + 40]], .8, fadeCol(C.ink, a * .7, bg), 'inkfine', .1);
  boilSeed('door-leaf-panel2');
  inkLine([[x1 + 22, y0 + 340], [x1 + fx - 20, y0 + 300], [x1 + fx - 20, y1 - 30], [x1 + 22, y1 - 60], [x1 + 22, y0 + 340]], .8, fadeCol(C.ink, a * .7, bg), 'inkfine', .1);
  boilSeed('door-sill');
  paint(rectPts(x0 - 34, y1 - 2, x1 - x0 + 68, 20), { wash: fadeCol(C.wall2, a, bg), ink: fadeCol(C.ink, a, bg), sw: 1 });
  boilSeed('door-lightpatch');   // daylight lying on the floor
  paint([[x0, y1 + 20], [x1, y1 + 20], [x1 + 320, y1 + 250], [x0 + 90, y1 + 275]], { wash: fadeCol(C.day, a, bg), washOp: 120 * a, ink: null });
  motes(t, x0 + 10, y0 + 30, x1 - 10, y1 - 20, 8, .75 * a, 'dm');
}

// ---------- the window: glass, frame, optional open sash, optional breath fog on the glass ----------
const WIN = { x0: 1330, x1: 1730, y0: 190, y1: 640 };
function windowPane(t, o = {}) {
  const a = 1 - (o.empty ?? 0); if (a < .02 || !seen(1280, 1900)) return;
  const { x0, x1, y0, y1 } = WIN, w = x1 - x0, h = y1 - y0, bg = o.bg || C.wall, open = o.open ?? 0;
  boilSeed('win-glass');
  paint(rectPts(x0, y0, w, h), { wash: fadeCol('#F3E4AE', a, bg), ink: null });
  boilSeed('win-sky');
  paint(ellPts(x0 + w * .6, y0 + 90, 150, 70, 16, 5), { wash: fadeCol('#CFE0D8', a, bg), washOp: 70 * a, ink: null });
  boilSeed('win-roof');
  paint([[x0, y1], [x0, y1 - 90], [x0 + 90, y1 - 120], [x0 + 150, y1 - 95], [x0 + 250, y1 - 140], [x0 + 330, y1 - 100], [x1, y1 - 130], [x1, y1]], { wash: fadeCol('#E3D69A', a, bg), ink: null });
  glow(1560, 400, 330 + 90 * open + 14 * Math.sin(t * .4), C.glowY, (.38 + .3 * open + .1 * (o.day ?? 0)) * a);
  if (o.cloud != null && o.cloud > .001 && o.cloud < .999) {   // a cloud shadow crossing the glass, left to right
    boilSeed('cloud');
    const c = lerp(x0 - 120, x1 + 260, o.cloud), xs = Math.max(x0, c - 260), xe = Math.min(x1, c);
    if (xe - xs > 4) paint(rectPts(xs, y0, xe - xs, h, 2), { wash: '#A9B0AE', washOp: 85 * Math.sin(Math.PI * o.cloud) * a, ink: null });
  }
  if (o.fog && o.fog.k > .01) glassFog(t, o.fog.k, o.fog.wipe || 0, a);
  boilSeed('win-frame');
  inkLine([[x0, y1], [x0 - 1, y0], [x1, y0 - 2], [x1 + 1, y1], [x0, y1 + 2]], 2.3, fadeCol(C.ink, a, bg), 'ink', .1);
  boilSeed('win-bars');
  inkLine([[(x0 + x1) / 2, y0], [(x0 + x1) / 2 + 1, y1]], 1.3, fadeCol(C.ink, a, bg), 'ink', 0);
  inkLine([[x0, (y0 + y1) / 2 - 20], [x1, (y0 + y1) / 2 - 18]], 1.3, fadeCol(C.ink, a, bg), 'ink', 0);
  boilSeed('win-sill');
  paint(rectPts(x0 - 28, y1, w + 56, 22), { wash: fadeCol(C.wall2, a, bg), ink: fadeCol(C.ink, a, bg), sw: 1.2 });
  if (open > .01) {   // the sash swung into the room: tall trapezoid on the hinge side (right)
    boilSeed('win-sash');
    const sx = 120 * ease(open), sy = 44 * ease(open);
    paint([[x1, y0], [x1 + sx, y0 - sy], [x1 + sx, y1 + sy], [x1, y1]], { wash: fadeCol('#F7EBC0', a, bg), washOp: 200, ink: fadeCol(C.ink, a, bg), sw: 1.5 });
    inkLine([[x1 + sx * .5, y0 - sy * .5], [x1 + sx * .5, y1 + sy * .5]], .9, fadeCol(C.ink, a, bg), 'inkfine', 0);
  }
}
// breath fog on the glass: horizontal bands that a wipe (0..1) clears from the left
function glassFog(t, k, wipe, a) {
  const { x0, x1, y0, y1 } = WIN, n = 9, bh = (y1 - y0) / n;
  for (let i = 0; i < n; i++) {
    boilSeed('fog' + i);
    const d = i * .045, xc = lerp(x0 - 24, x1 + 24, ease(seg(wipe, d, d + .55)));
    if (xc >= x1 + 20) continue;
    const xs = Math.max(x0, xc), yy = y0 + i * bh;
    paint(rectPts(xs, yy - 2, x1 - xs, bh + 5, 3), { wash: C.fog, washOp: 190 * k * a, ink: null });
  }
  if (wipe < .9) for (let i = 0; i < 9; i++) {   // droplets
    boilSeed('drop' + i);
    const dx = x0 + 30 + (w => w * hash(i + 3))(x1 - x0 - 60), dy = y0 + 20 + (h => h * hash(i + 30))(y1 - y0 - 40) + 6 * seg(t, 60, 80) * hash(i);
    if (xc_clear(dx, wipe)) continue;
    paint(ellPts(dx, dy, 3, 5, 8, .4), { wash: C.cream, washOp: 200 * k * a, ink: null });
  }
}
const xc_clear = (x, wipe) => x < lerp(WIN.x0 - 24, WIN.x1 + 24, ease(seg(wipe, .1, .65)));

// ---------- the curtain: cloth with yellow behind the folds; strip = how far it is drawn back; lift = a breath of air ----------
function curtain(t, o = {}) {
  const a = 1 - (o.empty ?? 0); if (a < .02 || !seen(1150, 1900)) return;
  const bg = o.bg || C.wall, strip = o.strip ?? .7, sw = o.sway ?? 1, lift = o.lift ?? 0, yT = 150, yB = 770;
  const xL = 1205, xR = 1500 - 85 * strip, N = 7;
  const sx = (y, ph) => sw * (5 + 4 * lift) * Math.sin(t * .55 + y * .006 + ph);
  const edge = (x, ph, extra) => { const P = []; for (let k = 0; k <= 6; k++) { const f = k / 6, y = yT + (yB - yT) * f; P.push([x + sx(y, ph) * f + extra * f * f, y - (k === 6 ? 78 * lift : 0)]); } return P; };
  const left = edge(xL, 0, 0), right = edge(xR, 1.3, 46 * lift);
  const hem = []; for (let i = N; i >= 0; i--) { const f = i / N; hem.push([lerp(left[6][0], right[6][0], f), lerp(left[6][1], right[6][1], f) + 7 * Math.sin(i * 1.7 + t * .4) + 10 * Math.sin(f * Math.PI) * (1 - lift)]); }
  const outline = [...left, ...hem.slice().reverse().slice(0), ...right.slice().reverse()];
  // outline order: top-left down the left edge, along the hem to the right, up the right edge
  boilSeed('curtain-body');
  paint(outline, { wash: fadeCol(C.cloth, a, bg), ink: fadeCol(C.ink, a, bg), sw: 1.5, curv: 0 });
  const folds = []; for (let i = 1; i < 6; i++) { const f = i / 6, P = []; for (let k = 0; k <= 6; k++) { const L = left[k], R = right[k]; P.push([lerp(L[0], R[0], f) + 6 * Math.sin(k * 1.1 + i * 1.9) * (k / 6), L[1] + (k === 6 ? lerp(0, 0, f) : 0)]); } P[6][1] = lerp(left[6][1], right[6][1], f) + 8 * Math.sin(f * Math.PI); folds.push(P); }
  for (let i = 0; i < folds.length; i += 2) {   // darker cloth between alternate folds
    const A = folds[i], B = folds[Math.min(i + 1, folds.length - 1)];
    boilSeed('curtain-shade' + i);
    paint([...A, ...B.slice().reverse()], { wash: fadeCol(C.clothDk, a, bg), washOp: 90 * a, ink: null });
  }
  for (let i = 0; i < folds.length; i++) { boilSeed('curtain-fold' + i); inkLine(folds[i], .9, fadeCol(C.ink, a * .75, bg), 'inkfine', .5); }
  boilSeed('curtain-rail');
  inkLine([[1170, yT], [1500, yT - 2], [1800, yT]], 2, fadeCol(C.ink, a, bg), 'ink', .1);
  for (let i = 0; i < 7; i++) { boilSeed('ring' + i); paint(ellPts(1215 + i * 48, yT + 6, 5, 8, 8, .3), { wash: fadeCol(C.wall2, a, bg), ink: fadeCol(C.ink, a, bg), sw: .7 }); }
  // yellow behind the cloth (the light comes through the folds)
  const gl = (.34 + .46 * strip + .16 * (o.day ?? 0) + .1 * (o.pulse ?? 0)) * a;
  glow(xR - 70, 430, 300 + 110 * strip, C.glowY, gl);
  glow(1700, 400, 260, C.glowY, (.25 + .3 * strip) * a * .7);
  // a short drape on the other side of the window
  boilSeed('curtain-r');
  const rx = 1738, rs = sx(400, 2.1) * .6;
  paint([[rx, yT + 6], [rx + 70, yT + 6], [rx + 74 + rs, 400], [rx + 70 + rs, yB - 30 - 50 * lift], [rx + 4 + rs, yB - 34 - 50 * lift], [rx + 2, 400]], { wash: fadeCol(C.cloth, a, bg), ink: fadeCol(C.ink, a, bg), sw: 1.3 });
  boilSeed('curtain-r-fold');
  inkLine([[rx + 36, yT + 8], [rx + 38 + rs * .6, 420], [rx + 36 + rs, yB - 38 - 50 * lift]], .8, fadeCol(C.ink, a * .7, bg), 'inkfine', .5);
  boilSeed('curtain-floorlight');   // the strip, lying on the floor
  paint([[1500, 790], [1740, 790], [1560, 1000], [1240, 1040]], { wash: fadeCol(C.day, a, bg), washOp: 90 * a * (.5 + .5 * strip), ink: null });
  motes(t, 1480, 230, 1730, 770, 12, (.5 + .5 * strip) * a, 'cm');
}

// ---------- the lamp: the heartbeat ----------
const LAMP = { x: 860, y: 190 };
function lamp(t, o = {}) {
  const a = 1 - (o.empty ?? 0); if (a < .02 || !seen(560, 1160)) return;
  const bg = o.bg || C.wall, level = o.level ?? .7, lx = LAMP.x + 5 * Math.sin(t * .35);
  boilSeed('lamp-glow');
  glow(lx, 310, 250 + 250 * level, C.glowY, (.3 + .7 * level) * a);
  glow(lx, 340, 640, C.glowPale, (.1 + .25 * level) * a);
  boilSeed('lamp-cord');
  inkLine([[lx, -240], [lx + 1, -20], [lx, 190]], 1.4, fadeCol(C.ink, a, bg), 'ink', 0);
  boilSeed('lamp-shade');
  paint([[lx - 46, 190], [lx + 46, 190], [lx + 92, 278], [lx - 92, 278]], { wash: fadeCol(mixCol(C.shade, '#FFF1C0', level), a, bg), ink: fadeCol(C.ink, a, bg), sw: 1.5 });
  boilSeed('lamp-bulb');
  paint(ellPts(lx, 286, 26, 15, 12, .6), { wash: fadeCol('#FFF3C4', a, bg), ink: null });
  glow(lx, 288, 80 + 50 * level, '#FFF1C0', .55 * a);
}

// ---------- the low bed edge under the window, one pillow on it (a soft square with a seam and a dent), and the room's one shadow ----------
// Everything sits above y 782: the text lane (y 800-980) stays clear of props.
const BED = { x0: 1450, x1: 1880, top: 748, bot: 782 }, PIL = { cx: 1595, cy: 706, w: 190, h: 88 };
function pillow(t, o = {}) {
  const a = 1 - (o.empty ?? 0); if (a < .02 || !seen(1380, 1960)) return;
  const bg = o.bg || C.floor, wb = o.wall || C.wall, br = 1 + .012 * (o.hb ?? 0);
  const { x0, x1, top, bot } = BED, { cx, cy, w, h } = PIL;
  boilSeed('bed');
  paint(rectPts(x0, top, x1 - x0, bot - top, 1.5), { wash: fadeCol('#D8C8A4', a, wb), ink: fadeCol(C.ink, a, wb), sw: 1.4 });
  boilSeed('bed-top');
  inkLine([[x0 + 4, top + 8], [(x0 + x1) / 2, top + 10], [x1 - 4, top + 8]], .8, fadeCol(C.ink, a * .6, wb), 'inkfine', .2);
  const lx = LAMP.x + 5 * Math.sin(t * .35);
  boilSeed('pillow-shadow');   // the one shadow, on the mattress, away from the one light
  paint(ellPts(cx + 32 + (cx - lx) * .03, top + 3, w * .55, 9, 20, 1), { wash: fadeCol(C.graphite, a, wb), washOp: 80 * a, ink: null });
  boilSeed('pillow-body');
  paint(rrPts(cx - w / 2 * br, cy - h / 2 * br, w * br, h * br, 34, 1), { wash: fadeCol(C.pillow, a, wb), ink: fadeCol(C.ink, a, wb), sw: 1.4, curv: .6 });
  boilSeed('pillow-seam');   // a stitched seam just inside the edge
  inkLine(rrPts(cx - w / 2 + 11, cy - h / 2 + 10, w - 22, h - 20, 26, 0), .8, fadeCol(C.ink, a * .55, wb), 'inkfine', .6);
  boilSeed('pillow-dent');   // the dent in the middle
  paint(ellPts(cx, cy + 3, w * .22, h * .2, 16, .6), { wash: fadeCol(C.graphiteLt, a, wb), washOp: 70 * a, ink: null });
  inkLine([[cx - w * .16, cy - 2], [cx, cy + h * .17], [cx + w * .16, cy - 2]], .8, fadeCol(C.ink, a * .5, wb), 'inkfine', .6);
  boilSeed('pillow-light');
  paint(ellPts(cx - 30, cy - 22, 52, 7, 12, .6), { wash: fadeCol(C.cream, a, wb), washOp: 150 * a, ink: null });
}
// the yellowed thread on the bed beside the pillow: a clean ink line with a knot at its start. p = 0 at rest, 1 gone:
// it slides off to the right in one smooth move (0.8 s on "Druck") and does not come back
function thread(t, o = {}) {
  const p = o.p ?? 0, a = 1 - (o.empty ?? 0); if (p >= .999 || a < .02 || !seen(1500, 2800)) return;
  const wb = o.wall || C.wall, dx = 620 * p;
  const P = [[1700, 727], [1730, 735], [1768, 731], [1806, 738], [1846, 733]].map(([x, y]) => [x + dx, y]);
  boilSeed('thread');
  inkLine(P, 1.6, fadeCol(C.thread, a, wb), 'ink', .6);
  boilSeed('thread-knot');
  paint(ellPts(1700 + dx, 727, 4.5, 4.5, 10, .3), { wash: fadeCol(C.thread, a, wb), ink: fadeCol(C.goldDk, a, wb), sw: .6 });
}

// ---------- the paper wall with the repaired seam (the Riss) ----------
const WALL = { x0: 2040, x1: 3900, y0: 110, y1: 810, seamX: 2440 };
const SEAM = [[2452, 128], [2436, 215], [2462, 300], [2430, 390], [2448, 470], [2418, 560], [2440, 640], [2410, 720], [2424, 792]];
const seamCol = l => mixCol(C.goldDk, C.gold, clamp(l));
function paperWall(t, o = {}) {
  if (!seen(WALL.x0 - 40, WALL.x1 + 40)) return;
  const { x0, x1, y0, y1 } = WALL, bg = o.bg || C.wall, lvl = o.lvl ?? .6, g = o.glint || null;
  const xa = Math.max(x0, VIEW[0] - 20), xb = Math.min(x1, VIEW[2] + 20);
  boilSeed('pw-base');
  paint(rectPts(xa, y0, xb - xa, y1 - y0), { wash: '#F0E7CF', ink: null });
  for (const sx of [2040, 2860, 3680]) if (sx > xa - 30 && sx < xb + 30) { boilSeed('pw-stile' + sx); inkLine([[sx, y0 - 8], [sx + 2, (y0 + y1) / 2], [sx, y1 + 8]], 2.4, C.ink, 'ink', .1); }
  for (let x = xa; x < xb; x += 1500) {
    const xe = Math.min(xb, x + 1500), k = Math.round(x / 1500);
    boilSeed('pw-top' + k); inkLine([[x, y0], [(x + xe) / 2, y0 - 2], [xe, y0]], 2.4, C.ink, 'ink', .1);
    boilSeed('pw-bot' + k); inkLine([[x, y1], [(x + xe) / 2, y1 + 2], [xe, y1]], 2.4, C.ink, 'ink', .1);
  }
  if (o.ghost > .01) {   // the room, faintly mirrored in the paper
    boilSeed('pw-ghost-door');
    paint([[2640, 160], [2900, 120], [2900, 840], [2640, 800]], { wash: C.graphiteLt, washOp: 46 * o.ghost, ink: null });
    boilSeed('pw-ghost-win');
    paint(rectPts(2130, 250, 230, 300, 4), { wash: C.graphiteLt, washOp: 40 * o.ghost, ink: null });
    boilSeed('pw-ghost-lamp');
    paint(ellPts(2300, 190, 40, 24, 12, 2), { wash: C.graphiteLt, washOp: 40 * o.ghost, ink: null });
  }
  if (o.wallLight > .01) wallLight(t, o.wallLight);
  // the seam: a line of repair, one gold; its brightness is level l, and a glint (head s 0..1, strength gk) may run along it
  const spans = SEAM.length - 1;
  boilSeed('seam-edge');
  inkLine(SEAM.map(([x, y], i) => [x - 9 + 2 * Math.sin(i), y]), .7, mixCol(C.ink, C.paper, .35), 'inkfine', .5);
  inkLine(SEAM.map(([x, y], i) => [x + 9 + 2 * Math.sin(i + 1), y]), .7, mixCol(C.ink, C.paper, .35), 'inkfine', .5);
  for (let i = 0; i < spans; i++) {
    const s = (i + .5) / spans, b = g ? g.k * Math.exp(-(((s - g.s) / .17) ** 2)) : 0;
    const P = [SEAM[i], [(SEAM[i][0] + SEAM[i + 1][0]) / 2 + 3 * Math.sin(i), (SEAM[i][1] + SEAM[i + 1][1]) / 2], SEAM[i + 1]];
    boilSeed('seam' + i);
    paint(ribbon(P, 8, 6), { wash: seamCol(lvl + (1 - lvl) * b), ink: mixCol(C.goldDk, C.ink, .5), sw: .5 });
  }
  boilSeed('seam-branch');
  inkLine([[2448, 470], [2490, 492], [2530, 520]], 1.6, seamCol(lvl), 'ink', .4);
  if (g && g.k > .02) {   // the glint's own light
    const hy = lerp(SEAM[0][1], SEAM[spans][1], g.s);
    boilSeed('seam-glint');
    glow(WALL.seamX, hy, 120 + 90 * g.k, C.gold, .7 * g.k);
  }
  motes(t, xa, y0 + 30, xb, y1 - 30, 8, .5, 'pm');
}
// warm light lying on the paper wall; k 0..1 spreads from the seam outward (held at 60 %)
function wallLight(t, k) {
  const xs = [2440, 2640, 2240, 2840, 2040, 3040];
  for (let i = 0; i < xs.length; i++) {
    const d = Math.abs(xs[i] - 2440) / 600, kk = clamp(k * 1.3 - d * .55);
    if (kk <= .01) continue;
    boilSeed('wl' + i);
    glow(xs[i], 450 + 20 * Math.sin(t * .4 + i), 260 + 60 * kk, C.glowY, .5 * kk * .6 * 1.6);
  }
}
// a travelling shaft of light, from (x0,y0) toward (x1,y1); head 0..1 how far it has come
function shaft(x0, y0, x1, y1, head, a = 1) {
  const n = 7;
  for (let j = 0; j < n; j++) {
    const f = j / (n - 1), hf = clamp(head * 1.15 - f * .15) , kk = clamp((head - f * .9) * 2.5);
    if (kk <= .01) continue;
    boilSeed('sh' + j);
    glow(lerp(x0, x1, f * head), lerp(y0, y1, f * head), 150 + 60 * f, C.glowY, .5 * kk * a);
  }
}

// ---------- the ping: Clean Ping, one point, once ----------
const PING = { x: 1754, y: 170 };
function ping(t, k = 1, pos = PING, boost = 0) {
  if (k <= .01) return;
  boilSeed('ping');
  glow(pos.x, pos.y, (130 + 90 * boost) * k, C.ping, Math.min(1, .95 + .3 * boost) * k);
  glow(pos.x, pos.y, 46 * k, C.ping, .9 * k);
  paint(ellPts(pos.x, pos.y, 10 * k, 10 * k, 10, .3), { wash: C.ping, ink: null });
}

// ---------- breath fog: a soft watercolour wash that opens and closes ----------
function breathFog(t, cx, cy, k, a = 1) {
  if (k <= .01) return;
  for (let i = 0; i < 6; i++) {
    boilSeed('bf' + i);
    const dx = (hash(i) - .5) * 260 * k + 14 * Math.sin(t * .4 + i), dy = (hash(i + 7) - .5) * 120 * k - 20 * k * i * .2;
    paint(ellPts(cx + dx, cy + dy, (80 + 90 * hash(i + 3)) * k, (50 + 50 * hash(i + 11)) * k, 18, 3), { wash: C.fog, washOp: 90 * k * a, ink: null });
  }
}

// ---------- the room ----------
// o overrides: empty, doorGone, level, strip, lift, sway, open, fog {k, wipe}, thread, seam lvl, glint {s,k}, ghost,
// wallLight, shafts [], mist {x, y, k}, pingK. Everything defaults to worldState(t).
function room(t, o = {}) {
  const S = worldState(t), e = o.empty ?? S.empty, a = 1 - e;
  const bg = mixCol(C.wall, C.paper, e), fbg = mixCol(C.floor, C.paper, e);
  backdrop(t, S, e);
  paperWall(t, { bg, lvl: o.seamLvl ?? .6, glint: o.glint, ghost: o.ghost, wallLight: o.wallLight });
  door(t, { gone: o.doorGone ?? S.doorGone, bg, day: S.daylight });
  windowPane(t, { empty: e, bg, open: o.open, day: S.daylight, fog: o.fog, cloud: o.cloud });
  if (o.patch && o.patch.k > .01) {   // a patch of window light travelling across the floor and up the wall
    const { k, p } = o.patch, px = lerp(1420, 700, ease(seg(p, 0, .7))), py = lerp(920, 470, ease(seg(p, .55, 1)));
    boilSeed('patch');
    paint([[px - 110, py - 55], [px + 90, py - 55], [px + 135, py + 55], [px - 65, py + 55]], { wash: C.day, washOp: 190 * k, ink: null });
    glow(px, py, 340, C.glowY, .7 * k);
  }
  if (o.shafts) for (const s of o.shafts) shaft(...s);
  lamp(t, { empty: e, bg, level: o.level ?? S.level });
  curtain(t, { empty: e, bg, strip: o.strip ?? S.strip, sway: o.sway, lift: o.lift, day: S.daylight, pulse: S.pulseOn * S.hb });
  pillow(t, { empty: e, bg: fbg, wall: bg, hb: S.hb * S.pulseOn });
  thread(t, { p: o.thread ?? S.thread, empty: e, wall: bg });
  if (o.mist) breathFog(t, o.mist.x, o.mist.y, o.mist.k);
  const dk = darkK(t);
  if (dk > .002) {   // night paper: a wash of ink-tinted dark over the whole view; the light point sits on top of it
    boilSeed('night');
    paint(rectPts(VIEW[0], VIEW[1], VIEW[2] - VIEW[0], VIEW[3] - VIEW[1]), { wash: '#35232B', washOp: 255 * dk, ink: null });
    for (let i = 0; i < 4; i++) { boilSeed('nightgrain' + i); paint(ellPts(VIEW[0] + (VIEW[2] - VIEW[0]) * (.2 + .2 * i), VIEW[1] + (VIEW[3] - VIEW[1]) * (.3 + .4 * hash(i + 2)), 380, 220, 16, 6), { wash: '#4A3139', washOp: 60 * dk, ink: null }); }
  }
  ping(t, o.pingK ?? S.pingK, S.pingPos, S.pingBoost);
  if (o.roomLight > .01) {   // daylight lying on the wall and the floor of the room
    boilSeed('rl');
    glow(660, 520, 460, C.glowY, .5 * o.roomLight); glow(1130, 560, 480, C.glowY, .5 * o.roomLight); glow(900, 930, 560, C.glowPale, .45 * o.roomLight);
  }
}

// ---------- transitions and the shot machine ----------
function paperWash(k) {
  if (k <= .004) return;
  boilSeed('wash');
  paint(rectPts(-60, -60, W + 120, H + 120), { wash: C.paper, washOp: 255 * clamp(k), ink: null });
}
// a sliding paper screen: p 0..1; the panel enters from the right and leaves to the left
function shojiWipe(p) {
  if (p <= 0 || p >= 1) return;
  const q = p < .5 ? ease(p * 2) : ease((p - .5) * 2), xe = p < .5 ? lerp(W + 70, -70, q) : -70, xs = p < .5 ? W + 70 : lerp(W + 70, -70, q);
  if (xs - xe < 4) return;
  boilSeed('shoji');
  paint(rectPts(Math.min(xe, xs), -60, Math.abs(xs - xe) + 4, H + 120), { wash: C.paper, washOp: 255, ink: null });
  const edge = p < .5 ? xe : xs;   // the leading edge of the screen: a stile and a rail
  inkLine([[edge, -20], [edge + 3, H / 2], [edge, H + 20]], 2.6, C.ink, 'ink', .1);
  inkLine([[edge + 90 * SC, -20], [edge + 92 * SC, H / 2], [edge + 90 * SC, H + 20]], 1.1, C.graphiteLt, 'inkfine', .1);
  inkLine([[edge - 110 * SC, H * .5], [edge + 90 * SC, H * .5 + 2]], 1.1, C.graphiteLt, 'inkfine', .1);
}
const SD = {};
function defShot(id, d) { SD[id] = d; return (t, lt, dur) => runShot(id, t, lt, dur); }
function runShot(id, t, lt, dur) {
  const d = SD[id], out = d.out || {}, prev = SD[id - 1], pout = prev && prev.out || {};
  let c = d.cam(lt, t, dur);
  let pOut = 0;
  if (out.type === 'slide' || out.type === 'wash' || out.type === 'shoji') pOut = seg(lt, dur - out.dur, dur);
  if (out.type === 'slide') { const n = SD[out.to].cam(0, t, 0), p = ease(pOut); c = [lerp(c[0], n[0], p), lerp(c[1], n[1], p), lerp(c[2], n[2], p)]; }
  camSet(c[0], c[1], c[2]);
  d.world(t, lt, dur);
  camEnd();
  if (d.over) d.over(t, lt, dur);
  // transitions: out
  if (out.type === 'wash') paperWash(ease(pOut));
  else if (out.type === 'slide' && out.wash) paperWash(out.wash * Math.sin(Math.PI * ease(pOut)));
  else if (out.type === 'shoji') shojiWipe(pOut * .5);
  // transitions: in
  if (pout.type === 'wash') paperWash(1 - ease(seg(lt, 0, pout.dur)));
  else if (pout.type === 'shoji') shojiWipe(.5 + .5 * seg(lt, 0, pout.dur));
}

window.HOLDS = [[0, .6], [DUR - 2, DUR]];   // blank paper under the opening notice; the last seconds are blank paper   // the last two seconds are blank paper: a declared hold
