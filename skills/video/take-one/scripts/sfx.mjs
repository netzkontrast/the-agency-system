#!/usr/bin/env node
// Adapted from anidoodle (github.com/alexgreensh/anidoodle), Apache License 2.0, Copyright 2026 Alex Greenshpun
//
// Procedural SFX kit for take-one films: every effect synthesized in code (no samples,
// no ElevenLabs), deterministic per seed, placed on exact film frames over a music bed.
//
//   node sfx.mjs list                                   # kinds, variants, levels, uses
//   node sfx.mjs one <kind> [variant] [seed] <out.wav>  # one sound (KEY=C BPM=90 env for tuned kinds)
//   node sfx.mjs kit <outdir>                           # every kind x variant + metrics check (exit 1 on fail)
//   node sfx.mjs mix <plan.json> <bed-audio> <out.wav>  # place a cue plan over a music bed
//
// plan.json: { fps, frames?, bpm?, beatZeroS?, beatsPerBar?, key?, seed, snap?, minDb?, ceilingDb?,
//              cues: [{ kind, frame, variant?, snap?, seed?, pitch?, lengthS?, beats?, key?, bpm?,
//                       dir?, gainDb?, duckDb?, minDb?, label? }] }
// frames defaults to the bed's length. Cues are addressed by INTEGER film frame (fractional throws).
// The frame is the sound's sync point: the hit; the PASS-BY of a whoosh; the END of a riser.
// The bed ducks under cues (raised-cosine 40 ms attack, 280 ms release, 1.2 s after an impact,
// capped at 9 dB), the final mix goes through a look-ahead -1 dBTP ceiling, and every cue must sit
// within 6 dB of the ducked bed over its speaking window or the mix throws "buried cue".
// Taste rules (warnings): one riser + one impact per film; at most 2 cues in any 100 ms.
import { execFileSync } from "node:child_process";
import { writeFileSync, mkdirSync, realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { readFile } from "node:fs/promises";
import { join, resolve } from "node:path";

const SR = 48000;
const TAU = Math.PI * 2;
const db = (x) => Math.pow(10, x / 20);
const dB = (x) => 20 * Math.log10(Math.max(x, 1e-12));
const clamp = (x, a, b) => (x < a ? a : x > b ? b : x);
const panGains = (p) => { const a = ((clamp(p, -1, 1) + 1) * Math.PI) / 4; return [Math.cos(a), Math.sin(a)]; };
const mkRng = (seed) => {
  let a = seed >>> 0;
  return () => { a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
};

// ---------------------------------------------------------------- filters
/** Zavalishin TPT state-variable filter; set() may be called per sample for sweeps. */
class SVF {
  constructor(sr, f = 1000, q = 0.707) { this.sr = sr; this.ic1 = 0; this.ic2 = 0; this.lp = 0; this.bp = 0; this.hp = 0; this.set(f, q); }
  set(f, q) { this.g = Math.tan((Math.PI * clamp(f, 5, this.sr * 0.49)) / this.sr); this.k = 1 / q; this.a1 = 1 / (1 + this.g * (this.g + this.k)); this.a2 = this.g * this.a1; this.a3 = this.g * this.a2; }
  tick(x) { const v3 = x - this.ic2, v1 = this.a1 * this.ic1 + this.a2 * v3, v2 = this.ic2 + this.a2 * this.ic1 + this.a3 * v3; this.ic1 = 2 * v1 - this.ic1; this.ic2 = 2 * v2 - this.ic2; this.lp = v2; this.bp = v1; this.hp = x - this.k * v1 - v2; return v2; }
}
/** RBJ biquad (direct form I). */
class Biquad {
  constructor() { this.x1 = 0; this.x2 = 0; this.y1 = 0; this.y2 = 0; this.b0 = 1; this.b1 = 0; this.b2 = 0; this.a1 = 0; this.a2 = 0; }
  static make(sr, type, f, q) {
    const bq = new Biquad(), w = (TAU * f) / sr, c = Math.cos(w), s = Math.sin(w), al = s / (2 * q);
    let b0 = 1, b1 = 0, b2 = 0, a0 = 1, a1 = 0, a2 = 0;
    if (type === "lp") { b0 = (1 - c) / 2; b1 = 1 - c; b2 = b0; a0 = 1 + al; a1 = -2 * c; a2 = 1 - al; }
    else if (type === "hp") { b0 = (1 + c) / 2; b1 = -(1 + c); b2 = b0; a0 = 1 + al; a1 = -2 * c; a2 = 1 - al; }
    else { b0 = al; b1 = 0; b2 = -al; a0 = 1 + al; a1 = -2 * c; a2 = 1 - al; } // bp
    bq.b0 = b0 / a0; bq.b1 = b1 / a0; bq.b2 = b2 / a0; bq.a1 = a1 / a0; bq.a2 = a2 / a0; return bq;
  }
  tick(x) { const y = this.b0 * x + this.b1 * this.x1 + this.b2 * this.x2 - this.a1 * this.y1 - this.a2 * this.y2; this.x2 = this.x1; this.x1 = x; this.y2 = this.y1; this.y1 = y; return y; }
  run(buf) { for (let i = 0; i < buf.length; i++) buf[i] = this.tick(buf[i]); return buf; }
}
const onePoleCoef = (sr, f) => 1 - Math.exp((-TAU * f) / sr);

/** A small room: early reflections plus a short 8-line FDN tail. Returns the WET signal only. */
const room = (L, R, sr, o) => {
  const n = L.length, wL = new Float32Array(n), wR = new Float32Array(n), r = o.rng;
  const inL = Float32Array.from(L), inR = Float32Array.from(R);
  Biquad.make(sr, "hp", o.hp, 0.7).run(inL); Biquad.make(sr, "hp", o.hp, 0.7).run(inR);
  Biquad.make(sr, "lp", o.lp, 0.7).run(inL); Biquad.make(sr, "lp", o.lp, 0.7).run(inR);
  for (const [src, dst, side] of [[inL, wL, 0], [inR, wR, 1], [inR, wL, 2], [inL, wR, 3]]) {
    let acc = 0; const k = onePoleCoef(sr, 5200);
    for (let t = 0; t < 7; t++) {
      const ms = 6 + t * 4.6 + r() * 3 + side * 0.7, d = Math.round((ms / 1000) * sr), g = (o.er * (side < 2 ? 1 : 0.55) * Math.pow(0.8, t) * (t % 2 ? -1 : 1)) / 2.2;
      acc = 0; for (let i = d; i < n; i++) { acc += k * (src[i - d] - acc); dst[i] += acc * g; }
    }
  }
  if (o.late > 0) {
    const N = 8, lens = [1123, 1289, 1447, 1597, 1777, 1913, 2053, 2239].map((x) => Math.round(((x * sr) / 48000) * (0.7 + 0.3 * r())));
    const bufs = lens.map((l) => new Float32Array(l)), idx = new Array(N).fill(0), lp = new Array(N).fill(0);
    const gains = lens.map((l) => Math.pow(10, (-3 * l) / (sr * o.rt60))), dampK = onePoleCoef(sr, 3200);
    const pd = Math.round(o.predelay * sr), out = new Float64Array(N), h = new Float64Array(N);
    for (let i = 0; i < n; i++) {
      const xl = i >= pd ? inL[i - pd] : 0, xr = i >= pd ? inR[i - pd] : 0;
      for (let j = 0; j < N; j++) out[j] = bufs[j][idx[j]];
      h.set(out);
      for (let s = 1; s < N; s <<= 1) for (let j = 0; j < N; j += s << 1) for (let q = j; q < j + s; q++) { const a = h[q], b = h[q + s]; h[q] = a + b; h[q + s] = a - b; }
      for (let j = 0; j < N; j++) {
        let v = (h[j] / Math.sqrt(N)) * gains[j];
        lp[j] += dampK * (v - lp[j]); v = lp[j];
        bufs[j][idx[j]] = v + (j % 2 ? xr : xl) * 0.5; idx[j] = (idx[j] + 1) % lens[j];
      }
      wL[i] += (out[0] - out[2] + out[4] - out[6]) * o.late * 0.5; wR[i] += (out[1] - out[3] + out[5] - out[7]) * o.late * 0.5;
    }
  }
  return [wL, wR];
};

// ---------------------------------------------------------------- sfx building blocks
const buf = (n) => new Float64Array(Math.max(0, Math.round(n)));
const secs = (sr, s) => Math.max(0, Math.round(s * sr));
/** 32-bit integer hash of two values: per-cue seeds that stay put when other cues move. */
const mixSeed = (a, b) => {
  let h = (Math.imul(a | 0, 0x9e3779b1) ^ Math.imul(b | 0, 0x85ebca6b)) >>> 0;
  h = Math.imul(h ^ (h >>> 16), 0x7feb352d) >>> 0; h = Math.imul(h ^ (h >>> 15), 0x846ca68b) >>> 0;
  return (h ^ (h >>> 16)) >>> 0;
};
const strSeed = (s) => { let h = 2166136261; for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619); return h >>> 0; };

/** A stereo bus. Mono layers are placed with a pan (constant, or per sample) and an optional Haas offset. */
class Bus {
  constructor(sr, n) { this.sr = sr; this.n = n; this.L = buf(n); this.R = buf(n); }
  add(sig, at = 0, g = 1, p = 0, haasMs = 0) {
    const d = Math.round((Math.abs(haasMs) * this.sr) / 1000), dL = haasMs < 0 ? d : 0, dR = haasMs > 0 ? d : 0;
    const fixed = typeof p === "number" ? panGains(p) : null;
    for (let i = 0; i < sig.length; i++) {
      const v = sig[i] * g; if (v === 0) continue;
      const [gl, gr] = fixed ?? panGains(p(i));
      const a = at + i + dL, b = at + i + dR;
      if (a >= 0 && a < this.n) this.L[a] += v * gl;
      if (b >= 0 && b < this.n) this.R[b] += v * gr;
    }
  }
  add2(l, r, at = 0, g = 1) { for (let i = 0; i < l.length; i++) { const k = at + i; if (k < 0 || k >= this.n) continue; this.L[k] += l[i] * g; this.R[k] += r[i] * g; } }
}

const white = (r, n) => { const o = buf(n); for (let i = 0; i < o.length; i++) o[i] = r() * 2 - 1; return o; };
/** Pink noise (Paul Kellet's refined filter). */
const pink = (r, n) => {
  const o = buf(n); let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
  for (let i = 0; i < o.length; i++) {
    const w = r() * 2 - 1;
    b0 = 0.99886 * b0 + w * 0.0555179; b1 = 0.99332 * b1 + w * 0.0750759; b2 = 0.969 * b2 + w * 0.153852;
    b3 = 0.8665 * b3 + w * 0.3104856; b4 = 0.55 * b4 + w * 0.5329522; b5 = -0.7616 * b5 - w * 0.016898;
    o[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + w * 0.5362) * 0.11; b6 = w * 0.115926;
  }
  return o;
};
/** Modal synthesis: sum of damped sinusoids (bubbles rise, bodies drop); no aliasing, stops at -100 dB. */
const modal = (sr, n, modes) => {
  const o = buf(n), ny = 0.45 * sr;
  for (const m of modes) {
    if (!(m.f > 0) || m.f > ny) continue;
    const i0 = secs(sr, m.t0 ?? 0), att = m.att ?? 0.00006, end = Math.min(o.length, i0 + Math.ceil(m.tau * 11.5 * sr)), riseEnd = m.tau * 6.9;
    let ph = m.ph ?? 0;
    for (let i = i0; i < end; i++) {
      const t = (i - i0) / sr, f = m.f * (1 + (m.glide ?? 0) * (1 - Math.exp(-t / (m.glideTau ?? 0.01)))) * (1 + (m.rise ?? 0) * Math.min(t, riseEnd));
      o[i] += Math.sin(ph) * m.a * (1 - Math.exp(-t / att)) * Math.exp(-t / m.tau);
      ph += (TAU * Math.min(f, ny)) / sr;
    }
  }
  return o;
};
const endFade = (o, sr, s = 0.008) => { const f = Math.min(o.length, secs(sr, s)); for (let i = 0; i < f; i++) o[o.length - 1 - i] *= 0.5 - 0.5 * Math.cos((Math.PI * i) / f); return o; };
/** A sine whose frequency and amplitude are functions of time (phase-accumulated, so glides never click). */
const chirp = (sr, n, f, env, ph0 = 0) => {
  const o = buf(n); let ph = ph0;
  for (let i = 0; i < o.length; i++) { const t = i / sr; o[i] = Math.sin(ph) * env(t); ph += (TAU * Math.min(f(t), sr * 0.45)) / sr; }
  return endFade(o, sr, 0.03);
};
/** Enveloped noise burst, optionally band-limited: the contact transient of almost every hit. */
const burst = (sr, r, len, tau, o = {}) => {
  const n = secs(sr, len), s = o.pink ? pink(r, n) : white(r, n);
  for (let i = 0; i < n; i++) s[i] *= Math.exp(-i / sr / tau) * Math.min(1, i / (sr * 0.00008) + 0.35);
  filt(s, sr, o); return endFade(s, sr, 0.008);
};
const filt = (s, sr, o) => {
  const run = (bq) => { for (let i = 0; i < s.length; i++) s[i] = bq.tick(s[i]); };
  if (o.hp) run(Biquad.make(sr, "hp", o.hp, 0.707));
  if (o.lp) run(Biquad.make(sr, "lp", o.lp, 0.707));
  if (o.bp) run(Biquad.make(sr, "bp", o.bp, o.q ?? 1));
  return s;
};
/** Time-varying state-variable filter (a sweep): f(t) in Hz. */
const sweep = (s, sr, f, q, mode) => {
  const sv = new SVF(sr, f(0), typeof q === "number" ? q : q(0));
  for (let i = 0; i < s.length; i++) {
    if ((i & 15) === 0) { const t = i / sr; sv.set(clamp(f(t), 20, sr * 0.45), typeof q === "number" ? q : q(t)); }
    sv.tick(s[i]); s[i] = mode === "lp" ? sv.lp : mode === "bp" ? sv.bp : sv.hp;
  }
  return s;
};
const shape = (s, sr, env) => { for (let i = 0; i < s.length; i++) s[i] *= env(i / sr); return s; };
/** Attack-decay envelope: raised-cosine attack of `a` seconds, exponential decay of time constant `tau`. */
const ad = (a, tau) => (t) => (t < a ? 0.5 - 0.5 * Math.cos((Math.PI * t) / a) : Math.exp(-(t - a) / tau));
const smooth = (u) => { const x = clamp(u, 0, 1); return x * x * (3 - 2 * x); };

/** Put the bus in a small space: room's wet signal, mixed in. Stereo width comes from here. */
const space = (b, r, o) => {
  const L = Float32Array.from(b.L), R = Float32Array.from(b.R);
  const [wL, wR] = room(L, R, b.sr, { er: o.er ?? 0.5, late: 0.6, rt60: o.rt60, predelay: o.predelay ?? 0.012, hp: o.hp ?? 250, lp: o.lp ?? 7000, rng: r });
  for (let i = 0; i < b.n; i++) { b.L[i] += wL[i] * o.mix; b.R[i] += wR[i] * o.mix; }
};

/** DC block (22 Hz HP), air roll-off (16.5 kHz), NaN guard, trailing silence trimmed, end fade. */
const finish = (b, keep) => {
  const sr = b.sr, top = Math.min(16500, sr * 0.4);
  for (const c of [b.L, b.R]) {
    const h = Biquad.make(sr, "hp", 22, 0.707), l1 = Biquad.make(sr, "lp", top, 0.5412), l2 = Biquad.make(sr, "lp", top, 1.3066);
    for (let i = 0; i < c.length; i++) { const v = l2.tick(l1.tick(h.tick(c[i]))); c[i] = Number.isFinite(v) ? v : 0; }
  }
  let peak = 0; for (let i = 0; i < b.n; i++) peak = Math.max(peak, Math.abs(b.L[i]), Math.abs(b.R[i]));
  let end = b.n; const floor = peak * 1e-4;
  while (end > keep + 1 && Math.abs(b.L[end - 1]) < floor && Math.abs(b.R[end - 1]) < floor) end--;
  const rang = end === b.n;
  end = Math.min(b.n, end + secs(sr, 0.004));
  const L = new Float32Array(end), R = new Float32Array(end), fade = Math.min(end, rang ? Math.min(secs(sr, 0.4), Math.round(end * 0.2)) : secs(sr, 0.004));
  for (let i = 0; i < end; i++) { const g = i >= end - fade ? 0.5 - 0.5 * Math.cos((Math.PI * (end - 1 - i)) / fade) : 1; L[i] = b.L[i] * g; R[i] = b.R[i] * g; }
  return [L, R];
};

// ---- measurement: K-weighted (BS.1770) power, the same yardstick for levels and audibility
const kWeight = (x, sr) => {
  const out = new Float64Array(x.length);
  { const G = 3.999843853973347, Q = 0.7071752369554196, fc = 1681.974450955533, K = Math.tan((Math.PI * fc) / sr), Vh = Math.pow(10, G / 20), Vb = Math.pow(Vh, 0.4996667741545416);
    const a0 = 1 + K / Q + K * K, b0 = (Vh + (Vb * K) / Q + K * K) / a0, b1 = (2 * (K * K - Vh)) / a0, b2 = (Vh - (Vb * K) / Q + K * K) / a0, a1 = (2 * (K * K - 1)) / a0, a2 = (1 - K / Q + K * K) / a0;
    let x1 = 0, x2 = 0, y1 = 0, y2 = 0; for (let i = 0; i < x.length; i++) { const y = b0 * x[i] + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2; x2 = x1; x1 = x[i]; y2 = y1; y1 = y; out[i] = y; } }
  { const fc = 38.13547087602444, Q = 0.5003270373238773, K = Math.tan((Math.PI * fc) / sr), a0 = 1 + K / Q + K * K, a1 = (2 * (K * K - 1)) / a0, a2 = (1 - K / Q + K * K) / a0;
    let x1 = 0, x2 = 0, y1 = 0, y2 = 0; for (let i = 0; i < out.length; i++) { const xi = out[i], y = xi - 2 * x1 + x2 - a1 * y1 - a2 * y2; x2 = x1; x1 = xi; y2 = y1; y1 = y; out[i] = y; } }
  return out;
};
/** Loudness (LUFS-scaled, ungated) of K-weighted channels over samples [a, b). */
const winLufs = (kL, kR, a, b) => {
  let s = 0; const lo = Math.max(0, a), hi = Math.min(kL.length, b), len = Math.max(1, hi - lo);
  for (let i = lo; i < hi; i++) s += kL[i] * kL[i] + kR[i] * kR[i];
  return -0.691 + 10 * Math.log10(Math.max(s / len, 1e-20));
};
/** The window where a sound actually speaks: 10 ms frames within 10 dB of its loudest, 15-500 ms. */
const speakingWindow = (kL, kR, sr) => {
  const hop = Math.max(1, secs(sr, 0.01)), nf = Math.ceil(kL.length / hop), e = new Float64Array(nf);
  for (let f = 0; f < nf; f++) { let s = 0; for (let i = f * hop; i < Math.min(kL.length, (f + 1) * hop); i++) s += kL[i] * kL[i] + kR[i] * kR[i]; e[f] = s; }
  let mx = 0, at = 0; for (let f = 0; f < nf; f++) if (e[f] > mx) { mx = e[f]; at = f; }
  let a = at, b = at; const th = mx * 0.1;
  while (a > 0 && e[a - 1] >= th) a--;
  while (b < nf - 1 && e[b + 1] >= th) b++;
  let s0 = a * hop, s1 = Math.min(kL.length, (b + 1) * hop);
  const min = secs(sr, 0.015), max = secs(sr, 0.5);
  if (s1 - s0 > max) { const c = at * hop + hop / 2; s0 = Math.max(s0, Math.round(c - max / 2)); s1 = Math.min(s1, s0 + max); }
  if (s1 - s0 < min) s1 = Math.min(kL.length, s0 + min);
  return [s0, s1];
};
/** Integrated LUFS (BS.1770-4 gating), for the mix report. */
const integratedLufs = (L, R, sr) => {
  const kL = kWeight(L, sr), kR = kWeight(R, sr), n = L.length, bl = Math.round(0.4 * sr), hop = Math.round(0.1 * sr);
  const lufs = (z) => -0.691 + 10 * Math.log10(Math.max(z, 1e-20)), blocks = [];
  for (let a = 0; a + bl <= n; a += hop) { let s = 0; for (let i = a; i < a + bl; i++) s += kL[i] * kL[i] + kR[i] * kR[i]; blocks.push(s / bl); }
  const abs = blocks.filter((z) => lufs(z) > -70), rel = lufs(abs.reduce((a, b) => a + b, 0) / Math.max(1, abs.length)) - 10;
  const gated = abs.filter((z) => lufs(z) > rel);
  return lufs(gated.reduce((a, b) => a + b, 0) / Math.max(1, gated.length));
};
/** True peak, 4x oversampled (windowed-sinc polyphase), dBTP. */
const truePeak = (chans) => {
  const O = 4, T = 16, h = [];
  for (let ph = 0; ph < O; ph++) { const row = []; for (let t = 0; t < T; t++) { const x = t - T / 2 + 1 - ph / O, w = 0.5 + 0.5 * Math.cos((Math.PI * x) / (T / 2)); row.push(x === 0 ? 1 : (Math.sin(Math.PI * x) / (Math.PI * x)) * w); } h.push(row); }
  let peak = 0;
  for (const c of chans) for (let i = 0; i < c.length; i++) {
    const a = Math.abs(c[i]);
    if (a < peak * 0.5) continue;
    for (let ph = 1; ph < O; ph++) { let s = 0; for (let t = 0; t < T; t++) { const j = i + t - T / 2 + 1; if (j >= 0 && j < c.length) s += c[j] * h[ph][t]; } const v = Math.abs(s); if (v > peak) peak = v; }
    if (a > peak) peak = a;
  }
  return dB(peak);
};

// ---------------------------------------------------------------- the kit: 10 kinds, each layered (transient + body + tail)
const PC = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
const parseKey = (key) => {
  const m = /^([A-G])(#|b)?(m|min|minor)?$/.exec(String(key).trim());
  if (!m) throw new Error(`sfx: bad key "${key}" (use e.g. "C", "Eb", "F#m")`);
  return { pc: (PC[m[1]] + (m[2] === "b" ? -1 : m[2] === "#" ? 1 : 0) + 12) % 12, minor: !!m[3] };
};
const keyHz = (c, octave, semis = 0) => 440 * Math.pow(2, (c.key.pc + semis + 12 * (octave + 1) - 69) / 12);
const PENTA = { major: [0, 2, 4, 7, 9], minor: [0, 3, 5, 7, 10] };
/** Glockenspiel-bar partials: a bright tuned strike that sits above a mix. */
const glock = (f, tau, a, t0 = 0) => [
  { f, tau, a, t0 }, { f: f * 2.756, tau: tau * 0.42, a: a * 0.32, t0 }, { f: f * 5.404, tau: tau * 0.18, a: a * 0.14, t0 }, { f: f * 8.933, tau: tau * 0.09, a: a * 0.06, t0 },
];

const tick = {
  variants: ["key", "soft", "ui", "space"], level: -20.5, duckDb: 0,
  use: "typing (one per character: key), a laptop key (soft), an interface tick (ui), the space bar (space)",
  make(c, v) {
    const { sr, r, P } = c, n = secs(sr, 0.22), b = new Bus(sr, n), p0 = (r() - 0.5) * 0.5;
    if (v === "ui") {
      const f = c.j(4300, 0.05) * P;
      b.add(modal(sr, n, [{ f, tau: 0.0017, a: 1 }, { f: f * 2.03, tau: 0.0009, a: 0.3 }, { f: f * 0.51, tau: 0.004, a: 0.25 }]), 0, 0.8, p0);
      b.add(burst(sr, r, 0.002, 0.00028, { hp: 5500 }), 0, 0.45, p0);
      space(b, r, { rt60: 0.18, mix: 0.05, hp: 1500 });
      return { bus: b, hit: 0 };
    }
    const soft = v === "soft", spc = v === "space";
    const f1 = c.j(soft ? 1550 : spc ? 1900 : 3150, 0.07) * P;
    // 1 the key's plastic click (three stiff modes), 2 the contact transient, 3 bottom-out into the plate
    b.add(burst(sr, r, 0.0016, 0.00035, { hp: soft ? 1200 : 2800 }), 0, soft ? 0.3 : 0.55, p0);
    b.add(modal(sr, n, [{ f: f1, tau: soft ? 0.0024 : 0.0031, a: 1 }, { f: f1 * c.j(1.63, 0.03), tau: 0.002, a: 0.5 }, { f: f1 * c.j(2.41, 0.03), tau: 0.0014, a: 0.3 }]), 0, soft ? 0.45 : 0.65, p0, 0.12);
    b.add(modal(sr, n, [{ f: c.j(spc ? 145 : soft ? 205 : 265, 0.1) * P, tau: spc ? 0.02 : 0.009, a: 1, t0: c.j(0.0028, 0.3), att: 0.0004 }, { f: c.j(spc ? 520 : 780, 0.1) * P, tau: 0.004, a: 0.35, t0: 0.003 }]), 0, spc ? 0.9 : 0.55, p0);
    if (spc) b.add(modal(sr, n, [{ f: c.j(2500, 0.1) * P, tau: 0.004, a: 1 }, { f: c.j(4100, 0.1) * P, tau: 0.002, a: 0.5 }]), secs(sr, c.j(0.0065, 0.25)), 0.28, p0 + 0.15); // stabiliser wire
    if (!soft) { // the upstroke, a quieter higher click as the key returns
      const up = secs(sr, c.j(spc ? 0.12 : 0.085, 0.25));
      b.add(modal(sr, n, [{ f: f1 * 1.18, tau: 0.0017, a: 1 }, { f: f1 * 1.9, tau: 0.001, a: 0.4 }]), up, 0.17, p0);
      b.add(burst(sr, r, 0.001, 0.00025, { hp: 4000 }), up, 0.1, p0);
    }
    if (soft) for (const ch of [b.L, b.R]) filt(ch, sr, { lp: 6000 });
    space(b, r, { rt60: 0.22, mix: 0.06, hp: 600 });
    return { bus: b, hit: 0 };
  },
};

const press = {
  variants: ["thock", "soft", "confirm"], level: -13, duckDb: 2,
  use: "a button press, the Generate thock (thock), a gentle toggle (soft), a press that succeeds, tuned to the key (confirm)",
  make(c, v) {
    const { sr, r, P } = c, n = secs(sr, v === "confirm" ? 2.8 : 1.2), b = new Bus(sr, n), soft = v === "soft";
    // body: a pitch-dropping sine, the "th" of thock
    const lo = c.j(soft ? 70 : 84, 0.05) * P, drop = c.j(soft ? 105 : 150, 0.1) * P, tau = c.j(soft ? 0.065 : 0.052, 0.1);
    const body = chirp(sr, secs(sr, 0.5), (t) => lo + drop * Math.exp(-t / 0.017), ad(0.0006, tau));
    b.add(body.map((x) => Math.tanh(x * 1.5) / Math.tanh(1.5)), 0, 1, 0);
    b.add(burst(sr, r, 0.004, soft ? 0.001 : 0.0006, { lp: soft ? 2500 : 7000, hp: 500 }), 0, soft ? 0.3 : 0.5, 0);
    if (!soft) {
      // the plastic cap: three modes, a hair to the side
      b.add(modal(sr, n, [{ f: c.j(1060, 0.05) * P, tau: 0.007, a: 1 }, { f: c.j(1790, 0.05) * P, tau: 0.005, a: 0.6 }, { f: c.j(2870, 0.05) * P, tau: 0.0035, a: 0.4 }]), 0, 0.42, 0.08, 0.3);
      const up = secs(sr, c.j(0.14, 0.2)); // release: the button coming back up
      b.add(modal(sr, n, [{ f: c.j(1420, 0.05) * P, tau: 0.003, a: 1 }, { f: c.j(2330, 0.05) * P, tau: 0.002, a: 0.5 }]), up, 0.13, 0.05);
      b.add(chirp(sr, secs(sr, 0.1), () => lo * 1.6, ad(0.0005, 0.012)), up, 0.12, 0);
    }
    if (v === "confirm") { // a glassy tuned answer 12 ms after the press
      const f = keyHz(c, 6);
      b.add(modal(sr, n, glock(f, 0.35, 1, 0.012)), 0, 0.18, -0.25);
      b.add(modal(sr, n, glock(f * 1.5, 0.28, 1, 0.07)), 0, 0.12, 0.3);
    }
    space(b, r, { rt60: v === "confirm" ? 0.9 : 0.4, mix: v === "confirm" ? 0.16 : 0.1, hp: 220 });
    return { bus: b, hit: 0 };
  },
};

const pop = {
  variants: ["pop", "cork", "tiny"], level: -16, duckDb: 1,
  use: "something appears (pop), a cap coming off / a card landing (cork), a small dot or badge appearing (tiny)",
  make(c, v) {
    const { sr, r, P } = c, n = secs(sr, 0.5), b = new Bus(sr, n), p0 = (r() - 0.5) * 0.3;
    const [f0, rise, tau, nz] = v === "cork" ? [260, 0.9, 0.032, 0.7] : v === "tiny" ? [920, 1.1, 0.012, 0.3] : [420, 1.6, 0.022, 0.45];
    const f = c.j(f0, 0.1) * P, tt = c.j(tau, 0.15);
    b.add(chirp(sr, n, (t) => f * (1 + rise * (1 - Math.exp(-t / 0.005))), ad(0.0004, tt)), 0, 1, p0);
    b.add(burst(sr, r, 0.005, v === "cork" ? 0.0014 : 0.0008, { bp: v === "tiny" ? 3200 : v === "cork" ? 900 : 1400, q: 1.4 }), 0, nz * 2.2, p0);
    if (v !== "tiny") b.add(modal(sr, n, [{ f: c.j(v === "cork" ? 110 : 140, 0.1) * P, tau: 0.01, a: 1, att: 0.0005 }]), 0, 0.3, 0);
    if (v === "cork") b.add(shape(filt(pink(r, secs(sr, 0.12)), sr, { hp: 1800 }), sr, ad(0.004, 0.025)), secs(sr, 0.004), 0.25, p0); // the rush of air
    space(b, r, { rt60: 0.35, mix: 0.1 });
    return { bus: b, hit: 0 };
  },
};

const dropAt = (c, b, at, f0, tau, g, p) => {
  const { sr, r } = c;
  b.add(burst(sr, r, 0.001, 0.00025, { hp: 2500 }), at, 0.35 * g, p); // the surface tick
  // the plink: a bubble of air trapped by the drop rings with a RISING pitch (van den Doel)
  b.add(modal(sr, b.n, [{ f: f0, tau, a: 1, t0: 0.0015, att: 0.0012, rise: 0.4 / tau }, { f: f0 * 2.01, tau: tau * 0.3, a: 0.08, t0: 0.0015, att: 0.0012, rise: 0.4 / tau }]), at, g, p);
};
const ink = {
  variants: ["plip", "double", "bloom"], level: -15, duckDb: 2,
  use: "an ink drop landing (plip), a drop and its smaller echo (double), the drop that opens an ink bloom (bloom)",
  make(c, v) {
    const { sr, r, P } = c, n = secs(sr, 3), b = new Bus(sr, n), p0 = (r() - 0.5) * 0.3, f0 = c.j(1150, 0.12) * P, tau = c.j(0.04, 0.15);
    dropAt(c, b, 0, f0, tau, 1, p0);
    if (v === "double") dropAt(c, b, secs(sr, c.j(0.085, 0.2)), f0 * c.j(1.35, 0.06), tau * 0.7, 0.42, p0 + 0.25);
    if (v === "bloom") { // the ink spreads: a soft wet swell and a low round note under it
      const sw = shape(filt(pink(r, secs(sr, 1.5)), sr, { lp: 750, hp: 120 }), sr, ad(0.09, 0.45));
      const sw2 = shape(filt(pink(r, secs(sr, 1.5)), sr, { lp: 750, hp: 120 }), sr, ad(0.11, 0.45));
      b.add2(sw, sw2, secs(sr, 0.02), 0.5);
      b.add(chirp(sr, secs(sr, 2.2), (t) => c.j(98, 0.04) * P * (1 - 0.06 * smooth(t / 0.6)), ad(0.05, 0.34)), secs(sr, 0.01), 0.22, 0);
    }
    space(b, r, { rt60: v === "bloom" ? 1.1 : 0.6, mix: v === "bloom" ? 0.22 : 0.14, hp: 300 });
    return { bus: b, hit: 0 };
  },
};

const paper = {
  variants: ["slide", "flip", "rustle"], level: -18, duckDb: 1.5,
  use: "a sheet sliding in and landing (slide, hit = the landing), a page turn (flip, hit = the snap), handling paper (rustle)",
  make(c, v) {
    const { sr, r, P } = c;
    if (v === "flip") {
      const len = c.o.lengthS ?? c.j(0.32, 0.1), N = secs(sr, len), b = new Bus(sr, N + secs(sr, 0.6));
      let ph = 0; const am = buf(N); for (let i = 0; i < N; i++) { const u = i / N; ph += (2 * Math.PI * (55 - 30 * u)) / sr; am[i] = 1 - 0.55 * (0.5 + 0.5 * Math.sin(ph)); }
      const env = (t) => { const u = t / len; return smooth(u / 0.55) * (u < 0.55 ? 1 : 1 - smooth((u - 0.55) / 0.45) * 0.85); };
      for (const [side, amt] of [[0, 1], [1, 1]]) {
        const s = white(r, N); sweep(s, sr, (t) => (1500 + 2700 * Math.sin(Math.PI * Math.min(1, t / len))) * P, 0.9, "bp");
        for (let i = 0; i < N; i++) s[i] *= am[i] * env(i / sr);
        b.add(s, 0, 1.1 * amt, side ? 0.2 * c.dir : -0.2 * c.dir);
      }
      const snap = N - secs(sr, 0.01);
      b.add(burst(sr, r, 0.006, 0.0009, { hp: 1500 }), snap, 0.55, 0.25 * c.dir);
      b.add(modal(sr, b.n, [{ f: c.j(880, 0.1) * P, tau: 0.005, a: 1 }, { f: c.j(190, 0.1) * P, tau: 0.012, a: 0.6, att: 0.0005 }]), snap, 0.3, 0.2 * c.dir);
      space(b, r, { rt60: 0.4, mix: 0.1 });
      return { bus: b, hit: snap };
    }
    if (v === "rustle") {
      const len = c.o.lengthS ?? c.j(0.5, 0.15), N = secs(sr, len), b = new Bus(sr, N + secs(sr, 0.5)), k = 28 + Math.floor(r() * 24);
      for (let g = 0; g < k; g++) {
        const t = len * Math.pow(r(), 1.3), gl = c.j(0.008, 0.6), f = (1500 + 4500 * r()) * P;
        b.add(burst(sr, r, gl, gl * 0.35, { bp: f, q: 1.3 }), secs(sr, t), (0.4 + r()) * 1.2 * Math.sin(Math.PI * Math.min(1, t / len + 0.05)), (r() - 0.5) * 0.8);
      }
      const bed = shape(filt(pink(r, N), sr, { lp: 3200, hp: 500 }), sr, (t) => Math.sin(Math.PI * Math.min(1, t / len)));
      b.add(bed, 0, 0.35, 0);
      space(b, r, { rt60: 0.35, mix: 0.08 });
      return { bus: b, hit: 0 };
    }
    // slide: the sheet travels, speeding then braking, then lands
    const len = c.o.lengthS ?? c.j(0.45, 0.12), N = secs(sr, len), land = secs(sr, len * 0.86), b = new Bus(sr, N + secs(sr, 0.6));
    const sp = (t) => { const u = t / (len * 0.86); return u < 1 ? smooth(u / 0.3) * (1 - 0.4 * u) : 0.15 * Math.exp(-(t - len * 0.86) / 0.02); };
    const pan = (i) => c.dir * (-0.3 + 0.55 * Math.min(1, i / land));
    for (const side of [0, 1]) {
      const s = pink(r, N); sweep(s, sr, (t) => (1000 + 1700 * sp(t)) * P, 0.8, "bp"); for (let i = 0; i < N; i++) s[i] *= sp(i / sr);
      b.add(s, 0, 1.3, (i) => pan(i) + (side ? 0.15 : -0.15));
    }
    const fib = buf(N); for (let i = 0; i < N; i++) if (r() < (180 * sp(i / sr)) / sr) fib[i] = (r() - 0.5) * 2;
    b.add(filt(fib, sr, { hp: 3000 }), 0, 0.35, pan);
    b.add(modal(sr, b.n, [{ f: c.j(150, 0.1) * P, tau: 0.02, a: 1, att: 0.0008 }, { f: c.j(620, 0.1) * P, tau: 0.006, a: 0.3 }]), land, 0.45, pan(land));
    b.add(burst(sr, r, 0.008, 0.0015, { lp: 3000, pink: true }), land, 0.5, pan(land));
    space(b, r, { rt60: 0.4, mix: 0.1 });
    return { bus: b, hit: land };
  },
};

/**
 * A pass-by: the source moves along a line past the listener. Distance sets level and air
 * absorption, the radial velocity sets the doppler glide (high approaching, low leaving) and the
 * angle sets the pan. hit = the closest point.
 */
const passBy = (c, b, len, o) => {
  const { sr, r, P } = c, N = secs(sr, len), tc = len * 0.56, w = len * 0.2;
  const geo = (t) => { const x = (t - tc) / w, d = Math.sqrt(1 + x * x); return { x, d, D: 1 / (1 + o.dop * (x / d)) }; };
  const edge = (t) => Math.min(1, t / 0.03, (len - t) / 0.03);
  const amp = (t) => { const { d } = geo(t); return Math.pow(d, -1.7) * Math.max(0, edge(t)); };
  const panAt = (i) => { const { x, d } = geo(i / sr); return clamp(c.dir * o.spread * (x / d), -1, 1); };
  const air = [pink(r, N), pink(r, N)];
  for (const s of air) { sweep(s, sr, (t) => { const g = geo(t); return o.air * P * g.D * (0.55 + 0.45 / g.d); }, 0.7, "bp"); for (let i = 0; i < N; i++) s[i] *= amp(i / sr); }
  // mostly panned (the source moves), partly decorrelated (the air around it)
  const mono = air[0].map((x, i) => x * 0.75 + air[1][i] * 0.25);
  b.add(mono, 0, 3.2, panAt);
  b.add2(air[1], air[0], 0, 0.9);
  if (o.toneAmt > 0) { const t = white(r, N); sweep(t, sr, (tt) => o.tone * P * geo(tt).D, o.toneQ, "bp"); for (let i = 0; i < N; i++) t[i] *= amp(i / sr); b.add(t, 0, o.toneAmt, panAt); }
  if (o.bodyAmt > 0) { const s = pink(r, N); sweep(s, sr, (t) => o.body * geo(t).D, 0.8, "lp"); for (let i = 0; i < N; i++) s[i] *= amp(i / sr); b.add(s, 0, o.bodyAmt, (i) => panAt(i) * 0.4); }
  return secs(sr, tc);
};
const whoosh = {
  variants: ["soft", "air", "fast", "deep"], level: -16, duckDb: 2,
  use: "something travels past camera: a gentle transition (soft, the default), a card flying (air), a quick flick (fast), a big heavy move (deep). hit = the pass-by",
  make(c, v) {
    const cfg = { soft: { len: 0.9, air: 620, tone: 1050, toneQ: 5, body: 180, toneAmt: 0.35, bodyAmt: 0.25, dop: 0.14, spread: 0.6 },
      air: { len: 0.7, air: 950, tone: 1750, toneQ: 7, body: 220, toneAmt: 0.5, bodyAmt: 0.3, dop: 0.22, spread: 0.8 },
      fast: { len: 0.38, air: 1400, tone: 2600, toneQ: 8, body: 260, toneAmt: 0.55, bodyAmt: 0.15, dop: 0.32, spread: 0.85 },
      deep: { len: 1.05, air: 460, tone: 780, toneQ: 5, body: 150, toneAmt: 0.3, bodyAmt: 0.9, dop: 0.2, spread: 0.7 } }[v];
    const len = c.o.lengthS ?? c.j(cfg.len, 0.08), b = new Bus(c.sr, secs(c.sr, len + 0.8));
    const hit = passBy(c, b, len, { ...cfg, air: c.j(cfg.air, 0.1), tone: c.j(cfg.tone, 0.1) });
    space(b, c.r, { rt60: v === "deep" ? 1.2 : 0.7, mix: 0.12, hp: 300 });
    return { bus: b, hit };
  },
};

const swish = {
  variants: ["in", "out", "soft"], level: -17, duckDb: 1,
  use: "a UI panel or card sliding (in = rising, out = falling), a subtle nudge (soft). Short, never sharp",
  make(c, v) {
    const { sr, r, P } = c, len = c.o.lengthS ?? c.j(v === "soft" ? 0.28 : 0.2, 0.1), N = secs(sr, len), b = new Bus(sr, secs(sr, len + 0.5));
    const [f1, f2] = v === "out" ? [3400, 1300] : v === "soft" ? [900, 1900] : [1300, 3400], pk = 0.35;
    const f = (t) => f1 * Math.pow(f2 / f1, smooth(t / len)) * P;
    const env = (t) => { const u = t / len; return u < pk ? 0.5 - 0.5 * Math.cos((Math.PI * u) / pk) : Math.exp(-(u - pk) * 4.5) * (1 - smooth((u - 0.85) / 0.15)); };
    const pan = (i) => c.dir * (-0.35 + (0.7 * i) / N);
    for (const side of [0, 1]) { const s = pink(r, N); sweep(s, sr, f, v === "soft" ? 0.9 : 1.3, "bp"); sweep(s, sr, f, 0.8, "bp"); shape(s, sr, env); b.add(s, 0, 1.4, (i) => pan(i) + (side ? 0.2 : -0.2)); }
    const t = white(r, N); sweep(t, sr, f, 6, "bp"); shape(t, sr, env); b.add(t, 0, v === "soft" ? 0.1 : 0.2, pan);
    space(b, r, { rt60: 0.35, mix: 0.08 });
    return { bus: b, hit: secs(sr, len * pk) };
  },
};

const riser = {
  variants: ["soft", "air", "tonal"], level: -15, duckDb: 2,
  use: "the ONE build into the big reveal: soft (the signature: air + a tuned chord), air (noise only), tonal (more chord). Tempo-synced: beats + bpm; hit = its end, on the downbeat",
  make(c, v) {
    const { sr, r } = c, len = c.o.lengthS ?? ((c.o.beats ?? 4) * 60) / c.bpm, N = secs(sr, len), b = new Bus(sr, N + secs(sr, 0.03));
    const [nz, tn] = v === "air" ? [1, 0] : v === "tonal" ? [0.45, 1] : [0.8, 0.55];
    const cut = (t) => Math.min(1, (len - t) / 0.02); // it stops ON the downbeat
    // 1 air: noise through a resonant low-pass opening 250 Hz -> 10 kHz, growing wider
    for (const side of [0, 1]) {
      const s = pink(r, N); sweep(s, sr, (t) => 250 * Math.pow(40, Math.pow(t / len, 1.4)), (t) => 1.2 + 1.6 * (t / len), "lp"); filt(s, sr, { hp: 160 });
      shape(s, sr, (t) => Math.pow(t / len, 2.2) * cut(t));
      b.add(s, 0, nz * 1.6, (i) => (side ? 1 : -1) * (0.15 + 0.6 * (i / N)));
    }
    // 2 a tuned chord (root, fifth, octave, the octave above fading in) pulsing in tempo: 8ths -> 16ths -> 32nds
    if (tn > 0) {
      const beat = c.bpm / 60, voices = [[keyHz(c, 3), -0.5, 0], [keyHz(c, 3, 7), 0.5, 0.5], [keyHz(c, 4), 0, 0.25], [keyHz(c, 5), 0, 0.75]];
      voices.forEach(([f, p, phase], vi) => {
        const s = buf(N); let ph = 0, tp = phase;
        for (let i = 0; i < N; i++) {
          const t = i / sr, u = t / len, rate = beat * (u < 0.5 ? 2 : u < 0.8 ? 4 : 8), I = 0.2 + 1.6 * u;
          tp += rate / sr; ph += (2 * Math.PI * f * c.P) / sr;
          const trem = 1 - (0.25 + 0.45 * u) * (0.5 + 0.5 * Math.cos(2 * Math.PI * tp));
          const fadeIn = vi === 3 ? smooth((u - 0.55) / 0.35) : 1;
          s[i] = Math.sin(ph + I * Math.sin(2 * ph)) * trem * Math.pow(u, 1.8) * fadeIn * cut(t);
        }
        b.add(s, 0, tn * 0.22, p);
      });
    }
    for (const ch of [b.L, b.R]) for (let i = 0; i < ch.length; i++) ch[i] = Math.tanh(ch[i] * 1.3) / 1.3;
    return { bus: b, hit: N };
  },
};

const impact = {
  variants: ["boom", "soft", "bloom"], level: -9, duckDb: 6,
  use: "the ONE big reveal (boom), a smaller landing (soft), the reveal with a tuned shimmer and a breath in before it (bloom)",
  make(c, v) {
    const { sr, r, P } = c, soft = v === "soft", pre = v === "bloom" ? secs(sr, 0.28) : 0, n = pre + secs(sr, soft ? 3.5 : 5.5), b = new Bus(sr, n);
    // 1 sub drop, saturated so small speakers still hear its harmonics
    const lo = c.j(soft ? 40 : 44, 0.04) * P, subTau = c.j(soft ? 0.32 : 0.6, 0.1), sub = chirp(sr, secs(sr, subTau * 8), (t) => lo + (soft ? 55 : 72) * P * Math.exp(-t / 0.07), ad(0.002, subTau));
    b.add(sub.map((x) => Math.tanh(x * 1.8) / Math.tanh(1.8)), pre, 1, 0);
    // 2 punch: dark noise + two chest modes, a hair wide
    b.add(burst(sr, r, 0.35, soft ? 0.05 : 0.07, { lp: soft ? 500 : 950, pink: true }), pre, soft ? 0.9 : 1.3, -0.1, 0.4);
    b.add(burst(sr, r, 0.35, soft ? 0.05 : 0.07, { lp: soft ? 500 : 950, pink: true }), pre, soft ? 0.9 : 1.3, 0.1, -0.4);
    b.add(modal(sr, n, [{ f: c.j(170, 0.06) * P, tau: 0.09, a: 1, att: 0.001 }, { f: c.j(96, 0.06) * P, tau: 0.15, a: 0.8, att: 0.001 }]), pre, soft ? 0.25 : 0.4, 0);
    if (!soft) b.add(burst(sr, r, 0.004, 0.0007, { hp: 1500 }), pre, 0.35, 0); // 3 the crack on top
    if (v === "bloom") {
      // a breath in before it: a reversed swell that stops on the hit
      for (const side of [0, 1]) { const s = pink(r, pre); sweep(s, sr, (t) => 400 * Math.pow(8, t / 0.28), 1, "lp"); shape(s, sr, (t) => Math.pow(t / 0.28, 3)); b.add(s, 0, 0.8, side ? 0.4 : -0.4); }
      // and a tuned shimmer on the key: root, 3rd, 5th, 9th in the upper octaves, spread across the field
      const third = c.key.minor ? 3 : 4;
      [[keyHz(c, 5), -0.6], [keyHz(c, 5, third), 0.6], [keyHz(c, 5, 7), -0.3], [keyHz(c, 6, 2), 0.3], [keyHz(c, 6), 0]].forEach(([f, p], k) => {
        const ms = glock(f * c.P, 1.5, 1, 0.02 + k * 0.012).map((m) => ({ ...m, att: 0.03 }));
        b.add(modal(sr, n, ms), pre, 0.09, p);
      });
    }
    space(b, r, { rt60: soft ? 1.2 : 2.4, mix: soft ? 0.2 : 0.34, hp: 120, lp: 3500, predelay: 0.02, er: 0.35 });
    return { bus: b, hit: pre };
  },
};

const chime = {
  variants: ["sparkle", "bell", "glint"], level: -17, duckDb: 1.5,
  use: "magic / success, tuned to the film's key: a rising pentatonic sparkle (sparkle), one bell (bell), a tiny glint on a highlight (glint)",
  make(c, v) {
    const { sr, r } = c, n = secs(sr, v === "bell" ? 6 : v === "glint" ? 2 : 4), b = new Bus(sr, n), scale = PENTA[c.key.minor ? "minor" : "major"];
    if (v === "bell") {
      b.add(modal(sr, n, glock(keyHz(c, 5) * c.P, 1.4, 1)), 0, 1, -0.1);
      b.add(modal(sr, n, glock(keyHz(c, 6, 7) * c.P, 0.9, 1, 0.004)), 0, 0.3, 0.3);
      b.add(burst(sr, r, 0.003, 0.0005, { hp: 5000 }), 0, 0.2, 0);
      space(b, r, { rt60: 1.6, mix: 0.25, hp: 400 });
      return { bus: b, hit: 0 };
    }
    const count = v === "glint" ? 2 : 4 + Math.floor(r() * 3), oct = v === "glint" ? 7 : 6, start = Math.floor(r() * 3);
    let t = 0;
    for (let k = 0; k < count; k++) {
      const d = start + k, f = keyHz(c, oct + Math.floor(d / 5), scale[d % 5]) * c.P, g = 0.6 + (0.4 * k) / count;
      const p = c.dir * (-0.55 + (1.1 * k) / Math.max(1, count - 1)) * (k % 2 ? 1 : 0.8);
      b.add(modal(sr, n, glock(f, v === "glint" ? 0.14 : c.j(0.5, 0.15), 1)), secs(sr, t), g, p);
      t += c.j(v === "glint" ? 0.04 : 0.055, 0.15);
    }
    if (v === "sparkle") { const s = [white(r, secs(sr, 1)), white(r, secs(sr, 1))]; for (const x of s) { filt(x, sr, { hp: 7500 }); shape(x, sr, ad(0.06, 0.3)); } b.add2(s[0], s[1], 0, 0.035); }
    space(b, r, { rt60: v === "glint" ? 0.8 : 1.8, mix: v === "glint" ? 0.15 : 0.3, hp: 400, predelay: 0.015 });
    return { bus: b, hit: 0 };
  },
};

export const SFX = { tick, press, pop, whoosh, swish, riser, impact, chime, paper, ink };
export const SFX_KINDS = Object.keys(SFX);
export const sfxInfo = (k) => ({ variants: SFX[k].variants, levelLufs: SFX[k].level, duckDb: SFX[k].duckDb, use: SFX[k].use });

const checkSeed = (seed) => { if (!Number.isSafeInteger(seed) || seed < 0 || seed > 0xffffffff) throw new Error(`sfx: seed must be an integer 0..4294967295, got ${String(seed)}`); };
const checkRange = (name, x, lo, hi) => { if (x !== undefined && (typeof x !== "number" || !Number.isFinite(x) || x < lo || x > hi)) throw new Error(`sfx: ${name} must be a number ${lo}..${hi}, got ${String(x)}`); };
export const validateSfx = (kind, o = {}) => {
  if (!(kind in SFX)) throw new Error(`sfx: unknown kind "${kind}" (kinds: ${SFX_KINDS.join(", ")})`);
  const d = SFX[kind];
  if (o.variant !== undefined && !d.variants.includes(o.variant)) throw new Error(`sfx: ${kind} has no variant "${o.variant}" (variants: ${d.variants.join(", ")})`);
  if (o.seed !== undefined) checkSeed(o.seed);
  checkRange("pitch", o.pitch, -24, 24); checkRange("lengthS", o.lengthS, 0.05, 30); checkRange("beats", o.beats, 0.25, 64); checkRange("bpm", o.bpm, 20, 300); checkRange("gainDb", o.gainDb, -60, 24);
  if (o.dir !== undefined && o.dir !== 1 && o.dir !== -1) throw new Error(`sfx: dir must be 1 or -1, got ${String(o.dir)}`);
  if (o.key !== undefined) parseKey(o.key);
};
/**
 * What a sound needs from the film: a key (tuned kinds) and a bpm (tempo-synced kinds). Never
 * defaulted: an effect tuned to a key the score isn't in, or pulsing at a tempo it isn't at, is wrong.
 */
export const sfxNeeds = (kind, variant, o = {}) => ({
  key: kind === "chime" || (kind === "riser" && variant !== "air") || (kind === "press" && variant === "confirm") || (kind === "impact" && variant === "bloom"),
  bpm: kind === "riser" && !(variant === "air" && o.lengthS !== undefined),
});
/**
 * Render one sound. Pure in (kind, opts, sr). The level is calibrated: the kind's target loudness
 * (K-weighted over its speaking window), +-1 dB per-seed variation, + opts.gainDb; peak capped at -1 dBFS.
 */
export const renderSfx = (kind, o = {}, sr = SR) => {
  validateSfx(kind, o);
  const d = SFX[kind], variant = o.variant ?? d.variants[0], seed = o.seed ?? 1, r = mkRng((seed ^ 0x5f3759df) >>> 0);
  const need = sfxNeeds(kind, variant, o);
  if (need.key && o.key === undefined) throw new Error(`sfx: ${kind}:${variant} is tuned and needs a key (opts.key or plan.key); there is no default key`);
  if (need.bpm && o.bpm === undefined) throw new Error(`sfx: ${kind}:${variant} is tempo-synced and needs a bpm (opts.bpm or plan.bpm); there is no default tempo`);
  const c = { sr, r, P: Math.pow(2, (o.pitch ?? 0) / 12), o, dir: o.dir ?? 1, key: o.key === undefined ? null : parseKey(o.key), bpm: o.bpm ?? NaN, j: (x, amt) => x * (1 + (r() * 2 - 1) * amt) };
  const made = d.make(c, variant), [L, R] = finish(made.bus, made.hit);
  const kL = kWeight(L, sr), kR = kWeight(R, sr), window = speakingWindow(kL, kR, sr), now = winLufs(kL, kR, window[0], window[1]);
  let g = d.level + (r() * 2 - 1) + (o.gainDb ?? 0) - now;
  let peak = 0; for (let i = 0; i < L.length; i++) peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i]));
  g = Math.min(g, -1 - dB(peak));
  const G = db(g); for (let i = 0; i < L.length; i++) { L[i] *= G; R[i] *= G; }
  return { L, R, sr, kind, variant, seed, hit: Math.min(made.hit, L.length - 1), window, lufs: now + g };
};

