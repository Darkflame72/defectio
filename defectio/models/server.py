from __future__ import annotations

from typing import Optional
from typing import TYPE_CHECKING

from defectio.models.colour import Colour
from defectio.models.permission import ChannelPermission
from defectio.models.permission import ServerPermission

from .mixins import Hashable
from .objects import Unique

if TYPE_CHECKING:
    from ..types.payloads import (
        ServerPayload,
        CategoryPayload,
        SystemMessagePayload,
        RolePayload,
    )
    from ..state import ConnectionState
    from ..types.websocket import ServerUpdate, ServerRoleUpdate
    from .member import Member
    from .channel import MessageableChannel
    from defectio.types.payloads import IconPayload


class Icon:
    __slots__ = (
        "id",
        "tag",
        "size",
        "filename",
        "content_type",
        "metadata",
        "_state",
    )

    def __init__(self, payload: IconPayload, state: ConnectionState) -> None:
        self.id = payload["_id"]
        self._state = state
        self.tag = payload["tag"]
        self.size = payload["size"]
        self.filename = payload["filename"]
        self.content_type = payload["content_type"]
        self.metadata = payload["metadata"]

    @property
    def url(self) -> str:
        return f"{self._state.http.api_info.features.autumn.url}/icons/{self.id}"


class SystemMessages:

    __slots__ = (
        "_user_joined",
        "_user_left",
        "_user_kicked",
        "_user_banned",
        "_state",
        "server",
    )

    def __init__(
        self, data: SystemMessagePayload, server: Server, state: ConnectionState
    ) -> None:
        self._state = state
        self.server = server
        self._user_joined = data.get("user_joined")
        self._user_left = data.get("user_left")
        self._user_kicked = data.get("user_kicked")
        self._user_banned = data.get("user_banned")

    @property
    def user_joined(self) -> Optional[MessageableChannel]:
        return self._state.get_channel(self._user_joined)

    @property
    def user_left(self) -> Optional[MessageableChannel]:
        return self._state.get_channel(self._user_left)

    @property
    def user_kicked(self) -> Optional[MessageableChannel]:
        return self._state.get_channel(self._user_kicked)

    @property
    def user_banned(self) -> Optional[MessageableChannel]:
        return self._state.get_channel(self._user_banned)

    def __repr__(self) -> str:
        return (
            f"<SystemMessages server={self.server.id} "
            f"user_joined={self.user_joined} "
            f"user_left={self.user_left} "
            f"user_kicked={self.user_kicked} "
            f"user_banned={self.user_banned}>"
        )

    def __str__(self) -> str:
        return self.__repr__()


class Role(Unique):
    def __init__(self, id: str, data: RolePayload, state: ConnectionState) -> None:
        self.id = id
        self._state = state
        self.name = data.get("name")
        if "colour" in data:
            self.colour = Colour.from_hex(data["colour"])
        else:
            self.colour = None
        self.hoist = data.get("hoist", False)
        self.rank = data.get("rank")
        self.default_server_permissions = ServerPermission(data.get("permissions")[0])
        self.default_channel_permissions = ChannelPermission(data.get("permissions")[1])

    def _update(self, event: ServerRoleUpdate) -> None:
        if event.get("clear") == "Colour":
            self.colour = None
        self.name = event.get("name", self.name)
        self.hoist = event.get("hoist", self.hoist)
        self.rank = event.get("rank", self.rank)

    @property
    def color(self) -> Optional[Colour]:
        return self.colour

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"<Role server={self.server.id} name={self.name} colour={self.colour}>"


class Category(Hashable):
    def __init__(self, data: CategoryPayload, state: ConnectionState) -> None:
        self._state = state
        self.channels: list[MessageableChannel] = []
        self._from_data(data)

    def _from_data(self, data: CategoryPayload) -> None:
        self.id = data.get("id")
        self.title = data.get("title")
        for channel in data.get("channels", []):
            self.channels.append(self._state.get_channel(channel))


