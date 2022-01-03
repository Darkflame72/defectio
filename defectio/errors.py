"""Exceptions and warnings that can be thrown by this library."""
from __future__ import annotations

__all__: typing.List[str] = [
    "DefectioError",
    "DefectioWarning",
    "DefectioInterrupt",
    "ComponentStateConflictError",
    "UnrecognisedEntityError",
    "NotFoundError",
    "RateLimitedError",
    "RateLimitTooLongError",
    "UnauthorizedError",
    "ForbiddenError",
    "BadRequestError",
    "HTTPError",
    "HTTPResponseError",
    "ClientHTTPResponseError",
    "InternalServerError",
    "GatewayConnectionError",
    "GatewayServerClosedConnectionError",
    "GatewayError",
    "MissingIntentWarning",
    "MissingIntentError",
    "BulkDeleteError",
    "VoiceError",
]

import http
import typing

import attr


@attr.define(auto_exc=True, repr=False, init=False, weakref_slot=False)
class DefectioError(RuntimeError):
    """Base for an error raised by this API.

    Any exceptions should derive from this.

    .. warning
        You should never initialize this exception directly.
    """


@attr.define(auto_exc=True, repr=False, init=False, weakref_slot=False)
class DefectioWarning(RuntimeWarning):
    """Base for a warning raised by this API.

    Any warnings should derive from this.

    .. warning
        You should never initialize this warning directly.
    """


@attr.define(auto_exc=True, repr=False, weakref_slot=False)
class DefectioInterrupt(KeyboardInterrupt, DefectioError):
    """Exception raised when a kill signal is handled internally."""

    signum: int = attr.field()
    """The signal number that was raised."""

    signame: str = attr.field()
    """The signal name that was raised."""


@attr.define(auto_exc=True, repr=False, weakref_slot=False)
class ComponentStateConflictError(DefectioError):
    """Exception thrown when an action cannot be executed in the component's current state.

    Dependent on context this will be thrown for components which are already
    running or haven't been started yet.
    """

    reason: str = attr.field()
    """A string to explain the issue."""

    def __str__(self) -> str:
        return self.reason


@attr.define(auto_exc=True, repr=False, weakref_slot=False)
class UnrecognisedEntityError(DefectioError):
    """An exception thrown when an unrecognised entity is found."""

    reason: str = attr.field()
    """A string to explain the issue."""

    def __str__(self) -> str:
        return self.reason


@attr.define(auto_exc=True, repr=False, weakref_slot=False)
class GatewayError(DefectioError):
    """A base exception type for anything that can be thrown by the Gateway."""

    reason: str = attr.field()
    """A string to explain the issue."""

    def __str__(self) -> str:
        return self.reason


@attr.define(auto_exc=True, repr=False, weakref_slot=False)
class GatewayConnectionError(GatewayError):
    """An exception thrown if a connection issue occurs."""

    def __str__(self) -> str:
        return f"Failed to connect to server: {self.reason!r}"


@attr.define(auto_exc=True, repr=False, weakref_slot=False)
class HTTPError(DefectioError):
    """Base exception raised if an HTTP error occurs while making a request."""

    message: str = attr.field()
    """The error message."""


@attr.define(auto_exc=True, repr=False, weakref_slot=False)
class HTTPResponseError(HTTPError):
    """Base exception for an erroneous HTTP response."""

    url: str = attr.field()
    """The URL that produced this error message."""

    status: http.HTTPStatus = attr.field()
    """The HTTP status code for the response."""

    raw_body: typing.Any = attr.field()
    """The response body."""

    message: str = attr.field(default="")
    """The error message."""

    code: int = attr.field(default=0)
    """The error code."""

    def __str__(self) -> str:
        name = self.status.name.replace("_", " ").title()
        name_value = f"{name} {self.status.value}"

        if self.code:
            code_str = f" ({self.code})"
        else:
            code_str = ""

        if self.message:
            body = self.message
        else:
            try:
                body = self.raw_body.decode("utf-8")
            except (AttributeError, UnicodeDecodeError, TypeError, ValueError):
                body = str(self.raw_body)

        chomped = len(body) > 200

        return f"{name_value}:{code_str} '{body[:200]}{'...' if chomped else ''}' for {self.url}"


@attr.define(auto_exc=True, repr=False, weakref_slot=False)
class ClientHTTPResponseError(HTTPResponseError):
    """Base exception for an erroneous HTTP response that is a client error.

    All exceptions derived from this base should be treated as 4xx client
    errors when encountered.
    """


@attr.define(auto_exc=True, repr=False, weakref_slot=False)
class BadRequestError(ClientHTTPResponseError):
    """Raised when you send an invalid request somehow."""

    status: http.HTTPStatus = attr.field(
        default=http.HTTPStatus.BAD_REQUEST, init=False
    )
    """The HTTP status code for the response."""


