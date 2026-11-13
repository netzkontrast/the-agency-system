// dither.frag — recipe 31 (shader): ditherLevels(vec3(luma(c)), floor(fragCoord / 2.), 2.), mapped to paper / ink.
#include "engine/glsl/color.glsl"
#include "engine/glsl/dither.glsl"
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
  vec3 c = texture(iChannel0, fragCoord / iResolution.xy).rgb;
  vec3 col = ditherLevels(vec3(luma(c)), floor(fragCoord / 2.0), 2.0);
  fragColor = vec4(mix(hex(0x1a1a1a), hex(0xf2efe6), clamp(col.r, 0.0, 1.0)), 1.0);
}
