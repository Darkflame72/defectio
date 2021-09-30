"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
Copyright (c) 2021-present Darkflame72

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import annotations

import inspect
import re
from typing import Any
from typing import Dict
from typing import Generic
from typing import Iterable
from typing import List
from typing import Literal
from typing import Optional
from typing import Protocol
from typing import runtime_checkable
from typing import Tuple
from typing import Type
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import Union

import defectio

from . import utils
from .errors import *

if TYPE_CHECKING:
    from .context import Context
    from defectio import PartialMessageableChannel


__all__ = (
    "Converter",
    "MemberConverter",
    "UserConverter",
    "TextChannelConverter",
    "ServerConverter",
    "VoiceChannelConverter",
    "CategoryConverter",
    "IDConverter",
    "ServerChannelConverter",
    "clean_content",
    "Greedy",
    "run_converters",
)


def _get_from_servers(bot, getter, argument):
    result = None
    for server in bot.servers:
        result = getattr(server, getter)(argument)
        if result:
            return result
    return result


_utils_get = defectio.utils.get
T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
CT = TypeVar("CT", bound=defectio.abc.ServerChannel)


@runtime_checkable
class Converter(Protocol[T_co]):
    """The base class of custom converters that require the :class:`.Context`
    to be passed to be useful.

    This allows you to implement converters that function similar to the
    special cased ``defectio`` classes.

    Classes that derive from this should override the :meth:`~.Converter.convert`
    method to do its conversion logic. This method must be a :ref:`coroutine <coroutine>`.
    """

    async def convert(self, ctx: Context, argument: str) -> T_co:
        """|coro|

        The method to override to do conversion logic.

        If an error is found while converting, it is recommended to
        raise a :exc:`.CommandError` derived exception as it will
        properly propagate to the error handlers.

        Parameters
        -----------
        ctx: :class:`.Context`
            The invocation context that the argument is being used in.
        argument: :class:`str`
            The argument that is being converted.

        Raises
        -------
        :exc:`.CommandError`
            A generic exception occurred when converting the argument.
        :exc:`.BadArgument`
            The converter failed to convert the argument.
        """
        raise NotImplementedError("Derived classes need to implement this.")


_ID_REGEX = re.compile(r"([0-9A-Z]{26})$")


class IDConverter(Converter[T_co]):
    @staticmethod
    def _get_id_match(argument):
        return _ID_REGEX.match(argument)


class MemberConverter(IDConverter[defectio.Member]):
    async def query_member_named(self, server, argument):
        cache = server._state.member_cache_flags.joined
        if len(argument) > 5 and argument[-5] == "#":
            username, _, discriminator = argument.rpartition("#")
            members = await server.query_members(username, limit=100, cache=cache)
            return defectio.utils.get(
                members, name=username, discriminator=discriminator
            )
        else:
            members = await server.query_members(argument, limit=100, cache=cache)
            return defectio.utils.find(
                lambda m: m.name == argument or m.nick == argument, members
            )

    async def query_member_by_id(self, bot, server, user_id):
        ws = bot._get_websocket(shard_id=server.shard_id)
        try:
            member = await server.fetch_member(user_id)
        except defectio.HTTPException:
            return None

        # If we're not being rate limited then we can use the websocket to actually query
        members = await server.query_members(limit=1, user_ids=[user_id])
        if not members:
            return None
        return members[0]

    async def convert(self, ctx: Context, argument: str) -> defectio.Member:
        bot = ctx.bot
        match = self._get_id_match(argument) or re.match(
            r"<@!?([0-9A-Z]{26})>$", argument
        )
        server = ctx.server
        result = None
        user_id = None
        if match is None:
            if server:
                result = server.get_member_named(argument)
        else:
            user_id = match.group(1)
            if server:
                result = server.get_member(user_id) or _utils_get(
                    ctx.message.mentions, id=user_id
                )
            else:
                result = _get_from_servers(bot, "get_member", user_id)

        if result is None:
            if server is None:
                raise MemberNotFound(argument)

            if user_id is not None:
                result = await self.query_member_by_id(bot, server, user_id)
            else:
                result = await self.query_member_named(server, argument)

            if not result:
                raise MemberNotFound(argument)

        return result


