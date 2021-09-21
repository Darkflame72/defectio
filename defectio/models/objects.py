"""Implementation of a Object type."""
from __future__ import annotations

__all__: typing.List[str] = [
    "Object",
    "Unique",
    "Objectish",
    "ObjectishOr",
    "ObjectishIterable",
    "ObjectishSequence",
]

import abc
import typing
import ulid


if typing.TYPE_CHECKING:
    import datetime


@typing.final
class Object(str):
    """A concrete representation of a unique ID for an entity on Revolt.

    This object can be treated as a regular `builtins.str` for most purposes.
    """

    __slots__: typing.Sequence[str] = ()

    @property
    def created_at(self) -> datetime.datetime:
        """When the object was created."""
        epoch = ulid.parse(self).timestamp()
        return epoch.datetime


class Unique(abc.ABC):
    """Mixin for a class that enforces uniqueness by a object ID."""

    __slots__: typing.Sequence[str] = "id"

    id: Object

    @property
    def created_at(self) -> datetime.datetime:
        """When the object was created."""
        return self.id.created_at

    def __str__(self) -> str:
        return str(self.id)

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: typing.Any) -> bool:
        return type(self) is type(other) and self.id == other.id


Objectish = typing.Union[Object, str]
"""Type hint for a value that resembles a `Object` object functionally.

This is a value that is `Object`-ish.

A value is `Object`-ish if casting it to an `str` allows it to be cast to
a `Object`.

The valid types for this type hint are:

- `builtins.str`
- `Object`
"""

T = typing.TypeVar("T", covariant=True, bound=Unique)

ObjectishOr = typing.Union[T, Objectish]
"""Type hint representing a unique object entity.

This is a value that is `Object`-ish or a specific type covariant.

If you see `ObjectishOr[Foo]` anywhere as a type hint, it means the value
may be a `Foo` instance, a `Object`, a `builtins.int` or a `builtins.str`
with numeric digits only.

Essentially this represents any concrete object, or ID of that object. It is
used across Defectio's API to allow use of functions when information is only
partially available (due to Discord inconsistencies, edge case behaviour, or
use of intents).

The valid types for this type hint are:

- `buitlins.str`
- `Object`
"""

ObjectishIterable = typing.Iterable[ObjectishOr[T]]
"""Type hint representing an iterable of unique object entities."""


ObjectishSequence = typing.Sequence[ObjectishOr[T]]
"""Type hint representing a collection of unique object entities."""
