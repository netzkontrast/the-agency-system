---
description: Use when you want to list the agency capabilities and their verbs.
---

Map the agency engine's capabilities (macroskills) to their verbs (micro-skills) by running the engine's code-mode contract:

    python -m agency.cli --db agency.db execute --code 'return await call_tool("capability_plugin_help", {"intent_id": INTENT})'

