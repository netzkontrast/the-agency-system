# Canonical Novel On-Disk Layout

This specification dictates the directory structure and naming conventions for all novel projects managed by the Agency System. This structure mirrors the `artists/` structure used for music.

## Slug Rules

All identifiers used in directory and file names must conform to the following slug rules:
- Format: `kebab-case`
- Character Set: ASCII letters, numbers, and hyphens (`[a-z0-9-]+`)
- Length: Maximum 64 characters
- Collision Resolution: If a slug already exists, append an incremental counter (e.g., `-2`, `-3`).

## Directory Shape

The root path for all novels is `novels/` at the repository root.

The canonical shape for a specific work is:
`novels/{author-slug}/works/{genre-slug}/{work-slug}/`

### Required Subfolders
Every work folder must contain the following subdirectories:
- `chapters/` — For individual chapter files.
- `scenes/` — For individual scene files.
- `characters/` — For individual character files.
- `world/` — For world-building element files.
- `revisions/` — For keeping track of previous drafts and revisions.
- `art/` — For related artwork and imagery.
- `research/` — For background research notes.

### Required Files per Work
The root of every work folder must contain exactly these 7 files:
1. `work.md` — Top-level work descriptor.
2. `premise.md` — Premise, logline, and central question.
3. `cast.md` — Roster of player slots with throughline assignments.
4. `dramatica.md` — Storyform notes.
5. `outline.md` — Work-level outline.
6. `ncp.json` — NCP structure document.
7. `README.md` — Map of the folder for humans/agents.

## Template Placeholders

When scaffolding a new work, the `templates/novel/` files are used. They contain the following placeholders which handlers must substitute:
- `{{author_slug}}` — Slug of the author.
- `{{work_slug}}` — Slug of the work.
- `{{genre_slug}}` — Slug of the genre.
- `{{work_title}}` — Human-readable title of the work.
- `{{premise_logline}}` — A short logline describing the premise.
- `{{created}}` — The ISO 8601 creation date.

## External References (Cite-don't-copy)

For the historical bootstrapping and integration context of novel generation, refer to the legacy vendor repository. Do not copy these files into the plugin; use the references below:

- Bootstrap phases: `agency/skills/novel-architect/phases/phase0-bootstrap.md` (Commit SHA: 867453e49065e16b9298b960a22fd34746985572)
- NCP Integration Contract: `agency/skills/novel-architect/references/ncp-integration-contract.md` (Commit SHA: 867453e49065e16b9298b960a22fd34746985572)
