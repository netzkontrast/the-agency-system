import os
import time
import hashlib
import threading
import subprocess
from typing import Callable, Literal, NamedTuple, Optional
from agency_mcp.lib.codemode.context_manifest import ContextManifest
import fnmatch
from pathlib import Path

class ChangeEvent(NamedTuple):
    id: str
    kind: Literal["modified", "deleted", "added"]
    old_sha256: Optional[str]
    new_sha256: Optional[str]

class ContextWatcher:
    """Polls manifest's tracked paths to detect changes and emit events."""

    def __init__(self, manifest: ContextManifest, on_change: Callable[[ChangeEvent], None], poll_interval_s: float = 5.0, mcp=None):
        self._manifest = manifest
        self._on_change = on_change
        self._poll_interval_s = poll_interval_s
        self._mcp = mcp

        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    def start(self) -> None:
        if self._thread is not None:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join()
            self._thread = None

    def _get_tracked_files(self) -> set[str]:
        # Emulate the glob logic from build_context_manifest
        repo_root = Path(self._manifest.repo_root)
        files = set()

        # Spec 108: Plan/**/*.md, Plan/**/*.json, _lessons-learned/**/*.md, overrides/**/*.json, reference/**/*.md
        patterns = [
            "Plan/**/*.md", "Plan/**/*.json",
            "_lessons-learned/**/*.md",
            "overrides/**/*.json",
            "reference/**/*.md"
        ]

        for pattern in patterns:
            for p in repo_root.glob(pattern):
                if p.is_file():
                    files.add(str(p.relative_to(repo_root)))
        return files

    def _derive_id(self, rel_path: str) -> str:
        # Based on build_context_manifest.py logic
        p = Path(rel_path)
        base = p.with_suffix("").as_posix()
        # simplified fallback for derive_id
        # In reality, the rebuild subprocess will assign the exact ID. We just need a placeholder ID.
        parts = base.split("/")
        if parts[0] == "Plan":
            return f"plan:{'-'.join(parts[1:])}:spec"
        return f"file:{base.replace('/', ':')}"

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            time.sleep(self._poll_interval_s)
            if self._stop_event.is_set():
                break

            self.poll_once()

    def _compute_sha256(self, path: str) -> str:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def poll_once(self) -> None:
        repo_root = self._manifest.repo_root
        events: list[ChangeEvent] = []

        manifest_paths = {}
        for entry in self._manifest.entries:
            manifest_paths[entry["path"]] = entry

        # Check for modified or deleted
        for path, entry in manifest_paths.items():
            full_path = os.path.join(repo_root, path)
            try:
                stat = os.stat(full_path)
                if stat.st_size != entry["size_bytes"] or stat.st_mtime != entry["last_modified"]:
                    new_sha = self._compute_sha256(full_path)
                    if new_sha != entry["sha256"]:
                        events.append(ChangeEvent(entry["id"], "modified", entry["sha256"], new_sha))
                        # Update in-memory to prevent repeated events before rebuild completes
                        entry["size_bytes"] = stat.st_size
                        entry["last_modified"] = stat.st_mtime
                        entry["sha256"] = new_sha
            except OSError:
                events.append(ChangeEvent(entry["id"], "deleted", entry["sha256"], None))

        # Check for added
        actual_files = self._get_tracked_files()
        for path in actual_files:
            if path not in manifest_paths:
                full_path = os.path.join(repo_root, path)
                try:
                    new_sha = self._compute_sha256(full_path)
                    derived_id = self._derive_id(path)
                    events.append(ChangeEvent(derived_id, "added", None, new_sha))
                    # Prevent repeated events
                    self._manifest.entries.append({
                        "id": derived_id,
                        "path": path,
                        "sha256": new_sha,
                        "size_bytes": os.stat(full_path).st_size,
                        "last_modified": os.stat(full_path).st_mtime
                    })
                except OSError:
                    pass

        needs_rebuild = False
        for event in events:
            # Emit event, but ensure we don't hold any locks
            self._on_change(event)
            if event.kind in ("added", "deleted"):
                needs_rebuild = True

        if needs_rebuild:
            self._trigger_rebuild()

    def _trigger_rebuild(self) -> None:
        # In a daemon thread, execute build_context_manifest.py subprocess
        try:
            # The manifest path is known
            # e.g., servers/agency-mcp/src/agency_mcp/codemode/context_manifest.json
            manifest_path = Path(self._manifest.repo_root) / "servers/agency-mcp/src/agency_mcp/codemode/context_manifest.json"
            builder_script = Path(self._manifest.repo_root) / "bin/build_context_manifest.py"
            if not builder_script.exists():
                return

            res = subprocess.run(
                ["python", str(builder_script), "--out", str(manifest_path)],
                capture_output=True,
                text=True,
                cwd=self._manifest.repo_root
            )
            if res.returncode == 0:
                # Success: reload in-memory manifest
                from agency_mcp.lib.codemode.context_manifest import load_context_manifest
                from agency_mcp.handlers.context.resources import _manifest_cache
                new_manifest = load_context_manifest(str(manifest_path))
                import agency_mcp.handlers.context.resources as context_resources
                context_resources._manifest_cache = new_manifest
                self._manifest = new_manifest
            else:
                if self._mcp and hasattr(self._mcp, "logger"):
                    self._mcp.logger.warning(f"Manifest rebuild failed: {res.stderr}")
        except Exception as e:
            if self._mcp and hasattr(self._mcp, "logger"):
                self._mcp.logger.warning(f"Exception during manifest rebuild: {e}")