class UserConverter(IDConverter[defectio.User]):
    """Converts to a :class:`~defectio.User`.

    All lookups are via the global user cache.

    The lookup strategy is as follows (in order):

    1. Lookup by ID.
    2. Lookup by mention.
    3. Lookup by name#discrim
    4. Lookup by name
    """

    async def convert(self, ctx: Context, argument: str) -> defectio.User:
        match = self._get_id_match(argument) or re.match(
            r"<@!?([0-9A-Z]{26})>$", argument
        )
        result = None
        state = ctx._state

        if match is not None:
            user_id = match.group(1)
            result = ctx.bot.get_user(user_id)

            if result is None:
                try:
                    result = await ctx.bot.fetch_user(user_id)
                except defectio.HTTPException:
                    raise UserNotFound(argument) from None

            return result

        arg = argument

        # Remove the '@' character if this is the first character from the argument
        if arg[0] == "@":
            # Remove first character
            arg = arg[1:]

        # check for discriminator if it exists,
        if len(arg) > 5 and arg[-5] == "#":
            discrim = arg[-4:]
            name = arg[:-5]
            predicate = lambda u: u.name == name and u.discriminator == discrim
            result = defectio.utils.find(predicate, state._users.values())
            if result is not None:
                return result

        predicate = lambda u: u.name == arg
        result = defectio.utils.find(predicate, state._users.values())

        if result is None:
            raise UserNotFound(argument)

        return result


class ServerChannelConverter(IDConverter[defectio.abc.ServerChannel]):
    """Converts to a :class:`~defectio.abc.ServerChannel`.

    All lookups are via the local server. If in a DM context, then the lookup
    is done by the global cache.

    The lookup strategy is as follows (in order):

    1. Lookup by ID.
    2. Lookup by mention.
    3. Lookup by name.
    """

    async def convert(self, ctx: Context, argument: str) -> defectio.abc.ServerChannel:
        return self._resolve_channel(
            ctx, argument, "channels", defectio.abc.ServerChannel
        )

    @staticmethod
    def _resolve_channel(
        ctx: Context, argument: str, attribute: str, type: Type[CT]
    ) -> CT:
        bot = ctx.bot

        match = IDConverter._get_id_match(argument) or re.match(
            r"<#([0-9A-Z]{26})>$", argument
        )
        result = None
        server = ctx.server

        if match is None:
            # not a mention
            if server:
                iterable: Iterable[CT] = getattr(server, attribute)
                result: Optional[CT] = defectio.utils.get(iterable, name=argument)
            else:

                def check(c):
                    return isinstance(c, type) and c.name == argument

                result = defectio.utils.find(check, bot.get_all_channels())
        else:
            channel_id = match.group(1)
            if server:
                result = server.get_channel(channel_id)
            else:
                result = _get_from_servers(bot, "get_channel", channel_id)

        if not isinstance(result, type):
            raise ChannelNotFound(argument)

        return result


class TextChannelConverter(IDConverter[defectio.TextChannel]):
    """Converts to a :class:`~defectio.TextChannel`.

    All lookups are via the local server. If in a DM context, then the lookup
    is done by the global cache.

    The lookup strategy is as follows (in order):

    1. Lookup by ID.
    2. Lookup by mention.
    3. Lookup by name
    """

    async def convert(self, ctx: Context, argument: str) -> defectio.TextChannel:
        return ServerChannelConverter._resolve_channel(
            ctx, argument, "text_channels", defectio.TextChannel
        )


class VoiceChannelConverter(IDConverter[defectio.VoiceChannel]):
    """Converts to a :class:`~defectio.VoiceChannel`.

    All lookups are via the local server. If in a DM context, then the lookup
    is done by the global cache.

    The lookup strategy is as follows (in order):

    1. Lookup by ID.
    2. Lookup by mention.
    3. Lookup by name
    """

    async def convert(self, ctx: Context, argument: str) -> defectio.VoiceChannel:
        return ServerChannelConverter._resolve_channel(
            ctx, argument, "voice_channels", defectio.VoiceChannel
        )


class CategoryConverter(IDConverter[defectio.Category]):
    """Converts to a :class:`~defectio.Category`.

    All lookups are via the local server. If in a DM context, then the lookup
    is done by the global cache.

    The lookup strategy is as follows (in order):

    1. Lookup by ID.
    2. Lookup by mention.
    3. Lookup by name
    """

    async def convert(self, ctx: Context, argument: str) -> defectio.Category:
        return ServerChannelConverter._resolve_channel(
            ctx, argument, "categories", defectio.Category
        )


class ServerConverter(IDConverter[defectio.Server]):
    """Converts to a :class:`~defectio.Server`.

    The lookup strategy is as follows (in order):

    1. Lookup by ID.
    2. Lookup by name. (There is no disambiguation for Servers with multiple matching names).
    """

    async def convert(self, ctx: Context, argument: str) -> defectio.Server:
        match = self._get_id_match(argument)
        result = None

        if match is not None:
            server_id = match.group(1)
            result = ctx.bot.get_server(server_id)

        if result is None:
            result = defectio.utils.get(ctx.bot.servers, name=argument)

            if result is None:
                raise ServerNotFound(argument)
        return result


