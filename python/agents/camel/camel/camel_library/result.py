"""Module containing definitions for the result type.

It works like Rust's Result type.
"""

import dataclasses
from typing import Generic, TypeAlias, TypeVar

_T = TypeVar("_T")
_E = TypeVar("_E")


@dataclasses.dataclass(frozen=True)
class Ok(Generic[_T]):
    value: _T


@dataclasses.dataclass(frozen=True)
class Error(Generic[_E]):
    error: _E


Result: TypeAlias = Ok[_T] | Error[_E]
