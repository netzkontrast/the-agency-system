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
    const m = new THREE.Mesh(g, toon(['#d97757', '#3a9c98', '#e8aa38', '#7b5ca8'][i % 4]));
    m.userData = { a: (i / 7) * Math.PI * 2, r: 1.4 + r() * 1.2, h: 0.5 + r() * 0.8, s: 0.5 + r() };
    scene.add(m); shapes.push(m);
  }

  const passes = [FX.ink({ threshold: 0.12, keep: 1 }), FX.boil({ fps: 12, amount: 1.0 }), FX.paper({ strength: 0.2 }), FX.grain({ amount: 0.04 }), FX.vignette()];

  function update(t, { SONG }) {
    const beat = SONG ? SONG.pulse(t, 6) : 0;
    camera.position.set(Math.cos(t * 0.25) * 6, 2.6 + Math.sin(t * 0.4) * 0.3, Math.sin(t * 0.25) * 6);
    camera.lookAt(0, 0.6, 0);
    for (const m of shapes) {
      const { a, r: rad, h, s } = m.userData;
      m.position.set(Math.cos(a + t * 0.3 * s) * rad, h + Math.sin(t * 1.3 * s + a) * 0.2 + beat * 0.15, Math.sin(a + t * 0.3 * s) * rad);
      m.rotation.set(t * 0.7 * s, t * 0.5 + a, 0);
    }
  }
  return { scene, camera, passes, update, step: 12 };   // step: the boil pass redraws 12 times a second
}
