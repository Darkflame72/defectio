from __future__ import annotations

import asyncio
import copy
from defectio.models.server import Role
import inspect
import logging
from collections import deque
from typing import Any
from typing import Callable
from typing import Deque
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from . import utils
from .gateway import DefectioWebsocket
from .http import DefectioHTTP
from .models import channel_factory
from .models import Member
from .models import Message
from .models import MessageableChannel
from .models import Server
from .models import User
from .models import VoiceChannel
from .models.apiinfo import ApiInfo
from .models.auth import Auth
from .models.channel import DMChannel
from .models.channel import GroupChannel
from .models.channel import TextChannel
from .models.member import PartialMember
from .models.raw_models import RawMessageDeleteEvent
from .models.raw_models import RawMessageUpdateEvent
from .models.user import ClientUser


if TYPE_CHECKING:
    from .types.websocket import (
        ChannelAck as ChannelAckPayload,
        ChannelCreate,
        ChannelDelete,
        ChannelGroupJoin,
        ChannelGroupLeave,
        ChannelStartTyping,
        ChannelStopTyping,
        ChannelUpdate,
        MessageDelete,
        MessageUpdate,
        Ready,
        ServerDelete,
        ServerMemberJoin,
        ServerMemberLeave,
        ServerMemberUpdate,
        ServerRoleDelete,
        ServerRoleUpdate,
        ServerUpdate,
        UserRelationship,
        UserUpdate,
        Message as MessagePayload,
    )

    from .types.payloads import (
        UserPayload,
        ServerPayload,
        ChannelPayload,
        MemberPayload,
        BasicMemberPayload,
        ApiInfoPayload,
    )

    Channel = Union[DMChannel, GroupChannel, TextChannel, VoiceChannel]

logger = logging.getLogger("defectio")


