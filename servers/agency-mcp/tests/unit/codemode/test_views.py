from agency_mcp.lib.codemode.views import View, BODY_PREVIEW_CHARS

def test_view_enum():
    assert View.id == "id"
    assert View.summary == "summary"
    assert View.preview == "preview"
    assert View.full == "full"

    assert BODY_PREVIEW_CHARS == 400
