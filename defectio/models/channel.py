from __future__ import annotations

from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from defectio.models.objects import Object, Unique
from defectio.models.permission import ChannelPermission
from defectio.models.server import Role

from . import abc
from .user import User

if TYPE_CHECKING:
    from ..types.payloads import ChannelPayload
    from defectio.state import ConnectionState
    from defectio.models.server import Server
    from defectio.types.payloads import DMChannelPayload, EditChannelPayload

__all__ = (
    "TextChannel",
    "VoiceChannel",
    "DMChannel",
    "GroupChannel",
    "PartialChannel",
    "channel_factory",
    "MessageableChannel",
    "ServerChannel",
    "DirectMessage",
)


class PartialChannel(Unique):

    __slots__ = "_state"

    def __init__(self, data: ChannelPayload, state: ConnectionState):
        self.id = Object(data["_id"])
        self._state = state


class Invite:
    __slots__ = "code"

    def __init__(self, code: str):
        self.code = code


class TextChannel(PartialChannel, abc.Messageable, abc.ServerChannel):
    __slots__ = (
        "name",
        "description",
        "_state",
        "type",
        "server",
        "nsfw",
        "overrides",
    )

    def __init__(self, *, state: ConnectionState, server: Server, data: ChannelPayload):
        super().__init__(state=state, data=data)
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


class SavedMessageChannel(PartialChannel, abc.Messageable):
    def __init__(self, data: ChannelPayload, state: ConnectionState):
        super().__init__(state=state, data=data)

    async def _get_channel(self) -> SavedMessageChannel:
        return self


class DMChannel(PartialChannel, abc.Messageable):

    __slots__ = ("active", "_recipients")

    def __init__(self, data: DMChannelPayload, state: ConnectionState):
        super().__init__(state=state, data=data)
        self.active = data.get("active")
        # if "last_message" in data:
        #     self.last_message = state.get_message(data.get("last_message").get("_id"))
        # else:
        #     self.last_message = None
        self._recipients = data.get("recipients")

    def _update(self, data: EditChannelPayload) -> None:
        pass

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


class GroupChannel(PartialChannel, abc.Messageable):
    def __init__(self, data: ChannelPayload, state: ConnectionState):
        super().__init__(data, state)
        self.name = data.get("name")
        self.active = data.get("active")
        self._recipients = data.get("recipients")
        self._state: ConnectionState = state

    def _update(self, data: EditChannelPayload) -> None:
        self.name = data.get("name", self.name)
        self.active = data.get("active", self.active)
        self._recipients = data.get("recipients", self._recipients)
        # self.last_message = Message(self._state, data.get("last_message"))

    async def _get_channel(self) -> GroupChannel:
        return self

    @property
    def recipients(self) -> list[User]:
        return [self._state.get_user(user) for user in self._recipients]


class VoiceChannel(PartialChannel, abc.Messageable):
    def __init__(self, state: ConnectionState, server: Server, data):
        super().__init__(state=state, data=data)
        self.server = server
        self.name: str = data["name"]
        self.description: Optional[str] = data.get("description")
        self.overrides: list[Role] = []
        for role_id, perm in data.get("role_permissions", {}).items():
            self.overrides.append({role_id: ChannelPermission(perm)})

    def _update(self, data: EditChannelPayload) -> None:
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


def channel_factory(data: ChannelPayload) -> Channel:
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


ServerChannel = Union[TextChannel, VoiceChannel]
DirectMessage = Union[GroupChannel, DMChannel]
Channel = Union[
    TextChannel, SavedMessageChannel, DirectMessage, GroupChannel, VoiceChannel
]
MessageableChannel = Union[TextChannel, DMChannel, GroupChannel, SavedMessageChannel]
