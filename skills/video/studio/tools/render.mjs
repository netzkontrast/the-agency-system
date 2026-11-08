#!/usr/bin/env node
// tools/render.mjs — the studio's one renderer for every film that follows the film contract
// (references/film-contract.md: window.FILM_DURATION, window.renderFrame(t), window.READY, optional window.FILM_CANVAS).
// It serves the project folder over 127.0.0.1, drives headless Chrome (tools/lib/browser.mjs) and writes
// review images, frame sequences and the MP4. Run it from the project folder.
//
//   Look at it (open the images with the Read tool):
//     node <studio>/tools/render.mjs --sheet=0.5,1,1.5,2 [--cols=4] [--w=480] --out=review/a.jpg     contact sheet
//     node <studio>/tools/render.mjs --strip=2.0:2.5 [--cols=6] [--w=320] --out=review/strip.jpg      EVERY frame of a stretch
//     node <studio>/tools/render.mjs --sheet=2.1,2.2 --crop=760,300,400,400 --w=600 --out=review/c.jpg full-res crop
//     node <studio>/tools/render.mjs --strip=2:2.5 --crop-at=960,780,500,400 --out=review/f.jpg       crop around a WORLD point
//         (needs window.FILM_TO_SCREEN(x, y) on the page; the paint medium provides it)
//     node <studio>/tools/render.mjs --stills=1.2,3.4 --out=review/stills                              full-size PNGs
//   Make the video:
//     node <studio>/tools/render.mjs --frames [--range=0:8] [--workers=4] [--twos]                     JPEGs → out/frames (resumable)
//     node <studio>/tools/render.mjs --encode [--audio=song.wav] --out=out/film.mp4                     out/frames → MP4
//     node <studio>/tools/render.mjs --clip [--audio=song.wav] --out=out/film.mp4                       frames + encode in one go
//   Common: --query=loop=emotions (extra URL parameters for the page)  --film=film.html  --fps=24  --size=1920x1080 | --aspect=16:9|9:16|1:1|4:5  --png (lossless frames)
//           --twos: render even frames only and copy each to the next (stepped art on twos; never for smooth motion)
//   The page receives the size as ?w=…&h=… (and ?portrait=1 when taller than wide) and must draw at that size.
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync, existsSync, renameSync, readdirSync, copyFileSync, rmSync } from 'node:fs';
import { dirname, resolve, join } from 'node:path';
import { serve } from './serve.mjs';
import { launch, navTimeout, CANVAS_PICK, findChrome } from './lib/browser.mjs';

const args = Object.fromEntries(process.argv.slice(2).map((a) => { const [k, ...v] = a.replace(/^--/, '').split('='); return [k, v.length ? v.join('=') : true]; }));
if (args.help || process.argv.length <= 2) { console.log(String(await import('node:fs').then((f) => f.readFileSync(new URL(import.meta.url)))).split('\n').filter((l) => l.startsWith('//')).map((l) => l.slice(3)).join('\n')); process.exit(0); }

const FILM = args.film || 'film.html', fps = Number(args.fps || 24), FRAMES = args.dir || 'out/frames';
const ASPECTS = { '16:9': [1920, 1080], '9:16': [1080, 1920], '1:1': [1080, 1080], '4:5': [1080, 1350] };
const [W, H] = args.size ? String(args.size).split('x').map(Number) : (ASPECTS[args.aspect] || ASPECTS['16:9']);
const times = (s) => String(s).split(',').map(Number);
const span = (s) => String(s).split(':').map(Number);
const run = (cmd, a) => new Promise((ok, bad) => { const p = spawn(cmd, a, { stdio: 'inherit' }); p.on('close', (c) => (c ? bad(new Error(`${cmd} exited ${c}`)) : ok())); });

