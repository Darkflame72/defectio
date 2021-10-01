from __future__ import annotations

import asyncio
import logging
import signal
import sys
import traceback
from typing import Any
from typing import Callable
from typing import Coroutine
from typing import Optional
from typing import TYPE_CHECKING
from typing import TypeVar, Sequence

import aiohttp
from defectio.models.auth import Auth
from defectio.models.user import ClientUser
from defectio import utils
from .models import Message

from . import __version__
from .gateway import DefectioWebsocket
from .http import DefectioHTTP
from .models import User
from .state import ConnectionState

if TYPE_CHECKING:
    from .models import Channel, Server

__all__ = ("Client",)

Coro = TypeVar("Coro", bound=Callable[..., Coroutine[Any, Any, Any]])

logger = logging.getLogger("defectio")


def _cancel_tasks(loop: asyncio.AbstractEventLoop) -> None:
    tasks = {t for t in asyncio.all_tasks(loop=loop) if not t.done()}

    if not tasks:
        return

    logger.info("Cleaning up after %d tasks.", len(tasks))
    for task in tasks:
        task.cancel()

    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    logger.info("All tasks finished cancelling.")

    for task in tasks:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler(
                {
                    "message": "Unhandled exception during Client.run shutdown.",
                    "exception": task.exception(),
                    "task": task,
                }
            )


def _cleanup_loop(loop: asyncio.AbstractEventLoop) -> None:
    try:
        _cancel_tasks(loop)
        loop.run_until_complete(loop.shutdown_asyncgens())
    finally:
        logger.info("Closing the event loop.")
        loop.close()


