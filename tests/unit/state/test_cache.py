import asyncio
import json
import os
import tempfile
import time
from pathlib import Path
import pytest
import jsonschema

from agency_mcp.state.cache import StateCache

@pytest.fixture
def temp_cache_dir(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        monkeypatch.setattr("agency_mcp.state.cache.STATE_CACHE_DIR", tmp_path)
        yield tmp_path

@pytest.fixture
def schema():
    schema_path = Path(__file__).parents[3] / "state" / "schema" / "state.schema.json"
    with open(schema_path) as f:
        return json.load(f)

@pytest.mark.asyncio
async def test_concurrent_writes_do_not_deadlock(temp_cache_dir):
    cache = StateCache()

    # Pre-populate to avoid schema validation issues later if empty file is loaded
    # but write() will handle the initialization if file doesn't exist

    async def write_music():
        await cache.write("music", {"_generated": "2023-01-01T00:00:00Z", "data": "music_data"})

    async def write_novel():
        await cache.write("novel", {"_generated": "2023-01-01T00:00:00Z", "data": "novel_data"})

    # Both writes should complete without deadlock
    await asyncio.wait_for(
        asyncio.gather(write_music(), write_novel()),
        timeout=2.0
    )

    snapshot = await cache.snapshot()
    assert "data" in snapshot["music"]
    assert "data" in snapshot["novel"]
    assert snapshot["music"]["data"] == "music_data"
    assert snapshot["novel"]["data"] == "novel_data"


@pytest.mark.asyncio
async def test_mtime_change_triggers_reload(temp_cache_dir):
    cache = StateCache()
    await cache.write("music", {"_generated": "T0"})

    snapshot1 = await cache.snapshot()
    assert snapshot1["music"]["_generated"] == "T0"

    # Simulate an external process modifying the file
    state_file = temp_cache_dir / "state.json"
    with open(state_file, "r") as f:
        data = json.load(f)

    data["music"]["_generated"] = "T1"

    with open(state_file, "w") as f:
        json.dump(data, f)

    # Bump mtime
    new_time = time.time() + 10
    os.utime(state_file, (new_time, new_time))

    snapshot2 = await cache.snapshot()
    assert snapshot2["music"]["_generated"] == "T1"


@pytest.mark.asyncio
async def test_namespace_isolation(temp_cache_dir):
    cache = StateCache()

    # Initialize both namespaces
    await cache.write("music", {"_generated": "T0"})
    await cache.write("novel", {"_generated": "T0"})

    # Write to music only
    await cache.write("music", {"_generated": "T1"})

    snapshot = await cache.snapshot()
    assert snapshot["music"]["_generated"] == "T1"
    assert snapshot["novel"]["_generated"] == "T0"


@pytest.mark.asyncio
async def test_state_dict_validates_against_schema(temp_cache_dir, schema):
    cache = StateCache()
    await cache.write("music", {"_generated": "2023-01-01T00:00:00Z"})

    snapshot = await cache.snapshot()

    # Check keys
    expected_keys = {"music", "novel", "jules", "agentic", "_version"}
    assert set(snapshot.keys()) == expected_keys

    # Validate against schema
    jsonschema.validate(instance=snapshot, schema=schema, format_checker=jsonschema.FormatChecker())
