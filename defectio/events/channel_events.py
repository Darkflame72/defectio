import abc
from defectio.models.channel import PartialChannel
from .base_events import Event
from defectio.models import objects


class ChannelEvent(Event, abc.ABC):
    """Event base for any channel-bound event in server or private messages."""

    @property
    @abc.abstractmethod
    def channel_id(self) -> objects.ObjectishOr[PartialChannel]:
        """ID of the channel the event relates to.

        Returns
        -------
        objects.ObjectishOr[PartialChannel]
            The ID of the channel this event relates to.
        """
