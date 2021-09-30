from __future__ import annotations

from typing import Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .message import Message


__all__ = (
    "RawMessageDeleteEvent",
    "RawMessageUpdateEvent",
)


class _RawReprMixin:
    def __repr__(self) -> str:
        value = " ".join(f"{attr}={getattr(self, attr)!r}" for attr in self.__slots__)
        return f"<{self.__class__.__name__} {value}>"


class RawMessageDeleteEvent(_RawReprMixin):
    """Represents the event payload for a :func:`on_raw_message_delete` event.
    Attributes
    ------------
    channel_id: :class:`str`
        The channel ID where the deletion took place.
    message_id: :class:`str`
        The message ID that got deleted.
    cached_message: Optional[:class:`Message`]
        The cached message, if found in the internal message cache.
    """

    __slots__ = ("message_id", "channel_id", "cached_message")

    def __init__(self, data) -> None:
        self.message_id: str = data["id"]
        self.channel_id: str = data["channel"]
        self.cached_message: Optional[Message] = None


class RawMessageUpdateEvent(_RawReprMixin):
    """Represents the payload for a :func:`on_raw_message_edit` event.

    Attributes
    -----------
    message_id: :class:`str`
        The message ID that got updated.
    data: :class:`dict`
        The raw data given by the `gateway https://developers.revolt.chat/api#tag/Messaging/paths/~1channels~1:channel~1messages/get`
    cached_message: Optional[:class:`Message`]
        The cached message, if found in the internal message cache. Represents the message before
        it is modified by the data in :attr:`RawMessageUpdateEvent.data`.
    """

    __slots__ = ("message_id", "data", "cached_message")

    def __init__(self, data) -> None:
        self.message_id: str = data["id"]
        self.data = data
        self.cached_message: Optional[Message] = None
