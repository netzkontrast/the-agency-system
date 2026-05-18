## Spec

Plan/112-context-anchor-triad/spec.md

## Confidence

| # | Check | Pass when... |
|---|---|---|
| 1 | Prereqs | `context_manifest.json` and `anchor_triad.py` exist and projection helper is present. |
| 2 | FastMCP `mcp.resource` doc read | Familiarized with the syntax and implementation of FastMCP Code Mode and resources via web docs. |
| 3 | TDD implementation | Tests run perfectly under TDD rules. |
| 4 | Token constraint check | `test_boot_token_budget.py` is correctly extended to assert overhead <= 1.05x and log deferred doc tokens. |
| 5 | Output verified | `context_read` appropriately uses views with precise token estimates and truncation markers where necessary. |

**Total Score:** 1.0. All checks pass perfectly!

## Evidence

### Pytest outputs

```
=== Unit and Integration Tests ===
============================= test session starts ==============================
platform linux -- Python 3.12.13, pytest-9.0.3, pluggy-1.6.0 -- /home/jules/.pyenv/versions/3.12.13/bin/python
cachedir: .pytest_cache
rootdir: /app
plugins: asyncio-1.3.0, anyio-4.13.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 11 items

tests/integration/test_boot_token_budget.py::test_boot_byte_budget PASSED [  9%]
tests/integration/test_boot_token_budget.py::test_boot_token_budget PASSED [ 18%]
tests/integration/test_boot_token_budget.py::test_codemode_meta_tools_present PASSED [ 27%]
tests/unit/context/test_context_anchors.py::test_search_returns_at_most_limit_entries PASSED [ 36%]
tests/unit/context/test_context_anchors.py::test_describe_includes_views_block PASSED [ 45%]
tests/unit/context/test_context_anchors.py::test_read_summary_view_under_120_tokens PASSED [ 54%]
tests/unit/context/test_context_anchors.py::test_read_full_truncates_when_over_4000_tokens PASSED [ 63%]
tests/unit/context/test_context_anchors.py::test_read_with_fields_projects_json PASSED [ 72%]
tests/unit/context/test_context_anchors.py::test_read_unknown_id_raises_context_not_found PASSED [ 81%]
tests/unit/context/test_context_anchors.py::test_read_missing_view_falls_back_gracefully PASSED [ 90%]
tests/integration/test_context_anchor_triad.py::test_context_anchor_triad_end_to_end PASSED [100%]

============================== 11 passed in 6.26s ==============================
```

## Self-Review

**1. Did I drift from the spec?**
No, I adhered exactly to the spec. No custom `list_tools`/`search_tools` were added. The `test_boot_token_budget.py` correctly tests for the absolute maximum token allowance that corresponds to a `< 1.05` increment against the baseline (using a cap of 525 vs 500, but observing that it yields 344 tokens due to aggressive deferment of many tools). Deferred document tokens log output is 486509. The previous issue where `@apply_view` was incorrectly commented out has been completely resolved; instead, the root cause in `projection.py` signature type evaluation was fixed.

**2. What residual risk remains?**
The `.ncp.json` validator uses `jsonschema`, which may raise errors if users manually insert elements that don't match exactly. The `context_read` truncation marker calculation splits the string crudely using Python's `rfind` and may cause non-terminal boundaries if the target hits precisely in the middle of a Unicode combination character string.

**3. Preview view slice hitting mid-word:**
Currently `context_manifest.json` stores views natively up to exact byte ranges without accounting for full word semantics. Therefore, an indexer that generated `context_manifest.json` (from Spec 111) simply takes byte slices, which may land mid-word. I flag this here as instructed: the indexer in Spec 111 should be updated in a future issue to adjust `byte_length` in previews by stepping backward/forward to the nearest space or newline character.
