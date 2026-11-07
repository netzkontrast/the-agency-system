# Style: Pixel art film

Chunky 16-bit-era pixel cinema: a hard pixel grid, small hand-set palettes, ordered dithering for every gradient, sprite characters that snap between poses. References: a pixel film that spread widely, "Pokémon Claude Red", and IN-HOUSE: our own 60 s one-prompt pixel film (216x216 logical canvas, 5x blocks to 1080; source in film.html). The engine notes below are lifted from that working film, not theory.

## Why this style exists in our gallery

Pixel art is the second "imperfection is the aesthetic" bet after crayon: the grid forgives everything the code can't do. A character is 20 pixels tall, so anatomy is impossible and therefore never wrong; emotion is one eye pixel and a lean. It reads instantly as a deliberate medium (people name it in one frame), it compresses beautifully for feed video, and it carries built-in nostalgia for exactly the X/LinkedIn audience. The one law: the grid must be HARD. A single anti-aliased edge, blurred upscale, or sub-pixel slide breaks the spell and the whole frame reads as "cheap filter" instead of "crafted game".

## Design system

- **Grid:** one fixed logical resolution for the whole film — 320x180 for 16:9 (or 216x216 square like the in-house film), upscaled by an integer factor (4x → 1280x720) with nearest-neighbor. Every mark is a whole logical pixel. Nothing ever lands on a half pixel.
- **Palette:** small and owned per scene: 8-16 colors, built as ramps (4-7 steps from shadow to light per material), declared as a table at the top of the file. Hue-shift the ramps (shadows lean blue/purple, lights lean warm), never just darken. A scene change is first a palette change.
- **Gradients = ordered dithering:** skies, glows, water depth, vignettes — all Bayer-dithered between adjacent ramp steps. No smooth gradients anywhere, no alpha soup. A dawn sky is 5-8 dithered bands, and the dither checker itself is part of the look.
- **Characters:** sprites, 16-32 px tall, designed as pixel maps (string grids) with a palette key, not drawn with math curves. Silhouette first: the character must read as a black shape. Emotion via 1-2 px changes (eye, brow tilt, lean) — see the in-house film's ticket character, which acts a whole film with an outline, one eye and posture.
- **Motion:** animation on ticks. Sprites snap between 2-4 discrete frames (bob = 2 frames, walk = 4) at 6-12 fps steps while the world can pan at full fps. Positions are rounded to the grid every frame. NEVER tween a sprite between poses and never let it slide sub-pixel — pixel characters snap, that snap is the charm.
- **Depth:** parallax layers (far sky / mid silhouettes / playfield / near foreground), each scrolling at its own speed, each with its own slice of the palette (far = fewer, desaturated colors). 3-4 layers reads as a world.
- **Light:** light is palette, not glow. A lamp = the nearby pixels promoted 1-2 ramp steps + a dithered halo. Sparkle = single bright pixels blinking on ticks.
- **CRT grade (optional, OFF by default):** subtle scanlines + slight bloom, applied after upscale, only if the film's fiction is "footage from an old machine". Ticket-film shipped without it and looked crafted, not retro-decorated; random scanlines are the #1 tell of generic retro.
- **Type:** your own bitmap font (5x7-ish glyphs as bitmask rows, see engine notes), drawn on the logical grid and scaled with the frame. Never a vector font over pixel art.

## Variants worth naming when pitching

- **Lofi loop:** one seamless ambient scene (rainy window, night desk), tiny palette, 2-4 s perfect loop; the lo-fi-girl economy. Lowest effort, high mood.
- **16-bit RPG:** top-down or side-view adventure grammar — dialog boxes, map transitions, battle screens; great for "X as a video game" explainers (Pokémon Claude Red energy).
- **HD-2D:** pixel sprites + modern lighting (soft shadows, depth-of-field on the far layer, particle light) — the Octopath look. The sprites stay hard-grid; only light gets to be soft, and dithered where possible.
- **Demoscene:** the effects themselves are the star — plasma, rotozoom, starfields, sine-scrolling text — a flex reel for "drawn by code" posts.

## Story grammar (from the in-house pixel film, our proof)

