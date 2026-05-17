import pkgutil
import importlib
import agency_mcp.tools
def test_every_submodule_imports():
    failed = []
    for _, name, _ in pkgutil.walk_packages(agency_mcp.tools.__path__, prefix='agency_mcp.tools.'):
        try:
            importlib.import_module(name)
        except Exception as e:
            failed.append(f"{name}: {e}")
    assert not failed, f"Failed imports:\n" + "\n".join(failed)
