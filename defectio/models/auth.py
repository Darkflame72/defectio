from __future__ import annotations

from typing import TypedDict, Union

__all__ = ["Auth"]

BotAuthHeader = TypedDict("BotAuthHeder", {"x-bot-token": str})
UserAuthHeader = TypedDict("BotAuthHeder", {"x-user-token": str})
WebsocketAuthPayload = TypedDict("BotAuthHeder", {"x-user-token": str})


class Auth:

    __slots__ = ("token", "bot")

    def __init__(self, data: str, bot: bool = True):
        self.token = str(data)
        self.bot = bot

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
