# PORTING ROADMAP — every skill & function → agency v4

> Target architecture: one Engine + one bi-temporal GraphQLite graph; FOUR concepts —
> **Intent** (human goal: `capture·confirm·supersede`), **Capability** (the craft, open verbs
> role-tagged `act`/`transform`/`effect`), **Lifecycle** (task/agent state-machine; write frame
> `open·move·close` + observe frame `read·find·check·watch`; an agent = a Lifecycle parameterization),
> **Memory** (the graph; `record·link·supersede` + `recall·find·validate`). Tool names
> `<concept>_<capability>_<verb>` (underscores, ≤64, no dots). Read `CORE.md` for the full spec.
>
> Legend per line: `name | source plugin | → concept | verb + role | how-to-port note`.
> ⚠ = does NOT map cleanly (the valuable findings — see the dedicated section at the end).

---

## 1. bitwize-music — SKILLS (`skills/music/`, 54 dirs)

Most music skills are **Capabilities** (craft acts) or **Lifecycle observers** that read/check album
state. The album/track/idea workflow itself is a **Lifecycle** parameterization; every craft act and
gate edges back to the album's **Intent** via `SERVES`.

### Craft / authoring capabilities (act)
- lyric-writer | bitwize-music | → Capability | `act` | `capability_lyric_act`; drafts lyrics, writes craft artefact, `PRODUCES` lyric node `SERVES` album Intent.
- lyric-refiner | bitwize-music | → Capability | `act` (multi-pass) | `capability_lyric_refine`; each pass = a Lifecycle `move`, refined draft `SUPERSEDES` prior via Memory.
- suno-engineer | bitwize-music | → Capability | `act` | `capability_suno_prompt_act`; constructs style-box prompt artefact; auto-invoked by lyric-writer (PRECEDES edge).
- album-conceptualizer | bitwize-music | → Capability + Lifecycle gate | `act` then `check` | `capability_album_concept_act`; ⚠ its Phase-7 confirmation is an Intent `confirm` gate, not a craft act — split (see §End).
- album-art-director | bitwize-music | → Capability | `act` | `capability_art_direct_act`; produces art-prompt + concept artefacts.
- promo-writer | bitwize-music | → Capability | `act` | `capability_promo_write_act`; generates platform copy artefacts.
- genre-creator | bitwize-music | → Capability | `act` | `capability_genre_create_act`; writes new genre-doc artefact into reference set.
- rename | bitwize-music | → Lifecycle / Memory | `move` + `supersede` | `lifecycle_album_rename_move`; renames slug/title, `SUPERSEDES` old identity across mirrored paths.

### Compute / analysis capabilities (transform — stateless, no side-effect)
- pronunciation-specialist | bitwize-music | → Capability | `transform` | `capability_pronunciation_transform`; scans for homograph/proper-noun risk, returns annotated set.
- lyric-reviewer | bitwize-music | → Capability + Lifecycle check | `transform` then `check` | `capability_lyric_review_transform`; 14-pt QC + auto phonetic fix; pass/fail = Lifecycle `check`.
- voice-checker | bitwize-music | → Capability | `transform` (advisory) | `capability_voice_check_transform`; AI-pattern flags, NEVER gates — emits Info/Warning only.
- explicit-checker | bitwize-music | → Capability | `transform` | `capability_explicit_check_transform`; scans, reconciles flag vs content.
- plagiarism-checker | bitwize-music | → Capability | `transform` (+web effect) | `capability_plagiarism_check`; ⚠ mixed: web-search is `effect`, phrase-match is `transform`.

