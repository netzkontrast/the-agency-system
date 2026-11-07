#!/usr/bin/env node
// Adapted from anidoodle (github.com/alexgreensh/anidoodle), Apache License 2.0, Copyright 2026 Alex Greenshpun
// CODE MUSIC ENGINE CLI. Renders a Piece module to a 48 kHz 32-bit FLOAT WAV (no PCM16 clipping on
// the way) and meters it: integrated LUFS (BS.1770-4), LRA (EBU 3342), true peak (4x), onsets/s
// (spectral flux), spectral centroid, cross-checked against ffmpeg's ebur128.
//
// <piece.mjs> is a module whose default export is a Piece or a function returning one
// (path/to/score.mjs#exportName picks another export). See references/music-engine.md.
//
//   node scripts/music.mjs render <piece.mjs> [--seconds N] [--out out.wav] [--flat] [--tempo N] [--loop] [--no-fit]
//   node scripts/music.mjs check  <piece.mjs> [--seconds N]   # bar math, key/mode, LUFS/peak + ffmpeg cross-check, determinism, onsets
//   node scripts/music.mjs meter  <file.wav|file.mp4>         # meter any audio file (decoded through ffmpeg)
import { execFileSync } from "node:child_process";
import { writeFileSync, unlinkSync, mkdtempSync } from "node:fs";
import { resolve, join } from "node:path";
import { tmpdir } from "node:os";
import { pathToFileURL } from "node:url";
import * as M from "./music/index.mjs";

const SR = 48000;

export const writeWavFloat = (path, L, R, sr = SR) => {
  const n = L.length, data = Buffer.alloc(n * 8), h = Buffer.alloc(58);
  for (let i = 0; i < n; i++) { data.writeFloatLE(L[i], i * 8); data.writeFloatLE(R[i], i * 8 + 4); }
  h.write("RIFF", 0); h.writeUInt32LE(50 + data.length, 4); h.write("WAVE", 8);
  h.write("fmt ", 12); h.writeUInt32LE(18, 16); h.writeUInt16LE(3, 20); h.writeUInt16LE(2, 22); h.writeUInt32LE(sr, 24); h.writeUInt32LE(sr * 8, 28); h.writeUInt16LE(8, 32); h.writeUInt16LE(32, 34); h.writeUInt16LE(0, 36);
  h.write("fact", 38); h.writeUInt32LE(4, 42); h.writeUInt32LE(n, 46); h.write("data", 50); h.writeUInt32LE(data.length, 54);
  writeFileSync(path, Buffer.concat([h, data]));
};
/** Decode ANY file through ffmpeg to float stereo 48 kHz: we meter what a player would decode. */
export const decode = (path) => {
  const buf = execFileSync("ffmpeg", ["-v", "error", "-i", path, "-vn", "-f", "f32le", "-acodec", "pcm_f32le", "-ac", "2", "-ar", String(SR), "pipe:1"], { maxBuffer: 1 << 30 });
  const f = new Float32Array(buf.buffer, buf.byteOffset, buf.length / 4), n = f.length / 2, L = new Float32Array(n), R = new Float32Array(n);
  for (let i = 0; i < n; i++) { L[i] = f[2 * i]; R[i] = f[2 * i + 1]; }
  return [L, R];
};
/** Independent cross-check: ffmpeg's own ebur128 summary (integrated, LRA, true peak). */
const ffmpegEbu = (path) => {
  const out = execFileSync("sh", ["-c", 'ffmpeg -hide_banner -nostats -i "$1" -vn -af ebur128=peak=true -f null - 2>&1', "sh", path], { encoding: "utf8", maxBuffer: 1 << 28 });
  const sum = out.slice(out.lastIndexOf("Summary:"));
  const g = (re) => { const m = re.exec(sum); return m ? Number(m[1]) : NaN; };
  return { I: g(/I:\s+(-?[\d.]+) LUFS/), LRA: g(/LRA:\s+(-?[\d.]+) LU/), TP: g(/Peak:\s+(-?[\d.]+) dBFS/) };
};

