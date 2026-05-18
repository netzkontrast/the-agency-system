from pathlib import Path
from fastmcp import FastMCP
from agency_mcp.lib.codemode.context_manifest import ContextManifest, load_context_manifest

# Module-level cache
_manifest_cache: ContextManifest | None = None

def _get_manifest() -> ContextManifest:
    global _manifest_cache
    if _manifest_cache is None:
        # Load from default path
        manifest_path = Path(__file__).resolve().parents[2] / "codemode" / "context_manifest.json"
        _manifest_cache = load_context_manifest(str(manifest_path))
    return _manifest_cache

def register_context_resources(mcp: FastMCP) -> None:
    manifest = _get_manifest()

    # We dynamically register each resource
    for entry in manifest.entries:
        id = entry["id"]
        # Convert colon to underscore in URI because pydantic rejects standard colons without a port
        safe_id = id.replace(":", "-")

        mime = entry.get("mime", "text/plain")
        title = entry.get("title", id)
        summary = entry.get("summary", "")

        # We must create a closure for each entry to bind the correct id
        def make_resource_handler(entry_id: str, mapped_id: str):
            @mcp.resource(f"context://{mapped_id}", mime_type=mime, name=title, description=summary)
            def read_resource() -> str:
                # The handler body reads the file (full view) and returns its contents
                m = _get_manifest()
                e = m.get(entry_id)
                if not e:
                    raise ValueError(f"Resource not found: {entry_id}")

                # Fetch full file contents
                file_path = Path(m.repo_root) / e["path"]
                if not file_path.exists():
                    raise ValueError(f"File not found: {e['path']}")

                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            return read_resource

        make_resource_handler(id, safe_id)
