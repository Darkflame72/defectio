"""Provides an interface for REST API implementations to follow."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import io
    from defectio.models.apiinfo import ApiInfo
    from defectio.types.payloads import AccountPayload, LoginPayload
    from defectio.models.user import ClientUser
    from defectio.models.message import Message
    from defectio.models.attachment import Attachment
    from defectio.models.permission import ChannelPermission
    from defectio.models.server import Role, Server, Colour
    from typing import Union
    from typing import Literal
    from typing import Optional
    from defectio.models.member import Member
    from defectio.models.permission import Permission
    from defectio.models.server import Ban
    from defectio.models.server import Category
    from defectio.models.server import SystemMessages
    from defectio.models.user import Bot
    from defectio.state import Channel
    from defectio.models.channel import (
        DMChannel,
        DMChannel,
        GroupChannel,
        Invite,
        PartialChannel,
        ServerChannel,
        TextChannel,
        VoiceChannel,
    )
    from defectio.models import objects
    from defectio.models.user import PartialUser, Profile, Relationship, Status
    from defectio.types.payloads import (
        JoinVoice,
        Messages,
        RelationType,
        SessionPayload,
    )

__all__ = ["RESTClient"]

import abc


class RESTClient(abc.ABC):
    """Interface for functionality that a REST API implementation provides."""

    __slots__: tuple[str] = ()

    @property
    @abc.abstractmethod
    def is_alive(self) -> bool:
        """Whether this component is alive."""

    @abc.abstractmethod
    async def close(self) -> None:
        """Close the client session."""

    @abc.abstractmethod
    async def node_info(self) -> ApiInfo:
        """Get the info about the Revolt server we are connected to.

        Returns
        -------
        ApiInfo
            ApiInfo object describing the Revolt server.
        """

    @abc.abstractmethod
    async def check_onboarding(self) -> bool:
        """Check whether the user is onboarded.

        Returns
        -------
        bool
            Whether the user is onboarded.
        """

    @abc.abstractmethod
    async def complete_onboarding(self, username: str) -> None:
        """Complete onboarding and set username.

        Parameters
        ----------
        username : str
            Username to set.
        """

    @abc.abstractmethod
    async def fetch_account(self) -> AccountPayload:
        """Fetch account information.

        Returns
        -------
        AccountPayload
            Account information.
        """

    @abc.abstractmethod
    async def create_account(
        self,
        email: str,
        password: str,
        *,
        invite: Optional[str] = None,
        captcha: Optional[str] = None,
    ) -> None:
        """Create a new account.

        Parameters
        ----------
        email : str
            Email address to use for the account.
        password : str
            Password to use for the account.
        invite : Optional[str], optional
            Invite code to use for the account.
        captcha : Optional[str], optional
            Captcha to use for the account.
        """

    @abc.abstractmethod
    async def resend_verification(
        self, email: str, *, captch: Optional[str] = None
    ) -> None:
        """Resend the verification email.

        Parameters
        ----------
        email : str
            Email address to use for the account.
        captch : Optional[str], optional
            Captcha to use for the account.
        """

    @abc.abstractmethod
    async def verify_email(self, code: str) -> None:
        """Verifies an email with code.

        Parameters
        ----------
        code : str
            Code to use for verification.
        """

    @abc.abstractmethod
    async def send_password_reset(
        self, email: str, *, captcha: Optional[str] = None
    ) -> None:
        """Send a password reset email.

        Parameters
        ----------
        email : str
            Email address to use for the account.
        captcha : Optional[str], optional
            Captcha to use for the account.
        """

    @abc.abstractmethod
    async def password_reset(self, password: str, token: str) -> None:
        """Reset the password.

        Parameters
        ----------
        password : str
            Password to use for the account.
        token : str
            Token to use for the account.
        """

    @abc.abstractmethod
    async def change_password(self, password: str, current_password: str) -> None:
        """Change the password.

        Parameters
        ----------
        password : str
            New password to use for the account.
        current_password : str
            Current password used for the account.
        """

    @abc.abstractmethod
    async def change_email(self, current_password: str, email: str) -> None:
        """Change the email.

        Parameters
        ----------
        current_password : str
            Current password used for the account.
        email : str
            New email address to use for the account.
        """

    @abc.abstractmethod
    async def login(
        self,
        email: str,
        *,
        password: Optional[str] = None,
        challange: Optional[str] = None,
        friendly_name: Optional[str] = None,
        captcha: Optional[str] = None,
    ) -> LoginPayload:
        """Login to the Revolt server and get a new session.

        Parameters
        ----------
        email : str
            Email address to use for the account.
        password : Optional[str], optional
            Password to use for the account.
        challange : Optional[str], optional
            Challange to use for the account.
        friendly_name : Optional[str], optional
            Friendly name to use for the session.
        captcha : Optional[str], optional
            Captcha to use for verification.

        Returns
        -------
        LoginPayload
            Login information.
        """

    @abc.abstractmethod
    async def logout(self) -> None:
        """Logout of the current session."""

    @abc.abstractmethod
    async def edit_session(self, friendly_name: str) -> None:
        """Edit the session.

        Parameters
        ----------
        friendly_name : str
            Friendly name to use for the session.
        """

    @abc.abstractmethod
    async def delete_session(self) -> None:
        """Delete the session."""

    @abc.abstractmethod
    async def fetch_sessions(self) -> List[SessionPayload]:
        """Fetch all existing sessions.

        Returns
        -------
        List[SessionPayload]
            List of session information.
        """

    @abc.abstractmethod
    async def delete_all_sessions(self, revoke_self: bool) -> None:
        """Delete all sessions.

        Parameters
        ----------
        revoke_self : bool
            Whether to revoke the current session.
        """

    @abc.abstractmethod
    async def fetch_user(self) -> ClientUser:
        """Fetch the current user.

        Returns
        -------
        ClientUser
            User information.
        """

    @abc.abstractmethod
    async def edit_user(
        self,
        *,
        status: Optional[Status] = None,
        profile: Optional[Profile] = None,
        avatar: Optional[str] = None,
        remove: Optional[
            Literal["Avatar", "ProfileBackground", "ProfileContent", "StatusText"]
        ] = None,
    ) -> None:
        """Edit the user.

        Parameters
        ----------
        status : Optional[Status], optional
            Status to use for the user.
        profile : Optional[Profile], optional
            Profile to use for the user.
        avatar : Optional[str], optional
            Autumn ID of image to use for the avatar.
        remove : Optional[Literal["Avatar", "ProfileBackground", "ProfileContent", "StatusText"]], optional
            Which field to remove.
        """

    @abc.abstractmethod
    async def change_username(self, username: str, password: str) -> None:
        """Change the username.

        Parameters
        ----------
        username : str
            New username to use for the account.
        password : str
            Password used for the account.
        """

    @abc.abstractmethod
    async def fetch_user_profile(
        self, user: objects.ObjectishOr[PartialUser]
    ) -> Profile:
        """Fetch the user profile.

        Parameters
        ----------
        user : ObjectishOr[PartialUser]
            User to fetch the profile for.

        Returns
        -------
        Profile
            User profile.
        """

    @abc.abstractmethod
    async def fetch_default_avatar(self) -> io.BytesIO:
        """Fetch the default avatar.

        Returns
        -------
        io.BytesIO
            Default avatar as a PNG image.
        """

    @abc.abstractmethod
    async def fetch_mutual_friends(
        self, user: objects.ObjectishOr[PartialUser]
    ) -> list[objects.Object]:
        """Fetch the mutual friends.

        Parameters
        ----------
        user : ObjectishOr[PartialUser]
            User to fetch the mutual friends for.

        Returns
        -------
        list[Object]
            List of mutual friends ID's.
        """

    @abc.abstractmethod
    async def fetch_direct_message_channels(self) -> list[DMChannel]:
        """This fetches your direct messages, including any DM and group DM conversations.

        Returns
        -------
        list[DMChannel]
            List of direct message channels.
        """

    @abc.abstractmethod
    async def open_direct_message(
        self, user: objects.ObjectishOr[PartialUser]
    ) -> DMChannel:
        """Open a DM with another user.

        Parameters
        ----------
        user : ObjectishOr[PartialUser]
            User to open a direct message channel with.

        Returns
        -------
        DMChannel
            Direct message channel.
        """

    @abc.abstractmethod
    async def fetch_relationships(self) -> list[Relationship]:
        """Fetch all relationships.

        Returns
        -------
        list[Relationship]
            List of relationships.
        """

    @abc.abstractmethod
    async def fetch_relationship(
        self, user: objects.ObjectishOr[PartialUser]
    ) -> Relationship:
        """Fetch your relationship with another other user.

        Parameters
        ----------
        user : ObjectishOr[PartialUser]
            User to fetch the relationship for.

        Returns
        -------
        Relationship
            Relationship.
        """

    @abc.abstractmethod
    async def friend_request(self, username: Union[str, PartialUser]) -> RelationType:
        """Send a friend request to another user or accept another user's friend request.

        Parameters
        ----------
        username : Union[str, PartialUser]
            Username or user to send a friend request to.

        Returns
        -------
        RelationType
            Relation type.
        """

    @abc.abstractmethod
    async def remove_friend(self, username: Union[str, PartialUser]) -> RelationType:
        """Denies another user's friend request or removes an existing friend.

        Parameters
        ----------
        username : Union[str, PartialUser]
            Username or user to remove.

        Returns
        -------
        RelationType
            Relation type.
        """

    @abc.abstractmethod
    async def block_user(self, user: objects.ObjectishOr[PartialUser]) -> RelationType:
        """Block another user.

        Parameters
        ----------
        user : ObjectishOr[PartialUser]
            User to block

        Returns
        -------
        RelationType
            Relation type.
        """

    @abc.abstractmethod
    async def unblock_user(
        self, user: objects.ObjectishOr[PartialUser]
    ) -> RelationType:
        """Unblock another user.

        Parameters
        ----------
        user : ObjectishOr[PartialUser]
            User to unblock

        Returns
        -------
        RelationType
            Relation type.
        """

    @abc.abstractmethod
    async def fetch_channel(
        self, channel: objects.ObjectishOr[PartialChannel]
    ) -> Channel:
        """Retrieve a channel.

        Parameters
        ----------
        channel : ObjectishOr[PartialChannel]
            Channel to fetch.

        Returns
        -------
        PartialChannel
            PartialChannel.
        """

    @abc.abstractmethod
    async def edit_channel(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        nsfw: Optional[bool] = None,
        remove: Optional[Literal["Description", "Icon"]] = None,
    ) -> None:
        """Edit a channel.

        Parameters
        ----------
        name : Optional[str], optional
            Name to use for the channel.
        description : Optional[str], optional
            Description to use for the channel.
        icon : Optional[str], optional
            Autumn ID of image to use for the icon.
        nsfw : Optional[bool], optional
            Whether the channel is NSFW.
        remove : Optional[Literal["Description", "Icon"]], optional
            Which field to remove.
        """

    @abc.abstractmethod
    async def close_channel(self, channel: objects.ObjectishOr[PartialChannel]) -> None:
        """Deletes a server channel, leaves a group or closes a DM.

        Parameters
        ----------
        channel : ObjectishOr[PartialChannel]
            Channel to close.
        """

    @abc.abstractmethod
    async def create_invite(self, channel: objects.ObjectishOr[TextChannel]) -> Invite:
        """Create an invite for a channel.

        Parameters
        ----------
        channel : ObjectishOr[TextChannel]
            Channel to create an invite for.

        Returns
        -------
        Invite
            Invite.
        """

    @abc.abstractmethod
    async def set_role_permission_channel(
        self,
        channel: objects.ObjectishOr[ServerChannel],
        role: objects.ObjectishOr[Role],
        permissions: ChannelPermission,
    ) -> None:
        """Set the permissions for a role in a channel.

        Parameters
        ----------
        channel : ObjectishOr[ServerChannel]
            Channel to set the permissions for.
        role : ObjectishOr[Role]
            Role to set the permissions for.
        permissions : ChannelPermission
            Permissions to set.
        """

    @abc.abstractmethod
    async def set_default_permission_channel(
        self,
        channel: objects.ObjectishOr[ServerChannel],
        permissions: ChannelPermission,
    ) -> None:
        """Set the default permissions for a channel.

        Parameters
        ----------
        channel : ObjectishOr[ServerChannel]
            Channel to set the permissions for.
        permissions : ChannelPermission
            Permissions to set.
        """

    @abc.abstractmethod
    async def send_message(
        self,
        channel: objects.ObjectishOr[TextChannel],
        content: str,
        nonce: str,
        *,
        attachments: Optional[list[objects.ObjectishOr[Attachment]]] = None,
        replies: Optional[list[objects.ObjectishOr[Message]]] = None,
    ) -> Message:
        """Send a message in a channel.

        Parameters
        ----------
        channel : ObjectishOr[TextChannel]
            Channel to send the message in.
        content : str
            Content of the message.
        nonce : str
            Nonce to use for the message.
        attachments : Optional[list[ObjectishOr[Attachment]]], optional
            Attachments to use for the message.
        replies : Optional[list[ObjectishOr[Message]]], optional
            Messages to reply to.

        Returns
        -------
        Message
            Message.
        """

    @abc.abstractmethod
    async def fetch_messages(
        self,
        channel: objects.ObjectishOr[TextChannel],
        sort: Literal["Latest", "Oldest"],
        *,
        limit: Optional[int] = None,
        before: Optional[objects.ObjectishOr[Message]] = None,
        after: Optional[objects.ObjectishOr[Message]] = None,
        nearby: Optional[objects.ObjectishOr[Message]] = None,
        include_users: Optional[bool] = None,
    ) -> Messages:
        """Fetch messages in a channel.

        Parameters
        ----------
        channel : ObjectishOr[TextChannel]
            Channel to fetch messages from.
        sort : Literal["Latest", "Oldest"]
            Sort to use.
        limit : Optional[int], optional
            Limit to use.
        before : Optional[ObjectishOr[Message]], optional
            Message to fetch messages before.
        after : Optional[ObjectishOr[Message]], optional
            Message to fetch messages after.
        nearby : Optional[ObjectishOr[Message]], optional
            Message to fetch messages nearby.
        include_users : Optional[bool], optional
            Whether to include users in the messages.

        Returns
        -------
        Messages
            Messages.
        """

    @abc.abstractmethod
    async def fetch_message(
        self,
        channel: objects.ObjectishOr[TextChannel],
        message: objects.ObjectishOr[Message],
    ) -> Message:
        """Retrieves a message by ID.

        Parameters
        ----------
        channel : ObjectishOr[TextChannel]
            Channel to fetch the message from.
        message : ObjectishOr[Message]
            Message to fetch.

        Returns
        -------
        Message
            Message.
        """

    @abc.abstractmethod
    async def edit_message(
        self,
        channel: objects.ObjectishOr[TextChannel],
        message: objects.ObjectishOr[Message],
        content: str,
    ) -> None:
        """Edit a message.

        Parameters
        ----------
        channel : ObjectishOr[TextChannel]
            Channel to edit the message in.
        message : ObjectishOr[Message]
            Message to edit.
        content : str
            Content to use.
        """

    @abc.abstractmethod
    async def delete_message(
        self,
        channel: objects.ObjectishOr[TextChannel],
        message: objects.ObjectishOr[Message],
    ) -> None:
        """Delete a message.

        Parameters
        ----------
        channel : ObjectishOr[TextChannel]
            Channel to delete the message from.
        message : ObjectishOr[Message]
            Message to delete.
        """

    @abc.abstractmethod
    async def poll_message_changes(
        self,
        channel: objects.ObjectishOr[TextChannel],
        messages: list[objects.ObjectishOr[Message]],
    ) -> list[objects.Object]:
        """This route returns any changed message objects and tells you if any have been deleted.

        .. note
            This should be used to update the local cache of messages.

        Parameters
        ----------
        channel : ObjectishOr[TextChannel]
            Channel to poll for changes.
        messages : list[ObjectishOr[Message]]
            Messages to poll for changes.
            .. note
                maximum of 150 messages

        Returns
        -------
        list[Object]
            Changes.
        """

    @abc.abstractmethod
    async def search_for_messages(
        self,
        channel: objects.ObjectishOr[TextChannel],
        query: str,
        *,
        sort: Literal["Latest", "Oldest"] = "Latest",
        limit: Optional[int] = None,
        before: Optional[objects.ObjectishOr[Message]] = None,
        after: Optional[objects.ObjectishOr[Message]] = None,
        nearby: Optional[objects.ObjectishOr[Message]] = None,
        include_users: Optional[bool] = None,
    ) -> Messages:
        """This route searches for messages within the given parameters.

        Parameters
        ----------
        channel : ObjectishOr[TextChannel]
            Channel to search for messages in.
        query : str
            Full-text search query.
            See MongoDB documentation for more information.
        sort : Literal["Latest", "Oldest"], optional
            Sort to use.
        limit : Optional[int], optional
            Limit to use.
        before : Optional[ObjectishOr[Message]], optional
            Message to fetch messages before.
        after : Optional[ObjectishOr[Message]], optional
            Message to fetch messages after.
        nearby : Optional[ObjectishOr[Message]], optional
            Message to fetch messages nearby.
        include_users : Optional[bool], optional
            Whether to include users in the messages.

        Returns
        -------
        Messages
            Messages.
        """

    @abc.abstractmethod
    async def acknowledge_message(
        self,
        channel: objects.ObjectishOr[TextChannel],
        message: objects.ObjectishOr[Message],
    ) -> None:
        """Acknowledge a message.

        Parameters
        ----------
        channel : ObjectishOr[TextChannel]
            Channel to acknowledge the message in.
        message : ObjectishOr[Message]
            Message to acknowledge.
        """

    @abc.abstractmethod
    async def create_group(
        self,
        name: str,
        nonce: str,
        *,
        description: Optional[str] = None,
        users: Optional[list[objects.ObjectishOr[PartialUser]]] = None,
        nsfw: Optional[bool] = None,
    ) -> GroupChannel:
        """Create a new group with friends.

        Parameters
        ----------
        name : str
            Name to use.
        nonce : str
            Nonce to use.
        description : Optional[str], optional
            Description to use.
        users : Optional[list[ObjectishOr[PartialUser]]], optional
            Users to invite to the group. You must be friends with the users.
        nsfw : Optional[bool], optional
            Whether to use NSFW.

        Returns
        -------
        GroupChannel
            Group.
        """

    @abc.abstractmethod
    async def fetch_group_members(
        self, channel: objects.ObjectishOr[GroupChannel]
    ) -> list[PartialUser]:
        """Fetch members of a group.

        Parameters
        ----------
        channel : ObjectishOr[GroupChannel]
            Group to fetch members of.

        Returns
        -------
        list[PartialUser]
            Members.
        """

    @abc.abstractmethod
    async def add_group_member(
        self,
        channel: objects.ObjectishOr[GroupChannel],
        user: objects.ObjectishOr[PartialUser],
    ) -> None:
        """Add a member to a group.

        Parameters
        ----------
        channel : ObjectishOr[GroupChannel]
            Group to add the member to.
        user : ObjectishOr[PartialUser]
            User to add.
        """

    @abc.abstractmethod
    async def remove_group_member(
        self,
        channel: objects.ObjectishOr[GroupChannel],
        user: objects.ObjectishOr[PartialUser],
    ) -> None:
        """Remove a member from a group.

        Parameters
        ----------
        channel : ObjectishOr[GroupChannel]
            Group to remove the member from.
        user : ObjectishOr[PartialUser]
            User to remove.
        """

    @abc.abstractmethod
    async def join_call(self, channel: objects.ObjectishOr[VoiceChannel]) -> JoinVoice:
        """Asks the voice server for a token to join the call.

        Parameters
        ----------
        channel : ObjectishOr[VoiceChannel]
            Channel to join.

        Returns
        -------
        JoinVoice
            Join.
        """

    @abc.abstractmethod
    async def fetch_server(self, server: objects.ObjectishOr[Server]) -> Server:
        """Fetch a server.

        Parameters
        ----------
        server : ObjectishOr[Server]
            Server to fetch.

        Returns
        -------
        Server
            Server.
        """

    @abc.abstractmethod
    async def edit_server(
        self,
        server: objects.ObjectishOr[Server],
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        banner: Optional[str] = None,
        categories: Optional[Category] = None,
        system_messages: Optional[SystemMessages] = None,
        nsfw: Optional[bool] = None,
        remove: Optional[Literal["Banner", "Description", "Icon"]] = None,
    ) -> None:
        """Edit a server.

        Parameters
        ----------
        server : ObjectishOr[Server]
            Server to edit.
        name : Optional[str], optional
            New name to use.
        description : Optional[str], optional
            New description to use.
        icon : Optional[str], optional
            Autumn ID of new icon to use
        banner : Optional[str], optional
            Autumn ID of new banner to use
        categories : Optional[Category], optional
            Edited categories.
        system_messages : Optional[SystemMessages], optional
            Edited system messages.
        nsfw : Optional[bool], optional
            Whether to use NSFW.
        remove : Optional[Literal["Banner", "Description", "Icon"]], optional
            Remove a banner, description, or icon.
        """

    @abc.abstractmethod
    async def delete_server(self, server: objects.ObjectishOr[Server]) -> None:
        """Deletes a server if owner otherwise leaves.

        Parameters
        ----------
        server : ObjectishOr[Server]
            Server to delete.
        """

    @abc.abstractmethod
    async def create_server(
        self,
        name: str,
        nonce: str,
        *,
        description: Optional[str],
        nsfw: Optional[bool] = None,
    ) -> Server:
        """Create a new server.

        Parameters
        ----------
        name : str
            Name to use.
        nonce : str
            Nonce to use.
        description : Optional[str], optional
            Description to use.
        nsfw : Optional[bool], optional
            Whether to use NSFW.

        Returns
        -------
        Server
            Server.
        """

    @abc.abstractmethod
    async def create_channel(
        self,
        server: objects.ObjectishOr[Server],
        name: str,
        type: Literal["TextChannel", "VoiceChannel"],
        nonce: str,
        *,
        description: Optional[str] = None,
        nsfw: Optional[bool] = None,
    ) -> ServerChannel:
        """Create a new channel.

        Parameters
        ----------
        server : ObjectishOr[Server]
            Server to create the channel in.
        name : str
            Name to use.
        type : Literal["TextChannel", "VoiceChannel"]
            Type to use.
        nonce : str
            Nonce to use.
        description : Optional[str], optional
            Description to use.
        nsfw : Optional[bool], optional
            Whether to use NSFW.

        Returns
        -------
        ServerChannel
            Created channel.
        """

    @abc.abstractmethod
    async def fetch_invites(self, server: objects.ObjectishOr[Server]) -> list[Invite]:
        """Fetch invites for a server.

        Parameters
        ----------
        server : ObjectishOr[Server]
            Server to fetch invites for.

        Returns
        -------
        list[Invite]
            Invites.
        """

    @abc.abstractmethod
    async def mark_server_as_read(self, server: objects.ObjectishOr[Server]) -> None:
        """Mark all channels in a server as read.

        Parameters
        ----------
        server : ObjectishOr[Server]
            Server to mark as read.
        """

    @abc.abstractmethod
    async def fetch_member(
        self,
        server: objects.ObjectishOr[Server],
        user: objects.ObjectishOr[PartialUser],
    ) -> Optional[Member]:
        """Fetch a member.

        Parameters
        ----------
        server : ObjectishOr[Server]
            Server to fetch the member from.
        user : ObjectishOr[PartialUser]
            User to fetch.

        Returns
        -------
        Optional[Member]
            Member.
        """

    @abc.abstractmethod
    async def edit_member(
        self,
        server: objects.ObjectishOr[Server],
        user: objects.ObjectishOr[PartialUser],
        *,
        nickname: Optional[str] = None,
        avatar: Optional[str] = None,
        roles: list[objects.ObjectishOr[Role]] = None,
        remove: Optional[Literal["Avatar", "Nickname"]] = None,
    ) -> None:
        """Edit a member.

        Parameters
        ----------
        server : ObjectishOr[Server]
            Server to edit the member in.
        user : ObjectishOr[PartialUser]
            User to edit.
        nickname : Optional[str], optional
            New nickname to use.
        avatar : Optional[str], optional
            Autumn ID of new avatar to use.
        roles : list[ObjectishOr[Role]], optional
            New roles to use.
        remove : Optional[Literal["Avatar", "Nickname"]], optional
            Remove an avatar or nickname.
        """

    @abc.abstractmethod
    async def kick_member(
        self,
        server: objects.ObjectishOr[Server],
        user: objects.ObjectishOr[PartialUser],
    ) -> None:
        """Kick a member.

        Parameters
        ----------
        server : ObjectishOr[Server]
            Server to kick the member from.
        user : ObjectishOr[PartialUser]
            User to kick.
        """

    @abc.abstractmethod
    async def fetch_members(self, server: objects.ObjectishOr[Server]) -> list[Member]:
        """Fetch members for a server.

        Parameters
        ----------
        server : ObjectishOr[Server]
            Server to fetch members for.

        Returns
        -------
        list[Member]
            Members.
        """

    @abc.abstractmethod
    async def ban_user(
        self,
        server: objects.ObjectishOr[Server],
        user: objects.ObjectishOr[PartialUser],
        *,
        reason: Optional[str] = None,
    ) -> None:
        """Ban a member.

        Parameters
        ----------
        server : ObjectishOr[Server]
            Server to ban the member from.
        user : ObjectishOr[PartialUser]
            User to ban.
        reason : Optional[str], optional
            Reason to use.
        """

    @abc.abstractmethod
    async def unban_user(
        self,
        server: objects.ObjectishOr[Server],
        user: objects.ObjectishOr[PartialUser],
    ) -> None:
        """Unban a member.

        Parameters
        ----------
        server : ObjectishOr[Server]
            Server to unban the member from.
        user : ObjectishOr[PartialUser]
            User to unban.
        """

    @abc.abstractmethod
    async def fetch_bans(self, server: objects.ObjectishOr[Server]) -> list[Ban]:
        """Fetch bans for a server.

        Parameters
        ----------
        server : ObjectishOr[Server]
            Server to fetch bans for.

        Returns
        -------
        list[Ban]
            Bans.
        """

    @abc.abstractmethod
    async def set_role_permissions_server(
        self,
        server: objects.ObjectishOr[Server],
        role: objects.ObjectishOr[Role],
        permissions: Permission,
    ) -> None:
        """Set permissions for a role.

        Parameters
        ----------
        server : ObjectishOr[Server]
            Server to set permissions for.
        role : ObjectishOr[Role]
            Role to set permissions for.
        permissions : Permission
            Permissions to set.
        """

    @abc.abstractmethod
    async def set_default_permissions_server(
        self, server: objects.ObjectishOr[Server], permissions: Permission
    ) -> None:
        """Set default permissions for a server.

        Parameters
        ----------
        server : ObjectishOr[Server]
            Server to set default permissions for.
        permissions : Permission
            Permissions to set.
        """

    @abc.abstractmethod
    async def create_role(self, server: objects.ObjectishOr[Server], name: str) -> Role:
        """Create a new role.

        Parameters
        ----------
        server : ObjectishOr[Server]
            Server to create the role in.
        name : str
            Name to use.

        Returns
        -------
        Role
            Created role.
        """

    @abc.abstractmethod
    async def edit_role(
        self,
        server: objects.ObjectishOr[Server],
        role: objects.ObjectishOr[Role],
        name: str,
        *,
        colour: Optional[Colour] = None,
        hoist: Optional[bool] = None,
        rank: Optional[int] = None,
        remove: Optional[Literal["Colour"]] = None,
    ) -> None:
        """Edit a role.

        Parameters
        ----------
        server : ObjectishOr[Server]
            Server to edit the role in.
        role : ObjectishOr[Role]
            Role to edit.
        name : str
            New name to use.
        colour : Optional[Colour], optional
            New colour to use.
        hoist : Optional[bool], optional
            New hoist to use.
        rank : Optional[int], optional
            New rank to use.
        remove : Optional[Literal["Colour"]], optional
            Remove a colour.
        """

    @abc.abstractmethod
    async def delete_role(
        self, server: objects.ObjectishOr[Server], role: objects.ObjectishOr[Role]
    ) -> None:
        """Delete a role.

        Parameters
        ----------
        server : ObjectishOr[Server]
            Server to delete the role from.
        role : ObjectishOr[Role]
            Role to delete.
        """

    @abc.abstractmethod
    async def create_bot(self, name: str) -> Bot:
        """Create a new bot.

        Parameters
        ----------
        name : str
            Name to use.

        Returns
        -------
        Bot
            Created bot.
        """

    @abc.abstractmethod
    async def fetch_owned_bots(self) -> list[Bot]:
        """Fetch owned bots.

        Returns
        -------
        list[Bot]
            Owned bots.
        """

    @abc.abstractmethod
    async def fetch_bot(self, bot: objects.ObjectishOr[Bot]) -> Bot:
        """Fetch a bot.

        Parameters
        ----------
        bot : ObjectishOr[Bot]
            Bot to fetch.

        Returns
        -------
        Bot
            Fetched bot.
        """

    @abc.abstractmethod
    async def edit_bot(
        self,
        bot: objects.ObjectishOr[Bot],
        *,
        name: Optional[str] = None,
        public: Optional[bool] = None,
        interactions_url: Optional[str] = None,
        remove: Optional[Literal["InteractionsURL"]] = None,
    ) -> None:
        """Edit a bot.

        Parameters
        ----------
        bot : ObjectishOr[Bot]
            Bot to edit.
        name : Optional[str], optional
            New name to use.
        public : Optional[bool], optional
            New public to use.
        interactions_url : Optional[str], optional
            New interactions URL to use.
        remove : Optional[Literal["InteractionsURL"]], optional
            Remove an interactions URL.
        """

    @abc.abstractmethod
    async def delete_bot(self, bot: objects.ObjectishOr[Bot]) -> None:
        """Delete a bot.

        Parameters
        ----------
        bot : ObjectishOr[Bot]
            Bot to delete.
        """

    @abc.abstractmethod
    async def fetch_public_bot(
        self, bot: objects.ObjectishOr[Union[Bot, PartialUser]]
    ) -> PartialUser:
        """Fetch a public bot.

        Parameters
        ----------
        bot : ObjectishOr[Union[Bot, PartialUser]]
            Bot to fetch.

        Returns
        -------
        PartialUser
            Fetched bot.
        """

    @abc.abstractmethod
    async def invite_public_bot(
        self, bot: objects.ObjectishOr[Bot], server: objects.ObjectishOr[Server]
    ) -> None:
        """Invite a public bot to a server.

        Parameters
        ----------
        bot : ObjectishOr[Bot]
            Bot to invite.
        server : ObjectishOr[Server]
            Server to invite the bot to.
        """

    @abc.abstractmethod
    async def fetch_invite(self, invite: Union[Invite, str]) -> Invite:
        """Fetch an invite.

        Parameters
        ----------
        invite : Union[Invite, str]
            Invite to fetch.

        Returns
        -------
        Invite
            Fetched invite.
        """

    # @abc.abstractmethod
    # async def join_invite(self, invite: Union[Invite, str]) -> Server:
    #     """Join an invite.

    #     Parameters
    #     ----------
    #     invite : Union[Invite, str]
    #         Invite to join.

    #     Returns
    #     -------
    #     Server
    #         Joined server.
    #     """

    @abc.abstractmethod
    async def delete_invite(self, invite: Union[Invite, str]) -> None:
        """Delete an invite.

        Parameters
        ----------
        invite : Union[Invite, str]
            Invite to delete.
        """

    @abc.abstractmethod
    async def fetch_settings(self) -> dict[str, list[str]]:
        """Fetch settings from server filtered by keys.

        This will return an object with the requested keys, each value
        is a tuple of (timestamp, value), the value is the previously
        uploaded data.

        Returns
        -------
        dict[str, list[str]]
            Settings.
        """

    @abc.abstractmethod
    async def set_settings(self, name: str, value: str) -> None:
        """Set settings.

        Parameters
        ----------
        name : str
            Name to use.
        value : str
            Value to use.
        """

    @abc.abstractmethod
    async def fetch_unreads(self) -> list[TextChannel]:
        """Fetch unread channels.

        Returns
        -------
        list[TextChannel]
            Unread channels.
        """

    @abc.abstractmethod
    async def subscribe_web_push(self, endpoint: str, p256dh: str, auth: str) -> None:
        """Subscribe to web push.

        Parameters
        ----------
        endpoint : str
            Endpoint to use.
        p256dh : str
            P256DH to use.
        auth : str
            Auth to use.
        """

    @abc.abstractmethod
    async def unsubscribe_web_push(self) -> None:
        """Remove the Web Push subscription associated with the current session."""
