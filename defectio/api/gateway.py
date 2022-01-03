from __future__ import annotations

import asyncio
import logging
from typing import Any
from typing import final
from typing import Optional
from typing import TYPE_CHECKING

import aiohttp
import msgpack
from aiohttp.client import ClientSession
from defectio.backoff import ExponentialBackoff
from defectio.base import gateway
from defectio.errors import GatewayError
from defectio.models import auth

if TYPE_CHECKING:
    from defectio.base.event_manager import EventManager
    from defectio.models import objects
    from defectio.models.auth import Auth
    from defectio.models.channel import TextChannel


__all__ = ["Gateway"]

_logger = logging.getLogger("defectio.gateway")


@final
class Gateway(gateway.Gateway):
    def __init__(
        self,
        *,
        auth: Auth,
        url: str,
        event_manager: EventManager,
        data_format: str = gateway.GatewayDataFormat.MSGPACK,
        user_agent: str = "defectio",
    ) -> None:
        """Initialise Gateway

        Parameters
        ----------
        auth : Auth
            Authentication details
        url : str
            url to Revolt instance for websocket
        event_manager : EventManager
            Manager for events
        data_format : str, optional
            format for connection, by default gateway.GatewayDataFormat.MSGPACK
        """
        if data_format == gateway.GatewayDataFormat.MSGPACK:
            url = url + "?format=msgpack"
            self._send = self._send_msgpack
            self._read = self._read_msgpack
        else:
            url = url + "?format=json"
            self._send = self._send_json
            self._read = self._read_json

        self._closing = asyncio.Event()
        self._closed = asyncio.Event()
        self._event_manager = event_manager
        self._auth = auth
        self._url = url
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._run_task: Optional[asyncio.Task[None]] = None
        self.user_agent = user_agent

    async def _send_json(self, payload: dict[str, Any]) -> None:
        await self._ws.send_json(payload)

    async def _read_json(
        self, payload: aiohttp.http_websocket.WSMessage
    ) -> dict[str, Any]:
        return payload.json()

    async def _send_msgpack(self, payload: dict[str, Any]) -> None:
        payload = msgpack.packb(payload)
        await self._ws.send_bytes(payload)

    async def _read_msgpack(
        self, payload: aiohttp.http_websocket.WSMessage
    ) -> dict[str, Any]:
        return msgpack.unpackb(payload.data)

    async def _wait_for_auth(self) -> bool:
        valid = ["Error", "Authenticated"]
        while True:
            auth_event = await self._ws.receive()
            payload = await self._read(auth_event)
            if payload.get("type") in valid:
                break

        if payload.get("type") != "Authenticated":
            _logger.error("Failed to authenticate with the gateway.")
            raise GatewayError(reason=payload)
        return True

    async def _authenticate(self) -> None:
        payload = {
            "type": "Authenticate",
            **self._auth.payload,
        }
        await self._send(payload)
        try:
            await asyncio.wait_for(self._wait_for_auth(), timeout=10)
        except asyncio.TimeoutError:
            raise GatewayError(reason=str("Timeout error"))
        _logger.info("Websocket authenticated.")

        self.authenticated = True

    async def _received_message(self, msg: aiohttp.http_websocket.WSMessage) -> None:
        payload = await self._read(msg)

        _logger.debug("WebSocket Event: %s %s", msg, payload)

        name = payload.get("type")

        await self._dispatch(name, payload)

    async def _dispatch(self, name: str, data: dict[str, Any]) -> None:
        try:
            await self._event_manager.consume_raw_event(name, data)
        except LookupError:
            self._logger.debug("ignoring unknown event %s:\n    %r", name, data)

    async def close(self) -> None:
        """Close the websocket connection."""
        if not self._closing.is_set():
            if self._ws is not None:
                _logger.debug(
                    "gateway.close() was called and the websocket was still alive."
                )
                await self._ws.close()
            self._closing.set()

    async def start(self) -> None:
        """Start the websocket connection."""
        backoff = ExponentialBackoff()
        self._closed.clear()

        while not self._closed.is_set():
            backoff.delay()
            try:
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
                session = ClientSession()
                self._ws = await session.ws_connect(self._url, **kwargs)
                _logger.debug("Websocket connected to %s", self._url)
                await self._authenticate()

                async for msg in self._ws:
                    await self._received_message(msg)
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                _logger.warning(
                    "Failed to connect to the gateway, attempting a reconnect..."
                )
                continue

            if self._ws.close_code is None:
                _logger.info("Websocket connection closed by the client.")
                return

            _logger.info(
                "Websocket connection closed with code %s, attempting a reconnect...",
                self._ws.close_code,
            )

    async def begin_typing(self, channel: objects.ObjectishOr[TextChannel]) -> None:
        """Begin typing in a channel.

        Parameters
        ----------
        channel : objects.ObjectishOr[TextChannel]
            Channel to begin typing in.
        """
        payload = {"type": "BeginTyping", "channel": channel.id}
        await self._send(payload)

    async def stop_typing(self, channel: objects.ObjectishOr[TextChannel]) -> None:
        """Stop typing in a channel.

        Parameters
        ----------
        channel : objects.ObjectishOr[TextChannel]
            Channel to stop typing in.
        """
        payload = {"type": "StopTyping", "channel": channel.id}
        await self._send(payload)

    async def ping(self) -> None:
        """Send a ping to the gateway."""
        payload = {"type": "Ping"}
        await self._send(payload)