// ---------------------------------------------------------------- placement: cues by film frame over a music bed
const GRID = { bar: 0, beat: 1, "8th": 0.5, "16th": 0.25 };
const cueName = (c, i) => `cue #${i} (${c.kind}${c.variant ? ":" + c.variant : ""}${c.label ? ` "${c.label}"` : ""} @ frame ${c.frame})`;
const optsOf = (p, c, seed) => ({ seed: c.seed ?? seed, variant: c.variant, pitch: c.pitch, lengthS: c.lengthS, beats: c.beats, bpm: c.bpm ?? p.bpm, key: c.key ?? p.key, dir: c.dir, gainDb: c.gainDb });

export const validateSfxPlan = (p) => {
  if (!Number.isSafeInteger(p.fps) || p.fps <= 0) throw new Error(`sfx plan: fps must be a positive integer, got ${String(p.fps)}`);
  if (!Number.isSafeInteger(p.frames) || p.frames <= 0) throw new Error(`sfx plan: frames must be a positive integer, got ${String(p.frames)}`);
  if (p.seed !== undefined) checkSeed(p.seed);
  if (p.bpm !== undefined && (!Number.isFinite(p.bpm) || p.bpm < 20 || p.bpm > 300)) throw new Error(`sfx plan: bpm must be 20..300, got ${String(p.bpm)}`);
  if (!Array.isArray(p.cues)) throw new Error("sfx plan: cues must be an array");
  p.cues.forEach((c, i) => {
    if (!c || typeof c !== "object") throw new Error(`sfx plan: cue #${i} is not an object`);
    if (!(c.kind in SFX)) throw new Error(`sfx plan: cue #${i} has unknown kind "${String(c.kind)}" (kinds: ${SFX_KINDS.join(", ")})`);
    if (typeof c.frame !== "number" || !Number.isFinite(c.frame) || c.frame < 0 || c.frame >= p.frames) throw new Error(`sfx plan: ${cueName(c, i)}: frame must be 0..${p.frames - 1}`);
    if (!Number.isInteger(c.frame)) throw new Error(`sfx plan: ${cueName(c, i)}: frame must be a whole frame (cues are addressed by the frame the picture shows; for a hit between frames, snap it to the beat grid)`);
    const snap = c.snap ?? p.snap ?? "none";
    if (!(snap === "none" || snap in GRID)) throw new Error(`sfx plan: ${cueName(c, i)}: snap must be none|bar|beat|8th|16th`);
    if ((snap !== "none" || c.beats !== undefined) && p.bpm === undefined && c.bpm === undefined) throw new Error(`sfx plan: ${cueName(c, i)}: snap/beats need a bpm (plan.bpm)`);
    if (c.duckDb !== undefined && (!Number.isFinite(c.duckDb) || c.duckDb < 0 || c.duckDb > 18)) throw new Error(`sfx plan: ${cueName(c, i)}: duckDb must be 0..18`);
    try { validateSfx(c.kind, optsOf(p, c, 0)); } catch (e) { throw new Error(`sfx plan: ${cueName(c, i)}: ${e.message}`); }
    const o = optsOf(p, c, 0), need = sfxNeeds(c.kind, c.variant ?? SFX[c.kind].variants[0], o);
    if (need.key && o.key === undefined) throw new Error(`sfx plan: ${cueName(c, i)} is tuned: set plan.key or cue.key; there is no default key`);
    if (need.bpm && o.bpm === undefined) throw new Error(`sfx plan: ${cueName(c, i)} is tempo-synced: set plan.bpm or cue.bpm; there is no default tempo`);
  });
};

