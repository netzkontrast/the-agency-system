// scenes/recipes.js — recipe sampler, canvas medium (references/style-recipes.md). Each recipe: setup(ctx) once
// (seeded data, bakes, fonts), draw(g, t, state) a pure function of t.
//
//   node <studio>/tools/render.mjs --stills=2 --size=480x270 --query=recipe=stained-glass --out=review/stained-glass
//
// Without ?recipe= DEFAULT_RECIPE is used (the gate cannot pass a query: switch it to gate another recipe).
import { createNoise2D, createNoise3D } from 'simplex-noise';

export const DEFAULT_RECIPE = 'stained-glass';

// culori and opentype come in as classic globals (see film.html); as ESM it would be
// `import { interpolate, formatHex } from 'culori'` and `import * as opentype from 'opentype.js'` (no default export)
const { d3, Alea, Spring, opentype } = window;
const { interpolate, formatHex } = window.culori;

export const RECIPES = {
  // ------------------------------------------------------------------ 15. stained glass (d3.Delaunay Voronoi)
  'stained-glass': {
    n: 15, title: 'Stained glass',
    async setup({ W, H }) {
      const rnd = new Alea('glass'), n2 = createNoise2D(new Alea('glass-drift'));
      // a rose window: rings of seeds around the centre plus a jittered field, all from a seeded rng
      const pts = [], cx = W / 2, cy = H / 2, R0 = Math.min(W, H) * 0.46;
      pts.push([cx, cy]);
      for (const [ring, count] of [[0.16, 6], [0.34, 12], [0.55, 18], [0.78, 24], [1.0, 30]])
        for (let i = 0; i < count; i++) { const a = (i + (ring * 7 % 1)) / count * Math.PI * 2; pts.push([cx + Math.cos(a) * R0 * ring, cy + Math.sin(a) * R0 * ring]); }
      for (let i = 0; i < 140; i++) pts.push([rnd() * W, rnd() * H]);
      const glass = ['#1d4fa8', '#9c1630', '#e0a21b', '#17784a', '#2a68c9', '#c22a3c', '#5b2a86'];
      const cols = pts.map((p, i) => { const d = Math.hypot(p[0] - cx, p[1] - cy) / R0; return d > 1.05 ? (rnd() < .5 ? '#1d3f7a' : '#16305e') : glass[Math.floor(rnd() * glass.length)]; });
      return { pts, cols, n2, cx, cy, R0 };
    },
    draw(g, t, { pts, cols, n2, R0 }) {
      const W = g.canvas.width, H = g.canvas.height, s = H / 1080;
      // cells stay put; they move a few px with snoise so nothing re-triangulates into a pop
      const live = pts.map(([x, y], i) => [x + 3 * s * n2(i * 0.37, t * 0.2), y + 3 * s * n2(i * 0.37 + 50, t * 0.2)]);
      const vor = d3.Delaunay.from(live).voronoi([0, 0, W, H]);
      g.fillStyle = '#1b1714'; g.fillRect(0, 0, W, H);
      for (let i = 0; i < live.length; i++) {
        g.beginPath(); vor.renderCell(i, g); g.fillStyle = cols[i]; g.fill();
        // glass texture: a darker rim inside each cell
        g.save(); g.clip(); g.globalAlpha = 0.35; g.lineWidth = 14 * s; g.strokeStyle = '#000'; g.stroke(); g.restore();
      }
      // leading
      g.beginPath(); vor.render(g); vor.renderBounds(g); g.lineWidth = 6 * s; g.strokeStyle = '#1b1714'; g.lineJoin = 'round'; g.stroke();
      // light pass: a slow sun sweep through the glass, radial gradient 'lighter' at 30 %, a soft bloom on the beat
      const lx = W * (0.2 + 0.6 * (0.5 + 0.5 * Math.sin(t * 0.35))), ly = H * 0.3;
      const pulse = window.SONG ? window.SONG.pulseSoft(t) : 0;
      const rg = g.createRadialGradient(lx, ly, 0, lx, ly, R0 * (1.2 + 0.15 * pulse));
      rg.addColorStop(0, 'rgba(255,240,200,1)'); rg.addColorStop(1, 'rgba(255,240,200,0)');
      g.globalCompositeOperation = 'lighter'; g.globalAlpha = 0.3; g.fillStyle = rg; g.fillRect(0, 0, W, H);
      g.globalAlpha = 1; g.globalCompositeOperation = 'source-over';
    },
  },

  // ------------------------------------------------------------------ 41. generative flow field (baked in setup)
  'flow-field': {
    n: 41, title: 'Generative flow field',
    async setup({ duration }) {
      // positions integrated ONCE from t = 0 at fixed dt in a 1920×1080 design space, then drawn per frame
      const n3 = createNoise3D(new Alea('flow')), rnd = new Alea('flow-seeds');
      const N = 4000, fps = 24, steps = Math.ceil(duration * fps) + 1, VW = 1920, VH = 1080, speed = 140 / fps;
      // a plain noise-angle field is not divergence-free: within ~2 s every particle collapses into a few sink lines.
      // So each particle lives 1–2.5 s and is reborn at a seeded place (README problem 9); AGE[] = seconds since birth.
      const X = new Float32Array(N * steps), Y = new Float32Array(N * steps), AGE = new Float32Array(N * steps);
      for (let i = 0; i < N; i++) {
        let x = rnd() * VW, y = rnd() * VH, life = 1 + 1.5 * rnd(), age = rnd() * life;
        for (let f = 0; f < steps; f++) {
          if (age >= life) { x = rnd() * VW; y = rnd() * VH; life = 1 + 1.5 * rnd(); age = 0; }
          X[i * steps + f] = x; Y[i * steps + f] = y; AGE[i * steps + f] = age / life; age += 1 / fps;
          const a = n3(x * 0.0015, y * 0.0015, (f / fps) * 0.05) * Math.PI * 2;
          x += Math.cos(a) * speed; y += Math.sin(a) * speed;
          if (x < -20) x += VW + 40; if (x > VW + 20) x -= VW + 40; if (y < -20) y += VH + 40; if (y > VH + 20) y -= VH + 40;
        }
      }
      const ramp = interpolate(['#0b132b', '#5bc0be', '#f5f5f5'], 'oklch');
      const colours = Array.from({ length: 16 }, (_, k) => formatHex(ramp(k / 15)));
      return { X, Y, AGE, N, steps, fps, VW, VH, colours };
    },
    draw(g, t, { X, Y, AGE, N, steps, fps, VW, VH, colours }) {
      const W = g.canvas.width, H = g.canvas.height, s = Math.min(W / VW, H / VH);
      g.fillStyle = '#0b132b'; g.fillRect(0, 0, W, H);
      g.setTransform(s, 0, 0, s, (W - VW * s) / 2, (H - VH * s) / 2);
      const f = Math.min(steps - 1, Math.round(t * fps)), f0 = Math.max(0, f - 12);   // trail segments [f-12, f]
      g.lineWidth = 1.6; g.lineCap = 'round';
      for (let i = 0; i < N; i++) {
        const age = AGE[i * steps + f];                                                // colour along particle age
        g.strokeStyle = colours[Math.floor(age * 15.999)]; g.globalAlpha = 0.75;
        g.beginPath();
        for (let k = f0; k <= f; k++) {
          const x = X[i * steps + k], y = Y[i * steps + k];
          if (k === f0 || AGE[i * steps + k] < AGE[i * steps + k - 1] || Math.abs(x - X[i * steps + k - 1]) > 100 || Math.abs(y - Y[i * steps + k - 1]) > 100) g.moveTo(x, y); else g.lineTo(x, y);
        }
        g.stroke();
      }
    },
  },

  // ------------------------------------------------------------------ 37. kinetic typography (one word, springs)
  'kinetic-type': {
    n: 37, title: 'Kinetic typography',
    async setup() {
      // the font is loaded as an ArrayBuffer before READY (DejaVu Sans Bold, subset to the word's letters)
      const font = opentype.parse(await (await fetch('assets/dejavu-sans-bold-subset.ttf')).arrayBuffer());
      // no song map in the sampler: one stressed word at a fixed time stands in for SONG.word(t)
      const fallback = { w: 'RESONANCE', t: 1.5, end: 3.8, stress: 1 };
      return { font, fallback };
    },
    draw(g, t, { font, fallback }) {
      const W = g.canvas.width, H = g.canvas.height;
      g.fillStyle = '#f3efe6'; g.fillRect(0, 0, W, H);
      const word = (window.SONG && window.SONG.word(t)) || (t >= fallback.t - 1.5 ? fallback : null);
      if (!word) return;
      const size = H * 0.16 * (word.stress ? 1.5 : 1);                                // stressed words 1.5×
      const glyphs = font.stringToGlyphs(word.w), scale = size / font.unitsPerEm;
      const adv = glyphs.map((gl) => gl.advanceWidth * scale), total = adv.reduce((a, b) => a + b, 0);
      let x = (W - total) / 2; const base = H * 0.5 + size * 0.36;
      glyphs.forEach((gl, i) => {
        const lt = t - word.t - i * 0.06;                                             // stagger per glyph
        const k = Spring.unit(lt, 'snappy'), wob = Spring.unit(lt, 'playful');
        const ch = word.w[i], cx = x + adv[i] / 2;
        const p = new Path2D(font.getPath(ch, -adv[i] / 2, size * 0.36, size).toPathData(2));
        g.save();
        g.translate(cx, base - size * 0.36 + (1 - k) * H * 0.35);                       // rise into place
        g.rotate((1 - wob) * 0.6 * (i % 2 ? 1 : -1));                                  // settle a tilt
        g.scale(0.4 + 0.6 * k, 0.4 + 0.6 * k);
        g.globalAlpha = Math.min(1, k * 1.5);
        g.fillStyle = i === 4 ? '#e4572e' : '#1d1b26'; g.fill(p);
        g.restore();
        x += adv[i];
      });
      // an underline that springs out after the last glyph lands
      const u = Spring.unit(t - word.t - glyphs.length * 0.06, 'heavy');
      g.fillStyle = '#e4572e'; g.fillRect(W / 2 - total / 2 * u, base + size * 0.12, total * u, Math.max(2, size * 0.04));
    },
  },
};
