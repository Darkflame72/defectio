from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Protocol
from typing import runtime_checkable
from typing import TYPE_CHECKING
from typing import Union

if TYPE_CHECKING:
    from ..state import ConnectionState
    from .server import Server
    from .message import Message
    from ..types.payloads import ChannelType
    from .channel import DMChannel, TextChannel, GroupChannel
    from defectio.models.message import File

    PartialMessageableChannel = Union[TextChannel, DMChannel]
    MessageableChannel = Union[PartialMessageableChannel, GroupChannel]


class DefectioBase(Protocol):
    """An ABC that details the common operations on a Defectio model.

    Almost all :ref:`Defectio models <defectoi_api_models>` meet this
    abstract base class.

    If you want to create a defectiobase on your own, consider using
    :class:`.Object`.

    Attributes
    -----------
    id: :class:`int`
        The model's unique ID.
    """

    __slots__ = ()
    id: int


@runtime_checkable
class User(DefectioBase, Protocol):
    """An ABC that details the common operations on a Revolt user.

    The following implement this ABC:

    - :class:`~defectio.User`
    - :class:`~defectio.Member`

    Attributes
    -----------
    name: :class:`str`
        The user's username.
    bot: :class:`bool`
        If the user is a bot account.
    """

    __slots__ = ()

    name: str
    bot: bool

    @property
    def display_name(self) -> str:
        """:class:`str`: Returns the user's display name."""
        raise NotImplementedError

    @property
    def mention(self) -> str:
        """:class:`str`: Returns a string that allows you to mention the given user."""
        raise NotImplementedError


@runtime_checkable
class PrivateChannel(DefectioBase, Protocol):
    """An ABC that details the common operations on a private Discord channel.

    The following implement this ABC:

    - :class:`~defectio.DMChannel`
    - :class:`~defectio.GroupChannel`

    This ABC must also implement :class:`~defectio.abc.DefectioBase`.

    Attributes
    -----------
    me: :class:`~discord.User`
        The user presenting yourself.
    """

    __slots__ = ()

    me: User


class ServerChannel:
    __slots__ = ()

    id: int
    name: str
    server: Server
    type: str
    position: int
    category_id: Optional[int]
    _state: ConnectionState

    if TYPE_CHECKING:

        def __init__(
            self, *, state: ConnectionState, server: Server, data: Dict[str, Any]
        ):
            ...

    def __str__(self) -> str:
        return self.name

    def _update(self, server: Server, data: Dict[str, Any]) -> None:
        raise NotImplementedError

    async def delete(self, *, reason: Optional[str] = None) -> None:
        await self._state.http.close_channel(self.id)


class GuildChannel:
    """An ABC that details the common operations on a Revolt server channel.

    The following implement this ABC:

    - :class:`~defectio.TextChannel`
    - :class:`~defectio.VoiceChannel`
    - :class:`~defectio.CategoryChannel`

    This ABC must also implement :class:`~defectio.abc.DefectioBase`.

    Attributes
    -----------
    name: :class:`str`
        The channel name.
    server: :class:`~discord.Server`
        The server the channel belongs to.
    """

    __slots__ = ()

    id: int
    name: str
    server: Server
    type: ChannelType
    category_id: Optional[str]
    _state: ConnectionState

    if TYPE_CHECKING:

        def __init__(
            self, *, state: ConnectionState, server: Server, data: Dict[str, Any]
        ):
            ...

    def __str__(self) -> str:
        return self.name

    def _update(self, server: Server, data: Dict[str, Any]) -> None:
        raise NotImplementedError

    @property
    def mention(self) -> str:
        """:class:`str`: The string that allows you to mention the channel."""
        return f"<#{self.id}>"

    async def delete(self) -> None:
        """|coro|
        Deletes the channel.

        Raises
        -------
        ~defectio.Forbidden
            You do not have proper permissions to delete the channel.
        ~defectio.NotFound
            The channel was not found or was already deleted.
        ~defectio.HTTPException
            Deleting the channel failed.
        """
        await self._state.http.close_channel(self.id)


class Messageable(Protocol):
    """An ABC that details the common operations on a model that can send messages.

    The following implement this ABC:

    - :class:`~defectio.TextChannel`
    - :class:`~defectio.DMChannel`
    - :class:`~defectio.GroupChannel`
    - :class:`~defectio.User`
    - :class:`~defectio.Member`
    """

    __slots__ = ()
    _state: ConnectionState

    async def _get_channel(self) -> MessageableChannel:
        raise NotImplementedError

    async def send(
        self,
        content: str = None,
        *,
        file: Optional[File] = None,
        files: Optional[List[File]] = None,
        delete_after: int = None,
        nonce=None,
    ):

        channel = await self._get_channel()
        state = self._state
        content = str(content) if content is not None else None

        attachment_ids: list[str] = []
        if file is not None:
            files = [file]
        if files is not None:
            for attachment in files:
                attach = await self._state.http.send_file(
                    file=attachment, tag="attachments"
                )
                attachment_ids.append(attach["id"])

        data = await state.http.send_message(
            channel.id, content=content, attachments=attachment_ids
        )

        new_message = state.create_message(channel=channel, data=data)
        if delete_after is not None:
            await new_message.delete(delay=delete_after)
        return new_message

    async def fetch_message(self, id):
        channel = await self._get_channel()
        data = await self._state.http.get_message(channel.id, id)
        return self._state.create_message(channel=channel, data=data)

    async def start_typing(self):
        channel = await self._get_channel()
        await self._state.websocket.begin_typing(channel.id)

    async def stop_typing(self):
        channel = await self._get_channel()
        await self._state.websocket.stop_typing(channel.id)

    async def fetch_message(self, id: int) -> Message:
        """|coro|

        Retrieves a single :class:`~defectio.Message` from the destination.

        Parameters
        ------------
        id: :class:`int`
            The message ID to look for.

        Raises
        --------
        ~defectio.NotFound
            The specified message was not found.
        ~defectio.Forbidden
            You do not have the permissions required to get a message.
        ~defectio.HTTPException
            Retrieving the message failed.

        Returns
        --------
        :class:`~defectio.Message`
            The message asked for.
        """

        channel = await self._get_channel()
        data = await self._state.http.get_message(channel.id, id)
        return self._state.create_message(channel=channel, data=data)
