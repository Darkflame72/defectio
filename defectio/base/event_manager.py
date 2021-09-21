from __future__ import annotations

from typing import Any
from typing import TYPE_CHECKING

from defectio.types.websocket import ChannelCreatePayload

__all__: list[str] = ["EventFactory"]

import abc
import asyncio

if TYPE_CHECKING:
    from defectio.types.websocket import (
        ReadyPayload,
        MessagePayload,
        MessageDeletePayload,
        MessageUpdatePayload,
        ChannelUpdatePayload,
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


class EventManager(abc.ABC):
    @abc.abstractmethod
    async def dispatch(self, *args: list[Any]) -> asyncio.Future[Any]:
        """Dispatch event with given arguments.

        Returns
        -------
        asyncio.Future[Any]
            event to dispatch.
        """

    @abc.abstractmethod
    async def consume_raw_event(self, name: str, raw_event: dict[str, Any]) -> None:
        """Consume a raw event. Will generally call the related parser if it exists.

        Parameters
        ----------
        raw_event : dict[str, Any]
            The raw event.
        """

    @abc.abstractmethod
    async def parse_ready(self, payload: ReadyPayload) -> None:
        """Parse a ready event.

        Parameters
        ----------
        payload : ReadyPayload
            The payload of the event.
        """

    @abc.abstractmethod
    async def parse_message(self, payload: MessagePayload) -> None:
        """Parse a ready event.

        Parameters
        ----------
        payload : MessagePayload
            The payload of the event.
        """

    @abc.abstractmethod
    async def parse_message_update(self, payload: MessageUpdatePayload) -> None:
        """Parse a message update event.

        Parameters
        ----------
        payload : MessageUpdatePayload
            The payload of the event.
        """

    @abc.abstractmethod
    async def parse_message_delete(self, payload: MessageDeletePayload) -> None:
        """Parse a message delete event.

        Parameters
        ----------
        payload : MessageDeletePayload
            The payload of the event.
        """

    @abc.abstractmethod
    async def parse_channel_create(self, payload: ChannelCreatePayload) -> None:
        """Parse a channel create event.

        Parameters
        ----------
        payload : ChannelCreatePayload
            The payload of the event.
        """

    @abc.abstractmethod
    async def parse_channel_update(self, payload: ChannelUpdatePayload) -> None:
        """Parse a channel update event.

        Parameters
        ----------
        payload : ChannelUpdatePayload
            The payload of the event.
        """

    @abc.abstractmethod
    async def parse_channel_delete(self, payload: ChannelDeletePayload) -> None:
        """Parse a channel delete event.

        Parameters
        ----------
        payload : ChannelDeletePayload
            The payload of the event.
        """

    @abc.abstractmethod
    async def parse_channel_group_join(self, payload: ChannelGroupJoinPayload) -> None:
        """Parse a channel group join event.

        Parameters
        ----------
        payload : ChannelGroupJoinPayload
            The payload of the event.
        """

    @abc.abstractmethod
    async def parse_channel_group_leave(
        self, payload: ChannelGroupLeavePayload
    ) -> None:
        """Parse a channel group leave event.

        Parameters
        ----------
        payload : ChannelGroupLeavePayload
            The payload of the event.
        """

    @abc.abstractmethod
    async def parse_channel_start_typing(
        self, payload: ChannelStartTypingPayload
    ) -> None:
        """Parse a channel start typing event.

        Parameters
        ----------
        payload : ChannelStartTypingPayload
            The payload of the event.
        """

    @abc.abstractmethod
    async def parse_channel_stop_typing(
        self, payload: ChannelStopTypingPayload
    ) -> None:
        """Parse a channel stop typing event.

        Parameters
        ----------
        payload : ChannelStopTypingPayload
            The payload of the event.
        """

    @abc.abstractmethod
    async def parse_channel_ack(self, payload: ChannelAckPayload) -> None:
        """Parse a channel ack event.

        Parameters
        ----------
        payload : ChannelAckPayload
            The payload of the event.
        """

    @abc.abstractmethod
    async def parse_server_update(self, payload: ServerUpdatePayload) -> None:
        """Parse a server update event.

        Parameters
        ----------
        payload : ServerUpdatePayload
            The payload of the event.
        """

    @abc.abstractmethod
    async def parse_server_delete(self, payload: ServerDeletePayload) -> None:
        """Parse a server delete event.

        Parameters
        ----------
        payload : ServerDeletePayload
            The payload of the event.
        """

    @abc.abstractmethod
    async def parse_server_member_join(self, payload: ServerMemberJoinPayload) -> None:
        """Parse a server member join event.

        Parameters
        ----------
        payload : ServerMemberJoinPayload
            The payload of the event.
        """

    @abc.abstractmethod
    async def parse_server_member_leave(
        self, payload: ServerMemberLeavePayload
    ) -> None:
        """Parse a server member leave event.

        Parameters
        ----------
        payload : ServerMemberLeavePayload
            The payload of the event.
        """

    @abc.abstractmethod
    async def parse_server_member_update(
        self, payload: ServerMemberUpdatePayload
    ) -> None:
        """Parse a server member update event.

        Parameters
        ----------
        payload : ServerMemberUpdatePayload
            The payload of the event.
        """

    @abc.abstractmethod
    async def parse_server_role_update(self, payload: ServerRoleUpdatePayload) -> None:
        """Parse a server role update event.

        Parameters
        ----------
        payload : ServerRoleUpdatePayload
            The payload of the event.
        """

    @abc.abstractmethod
    async def parse_server_role_delete(self, payload: ServerRoleDeletePayload) -> None:
        """Parse a server role delete event.

        Parameters
        ----------
        payload : ServerRoleDeletePayload
            The payload of the event.
        """

    @abc.abstractmethod
    async def parse_user_update(self, payload: UserUpdatePayload) -> None:
        """Parse a user update event.

        Parameters
        ----------
        payload : UserUpdatePayload
            The payload of the event.
        """

    @abc.abstractmethod
    async def parse_user_relationship(self, payload: UserRelationshipPayload) -> None:
        """Parse a user relationship event.

        Parameters
        ----------
        payload : UserRelationshipPayload
            The payload of the event.
        """
