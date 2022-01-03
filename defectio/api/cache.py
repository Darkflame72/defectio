from copy import copy
from typing import Optional
from typing import Sequence

from defectio import config
from defectio.base.cache import Cache as BaseCache
from defectio.base.cache import MutableCache as BaseMutableCache
from defectio.models import OwnUser
from defectio.models import Message
from defectio.models import objects
from defectio.models import PartialUser
from defectio.models import Server
from defectio.models import User
from defectio.models.channel import PartialChannel
from defectio.models.member import Member
from defectio.models.server import Server
from defectio.models.user import BaseUser
from defectio.models.user import OwnUser

__all__ = ["Cache", "MutableCache"]


class Cache(BaseCache):
    """
    Cache class.
    """

    __slots__ = (
        "_me",
        "_users",
        "_channels",
        "_servers",
        "_members",
        "_messages",
        "_settings",
    )

    _me: Optional[OwnUser]
    _users: dict[objects.Object, BaseUser]
    _channels: dict[objects.Object, PartialChannel]
    _servers: dict[objects.Object, Server]
    _members: dict[objects.Object, Member]
    _settings: config.CacheSettings
    _messages: dict[objects.Object, Message]

    def __init__(self, settings: config.CacheSettings) -> None:
        """
        Initialize the cache.
        """
        self._settings = settings
        self._create_cache()

    @property
    async def settings(self) -> config.CacheSettings:
        return self._settings

    def _create_cache(self) -> None:
        """
        Create the cache.
        """
        self._me = {}
        self._users = {}
        self._channels = {}
        self._servers = {}
        self._members = {}
        self._messages = {}

    async def clear(self) -> None:
        if self._settings.components == config.CacheComponents.NONE:
            return None

        self._create_cache()

    async def get_me(self) -> Optional[OwnUser]:
        return self._me

    async def get_user(
        self, user: objects.ObjectishOr[PartialUser], /
    ) -> Optional[User]:
        return self._users.get(objects.Object(user), None)

    async def get_users_view(self) -> dict[objects.Object, User]:
        return self._users

    async def get_channel(
        self, channel: objects.ObjectishOr[PartialChannel]
    ) -> Optional[PartialChannel]:
        return self._channels.get(str(channel), None)

    async def get_channel_view(self) -> dict[str, PartialChannel]:
        return self._channels

    async def get_server(self, server: objects.ObjectishOr[Server]) -> Optional[Server]:
        return self._servers.get(str(server), None)

    async def get_servers_view(self) -> dict[str, Server]:
        return self._servers

    async def get_member(
        self, server: objects.ObjectishOr[Server], user: objects.ObjectishOr[User], /
    ) -> Optional[Member]:
        # TODO
        return self._members.get(str())

    async def get_members_view(
        self,
    ) -> dict[objects.Object, dict[objects.Object, Member]]:
        return self._members

    async def get_message(
        self, message: objects.ObjectishOr[Message], /
    ) -> Optional[Message]:
        return self._messages.get(str(message), None)

    async def get_messages_view(self) -> dict[objects.Objectish, Message]:
        return self._messages


class MutableCache(Cache, BaseMutableCache):

    __slots__: Sequence[str] = ()

    async def clear(self) -> None:
        self._create_cache()

    async def clear_me(self) -> Optional[OwnUser]:
        old_me = copy.copy(self._me)
        self._me = None
        return old_me

    async def set_me(self, user: OwnUser) -> None:
        self._me = user

    async def update_me(self, user: OwnUser) -> tuple[Optional[OwnUser], OwnUser]:
        old_me = copy.copy(self._me)
        self._me = user
        return tuple(old_me, self._me)

    async def clear_users(self) -> dict[objects.Object, User]:
        old_users = copy.copy(self._users)
        self._users = {}
        return old_users

    async def delete_user(
        self, user: objects.ObjectishOr[PartialUser], /
    ) -> Optional[PartialUser]:
        old_user = self._users.pop(objects.Object(user), None)
        return old_user

    async def set_user(self, user: PartialUser, /) -> None:
        self._users[objects.Object(user)] = user

    async def update_user(
        self, user: PartialUser, /
    ) -> tuple[Optional[PartialUser], PartialUser]:
        old_user = self._users.get(objects.Object(user), None)
        self._users[objects.Object(user)] = user
        return tuple(old_user, self._users[objects.Object(user)])

    async def clear_channels(self) -> dict[objects.Object, PartialChannel]:
        old_channels = self._channels
        self._channels = {}
        return (old_channels, self._channels)

    async def delete_channel(
        self, channel: objects.ObjectishOr[PartialChannel], /
    ) -> Optional[PartialChannel]:
        old_channel = self._channels.pop(objects.Object(channel), None)
        return old_channel

    async def set_channel(self, channel: PartialChannel, /) -> None:
        self._channels[objects.Object(channel)] = channel

    async def update_channel(
        self, channel: PartialChannel, /
    ) -> tuple[Optional[PartialChannel], PartialChannel]:
        old_channel = self._channels.get(objects.Object(channel), None)
        self._channels[objects.Object(channel)] = channel
        return tuple(old_channel, self._channels[objects.Object(channel)])

    async def clear_servers(self) -> dict[objects.Object, Server]:
        old_servers = self._servers
        self._servers = {}
        return old_servers

    async def delete_server(
        self, server: objects.ObjectishOr[Server], /
    ) -> Optional[Server]:
        old_server = self._servers.pop(objects.Object(server), None)
        return old_server

    async def set_server(self, server: objects.ObjectishOr[Server], /) -> None:
        self._servers[objects.Object(server)] = server

    async def update_server(
        self,
        server: objects.ObjectishOr[Server],
        /,
    ) -> tuple[Server, Server]:
        old_server = self._servers.get(objects.Object(server), None)
        self._servers[objects.Object(server)] = server
        return tuple(old_server, self._servers[objects.Object(server)])

    async def clear_members(self) -> dict[objects.Object, Member]:
        old_members = self._members
        self._members = {}
        return old_members

    async def delete_member(
        self, member: objects.ObjectishOr[Member], /
    ) -> Optional[Member]:
        old_member = self._members.pop(objects.Object(member), None)
        return old_member

    async def set_member(self, member: Member, /) -> None:
        self._members[objects.Object(member)] = member

    async def update_member(self, member: Member, /) -> tuple[Optional[Member], Member]:
        old_member = self._members.get(objects.Object(member), None)
        self._members[objects.Object(member)] = member
        return tuple(old_member, self._members[objects.Object(member)])

    async def clear_messages(self) -> dict[objects.Object, Message]:
        old_messages = self._messages
        self._messages = {}
        return old_messages

    async def delete_message(
        self, message: objects.ObjectishOr[Message], /
    ) -> Optional[Message]:
        old_message = self._messages.pop(objects.Object(message), None)
        return old_message

    async def set_message(self, message: Message, /) -> None:
        self._messages[objects.Object(message)] = message

    async def update_message(
        self, message: Message, /
    ) -> tuple[Optional[Message], Message]:
        old_message = self._messages.get(objects.Object(message), None)
        self._messages[objects.Object(message)] = message
        return tuple(old_message, self._messages[objects.Object(message)])
