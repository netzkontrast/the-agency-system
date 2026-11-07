#!/usr/bin/env node
// scripts/edge-audit.mjs : find pictures and shapes cut by an edge, the frame's or a window's inside it.
//
//   node <skill>/scripts/edge-audit.mjs [film.html] [--step 0.1] [--min 0.8] [--json out.json] [--shots dir]
//   node <skill>/scripts/edge-audit.mjs --self-test
//
// The text audit already catches words that leave the frame. This catches everything else: a card, an icon, a photo,
// a panel or a person's picture cut by the frame's edge or by the edge of a window drawn inside the film (a player, a
// phone screen, a browser), and held there. A cropped card reads as a mistake.
//
// It loads the film in headless Chrome and records, for every sampled frame, each drawImage, fillRect / strokeRect and
// fill / stroke the film makes on a frame-size canvas: where it lands on screen and which clip window it was drawn in
// (rect, roundRect, arc and path clips are followed through save and restore). An item counts as CUT when one side of it
// runs past its window by more than 1 % of its size and 3 px. It reports an item that sits still while cut for --min
// seconds (default 0.8). Left alone, on purpose:
//   - anything that fills its window, or runs past both opposite sides of it (a backdrop, a strip, a long timeline)
//   - anything moving (more than 0.6 % of the frame's width between samples): an entrance, an exit, a pan
//   - anything mostly out of its window (under 15 % of it showing): it is arriving or leaving
//   - specks and hairlines (under 1.5 % of the frame's height across)
//   - draws made while the page sets window.EDGE_AUDIT_SKIP = true (texture, a film replayed inside the film)
//
// Inside pictures too: for every picture big enough to hold a screen (2 % of the frame or more, footage of a product, a
// screen recording), it reads the pixels along each of its edges and reports content that runs into one: a label, a
// card or a panel crossing the edge instead of sitting inside it with a margin. This is what a slow push into footage
// does to the labels at its sides. "its own edge" means the picture itself was not cropped there: the cut is in the
// footage (re-cut it with content-box.py), not made by the film's zoom or window.
//
// Every line is a WARN: a lead to look at, never a stop. Open the frame (frames.mjs, or --shots) and either fix it
// (move it in, make it smaller, keep a clear margin) or say why it stays. Exit is 0 unless the film cannot be loaded.
// Limits: a photograph's edge is full of picture, so a photo can raise a "runs into" line that is not a mistake, and a
// line drawn edge to edge on purpose reads the same as a cut one: look at the frame. Clips made from a Path2D are
// skipped, and something painted over the cut later still counts.
import fs from 'node:fs';
import os from 'node:os';
import http from 'node:http';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const SELF = fileURLToPath(import.meta.url);
const args = process.argv.slice(2);
if (args.includes('--self-test')) process.exit(selfTest());
const opt = (name, def) => { const i = args.indexOf('--' + name); if (i < 0) return def; const v = args[i + 1]; args.splice(i, 2); return v; };
const STEP = Number(opt('step', 0.1)), MIN = Number(opt('min', 0.8)), JSON_OUT = opt('json', null), SHOTS = opt('shots', null);
const film = path.resolve(args[0] || 'film.html');
if (!fs.existsSync(film)) { console.error(`edge-audit: no film at ${film}\nusage: node edge-audit.mjs [film.html] [--step 0.1] [--min 0.8] [--json out.json] [--shots dir]`); process.exit(2); }
const loadChromium = () => {
  for (const r of [process.env.PLAYWRIGHT_NODE_MODULES, path.join(path.dirname(film), 'node_modules'), path.join(process.cwd(), 'node_modules'), path.join(path.dirname(SELF), 'node_modules')].filter(Boolean)) {
    try { return createRequire(path.join(r, 'x.cjs'))('playwright-core').chromium; } catch { /* next */ } }
  try { return createRequire(SELF)('playwright-core').chromium; } catch { /* fall through */ }
  console.error('edge-audit: playwright-core not found. Run it from the film project folder (new-canvas-project.sh installs it there), or set PLAYWRIGHT_NODE_MODULES.'); process.exit(2);
};
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.css': 'text/css', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf', '.mp4': 'video/mp4', '.wav': 'audio/wav', '.mp3': 'audio/mpeg' };
const serve = (root) => new Promise((res) => { const srv = http.createServer((req, rs) => {
  // only files inside the film folder: a neighbour folder whose name starts the same way is refused too
  let p = ''; try { p = path.join(root, decodeURIComponent(new URL(req.url, 'http://x').pathname)); } catch {}
  if ((p !== root && !p.startsWith(root + path.sep)) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { rs.writeHead(404); return rs.end(); }
  rs.writeHead(200, { 'content-type': TYPES[path.extname(p).toLowerCase()] || 'application/octet-stream' }); fs.createReadStream(p).pipe(rs); });
  srv.listen(0, '127.0.0.1', () => res({ srv, url: `http://127.0.0.1:${srv.address().port}` })); });

const { srv, url } = await serve(path.dirname(film));
const browser = await loadChromium().launch({ channel: 'chrome', headless: true });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
// follow each context's clip window (through save / restore) and record where every picture and shape lands
await page.addInitScript(() => {
  const P = CanvasRenderingContext2D.prototype, st = new WeakMap();
  const S = (c) => { let s = st.get(c); if (!s) { s = { clip: null, stack: [], path: null }; st.set(c, s); } return s; };
  const pt = (c, x, y) => { const t = c.getTransform(); return [t.a * x + t.c * y + t.e, t.b * x + t.d * y + t.f]; };
  const grow = (b, p) => (b ? [Math.min(b[0], p[0]), Math.min(b[1], p[1]), Math.max(b[2], p[0]), Math.max(b[3], p[1])] : [p[0], p[1], p[0], p[1]]);
  const box = (c, pts) => { let b = null; for (const [x, y] of pts) b = grow(b, pt(c, x, y)); return b; };
  const rp = (x, y, w, h) => [[x, y], [x + w, y], [x, y + h], [x + w, y + h]];
  const meet = (a, b) => (!a ? b : !b ? a : [Math.max(a[0], b[0]), Math.max(a[1], b[1]), Math.min(a[2], b[2]), Math.min(a[3], b[3])]);
  const add = (c, pts) => { const s = S(c), b = box(c, pts); s.path = s.path ? grow(grow(s.path, [b[0], b[1]]), [b[2], b[3]]) : b; };
  const wrap = (fn, pre) => { const orig = P[fn]; if (!orig) return; P[fn] = function (...a) { try { pre.call(this, ...a); } catch { /* never break the film's drawing */ } return orig.apply(this, a); }; };
  wrap('save', function () { const s = S(this); s.stack.push(s.clip); });
  wrap('restore', function () { const s = S(this); if (s.stack.length) s.clip = s.stack.pop(); });
  wrap('reset', function () { st.delete(this); });
  wrap('beginPath', function () { S(this).path = null; });
  wrap('moveTo', function (x, y) { add(this, [[x, y]]); });
  wrap('lineTo', function (x, y) { add(this, [[x, y]]); });
  wrap('rect', function (x, y, w, h) { add(this, rp(x, y, w, h)); });
  wrap('roundRect', function (x, y, w, h) { add(this, rp(x, y, w, h)); });
  wrap('arc', function (x, y, r) { add(this, rp(x - r, y - r, 2 * r, 2 * r)); });
  wrap('ellipse', function (x, y, rx, ry) { const r = Math.max(rx, ry); add(this, rp(x - r, y - r, 2 * r, 2 * r)); });
  wrap('arcTo', function (x1, y1, x2, y2) { add(this, [[x1, y1], [x2, y2]]); });
  wrap('quadraticCurveTo', function (a, b, x, y) { add(this, [[a, b], [x, y]]); });
  wrap('bezierCurveTo', function (a, b, c, d, x, y) { add(this, [[a, b], [c, d], [x, y]]); });
  wrap('clip', function (a) { const s = S(this); if (s.clip === 'path2d') return; s.clip = a instanceof Path2D ? 'path2d' : s.path ? meet(s.clip, s.path) : s.clip; });
  const rec = (c, kind, id, b, crop) => {
    if (!window.__EA_ON || window.EDGE_AUDIT_SKIP || !b || id == null || c.globalAlpha < 0.3) return;
    if (c.canvas.width !== window.__EA_W || c.canvas.height !== window.__EA_H) return;   // pictures built off screen are judged where they land
    const clip = S(c).clip; if (clip === 'path2d') return;
    window.__EA.push({ kind, id, crop, b: b.map((v) => Math.round(v * 10) / 10), clip: clip && clip.map((v) => Math.round(v * 10) / 10) });
  };
  const style = (v) => (typeof v === 'string' ? v : null);   // a gradient or pattern fill is a light, a glow or a vignette, not an object
  const srcName = (img) => { const s = img.currentSrc || img.src || ''; if (s) return decodeURIComponent(s.split('/').pop().split('?')[0]).slice(0, 40);
    const w = img.videoWidth || img.naturalWidth || img.width, h = img.videoHeight || img.naturalHeight || img.height; return `${img.constructor.name.replace(/^HTML|Element$/g, '')} ${w}x${h}`; };
  wrap('drawImage', function (img, ...a) {
    const nw = img.videoWidth || img.naturalWidth || img.width || 0, nh = img.videoHeight || img.naturalHeight || img.height || 0;
    const [dx, dy, dw, dh] = a.length >= 8 ? a.slice(4, 8) : a.length >= 4 ? a.slice(0, 4) : [a[0], a[1], nw, nh];
    const [sx, sy, sw, sh] = a.length >= 8 ? a.slice(0, 4) : [0, 0, nw, nh];   // which sides of the source were cropped away
    if (img.width === window.__EA_W && img.height === window.__EA_H && Math.abs(dw - nw) < 1 && Math.abs(dh - nh) < 1 && Math.abs(dx) < 1 && Math.abs(dy) < 1) return;   // a frame-size buffer laid down whole
    rec(this, 'picture', srcName(img), box(this, rp(dx, dy, dw, dh)), [sx > 0.5, sy > 0.5, sx + sw < nw - 0.5, sy + sh < nh - 0.5]);
  });
  wrap('fillRect', function (x, y, w, h) { rec(this, 'shape', style(this.fillStyle), box(this, rp(x, y, w, h))); });
  wrap('strokeRect', function (x, y, w, h) { rec(this, 'shape', style(this.strokeStyle), box(this, rp(x, y, w, h))); });
  wrap('fill', function (a) { if (!(a instanceof Path2D)) rec(this, 'shape', style(this.fillStyle), S(this).path); });
  wrap('stroke', function (a) { if (!(a instanceof Path2D)) rec(this, 'shape', style(this.strokeStyle), S(this).path); });
});
const errs = []; page.on('pageerror', (e) => errs.push(e.message));
await page.goto(url + '/' + path.basename(film));
await page.waitForFunction(() => typeof window.renderFrame === 'function' && window.READY === true, null, { timeout: 120000 });
const { W, H, D } = await page.evaluate(() => { const c = [...document.querySelectorAll('canvas')].sort((a, b) => b.width * b.height - a.width * a.height)[0];
  window.__EA_W = c.width; window.__EA_H = c.height; window.__EA_C = c; return { W: c.width, H: c.height, D: window.FILM_DURATION }; });
const n = Math.floor(D / STEP);
// and, for every picture big enough to hold a screen (2 % of the frame or more), whether its content runs into one of its edges
const samples = await page.evaluate(async ({ n, STEP }) => { const out = [], W = window.__EA_W, H = window.__EA_H, F = [0, 0, W, H], g = window.__EA_C.getContext('2d');
  const meet = (a, b) => [Math.max(a[0], b[0]), Math.max(a[1], b[1]), Math.min(a[2], b[2]), Math.min(a[3], b[3])];
  // along one side: the ground is the usual brightness 9 px in. Content touches the edge where it differs from the ground both
  // close to the edge (somewhere 3 to 15 px in, so an edge that fades into the screen still counts) and 32 to 36 px in (a card's
  // border or a line of text crossing the edge, not a line running along it). A band that is mostly not one ground (a photograph,
  // a busy scene) is left alone: its edge is picture, not a layout.
  const touch = (px, v, side) => {
    const vert = side === 'left' || side === 'right', L = vert ? v[3] - v[1] : v[2] - v[0];
    const at = (s, d) => { const x = side === 'left' ? v[0] + d : side === 'right' ? v[2] - 1 - d : v[0] + s, y = side === 'top' ? v[1] + d : side === 'bottom' ? v[3] - 1 - d : v[1] + s;
      const k = (y * W + x) * 4; return (0.2126 * px[k] + 0.7152 * px[k + 1] + 0.0722 * px[k + 2]) / 255; };
    const mid = [], near = [], deep = [];
    for (let s = 4; s < L - 4; s++) { mid.push(at(s, 9)); near.push([3, 6, 9, 12, 15].map((d) => at(s, d))); deep.push((at(s, 32) + at(s, 34) + at(s, 36)) / 3); }
    if (mid.length < 30) return null;
    const gr = [...mid].sort((a, b) => a - b)[mid.length >> 1];
    if (mid.filter((x) => Math.abs(x - gr) < 0.05).length < 0.6 * mid.length) return null;
    const runs = []; let r = null;
    for (let s = 0; s < mid.length; s++) { const on = Math.max(...near[s].map((x) => Math.abs(x - gr))) > 0.12 && Math.abs(deep[s] - gr) > 0.12;
      if (on) { if (r && s - r[1] <= 2) r[1] = s; else { r = [s, s]; runs.push(r); } } }
    const kept = runs.filter(([a, b]) => b - a + 1 >= 2 && b - a + 1 <= 0.4 * mid.length);
    return kept.length ? { runs: kept.length, at: Math.round((vert ? v[1] : v[0]) + 4 + (kept[0][0] + kept[0][1]) / 2) } : null;
  };
  for (let i = 0; i <= n; i++) { const t = Math.min(i * STEP, window.FILM_DURATION - 1e-3); window.__EA = []; window.__EA_ON = true; await window.renderFrame(t); window.__EA_ON = false;
    const into = [], seen = new Set(); let px = null;
    for (const d of window.__EA) { if (d.kind !== 'picture') continue;
      const win = d.clip ? meet(d.clip, F) : F, v = meet(d.b, win).map(Math.round), w = v[2] - v[0], h = v[3] - v[1];
      if (w < 100 || h < 100 || w * h < 0.02 * W * H || (w >= W - 1 && h >= H - 1) || seen.has(v.join())) continue; seen.add(v.join());   // a picture filling the frame: its edges are the frame's, checked above
      px = px || g.getImageData(0, 0, W, H).data;
      ['left', 'top', 'right', 'bottom'].forEach((side, j) => { const r = touch(px, v, side); if (!r) return;
        const cropped = d.crop[j] || Math.abs(v[j] - d.b[j]) > 1;   // the picture was cut on this side: by its source crop, its window or the frame
        into.push({ id: d.id, v, side, cropped, ...r }); }); }
    out.push({ t, d: window.__EA, into }); }
  return out; }, { n, STEP });

// judge each draw: what it was cut by, on which side, by how much
const FRAME = [0, 0, W, H], meet = (a, b) => [Math.max(a[0], b[0]), Math.max(a[1], b[1]), Math.min(a[2], b[2]), Math.min(a[3], b[3])];
const area = (b) => Math.max(0, b[2] - b[0]) * Math.max(0, b[3] - b[1]);
const cutOf = (d) => {
  const win = d.clip ? meet(d.clip, FRAME) : FRAME, b = d.b, w = b[2] - b[0], h = b[3] - b[1];
  if (w < 0.015 * H || h < 0.015 * H || area(win) <= 0) return null;                                   // a speck or a hairline
  const vis = meet(b, win); if (area(vis) < 0.15 * area(b)) return null;                               // arriving or leaving
  const L = win[0] - b[0], R = b[2] - win[2], T = win[1] - b[1], B = b[3] - win[3];
  const past = (o, size) => o > Math.max(3, 0.01 * size);
  const l = past(L, w), r = past(R, w), t = past(T, h), bt = past(B, h);
  if ((l && r) || (t && bt)) return null;                                                               // fills its window, or runs right through it
  const sides = [l && ['left', L, w], r && ['right', R, w], t && ['top', T, h], bt && ['bottom', B, h]].filter(Boolean);
  if (!sides.length) return null;
  const inner = d.clip && (win[0] > 1 || win[1] > 1 || win[2] < W - 1 || win[3] < H - 1);
  return { by: inner ? `the window at ${win.map(Math.round).join(',')}` : 'the frame', sides: sides.map(([s, o, size]) => `${s} ${Math.round(o)} px (${Math.round(o / size * 100)}%)`).join(', '), win };
};
// join samples into still runs: the same item (kind, id, size) in the same place, cut the same way
const runs = [], open = [];
for (const smp of samples) {
  const used = new Set();
  for (const d of smp.d) { const c = cutOf(d); if (!c) continue;
    const w = d.b[2] - d.b[0], h = d.b[3] - d.b[1], cx = (d.b[0] + d.b[2]) / 2, cy = (d.b[1] + d.b[3]) / 2, k = `${d.kind}|${d.id}|${c.by}`;
    let r = open.find((o) => !used.has(o) && o.k === k && smp.t - o.t1 < STEP * 2.5 && Math.abs(o.w - w) < 0.02 * W && Math.abs(o.h - h) < 0.02 * H && Math.hypot(o.cx - cx, o.cy - cy) < 0.006 * W);
    if (!r) { r = { k, kind: d.kind, id: d.id, by: c.by, sides: c.sides, b: d.b, t0: smp.t, t1: smp.t, held: 0 }; open.push(r); runs.push(r); }
    else r.held += smp.t - r.t1;
    used.add(r); Object.assign(r, { t1: smp.t, w, h, cx, cy, b: d.b, sides: c.sides });
  }
  for (let i = open.length - 1; i >= 0; i--) if (smp.t - open[i].t1 >= STEP * 2.5) open.splice(i, 1);
}
// one line per item and stretch of time: overlapping runs of the same item (several strokes of one card) are one finding
const kept = runs.filter((r) => r.held + STEP >= MIN - 1e-6).sort((a, b) => a.t0 - b.t0), finds = [];
for (const r of kept) { const same = finds.find((f) => f.by === r.by && r.t0 <= f.t1 + STEP && r.t1 >= f.t0 - STEP && Math.abs((f.b[0] + f.b[2]) / 2 - (r.b[0] + r.b[2]) / 2) < 0.1 * W && Math.abs((f.b[1] + f.b[3]) / 2 - (r.b[1] + r.b[3]) / 2) < 0.1 * H);
  if (same) { same.t0 = Math.min(same.t0, r.t0); same.t1 = Math.max(same.t1, r.t1); same.items.add(`${r.kind} ${r.id}`); continue; }
  finds.push({ t0: r.t0, t1: r.t1, by: r.by, sides: r.sides, b: r.b, items: new Set([`${r.kind} ${r.id}`]) }); }

// content running into a picture's edge: the same side of the same window, held still
const touches = [], openT = [];
for (const smp of samples) {
  for (const x of smp.into) {   // followed as the picture drifts (a slow push moves its box a little every frame)
    let r = openT.find((o) => o.side === x.side && smp.t - o.t1 < STEP * 2.5 && o.v.every((c, j) => Math.abs(c - x.v[j]) < 0.0125 * W));
    if (!r) { r = { side: x.side, v: x.v, id: x.id, t0: smp.t, t1: smp.t, held: 0, cropped: 0, n: 0, runs: 0, at: x.at }; openT.push(r); touches.push(r); }
    else r.held += smp.t - r.t1;
    r.t1 = smp.t; r.v = x.v; r.n++; r.cropped += x.cropped ? 1 : 0; r.runs = Math.max(r.runs, x.runs); }
  for (let i = openT.length - 1; i >= 0; i--) if (smp.t - openT[i].t1 >= STEP * 2.5) openT.splice(i, 1);
}
const into = touches.filter((r) => r.held + STEP >= MIN - 1e-6).sort((a, b) => a.t0 - b.t0);
const f1 = (t) => t.toFixed(1);
console.log(`EDGE AUDIT   ${path.basename(film)}   ${W}x${H}, ${f1(D)} s, a sample every ${STEP} s, held cut ${MIN} s or more`);
if (errs.length) console.log('  page errors while drawing: ' + errs.slice(0, 3).join(' | '));
for (const x of finds) { const items = [...x.items], what = items.slice(0, 2).join(' + ') + (items.length > 2 ? ` + ${items.length - 2} more` : '');
  console.log(`  WARN  ${(f1(x.t0) + '-' + f1(Math.min(D, x.t1 + STEP)) + ' s').padEnd(13)} cut by ${x.by}, ${x.sides}   ${what}   at ${x.b.map(Math.round).join(',')}`); }
for (const x of into) console.log(`  WARN  ${(f1(x.t0) + '-' + f1(Math.min(D, x.t1 + STEP)) + ' s').padEnd(13)} content runs into the ${x.side} edge of a picture (${x.runs} place${x.runs > 1 ? 's' : ''}, first at ${x.at})${x.cropped * 2 >= x.n ? '' : ', its own edge'}   ${x.id}   at ${x.v.join(',')}`);
const total = finds.length + into.length;
console.log(total ? `EDGE AUDIT: ${total} to look at` : 'EDGE AUDIT: nothing cut');
const shots = [...finds.map((x) => ({ t0: x.t0, t1: x.t1, b: x.b, by: x.by })), ...into.map((x) => ({ t0: x.t0, t1: x.t1, b: x.v, by: '', side: x.side }))];
if (SHOTS && shots.length) {   // the frame in the middle of each finding: the item in red, its window in yellow, the side content runs into in magenta
  fs.mkdirSync(SHOTS, { recursive: true });
  for (const [i, x] of shots.entries()) { const t = (x.t0 + x.t1) / 2;
    const png = await page.evaluate(async ({ t, b, by, side }) => { await window.renderFrame(t);
      const src = [...document.querySelectorAll('canvas')].sort((p, q) => q.width * q.height - p.width * p.height)[0], c = document.createElement('canvas'); c.width = src.width; c.height = src.height;
      const g = c.getContext('2d'); g.drawImage(src, 0, 0); g.lineWidth = Math.max(3, src.width / 400);
      const m = /window at ([\d.-]+),([\d.-]+),([\d.-]+),([\d.-]+)/.exec(by); if (m) { const [a, b2, c2, d2] = m.slice(1).map(Number); g.strokeStyle = '#ffd400'; g.strokeRect(a, b2, c2 - a, d2 - b2); }
      g.strokeStyle = '#ff2020'; g.strokeRect(b[0], b[1], b[2] - b[0], b[3] - b[1]);
      if (side) { g.strokeStyle = '#ff00ff'; g.lineWidth *= 3; g.beginPath(); const [x0, y0, x1, y1] = b;
        if (side === 'left') { g.moveTo(x0, y0); g.lineTo(x0, y1); } else if (side === 'right') { g.moveTo(x1, y0); g.lineTo(x1, y1); } else if (side === 'top') { g.moveTo(x0, y0); g.lineTo(x1, y0); } else { g.moveTo(x0, y1); g.lineTo(x1, y1); } g.stroke(); }
      return c.toDataURL('image/jpeg', 0.8); }, { t, b: x.b, by: x.by, side: x.side });
    const out = path.join(SHOTS, `edge-${String(i + 1).padStart(2, '0')}-${f1(t)}s.jpg`); fs.writeFileSync(out, Buffer.from(png.split(',')[1], 'base64')); }
  console.log(`  frames with each finding outlined: ${SHOTS}`);
}
await browser.close(); srv.close();
if (JSON_OUT) fs.writeFileSync(JSON_OUT, JSON.stringify({ film: path.basename(film), W, H, D, step: STEP, min: MIN, finds: finds.map((x) => ({ ...x, items: [...x.items] })), into }, null, 1));
process.exit(0);

// a small film with two cuts the audit must find and six things it must leave alone
function selfTest() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'edge-audit-')), html = path.join(dir, 'film.html');
  fs.writeFileSync(html, `<!doctype html><canvas id="c" width="640" height="360"></canvas><script>
const c = document.getElementById('c'), g = c.getContext('2d'), icon = document.createElement('canvas'); icon.width = icon.height = 80;
icon.getContext('2d').fillRect(0, 0, 80, 80);
window.FILM_DURATION = 3;
window.renderFrame = (t) => {
  g.fillStyle = '#eee'; g.fillRect(0, 0, 640, 360);                                  // backdrop: fills the frame
  g.save(); g.beginPath(); g.roundRect(100, 60, 300, 200, 12); g.clip();
  g.fillStyle = '#222'; g.fillRect(90, 50, 320, 220);                                  // the player's ground: fills its window
  g.fillStyle = '#c33'; g.beginPath(); g.roundRect(320, 120, 140, 60, 8); g.fill();    // CUT 1: a card past the player's right edge
  g.fillStyle = '#39c'; g.fillRect(50, 200, 400, 30);                                  // a strip right through the player
  g.restore();
  g.fillStyle = '#3a3'; g.fillRect(-200 + t * 300, 290, 120, 40);                      // a card sliding across: moving
  g.drawImage(icon, 600, 20);                                                          // CUT 2: an icon past the frame's right edge
  g.fillStyle = '#000'; g.fillRect(636, 200, 6, 6);                                    // a speck at the edge
  g.fillRect(-170, 120, 180, 50);                                                      // a card almost all out: arriving
  window.EDGE_AUDIT_SKIP = true; g.fillRect(560, 300, 120, 40); window.EDGE_AUDIT_SKIP = false;   // skipped on purpose
};
window.READY = true;
</script>`);
  const r = spawnSync(process.execPath, [SELF, html], { encoding: 'utf8', cwd: process.cwd() });
  fs.rmSync(dir, { recursive: true, force: true });
  const out = (r.stdout || '') + (r.stderr || ''), warns = out.split('\n').filter((l) => l.includes('WARN'));
  const ok = r.status === 0 && warns.length === 2 && warns.some((l) => /window at 100,60,400,260, right 60 px/.test(l)) && warns.some((l) => /the frame, right 40 px/.test(l));
  console.log(out.trim()); console.log(ok ? 'edge-audit self-test: PASS (found both cuts, left the other six alone)' : 'edge-audit self-test: FAIL');
  return ok ? 0 : 1;
}
