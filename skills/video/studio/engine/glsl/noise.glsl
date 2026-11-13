// noise.glsl — value noise, 2D simplex noise and fBm.
// snoise(): "Array and textureless GLSL 2D simplex noise function", Ian McEwan, Ashima Arts / Stefan Gustavson,
// MIT License (https://github.com/ashima/webgl-noise, https://github.com/stegu/webgl-noise). Copyright (C) 2011 Ashima Arts.
// vnoise(), fbm2(), warp2() are the studio's own (MIT).
vec3 _mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec2 _mod289(vec2 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec3 _permute(vec3 x) { return _mod289(((x * 34.0) + 10.0) * x); }
float snoise(vec2 v) {
  const vec4 C = vec4(0.211324865405187, 0.366025403784439, -0.577350269189626, 0.024390243902439);
  vec2 i = floor(v + dot(v, C.yy));
  vec2 x0 = v - i + dot(i, C.xx);
  vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
  vec4 x12 = x0.xyxy + C.xxzz;
  x12.xy -= i1;
  i = _mod289(i);
  vec3 p = _permute(_permute(i.y + vec3(0.0, i1.y, 1.0)) + i.x + vec3(0.0, i1.x, 1.0));
  vec3 m = max(0.5 - vec3(dot(x0, x0), dot(x12.xy, x12.xy), dot(x12.zw, x12.zw)), 0.0);
  m = m * m; m = m * m;
  vec3 x = 2.0 * fract(p * C.www) - 1.0;
  vec3 h = abs(x) - 0.5;
  vec3 ox = floor(x + 0.5);
  vec3 a0 = x - ox;
  m *= 1.79284291400159 - 0.85373472095314 * (a0 * a0 + h * h);
  vec3 g;
  g.x = a0.x * x0.x + h.x * x0.y;
  g.yz = a0.yz * x12.xz + h.yz * x12.yw;
  return 130.0 * dot(m, g);
}
float vnoise(vec2 p) {
  vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
  float a = fract(sin(dot(i, vec2(127.1, 311.7))) * 43758.5453), b = fract(sin(dot(i + vec2(1, 0), vec2(127.1, 311.7))) * 43758.5453);
  float c = fract(sin(dot(i + vec2(0, 1), vec2(127.1, 311.7))) * 43758.5453), d = fract(sin(dot(i + vec2(1, 1), vec2(127.1, 311.7))) * 43758.5453);
  return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}
float fbm2(vec2 p) { float s = 0.0, a = 0.5; for (int i = 0; i < 6; i++) { s += a * snoise(p); p = p * 2.02 + 17.3; a *= 0.5; } return 0.5 + 0.5 * s; }
// domain warp: organic smoke, marble, ink in water
vec2 warp2(vec2 p, float t) { return p + vec2(fbm2(p + vec2(0.0, t)), fbm2(p + vec2(5.2, 1.3 - t))) - 0.5; }
