import pytest
import os
import time
import hashlib
from typing import Any
from agency_mcp.lib.codemode.context_cache import ContextCache, ContextBody
from agency_mcp.lib.codemode.context_manifest import ContextManifest

@pytest.fixture
def mock_manifest(tmp_path):
    f1 = tmp_path / "f1.txt"
    f1.write_text("hello")
    f2 = tmp_path / "f2.txt"
    f2.write_text("world")


    class MockManifest:
        repo_root = str(tmp_path)
        def __init__(self):
            import hashlib
            self.sha1 = hashlib.sha256(open(str(self.repo_root) + "/f1.txt", "rb").read()).hexdigest()
            self.m1 = os.stat(str(self.repo_root) + "/f1.txt").st_mtime
            self.sha2 = hashlib.sha256(open(str(self.repo_root) + "/f2.txt", "rb").read()).hexdigest()
            self.m2 = os.stat(str(self.repo_root) + "/f2.txt").st_mtime

        def get(self, id: str) -> dict[str, Any] | None:
            if id == "id1":
                return {"path": "f1.txt", "sha256": self.sha1, "size_bytes": 5, "last_modified": self.m1}
            if id == "id2":
                return {"path": "f2.txt", "sha256": self.sha2, "size_bytes": 5, "last_modified": self.m2}
            return None

    return MockManifest()

def test_get_miss_returns_none(mock_manifest):
    cache = ContextCache(manifest=mock_manifest)
    assert cache.get("id1", "preview") is None

def test_put_then_get_hit(mock_manifest):
    cache = ContextCache(manifest=mock_manifest)
    body = ContextBody("hello", False)
    cache.put("id1", "preview", body)
    hit = cache.get("id1", "preview")
    assert hit is not None
    assert hit.content == "hello"

def test_ttl_expiry_returns_none(mock_manifest):
    cache = ContextCache(default_ttl_s=0, manifest=mock_manifest)
    cache.put("id1", "preview", ContextBody("hello", False))
    time.sleep(0.01)
    assert cache.get("id1", "preview") is None

def test_sha256_mismatch_invalidates(mock_manifest, tmp_path):
    cache = ContextCache(manifest=mock_manifest)
    cache.put("id1", "preview", ContextBody("hello", False))

    # Modify file directly to trigger sha256 mismatch
    f1 = tmp_path / "f1.txt"
    f1.write_text("modified")

    # Update mtime explicitly so it thinks it changed (or size changed)
    # The size definitely changed (5 vs 8 bytes), so it will re-hash and see mismatch
    assert cache.get("id1", "preview") is None

def test_lru_eviction_when_maxsize_exceeded(mock_manifest):
    cache = ContextCache(maxsize=1, manifest=mock_manifest)
    cache.put("id1", "preview", ContextBody("hello", False))
    cache.put("id2", "preview", ContextBody("world", False))
    assert cache.get("id1", "preview") is None
    assert cache.get("id2", "preview") is not None

def test_get_does_not_burn_read_when_size_and_mtime_match(mock_manifest, monkeypatch):
    cache = ContextCache(manifest=mock_manifest)
    cache.put("id1", "preview", ContextBody("hello", False))

    reads = 0
    original_open = open
    def mock_open(*args, **kwargs):
        nonlocal reads
        reads += 1
        return original_open(*args, **kwargs)

    monkeypatch.setattr("builtins.open", mock_open)

    hit = cache.get("id1", "preview")
    assert hit is not None
    assert reads == 0
