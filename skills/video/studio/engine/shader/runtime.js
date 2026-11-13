// engine/shader/runtime.js — the shader medium: fullscreen fragment shaders on WebGL2, no dependencies (MIT, this repo).
//
// A film is a list of passes. Each pass is a fragment shader with a Shadertoy-style entry point
//     void mainImage(out vec4 fragColor, in vec2 fragCoord)
// and these uniforms (declared for you):
//     float iTime (= film time t)  vec3 iResolution  int iFrame  float iFps
//     float iBeat, iBar, iPulse    (from the song map: SONG.beatAt / barAt / pulse — 0 without one)
//     sampler2D iChannel0..3       (outputs of earlier passes this frame, the pass's own previous frame, or images)
// `#include "engine/glsl/noise.glsl"` pulls in the studio's GLSL library (paths relative to the project).
//
// Determinism: a frame is a pure function of t. A pass with { feedback: true } reads its own previous frame; the
// runtime then re-simulates from max(0, t - warmup) to t at a fixed dt = 1 / fps on every render, so any frame can be
// rendered alone, in any order, on any worker. Keep warmup short (the cost is warmup × fps passes per frame) or bake.
//
//   scenes/film.js:
//   export default { passes: [
//     { name: 'trail', frag: 'scenes/trail.frag', feedback: true, inputs: [] },      // iChannel0 = its previous frame
//     { name: 'main',  frag: 'scenes/main.frag',  inputs: ['trail', 'assets/paper.png'] },  // last pass is shown
//   An input like 'assets/bake/%05d.png' is an image SEQUENCE: frame round(t * fps) is loaded for every rendered
//   frame (use it for long simulations baked once, or footage pre-extracted with ffmpeg at the film's fps).
//   ], warmup: 2.0, fps: 24 };

const HEADER = `#version 300 es
precision highp float; precision highp int;
uniform float iTime; uniform vec3 iResolution; uniform int iFrame; uniform float iFps;
uniform float iBeat; uniform float iBar; uniform float iPulse;
uniform sampler2D iChannel0; uniform sampler2D iChannel1; uniform sampler2D iChannel2; uniform sampler2D iChannel3;
out vec4 studioFragColor;
void mainImage(out vec4 fragColor, in vec2 fragCoord);
void main() { mainImage(studioFragColor, gl_FragCoord.xy); }
#line 1
`;
const VERT = `#version 300 es
in vec2 p; void main() { gl_Position = vec4(p, 0.0, 1.0); }`;

