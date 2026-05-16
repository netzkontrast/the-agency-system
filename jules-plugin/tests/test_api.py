import urllib.error
from unittest.mock import patch, MagicMock

import pytest

from jules_mcp.api import JulesAPIError, _short_id, _translate_http_error, _request

def test_jules_api_error_shape():
    err = JulesAPIError(404, "Not Found", '{"error": "not found"}')
    assert err.status == 404
    assert str(err) == "Not Found"
    assert err.body == '{"error": "not found"}'

def test_short_id():
    assert _short_id("sessions/123") == "123"
    assert _short_id("123") == "123"
    assert _short_id("sources/github/owner/repo") == "repo"
    assert _short_id("") == ""

def test_translate_http_error():
    assert "400 Bad Request" in _translate_http_error(400, "oops")
    assert "oops" in _translate_http_error(400, "oops")
    assert "401 Unauthorized" in _translate_http_error(401, "")
    assert "403 Permission Denied" in _translate_http_error(403, "")
    assert "404 Not Found" in _translate_http_error(404, "")
    assert "405 Method Not Allowed" in _translate_http_error(405, "")
    assert "409 Conflict" in _translate_http_error(409, "")
    assert "429 Quota Exceeded" in _translate_http_error(429, "")
    assert "5xx Server Error" in _translate_http_error(503, "internal error")
    assert "HTTP 418" in _translate_http_error(418, "")

@patch("jules_mcp.api.urllib.request.urlopen")
@patch.dict("os.environ", {"JULES_API_KEY": "test-key"})
def test_request_success(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = b'{"hello": "world"}'
    mock_urlopen.return_value.__enter__.return_value = mock_resp
    
    result = _request("GET", "/test")
    assert result == {"hello": "world"}
    
@patch("jules_mcp.api.urllib.request.urlopen")
@patch.dict("os.environ", {"JULES_API_KEY": "test-key"})
def test_request_error(mock_urlopen):
    mock_err_resp = MagicMock()
    mock_err_resp.read.return_value = b'{"error": "bad"}'
    mock_err = urllib.error.HTTPError("url", 400, "Bad Request", {}, mock_err_resp)
    mock_urlopen.side_effect = mock_err
    
    with pytest.raises(JulesAPIError) as exc_info:
        _request("GET", "/test")
        
    assert exc_info.value.status == 400
    assert "400 Bad Request" in str(exc_info.value)
    assert exc_info.value.body == '{"error": "bad"}'

