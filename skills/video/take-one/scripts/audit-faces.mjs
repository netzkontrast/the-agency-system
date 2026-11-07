// Face audit: step through the film and report every overlay that touches the main character's face.
// Contract: after renderFrame(t) the page sets window.__hits (labels of overlays touching the face) and window.__shot.
// See references/pipeline.md (Face audit). Usage: node audit-faces.mjs [portrait 0|1] [step=0.125]   env: FILM=film.html
import { chromium } from 'playwright-core';
import { serve } from './serve.mjs';
const portrait = process.argv[2] === '1', step = Number(process.argv[3] || 0.125);
const FILM = process.env.FILM || 'film.html';
const W = portrait ? 1080 : 1920, H = portrait ? 1920 : 1080;
const { srv, url } = await serve('.');
// Metal is the Mac's graphics engine: ask for it on a Mac only, every other system keeps Chrome's own choice
const GPU = process.platform === 'darwin' ? ['--use-angle=metal', '--ignore-gpu-blocklist'] : ['--ignore-gpu-blocklist'];
const browser = await chromium.launch({ channel: 'chrome', headless: true, args: GPU });
const page = await browser.newPage({ viewport: { width: W, height: H } });
await page.goto(url + '/' + FILM + (portrait ? '?portrait=1' : ''));
await page.waitForFunction(() => typeof window.renderFrame === 'function' && window.READY === true, null, { timeout: 120000 });
const dur = await page.evaluate(() => window.FILM_DURATION);
const res = await page.evaluate(({ dur, step }) => { const out = []; for (let t = 0; t < dur; t += step) { window.renderFrame(t); if (window.__hits.length) out.push([+t.toFixed(3), window.__shot, [...new Set(window.__hits)]]); } return out; }, { dur, step });
await browser.close(); srv.close();
// merge into ranges per shot+element
const ranges = {};
for (const [t, shot, hits] of res) for (const h of hits) { const k = `shot ${String(shot).padStart(2, '0')} · ${h}`; const r = ranges[k] ||= []; const last = r[r.length - 1]; if (last && t - last[1] <= step * 1.5) last[1] = t; else r.push([t, t]); }
const keys = Object.keys(ranges).sort();
console.log(`${portrait ? '9:16' : '16:9'}: ${keys.length ? keys.length + ' face overlaps' : 'no face overlaps'}`);
for (const k of keys) console.log('  ' + k + '  ' + ranges[k].map(([a, b]) => `${a.toFixed(2)}-${b.toFixed(2)}s`).join(', '));