### Researchers family (Capability `transform`, web/source `effect`) — a Lifecycle fan-out
- researcher | bitwize-music | → Lifecycle (orchestrator) | `open·move·close` | `lifecycle_research_*`; parent research session that dispatches the specialist researchers below (DISPATCHED_TO edges) — agent parameterization.
- researchers-biographical | bitwize-music | → Capability | `effect` (search) + `transform` | `capability_research_bio`; sub-agent Lifecycle, findings `SERVE` research Intent.
- researchers-financial | bitwize-music | → Capability | `effect`+`transform` | `capability_research_financial`.
- researchers-gov | bitwize-music | → Capability | `effect`+`transform` | `capability_research_gov`.
- researchers-historical | bitwize-music | → Capability | `effect`+`transform` | `capability_research_historical`.
- researchers-journalism | bitwize-music | → Capability | `effect`+`transform` | `capability_research_journalism`.
- researchers-legal | bitwize-music | → Capability | `effect`+`transform` | `capability_research_legal`.
- researchers-primary-source | bitwize-music | → Capability | `effect`+`transform` | `capability_research_primary`.
- researchers-security | bitwize-music | → Capability | `effect`+`transform` | `capability_research_security`.
- researchers-tech | bitwize-music | → Capability | `effect`+`transform` | `capability_research_tech`.
- researchers-verifier | bitwize-music | → Memory | `validate` | `memory_research_validate`; cross-checks citations → Memory `validate`, not a craft act.
- document-hunter | bitwize-music | → Capability | `effect` | `capability_document_hunt`; browser-driven doc retrieval = external side-effect.

### Audio capabilities (effect — touch the filesystem / DSP)
- mix-engineer | bitwize-music | → Capability | `effect` | `capability_mix_effect`; processes per-stem WAVs → polished stereo; output artefact `PRODUCES`.
- mastering-engineer | bitwize-music | → Capability | `effect` | `capability_master_effect`; qc→master→qc chain; each step a Lifecycle `move`.
- sheet-music-publisher | bitwize-music | → Capability | `effect` | `capability_sheet_publish_effect`; transcribe→songbook artefacts.
- promo-director | bitwize-music | → Capability | `effect` | `capability_promo_video_effect`; renders 15-s vertical videos.
- cloud-uploader | bitwize-music | → Capability | `effect` (external) | `capability_cloud_upload_effect`; R2/S3 upload.

### Import / placement capabilities (effect — fs moves)
- import-audio | bitwize-music | → Capability / Lifecycle | `effect` (`move`) | `capability_import_audio_effect`; relocates WAVs to album path.
- import-art | bitwize-music | → Capability | `effect` | `capability_import_art_effect`; places art ≥3000×3000 into audio+content dirs.
- import-track | bitwize-music | → Capability | `effect` | `capability_import_track_effect`; moves track md to album.
- clipboard | bitwize-music | → Capability | `effect` (system) | `capability_clipboard_effect`; copies content to system clipboard.

### Lifecycle / state observers (read·find·check·watch) and gates
- pre-generation-check | bitwize-music | → Lifecycle | `check` (hard gate) | `lifecycle_track_pregate_check`; 6 BLOCKING gates → `input-required` on fail (Intent re-entry).
- release-director | bitwize-music | → Lifecycle | `check` (hard gate) | `lifecycle_album_release_check`; 9-domain QA gate; blocks until all pass.
- validate-album | bitwize-music | → Lifecycle / Memory | `check` + `validate` | `lifecycle_album_validate_check`; structural integrity of nodes/paths.
- verify-sources | bitwize-music | → Memory / Intent | `validate` + `confirm` | `memory_sources_validate`; captures human verification, timestamps → Intent gate for documentary albums.
- next-step | bitwize-music | → Lifecycle | `find` | `lifecycle_album_next_find`; decision-tree over album state → recommended transition.
- resume | bitwize-music | → Lifecycle | `read`/`find` | `lifecycle_album_resume_read`; finds album, reports detailed state + next steps.
- album-dashboard | bitwize-music | → Lifecycle / Memory | `read` | `lifecycle_album_dashboard_read`; %-complete-per-phase projection (a Memory `project` over Lifecycle states).
- new-album | bitwize-music | → Lifecycle + Intent | `open` + `capture` | `lifecycle_album_open` / `intent_album_capture`; ⚠ creating an album *is* capturing the Intent AND opening its Lifecycle (see §End).
- promote-idea | bitwize-music | → Intent / Lifecycle | `supersede`/`move` | `intent_idea_promote`; idea node → album Intent (idea `SUPERSEDES`-into project).
- album-ideas | bitwize-music | → Intent (backlog) | `capture` + `read` | `intent_idea_capture`; manages the pre-Intent idea backlog.

