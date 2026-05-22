#!/usr/bin/env python3
"""PostToolUse hook: Validate chapter file YAML frontmatter after Write/Edit.

Only activates for files matching */chapters/*.md pattern.
Checks required frontmatter fields based on spec 013.
"""
import json
import sys
import re

REQUIRED_FIELDS = ["status", "chapter_number", "pov", "scene_ids", "ncp_link"]

def is_chapter_file(file_path: str) -> bool:
    return "/chapters/" in file_path and file_path.endswith(".md")

def get_file_content(data: dict) -> str | None:
    tool_input = data.get("tool_input", {})
    # Write tool provides full content
    if "content" in tool_input:
        return tool_input["content"]
    return None

def extract_frontmatter(content: str) -> dict | None:
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None
    fm = {}
    lines = match.group(1).split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if ":" in line and not line.strip().startswith("-"):
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if not value and i + 1 < len(lines) and lines[i+1].strip().startswith("-"):
                # It's a list
                list_vals = []
                i += 1
                while i < len(lines) and lines[i].strip().startswith("-"):
                    list_item = lines[i].strip()[1:].strip().strip('"').strip("'")
                    list_vals.append(list_item)
                    i += 1
                fm[key] = list_vals
                continue
            else:
                fm[key] = value
        i += 1
    return fm

def validate(data: dict) -> list[dict]:
    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not is_chapter_file(file_path):
        return []

    content = get_file_content(data)
    if content is None:
        # Edit tool — can't validate full frontmatter from partial edit
        return []

    fm = extract_frontmatter(content)
    if fm is None:
        return [{"field": "frontmatter", "reason": "Chapter file is missing or has invalid YAML frontmatter (--- block)."}]

    if not isinstance(fm, dict):
        return [{"field": "frontmatter", "reason": "YAML frontmatter must be a key-value mapping."}]

    issues = []

    if "status" not in fm or not fm["status"]:
        issues.append({"field": "status", "reason": "Missing or empty required field."})

    try:
        chap_num = int(fm.get("chapter_number", 0))
        if chap_num <= 0:
            issues.append({"field": "chapter_number", "reason": "Missing or must be a positive integer."})
    except ValueError:
        issues.append({"field": "chapter_number", "reason": "Missing or must be a positive integer."})

    if "pov" not in fm or not isinstance(fm["pov"], str) or not fm["pov"].strip():
        issues.append({"field": "pov", "reason": "Missing or must be a non-empty string."})

    if "scene_ids" not in fm or not isinstance(fm["scene_ids"], list) or not all(isinstance(x, str) for x in fm["scene_ids"]):
        issues.append({"field": "scene_ids", "reason": "Missing or must be a list of strings."})

    if "ncp_link" not in fm or not isinstance(fm["ncp_link"], str) or not fm["ncp_link"].strip():
        issues.append({"field": "ncp_link", "reason": "Missing or must be a path-shaped string."})

    return issues

def main():
    if len(sys.argv) > 1:
        # For testing purposes, pass a file path
        try:
            with open(sys.argv[1], "r") as f:
                content = f.read()
            data = {"tool_input": {"file_path": sys.argv[1], "content": content}}
        except Exception as e:
            print(json.dumps({"field": "file", "reason": f"Error reading {sys.argv[1]}: {e}"}), file=sys.stderr)
            sys.exit(1)
    else:
        try:
            data = json.load(sys.stdin)
        except (json.JSONDecodeError, EOFError):
            sys.exit(0)

    issues = validate(data)
    if issues:
        for issue in issues:
            print(json.dumps(issue), file=sys.stderr)
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