/** Taste rules, as warnings: one riser + one impact per film; at most 2 cues in any 100 ms. */
export const tasteWarnings = (p, placed) => {
  const warn = [];
  for (const kind of ["riser", "impact"]) {
    const of = p.cues.filter((c) => c.kind === kind);
    if (of.length > 1) warn.push(`taste: ${of.length} ${kind}s (frames ${of.map((c) => c.frame).join(", ")}); one ${kind} per film marks THE reveal, a second halves both`);
  }
  const times = placed.map((pc) => ({ t: pc.hitS, i: pc.i })).sort((a, b) => a.t - b.t);
  for (let i = 0; i + 2 < times.length; i++) if (times[i + 2].t - times[i].t <= 0.1)
    warn.push(`taste: 3+ cues within 100 ms around ${times[i].t.toFixed(2)} s (cues #${times[i].i}, #${times[i + 1].i}, #${times[i + 2].i}); at most 2 cues per 100 ms`);
  return warn;
};

/** Render and place every cue. Per-cue seed depends on (kind, frame, occurrence), never on list order. */
export const placeSfx = (p, sr = SR) => {
  validateSfxPlan(p);
  const seen = new Map(), filmS = p.frames / p.fps;
  return p.cues.map((cue, i) => {
    const k = `${cue.kind}@${cue.frame}`, occ = seen.get(k) ?? 0; seen.set(k, occ + 1);
    const seed = mixSeed(p.seed ?? 0, (strSeed(cue.kind) ^ Math.round(cue.frame * 1000) ^ (occ * 7919)) >>> 0);
    const t0 = cue.frame / p.fps, snap = cue.snap ?? p.snap ?? "none";
    let hitS = t0;
    if (snap !== "none") {
      const bpm = cue.bpm ?? p.bpm, beat = 60 / bpm, g = snap === "bar" ? beat * (p.beatsPerBar ?? 4) : beat * GRID[snap], z = p.beatZeroS ?? 0;
      hitS = z + Math.round((t0 - z) / g) * g;
      if (hitS >= filmS) hitS -= g;
      if (hitS < 0) hitS += g;
    }
    const sound = renderSfx(cue.kind, optsOf(p, cue, seed), sr), start = Math.round(hitS * sr) - sound.hit;
    if (start < 0) {
      const pre = sound.hit / sr, need = Math.ceil(pre * p.fps);
      throw new Error(`sfx plan: ${cueName(cue, i)}: its ${pre.toFixed(2)} s pre-roll starts before frame 0; move it to frame >= ${need} or shorten it (lengthS/beats)`);
    }
    return { i, cue, sound, hitS, snappedFromS: t0, start, window: [start + sound.window[0], start + sound.window[1]] };
  });
};

