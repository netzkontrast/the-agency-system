from fastmcp import FastMCP


def register_shared_handlers(mcp: FastMCP) -> None:
    from .search import shared_search
    from .skills import shared_list_skills, shared_get_skill, plugin_help
    from .reference import shared_get_reference, shared_load_override
    from .config import shared_get_config
    from .session import (
        shared_get_session,
        shared_update_session,
        shared_get_pending_verifications,
    )

    mcp.tool(
        name="shared_search",
        description="Search across state namespaces, references, and skills.",
    )(shared_search)
    mcp.tool(name="shared_list_skills", description="List available skills by domain.")(
        shared_list_skills
    )
    mcp.tool(
        name="shared_get_skill",
        description="Get a skill's frontmatter and body preview.",
    )(shared_get_skill)
    mcp.tool(
        name="plugin_help",
        description="Returns a markdown cheat-sheet of available skills for a domain.",
    )(plugin_help)
    mcp.tool(
        name="shared_get_reference", description="Get the content of a reference file."
    )(shared_get_reference)
    mcp.tool(name="shared_load_override", description="Load a config override file.")(
        shared_load_override
    )
    mcp.tool(name="shared_get_config", description="Load the shared system config.")(
        shared_get_config
    )
    mcp.tool(name="shared_get_session", description="Get the current session state.")(
        shared_get_session
    )
    mcp.tool(
        name="shared_update_session", description="Update the current session state."
    )(shared_update_session)
    mcp.tool(
        name="shared_get_pending_verifications",
        description="Get pending verifications from the session.",
    )(shared_get_pending_verifications)
