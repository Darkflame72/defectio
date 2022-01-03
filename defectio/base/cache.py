import abc
from typing import Optional
from typing import Sequence

from defectio.models import OwnUser
from defectio.models import Message
from defectio.models import objects
from defectio.models import PartialUser
from defectio.models import Server
from defectio.models import User
from defectio.models.channel import PartialChannel
from defectio.models.member import Member


__all__ = ["Cache", "MutableCache"]


class Cache(abc.ABC):
    __slots__ = ()

    @abc.abstractmethod
    async def get_me(self) -> Optional[OwnUser]:
        """Get own client User from cache.

        Returns
        -------
        Optional[OwnUser]
            Own user object from cache.
        """

    @abc.abstractmethod
    async def get_user(
        self, user: objects.ObjectishOr[PartialUser], /
    ) -> Optional[User]:
        """Get a user object from the cache.

        Parameters
        ----------
        user : objects.ObjectishOr[PartialUser]
            Object or ID of the user to get from the cache.

        Returns
        -------
        Optional[User]
            The object of the user that was found in the cache, else
            `builtins.None`.
        """

    @abc.abstractmethod
    async def get_users_view(self) -> dict[objects.Object, User]:
        """Get a view of the user objects in the cache.

        Returns
        -------
        dict[objects.Object, User]
            The view of user IDs to the users found in the cache.
        """

    @abc.abstractmethod
    async def get_channel(
        self, channel: objects.ObjectishOr[PartialChannel]
    ) -> Optional[PartialChannel]:
        """Get a channel object from an id.

        Parameters
        ----------
        channel : objects.ObjectishOr[PartialChannel]
            Channel object

        Returns
        -------
        Optional[Channel]
            Channel object
        """

    @abc.abstractmethod
    async def get_channel_view(self) -> dict[str, PartialChannel]:
        """Get a view of all of the channels.

        Returns
        -------
        dict[str, Channel]
            dictionary of all chanels
        """

    @abc.abstractmethod
    async def get_server(self, server: objects.ObjectishOr[Server]) -> Optional[Server]:
        """Get a server from the cache.

        Parameters
        ----------
        server : objects.ObjectishOr[Server]
            ID of the server to get.

        Returns
        -------
        Optional[Server]
            `Server` if found in the cache otherwise `None`.
        """

    @abc.abstractmethod
    async def get_servers_view(self) -> dict[str, Server]:
        """Get a view of all server ID's and their Server objects.

        Returns
        -------
        dict[str, Server]
            Server ID to Server object.
        """

    @abc.abstractmethod
    async def get_member(
        self, server: objects.ObjectishOr[Server], user: objects.ObjectishOr[User], /
    ) -> Optional[Member]:
        """Get a member object from the cache.

        Parameters
        ----------
        server : objects.ObjectishOr[Server]
            Object or ID of the server to get a cached member for.
        user : objects.ObjectishOr[User]
            Object or ID of the user to get a cached member for.

        Returns
        -------
        typing.Optional[Member]
            The object of the member found in the cache, else `builtins.None`.
        """

    @abc.abstractmethod
    async def get_members_view(
        self,
    ) -> dict[objects.Object, dict[objects.Object, Member]]:
        """Get a view of all the members objects in the cache.

        Returns
        -------
        dict[objects.Object, dict[objects.Object, Member]]
            A view of server IDs to views of user IDs to objects of the members
            that were found from the cache.
        """

    @abc.abstractmethod
    async def get_message(
        self, message: objects.ObjectishOr[Message], /
    ) -> Optional[Message]:
        """Get a message object from the cache.

        Parameters
        ----------
        message : objects.ObjectishOr[Message]
            Object or ID of the message to get from the cache.

        Returns
        -------
        Optional[Message]
            The object of the message found in the cache or `builtins.None`.
        """

    @abc.abstractmethod
    async def get_messages_view(self) -> dict[objects.Objectish, Message]:
        """Get a view of all the message objects in the cache.

        Returns
        -------
        dict[objects.Objectish, Message]
            A view of message objects found in the cache.
        """


