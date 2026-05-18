#!/usr/bin/env python3
"""Boot entrypoint for the agency-mcp FastMCP server."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agency_mcp.server import create_mcp  # noqa: E402

if __name__ == "__main__":
    if "--check" in sys.argv:
        create_mcp()
        print("agency-system v0.0.1 healthy")
        sys.exit(0)
    create_mcp().run()
