from aiohttp.client import ClientSession
from defectio.errors import LoginFailure, Authenticated, Error
from typing import Optional, TYPE_CHECKING, Any, Union, final
from defectio.base import gateway
import asyncio
import aiohttp
import logging
from defectio.backoff import ExponentialBackoff
import msgpack

if TYPE_CHECKING:
    from defectio.base.event_manager import EventManager
    from defectio.models import objects
    from defectio.models.auth import Auth
    from defectio.models.channel import TextChannel


_logger = logging.getLogger("defectio.gateway")


@final
class Gateway(gateway.Gateway):
    def __init__(
        self,
        *,
        data_format: str = gateway.GatewayDataFormat.JSON,
        event_manager: EventManager,
        auth: Auth,
        url: str,
    ) -> None:
        if data_format == gateway.GatewayDataFormat.MSGPACK:
            # TODO: fix msgpack
            url = url + "?format=msgpack"
            self._send = self.send_msgpack
            self._read = self.read_msgpack
        elif data_format == gateway.GatewayDataFormat.JSON:
            self._send = self.send_json
            self._read = self._read
        else:
            raise NotImplementedError(f"Unsupported gateway data format: {data_format}")
        self._closing = asyncio.Event()
        self._closed = asyncio.Event()
        self._event_manager = event_manager
        self._auth = auth
        self._url = url
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._run_task: Optional[asyncio.Task[None]] = None

    async def send_json(self, payload: dict[str, Any]) -> None:
        await self._ws.send_json(payload)

    async def read_json(
        self, payload: aiohttp.http_websocket.WSMessage
    ) -> dict[str, Any]:
        return await payload.json()

    async def send_msgpack(self, payload: dict[str, Any]) -> None:
        payload = msgpack.packb(payload)
        await self._ws.send_bytes(payload)

    async def read_msgpack(
        self, payload: aiohttp.http_websocket.WSMessage
    ) -> dict[str, Any]:
        data = await payload.read()
        return msgpack.unpackb(data)

    async def close(self) -> None:
        if not self._closing.is_set():
            if self._ws is not None:
                _logger.debug(
                    "gateway.close() was called and the websocket was still alive."
                )
                await self._ws.close()
            self._closing.set()

    async def start(self) -> None:
        backoff = ExponentialBackoff()

        while not self._closed:
            backoff.delay()
            try:
                kwargs = {
                    "max_msg_size": 0,
                    "timeout": 30.0,
                    "autoclose": False,
                    # "headers": {
                    #     "User-Agent": self.user_agent,
                    # },
                    "compress": 0,
                    "heartbeat": 15.0,
                }
                session = ClientSession()
                self._ws = await session.ws_connect(self._ws_url, **kwargs)
                _logger.debug("Websocket connected to %s", self._ws_url)

                await self._authenticate()

                async for msg in self._ws:
                    await self._received_message(msg)
            except (aiohttp.ClientError, asyncio.TimeoutError):
                _logger.info(
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
        payload = {"type": "BeginTyping", "channel": channel}
        await self._send(payload)

    async def stop_typing(self, channel: objects.ObjectishOr[TextChannel]) -> None:
        payload = {"type": "StopTyping", "channel": channel}
        await self._send(payload)

    async def ping(self) -> None:
        payload = {"type": "Ping"}
        await self._send(payload)

    async def _wait_for_auth(self) -> Union[Error, Authenticated]:
        valid = ["Error", "Authenticated"]
        while True:
            auth_event = await self._ws.receive()
            if auth_event.type == aiohttp.WSMsgType.TEXT:
                payload = await self._read(auth_event)
                if payload.get("type") in valid:
                    break

        response: Union[Error, Authenticated]
        if payload.get("type") == "Error":
            response = Error(payload)
        elif payload.get("type") == "Authenticated":
            response = Authenticated(payload)
        return response

    async def _authenticate(self) -> None:
        payload = {
            "type": "Authenticate",
            **self._auth.payload,
        }
        await self._send(payload)
        try:
            authenticated = await asyncio.wait_for(self._wait_for_auth(), timeout=10)
        except asyncio.TimeoutError:
            authenticated = Error({"type": "InternalError", "error": "timeout"})
        if authenticated["type"] != "Authenticated":
            _logger.error("Authentication failed.")
            raise LoginFailure(authenticated)
        self.authenticated = True

    async def _received_message(self, msg: aiohttp.http_websocket.WSMessage) -> None:
        payload = await self._read(msg)

        _logger.debug("WebSocket Event: %s", msg)

        name = payload.get("type")

        await self._dispatch(name, payload)

    def _dispatch(self, name: str, data: dict[str, Any]) -> None:
        try:
            self._event_manager.consume_raw_event(name, self, data)
        except LookupError:
            self._logger.debug("ignoring unknown event %s:\n    %r", name, data)
