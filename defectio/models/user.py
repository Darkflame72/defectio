"""Application and entities that are used to describe Users on Discord."""
from __future__ import annotations

from defectio.models.attachmet import Attachment
from defectio.models.base import Messageable
from defectio.types.base import RelationType
from defectio.types.base import StatusPayload
from defectio.types.base import StatusType

__all__ = [
    "Status",
    "Relationship",
    "Profile",
    "UserBot",
    "PartialUser",
    "BaseUser",
    "OwnUser",
    "User",
]

from typing import Optional, TYPE_CHECKING

import attr

from defectio.models import objects
from defectio import traits


if TYPE_CHECKING:
    pass


@attr.define(hash=False, kw_only=True, weakref_slot=False)
class Status:
    """Status of a user or bot."""

    presence: StatusType = attr.field(eq=False, hash=False, repr=True, default="Online")
    """The presence status."""

    text: str = attr.field(eq=False, hash=False, repr=True)
    """The presence status."""

    @property
    def online(self) -> bool:
        """If the status is online."""
        return self.presence != "Offline"


@attr.define(hash=False, kw_only=True, weakref_slot=False)
class Relationship:
    app: traits.RESTAware = attr.ib(eq=False, hash=False, repr=True)
    """The application instance."""

    other_user_id: str = attr.ib(eq=False, hash=False, repr=True)
    """The ID of the other user."""

    status: RelationType = attr.ib(eq=False, hash=False, repr=True)
    """The status of the relationship."""

    async def send_friend_request(self) -> None:
        """Send or accept a friend request to the user."""
        res = self.app.rest.friend_request(self.other_user_id)
        self.status = res

    async def remove_friend(self) -> None:
        """Deny or remove friend."""
        res = self.app.rest.remove_friend(self.other_user_id)
        self.status = res

    async def unblock(self) -> None:
        """Unblock user."""
        res = self.app.rest.unblock_user(self.other_user_id)
        self.status = res

    async def block(self) -> None:
        """Block user."""
        res = self.app.rest.block_user(self.other_user_id)
        self.status = res


@attr.define(hash=True, kw_only=True, weakref_slot=False)
class Profile:
    """Profile of a user."""

    app: traits.RESTAware = attr.ib(eq=False, hash=False, repr=True)
    """The application instance."""

    id: objects.Object = attr.ib(eq=False, hash=False, repr=True)
    """The ID of the user."""

    content: str = attr.ib(eq=False, hash=False, repr=True)
    """The content of the profile."""

    background: Attachment = attr.ib(eq=False, hash=False, repr=True)
    """The background of the profile."""


class UserBot:
    """Bot information of a user."""

    app: traits.RESTAware = attr.ib(eq=False, hash=False, repr=True)
    """The application instance."""

    bot: bool = attr.ib(eq=False, hash=False, repr=True)
    """Whether the user is a bot or not."""

    owner_id: Optional[objects.Object] = attr.ib(eq=False, hash=False, repr=True)
    """The ID of the bot owner."""

    def __bool__(self) -> bool:
        return self.bot

    @property
    def owner(self):
        if self.bot and self.app is traits.CacheAware:
            return self.app.cache.get_user(self.owner_id)
        return None


@attr.define(hash=True, kw_only=True, weakref_slot=False)
class PartialUser(Messageable):
    """A Partial User Object."""

    @property
    def mention(self) -> str:
        """The mention of this user."""
        return f"#{self.id}"

    def _get_channel(self):
        raise NotImplementedError


@attr.define(hash=True, kw_only=True, weakref_slot=False)
class BaseUser(PartialUser):
    """A BaseUser object."""

    name: str = attr.field(eq=False, hash=False, repr=True)
    """The name of the user."""

    status: Optional[Status] = attr.field(eq=False, hash=False, repr=True)
    """The status of the user."""

    our_relation: Relationship = attr.field(eq=False, hash=False, repr=True)
    """Our relationship with the user."""

    relationships: list[Relationship] = attr.field(eq=False, hash=False, repr=True)
    """Relationships the user has."""

    online: bool = attr.ib(eq=False, hash=False, repr=True, default=False)
    """Whether the user is online or not."""

    # TODO
    # def mentioned_in(self, message: Message) -> bool:
    #     """Checks if the user is mentioned in the specified message.

    #     Parameters
    #     -----------
    #     message: :class:`Message`
    #         The message to check if you're mentioned in.

    #     Returns
    #     -------
    #     :class:`bool`
    #         Indicates if the user is mentioned in the message.
    #     """

    #     return any(user.id == self.id for user in message.mentions)


@attr.define(hash=True, kw_only=True, weakref_slot=False)
class OwnUser(BaseUser):
    """Our User object."""


@attr.define(hash=True, kw_only=True, weakref_slot=False)
class User(BaseUser):
    """A User object."""
