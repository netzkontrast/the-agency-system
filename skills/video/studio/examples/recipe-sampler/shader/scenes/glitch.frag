// glitch.frag — recipe 46 (shader): row displacement on chosen beats, gated by iPulse; clean frames otherwise.
#include "engine/glsl/hash.glsl"
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
  vec2 uv = fragCoord / iResolution.xy;
  float row = floor(uv.y * 32.0);
  float on = step(0.5, hash11(floor(iBeat) + 0.37));        // only some beats glitch
  if (hash12(vec2(row, floor(iBeat))) < iPulse * 0.4 * on) uv.x += (hash12(vec2(row * 3.1, floor(iBeat))) - 0.5) * 0.12 * iPulse;
  float s = 0.006 * iPulse * on;
  vec3 c = vec3(texture(iChannel0, uv + vec2(s, 0.0)).r, texture(iChannel0, uv).g, texture(iChannel0, uv - vec2(s, 0.0)).b);
  fragColor = vec4(c, 1.0);
}
