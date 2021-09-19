import abc
from defectio.base.gateway import Gateway


class Event(abc.ABC):
    """Base event type that all Defectio events should subclass."""

    @property
    @abc.abstractmethod
    def app(self):
        """The application that is sending the event."""


class GatewayEvent(Event, abc.ABC):
    """Base class for any event that was gateway-specific."""

    @property
    @abc.abstractmethod
    def gatewat(self) -> Gateway:
        """Shard that received this event.

        Returns
        -------
        Gateway
            The shard that triggered the event.
        """
