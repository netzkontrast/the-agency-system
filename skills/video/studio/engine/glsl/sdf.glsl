// sdf.glsl — 2D signed distance functions and operators. Studio's own (MIT), except smin(): the polynomial smooth
// minimum from Inigo Quilez, iquilezles.org/articles/smin (his article code snippets are MIT-licensed).
float sdCircle(vec2 p, float r) { return length(p) - r; }
float sdBox(vec2 p, vec2 b) { vec2 d = abs(p) - b; return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0); }
float sdRoundBox(vec2 p, vec2 b, float r) { return sdBox(p, b - r) - r; }
float sdSegment(vec2 p, vec2 a, vec2 b) { vec2 pa = p - a, ba = b - a; float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0); return length(pa - ba * h); }
float sdRing(vec2 p, float r, float w) { return abs(length(p) - r) - w; }
float smin(float a, float b, float k) { float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0); return mix(b, a, h) - k * h * (1.0 - h); }
float opOnion(float d, float w) { return abs(d) - w; }
mat2 rot2(float a) { float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }
// anti-aliased fill and stroke from a distance (px = one pixel in the units of d)
float fillAA(float d, float px) { return clamp(0.5 - d / px, 0.0, 1.0); }
float strokeAA(float d, float w, float px) { return clamp(0.5 - (abs(d) - w) / px, 0.0, 1.0); }
