from __future__ import annotations

__all__ = [
    "RESTApp",
    "RESTClient",
]

import asyncio
import logging
from typing import Any
from typing import final
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union, NoReturn
import typing

import aiohttp
from defectio.base import rest

# from defectio.errors import Authenticated
# from defectio.errors import Error
# from defectio.errors import LoginFailure

if TYPE_CHECKING:
    from defectio.base.event_manager import EventManager
    from defectio.models import objects
    from defectio.models.auth import Auth
    from defectio.models.channel import TextChannel
    import concurrent.futures
    from defectio import config


_logger = logging.getLogger("defectio.rest")


class RESTApp:
    def __init__(
        self,
        *,
        executor: Optional[concurrent.futures.Executor] = None,
        http_settings: Optional[config.HTTPSettings] = None,
        max_rate_limit: float = 300,
        max_retries: int = 3,
        proxy_settings: Optional[config.ProxySettings] = None,
        url: Optional[str] = None,
    ) -> None:
        self._http_settings = (
            config.HTTPSettings() if http_settings is None else http_settings
        )
        self._proxy_settings = (
            config.ProxySettings() if proxy_settings is None else proxy_settings
        )
        self._executor = executor
        self._max_rate_limit = max_rate_limit
        self._max_retries = max_retries
        self._url = url

    @property
    def executor(self) -> Optional[concurrent.futures.Executor]:
        return self._executor

    @property
    def http_settings(self) -> config.HTTPSettings:
        return self._http_settings

    @property
    def proxy_settings(self) -> config.ProxySettings:
        return self._proxy_settings

    def acquire(
        self,
        auth: Optional[Auth] = None,
    ) -> RESTClient:
        """Acquire an instance of this REST client.

        .. note
            The returned REST client should be started before it can be used,
            either by calling `RESTClient.start` or by using it as an
            asynchronous context manager.

        Examples
        --------
        ```py
        auth = Auth(token="...", bot=False)
        rest_app = RESTApp()

        # Using the returned client as a context manager to implicitly start
        # and stop it.
        async with rest_app.acquire(auth) as client:
            user = await client.fetch_my_user()
        ```

        Parameters
        ----------
        token : Optional[Auth]
            The bot or bearer token. If no token is to be used,
            this can be undefined.

        Returns
        -------
        RESTClientImpl
            An instance of the REST client.

        Raises
        ------
        builtins.ValueError
            If `token_type` is provided when a token strategy is passed for `token`.
        """
        # Since we essentially mimic a fake App instance, we need to make a circular provider.
        # We can achieve this using a lambda. This allows the entity factory to build models that
        # are also REST-aware
        provider = _RESTProvider(
            lambda: entity_factory, self._executor, lambda: rest_client
        )
        entity_factory = entity_factory.EntityFactoryImpl(provider)

        rest_client = RESTClient(
            cache=None,
            entity_factory=entity_factory,
            executor=self._executor,
            http_settings=self._http_settings,
            max_rate_limit=self._max_rate_limit,
            max_retries=self._max_retries,
            proxy_settings=self._proxy_settings,
            auth=auth,
            rest_url=self._url,
        )

        return rest_client


class _LiveAttributes:
    """Fields which are only present within `RESTClient` while it's "alive".

    .. note
        This must be started within an active asyncio event loop.
    """

    client_session: aiohttp.ClientSession
    closed_event: asyncio.Event
    tcp_connector: aiohttp.TCPConnector
    is_closing: bool = False

    @classmethod
    def build(
        cls,
        max_rate_limit: float,
        http_settings: config.HTTPSettings,
        proxy_settings: config.ProxySettings,
    ) -> _LiveAttributes:
        """Build a live attributes object.

        .. warning
            This can only be called when the current thread has an active
            asyncio loop.
        """
        # This asserts that this is called within an active event loop.
        asyncio.get_running_loop()
        tcp_connector = net.create_tcp_connector(http_settings)
        _logger.info("acquired new tcp connector")
        client_session = net.create_client_session(
            connector=tcp_connector,
            # No, this is correct. We manage closing the connector ourselves in this class.
            # This works around some other lifespan issues.
            connector_owner=False,
            http_settings=http_settings,
            raise_for_status=False,
            trust_env=proxy_settings.trust_env,
        )
        _logger.info("acquired new aiohttp client session")
        return _LiveAttributes(
            client_session=client_session,
            closed_event=asyncio.Event(),
            tcp_connector=tcp_connector,
        )

    async def close(self) -> None:
        self.is_closing = True
        self.closed_event.set()
        await self.client_session.close()
        await self.tcp_connector.close()

    def still_alive(self) -> _LiveAttributes:
        """Chained method used to Check if `close` has been called before using this object's resources."""
        if self.is_closing:
            raise RuntimeError("The REST client was closed mid-request")

        return self


