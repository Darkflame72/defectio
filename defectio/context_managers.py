from __future__ import annotations

import asyncio
from typing import Optional
from typing import Type
from typing import TYPE_CHECKING
from typing import TypeVar

if TYPE_CHECKING:
    from .models.abc import Messageable

    from types import TracebackType

    TypingT = TypeVar("TypingT", bound="Typing")

__all__ = ("Typing",)


def _typing_done_callback(fut: asyncio.Future) -> None:
    try:
        fut.exception()
    except (asyncio.CancelledError, Exception):
        pass


class Typing:
    def __init__(self, messageable: Messageable) -> None:
        self.loop: asyncio.AbstractEventLoop = messageable._state.loop
        self.messageable: Messageable = messageable

    async def do_typing(self) -> None:
        try:
            channel = self._channel
        except AttributeError:
            channel = await self.messageable._get_channel()

        typing = channel._state.websocket.begin_typing

        while True:
            await typing(channel.id)
            await asyncio.sleep(10)

    async def end_typing(self) -> None:
        try:
            channel = self._channel
        except AttributeError:
            channel = await self.messageable._get_channel()

        typing = channel._state.websocket.stop_typing

        while True:
            await typing(channel.id)
            await asyncio.sleep(10)

    def __enter__(self: TypingT) -> TypingT:
        self.task: asyncio.Task = self.loop.create_task(self.do_typing())
        self.task.add_done_callback(_typing_done_callback)
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.task.cancel()
        self.task: asyncio.Task = self.loop.run_until_complete(self.end_typing())

    async def __aenter__(self: TypingT) -> TypingT:
        self._channel = channel = await self.messageable._get_channel()
        await channel._state.websocket.begin_typing(channel.id)
        return self.__enter__()

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.task.cancel()
        await self.end_typing()
