from pathlib import Path
from typing import Any
import yaml

CONFIG_PATH = Path.home() / ".agency-system" / "config.yaml"


def shared_get_config() -> dict[str, Any]:
    try:
        if CONFIG_PATH.exists():
            content = CONFIG_PATH.read_text(encoding="utf-8")
            data = yaml.safe_load(content) or {}
            return {
                "ok": True,
                "data": data,
                "warnings": [],
                "artefacts_written": [],
                "next_suggested_tools": [],
            }
        else:
            return {
                "ok": True,
                "data": {},
                "warnings": ["config.yaml not found, returning empty"],
                "artefacts_written": [],
                "next_suggested_tools": [],
            }
    except Exception as e:
        return {
            "ok": False,
            "data": {},
            "warnings": [f"Error reading config: {str(e)}"],
            "artefacts_written": [],
            "next_suggested_tools": [],
        }
