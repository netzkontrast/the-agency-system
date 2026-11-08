// scenes/scene.js — a three medium film. setup() builds once; update(t) sets every animated value from t.
// Read <studio>/references/three-medium.md before building (contract, determinism, passes, style recipes).
export async function setup({ THREE, FX, W, H, rng }) {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#efe7d6');
  const camera = new THREE.PerspectiveCamera(35, W / H, 0.1, 100);

  // light with shape: a key and a rim, never a flat wash
  const key = new THREE.DirectionalLight('#fff4e0', 2.2); key.position.set(3, 5, 4); scene.add(key);
  const rim = new THREE.DirectionalLight('#9fb7ff', 1.2); rim.position.set(-4, 2, -3); scene.add(rim);
  scene.add(new THREE.HemisphereLight('#ffffff', '#8a7a66', 0.6));

  // toon material with a 4-step ramp: reads as cel animation under the ink pass
  const ramp = new THREE.DataTexture(new Uint8Array([40, 110, 190, 255]), 4, 1, THREE.RedFormat);
  ramp.minFilter = ramp.magFilter = THREE.NearestFilter; ramp.needsUpdate = true;
  const toon = (c) => new THREE.MeshToonMaterial({ color: c, gradientMap: ramp });

  const ground = new THREE.Mesh(new THREE.CircleGeometry(6, 64), toon('#d9c7a6'));
  ground.rotation.x = -Math.PI / 2; scene.add(ground);
  const r = rng(7), shapes = [];
  for (let i = 0; i < 7; i++) {
    const g = i % 3 === 0 ? new THREE.IcosahedronGeometry(0.45, 0) : i % 3 === 1 ? new THREE.TorusKnotGeometry(0.3, 0.1, 96, 12) : new THREE.BoxGeometry(0.6, 0.6, 0.6);
    const m = new THREE.Mesh(g, toon(i === 1 ? '#3a9c98' : ['#d97757', '#e8aa38', '#7b5ca8'][i % 3]));
    m.userData = { a: (i / 7) * Math.PI * 2, r: 1.4 + r() * 1.2, h: 0.5 + r() * 0.8, s: 0.5 + r() };
    scene.add(m); shapes.push(m);
  }

  const fade = FX.fade({ amount: 0 });   // last in the chain: fades the inked frame, so no outline is left behind
  const passes = [FX.ink({ threshold: 0.12, keep: 1 }), FX.boil({ fps: 12, amount: 1.0 }), FX.paper({ strength: 0.2 }), FX.grain({ amount: 0.04 }), FX.vignette(), fade];

  // timings from the song map (stressed syllables), never hand-typed
  const W0 = SONG && SONG.map ? SONG.map.words : [];
  const stressOf = (i, fb) => (W0[i] ? W0[i].stress : fb);
  const PULLS = [stressOf(1, 1.5), stressOf(3, 2.05)];                // "mich", "mich": small inward breaths
  const BREATH = SONG && SONG.line(0) ? SONG.line(0).key.stress : 2.5;   // "atmen": breathe out
  const ICH = SONG && SONG.line(1) ? SONG.line(1).key.stress : 4.0;      // "ich": the camera starts to choose
  const HIER = stressOf(7, 5.0);                                        // "hier": the push settles
  const END0 = 7.0;    // closing gesture from the 7.0 beat, blank paper on the 7.51 downbeat, held to 8.0
  const back0 = (t) => ease((t - END0) / 0.9);   // the page returns with the audio's fade: paper only at 7.9 s
  const LAST = SONG && SONG.map && SONG.map.downbeats ? SONG.map.downbeats.filter((d) => d < 7.9).pop() : 7.5;
  const ease = (x) => { x = Math.min(1, Math.max(0, x)); return x * x * (3 - 2 * x); };
  const spring = (x, k = 5, w = 9) => (x < 0 ? 0 : 1 - Math.exp(-k * x) * Math.cos(w * x));
  // eased kick: starts with zero velocity (no one-frame jump), peaks ~0.12 s after the hit, settles
  const kick = (x) => (x < 0 ? 0 : Math.pow(Math.sin(Math.min(x * 6, Math.PI)), 2) * Math.exp(-4 * x));
  const DOWNS = SONG && SONG.map && SONG.map.downbeats ? SONG.map.downbeats : [1.53, 3.53, 5.53, 7.51];
  const bar = (t) => DOWNS.reduce((s, d) => s + kick(t - d), 0);   // a squash-and-stretch kick on every downbeat
  const hero = shapes[1];                                              // the teal knot
  hero.scale.setScalar(0.8);   // the hub of the ring: always mid-ground, the same size as the others — found, not given
  const orbit = new THREE.Vector3(), close = new THREE.Vector3(), look = new THREE.Vector3(), target = new THREE.Vector3();

  function update(t, { SONG }) {
    const beat = SONG ? SONG.pulseSoft(t) : 0;   // soft attack: positions never jump in one frame
    const clear = ease((t - ICH + 0.3) / (HIER - ICH + 0.3));   // the others start to clear just before "ich"
    const leave = clear;                          // once gone, the six stay gone: the closing gesture shows only the knot
    const inhale = kick(t - PULLS[0]) * 0.08 + kick(t - PULLS[1]) * 0.15;   // two pulls, the second deeper, build into the release
    const out = spring(t - BREATH + 0.15) * 0.9;                         // anticipation 0.15 s before the syllable
    const down = bar(t);
    const push = ease((t - ICH) / Math.max(0.4, HIER - ICH));            // settles exactly on "hier"
    for (const m of shapes) {
      const { a: a0, r: rad, h, s } = m.userData;
      if (m === hero) { m.position.set(0, 1.05 + Math.sin(t * 1.1) * 0.12 + beat * 0.08, 0);   // raised: never hidden behind the ring
        m.rotation.set(t * 0.6, t * 0.45 + Math.PI * ease((t - 5.53) / 0.7), 0); continue; }   // a half-turn on the 5.53 downbeat
      const rr = rad * (1 + out * 0.45 - inhale + clear * 2.0);  // the others breathe out, then drift outward …
      const sq = 1 + 0.35 * kick(t - BREATH) + 0.18 * down;      // … swell on "atmen" and kick on every downbeat …
      const k0 = 0.78 * (1 - leave);                             // smaller than the hero: one focal point from frame 0
      m.scale.set(sq * k0, (2 - sq) * k0, sq * k0);   // … and shrink away, gone by "hier"
      m.position.set(Math.cos(a0 + t * 0.3 * s) * rr, h + Math.sin(t * 1.3 * s + a0) * 0.2 + beat * 0.12, Math.sin(a0 + t * 0.3 * s) * rr);
      m.rotation.set(t * 0.7 * s, t * 0.5 + a0, 0);
    }
    const a = 0.9 + t * 0.25;                    // start phase: the knot is visible between its neighbours at frame 0
    orbit.set(Math.cos(a) * 6, 2.6 + Math.sin(t * 0.4) * 0.2, Math.sin(a) * 6);
    close.copy(hero.position).add(new THREE.Vector3(Math.cos(a) * 1.9, 0.5, Math.sin(a) * 1.9));
    const back = back0(t);                                             // ONE closing gesture 7.0–7.51: back to the wide view while the page returns
    const k2 = push * (1 - back);
    camera.position.lerpVectors(orbit, close, k2);
    look.set(0, 0.8, 0); target.lerpVectors(look, hero.position, k2);
    const acc = t > HIER && t < END0 ? (SONG ? SONG.pulseSoft(t, 0.12, 9) : 0) : 0;   // accents on the beats of the hold
    const hk = 1 + 0.12 * acc + 0.22 * down + 0.3 * kick(t - BREATH);   // the hero answers downbeats and the breath too
    hero.scale.set(0.95 * hk, 0.95 * (2 - hk), 0.95 * hk);
    hero.rotation.z = 0.35 * down;
    camera.lookAt(target);
    fade.uniforms.u_amount.value = Math.min(1, 0.55 * (1 - ease(t / 0.4)) + back * back);   // frame 0 already shows the scene; the closing gesture ends on paper
  }
  // the release: blank paper from the 7.51 downbeat to the end is a deliberate hold (storyboard shot 5)
  return { scene, camera, passes, update, step: 12, holds: [[7.8, 8.0]] };   // step: the boil pass redraws 12 times a second
}
