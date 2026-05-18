with open("Plan/phase-7-domain-handler-completion/acceptance.feature", "r") as f:
    text = f.read()

text = text.replace("Feature: Phase 7 — Domain handler completion (music + novel + agentic)", "Feature: Phase 7 — Domain handler completion")
text = text.replace("Then exactly 28 skill files named SKILL.md exist under skills/novel/ excluding prompt builders", "Then exactly 28 SKILL.md files exist under skills/novel/ that are NOT under skills/novel/prompts/")
text = text.replace("And tools for specs, plans, workflows, research, ralph, and confidence are present", "And the prefixes agentic_spec_*, agentic_plan_*, agentic_workflow_*, agentic_research_*, agentic_ralph_*, and agentic_confidence_* are non-empty")
text = text.replace("Then it contains cross-project preference files including prose-style-guide.md and narrative-preferences.md", "Then it contains cross-project preference files including prose-style-guide.md, narrative-preferences.md, dramatica-defaults.md, and ncp-defaults.md")
text = text.replace("When I cross-reference every domain handler against the skill, command, and hook callers", "When I parse the agency-mcp tool registry and grep skills/, commands/, hooks/ for each tool name")
text = text.replace("Then every domain handler has at least one corresponding caller\n    And no orphaned handler functions exist without a consumer", "Then every registered handler appears as a caller in at least one of those three trees")

with open("Plan/phase-7-domain-handler-completion/acceptance.feature", "w") as f:
    f.write(text)
