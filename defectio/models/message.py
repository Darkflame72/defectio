from __future__ import annotations

from typing import TYPE_CHECKING

import attr
from defectio.models import objects
from defectio.models.attachmet import Attachment


if TYPE_CHECKING:
    from defectio.models.user import PartialUser
    from defectio.models.file import File
    from defectio import traits
    from typing import Optional
    from defectio.models.channel import MessageableChannel


import asyncio

__all__ = ["Reply", "Message"]


@attr.define(hash=False, kw_only=True, weakref_slot=False)
class Reply:
    """A reply to a message."""

    message: Message = attr.ib(eq=False, hash=False, repr=True)
    """The message that this reply is replying to."""

    mention: Optional[bool] = attr.ib(eq=False, hash=False, repr=True)
    """Whether or not the reply should mention the author of the message."""

    def __repr__(self):
        return "<Reply message={0!r} mention={1}>".format(self.message, self.mention)


@attr.define(hash=True, kw_only=True, weakref_slot=False)
class Message(objects.Unique):
    """A message in a channel."""

    app: traits.RESTAware = attr.ib(eq=False, hash=False, repr=True)
    """The application instance."""

    id: objects.Object = attr.ib(eq=False, hash=False, repr=True)
    """The ID of the message."""

    content: str = attr.ib(eq=False, hash=False, repr=True)
    """The content of the message."""

    channel_id: objects.Object = attr.ib(eq=False, hash=False, repr=True)
    """The channel that the message is in."""

    author_id: objects.Object = attr.ib(eq=False, hash=False, repr=True)
    """The author of the message."""

    replies_ids: list[objects.Object] = attr.ib(eq=False, hash=False, repr=True)
    """The replies to this message."""

    attachments: list[Attachment] = attr.ib(eq=False, hash=False, repr=True)
    """The attachments to this message."""

    @property
    def server(self) -> str:
        """The server that the message is in."""
        return self.channel.server

    @property
    def author(self) -> PartialUser:
        """The author of the message."""
        return self.app.cache.get_user(self.author_id)

    async def reply(
        self,
        content: str = None,
        *,
        file: Optional[File] = None,
        files: Optional[list[File]] = None,
        mention: bool = False,
        delete_after: int = None,
        nonce=None,
    ):
        """Reply to the message.

        Parameters
        ----------
        content : str, optional
            The content of the reply.
        file : File, optional
            The file to attach to the reply.
        files : list[File], optional
            The files to attach to the reply.
        mention : bool, optional
            Whether or not the reply should mention the author of the message.
        delete_after : int, optional
            The number of seconds to wait before deleting the reply.
        nonce : int, optional
            The nonce to use for the reply.
        """
        return await self.channel.send(
            content,
            file=file,
            files=files,
            delete_after=delete_after,
            nonce=nonce,
            replies=[Reply(self, mention)],
        )

    async def delete(self, *, delay: Optional[float] = None) -> None:
        """Delete the message.

        Parameters
        ----------
        delay : Optional[float], optional
            Delay before deleting the message, by default None
        """
        if delay is not None:

            async def delete(delay: float):
                await asyncio.sleep(delay)
                await self.app.rest.delete_message(self.channel, self)

            asyncio.create_task(delete(delay))
        else:
            await self.app.rest.delete_message(self.channel, self)

    async def edit(self, content: str) -> Message:
        """Edit the message.

        Parameters
        ----------
        content : str
            The new content of the message.

        Returns
        -------
        Message
            The edited message.
        """
        await self.app.rest.edit_message(self.channel, self, content=content)
        self.content = content

        return self