/** The bed's gain under the cues: raised-cosine dip (40 ms attack), held, released (280 ms; 1.2 s after an impact), capped at 9 dB. */
export const sfxDuck = (placed, n, sr, o = {}) => {
  const g = new Float32Array(n).fill(1), att = secs(sr, o.attackS ?? 0.04), maxDb = o.maxDb ?? 9;
  for (const pc of placed) {
    const depth = Math.min(maxDb, pc.cue.duckDb ?? SFX[pc.cue.kind].duckDb); if (depth <= 0) continue;
    const rel = secs(sr, pc.cue.kind === "impact" ? 1.2 : o.releaseS ?? 0.28), lo = db(-depth), [a, b] = pc.window;
    for (let i = Math.max(0, a - att); i < Math.min(n, b + rel); i++) {
      const s = i < a ? 0.5 - 0.5 * Math.cos((Math.PI * (i - (a - att))) / att) : i < b ? 1 : 0.5 + 0.5 * Math.cos((Math.PI * (i - b)) / rel);
      const v = 1 - (1 - lo) * s; if (v < g[i]) g[i] = v;
    }
  }
  return g;
};

/** Look-ahead true-peak ceiling (2 ms look-ahead, 80 ms release, 1.12 inter-sample margin). Returns deepest GR in dB. */
const ceiling = (L, R, sr, ceil) => {
  const n = L.length, la = secs(sr, 0.002), rel = Math.exp(-1 / (0.08 * sr)), need = new Float32Array(n), g = new Float32Array(n);
  for (let i = 0; i < n; i++) { const a = Math.max(Math.abs(L[i]), Math.abs(R[i])) * 1.12; need[i] = a > ceil ? ceil / a : 1; }
  for (let i = n - 1; i >= 0; i--) { let m = 1; for (let j = i; j < Math.min(n, i + la); j++) if (need[j] < m) m = need[j]; g[i] = m; }
  let cur = 1, deepest = 1;
  for (let i = 0; i < n; i++) { cur = g[i] < cur ? g[i] : 1 - (1 - cur) * rel; if (cur > g[i]) cur = g[i]; L[i] *= cur; R[i] *= cur; if (cur < deepest) deepest = cur; }
  return 20 * Math.log10(deepest);
};

