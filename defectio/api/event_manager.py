import inspect
import logging
import re
from copy import copy
from typing import Any
from typing import Callable
from typing import Optional
from typing import TYPE_CHECKING

from defectio.base import cache as cache_
from defectio.base import event_manager
from defectio.models.abc import User
from defectio.models.channel import Channel, GroupChannel
from defectio.models.member import Member
from defectio.models.message import Message
from defectio.models.raw_models import RawMessageDeleteEvent
from defectio.models.raw_models import RawMessageUpdateEvent
from defectio.models.server import Server

if TYPE_CHECKING:
    from defectio.types.websocket import (
        ReadyPayload,
        MessagePayload,
        MessageDeletePayload,
        MessageUpdatePayload,
        ChannelUpdatePayload,
        ChannelCreatePayload,
        ChannelDeletePayload,
        ChannelGroupJoinPayload,
        ChannelGroupLeavePayload,
        ChannelStopTypingPayload,
        ChannelStartTypingPayload,
        ChannelAckPayload,
        ServerUpdatePayload,
        ServerDeletePayload,
        ServerMemberJoinPayload,
        ServerMemberLeavePayload,
        ServerMemberUpdatePayload,
        ServerRoleUpdatePayload,
        ServerRoleDeletePayload,
        UserUpdatePayload,
        UserRelationshipPayload,
    )
    import asyncio

__all__ = ["EventManager"]


_logger = logging.getLogger("defectio.event_manager")


