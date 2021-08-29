from __future__ import annotations

from .server import Server
from typing import Dict, List, Deque, Optional, TYPE_CHECKING, Any, Callable, Union
from collections import deque
import asyncio
import inspect
from .message import Message
from .channel import TextChannel, channel_factory
from .user import User
from . import utils
import copy
from .raw_models import RawMessageDeleteEvent, RawMessageUpdateEvent

if TYPE_CHECKING:
    from .http import HttpClient
    from .channel import TextChannel
    from . import abc
    from .websocket import WebsocketHandler
    from defectio.types.websocket import (
        Authenticated,
        ChannelAck,
        ChannelCreate,
        ChannelDelete,
        ChannelGroupJoin,
        ChannelGroupLeave,
        ChannelStartTyping,
        ChannelStopTyping,
        ChannelUpdate,
        MessageDelete,
        MessageUpdate,
        Pong,
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
        User as UserPayload,
        Server as ServerPayload,
        Channel as ChannelPayload,
    )


class ConnectionState:
    get_websocket: WebsocketHandler
    if TYPE_CHECKING:
        _parsers: Dict[str, Callable[[Dict[str, Any]], None]]

    def __init__(
        self,
        dispatch: Callable,
        handlers: Dict[str, Callable],
        http: HttpClient,
        loop: asyncio.AbstractEventLoop,
        **options: Any,
    ):
        self.handlers: Dict[str, Callable] = handlers
        self.dispatch: Callable = dispatch
        self.http: HttpClient = http
        self.max_messages: Optional[int] = options.get("max_messages", 1000)
        self.loop: asyncio.AbstractEventLoop = loop
        self.servers: Dict[str, Server] = {}
        self.channels: Dict[str, abc.Messageable] = {}
        self.users: Dict[str, User] = {}
        self.user: Optional[User] = None

        self._messages: Optional[List[Message]] = deque(maxlen=self.max_messages)

        self.parsers = parsers = {}
        for attr, func in inspect.getmembers(self):
            if attr.startswith("parse_"):
                parsers[attr[6:]] = func

    def call_handlers(self, key: str, *args: Any, **kwargs: Any) -> None:
        try:
            func = self.handlers[key]
        except KeyError:
            pass
        else:
            func(*args, **kwargs)

    # Parsers

    def parse_authenticated(self, data: Authenticated):
        self.dispatch("authenticated", data)

    def parse_pong(self, data: Pong):
        self.dispatch("pong", data)

    def parse_ready(self, data: Ready) -> None:
        # if self._ready_task is not None:
        #     self._ready_task.cancel()

        for user in data["users"]:
            self.add_user(user)

        self.user = self.create_user(data=data["users"][0])

        for server in data["servers"]:
            self.add_server(server)

        for channel in data["channels"]:
            self.add_channel(channel)
        self.dispatch("ready")
        self.dispatch("connect")

    def parse_message(self, data: MessagePayload) -> None:
        channel = self.get_channel(data["channel"])
        print(channel)
        message = Message(channel=channel, data=data, state=self)
        self.dispatch("message", message)
        if self._messages is not None:
            self._messages.append(message)

    def parse_messageupdate(self, data: MessageUpdate):
        raw = RawMessageUpdateEvent(data)
        message = self._get_message(raw.message_id)
        if message is not None:
            older_message = copy.copy(message)
            raw.cached_message = older_message
            self.dispatch("raw_message_edit", raw)
            message._update(data)
            self.dispatch("message_edit", older_message, message)
        else:
            self.dispatch("raw_message_edit", raw)

    def parse_messagedelete(self, data: MessageDelete):
        raw = RawMessageDeleteEvent(data)
        found = self._get_message(data["id"])
        raw.cached_message = found
        self.dispatch("raw_message_delete", raw)
        if self._messages is not None and found is not None:
            self.dispatch("message_delete", found)
            self._messages.remove(found)

    def parse_channelcreate(self, data: ChannelCreate):
        self.dispatch("channel_create", data)

    def parse_channelupdate(self, data: ChannelUpdate):
        # self.add_channel(data)
        # self.users.get(data["id"]).online = True
        self.dispatch("channel_update", data)

    def parse_channeldelete(self, data: ChannelDelete):
        self.dispatch("channel_delete", data)

    def parse_channelgroupjoin(self, data: ChannelGroupJoin):
        self.dispatch("channel_group_join", data)

    def parse_channelgroupleave(self, data: ChannelGroupLeave):
        self.dispatch("channel_group_leave", data)

    def parse_channelstarttyping(self, data: ChannelStartTyping):
        self.dispatch("channel_start_typing", data)

    def parse_channelstoptyping(self, data: ChannelStopTyping):
        self.dispatch("channel_stop_typing", data)

    def parse_channelack(self, data: ChannelAck):
        self.dispatch("channel_ack", data)

    def parse_serverupdate(self, data: ServerUpdate):
        # self.add_server(data)
        self.dispatch("server_update", data)

    def parse_serverdelete(self, data: ServerDelete):
        self.dispatch("server_delete", data)

    def parse_servermemberjoin(self, data: ServerMemberJoin):
        self.dispatch("server_member_join", data)

    def parse_servermemberleave(self, data: ServerMemberLeave):
        self.dispatch("server_member_leave", data)

    def parse_servermemberupdate(self, data: ServerMemberUpdate):
        self.dispatch("server_member_update", data)

    def parse_serverroleupdate(self, data: ServerRoleUpdate):
        self.dispatch("server_role_update", data)

    def parse_serverroledelete(self, data: ServerRoleDelete):
        self.dispatch("server_role_delete", data)

    def parse_userupdate(self, data: UserUpdate):
        # self.add_user(data)
        self.dispatch("user_update", data)

    def parse_userrelationship(self, data: UserRelationship):
        self.dispatch("user_relationship", data)

    # Getters

    def get_user(self, id: str) -> Optional[User]:
        return self.users.get(id)

    def get_channel(self, id: str) -> Optional[abc.Messageable]:
        return self.channels.get(id)

    def get_server(self, id: str) -> Optional[Server]:
        return self.channels.get(id)

    def _get_message(self, msg_id: str) -> Optional[Message]:
        return (
            utils.find(lambda m: m.id == msg_id, reversed(self._messages))
            if self._messages
            else None
        )

    # Setters

    def add_user(self, payload: UserPayloaad) -> User:
        user = self.create_user(data=payload)
        self.users[user.id] = user
        return user

    def add_channel(self, payload: ChannelPayload) -> abc.Messageable:
        cls = channel_factory(payload)
        server = self.get_server(payload["server"])
        channel = cls(state=self, data=payload, server=server)
        self.channels[channel.id] = channel
        return channel

    def add_server(self, payload: ServerPayload) -> Server:
        server = Server(payload, self)
        self.servers[server.id] = server
        return server

    # creaters

    def create_message(
        self,
        *,
        channel: Union[TextChannel],
        data,
    ) -> Message:
        return Message(state=self, channel=channel, data=data)

    def create_user(self, *, data: UserPayload) -> User:
        user = User(data, self)
        return user
