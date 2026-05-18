import pkgutil
import importlib
import sys
from pathlib import Path

# Add project root to sys.path
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT / "servers" / "agency-mcp" / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "servers" / "agency-mcp" / "src"))

import agency_mcp.tools

def test_every_submodule_imports():
    failed = []
    for _, name, _ in pkgutil.walk_packages(agency_mcp.tools.__path__, prefix='agency_mcp.tools.'):
        # We simulate the case where some optional dependencies are not installed
        try:
            importlib.import_module(name)
        except (Exception, SystemExit) as e:
            failed.append(f"{name}: {e}")
    assert not failed, f"Failed imports:\n" + "\n".join(failed)
