# Video domain — ported engines

Three external repos, ported into the plugin as the basis of the **video domain** planned in
[`Plan/140-video-domain/spec.md`](../../Plan/140-video-domain/spec.md). Each folder is the
upstream repo at the commit below, unchanged, so its own relative paths keep working.
`.git` and upstream CI (`.github/`) are not ported; everything else is.

| Folder | Upstream | Commit | Licence | Layer | Entry point |
|---|---|---|---|---|---|
| `take-one/` | [netzkontrast/take-one](https://github.com/netzkontrast/take-one) | `830621cce11127a30120d7878570eb8acaaa5bad` | MIT (`LICENSE`); files adapted from anidoodle stay Apache-2.0 (`THIRD_PARTY.md`, `LICENSES/`); the Take One name and logo are not licensed | process & quality: studio jobs, song → music video, critic, fresh reviewer, review room, gate / text / audio audits | `take-one/SKILL.md` |
| `claude-animation-base/` | [netzkontrast/ClaudeAnimationBase](https://github.com/netzkontrast/ClaudeAnimationBase) | `0ac8bf2b31942376cb6b8c4074715595d512acd2` | MIT (`LICENSE`) | medium: painted 2D with p5.js + p5.brush, `render.mjs`, `studio.html` | `claude-animation-base/SKILL.md` (added on port) → `ANIMATION_GUIDE.md` |
| `higgsfield-video-engineer/` | [netzkontrast/higgsfield-video-engineer](https://github.com/netzkontrast/higgsfield-video-engineer) | `082bfd7b7b0b863799fa9afcdfeb3e84ba72e015` | MIT (`LICENSE`); engine credits in `skills/code-based-films/engine/NOTICE.md`; example font under OFL | bar map (`tools/beatmap.py`); optional WebGPU path tracer for stills | `higgsfield-video-engineer/skills/code-based-films/SKILL.md` |

The only file added on top of the upstream trees is `claude-animation-base/SKILL.md`
(ClaudeAnimationBase ships no skill file).

## How they fit together

```
take-one                 drives the work: pitch, song map, storyboard, critic, test section,
                         chaptered build, gate, fresh reviewer, review room, delivery
  └─ claude-animation-base   draws every frame (ink, charcoal, watercolour, paper)
  └─ higgsfield beatmap.py   bars, sections, drop → timing of cuts and hits
the-agency-system        album DNA (skills/theagencysystem/), track state, hard gates
```

For an Agency System album: load `skills/theagencysystem/` first, then read the album's
`VIDEO-CONCEPT.md` (for example
`artists/the-agency-system/albums/dystopian-future-synth/lass-mich-lass-mich-atmen/VIDEO-CONCEPT.md`).
It overrides the engines' defaults where it says so.

## Updating from upstream

Re-run the port for one repo, then review the diff:

```bash
rm -rf skills/video/<folder> && mkdir -p skills/video/<folder>
git -C <clone of upstream> archive HEAD | tar -x -C skills/video/<folder>
# claude-animation-base: keep our SKILL.md; higgsfield: drop .github/
```

Update the commit column above in the same change.