class Client:
    def __init__(
        self,
        *,
        api_url: Optional[str] = "https://api.revolt.chat",
        loop: Optional[asyncio.AbstractEventLoop] = None,
        **kwargs: Any,
    ) -> None:
        """Creates a new client.

        Parameters
        ----------
        api_url : Optional[str], optional
            url to revolt instance, by default "https://api.revolt.chat"
        loop : Optional[asyncio.AbstractEventLoop], optional
            asyncio event loop to use otherwise it is grabbed, by default None
        """

        self.api_url: str = api_url
        self.loop: asyncio.AbstractEventLoop = (
            asyncio.get_event_loop() if loop is None else loop
        )

        self.websocket: DefectioWebsocket = None
        self.http: DefectioHTTP = None
        self.session = kwargs.pop("session", None)

        self._handlers: dict[str, Callable] = {"ready": self._handle_ready}
        self._listeners: list[
            str, list[tuple[asyncio.Future, Callable[..., bool]]]
        ] = {}

        self._ready = asyncio.Event()
        self._closed = True
        self._auth: Optional[Auth] = None
        self._connection: ConnectionState = self._get_state(**kwargs)

    def _get_state(self, **options: Any) -> ConnectionState:
        """Returns the connection state.

        Returns
        -------
        ConnectionState
            The connection state.
        """
        return ConnectionState(
            dispatch=self.dispatch,
            handlers=self._handlers,
            http=self.get_http,
            websocket=self.get_websocket,
            auth=self.get_auth,
            loop=self.loop,
            **options,
        )

    def _handle_ready(self) -> None:
        """Handles the ready event."""
        self._ready.set()

    async def _run_event(
        self,
        coro: Callable[..., Coroutine[Any, Any, Any]],
        event_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Runs an event.

        Parameters
        ----------
        coro : Callable[..., Coroutine[Any, Any, Any]]
            The coroutine to run.
        event_name : str
            The name of the event to run.
        """
        try:
            await coro(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except Exception:
            try:
                await self.on_error(event_name, *args, **kwargs)
            except asyncio.CancelledError:
                pass

    def _schedule_event(
        self,
        coro: Callable[..., Coroutine[Any, Any, Any]],
        event_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> asyncio.Task:
        """Schedules an event to be run.

        Parameters
        ----------
        coro : Callable[..., Coroutine[Any, Any, Any]]
            The coroutine to run.
        event_name : str
            The name of the event to run.

        Returns
        -------
        asyncio.Task
            The task that the event was scheduled for.
        """
        wrapped = self._run_event(coro, event_name, *args, **kwargs)
        # Schedules the task
        return asyncio.create_task(wrapped, name=f"defectio: {event_name}")

    def dispatch(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Dispatch an event

        Parameters
        ----------
        event : str
            The event to dispatch.
        """
        logger.debug("Dispatching event %s", event)
        method = "on_" + event
        listeners = self._listeners.get(event)
        if listeners:
            removed = []
            for i, (future, condition) in enumerate(listeners):
                if future.cancelled():
                    removed.append(i)
                    continue

                try:
                    result = condition(*args)
                except Exception as exc:
                    future.set_exception(exc)
                    removed.append(i)
                else:
                    if result:
                        if len(args) == 0:
                            future.set_result(None)
                        elif len(args) == 1:
                            future.set_result(args[0])
                        else:
                            future.set_result(args)
                        removed.append(i)

            if len(removed) == len(listeners):
                self._listeners.pop(event)
            else:
                for idx in reversed(removed):
                    del listeners[idx]
        try:
            coro = getattr(self, method)
        except AttributeError:
            pass
        else:
            self._schedule_event(coro, method, *args, **kwargs)

    async def on_error(self, event_method: str, *args: Any, **kwargs: Any) -> None:
        """|coro|
        The default error handler provided by the client.
        By default this prints to :data:`sys.stderr` however it could be
        overridden to have a different implementation.
        """
        print(f"Ignoring exception in {event_method}", file=sys.stderr)
        traceback.print_exc()

    async def wait_until_ready(self) -> None:
        """|coro|
        Waits until the client's internal cache is all ready.
        """
        await self._ready.wait()

    def wait_for(
        self,
        event: str,
        *,
        check: Optional[Callable[..., bool]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """Waits for a specific event to be dispatched.

        Parameters
        ----------
        event : str
            The event to wait for.
        check : Optional[Callable[..., bool]], optional
            A check to run on the event, by default None
        timeout : Optional[float], optional
            timeout to wait, by default None

        Returns
        -------
        Any
            response from method
        """
        future = self.loop.create_future()
        if check is None:

            def _check(*args):
                return True

            check = _check

        ev = event.lower()
        try:
            listeners = self._listeners[ev]
        except KeyError:
            listeners = []
            self._listeners[ev] = listeners

        listeners.append((future, check))
        return asyncio.wait_for(future, timeout)

        # event registration

    def event(self, coro: Coro) -> Coro:
        """A decorator that registers an event to listen to.

        Example
        ---------

        .. code-block:: python3

            @client.event
            async def on_ready():
                print('Ready!')

        Raises
        --------
        TypeError
            The coroutine passed is not actually a coroutine.
        """

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("event registered must be a coroutine function")

        setattr(self, coro.__name__, coro)
        logger.debug("%s has successfully been registered as an event", coro.__name__)
        return coro

    ################
    ## Properties ##
    ################

    @property
    def user(self) -> Optional[ClientUser]:
        """Optional[:class:`.ClientUser`]: Represents the connected client. ``None`` if not logged in."""
        return self._connection.user

    @property
    def users(self) -> list[User]:
        """Returns a list of all the users stored in the internal cache.

        Returns
        -------
        list[User]
            A list of cached users.
        """
        return list(self._connection._users.values())

    @property
    def cached_messages(self) -> Sequence[Message]:
        """Sequence[:class:`.Message`]: Read-only list of messages the connected client has cached.
        .. versionadded:: 1.1
        """
        return utils.SequenceProxy(self._connection._messages or [])

    @property
    def servers(self) -> list[Server]:
        """Returns a list of all the servers stored in the internal cache.

        Returns
        -------
        list[Server]
            A list of cached servers.
        """
        return list(self._connection._servers.values())

    @property
    def channels(self) -> list[Channel]:
        """Returns a list of all the channels stored in the internal cache.

        Returns
        -------
        list[Channel]
            [A list of cached channels
        """
        return list(self._connection._server_channels.values())

    def get_auth(self) -> Auth:
        """Returns the Auth object used for logging in."""
        return self._auth

    def get_http(self) -> DefectioHTTP:
        return self.http

    def get_websocket(self) -> DefectioWebsocket:
        return self.websocket

    #############
    ## Getters ##
    #############

    def get_channel(self, channel_id: str) -> Optional[Channel]:
        """Get a channel with the specified ID from the internal cache.

        Parameters
        ----------
        channel_id : str
            The channel ID to look for.

        Returns
        -------
        Optional[Channel]
            The requested channel. If not found, returns ``None``.
        """
        channel = self._connection.get_channel(channel_id)
        return channel

    def get_server(self, server_id: str) -> Optional[Server]:
        """Get a server with the specified ID from the internal cache.

        Parameters
        ----------
        server_id : str
            The server ID to look for.

        Returns
        -------
        Optional[Server]
            The requested server. If not found, returns ``None``.
        """
        server = self._connection.get_server(server_id)
        return server

    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user with the specified ID from the internal cache.

        Parameters
        ----------
        user_id : str
            The user ID to look for.

        Returns
        -------
        Optional[User]
            The requested user. If not found, returns ``None``.
        """
        user = self._connection.get_user(user_id)
        return user

    async def fetch_channel(self, channel_id: str) -> Optional[Channel]:
        """Fetches a channel from revolt bypassing the internal cache.

        This should be used if you beleive the cache may be stale but
        it is recommended to use :meth:`get_channel` instead.

        Parameters
        ----------
        channel_id : str
            The channel ID to look for.

        Returns
        -------
        Optional[Channel]
            The requested channel. If not found, returns ``None``.
        """
        channel = await self._connection.http.get_channel(channel_id)
        if channel:
            channel = self._connection._add_channel_from_data(channel)
        return channel

    async def fetch_server(self, server_id: str) -> Optional[Server]:
        """Fetches a server from revolution bypassing the internal cache.

        This should be used if you beleive the cache may be stale but
        it is recommended to use :meth:`get_server` instead.

        Parameters
        ----------
        server_id : str
            The server ID to look for.

        Returns
        -------
        Optional[Server]
            The requested server. If not found, returns ``None``.
        """
        server = await self._connection.http.get_server(server_id)
        if server:
            server = self._connection._add_server_from_data(server)
        return server

    async def fetch_user(self, user_id: str) -> Optional[User]:
        """Fetches a user from revolution bypassing the internal cache.

        This should be used if you beleive the cache may be stale but
        it is recommended to use :meth:`get_user` instead.

        Parameters
        ----------
        user_id : str
            The user ID to look for.

        Returns
        -------
        Optional[User]
            The requested user. If not found, returns ``None``.
        """
        user = await self._connection.http.get_user(user_id)
        if user:
            user = self._connection._add_user_from_data(user)
        return user

    ######################
    ## State Management ##
    ######################

    def is_closed(self):
        """Indicates if the websocket connection is closed."""
        return self.websocket.closed and self.session.closed

    async def close(self) -> None:
        """|coro|
        Closes the connection to revolt.
        """
        if self._closed:
            return

        self._closed = True
        if self.websocket is not None:
            await self.websocket.close()

        if self.session is not None:
            await self.session.close()

    async def create(self) -> None:
        """|coro|
        Creates the client with the cache, websocket and http client.
        """
        user_agent = "Defectio (https://github.com/Darkflame72/defectio {0}) Python/{1[0]}.{1[1]} aiohttp/{2}".format(
            __version__, sys.version_info, aiohttp.__version__
        )
        self.session = aiohttp.ClientSession()
        self.http = DefectioHTTP(self.session, self.api_url, user_agent)
        api_info = await self.http.node_info()
        api_info = self._connection.set_api_info(api_info)
        self.api_info = api_info
        self.websocket = DefectioWebsocket(
            self.session, api_info.ws_url, user_agent, self
        )

    async def connect(self) -> None:
        self._closed = False

    async def login(self, token: str, bot: bool = True) -> None:
        """|coro|
        Logs in using the token provided as a bot.

        Parameters
        ----------
        token : str
            The authentication token.
        """
        self._auth = self.http.start(token, bot=bot)
        await self.websocket.start(self._auth)

    async def start(
        self,
        *,
        token: Optional[str] = None,
        bot: bool = True,
    ) -> None:
        """|coro|
        Creates a client and logs the user in.

        Parameters
        ----------
        token : Optional[str]
            The Revolt API token.

        session_token : Optional[str]
            The Revolt session ID of a user

        user_id : Optional[str]
            The ID of the user which th session token belongs to
        """
        await self.create()
        await self.login(token, bot=bot)
        await self.connect()

    def run(self, token: Optional[str] = None, *, bot: bool = True) -> None:
        """A blocking call that abstracts away the event loop
        initialisation from you.

        If you want more control over the event loop then this
        function should not be used. Use :meth:`start` coroutine
        or :meth:`connect` + :meth:`login`.

        Roughly Equivalent to: ::

            try:
                loop.run_until_complete(start(*args, **kwargs))
            except KeyboardInterrupt:
                loop.run_until_complete(close())
                # cancel all tasks lingering
            finally:
                loop.close()

        .. warning::
            This function must be the last function to call due to the fact that it
            is blocking. That means that registration of events or anything being
            called after this function call will not execute until it returns.

        Parameters
        -----------
        token: Optional[:class:`str`]
            The authentication token of the bot to login.

        bot: bool
            Indicates if the client is a bot account. Defaults to ``True``.

        """
        loop = self.loop

        try:
            loop.add_signal_handler(signal.SIGINT, loop.stop)
            loop.add_signal_handler(signal.SIGTERM, loop.stop)
        except NotImplementedError:
            pass

        async def runner() -> None:
            try:
                await self.start(token=token, bot=bot)
            finally:
                if not self.is_closed():
                    await self.close()

        def stop_loop_on_completion(f):
            loop.stop()

        future = asyncio.ensure_future(runner(), loop=loop)
        future.add_done_callback(stop_loop_on_completion)

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            logger.info("Received signal to terminate bot and event loop.")
        finally:
            future.remove_done_callback(stop_loop_on_completion)
            logger.info("Cleaning up tasks.")
            _cleanup_loop(loop)
