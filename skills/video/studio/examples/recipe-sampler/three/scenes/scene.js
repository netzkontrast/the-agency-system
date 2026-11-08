// scenes/scene.js — recipe sampler, three medium. ONE still-life (torus knot, box, icosahedron on a ground plane,
// key + rim light, slow camera orbit by t), restyled per recipe from references/style-recipes.md.
//
//   node <studio>/tools/render.mjs --stills=2 --size=480x270 --query=recipe=anime-cel --out=review/anime-cel
//
// The recipe comes from ?recipe=<id>; without it DEFAULT_RECIPE is used (the gate cannot pass a query, so switch
// this constant to gate another recipe). Every recipe applies its material changes and FX chain as written in
// style-recipes.md; where the sampler had to deviate, the entry says so in `note` (see ../README.md).
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { Reflector } from 'three/addons/objects/Reflector.js';
import { createNoise2D } from 'simplex-noise';

const DEFAULT_RECIPE = 'anime-cel';
// recipe 26 says colours ×4 with UnrealBloomPass strength 1.6: the haze then fills the frame at any size (README problem 6)
const NEON = 1.5;

const VERT = `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`;
const h1 = (n) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };   // stable hash

// a tiny custom ShaderPass (recipes 28 and 32 ask for one)
const customPass = (name, uniforms, frag) => {
  const p = new ShaderPass({ name, uniforms: { tDiffuse: { value: null }, uTime: { value: 0 }, uResolution: { value: [1920, 1080] }, ...uniforms },
    vertexShader: VERT, fragmentShader: frag });
  return p;
};

