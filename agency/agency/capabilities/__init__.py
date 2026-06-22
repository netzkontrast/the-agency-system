"""Capabilities — discovered by REFLECTION, not hand-wired.

Drop a module in this package that defines one or more `Capability` instances at
module level; `discover()` finds them via the stdlib reflection APIs
(`pkgutil.iter_modules` to walk this package's directory + `importlib` to import
each module + `isinstance` to pick out the `Capability` objects). The engine
calls `discover()` and registers everything, and auto-wires one MCP tool per verb
from the verb function's signature (`inspect.signature`). Adding a capability =
adding a file. No registration code, no per-tool boilerplate.
"""
from __future__ import annotations

import importlib
import pkgutil

from ..capability import Capability


def discover() -> list[Capability]:
    """Every `Capability` instance defined at the top level of any non-private
    module in this package, in stable (module, name) order."""
    found: list[Capability] = []
    for info in sorted(pkgutil.iter_modules(__path__), key=lambda i: i.name):
        if info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{__name__}.{info.name}")
        for value in vars(module).values():
            if isinstance(value, Capability) and value not in found:
                found.append(value)
    return found
