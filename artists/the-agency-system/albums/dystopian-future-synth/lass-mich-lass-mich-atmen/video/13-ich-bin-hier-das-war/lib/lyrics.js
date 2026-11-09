// lyrics.js: the typographic layer of "Ich bin hier / Das war" (STORYBOARD.md, "Lyrics animation" + "Content warning board").
// Owner: typographer. Every time comes from the song map (SONG / SONGMAP.words) at load time; every frame is a pure
// function of t (the layout cache depends only on fonts and the song map, never on the previous frame).
// Drawn after the shot, before the paper grain: film.html wraps drawWorld so that drawLyrics(t) runs right after it.
// Public: drawLyrics(t), lyricInk(t), window.LYRICS_READY.
(function () {
  'use strict';
  const INK = '#2B2233', PAPER = '#F3EBDC', YEL = '#F2C14E', GOLDLT = '#E3AE00', OCHRE = '#9A6B12', PING = '#FCEE0C';
  const FAMILY = '"EB Garamond", Garamond, "Times New Roman", serif';
  const DW = 1920, DH = 1080;

  // ---------- fonts: shipped as files, registered before window.READY ----------
  const LATIN = 'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD';
  const LATINEXT = 'U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF';
  const FACES = [];
  for (const [sub, range] of [['latin', LATIN], ['latin-ext', LATINEXT]])
    for (const w of ['400', '500']) for (const st of ['normal', 'italic'])
      FACES.push([`eb-garamond-${sub}-${w}-${st}.woff2`, st, w, range]);
  async function loadFonts() {
    try {
      await Promise.all(FACES.map(async ([file, style, weight, unicodeRange]) => {
        const ff = new FontFace('EB Garamond', `url(assets/fonts/${file})`, { style, weight, unicodeRange });
        await ff.load(); document.fonts.add(ff);
      }));
      await document.fonts.ready;
    } catch (e) { console.warn('lyrics.js: EB Garamond failed to load, falling back to a system serif', e && e.message); }
  }
  // engine/ is read-only: wrap setup() so that fonts are in before it sets window.READY.
  if (typeof window.setup === 'function') {
    const _setup = window.setup;
    window.setup = async function () { await loadFonts(); return _setup.apply(this, arguments); };
  }

  // ---------- small helpers (the engine's globals: clamp, seg, ease, easeOut, hash, mixCol, W, H) ----------
  const easeIO = x => ease(x);
  const SM = () => (window.SONGMAP && window.SONGMAP.words) || [];
  const LINE = i => (typeof SONG !== 'undefined' && SONG.line(i)) || null;
  const lineT = (i, d = 0) => { const l = LINE(i); return l ? l.t : d; };
  const lineEnd = (i, d = 0) => { const l = LINE(i); return l ? l.end : d; };

  // ---------- ink colour: ink on paper, paper on the dark paper of the bridge ----------
  // dark paper = shot 19 (end of line 16 to the start of line 18); eased in and out so no frame flips.
  function darkK(t) {
    const a = lineEnd(16, 92.8), b = lineT(18, 102.3);
    return easeIO(seg(t, a, a + 1.2)) * (1 - easeIO(seg(t, b - 1.0, b)));
  }
  function lyricInk(t) { const k = darkK(t); return k <= 0.001 ? INK : mixCol(INK, PAPER, k); }
  window.lyricInk = lyricInk;

  // ---------- the layout spec (design space 1920x1080; the text-safe frame is x 160..1760, y 120..960) ----------
  const LOW = { x: 200, y: 855, align: 'left' };         // first row baseline; further rows go below it (inside y 960), clear of the door         // strophes: lower third, left-aligned
  const BESIDE = { x: 1130, y: 850, align: 'left' };      // lower third, to the right of the pillow (shots 2 and 7)
  const UP = { x: 200, y: 230, align: 'left' };          // upper third, where a prop sits low (the pillow, shot 5)
  const CEN = y => ({ x: 960, y, align: 'center' });     // refrains: centred, mid-frame
  const SPECS = [
    { lines: [0], at: BESIDE, size: 64, rows: [3], puls: true, introGlow: true },
    { lines: [1], at: LOW, size: 64, rows: [5], tintWord: 1, evenGlow: true },
    { lines: [2], at: UP, size: 64, rows: [4], thread: 2, exhale: 9, wordK: { 9: .85 } },
    { lines: [3], at: LOW, size: 64, rows: [5], rowK: [1, .8], track: [0, 1, 2, 3, 4, 5] },
    { lines: [4], at: BESIDE, size: 64, rows: [3] },
    { lines: [5], at: CEN(500), size: 150, keyK: 1.2 },
    { lines: [6], at: { x: 880, y: 670, align: 'right' }, size: 96, keyK: 1.2, goldWord: 1 },
    { lines: [7], at: LOW, size: 64, rows: [3], rowAlpha: [.6, 1] },
    { lines: [8], at: CEN(580), size: 150, keyK: 1.2 },
    { lines: [9], at: LOW, size: 64, rows: [4], emph: [8], dim: .82, leaveAt: -.2, leaveTot: .6 },
    { lines: [10], at: LOW, size: 64, rows: [4], floatFrom: 5, leaveAt: .2, leaveTot: .7 },
    { lines: [11], at: UP, size: 64, rows: [4], slide: true },
    { lines: [12], at: LOW, size: 64, rows: [5], leaveAt: -.15, leaveTot: .6 },
    { lines: [13, 14], at: LOW, size: 56, goldSweep: true, leave: 'group' },
    { lines: [15], at: LOW, size: 64, rows: [3], alpha: .6 },
    { lines: [16], at: { x: 700, y: 520, align: 'right' }, size: 110, keyK: 1.2 },
    { lines: [17], at: { x: 1650, y: 190, align: 'right' }, size: 48, ping: true },
    { lines: [18, 19], at: { x: 1180, y: 540, align: 'center' }, size: 104, keyK: 1.2, leave: 'group', leaveHold: 1.2, leaveDur: 2.2 },
    { lines: [20, 21], at: { x: 160, y: 600, align: 'left' }, size: 80, rows: [2], keyK: 1.2, leave: 'rtl' },
  ];
  const KEYK = 84 / 64;

  // ---------- build: words per group, measured at the real fonts (once; depends on fonts + song map only) ----------
  let GROUPS = null, mctx = null;
  const fontOf = (size, key, hero) => key ? `500 ${size}px ${FAMILY}` : `italic 500 ${size}px ${FAMILY}`;
  function build() {
    mctx = document.createElement('canvas').getContext('2d');
    const all = SM();
    GROUPS = SPECS.map(sp => {
      const words = []; let gk = 0;
      for (const li of sp.lines) {
        const L = LINE(li), ws = all.map((w, g) => ({ w, g })).filter(o => o.w.line === li);
        ws.forEach((o, k) => words.push({ g: o.g, line: li, k, n: ws.length, gk: gk++, txt: o.w.w, t: o.w.t, end: o.w.end,
          stress: o.w.stress != null ? o.w.stress : o.w.t, key: !!(L && L.key && Math.abs(L.key.t - o.w.t) < 1e-6) }));
      }
      words.forEach(w => { w.gn = words.length; });
      // appear start; words that would show while the content-warning board is still up wait for it, then come in .3 s apart
      let prev = -1e9; words.forEach(w => { w.at = Math.max(w.t - .12, prev + (w.t - .12 < GATE ? .3 : 0), w.t - .12 < GATE ? GATE : -1e9); prev = w.at; w.stress = Math.max(w.stress, w.at + .45); });
      if (!words.length) return null;
      // rows
      const rows = [[]]; let br = (sp.rows || []).slice();
      words.forEach((w, i) => { rows[rows.length - 1].push(w); if (br.length && br[0] === i) { br.shift(); rows.push([]); } });
      const nR = rows.length, gap = sp.size * 1.27;
      rows.forEach((row, ri) => {
        const rk = (sp.rowK && sp.rowK[ri]) || 1;
        row.forEach(w => {
          w.row = ri; w.isKey = w.key || (sp.emph || []).includes(w.gk);
          w.size = sp.size * rk * (w.isKey ? (sp.keyK || KEYK) : 1) * ((sp.wordK && sp.wordK[w.gk]) || 1);
          w.font = fontOf(w.size, w.isKey);
          mctx.font = w.font; let wd = mctx.measureText(w.txt).width;
          w.w0 = wd; w.tracked = !!(sp.track && sp.track.includes(w.gk));
          w.wR = wd; w.cw = null;                                              // tracked words are re-laid per frame (the sentence breathes)
          w.alpha = ((sp.rowAlpha && sp.rowAlpha[ri]) ?? 1) * (sp.alpha ?? 1) * ((sp.dim && !w.isKey && !(sp.emph || []).includes(w.gk)) ? sp.dim : 1);
          w.base = sp.size * rk;
        });
        const sw = sp.size * rk * .27, rw = row.reduce((s, w) => s + w.wR, 0) + sw * (row.length - 1);
        let x0 = sp.at.align === 'left' ? sp.at.x : sp.at.align === 'right' ? sp.at.x - rw : sp.at.x - rw / 2;
        row.forEach(w => { w.x = x0; w.y = sp.at.y + ri * gap; x0 += w.wR + sw; });
        row.x0 = row[0].x; row.x1 = x0 - sw; row.idx = ri;
      });
      return { sp, words, rows };
    }).filter(Boolean);
  }

  // ---------- one word ----------
  function leaveOf(sp, w) {   // { s, d }: when this word starts to dissolve and for how long
    if (sp.leave === 'group' || sp.leave === 'rtl') {
      const last = sp.lines[sp.lines.length - 1], s = lineEnd(last) + (sp.leaveHold != null ? sp.leaveHold : (sp.leave === 'rtl' ? 0 : .9)), tot = sp.leaveDur || .8;
      const ord = sp.leave === 'rtl' ? (w.gn - 1 - w.gk) : w.gk, dd = Math.min(.5, tot * .6);
      if (sp.leave === 'rtl') return { s: (LINE(21) ? LINE(21).key.stress : s) - .0 + ord / w.gn * (tot * .8 - dd) , d: dd };
      return { s: s + ord / w.gn * (tot - dd), d: dd };
    }
    const e = lineEnd(w.line); let s = e + .9, tot = .8;
    if (sp.leaveAt != null) { s = e + sp.leaveAt; tot = sp.leaveTot || .6; }   // line 9: the shot's brush wipe takes laut verlangt with it; line 12 makes room for line 13
    const dd = Math.min(.4, tot * .55);
    return { s: s + w.k / w.n * (tot - dd), d: dd };
  }
  function wobXY(w, t) {                                   // 0.6 px ink wobble at 12 drawings per second, seeded by word and boil frame
    const f = Math.floor(t * 12 + 1e-6);
    return [(hash(w.g * 3.17 + f * 17.3 + .5) - .5) * 1.2, (hash(w.g * 5.71 + f * 11.9 + 2.5) - .5) * 1.2];
  }
  const glowStyle = (c, rgb, a, blur, off) => { c.shadowColor = `rgba(${rgb},${a})`; c.shadowBlur = blur; c.shadowOffsetX = off; c.shadowOffsetY = 0; };

  function drawWord(c, G, w, t, ink, kk) {
    const sp = G.sp;
    // appear: rises 14 px, 0 -> 1 over 0.45 s ease-out, starting 0.12 s before the word is sung
    const afloat = sp.floatFrom != null && w.gk >= sp.floatFrom, ad = afloat ? .8 : .45, a0 = w.at;
    const ak = easeOut(seg(t, a0, a0 + ad)), rise = (afloat ? 20 : 14) * (1 - ak);
    const lv = leaveOf(sp, w), lk = ease(seg(t, lv.s, lv.s + lv.d));
    let al = ak * (1 - lk) * w.alpha;
    if (al <= .003) return false;
    // settle on the stressed syllable: 3 % swell that eases back over 0.3 s (no overshoot, no jump)
    let sc = 1 + .03 * ease(seg(t, w.stress - .12, w.stress)) * (1 - ease(seg(t, w.stress, w.stress + .3)));
    if (sp.puls && /^Puls/.test(w.txt) && t >= (LINE(0) ? LINE(0).t : 0)) sc *= 1 + .04 * SONG.pulseSoft(t, .12, 5) * (FIRST_BEAT_OK(t) ? 1 : 0);
    let ox = 0, oy = -rise - 10 * lk;
    const [wx, wy] = wobXY(w, t); ox += wx; oy += wy;
    // row effects
    if (sp.slide) {
      const t0 = lineT(11, 70.3), tm = LINE(11) ? LINE(11).key.stress : 73.9, t1 = lineEnd(11, 74.1) + 1.5;
      const r0 = w.row === 0;   // slow drift to the stressed "mir", then the line slides out to the left with the seam
      ox -= (r0 ? 40 : 90) * seg(t, t0, tm) + (r0 ? 220 : 480) * ease(seg(t, tm, t1));
      if (!r0) ox += 60;
    }
    // colour
    let col = ink, tint = 0;
    if (sp.tintWord != null && w.gk === sp.tintWord) {
      const lt = LINE(1) ? LINE(1).key.stress : 25.9;
      tint = easeOut(seg(t, w.t, w.t + .5)) * (1 - ease(seg(t, lt, lt + .7)));
      col = mixCol(ink, OCHRE, tint);
    }
    if (sp.ping && w.isKey) { const ps = w.stress, pk = ease(seg(t, ps - .15, ps + .45)); col = mixCol(ink, PING, .55 * pk); }
    // geometry
    const wr = w.cw != null ? w.cw : w.wR, cx = w.x + wr / 2, by = w.y;
    c.save(); c.translate(cx + ox, by + oy); c.scale(sc, sc); c.font = w.font; c.textAlign = 'left'; c.textBaseline = 'alphabetic';
    const lx = -wr / 2;
    // soft morning-yellow glow, only as a glow (the shadow of text drawn off to the side: no fill ever lands in the picture)
    let gk = 0, grgb = '242,193,78';
    if (w.isKey && sp.lines[0] !== 17) gk = easeOut(seg(t, w.stress - .1, w.stress + .5));
    if (sp.introGlow && w.isKey) gk *= (.6 + .4 * SONG.pulseSoft(t, .12, 5));
    if (sp.evenGlow && t >= (LINE(1) ? LINE(1).key.stress : 25.9)) gk = Math.max(gk, .55 * easeOut(seg(t, 25.9, 26.6)));
    if (sp.ping && w.isKey) { gk = ease(seg(t, w.stress - .15, w.stress + .6)); grgb = '252,238,12'; }
    if (sp.goldWord === w.gk && w.isKey) gk = Math.max(gk, .9 * Math.sin(Math.PI * clamp(seg(t, w.stress - .4, w.stress + 1.1))));
    const OFF = 6000, offL = OFF / (kk * sc);
    c.globalAlpha = al;
    if (gk > .01) {
      const dark = darkK(t) > .5, ga = (dark ? .95 : .85) * gk;
      glowStyle(c, sp.goldWord === w.gk ? '255,223,0' : grgb, ga, w.size * .55, OFF); c.fillStyle = '#000';
      c.fillText(w.txt, lx - offL, 0); c.fillText(w.txt, lx - offL, 0);
      c.shadowColor = 'rgba(0,0,0,0)'; c.shadowBlur = 0; c.shadowOffsetX = 0;
    }
    // fill
    const n = [...w.txt].length;
    if (w.tracked) {
      const trk = trackOf(t) * w.size;
      c.fillStyle = col;
      [...w.txt].forEach((ch, i) => { const px = lx + mctxW(w, i) + i * trk; c.fillText(ch, px, 0); });
    } else if (sp.exhale === w.gk) {
      const s0 = w.stress + .35;
      [...w.txt].forEach((ch, i) => {
        const ls = s0 + (n - 1 - i) / n * .7, k = ease(seg(t, ls, ls + .35));
        if (k >= 1) return; c.globalAlpha = al * (1 - k); c.fillStyle = col;
        c.fillText(ch, lx + mctxW(w, i), -7 * k);
      });
    } else {
      const g = sp.goldWord === w.gk ? goldBand(c, w, t, lx, 0, w.stress - .45, w.stress + 1.0, lx - 20, lx + w.wR + 20, col)
        : sp.goldSweep ? sweepBand(c, G, w, t, cx + ox, sc, lx, col) : col;
      c.fillStyle = g; c.fillText(w.txt, lx, 0);
    }
    // thread under "Faden": a thin ink line that slides out to the left on "Druck"
    if (sp.thread != null && w.gk === 1) { /* drawn once per group in drawThread */ }
    c.restore();
    return true;
  }
  // line 3: letter-spacing opens on "ein" (0 -> +14 %, read as 0.09 em) and closes on "aus"
  function trackOf(t) {
    const e = LINE(3) ? LINE(3).key.stress : 34.9, ein = (SM().find(x => x.line === 3 && /^ein/.test(x.w)) || { t: 33.22 }).t;
    return .09 * (easeIO(seg(t, ein, ein + .9)) - easeIO(seg(t, e - .14, e + .7)));
  }
  function relayTracked(G, t) {
    const sp = G.sp, trk = trackOf(t);
    for (const row of G.rows) {
      if (!row.some(w => w.tracked)) continue;
      const sw = sp.size * .27; let x = sp.at.x;
      for (const w of row) { w.x = x; w.cw = w.w0 + (w.tracked ? [...w.txt].length * trk * w.size : 0); x += w.cw + sw; }
    }
  }
  function FIRST_BEAT_OK(t) { return t >= 2.4; }
  const _pre = new Map();
  function mctxW(w, i) { mctx.font = w.font; return mctx.measureText([...w.txt].slice(0, i).join('')).width; }
  function band(c, x0, x1, base, hot) {
    const g = c.createLinearGradient(x0, 0, x1, 0); g.addColorStop(0, base); g.addColorStop(.5, hot); g.addColorStop(1, base); return g;
  }
  // a thin gold light that runs once through the letters of one word
  function goldBand(c, w, t, lx, _y, ts, te, xa, xb, col) {
    const p = seg(t, ts, te); if (p <= 0 || p >= 1) return col;
    const cxp = xa + (xb - xa) * ease(p), hw = Math.max(18, w.size * .55);
    return band(c, cxp - hw, cxp + hw, col, mixCol(col, GOLDLT, .9));
  }
  // lines 13-14: one gold light travels through the whole row as it travels across the seam
  function sweepBand(c, G, w, t, absCx, sc, lx, col) {
    const row = G.rows[w.row], ts = lineT(13, 78.6) + .5, te = lineEnd(14, 82.5) + .35, p = seg(t, ts, te); if (p <= 0 || p >= 1) return col;
    const abs = row.x0 - 120 + (row.x1 - row.x0 + 240) * ease(p), hw = 130, off = (abs - absCx) / sc;
    return band(c, off - hw, off + hw, col, mixCol(col, GOLDLT, .9));
  }
  // thread under "Faden" (line 2)
  function drawThread(c, G, t, ink, kk) {
    const w = G.words[1]; if (!w) return;
    const a0 = w.t - .12, ak = easeOut(seg(t, a0, a0 + .45)), dr = LINE(2).key.stress;
    const slide = Math.pow(seg(t, dr - .05, dr + 1.15), 2.2), lk = ease(seg(t, dr + .5, dr + 1.15));
    const al = ak * (1 - lk) * .85; if (al <= .003) return;
    const x0 = w.x - 18 - slide * 1500, x1 = w.x + w.wR + 150 - slide * 1500, y = w.y + 13 + (hash(Math.floor(t * 12)) - .5) * .8;
    c.save(); c.globalAlpha = al; c.strokeStyle = ink; c.lineWidth = 2; c.lineCap = 'round'; c.beginPath(); c.moveTo(x0, y);
    c.bezierCurveTo(x0 + (x1 - x0) * .3, y + 5, x0 + (x1 - x0) * .6, y - 5, x1, y + 1); c.stroke(); c.restore();
  }

  // ---------- the content-warning board (shot 0, 0.0-2.3 s): opaque paper board, three lines, then it fades ----------
  const BOARD = [
    { txt: 'Dieses Album behandelt sexualisierte Gewalt in der Kindheit.', size: 64, y: 500, alpha: 1, gap: 84 },
    { txt: 'Hör nur zu, wenn du dich sicher fühlst.', size: 52, y: 620, alpha: .9 },
  ];
  function wrapLines(c, txt, maxW) {
    const ws = txt.split(' '), rows = []; let cur = '';
    for (const w of ws) { const tst = cur ? cur + ' ' + w : w; if (cur && c.measureText(tst).width > maxW) { rows.push(cur); cur = w; } else cur = tst; }
    rows.push(cur); return rows;
  }
  const BOARD_END = 4.8, BOARD_FADE0 = 4.0, BOARD_STEP = .5, BOARD_IN0 = .2, BOARD_IN = .5;
  const GATE = BOARD_FADE0 + (BOARD_END - BOARD_FADE0) * .68;   // board opacity is below 0.3 from here; no lyric word appears before it
  function drawBoard(c, t, kk) {
    if (t >= BOARD_END) return;
    const ba = 1 - ease(seg(t, BOARD_FADE0, BOARD_END));
    c.save(); c.globalAlpha = ba;
    const pg = window.__paperSrc && window.__paperSrc();
    if (pg) c.drawImage(pg, 0, 0, DW, DH); else { c.fillStyle = PAPER; c.fillRect(0, 0, DW, DH); }
    BOARD.forEach((b, i) => {
      const a = ease(seg(t, BOARD_IN0 + i * BOARD_STEP, BOARD_IN0 + i * BOARD_STEP + BOARD_IN)) * ba * b.alpha;
      if (a <= .003) return;
      c.font = `italic 500 ${b.size}px ${FAMILY}`; c.textAlign = 'center'; c.textBaseline = 'alphabetic'; c.fillStyle = INK;
      const rows = b.wrap ? wrapLines(c, b.txt, b.wrap) : [b.txt], f = Math.floor(t * 12 + 1e-6);
      c.globalAlpha = a;
      rows.forEach((r, ri) => c.fillText(r, 960 + (hash(i * 7 + f * 3.3) - .5) * 1.0, b.y + ri * (b.gap || 0) + (hash(i * 5 + f * 9.1) - .5) * 1.0));
    });
    // a hairline above the notice (paper-ruled, no ornament)
    const ha = ease(seg(t, BOARD_IN0, BOARD_IN0 + BOARD_IN)) * ba * .5;
    c.globalAlpha = ha; c.strokeStyle = INK; c.lineWidth = 1.5; c.beginPath(); c.moveTo(900, 400); c.lineTo(1020, 400); c.stroke();
    c.restore();
  }

  // ---------- the frame ----------
  let lyG = null;
  function drawLyrics(t) {
    if (!window.SONGMAP) return;
    if (!GROUPS) build();
    if (!lyG) { lyG = createGraphics(W, H); lyG.pixelDensity(1); }
    const c = lyG.drawingContext, kk = Math.min(W / DW, H / DH), ink = lyricInk(t);
    c.setTransform(1, 0, 0, 1, 0, 0); c.clearRect(0, 0, W, H);
    c.save(); c.translate((W - DW * kk) / 2, (H - DH * kk) / 2); c.scale(kk, kk);
    let any = false;
    for (const G of GROUPS) {
      const sp = G.sp, a = G.words[0].at - .1, lastW = G.words[G.words.length - 1];
      const lv = leaveOf(sp, G.words.reduce((m, w) => (leaveOf(sp, w).s > leaveOf(sp, m).s ? w : m), G.words[0]));
      if (t < a || t > lv.s + lv.d + .1) continue;
      if (sp.track) relayTracked(G, t);
      for (const w of G.words) if (drawWord(c, G, w, t, ink, kk)) any = true;
      if (sp.thread != null) { drawThread(c, G, t, ink, kk); any = true; }
    }
    if (t < BOARD_END) { drawBoard(c, t, kk); any = true; }
    c.restore();
    if (!any) return;
    if (typeof flushBrush === 'function') flushBrush();
    push(); resetMatrix(); translate(-W / 2, -H / 2); image(lyG, 0, 0); pop();
  }
  window.drawLyrics = drawLyrics;
  window.__paperSrc = () => (typeof paperG !== 'undefined' && paperG) ? (paperG.elt || paperG.canvas) : null;
  window.LYRICS_READY = true;
})();
