import json
import os
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = os.environ.get("JULES_API_BASE_URL", "https://jules.googleapis.com")


class JulesAPIError(RuntimeError):
    """Raised when the Jules REST API returns a non-2xx response.

    Carries the HTTP status code so callers can react to specific cases
    (e.g. 404 → 'session not found', not 'unknown error') instead of
    string-matching the message.
    """

    def __init__(self, status: int, message: str, body: str = ""):
        super().__init__(message)
        self.status = status
        self.body = body


def _api_key() -> str:
    key = os.environ.get("JULES_API_KEY", "")
    if not key:
        raise RuntimeError(
            "JULES_API_KEY is not set. Export it in the shell that launched "
            "Claude Code, then restart the session."
        )
    return key


def _request(method: str, path: str, body: dict | None = None) -> dict:
    url = f"{BASE_URL}{path}"
    headers = {"x-goog-api-key": _api_key()}
    data: bytes | None = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode("utf-8")
        except Exception:
            pass
        msg = _translate_http_error(e.code, err_body)
        raise JulesAPIError(e.code, msg, err_body) from None


def _translate_http_error(code: int, body: str) -> str:
    mapping = {
        400: "400 Bad Request — malformed payload. Body: ",
        401: "401 Unauthorized — JULES_API_KEY rejected. Re-export the key.",
        403: "403 Permission Denied — Jules cannot access the source. Connect the GitHub repo via the Jules GitHub app.",
        404: "404 Not Found — resource does not exist.",
        405: "405 Method Not Allowed — endpoint exists but does not accept this verb.",
        409: "409 Conflict — illegal state transition. Check current session state first.",
        429: "429 Quota Exceeded — pause polling and check billing/quota.",
    }
    if 500 <= code < 600:
        return f"5xx Server Error ({code}) — retryable. Body: {body[:300]}"
    base = mapping.get(code, f"HTTP {code}")
    if code == 400 and body:
        return base + body[:500]
    return base


def _paginate(path: str, params: dict, max_pages: int = 50) -> tuple[list[dict], str, int, bool]:
    """Walk pageToken across a list endpoint and concatenate the first array
    field in the response. Returns (items, last_page_token, pages_scanned, truncated).

    Stops early when nextPageToken is empty or max_pages is reached.
    """
    items: list[dict] = []
    token = ""
    pages = 0
    truncated = False
    array_key: str | None = None
    while pages < max_pages:
        q = dict(params)
        if token:
            q["pageToken"] = token
        sep = "&" if "?" in path else "?"
        raw = _request("GET", f"{path}{sep}{urllib.parse.urlencode(q)}")
        pages += 1
        if array_key is None:
            for k, v in raw.items():
                if isinstance(v, list):
                    array_key = k
                    break
            if array_key is None:
                break
        items.extend(raw.get(array_key, []) or [])
        token = raw.get("nextPageToken", "")
        if not token:
            return items, "", pages, False
    truncated = bool(token)
    return items, token, pages, truncated


def _short_id(name_or_id: str) -> str:
    """Accept 'sessions/123' or '123' and return '123'."""
    return name_or_id.rsplit("/", 1)[-1]
