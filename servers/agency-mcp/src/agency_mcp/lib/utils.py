import json
from pathlib import Path
from typing import Any

def load_json_with_sha_header(path: Path) -> Any:
    """Helper to consistently load JSON files which may have a sibling .sha file or a header."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
