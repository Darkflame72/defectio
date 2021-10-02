from __future__ import annotations
from defectio.models.permission import ChannelPermission
from defectio.models.server import Role

from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from .user import User

from . import abc
from .mixins import Hashable

if TYPE_CHECKING:
    from ..types.payloads import ChannelPayload
    from ..state import ConnectionState
    from .server import Server
    from ..types.payloads import DMChannelPayload
    from .message import Message

__all__ = (
    "TextChannel",
    "VoiceChannel",
    "DMChannel",
    "GroupChannel",
)


class TextChannel(abc.Messageable, abc.ServerChannel, Hashable):
    __slots__ = (
        "name",
        "description",
        "_state",
        "id",
        "type",
        "server",
        "nsfw",
        "overrides",
    )

    def __init__(self, *, state: ConnectionState, server: Server, data: ChannelPayload):
        self._state: ConnectionState = state
        self.id: str = data["_id"]
        self.type: str = data["channel_type"]
        self.server = server
        self.name = data["name"]
        self.description = data.get("description")
        self.nsfw = data.get("nsfw")
        self.overrides: list[Role] = []
        for role_id, perm in data.get("role_permissions", {}).items():
            self.overrides.append({role_id: ChannelPermission(perm)})

    def __repr__(self) -> str:
        attrs = [
            ("id", self.id),
            ("name", self.name),
        ]
        joined = " ".join("%s=%r" % t for t in attrs)
        return f"<{self.__class__.__name__} {joined}>"

    def _update(self, data) -> None:
        self.name = data.get("name", self.name)
        self.description = data.get("description", self.description)
        if "role_permissions" in data:
            for role_id, perm in data.get("role_permissions").items():
                if role_id not in self.overrides:
                    self.overrides.append({role_id: ChannelPermission(perm)})
                else:
                    self.overrides[role_id] = ChannelPermission(perm)

    async def _get_channel(self) -> TextChannel:
        return self


class SavedMessageChannel(abc.Messageable):
    def __init__(self, data: ChannelPayload, state: ConnectionState):
        self.id = data.get("_id")
        self._state: ConnectionState = state
        self.type: str = data["channel_type"]
        # super().__init__(data, state)

    async def _get_channel(self) -> SavedMessageChannel:
        return self


class DMChannel(abc.Messageable):
    def __init__(self, data: DMChannelPayload, state: ConnectionState):
        self._state = state
        self.id = data.get("_id")
        self.active = data.get("active")
        self.type: str = data["channel_type"]
        # if "last_message" in data:
        #     self.last_message = state.get_message(data.get("last_message").get("_id"))
        # else:
        #     self.last_message = None
        self._recipients = data.get("recipients")

    async def _get_channel(self) -> DMChannel:
        return self

    @property
    def recipients(self) -> list[User]:
        return [self._state.get_user(user) for user in self._recipients]

    def __str__(self) -> str:
        if self.recipient:
            return f"Direct Message with {self.recipient}"
        return "Direct Message with Unknown User"

    def __repr__(self) -> str:
        return f"<DMChannel id={self.id} recipient={self.recipient!r}>"


class GroupChannel(abc.Messageable):
    def __init__(self, data: ChannelPayload, state: ConnectionState):
        # super().__init__(data, state)
        self.id = data.get("_id")
        self.name = data.get("name")
        self.active = data.get("active")
        self._recipients = data.get("recipients")
        self._state: ConnectionState = state
        self.type: str = data["channel_type"]

    def _update(self, data: ChannelPayload) -> None:
        self.name = data.get("name", self.name)
        self.active = data.get("active", self.active)
        self._recipients = data.get("recipients", self._recipients)
        # self.last_message = Message(self._state, data.get("last_message"))

    async def _get_channel(self) -> GroupChannel:
        return self

    @property
    def recipients(self) -> list[User]:
        return [self._state.get_user(user) for user in self._recipients]


class VoiceChannel(abc.Messageable):
    def __init__(self, state: ConnectionState, server: Server, data):
        self._state: ConnectionState = state
        self.id: str = data["_id"]
        self.type: str = data["channel_type"]
        self.server = server
        self.name: str = data["name"]
        self.description: Optional[str] = data.get("description")
        self.overrides: list[Role] = []
        for role_id, perm in data.get("role_permissions", {}).items():
            self.overrides.append({role_id: ChannelPermission(perm)})

    def _update(self, data) -> None:
        self.name: str = data.get("name", self.name)
        self.description: Optional[str] = data.get("description", self.description)
        if "role_permissions" in data:
            for role_id, perm in data.get("role_permissions").items():
                if role_id not in self.overrides:
                    self.overrides.append({role_id: ChannelPermission(perm)})
                else:
                    self.overrides[role_id] = ChannelPermission(perm)

    async def _get_channel(self) -> VoiceChannel:
        return self


MessageableChannel = Union[TextChannel, DMChannel, GroupChannel, SavedMessageChannel]


def channel_factory(data: ChannelPayload) -> type[abc.Messageable]:
    # Literal["SavedMessages", "DirectMessage", "Group", "TextChannel", "VoiceChannel"]
    channel_type = data["channel_type"]
    if channel_type == "SavedMessages":
        return SavedMessageChannel
    elif channel_type == "DirectMessage":
        return DMChannel
    elif channel_type == "Group":
        return GroupChannel
    elif channel_type == "TextChannel":
        return TextChannel
    elif channel_type == "VoiceChannel":
        return VoiceChannel
    else:
        raise Exception