async function encode(out) {
  const files = readdirSync(FRAMES).filter((f) => /^f\d{5}\.(jpg|png)$/.test(f)).sort();
  if (!files.length) throw new Error(`no frames in ${FRAMES}`);
  const ext = files[0].endsWith('.png') ? 'png' : 'jpg', audio = args.audio;
  mkdirSync(dirname(out), { recursive: true });
  console.log(`encoding ${files.length} frames → ${out}${audio ? ' with ' + audio : ''}`);
  await run('ffmpeg', ['-y', '-loglevel', 'error', '-stats', '-framerate', String(fps), '-i', `${FRAMES}/f%05d.${ext}`,
    ...(audio ? ['-i', audio, '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '256k', '-shortest'] : []),
    '-c:v', 'libx264', '-preset', 'slow', '-crf', String(args.crf || 17), '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]);
  console.log('wrote ' + out);
}

if (args.encode) { await encode(args.out || 'out/film.mp4'); process.exit(0); }

if (!findChrome()) console.warn('render: no Chrome/Chromium binary found; trying the installed Chrome channel (set CHROME_PATH if this fails)');
const { srv, url } = await serve(resolve('.'));
const browser = await launch([`--window-size=${W},${H}`]);
const query = `?render=1&w=${W}&h=${H}${H > W ? '&portrait=1' : ''}${args.query ? '&' + args.query : ''}`;

async function openPage(tag = '') {
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  page.on('console', (m) => { if (['error', 'warning'].includes(m.type())) console.log(`[page${tag}]`, m.text()); });
  page.on('pageerror', (e) => console.log(`[page error${tag}]`, e.message));
  // a script error before READY would otherwise wait out the whole timeout: fail at once, with the error
  let failed; const broke = new Promise((_, bad) => { failed = bad; });
  page.on('pageerror', (e) => failed(new Error(`film page error before READY: ${e.message}`)));
  await page.goto(`${url}/${FILM}${query}`, { timeout: navTimeout() });
  await Promise.race([page.waitForFunction(() => typeof window.renderFrame === 'function' && window.READY === true, null, { timeout: navTimeout() }), broke]);
  page.removeAllListeners('pageerror'); page.on('pageerror', (e) => console.log(`[page error${tag}]`, e.message));
  return page;
}
const grab = (page, t, type = 'image/jpeg', q = 0.92) => page.evaluate(async ([t, type, q, pick]) => {
  await window.renderFrame(t); const c = (0, eval)(pick); return c.toDataURL(type, q);
}, [t, type, q, CANVAS_PICK]).then((u) => Buffer.from(u.slice(u.indexOf(',') + 1), 'base64'));
const durationOf = (page) => page.evaluate(() => window.FILM_DURATION);

try {
  if (args.sheet || args.strip) {
    const page = await openPage(), out = args.out || 'review/sheet.jpg'; mkdirSync(dirname(out), { recursive: true });
    let ts;
    if (args.strip) { const [a, b] = span(args.strip); ts = []; for (let i = Math.round(a * fps); i <= Math.round(b * fps); i++) ts.push(i / fps); } else ts = times(args.sheet);
    const cols = Number(args.cols || (args.strip ? 6 : 3)), w = Number(args.w || (args.strip ? 320 : 640));
    const crop = args.crop ? times(args.crop) : null, at = args['crop-at'] ? times(args['crop-at']) : null;
    const res = await page.evaluate(async ([ts, cols, w, crop, at, pick]) => {
      const src = () => (0, eval)(pick), first = src(), FW = first.width, FH = first.height;
      const [, , cw, ch] = at || crop || [0, 0, FW, FH], h = Math.round(w * ch / cw), rows = Math.ceil(ts.length / cols);
      const sc = document.createElement('canvas'); sc.width = cols * w; sc.height = rows * h; const c = sc.getContext('2d'), ms = [];
      for (let i = 0; i < ts.length; i++) {
        const t0 = performance.now(); await window.renderFrame(ts[i]); ms.push(Math.round(performance.now() - t0));
        const x = (i % cols) * w, y = Math.floor(i / cols) * h;
        let [cx, cy] = crop || [0, 0];
        if (at) { const p = window.FILM_TO_SCREEN ? window.FILM_TO_SCREEN(at[0], at[1]) : [at[0], at[1]]; cx = p[0] - cw / 2; cy = p[1] - ch / 2; }
        c.drawImage(src(), cx, cy, cw, ch, x, y, w, h);
        c.fillStyle = 'rgba(0,0,0,.65)'; c.fillRect(x, y, 84, 24); c.fillStyle = '#fff'; c.font = '15px sans-serif'; c.fillText(ts[i].toFixed(2) + 's', x + 6, y + 17);
      }
      return { url: sc.toDataURL('image/jpeg', 0.9), ms };
    }, [ts, cols, w, crop, at, CANVAS_PICK]);
    writeFileSync(out, Buffer.from(res.url.slice(res.url.indexOf(',') + 1), 'base64'));
    console.log(`${out}  (${ts.length} frames)  ms/frame: ${res.ms.join(' ')}`);
  } else if (args.stills) {
    const page = await openPage(), out = args.out || 'review/stills'; mkdirSync(out, { recursive: true });
    for (const s of times(args.stills)) {
      const t0 = Date.now(), f = `${out}/t${s.toFixed(2).replace('.', '_')}.png`;
      writeFileSync(f, await grab(page, s, 'image/png')); console.log(`${f}  ${Date.now() - t0} ms`);
    }
  } else if (args.frames || args.clip) {
    // Parallel and resumable: each worker takes the next missing frame; files are written atomically.
    const probe = await openPage(), len = await durationOf(probe); await probe.close();
    const [a, b] = args.range ? span(args.range) : [0, len], workers = Number(args.workers || 4), png = !!args.png, ext = png ? 'png' : 'jpg';
    const i0 = Math.round(a * fps), i1 = Math.round(b * fps), twos = !!args.twos;
    mkdirSync(FRAMES, { recursive: true });
    const name = (i) => join(FRAMES, `f${String(i).padStart(5, '0')}.${ext}`);
    const todo = []; for (let i = i0; i < i1; i++) if (!(twos && (i - i0) % 2) && !existsSync(name(i))) todo.push(i);
    let next = 0, done = 0; const start = Date.now();
    console.log(`${todo.length} frames to render (${i1 - i0} in range${twos ? ', on twos' : ''}), ${workers} workers`);
    await Promise.all(Array.from({ length: Math.min(workers, todo.length || 1) }, async (_, w) => {
      const page = await openPage('#' + w);
      while (next < todo.length) {
        const i = todo[next++], tmp = name(i) + '.part';
        writeFileSync(tmp, await grab(page, i / fps, png ? 'image/png' : 'image/jpeg', 0.95)); renameSync(tmp, name(i));
        if (++done % 24 === 0) { const ms = (Date.now() - start) / done; process.stdout.write(`\r${done}/${todo.length}  ${(ms / 1000).toFixed(2)} s/frame  eta ${((todo.length - done) * ms / 60000).toFixed(1)} min`); }
      }
    }));
    if (twos) for (let i = i0 + 1; i < i1; i += 2) if (!existsSync(name(i)) && existsSync(name(i - 1))) copyFileSync(name(i - 1), name(i));
    console.log(`\nframes ready in ${FRAMES} (${((Date.now() - start) / 1000).toFixed(0)} s)`);
    if (args.clip) await encode(args.out || 'out/film.mp4');
  } else {
    console.error('nothing to do: pass --sheet, --strip, --stills, --frames, --clip or --encode (--help for all)'); process.exitCode = 2;
  }
} finally {
  await browser.close(); srv.close();
}
if (args['clean-frames'] && existsSync(FRAMES)) rmSync(FRAMES, { recursive: true });