/** Audibility of each cue vs the ducked bed over the cue's speaking window (the bed's window at least 100 ms). */
export const sfxAudibility = (placed, music, sr, p) => {
  const mL = kWeight(music[0], sr), mR = kWeight(music[1], sr), minWin = secs(sr, 0.1);
  return placed.map((pc) => {
    const s = pc.sound, kL = kWeight(s.L, sr), kR = kWeight(s.R, sr), [wa, wb] = s.window, cueLufs = winLufs(kL, kR, wa, wb);
    let [a, b] = pc.window; if (b - a < minWin) { const c = (a + b) >> 1; a = c - (minWin >> 1); b = a + minWin; }
    const musicLufs = winLufs(mL, mR, a, b);
    const silent = musicLufs < -70, marginDb = silent ? 99 : cueLufs - musicLufs;
    const minDb = pc.cue.minDb ?? p.minDb ?? -6;
    return { i: pc.i, kind: pc.cue.kind, variant: s.variant, label: pc.cue.label ?? "", atS: pc.hitS, cueLufs, musicLufs, marginDb, minDb, ok: marginDb >= minDb };
  });
};

/**
 * The whole film's sound: bed (padded or cut to the film) ducked under the cues, effects added,
 * one look-ahead true-peak ceiling at -1 dBTP. music = [L, R] Float32Arrays at `sr`, or null.
 */