class clean_content(Converter[str]):
    """Converts the argument to mention scrubbed version of
    said content.

    This behaves similarly to :attr:`~defectio.Message.clean_content`.

    Attributes
    ------------
    fix_channel_mentions: :class:`bool`
        Whether to clean channel mentions.
    use_nicknames: :class:`bool`
        Whether to use nicknames when transforming mentions.
    escape_markdown: :class:`bool`
        Whether to also escape special markdown characters.
    remove_markdown: :class:`bool`
        Whether to also remove special markdown characters. This option is not supported with ``escape_markdown``
    """

    def __init__(
        self,
        *,
        fix_channel_mentions: bool = False,
        use_nicknames: bool = True,
        escape_markdown: bool = False,
        remove_markdown: bool = False,
    ) -> None:
        self.fix_channel_mentions = fix_channel_mentions
        self.use_nicknames = use_nicknames
        self.escape_markdown = escape_markdown
        self.remove_markdown = remove_markdown

    async def convert(self, ctx: Context, argument: str) -> str:
        msg = ctx.message

        if ctx.server:

            def resolve_member(id: str) -> str:
                m = _utils_get(msg.mentions, id=id) or ctx.server.get_member(id)
                return (
                    f"@{m.display_name if self.use_nicknames else m.name}"
                    if m
                    else "@deleted-user"
                )

            def resolve_role(id: str) -> str:
                r = _utils_get(msg.role_mentions, id=id) or ctx.server.get_role(id)
                return f"@{r.name}" if r else "@deleted-role"

        else:

            def resolve_member(id: str) -> str:
                m = _utils_get(msg.mentions, id=id) or ctx.bot.get_user(id)
                return f"@{m.name}" if m else "@deleted-user"

            def resolve_role(id: str) -> str:
                return "@deleted-role"

        if self.fix_channel_mentions and ctx.server:

            def resolve_channel(id: str) -> str:
                c = ctx.server.get_channel(id)
                return f"#{c.name}" if c else "#deleted-channel"

        else:

            def resolve_channel(id: str) -> str:
                return f"<#{id}>"

        transforms = {
            "@": resolve_member,
            "@!": resolve_member,
            "#": resolve_channel,
            "@&": resolve_role,
        }

        def repl(match: re.Match) -> str:
            type = match[1]
            id = match[2]
            transformed = transforms[type](id)
            return transformed

        result = re.sub(r"<(@[!&]?|#)([0-9A-Z]{26})>", repl, argument)
        if self.escape_markdown:
            result = utils.escape_markdown(result)
        elif self.remove_markdown:
            result = utils.remove_markdown(result)

        # Completely ensure no mentions escape:
        return utils.escape_mentions(result)


class Greedy(List[T]):
    r"""A special converter that greedily consumes arguments until it can't.
    As a consequence of this behaviour, most input errors are silently discarded,
    since it is used as an indicator of when to stop parsing.

    When a parser error is met the greedy converter stops converting, undoes the
    internal string parsing routine, and continues parsing regularly.

    For example, in the following code:

    .. code-block:: python3

        @commands.command()
        async def test(ctx, numbers: Greedy[int], reason: str):
            await ctx.send("numbers: {}, reason: {}".format(numbers, reason))

    An invocation of ``[p]test 1 2 3 4 5 6 hello`` would pass ``numbers`` with
    ``[1, 2, 3, 4, 5, 6]`` and ``reason`` with ``hello``\.

    For more information, check :ref:`ext_commands_special_converters`.
    """

    __slots__ = ("converter",)

    def __init__(self, *, converter: T):
        self.converter = converter

    def __repr__(self):
        converter = getattr(self.converter, "__name__", repr(self.converter))
        return f"Greedy[{converter}]"

    def __class_getitem__(cls, params: Union[Tuple[T], T]) -> Greedy[T]:
        if not isinstance(params, tuple):
            params = (params,)
        if len(params) != 1:
            raise TypeError("Greedy[...] only takes a single argument")
        converter = params[0]

        origin = getattr(converter, "__origin__", None)
        args = getattr(converter, "__args__", ())

        if not (
            callable(converter)
            or isinstance(converter, Converter)
            or origin is not None
        ):
            raise TypeError("Greedy[...] expects a type or a Converter instance.")

        if converter in (str, type(None)) or origin is Greedy:
            raise TypeError(f"Greedy[{converter.__name__}] is invalid.")

        if origin is Union and type(None) in args:
            raise TypeError(f"Greedy[{converter!r}] is invalid.")

        return cls(converter=converter)


