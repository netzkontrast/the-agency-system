import pytest
from jules_mcp.trim import apply_fields, apply_summary, apply_list_trim

def test_apply_fields():
    obj = {"a": 1, "b": 2, "c": 3}
    assert apply_fields(obj, "*") == obj
    assert apply_fields(obj, "a,c") == {"a": 1, "c": 3}
    assert apply_fields(obj, "d") == {}
    assert apply_fields(obj, "a,  b  ") == {"a": 1, "b": 2}
    
def test_apply_list_trim():
    items = [{"a": 1, "b": 2}, {"a": 3, "c": 4}]
    assert apply_list_trim(items, "a") == [{"a": 1}, {"a": 3}]

def test_apply_summary():
    # planGenerated
    a1 = {
        "name": "sessions/1/activities/a1",
        "originator": "JULES",
        "planGenerated": {
            "plan": {"steps": [{"title": "step1"}, {"title": "step2"}]}
        }
    }
    s1 = apply_summary(a1)
    assert s1["id"] == "a1"
    assert s1["originator"] == "JULES"
    assert s1["kind"] == "planGenerated"
    assert s1["summary"] == "step1; step2"
    
    # agentMessaged
    a2 = {
        "id": "a2",
        "agentMessaged": {"agentMessage": "hello world"}
    }
    s2 = apply_summary(a2)
    assert s2["kind"] == "agentMessaged"
    assert s2["summary"] == "hello world"

    # unknown
    a3 = {
        "name": "a3",
        "someUnknownField": {"data": 123}
    }
    s3 = apply_summary(a3)
    assert s3["kind"] == "someUnknownField"
    assert s3["summary"] == "(unrecognized activity shape)"