### Meta / housekeeping skills (mostly Engine or drop)
- help | bitwize-music | → Engine | `list_skills` | folds into the four-verb contract `list_skills`; drop as standalone.
- about | bitwize-music | → Engine / Capability `.help` | progressive disclosure | becomes `<capability>.help`; drop as standalone skill.
- tutorial | bitwize-music | → ⚠ harness onboarding | n/a | ⚠ doc/onboarding content, not a graph concept — keep as docs, not a tool.
- session-start | bitwize-music | → Engine middleware | n/a | ⚠ becomes engine session-bootstrap, not a Capability.
- health-check | bitwize-music | → Engine | `check` | `engine_health_check`; engine self-test, not domain.
- setup | bitwize-music | → Engine | n/a | install/bootstrap → engine provisioning script, drop as skill.
- configure | bitwize-music | → Engine | n/a | config read/write → engine config surface.
- skill-model-updater | bitwize-music | → ⚠ meta-tooling | n/a | ⚠ dev-harness maintenance (rewrites model refs) — belongs to the dev toolchain (§4), not agency.
- test | bitwize-music | → ⚠ dev toolchain | n/a | ⚠ plugin-integrity tests — dev loop, not a domain capability (§4).

---

## 2. bitwize-music — MCP TOOLS (`handlers/music/` + `tools/{mastering,mixing,sheet_music,promotion}`)

These are the low-level primitives the skills call. Naming drops the `music_` prefix for
`<concept>_<capability>_<verb>`. Grouped by graph concept.

### Memory — record / link / supersede (graph writes; replace SQLite cache + state/)
- music_create_album_structure | bitwize-music | → Memory + Lifecycle | `record`+`open` | `memory_album_record` / `lifecycle_album_open`.
- music_create_track | bitwize-music | → Memory | `record` | `memory_track_record`; track node `SERVES` album Intent.
- music_create_idea | bitwize-music | → Intent/Memory | `capture`/`record` | `intent_idea_capture`.
- music_update_track_field | bitwize-music | → Lifecycle / Memory | `move` (enforced) | `lifecycle_track_move`; MCP-enforced status transitions = Lifecycle edges (illegal transitions rejected).
- music_update_idea | bitwize-music | → Intent/Memory | `supersede` | `intent_idea_supersede`.
- music_update_session | bitwize-music | → Memory | `record` | `memory_session_record`.
- music_update_streaming_url | bitwize-music | → Memory | `record`/`link` | `memory_streaming_link`.
- music_rebuild_state | bitwize-music | → Memory | `record` (rebuild) | ⚠ exists only because of dual-store drift; with one graph this **disappears** (see §End).
- music_db_init / db_sync_album / db_create_tweet / db_update_tweet / db_delete_tweet / db_list_tweets / db_search_tweets / db_get_tweet_stats | bitwize-music | → Memory | `record`/`recall`/`supersede` | `memory_tweet_*`; ⚠ the whole separate tweet SQLite collapses into graph nodes (§End).
- music_promote_idea | bitwize-music | → Intent | `supersede` | `intent_idea_promote`.
- music_reset_mastering | bitwize-music | → Memory / Lifecycle | `supersede` | `lifecycle_master_reset`; reverts mastering state via supersession.

### Memory — recall / find / validate (graph reads; replace search + getters)
- music_get_album_full / get_track / get_album_progress / list_albums / list_tracks / list_track_files / find_album | bitwize-music | → Memory | `recall`/`find` | `memory_album_recall` etc.; all become `project(query,budget)` reads.
- music_search_items | bitwize-music | → Memory | `find` | `memory_search_find`; full-text → graph query.
- music_get_ideas / get_session / get_streaming_urls / get_pending_verifications | bitwize-music | → Memory | `recall`/`find` | `memory_*_recall`.
- music_get_lyrics_stats | bitwize-music | → Capability | `transform` | `capability_lyrics_stat_transform`.
- music_resolve_path / resolve_track_file | bitwize-music | → Memory | `find` | `memory_path_find`; ⚠ path-resolution exists because content lives on disk not in graph (§End).
- music_get_config / get_reference / load_override / get_plugin_version / get_python_command | bitwize-music | → Engine | config/read | engine surface, not domain.

