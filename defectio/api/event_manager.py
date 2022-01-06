from __future__ import annotations

import asyncio
import inspect
import logging
import re
from copy import copy
from typing import Any
from typing import Callable
from typing import Optional
from typing import TYPE_CHECKING

from defectio import traits
from defectio.api import cache as cache_
from defectio.base import event_manager
from defectio.models import member
from defectio.models import objects
from defectio.models.attachmet import MetaData
from defectio.models.channel import DMChannel
from defectio.models.channel import GroupChannel
from defectio.models.channel import PartialChannel
from defectio.models.channel import SavedMessageChannel
from defectio.models.channel import TextChannel
from defectio.models.channel import VoiceChannel
from defectio.models.member import Member
from defectio.models.message import Attachment, Reply
from defectio.models.message import Message
from defectio.models.permission import ServerPermission
from defectio.models.server import Server
from defectio.models.user import Relationship
from defectio.models.user import Status
from defectio.models.user import User

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
        app: traits.RESTAware,
        /,
        *,
        cache: Optional[cache_.MutableCache] = None,
    ) -> None:
        self.app = app
        self._cache = cache

        # convert camelCase to snake_case
        self._convert_pattern = re.compile(r"(?<!^)(?=[A-Z])")

        # load all parsers
        self._parsers: dict[str, Callable[[dict[str, Any]], None]] = {}
        for attr, func in inspect.getmembers(self):
            if attr.startswith("parse_"):
                self._parsers[attr[6:]] = func

    async def dispatch(self, *args: list[Any]) -> asyncio.Future[Any]:
        pass

    async def consume_raw_event(self, name: str, raw_event: dict[str, Any]) -> None:
        name = self._convert_pattern.sub("_", name).lower()
        try:
            func = self._parsers[name]
        except KeyError:
            _logger.debug("Unknown event %s.", name)
        else:
            try:
                await self.dispatch(f"raw_{name}", raw_event)
                await func(raw_event)
            except Exception as e:
                _logger.exception(e)

    async def parse_ready(self, payload: ReadyPayload) -> None:
        if self._cache:
            for payload_user in payload["users"]:
                user = User(
                    app=self.app,
                    id=objects.Object(payload_user["_id"]),
                    name=payload_user["username"],
                    status=Status(
                        presence=payload_user["status"].get("presence"),
                        text=payload_user["status"].get("text"),
                    )
                    if "status" in payload_user
                    else None,
                    our_relation=Relationship(
                        other_user_id=self._cache._me,
                        status=payload_user["relationship"],
                        app=self.app,
                    ),
                    relationships=[
                        Relationship(
                            app=self.app,
                            other_user_id=objects.Object(relationship["_id"]),
                            status=relationship["status"],
                        )
                        for relationship in payload_user.get("relations", [])
                    ],
                    online=payload_user["online"],
                )
                await self._cache.set_user(user)

            for payload_server in payload["servers"]:
                server = Server(
                    app=self.app,
                    id=objects.Object(payload_server["_id"]),
                    name=payload_server["name"],
                    owner_id=objects.Object(payload_server["owner"]),
                    description=payload_server.get("description", None),
                    channel_ids=[
                        objects.Object(channel)
                        for channel in payload_server["channels"]
                    ],
                    banner=Attachment(
                        app=self.app,
                        id=objects.Object(payload_server["banner"]["_id"]),
                        tag=payload_server["banner"]["tag"],
                        size=payload_server["banner"]["size"],
                        filename=payload_server["banner"]["filename"],
                        content_type=payload_server["banner"]["content_type"],
                        metadata=MetaData(
                            type=payload_server["banner"]["metadata"]["type"]
                        ),
                    )
                    if "banner" in payload_server
                    else None,
                    icon=Attachment(
                        app=self.app,
                        id=objects.Object(payload_server["icon"]["_id"]),
                        tag=payload_server["icon"]["tag"],
                        size=payload_server["icon"]["size"],
                        filename=payload_server["icon"]["filename"],
                        content_type=payload_server["icon"]["content_type"],
                        metadata=MetaData(
                            type=payload_server["icon"]["metadata"]["type"]
                        ),
                    )
                    if "icon" in payload_server
                    else None,
                    server_permissions=ServerPermission(
                        payload_server["default_permissions"]
                    ),
                )
                await self._cache.set_server(server)

            for payload_channel in payload["channels"]:
                if payload_channel["channel_type"] == "SavedMessage":
                    channel = SavedMessageChannel(
                        app=self.app, id=objects.Object(payload_channel["_id"])
                    )
                elif payload_channel["channel_type"] == "DirectMessage":
                    channel = SavedMessageChannel(
                        app=self.app, id=objects.Object(payload_channel["_id"])
                    )
                elif payload_channel["channel_type"] == "Group":
                    channel = SavedMessageChannel(
                        app=self.app, id=objects.Object(payload_channel["_id"])
                    )
                elif payload_channel["channel_type"] == "TextChannel":
                    channel = TextChannel(
                        app=self.app,
                        id=objects.Object(payload_channel["_id"]),
                        server_id=objects.Object(payload_channel["server"]),
                        description=payload_channel.get("description"),
                        name=payload_channel["name"],
                    )
                elif payload_channel["channel_type"] == "VoiceChannel":
                    channel = SavedMessageChannel(
                        app=self.app, id=objects.Object(payload_channel["_id"])
                    )
                    pass
                else:
                    _logger.warn(
                        "Unknown channel type %s", payload_channel["channel_type"]
                    )
                    pass
                await self._cache.set_channel(channel)

        await self.dispatch("ready")

    async def parse_message(self, payload: MessagePayload) -> None:
        message = Message(
            app=self.app,
            id=objects.Object(payload["_id"]),
            channel_id=objects.Object(payload["channel"]),
            author_id=objects.Object(payload["author"]),
            content=payload["content"],
            replies_ids=[objects.Object(reply) for reply in payload.get("replies", [])],
            attachments=[],
        )

        if self._cache:
            await self._cache.set_message(message)

        await self.dispatch("message", message)

    async def parse_message_update(self, payload: MessageUpdatePayload) -> None:
        if self._cache:
            # message = await self._cache.get_message(payload["_id"])
            # old_message = copy(message)
            # message._update(payload)
            # await self.dispatch("message_update", old_message, message)
            pass

    async def parse_message_delete(self, payload: MessageDeletePayload) -> None:
        # if self._cache:
        #     message = await self._cache.get_message(payload["_id"])
        #     if message is not None:
        #         await self.dispatch("message_delete", message)
        #         await self._cache.delete_message(message)
        pass

    async def parse_channel_create(self, payload: ChannelCreatePayload) -> None:
        channel = PartialChannel(payload)

        if self._cache:
            await self._cache.set_server_channel(channel)

        await self.dispatch("channel_create", channel)

    async def parse_channel_update(self, payload: ChannelUpdatePayload) -> None:
        if self._cache:
            channel = await self._cache.get_server_channel(payload["_id"])
            if channel is not None:
                # old_channel = copy(channel)
                # channel._update(payload)
                # await self.dispatch("channel_update", old_channel, channel)
                pass

    async def parse_channel_delete(self, payload: ChannelDeletePayload) -> None:
        if self._cache:
            channel = await self._cache.get_server_channel(payload["_id"])
            if channel is not None:
                old_channel = copy(channel)
                await self._cache.delete_server_channel(channel)
                await self.dispatch("channel_delete", old_channel, channel)

    async def parse_channel_group_join(self, payload: ChannelGroupJoinPayload) -> None:
        channel_group = GroupChannel(payload)

        if self._cache:
            # await self._cache.set_dm_channel_id(channel_group.id, channel_group.recipients)
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
            channel = await self._cache.get_channel(payload["id"])
            user = await self._cache.get_user(payload["user"])

            await self.dispatch("channel_start_typing", channel, user)

    async def parse_channel_stop_typing(
        self, payload: ChannelStopTypingPayload
    ) -> None:
        if self._cache:
            channel = await self._cache.get_channel(payload["id"])
            user = await self._cache.get_user(payload["user"])

            await self.dispatch("channel_start_typing", channel, user)

    async def parse_channel_ack(self, payload: ChannelAckPayload) -> None:
        if self._cache:
            channel = await self._cache.get_channel(payload["id"])
            await self.dispatch("channel_ack", channel)

    async def parse_server_update(self, payload: ServerUpdatePayload) -> None:
        if self._cache:
            # server = await self._cache.get_server(payload["_id"])
            # old_server = copy(server)
            # server._update(payload)
            # await self.dispatch("server_update", old_server, server)
            pass

    async def parse_server_delete(self, payload: ServerDeletePayload) -> None:
        if self._cache:
            server = await self._cache.get_server(payload["_id"])
            if server is not None:
                await self.dispatch("server_delete", server)
                await self._cache.delete_server(server)

    async def parse_server_member_join(self, payload: ServerMemberJoinPayload) -> None:
        member = Member(
            app=self.app,
            id=objects.Object(payload["id"]),
            user_id=objects.Object(payload["user"]),
        )

        if self._cache:
            await self._cache.set_member(member)

        await self.dispatch("server_member_join", member)

    async def parse_server_member_leave(
        self, payload: ServerMemberLeavePayload
    ) -> None:
        if self._cache:
            member = await self._cache.get_member(
                objects.Object(payload["id"]), objects.Object(payload["user"])
            )
            if member is not None:
                await self.dispatch("server_member_leave", copy(member))
                await self._cache.delete_member(member)

    async def parse_server_member_update(
        self, payload: ServerMemberUpdatePayload
    ) -> None:
        if self._cache:
            # member = await self._cache.get_member(payload["_id"])
            # old_member = copy(member)
            # member._update(payload)
            # await self.dispatch("server_member_update", old_member, member)
            pass

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
            user = await self._cache.get_user(payload["id"])
            if user is None:
                return
            old_user = copy(user)
            if "delete" in payload:
                if payload["delete"] == "StatusText":
                    user.status.text = None
            if "data" in payload:
                if "username" in payload["data"]:
                    user.username = payload["data"]["username"]
                if "badges" in payload["data"]:
                    user.badges = payload["data"]["badges"]
                if "avatar" in payload["data"]:
                    user.avatar = Attachment(
                        app=self.app,
                        id=objects.Object(payload["data"]["avatar"]["_id"]),
                        tag=payload["data"]["avatar"]["tag"],
                        size=payload["data"]["avatar"]["size"],
                        filename=payload["data"]["avatar"]["filename"],
                        metadata=MetaData(
                            type=payload["data"]["avatar"]["metadata"]["type"]
                        ),
                        content_type=payload["data"]["avatar"]["contentType"],
                    )
                if "flags" in payload["data"]:
                    user.flags = payload["data"]["flags"]
                if "relationship" in payload["data"]:
                    user.relationship = payload["data"]["relationship"]
                if "online" in payload["data"]:
                    user.online = payload["data"]["online"]
            await self._cache.update_user(user)

            await self.dispatch("user_update", old_user, user)

    async def parse_user_relationship(self, payload: UserRelationshipPayload) -> None:
        if self._cache:
            pass

        await self.dispatch("user_relationship")
