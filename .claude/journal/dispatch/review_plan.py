#!/usr/bin/env python3
"""Fetch a Jules session's plan and dump as compact markdown for review."""
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location("jm", ".claude/mcp/jules-mcp/server.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

if len(sys.argv) < 2:
    print("usage: review_plan.py <session_id>"); sys.exit(2)

sid = sys.argv[1]
fn = getattr(mod.jules_plan, "fn", mod.jules_plan)
plan = fn(sid)
if "error" in plan:
    print(f"ERROR: {plan['error']}"); sys.exit(1)
print(f"# Plan for {sid}\n")
for i, s in enumerate(plan.get("steps", []), 1):
    print(f"{i}. **{s.get('title', '?')}**")
    desc = s.get("description", "").strip()
    if desc:
        # Trim to one line each for review
        print(f"   {desc[:200]}{'…' if len(desc) > 200 else ''}")
print(f"\n_create_time: {plan.get('create_time', '?')}_")