// ---------------------------------------------------------------- material helpers
const toonRamp = (THREE, steps) => {
  const r = new THREE.DataTexture(new Uint8Array(steps), steps.length, 1, THREE.RedFormat);
  r.minFilter = r.magFilter = THREE.NearestFilter; r.needsUpdate = true; return r;
};
// inverted-hull outline: back faces pushed out along the normals, flat ink colour
const hullMaterial = (THREE, color, push) => {
  const m = new THREE.MeshBasicMaterial({ color, side: THREE.BackSide });
  m.onBeforeCompile = (s) => { s.vertexShader = s.vertexShader.replace('#include <begin_vertex>', `#include <begin_vertex>\n transformed += normal * ${push.toFixed(3)};`); };
  return m;
};
// clay: rough standard material + fbm bump (thumbprints) via onBeforeCompile
const clayMaterial = (THREE, color) => {
  const m = new THREE.MeshStandardMaterial({ color, roughness: 0.9, metalness: 0 });
  m.onBeforeCompile = (s) => {
    s.vertexShader = s.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vObj;').replace('#include <begin_vertex>', '#include <begin_vertex>\n vObj = position;');
    s.fragmentShader = s.fragmentShader.replace('#include <common>', `#include <common>
varying vec3 vObj;
float ch(vec3 p){ return fract(sin(dot(p, vec3(127.1,311.7,74.7)))*43758.5453); }
float vn3(vec3 p){ vec3 i=floor(p), f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(mix(ch(i),ch(i+vec3(1,0,0)),f.x),mix(ch(i+vec3(0,1,0)),ch(i+vec3(1,1,0)),f.x),f.y),
             mix(mix(ch(i+vec3(0,0,1)),ch(i+vec3(1,0,1)),f.x),mix(ch(i+vec3(0,1,1)),ch(i+vec3(1,1,1)),f.x),f.y),f.z); }
float fbm3(vec3 p){ float s=0., a=.5; for(int i=0;i<4;i++){ s+=a*vn3(p); p*=2.07; a*=.5; } return s; }`)
      .replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
 { vec3 q = vObj*7.; vec3 b = vec3(fbm3(q), fbm3(q+3.1), fbm3(q+7.7)) - .5; normal = normalize(normal + .55*b); }`);
  };
  return m;
};

// ---------------------------------------------------------------- the registry (self-documenting)
// mat(kind, color): the material for the knot / box / ico / ground.   passes(c): the FX chain, in order.
// Optional: bg, toneMapping, camera 'ortho', step, quantise (pose on twos), lights(c), extras(c) → update(t), outline.
export const RECIPES = {
  'anime-cel': {
    n: 1, title: 'Anime cel / toon with outlines', bg: '#bfe0f2', outline: true, step: 12, quantise: true,
    mat: (c, kind, col) => new c.THREE.MeshToonMaterial({ color: col, gradientMap: c.ramp3 }),
    // FX.toon as written in the recipe (README problem 1 is fixed in the pass: perceptual bands, never black)
    passes: ({ FX }) => [FX.toon({ bands: 3, softness: .03 }), FX.ink({ threshold: .1, width: 1, keep: 1 }), FX.grade({ sat: 1.15 }), FX.grain({ amount: .02 })],
  },
  'ligne-claire': {
    n: 2, title: 'Ligne claire', bg: '#cfe6ee', flatShadows: true, step: 12, quantise: true,
    mat: (c, kind, col) => new c.THREE.MeshBasicMaterial({ color: col }),
    passes: ({ FX }) => [FX.ink({ threshold: .05, width: 1.2, color: [.05, .05, .06], keep: 1 }), FX.paper({ strength: .08 })],
  },
  woodblock: {
    n: 4, title: 'Woodblock print', orthoSize: 1.55, bg: '#e9dcc0', camera: 'ortho', flatShadows: true,
    palette: { knot: '#c0392b', box: '#1f4e79', ico: '#d9a441', ground: '#8fa6b8' },
    mat: (c, kind, col) => new c.THREE.MeshBasicMaterial({ color: col }),
    passes: ({ FX }) => [FX.ink({ threshold: .08, width: 1.5, color: [.1, .08, .1], keep: 1 }), FX.posterize({ levels: 5 }),
      FX.paper({ strength: .25, tint: [.93, .88, .76] }), FX.grain({ amount: .03, size: 2 })],
  },
  etching: {
    n: 6, title: 'Etching / engraving', bg: '#d8d2c4',
    mat: (c, kind, col) => new c.THREE.MeshStandardMaterial({ color: col, roughness: .8 }),
    // recipe order is hatch → ink, but ink after hatch traces every hatch line (frame turns solid ink, README problem 3):
    // the sampler runs ink first, then hatch turns the ink lines into dense cross-hatch
    passes: ({ FX }) => [FX.ink({ threshold: .1, width: 1, keep: 1 }), FX.hatch({ spacing: 4, angle: .4, layers: 4, color: [.12, .1, .08] }),
      FX.paper({ strength: .22, tint: [.95, .92, .84] }), FX.vignette({ strength: .3 })],
  },
  oil: {
    n: 11, title: 'Oil painting', bg: '#6a6578', palette: { knot: '#c4573a', box: '#3f7a7f', ico: '#e0b25a', ground: '#9a8060' },   // mid-value palette: posterize in linear light bands dark tones into hue stripes (README problem 4)
    mat: (c, kind, col) => new c.THREE.MeshStandardMaterial({ color: col, roughness: 1 }),
    passes: ({ FX }) => [FX.kuwahara({ radius: 6 }), FX.posterize({ levels: 12 }), FX.paper({ strength: .12, scale: 2, tint: [.95, .9, .82] }),
      FX.grade({ sat: 1.15 }), FX.vignette({ strength: .3 })],
  },
  watercolor: {
    n: 13, title: 'Watercolor wash', bg: '#f4efe4', step: 12,
    mat: (c, kind, col) => new c.THREE.MeshStandardMaterial({ color: col, roughness: 1 }),
    passes: ({ FX }) => [FX.watercolor({ edge: .7, granulation: .45, bleed: 2 }), FX.ink({ threshold: .15, keep: 1, color: [.25, .2, .2] }), FX.paper({ strength: .22 })],
  },
  claymation: {
    n: 19, title: 'Claymation look', bg: '#b9c7d6', step: 12, quantise: true, jitter: true, softKey: true,
    palette: { knot: '#e0533d', box: '#3c78c3', ico: '#f2c230', ground: '#8db36b' },
    mat: (c, kind, col) => clayMaterial(c.THREE, col),
    passes: ({ FX }) => [FX.toon({ bands: 6, softness: .2 }), FX.grain({ amount: .03 }), FX.vignette({ strength: .25 })],
  },
  'low-poly': {
    n: 20, title: 'Low-poly flat shading', bg: '#f6d7a7', lowPoly: true,
    palette: { knot: '#e76f51', box: '#2a9d8f', ico: '#e9c46a', ground: '#8ab17d' },
    mat: (c, kind, col) => new c.THREE.MeshLambertMaterial({ color: col, flatShading: true }),
    passes: ({ FX }) => [FX.grade({ sat: 1.1 }), FX.vignette({ strength: .2 })],
  },
  synthwave: {
    n: 24, title: 'Synthwave grid (three)', bg: '#1a0b2e', noGround: true,
    palette: { knot: '#05d9e8', box: '#2b1250', ico: '#ff2a6d', ground: '#1a0b2e' },
    mat: (c, kind, col) => new c.THREE.MeshStandardMaterial({ color: col, roughness: .4, metalness: .3 }),   // only grid + sun are emissive, as the recipe says
    extras: ({ THREE, scene }) => {
      const cell = 1;
      const grid = new THREE.GridHelper(40, 40, '#ff2a6d', '#ff2a6d'); scene.add(grid);
      const sun = new THREE.Mesh(new THREE.SphereGeometry(4, 48, 24), new THREE.MeshBasicMaterial({ color: '#ff5a3d' }));
      sun.position.set(0, 2.5, -18); scene.add(sun);
      return (t, cam) => { grid.position.z = (t * 1.6) % cell; sun.position.set(cam.position.x * -5, 3, cam.position.z * -5); };
    },
    passes: ({ FX, THREE, W, H }) => [new UnrealBloomPass(new THREE.Vector2(W, H), 1.2, .4, .2), FX.crt({ curve: .03, scan: .2, mask: .1 })],
  },
  neon: {
    n: 26, title: 'Neon glow / cyberpunk night', bg: '#030308', dark: true, noGround: true, thinKnot: true,
    palette: { knot: '#00e5ff', box: '#16161f', ico: '#ff2bd6', ground: '#0b0b12' },
    mat: (c, kind, col) => kind === 'knot' || kind === 'ico'
      ? new c.THREE.MeshBasicMaterial({ color: new c.THREE.Color(col).multiplyScalar(NEON), wireframe: kind === 'ico' })
      : new c.THREE.MeshStandardMaterial({ color: col, roughness: .5, metalness: .2 }),
    extras: ({ THREE, scene, W, H }) => {
      const mirror = new Reflector(new THREE.PlaneGeometry(14, 14), { textureWidth: W, textureHeight: H, color: '#556070', clipBias: .003 });
      mirror.rotation.x = -Math.PI / 2; mirror.position.y = -0.002; scene.add(mirror);
      const wet = new THREE.Mesh(new THREE.PlaneGeometry(14, 14), new THREE.MeshStandardMaterial({ color: '#0b0b12', roughness: .15, metalness: .6, transparent: true, opacity: .55 }));
      wet.rotation.x = -Math.PI / 2; scene.add(wet);
      const amber = new THREE.Mesh(new THREE.TorusGeometry(.35, .035, 12, 48), new THREE.MeshBasicMaterial({ color: new THREE.Color('#ffae42').multiplyScalar(NEON) }));
      amber.position.set(-1.4, 1.35, .6); scene.add(amber);
      const p1 = new THREE.PointLight('#00e5ff', 6, 6); p1.position.set(0, 1.2, 0); scene.add(p1);
      const p2 = new THREE.PointLight('#ff2bd6', 4, 5); p2.position.set(1.3, .8, .4); scene.add(p2);
      const tubes = scene.userData.heroes.filter((m) => m.userData.kind === 'knot' || m.userData.kind === 'ico');
      return (t) => tubes.forEach((m, id) => { const on = h1(Math.floor(t * 24) + id * 17) > .97 ? .25 : 1; m.material.color.set(m.userData.col).multiplyScalar(NEON * on); });
    },
    passes: ({ FX, THREE, W, H }) => [new UnrealBloomPass(new THREE.Vector2(W, H), 1.6, .5, .85), FX.chroma({ amount: 1.8 }),
      FX.grade({ lift: [.02, 0, .05], gain: [1, .95, 1.1], sat: 1.2 }), FX.grain({ amount: .04 }), FX.vignette({ strength: .4 })],
  },
  noir: {
    n: 27, title: 'Film noir', bg: '#000000', noir: true,
    mat: (c, kind, col) => new c.THREE.MeshStandardMaterial({ color: kind === 'ground' ? '#777' : '#bbb', roughness: .7 }),
    passes: ({ FX }) => [FX.grade({ lift: [0, 0, 0], gamma: [.85, .85, .85], gain: [1.15, 1.15, 1.15], sat: 0 }), FX.grain({ amount: .08, size: 1.5 }),
      FX.vignette({ strength: .5, softness: .4 })],
  },
  'film-stock': {
    n: 28, title: '70s/80s film stock', bg: '#a9c4c9', weave: true,
    mat: (c, kind, col) => new c.THREE.MeshStandardMaterial({ color: col, roughness: .6 }),
    passes: ({ FX, THREE, W, H }) => {
      const dust = customPass('dust', {}, `uniform sampler2D tDiffuse; uniform float uTime; uniform vec2 uResolution; varying vec2 vUv;
        float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)))*43758.5453); }
        void main(){ vec3 c = texture2D(tDiffuse, vUv).rgb; float f = floor(uTime*24.);
          for (int i=0;i<6;i++){ vec2 q = vec2(h(vec2(f, float(i))), h(vec2(float(i), f+3.))); float r = (1.+3.*h(vec2(f+float(i), 7.)))/uResolution.y;
            vec2 d = (vUv-q)*vec2(uResolution.x/uResolution.y, 1.); c *= 1. - .7*smoothstep(r, r*.4, length(d)); }
          float sx = h(vec2(f, 11.)); if (h(vec2(f, 13.)) > .6) c *= 1. - .35*smoothstep(1.5/uResolution.x, 0., abs(vUv.x - sx));
          gl_FragColor = vec4(c, 1.); }`);
      return [new UnrealBloomPass(new THREE.Vector2(W, H), .3, .4, .8),            // halation, weak
        FX.grade({ lift: [.04, .03, .01], gamma: [1.05, 1, .92], gain: [1.05, .98, .88], sat: .85 }), FX.chroma({ amount: 1.2 }), dust,
        FX.grain({ amount: .07, size: 2 }), FX.vignette({ strength: .35 })];
    },
  },
  '1-bit': {
    n: 31, title: '1-bit dithered monochrome', bg: '#d8d8d8', step: 12, quantise: true,
    mat: (c, kind, col) => new c.THREE.MeshStandardMaterial({ color: col, roughness: .7 }),
    passes: ({ FX }) => [FX.grade({ gain: [1.1, 1.1, 1.1] }), FX.dither({ levels: 2, scale: 2, mono: 1 })],
  },
  'four-colour': {
    n: 32, title: 'Four-colour handheld palette', bg: '#9bbc0f', toneMapping: 'none', step: 12, quantise: true,
    mat: (c, kind, col) => new c.THREE.MeshLambertMaterial({ color: col }),
    passes: ({ FX }) => [FX.pixelate({ size: 6, levels: 4 }),
      // palette map: film.html appends OutputPass after this, so the pass writes LINEAR palette colours that the
      // sRGB encode turns into the exact hexes (#0f380f #306230 #8bac0f #9bbc0f)
      customPass('palette4', {}, `uniform sampler2D tDiffuse; varying vec2 vUv;
        vec3 lin(vec3 c){ return mix(c/12.92, pow((c+.055)/1.055, vec3(2.4)), step(.04045, c)); }
        void main(){ vec3 c = texture2D(tDiffuse, vUv).rgb; float l = pow(max(dot(c, vec3(.2126,.7152,.0722)), 0.), 1./2.2);
          int idx = int(floor(clamp(l, 0., 1.) * 3.999)); vec3 p = idx == 0 ? vec3(15.,56.,15.) : idx == 1 ? vec3(48.,98.,48.) : idx == 2 ? vec3(139.,172.,15.) : vec3(155.,188.,15.);
          gl_FragColor = vec4(lin(p/255.), 1.); }`)],
  },
  halftone: {
    n: 34, title: 'Halftone comic', bg: '#f2e6c9', step: 12, quantise: true,
    mat: (c, kind, col) => new c.THREE.MeshToonMaterial({ color: col, gradientMap: c.ramp3 }),
    passes: ({ FX }) => [FX.ink({ threshold: .1, width: 1.5, keep: 1 }), FX.posterize({ levels: 4 }), FX.halftone({ cell: 7, angle: .26, cmyk: 1 }),
      FX.paper({ strength: .15, tint: [.97, .94, .86] })],
  },
  riso: {
    n: 35, title: 'Risograph zine', bg: '#d9cfbb', keyI: 1.3, toneMapping: 'none', step: 8,
    mat: (c, kind, col) => new c.THREE.MeshStandardMaterial({ color: col, roughness: .8 }),
    // the optional FX.halftone({cell:5, cmyk:0}) before riso is left out: it turns both plates into the same grey dots and the print reads pale
    passes: ({ FX }) => [FX.riso({ inkA: [.97, .33, .48], inkB: [.12, .38, .78], offset: [3, -2] }), FX.grain({ amount: .03 })],
    animate: (t, passes) => { const k = Math.floor(t * 8); passes[0].uniforms.u_offset.value = [2 + h1(k), -1 - h1(k + 1)]; },
  },
  glitch: {
    n: 46, title: 'Glitch art on beats', bg: '#bfe0f2',
    mat: (c, kind, col) => new c.THREE.MeshToonMaterial({ color: col, gradientMap: c.ramp3 }),
    // look passes = recipe 1 (ink over MeshToonMaterial; FX.toon left out, see anime-cel), then glitch + chroma as written
    passes: ({ FX }) => [FX.ink({ threshold: .1, keep: 1 }), FX.glitch({ amount: 0, seed: 3 }), FX.chroma({ amount: 1 })],
    animate: (t, passes, { SONG }) => {
      // recipe: amount = section is 'drop' ? pulse(t, 12) * .8 : 0. Without a song map section() is null, so the
      // sampler treats "no map" as a drop; otherwise the glitch would never fire.
      const sec = SONG.section(t), drop = sec ? sec.kind === 'drop' : true;
      passes[1].uniforms.u_amount.value = drop ? SONG.pulse(t, 12) * .8 : 0;
    },
  },
};

export async function setup(ctx) {
  const { THREE, renderer, W, H, rng } = ctx;
  const id = new URLSearchParams(location.search).get('recipe') || DEFAULT_RECIPE;
  const R = RECIPES[id];
  if (!R) throw new Error(`unknown recipe "${id}" — one of ${Object.keys(RECIPES).join(', ')}`);

  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFShadowMap;
  if (R.toneMapping === 'none') renderer.toneMapping = THREE.NoToneMapping;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(R.bg);
  const camera = R.camera === 'ortho'
    ? new THREE.OrthographicCamera(-R.orthoSize * W / H, R.orthoSize * W / H, R.orthoSize, -R.orthoSize, .1, 100)
    : new THREE.PerspectiveCamera(35, W / H, .1, 100);
  const c = { ...ctx, scene, camera, ramp3: toonRamp(THREE, [60, 160, 255]) };

  // light with shape: key + rim (+ hemi fill), shadows on
  const key = new THREE.DirectionalLight('#fff2dc', R.keyI ?? (R.dark ? .2 : 2.4)); key.position.set(3, 5, 4); key.castShadow = !R.noir;
  key.shadow.mapSize.set(2048, 2048); Object.assign(key.shadow.camera, { left: -4, right: 4, top: 4, bottom: -4 }); key.shadow.bias = -.0005;
  if (R.softKey) key.shadow.radius = 8;
  const rim = new THREE.DirectionalLight(R.dark ? '#ff2bd6' : '#9fb7ff', R.dark ? .6 : 1.3); rim.position.set(-4, 2.5, -3);
  const hemi = new THREE.HemisphereLight('#ffffff', '#7a6a58', R.softKey ? 1.2 : .6);
  if (!R.noir) scene.add(key, rim, hemi);

  const pal = { knot: '#d9534f', box: '#3a9c98', ico: '#e8aa38', ground: '#d9c7a6', ...(R.palette || {}) };
  const mk = (kind, geo) => { const m = new THREE.Mesh(geo, R.mat(c, kind, pal[kind])); m.userData = { kind, col: pal[kind] }; m.castShadow = m.receiveShadow = true; return m; };
  const knot = mk('knot', new THREE.TorusKnotGeometry(.48, R.thinKnot ? .03 : .16, 160, R.thinKnot ? 8 : 20));
  const box = mk('box', new THREE.BoxGeometry(.85, .85, .85));
  const ico = mk('ico', new THREE.IcosahedronGeometry(.55, R.lowPoly ? 1 : 0));
  const heroes = [knot, box, ico];
  scene.userData.heroes = heroes;
  scene.add(...heroes);
  if (!R.noGround) {
    const ground = mk('ground', new THREE.PlaneGeometry(14, 14)); ground.rotation.x = -Math.PI / 2; ground.castShadow = false; scene.add(ground);
  }
  if (R.outline) for (const m of heroes) { const hull = new THREE.Mesh(m.geometry, hullMaterial(THREE, '#1a1416', .03)); m.add(hull); }
  // ligne claire / woodblock: shadows only as flat darker patches (separate meshes), never gradients
  if (R.flatShadows) for (const [x, z, r] of [[0, 0, .75], [-1.35, .55, .62], [1.3, .45, .55]]) {
    const s = new THREE.Mesh(new THREE.CircleGeometry(r, 40), new THREE.MeshBasicMaterial({ color: new THREE.Color(pal.ground).multiplyScalar(.72) }));
    s.rotation.x = -Math.PI / 2; s.position.set(x + .25, .003, z - .18); s.scale.set(1.25, .8, 1); scene.add(s);
  }
  // film noir: one hard spot through venetian blinds, black exponential fog
  if (R.noir) {
    scene.fog = new THREE.FogExp2('#000', .08);
    const spot = new THREE.SpotLight('#ffffff', 220, 0, .5, .1, 2); spot.position.set(4.5, 5.5, 3); spot.target.position.set(0, .4, 0);
    spot.castShadow = true; spot.shadow.mapSize.set(4096, 4096); spot.shadow.bias = -.0004; scene.add(spot, spot.target);
    scene.add(new THREE.HemisphereLight('#ffffff', '#000000', .04));
    const blinds = new THREE.Group();
    for (let i = 0; i < 12; i++) { const s = new THREE.Mesh(new THREE.BoxGeometry(2.2, .07, .02), new THREE.MeshBasicMaterial({ color: '#000' })); s.position.y = (i - 5.5) * .16; s.castShadow = true; blinds.add(s); }
    blinds.position.set(3.0, 3.7, 2.0); blinds.lookAt(spot.position); scene.add(blinds);
  }
  const extraUpdate = R.extras ? R.extras(c) : null;
  const passes = R.passes(c);
  const noise = R.weave ? createNoise2D(rng(28)) : null;

  function update(t, uctx) {
    const tq = R.quantise ? Math.floor(t * 12) / 12 : t;           // poses on twos, camera on ones
    const a = .6 + t * .15;
    camera.position.set(Math.sin(a) * 5.6, 2.3, Math.cos(a) * 5.6);
    camera.lookAt(0, .55, 0);
    if (R.camera === 'ortho') { camera.position.multiplyScalar(2); camera.lookAt(0, .55, 0); }
    if (noise) {
      const f = Math.floor(t * 24);
      camera.setViewOffset(W, H, 1.5 * noise(f * .3, 0), 1 * noise(f * .3 + 9, 0), W, H);   // gate weave per frame index
      camera.rotateZ((.3 * Math.PI / 180) * noise(t * .5, 5));                               // handheld, low frequency
    }
    knot.position.set(0, 1.0 + .08 * Math.sin(tq * 1.4), 0); knot.rotation.set(tq * .5, tq * .7, 0);
    box.position.set(-1.35, .425, .55); box.rotation.set(0, .4 + tq * .2, 0);
    ico.position.set(1.3, .55, .45); ico.rotation.set(tq * .3, tq * .25, 0);
    if (R.jitter) {   // replacement boil: micro-jitter per drawing
      const k = Math.floor(t * 12);
      heroes.forEach((m, i) => m.position.add(new THREE.Vector3(h1(k * 3 + i) - .5, h1(k * 5 + i + 1) - .5, h1(k * 7 + i + 2) - .5).multiplyScalar(.004)));
    }
    if (extraUpdate) extraUpdate(t, camera);
    if (R.animate) R.animate(t, passes, uctx);
  }
  return { scene, camera, passes, update, ...(R.step ? { step: R.step } : {}) };
}
