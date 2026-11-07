# Video domain

One suite: **[`studio/`](studio/SKILL.md) — Video Studio** (skill `video-studio`). It plans, builds, reviews and
delivers code-based videos: every frame is a pure function of time, drawn in a web page (painted 2D with p5.brush, or
a plain canvas) or by a WebGPU path tracer, timed to a measured song or voice map, made by a team of subagents through
hard gates.

| Start here | |
|---|---|
| [`studio/SKILL.md`](studio/SKILL.md) | the pipeline (phases 0–11), the team and fan-out rules, hard rules |
| [`studio/playbooks/`](studio/playbooks/README.md) | 13 project types: music video, album suite, lyric video, visualizer/loop, explainer, product launch, brand/title, animated short, documentary, data story, social vertical, teaser/cut-down, path-traced short |
| [`studio/agents/`](studio/agents/README.md) | 12 subagent briefs, ready to paste |
| [`studio/references/film-contract.md`](studio/references/film-contract.md) | the one contract every medium and tool shares |
| `bash studio/bin/studio help` | the CLI: doctor, new, render, gate, songmap, srt, flash, loudness, pack, review … |

## Where it came from

Video Studio replaces the three repos that were first ported here unchanged (take-one, ClaudeAnimationBase,
higgsfield-video-engineer) and combines them: take-one's process and QA, ClaudeAnimationBase's paint medium,
higgsfield's path tracer and bar map — plus a shared film contract, one renderer (`tools/render.mjs`), one browser
launcher, a song map for any medium (`engine/lib/beat.js`), forced lyric alignment, subtitles, a flash gate and
stepped-art support in the gate. Commits and licences: [`studio/THIRD_PARTY.md`](studio/THIRD_PARTY.md) and
`studio/LICENSES/`. Tools from other projects that were evaluated: `studio/references/research-2026-11.md`.

## Setup

```bash
bash skills/video/studio/bin/studio doctor     # installs the studio's Node packages, reports what else is missing
```

`studio/node_modules/` is not committed. npm packages may ship their own `SKILL.md` files; the plugin's skill listing
ignores anything under `node_modules/`.
