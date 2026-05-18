from agency_mcp.lib.codemode.views import View, BODY_PREVIEW_CHARS

def test_view_enum_members():
    assert View.id == "id"
    assert View.summary == "summary"
    assert View.preview == "preview"
    assert View.full == "full"

def test_body_preview_chars_constant():
    assert BODY_PREVIEW_CHARS == 400