export const mixSfx = (music, p, sr = SR) => {
  const n = Math.round((p.frames / p.fps) * sr), placed = placeSfx(p, sr);
  const warnings = tasteWarnings(p, placed);
  const fxL = new Float32Array(n), fxR = new Float32Array(n);
  for (const pc of placed) { const { L, R } = pc.sound; for (let i = 0; i < L.length && pc.start + i < n; i++) { fxL[pc.start + i] += L[i]; fxR[pc.start + i] += R[i]; } }
  const duck = sfxDuck(placed, n, sr, p.duck), mL = new Float32Array(n), mR = new Float32Array(n);
  if (music) { const m = Math.min(n, music[0].length); for (let i = 0; i < m; i++) { mL[i] = music[0][i] * duck[i]; mR[i] = music[1][i] * duck[i]; } }
  const L = new Float32Array(n), R = new Float32Array(n);
  for (let i = 0; i < n; i++) { L[i] = mL[i] + fxL[i]; R[i] = mR[i] + fxR[i]; }
  const limiterDb = ceiling(L, R, sr, db((p.ceilingDb ?? -1) - 0.3));
  const fade = Math.min(n, secs(sr, 0.015)); for (let i = 0; i < fade; i++) { const g = i / fade; L[n - 1 - i] *= g; R[n - 1 - i] *= g; }
  const audibility = sfxAudibility(placed, [mL, mR], sr, p);
  return { L, R, sfx: [fxL, fxR], music: [mL, mR], duck, placed, audibility, warnings, ok: audibility.every((a) => a.ok), lufs: integratedLufs(L, R, sr), dbtp: truePeak([L, R]) };
};