const fmt = (x, d = 1) => (Number.isFinite(x) ? x.toFixed(d) : "n/a");

/** Load a piece factory from a .mjs module: default export (or #name), a Piece or () => Piece. */
const getPiece = async (ref) => {
  const [file, exp = "default"] = ref.split("#");
  const mod = await import(pathToFileURL(resolve(file)).href);
  const v = mod[exp];
  if (v === undefined) throw new Error(`${file} has no export "${exp}" (exports: ${Object.keys(mod).join(", ")})`);
  return () => { const x = typeof v === "function" ? v() : v; if (!x || !x.plan || !x.parts) throw new Error(`${ref} is not a Piece (needs plan, parts, harmony)`); return x; };
};

const renderOne = (make, spec) => {
  let piece = make();
  let tempo = spec.tempo ?? piece.plan.tempo, form;
  const loop = spec.loop || piece.plan.loop;
  if (spec.seconds && spec.fit !== false && !loop) {
    const f = M.fitToDuration(piece, spec.seconds); piece = f.piece; tempo = f.tempo;
    form = `${f.form}: ${f.piece.plan.sections.map((x) => x.id).join(", ")}`;
  }
  const opts = { seconds: spec.seconds, tempo };
  if (spec.flat) Object.assign(opts, { expressive: false, piano: M.PIANO_FLAT, flatVelocity: 0.6 });
  const go = () => (loop ? M.renderLoop(piece, SR) : M.renderPiece(piece, SR, opts));
  const t0 = Date.now(), r = go(), ms = Date.now() - t0;
  // determinism: a second render must be bit-identical
  const r2 = go(); let same = r.L.length === r2.L.length;
  if (same) for (let i = 0; i < r.L.length; i++) if (r.L[i] !== r2.L[i] || r.R[i] !== r2.R[i]) { same = false; break; }
  return { r, piece, tempo, ms, deterministic: same, form, loop };
};

const beatsOf = (piece) => piece.plan.sections.reduce((a, s) => a + s.bars * M.beatsPerBar(piece.plan.meter), 0);
const onsetsFromData = (r) => {
  const ts = r.perf.parts.flatMap((p) => p.keys.map((k) => k.t)).sort((a, b) => a - b); let c = 0, last = -1;
  for (const t of ts) if (t - last > 0.03) { c++; last = t; } return c;
};

const printMeters = (L, R, label) => {
  const m = M.measure([L, R], SR);
  console.log(`${label}: ${fmt(m.durationS, 2)} s | ${fmt(m.lufs)} LUFS | LRA ${fmt(m.lra)} LU | ${fmt(m.dbtp, 2)} dBTP | ${m.onsetCount} onsets (${fmt(m.onsetsPerS, 2)}/s) | centroid ${Math.round(m.centroidHz)} Hz`);
  return m;
};

