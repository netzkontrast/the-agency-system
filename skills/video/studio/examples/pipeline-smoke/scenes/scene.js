// scenes/scene.js — take 4 of the pipeline smoke film (three medium). Every value is a function of t; every event
// time comes from the song map. Reads, in order: shapes drop in on the first beats (hook) → two inhales on "mich" →
// the ring breathes out on "atmen" with a warm light → a wave runs round the ring on 3.0 / 3.5 → on "ich" the others
// snap away and the teal knot pops → the camera lands on it on "hier" → half-turn on 5.53, swells on the beats,
// the light turns cool → pull back and return to the page with the audio's fade.
export async function setup({ THREE, FX, W, H, SONG }) {
  const scene = new THREE.Scene();
  const bgWarm = new THREE.Color('#f1e6cf'), bgCool = new THREE.Color('#dfe6ea');
  scene.background = bgWarm.clone();
  const camera = new THREE.PerspectiveCamera(35, W / H, 0.1, 100);

  const key = new THREE.DirectionalLight('#fff4e0', 2.2); key.position.set(3, 5, 4); scene.add(key);
  const rim = new THREE.DirectionalLight('#9fb7ff', 1.2); rim.position.set(-4, 2, -3); scene.add(rim);
  const hemi = new THREE.HemisphereLight('#ffffff', '#8a7a66', 0.6); scene.add(hemi);
  const warm = new THREE.PointLight('#ffb347', 0, 12); warm.position.set(0, 2.2, 0); scene.add(warm);

  const ramp = new THREE.DataTexture(new Uint8Array([40, 110, 190, 255]), 4, 1, THREE.RedFormat);
  ramp.minFilter = ramp.magFilter = THREE.NearestFilter; ramp.needsUpdate = true;
  const toon = (c) => new THREE.MeshToonMaterial({ color: c, gradientMap: ramp });

  const groundBase = new THREE.Color('#d9c7a6'), groundWarm = new THREE.Color('#f0823f');
  const ground = new THREE.Mesh(new THREE.CircleGeometry(6, 64), toon('#d9c7a6'));
  ground.rotation.x = -Math.PI / 2; scene.add(ground);

  // the ring: six shapes on a fixed circle (radius 1.7) around the hero, all inside the wide frame
  const ring = [];
  const geos = [new THREE.IcosahedronGeometry(0.4, 0), new THREE.BoxGeometry(0.55, 0.55, 0.55), new THREE.OctahedronGeometry(0.45, 0)];
  const cols = ['#d97757', '#e8aa38', '#7b5ca8'];
  for (let i = 0; i < 6; i++) {
    const m = new THREE.Mesh(geos[i % 3], toon(cols[i % 3]));
    m.userData = { a: (i / 6) * Math.PI * 2 + 0.3, drop: i * 0.083 };   // drop-in staggered by 2 frames each
    scene.add(m); ring.push(m);
  }
  // the hero gets a softer 3-step ramp: close up, hard bands would be inked as seams
  const softRamp = new THREE.DataTexture(new Uint8Array([120, 190, 255]), 3, 1, THREE.RedFormat);
  softRamp.minFilter = softRamp.magFilter = THREE.NearestFilter; softRamp.needsUpdate = true;
  const hero = new THREE.Mesh(new THREE.TorusKnotGeometry(0.42, 0.14, 192, 24), new THREE.MeshToonMaterial({ color: '#3a9c98', gradientMap: softRamp }));
  scene.add(hero);

  // timings from the song map (stress times), with fallbacks for a missing map
  const words = SONG && SONG.map ? SONG.map.words : [];
  const st = (i, fb) => (words[i] ? words[i].stress : fb);
  const MICH = [st(1, 1.5), st(3, 2.04)], ATMEN = st(4, 2.5), ICH = st(5, 4.0), HIER = st(7, 5.0);
  const DOWNS = SONG && SONG.map && SONG.map.downbeats ? SONG.map.downbeats : [1.53, 3.53, 5.53, 7.51];
  const WAVE = [3.0, 3.5];                                    // beats in the gap between the lines

  const ease = (x) => { x = Math.min(1, Math.max(0, x)); return x * x * (3 - 2 * x); };
  const easeOut = (x) => 1 - Math.pow(1 - Math.min(1, Math.max(0, x)), 3);
  const kick = (x) => (x < 0 ? 0 : Math.pow(Math.sin(Math.min(x * 6, Math.PI)), 2) * Math.exp(-4 * x));   // no one-frame jump
  const land = (x) => (x < 0 ? 0 : Math.exp(-7 * x) * Math.sin(x * 22) * 0.35);   // squash after a landing

  const fade = FX.fade({ amount: 0 });
  const passes = [FX.ink({ threshold: 0.2, keep: 1 }), FX.boil({ fps: 12, amount: 1.0 }), FX.paper({ strength: 0.2 }), FX.grain({ amount: 0.04 }), FX.vignette(), fade];
  const orbit = new THREE.Vector3(), close = new THREE.Vector3(), target = new THREE.Vector3(), look = new THREE.Vector3();

  function update(t) {
    const soft = SONG ? SONG.pulseSoft(t) : 0;
    const down = DOWNS.reduce((s, d) => s + kick(t - d), 0);
    const inhale = kick(t - MICH[0]) * 0.1 + kick(t - MICH[1]) * 0.18;
    const out = ease((t - ATMEN + 0.12) / 0.25) * (1 - 0.5 * ease((t - ATMEN - 0.7) / 0.9));   // a big breath out, settles half back
    const beatHop = SONG ? SONG.pulseSoft(t, 0.1, 5) : 0;     // every shape hops on every beat until "ich"
    const leap = ease((t - ICH + 0.05) / 0.7);                 // on "ich" the ring leaps away over 0.7 s (readable, not a 2-frame scatter)
    const shrink = ease((t - ICH - 0.2) / 0.3);                // and shrinks only in the second half of the leap, already off-centre
    const gone = leap;
    const back = ease((t - 7.0) / 0.9);                         // closing gesture with the audio fade

    ring.forEach((m, i) => {
      const { a, drop } = m.userData;
      const dt = t - drop;                                      // drop-in: falls from y = 3.2, lands at 0.35 + drop
      const fall = dt < 0.35 ? 3.2 - 2.85 * Math.pow(Math.max(0, dt) / 0.35, 2) : 0.35;
      const wave = WAVE.reduce((s, w) => s + kick(t - w - i * 0.05), 0);
      const r = 1.7 * (1 - 1.8 * inhale + 0.3 * out) + 2.6 * leap;   // on "ich" they leap outward …
      const sink = -1.6 * Math.sin(Math.PI * leap);                    // … on a high arc, never through the floor
      m.position.set(Math.cos(a + t * 0.25) * r, fall + 0.3 * wave + 0.22 * beatHop * (1 - gone) - sink, Math.sin(a + t * 0.25) * r);
      const sq = 1 + (dt > 0.35 ? land(dt - 0.35) : 0) + 0.2 * down * (1 - gone);
      const k = 0.85 * (1 + 0.12 * out) * (1 - shrink);            // … and are gone by 4.7 s, at the top of the arc
      m.scale.set(sq * k, (2 - sq) * k, sq * k);
      m.rotation.set(t * 0.8 + i, t * 0.6 + a, 0);
    });

    const hold = ease((t - HIER) / 0.3);   // eased switch: a hard 0/1 would jump while a pulse is high
    const pop = kick(t - ICH) * 0.45 + kick(t - HIER) * 0.25 + 0.25 * down + 0.35 * kick(t - ATMEN) + 0.3 * soft * hold;   // the knot answers every beat in the hold
    hero.position.set(0, 0.95 + Math.sin(t * 1.1) * 0.1 + 0.06 * soft + 0.18 * soft * hold, 0);
    hero.rotation.set(t * 0.6, t * 0.45 + Math.PI * ease((t - 5.53) / 0.7), 0.3 * down);
    hero.scale.set(1 + pop, 1 - pop * 0.6, 1 + pop);

    // camera: starts close and already moving (hook), opens to the ring on the first beats, pushes in on "ich"
    const a = 0.9 + t * 0.25 + 0.9 * ease((t - ICH) / 2.5);   // the orbit speeds up after "ich": the hold keeps travelling
    const open = easeOut(t / 0.9);
    const rOrbit = (3.9 + 2.6 * open) * (1 - 0.08 * kick(t - ATMEN));   // a camera nudge on "atmen"
    orbit.set(Math.cos(a) * rOrbit, 1.9 + 0.7 * open, Math.sin(a) * rOrbit);
    close.set(Math.cos(a) * 3.4, 1.7, Math.sin(a) * 3.4);   // close, with air above and below the knot
    const push = ease((t - ICH) / Math.max(0.4, HIER - ICH)) * (1 - back);
    camera.position.lerpVectors(orbit, close, push);
    look.set(0, 0.7, 0); target.lerpVectors(look, hero.position, push);
    camera.lookAt(target);

    warm.intensity = 3 * kick(t - ATMEN);   // light only on the breath: on toon materials a light pulse flips whole bands (a pop)
    const flush = kick(t - ATMEN);                                                   // "atmen": the page flushes warm
    scene.background.copy(bgWarm).lerp(new THREE.Color('#f6c98f'), 0.8 * flush).lerp(bgCool, ease((t - HIER) / 1.5));
    ground.material.color.copy(groundBase).lerp(groundWarm, 0.95 * flush);   // the floor glows warm on the breath
    fade.uniforms.u_amount.value = 0;   // no fade: the last image is the knot in full colour on the page, settling on the 7.51 downbeat
  }
  return { scene, camera, passes, update, step: 12 };
}
