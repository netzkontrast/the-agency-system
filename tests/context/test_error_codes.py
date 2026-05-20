"""v0.2 follow-up #3 — error-code catalogue smoke test.

* Every constant in `context._shared.error_codes` is an UPPER_SNAKE_CASE
  string whose value equals its name.
* No code-producer site under `agentic/_harness/` or `workflow/_runner/`
  hardcodes an `error.code` string literal — they all import from the
  catalogue. The catalogue is the single source of truth.
"""

import re
from pathlib import Path

from context._shared import error_codes


REPO_ROOT = Path(__file__).resolve().parents[2]
SCAN_DIRS = [
    REPO_ROOT / "agentic" / "_harness",
    REPO_ROOT / "workflow" / "_runner",
]
INLINE_CODE_RE = re.compile(r'"code":\s*"([A-Z][A-Z_]+)"')


def test_constants_match_their_string_values():
    for name in dir(error_codes):
        if name.startswith("_"):
            continue
        value = getattr(error_codes, name)
        if not isinstance(value, str) or not name.isupper():
            continue
        assert value == name, (
            f"error_codes.{name} has value {value!r}; "
            f"convention requires the value to equal the constant name."
        )


def test_no_inline_error_codes_in_producers():
    offenders = []
    for d in SCAN_DIRS:
        for py in d.rglob("*.py"):
            if "__pycache__" in py.parts:
                continue
            text = py.read_text(encoding="utf-8")
            for m in INLINE_CODE_RE.finditer(text):
                offenders.append((py.relative_to(REPO_ROOT), m.group(1)))
    assert not offenders, (
        "Inline error codes found — import from context._shared.error_codes "
        f"instead. Offenders: {offenders}"
    )
