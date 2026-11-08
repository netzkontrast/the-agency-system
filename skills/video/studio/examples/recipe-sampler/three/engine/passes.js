// engine/three/passes.js — the studio's stylisation passes for the three medium (and any EffectComposer).
//
// Every pass is our own GLSL (MIT, this repo). Each is a ShaderPass whose uniforms uTime (seconds, = film time t) and
// uResolution are set by setFxTime(composer, t) once per frame, so a frame never depends on the one before it.
// Order matters: put structure passes (outline, kuwahara, toon) first, then medium passes (halftone, riso, dither,
// pixelate), then surface passes (paper, grain, vignette, chroma), and OutputPass last (tone mapping + sRGB).
//
//   import { FX, setFxTime } from './engine/passes.js';
//   return { scene, camera, passes: [FX.ink({ threshold: 0.18 }), FX.paper(), FX.grain({ amount: 0.06 })], update };
//
// The catalogue (options, defaults):
//   ink        edge lines from luminance + depth-free Sobel: { threshold .15, width 1, color [.12,.1,.12], keep 1 } keep 0 = lines only
//   toon       quantise light into bands: { bands 4, softness .05 }
//   kuwahara   painterly 4-sector Kuwahara (oil / gouache): { radius 4 }
//   watercolor edge darkening + pigment granulation + paper bleed: { edge .6, granulation .35, bleed 1.5 }
//   hatch      cross-hatching from luminance (pencil / engraving): { spacing 6, angle .6, layers 3, color [.15,.13,.12] }
//   halftone   rotated dot screen per channel (print, comics): { cell 8, angle .26, cmyk 1 }
//   riso       two-ink risograph with misregistration: { inkA [.97,.33,.48], inkB [.12,.38,.78], offset [2,-1] }
//   dither     ordered Bayer 8×8 (1-bit / limited palette): { levels 2, scale 1, mono 1 }
//   pixelate   pixel-art downsample with palette snap: { size 6, levels 6 }
//   posterize  { levels 5 }
//   crt        curvature + scanlines + mask + glow: { curve .08, scan .35, mask .2 }
//   boil       hand-drawn line boil: UV wobble from noise stepped at { fps 12, amount 1.2 } px
//   paper      procedural paper fibre multiply: { strength .18, scale 1, tint [.96,.93,.86] }
//   grain      film grain, new pattern per frame from t: { amount .05, size 1.5 }
//   vignette   { strength .35, softness .45 }
//   chroma     radial chromatic aberration: { amount 1.5 } px at the corners
//   grade      lift / gamma / gain / saturation: { lift [0,0,0], gamma [1,1,1], gain [1,1,1], sat 1 }
//   glitch     block displacement on given beats (deterministic): { amount 0, seed 1 } — drive amount from SONG.pulse(t)
//   fade       mix the finished frame toward a colour: { amount 0, color [.94,.91,.84] } — put it LAST, drive amount
//              from t for fades to/from paper or black (a veil in the scene would be re-inked by the ink pass)
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';

const COMMON = /* glsl */ `
uniform sampler2D tDiffuse; uniform float uTime; uniform vec2 uResolution; varying vec2 vUv;
float h21(vec2 p){ p = fract(p * vec2(123.34, 456.21)); p += dot(p, p + 45.32); return fract(p.x * p.y); }
float vnoise(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f);
  return mix(mix(h21(i), h21(i+vec2(1,0)), f.x), mix(h21(i+vec2(0,1)), h21(i+vec2(1,1)), f.x), f.y); }
float fbm(vec2 p){ float a = .5, s = 0.; for (int i = 0; i < 5; i++){ s += a*vnoise(p); p *= 2.03; a *= .5; } return s; }
float luma(vec3 c){ return dot(c, vec3(.2126,.7152,.0722)); }
// passes run before OutputPass, i.e. in linear light: thresholds that should match what the eye sees use pluma()
float pluma(vec3 c){ return pow(max(luma(c), 0.), 1./2.2); }
vec4 tex(vec2 uv){ return texture2D(tDiffuse, uv); }
`;
const VERT = /* glsl */ `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`;