class RESTClient(rest.RESTClient):
    def __init__(
        self,
        *,
        cache: Optional[cache_api.MutableCache],
        entity_factory: entity_factory_.EntityFactory,
        executor: Optional[concurrent.futures.Executor],
        http_settings: config.HTTPSettings,
        max_rate_limit: float,
        max_retries: int = 3,
        proxy_settings: config.ProxySettings,
        auth: Optional[Auth],
        rest_url: typing.Optional[str],
    ) -> None:

        self._cache = cache
        self._entity_factory = entity_factory
        self._executor = executor
        self._http_settings = http_settings
        # self._live_attributes: Optional[_LiveAttributes] = None
        self._max_rate_limit = max_rate_limit
        self._max_retries = max_retries
        self._proxy_settings = proxy_settings
        self._auth = auth

        self._rest_url = rest_url if rest_url is not None else "https://api.revolt.chat"

    @property
    def is_alive(self) -> bool:
        return self._live_attributes is not None

    @property
    def http_settings(self) -> config.HTTPSettings:
        return self._http_settings

    @property
    def proxy_settings(self) -> config.ProxySettings:
        return self._proxy_settings

    @final
    async def close(self) -> None:
        """Close the HTTP client and any open HTTP connections."""
        live_attributes = self._get_live_attributes()
        self._live_attributes = None
        await live_attributes.close()

        # We have to sleep to allow aiohttp time to close SSL transports...
        # https://github.com/aio-libs/aiohttp/issues/1925
        # https://docs.aiohttp.org/en/stable/client_advanced.html#graceful-shutdown
        #
        # TODO: Remove when we update to aiohttp 4.0.0
        # https://github.com/aio-libs/aiohttp/issues/1925#issuecomment-715977247
        await asyncio.sleep(0.25)

    @final
    def start(self) -> None:
        """Start the HTTP client.

        .. note
            This must be called within an active event loop.

        Raises
        ------
        RuntimeError
            If this is called in an environment without an active event loop.
        """
        if self._live_attributes:
            raise RuntimeError("Cannot start a REST Client which is already alive")

        self._live_attributes = _LiveAttributes.build(
            self._max_rate_limit, self._http_settings, self._proxy_settings
        )

    def _get_live_attributes(self) -> _LiveAttributes:
        if self._live_attributes:
            return self._live_attributes

        raise RuntimeError("Cannot use an inactive REST client")

    async def __aenter__(self) -> RESTClient:
        self.start()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[BaseException],
        exc_val: Optional[BaseException],
        exc_tb,
    ) -> None:
        await self.close()

    @final
    async def _request(
        self,
        compiled_route: routes.CompiledRoute,
        *,
        query: typing.Optional[data_binding.StringMapBuilder] = None,
        form: typing.Optional[aiohttp.FormData] = None,
        json: typing.Union[
            data_binding.JSONObjectBuilder, data_binding.JSONArray, None
        ] = None,
        reason: Optional[str] = None,
        no_auth: bool = False,
        auth: typing.Optional[str] = None,
    ) -> typing.Union[None, data_binding.JSONObject, data_binding.JSONArray]:
        # Make a ratelimit-protected HTTP request to a JSON endpoint and expect some form
        # of JSON response.
        live_attributes = self._get_live_attributes()
        headers = data_binding.StringMapBuilder()
        headers.setdefault(_USER_AGENT_HEADER, _HTTP_USER_AGENT)

        retried = False
        token: typing.Optional[str] = None
        if auth:
            headers[_AUTHORIZATION_HEADER] = auth

        elif not no_auth:
            if isinstance(self._token, str):
                headers[_AUTHORIZATION_HEADER] = self._token

            elif self._token is not None:
                token = await self._token.acquire(self)
                headers[_AUTHORIZATION_HEADER] = token

        headers.put(_X_AUDIT_LOG_REASON_HEADER, reason)

        url = compiled_route.create_url(self._rest_url)

        # This is initiated the first time we hit a 5xx error to save memory when nothing goes wrong
        backoff: typing.Optional[rate_limits.ExponentialBackOff] = None
        retries_done = 0

        while True:
            try:
                uuid = time.uuid()
                async with live_attributes.still_alive().buckets.acquire(
                    compiled_route
                ):
                    # Buckets not using authentication still have a global
                    # rate limit, but it is different from the token one.
                    if not no_auth:
                        await live_attributes.still_alive().global_rate_limit.acquire()

                    if _LOGGER.isEnabledFor(ux.TRACE):
                        _LOGGER.log(
                            ux.TRACE,
                            "%s %s %s\n%s",
                            uuid,
                            compiled_route.method,
                            url,
                            self._stringify_http_message(headers, json),
                        )
                        start = time.monotonic()

                    # Make the request.
                    response = (
                        await live_attributes.still_alive().client_session.request(
                            compiled_route.method,
                            url,
                            headers=headers,
                            params=query,
                            json=json,
                            data=form,
                            allow_redirects=self._http_settings.max_redirects
                            is not None,
                            max_redirects=self._http_settings.max_redirects,
                            proxy=self._proxy_settings.url,
                            proxy_headers=self._proxy_settings.all_headers,
                        )
                    )

                    if _LOGGER.isEnabledFor(ux.TRACE):
                        time_taken = (time.monotonic() - start) * 1_000
                        _LOGGER.log(
                            ux.TRACE,
                            "%s %s %s in %sms\n%s",
                            uuid,
                            response.status,
                            response.reason,
                            time_taken,
                            self._stringify_http_message(
                                response.headers, await response.read()
                            ),
                        )

                    # Ensure we are not rate limited, and update rate limiting headers where appropriate.
                    await self._parse_ratelimits(
                        compiled_route, response, live_attributes
                    )

                # Don't bother processing any further if we got NO CONTENT. There's not anything
                # to check.
                if response.status == http.HTTPStatus.NO_CONTENT:
                    return None

                # Handle the response.
                if 200 <= response.status < 300:
                    if response.content_type == _APPLICATION_JSON:
                        # Only deserializing here stops Cloudflare shenanigans messing us around.
                        return data_binding.load_json(await response.read())

                    real_url = str(response.real_url)
                    raise errors.HTTPError(
                        f"Expected JSON [{response.content_type=}, {real_url=}]"
                    )

                # Handling 5xx errors
                if (
                    response.status in _RETRY_ERROR_CODES
                    and retries_done < self._max_retries
                ):
                    if backoff is None:
                        backoff = rate_limits.ExponentialBackOff(
                            maximum=_MAX_BACKOFF_DURATION
                        )

                    sleep_time = next(backoff)
                    _LOGGER.warning(
                        "Received status %s on request, backing off for %.2fs and retrying. Retries remaining: %s",
                        response.status,
                        sleep_time,
                        self._max_retries - retries_done,
                    )
                    retries_done += 1

                    await asyncio.sleep(sleep_time)
                    raise self._RetryRequest

                can_re_auth = response.status == 401 and not (
                    auth or no_auth or retried
                )
                if can_re_auth and isinstance(self._token, rest_api.TokenStrategy):
                    assert token is not None
                    self._token.invalidate(token)
                    token = await self._token.acquire(self)
                    headers[_AUTHORIZATION_HEADER] = token
                    retried = True
                    continue

                await self._handle_error_response(response)

            except self._RetryRequest:
                continue

    @staticmethod
    @final
    def _stringify_http_message(headers: data_binding.Headers, body: typing.Any) -> str:
        string = "\n".join(
            f"    {name}: {value}"
            if name != _AUTHORIZATION_HEADER
            else f"    {name}: **REDACTED TOKEN**"
            for name, value in headers.items()
        )

        if body is not None:
            string += "\n\n    "
            string += body.decode("ascii") if isinstance(body, bytes) else str(body)

        return string

    @staticmethod
    @final
    async def _handle_error_response(
        response: aiohttp.ClientResponse,
    ) -> NoReturn:
        raise await net.generate_error_response(response)
