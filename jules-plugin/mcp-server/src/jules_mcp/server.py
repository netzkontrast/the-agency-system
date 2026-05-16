import sys
from fastmcp import FastMCP

def create_mcp() -> FastMCP:
    mcp = FastMCP("jules")
    # Tools will be attached here
    print("stub — register_*_tools() not yet wired", file=sys.stderr)
    return mcp

if __name__ == "__main__":
    mcp = create_mcp()
    mcp.run()
