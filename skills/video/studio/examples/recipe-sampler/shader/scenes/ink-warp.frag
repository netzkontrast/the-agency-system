// ink-warp.frag — recipe 43, cheap: no simulation. warp2 twice, density = smoothstep(.45, .6, fbm2(q * 3)), multiply over paper.
#include "engine/glsl/hash.glsl"
#include "engine/glsl/noise.glsl"
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
  vec2 p = (fragCoord - 0.5 * iResolution.xy) / iResolution.y;
  vec2 q = warp2(warp2(p * 1.5, iTime * 0.1), iTime * 0.07);
  float ink = smoothstep(0.45, 0.6, fbm2(q * 3.0));
  float paper = 0.92 + 0.06 * fbm2(p * 9.0) + 0.03 * snoise(p * 120.0);
  vec3 col = vec3(0.96, 0.94, 0.89) * paper;
  col *= mix(vec3(1.0), vec3(0.12, 0.16, 0.32), ink * 0.9);         // multiply indigo ink over paper
  fragColor = vec4(col, 1.0);
}
