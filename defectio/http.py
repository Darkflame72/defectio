from __future__ import annotations

import logging
from typing import Any
from typing import Literal
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

import aiohttp
import orjson as json
import ulid
from defectio.errors import HTTPException, NotFound, Forbidden
from defectio.errors import LoginFailure
from defectio.errors import RevoltServerError
from defectio.models.apiinfo import ApiInfo

from . import __version__
from .models import Auth

if TYPE_CHECKING:
    import aiohttp
    
    from .types.embed import Embed
    
    from .types.payloads import (
        AccountPayload,
        ApiInfoPayload,
        DMChannelPayload,
        LoginPayload,
        MutualFriendsPayload,
        ProfilePayload,
        RelationshipPayload,
        RelationshipStatusPayload,
        SessionPayload,
        ChannelPayload,
        UserPayload,
        ChannelInvitePayload,
        EditChannelPayload,
        FetchMessagePayload,
        GroupPayload,
        JoinCallPayload,
        MessagePayload,
        MessagePollPayload,
        SearchMessagePayload,
        ServerPayload,
        BansPayload,
        BotPayload,
        CreateRolePayload,
        InvitePayload,
        JoinInvitePayload,
        MemberPayload,
        PublicBotPayload,
        ServerMembersPayload,
        SettingsPayload,
        UnreadsPayload,
    )
    from .models import File

logger = logging.getLogger("defectio")


