import abc
from defectio.base.gateway import Gateway


class Event(abc.ABC):
    """Base event type that all Defectio events should subclass."""

    @property
    @abc.abstractmethod
    def app(self):
        """The application that is sending the event."""
