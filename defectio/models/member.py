from __future__ import annotations
from defectio.models.objects import Unique

from typing import TYPE_CHECKING

from defectio.models.server import Role
from defectio.types.websocket import ServerMemberUpdate

from . import abc
from .mixins import Hashable

if TYPE_CHECKING:
    from ..state import ConnectionState
    from ..types.payloads import MemberPayload


class PartialMember(abc.Messageable, Unique):
    def __init__(self, id: str, state: ConnectionState):
        self._state = state
        self.id = id

    def __repr__(self) -> str:
        return f"<PartialMember {self.id}>"


class Member(PartialMember):
    def __init__(self, data: MemberPayload, state: ConnectionState):
        self._state = state
        self.nickname = data.get("nickname")
        self.id = data.get("_id").get("user")

    def _update(self, data: ServerMemberUpdate):
        self.nickname = data.get("nickname", self.nickname)

    def __repr__(self) -> str:
        return f"<Member id={self.id} nickname={self.nickname}>"
