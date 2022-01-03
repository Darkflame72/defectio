"""Core app interface for application implementations."""
from __future__ import annotations

__all__: typing.List[str] = [
    "CacheAware",
    "EventManagerAware",
    "EntityFactoryAware",
    "EventFactoryAware",
    "ExecutorAware",
    "GatewayBotAware",
    "IntentsAware",
    "NetworkSettingsAware",
    "RESTAware",
    "RESTBotAware",
    "Runnable",
    "InteractionServerAware",
    "ShardAware",
    "VoiceAware",
]

import typing

if typing.TYPE_CHECKING:
    import datetime
    from concurrent import futures

    from defectio import channels
    from defectio import config
    from defectio import servers
    from defectio import objects
    from defectio import users as users_
    from defectio.base import cache as cache_
    from defectio.base import event_manager as event_manager_
    from defectio.base import gateway as gateway_
    from defectio.base import rest as rest_
    from defectio.models.api_info import ApiInfo


@typing.runtime_checkable
class NetworkSettingsAware(typing.Protocol):
    """Structural supertype for any component aware of network settings."""

    __slots__: typing.Sequence[str] = ()

    @property
    def http_settings(self) -> config.HTTPSettings:
        raise NotImplementedError

    @property
    def proxy_settings(self) -> config.ProxySettings:
        raise NotImplementedError

    @property
    def api_info(self) -> ApiInfo:
        raise NotImplementedError


@typing.runtime_checkable
class EventManagerAware(typing.Protocol):
    """Structural supertype for a event manager-aware object.
    event manager-aware components are able to manage event listeners and waiters.
    """

    __slots__: typing.Sequence[str] = ()

    @property
    def event_manager(self) -> event_manager_.EventManager:
        raise NotImplementedError


@typing.runtime_checkable
class GatewayAware(typing.Protocol):
    """Structural supertype for a gateway-aware object.
    gateway-aware components are able to receive events from the websocket.
    """

    __slots__: typing.Sequence[str] = ()

    @property
    def gateway(self) -> gateway_.Gateway:
        raise NotImplementedError


@typing.runtime_checkable
class RESTAware(
    GatewayAware,
    NetworkSettingsAware,
    EventManagerAware,
    typing.Protocol,
):
    """Structural supertype for a REST-aware object.
    These are able to perform REST API calls.
    """

    __slots__: typing.Sequence[str] = ()

    @property
    def rest(self) -> rest_.RESTClient:
        raise NotImplementedError


@typing.runtime_checkable
class ApplicationAware(
    GatewayAware,
    NetworkSettingsAware,
    typing.Protocol,
):
    """Structural supertype for a application-aware object.
    These will expose a mapping of shards, the intents in use
    and the bot user object.
    """

    __slots__: typing.Sequence[str] = ()

    def get_me(self) -> typing.Optional[users_.OwnUser]:
        raise NotImplementedError


@typing.runtime_checkable
class CacheAware(typing.Protocol):
    """Structural supertype for a cache-aware object.
    Any cache-aware objects are able to access the Discord application cache.
    """

    __slots__: typing.Sequence[str] = ()

    @property
    def cache(self) -> cache_.Cache:
        """Return the immutable cache implementation for this object.
        Returns
        -------
        hikari.api.cache.Cache
            The cache component for this object.
        """
        raise NotImplementedError


@typing.runtime_checkable
class Runnable(typing.Protocol):
    """Structural super-type for an application which can be run independently."""

    __slots__: typing.Sequence[str] = ()

    @property
    def is_alive(self) -> bool:
        """Check whether the application is running or not.
        This is useful as some functions might raise
        `hikari.errors.ComponentStateConflictError` if this is
        `builtins.False`.
        Returns
        -------
        builtins.bool
            Whether the bot is running or not.
        """
        raise NotImplementedError

    async def close(self) -> None:
        """Kill the application by shutting all components down."""

    async def join(self) -> None:
        """Wait indefinitely until the application closes.
        This can be placed in a task and cancelled without affecting the
        application runtime itself. Any exceptions raised by shards will be
        propagated to here.
        """
        raise NotImplementedError

    def run(self) -> None:
        """Start the application and block until it's finished running."""
        raise NotImplementedError

    async def start(self) -> None:
        """Start the application and then return."""
        raise NotImplementedError


@typing.runtime_checkable
class GatewayBotAware(
    RESTAware,
    Runnable,
    ApplicationAware,
    EventManagerAware,
    CacheAware,
    typing.Protocol,
):
    """Structural supertype for a component that has all the gateway components."""

    __slots__: typing.Sequence[str] = ()

    async def join(self, until_close: bool = True) -> None:
        raise NotImplementedError

    def run(self) -> None:
        raise NotImplementedError

    async def start(self) -> None:
        raise NotImplementedError


@typing.runtime_checkable
class RESTBotAware(
    RESTAware,
    Runnable,
    typing.Protocol,
):
    """Structural supertype for a component that has all the RESTful components."""

    __slots__: typing.Sequence[str] = ()