function pass(name, defaults, body, opts = {}) {
  const o = { ...defaults, ...opts };
  const uniforms = { tDiffuse: { value: null }, uTime: { value: 0 }, uResolution: { value: [1920, 1080] } };
  let decl = '';
  for (const [k, v] of Object.entries(o)) {
    const type = Array.isArray(v) ? `vec${v.length}` : 'float';
    uniforms['u_' + k] = { value: v };
    decl += `uniform ${type} u_${k};\n`;
  }
  const p = new ShaderPass({ name, uniforms, vertexShader: VERT, fragmentShader: COMMON + decl + body });
  p.studioFx = name;
  return p;
}

export const FX = {
  ink: (o) => pass('ink', { threshold: 0.15, width: 1, color: [0.12, 0.1, 0.12], keep: 1 }, `
    void main(){ vec2 px = u_width / uResolution; float tl=luma(tex(vUv+px*vec2(-1,1)).rgb), t=luma(tex(vUv+px*vec2(0,1)).rgb), tr=luma(tex(vUv+px*vec2(1,1)).rgb),
      l=luma(tex(vUv+px*vec2(-1,0)).rgb), r=luma(tex(vUv+px*vec2(1,0)).rgb), bl=luma(tex(vUv+px*vec2(-1,-1)).rgb), b=luma(tex(vUv+px*vec2(0,-1)).rgb), br=luma(tex(vUv+px*vec2(1,-1)).rgb);
      float gx = -tl-2.*l-bl+tr+2.*r+br, gy = -tl-2.*t-tr+bl+2.*b+br, e = smoothstep(u_threshold, u_threshold*1.6, length(vec2(gx,gy)));
      vec3 base = mix(vec3(1.), tex(vUv).rgb, u_keep); gl_FragColor = vec4(mix(base, u_color, e), 1.); }`, o),
  toon: (o) => pass('toon', { bands: 4, softness: 0.05 }, `
    // bands are cut in perceptual luma (pluma) and each band takes its centre value, so the darkest band is never black
    void main(){ vec4 c = tex(vUv); float l = luma(c.rgb), p = pluma(c.rgb), b = floor(p*u_bands), f = fract(p*u_bands);
      float q = (b + .5 + smoothstep(1.-u_softness*u_bands, 1., f))/u_bands; q = pow(min(q, 1.), 2.2);
      gl_FragColor = vec4(c.rgb*(q/max(l,1e-4)), c.a); }`, o),
  kuwahara: (o) => pass('kuwahara', { radius: 4 }, `
    void main(){ vec2 px = 1./uResolution; int R = int(u_radius); vec3 m[4]; vec3 s[4];
      for (int k=0;k<4;k++){ m[k]=vec3(0.); s[k]=vec3(0.); }
      for (int j=-8;j<=8;j++) for (int i=-8;i<=8;i++){ if (abs(i)>R||abs(j)>R) continue; vec3 c = tex(vUv+vec2(i,j)*px).rgb;
        if (i<=0&&j<=0){m[0]+=c;s[0]+=c*c;} if (i>=0&&j<=0){m[1]+=c;s[1]+=c*c;} if (i<=0&&j>=0){m[2]+=c;s[2]+=c*c;} if (i>=0&&j>=0){m[3]+=c;s[3]+=c*c;} }
      float n = float((R+1)*(R+1)), best = 1e9; vec3 outc = vec3(0.);
      for (int k=0;k<4;k++){ vec3 mu = m[k]/n, v = abs(s[k]/n - mu*mu); float sv = v.r+v.g+v.b; if (sv<best){best=sv;outc=mu;} }
      gl_FragColor = vec4(outc, 1.); }`, o),
  watercolor: (o) => pass('watercolor', { edge: 0.6, granulation: 0.35, bleed: 1.5 }, `
    void main(){ vec2 px = 1./uResolution; vec2 w = (vec2(fbm(vUv*6.+3.), fbm(vUv*6.+7.))-.5)*u_bleed*px*8.;
      vec3 c = tex(vUv+w).rgb; float l = luma(c), lb = luma(tex(vUv+w+px*2.).rgb)+luma(tex(vUv+w-px*2.).rgb);
      float edge = clamp(abs(l*2.-lb)*6., 0., 1.); float g = fbm(vUv*uResolution/6.);
      vec3 pig = c*(1.-u_edge*edge*.5)*(1.-u_granulation*(g-.5)*(1.-l));
      gl_FragColor = vec4(mix(vec3(1.), pig, .92+.08*g), 1.); }`, o),
  hatch: (o) => pass('hatch', { spacing: 6, angle: 0.6, layers: 3, color: [0.15, 0.13, 0.12] }, `
    void main(){ vec3 c = tex(vUv).rgb; float l = pluma(c); vec2 p = vUv*uResolution; float ink = 0.;
      for (int k=0;k<4;k++){ if (float(k)>=u_layers) break; float a = u_angle + float(k)*1.0472; vec2 d = vec2(cos(a), sin(a));
        float line = abs(fract(dot(p,d)/u_spacing + vnoise(p*.05+float(k))*.3) - .5); float thr = 1. - (float(k)+1.)/(u_layers+1.);
        ink = max(ink, (l<thr ? 1. : 0.) * smoothstep(.18, .08, line)); }
      gl_FragColor = vec4(mix(vec3(1.), u_color, ink), 1.); }`, o),
  halftone: (o) => pass('halftone', { cell: 8, angle: 0.26, cmyk: 1 }, `
    float dots(vec2 p, float a, float v){ mat2 r = mat2(cos(a),-sin(a),sin(a),cos(a)); vec2 q = r*p/u_cell; vec2 f = fract(q)-.5;
      return smoothstep(.02, -.02, length(f) - sqrt(v)*.55); }
    void main(){ vec2 p = vUv*uResolution; vec3 c = tex(vUv).rgb;
      if (u_cmyk > .5){ vec3 cmy = 1.-c; float k = min(min(cmy.r,cmy.g),cmy.b); vec3 ink = vec3(dots(p,u_angle,cmy.r-k), dots(p,u_angle+.52,cmy.g-k), dots(p,u_angle+1.05,cmy.b-k));
        float kd = dots(p, u_angle+.78, k); gl_FragColor = vec4((1.-ink)*(1.-kd), 1.); }
      else { float d = dots(p, u_angle, 1.-pluma(c)); gl_FragColor = vec4(vec3(1.-d), 1.); } }`, o),
  riso: (o) => pass('riso', { inkA: [0.97, 0.33, 0.48], inkB: [0.12, 0.38, 0.78], offset: [2, -1] }, `
    void main(){ vec2 px = 1./uResolution; float a = 1.-pluma(tex(vUv).rgb), b = 1.-pow(tex(vUv+u_offset*px).b, 1./2.2);
      float g = vnoise(vUv*uResolution*.7); a = smoothstep(.2,.9,a+.15*(g-.5)); b = smoothstep(.3,.95,b+.15*(g-.5));
      vec3 paper = vec3(.97,.95,.9); vec3 c = paper*mix(vec3(1.), u_inkA, a)*mix(vec3(1.), u_inkB, b); gl_FragColor = vec4(c,1.); }`, o),
  dither: (o) => pass('dither', { levels: 2, scale: 1, mono: 1 }, `
    float bayer(vec2 p){ vec2 q = mod(floor(p), 8.); float v = 0., s = 1.;
      for (int i=0;i<3;i++){ vec2 b = mod(floor(q/s), 2.); v = v*4. + (b.x==b.y ? (b.x==0.?0.:1.) : (b.x==0.?2.:3.)); s *= 2.; } return (v+.5)/64.; }
    void main(){ vec3 c = tex(vUv).rgb; if (u_mono > .5) c = vec3(pluma(c)); float t = bayer(vUv*uResolution/u_scale) - .5;
      vec3 q = floor(c*(u_levels-1.) + .5 + t)/(u_levels-1.); gl_FragColor = vec4(clamp(q,0.,1.), 1.); }`, o),
  pixelate: (o) => pass('pixelate', { size: 6, levels: 6 }, `
    void main(){ vec2 cell = u_size/uResolution; vec2 uv = (floor(vUv/cell)+.5)*cell; vec3 c = tex(uv).rgb;
      gl_FragColor = vec4(floor(c*u_levels+.5)/u_levels, 1.); }`, o),
  posterize: (o) => pass('posterize', { levels: 5 }, `void main(){ vec3 c = tex(vUv).rgb; gl_FragColor = vec4(floor(c*u_levels+.5)/u_levels, 1.); }`, o),
  crt: (o) => pass('crt', { curve: 0.08, scan: 0.35, mask: 0.2 }, `
    void main(){ vec2 uv = vUv*2.-1.; uv *= 1. + u_curve*dot(uv,uv); uv = uv*.5+.5;
      if (uv.x<0.||uv.y<0.||uv.x>1.||uv.y>1.){ gl_FragColor = vec4(0.,0.,0.,1.); return; }
      vec3 c = tex(uv).rgb; float s = .5+.5*sin(uv.y*uResolution.y*3.14159); c *= 1.-u_scan*(1.-s);
      float m = mod(floor(uv.x*uResolution.x), 3.); c *= 1.-u_mask + u_mask*vec3(m==0.?1.:.6, m==1.?1.:.6, m==2.?1.:.6)*1.2;
      gl_FragColor = vec4(c, 1.); }`, o),
  boil: (o) => pass('boil', { fps: 12, amount: 1.2 }, `
    void main(){ float k = floor(uTime*u_fps); vec2 px = 1./uResolution;
      vec2 off = (vec2(vnoise(vUv*9.+k*7.31), vnoise(vUv*9.+k*3.17+11.))-.5)*2.*u_amount*px; gl_FragColor = tex(vUv+off); }`, o),
  paper: (o) => pass('paper', { strength: 0.18, scale: 1, tint: [0.96, 0.93, 0.86] }, `
    void main(){ vec2 p = vUv*uResolution/u_scale; float f = fbm(p*.02)*.6 + vnoise(p*.9)*.25 + vnoise(vec2(p.x*.05, p.y*1.3))*.15;
      vec3 c = tex(vUv).rgb * mix(vec3(1.), u_tint*(.85+.3*f), u_strength*4.); gl_FragColor = vec4(c, 1.); }`, o),
  grain: (o) => pass('grain', { amount: 0.05, size: 1.5 }, `
    void main(){ vec2 p = floor(vUv*uResolution/u_size); float n = h21(p + floor(uTime*24.)*vec2(17.13, 3.71)) - .5;
      vec3 c = tex(vUv).rgb; gl_FragColor = vec4(c + n*u_amount*(1.-luma(c)*.5), 1.); }`, o),
  vignette: (o) => pass('vignette', { strength: 0.35, softness: 0.45 }, `
    void main(){ vec2 d = vUv-.5; d.x *= uResolution.x/uResolution.y; float v = smoothstep(.85, .85-u_softness, length(d));
      gl_FragColor = vec4(tex(vUv).rgb*mix(1.-u_strength, 1., v), 1.); }`, o),
  chroma: (o) => pass('chroma', { amount: 1.5 }, `
    void main(){ vec2 d = (vUv-.5)*2.; vec2 o = d*dot(d,d)*u_amount/uResolution;
      gl_FragColor = vec4(tex(vUv+o).r, tex(vUv).g, tex(vUv-o).b, 1.); }`, o),
  grade: (o) => pass('grade', { lift: [0, 0, 0], gamma: [1, 1, 1], gain: [1, 1, 1], sat: 1 }, `
    void main(){ vec3 c = tex(vUv).rgb; c = c*u_gain + u_lift*(1.-c); c = pow(max(c,0.), 1./u_gamma); c = mix(vec3(luma(c)), c, u_sat);
      gl_FragColor = vec4(c, 1.); }`, o),
  glitch: (o) => pass('glitch', { amount: 0, seed: 1 }, `
    void main(){ float row = floor(vUv.y*24.), k = floor(uTime*12.); float r = h21(vec2(row, k+u_seed));
      vec2 uv = vUv; if (r < u_amount*.5) uv.x += (h21(vec2(row*3.1, k))-.5)*u_amount*.15;
      vec3 c = vec3(tex(uv+vec2(u_amount*.004,0.)).r, tex(uv).g, tex(uv-vec2(u_amount*.004,0.)).b); gl_FragColor = vec4(c,1.); }`, o),
  fade: (o) => pass('fade', { amount: 0, color: [0.94, 0.91, 0.84] }, `
    void main(){ vec3 c = tex(vUv).rgb; gl_FragColor = vec4(mix(c, u_color, clamp(u_amount, 0., 1.)), 1.); }`, o),
};

// Set time and size on every studio pass of a composer (call once per frame, before composer.render(0)).
export function setFxTime(composer, t, W, H) {
  for (const p of composer.passes) {
    const u = p.uniforms || (p.material && p.material.uniforms);
    if (!u) continue;
    if (u.uTime) u.uTime.value = t;
    if (u.uResolution && W) u.uResolution.value = [W, H];
  }
}