1. Side-scroll as spine: the camera travels one continuous world; rooms/chapters are met left to right, so the film feels like a journey, not cuts.
2. Cut on the beat: lock scene changes to bar lines (in-house film: 120 BPM, one bar = 2 s) so music drops in later without editing.
3. Scale beats: the tiny sprite against an enormous machine/wave/door — smallness is the emotion pixel art does best.
4. Save camera moves: mostly steady scroll, then one pull-back and one push-in that count.
5. Loop the ending to the opening frame when possible; feed video rewards seamless loops.

## Engine notes

- **Canvas pair:** an offscreen logical canvas (`lo.width=320, lo.height=180`), draw EVERYTHING there in whole pixels, then blit: `G.imageSmoothingEnabled=false; G.drawImage(lo,0,0,1280,720)`. Set `image-rendering: pixelated` on the visible canvas as CSS backup. Re-assert `imageSmoothingEnabled` every blit (some contexts reset it on resize).
- **Camera variant (in-house film):** for zooms, draw in world units through a snapped camera: `sx=x=>(x-CX)*Z+HW`, and every rect rounds BOTH corners to the logical grid (`Math.round(sx(x))..Math.round(sx(x+w))`, min 1 px). Zoom Z changes apparent pixel size but everything stays on-grid — this is how you get camera moves without sub-pixel mush.
- **Palette tables:** named ramps as consts, e.g. the in-house film's brass `B0 #24160a → B6 #fff1c8` and navy `N0 #060916 → N6 #3f5596`, plus per-character 5-key palettes `{o,b,s,d,i}` (outline, base, shade, dark, ink) so a character re-lights by swapping the table, and a `mixHex`-based `palDim(p,k)` (quantize k, cache results) for distance/dusk dimming.
- **Bayer thresholds:** `B4=[[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]`, threshold `(B4[y&3][x&3]+0.5)/16`; the 8x8 matrix (recursive: `B8[y][x]=4*B4[y&3][x&3]+B4[y>>2&3][x>>2&3]`, /64) for wider, calmer bands like big skies. Per pixel of a gradient: compute float ramp position `f`, `i=floor(f)`, color = `ramp[f - i > bayer(x,y) ? i+1 : i]`. Index by SCREEN-logical x,y so the checker stays still while things move behind it (or by world coords if the dither should travel with a surface — pick one per layer, deliberately).
- **Per-scene palettes:** each scene owns its ramps; a mood shift = swap the table, ideally on a bar line. Don't blend two scenes' palettes — hard-cut or dither-wipe between them.
- **Sprites:** string-grid maps, one char per pixel keyed to the palette; a draw function walks the grid with `fillRect(x+i, y+j, 1, 1)`. Mirror by iterating columns backwards for facing. Cache `fillStyle` (only set when the color changes — the in-house film's `fs(k)`) or the frame gets slow.
- **Ticks not tweens:** `frame = floor(t*fps_anim) % nFrames` with `fps_anim` 6-12 for sprite cycles; world motion may use full-fps floats but is rounded to ints at draw time. A bob is `y + (tick%2)` and maybe a 1 px nose tilt — two drawn frames, zero interpolation.
- **Bitmap font:** glyphs as arrays of row bitmasks (5 wide: `row & (16>>bit)`), per-char advance table for narrow glyphs, draw at integer scale only (2x, 3x). Keep the FONT and ADV tables beside the draw function.
- **Determinism:** seeded integer hash (the in-house film's `hash(a,b)` imul mixer) for stars, dust, foam, blink timing; every frame a pure function of t (`window.renderFrame(t)`), so export is frame-exact.
- **Cheap ellipse/ring/line:** scanline ellipses (per-row `fillRect`), point-stepped lines of 1 px rects — never `arc()`/`stroke()`, which anti-alias.
- **Crispness audit (mandatory):** zoom into an exported frame; every edge must be a staircase of identical blocks. Blur means smoothing got re-enabled, a shape used canvas curves, or something drew at non-integer coords.

**Best for:** software/process satire and dev-audience stories (proven in-house), "X as a retro game", journeys and scale gags, lofi mood loops, model-launch demos where "every pixel drawn in code" is the flex. Choose it when characters must act a lot on a small budget of pixels, or when the audience should feel the game era in one frame.
