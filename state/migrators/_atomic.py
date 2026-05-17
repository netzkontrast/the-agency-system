import json
import os
import tempfile
from pathlib import Path

def atomic_write_json(path: Path, payload: dict) -> None:
    """Writes a JSON payload atomically using os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)

    # Create tempfile in the same directory to ensure it's on the same filesystem
    # so os.replace is atomic.
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False, suffix='.tmp', mode='w', encoding='utf-8') as f:
            tmp_path = Path(f.name)
            f.write(json.dumps(payload, indent=2, sort_keys=True))
            f.flush()
            os.fsync(f.fileno())

        # Replace atomically
        os.replace(tmp_path, path)
    except Exception:
        if tmp_path and tmp_path.exists():
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        raise
