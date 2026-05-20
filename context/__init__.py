"""Context base layer for the agency-system."""

from ._store.sqlite import Store
from . import _hooks as hooks
from . import _drivers as drivers

_STORE = None


def get_store():
    """Return the process-wide Store singleton.

    All runtime callers (hooks, pipeline, gate evaluator, envelope) reach
    the graph through this accessor. Constructing Store() directly is
    permitted only in tests (which monkeypatch via:
    ``monkeypatch.setattr("context._STORE", Store(db_path=tmp))``).

    See ``vision/specs/08-context-base-v1.md`` §FR1.

    Concurrency: FastMCP serves requests in a single asyncio loop, so the
    bare check-and-set is intentional. If a future deployment wraps tools
    in worker threads, this needs an :class:`threading.Lock` around the
    lazy init.
    """
    global _STORE
    if _STORE is None:
        _STORE = Store()
        _STORE.boot()
    return _STORE


__all__ = ['Store', 'hooks', 'drivers', 'get_store']