### Capability — transform (stateless text/lyric/audio analysis)
- music_count_syllables | bitwize-music | → Capability | `transform` | `capability_syllable_transform`.
- music_analyze_rhyme_scheme | bitwize-music | → Capability | `transform` | `capability_rhyme_transform`.
- music_analyze_readability | bitwize-music | → Capability | `transform` | `capability_readability_transform`.
- music_check_homographs | bitwize-music | → Capability | `transform` | `capability_homograph_transform`.
- music_check_pronunciation_enforcement | bitwize-music | → Capability | `transform` | `capability_pronunciation_transform`.
- music_check_explicit_content | bitwize-music | → Capability | `transform` | `capability_explicit_transform`.
- music_extract_distinctive_phrases | bitwize-music | → Capability | `transform` | `capability_phrase_extract_transform`.
- music_extract_section / extract_links | bitwize-music | → Capability | `transform` | `capability_extract_transform`.
- music_check_cross_track_repetition | bitwize-music | → Capability/Memory | `transform`/`find` | `capability_repetition_transform`; cross-track read = Memory traversal.
- music_check_streaming_lyrics | bitwize-music | → Lifecycle | `check` | `lifecycle_streaming_lyrics_check`.
- music_format_for_clipboard | bitwize-music | → Capability | `transform` | `capability_clipboard_format_transform`.
- music_scan_artist_names | bitwize-music | → Capability | `transform` | `capability_artist_scan_transform`.
- music_analyze_mix_issues | bitwize-music | → Capability | `transform` | `capability_mix_analyze_transform`.
- music_album_coherence_check | bitwize-music | → Lifecycle/Memory | `check`/`validate` | `lifecycle_album_coherence_check`.
- music_album_coherence_correct | bitwize-music | → Capability | `act` | `capability_album_coherence_act`.

### Capability — effect (audio DSP / external, `tools/{mastering,mixing,sheet_music,promotion}`)
- music_analyze_audio | bitwize-music | → Capability | `transform` (read-only DSP) | `capability_audio_analyze_transform`.
- music_master_audio / master_album / master_with_reference | bitwize-music | → Capability | `effect` | `capability_master_effect`; (tools/mastering/master_tracks, reference_master).
- music_polish_audio / polish_album / polish_and_master_album | bitwize-music | → Capability | `effect` | `capability_polish_effect` (tools/mixing/mix_tracks, excitation).
- music_qc_audio | bitwize-music | → Lifecycle | `check` | `lifecycle_audio_qc_check` (tools/mastering/qc_tracks).
- music_measure_album_signature | bitwize-music | → Capability/Memory | `transform`/`record` | `capability_signature_measure` (tools/mastering/album_signature, signature_persistence).
- music_mono_fold_check | bitwize-music | → Lifecycle | `check` | `lifecycle_mono_fold_check` (tools/mastering/mono_fold).
- music_render_codec_preview | bitwize-music | → Capability | `effect` | `capability_codec_preview_effect` (tools/mastering/codec_preview).
- music_fix_dynamic_track | bitwize-music | → Capability | `effect` | `capability_dynamic_fix_effect` (tools/mastering/fix_dynamic_track).
- music_migrate_audio_layout | bitwize-music | → ⚠ Engine migration | one-shot | ⚠ data-layout migration, not a recurring capability (tools/mastering/layout) (§End).
- music_prune_archival | bitwize-music | → Memory | `supersede` | `memory_archival_supersede` (tools/mastering/archival).
- music_transcribe_audio | bitwize-music | → Capability | `effect` | `capability_transcribe_effect` (tools/sheet_music/transcribe).
- music_create_songbook | bitwize-music | → Capability | `effect` | `capability_songbook_effect` (tools/sheet_music/create_songbook).
- music_prepare_singles | bitwize-music | → Capability | `effect` | `capability_singles_prepare_effect` (tools/sheet_music/prepare_singles).
- music_publish_sheet_music | bitwize-music | → Capability | `effect` | `capability_sheet_publish_effect`.
- music_generate_promo_videos | bitwize-music | → Capability | `effect` | `capability_promo_video_effect` (tools/promotion/generate_promo_video, generate_all_promos).
- music_generate_album_sampler | bitwize-music | → Capability | `effect` | `capability_album_sampler_effect` (tools/promotion/generate_album_sampler).
- music_get_promo_content / get_promo_status | bitwize-music | → Memory | `recall` | `memory_promo_recall`.

