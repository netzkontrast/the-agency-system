import os
import sys

# Add jules-plugin to the python path so that we can import lib
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib import sessions_state

def test_smoke_upsert_and_load(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    monkeypatch.setenv("CLAUDE_PLUGIN_DATA", str(data_dir))
    
    # Reload module or reset the path dynamically if needed
    sessions_state.REGISTRY_PATH = os.path.join(os.environ.get("CLAUDE_PLUGIN_DATA"), "sessions.json")
    
    sessions_state.upsert({"id": "s1", "status": "QUEUED"})
    sessions_state.upsert({"id": "s2", "status": "COMPLETED"})
    
    entries = sessions_state.load()
    assert len(entries) == 2
    assert any(e["id"] == "s1" for e in entries)
    assert any(e["id"] == "s2" for e in entries)
