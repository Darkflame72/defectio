import abc
from .base_events import GatewayEvent
from defectio.models import objects


class ChannelEvent(GatewayEvent, abc.ABC):
    """Event base for any channel-bound event in server or private messages."""

    @property
    @abc.abstractmethod
    def channel_id(self) -> objects:
        """ID of the channel the event relates to.
        Returns
        -------
        hikari.snowflakes.Snowflake
            The ID of the channel this event relates to.
        """
