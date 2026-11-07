# Style: Broadcast title sequence

A beat-locked, typography-led motion reel, like the opening titles of a sports season or a festival. Pure code. Reference: "Motion designers are cooked lol I just made this with Opus 5.5 in Claude Code in just 15 minutes" (Sep 2026): "THE FRONTIER · Season 2026", three AI labs presented as contenders, 26 s, 60 fps, 150 BPM.

## Structure

A title card → one chapter per subject (2-4 subjects, 4-6 s each) → all subjects together → the title again. Great for comparisons, lineups, a product's pillars, a team, a season, a launch with several features.

## Design system

- **One color world per chapter**, hard-cut between them, each with a single accent: e.g. black + neon green, electric blue + white, warm paper cream + orange. The contrast between worlds is the energy.
- **Type is the hero:** a very heavy wide sans (Archivo Black / Druk Wide / Anton style) filling the frame; one italic serif accent per title ("GEMINI *3m*", "FABLE *5.1*"); outlined (stroke-only) versions of the same word scrolling as a marquee behind it.
- **Signature type effects:** split-flap letters flipping into place (20 flips/s, locking on the beat), letter-spaced reveals, glitch slices on cuts, a word stretched vertically in a column for the lineup shot.
- **A HUD frame** that makes it feel engineered: corner brackets, mono meta top-left/right (`THE FRONTIER  SEASON 2026`, `03 — FABLE 5.1`), a running timecode + fps bottom-left, `150 BPM ▢■▢▢ BAR 09/16` bottom-right, and a small technical caption under each effect (`SPLIT-FLAP × 5 · 20 FLIPS/S · LOCK ON THE 1/16`).
- **One signature visual per chapter**, tied to the subject: a particle globe around a logo, a warp tunnel, a DNA-like ribbon of dots, a book whose pages turn. Built in code (canvas or WebGL), simple geometry, strong motion.
- **Texture:** fine film grain on everything, subtle vignette on dark worlds, paper texture on the light one.

## Rhythm

Set a BPM (140-160 feels right) and land every cut, flap lock and slam on beats or 1/16ths. Bars of 1.5-1.7 s. The end sequence slows down: the finale holds.

## Engine

Canvas 2D (WebGL for particles/tunnel if needed) via `scripts/new-canvas-project.sh`. Load display fonts from Google Fonts and wait for `document.fonts.ready`. If the user has a music track, measure its BPM first and drive the whole timeline from it.

## Logos and names

Real company or product logos and names belong only to the user's own brands or clearly editorial/fan use; ask before putting third-party marks at the center of a piece.
