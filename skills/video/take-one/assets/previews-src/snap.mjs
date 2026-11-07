// Renders frames a+b from a boat.html (see BOAT-BRIEF.md). Usage:
//   NODE_PATH=<dir containing node_modules with playwright-core>/node_modules node ../snap.mjs boat.html
import { chromium } from 'playwright-core';
import path from 'node:path';
const file = process.argv[2] || 'boat.html';
const b = await chromium.launch({ channel: 'chrome', headless: true, args: ['--allow-file-access-from-files'] });
const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
p.on('pageerror', e => console.log('PAGEERR', e.message));
p.on('console', m => { if (m.type() === 'error') console.log('CONSOLE', m.text()); });
await p.goto('file://' + path.resolve(file));
await p.waitForFunction(() => window.READY, null, { timeout: 20000 });
for (const which of ['a', 'b']) {
  await p.evaluate(async (w) => { window.DONE = false; const r = window.drawFrame(w); if (r && r.then) await r; }, which);
  await p.waitForFunction(() => window.DONE !== false, null, { timeout: 60000 }).catch(() => {});
  await p.locator('#c').screenshot({ path: `${which}.png` });
}
await b.close(); console.log('wrote a.png b.png');
