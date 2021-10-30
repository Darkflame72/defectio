import abc
from typing import Optional
from typing import Sequence
from typing import TYPE_CHECKING

from defectio.models import ClientUser
from defectio.models import DirectMessage
from defectio.models import Message
from defectio.models import objects
from defectio.models import PartialUser
from defectio.models import Server
from defectio.models import ServerChannel
from defectio.models import User
from defectio.models.member import Member
from defectio.models.server import Role


__all__ = ["Cache", "MutableCache"]


class Cache(abc.ABC):
    __slots__ = ()

    @abc.abstractmethod
    def get_dm_channel_id(
        self, user: objects.ObjectishOr[PartialUser]
    ) -> Optional[objects.Object]:
        """Get the DM channel ID for a user.

        Parameters
        ----------
        user : objects.ObjectishOr[PartialUser]
            User to get the DM channel for.

        Returns
        -------
        Optional[objects.Object]
            The DM channel ID, or None if the user does not have a DM channel.
        """

    @abc.abstractmethod
    def get_dm_channel_ids_view(self) -> dict[objects.Object, objects.Object]:
        """Get a view of all users and their linked DM channel IDs.

        Returns
        -------
        dict[objects.Object, objects.Object]
            User to DM channel ID.
        """

    @abc.abstractmethod
    def get_server(self, server: objects.ObjectishOr[Server]) -> Optional[Server]:
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
    def get_servers_view(self) -> dict[str, Server]:
        """Get a view of all server ID's and their Server objects.

        Returns
        -------
        dict[str, Server]
            Server ID to Server object.
        """

    @abc.abstractmethod
    def get_server_channel(
        self, channel: objects.ObjectishOr[ServerChannel]
    ) -> Optional[ServerChannel]:
        """Get a Server Channel from the cache.

        Parameters
        ----------
        channel : objects.ObjectishOr[ServerChannel]
            Channel to get.

        Returns
        -------
        Optional[ServerChannel]
            Channel that belongs to a server.
        """

    @abc.abstractmethod
    def get_server_channels_view(self) -> dict[str, ServerChannel]:
        """Get a view of all server ID's and their Server Channel objects.

        Returns
        -------
        dict[str, ServerChannel]
            Channel ID to Channel object.
        """

    @abc.abstractmethod
    def get_server_channels_view_for_server(
        self, server: objects.ObjectishOr[Server]
    ) -> dict[str, ServerChannel]:
        """Get a view of the Server Channels for a specific Server

        Parameters
        ----------
        server : [type]
            Server to get the channels for.

        Returns
        -------
        dict[str, ServerChannel]
            A view of channel ID to Channel object.
        """

    @abc.abstractmethod
    def get_me(self) -> Optional[ClientUser]:
        """Get own client User from cache.

        Returns
        -------
        Optional[ClientUser]
            Own user object from cache.
        """

    @abc.abstractmethod
    def get_member(
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
    def get_members_view(
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
    def get_members_view_for_server(
        self, server_id: objects.Objectish, /
    ) -> dict[objects.Object, Member]:
        """Get a view of the members cached for a specific server.

        Parameters
        ----------
        server_id : objects.Objectish
            The ID of the server to get the cached member view for.

        Returns
        -------
        CacheView[objects.Object, Member]
            The view of user IDs to the members cached for the specified server.
        """

    @abc.abstractmethod
    def get_message(
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
    def get_messages_view(self) -> dict[objects.Objectish, Message]:
        """Get a view of all the message objects in the cache.

        Returns
        -------
        dict[objects.Objectish, Message]
            A view of message objects found in the cache.
        """

    @abc.abstractmethod
    def get_role(self, role: objects.ObjectishOr[Role], /) -> Optional[Role]:
        """Get a role object from the cache.

        Parameters
        ----------
        role : objects.ObjectishOr[Role]
            Object or ID of the role to get from the cache.

        Returns
        -------
        Optional[Role]
            The object of the role found in the cache or `builtins.None`.
        """

    @abc.abstractmethod
    def get_roles_view(self) -> dict[objects.Object, Role]:
        """Get a view of all the role objects in the cache.

        Returns
        -------
        dict[objects.Object, Role]
            A view of role IDs to objects of the roles found in the cache.
        """

    @abc.abstractmethod
    def get_roles_view_for_server(
        self, server: objects.ObjectishOr[Server], /
    ) -> dict[objects.Object, Role]:
        """Get a view of the roles in the cache for a specific server.

        Parameters
        ----------
        server : objects.ObjectishOr[Server]
            Object or ID of the server to get the cached roles for.

        Returns
        -------
        dict[objects.Object, Role]
            A view of role IDs to objects of the roles that were found in the
            cache for the specified server.
        """

    @abc.abstractmethod
    def get_user(self, user: objects.ObjectishOr[PartialUser], /) -> Optional[User]:
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
    def get_users_view(self) -> dict[objects.Object, User]:
        """Get a view of the user objects in the cache.

        Returns
        -------
        dict[objects.Object, User]
            The view of user IDs to the users found in the cache.
        """


class MutableCache(Cache, abc.ABC):
    """Cache that exposes read-only operations as well as mutation operations.

    This is only exposed to internal components. There is no guarantee the
    user-facing cache will provide these methods or not.
    """

    __slots__: Sequence[str] = ()

    @abc.abstractmethod
    def clear(self) -> None:
        """Clear the full cache."""

    @abc.abstractmethod
    def clear_dm_channel_ids(
        self,
    ) -> dict[objects.Object, DirectMessage]:
        """Remove all the cached DM channel IDs.

        Returns
        -------
        dict[objects.Object, DirectMessage]
            Cache view of user IDs to DM channel IDs which were cleared from
            the cache.
        """

    @abc.abstractmethod
    def delete_dm_channel_id(
        self, user: objects.ObjectishOr[PartialUser], /
    ) -> Optional[objects.Object]:
        """Remove a DM channel ID from the cache.

        Parameters
        ----------
        user : objects.ObjectishOr[PartialUser]
            Object or ID of the user to remove the cached DM channel ID for.

        Returns
        -------
        Optional[objects.Object]
            The DM channel ID which was removed from the cache if found, else
            `builtins.None`.
        """

    @abc.abstractmethod
    def set_dm_channel_id(
        self,
        user: objects.ObjectishOr[PartialUser],
        channel: objects.ObjectishOr[DirectMessage],
        /,
    ) -> None:
        """Add a DM channel ID to the cache.

        Parameters
        ----------
        user : objects.ObjectishOr[PartialUser]
            Object or ID of the user to add a DM channel ID to the cache for.
        channel : objects.ObjectishOr[DirectMessage]
            Object or ID of the DM channel to add to the cache.
        """

    @abc.abstractmethod
    def clear_servers(self) -> dict[objects.Object, Server]:
        """Remove all the server objects from the cache.

        Returns
        -------
        dict[objects.Object, objects.Object]
            Cache view of server IDs to server IDs which were cleared from the
            cache.
        """

    @abc.abstractmethod
    def delete_server(self, server: objects.ObjectishOr[Server], /) -> Optional[Server]:
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
    def set_server(self, server: objects.ObjectishOr[Server], /) -> None:
        """Add a server object to the cache.

        Parameters
        ----------
        server : objects.ObjectishOr[Server]
            Object or ID of the server to add to the cache.
        """

    @abc.abstractmethod
    def update_server(
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
    def clear_server_channels(self) -> dict[objects.Object, ServerChannel]:
        """Remove all the channel objects from the cache.

        Returns
        -------
        dict[objects.Object, ServerChannel]
            Cache view of channel IDs to channel IDs which were cleared from the
            cache.
        """

    @abc.abstractmethod
    def clear_server_channels_for_server(
        self, server: objects.ObjectishOr[Server], /
    ) -> dict[objects.Object, ServerChannel]:
        """Remove all the channel objects from the cache for a specific server.

        Parameters
        ----------
        server : objects.ObjectishOr[Server]
            Object or ID of the server to remove all the channel objects from
            the cache for.

        Returns
        -------
        dict[objects.Object, ServerChannel]
            Cache view of channel IDs to channel IDs which were cleared from the
            cache for the specified server.
        """

    @abc.abstractmethod
    def delete_server_channel(
        self, channel: objects.ObjectishOr[ServerChannel], /
    ) -> Optional[ServerChannel]:
        """Remove a channel object from the cache.

        Parameters
        ----------
        channel : objects.ObjectishOr[ServerChannel]
            Object or ID of the channel to remove from the cache.

        Returns
        -------
        Optional[ServerChannel]
            The channel object which was removed from the cache if found, else
            `builtins.None`.
        """

    @abc.abstractmethod
    def set_server_channel(
        self,
        channel: objects.ObjectishOr[ServerChannel],
        /,
    ) -> None:
        """Add a channel object to the cache.

        Parameters
        ----------
        channel : objects.ObjectishOr[ServerChannel]
            Object or ID of the channel to add to the cache.
        """

    @abc.abstractmethod
    def update_server_channel(
        self,
        channel: objects.ObjectishOr[ServerChannel],
        /,
    ) -> tuple[ServerChannel, ServerChannel]:
        """Update a channel object in the cache.

        Parameters
        ----------
        channel : objects.ObjectishOr[ServerChannel]
            Object or ID of the channel to update in the cache.

        Returns
        -------
        Tuple[ServerChannel], Optional[ServerChannel]]
            A tuple of the old cached channel object if found (else `builtins.None`)
            and the object of the channel that was added to the cache if it could
            be added (else `builtins.None`).
        """

    @abc.abstractmethod
    def delete_me(self) -> Optional[ClientUser]:
        """Remove the own user object from the cache.

        Returns
        -------
        Optional[ClientUser]
            The own user object that was removed from the cache if found,
            else `builtins.None`.
        """

    @abc.abstractmethod
    def set_me(self, user: objects.ObjectishOr[ClientUser], /) -> None:
        """Add the own user object to the cache.

        Parameters
        ----------
        user : objects.ObjectishOr[ClientUser]
            Object or ID of the own user to add to the cache.
        """

    @abc.abstractmethod
    def update_me(
        self,
        user: objects.ObjectishOr[ClientUser],
        /,
    ) -> tuple[ClientUser, ClientUser]:
        """Update the own user object in the cache.

        Parameters
        ----------
        user : objects.ObjectishOr[ClientUser]
            Object or ID of the own user to update in the cache.

        Returns
        -------
        Tuple[ClientUser], Optional[ClientUser]]
            A tuple of the old cached own user object if found (else `builtins.None`)
            and the object of the own user that was added to the cache if it could
            be added (else `builtins.None`).
        """

    @abc.abstractmethod
    def clear_members(self) -> dict[objects.Object, Member]:
        """Remove all the member objects from the cache.

        Returns
        -------
        dict[objects.Object, Member]
            Cache view of member IDs to member IDs which were cleared from the
            cache.
        """

    @abc.abstractmethod
    def clear_members_for_server(
        self, server: objects.ObjectishOr[Server], /
    ) -> dict[objects.Object, Member]:
        """Remove all the member objects from the cache for a specific server.

        Parameters
        ----------
        server : objects.ObjectishOr[Server]
            Object or ID of the server to remove all the member objects from
            the cache for.

        Returns
        -------
        dict[objects.Object, Member]
            Cache view of member IDs to member IDs which were cleared from the
            cache for the specified server.
        """

    @abc.abstractmethod
    def delete_member(self, member: objects.ObjectishOr[Member], /) -> Optional[Member]:
        """Remove a member object from the cache.

        Parameters
        ----------
        member : objects.ObjectishOr[Member]
            Object or ID of the member to remove from the cache.

        Returns
        -------
        Optional[Member]
            The member object which was removed from the cache if found, else
            `builtins.None`.
        """

    @abc.abstractmethod
    def set_member(self, member: objects.ObjectishOr[Member], /) -> None:
        """Add a member object to the cache.

        Parameters
        ----------
        member : objects.ObjectishOr[Member]
            Object or ID of the member to add to the cache.
        """

    @abc.abstractmethod
    def update_member(
        self,
        member: objects.ObjectishOr[Member],
        /,
    ) -> tuple[Member, Member]:
        """Update a member object in the cache.

        Parameters
        ----------
        member : objects.ObjectishOr[Member]
            Object or ID of the member to update in the cache.

        Returns
        -------
        Tuple[Member], Optional[Member]]
            A tuple of the old cached member object if found (else `builtins.None`)
            and the object of the member that was added to the cache if it could
            be added (else `builtins.None`).
        """

    @abc.abstractmethod
    def clear_roles(self) -> dict[objects.Object, Role]:
        """Remove all the role objects from the cache.

        Returns
        -------
        dict[objects.Object, Role]
            Cache view of role IDs to role IDs which were cleared from the
            cache.
        """

    @abc.abstractmethod
    def clear_roles_for_server(
        self, server: objects.ObjectishOr[Server], /
    ) -> dict[objects.Object, Role]:
        """Remove all the role objects from the cache for a specific server.

        Parameters
        ----------
        server : objects.ObjectishOr[Server]
            Object or ID of the server to remove all the role objects from
            the cache for.

        Returns
        -------
        dict[objects.Object, Role]
            Cache view of role IDs to role IDs which were cleared from the
            cache for the specified server.
        """

    @abc.abstractmethod
    def delete_role(self, role: objects.ObjectishOr[Role], /) -> Optional[Role]:
        """Remove a role object from the cache.

        Parameters
        ----------
        role : objects.ObjectishOr[Role]
            Object or ID of the role to remove from the cache.

        Returns
        -------
        Optional[Role]
            The role object which was removed from the cache if found, else
            `builtins.None`.
        """

    @abc.abstractmethod
    def set_role(self, role: objects.ObjectishOr[Role], /) -> None:
        """Add a role object to the cache.

        Parameters
        ----------
        role : objects.ObjectishOr[Role]
            Object or ID of the role to add to the cache.
        """

    @abc.abstractmethod
    def update_role(
        self,
        role: objects.ObjectishOr[Role],
        /,
    ) -> tuple[Role, Role]:
        """Update a role object in the cache.

        Parameters
        ----------
        role : objects.ObjectishOr[Role]
            Object or ID of the role to update in the cache.

        Returns
        -------
        Tuple[Role], Optional[Role]]
            A tuple of the old cached role object if found (else `builtins.None`)
            and the object of the role that was added to the cache if it could
            be added (else `builtins.None`).
        """

    @abc.abstractmethod
    def clear_messages(self) -> dict[objects.Object, Message]:
        """Remove all the message objects from the cache.

        Returns
        -------
        dict[objects.Object, Message]
            Cache view of message IDs to message IDs which were cleared from the
            cache.
        """

    @abc.abstractmethod
    def delete_message(
        self, message: objects.ObjectishOr[Message], /
    ) -> Optional[Message]:
        """Remove a message object from the cache.

        Parameters
        ----------
        message : objects.ObjectishOr[Message]
            Object or ID of the message to remove from the cache.

        Returns
        -------
        Optional[Message]
            The message object which was removed from the cache if found, else
            `builtins.None`.
        """

    @abc.abstractmethod
    def set_message(self, message: objects.ObjectishOr[Message], /) -> None:
        """Add a message object to the cache.

        Parameters
        ----------
        message : objects.ObjectishOr[Message]
            Object or ID of the message to add to the cache.
        """

    @abc.abstractmethod
    def update_message(
        self,
        message: objects.ObjectishOr[Message],
        /,
    ) -> tuple[Message, Message]:
        """Update a message object in the cache.

        Parameters
        ----------
        message : objects.ObjectishOr[Message]
            Object or ID of the message to update in the cache.

        Returns
        -------
        Tuple[Message], Optional[Message]]
            A tuple of the old cached message object if found (else `builtins.None`)
            and the object of the message that was added to the cache if it could
            be added (else `builtins.None`).
        """
