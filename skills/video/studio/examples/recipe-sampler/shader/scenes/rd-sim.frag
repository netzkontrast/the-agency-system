// rd-sim.frag — recipe 42: one Gray-Scott step on RG (R = A, G = B), Da 1, Db .5, f .055, k .062, dt 1.
// iChannel0 = own previous frame (unused), iChannel1 = the previous substep. Seeds when the read is zero.
#include "engine/glsl/hash.glsl"
vec2 S(vec2 fc) { return texture(iChannel1, fc / iResolution.xy).rg; }
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
  vec2 c = S(fragCoord);
  if (c.r == 0.0 && c.g == 0.0) {
    // seed: A = 1 everywhere, B in a few hashed blobs (deterministic)
    float b = 0.0;
    for (int i = 0; i < 14; i++) {
      vec2 ctr = hash22(vec2(float(i), 7.0)) * iResolution.xy;
      b = max(b, step(length(fragCoord - ctr), 6.0 + 6.0 * hash11(float(i) + 0.5)));
    }
    fragColor = vec4(1.0, b, 0.0, 1.0); return;
  }
  // 3x3 Laplacian (centre -1, edges .2, corners .05)
  vec2 lap = -c
    + 0.2 * (S(fragCoord + vec2(1, 0)) + S(fragCoord - vec2(1, 0)) + S(fragCoord + vec2(0, 1)) + S(fragCoord - vec2(0, 1)))
    + 0.05 * (S(fragCoord + vec2(1, 1)) + S(fragCoord + vec2(-1, 1)) + S(fragCoord + vec2(1, -1)) + S(fragCoord + vec2(-1, -1)));
  float A = c.r, B = c.g, f = 0.055, k = 0.062;
  float abb = A * B * B;
  A += (1.0 * lap.r - abb + f * (1.0 - A));
  B += (0.5 * lap.g + abb - (k + f) * B);
  fragColor = vec4(clamp(A, 1e-4, 1.0), clamp(B, 0.0, 1.0), 0.0, 1.0);   // A never exactly 0: zero means "unseeded"
}
