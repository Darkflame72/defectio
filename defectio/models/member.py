from __future__ import annotations

from typing import TYPE_CHECKING, Optional
import attr

from defectio.models import objects
from defectio.models.user import PartialUser

__all__ = ["PartialMember", "Member"]


@attr.define(hash=True, kw_only=True, weakref_slot=False)
class PartialMember(PartialUser):
    """A partial member."""

    pass


@attr.define(hash=True, kw_only=True, weakref_slot=False)
class Member(PartialMember):
    """A member."""

    nickname: Optional[str] = attr.ib(eq=False, hash=False, repr=True)
    """The nickname of the member."""