class EventManager(event_manager.EventManager):
    """Provides event handling logic for Revolt events."""

    __slots__: tuple[str] = ("_cache",)

    def __init__(
        self,
        # event_factory: event_factory_.EventFactory,
        /,
        *,
        cache: Optional[cache_.MutableCache] = None,
    ) -> None:
        self._cache = cache

        # convert camelCase to snake_case
        self._convert_pattern = re.compile(r"(?<!^)(?=[A-Z])")

        # load all parsers
        self.parsers: dict[str, Callable[[dict[str, Any]], None]] = {}
        for attr, func in inspect.getmembers(self):
            if attr.startswith("parse_"):
                self.parsers[attr[6:]] = func

    async def dispatch(self, *args: list[Any]) -> asyncio.Future[Any]:
        pass

    async def consume_raw_event(self, name: str, raw_event: dict[str, Any]) -> None:
        name = self._convert_pattern.sub("_", name).lower()
        try:
            func = self._parsers[name]
        except KeyError:
            _logger.debug("Unknown event %s.", name)
        else:
            await func(raw_event)

    async def parse_ready(self, payload: ReadyPayload) -> None:
        if self._cache:
            for payload_user in payload["users"]:
                user = User(payload_user)
                self._cache.set_user(user)

            for payload_server in payload["servers"]:
                server = Server(payload_server)
                self._cache.set_server(server)

            for payload_channel in payload["channels"]:
                channel = Channel(payload_channel)
                self._cache.set_channel(channel)

        await self.dispatch("ready")

    async def parse_message(self, payload: MessagePayload) -> None:
        message = Message(payload)

        if self._cache:
            self._cache.set_message(message)

        await self.dispatch("message", message)

    async def parse_message_update(self, payload: MessageUpdatePayload) -> None:
        await self.dispatch("raw_message_update", RawMessageUpdateEvent(payload))

        if self._cache:
            message = self._cache.get_message(payload["_id"])
            old_message = copy(message)
            message._update(payload)
            await self.dispatch("message_update", old_message, message)

    async def parse_message_delete(self, payload: MessageDeletePayload) -> None:
        await self.dispatch("raw_message_delete", RawMessageDeleteEvent(payload))

        if self._cache:
            message = self._cache.get_message(payload["_id"])
            if message is not None:
                await self.dispatch("message_delete", message)
                self._cache.delete_message(message)

    async def parse_channel_create(self, payload: ChannelCreatePayload) -> None:
        channel = Channel(payload)

        if self._cache:
            self._cache.set_server_channel(channel)

        await self.dispatch("channel_create", channel)

    async def parse_channel_update(self, payload: ChannelUpdatePayload) -> None:
        if self._cache:
            channel = self._cache.get_server_channel(payload["_id"])
            if channel is not None:
                old_channel = copy(channel)
                channel._update(payload)
                await self.dispatch("channel_update", old_channel, channel)

        await self.dispatch("channel_update")

    async def parse_channel_delete(self, payload: ChannelDeletePayload) -> None:
        if self._cache:
            channel = self._cache.get_server_channel(payload["_id"])
            if channel is not None:
                old_channel = copy(channel)
                self._cache.delete_server_channel(channel)
                await self.dispatch("channel_delete", old_channel, channel)

    async def parse_channel_group_join(self, payload: ChannelGroupJoinPayload) -> None:
        channel_group = GroupChannel(payload)

        if self._cache:
            # self._cache.set_dm_channel_id(channel_group.id, channel_group.recipients)
            pass

        await self.dispatch("channel_group_join", channel_group)

    async def parse_channel_group_leave(
        self, payload: ChannelGroupLeavePayload
    ) -> None:
        if self._cache:
            pass

        await self.dispatch("channel_group_leave")

    async def parse_channel_start_typing(
        self, payload: ChannelStartTypingPayload
    ) -> None:
        if self._cache:
            channel = self._cache.get_server_channel(payload["id"])
            user = self._cache.get_user(payload["user"])

            await self.dispatch("channel_start_typing", channel, user)

    async def parse_channel_stop_typing(
        self, payload: ChannelStopTypingPayload
    ) -> None:
        if self._cache:
            channel = self._cache.get_server_channel(payload["id"])
            user = self._cache.get_user(payload["user"])

            await self.dispatch("channel_start_typing", channel, user)

    async def parse_channel_ack(self, payload: ChannelAckPayload) -> None:
        if self._cache:
            pass

        await self.dispatch("channel_ack")

    async def parse_server_update(self, payload: ServerUpdatePayload) -> None:
        await self.dispatch("raw_server_update", payload)

        if self._cache:
            server = self._cache.get_server(payload["_id"])
            old_server = copy(server)
            server._update(payload)
            await self.dispatch("server_update", old_server, server)

    async def parse_server_delete(self, payload: ServerDeletePayload) -> None:
        await self.dispatch("raw_server_delete", payload)

        if self._cache:
            server = self._cache.get_server(payload["_id"])
            if server is not None:
                await self.dispatch("server_delete", server)
                self._cache.delete_server(server)

    async def parse_server_member_join(self, payload: ServerMemberJoinPayload) -> None:
        member = Member(payload)

        if self._cache:
            self._cache.set_member(member)

        await self.dispatch("server_member_join", member)

    async def parse_server_member_leave(
        self, payload: ServerMemberLeavePayload
    ) -> None:
        if self._cache:
            member = self._cache.de(payload["_id"], payload["user"])
            if member is not None:
                await self.dispatch("server_member_leave", copy(member))
                self._cache.delete_member(member)

    async def parse_server_member_update(
        self, payload: ServerMemberUpdatePayload
    ) -> None:
        if self._cache:
            member = self._cache.get_member(payload["_id"])
            old_member = copy(member)
            member._update(payload)
            await self.dispatch("server_member_update", old_member, member)

    async def parse_server_role_update(self, payload: ServerRoleUpdatePayload) -> None:
        if self._cache:
            pass

        await self.dispatch("server_role_update")

    async def parse_server_role_delete(self, payload: ServerRoleDeletePayload) -> None:
        if self._cache:
            pass

        await self.dispatch("server_role_delete")

    async def parse_user_update(self, payload: UserUpdatePayload) -> None:
        if self._cache:
            user = self._cache.get_user(payload["_id"])
            old_user = copy(user)
            user._update(payload)
            await self.dispatch("user_update", old_user, user)

    async def parse_user_relationship(self, payload: UserRelationshipPayload) -> None:
        if self._cache:
            pass

        await self.dispatch("user_relationship")
