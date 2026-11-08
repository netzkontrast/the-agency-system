// swarm.frag — draws the 400 analytic particles from the position pass; bursts on the pulse.
#include "engine/glsl/color.glsl"
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
  vec2 uv = fragCoord / iResolution.xy;
  float aspect = iResolution.x / iResolution.y;
  vec2 q = vec2((uv.x - 0.5) * aspect, uv.y - 0.5);
  vec3 col = mix(vec3(0.02, 0.03, 0.06), vec3(0.06, 0.05, 0.12), uv.y);
  float px = 1.0 / iResolution.y;
  for (int i = 0; i < 400; i++) {
    vec4 s = texelFetch(iChannel0, ivec2(i, 0), 0);
    vec2 c = vec2((s.x - 0.5) * aspect * 0.9, (s.y - 0.5) * 0.9);
    float r = (1.2 + 1.8 * s.z) * px * (1.0 + 0.8 * iPulse);
    float d = length(q - c);
    vec3 tint = palette(s.z * 0.5 + 0.55, vec3(0.5), vec3(0.5), vec3(1.0), vec3(0.0, 0.33, 0.67));
    col += tint * (smoothstep(r, r * 0.3, d) + 0.25 * exp(-d / (r * 3.0)) * 0.5);
  }
  fragColor = vec4(col, 1.0);
}
