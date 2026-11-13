// raymarch.frag — recipe 44: inline 3D SDFs, 96 steps, eps .001, central-difference normals, soft shadows,
// smin() from sdf.glsl, fog mix(col, fogCol, 1 - exp(-.02 d²)), look-at camera from iTime, palette() + toSRGB once.
#include "engine/glsl/sdf.glsl"
#include "engine/glsl/color.glsl"
float sdSphere(vec3 p, float r) { return length(p) - r; }
float sdBox3(vec3 p, vec3 b) { vec3 q = abs(p) - b; return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0); }
float sdTorus(vec3 p, vec2 t) { vec2 q = vec2(length(p.xz) - t.x, p.y); return length(q) - t.y; }
vec2 map(vec3 p) {   // x = distance, y = material
  float k = 0.3 + 0.25 * iPulse;                                  // morph: smin k on the pulse
  float blob = smin(sdSphere(p - vec3(0.0, 1.0 + 0.2 * sin(iTime), 0.0), 0.7), sdTorus(p - vec3(0.0, 0.7, 0.0), vec2(1.1, 0.22)), k);
  vec3 bp = p - vec3(1.9, 0.5, -0.6); bp.xz = rot2(iTime * 0.4) * bp.xz;
  float box = sdBox3(bp, vec3(0.45)) - 0.05;
  float ground = p.y;
  vec2 r = vec2(ground, 0.0);
  if (blob < r.x) r = vec2(blob, 1.0);
  if (box < r.x) r = vec2(box, 2.0);
  return r;
}
vec3 normalAt(vec3 p) {
  vec2 e = vec2(0.001, 0.0);
  return normalize(vec3(map(p + e.xyy).x - map(p - e.xyy).x, map(p + e.yxy).x - map(p - e.yxy).x, map(p + e.yyx).x - map(p - e.yyx).x));
}
float softShadow(vec3 ro, vec3 rd, float k) {   // penumbra from the closest miss along the shadow ray
  float res = 1.0, t = 0.02;
  for (int i = 0; i < 48; i++) {
    float h = map(ro + rd * t).x;
    if (h < 0.001) return 0.0;
    res = min(res, k * h / t);
    t += clamp(h, 0.02, 0.3);
    if (t > 12.0) break;
  }
  return clamp(res, 0.0, 1.0);
}
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
  vec2 uv = (fragCoord - 0.5 * iResolution.xy) / iResolution.y;
  float a = 0.6 + iTime * 0.2;                                   // closed-form camera orbit
  vec3 ro = vec3(sin(a) * 6.0, 2.4 + 0.3 * sin(iTime * 0.3), cos(a) * 6.0), ta = vec3(0.0, 0.8, 0.0);
  vec3 ww = normalize(ta - ro), uu = normalize(cross(ww, vec3(0, 1, 0))), vv = cross(uu, ww);
  vec3 rd = normalize(uv.x * uu + uv.y * vv + 1.8 * ww);
  float t = 0.0; vec2 h = vec2(1.0, -1.0);
  for (int i = 0; i < 96; i++) { h = map(ro + rd * t); if (h.x < 0.001 || t > 40.0) break; t += h.x; }
  vec3 fogCol = vec3(0.62, 0.66, 0.78);
  vec3 col = fogCol;
  if (t < 40.0) {
    vec3 p = ro + rd * t, n = normalAt(p), L = normalize(vec3(0.6, 0.8, 0.4));
    vec3 alb = h.y < 0.5 ? vec3(0.5 + 0.1 * mod(floor(p.x) + floor(p.z), 2.0))
             : palette(h.y * 0.3 + 0.1 * iTime, vec3(0.5), vec3(0.5), vec3(1.0), vec3(0.0, 0.33, 0.67));
    float dif = max(dot(n, L), 0.0) * softShadow(p + n * 0.002, L, 10.0);
    float sky = 0.5 + 0.5 * n.y;
    col = alb * (1.6 * dif * vec3(1.0, 0.95, 0.85) + 0.35 * sky * vec3(0.6, 0.7, 1.0));
    col = mix(col, fogCol, 1.0 - exp(-0.02 * t * t * 0.1));
  }
  fragColor = vec4(toSRGB(clamp(col, 0.0, 1.0)), 1.0);
}
