from __future__ import annotations
from typing import Optional

import attr
from typing import TYPE_CHECKING
from defectio.models.colour import Colour
from defectio.models import objects
from defectio import traits
from defectio.models.attachmet import Attachment
from defectio.models.permission import ChannelPermission
from defectio.models.permission import ServerPermission
from defectio.models.user import PartialUser

if TYPE_CHECKING:
    from defectio.models.channel import MessageableChannel
    from defectio.models.member import Member


@attr.define(hash=False, kw_only=True, weakref_slot=False)
class Invite:
    """An invite to a channel."""

    code: str = attr.ib(eq=False, hash=False, repr=True)
    """Invite code."""


@attr.define(hash=True, kw_only=True, weakref_slot=False)
class Role(objects.Unique):
    """A role in a server."""

    app: traits.RESTAware = attr.ib(eq=False, hash=False, repr=True)
    """The application instance."""

    id: objects.Object = attr.ib(eq=False, hash=False, repr=True)
    """The ID of the role."""

    name: str = attr.ib(eq=False, hash=False, repr=True)
    """The name of the role."""

    colour: Colour = attr.ib(eq=False, hash=False, repr=True)
    """The colour of the role."""

    hoist: bool = attr.ib(eq=False, hash=False, repr=True, default=False)
    """Whether or not the role is hoisted."""

    rank: int = attr.ib(eq=False, hash=False, repr=True, default=0)
    """The rank of the role."""

    default_server_permissions: ServerPermission = attr.ib(
        eq=False, hash=False, repr=True
    )
    """The default server permissions of the role."""

    default_channel_permissions: ChannelPermission = attr.ib(
        eq=False, hash=False, repr=True
    )
    """The default channel permissions of the role."""

    @property
    def color(self) -> Optional[Colour]:
        """The colour of the role for those who use the American spelling."""
        return self.colour


@attr.define(hash=True, kw_only=True, weakref_slot=False)
class Category(objects.Unique):
    """A category in a server."""

    app: traits.RESTAware = attr.ib(eq=False, hash=False, repr=True)
    """The application instance."""

    id: objects.Object = attr.ib(eq=False, hash=False, repr=True)
    """The ID of the category."""

    channels: list[MessageableChannel] = attr.ib(
        eq=False, hash=False, repr=True, default=[]
    )
    """The channels in the category."""


@attr.define(hash=True, kw_only=True, weakref_slot=False)
class Server(objects.Unique):
    """Server object."""

    app: traits.RESTAware = attr.ib(eq=False, hash=False, repr=True)
    """The application instance."""

    id: objects.Object = attr.ib(eq=False, hash=True, repr=True)
    """The ID of the server."""

    name: str = attr.ib(eq=False, hash=False, repr=True)
    """The name of the server."""

    owner_id: objects.Object = attr.ib(eq=False, hash=False, repr=True)
    """The owner of the server."""

    description: Optional[str] = attr.ib(eq=False, hash=False, repr=True)
    """The description of the server."""

    channel_ids: list[objects.Object] = attr.ib(
        eq=False, hash=False, repr=True, default=[]
    )
    """The IDs of the channels in the server."""

    member_ids: list[objects.Object] = attr.ib(
        eq=False, hash=False, repr=True, default=[]
    )
    """The IDs of the members in the server."""

    roles: list[Role] = attr.ib(eq=False, hash=False, repr=True, default=[])
    """The roles in the server."""

    banner: Optional[Attachment] = attr.ib(
        eq=False, hash=False, repr=True, default=None
    )
    """The banner of the server."""

    server_permissions: ServerPermission = attr.ib(eq=False, hash=False, repr=True)
    """The server permissions of the server."""

    # TODO
    # channel_permissions: ChannelPermission = attr.ib(eq=False, hash=False, repr=True)
    """The channel permissions of the server."""

    icon: Optional[Attachment] = attr.ib(eq=False, hash=False, repr=True)
    """The icon of the server."""

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


@attr.define(hash=False, kw_only=True, weakref_slot=False)
class Ban:
    """A ban object."""

    user: PartialUser = attr.ib(eq=False, hash=False, repr=True)
    """The user banned."""

    reason: Optional[str] = attr.ib(eq=False, hash=False, repr=True, default=None)
    """The reason for the ban."""

    server: Server = attr.ib(eq=False, hash=False, repr=True)
    """The server the ban is for."""

    user: Member = attr.ib(eq=False, hash=False, repr=True)
    """The user banned."""

    reason: Optional[str] = attr.ib(eq=False, hash=False, repr=True, default=None)
    """The reason for the ban."""

    def __str__(self) -> str:
        return f"{self.user.name}#{self.user.discriminator} ({self.user.id})"

    def __repr__(self) -> str:
        return f"<Ban user={self.user} reason={self.reason}>"
