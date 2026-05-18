import sys
import pytest

def test_upload_to_cloud_raises_import_error_not_sys_exit(monkeypatch):
    import agency_mcp.tools.cloud.upload_to_cloud
    monkeypatch.setitem(sys.modules, "yaml", None)
    monkeypatch.setitem(sys.modules, "boto3", None)

    with pytest.raises(ImportError):
        import importlib
        importlib.reload(agency_mcp.tools.cloud.upload_to_cloud)
