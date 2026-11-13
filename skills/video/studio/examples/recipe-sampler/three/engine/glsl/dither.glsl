// dither.glsl — ordered dithering. Studio's own (MIT). For blue-noise dithering load a CC0 blue-noise texture
// (Christoph Peters, MomentsInGraphics/BlueNoise) as an iChannel and threshold against it.
float bayer2(vec2 p) { p = floor(mod(p, 2.0)); return (p.x * 2.0 + p.y * 3.0 - 4.0 * p.x * p.y) / 4.0; }
float bayer4(vec2 p) { return bayer2(p * 0.5) * 0.25 + bayer2(p); }
float bayer8(vec2 p) { return bayer4(p * 0.5) * 0.25 + bayer2(p); }
vec3 ditherLevels(vec3 c, vec2 fragCoord, float levels) { float t = bayer8(fragCoord) - 0.5; return floor(c * (levels - 1.0) + 0.5 + t) / (levels - 1.0); }