/** A cue nobody hears is a bug, not a subtle choice. */
export const assertSfxAudible = (m) => {
  const bad = m.audibility.filter((a) => !a.ok);
  if (bad.length) throw new Error(`buried cue: ${bad.length} cue(s) under the bed:\n` + bad.map((a) => `  #${a.i} ${a.kind}:${a.variant}${a.label ? ` "${a.label}"` : ""} @ ${a.atS.toFixed(2)} s is ${a.marginDb.toFixed(1)} dB vs the bed (floor ${a.minDb} dB): raise its gainDb or its duckDb`).join("\n"));
  return m;
};

// ---------------------------------------------------------------- io
/** 32-bit float stereo WAV (no clipping on the way to the encoder). */
export const writeWavFloat = (path, L, R, sr = SR) => {
  const n = L.length, data = Buffer.alloc(n * 8), h = Buffer.alloc(44);
  for (let i = 0; i < n; i++) { data.writeFloatLE(L[i], i * 8); data.writeFloatLE(R[i], i * 8 + 4); }
  h.write("RIFF", 0); h.writeUInt32LE(36 + data.length, 4); h.write("WAVEfmt ", 8); h.writeUInt32LE(16, 16); h.writeUInt16LE(3, 20); h.writeUInt16LE(2, 22);
  h.writeUInt32LE(sr, 24); h.writeUInt32LE(sr * 8, 28); h.writeUInt16LE(8, 32); h.writeUInt16LE(32, 34); h.write("data", 36); h.writeUInt32LE(data.length, 40);
  writeFileSync(path, Buffer.concat([h, data]));
};
const writeAudio = (path, L, R) => {
  if (/\.(mp3|m4a|aac|flac|ogg)$/i.test(path)) { // ffmpeg only for the final encode
    const w = path + ".tmp.wav"; writeWavFloat(w, L, R, SR);
    execFileSync("ffmpeg", ["-v", "error", "-y", "-i", w, path]); execFileSync("rm", [w]);
  } else writeWavFloat(path, L, R, SR);
};
/** Decode any audio file to 48 kHz stereo float via ffmpeg. */
export const readBed = (path) => {
  const raw = execFileSync("ffmpeg", ["-v", "error", "-i", path, "-ac", "2", "-ar", String(SR), "-f", "f32le", "-"], { maxBuffer: 1 << 30 });
  const n = Math.floor(raw.length / 8), L = new Float32Array(n), R = new Float32Array(n);
  for (let i = 0; i < n; i++) { L[i] = raw.readFloatLE(i * 8); R[i] = raw.readFloatLE(i * 8 + 4); }
  return [L, R];
};

