from __future__ import annotations

import asyncio
import logging
from typing import Any
from typing import TYPE_CHECKING
from typing import Union
from .backoff import ExponentialBackoff

import aiohttp
import aiohttp.http_websocket

import orjson as json
from defectio.errors import LoginFailure

from .types.websocket import Authenticated
from .types.websocket import Error

if TYPE_CHECKING:
    from defectio.client import Client
    from .models import Auth

logger = logging.getLogger("defectio")


class DefectioWebsocket:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        ws_url: str,
        user_agent: str,
        client: Client,
    ) -> None:
        self.session = session
        self.ws_url = ws_url
        self.websocket: aiohttp.ClientWebSocketResponse
        self.user_agent = user_agent
        self._closed = False
        self._dispatch: Client.dispatch = client.dispatch
        self._parsers = client._connection.parsers

        self.auth: Auth
        self.authenticated = False

    @property
    def closed(self) -> bool:
        return self._closed

    async def close(self) -> None:
        if self._closed:
            return        
        elif not self.websocket.closed:
            await self.websocket.close()
            
        self._closed = True
        self.authenticated = False

    async def send_payload(self, payload: Any) -> None:
        await self.websocket.send_str(json.dumps(payload).decode("utf-8"))

    async def wait_for_auth(self) -> Union[Error, Authenticated]:
        response: Union[Error, Authenticated]
        valid = ["Error", "Authenticated"]
        while True:
            auth_event = await self.websocket.receive()
            if auth_event.type == aiohttp.WSMsgType.TEXT:
                payload = json.loads(auth_event.data)
                if payload.get("type") in valid:
                    break
                
        if payload.get("type") == "Error":
            response = Error(payload)
        elif payload.get("type") == "Authenticated":
            response = Authenticated(payload)
        return response

    async def start(self, auth: Auth) -> None:
        backoff = ExponentialBackoff()

        while not self._closed:
            backoff.delay()

            try:
                await self.connect(auth)
            except (aiohttp.ClientError, asyncio.TimeoutError):
                logger.info(
                    "Failed to connect to the gateway, attempting a reconnect..."
                )
                continue

            if self.websocket.close_code is None:
                logger.info("Websocket connection closed by the client.")
                return
            logger.info(
                "Websocket connection closed with code %s, attempting a reconnect...",
                self.websocket.close_code,
            )

    async def send_authenticate(self) -> None:
        payload = {
            "type": "Authenticate",
            **self.auth.payload,
        }
        await self.send_payload(payload)
        try:
            authenticated = await asyncio.wait_for(self.wait_for_auth(), timeout=10)
        except asyncio.TimeoutError:
            authenticated = Error({"type": "InternalError", "error": "timeout"})
        if authenticated["type"] != "Authenticated":
            logger.error("Authentication failed.")
            raise LoginFailure(authenticated)
        self.authenticated = True

    async def connect(self, auth: Auth) -> None:
        self.auth = auth
        kwargs = {
            "max_msg_size": 0,
            "timeout": 30.0,
            "autoclose": False,
            "headers": {
                "User-Agent": self.user_agent,
            },
            "compress": 0,
            "heartbeat": 15.0,
        }
        self.websocket = await self.session.ws_connect(self.ws_url, **kwargs)
        logger.debug("Websocket connected to %s", self.ws_url)

        await self.send_authenticate()

        async for msg in self.websocket:
            await self.received_message(msg)

    async def received_message(self, msg: aiohttp.http_websocket.WSMessage) -> None:
        payload = json.loads(msg.data)

        logger.debug("WebSocket Event: %s", msg)
        event = payload.get("type").lower()
        if event:
            self._dispatch("socket_event_type", event)

        try:
            func = self._parsers[event]
        except KeyError:
            logger.debug("Unknown event %s.", event)
        else:
            await func(payload)

    async def begin_typing(self, channel: str) -> None:
        payload = {"type": "BeginTyping", "channel": channel}
        await self.send_payload(payload)

    async def stop_typing(self, channel: str) -> None:
        payload = {"type": "StopTyping", "channel": channel}
        await self.send_payload(payload)

    async def ping(self) -> None:
        payload = {"type": "Ping"}
        await self.send_payload(payload)
