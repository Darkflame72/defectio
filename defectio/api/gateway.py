from aiohttp.client import ClientSession
from defectio.models.channel import TextChannel
from defectio.errors import LoginFailure
from defectio.types.websocket import Authenticated, Error
from defectio.models.auth import Auth
import typing
from defectio.base import gateway
import asyncio
import aiohttp
import logging
from defectio.backoff import ExponentialBackoff
from defectio.models import objects
import msgpack


_logger = logging.getLogger("defectio.gateway")


@typing.final
class Gateway(gateway.Gateway):
    def __init__(
        self,
        *,
        data_format: str = gateway.GatewayDataFormat.JSON,
        # TODO: add event manager
        # event_manager: event_manager_.EventManager,
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
        # self._event_manager = event_manager
        self._auth = auth
        self._url = url
        self._ws: typing.Optional[aiohttp.ClientWebSocketResponse] = None
        self._run_task: typing.Optional[asyncio.Task[None]] = None

    async def send_json(self, payload: dict[str, typing.Any]) -> None:
        await self._ws.send_json(payload)

    async def read_json(
        self, payload: aiohttp.http_websocket.WSMessage
    ) -> dict[str, typing.Any]:
        return await payload.json()

    async def send_msgpack(self, payload: dict[str, typing.Any]) -> None:
        payload = msgpack.packb(payload)
        await self._ws.send_bytes(payload)

    async def read_msgpack(
        self, payload: aiohttp.http_websocket.WSMessage
    ) -> dict[str, typing.Any]:
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

    async def _wait_for_auth(self) -> typing.Union[Error, Authenticated]:
        response: typing.Union[Error, Authenticated]
        valid = ["Error", "Authenticated"]
        while True:
            auth_event = await self._ws.receive()
            if auth_event.type == aiohttp.WSMsgType.TEXT:
                payload = await self._read(auth_event)
                if payload.get("type") in valid:
                    break

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

        name = payload.get("type").lower()
        await self._dispatch(name, payload)

    def _dispatch(self, name: str, data: dict[str, typing.Any]) -> None:
        try:
            self._event_manager.consume_raw_event(name, self, data)
        except LookupError:
            self._logger.debug("ignoring unknown event %s:\n    %r", name, data)
