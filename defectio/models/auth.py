from __future__ import annotations

__all__ = ["Auth"]


class Auth:
    def __init__(self, data: str, bot: bool = True):
        self.token = str(data)
        self.is_bot = bot

    @property
    def headers(self):
        if self.is_bot is True:
            return {"x-bot-token": self.token}
        return {"x-session-token": self.token}

    @property
    def payload(self):
        return {"token": self.token}
