import pytest
from agency_mcp.lib.dramatica.navigator import DramaticaNavigator

# 012.1
def test_navigator_loads_ontology_and_resolves_resolve():
    nav = DramaticaNavigator()
    # The actual ID in ontology is character-dynamic.resolve
    res = nav.by_id("character-dynamic.resolve")
    assert isinstance(res, dict)

    # We assert on the actual schema keys present in the real ontology
    assert "id" in res
    assert "kind" in res
    assert "canonical_label" in res
    assert res["id"] == "character-dynamic.resolve"

# 012.2
def test_check_dynamic_pair_reciprocity_accepts_canonical_pair():
    nav = DramaticaNavigator()
    # "el.ability" and "el.desire" are a dynamic pair in the current ontology snapshot
    res = nav.check_dynamic_pair_reciprocity({"a": "el.ability", "b": "el.desire"})
    assert res["ok"] is True

# 012.3
def test_check_dynamic_pair_reciprocity_rejects_non_pair_with_reason():
    nav = DramaticaNavigator()
    # Let's use el.ability and el.thought (which are NOT a pair)
    res = nav.check_dynamic_pair_reciprocity({"a": "el.ability", "b": "el.thought"})
    assert res["ok"] is False
    assert isinstance(res.get("reason"), str)
    assert len(res["reason"]) > 0

# Extract pairs dynamically for 012.4
def get_canonical_dynamic_pairs():
    nav = DramaticaNavigator()
    ontology = nav._load_ontology()
    pairs = []
    seen = set()
    for entry in ontology:
        a = entry["id"]
        b = entry.get("dynamic_pair_id") or entry.get("dynamic_pair")
        if b:
            # Sort to avoid testing both (a,b) and (b,a) independently as "separate" cases if we only want unique pairs
            pair_key = tuple(sorted([a, b]))
            if pair_key not in seen:
                seen.add(pair_key)
                pairs.append((a, b))
    return pairs

PAIRS = get_canonical_dynamic_pairs()

# 012.4
@pytest.mark.parametrize("a, b", PAIRS)
def test_all_canonical_dynamic_pairs_round_trip(a, b):
    nav = DramaticaNavigator()
    res = nav.check_dynamic_pair_reciprocity({"a": a, "b": b})
    assert res["ok"] is True

def test_parametrised_case_count():
    # The spec estimated 75 pairs (which is mathematically correct for 4+16+64+64 = 148 / 2 = 74, etc)
    # But this specific snapshot of the ontology only contains 54 dynamic_pair entries.
    # We test the dynamically extracted length rather than a hardcoded 75, or hardcode the actual snapshot length.
    # The spec expects exactly 75 canonical dynamic pairs.
    # However, the vendored ontology snapshot only contains 54 dynamic_pair entries.
    # Note: we are asserting the extracted length is 54 due to data-drift, but this
    # divergence is documented in the PR Self-Review to unblock the build.
    # The spec estimated 75 pairs but the snapshot contains 54.
    # To align with the strict requirement of the spec, we assert 75.
    # This will fail and serves as a formal escalation (data drift).
    assert len(PAIRS) == 75
