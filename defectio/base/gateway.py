"""Provides an interface to connect to the Revolt websocket."""
import abc
import enum
import typing

from defectio.models import objects
from defectio.models.channel import TextChannel


__all__ = ["Gateway", "GatewayDataFormat"]


@typing.final
class GatewayDataFormat(str, enum.Enum):
    """Format of inbound gateway payloads."""

    JSON = "json"
    """Javascript serialized object notation."""
    MSGPACK = "msgpack"
    """MSGPack transmission format."""


class Gateway(abc.ABC):
    """Interface for communicating with the Revolt websocket."""

    __slots__: tuple[str] = ()

    @abc.abstractmethod
    async def close(self) -> None:
        """Close the websocket if it is connected, otherwise do nothing."""

    @abc.abstractmethod
    async def start(self) -> None:
        """Start the websocket, this is a blocking call as it will cycle though websocket events."""

    @abc.abstractmethod
    async def begin_typing(self, channel: objects.ObjectishOr[TextChannel]) -> None:
        """Start typing in a channel.

        Parameters
        ----------
        channel : objects.ObjectishOr[TextChannel]
            The channel to start typing in.
        """

    @abc.abstractmethod
    async def stop_typing(self, channel: objects.ObjectishOr[TextChannel]) -> None:
        """Stop typing in a channel.

        Parameters
        ----------
        channel : objects.ObjectishOr[TextChannel]
            Channel to stop typing in.
        """

    @abc.abstractmethod
    async def ping(self) -> None:
        """Send a ping packet to the websocket."""
