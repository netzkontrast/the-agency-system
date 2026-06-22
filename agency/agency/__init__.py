"""agency — an installable Claude Code plugin: the v4 core on the real substrate.

Four concepts (Intent, Capability, Lifecycle, Memory) + a FastMCP engine, over a
real GraphQLite bi-temporal graph. The moat: cross-concern provenance as one
graph traversal. Capabilities self-register by reflection, and the engine authors
(and validates) its own Claude Code plugin install. Code-mode IS the contract,
exposed isomorphically over MCP · Skills · a bash CLI.
"""
# Portability (Jules review, PR #175): GraphQLite loads a SQLite extension, but
# many Python builds ship a `sqlite3` with extension loading disabled. If so, and
# `pysqlite3` (a full SQLite) is installed, transparently swap it in BEFORE
# graphqlite imports sqlite3. On builds where stdlib sqlite3 already supports
# extensions, nothing changes.
import sys as _sys


def _stdlib_sqlite_supports_extensions() -> bool:
    try:
        import sqlite3
        conn = sqlite3.connect(":memory:")
        try:
            conn.enable_load_extension(True)
            return True
        except Exception:
            return False
        finally:
            conn.close()
    except Exception:
        return False


if not _stdlib_sqlite_supports_extensions():
    try:
        import pysqlite3  # type: ignore
        _sys.modules["sqlite3"] = pysqlite3
        _sys.modules["sqlite3.dbapi2"] = pysqlite3.dbapi2
    except ImportError:
        pass  # leave stdlib; graphqlite will raise a clear, actionable error
