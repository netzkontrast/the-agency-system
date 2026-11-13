// rd-show.frag — maps B through palette() over paper.
#include "engine/glsl/color.glsl"
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
  float B = texture(iChannel0, fragCoord / iResolution.xy).g;
  vec3 ink = palette(0.6 + B * 0.8, vec3(0.5), vec3(0.5), vec3(1.0), vec3(0.0, 0.33, 0.67));
  vec3 col = mix(vec3(0.95, 0.92, 0.86), ink * 0.85, smoothstep(0.08, 0.3, B));
  fragColor = vec4(col, 1.0);
}