class Server(Unique):
    def __init__(self, data: ServerPayload, state: ConnectionState):
        self.channel_ids: list[str] = []
        self.member_ids: list[str] = []
        self._categories: dict[str, Category] = {}
        self._state: ConnectionState = state
        self._from_data(data)

    def _from_data(self, data: ServerPayload) -> None:
        self.id = data.get("_id")
        self.owner = data.get("owner")
        self.name = data.get("name")
        self.description = data.get("description")
        self.channel_ids = data.get("channels")
        self.member_ids = data.get("members")
        for category in data.get("categories", []):
            self._categories[category["id"]] = Category(category, self._state)
        self.roles: list[Role] = []
        for key, value in data.get("roles", {}).items():
            self.roles.append(Role(key, value, self._state))
        self.banner = data.get("banner")
        self.system_message = SystemMessages(
            data.get("system_messages"), self, self._state
        )
        self.server_permissions = ServerPermission(data.get("default_permissions")[0])
        self.channel_permissions = ChannelPermission(data.get("default_permissions")[1])
        if "icon" in data:
            self.icon = Icon(data["icon"], self._state)
        else:
            self.icon = None

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        attrs = (
            ("id", self.id),
            ("name", self.name),
            ("description", self.description or ""),
        )
        inner = " ".join("%s=%r" % t for t in attrs)
        return f"<Server {inner}>"

    def _update(self, payload: ServerUpdate):
        """[summary]

        Parameters
        ----------
        payload : ServerUpdate
            [description]
        """
        self.owner = payload.get("owner", self.owner)
        self.name = payload.get("name", self.name)
        self.description = payload.get("description", self.description)
        if "icon" in payload:
            self.icon = Icon(payload["icon"], self._state)
        else:
            self.icon = None

    def get_role(self, role_id: str) -> Optional[Role]:
        for role in self.roles:
            if role.id == role_id:
                return role
        return None

    def create_text_channel(
        self, name: str, *, description: Optional[str] = None
    ) -> MessageableChannel:
        channel = self._state.http.create_channel(self.id, name, "Text", description)
        self._state.add_channel(channel)
        self.channel_ids.append(channel["_id"])

    def create_voice_channel(self, name: str):
        channel = self._state.http.create_channel(self.id, name, "Voice")
        self._state.add_channel(channel)
        self.channel_ids.append(channel["_id"])

    def get_member_named(self, name: str):
        for member in self.members:
            if member.name == name:
                return member
        return None

    def get_category_channel(self, channel_id: str) -> Optional[Category]:
        for category in self._categories.values():
            for channel in category.channels:
                if channel.id == channel_id:
                    return category
        return None

    def get_channel(self, id: str) -> Optional[MessageableChannel]:
        for channel in self.channels:
            if channel.id == id:
                return channel
        return None

    @property
    def channels(self):
        """All channels in the server

        Returns
        -------
        [type]
            list of all channels
        """
        return [self._state.get_channel(channel_id) for channel_id in self.channel_ids]

    @property
    def text_channels(self):
        """All text channels in the server

        Returns
        -------
        [type]
            list of all text channels
        """
        from .channel import TextChannel

        return [i for i in self.channels if isinstance(i, TextChannel)]

    @property
    def voice_channels(self):
        """All voice channels in the server

        Returns
        -------
        [type]
            list of all voice channels
        """
        from .channel import VoiceChannel

        return [i for i in self.channels if isinstance(i, VoiceChannel)]

    @property
    def members(self) -> list[Member]:
        """All cached members in the server.

        Returns
        -------
        list[Member]
            list of all cached members in the server.
        """
        return [self._state.get_member(member_id) for member_id in self.member_ids]

    @property
    def categories(self) -> list[Category]:
        """All categories in the server

        Returns
        -------
        list[Category]
            list of all categories
        """
        return list(self._categories.values())


class Ban:
    __slots__ = ("user", "server", "reason")

    def __init__(self, user: Member, server: Server, reason: Optional[str] = None):
        self.user = user
        self.server = server
        self.reason = reason
