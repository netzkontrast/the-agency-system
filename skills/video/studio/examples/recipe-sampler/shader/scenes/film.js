// scenes/film.js — recipe sampler, shader medium. Picks the passes for ?recipe=<id> (references/style-recipes.md).
//
//   node <studio>/tools/render.mjs --stills=2 --size=480x270 --query=recipe=raymarch --out=review/raymarch
//
// Without ?recipe= the DEFAULT_RECIPE below is used (the gate cannot pass a query: switch this constant to gate
// another recipe). All GLSL in scenes/ is the sampler's own, plus the studio includes in engine/glsl/.
const DEFAULT_RECIPE = 'synthwave';

export const RECIPES = {
  synthwave: { n: 24, title: 'Synthwave / outrun grid', passes: [{ name: 'main', frag: 'scenes/synthwave.frag' }] },
  'flow-field': { n: 41, title: 'Generative flow field (shader: streamline convolution)', passes: [{ name: 'main', frag: 'scenes/flow.frag' }] },
  'reaction-diffusion': {
    n: 42, title: 'Reaction-diffusion (Gray-Scott, 8 substeps per frame)', warmup: 3,
    // 8 identical sim passes; each is a feedback pass (so the runtime clears it before the warm-up) and reads the pass
    // before it as iChannel1; sim1 reads sim8, which at that moment still holds the previous frame's last substep.
    passes: [
      ...Array.from({ length: 8 }, (_, i) => ({ name: 'sim' + (i + 1), frag: 'scenes/rd-sim.frag', feedback: true, inputs: ['sim' + (i === 0 ? 8 : i)] })),
      { name: 'main', frag: 'scenes/rd-show.frag', inputs: ['sim8'] },
    ],
  },
  'fluid-ink': { n: 43, title: 'Fluid ink in water (cheap: double domain warp)', passes: [{ name: 'main', frag: 'scenes/ink-warp.frag' }] },
  'fluid-ink-fb': {
    n: 43, title: 'Fluid ink in water (feedback advection, warmup 2)', warmup: 2,
    passes: [{ name: 'ink', frag: 'scenes/ink-sim.frag', feedback: true }, { name: 'main', frag: 'scenes/ink-show.frag', inputs: ['ink'] }],
  },
  raymarch: { n: 44, title: 'Raymarched SDF world', passes: [{ name: 'main', frag: 'scenes/raymarch.frag' }] },
  swarm: {
    n: 45, title: 'Particle swarm (analytic)',
    passes: [{ name: 'pos', frag: 'scenes/swarm-pos.frag' }, { name: 'main', frag: 'scenes/swarm.frag', inputs: ['pos'] }],
  },
  '1-bit': {
    n: 31, title: '1-bit dither over the SDF world', step: 12,
    passes: [{ name: 'world', frag: 'scenes/raymarch.frag' }, { name: 'main', frag: 'scenes/dither.frag', inputs: ['world'] }],
  },
  glitch: {
    n: 46, title: 'Glitch on beats over the grid',
    passes: [{ name: 'grid', frag: 'scenes/synthwave.frag' }, { name: 'main', frag: 'scenes/glitch.frag', inputs: ['grid'] }],
  },
};

const id = new URLSearchParams(location.search).get('recipe') || DEFAULT_RECIPE;
const R = RECIPES[id];
if (!R) throw new Error(`unknown recipe "${id}" — one of ${Object.keys(RECIPES).join(', ')}`);

export default { fps: 24, warmup: R.warmup || 0, step: R.step || 0, passes: R.passes };
