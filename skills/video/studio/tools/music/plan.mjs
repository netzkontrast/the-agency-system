// Adapted from anidoodle (github.com/alexgreensh/anidoodle), Apache License 2.0, Copyright 2026 Alex Greenshpun
// The Piece/Section/Part model, the bar-checked line() text notation, the plan validator, and
// resequence() (repeat/drop sections so a piece fits any film duration).
//
// A Note is { t, d, p, v, role, roll?, kind? }: t, d in beats from the piece start; p = MIDI;
// v = written velocity 0..1 (performance shapes it). Roles: melody | inner | bass | accomp | color | drum.
import { midi, MODES, detectMode, pcOf, modeFit } from "./theory.mjs";
import { MOODS, STYLES, REFUSED_BLENDS } from "./tables.mjs";

export const beatsPerBar = (m) => (m === "3/4" ? 3 : m === "4/4" ? 4 : m === "6/8" ? 2 : 4);

// ---------------------------------------------------------------- notation
// "Eb4:1 | C5:2 Bb4:.5 Ab4:.5 | [Ab2 Eb3]:1 r:2 | G5:1/3@0.8 ..." ; a token is NOTE:DUR[@VEL] or
// [CHORD]:DUR[@VEL] or r:DUR. Every bar must sum to the meter, the last one too (a line that ends
// mid-bar writes its rest: "C2:3 r:1"): a wrong bar throws, so a gap is always written, never
// silent. The first bar may instead be a declared `pickup`, or, when the line starts off the
// barline, exactly the beats left to the next barline. A `hit` (a ping, a sting placed on any beat)
// is one bar no longer than the meter, said out loud with `hit: true`.
const dur = (s) => { if (s.includes("/")) { const [a, b] = s.split("/").map(Number); return a / b; } return Number(s); };
export const line = (start, src, o) => {
  const out = []; let t = start; const bars = src.split("|").map((b) => b.trim()).filter((b, i, a) => b.length || (i > 0 && i < a.length - 1));
  if (o.hit && bars.length !== 1) throw new Error(`a hit is one bar, got ${bars.length}: "${src}"`);
  bars.forEach((bar, bi) => {
    let sum = 0;
    for (const tok of bar.split(/\s+(?![^\[]*\])/).filter(Boolean)) {
      const m = /^(\[[^\]]+\]|[^:]+):([0-9./]+)(?:@([0-9.]+))?$/.exec(tok); if (!m) throw new Error(`bad token "${tok}" in "${bar}"`);
      const d = dur(m[2]), vel = (o.v ?? 0.7) * (m[3] ? Number(m[3]) : 1);
      if (m[1] !== "r") {
        const names = m[1].startsWith("[") ? m[1].slice(1, -1).trim().split(/\s+/) : [m[1]];
        for (const nm of names) out.push({ t, d, p: midi(nm), v: vel, role: o.role, roll: names.length > 1 ? o.roll ?? 0.012 : undefined, kind: o.kind });
      }
      t += d; sum += d;
    }
    const first = bi === 0, toBarline = o.bpb - (((start % o.bpb) + o.bpb) % o.bpb);
    const ok = Math.abs(sum - o.bpb) < 1e-6 || (first && o.pickup !== undefined && Math.abs(sum - o.pickup) < 1e-6) || (first && toBarline < o.bpb - 1e-6 && Math.abs(sum - toBarline) < 1e-6) || (o.hit === true && sum <= o.bpb + 1e-6);
    if (!ok) throw new Error(`bar ${bi} sums to ${+sum.toFixed(4)} beats, meter wants ${o.bpb}: "${bar}"${sum < o.bpb && bi === bars.length - 1 ? ` (a line that ends mid-bar writes its rest: "${bar} r:${+(o.bpb - sum).toFixed(4)}")` : ""}`);
  });
  return out;
};

