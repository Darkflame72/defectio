"""Core app interface for application implementations."""
from __future__ import annotations

from typing import Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from defectio.base import event_manager as event_manager_
    from defectio.base import cache as cache_
    from defectio.base import resr as rest_
    from defectio import config


@runtime_checkable
class NetworkSettingsAware(Protocol):
    """Structural supertype for any component aware of network settings."""

    __slots__: tuple[str] = ()

    @property
    def http_settings(self) -> config.HTTPSettings:
        """Return the HTTP settings in use by this component.

        Returns
        -------
        defectio.config.HTTPSettings
            The HTTP settings in use.
        """
        raise NotImplementedError

    @property
    def proxy_settings(self) -> config.ProxySettings:
        """Return the proxy settings in use by this component.

        Returns
        -------
        defectio.config.ProxySettings
            The proxy settings in use.
        """
        raise NotImplementedError


@runtime_checkable
class EventManagerAware(Protocol):
    """Structural supertype for a event manager-aware object.

    event manager-aware components are able to manage event listeners and waiters.
    """

    __slots__: tuple[str] = ()

    @property
    def event_manager(self) -> event_manager_.EventManager:
        """Return the event manager for this object.
        Returns
        -------
        defectio.base.event_manager.EventManager
            The event manager component.
        """
        raise NotImplementedError


@runtime_checkable
class RESTAware(
    NetworkSettingsAware,
    Protocol,
):
    """Structural supertype for a REST-aware object.

    These are able to perform REST API calls.
    """

    __slots__: tuple[str] = ()

    @property
    def rest(self) -> rest_.RESTClient:
        """Return the REST client to use for HTTP requests.

        Returns
        -------
        defectio.api.rest.RESTClient
            The REST client to use.
        """
        raise NotImplementedError


@runtime_checkable
class GatewayAware(
    NetworkSettingsAware,
    Protocol,
):
    """Structural supertype for a gateway-aware object.

    These will expose the gateway and the bot user object.
    """

    __slots__: tuple[str] = ()


@runtime_checkable
class CacheAware(Protocol):
    """Structural supertype for a cache-aware object.

    Any cache-aware objects are able to access the Revolt application cache.
    """

    __slots__: tuple[str] = ()

    @property
    def cache(self) -> cache_.Cache:
        """Return the immutable cache implementation for this object.

        Returns
        -------
        defectio.api.cache.Cache
            The cache component for this object.
        """
        raise NotImplementedError
