// ink-show.frag — ink density multiplied over paper.
#include "engine/glsl/noise.glsl"
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
  vec2 uv = fragCoord / iResolution.xy;
  vec2 p = (fragCoord - 0.5 * iResolution.xy) / iResolution.y;
  float d = texture(iChannel0, uv).r;
  vec3 paper = vec3(0.96, 0.94, 0.89) * (0.93 + 0.05 * fbm2(p * 9.0));
  fragColor = vec4(paper * mix(vec3(1.0), vec3(0.55, 0.08, 0.12), smoothstep(0.0, 0.6, d)), 1.0);
}
