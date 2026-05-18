import json
import math
import typing
from pathlib import Path

from agency_mcp.lib.codemode.context_manifest import ContextManifest, load_context_manifest

class ContextNotFound(ValueError):
    """Raised when a context ID is not found in the manifest."""
    pass

TRUNCATED_MARKER = "\n\n… [truncated; ask for fields= or read direct file]"

def _context_search(query: str, manifest: ContextManifest, *, domain: str | None = None, tags: list[str] | None = None, limit: int = 10) -> list[dict]:
    return manifest.search(query=query, domain=domain, tags=tags, limit=min(limit, 20))

def _context_describe(id: str, manifest: ContextManifest) -> dict:
    entry = manifest.get(id)
    if not entry:
        raise ContextNotFound(f"Context ID not found: {id}")
    
    # Return the entry minus body/raw content (which isn't in manifest anyway, but ensure it's just the JSON record)
    # entry is already a dict from the JSON
    return dict(entry)

def _context_read(id: str, manifest: ContextManifest, *, view: typing.Literal["summary", "preview", "full"] = "summary", fields: list[str] | None = None) -> dict:
    entry = manifest.get(id)
    if not entry:
        raise ContextNotFound(f"Context ID not found: {id}")
    
    views = entry.get("views", {})
    actual_view = view
    
    # 1. View resolution
    if actual_view not in views:
        if actual_view == "preview":
            actual_view = "full" if "full" in views else ("summary" if "summary" in views else None)
        elif actual_view == "summary":
            actual_view = "preview" if "preview" in views else ("full" if "full" in views else None)
        elif actual_view == "full":
            actual_view = "preview" if "preview" in views else ("summary" if "summary" in views else None)
            
    if not actual_view or actual_view not in views:
        # Fallback to whatever is available
        if "full" in views: actual_view = "full"
        elif "preview" in views: actual_view = "preview"
        elif "summary" in views: actual_view = "summary"
        else: actual_view = "full" # default fallback
        
    view_data = views.get(actual_view, {})
    
    byte_offset = view_data.get("byte_offset", 0)
    byte_length = view_data.get("byte_length", entry.get("size_bytes", 0))
    token_estimate = view_data.get("token_estimate", 0)
    
    # 2. Body loading
    file_path = Path(manifest.repo_root) / entry["path"]
    
    body = ""
    if file_path.exists():
        with open(file_path, "rb") as f:
            f.seek(byte_offset)
            raw_bytes = f.read(byte_length)
            
        try:
            body_str = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            body_str = str(raw_bytes) # fallback
            
        if (entry.get("mime") in ("application/json", "text/yaml", "application/yaml")) and fields:
            # Try to parse and project
            try:
                import json
                parsed = json.loads(body_str)
                
                # Import project helper
                from agency_mcp.lib.codemode.projection import project
                
                projected = project(parsed, fields=fields)
                body = json.dumps(projected, indent=2)
                
                # Re-estimate tokens for projected body
                try:
                    import tiktoken
                    enc = tiktoken.get_encoding("cl100k_base")
                    token_estimate = len(enc.encode(body))
                except ImportError:
                    token_estimate = math.ceil(len(body.encode("utf-8")) / 4)
            except json.JSONDecodeError:
                body = body_str # fallback to raw string if JSON parsing fails
        else:
            body = body_str
    
    # 3. Token-cap enforcement
    truncated = False
    if token_estimate > 4000:
        # Estimate how many bytes ~ 4000 tokens
        # Roughly 4 chars per token, so 16000 chars
        # We will do a rough cut
        cut_point = min(16000, len(body))
        
        # Find nearest line boundary
        last_newline = body.rfind('\n', 0, cut_point)
        if last_newline != -1:
            cut_point = last_newline
            
        body = body[:cut_point] + TRUNCATED_MARKER
        truncated = True
        
        # Re-estimate
        try:
            import tiktoken
            enc = tiktoken.get_encoding("cl100k_base")
            token_estimate = len(enc.encode(body))
        except ImportError:
            token_estimate = math.ceil(len(body.encode("utf-8")) / 4)

    return {
        "id": entry["id"],
        "view": actual_view,
        "mime": entry.get("mime", "text/plain"),
        "body": body,
        "token_estimate": token_estimate,
        "truncated": truncated
    }

def register_context_anchor_triad(mcp, manifest: ContextManifest):
    # This will be wired by handlers/context/anchors.py, but defined here if needed,
    # or handlers/context/anchors.py can call the _ functions directly.
    pass
