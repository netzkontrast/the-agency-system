# Spec 005 — Music Skills Port: Old → New Slug Mapping

This table documents the 54 music skills ported verbatim from
`bitwize-music @ v0.91.0` into `skills/music/` for the unified
`agency-system` plugin.

- **old slug**: the original bitwize-music skill folder name. Slash form: `/bitwize-music:<old-slug>`.
- **new slug**: the ported folder name with the `music-` frontmatter
  prefix. Slash form: `/agency-system:music-<old-slug>`.
- **category**: one of `lifecycle` (setup, session, navigation), `drafting`
  (lyric/concept/voice work), `qc` (review/validation gates), `release`
  (mixing/mastering/distribution), `research` (researcher-* family + sources),
  `utility` (everything else: clipboard, rename, dashboards, art, promo).
- **trigger_phrases**: 1–2 representative invocation cues taken
  verbatim from the skill's frontmatter `description:` field.

Body bytes are byte-identical to vendor; only the YAML frontmatter
`name:` and `allowed-tools:` server reference were rewritten. See
`Plan/005-music-skills-port/spec.md` for porting discipline.

| old slug | new slug | category | trigger_phrases |
|---|---|---|---|
| about | music-about | lifecycle | "user asks about the plugin" / "purpose, version, or capabilities" |
| album-art-director | music-album-art-director | utility | "during planning for concept discussion" / "after all tracks are Final for actual artwork generation" |
| album-conceptualizer | music-album-conceptualizer | drafting | "planning a new album" / "reworking an existing album concept" |
| album-dashboard | music-album-dashboard | utility | "quick visual overview of album progress" / "structured progress dashboard" |
| album-ideas | music-album-ideas | utility | "add, review, or organize their album idea backlog" / "brainstorming, planning, and status updates" |
| clipboard | music-clipboard | utility | "paste lyrics or style prompts into Suno" / "copy track content (lyrics, style prompts, streaming lyrics)" |
| cloud-uploader | music-cloud-uploader | release | "host promo content for social media or distribution" / "Cloudflare R2 or AWS S3" |
| configure | music-configure | lifecycle | "first-time setup" / "config is missing, or when the user wants to change settings" |
| document-hunter | music-document-hunter | research | "court filings, government reports, or public records" / "research needs primary source documents" |
| explicit-checker | music-explicit-checker | qc | "before Suno generation or release" / "verifies that explicit flags match actual content" |
| genre-creator | music-genre-creator | utility | "user wants to add a genre" / "neues Genre erstellen / add genre" |
| health-check | music-health-check | lifecycle | "check plugin health" / "verify setup, or troubleshoot missing skills" |
| help | music-help | lifecycle | "user asks for help" / "what skills are available, or how to do something" |
| import-art | music-import-art | utility | "generated or downloaded album artwork that needs to be saved" / "places album art files in the correct audio and content directory locations" |
| import-audio | music-import-audio | release | "downloaded WAV files from Suno or other sources" / "moves audio files to the correct album location with proper path structure" |
| import-track | music-import-track | utility | "track files in Downloads or other locations that need to be placed in an album" / "moves track markdown files to the correct album location" |
| lyric-refiner | music-lyric-refiner | drafting | "after lyrics are written to polish a track or entire album" / "autonomous multi-pass lyric refinement" |
| lyric-reviewer | music-lyric-reviewer | qc | "before generating tracks" / "catch rhyme, prosody, pronunciation, and structural issues" |
| lyric-writer | music-lyric-writer | drafting | "writing new lyrics, revising existing lyrics" / "let's work on a track" |
| mastering-engineer | music-mastering-engineer | release | "user has approved tracks and wants to master audio files" / "loudness optimization and tonal balance" |
| mix-engineer | music-mix-engineer | release | "after audio import and before mastering" / "processing per-stem WAVs ... into a polished stereo WAV" |
| new-album | music-new-album | lifecycle | "make a new album" / "creates a new album with the correct directory structure and templates" |
| next-step | music-next-step | lifecycle | "what should I do next?" / "what's left to do?" |
| plagiarism-checker | music-plagiarism-checker | qc | "before release" / "check for unintentional borrowing" |
| pre-generation-check | music-pre-generation-check | qc | "before generating tracks on Suno" / "pre-gen check / ready to generate" |
| promo-director | music-promo-director | release | "after mastering is complete and before release" / "15-second vertical promo videos for social media" |
| promo-reviewer | music-promo-reviewer | qc | "after populating promo templates and before release" / "polish platform-specific posts" |
| promo-writer | music-promo-writer | drafting | "promo/ templates need to be populated before release" / "platform-specific social media copy from album themes" |
| promote-idea | music-promote-idea | lifecycle | "promote [idea title]" / "turn idea into album / start working on [idea]" |
| pronunciation-specialist | music-pronunciation-specialist | qc | "writing lyrics with proper nouns, technical terms, homographs, or non-English words" / "prevents Suno mispronunciations" |
| release-director | music-release-director | release | "mastering and album art are complete and the user is ready to release" / "coordinates album release including QA, distribution prep, and platform uploads" |
| rename | music-rename | utility | "user wants to rename an album or track" / "updating slugs, titles, and all mirrored paths" |
| researcher | music-researcher | research | "album needs factual research, source material, or verification of claims" / "investigative-grade research with primary source analysis" |
| researchers-biographical | music-researchers-biographical | research | "research needs biographical context about people involved in the album's subject" / "personal backgrounds, interviews, motivations" |
| researchers-financial | music-researchers-financial | research | "financial crimes, corporate stories, or market events" / "SEC filings, earnings calls, analyst reports" |
| researchers-gov | music-researchers-gov | research | "research needs official government records" / "DOJ/FBI/SEC press releases, agency statements" |
| researchers-historical | music-researchers-historical | research | "historical events that need primary source verification" / "archives, contemporary accounts, and timeline reconstruction" |
| researchers-journalism | music-researchers-journalism | research | "research needs journalistic sources for cross-referencing" / "investigative articles, interviews, and news coverage" |
| researchers-legal | music-researchers-legal | research | "legal proceedings or criminal cases" / "court documents, indictments, plea agreements, and sentencing records" |
| researchers-primary-source | music-researchers-primary-source | research | "research needs direct quotes or first-person accounts" / "subject's own words from tweets, blogs, forums, and chat logs" |
| researchers-security | music-researchers-security | research | "cybersecurity incidents or threat actors" / "malware analysis, CVEs, attribution reports" |
| researchers-tech | music-researchers-tech | research | "technology projects or developer stories" / "project histories, changelogs, developer interviews" |
| researchers-verifier | music-researchers-verifier | research | "after research is complete to verify all sources and claims" / "quality control, citation validation, and fact-checking before human review" |
| resume | music-resume | lifecycle | "user mentions an album name or wants to continue previous work" / "finds an album by name and shows detailed status with next steps" |
| session-start | music-session-start | lifecycle | "beginning of a fresh session" / "verifies setup, loads config and state, checks skill models" |
| setup | music-setup | lifecycle | "first-time setup" / "MCP server fails to start" |
| sheet-music-publisher | music-sheet-music-publisher | release | "after mastering when the user wants sheet music or a songbook" / "converts mastered audio to sheet music" |
| skill-model-updater | music-skill-model-updater | utility | "Anthropic releases new Claude models" / "updates model references across all skill files" |
| suno-engineer | music-suno-engineer | drafting | "creating or refining Suno prompts for track generation" / "Suno V5/V5.5 style prompts, genre selection, generation settings" |
| test | music-test | utility | "before creating PRs, after making changes to skills or templates" / "automated tests to validate plugin integrity across 14 categories" |
| tutorial | music-tutorial | lifecycle | "user is new to the plugin" / "walkthrough of the album creation process" |
| validate-album | music-validate-album | qc | "before release or whenever the user wants to check an album's structural health" / "validates album directory structure, file locations, and content integrity" |
| verify-sources | music-verify-sources | research | "sources need human review before generation" / "captures human source verification for tracks, timestamps it, and updates track files" |
| voice-checker | music-voice-checker | qc | "reviewing lyrics for authenticity or before generation" / "AI-written patterns (abstract noun stacking, over-explained metaphors, cliche escalation)" |

## Summary

- **Total skills**: 54
- **Categories**: lifecycle (12), drafting (6), qc (9), release (8), research (12), utility (7)
- **Source**: `bitwize-music @ v0.91.0`
  (`https://github.com/bitwize-music-studio/claude-ai-music-skills`)
- **Body bytes**: byte-identical to vendor source (verified by per-file
  diff restricted to YAML frontmatter region; only `name:` and the
  `allowed-tools:` server identifier line differ).
- **Inline `/bitwize-music:` slash references in skill bodies**: preserved
  verbatim per port discipline; their rewrite is owned by Spec 020
  (CLAUDE.md + cross-cutting body rewrites).
