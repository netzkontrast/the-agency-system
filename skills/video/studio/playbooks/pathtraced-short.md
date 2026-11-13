# Playbook: Path-traced short

**Use when** the film needs physically lit 3D made entirely in code: felt, paper, clay, yarn, glass, metal, smoke,
real shadows and depth of field; a 15–30 s short or a set of stills; a hero shot inside another film. **Not when**
the piece is longer than ~60 s or a full song (per-frame cost is too high: `music-video.md` in paint), the look is
flat 2D or type (`explainer.md`, `brand-title.md`), or there is no GPU machine for the final render.

## Inputs to collect

- Story or brief; the world's material (the twist should be only possible in it: yarn that holds up the sun).
- Music: own or generated track with rights, or a code score (`tools/music.mjs`); the window the film uses.
- Render machine: GPU model (adapter name), VRAM, laptop or desktop, hours available; remote GPUs only with the
  person's yes and price (`references/pathtracer/rendering.md`, optional remote).
- Reference sequences for the bar (2–3), and whether generated styleframes/turnarounds may be made as targets (price).
- Delivery size and ratio (default 4:3 1440×1080).

## Defaults

| Item | Default |
|---|---|
| Length | 15–30 s (the example: 20 s, 480 frames) |
| Size / aspect | 1440×1080 (4:3) or as briefed; preview 640×480 or 720×540 |
| fps | 24 |
| Medium | pathtracer: `bash <studio>/tools/new-project.sh <dir> --medium pathtracer --duration 20` (copies `examples/felt-good-morning/`, links `engine-pt`); then `bash <studio>/engine/pathtracer/setup.sh` once and `node render_local.mjs --dry-run` in the project |
| spp | preview 32–64 (example preset 48, max 20 s/frame); look test at final; final 192–1024 (example 192, max 120 s/frame) |
| Encode | H.264 yuv420p CRF 16–18, AAC 48 kHz, −14 LUFS, ≤ −1 dBTP |

No style file applies directly; the look is set by `references/pathtracer/light-standard.md` and the styleframes.
Neighbours for 2D inserts: `references/styles/paper-cutout.md`, `animated-short.md`.

## Phase deltas

Route everything through `references/pathtracer/README.md` and `references/pathtracer/production-map.md`; this table
maps its phases onto the studio pipeline.

| # | Studio phase | Path-tracer phase |
|---|---|---|
| 0 | Intake | + GPU check: the CLI prints `adapter: {...}`; it must name the real (discrete) GPU, not a fallback. Estimate: frames × measured s/frame from the first preview frame (`render_local.mjs` prints it). |
| 2 | Route | research and bar frames (production-map §0). |
| 3 | Pitch | three loglines → one; hook in the first second (an event, not a mood), twist in the material, final image (§1). |
| 4 | Map | music first, then `python3 <studio>/tools/audio/beatmap.py` on the window; drop at ~45–60 % of runtime (§2). |
| 5 | Storyboard | `BEATS.md`: one row per shot with time, frame range, picture, lens, light, sound; named event frames (§3). Critic reads it. |
| A | Styleframes & turnarounds | generated **targets only** in `refs/`, never rendered, sampled or used as textures (§4). Gate: approved as target. |
| A | Assets in code | one module per asset (`references/pathtracer/asset-contract.md`), proof set + honest `GAPS.md` (§5). |
| 6 | Test section | **animatic under music** at preview settings (§6), gate: edit lock; then light & look pass, 2–3 frames per shot at final settings beside their styleframes (§8). |
| 7 | Build | final render in chunks, resumable: `node render_local.mjs --quality final --frames 0-119`, then the next range (§9). |
| 8 | Gates | the fixed gates in `references/pathtracer/qa.md` §5 (the page battery does not apply: there is no `film.html`). |
| 11 | Deliver | IP check (`references/pathtracer/ip-clean-delivery.md`); `node render_local.mjs --quality final --encode`. |

## Team & fan-out

Producer = lead (owns story, `BEATS.md`, `story.mjs` timing, the cut, acceptance), director, critic, art-director
(styleframes, light standard), **one agent per asset / simulation / shot polish** (`references/pathtracer/briefing-agents.md`),
qa-operator, reviewer, sound (synthesised SFX on events, mix). All agents share one GPU: **one render process at a
time**, jobs capped with `--max-seconds`; agents render into their own folders (`assets/<name>/proof/`, `out/test/<shot>/`).

## Craft rules specific to this type

1. **Our code only in the frame;** generated images are targets, never content.
2. **`sceneFor(i)` is a pure function of the frame index;** simulations pre-baked to per-frame caches; seeded RNG.
3. **Light has shape:** key + rim on every hero, real shadows and contact; exposure tuned per shot in the shot list
   (`references/pathtracer/light-standard.md`).
4. **Time is the music:** big events on downbeats, the drop carries the peak; music stops get one growing gesture.
5. Weight from curves: anticipation, `backOut` overshoot, `ring` follow-through; contacts solved from the contact.
6. Something moves in the first 0.5 s; static openers lose the hook.
7. A same-angle cut with a small scale change reads as a mistake: change angle and lens decisively or keep one shot.
8. Keep the cause of a gag in a medium shot.
9. Judge the animatic under music, not stills.
10. Finals at enough spp that the denoiser polishes rather than reconstructs; check a test chunk in motion for flicker.

## Gates & bar

- Animatic edit lock (hard), look pass side by side with styleframes (hard), `qa.md` §5 fixed gates, fresh-eyes
  review (§6), verdict ACCEPT / FIX / REBUILD with frame-numbered fixes.
- Studio checks that still apply on the encoded MP4: `bash <studio>/bin/studio flash out/<name>.mp4` (hard),
  `node <studio>/tools/audio-check.mjs out/<name>.mp4`, a contact sheet (`bash <studio>/tools/contact-sheet.sh`).
- **Reviewer locked items:** the material world, the approved styleframes, the music.
- **8/10 here:** test frames sit next to their styleframes with no visible step in quality; the story reads without
  words; the peak lands on the drop; no flicker in motion.

## Pitfalls

- Rendering finals in a GPU-less container (software adapter): hours per second of film.
- Two render jobs on one GPU; a laptop on battery; no `--max-seconds` cap.
- Re-rendering finished frames whose inputs did not change (render missing frames only).
- Copying the felt example's story, characters or set instead of its structure.
- Rented pods left running: record each in a ledger, delete when its part is done, confirm deletion.

## Deliverables

`out/<name>_final.mp4`, selected stills (PNG), `BEATS.md`, asset proof sets and `GAPS.md`, `review.md` (verdict,
gates, loudness, fresh-eyes score), IP checklist, render ledger if pods were used; temporary frame dumps deleted.

## Checklist

- [ ] GPU adapter verified; ETA from first frame told
- [ ] Logline + beat sheet on the bar map
- [ ] Styleframes approved as targets only
- [ ] Assets with proof sets and honest GAPS
- [ ] Animatic edit lock under music
- [ ] Look pass beside styleframes
- [ ] Final in chunks; QA §5 gates; flash + loudness
- [ ] IP check; temp images deleted
