from __future__ import annotations

from typing import TYPE_CHECKING
import attr

if TYPE_CHECKING:
    from defectio.types.payloads import ApiInfoPayload, ApiInfoFeaturePayload

__all__ = ["ApiInfo", "ApiFeatures", "ApiUrl"]


@attr.define(hash=False, kw_only=True, weakref_slot=False)
class Feature:
    """The details of the api feature."""

    enabled: bool = attr.ib(eq=False, hash=False, repr=True)
    """If the feature is enabled."""

    url: str = attr.ib(eq=False, hash=False, repr=True)
    """The url of the api feature."""


@attr.define(hash=False, kw_only=True, weakref_slot=False)
class ApiFeatures:
    """The features of the api."""

    captcha: bool = attr.ib(eq=False, hash=False, repr=True)
    """If the captcha feature is enabled."""

    email: bool = attr.ib(eq=False, hash=False, repr=True)
    """If the email feature is enabled."""

    invite_only: bool = attr.ib(eq=False, hash=False, repr=True)
    """If the invite only feature is enabled."""

    autumn: Feature = attr.ib(eq=False, hash=False, repr=True)
    """The autumn feature."""

    january: Feature = attr.ib(eq=False, hash=False, repr=True)
    """The january feature."""

    voso: Feature = attr.ib(eq=False, hash=False, repr=True)
    """The voso feature."""


@attr.define(hash=False, kw_only=True, weakref_slot=False)
class ApiInfo:
    """The details of the api."""

    revolt_version: str = attr.ib(eq=False, hash=False, repr=True)
    """The version of the revolt api."""

    ws_url: str = attr.ib(eq=False, hash=False, repr=True)
    """The url of the websocket."""

    app_url: str = attr.ib(eq=False, hash=False, repr=True)
    """The url of the app."""

    vapid_url: str = attr.ib(eq=False, hash=False, repr=True)
    """The url of the vapid."""