def _convert_to_bool(argument: str) -> bool:
    lowered = argument.lower()
    if lowered in ("yes", "y", "true", "t", "1", "enable", "on"):
        return True
    elif lowered in ("no", "n", "false", "f", "0", "disable", "off"):
        return False
    else:
        raise BadBoolArgument(lowered)


def get_converter(param: inspect.Parameter) -> Any:
    converter = param.annotation
    if converter is param.empty:
        if param.default is not param.empty:
            converter = str if param.default is None else type(param.default)
        else:
            converter = str
    return converter


_GenericAlias = type(List[T])


def is_generic_type(tp: Any, *, _GenericAlias: Type = _GenericAlias) -> bool:
    return isinstance(tp, type) and issubclass(tp, Generic) or isinstance(tp, _GenericAlias)  # type: ignore


CONVERTER_MAPPING: Dict[Type[Any], Any] = {
    defectio.Member: MemberConverter,
    defectio.User: UserConverter,
    defectio.TextChannel: TextChannelConverter,
    defectio.Server: ServerConverter,
    defectio.VoiceChannel: VoiceChannelConverter,
    defectio.Category: CategoryConverter,
    defectio.abc.ServerChannel: ServerChannelConverter,
}


async def _actual_conversion(
    ctx: Context, converter, argument: str, param: inspect.Parameter
):
    if converter is bool:
        return _convert_to_bool(argument)

    try:
        module = converter.__module__
    except AttributeError:
        pass
    else:
        if module is not None and (
            module.startswith("defectio.") and not module.endswith("converter")
        ):
            converter = CONVERTER_MAPPING.get(converter, converter)

    try:
        if inspect.isclass(converter) and issubclass(converter, Converter):
            if inspect.ismethod(converter.convert):
                return await converter.convert(ctx, argument)
            else:
                return await converter().convert(ctx, argument)
        elif isinstance(converter, Converter):
            return await converter.convert(ctx, argument)
    except CommandError:
        raise
    except Exception as exc:
        raise ConversionError(converter, exc) from exc

    try:
        return converter(argument)
    except CommandError:
        raise
    except Exception as exc:
        try:
            name = converter.__name__
        except AttributeError:
            name = converter.__class__.__name__

        raise BadArgument(
            f'Converting to "{name}" failed for parameter "{param.name}".'
        ) from exc


async def run_converters(
    ctx: Context, converter, argument: str, param: inspect.Parameter
):
    """|coro|

    Runs converters for a given converter, argument, and parameter.

    This function does the same work that the library does under the hood.

    Parameters
    ------------
    ctx: :class:`Context`
        The invocation context to run the converters under.
    converter: Any
        The converter to run, this corresponds to the annotation in the function.
    argument: :class:`str`
        The argument to convert to.
    param: :class:`inspect.Parameter`
        The parameter being converted. This is mainly for error reporting.

    Raises
    -------
    CommandError
        The converter failed to convert.

    Returns
    --------
    Any
        The resulting conversion.
    """
    origin = getattr(converter, "__origin__", None)

    if origin is Union:
        errors = []
        _NoneType = type(None)
        union_args = converter.__args__
        for conv in union_args:
            # if we got to this part in the code, then the previous conversions have failed
            # so we should just undo the view, return the default, and allow parsing to continue
            # with the other parameters
            if conv is _NoneType and param.kind != param.VAR_POSITIONAL:
                ctx.view.undo()
                return None if param.default is param.empty else param.default

            try:
                value = await run_converters(ctx, conv, argument, param)
            except CommandError as exc:
                errors.append(exc)
            else:
                return value

        # if we're here, then we failed all the converters
        raise BadUnionArgument(param, union_args, errors)

    if origin is Literal:
        errors = []
        conversions = {}
        literal_args = converter.__args__
        for literal in literal_args:
            literal_type = type(literal)
            try:
                value = conversions[literal_type]
            except KeyError:
                try:
                    value = await _actual_conversion(ctx, literal_type, argument, param)
                except CommandError as exc:
                    errors.append(exc)
                    conversions[literal_type] = object()
                    continue
                else:
                    conversions[literal_type] = value

            if value == literal:
                return value

        # if we're here, then we failed to match all the literals
        raise BadLiteralArgument(param, literal_args, errors)

    # This must be the last if-clause in the chain of origin checking
    # Nearly every type is a generic type within the typing library
    # So care must be taken to make sure a more specialised origin handle
    # isn't overwritten by the widest if clause
    if origin is not None and is_generic_type(converter):
        converter = origin

    return await _actual_conversion(ctx, converter, argument, param)
