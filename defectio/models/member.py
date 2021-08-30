from __future__ import annotations
from .mixins import Hashable

from . import abc


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..state import ConnectionState
    from .server import Server
    from ..types.payloads import MemberPayload


class PartialMember(abc.Messageable, Hashable):
    def __init__(self, id: str, server: Server, state: ConnectionState):
        self._state = state
        self.server = server
        self.id = id

    def __repr__(self) -> str:
        return f"<PartialMember {self.id}>"

    def __str__(self) -> str:
        return self.id


class Member(PartialMember):
    def __init__(self, data: MemberPayload, server: Server, state: ConnectionState):
        self._state = state
        self.server = server
        self.nickname = data.get("nickname")
        self.id = data.get("_id").get("user")

    def __repr__(self) -> str:
        return f"<Member id={self.id} nickname={self.nickname}>"

    def __str__(self) -> str:
        return self.nickname
