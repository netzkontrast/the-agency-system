#!/usr/bin/env node
// tools/libs-check.mjs — load every library in engine/lib/importmap.json (plus the classic d3/lottie/Alea scripts)
// in headless Chrome and report which ones resolve. Run after `npm install` in the studio or a version bump.
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { serve } from './serve.mjs';
import { launch, navTimeout } from './lib/browser.mjs';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const { srv, url } = await serve(root);
const browser = await launch();
try {
  const page = await browser.newPage();
  await page.goto(`${url}/engine/lib/libs-check.html`, { timeout: navTimeout() });
  await page.waitForFunction(() => window.LIBS, null, { timeout: navTimeout() });
  const res = await page.evaluate(() => window.LIBS);
  let bad = 0;
  for (const [k, v] of Object.entries(res)) { console.log(`${v === 'ok' ? '  ok  ' : '  FAIL'}  ${k}${v === 'ok' ? '' : '  ' + v}`); if (v !== 'ok') bad++; }
  process.exitCode = bad ? 1 : 0;
} finally { await browser.close(); srv.close(); }
