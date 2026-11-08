// scenes/film.js — the passes of a shader film (see <studio>/references/shader-medium.md).
// The last pass is what the viewer sees. A pass with feedback: true reads its own previous frame as iChannel0;
// the runtime re-simulates `warmup` seconds before each frame so frames stay independent.
export default {
  fps: 24,
  warmup: 1.5,
  passes: [
    { name: 'trails', frag: 'scenes/trails.frag', feedback: true },
    { name: 'main', frag: 'scenes/main.frag', inputs: ['trails'] },
  ],
};
