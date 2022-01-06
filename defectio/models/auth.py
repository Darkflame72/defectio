from __future__ import annotations

from typing import TypedDict
from typing import Union

import attr

__all__ = ["Auth"]

BotAuthHeader = TypedDict("BotAuthHeder", {"x-bot-token": str})
UserAuthHeader = TypedDict("BotAuthHeder", {"x-user-token": str})
WebsocketAuthPayload = TypedDict("BotAuthHeder", {"x-user-token": str})


@attr.define(hash=False, kw_only=True, weakref_slot=False)
class Auth:
    """Authentication details for the api."""

    token: str = attr.ib(eq=False, hash=False, repr=True)
    """The token to use for authentication."""

    bot: bool = attr.ib(eq=False, hash=False, repr=True)
    """If the token is for a bot."""

    @property
    def headers(self) -> Union[BotAuthHeader, UserAuthHeader]:
        """Authentication headers to use for api.

        Returns
        -------
        Union[BotAuthHeader, UserAuthHeader]
            Authentication header to use.
        """
        if self.bot is True:
            return {"x-bot-token": self.token}
        return {"x-session-token": self.token}

    @property
    def payload(self) -> WebsocketAuthPayload:
        """Authentication payload for websocket.

        Returns
        -------
        WebsocketAuthPayload
            payload to send to websocket.
        """
        return {"token": self.token}
