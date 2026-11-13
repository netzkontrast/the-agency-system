// swarm-pos.frag — recipe 45: particle i's position, closed form in t: base = hash22(vec2(i)),
// p = base + .2 * vec2(snoise(base*3 + t*.2), snoise(base*3 + 9 - t*.2)). Written to texel (i, 0); other pixels idle.
#include "engine/glsl/hash.glsl"
#include "engine/glsl/noise.glsl"
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
  if (fragCoord.y > 1.0 || fragCoord.x > 400.0) { fragColor = vec4(0.0); return; }
  float i = floor(fragCoord.x);
  vec2 base = hash22(vec2(i, i * 0.37 + 1.0));
  float t = iTime;
  vec2 shared = 0.25 * vec2(snoise(vec2(t * 0.15, 1.0)), snoise(vec2(4.0, t * 0.15)));    // flocking: shared low-frequency drift
  vec2 p = base + 0.2 * vec2(snoise(base * 3.0 + t * 0.2), snoise(base * 3.0 + 9.0 - t * 0.2)) + shared;
  fragColor = vec4(p, hash11(i + 0.5), 1.0);
}
