"""Component that provides the ability to generate event models."""

from __future__ import annotations
from typing import Any

__all__: list[str] = ["EventFactory"]

import abc


class EventFactory(abc.ABC):
    """Interface for components that deserialize JSON events."""

    @abc.abstractmethod
    async parse_ready_event(self, payload: dict[str, Any])
