// scenes/scene.js — take 8 of the pipeline smoke film (three medium). One idea: a ring of shapes crowds the teal
// knot until it cannot breathe; on "atmen" it pushes them back; on "ich" they lie down and become marks on the floor;
// on "hier" the knot lands among them; on 5.53 they stand up again at a distance — room to breathe — and all of
// them breathe together to the last downbeat. Every value is a function of t; every event time comes from the song map.
export async function setup({ THREE, FX, W, H, SONG, renderer }) {
  const scene = new THREE.Scene();
  const bgWarm = new THREE.Color('#f1e6cf'), bgDeep = new THREE.Color('#e9cfa8');
  scene.background = bgWarm.clone();
  const camera = new THREE.PerspectiveCamera(35, W / H, 0.1, 100);

  const key = new THREE.DirectionalLight('#fff4e0', 2.2); key.position.set(3, 6, 4); scene.add(key);
  const rim = new THREE.DirectionalLight('#9fb7ff', 1.1); rim.position.set(-4, 2, -3); scene.add(rim);
  scene.add(new THREE.HemisphereLight('#ffffff', '#8a7a66', 0.6));

  const ramp = new THREE.DataTexture(new Uint8Array([70, 140, 205, 255]), 4, 1, THREE.RedFormat);
  ramp.minFilter = ramp.magFilter = THREE.NearestFilter; ramp.needsUpdate = true;
  const softRamp = new THREE.DataTexture(new Uint8Array([130, 195, 255]), 3, 1, THREE.RedFormat);
  softRamp.minFilter = softRamp.magFilter = THREE.NearestFilter; softRamp.needsUpdate = true;
  const toon = (c, r = ramp) => new THREE.MeshToonMaterial({ color: c, gradientMap: r });

  const groundBase = new THREE.Color('#dcc9a6'), groundWarm = new THREE.Color('#efa25e');
  const ground = new THREE.Mesh(new THREE.CircleGeometry(60, 96), toon('#dcc9a6'));
  ground.rotation.x = -Math.PI / 2; scene.add(ground);
  // drawn blob shadows straight below each object (a shadow map gave the knot a face and the blocks drifting shadows)
  const blobGeo = new THREE.CircleGeometry(1, 48), shadowCol = new THREE.Color('#c9b48f');
  const blob = (r) => { const b = new THREE.Mesh(blobGeo, new THREE.MeshBasicMaterial({ color: shadowCol })); b.rotation.x = -Math.PI / 2; b.position.y = 0.014; b.renderOrder = 2; b.userData.r = r; scene.add(b); return b; };
  const setBlob = (b, obj, h0) => { const lift = Math.min(1, Math.max(0, (obj.position.y - h0) / 0.8)); b.material.color.copy(shadowCol).lerp(groundNow, 0.75 * lift); const k = b.userData.r * (1 - 0.45 * lift); b.position.x = obj.position.x; b.position.z = obj.position.z; b.scale.set(k * obj.scale.x, k * obj.scale.z, 1); };

  // floor ripples: flat rings that run out from the knot on the big beats (drawn lines, not light — no band pops)
  const ripples = [];
  for (let i = 0; i < 12; i++) {
    const r = new THREE.Mesh(new THREE.RingGeometry(0.96, 1, 96), new THREE.MeshBasicMaterial({ color: '#b98a5a', side: THREE.DoubleSide }));
    r.rotation.x = -Math.PI / 2; r.position.y = 0.004; r.renderOrder = 1; scene.add(r); ripples.push(r);
  }

  const inkBrown = new THREE.Color('#b98a5a');
  // the crowd: six shapes in a ring around the knot
  const ring = [];
  const geos = [new THREE.IcosahedronGeometry(0.36, 0), new THREE.BoxGeometry(0.5, 0.5, 0.5), new THREE.OctahedronGeometry(0.4, 0)];
  const cols = ['#d97757', '#e8aa38', '#7b5ca8'];
  for (let i = 0; i < 6; i++) {
    const m = new THREE.Mesh(geos[i % 3], toon(cols[i % 3]));
    m.userData = { a: (i / 6) * Math.PI * 2 + 0.3 };
    m.userData.blob = blob(0.34); scene.add(m); ring.push(m);
  }
  const hero = new THREE.Mesh(new THREE.TorusKnotGeometry(0.42, 0.15, 256, 32), toon('#3a9c98', softRamp));
  const heroBlob = blob(0.62); scene.add(hero);

  // timings from the song map, with fallbacks
  const words = SONG && SONG.map ? SONG.map.words : [];
  const st = (i, fb) => (words[i] ? words[i].stress : fb);
  const MICH = [st(1, 1.5), st(3, 2.04)], ATMEN = st(4, 2.5), ICH = st(5, 4.0), HIER = st(7, 5.0);
  const DOWNS = SONG && SONG.map && SONG.map.downbeats ? SONG.map.downbeats : [1.53, 3.53, 5.53, 7.51];
  const BEATS = SONG && SONG.map && SONG.map.beats ? SONG.map.beats : [0, .5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5];
  const [D1, D2, D3, D4] = DOWNS;

  const clamp = (x) => Math.min(1, Math.max(0, x));
  const ease = (x) => { x = clamp(x); return x * x * (3 - 2 * x); };
  const easeOut = (x) => 1 - Math.pow(1 - clamp(x), 3);
  const back = (x) => { x = clamp(x); const c = 1.7; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };   // overshoot
  // a hit that PEAKS on its time: smooth rise over the 0.08 s before, then decays (the old sin² envelope peaked 0.26 s late)
  const kick = (x) => { if (x < -0.08) return 0; if (x < 0) { const u = (x + 0.08) / 0.08; return u * u * (3 - 2 * u); } return Math.exp(-5 * x); };
  const step = (t, at, len = 0.22) => ease((t - at + 0.06) / len);   // a step that lands on `at` (6 frames, starts 1.5 frames early)

  const fade = FX.fade({ amount: 0 });
  const passes = [FX.ink({ threshold: 0.15, keep: 1 }), FX.boil({ fps: 12, amount: 0.9 }), FX.paper({ strength: 0.2 }), FX.grain({ amount: 0.035 }), FX.vignette(), fade];
  const cam = new THREE.Vector3(), look = new THREE.Vector3(), box = new THREE.Box3(), groundNow = new THREE.Color();

  function update(t) {
    groundNow.copy(groundBase).lerp(groundWarm, Math.max(0.9 * kick(t - ATMEN), 0.35 * ease((t - HIER) / 1.2)));
    // --- the crowd's radius: steps in on the first beats and both "mich", pushed back on "atmen", stands wide on 5.53
    const STOMPS = [BEATS[1], BEATS[2], MICH[0], MICH[1]];
    const B45 = BEATS[9];
    const press = 0.1 * (step(t, BEATS[1]) + step(t, BEATS[2])) + 0.12 * step(t, MICH[0]) + 0.13 * step(t, MICH[1]);   // 1.75 → 1.3: crowded, never overlapping
    const stomp = STOMPS.reduce((acc, b) => acc + Math.sin(Math.PI * clamp((t - b + 0.2) / 0.2)), 0);   // a hop that lands on each step
    const landK = STOMPS.reduce((acc, b) => acc + kick(t - b), 0);
    const pushed = ease((t - ATMEN + 0.12) / 0.3) + 0.12 * Math.sin(Math.PI * clamp((t - ATMEN - 0.18) / 0.5));   // "atmen": pushed back, a little overshoot
    let r = 1.75 - press + (2.1 - 1.3) * pushed;               // 2.1 after the breath
    const down = DOWNS.map((d) => kick(t - d));
    const lie = ease((t - ICH + 0.15) / 0.22);                  // "ich": they slam flat into floor marks (6 frames: an event, not a morph)
    const rise = ease((t - D3 + 0.1) / 0.2);                     // 5.53: they spring up again (5 frames: the in-between is a blink), far out
    r = r + 0.1 * rise;                                          // 2.2: the final ring

    const breathe = t > D3 ? 0.5 - 0.5 * Math.cos(Math.PI * 2 * (t - D3 - 0.5) / 1.0) : 0;   // one breath per bar-half, peaks on 6.53 and 7.53

    ring.forEach((m, i) => {
      const { a } = m.userData;
      const turns = STOMPS.reduce((acc, b) => acc + ease((t - b + 0.2) / 0.22), 0) + 2 * ease((t - 6.53 + 0.15) / 0.3) + 2 * ease((t - 7.03 + 0.15) / 0.3);
      const spin = a + 0.12 * t + 0.35 * pushed + (Math.PI / 12) * turns;   // the ring turns a notch on every stomp; one slot (60°) on 6.53 and on 7.03
      const wave = kick(t - 3.0 - i * 0.04) + kick(t - 3.5 - i * 0.04);   // hops round the ring in the gap
      const springUp = Math.sin(Math.PI * clamp((t - D3 + 0.1) / 0.45)) * 0.35;   // they jump as they stand up
      const shuffle = Math.sin(Math.PI * clamp((t - 6.53 + 0.15) / 0.3)) + Math.sin(Math.PI * clamp((t - 7.03 + 0.15) / 0.3));
      const finale = Math.sin(Math.PI * clamp((t - D4 + 0.25) / 0.25)) * 0.6;   // all jump together and land on 7.51
      const hop = 0.4 * wave + 0.75 * stomp + 0.3 * (down[0] + down[1]) + 0.08 * breathe * rise + springUp + 0.35 * shuffle + finale;
      const flat = lie * (1 - rise);                           // 1 = lying on the floor as a flat mark
      const markPulse = flat * 0.25 * (kick(t - B45) + kick(t - HIER));   // the marks answer the beats while the knot comes down
      const rr = r * (1 + 0.04 * breathe * rise);
      m.position.set(Math.cos(spin) * rr, (0.36 + hop) * (1 - flat) + 0.02 * flat, Math.sin(spin) * rr);
      const sq = 1 + 0.3 * landK + 0.25 * (down[0] + down[1] + down[3]) - 0.15 * wave;
      const k = 0.9 * (1 + 0.1 * breathe * rise);
      m.scale.set(sq * k * (1 + 0.25 * flat + markPulse), Math.max(0.04, (2 - sq) * k * (1 - 0.96 * flat)), sq * k * (1 + 0.25 * flat + markPulse));
      m.rotation.set((t * 0.7 + i) * (1 - flat), t * 0.5 + a, 0);
      setBlob(m.userData.blob, m, 0.36); m.userData.blob.visible = flat < 0.5;
    });

    // --- the knot: squeezed by the crowd, swells on "atmen", lands on "hier", breathes with the ring
    const squeeze = press / 0.45;                                  // 0..1 while crowded
    const swell = kick(t - ATMEN) * 0.55;
    const land = 0.5 * ease((t - B45 + 0.18) / 0.18) + 0.5 * ease((t - HIER + 0.18) / 0.18);   // two hops down: 4.53 and "hier"
    const hopArc = 0.25 * (Math.sin(Math.PI * clamp((t - B45 + 0.35) / 0.35)) + Math.sin(Math.PI * clamp((t - HIER + 0.35) / 0.35)));
    const thud = kick(t - HIER);
    const y = 1.0 + 0.08 * Math.sin(t * 1.3) * (1 - land);
    const beatK = SONG ? SONG.pulseSoft(t, 0.1, 5) : 0;
    const pulse = 0.12 * breathe + 0.22 * down[3] + 0.2 * (down[0] + down[1]) - 0.22 * landK + 0.12 * beatK * ease((t - HIER) / 0.3)
      + 0.25 * kick(t - ICH) + 0.15 * (kick(t - 3.0) + kick(t - 3.5)) + 0.15 * (kick(t - 6.53) + kick(t - 7.03));   // squeezed on every stomp, answers 'ich', the wave and every beat in the hold
    const sx = (1 - 0.18 * squeeze + swell + pulse + 0.2 * thud), sy = (1 - 0.1 * squeeze + 0.6 * swell + 0.8 * pulse - 0.25 * thud);
    hero.scale.set(sx, sy, sx);
    hero.rotation.set(t * 0.5 * (1 - 0.6 * land) + 0.9 * land, t * 0.4 + Math.PI * ease((t - D3 + 0.05) / 0.8), 0.25 * kick(t - ICH));
    // resting height from the knot's real extent this frame, so on "hier" it touches the floor (shadow meets it)
    hero.position.set(0, 0, 0); hero.updateMatrixWorld(true); box.setFromObject(hero, true);
    const rest = -box.min.y;
    hero.position.y = y * (1 - land) + rest * land + hopArc;
    setBlob(heroBlob, hero, rest);

    // --- ripples: one from the knot on "atmen", "hier", 5.53 and 7.51
    const RIP = [[ATMEN, 1.0], [HIER, 1.0], [D3, 1.0]];
    ripples.forEach((rp, i) => { if (i >= RIP.length) rp.visible = false; });
    RIP.forEach(([at, life], i) => {
      const x = t - at, rp = ripples[i];
      const on = x > 0 && x < life;
      rp.visible = on;
      if (on) { const s = 0.6 + 1.3 * easeOut(x / 1.2); rp.scale.set(s, s, 1); rp.material.color.copy(groundNow).lerp(inkBrown, ease(x / 0.12) * (1 - ease((x - life * 0.42) / (life * 0.5)))); }
    });

    // --- camera: high three-quarter view (floor fills the frame, horizon in the top third), close on the crowd,
    //     opens with the push, settles low and centred on "hier", eases out to the final composition from 7.0
    const ang = 0.9 + 0.22 * t - 0.12 * ease((t - 7.0) / 1.0);   // the orbit slows to rest with the fade
    const open = ease((t - ATMEN + 0.25) / 0.8), settle = ease((t - ICH - 0.4) / 1.2), out = ease((t - 6.8) / 1.0);
    const hold = ease((t - D3 + 0.3) / 1.2);   // the hold widens to keep the standing ring in frame
    const backs = 0.22 * (step(t, BEATS[1]) + step(t, BEATS[2]) + step(t, MICH[0]) + step(t, MICH[1]));   // the camera steps back on every beat of the hook
    const dist = 4.7 + backs + 1.3 * open - 0.6 * settle + 1.1 * hold - 0.15 * out;
    const hgt = 3.7 + 0.3 * backs + 0.7 * open - 0.7 * settle + 1.2 * hold - 0.1 * out;
    cam.set(Math.cos(ang) * dist, hgt, Math.sin(ang) * dist);
    camera.position.copy(cam);
    look.set(0, 0.45 - 0.2 * settle - 0.25 * open * (1 - settle) - 0.35 * hold, 0);
    const fwd = 0.55 * (1 - open); look.y += 0.45 * (1 - open);   // in the hook, aim a little toward the camera so the front of the ring stays in frame
    look.x += Math.cos(ang) * fwd; look.z += Math.sin(ang) * fwd; look.y += 0.05 * (1 - open);
    camera.lookAt(look);

    // --- light and colour: the floor flushes warm on "atmen" and stays a little warm from "hier" (no light pulses)
    const flush = kick(t - ATMEN), warmth = 0.35 * ease((t - HIER) / 1.2);
    scene.background.copy(bgWarm).lerp(bgDeep, Math.max(0.6 * flush, warmth));
    fade.uniforms.u_amount.value = 0.3 * ease((t - 7.2) / 0.75);   // settles into the paper with the audio fade (last pass in the chain)
    ground.material.color.copy(groundNow).lerp(groundWarm, 0.12 * (SONG ? SONG.pulseSoft(t, 0.05, 6) : 0) * (1 - ease((t - 7.6) / 0.3)));
  }
  return { scene, camera, passes, update, step: 12, holds: [[7.7, 8.0]] };   // the closing image rests on the audio fade
}
