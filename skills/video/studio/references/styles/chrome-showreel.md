# Style: Glossy chrome showreel

Studio-lit reflective chrome and liquid-metal pseudo-3D objects and type, in FULL COLOR poster fields, cut as rapid beat-locked vignettes with extreme eased morphs: a "showreel" that flexes range on purpose. #1 performing look in the Opus-video corpus. Top case: an Opus 5.5 one-prompt 15 s motion-design showreel (Sep 2026), 1920x1080 @ 60 fps. Studied via contact sheet; note honestly: that case pairs the showreel grammar below with flat Swiss color blocks, while the chrome/liquid-metal surfacing is the corpus's top LOOK. This style folds the top look onto the top structure. Do both.

## Why it works

A showreel is permission to show off: every 2 seconds is a new trick, so attention never settles. Beat-locking (the reference literally prints "128 BPM" and a bar counter on screen) makes the cuts feel inevitable rather than random. Chrome is the flex material: a reflective surface proves you computed light, and a specular streak sweeping across type is motion even when the object holds still. And the self-aware frame ("this is my resume") turns a capability demo into personality.

## Design system

- **Backdrops, full color, hard fields.** One saturated poster field per vignette, no gradients on the field itself: vermilion `#E8442C`, ultramarine `#3230EE`, acid yellow `#D8F000`, ink black `#0E0E10`, cream `#EFEBE0`. The chrome object reflects an implied STUDIO (softboxes, floor, horizon), not the backdrop, but tint the ramp's mid-tones toward the field color so object and field belong together.
- **Chrome ramp** (the material, as a vertical env gradient sampled by surface normal): sky white `#FAFBFF` to cool silver `#C6CDDA`, then a HARD horizon break to near-black `#181B22`, then ground bounce `#5C6472` and deep `#23262E`. The hard sky/ground break at the ramp's "horizon" is what makes metal read as mirror; a smooth ramp reads as plastic.
- **Specular streaks:** 1-3 long thin white softbox reflections (rounded-end bars) laid ACROSS the form, slightly off-axis; one hot core streak at ~100% white, the others at 40-60%. In motion they sweep; frozen, they must look mid-sweep.
- **Contact shadow:** every grounded object gets a tight dark ellipse (multiply, soft edge) plus a faint mirrored reflection fading out below. Floating objects get neither; floaty is a choice, make it once per vignette.
- **Type, two voices.** (1) Hero type: heavy extended grotesque, HUGE (60-80% of frame width), either flat ink `#0E0E10` on a color field or fully chromed pseudo-3D with a visible extrusion. (2) HUD chrome, the signature framing device: thin corner brackets at all four corners, small monospaced caps labels: project name top-left ("MOTION REEL - 2026"), vignette index top-right ("03 - SURFACES"), timecode bottom-left ("00:00:07:32  60 FPS"), beat meter bottom-right ("128 BPM ■□□□ BAR 5/8"), plus a thin progress rule along the bottom edge. The HUD persists across every cut; it is the reel's spine.
- **Motion grammar:** rapid vignettes, 1-2 bars each (~1.9-3.8 s at 128 BPM), HARD cuts exactly on the downbeat. Inside a vignette, ONE morph with extreme easing: expo-out arrivals, back-out overshoots, elastic settles, and motion-blur smears on anything faster than the eye (stretch + blur along velocity, like the reference's kinetic type). Never two ideas per vignette.
- **Structure (the reel):** open on a pulse (dot to burst), then an identity card (name in hero type on the loudest field), then 4-6 trick vignettes, each a different domain (easing chart, pattern field, wireframe or chrome 3D object, kinetic type, physics), then a closing card: logo + name + role, calm, on the identity color. The end card holds a full bar.
- **Format:** 16:9, 1920x1080, 60 fps, 15-30 s. Must work muted (the HUD beat meter SHOWS the rhythm), but ships with a beat-matched track.

## Engine notes: faking a studio in code

- **Canvas 2D, per-facet:** model the object as planar facets with 3D normals; fill each facet with a linear gradient that samples the chrome ramp by the facet's normal Y (up-facing gets sky whites, down-facing gets ground darks, near-horizontal crosses the hard break). High contrast BETWEEN adjacent facets is the crease; add a 1 px darker edge stroke where facets meet.
- **Canvas 2D, per-pixel (liquid metal):** for a chrome sea or blob, walk ImageData: height field h(x,y) from 2-4 seeded sines plus ridged noise, normal from finite differences, then color = ramp(reflected ny), plus specular = pow(max(0, dot(n, half-vector)), 60-200) added as white. One pass at full res is fine for stills; render at half res and upscale for motion.
- **Streaks and grounding:** softbox streaks are drawn shapes (rounded bars, screen/lighter blend), not computed; cheaper and more art-directable. Contact shadow: radial-gradient ellipse, multiply. Mirror reflection: redraw the object flipped, 15-25% alpha, fading mask.
- **Real 3D when the morph needs it:** Three.js `MeshPhysicalMaterial` (metalness 1.0, roughness 0.05-0.15, clearcoat 1.0) with an env map BUILT FROM GRADIENTS: render a small canvas (sky ramp above a hard horizon line, 2-3 white streak bars) through `PMREMGenerator` as an equirect texture. No downloaded HDRIs; the fake studio stays in code.
- **Beat lock:** pick BPM first, derive `beat = 60/BPM`, and schedule every cut and impact at integer beats. Drive the HUD bar counter and progress rule from the same clock so the HUD never lies.
- **Grain:** a faint seeded per-pixel grain (2-3% luma jitter) over the whole frame keeps the flat fields from banding and makes chrome feel filmed.
- **Determinism:** seeded RNG for noise, grain, streak jitter; the same seed must give the same pixels.

**Best for:** model-drop demos and capability flexes, tool and product hype teasers, personal showreels, launch stingers, "look what X made in one prompt" posts; anything where the point is range and craft density per second. The strongest opener style when the subject IS the maker.
