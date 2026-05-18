# Research Briefs (Jules dispatch artefacts)

Each `NN-<slug>.md` in this folder is the verbatim prompt body of a Jules research session that was dispatched via `jules-plugin/bin/jules-bulk fanout`. The brief lives in the repo so the dispatch is auditable, reproducible, and supersession-safe (edit only by adding a new brief that references the prior one).

## Convention

- Frontmatter declares: `type: research-brief`, `status: dispatched|superseded`, `dispatched_to: jules`, `dispatched_at`, `parent_specs`, `output_branch`, `output_files`.
- Body is the literal prompt sent to Jules. Includes goal, required reading, source-clone commands, output paths, acceptance criteria, and anti-patterns.
- Research output lands on the declared `output_branch` (Jules's own branch off `Master`) — never on the brief's host branch.
- Findings + draft specs land under `Plan/_research/<slug>/` so they do not collide with numbered Plan specs until promoted.

## Dispatch log

| # | Slug | Dispatched | Session ID | Status | Output |
|---|---|---|---|---|---|
| 01 | centralized-ontology | 2026-05-18 | (see `fanout-log.txt`) | dispatched | `Plan/_research/centralized-ontology/` |
| 02 | agency-tooling-codemode | 2026-05-18 | (see `fanout-log.txt`) | dispatched | `Plan/_research/agency-tooling-codemode/` |

## How to fan out a new brief

1. Author the brief in this folder following the existing template.
2. Append to `fanout.json` (or generate a fresh fanout file from the briefs via `tools/jules/build-fanout.py` if/when that lands).
3. Run from repo root: `CLAUDE_PLUGIN_ROOT=$(pwd)/jules-plugin ./jules-plugin/bin/jules-bulk fanout Plan/_research-briefs/fanout.json`
4. Capture session IDs into `fanout-log.txt`.
5. Update the dispatch log table above.

## Supersession rule

Never edit a brief in place once dispatched. To revise: add `NN+1-<slug>.md` with frontmatter `supersedes: NN-<slug>.md` and flip the prior brief's status to `superseded`.
