"""
Smoke tests for music handlers.
"""

def get_registered_tools(mcp):
    import asyncio
    return asyncio.run(mcp._local_provider.list_tools())

def test_all_modules_register_at_least_one_tool():
    from agency_mcp.server import create_mcp
    import importlib
    import pkgutil
    import agency_mcp.handlers.music as music_handlers

    modules = [name for _, name, _ in pkgutil.iter_modules(music_handlers.__path__) if not name.startswith("_")]

    # We should have exactly 16 modules
    expected_modules = {
        'core', 'audio', 'mixing', 'sheet_music', 'video',
        'lyrics_analysis', 'text_analysis', 'album_ops', 'gates',
        'database', 'ideas', 'streaming', 'content', 'health',
        'maintenance', 'promo'
    }

    assert set(modules) == expected_modules

    # Each should export a register function
    for mod_name in expected_modules:
        mod = importlib.import_module(f"agency_mcp.handlers.music.{mod_name}")
        assert hasattr(mod, 'register'), f"Module {mod_name} missing register(mcp) function"

def test_tool_count_at_least_60():
    from agency_mcp.server import create_mcp
    mcp = create_mcp()
    tools = get_registered_tools(mcp)
    # It must have at least 60 tools in total after music handlers are registered
    assert len(tools) >= 60

def test_every_music_tool_has_domain_tag():
    from agency_mcp.server import create_mcp
    mcp = create_mcp()
    tools = get_registered_tools(mcp)

    music_tools_count = 0
    for tool in tools:
        if tool.name.startswith("music_"):
            music_tools_count += 1
            assert "domain:music" in (tool.tags or []), f"Tool {tool.name} missing domain:music tag"
        elif tool.tags and "domain:music" in tool.tags:
            assert tool.name.startswith("music_"), f"Tool {tool.name} has domain:music tag but does not start with music_"

    assert music_tools_count > 0, "No music tools registered"

def test_tool_names_match_naming_convention():
    from agency_mcp.server import create_mcp
    import re
    mcp = create_mcp()
    tools = get_registered_tools(mcp)

    # ^music_[a-z]+(_[a-z0-9]+)+$
    pattern = re.compile(r"^music_[a-z]+(_[a-z0-9]+)+$")

    legacy_names = {"find_album", "create_track", "master_album"}

    music_tools_count = 0
    for tool in tools:
        if "domain:music" in (tool.tags or []):
            music_tools_count += 1
            assert pattern.match(tool.name), f"Tool name {tool.name} does not match convention"
            assert tool.name not in legacy_names, f"Legacy tool name {tool.name} is present"

    assert music_tools_count > 0, "No music tools registered"
