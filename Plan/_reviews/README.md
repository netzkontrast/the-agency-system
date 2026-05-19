# Jules review sessions for PR #133

Three independent Jules sessions, each with its own folder. Briefs in
`Plan/_jules-briefs/dispatch.yaml`. Dispatched via `bin/jules-bulk fanout`.

| Session | Folder | Stance | Quarantine |
|---|---|---|---|
| A | `session-A-critical/` | Critical review with evidence | Reads PR; writes review only |
| B | `session-B-improvements/` | Improvement ideas, leaner / more isomorphic | Reads PR; writes ideas only |
| C | `session-C-from-scratch/` | Independent design, triad floor, 12 Gherkin scenarios | **Does NOT read** PR design/ADRs/prototypes |

The three folders are merge-clean — no overlapping writes.
