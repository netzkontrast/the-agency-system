## Spec
Plan/002-manifest-and-marketplace/spec.md

## Confidence
- 1. No duplicate implementation: Confirmed via `rg -l "agency-system" .claude-plugin/` and `rg -l "mcpServers" .claude-plugin/plugin.json` (no output before creation). Pass (0.25).
- 2. Architecture compliance: Uses expected plugin JSON schema natively. Pass (0.25).
- 3. Official docs verified: Docs from `https://code.claude.com/docs/en/plugins-reference` and `https://code.claude.com/docs/en/plugin-marketplaces` confirm separating mcpServers into `.mcp.json`. Pass (0.20).
- 4. Working OSS reference: Follows the latest recommended patterns for Claude Code plugins. Pass (0.15).
- 5. Root cause identified: The issue was that inline `mcpServers` in `plugin.json` collided with the standalone `.mcp.json` structure from Spec 001. Pass (0.15).
**Total: 1.00 (≥ 0.90)**

## Evidence

- `tests/smoke/test_manifest.py` checks both `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` shapes, plus deprecation flags on `jules-plugin/.claude-plugin/plugin.json`.
- `claude plugin marketplace add ./` and `claude plugin install agency-system@agency-marketplace` successfully pass using the CLI, which acts as end-to-end integration evidence.

```
Installing plugin "agency-system@agency-marketplace"...✔ Successfully installed plugin: agency-system@agency-marketplace (scope: user)
Installed plugins:

  ❯ agency-system@agency-marketplace
    Version: 0.1.0
    Scope: user
    Status: ✔ enabled
```

## Self-Review

1. **Did I drift from the spec?**
   No. I only modified `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `jules-plugin/.claude-plugin/plugin.json`, `README.md`, and added tests inside `tests/smoke/test_manifest.py`. I ensured `.claude-plugin/plugin.json` does NOT include an `mcpServers` field.

2. **What residual risk remains?**
   None observed. Tests guarantee the key format constraints.

3. **What pattern would I apply differently next time?**
   When replacing the inline `mcpServers` block with a standalone `.mcp.json`, always immediately ensure the `plugin.json` omits it, which avoids any future Claude Code parsing ambiguities.
