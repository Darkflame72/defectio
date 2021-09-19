"""Data class containing configuration settings."""

from __future__ import annotations

__all__: typing.List[str] = [
    "CacheComponents",
    "CacheSettings",
]

import typing
import enum
import attr


class CacheComponents(enum.Flag):
    """Flags to control the cache components."""

    NONE = 0
    """Disables the cache."""

    SERVERS = 1 << 0
    """Enables the guild cache."""

    SERVER_CHANNELS = 1 << 1
    """Enables the guild channels cache."""

    MEMBERS = 1 << 2
    """Enables the members cache."""

    ROLES = 1 << 3
    """Enables the roles cache."""

    INVITES = 1 << 4
    """Enables the invites cache."""

    EMOJIS = 1 << 5
    """Enables the invites cache."""

    PRESENCES = 1 << 6
    """Enables the presences cache."""

    VOICE_STATES = 1 << 7
    """Enables the voice states cache."""

    MESSAGES = 1 << 8
    """Enables the messages cache."""

    DM_CHANNEL_IDS = 1 << 10
    """Enables the DM channel IDs cache."""

    ALL = (
        SERVERS
        | SERVER_CHANNELS
        | MEMBERS
        | ROLES
        | INVITES
        | EMOJIS
        | PRESENCES
        | VOICE_STATES
        | MESSAGES
        | DM_CHANNEL_IDS
    )
    """Fully enables the cache."""


class CacheSettings:
    """Settings to control the cache."""

    components: CacheComponents = attr.field(default=CacheComponents.ALL)
    """The cache components to use.

    Defaults to `CacheComponents.ALL`.
    """

    max_messages: int = attr.field(default=300)
    """The maximum number of messages to store in the cache at once.

    This will have no effect if the messages cache is not enabled.

    Defaults to `300`.
    """

    max_dm_channel_ids: int = attr.field(default=50)
    """The maximum number of channel IDs to store in the cache at once.

    This will have no effect if the channel IDs cache is not enabled.

    Defaults to `50`.
    """
