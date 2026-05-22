# SPECD Prompt Formula — Cross-Cutting

Every image prompt splits into **exactly five blocks separated by `::`**. This
forces clean weight distribution and minimizes concept-bleeding.

```
<Subject> :: <State> :: <Environment / Camera> :: <Style / Lighting> :: <Parameters & negatives>
```

## Slots

| Slot | Holds | Examples |
|---|---|---|
| **Subject** | One core semiotic symbol or data-encoded entity | `jagged deep black data fissure`, `mechanical surveillance lens`, `faceless humanoid silhouette of dense wireframes` |
| **State** | The tier (T0–T4) + state modifiers; the emotional truth | `Tier 2 state, paranoid atmosphere, executing hostile intrusion detection` |
| **Environment / Camera** | Vacuum, scale, lens, framing, angle | `vast empty black void`, `shot on 14mm CCTV`, `shot on 100mm macro, severe dutch angle` |
| **Style / Lighting** | The fixed clinical anchor (every prompt) + glitch + light | `interface brutalism, clinical dystopian aesthetic, high-contrast dark mode, sharp chromatic aberration, deep raytraced black shadows` |
| **Parameters & negatives** | `--no` ban list, aspect, `--style raw`, `--s`, `--v`, `--sref` | `--no 1980s retro, synthwave, daylight, soft lighting, analog texture --ar 16:9 --style raw --s 75 --v 7.0` |

Use **function/role** language in the subject, never an alter's personal name.

## Worked examples (FUNCTION/ROLE language)

**Protector function, Tier 2 (alert / defensive vigilance):**
```
mechanical surveillance lens emerging from shadows, cold glass sensor reflection :: Tier 2 state, hypervigilant protector posture, executing hostile intrusion detection :: claustrophobic close-up, aggressive asymmetrical tension, severe dutch angle :: interface brutalism, clinical dystopian aesthetic, sharp chromatic aberration on edges, hostile neon signal yellow warning lights, deep raytraced black shadows :: --no 1980s retro, synthwave, daylight, soft lighting, analog texture --ar 16:9 --style raw --s 75 --v 7.0
```

**Integrator function, Tier 4 (safe mode / repair):**
```
geometric breaks in a dark surface joined by glowing golden PCB circuit lines :: Tier 4 state, integrator resynthesis, exhausted clarity after collapse :: static calm composition, restrained distance, vast negative space :: interface brutalism, digital kintsugi repair aesthetic, desaturated washed-out concrete greys, single tiny Kintsugi Gold #FFDF00 repair seam, cold quiet atmosphere :: --no 1980s retro, synthwave, daylight, organic curves, visible paper texture --ar 1:1 --style raw --s 60 --v 7.0
```
