from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types.payloads import ApiInfoPayload, ApiInfoFeaturePayload

__all__ = ["ApiInfo", "ApiFeatures", "ApiUrl"]


class ApiUrl:
    def __init__(self, data: ApiInfoFeaturePayload):
        self.enabled = data.get("enabled", False)
        self.url = data.get("url", "")

    def __repr__(self):
        return f"<ApiUrl {self.enabled} {self.url}>"

    def __str__(self):
        return f"{self.enabled} {self.url}"


class ApiFeatures:
    def __init__(self, data: ApiInfoFeaturePayload) -> None:
        self.captcha = data.get("captcha")
        self.email = data.get("email")
        self.invite_only = data.get("invite_only")
        self.autumn = ApiUrl(data.get("autumn"))
        self.january = ApiUrl(data.get("january"))
        self.voso = ApiUrl(data.get("voso"))

    def __repr__(self) -> str:
        return f"<ApiFeatures {self.__dict__}>"

    def __str__(self) -> str:
        return f"<ApiFeatures {self.__dict__}>"


class ApiInfo:
    def __init__(self, data: ApiInfoPayload):
        self.revolt_version = data.get("revolt")
        self.features = ApiFeatures(data.get("features"))
        self.ws_url = data.get("ws")
        self.app_url = data.get("app")
        self.vapid_url = data.get("vapid")

    def __repr__(self) -> str:
        return f"<ApiInfo {self.__dict__}>"

    def __str__(self) -> str:
        return f"<ApiInfo {self.__dict__}>"
