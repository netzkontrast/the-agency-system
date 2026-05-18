import inspect
from session_log_mcp.server import create_mcp

def test_tool_signatures():
    mcp = create_mcp()
    import asyncio; tools = {t.name: t for t in asyncio.run(mcp.list_tools())}

    # 1. session_log_record(kind, payload, spec_id?, session_id?, pr_number?, actor?, ts?)
    sig_record = inspect.signature(tools["session_log_record"].fn)
    params = list(sig_record.parameters.keys())
    assert params == ["kind", "payload", "spec_id", "session_id", "pr_number", "actor", "ts"]
    assert sig_record.parameters["spec_id"].default is None

    # 2. session_log_query(kind?, spec_id?, session_id?, since?, until?, limit=50, cursor?)
    sig_query = inspect.signature(tools["session_log_query"].fn)
    params = list(sig_query.parameters.keys())
    assert params == ["kind", "spec_id", "session_id", "since", "until", "limit", "cursor"]
    assert sig_query.parameters["limit"].default == 50

    # 3. session_log_summary(spec_id?, session_id?, since?)
    sig_summary = inspect.signature(tools["session_log_summary"].fn)
    params = list(sig_summary.parameters.keys())
    assert params == ["spec_id", "session_id", "since"]

    # 4. session_log_export_md(spec_id?, since?, limit=200)
    sig_export = inspect.signature(tools["session_log_export_md"].fn)
    params = list(sig_export.parameters.keys())
    assert params == ["spec_id", "since", "limit"]
    assert sig_export.parameters["limit"].default == 200

    # 5. session_log_record_tokens(session_id, model, prompt_tokens, completion_tokens, ts?)
    sig_tokens = inspect.signature(tools["session_log_record_tokens"].fn)
    params = list(sig_tokens.parameters.keys())
    assert params == ["session_id", "model", "prompt_tokens", "completion_tokens", "ts"]
    assert sig_tokens.parameters["ts"].default is None
