#!/usr/bin/env node
// audio-check.mjs — AUDIO QUALITY METER for the take-one skill.
// Adapted from anidoodle (github.com/alexgreensh/anidoodle), Apache License 2.0, Copyright 2026 Alex Greenshpun
//
// Meters ANY audio or video file (decoded via ffmpeg, i.e. what a player would hear):
//   integrated LUFS  ITU-R BS.1770-4 K-weighting, 400 ms blocks at 75 % overlap,
//                    -70 LUFS absolute and -10 LU relative gates
//   LRA              EBU Tech 3342 (3 s short-term, -20 LU gate, P95 - P10)
//   true peak        4x oversampled (16-tap polyphase windowed sinc), dBTP
//   centroid         magnitude-weighted spectral centroid over non-silent frames
// Every LUFS number is cross-checked against ffmpeg's own `ebur128`; the two must
// agree within 0.5 LU or the run FAILS (that disagreement means a metering bug).
//
// Usage:
//   node audio-check.mjs <file> [more files] [--target film|dense|gentle]
//   node audio-check.mjs mix.wav --stems vocals.wav other.wav   # vocal-masking check
//
// Targets (see references/audio.md "Measure, don't guess"):
//   film   (default)  mixed film final audio: -14 LUFS integrated (+/-1 LU), true peak <= -1 dBTP
//   dense             music master, dense styles:  -14 LUFS (+/-1 LU), TP <= -1 dBTP
//   gentle            music master, gentle styles: -16 LUFS (+/-1 LU), TP <= -1 dBTP
//   --stems vocals.wav other.wav : the vocal stem must beat the rest by >= 3 dB in
//   500 Hz-4 kHz in >= 80 % of its active seconds, or the dialogue/vocal is likely masked.
//
// Exit code 0 = all checks pass; 1 = a verdict failed; 2 = self-meter vs ffmpeg disagree.

import { execFileSync, spawnSync } from "node:child_process";
import { basename } from "node:path";
import { existsSync } from "node:fs";

const SR = 48000;

// ---------------------------------------------------------------------------
// Decode ANY file through ffmpeg to float stereo 48 kHz: meter what a player decodes.
const decode = (path) => {
  let buf;
  try {
    buf = execFileSync(
      "ffmpeg",
      ["-v", "error", "-i", path, "-vn", "-f", "f32le", "-acodec", "pcm_f32le", "-ac", "2", "-ar", String(SR), "pipe:1"],
      { maxBuffer: 1 << 30, stdio: ["ignore", "pipe", "pipe"] },
    );
  } catch (e) {
    const lines = String(e.stderr || e.message).trim().split("\n");
    console.error(`cannot decode ${path}: ${lines.find((l) => /stream/i.test(l)) || lines[0]} (no audio stream?)`);
    process.exit(1);
  }
  if (buf.length < 8 * SR * 0.4) { console.error(`${path}: no audio stream, or under 400 ms of audio - nothing to meter`); process.exit(1); }
  const f = new Float32Array(buf.buffer, buf.byteOffset, buf.length / 4);
  const n = f.length / 2, L = new Float32Array(n), R = new Float32Array(n);
  for (let i = 0; i < n; i++) { L[i] = f[2 * i]; R[i] = f[2 * i + 1]; }
  return [L, R];
};

