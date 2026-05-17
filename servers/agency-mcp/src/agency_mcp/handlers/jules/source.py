from ._shared import _paginate

def _resolve_github_source(owner: str, repo: str) -> dict:
    """Lookup the opaque sources/{id} for a GitHub owner/repo.

    Returns the same shape as the public tool wrapper below.
    """
    items, _, _, _ = _paginate("/v1alpha/sources", {"pageSize": 100}, max_pages=10)
    for s in items:
        gh = s.get("githubRepo") or {}
        if gh.get("owner") == owner and gh.get("repo") == repo:
            return {
                "source": s.get("name", ""),
                "github": {"owner": owner, "repo": repo},
            }
    return {
        "error": (
            f"no Jules source connected for github.com/{owner}/{repo}. "
            "Connect the repository via the Jules GitHub app, then retry."
        )
    }

def _coerce_source(source: str) -> str:
    """Translate a user-supplied source string into the opaque form Jules expects.

    Accepts:
      - 'sources/<opaque>'              → returned unchanged (correct form)
      - 'owner/repo'                    → resolved via sources.list
      - 'sources/github/owner/repo'     → owner/repo extracted, resolved
      - 'https://github.com/owner/repo' → owner/repo extracted, resolved

    Raises JulesAPIError-like RuntimeError when no matching connected source
    is found, so the caller gets an actionable message instead of a 400 from
    the upstream API.
    """
    s = (source or "").strip()
    if not s:
        raise RuntimeError(
            "source is required. Pass 'sources/<id>', 'owner/repo', or a "
            "GitHub URL; use jules_resolve_source to look it up first."
        )
    if s.startswith("sources/") and s.count("/") == 1:
        return s
    owner: str | None = None
    repo: str | None = None
    if s.startswith("sources/github/"):
        rest = s[len("sources/github/"):]
        if rest.count("/") == 1:
            owner, repo = rest.split("/", 1)
    elif "github.com" in s:
        path = s.split("github.com", 1)[1].lstrip(":/").rstrip("/")
        if path.endswith(".git"):
            path = path[:-4]
        parts = path.split("/")
        if len(parts) >= 2:
            owner, repo = parts[0], parts[1]
    elif "/" in s and not s.startswith("sources/"):
        parts = s.split("/")
        if len(parts) == 2:
            owner, repo = parts
    if owner and repo:
        resolved = _resolve_github_source(owner, repo)
        if "error" in resolved:
            raise RuntimeError(resolved["error"])
        return resolved["source"]
    raise RuntimeError(
        f"could not parse source '{source}'. Expected 'sources/<id>', "
        "'owner/repo', or a github.com URL."
    )
