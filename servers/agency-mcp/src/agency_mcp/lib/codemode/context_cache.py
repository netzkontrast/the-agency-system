import hashlib
import os
import time
from collections import OrderedDict
from typing import NamedTuple, Optional
from agency_mcp.lib.codemode.context_manifest import load_context_manifest, ContextManifest

class ContextBody(NamedTuple):
    content: str
    truncated: bool

class CacheEntry(NamedTuple):
    body: ContextBody
    sha256: str
    inserted_at: float
    size_bytes: int
    last_modified: float

class ContextCache:
    """TTL + LRU cache for context layer reads."""

    def __init__(self, maxsize: int = 128, default_ttl_s: int = 300, manifest: Optional[ContextManifest] = None):
        self.maxsize = maxsize
        self.default_ttl_s = default_ttl_s
        self._cache: OrderedDict[tuple[str, str], CacheEntry] = OrderedDict()
        self._manifest = manifest

    def _get_manifest(self) -> ContextManifest:
        if self._manifest:
            return self._manifest
        from agency_mcp.handlers.context.resources import _get_manifest
        return _get_manifest()

    def get(self, id: str, view: str) -> Optional[ContextBody]:
        key = (id, view)
        if key not in self._cache:
            return None

        entry = self._cache[key]
        now = time.monotonic()

        if now - entry.inserted_at > self.default_ttl_s:
            del self._cache[key]
            return None

        manifest = self._get_manifest()
        manifest_entry = manifest.get(id)
        if not manifest_entry:
            del self._cache[key]
            return None

        path = os.path.join(manifest.repo_root, manifest_entry["path"])
        try:
            stat = os.stat(path)
        except OSError:
            del self._cache[key]
            return None

        size_matches = stat.st_size == entry.size_bytes
        # Only consider mtime match if it differs by more than 1s from insertion time,
        # to handle 1s mtime granularity on some FS.
        mtime_matches = stat.st_mtime == entry.last_modified

        needs_hash = True
        if size_matches and mtime_matches:
            # If the file's mtime is very close to when we inserted it into cache, it could have been
            # modified in the same second after our read. We force a hash check if inserted_at is close to mtime.
            # But inserted_at is monotonic, mtime is wall-clock. We can't compare them directly.
            # So we just trust size and mtime if they haven't changed from what we recorded when putting.
            needs_hash = False

        if needs_hash:
            try:
                with open(path, "rb") as f:
                    current_sha256 = hashlib.sha256(f.read()).hexdigest()
            except OSError:
                del self._cache[key]
                return None

            if current_sha256 != entry.sha256:
                del self._cache[key]
                return None

            # Update the cached stat info to avoid future hashes
            self._cache[key] = CacheEntry(
                body=entry.body,
                sha256=entry.sha256,
                inserted_at=entry.inserted_at,
                size_bytes=stat.st_size,
                last_modified=stat.st_mtime,
            )

        self._cache.move_to_end(key)
        return entry.body


    def put(self, id: str, view: str, body: ContextBody) -> None:
        manifest = self._get_manifest()
        manifest_entry = manifest.get(id)
        if not manifest_entry:
            return

        key = (id, view)
        self._cache[key] = CacheEntry(
            body=body,
            sha256=manifest_entry["sha256"],
            inserted_at=time.monotonic(),
            size_bytes=manifest_entry["size_bytes"],
            last_modified=manifest_entry["last_modified"],
        )
        self._cache.move_to_end(key)

        if len(self._cache) > self.maxsize:
            self._cache.popitem(last=False)


    def invalidate(self, id: str) -> None:
        keys_to_delete = [k for k in self._cache.keys() if k[0] == id]
        for k in keys_to_delete:
            del self._cache[k]