### Lifecycle / gates / health (MCP)
- music_run_pre_generation_gates | bitwize-music | → Lifecycle | `check` (hard gate) | `lifecycle_track_pregate_check` (handlers/music/gates.py).
- music_validate_album_structure / validate_section_structure | bitwize-music | → Lifecycle | `check` | `lifecycle_album_validate_check`.
- music_verify_streaming_urls | bitwize-music | → Lifecycle/Capability | `check`+`effect` | `lifecycle_streaming_verify_check`.
- music_get_album_progress | bitwize-music | → Lifecycle | `read` | `lifecycle_album_progress_read`.
- music_health_check / check_venv_health / cleanup_legacy_venvs / diagnose_issue | bitwize-music | → Engine | `check`/maintenance | ⚠ env/venv health — engine concern, not domain (§4/§End).

---

## 3. jules / agency-system

The Jules orchestrator is the clearest pre-existing instance of the v4 thesis: **an agent IS a
Lifecycle parameterization** whose transitions differ (it inserts a `verify` step because
`COMPLETED ≠ done`). Port it as the reference Lifecycle.

### Jules skills / slash commands (`commands/jules-*.md`, `skills/jules/SKILL.md`)
- jules (orchestrator SKILL) | jules-plugin | → Lifecycle (agent parameterization) | `open·move·close·watch` | `lifecycle_agent_*`; the canonical remote-async-agent Lifecycle.
- jules-create | jules-plugin | → Lifecycle | `open` | `lifecycle_agent_open`; opens a session Lifecycle, `DISPATCHED_TO` edge from Intent.
- jules-list | jules-plugin | → Lifecycle | `find` | `lifecycle_agent_find`.
- jules-watch | jules-plugin | → Lifecycle | `watch` | `lifecycle_agent_watch`; streams activities until terminal.
- jules-bulk | jules-plugin | → Lifecycle (fan-out) | `open` (×N) | `lifecycle_agent_bulk_open`; parallel orchestration = many Lifecycles under one Intent.
- jules-patch-summary | jules-plugin | → Memory/Capability | `transform`/`record` | `memory_patch_summarize`; summarizes produced artefact.

### Jules agentic discipline skills (`skills/agentic/`)
- jules-orchestrator-discipline | agentic | → Lifecycle (policy) | observer rules | ⚠ encodes the `COMPLETED ≠ done` + verify-before-trust rules — becomes Lifecycle **observer/transition policy**, not a callable tool (§End).
- silent-fail-recovery | agentic | → Lifecycle | `check`+`move` (verify) | `lifecycle_agent_verify`; the inserted `verify` step — verify branch on remote before trusting `COMPLETED`.
- context-safe-patch-handling | agentic | → Engine middleware | n/a | ⚠ the code-mode "deltas + elided_ref only" rule — this IS the engine's `execute(code)` contract, not a domain skill (§End).

### Jules MCP tools (`jules-plugin/.../tools/` + `handlers/jules/`)
- jules_create | jules-plugin | → Lifecycle | `open` | `lifecycle_agent_open`.
- jules_get | jules-plugin | → Lifecycle | `read` | `lifecycle_agent_read`.
- jules_list / jules_status_all | jules-plugin | → Lifecycle | `find` | `lifecycle_agent_find`.
- jules_activities | jules-plugin | → Lifecycle | `watch` | `lifecycle_agent_watch`.
- jules_message | jules-plugin | → Lifecycle | `move` | `lifecycle_agent_move`; resumes COMPLETED→IN_PROGRESS.
- jules_plan / jules_approve / jules_approve_awaiting | jules-plugin | → Lifecycle/Intent | `check`→`input-required`→`confirm` | `lifecycle_agent_gate`; plan-approval = Intent re-entry gate.
- jules_stop | jules-plugin | → Lifecycle | `close` (cancel) | `lifecycle_agent_close`.
- jules_session_summary | jules-plugin | → Memory | `recall` | `memory_agent_recall`.
- jules_quota | jules-plugin | → Engine | Slot/quota middleware | ⚠ engine quota guard, not a concept (§End).
- jules_patch | jules-plugin (patches.py) | → Memory | `recall` | `memory_patch_recall`; extract stats only (context-safe).
- jules_patch_summary | jules-plugin | → Memory/Capability | `transform` | `memory_patch_summarize`.
- jules_patch_apply | jules-plugin | → Capability | `effect` | `capability_patch_apply_effect`; applies extracted patch (github create_branch/file/PR).
- jules_pr_url | jules-plugin | → Memory | `recall` | `memory_agent_pr_recall`.
- jules_resolve_source / jules_resolve_alias | jules-plugin (source.py/aliases.py) | → Memory | `find` | `memory_source_find`; repo/alias resolution.
- register_*_tools / trim.py | jules-plugin | → Engine | n/a | wiring + response-trimming = engine middleware (trim = compaction guard).