@attr.define(auto_exc=True, repr=False, weakref_slot=False)
class UnauthorizedError(ClientHTTPResponseError):
    """Raised when you are not authorized to access a specific resource."""

    status: http.HTTPStatus = attr.field(
        default=http.HTTPStatus.UNAUTHORIZED, init=False
    )
    """The HTTP status code for the response."""


@attr.define(auto_exc=True, repr=False, weakref_slot=False)
class ForbiddenError(ClientHTTPResponseError):
    """Raised when you are not allowed to access a specific resource.

    This means you lack the permissions to do something, either because of
    permissions set in a guild, or because your application is not whitelisted
    to use a specific endpoint.
    """

    status: http.HTTPStatus = attr.field(default=http.HTTPStatus.FORBIDDEN, init=False)
    """The HTTP status code for the response."""


@attr.define(auto_exc=True, repr=False, weakref_slot=False)
class NotFoundError(ClientHTTPResponseError):
    """Raised when something is not found."""

    status: http.HTTPStatus = attr.field(default=http.HTTPStatus.NOT_FOUND, init=False)
    """The HTTP status code for the response."""


@attr.define(auto_exc=True, kw_only=True, repr=False, weakref_slot=False)
class RateLimitedError(ClientHTTPResponseError):
    """Raised when a non-global rate limit that cannot be handled occurs.

    If you receive one of these, you should NOT try again until the given
    time has passed, either discarding the operation you performed, or waiting
    until the given time has passed first. Note that it may still be valid to
    send requests with different attributes in them.

    A use case for this by Discord appears to be to stop abuse from bots that
    change channel names, etc, regularly. This kind of action allegedly causes
    a fair amount of overhead internally for Discord. In the case you encounter
    this, you may be able to send different requests that manipulate the same
    entities (in this case editing the same channel) that do not use the same
    collection of attributes as the previous request.
    """

    retry_after: float = attr.field()
    """How many seconds to wait before you can reuse the route with the specific request."""

    status: http.HTTPStatus = attr.field(
        default=http.HTTPStatus.TOO_MANY_REQUESTS, init=False
    )
    """The HTTP status code for the response."""

    message: str = attr.field(init=False)
    """The error message."""

    @message.default
    def _(self) -> str:
        return f"You are being rate-limited for {self.retry_after:,} seconds on route {self.route}. Please slow down!"


@attr.define(auto_exc=True, kw_only=True, repr=False, weakref_slot=False)
class RateLimitTooLongError(HTTPError):
    """Internal error raised if the wait for a rate limit is too long.

    This is similar to `asyncio.TimeoutError` in the way that it is used,
    but this will be raised pre-emptively and immediately if the period
    of time needed to wait is greater than a user-defined limit.

    This will almost always be route-specific. If you receive this, it is
    unlikely that performing the same call for a different channel/guild/user
    will also have this rate limit.
    """

    # route: routes.CompiledRoute = attr.field()
    """The route that produced this error."""

    retry_after: float = attr.field()
    """How many seconds to wait before you can retry this specific request."""

    max_retry_after: float = attr.field()
    """How long the client is allowed to wait for at a maximum before raising."""

    reset_at: float = attr.field()
    """UNIX timestamp of when this limit will be lifted."""

    limit: int = attr.field()
    """The maximum number of calls per window for this rate limit."""

    period: float = attr.field()
    """How long the rate limit window lasts for from start to end."""

    message: str = attr.field(init=False)
    """The error message."""

    @message.default
    def _(self) -> str:
        return (
            "The request has been rejected, as you would be waiting for more than"
            f"the max retry-after ({self.max_retry_after}) on route {self.route}"
        )

    # This may support other types of limits in the future, this currently
    # exists to be self-documenting to the user and for future compatibility
    # only.
    @property
    def remaining(self) -> typing.Literal[0]:
        """The number of requests remaining in this window.

        This will always be `0` symbolically.

        Returns
        -------
        builtins.int
            The number of requests remaining. Always `0`.
        """  # noqa: D401 - Imperative mood
        return 0

    def __str__(self) -> str:
        return self.message


@attr.define(auto_exc=True, repr=False, weakref_slot=False)
class InternalServerError(HTTPResponseError):
    """Base exception for an erroneous HTTP response that is a server error.

    All exceptions derived from this base should be treated as 5xx server
    errors when encountered. If you get one of these, it is not your fault!
    """


@attr.define(auto_exc=True, repr=False, init=False, weakref_slot=False)
class MissingIntentWarning(DefectioWarning):
    """Warning raised when subscribing to an event that cannot be fired.

    This is caused by your application missing certain intents.
    """
