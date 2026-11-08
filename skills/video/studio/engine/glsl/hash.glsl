// hash.glsl — deterministic hashes (GLSL ES 3.00). PCG hash after Jarzynski & Olano, "Hash Functions for GPU
// Rendering" (JCGT 2020); this implementation is the studio's own (MIT).
uint pcg(uint v) { uint s = v * 747796405u + 2891336453u; uint w = ((s >> ((s >> 28u) + 4u)) ^ s) * 277803737u; return (w >> 22u) ^ w; }
uvec2 pcg2(uvec2 v) { v = v * 1664525u + 1013904223u; v.x += v.y * 1664525u; v.y += v.x * 1664525u; v ^= v >> 16u; v.x += v.y * 1664525u; v.y += v.x * 1664525u; v ^= v >> 16u; return v; }
float hash11(float p) { return float(pcg(floatBitsToUint(p))) / 4294967295.0; }
float hash12(vec2 p) { return float(pcg(pcg(floatBitsToUint(p.x)) + floatBitsToUint(p.y))) / 4294967295.0; }
vec2 hash22(vec2 p) { return vec2(pcg2(floatBitsToUint(p))) / 4294967295.0; }
float hash13(vec3 p) { return float(pcg(pcg(pcg(floatBitsToUint(p.x)) + floatBitsToUint(p.y)) + floatBitsToUint(p.z))) / 4294967295.0; }
