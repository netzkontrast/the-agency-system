// review-room/server.mjs : a local review room for the cuts of a film. Watch a cut, click on the picture, leave a note on that exact frame.
// Nothing leaves this computer: it only listens on 127.0.0.1.
// Usage: node server.mjs <folder with the exported .mp4 cuts> [port=4400]     then open http://localhost:4400
// Notes go to <folder>/review-notes/notes.json, a snapshot of each noted frame (pin drawn in) to <folder>/review-notes/shots/,
// and every press of "Send notes" adds a line starting SENT to <folder>/review-notes/sent.log (watch that file to be told).
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
if (!process.argv[2]) { console.error('usage: node server.mjs <folder with the exported .mp4 cuts> [port]'); process.exit(1); }
const HERE = path.dirname(fileURLToPath(import.meta.url)), OUT = path.resolve(process.argv[2]), DIR = path.join(OUT, 'review-notes'), NOTES = path.join(DIR, 'notes.json'), SHOTS = path.join(DIR, 'shots'), LOG = path.join(DIR, 'sent.log'), PORT = Number(process.argv[3] || 4400);
fs.mkdirSync(SHOTS, { recursive: true });
const load = () => { try { return JSON.parse(fs.readFileSync(NOTES, 'utf8')); } catch { return { notes: [], sent: [] }; } };
const save = (d) => fs.writeFileSync(NOTES, JSON.stringify(d, null, 1));
const cuts = () => fs.readdirSync(OUT).filter((f) => /\.mp4$/i.test(f) && !/silent|small|draft-frames/.test(f))
  .map((f) => ({ name: f, mtime: fs.statSync(path.join(OUT, f)).mtimeMs })).sort((a, b) => b.mtime - a.mtime);      // newest first
const body = (req) => new Promise((res) => { const c = []; req.on('data', (d) => c.push(d)); req.on('end', () => { try { res(JSON.parse(Buffer.concat(c).toString() || '{}')); } catch { res({}); } }); });
const json = (res, code, o) => { res.writeHead(code, { 'content-type': 'application/json', 'cache-control': 'no-store' }); res.end(JSON.stringify(o)); };
function file(req, res, p, type) {
  if (!fs.existsSync(p)) { res.writeHead(404); return res.end('not found'); }
  const size = fs.statSync(p).size, r = /bytes=(\d*)-(\d*)/.exec(req.headers.range || '');
  if (r) { const a = r[1] ? Number(r[1]) : 0, b = r[2] ? Math.min(Number(r[2]), size - 1) : size - 1;
    res.writeHead(206, { 'content-type': type, 'accept-ranges': 'bytes', 'content-range': `bytes ${a}-${b}/${size}`, 'content-length': b - a + 1 }); return fs.createReadStream(p, { start: a, end: b }).pipe(res); }
  res.writeHead(200, { 'content-type': type, 'accept-ranges': 'bytes', 'content-length': size, 'cache-control': 'no-store' }); fs.createReadStream(p).pipe(res);
}
http.createServer(async (req, res) => {
  // the room answers only its own page: another website open in the same browser cannot read the notes or plant one
  const host = String(req.headers.host || ''), origin = req.headers.origin;
  if (!/^(localhost|127\.0\.0\.1):\d+$/.test(host) || (origin && origin !== 'http://' + host)) { res.writeHead(403); return res.end('forbidden'); }
  const u = new URL(req.url, 'http://x'), p = decodeURIComponent(u.pathname);
  if (p === '/') return file(req, res, path.join(HERE, 'index.html'), 'text/html; charset=utf-8');
  const LOGO = path.join(HERE, '..', '..', 'assets', 'logo');                                                  // the Take One mark and wordmark
  if (p === '/favicon.ico') return file(req, res, path.join(LOGO, 'take-one-mark.svg'), 'image/svg+xml');
  if (p.startsWith('/logo/') && /^[a-z0-9-]+\.svg$/.test(path.basename(p))) return file(req, res, path.join(LOGO, path.basename(p)), 'image/svg+xml');
  if (p === '/api/cuts') return json(res, 200, cuts());
  if (p.startsWith('/video/')) { const n = path.basename(p); return cuts().some((c) => c.name === n) ? file(req, res, path.join(OUT, n), 'video/mp4') : json(res, 404, {}); }
  if (p.startsWith('/shots/')) return file(req, res, path.join(SHOTS, path.basename(p)), 'image/jpeg');
  if (p === '/api/notes' && req.method === 'GET') return json(res, 200, load());
  if (p === '/api/notes' && req.method === 'POST') { const b = await body(req), d = load(), id = Date.now().toString(36);
    const n = { id, cut: String(b.cut || ''), t: typeof b.t === 'number' ? Math.round(b.t * 1000) / 1000 : null, frame: typeof b.t === 'number' ? Math.round(b.t * 30) : null,
      x: typeof b.x === 'number' ? Math.round(b.x * 1000) / 1000 : null, y: typeof b.y === 'number' ? Math.round(b.y * 1000) / 1000 : null, text: String(b.text || '').slice(0, 4000), at: new Date().toISOString(), done: false };
    if (typeof b.shot === 'string' && b.shot.startsWith('data:image/jpeg;base64,')) { fs.writeFileSync(path.join(SHOTS, id + '.jpg'), Buffer.from(b.shot.slice(23), 'base64')); n.shot = 'shots/' + id + '.jpg'; }
    d.notes.push(n); save(d); console.log(`NOTE ${n.cut} ${n.t ?? 'whole film'} ${n.text.slice(0, 80)}`); return json(res, 200, n); }
  const m = /^\/api\/notes\/([a-z0-9]+)$/.exec(p);
  if (m && req.method === 'POST') { const b = await body(req), d = load(), n = d.notes.find((x) => x.id === m[1]); if (!n) return json(res, 404, {}); if (typeof b.text === 'string') n.text = b.text.slice(0, 4000); if (typeof b.done === 'boolean') n.done = b.done; save(d); return json(res, 200, n); }
  if (m && req.method === 'DELETE') { const d = load(); d.notes = d.notes.filter((x) => x.id !== m[1]); save(d); const sf = path.join(SHOTS, m[1] + '.jpg'); if (fs.existsSync(sf)) fs.unlinkSync(sf); return json(res, 200, { ok: true }); }
  if (p === '/api/send' && req.method === 'POST') { const b = await body(req), d = load(); d.sent.push({ at: new Date().toISOString(), cut: String(b.cut || ''), open: d.notes.filter((n) => !n.done).length }); save(d);
    const line = `SENT ${d.notes.filter((n) => !n.done).length} open notes on ${b.cut || ''}`; console.log(line); fs.appendFileSync(LOG, line + '\n'); return json(res, 200, { ok: true }); }
  res.writeHead(404); res.end('not found');
}).listen(PORT, '127.0.0.1', () => console.log(`Take One review room on http://localhost:${PORT}`));
