#!/usr/bin/env node
// tools/serve-project.mjs — serve a film project on this computer only, so the person (or you) can scrub film.html in
// a browser with its own preview controls. Pages load over http, not file://, so canvases can read local images.
//   node <studio>/tools/serve-project.mjs [project dir=.] [port=4300]
import { resolve } from 'node:path';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const root = resolve(process.argv[2] || '.'), port = Number(process.argv[3] || 4300);
const types = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.css': 'text/css',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.woff2': 'font/woff2',
  '.ttf': 'font/ttf', '.otf': 'font/otf', '.mp3': 'audio/mpeg', '.wav': 'audio/wav', '.mp4': 'video/mp4' };
http.createServer((req, res) => {
  let p = '';
  try { p = path.join(root, decodeURIComponent(new URL(req.url, 'http://x').pathname)); } catch { /* bad url */ }
  if (p !== root && !p.startsWith(root + path.sep)) { res.writeHead(403); return res.end(); }   // never outside the project
  if (fs.existsSync(p) && fs.statSync(p).isDirectory()) p = path.join(p, 'film.html');
  fs.readFile(p, (e, d) => {
    if (e) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'content-type': types[path.extname(p).toLowerCase()] || 'application/octet-stream' }); res.end(d);
  });
}).listen(port, '127.0.0.1', () => console.log(`film preview: http://localhost:${port}/film.html   (this computer only; Ctrl-C to stop)`));