class DefectioHTTP:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_url: str,
        user_agent: str,
        *,
        api_info: Optional[ApiInfo] = None,
    ):
        self._session = session if session is not None else aiohttp.ClientSession()
        self.auth: Optional[Auth] = None
        self.api_url = api_url
        self.user_agent = user_agent
        self.api_info = api_info

    def set_api_info(self, api_info: ApiInfo) -> None:
        self.api_info = api_info

    async def request(
        self, method: str, path: str, *, auth_needed=True, **kwargs: Any
    ) -> dict[str, Any]:
        url = f"{self.api_url}/{path}"
        headers = kwargs.get("headers", {})
        headers["User-Agent"] = self.user_agent
        if auth_needed:
            if not self.auth:
                raise LoginFailure("Not logged in")
            headers = {**headers, **self.auth.headers}
        if "json" in kwargs:
            headers["Content-Type"] = "application/json"
        kwargs["headers"] = headers

        response: Optional[aiohttp.ClientResponse] = None
        data: Optional[Union[dict[str, Any], str]] = None
        async with self._session.request(method, url, **kwargs) as response:
            data = await response.text()
            if 300 > response.status >= 200:
                if data != "":
                    data = json.loads(data)
                logger.debug("%s %s has received %s", method, url, data)
                return data

            if 500 > response.status >= 400:
                raise HTTPException(response, data)

            if response.status >= 500:
                raise RevoltServerError(response, data)

    async def upload_request(self, method: str, tag: str, **kwargs: Any) -> Any:
        url = f"{self.api_info.features.autumn.url}/{tag}"
        headers = kwargs.get("headers", {})
        headers["User-Agent"] = self.user_agent

        if not self.auth:
            raise LoginFailure("Not logged in")

        kwargs["headers"] = {**headers, **self.auth.headers}

        response: Optional[aiohttp.ClientResponse] = None
        data: Optional[Union[dict[str, Any], str]] = None

        async with self._session.request(method, url, **kwargs) as response:
            data = await response.text()
            if 300 > response.status >= 200:
                if data != "":
                    data = json.loads(data)
                logger.debug("%s %s has received %s", method, url, data)
                return data

            if 500 > response.status >= 400:
                raise RevoltServerError(response, data)

            if response.status >= 500:
                raise RevoltServerError(response, data)

    async def get_from_url(self, url: str) -> bytes:
        async with self._session.get(url) as resp:
            if resp.status == 200:
                return await resp.read()
            elif resp.status == 404:
                # raise NotFound(resp, "asset not found")
                return None
            elif resp.status == 403:
                raise Forbidden(resp, "cannot retrieve asset")
            else:
                raise HTTPException(resp, "failed to get asset")

    def start(self, token: str, bot: bool = True) -> Auth:
        self.auth = Auth(token, bot=bot)
        self.is_bot = bot
        return self.auth

    async def user_login(self, email: str, password: str) -> Auth:
        session = await self.login(email, password)
        self.auth = Auth(session)
        self.is_bot = False
        return self.auth

    async def close(self) -> None:
        if self._session:
            await self._session.close()

    async def node_info(self) -> ApiInfoPayload:
        path = ""
        return await self.request("GET", path, auth_needed=False)

    async def send_file(self, *, file: File, tag: str):
        form = aiohttp.FormData()
        form.add_field("file", file.fp, filename=file.filename)

        return await self.upload_request("POST", tag, data=form)

    ################
    ## Onboarding ##
    ################

    async def check_onboarding(self):
        path = "onboard/hello"
        return await self.request("GET", path)

    async def complete_onboarding(self, username: str):
        path = "onboard/complete"
        return await self.request("GET", path, json={"username": username})

    ##########
    ## Auth ##
    ##########

    async def create_account(self, email: str, password: str, **kwargs):
        path = "auth/create"
        kwargs["email"] = email
        kwargs["password"] = password
        return await self.request("POST", path, json=kwargs, auth_needed=False)

    async def resend_verification(self, email: str, **kwargs) -> None:
        path = "auth/resend"
        kwargs["email"] = email
        return await self.request("POST", path, json=kwargs, auth_needed=False)

    async def login(self, email: str, password: str, **kwargs) -> LoginPayload:
        path = "auth/login"
        kwargs["email"] = email
        kwargs["password"] = password
        kwargs["device_name"] = self.user_agent
        return await self.request(
            "POST", path, json={"email": email, "password": password}, auth_needed=False
        )

    async def send_password_reset(self, email: str, **kwargs):
        path = "auth/send_reset"
        kwargs["email"] = email
        return await self.request("POST", path, json=kwargs, auth_needed=False)

    async def confirm_password_reset(self, password: str, token: str):
        path = "/auth/reset"
        return await self.request(
            "POST", path, json={"password": password, "token": token}, auth_needed=False
        )

    async def get_account(self) -> AccountPayload:
        path = "auth/user"
        return await self.request("GET", path)

    async def check_auth(self):
        path = "auth/check"
        return await self.request("GET", path)

    async def change_password(self, old_password: str, new_password: str):
        path = "auth/change/password"
        return await self.request(
            "POST",
            path,
            json={"password": old_password, "new_password": new_password},
        )

    async def change_email(self, password: str, email: str):
        path = "auth/change/email"
        return await self.request("POST", path, json={"email": email})

    async def delete_session(self, session_id: str):
        path = f"auth/sessions/{session_id}"
        return await self.request("POST", path)

    async def get_sessions(self) -> list[SessionPayload]:
        path = "auth/sessions"
        return await self.request("GET", path)

    async def logout(self):
        path = "auth/logout"
        return await self.request("POST", path)

    ######################
    ## User Information ##
    ######################

    ## Self

    async def edit_self(self, json):
        path = "users/@me"
        return await self.request("PATCH", path, json=json)

    async def change_username(self, username: str, password: str):
        path = "users/@me/username"
        return await self.request(
            "PATCH", path, json={"username": username, "password": password}
        )

    ## Users

    async def get_user(self, user_id: str) -> UserPayload:
        path = f"users/{user_id}"
        return await self.request("GET", path)

    async def get_user_profile(self, user_id: str) -> ProfilePayload:
        path = f"users/{user_id}/profile"
        return await self.request("GET", path)

    async def get_user_default_avatar(self, user_id: str):
        path = f"users/{user_id}/default_avatar"
        return await self.request("GET", path)

    async def get_mutual_friends(self, user_id: str) -> MutualFriendsPayload:
        path = f"users/{user_id}/mutual_friends"
        return await self.request("GET", path)

    ######################
    ## Direct Messaging ##
    ######################

    async def get_dms(self) -> list[DMChannelPayload]:
        path = "users/dms"
        return await self.request("GET", path)

    async def open_dm(self, user_id: str) -> DMChannelPayload:
        path = f"users/{user_id}/dm"
        return await self.request("GET", path)

    ###################
    ## Relationships ##
    ###################

    async def get_relationships(self) -> list[RelationshipPayload]:
        path = "users/relationships"
        return await self.request("GET", path)

    async def get_relationship(self, user_id: str) -> RelationshipPayload:
        path = f"users/{user_id}/relationships"
        return await self.request("GET", path)

    async def friend_request(self, user_id: str) -> RelationshipStatusPayload:
        path = f"users/{user_id}/friend"
        return await self.request("PUT", path)

    async def remove_friend(self, user_id: str) -> RelationshipStatusPayload:
        path = f"users/{user_id}/friend"
        return await self.request("DELETE", path)

    async def block_user(self, user_id: str) -> RelationshipStatusPayload:
        path = f"users/{user_id}/block"
        return await self.request("PUT", path)

    async def unblock_user(self, user_id: str) -> RelationshipStatusPayload:
        path = f"users/{user_id}/block"
        return await self.request("DELETE", path)

    #########################
    ## Channel Information ##
    #########################

    async def get_channel(self, channel_id: str) -> ChannelPayload:
        path = f"channels/{channel_id}"
        return await self.request("GET", path)

    async def edit_channel(self, channel_id: str, **kwargs) -> EditChannelPayload:
        path = f"channels/{channel_id}"
        return await self.request("PATCH", path, json=kwargs)

    async def close_channel(self, channel_id: str):
        path = f"channels/{channel_id}"
        return await self.request("DELETE", path)

    #####################
    ## Channel Invites ##
    #####################

    async def create_channel_invite(self, channel_id: str) -> ChannelInvitePayload:
        path = f"channels/{channel_id}/invites"
        return await self.request("POST", path)

    #########################
    ## Channel Permissions ##
    #########################

    async def set_channel_role_permissions(
        self, channel_id: str, role_id: str, permissions: int
    ):
        path = f"channels/{channel_id}/permissions/{role_id}"
        return await self.request("PUT", path, json={"permissions": permissions})

    async def set_channel_default_role_permissions(
        self, channel_id: str, permissions: int
    ):
        path = f"channels/{channel_id}/permissions/default"
        return await self.request("PUT", path, json={"permissions": permissions})

    ###############
    ## Messaging ##
    ###############

    async def send_message(
        self,
        channel_id: str,
        *,
        content: Optional[str] = None,
        attachments: Optional[list[str]] = None,
        replies: Optional[Any] = None,
        embeds: Optional[list[Embed]] = None
    ) -> MessagePayload:
        
        path = f"channels/{channel_id}/messages"
        json = {"nonce": ulid.new().str}
        
        if content is not None:
            json["content"] = content
            
        if attachments is not None and len(attachments) > 0:
            json["attachments"] = attachments
            
        if replies is not None:
            json["replies"] = replies
        
        if embeds:
            json["embeds"] = [e.to_dict() for e in embeds]
               
        return await self.request("POST", path, json=json)

    async def get_messages(
        self,
        channel_id: str,
        *,
        limit: int = 100,
        before: Optional[str] = None,
        after: Optional[str] = None,
        sort: Literal["Latest", "Oldest"] = "Latest",
        nearby: Optional[list[str]] = None,
        include_users: bool = True,
    ) -> list[FetchMessagePayload]:
        path = f"channels/{channel_id}/messages"
        json = {"sort": sort}
        if limit:
            json["limit"] = limit
        if before:
            json["before"] = before
        if after:
            json["after"] = after
        if nearby:
            json["nearby"] = nearby
        if not include_users:
            json["include_users"] = include_users
        return await self.request("GET", path, json=json)

    async def get_message(self, channel_id: str, message_id: str) -> MessagePayload:
        path = f"channels/{channel_id}/messages/{message_id}"
        return await self.request("GET", path)

    async def edit_message(
        self,
        channel_id: str,
        message_id: str,
        content: str,
    ):
        path = f"channels/{channel_id}/messages/{message_id}"
        return await self.request("PATCH", path, json={"content": content})

    async def delete_message(self, channel_id: str, message_id: str):
        path = f"channels/{channel_id}/messages/{message_id}"
        return await self.request("DELETE", path)

    async def poll_message_changes(
        self, channel_id: str, message_ids: list[str]
    ) -> MessagePayload:
        path = f"channels/{channel_id}/messages/stale"
        return await self.request("GET", path, json=message_ids)

    async def search_message(
        self,
        channel_id: str,
        query: str,
        *,
        limit: int = 100,
        before: Optional[str] = None,
        after: Optional[str] = None,
        sort: Literal["Latest", "Oldest", "Relevant"] = "Latest",
        include_users: bool = True,
    ) -> SearchMessagePayload:
        path = f"channels/{channel_id}/messages/search"
        json = {"query": query, "sort": sort, "include_users": include_users}
        if limit:
            json["limit"] = limit
        if before:
            json["before"] = before
        if after:
            json["after"] = after
        return await self.request("GET", path, json=json)

    async def acknoledge_message(self, channel_id: str, message_id: str):
        path = f"channels/{channel_id}/ack/{message_id}"
        return await self.request("PUT", path)

    ############
    ## Groups ##
    ############

    async def create_group(
        self,
        name: str,
        *,
        description: Optional[str] = None,
        users: Optional[list[str]] = None,
    ) -> GroupPayload:
        path = "channels/create"
        json = {"name": name, "nonce": ulid.new().str}
        if description:
            json["description"] = description
        if users:
            json["users"] = users
        return await self.request("POST", path, json=json)

    async def get_group_members(self, group_id: str) -> list[UserPayload]:
        path = f"channels/{group_id}/members"
        return await self.request("GET", path)

    async def add_group_member(self, group_id: str, user_id: str):
        path = f"channels/{group_id}/recipients/{user_id}"
        return await self.request("PUT", path)

    async def remove_group_member(self, group_id: str, user_id: str):
        path = f"channels/{group_id}/members/recipients/{user_id}"
        return await self.request("DELETE", path)

    async def join_call(self, channel_id: str) -> JoinCallPayload:
        path = f"channels/{channel_id}/join_call"
        return await self.request("POST", path)

    ########################
    ## Server Information ##
    ########################

    async def get_server(self, server_id: str) -> ServerPayload:
        path = f"servers/{server_id}"
        return await self.request("GET", path)

    async def edit_server(
        self,
        server_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        banner: Optional[str] = None,
        categories: Optional[list[Any]] = None,
        system_messages: Optional[Any] = None,
        remove: Optional[Literal["Banner", "Description", "Icon"]] = None,
    ):
        path = f"servers/{server_id}"
        json = {}
        if name:
            json["name"] = name
        if description:
            json["description"] = description
        if icon:
            json["icon"] = icon
        if banner:
            json["banner"] = banner
        if categories:
            json["categories"] = categories
        if system_messages:
            json["system_messages"] = system_messages
        if remove:
            json["remove"] = remove
        return await self.request("PATCH", path, json=json)

    async def remove_server(self, server_id: str):
        path = f"servers/{server_id}"
        return await self.request("DELETE", path)

    async def create_server(
        self, name: str, *, description: Optional[str] = None
    ) -> ServerPayload:
        path = "servers/create"
        json = {"name": name, "nonce": ulid.new().str}
        if description:
            json["description"] = description
        return await self.request("POST", path, json=json)

    async def create_channel(
        self,
        server_id: str,
        name: str,
        *,
        type: Literal["Text", "Voice"] = "Text",
        description: Optional[str] = None,
    ) -> ChannelPayload:
        path = f"servers/{server_id}/channels"
        json = {"name": name, "type": type, "nonce": ulid.new().str}
        if description:
            json["description"] = description
        return await self.request("POST", path, json=json)

    async def get_invite(self, server_id: str):
        path = f"invites/{server_id}/invites"
        return await self.request("GET", path)

    async def mark_channels_read(self, server_id: str):
        path = f"channels/{server_id}/ack"
        return await self.request("POST", path)

    ####################
    ## Server Members ##
    ####################

    async def get_member(self, server_id: str, member_id: str) -> MemberPayload:
        path = f"servers/{server_id}/members/{member_id}"
        return await self.request("GET", path)

    async def edit_member(
        self,
        server_id: str,
        member_id: str,
        *,
        nickname: Optional[list[str]] = None,
        roles: Optional[list[str]] = None,
        avatar: Optional[str] = None,
        remove: Optional[Literal["Avatar", "Nickname"]] = None,
    ):
        path = f"servers/{server_id}/members/{member_id}"
        json = {}
        if roles:
            json["roles"] = roles
        if nickname:
            json["nick"] = nickname
        if avatar:
            json["avatar"] = avatar
        if remove:
            json["remove"] = remove
        return await self.request("PATCH", path, json=json)

    async def kick_member(self, server_id: str, member_id: str):
        path = f"servers/{server_id}/members/{member_id}"
        return await self.request("DELETE", path)

    async def get_members(self, server_id: str) -> ServerMembersPayload:
        path = f"servers/{server_id}/members"
        return await self.request("GET", path)

    async def ban_member(
        self, server_id: str, member_id: str, reason: Optional[str] = None
    ):
        path = f"servers/{server_id}/ban/{member_id}"
        json = {"reason": reason}
        return await self.request("PUT", path, json=json)

    async def unban_member(self, server_id: str, member_id: str):
        path = f"servers/{server_id}/ban/{member_id}"
        return await self.request("DELETE", path)

    async def get_bans(self, server_id: str) -> BansPayload:
        path = f"servers/{server_id}/bans"
        return await self.request("GET", path)

    ########################
    ## Server Permissions ##
    ########################

    async def set_server_role_permissions(
        self, server_id: str, role_id: str, *, permissions: int
    ):
        path = f"servers/{server_id}/permissions/{role_id}"
        return await self.request("PUT", path, json={"permissions": 0})

    async def set_server_default_role_permissions(
        self, server_id: str, permissions: int
    ):
        path = f"servers/{server_id}/permissions/default_role"
        return await self.request("PUT", path, json={"permissions": permissions})

    async def create_role(self, server_id: str, *, name: str) -> CreateRolePayload:
        path = f"servers/{server_id}/roles"
        json = {"name": name}
        return await self.request("POST", path, json=json)

    async def edit_role(
        self,
        server_id: str,
        role_id: str,
        *,
        name: Optional[str] = None,
        colour: Optional[str] = None,
        hoist: Optional[bool] = None,
        rank: Optional[int] = None,
        remove: Optional[Literal["Colour"]] = None,
    ):
        path = f"servers/{server_id}/roles/{role_id}"
        json = {"name": name}
        if colour:
            json["colour"] = colour
        if hoist:
            json["hoist"] = hoist
        if rank:
            json["rank"] = rank
        if remove:
            json["remove"] = remove
        return await self.request("PATCH", path, json=json)

    async def delete_role(self, server_id: str, role_id: str):
        path = f"servers/{server_id}/roles/{role_id}"
        return await self.request("DELETE", path)

    ##########
    ## Bots ##
    ##########

    async def create_bot(self, name: str) -> BotPayload:
        path = "bots/create"
        json = {"name": name}
        return await self.request("POST", path, json=json)

    async def get_owned_bots(self) -> list[BotPayload]:
        path = "bots/@me"
        return await self.request("GET", path)

    async def get_bot(self, bot_id: str) -> BotPayload:
        path = f"bots/{bot_id}"
        return await self.request("GET", path)

    async def edit_bot(
        self,
        bot_id: str,
        *,
        name: Optional[str] = None,
        public: Optional[bool] = None,
        interactions_url: Optional[str] = None,
        remove: Optional[Literal["InteractionsURL"]] = None,
    ):
        path = f"bots/{bot_id}"
        json = {}
        if name:
            json["name"] = name
        if public:
            json["public"] = public
        if interactions_url:
            json["interactionsURL"] = interactions_url
        if remove:
            json["remove"] = remove
        return await self.request("PATCH", path, json=json)

    async def delete_bot(self, bot_id: str):
        path = f"bots/{bot_id}"
        return await self.request("DELETE", path)

    async def get_public_bot(self, bot_id: str) -> PublicBotPayload:
        path = f"bots/{bot_id}/invite"
        return await self.request("GET", path)

    async def invite_bot(
        self,
        bot_id: str,
        *,
        server_id: Optional[str] = None,
        group_id: Optional[str] = None,
    ):
        if server_id is None and group_id is None:
            raise ValueError("Either server_id or group_id must be provided")
        path = f"bots/{bot_id}/invite"
        json = {}
        if server_id:
            json["server"] = server_id
        if group_id:
            json["group"] = group_id
        return await self.request("POST", path)

    #############
    ## Invites ##
    #############

    async def get_invite(self, invite_id: str) -> InvitePayload:
        path = f"invites/{invite_id}"
        return await self.request("GET", path)

    async def join_invite(self, invite_id: str) -> JoinInvitePayload:
        path = f"invites/{invite_id}"
        return await self.request("POST", path)

    async def delete_invite(self, invite_id: str):
        path = f"invites/{invite_id}"
        return await self.request("DELETE", path)

    ##########
    ## Sync ##
    ##########

    async def get_settings(self, keys: list[str]) -> SettingsPayload:
        path = "sync/settings/fetch"
        json = {"keys": keys}
        return await self.request("POST", path, json=json)

    async def set_settings(self, settings: dict[str, Any]):
        path = "sync/settings/set"
        return await self.request("POST", path, json=settings)

    async def get_unread(self) -> UnreadsPayload:
        path = "sync/unreads"
        return await self.request("GET", path)

    ##############
    ## Web Push ##
    ##############

    async def subscribe_web_push(
        self,
        endpoint: Any,
        p256d: Any,
        auth: Any,
    ):
        path = f"push/subscribe"
        json = {"endpoint": endpoint, "p256d": p256d, "auth": auth}
        return await self.request("PUT", path, json=json)

    async def unsubscribe_web_push(self) -> None:
        path = f"push/unsubscribe"
        return await self.request("POST", path)
