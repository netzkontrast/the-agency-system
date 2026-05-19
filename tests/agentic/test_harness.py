import pytest
import tiktoken
import json
from fastmcp import FastMCP
from agentic._bootloader import boot
from agentic._harness.cell_loader import discover


@pytest.fixture
def empty_matrix(tmp_path):
    import os

    orig_dir = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(orig_dir)


@pytest.mark.asyncio
async def test_four_verb_contract_present(empty_matrix):
    mcp = boot()
    tools = []
    # get registered tools
    tools_response = await mcp._local_provider.list_tools()
    for t in tools_response:
        tools.append(t.name)

    assert "mcp__list_tools" in tools
    assert "mcp__call_tool" in tools
    assert "mcp__list_skills" in tools
    assert "mcp__dispatch_skill" in tools


@pytest.mark.asyncio
async def test_cold_boot_under_budget(empty_matrix):
    mcp = boot()

    tools_list = []
    tools_response = await mcp._local_provider.list_tools()
    for t in tools_response:
        # Pydantic v2 dump to dict safely
        # t.inputSchema should just be a plain dict representation
        if hasattr(t, "inputSchema") and t.inputSchema is not None:
            # FastMCP sets this
            schema = t.inputSchema
        else:
            schema = {"type": "object", "properties": {}}

        tools_list.append(
            {"name": t.name, "description": t.description, "inputSchema": schema}
        )

    payload_str = json.dumps({"tools": tools_list})

    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(payload_str)

    # 500 budget includes system prompt (which isn't modeled here), but the tools alone should be < 500
    assert len(tokens) < 500, f"Token payload is {len(tokens)}, which exceeds budget!"


def test_tool_return_validated(empty_matrix):
    pass  # we can verify manually or just test the validate_tool_result function


def test_tool_return_validated_schema(tmp_path):
    import os
    import json

    orig_dir = os.getcwd()
    os.chdir(tmp_path)

    # Create the schema file
    schema_dir = tmp_path / "context" / "_shared" / "schemas"
    schema_dir.mkdir(parents=True)
    schema_path = schema_dir / "tool_result.schema.json"

    schema_content = {
        "$id": "tag:agency-system.local,2026:schema:tool_result.schema.json",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "ok": {"type": "boolean"},
            "data": {"type": "object"},
            "warnings": {"type": "array"},
            "next_suggested_tools": {"type": "array"},
        },
        "required": ["ok", "data", "warnings", "next_suggested_tools"],
    }

    with open(schema_path, "w") as f:
        json.dump(schema_content, f)

    from agentic._harness.fastmcp_boot import validate_tool_result, ENVELOPE_SCHEMA_PATH
    import agentic._harness.fastmcp_boot as boot_module

    # Temporarily patch the path
    old_path = boot_module.ENVELOPE_SCHEMA_PATH
    boot_module.ENVELOPE_SCHEMA_PATH = schema_path

    try:
        # data needs to be an object per schema
        bad_result = {
            "ok": True,
            "data": "not an object",
            "warnings": [],
            "next_suggested_tools": [],
        }
        wrapped = validate_tool_result(bad_result)

        assert wrapped["ok"] is False
        assert "error" in wrapped["data"]
        assert wrapped["data"]["error"]["code"] == "ENVELOPE_INVALID"
    finally:
        boot_module.ENVELOPE_SCHEMA_PATH = old_path
        os.chdir(orig_dir)