// Independent cross-check: ffmpeg's own ebur128 summary (integrated, LRA, true peak).
const ffmpegEbu = (path) => {
  const r = spawnSync(
    "ffmpeg",
    ["-hide_banner", "-nostats", "-i", path, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"],
    { encoding: "utf8", maxBuffer: 1 << 28 },
  );
  const out = (r.stderr || "") + (r.stdout || "");
  const sum = out.slice(out.lastIndexOf("Summary:"));
  const g = (re) => { const m = re.exec(sum); return m ? Number(m[1]) : NaN; };
  return { I: g(/I:\s+(-?[\d.]+) LUFS/), LRA: g(/LRA:\s+(-?[\d.]+) LU/), TP: g(/Peak:\s+(-?[\d.]+) dBFS/) };
};

// ---------------------------------------------------------------------------
// BS.1770-4 K-weighting: stage 1 high shelf (+4 dB above ~1.7 kHz), stage 2 RLB
// high-pass ~38 Hz (pyloudnorm's closed-form coefficients).
const kWeight = (x, sr) => {
  const out = new Float64Array(x.length);
  {
    const G = 3.999843853973347, Q = 0.7071752369554196, fc = 1681.974450955533;
    const K = Math.tan((Math.PI * fc) / sr), Vh = Math.pow(10, G / 20), Vb = Math.pow(Vh, 0.4996667741545416);
    const a0 = 1 + K / Q + K * K, b0 = (Vh + (Vb * K) / Q + K * K) / a0, b1 = (2 * (K * K - Vh)) / a0,
      b2 = (Vh - (Vb * K) / Q + K * K) / a0, a1 = (2 * (K * K - 1)) / a0, a2 = (1 - K / Q + K * K) / a0;
    let x1 = 0, x2 = 0, y1 = 0, y2 = 0;
    for (let i = 0; i < x.length; i++) { const y = b0 * x[i] + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2; x2 = x1; x1 = x[i]; y2 = y1; y1 = y; out[i] = y; }
  }
  {
    const fc = 38.13547087602444, Q = 0.5003270373238773, K = Math.tan((Math.PI * fc) / sr);
    const a0 = 1 + K / Q + K * K, a1 = (2 * (K * K - 1)) / a0, a2 = (1 - K / Q + K * K) / a0;
    let x1 = 0, x2 = 0, y1 = 0, y2 = 0;
    for (let i = 0; i < out.length; i++) { const xi = out[i], y = xi - 2 * x1 + x2 - a1 * y1 - a2 * y2; x2 = x1; x1 = xi; y2 = y1; y1 = y; out[i] = y; }
  }
  return out;
};

const loudness = (chans, sr) => {
  const k = chans.map((c) => kWeight(c, sr)), n = chans[0].length;
  // prefix sums of the channel-summed squared K-weighted signal make every block O(1)
  const ps = new Float64Array(n + 1);
  for (let i = 0; i < n; i++) { let s = 0; for (const c of k) s += c[i] * c[i]; ps[i + 1] = ps[i] + s; }
  const ms = (a, len) => (ps[Math.min(a + len, n)] - ps[a]) / len;
  const lufs = (z) => -0.691 + 10 * Math.log10(Math.max(z, 1e-20));
  // integrated: 400 ms blocks, 75 % overlap (100 ms hop), -70 LUFS absolute + -10 LU relative gates
  const bl = Math.round(0.4 * sr), hop = Math.round(0.1 * sr), blocks = [];
  for (let a = 0; a + bl <= n; a += hop) blocks.push(ms(a, bl));
  const abs = blocks.filter((z) => lufs(z) > -70);
  const rel = lufs(abs.reduce((a, b) => a + b, 0) / Math.max(1, abs.length)) - 10;
  const gated = abs.filter((z) => lufs(z) > rel);
  const integrated = lufs(gated.reduce((a, b) => a + b, 0) / Math.max(1, gated.length));
  // LRA per EBU 3342: 3 s short-term, -70 absolute + -20 LU relative gates, P95 - P10
  const sl = Math.round(3 * sr), st = [];
  for (let a = 0; a + sl <= n; a += hop) st.push(ms(a, sl));
  const stAbs = st.filter((z) => lufs(z) > -70);
  const stRel = lufs(stAbs.reduce((a, b) => a + b, 0) / Math.max(1, stAbs.length)) - 20;
  const stG = stAbs.map(lufs).filter((l) => l > stRel).sort((a, b) => a - b);
  const pct = (p) => (stG.length ? stG[Math.min(stG.length - 1, Math.max(0, Math.round((p / 100) * (stG.length - 1))))] : NaN);
  return { integrated, lra: pct(95) - pct(10), shortMax: st.length ? Math.max(...st.map(lufs)) : NaN };
};

const truePeak = (chans) => {
  // 4x polyphase windowed sinc, 16 taps per phase
  const O = 4, T = 16, h = [];
  for (let ph = 0; ph < O; ph++) {
    const row = [];
    for (let t = 0; t < T; t++) {
      const x = t - T / 2 + 1 - ph / O, w = 0.5 + 0.5 * Math.cos((Math.PI * x) / (T / 2));
      row.push(x === 0 ? 1 : (Math.sin(Math.PI * x) / (Math.PI * x)) * w);
    }
    h.push(row);
  }
  let peak = 0, sample = 0;
  for (const c of chans) for (let i = 0; i < c.length; i++) {
    const a = Math.abs(c[i]); if (a > sample) sample = a;
    if (a < peak * 0.5) continue; // an inter-sample peak cannot exceed ~2x its neighbours here
    for (let ph = 1; ph < O; ph++) {
      let s = 0;
      for (let t = 0; t < T; t++) { const j = i + t - T / 2 + 1; if (j >= 0 && j < c.length) s += c[j] * h[ph][t]; }
      const v = Math.abs(s); if (v > peak) peak = v;
    }
    if (a > peak) peak = a;
  }
  return { dbtp: 20 * Math.log10(Math.max(peak, 1e-12)), samplePeakDb: 20 * Math.log10(Math.max(sample, 1e-12)) };
};

// ---------------------------------------------------------------------------
// Spectral centroid (magnitude-weighted, averaged over non-silent frames).
const fft = (re, im) => {
  const n = re.length;
  for (let i = 1, j = 0; i < n; i++) { let bit = n >> 1; for (; j & bit; bit >>= 1) j ^= bit; j ^= bit; if (i < j) { let t = re[i]; re[i] = re[j]; re[j] = t; t = im[i]; im[i] = im[j]; im[j] = t; } }
  for (let len = 2; len <= n; len <<= 1) {
    const ang = (-2 * Math.PI) / len, wr = Math.cos(ang), wi = Math.sin(ang);
    for (let i = 0; i < n; i += len) {
      let cr = 1, ci = 0;
      for (let j = 0; j < len / 2; j++) {
        const a = i + j, b = a + len / 2, xr = re[b] * cr - im[b] * ci, xi = re[b] * ci + im[b] * cr;
        re[b] = re[a] - xr; im[b] = im[a] - xi; re[a] += xr; im[a] += xi;
        const t = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = t;
      }
    }
  }
};
const mono = (chans) => { const n = chans[0].length, m = new Float32Array(n); for (const c of chans) for (let i = 0; i < n; i++) m[i] += c[i] / chans.length; return m; };
const centroid = (chans, sr) => {
  const N = 2048, hop = 512, m = mono(chans);
  const w = Float64Array.from({ length: N }, (_, i) => 0.5 - 0.5 * Math.cos((2 * Math.PI * i) / N));
  let emax = 0, sum = 0, c = 0, wsum = 0, wtot = 0;
  const frames = [];
  for (let a = 0; a + N <= m.length; a += hop) {
    const re = new Float64Array(N), im = new Float64Array(N);
    for (let i = 0; i < N; i++) re[i] = m[a + i] * w[i];
    fft(re, im);
    const mag = new Float64Array(N / 2 + 1);
    let e = 0;
    for (let k = 0; k <= N / 2; k++) { mag[k] = Math.hypot(re[k], im[k]); e += mag[k] * mag[k]; }
    emax = Math.max(emax, e); frames.push([mag, e]);
  }
  for (const [mag, e] of frames) {
    if (e < emax * 1e-5) continue;
    let num = 0, den = 0;
    for (let k = 1; k < mag.length; k++) { num += ((k * sr) / N) * mag[k]; den += mag[k]; }
    if (den > 0) { sum += num / den; c++; wsum += (num / den) * e; wtot += e; }
  }
  return { mean: c ? sum / c : 0, energyWeighted: wtot ? wsum / wtot : 0 };
};

// ---------------------------------------------------------------------------
// Vocal-masking check (adapted from anidoodle's masking guard): in 500 Hz-4 kHz the
// vocal stem must beat the sum of everything else by >= 3 dB in >= 80 % of the
// seconds where the vocal is active, or the dialogue/vocal is likely masked.
const biquad = (x, b0, b1, b2, a1, a2) => {
  const out = new Float64Array(x.length);
  let x1 = 0, x2 = 0, y1 = 0, y2 = 0;
  for (let i = 0; i < x.length; i++) { const y = b0 * x[i] + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2; x2 = x1; x1 = x[i]; y2 = y1; y1 = y; out[i] = y; }
  return out;
};
const bandpass500to4k = (x, sr) => {
  const Q = Math.SQRT1_2;
  const coeffs = (f, hp) => {
    const w0 = (2 * Math.PI * f) / sr, cw = Math.cos(w0), al = Math.sin(w0) / (2 * Q), a0 = 1 + al;
    return hp
      ? [(1 + cw) / 2 / a0, -(1 + cw) / a0, (1 + cw) / 2 / a0, (-2 * cw) / a0, (1 - al) / a0]
      : [(1 - cw) / 2 / a0, (1 - cw) / a0, (1 - cw) / 2 / a0, (-2 * cw) / a0, (1 - al) / a0];
  };
  return biquad(biquad(x, ...coeffs(500, true)), ...coeffs(4000, false));
};
const maskingCheck = (vocalChans, otherChans, sr, { beatDb = 3, activeFloorDb = -50, needShare = 0.8 } = {}) => {
  const v = bandpass500to4k(mono(vocalChans), sr), o = bandpass500to4k(mono(otherChans), sr);
  const n = Math.min(v.length, o.length), secs = Math.floor(n / sr);
  const rmsDb = (x, a, len) => { let s = 0; for (let i = a; i < a + len; i++) s += x[i] * x[i]; return 10 * Math.log10(s / len + 1e-12); };
  let active = 0, clear = 0; const maskedAt = [];
  for (let s = 0; s < secs; s++) {
    const vDb = rmsDb(v, s * sr, sr);
    if (vDb <= activeFloorDb) continue; // vocal not sounding this second
    active++;
    const oDb = rmsDb(o, s * sr, sr);
    if (vDb - oDb >= beatDb) clear++; else maskedAt.push(s);
  }
  const share = active ? clear / active : 1;
  return { active, clear, share, pass: share >= needShare, maskedAt, beatDb, needShare };
};

// ---------------------------------------------------------------------------
const fmt = (x, d = 1) => (Number.isFinite(x) ? x.toFixed(d) : "n/a");
const TARGETS = {
  film: { lufs: -14, tol: 1, tp: -1, label: "mixed film final audio: -14 LUFS +/-1, true peak <= -1 dBTP" },
  dense: { lufs: -14, tol: 1, tp: -1, label: "music master (dense): -14 LUFS +/-1, true peak <= -1 dBTP" },
  gentle: { lufs: -16, tol: 1, tp: -1, label: "music master (gentle): -16 LUFS +/-1, true peak <= -1 dBTP" },
};

const args = process.argv.slice(2);
if (!args.length || args.includes("--help")) {
  console.log("usage: node audio-check.mjs <file...> [--target film|dense|gentle] [--stems vocals.wav other.wav]");
  process.exit(args.length ? 0 : 1);
}
let target = "film"; const files = []; let stems = null;
for (let i = 0; i < args.length; i++) {
  if (args[i] === "--target") target = args[++i];
  else if (args[i] === "--stems") { stems = [args[++i], args[++i]]; }
  else files.push(args[i]);
}
if (!TARGETS[target]) { console.error(`unknown --target "${target}" (film | dense | gentle)`); process.exit(1); }
for (const f of [...files, ...(stems ?? [])]) if (!existsSync(f)) { console.error(`no such file: ${f}`); process.exit(1); }

let anyFail = false, meterBug = false;
for (const file of files) {
  const chans = decode(file), dur = chans[0].length / SR;
  const l = loudness(chans, SR), tp = truePeak(chans), c = centroid(chans, SR), ff = ffmpegEbu(file);
  const t = TARGETS[target];
  const dI = Math.abs(l.integrated - ff.I);
  const agree = Number.isFinite(ff.I) ? dI <= 0.5 : false;
  if (!agree) meterBug = true;

  console.log(`=== ${basename(file)} ===`);
  console.log(`duration    ${fmt(dur, 2)} s  (decoded to stereo float 48 kHz via ffmpeg)`);
  console.log(`integrated  ${fmt(l.integrated)} LUFS   ffmpeg ebur128 ${fmt(ff.I)} LUFS   delta ${fmt(dI, 2)} LU  ${agree ? "AGREE" : "DISAGREE (metering bug, fix before trusting anything)"}`);
  console.log(`LRA         ${fmt(l.lra)} LU     ffmpeg ${fmt(ff.LRA)} LU`);
  console.log(`true peak   ${fmt(tp.dbtp)} dBTP   ffmpeg ${fmt(ff.TP)} dBTP   sample peak ${fmt(tp.samplePeakDb)} dBFS`);
  console.log(`centroid    ${fmt(c.mean, 0)} Hz mean / ${fmt(c.energyWeighted, 0)} Hz energy-weighted`);

  const okL = Math.abs(l.integrated - t.lufs) <= t.tol;
  const okTp = tp.dbtp <= t.tp;
  if (!okL || !okTp) anyFail = true;
  console.log(`--- verdict (${target}: ${t.label}) ---`);
  console.log(`loudness    ${okL ? "PASS" : "FAIL"}  ${fmt(l.integrated)} LUFS vs ${t.lufs} +/-${t.tol}${okL ? "" : `  -> apply gain ${fmt(t.lufs - l.integrated)} dB (then re-check the peak)`}`);
  console.log(`true peak   ${okTp ? "PASS" : "FAIL"}  ${fmt(tp.dbtp)} dBTP vs <= ${t.tp} dBTP${okTp ? "" : "  -> lower the gain or limit; a hot peak clips on encode"}`);
  console.log("");
}

if (stems) {
  const [vf, of] = stems;
  const mk = maskingCheck(decode(vf), decode(of), SR);
  if (!mk.pass) anyFail = true;
  console.log(`=== vocal masking: ${basename(vf)} vs ${basename(of)} (500 Hz-4 kHz) ===`);
  console.log(`active seconds ${mk.active}, vocal beats the rest by >= ${mk.beatDb} dB in ${mk.clear}/${mk.active} (${fmt(mk.share * 100)} %)  ${mk.pass ? "PASS" : "FAIL"} (need >= ${mk.needShare * 100} %)`);
  if (!mk.pass) console.log(`masked at seconds: ${mk.maskedAt.slice(0, 20).join(", ")}${mk.maskedAt.length > 20 ? ", ..." : ""}  -> raise the vocal or dip the music 500 Hz-4 kHz under it`);
  console.log("");
}

// Leave through the event loop, never with process.exit() here. On Node 26 an exit taken while one of V8's background threads is
// waiting for a garbage collection deadlocks in shutdown: the numbers are printed, the process never ends, and a shell pipeline
// (or an agent) waits on it for ever. Seen three times in one day on a 74 s file. Setting the exit code and letting a short
// timer run gives the main thread a turn to serve that collection first; the process then ends by itself.
const leave = (code) => { process.exitCode = code; setTimeout(() => {}, 60); };
if (meterBug) { console.log("RESULT: METER DISAGREES WITH FFMPEG (> 0.5 LU) - do not trust these numbers"); leave(2); }
else {
console.log(anyFail ? "RESULT: FAIL" : "RESULT: PASS");
leave(anyFail ? 1 : 0);
}
