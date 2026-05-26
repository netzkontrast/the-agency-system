"""A REAL 2nd capability (not a toy): count_syllables — a stateless `transform`.

This is the falsifier the panel demanded: a genuinely different kind of
capability from an agent (jules). It mutates nothing and reads no persisted
state — it is pure compute, which is exactly the class the earlier verb frame
could NOT express until `transform` was added as a role.
"""
from __future__ import annotations

import re

from ..capability import Capability

_VOWELS = re.compile(r"[aeiouy]+")


def count_syllables(text: str) -> int:
    total = 0
    for word in re.findall(r"[a-zA-Z]+", text):
        groups = _VOWELS.findall(word.lower())
        n = len(groups)
        if word.lower().endswith("e") and n > 1:
            n -= 1            # silent trailing 'e'
        total += max(1, n)
    return total


syllables_capability = Capability(
    name="syllables",
    home="capability",
    verbs={"count": {"role": "transform", "fn": count_syllables}},
)
