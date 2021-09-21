import inspect
import logging
import re
from typing import Any
from typing import Callable
from typing import Optional
from typing import TYPE_CHECKING

from defectio.base import cache as cache_
from defectio.base import event_manager

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
            pass

        await self.dispatch("ready")

    async def parse_message(self, payload: MessagePayload) -> None:
        if self._cache:
            pass

        await self.dispatch("message")

    async def parse_message_update(self, payload: MessageUpdatePayload) -> None:
        if self._cache:
            pass

        await self.dispatch("message_update")

    async def parse_message_delete(self, payload: MessageDeletePayload) -> None:
        if self._cache:
            pass

        await self.dispatch("message_delete")

    async def parse_channel_create(self, payload: ChannelCreatePayload) -> None:
        if self._cache:
            pass

        await self.dispatch("channel_create")

    async def parse_channel_update(self, payload: ChannelUpdatePayload) -> None:
        if self._cache:
            pass

        await self.dispatch("channel_update")

    async def parse_channel_delete(self, payload: ChannelDeletePayload) -> None:
        if self._cache:
            pass

        await self.dispatch("channel_delete")

    async def parse_channel_group_join(self, payload: ChannelGroupJoinPayload) -> None:
        if self._cache:
            pass

        await self.dispatch("channel_group_join")

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
            pass

        await self.dispatch("channel_start_typing")

    async def parse_channel_stop_typing(
        self, payload: ChannelStopTypingPayload
    ) -> None:
        if self._cache:
            pass

        await self.dispatch("channel_stop_typing")

    async def parse_channel_ack(self, payload: ChannelAckPayload) -> None:
        if self._cache:
            pass

        await self.dispatch("channel_ack")

    async def parse_server_update(self, payload: ServerUpdatePayload) -> None:
        if self._cache:
            pass

        await self.dispatch("server_update")

    async def parse_server_delete(self, payload: ServerDeletePayload) -> None:
        if self._cache:
            pass

        await self.dispatch("server_delete")

    async def parse_server_member_join(self, payload: ServerMemberJoinPayload) -> None:
        if self._cache:
            pass

        await self.dispatch("server_member_join")

    async def parse_server_member_leave(
        self, payload: ServerMemberLeavePayload
    ) -> None:
        if self._cache:
            pass

        await self.dispatch("server_member_leave")

    async def parse_server_member_update(
        self, payload: ServerMemberUpdatePayload
    ) -> None:
        if self._cache:
            pass

        await self.dispatch("server_member_update")

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
            pass

        await self.dispatch("user_update")

    async def parse_user_relationship(self, payload: UserRelationshipPayload) -> None:
        if self._cache:
            pass

        await self.dispatch("user_relationship")
