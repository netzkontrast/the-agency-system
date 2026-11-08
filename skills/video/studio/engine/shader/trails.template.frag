// trails.frag — a feedback pass: last frame faded, plus new ink from a few orbiting points (deterministic in t).
#include "engine/glsl/hash.glsl"
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
  vec2 uv = fragCoord / iResolution.xy;
  vec4 prev = texture(iChannel0, uv + vec2(0.0, 0.0008));          // drift upward a little each step
  vec2 p = (fragCoord - 0.5 * iResolution.xy) / iResolution.y;
  float ink = 0.0;
  for (int i = 0; i < 5; i++) {
    float fi = float(i), a = iTime * (0.6 + 0.13 * fi) + fi * 1.7;
    vec2 c = vec2(cos(a), sin(a * 1.3)) * (0.25 + 0.05 * fi);
    ink += smoothstep(0.018, 0.0, length(p - c));
  }
  fragColor = vec4(max(prev.rgb * 0.965, vec3(ink) * vec3(0.95, 0.62, 0.25)), 1.0);
}
