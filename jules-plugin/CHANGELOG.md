# Changelog

## [v1.0.0] - Initial Release

This release cuts over the Jules orchestration suite to a standard Claude Desktop plugin architecture, removing the monolithic scripts and adopting a modular codebase.

### Added
- **16 MCP Tools**: Includes comprehensive multi-agent orchestration tools registered via FastMCP:
  - Lifecycle: `jules_create`, `jules_get`, `jules_list`, `jules_activities`, `jules_plan`, `jules_approve`, `jules_message`, `jules_resolve_source`
  - Patches: `jules_patch`, `jules_patch_apply`, `jules_patch_summary`, `jules_fetch_patch`
  - Bulk & Aliases: `jules_status_all`, `jules_approve_awaiting`, `jules_quota`, `jules_resolve_alias`
- **FastMCP Code Mode Opt-in**: The MCP server is now configured with the FastMCP CodeMode transform, replacing full-suite payload limits for faster, context-aware stateless tool resolutions.
- **Skill Restructuring**: The legacy 900-line `SKILL.md` is split into a streamlined skill instruction file and multiple focused reference files inside `jules-plugin/skills/jules/references/`.
- **Environment-Aware Paths**: Ported helper utilities (`lib/sessions_state.py`, `lib/watch_jules.py`, `bin/jules-bulk`) now resolve paths using the `${CLAUDE_PLUGIN_DATA}` environment variable for safer persistence across plugin upgrades.

### Removed
- **Stop Action Disabled**: The Jules API does not support cancellation. The `jules_stop` tool was removed/turned into a no-op as the underlying action isn't supported.
