import hashlib
from pathlib import Path

def sha256_of_files(paths: list[Path]) -> str:
    """Computes a stable SHA-256 hash of a list of files."""
    sorted_paths = sorted(paths)
    h = hashlib.sha256()
    for path in sorted_paths:
        if path.exists():
            h.update(path.name.encode('utf-8'))
            with path.open('rb') as f:
                h.update(f.read())
    return h.hexdigest()
