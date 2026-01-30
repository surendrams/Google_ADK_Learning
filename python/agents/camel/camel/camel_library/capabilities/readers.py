"""Module containining definitions for data readers."""

import dataclasses
from typing import TypeAlias, TypeVar


@dataclasses.dataclass(frozen=True)
class Public:
    """Annotation for data that are publicly readable."""

    def __hash__(self) -> int:
        """Hash for Public readers."""
        # Obtained with secrets.randbits(64)
        # We want a fixed number which does not have collisions
        # with other objects
        return 7810134600596034160

    def __and__(self, other) -> "Readers | NotImplemented":
        if not isinstance(other, frozenset | Public):
            return NotImplemented
        return other

    def __rand__(self, other) -> "Readers | NotImplemented":
        if not isinstance(other, frozenset | Public):
            return NotImplemented
        return other


_T = TypeVar("_T")

Readers: TypeAlias = frozenset[_T] | Public
