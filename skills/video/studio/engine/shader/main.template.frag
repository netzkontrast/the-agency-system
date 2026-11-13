// main.frag — the shown pass: the trails on paper, a beat pulse, film grain.
#include "engine/glsl/hash.glsl"
#include "engine/glsl/noise.glsl"
#include "engine/glsl/color.glsl"
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
  vec2 uv = fragCoord / iResolution.xy;
  vec3 trails = texture(iChannel0, uv).rgb;
  vec2 p = (fragCoord - 0.5 * iResolution.xy) / iResolution.y;
  float paper = 0.9 + 0.08 * fbm2(p * 6.0) + 0.04 * snoise(p * 80.0);
  vec3 col = vec3(0.95, 0.92, 0.85) * paper;
  col = mix(col, vec3(0.12, 0.1, 0.12), clamp(length(trails) * 1.4, 0.0, 1.0));
  col += 0.08 * iPulse * palette(0.6 + 0.1 * iBeat, vec3(0.5), vec3(0.5), vec3(1.0), vec3(0.0, 0.33, 0.67));
  col += (hash12(fragCoord + floor(iTime * 24.0) * 31.7) - 0.5) * 0.04;   // grain, new every frame, from t
  fragColor = vec4(col, 1.0);
}