---

## 4. Other agency-mcp handler families

### novel (`handlers/novel/`) — second domain, proves the verb frame carries two crafts
The novel handlers mirror music almost 1:1 and are the FALSIFICATION TEST from CORE.md ("does the
verb frame + one graph actually carry two different capabilities?"). Port as the same four concepts,
different Capability set.
- novel_create_work / create_chapter / create_scene / create_character / create_premise_idea | novel | → Memory+Lifecycle | `record`/`open` | `memory_*_record`; work=Intent, chapter/scene nodes `SERVE` it.
- novel_get_* / list_* / find_novel | novel | → Memory | `recall`/`find` | `memory_*_recall`.
- novel_update_*_status / mark_revision_pass / revert_to_pass | novel | → Lifecycle | `move` | `lifecycle_*_move`; revert = `supersede`.
- novel_rename_work / rename_chapter | novel | → Lifecycle/Memory | `move`+`supersede` | `lifecycle_*_rename_move`.
- novel_promote_premise / update_premise_idea / delete_premise_idea | novel | → Intent | `capture`/`supersede` | `intent_premise_*`.
- novel_rebuild_state | novel | → Memory | `record` | ⚠ same dual-store artefact as music — disappears with one graph (§End).
- novel_analyze_readability / analyze_rhythm / extract_distinctive_phrases | novel | → Capability | `transform` | `capability_prose_*_transform`.
- novel_scan_pov_violations / check_world_consistency / check_relationship_graph / check_slot_fill / check_throughline_partition / check_signpost_permutation / check_crucial_element_placement / check_approach_concern / check_resolve_outcome_judgment / check_mental_sex_problem_solving | novel | → Lifecycle/Capability | `check`/`transform` | `lifecycle_prose_*_check`; Dramatica-model gates.
- novel_run_pre_drafting_gates | novel | → Lifecycle | `check` (hard gate) | `lifecycle_prose_predraft_check`.
- novel_coherence_check / coherence_correct | novel | → Lifecycle / Capability | `check` / `act` | `lifecycle_prose_coherence_check` / `capability_prose_coherence_act`.
- novel_get_storyform / get_throughline / get_quad_menu / get_player / list_players / get_world / list_world_entities / assign_archetype / update_player_field | novel | → Memory | `recall`/`record` | `memory_storyform_*`; Dramatica storyform = graph subtree.
- novel_build_promo_pack / get_promo_content / update_promo_field | novel | → Capability/Memory | `act`/`recall` | `capability_prose_promo_*`.

### shared (`handlers/shared/`) — these ARE the four-verb engine contract
- shared_list_skills | shared | → Engine | `list_skills` | the contract verb verbatim.
- shared_get_skill | shared | → Engine | `dispatch_skill`/`.help` | progressive disclosure.
- shared_search | shared | → Memory | `find` | `memory_find`; cross-domain graph query.
- shared_get_session / update_session | shared | → Memory/Lifecycle | `recall`/`move` | session state → Lifecycle node.
- shared_get_pending_verifications | shared | → Memory/Lifecycle | `find` | `memory_pending_find`.
- shared_get_config / get_reference / load_override / plugin_help | shared | → Engine | config surface | engine, not domain.

### context (`handlers/context/`) — engine middleware, not concepts
- context/anchors.py, resources.py (emit_resource_updated, clear_search_describe_cache) | context | → Engine | n/a | ⚠ MCP resource/anchor plumbing = engine middleware (resource-updated notifications, describe-cache) (§End).

---

## 5. Dev-harness meta-plugins (sc / SuperClaude, superpowers, built-in CC skills)

**Do NOT port these as domain capabilities.** They are the **development loop's toolchain** — the meta
capabilities that DRIVE *building* the agency engine, not crafts the agency *runs for a user*. They
operate one level up: on the codebase and the spec, not on albums/novels/agent-sessions. They stay in
the dev harness (Claude Code) and are invoked while implementing the seed and porting each item above.

Examples of how they relate to the build, not the product:
- **superpowers:brainstorming / writing-plans / executing-plans** → drive the seed's design + the
  porting plan itself (this very roadmap is their output); never become `<concept>_<capability>_<verb>` tools.
- **superpowers:test-driven-development / verification-before-completion** → enforce CORE.md's "BUILD A
  SEED → passing test" mandate; they gate *our* commits, not user Intents.
- **sc:sc-implement / sc-analyze / sc-spec-panel** → the adversarial panel + implementation loop that
  cut v3 to v4 and will write the engine code; meta-orchestration of the build.
- **code-review / security-review / requesting-code-review** → quality gates on the engine's own PRs.
- **bitwize-music:test, skill-model-updater, session-start, setup, configure, health-check** (from §1/§2)
  belong with this toolchain, not the domain — they maintain the *plugin*, not produce *music*.

Mapping rule of thumb: if a skill's object is "the repo / the spec / the model refs / the test suite,"
it is dev-toolchain (here); if its object is "an album / a novel / an agent-session," it ports as a
concept above.

---

## 6. ⚠ ITEMS THAT DON'T MAP CLEANLY (the valuable findings)

1. **Dual-store drift tools vanish** — `music_rebuild_state`, `novel_rebuild_state`, and the entire
   `db_*` tweet SQLite (`db_init/sync_album/create/update/delete/list/search/get_tweet_stats`) exist
   ONLY because content lives on disk while a SQLite cache mirrors it. With one bi-temporal graph as the
   single store, **the cache and every rebuild/sync tool disappear** — there is nothing to re-sync.
   This is the strongest validation of the "one graph" thesis; ~12 tools delete rather than port.

2. **Path resolution is a disk-store smell** — `music_resolve_path`, `resolve_track_file`,
   `list_track_files`, `migrate_audio_layout` exist because artefacts are files at conventional paths.
   In the graph, artefacts are nodes reachable by `PRODUCES`/`SERVES` traversal; path-resolution
   collapses into `memory_find`. `migrate_audio_layout` is a one-shot data migration, not a capability.

3. **Skills that are BOTH Intent-capture AND Lifecycle-open** — `new-album`, `album-conceptualizer`
   (Phase-7), `promote-idea` straddle two concepts: creating the album simultaneously (a) `capture`s the
   human Intent (purpose+acceptance+deliverable) and (b) `open`s the Lifecycle. v4 must decide the edge
   order (Intent first, Lifecycle `SERVES` it) and split these skills into two calls. The album-
   conceptualizer Phase-7 confirmation is specifically an Intent `confirm` gate masquerading as a craft step.

4. **Agentic discipline skills are POLICY, not tools** — `jules-orchestrator-discipline`,
   `silent-fail-recovery`, `context-safe-patch-handling` encode behavioral rules
   (`COMPLETED ≠ done`, verify-before-trust, patch-stats-only). They don't map to a single verb; they
   become **Lifecycle transition/observer policy** and **engine code-mode contract** respectively.
   `silent-fail-recovery`'s inserted `verify` step is exactly CORE.md's "remote async agent inserts
   `verify`" — port it as a Lifecycle parameterization difference, not a callable.

5. **Advisory-only & web-mixed capabilities** — `voice-checker` must NEVER gate (Info/Warning only),
   so it is a `transform` whose output is explicitly *not* wired to a Lifecycle `check`. `plagiarism-
   checker` and the `researchers-*` family are split-role: web-search/document-hunt = `effect`,
   phrase-matching/analysis = `transform` — a single skill spans two capability roles and needs splitting.

6. **Engine middleware masquerading as tools** — `jules_quota`/`Slot`, `trim.py` (compaction),
   `context/resources.py` + `anchors.py` (resource-updated, describe-cache), `*_health_check`,
   `check_venv_health`, `cleanup_legacy_venvs`, config/reference getters are **cross-cutting guards**
   CORE.md explicitly says are engine middleware, **NOT concepts**. They port into the Engine substrate,
   not into the four-concept namespace.

7. **Pure onboarding/docs** — `tutorial`, `about`, `help`, `session-start`, `setup` are progressive-
   disclosure / bootstrap, absorbed by the four-verb contract (`list_skills`, `<capability>.help`) and
   engine session-bootstrap; they don't survive as standalone named tools.
