# Vendored from bitwize-music@v0.91.0: tools/state/__main__.py
#!/usr/bin/env python3
"""Allow running as: python3 -m tools.state <command>"""

import sys

from agency_mcp.tools.state.indexer import main

if __name__ == "__main__":
    sys.exit(main() or 0)
