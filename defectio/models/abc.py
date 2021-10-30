from __future__ import annotations

from typing import Any
from typing import Optional
from typing import runtime_checkable
from typing import TYPE_CHECKING
from typing import Union

from defectio.models.objects import Unique
from defectio.models.server import Category
from defectio.types.payloads import ChannelPayload

if TYPE_CHECKING:
    from defectio.state import ConnectionState
    from defectio.models.server import Server
    from defectio.models.message import Message, Reply
    from defectio.types.payloads import ChannelType
    from defectio.models.channel import DMChannel, TextChannel, GroupChannel
    from defectio.models.message import File
    from defectio.models.user import ClientUser

    PartialMessageableChannel = Union[TextChannel, DMChannel]
    MessageableChannel = Union[PartialMessageableChannel, GroupChannel]


class User(Unique):
    """An ABC that details the common operations on a Revolt user.

    The following implement this ABC:

    - :class:`~defectio.User`
    - :class:`~discord.ClientUser`
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


class PrivateChannel(Unique):
    """An ABC that details the common operations on a private Discord channel.

    The following implement this ABC:

    - :class:`~defectio.DMChannel`
    - :class:`~defectio.GroupChannel`

    This ABC must also implement :class:`~defectio.abc.Unique`.

    Attributes
    -----------
    me: :class:`~discord.User`
        The user presenting yourself.
    """

    __slots__ = ()

    me: ClientUser


class ServerChannel:
    __slots__ = ()

    id: int
    name: str
    server: Server
    type: str
    position: int
    _state: ConnectionState

    if TYPE_CHECKING:

        def __init__(
            self, *, state: ConnectionState, server: Server, data: ChannelPayload
        ):
            ...

    def __str__(self) -> str:
        return self.name

    def _update(self, server: Server, data: dict[str, Any]) -> None:
        raise NotImplementedError

    @property
    def mention(self) -> str:
        return f"<#{self.id}>"

    async def delete(self) -> None:
        await self._state.http.close_channel(self.id)

    @property
    def category(self) -> Optional[Category]:
        """Optional[:class:`~defectio.Category`]: The category this channel belongs to.

        If there is no category then this is ``None``.
        """
        return self.server.get_category_channel(self.id)


class Messageable(Unique):
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
        files: Optional[list[File]] = None,
        replies: Optional[list[Reply]] = [],
        delete_after: int = None,
        nonce=None,
    ):

        channel = await self._get_channel()
        state = self._state
        content = str(content) if content is not None else ""

        attachment_ids: list[str] = []
        if file is not None:
            files = [file]
        if files is not None:
            for attachment in files:
                attach = await self._state.http.send_file(
                    file=attachment, tag="attachments"
                )
                attachment_ids.append(attach["id"])

        replies = [{"id": r.message.id, "mention": r.mention} for r in replies]
        data = await state.http.send_message(
            channel.id, content=content, attachments=attachment_ids, replies=replies
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