async function loadText(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`shader runtime: cannot load ${url} (${r.status})`);
  return r.text();
}
async function resolveIncludes(src, seen = new Set()) {
  const out = [];
  for (const line of src.split('\n')) {
    const m = line.match(/^\s*#include\s+"([^"]+)"/);
    if (!m) { out.push(line); continue; }
    if (seen.has(m[1])) continue;            // include once
    seen.add(m[1]);
    out.push(`// --- ${m[1]}`, await resolveIncludes(await loadText(m[1]), seen), `// --- end ${m[1]}`);
  }
  return out.join('\n');
}
function loadImage(url) {
  return new Promise((ok, bad) => { const im = new Image(); im.onload = () => ok(im); im.onerror = () => bad(new Error(`cannot load ${url}`)); im.src = url; });
}

export async function createFilm(canvas, film, { W, H, SONG }) {
  const gl = canvas.getContext('webgl2', { preserveDrawingBuffer: true, antialias: false, premultipliedAlpha: false });
  if (!gl) throw new Error('shader runtime: WebGL2 is not available');
  gl.getExtension('EXT_color_buffer_float');
  const fps = film.fps || 24, warmup = film.warmup || 0;

  const compile = (type, src, name) => {
    const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(`shader ${name}: ${gl.getShaderInfoLog(s)}`);
    return s;
  };
  const quad = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, quad);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);

  const target = () => {
    const tex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA16F, W, H, 0, gl.RGBA, gl.HALF_FLOAT, null);
    for (const [k, v] of [[gl.TEXTURE_MIN_FILTER, gl.LINEAR], [gl.TEXTURE_MAG_FILTER, gl.LINEAR], [gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE], [gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE]]) gl.texParameteri(gl.TEXTURE_2D, k, v);
    const fb = gl.createFramebuffer(); gl.bindFramebuffer(gl.FRAMEBUFFER, fb);
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0);
    return { tex, fb };
  };
  const images = {};
  const passes = [];
  for (const [i, p] of film.passes.entries()) {
    const src = HEADER + await resolveIncludes(await loadText(p.frag));
    const prog = gl.createProgram();
    gl.attachShader(prog, compile(gl.VERTEX_SHADER, VERT, 'vertex'));
    gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, src, p.name || p.frag));
    gl.bindAttribLocation(prog, 0, 'p'); gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(`shader ${p.name}: ${gl.getProgramInfoLog(prog)}`);
    const u = (n) => gl.getUniformLocation(prog, n);
    const last = i === film.passes.length - 1;
    for (const inp of p.inputs || []) if (/\.(png|jpe?g|webp)$/i.test(inp) && !/%0?\d*d/.test(inp) && !images[inp]) {
      const im = await loadImage(inp), tex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, tex);
      gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, im);
      gl.generateMipmap(gl.TEXTURE_2D); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.REPEAT);
      images[inp] = tex;
    }
    passes.push({ ...p, prog, last, loc: {
      iTime: u('iTime'), iResolution: u('iResolution'), iFrame: u('iFrame'), iFps: u('iFps'), iBeat: u('iBeat'), iBar: u('iBar'), iPulse: u('iPulse'),
      ch: [0, 1, 2, 3].map((k) => u('iChannel' + k)) },
      // a feedback pass keeps two targets and swaps them; the shown (last) pass draws to the canvas unless it feeds back
      targets: p.feedback ? [target(), target()] : (last ? null : [target()]), cur: 0 });
  }
  if (passes.some((p) => p.feedback && p.last)) {
    // the last pass feeds back: render it into its targets and blit to the canvas
    passes.push({ name: '__blit', blit: true, last: true });
  }
  const blitProg = (() => {
    const prog = gl.createProgram();
    gl.attachShader(prog, compile(gl.VERTEX_SHADER, VERT, 'vertex'));
    gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, `#version 300 es\nprecision highp float; uniform sampler2D s; uniform vec2 r; out vec4 o; void main(){ o = texture(s, gl_FragCoord.xy / r); }`, 'blit'));
    gl.bindAttribLocation(prog, 0, 'p'); gl.linkProgram(prog); return prog;
  })();

  // image sequences: one texture per input, refilled with the frame's image before each render
  const seqInputs = [...new Set(film.passes.flatMap((p) => (p.inputs || []).filter((n) => /%0?\d*d/.test(n))))];
  for (const n of seqInputs) { const tex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    images[n] = tex; }
  const seqPath = (pat, f) => pat.replace(/%0?(\d*)d/, (_, w) => String(f).padStart(Number(w) || 0, '0'));
  async function loadSequences(frame) {
    for (const n of seqInputs) {
      const im = await loadImage(seqPath(n, frame));
      gl.bindTexture(gl.TEXTURE_2D, images[n]); gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, im);
    }
  }
  const outputOf = (name) => { const p = passes.find((q) => q.name === name); return p && p.targets ? p.targets[p.cur].tex : null; };
  function drawPass(p, t, frame, toCanvas) {
    const readOwn = p.feedback ? p.targets[p.cur].tex : null;
    if (p.feedback) p.cur ^= 1;
    gl.bindFramebuffer(gl.FRAMEBUFFER, toCanvas ? null : p.targets[p.feedback ? p.cur : 0].fb);
    gl.viewport(0, 0, W, H); gl.useProgram(p.prog);
    gl.bindBuffer(gl.ARRAY_BUFFER, quad); gl.enableVertexAttribArray(0); gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
    gl.uniform1f(p.loc.iTime, t); gl.uniform3f(p.loc.iResolution, W, H, 1); gl.uniform1i(p.loc.iFrame, frame); gl.uniform1f(p.loc.iFps, fps);
    gl.uniform1f(p.loc.iBeat, SONG ? SONG.beatAt(t) : 0); gl.uniform1f(p.loc.iBar, SONG ? SONG.barAt(t) : 0); gl.uniform1f(p.loc.iPulse, SONG ? SONG.pulse(t) : 0);
    const chans = p.feedback ? [readOwn, ...(p.inputs || []).map((n) => images[n] || outputOf(n))] : (p.inputs || []).map((n) => images[n] || outputOf(n));
    for (let k = 0; k < 4; k++) { gl.activeTexture(gl.TEXTURE0 + k); gl.bindTexture(gl.TEXTURE_2D, chans[k] || null); gl.uniform1i(p.loc.ch[k], k); }
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }
  function step(t, frame, show) {
    for (const p of passes) {
      if (p.blit) {
        if (!show) continue;
        const src = passes.find((q) => q.feedback && q.last && !q.blit);
        gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.viewport(0, 0, W, H); gl.useProgram(blitProg);
        gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, src.targets[src.cur].tex);
        gl.uniform1i(gl.getUniformLocation(blitProg, 's'), 0); gl.uniform2f(gl.getUniformLocation(blitProg, 'r'), W, H);
        gl.drawArrays(gl.TRIANGLES, 0, 3); continue;
      }
      if (p.last && !p.feedback && !show) continue;
      drawPass(p, t, frame, p.last && !p.feedback);
    }
  }
  const clearFeedback = () => { for (const p of passes) if (p.feedback) for (const tg of p.targets) { gl.bindFramebuffer(gl.FRAMEBUFFER, tg.fb); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT); } };
  const hasFeedback = passes.some((p) => p.feedback);

  return {
    async renderFrame(t) {
      const frame = Math.round(t * fps);
      if (seqInputs.length) await loadSequences(frame);   // sequences hold the shown frame during a feedback warm-up
      if (hasFeedback) {
        // re-simulate a fixed window ending at t: the result depends on t only, never on the previous call
        clearFeedback();
        const f0 = Math.max(0, frame - Math.round(warmup * fps));
        for (let f = f0; f < frame; f++) step(f / fps, f, false);
      }
      step(t, frame, true);
      gl.finish();
    },
  };
}
