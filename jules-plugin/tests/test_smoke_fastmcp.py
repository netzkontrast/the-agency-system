import asyncio
from jules_mcp.server import create_mcp

def test_registers_all_tools():
    async def go():
        mcp = create_mcp()
        # CodeMode transform hides original tools, so check the underlying provider
        tools = await mcp._local_provider.list_tools()
        return [t.name for t in tools]
    names = asyncio.run(go())
    jules_tools = [n for n in names if n.startswith("jules_")]
    assert len(jules_tools) >= 16, f"only {len(jules_tools)} jules_* tools: {jules_tools}"