// ---------------------------------------------------------------- validation
export const planProblems = (p) => {
  const probs = [], plan = p.plan, st = STYLES[plan.style], bpb = beatsPerBar(plan.meter);
  if (!st) probs.push(`unknown style ${plan.style}`);
  else if (plan.tempo < st.tempo[0] * 0.85 || plan.tempo > st.tempo[1] * 1.15) probs.push(`tempo ${plan.tempo} far outside style ${st.id} ${st.tempo.join("-")}`);
  let b0 = -(plan.pickupBeats ?? 0);
  for (const s of plan.sections) {
    const ids = Array.isArray(s.mood) ? [s.mood[0], s.mood[1]] : [s.mood];
    for (const id of ids) if (!MOODS[id]) probs.push(`${s.id}: unknown mood ${id}`);
    if (Array.isArray(s.mood) && REFUSED_BLENDS.some(([a, b]) => (a === s.mood[0] && b === s.mood[1]) || (a === s.mood[1] && b === s.mood[0]))) probs.push(`${s.id}: refused blend ${s.mood[0]}+${s.mood[1]}`);
    if (!MODES[s.mode]) probs.push(`${s.id}: unknown mode ${s.mode}`);
    const lo = b0, hi = b0 + s.bars * bpb + (b0 < 0 ? plan.pickupBeats ?? 0 : 0);
    const notes = p.parts.flatMap((pt) => pt.notes).filter((n) => n.t >= lo && n.t < hi && n.role !== "drum");
    if (notes.length) {
      const top = detectMode(notes, [s.mode, "major", "aeolian", "dorian", "mixolydian", "lydian"]);
      const want = pcOf(s.key.replace(/m$/, ""));
      const hit = top.slice(0, 2).some((c) => pcOf(c.tonic) === want && c.mode === s.mode);
      // a mode shares its notes with its relatives (D dorian = C major): accept the declared tonic when its scale explains the notes
      // as well as the winner does and the tonic is heard (>= 8 % of note time). Otherwise the tonic is not dominant enough.
      const fit = modeFit(notes, want, s.mode), best = modeFit(notes, pcOf(top[0].tonic), top[0].mode);
      if (!hit && !(fit.inScale >= best.inScale - 0.02 && fit.tonicShare >= 0.08)) probs.push(`${s.id}: declared ${s.key} ${s.mode}, notes measure ${top.map((c) => `${c.tonic} ${c.mode}`).join(" / ")} (tonic ${s.key} is ${Math.round(fit.tonicShare * 100)} % of note time, ${Math.round(fit.inScale * 100)} % in scale): make the tonic heard (bass on it at section starts and cadences) and state the mode's colour note`);
    }
    b0 = hi;
  }
  // voice guard: no close thirds below C3 in piano parts (nocturne style guard)
  for (const pt of p.parts) if (pt.inst === "piano") {
    const by = new Map(); for (const n of pt.notes) { const k = Math.round(n.t * 96); by.set(k, [...(by.get(k) ?? []), n.p]); }
    for (const [k, ps] of by) { ps.sort((a, b) => a - b); for (let i = 1; i < ps.length; i++) if (ps[i] < 48 && ps[i] - ps[i - 1] <= 4) probs.push(`close third below C3 at beat ${k / 96}`); }
  }
  return probs;
};

// ---------------------------------------------------------------- fit to any duration
/** Section beat spans [start, end) in piece beats (pickup lives before 0 and belongs to section 0). */
export const sectionSpans = (plan) => { const bpb = beatsPerBar(plan.meter); let b = 0; return plan.sections.map((s, i) => { const a = i === 0 ? -(plan.pickupBeats ?? 0) : b; b += s.bars * bpb; return { s, a, b: b }; }); };

/** Apply a repeat variation ("same" | "octaveDouble" | "octaveUp" | "thin") to one section's notes. */
const vary = (notes, v) => {
  if (v === "octaveDouble") return [...notes, ...notes.filter((n) => n.role === "melody").map((n) => ({ ...n, p: n.p - 12, role: "inner", v: n.v * 0.8 }))];
  if (v === "octaveUp") return notes.map((n) => (n.role === "melody" ? { ...n, p: n.p + 12, v: n.v * 0.9 } : n));
  if (v === "thin") return notes.filter((n) => n.role !== "accomp" || Math.abs(n.t - Math.round(n.t)) < 1e-6);
  return notes;
};

/**
 * Rebuild a piece from a list of section indices (repeat/drop), shifting notes and chords.
 * A section's `pickup` (melody beats before its downbeat) travels with it. Repeats cycle through
 * the section's `variations` so a returning theme is never a photocopy.
 */
export const resequence = (p, order) => {
  const spans = sectionSpans(p.plan); const parts = p.parts.map((pt) => ({ ...pt, notes: [] })); const harmony = []; const sections = [];
  let cursor = 0; const bpb = beatsPerBar(p.plan.meter), seen = new Map();
  order.forEach((si, k) => {
    const sec = p.plan.sections[si], sp = spans[si], start = si === 0 ? 0 : sp.a, len = sec.bars * bpb, shift = cursor - start;
    const rep = seen.get(si) ?? 0; seen.set(si, rep + 1);
    const vr = rep > 0 && sec.variations?.length ? sec.variations[(rep - 1) % sec.variations.length] : "same";
    const pk = si === 0 ? p.plan.pickupBeats ?? 0 : sec.pickup ?? 0;
    p.parts.forEach((pt, j) => {
      const body = pt.notes.filter((n) => n.t >= start && n.t < sp.b).map((n) => ({ ...n, t: n.t + shift }));
      if (pk > 0) {
        if (k > 0) parts[j].notes = parts[j].notes.filter((n) => !(n.role === "melody" && n.t >= cursor - pk - 1e-9));
        parts[j].notes.push(...vary(pt.notes.filter((n) => n.role === "melody" && n.t >= start - pk && n.t < start).map((n) => ({ ...n, t: n.t + shift })), vr));
      }
      parts[j].notes.push(...vary(body, vr));
    });
    for (const c of p.harmony) if (c.t >= (si === 0 ? -1e9 : start) && c.t < sp.b) harmony.push({ ...c, t: c.t + shift });
    sections.push({ ...sec, id: rep ? `${sec.id}#${rep}${vr === "same" ? "" : `(${vr})`}` : sec.id });
    cursor += len;
  });
  const pickupBeats = order[0] === 0 ? p.plan.pickupBeats : p.plan.sections[order[0]].pickup ?? 0;
  return { ...p, parts, harmony, plan: { ...p.plan, sections, pickupBeats } };
};
