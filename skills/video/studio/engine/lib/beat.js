// engine/lib/beat.js — the song map as pure functions of time t, for any medium (paint, canvas, pathtracer).
//
// Load it after a script that sets window.SONGMAP (tools/audio/songmap_js.py writes songmap.js from
// songmap/beatmap.json + songmap/words.json). Without a song map it falls back to a fixed tempo
// (PROJECT.bpm / PROJECT.offset when the paint medium is loaded, else 120 bpm from 0 s).
//
//   SONG.beatAt(t)    fractional beat index; follows the measured beats, so tempo ramps (60 → 90 bpm) stay in sync
//   SONG.barAt(t)     fractional bar index from the measured downbeats
//   SONG.pulse(t, k)  1 exactly on each beat, decaying after (k = decay speed)
//   SONG.downbeat(n)  time of bar n's downbeat
//   SONG.section(t)   { name, kind, t, end } of the song section at t (hook, verse, build, drop, stop, release …)
//   SONG.word(t)      the sung word at t: { w, t, end, stress, line } or null
//   SONG.line(i)      lyric line i: { i, text, t, end, key: { w, t, stress } }
//   SONG.hit(name)    a named event time from the map: 'drop', 'lastHit', or an index into hits[]
// Everything is deterministic and keeps no state between frames.
(function (root) {
  const M = root.SONGMAP || null;
  const P = root.PROJECT || {};
  const fixedBeat = 60 / (P.bpm || 120), fixedOff = P.offset || 0;
  const beats = (M && M.beats && M.beats.length > 1) ? M.beats : null;
  const downs = (M && M.downbeats && M.downbeats.length > 1) ? M.downbeats : null;

  // Piecewise-linear index into a sorted list of times; extrapolates with the first/last interval.
  function indexAt(list, t) {
    const n = list.length;
    if (t <= list[0]) return (t - list[0]) / (list[1] - list[0]);
    if (t >= list[n - 1]) return n - 1 + (t - list[n - 1]) / (list[n - 1] - list[n - 2]);
    let lo = 0, hi = n - 1;
    while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (list[mid] <= t) lo = mid; else hi = mid; }
    return lo + (t - list[lo]) / (list[hi] - list[lo]);
  }
  function timeAt(list, i) {
    const n = list.length;
    if (i <= 0) return list[0] + i * (list[1] - list[0]);
    if (i >= n - 1) return list[n - 1] + (i - n + 1) * (list[n - 1] - list[n - 2]);
    const k = Math.floor(i); return list[k] + (i - k) * (list[k + 1] - list[k]);
  }
  const beatAt = (t) => (beats ? indexAt(beats, t) : (t - fixedOff) / fixedBeat);
  const barAt = (t) => (downs ? indexAt(downs, t) : beatAt(t) / 4);
  const frac = (x) => x - Math.floor(x);
  const SONG = {
    map: M,
    beatAt, barAt,
    pulse: (t, k = 6) => Math.exp(-frac(beatAt(t)) * k),
    beatTime: (i) => (beats ? timeAt(beats, i) : fixedOff + i * fixedBeat),
    downbeat: (n) => (downs ? timeAt(downs, n) : fixedOff + n * 4 * fixedBeat),
    section(t) {
      const s = (M && M.sections) || [];
      for (let i = s.length - 1; i >= 0; i--) if (t >= s[i].t) return s[i];
      return null;
    },
    word(t) {
      const w = (M && M.words) || [];
      let lo = 0, hi = w.length - 1, best = null;
      while (lo <= hi) { const mid = (lo + hi) >> 1; if (w[mid].t <= t) { best = mid; lo = mid + 1; } else hi = mid - 1; }
      return best != null && t < w[best].end ? w[best] : null;
    },
    line: (i) => ((M && M.lines) || [])[i] || null,
    hit(name) {
      if (!M) return null;
      if (name === 'drop') return M.drop ?? null;
      if (name === 'lastHit') return M.lastHit ?? (M.hits && M.hits.length ? M.hits[M.hits.length - 1] : null);
      return (M.hits || [])[name] ?? null;
    },
  };
  root.SONG = SONG;
  // Paint medium: route its beat clock (pulse, beatN, dances) through the song map.
  try { if (beats && typeof bpOf !== 'undefined') bpOf = beatAt; } catch (e) { /* bpOf is const in an old core.js */ }
  if (typeof module !== 'undefined') module.exports = SONG;
})(typeof window !== 'undefined' ? window : globalThis);
