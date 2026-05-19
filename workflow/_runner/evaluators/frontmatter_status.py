from typing import Dict, Any

def assert_status_equals(envelope: dict, args: Dict[str, Any]) -> dict:
    # mock implementation
    expected = args.get("expected")
    return {"ok": True, "message": f"mock pass for expected {expected}"}
