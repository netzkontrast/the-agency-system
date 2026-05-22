#!/usr/bin/env python3
import sys
from agency_mcp.server import create_mcp

if __name__ == "__main__":
    if "--check" in sys.argv:
        print("agency-system v0.0.1 healthy")
        sys.exit(0)
    create_mcp().run()