// ---------------------------------------------------------------- cli
const peakOf = (L, R) => { let p = 0; for (let i = 0; i < L.length; i++) p = Math.max(p, Math.abs(L[i]), Math.abs(R[i])); return p; };
const envOpts = () => ({ key: process.env.KEY, bpm: process.env.BPM ? Number(process.env.BPM) : undefined, lengthS: process.env.LEN ? Number(process.env.LEN) : undefined });

const cmdList = () => {
  for (const k of SFX_KINDS) { const i = sfxInfo(k); console.log(`${k.padEnd(8)} [${i.variants.join(", ")}]  level ${i.levelLufs} LUFS(win), duck ${i.duckDb} dB\n         ${i.use}`); }
};
const cmdOne = (args) => {
  const out = args.pop(), [kind, variant, seed] = args;
  const s = renderSfx(kind, { variant, seed: seed ? Number(seed) : undefined, ...envOpts() }, SR);
  writeAudio(out, s.L, s.R);
  console.log(`${kind}:${s.variant} seed ${s.seed}: ${(s.L.length / SR).toFixed(2)} s, hit @ ${(s.hit / SR).toFixed(3)} s, ${s.lufs.toFixed(1)} LUFS(win), peak ${dB(peakOf(s.L, s.R)).toFixed(1)} dBFS`);
};
/** Every kind x variant, 3 seeds each: WAV out + metrics vs target (exit 1 if any fails). */
const cmdKit = (outdir) => {
  const dir = resolve(outdir); mkdirSync(dir, { recursive: true });
  let fail = 0; const meters = {};
  console.log("kind:variant        len(s)          hit(s)  LUFS(win) x3        target  worst-off  peak dBFS  ok");
  for (const kind of SFX_KINDS) {
    const info = sfxInfo(kind);
    for (const variant of info.variants) {
      const hits = [1, 2, 3].map((seed) => renderSfx(kind, { variant, seed, key: "C", bpm: 90 }, SR));
      // one listen-file per variant: the 3 varied hits back to back
      const gap = secs(SR, 0.35), lead = secs(SR, 0.15), n = lead + hits.reduce((a, h) => a + h.L.length + gap, 0);
      const L = new Float32Array(n), Rr = new Float32Array(n); let at = lead;
      for (const h of hits) { L.set(h.L, at); Rr.set(h.R, at); at += h.L.length + gap; }
      writeWavFloat(join(dir, `${kind}-${variant}.wav`), L, Rr, SR);
      const lens = hits.map((h) => h.L.length / SR), lufs = hits.map((h) => h.lufs), peak = dB(peakOf(L, Rr));
      const worstOff = Math.max(...lufs.map((l) => Math.abs(l - info.levelLufs)));
      const durOk = lens.every((l) => l >= 0.05 && l <= 12), clipOk = peak <= -0.99, lvlOk = worstOff <= 2;
      const finiteOk = hits.every((h) => { for (let i = 0; i < h.L.length; i++) if (!Number.isFinite(h.L[i]) || !Number.isFinite(h.R[i])) return false; return true; });
      const ok = durOk && clipOk && lvlOk && finiteOk; if (!ok) fail++;
      meters[`${kind}:${variant}`] = { lens, lufs, target: info.levelLufs, peak, ok };
      console.log(`${(kind + ":" + variant).padEnd(18)} ${lens.map((l) => l.toFixed(2)).join("/").padEnd(15)} ${(hits[0].hit / SR).toFixed(3).padStart(6)}  ${lufs.map((l) => l.toFixed(1)).join(" / ").padEnd(20)} ${String(info.levelLufs).padStart(5)}  ${worstOff.toFixed(2).padStart(8)}  ${peak.toFixed(1).padStart(8)}  ${ok ? "ok" : "FAIL" + (durOk ? "" : " dur") + (clipOk ? "" : " clip") + (lvlOk ? "" : " level")}`);
    }
  }
  writeFileSync(join(dir, "meters.json"), JSON.stringify(meters, null, 1));
  console.log(fail ? `\n${fail} variant(s) FAILED` : `\nall variants ok -> ${dir}`);
  process.exit(fail ? 1 : 0);
};
const cmdMix = async (planPath, bedPath, outPath) => {
  const plan = JSON.parse(await readFile(planPath, "utf8"));
  const bed = readBed(bedPath);
  if (plan.frames === undefined) plan.frames = Math.floor((bed[0].length / SR) * plan.fps);
  const m = mixSfx(bed, plan, SR);
  for (const w of m.warnings) console.error(w);
  console.log(`#   kind:variant      frame  hit(s)   cue LUFS  bed LUFS  margin  floor  ok`);
  for (const a of m.audibility) {
    const pc = m.placed[a.i];
    console.log(`${String(a.i).padEnd(3)} ${(a.kind + ":" + a.variant).padEnd(17)} ${String(pc.cue.frame).padStart(5)}  ${a.atS.toFixed(3).padStart(6)}  ${a.cueLufs.toFixed(1).padStart(8)}  ${a.musicLufs.toFixed(1).padStart(8)}  ${a.marginDb.toFixed(1).padStart(6)}  ${String(a.minDb).padStart(5)}  ${a.ok ? "ok" : "BURIED"}${a.label ? "  " + a.label : ""}`);
  }
  assertSfxAudible(m); // throws "buried cue: ..." naming each one
  writeAudio(outPath, m.L, m.R);
  let duckMin = 1; for (let i = 0; i < m.duck.length; i++) if (m.duck[i] < duckMin) duckMin = m.duck[i];
  console.log(`\n${outPath}: ${(m.L.length / SR).toFixed(2)} s, ${plan.cues.length} cues, ${m.lufs.toFixed(1)} LUFS, ${m.dbtp.toFixed(2)} dBTP, deepest duck ${dB(duckMin).toFixed(1)} dB, all cues audible: ${m.ok}`);
};

// compare real paths: the skill is often installed as a symlink, and a plain URL compare then says "not main" and the script exits without a word
const realOf = (p) => { try { return realpathSync(p); } catch { return resolve(p); } };
const isMain = !!process.argv[1] && realOf(fileURLToPath(import.meta.url)) === realOf(process.argv[1]);
if (isMain) {
  const [cmd, ...args] = process.argv.slice(2);
  if (cmd === "list") cmdList();
  else if (cmd === "one" && args.length >= 2) cmdOne(args);
  else if (cmd === "kit" && args[0]) cmdKit(args[0]);
  else if (cmd === "mix" && args.length === 3) await cmdMix(args[0], args[1], args[2]);
  else { console.log("usage: node sfx.mjs list | one <kind> [variant] [seed] <out.wav> | kit <outdir> | mix <plan.json> <bed> <out.wav>"); process.exit(cmd ? 1 : 0); }
}
