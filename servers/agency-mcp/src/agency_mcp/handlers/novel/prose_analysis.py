from fastmcp import FastMCP
from agency_mcp.lib.prose_processing.readability import analyze_readability
from agency_mcp.lib.prose_processing.rhythm import analyze_rhythm
from agency_mcp.lib.prose_processing.pov import scan_pov_violations

def novel_analyze_readability(text: str) -> dict: return analyze_readability(text)
def novel_analyze_rhythm(text: str) -> dict: return analyze_rhythm(text)
def novel_scan_pov_violations(text: str, declared_pov: str, viewpoint_character: str = None) -> list[dict]: return scan_pov_violations(text, declared_pov, viewpoint_character)
def novel_extract_distinctive_phrases(text: str) -> list[str]: return []

def register(mcp: FastMCP) -> None:
    mcp.tool(tags={"domain:novel"})(novel_analyze_readability)
    mcp.tool(tags={"domain:novel"})(novel_analyze_rhythm)
    mcp.tool(tags={"domain:novel"})(novel_scan_pov_violations)
    mcp.tool(tags={"domain:novel"})(novel_extract_distinctive_phrases)
