import pytest
from agency_mcp.handlers.novel.coherence import novel_coherence_check, novel_coherence_correct

def test_dynamic_pair_reciprocity_pass():
    res = novel_coherence_check("good_work")
    assert res["checks"]["dynamic_pair_reciprocity"]["ok"] == True

def test_dynamic_pair_reciprocity_fail():
    res = novel_coherence_check("broken_work_pair_reciprocity")
    assert res["checks"]["dynamic_pair_reciprocity"]["ok"] == False

def test_ktad_coherence_pass():
    res = novel_coherence_check("good_work")
    assert res["checks"]["ktad_coherence"]["ok"] == True

def test_ktad_coherence_fail():
    res = novel_coherence_check("broken_work_ktad_coverage")
    assert res["checks"]["ktad_coherence"]["ok"] == False

def test_throughline_uniqueness_pass():
    res = novel_coherence_check("good_work")
    assert res["checks"]["throughline_uniqueness"]["ok"] == True

def test_throughline_uniqueness_fail():
    res = novel_coherence_check("broken_work_throughline_partition")
    assert res["checks"]["throughline_uniqueness"]["ok"] == False

def test_signpost_ordering_pass():
    res = novel_coherence_check("good_work")
    assert res["checks"]["signpost_ordering"]["ok"] == True

def test_signpost_ordering_fail():
    res = novel_coherence_check("broken_work_signpost_permutation")
    assert res["checks"]["signpost_ordering"]["ok"] == False

def test_resolve_mirror_pass():
    res = novel_coherence_check("good_work")
    assert res["checks"]["resolve_mirror"]["ok"] == True

def test_mental_sex_pass():
    res = novel_coherence_check("good_work")
    assert res["checks"]["mental_sex"]["ok"] == True

def test_growth_pass():
    res = novel_coherence_check("good_work")
    assert res["checks"]["growth"]["ok"] == True

def test_driver_pass():
    res = novel_coherence_check("good_work")
    assert res["checks"]["driver"]["ok"] == True

def test_outcome_pass():
    res = novel_coherence_check("good_work")
    assert res["checks"]["outcome"]["ok"] == True

def test_judgment_pass():
    res = novel_coherence_check("good_work")
    assert res["checks"]["judgment"]["ok"] == True

def test_limit_pass():
    res = novel_coherence_check("good_work")
    assert res["checks"]["limit"]["ok"] == True

def test_coherence_correct_dry_run():
    res = novel_coherence_correct("broken_work_pair_reciprocity", autofix={"dynamic_pair_reciprocity"}, dry_run=True)
    assert res["would_apply"] == True
