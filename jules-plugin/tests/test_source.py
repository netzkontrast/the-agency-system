import pytest
from unittest.mock import patch

from jules_mcp.source import _coerce_source

@patch("jules_mcp.source._resolve_github_source")
def test_coerce_source_opaque(mock_resolve):
    # opaque sources are returned unchanged and not resolved
    assert _coerce_source("sources/123") == "sources/123"
    mock_resolve.assert_not_called()

@patch("jules_mcp.source._resolve_github_source")
def test_coerce_source_shorthand(mock_resolve):
    mock_resolve.return_value = {"source": "sources/xyz"}
    assert _coerce_source("owner/repo") == "sources/xyz"
    mock_resolve.assert_called_once_with("owner", "repo")

@patch("jules_mcp.source._resolve_github_source")
def test_coerce_source_github_url(mock_resolve):
    mock_resolve.return_value = {"source": "sources/xyz"}
    
    assert _coerce_source("https://github.com/owner/repo.git") == "sources/xyz"
    mock_resolve.assert_called_with("owner", "repo")
    
    assert _coerce_source("github.com/owner/repo") == "sources/xyz"
    
@patch("jules_mcp.source._resolve_github_source")
def test_coerce_source_jules_github_prefix(mock_resolve):
    mock_resolve.return_value = {"source": "sources/xyz"}
    assert _coerce_source("sources/github/owner/repo") == "sources/xyz"
    mock_resolve.assert_called_with("owner", "repo")

@patch("jules_mcp.source._resolve_github_source")
def test_coerce_source_errors(mock_resolve):
    with pytest.raises(RuntimeError, match="source is required"):
        _coerce_source("")
        
    with pytest.raises(RuntimeError, match="could not parse source"):
        _coerce_source("invalid")
        
    mock_resolve.return_value = {"error": "no Jules source connected"}
    with pytest.raises(RuntimeError, match="no Jules source connected"):
        _coerce_source("owner/repo")
