#!/usr/bin/env python3
"""Entry point for the agency-system MCP server.

`python run.py` runs the server over stdio. `python run.py --check`
boots the MCP, queries the health tool synchronously, prints the
healthy line, and exits zero — used by smoke tests and CI.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from agency_mcp import __version__
from agency_mcp.server import create_mcp


def _check() -> int:
    mcp = create_mcp()

    async def _query() -> dict:
        result = await mcp._call_tool_mcp("health_check", {})
        return result

    asyncio.run(_query())
    print(f"agency-system v{__version__} healthy")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="agency-mcp")
    parser.add_argument(
        "--check",
        action="store_true",
        help="boot the MCP, call health_check, print the healthy line, exit 0",
    )
    args = parser.parse_args()

    if args.check:
        return _check()

    create_mcp().run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
