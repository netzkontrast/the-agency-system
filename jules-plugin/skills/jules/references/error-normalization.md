This file provides error handling and normalisation rules. Load this when a Jules API request fails or returns an HTTP error code to understand how to interpret and report it.


Trap HTTP errors and translate, don't dump:

| HTTP | Meaning | What to tell the user |
|---|---|---|
| `400` | Malformed payload | Echo the API's error message; check `--source` / `--branch` formats. |
| `401` | Invalid `JULES_API_KEY` | "Jules rejected the API key. Re-export `JULES_API_KEY` and try again." |
| `403` | No access to the source | "Jules cannot access `<source>`. Make sure the GitHub repo is connected via the Jules GitHub app." |
| `404` | Unknown session | "No session `<id>` found. Use `/jules list` to see active sessions." |
| `409` | Illegal state transition | E.g. approving a session that isn't awaiting approval. Run `/jules status` first. |
| `429` | Quota exceeded | Stop polling. Tell the user to wait or check their billing/quota in the Jules console. |
| `5xx` | Server error | Retryable. Suggest waiting a minute. Do not auto-retry more than once. |

Use `curl -sS -o "$TMP" -w "%{http_code}"` so the status code is emitted,
and inspect it. Then parse the body from the tempfile with `jq < "$TMP"`.

---
