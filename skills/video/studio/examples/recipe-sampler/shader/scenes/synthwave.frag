// synthwave.frag — recipe 24: horizon at uv.y = .45, perspective grid scrolling forward, banded sun, magenta→purple sky.
#include "engine/glsl/hash.glsl"
#include "engine/glsl/sdf.glsl"
#include "engine/glsl/color.glsl"
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
  vec2 uv = fragCoord / iResolution.xy;
  float aspect = iResolution.x / iResolution.y;
  float hz = 0.45;
  vec3 col;
  if (uv.y < hz) {
    // ground: perspective grid, z = depth from the horizon
    float z = hz - uv.y;
    float x = (uv.x - 0.5) * aspect;
    vec2 g = vec2(x / z, 1.0 / z + iTime * 0.8);
    vec2 f = abs(fract(g) - 0.5);                  // 0 at cell centre, .5 on a line
    vec2 d = 0.5 - f;                              // distance to the nearest line, in grid units
    vec2 px = fwidth(g);                           // one pixel in grid units (anti-aliasing)
    float line = max(strokeAA(d.x, 0.02, px.x), strokeAA(d.y, 0.02, px.y));
    vec3 ground = mix(hex(0x1a0b2e), hex(0x2b0f45), z / hz);
    col = mix(ground, hex(0xff2a6d), line * smoothstep(0.0, 0.08, z));   // lines fade into the horizon haze
    col += hex(0xff2a6d) * 0.25 * exp(-z * 30.0);                          // horizon glow
  } else {
    // sky: cosine palette from magenta at the horizon to deep purple above
    float k = (uv.y - hz) / (1.0 - hz);
    col = palette(0.55 + 0.35 * k, vec3(0.45, 0.1, 0.45), vec3(0.45, 0.1, 0.35), vec3(1.0), vec3(0.0, 0.1, 0.2));
    col = mix(col, hex(0x1a0b2e), smoothstep(0.1, 1.0, k));
    // sun: disc with horizontal cut bands below its centre (bands drift down slowly)
    vec2 sc = vec2(0.5 * aspect, hz + 0.2);
    vec2 p = vec2(uv.x * aspect, uv.y);
    float px = 1.0 / iResolution.y;
    float disc = fillAA(sdCircle(p - sc, 0.2), px);
    float below = step(uv.y, sc.y);
    float bands = smoothstep(0.45, 0.55, fract(uv.y * 30.0 + iTime * 0.5));   // recipe: step(.5, fract(uv.y*30.)) — AA'd here
    disc *= 1.0 - below * (1.0 - bands) * smoothstep(sc.y, sc.y - 0.2, uv.y) * 1.0;
    vec3 sun = mix(hex(0xffd319), hex(0xff2a6d), smoothstep(sc.y + 0.2, sc.y - 0.2, uv.y));
    col = mix(col, sun, disc);
  }
  col += (hash12(fragCoord + floor(iTime * 24.0) * 31.7) - 0.5) * 0.03;
  fragColor = vec4(col, 1.0);
}