class MutableCache(Cache, abc.ABC):
    """Cache that exposes read-only operations as well as mutation operations.

    This is only exposed to internal components. There is no guarantee the
    user-facing cache will provide these methods or not.
    """

    __slots__: Sequence[str] = ()

    @abc.abstractmethod
    async def clear(self) -> None:
        """Clear the full cache."""

    @abc.abstractmethod
    async def clear_me(self) -> Optional[OwnUser]:
        """Clear the cache of the object for this client.

        Returns
        -------
        Optional[OwnUser]
            User object for this client
        """

    @abc.abstractmethod
    async def set_me(self, user: OwnUser) -> None:
        """Set Client user object.

        Parameters
        ----------
        user : OwnUser
            User to set as client user
        """

    @abc.abstractmethod
    async def update_me(self, user: OwnUser) -> tuple[Optional[OwnUser], OwnUser]:
        """Update user client object.

        Parameters
        ----------
        user : OwnUser
            object to update with.

        Returns
        -------
        tuple[Optional[OwnUser], OwnUser]
            tuple of original and new client user objects.
        """

    @abc.abstractmethod
    async def clear_users(self) -> dict[objects.Object, User]:
        """Clear users from the cache.

        Returns
        -------
        dict[objects.Object, User]
            previous user object
        """

    @abc.abstractmethod
    async def delete_user(
        self, user: objects.ObjectishOr[PartialUser], /
    ) -> Optional[PartialUser]:
        """Delete user from the cache.

        Parameters
        ----------
        user : objects.ObjectishOr[PartialUser]
            user to delete

        Returns
        -------
        Optional[PartialUser]
            User object that existed
        """

    @abc.abstractmethod
    async def set_user(self, user: PartialUser, /) -> None:
        """Set user object in the cache.

        Parameters
        ----------
        user : PartialUser
            User to set.
        """

    @abc.abstractmethod
    async def update_user(
        self, user: PartialUser, /
    ) -> tuple[Optional[PartialUser], PartialUser]:
        """Update user object in the cache.

        Parameters
        ----------
        user : PartialUser
            User object to udpate with

        Returns
        -------
        tuple[Optional[PartialUser], PartialUser]
            Previous user object and new one.
        """

    @abc.abstractmethod
    async def clear_channels(self) -> dict[objects.Object, PartialChannel]:
        """Clear channels from the cache.

        Returns
        -------
        dict[objects.Object, channel]
            previous channel object
        """

    @abc.abstractmethod
    async def delete_channel(
        self, channel: objects.ObjectishOr[PartialChannel], /
    ) -> Optional[PartialChannel]:
        """Delete channel from the cache.

        Parameters
        ----------
        channel : objects.ObjectishOr[PartialChannel]
            channel to delete

        Returns
        -------
        Optional[PartialChannel]
            channel object that existed
        """

    @abc.abstractmethod
    async def set_channel(self, channel: PartialChannel, /) -> None:
        """Set channel object in the cache.

        Parameters
        ----------
        channel : PartialChannel
            channel to set.
        """

    @abc.abstractmethod
    async def update_channel(
        self, channel: PartialChannel, /
    ) -> tuple[Optional[PartialChannel], PartialChannel]:
        """Update channel object in the cache.

        Parameters
        ----------
        channel : PartialChannel
            channel object to udpate with

        Returns
        -------
        tuple[Optional[PartialChannel], PartialChannel]
            Previous channel object and new one.
        """

    @abc.abstractmethod
    async def clear_servers(self) -> dict[objects.Object, Server]:
        """Remove all the server objects from the cache.

        Returns
        -------
        dict[objects.Object, objects.Object]
            Cache view of server IDs to server IDs which were cleared from the
            cache.
        """

    @abc.abstractmethod
    async def delete_server(
        self, server: objects.ObjectishOr[Server], /
    ) -> Optional[Server]:
        """Remove a server object from the cache.

        Parameters
        ----------
        server : objects.ObjectishOr[Server]
            Object or ID of the server to remove from the cache.

        Returns
        -------
        Optional[Server]
            The server object which was removed from the cache if found, else
            `builtins.None`.
        """

    @abc.abstractmethod
    async def set_server(self, server: objects.ObjectishOr[Server], /) -> None:
        """Add a server object to the cache.

        Parameters
        ----------
        server : objects.ObjectishOr[Server]
            Object or ID of the server to add to the cache.
        """

    @abc.abstractmethod
    async def update_server(
        self,
        server: objects.ObjectishOr[Server],
        /,
    ) -> tuple[Server, Server]:
        """Update a server object in the cache.

        Parameters
        ----------
        server : objects.ObjectishOr[Server]
            Object or ID of the server to update in the cache.

        Returns
        -------
        Tuple[Server], Optional[Server]]
            A tuple of the old cached server object if found (else `builtins.None`)
            and the object of the server that was added to the cache if it could
            be added (else `builtins.None`).
        """

    @abc.abstractmethod
    async def clear_members(self) -> dict[objects.Object, Member]:
        """Clear members from the cache.

        Returns
        -------
        dict[objects.Object, Member]
            previous member object
        """

    @abc.abstractmethod
    async def delete_member(
        self, member: objects.ObjectishOr[Member], /
    ) -> Optional[Member]:
        """Delete member from the cache.

        Parameters
        ----------
        member : objects.ObjectishOr[Member]
            member to delete

        Returns
        -------
        Optional[Member]
            member object that existed
        """

    @abc.abstractmethod
    async def set_member(self, member: Member, /) -> None:
        """Set member object in the cache.

        Parameters
        ----------
        member : Member
            member to set.
        """

    @abc.abstractmethod
    async def update_member(self, member: Member, /) -> tuple[Optional[Member], Member]:
        """Update member object in the cache.

        Parameters
        ----------
        member : Member
            member object to udpate with

        Returns
        -------
        tuple[Optional[Member], Member]
            Previous member object and new one.
        """

    @abc.abstractmethod
    async def clear_messages(self) -> dict[objects.Object, Message]:
        """Clear messages from the cache.

        Returns
        -------
        dict[objects.Object, Message]
            previous message object
        """

    @abc.abstractmethod
    async def delete_message(
        self, message: objects.ObjectishOr[Message], /
    ) -> Optional[Message]:
        """Delete message from the cache.

        Parameters
        ----------
        message : objects.ObjectishOr[Message]
            message to delete

        Returns
        -------
        Optional[Message]
            message object that existed
        """

    @abc.abstractmethod
    async def set_message(self, message: Message, /) -> None:
        """Set message object in the cache.

        Parameters
        ----------
        message : Message
            message to set.
        """

    @abc.abstractmethod
    async def update_message(
        self, message: Message, /
    ) -> tuple[Optional[Message], Message]:
        """Update message object in the cache.

        Parameters
        ----------
        message : Message
            message object to udpate with

        Returns
        -------
        tuple[Optional[Message], Message]
            Previous message object and new one.
        """