class ConnectionState:
    def __init__(
        self,
        dispatch: Callable,
        handlers: dict[str, Callable],
        http: Callable[[], DefectioHTTP],
        websocket: Callable[[], DefectioWebsocket],
        auth: Auth,
        loop: asyncio.AbstractEventLoop,
        **options: Any,
    ) -> None:
        """Initialize a new connection state

        Parameters
        ----------
        dispatch : Callable
            Callback to dispatch a message to a handler
        handlers : dict[str, Callable]
            Mapping of message type to handler functions
        http : Callable[[], DefectioHTTP]
            HTTP request handler
        websocket : Callable[[], DefectioWebsocket]
            Websocket request handler
        auth : Auth
            Authentication details
        loop : asyncio.AbstractEventLoop
            Event loop to use
        """
        self.get_http = http
        self.get_websocket = websocket
        self.auth = auth
        self.handlers: dict[str, Callable] = handlers
        self.dispatch: Callable = dispatch
        self.max_messages: Optional[int] = options.get("max_messages", 1000)
        self.loop: asyncio.AbstractEventLoop = loop
        self.parsers: dict[str, Callable[[dict[str, Any]], None]] = {}

        for attr, func in inspect.getmembers(self):
            if attr.startswith("parse_"):
                self.parsers[attr[6:]] = func

        self.clear()

    def clear(self) -> None:
        """Clear all data from the internal cache and reset the connection state."""
        self.user_id: Optional[str] = None
        self.api_info: Optional[ApiInfo] = None
        self._servers: dict[str, Server] = {}
        self._users: dict[str, User] = {}
        self._server_channels: dict[str, list[Channel]] = {}
        self._members: dict[str, list[Member]] = {}
        if self.max_messages is not None:
            self._messages: Optional[Deque[Message]] = deque(maxlen=self.max_messages)
        else:
            self._messages: Optional[Deque[Message]] = None

    def call_handlers(self, key: str, *args: Any, **kwargs: Any) -> None:
        """Call the handler for the key

        Parameters
        ----------
        key : str
            Key to call the handler for
        """
        try:
            func = self.handlers[key]
        except KeyError:
            pass
        else:
            func(*args, **kwargs)

    def set_api_info(self, api_info: ApiInfoPayload) -> ApiInfo:
        """Set the API info

        Parameters
        ----------
        api_info : ApiInfoPayload
            API info payload

        Returns
        -------
        ApiInfo
            API info object
        """
        api_info = ApiInfo(api_info)
        self.api_info = api_info
        self.http.set_api_info(api_info)
        return api_info

    @property
    def self_id(self) -> Optional[str]:
        u = self.user
        return u.id if u else None

    @property
    def http(self) -> DefectioHTTP:
        return self.get_http()

    @property
    def websocket(self) -> DefectioWebsocket:
        return self.get_websocket()

    @property
    def users(self) -> list[User]:
        """Get all users from internal cache

        Returns
        -------
        list[User]
            list of users
        """
        return list(self._users.values())

    def get_user(self, user_id: str) -> Optional[User | ClientUser]:
        """Get user from internal cache

        Parameters
        ----------
        user_id : Optional[str]
            User ID to get

        Returns
        -------
        Optional[User | ClientUser]
            User object from the cache
        """
        return self._users.get(user_id)

    async def fetch_user(self, user_id: str) -> Optional[User | ClientUser]:
        """Get user

        Parameters
        ----------
        user_id : Optional[str]
            User ID to get

        Returns
        -------
        Optional[User | ClientUser]
            User object from the cache
        """
        user = self._users.get(user_id)
        if user is None:
            user_data = await self.http.get_user(user_id)
            if user_data is not None:
                user = self._add_user_from_data(user_data)

        return user

    def _add_user(self, user: User) -> None:
        """Add a user in internal cache

        Parameters
        ----------
        user : User
            User object to add
        """
        self._users[user.id] = user

    def _add_user_from_data(self, data: UserPayload) -> User:
        """Add a user in internal cache

        Parameters
        ----------
        data : UserPayload
            User data

        Returns
        -------
        User
            User object from the provided data
        """
        user = User(state=self, data=data)
        self._add_user(user)
        return user

    def _remove_user(self, user_id: str) -> None:
        """Remove a user from internal cache

        Parameters
        ----------
        user_id : str
            User ID to remove
        """
        del self._users[user_id]

    @property
    def servers(self) -> list[Server]:
        return list(self._servers.values())

    def get_server(self, server_id: Optional[str]) -> Optional[Server]:
        """Get a server by ID from the cache

        Parameters
        ----------
        server_id : Optional[str]
            Server ID

        Returns
        -------
        Optional[Server]
            Server object
        """

        return self._servers.get(server_id)

    async def fetch_server(self, server_id: str) -> Optional[Server]:
        """Get a server by ID

        Parameters
        ----------
        server_id : Optional[str]
            Server ID

        Returns
        -------
        Optional[Server]
            Server object
        """

        server = self._servers.get(server_id)
        if server is None:
            server_data = await self.http.get_server(server_id)
            if server_data is not None:
                server = self._add_server_from_data(server_data)
                for channel_id in server.channel_ids:
                    channel_data = await self.http.get_channel(channel_id)
                    self._add_channel_from_data(channel_data)
        return server

    def _add_server(self, server: Server) -> None:
        """Add a server to the internal cache

        Parameters
        ----------
        server : Server
            Server to add
        """
        self._servers[server.id] = server

    def _add_server_from_data(self, data: ServerPayload) -> Server:
        """Add a server to the internal cache from raw data

        Parameters
        ----------
        data : ServerPayload
            Server data

        Returns
        -------
        Server
            Server object from the provided data
        """
        server = Server(data=data, state=self)
        self._add_server(server)
        return server

    def _remove_server(self, server: Server) -> None:
        """Remove a server from the internal cache

        Parameters
        ----------
        server : Server
            Server to remove
        """
        self._servers.pop(server.id, None)

        for channel in server.channels:
            self._remove_channel(channel)

        del server

    @property
    def channels(self) -> list[Channel]:
        return list(self._server_channels.values())

    def get_channel(self, channel_id: str) -> Optional[Channel]:
        """Get a channel from the cache

        Parameters
        ----------
        channel_id : str
            ID of the channel to get

        Returns
        -------
        Optional[Channel]
            Channel object from the cache
        """

        return self._server_channels.get(channel_id)

    async def fetch_channel(self, channel_id: str) -> Optional[Channel]:
        """Get a channel from the cache or api

        Parameters
        ----------
        channel_id : str
            ID of the channel to get

        Returns
        -------
        Optional[Channel]
            Channel object from the cache
        """

        channel = self._server_channels.get(channel_id)
        if channel is None:
            channel_data = await self.http.get_channel(channel_id)
            if channel_data is not None:
                channel = self._add_channel_from_data(channel_data)
                if "server" in channel_data:
                    await self.fetch_server(channel_data["server"])
        return channel

    def _add_channel(self, channel: Channel) -> None:
        """Add a channel to the internal cache

        Parameters
        ----------
        channel : Channel
            Channel to add
        """
        self._server_channels[channel.id] = channel

    def _add_channel_from_data(self, data: ChannelPayload) -> Channel:
        """Add a channel to the internal cache from raw data

        Parameters
        ----------
        data : ChannelPayload
            Channel data

        Returns
        -------
        Channel
            Channel object from the provided data
        """
        cls = channel_factory(data)
        server = self.get_server(data.get("server"))
        if server is not None:
            channel = cls(state=self, data=data, server=server)
        else:
            channel = cls(state=self, data=data)
        self._add_channel(channel)
        return channel

    def _remove_channel(self, channel: Channel) -> None:
        """Remove a channel from the internal cache

        Parameters
        ----------
        channel : Channel
            Channel to remove
        """
        self._server_channels.pop(channel.id, None)

        del channel

    @property
    def messages(self) -> Optional[list[Message]]:
        return list(self._messages)

    def get_message(self, msg_id: Optional[str]) -> Optional[Message]:
        """Get a message from the cache

        Parameters
        ----------
        msg_id : Optional[str]
            ID of the message to get

        Returns
        -------
        Optional[Message]
            Message from the cache
        """
        return (
            utils.find(lambda m: m.id == msg_id, reversed(self._messages))
            if self._messages
            else None
        )

    def _add_message(self, message: Message) -> None:
        """Add a message to the internal cache

        Parameters
        ----------
        message : Message
            Message to add
        """
        self._messages.append(message)

    def _add_message_from_data(self, data: MessagePayload) -> Message:
        """Add a message to the internal cache from raw data

        Parameters
        ----------
        data : MessagePayload
            Message data

        Returns
        -------
        Message
            Message object from the provided data
        """
        server = self.get_server(data.get("server"))
        channel = self.get_channel(data.get("channel"))
        message = Message(data=data, state=self, channel=channel)
        self._add_message(message)
        return message

    def _remove_message(self, message: Message) -> None:
        """Remove a message from the internal cache

        Parameters
        ----------
        message : Message
            Message to remove
        """
        self._messages.remove(message)

        del message

    @property
    def members(self) -> list[Member]:
        return list(self._members.values())

    def get_member(self, member_id: str) -> Optional[Member]:
        """Get a member from the cache

        Parameters
        ----------
        member_id : str
            ID of the member to get

        Returns
        -------
        Optional[Member]
            Member object from the cache
        """
        return self._members.get(member_id)

    def _add_member(self, member: Union[Member, PartialMember]) -> None:
        """Add a member to the internal cache

        Parameters
        ----------
        member : Union[Member, PartialMember]
            Member to add
        """
        self._members[member.id] = member

    def _add_member_from_data(
        self, data: Union[MemberPayload, BasicMemberPayload]
    ) -> Union[Member, PartialMember]:
        """Add a member to the internal cache from raw data

        Parameters
        ----------
        data : Union[MemberPayload, BasicMemberPayload]
            Member data

        Returns
        -------
        Union[Member, PartialMember]
            Member object from the provided data
        """
        if "user" in data:
            member = PartialMember(data["user"], self)
        else:
            member = Member(data, self)
        self._add_member(member)
        return member

    def _remove_member(self, member: Union[Member, PartialMember]) -> None:
        """Remove a member from the internal cache

        Parameters
        ----------
        member : Union[Member, PartialMember]
            Member to remove
        """
        self._members[member.server.id].pop(member.id, None)

        del member

    async def fetch_account(self):
        path = "/auth/account"
        return await self.http.request("GET", path)

    @property
    def user(self) -> ClientUser:
        user = self.get_user(self.user_id)
        return user

    async def parse_ready(self, data: Ready) -> None:
        self.clear()

        for user in data["users"]:
            if user["relationship"] == "User":
                user_data = ClientUser(state=self, data=user)
                self.user_id = user_data.id
                self._add_user(user_data)
            else:
                self._add_user_from_data(user)

        for server in data["servers"]:
            self._add_server_from_data(server)

        for channel in data["channels"]:
            self._add_channel_from_data(channel)

        for member in data["members"]:
            self._add_member_from_data(member)

        self.call_handlers("ready")
        self.dispatch("ready")

    async def parse_message(self, data: MessagePayload) -> None:
        if data["author"] == "00000000000000000000000000":
            return
        else:
            await self.fetch_user(data["author"])
        channel = await self.fetch_channel(data["channel"])
        if channel.type == "TextChannel":
            if data["author"] != "00000000000000000000000000":
                await self.fetch_user(data["author"])
        message = self._add_message_from_data(data)
        if self._messages is not None:
            self._messages.append(message)
            self.dispatch("message", message)

    async def parse_messageupdate(self, data: MessageUpdate) -> None:
        raw = RawMessageUpdateEvent(data)
        message = self.get_message(raw.message_id)
        if message is not None:
            older_message = copy.copy(message)
            raw.cached_message = older_message
            self.dispatch("raw_message_edit", raw)
            message._update(data)
            self.dispatch("message_edit", older_message, message)
        else:
            # done here so raw is always sent before message edit
            self.dispatch("raw_message_edit", raw)

    async def parse_messagedelete(self, data: MessageDelete) -> None:
        raw = RawMessageDeleteEvent(data)
        found = self.get_message(data["id"])
        raw.cached_message = found
        self.dispatch("raw_message_delete", raw)
        if self._messages is not None and found is not None:
            self.dispatch("message_delete", found)
            self._messages.remove(found)

    async def parse_channelcreate(self, data: ChannelCreate) -> None:
        channel = self._add_channel_from_data(data)          
        server = channel.server
        
        # Channel belongs to a non-cached server
        if data.get("server") is not None and server is None:
            server = await self.fetch_server(data.get("server"))
            channel = self._add_channel_from_data(data)
       
        if channel.id not in server.channel_ids:
            server.channel_ids.append(channel.id)
            
        self.dispatch("channel_create", channel)

    async def parse_channelupdate(self, data: ChannelUpdate) -> None:
        channel = self.get_channel(data["id"])
        if channel is not None:
            channel._update(data)
            self.dispatch("raw_channel_update", data)
            self.dispatch("channel_update", channel)
        self.dispatch("raw_channel_update", data)

    async def parse_channeldelete(self, data: ChannelDelete) -> None:
        channel = await self.fetch_channel(data["id"])
        if channel is not None:
            channel_copy = copy.copy(channel)
            self._remove_channel(channel)
            self.dispatch("raw_channel_delete", data)
            self.dispatch("channel_delete", channel_copy)
        self.dispatch("raw_channel_delete", data)

    async def parse_channelgroupjoin(self, data: ChannelGroupJoin) -> None:
        await self.fetch_channel(data["id"])
        self.dispatch("channel_group_join", data)

    async def parse_channelgroupleave(self, data: ChannelGroupLeave) -> None:       
        channel = self.get_channel(data["id"])
               
        if channel is not None:
            channel_copy = copy.copy(channel)
            self._remove_channel(channel)
            self.dispatch("channel_group_leave", channel_copy)

    async def parse_channelstarttyping(self, data: ChannelStartTyping) -> None:
        channel = self.get_channel(data["id"])
        user = self.get_user(data["user"])
        self.dispatch("channel_start_typing", channel, user)

    async def parse_channelstoptyping(self, data: ChannelStopTyping) -> None:
        channel = self.get_channel(data["id"])
        user = self.get_user(data["user"])
        self.dispatch("channel_stop_typing", channel, user)

    async def parse_channelack(self, data: ChannelAckPayload) -> None:
        self.dispatch("channel_ack", data)

    async def parse_serverupdate(self, data: ServerUpdate) -> None:
        server = self.get_server(data["id"])
        if server is not None:
            old_server = copy.copy(server)
            server._update(data)
            self.dispatch("server_update", old_server, server)

    async def parse_serverdelete(self, data: ServerDelete) -> None:        
        server = self.get_server(data["id"])
        if server is not None:
            self._servers.pop(server.id, None)
            self.dispatch("server_delete", server)

    async def parse_servermemberjoin(self, data: ServerMemberJoin) -> None:
        server = await self.fetch_server(data["id"])
        user = await self.fetch_user(data["user"])
        if data["user"] == self.user.id and server is not None:
            logger.info("Joined server %s", server.name)
        member = self._add_member_from_data(data)
        self.dispatch("server_member_join", member)

    async def parse_servermemberleave(self, data: ServerMemberLeave) -> None:
        member = self.get_member(data["id"])
        if member is not None:
            old_member = self._members.pop(member)
            self.dispatch("server_member_leave", old_member)

    async def parse_servermemberupdate(self, data: ServerMemberUpdate) -> None:
        member = self.get_member(data["id"]["user"])
        if isinstance(member, Member):
            old_member = copy.copy(member)
            member._update(data)
            self.dispatch("raw_server_member_update", data)
            self.dispatch("server_member_update", old_member, member)
        self.dispatch("raw_server_member_update", data)

    async def parse_serverroleupdate(self, data: ServerRoleUpdate) -> None:
        server = self.get_server(data["id"])
        if server is not None:
            role = utils.find(lambda r: r.id == data["role_id"], server.roles)
            if role is not None:
                role._update(data)
                self.dispatch("server_role_update", role)
            else:
                role = Role(data["role_id"], data["data"], self)
                server.roles.append(role)
                self.dispatch("server_role_update", role)
        else:
            logger.debug(
                "SERVER_ROLE_UPDATE referencing an unknown server ID: %s. Discarding.",
                data["id"],
            )

    async def parse_serverroledelete(self, data: ServerRoleDelete) -> None:
        server = self.get_server(data["id"])
        if server is not None:
            role = utils.find(lambda r: r.id == data["role_id"], server.roles)
            server.roles.remove(role)
            self.dispatch("server_role_delete", role)

    async def parse_userupdate(self, data: UserUpdate) -> None:
        user = self.get_user(data["id"])
        if user is not None:
            old_user = copy.copy(user)
            user._update(data)
            self.dispatch("raw_user_update", data)
            self.dispatch("user_update", old_user, user)
        self.dispatch("raw_user_update", data)

    async def parse_userrelationship(self, data: UserRelationship) -> None:
        user = self.get_user(data["user"])
        user.our_relation._update(data)
        self.dispatch("user_relationship", user)

    # creaters

    def create_message(
        self,
        channel: MessageableChannel,
        data,
    ) -> Message:
        """Creates a :class:`~defectio.Message` from the given parameters.

        Parameters
        ----------
        channel : MessageableChannel
            The channel to create the message in.
        data : [type]
            A list of parameters required to create a message.

        Returns
        -------
        Message
            The message created.
        """      
        return Message(state=self, channel=channel, data=data)

    def create_user(self, data: UserPayload) -> User:
        """Creates a :class:`~defectio.User` from the given parameters.

        Parameters
        ----------
        data : UserPayload
            A list of parameters required to create a user.

        Returns
        -------
        User
            The user created.
        """
        user = User(data, self)
        return user
