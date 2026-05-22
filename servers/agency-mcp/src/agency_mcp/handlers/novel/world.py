from fastmcp import FastMCP

def novel_get_world(work_id: str) -> dict: return {}
def novel_list_world_entities(work_id: str) -> list[dict]: return []
def novel_check_world_consistency(work_id: str) -> dict: return {}

def register(mcp: FastMCP) -> None:
    mcp.tool(tags={"domain:novel"})(novel_get_world)
    mcp.tool(tags={"domain:novel"})(novel_list_world_entities)
    mcp.tool(tags={"domain:novel"})(novel_check_world_consistency)
