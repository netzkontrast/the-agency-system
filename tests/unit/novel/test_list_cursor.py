import pytest
from agency_mcp.handlers.novel._shared import encode_cursor, decode_cursor

def test_cursor_encode_decode():
    offset = 20
    limit = 10
    encoded = encode_cursor(offset, limit)
    assert encoded

    decoded = decode_cursor(encoded)
    assert decoded["offset"] == 20
    assert decoded["limit"] == 10

def test_cursor_decode_invalid():
    decoded = decode_cursor("invalid-base64-!")
    assert decoded["offset"] == 0
    assert decoded["limit"] == 20
