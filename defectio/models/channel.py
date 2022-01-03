from __future__ import annotations
from typing import Optional, Union, TYPE_CHECKING

import attr

from defectio.models.base import Messageable
from defectio.models import objects

if TYPE_CHECKING:
    from defectio.models.permission import ChannelPermission
    from defectio.models.server import Server
    from defectio.models.user import PartialUser


__all__ = [
    "SavedMessageChannel",
    "DMChannel",
    "GroupChannel",
    "MessageableChannel",
    "TextChannel",
    "ServerChannel",
    "VoiceChannel",
]


class PartialChannel(objects.Unique):
    pass


@attr.define(hash=True, kw_only=True, weakref_slot=False)
class SavedMessageChannel(Messageable, PartialChannel):
    """A channel that can be saved."""

    async def _get_channel(self) -> SavedMessageChannel:
        return self


@attr.define(hash=True, kw_only=True, weakref_slot=False)
class DMChannel(Messageable, PartialChannel):
    """Direct Message Channel."""

    active: bool = attr.ib(eq=False, hash=False, repr=True)
    """Whether or not the channel is active."""

    recipient_ids: list[objects.Object] = attr.ib(eq=False, hash=False, repr=True)
    """The IDs of the recipients of the channel."""

    async def _get_channel(self) -> DMChannel:
        return self

    @property
    def recipients(self) -> list[PartialUser]:
        return [self.app.cache.get_user(user) for user in self._recipients]


class GroupChannel(DMChannel, PartialChannel):
    """Group DM Channel."""

    async def _get_channel(self) -> GroupChannel:
        return self


class ServerChannel(PartialChannel):
    pass


@attr.define(hash=True, kw_only=True, weakref_slot=False)
class TextChannel(Messageable, ServerChannel):
    """Text channel."""

    server_id: objects.Object = attr.ib(eq=False, hash=False, repr=True)
    """The server id s the channel belongs to."""

    description: Optional[str] = attr.ib(eq=False, hash=False, repr=True)
    """The description of the channel."""

    name: str = attr.ib(eq=False, hash=False, repr=True)
    """The name of the channel."""

    overrides: dict[objects.Object, ChannelPermission] = attr.ib(
        eq=False, hash=False, repr=True, default={}
    )
    """The overrides of the channel."""

    nsfw: bool = attr.ib(eq=False, hash=False, repr=True, default=False)
    """Whether the channel is nsfw."""

    @property
    def server(self) -> Server:
        return self.app.cache.get_server(server_id)

    async def _get_channel(self) -> TextChannel:
        return self


@attr.define(hash=True, kw_only=True, weakref_slot=False)
class VoiceChannel(ServerChannel):
    """Voice channel."""

    server: Server = attr.ib(eq=False, hash=False, repr=True)
    """The server the channel belongs to."""

    description: str = attr.ib(eq=False, hash=False, repr=True)
    """The description of the channel."""

    name: str = attr.ib(eq=False, hash=False, repr=True)
    """The name of the channel."""

    overrides: dict[objects.Object, ChannelPermission] = attr.ib(
        eq=False, hash=False, repr=True, default={}
    )
    """The overrides of the channel."""

    async def _get_channel(self) -> VoiceChannel:
        return self


MessageableChannel = Union[
    SavedMessageChannel,
    DMChannel,
    GroupChannel,
    TextChannel,
    VoiceChannel,
]