const main = async () => {
  const [cmd, ...args] = process.argv.slice(2);
  const flag = (k) => args.includes(k), val = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
  const ref = args.find((a) => !a.startsWith("--") && a !== val("--out") && a !== val("--seconds") && a !== val("--tempo"));

  if (cmd === "render") {
    const make = await getPiece(ref);
    const spec = { seconds: val("--seconds") ? Number(val("--seconds")) : undefined, tempo: val("--tempo") ? Number(val("--tempo")) : undefined, flat: flag("--flat"), loop: flag("--loop"), fit: !flag("--no-fit") };
    const { r, piece, tempo, ms, deterministic, form, loop } = renderOne(make, spec);
    const out = val("--out", "out.wav");
    writeWavFloat(out, r.L, r.R, SR);
    console.log(`"${piece.title}" -> ${out}`);
    console.log(`tempo ${fmt(tempo)} bpm${form ? ` | fit: ${form}` : ""}${loop ? ` | seamless loop ${fmt(r.loopS, 3)} s` : ""} | master ${r.masterMode} (gain ${fmt(r.gainDb)} dB) | rendered in ${ms} ms | deterministic: ${deterministic ? "yes (2 renders bit-identical)" : "NO"}`);
    printMeters(r.L, r.R, "meters");
    return;
  }

  if (cmd === "check") {
    // 1. bar math: line() already threw inside make() if any bar was wrong
    let make, piece;
    try { make = await getPiece(ref); piece = make(); } catch (e) { console.log(`FAIL (bar math / load): ${e.message}`); process.exit(1); }
    console.log(`"${piece.title}" | style ${piece.plan.style} | ${piece.plan.meter} at ${piece.plan.tempo} bpm | ${beatsOf(piece)} beats in ${piece.plan.sections.length} section(s)`);
    // 2. plan problems: key/mode histogram, tempo vs style, refused blends, close thirds
    const probs = M.planProblems(piece);
    for (const p of probs) console.log(`  PROBLEM: ${p}`);
    if (!probs.length) console.log("  plan: OK (key/mode histogram matches declarations)");
    // 3. render + meters
    const spec = { seconds: val("--seconds") ? Number(val("--seconds")) : undefined };
    const { r, tempo, deterministic, form, loop } = renderOne(make, spec);
    console.log(`  render: tempo ${fmt(tempo)} bpm${form ? ` | fit: ${form}` : ""}${loop ? ` | loop ${fmt(r.loopS, 3)} s` : ""} | master ${r.masterMode} | deterministic: ${deterministic ? "yes" : "NO"}`);
    const m = printMeters(r.L, r.R, "  meters");
    const target = r.masterMode === "dense" ? -14 : -16;
    const lufsOk = Math.abs(m.lufs - target) < 1 || (r.masterMode === "gentle" && m.lufs < target); // gentle may trade loudness for the peak cap
    console.log(`  master: target ${target} LUFS -> ${fmt(m.lufs)} (${lufsOk ? "ok" : "OFF TARGET"}), true peak ${fmt(m.dbtp, 2)} dBTP (${m.dbtp <= -0.9 ? "ok" : "OVER"})`);
    // onsets per beat (ghost-formlessness quick look; the full windowed guard is v2)
    const beats = (m.durationS / 60) * tempo;
    console.log(`  motion: ${fmt(m.onsetCount / beats, 2)} onsets/beat over the whole piece (a bed wants >= ~0.5, a groove >= 1)`);
    // 4. ffmpeg ebur128 cross-check on the written file
    const tmp = join(mkdtempSync(join(tmpdir(), "music-")), "check.wav");
    writeWavFloat(tmp, r.L, r.R, SR);
    try {
      const e = ffmpegEbu(tmp);
      const dI = Math.abs(e.I - m.lufs), dT = Math.abs(e.TP - m.dbtp);
      console.log(`  ffmpeg ebur128: I ${fmt(e.I)} LUFS (Δ${fmt(dI, 2)}) | LRA ${fmt(e.LRA)} LU | TP ${fmt(e.TP, 2)} dBTP (Δ${fmt(dT, 2)}) ${dI < 1 && dT < 1 ? "-- agrees" : "-- DISAGREES"}`);
    } catch { console.log("  ffmpeg ebur128: skipped (ffmpeg not found)"); }
    unlinkSync(tmp);
    const pass = !probs.length && deterministic && m.dbtp <= -0.9 && lufsOk;
    console.log(pass ? "PASS" : "FAIL");
    process.exit(pass ? 0 : 1);
  }

  if (cmd === "meter") {
    for (const f of args.filter((a) => !a.startsWith("--"))) { const [L, R] = decode(f); printMeters(L, R, f); }
    return;
  }

  console.log("usage: music.mjs render <piece.mjs> [--seconds N] [--out out.wav] [--flat] [--tempo N] [--loop] [--no-fit]\n       music.mjs check  <piece.mjs> [--seconds N]\n       music.mjs meter  <file.wav|mp4> ...");
};

main().catch((e) => { console.error(e.message); process.exit(1); });
