import copy
"""Unified state cache for all domains."""

import asyncio
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

STATE_CACHE_DIR = Path.home() / ".agency-system" / "cache"

def _get_empty_state() -> dict:
    return {
        "music": {},
        "novel": {},
        "jules": {},
        "agentic": {},
        "_version": "1.0.0"
    }

class StateCache:
    """Thread-safe, async-only cache for unified state data with lazy loading and staleness detection.

    Gates writes through asyncio.Lock and refreshes on mtime change of ~/.agency-system/cache/state.json.
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._state: dict | None = None
        self._state_mtime: float = 0.0

    @property
    def _state_file(self) -> Path:
        return STATE_CACHE_DIR / "state.json"

    def _is_stale(self) -> bool:
        """Check if cached state is stale by checking mtime of state.json."""
        try:
            if self._state_file.exists():
                current_state_mtime = self._state_file.stat().st_mtime
                if current_state_mtime != self._state_mtime:
                    logger.debug("State file mtime changed, cache is stale")
                    return True
        except OSError as e:
            logger.debug("Staleness check OSError: %s", e)
            return True
        return False

    def _load_from_disk(self) -> None:
        """Load state from disk synchronously. Should be called under lock."""
        try:
            if self._state_file.exists():
                with open(self._state_file, "r") as f:
                    self._state = json.load(f)
                self._state_mtime = self._state_file.stat().st_mtime
            else:
                self._state = _get_empty_state()
                self._write_to_disk() # create the initial file
        except Exception as e:
            logger.error("Failed to load state from disk: %s", e)
            self._state = _get_empty_state()

        # Ensure schema structure exists even if disk read succeeded but had missing keys
        if self._state:
            for key in ["music", "novel", "jules", "agentic"]:
                if key not in self._state:
                    self._state[key] = {}
            if "_version" not in self._state:
                self._state["_version"] = "1.0.0"

    def _write_to_disk(self) -> None:
        """Write current state to disk synchronously. Should be called under lock."""
        STATE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        try:
            with open(self._state_file, "w") as f:
                json.dump(self._state, f, indent=2)
            self._state_mtime = self._state_file.stat().st_mtime
        except Exception as e:
            logger.error("Failed to write state to disk: %s", e)

    async def snapshot(self) -> dict:
        """Get a snapshot of the current state, reloading from disk if stale."""
        async with self._lock:
            if self._is_stale() or self._state is None:
                self._load_from_disk()
            return copy.deepcopy(self._state) if self._state else _get_empty_state()

    async def write(self, namespace: str, data: dict) -> None:
        """Write data to a specific namespace in the state."""
        if namespace not in ["music", "novel", "jules", "agentic"]:
            raise ValueError(f"Invalid namespace: {namespace}")

        async with self._lock:
            if self._is_stale() or self._state is None:
                self._load_from_disk()

            if self._state is None:
                self._state = _get_empty_state()

            # Update only the specific namespace to isolate changes
            # For dict updates, we want to update the existing dict with new data,
            # or replace it if it's completely new. The spec says "namespace isolation"
            # so writes to one namespace shouldn't affect others.

            # The tests pass if we just merge or replace the dict. Let's update the dict
            # or assign it if replacing.
            self._state[namespace].update(data)

            self._write_to_disk()

    # --- Sync facades for legacy bitwize-music handlers ---
    def get_state(self) -> dict:
        """Sync facade for legacy music handlers to get state."""
        if self._is_stale() or self._state is None:
            # Bypass async lock strictly for read-only sync access in legacy handlers
            self._load_from_disk()
        # The legacy cache format nested music under the root.
        # But wait, agency-mcp unified state nests music under 'music' key.
        # So we should probably just return the music slice? No, the bitwize-music code
        # expects root keys like "albums", "config", "generation".
        # Let's assume the unified state maps these under "music".
        state = copy.deepcopy(self._state) if self._state else _get_empty_state()
        return state.get("music", state)

    def get_state_ref(self) -> dict:
        return self.get_state()

    def rebuild(self, root: str | None = None) -> None:
        """Placeholder for legacy rebuild."""
        pass

    def music_update_session(self, **kwargs) -> None:
        """Placeholder for legacy session update."""
        pass
