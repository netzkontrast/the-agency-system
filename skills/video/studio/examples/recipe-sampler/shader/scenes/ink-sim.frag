// ink-sim.frag — recipe 43, feedback: advect the previous frame along the curl of snoise, decay .985, inject on beats.
#include "engine/glsl/hash.glsl"
#include "engine/glsl/noise.glsl"
vec2 curl(vec2 p) {
  float e = 0.01;
  float n1 = snoise(p + vec2(0.0, e)), n2 = snoise(p - vec2(0.0, e)), n3 = snoise(p + vec2(e, 0.0)), n4 = snoise(p - vec2(e, 0.0));
  return vec2(n1 - n2, -(n3 - n4)) / (2.0 * e);
}
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
  vec2 uv = fragCoord / iResolution.xy;
  vec2 p = (fragCoord - 0.5 * iResolution.xy) / iResolution.y;
  vec2 vel = curl(p * 2.2 + vec2(iTime * 0.05, 0.0)) * 0.0022;
  float prev = texture(iChannel0, uv - vel * vec2(iResolution.y / iResolution.x, 1.0)).r * 0.985;
  // inject: a drop at a hashed place on every beat (iPulse), plus a constant thin source
  float b = floor(iBeat);
  vec2 at = (hash22(vec2(b, 3.0)) - 0.5) * vec2(1.2, 0.7);
  float drop = iPulse * smoothstep(0.07, 0.0, length(p - at));
  float src = 0.08 * smoothstep(0.03, 0.0, length(p - vec2(-0.55 + 0.1 * sin(iTime), 0.0)));
  fragColor = vec4(min(1.0, prev + drop + src), 0.0, 0.0, 1.0);
}
