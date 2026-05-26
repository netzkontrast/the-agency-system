"""agency-seed — a running proof of the v4 core on the real substrate.

Four concepts (Intent, Capability, Lifecycle, Memory) + a FastMCP engine, over a
real GraphQLite bi-temporal graph. The point is to PROVE the moat: cross-concern
provenance as one graph traversal — and to falsify the risk that "one graph +
the verb frame" can't carry two genuinely different capabilities.
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
