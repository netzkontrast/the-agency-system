import re
import hashlib
import os
import json
import yaml

def compute_sha256(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()

def estimate_tokens(body_bytes: bytes) -> int:
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(body_bytes.decode('utf-8', errors='ignore')))
    except ImportError:
        return (len(body_bytes) + 3) // 4

def _truncate_on_word_boundary(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    # Truncate and find last space
    truncated = text[:limit]
    last_space = truncated.rfind(' ')
    if last_space > 0:
        return truncated[:last_space] + "…"
    return truncated + "…"

def extract_summary(path: str, body: str) -> str:
    """Pure function to extract summary from markdown, json or yaml."""
    ext = os.path.splitext(path)[1].lower()

    if ext == '.md':
        # Remove frontmatter
        if body.startswith("---"):
            parts = body.split("---", 2)
            if len(parts) == 3:
                body = parts[2]

        lines = body.splitlines()
        h1 = None
        for line in lines:
            if line.strip().startswith("# "):
                h1 = line.strip()[2:].strip()
                break

        if not h1:
            h1 = os.path.basename(path)

        p = ""
        in_p = False
        for line in lines:
            line_strip = line.strip()
            if line.startswith("#"):
                continue
            if line_strip:
                if not in_p and p:
                    break # Already found first paragraph
                p += " " + line_strip if p else line_strip
                in_p = True
            else:
                if in_p:
                    break

        summary = h1
        if p:
            summary += " - " + p
        return _truncate_on_word_boundary(summary.strip(), 400)

    elif ext in ('.json', '.yaml', '.yml'):
        data = {}
        try:
            if ext == '.json':
                data = json.loads(body)
            else:
                data = yaml.safe_load(body)
        except Exception:
            pass

        if isinstance(data, dict):
            title = data.get('title')
            desc = data.get('description')
            if title and desc:
                return _truncate_on_word_boundary(f"{title} - {desc}", 400)
            if title:
                return _truncate_on_word_boundary(title, 400)
            if desc:
                return _truncate_on_word_boundary(desc, 400)

        # Fallback
        return _truncate_on_word_boundary(f"{os.path.basename(path)} - {body[:200]}", 400)

    else:
        return _truncate_on_word_boundary(f"{os.path.basename(path)} - {body[:200]}", 400)

def extract_views(path: str, body_bytes: bytes) -> dict:
    body_str = body_bytes.decode('utf-8', errors='ignore')
    summary_str = extract_summary(path, body_str)

    summary_bytes = summary_str.encode('utf-8')
    # Summary is max 400 chars, so ~400 bytes
    summary_bytes = summary_bytes[:400]

    preview_bytes = body_bytes[:3200]

    return {
        "summary": {
            "token_estimate": estimate_tokens(summary_bytes),
            "byte_offset": 0,
            "byte_length": len(summary_bytes)
        },
        "preview": {
            "token_estimate": estimate_tokens(preview_bytes),
            "byte_offset": 0,
            "byte_length": len(preview_bytes)
        },
        "full": {
            "token_estimate": estimate_tokens(body_bytes),
            "byte_offset": 0,
            "byte_length": len(body_bytes)
        }
    }

def infer_tags(path: str, body: str) -> list[str]:
    tags = []

    # Try frontmatter
    import yaml
    if body.startswith("---"):
        parts = body.split("---", 2)
        if len(parts) == 3:
            try:
                fm = yaml.safe_load(parts[1])
                if fm:
                    if 'spec_id' in fm: tags.append(f"spec:{fm['spec_id']:03d}")
                    if 'slug' in fm: tags.append(f"slug:{fm['slug']}")
                    if 'domain' in fm: tags.append(f"domain:{fm['domain']}")
                    if 'lesson_id' in fm: tags.append(f"lesson_id:{fm['lesson_id']}")
            except Exception:
                pass

    # Search for topic: tags in body
    for match in re.finditer(r'\btopic:[a-zA-Z0-9_-]+\b', body):
        if match.group(0) not in tags:
            tags.append(match.group(0))

    # Default tags based on path
    parts = Path(path).parts if "Path" in globals() else path.split(os.sep)
    if "Plan" in parts and "spec.md" in path:
        if "kind:spec" not in tags: tags.append("kind:spec")
    if "_lessons-learned" in parts:
        if "kind:lesson" not in tags: tags.append("kind:lesson")
    if "overrides" in parts:
        if "kind:override" not in tags: tags.append("kind:override")

    return tags
