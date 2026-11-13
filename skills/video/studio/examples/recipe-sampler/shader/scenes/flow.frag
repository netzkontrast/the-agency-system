// flow.frag — recipe 41 as a shader: the angle field a = snoise(p * k, t * .05) * 2π, shown by integrating each
// pixel's streamline a few steps both ways through a static seeded speckle (a line-integral convolution): pure in t.
#include "engine/glsl/hash.glsl"
#include "engine/glsl/noise.glsl"
#include "engine/glsl/color.glsl"
vec2 field(vec2 p) {
  float a = snoise(p * 1.6 + vec2(0.0, iTime * 0.05)) * 6.28318;   // field evolves at 0.05 / s
  return vec2(cos(a), sin(a));
}
float speckle(vec2 p) { vec2 c = floor(p * 140.0); return step(0.82, hash12(c)); }
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
  vec2 p = (fragCoord - 0.5 * iResolution.xy) / iResolution.y;
  float acc = 0.0, w = 0.0;
  for (int dir = -1; dir <= 1; dir += 2) {
    vec2 q = p;
    for (int i = 0; i < 24; i++) {
      q += field(q) * 0.0045 * float(dir);
      float k = 1.0 - float(i) / 24.0;
      acc += speckle(q) * k; w += k;
    }
  }
  float v = acc / w;
  float age = 0.5 + 0.5 * snoise(p * 0.9 + 3.0);
  // ramp #0b132b → #5bc0be → #f5f5f5 along "age"
  vec3 ramp = age < 0.5 ? mix(hex(0x0b132b), hex(0x5bc0be), age * 2.0) : mix(hex(0x5bc0be), hex(0xf5f5f5), age * 2.0 - 1.0);
  vec3 col = mix(hex(0x0b132b), ramp, smoothstep(0.05, 0.45, v));
  fragColor = vec4(col, 1.0);
}
