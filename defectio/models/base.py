from __future__ import annotations
from defectio.models.file import File
from defectio.models.message import Message, Reply

from defectio.models import objects
import attr
import abc
from typing import Optional
from defectio import traits

__all__ = ["Messageable"]


@attr.define(hash=True, kw_only=True, weakref_slot=False)
class Messageable(objects.Unique, abc.ABC):
    """Base class for any object that is messageable."""

    app: traits.RESTAware = attr.ib(eq=False, hash=False, repr=True)
    """The application instance."""

    id: objects.Object = attr.ib(hash=True, repr=True)
    """The ID of this entity."""

    @abc.abstractmethod
    async def _get_channel(self):
        """Get the channel for this object."""

    async def send(
        self,
        content: str = None,
        *,
        file: Optional[File] = None,
        files: Optional[list[File]] = None,
        replies: Optional[list[Reply]] = [],
        delete_after: int = None,
    ):

        channel = await self._get_channel()
        content = str(content) if content is not None else ""

        attachment_ids: list[str] = []
        if file is not None:
            files = [file]
        if files is not None:
            for attachment in files:
                attach = await self.app.rest.send_file(
                    file=attachment, tag="attachments"
                )
                attachment_ids.append(attach["id"])

        replies = [{"id": r.message.id, "mention": r.mention} for r in replies]
        new_message = await self.app.rest.send_message(
            channel, content=content, attachments=attachment_ids, replies=replies
        )

        if delete_after is not None:
            await new_message.delete(delay=delete_after)
        return new_message

    async def fetch_message(self, id):
        channel = await self._get_channel()
        data = await self.app.rest.fetch_message(channel, id)
        return self._state.create_message(channel=channel, data=data)

    async def start_typing(self):
        channel = await self._get_channel()
        await self.app.gateway.websocket.begin_typing(channel)

    async def stop_typing(self):
        channel = await self._get_channel()
        await self.app.gateway.stop_typing(channel)

    async def fetch_message(self, id: int) -> Message:
        """|coro|

        Retrieves a single :class:`~defectio.Message` from the destination.

        Parameters
        ------------
        id: int
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
        Message
            The message asked for.
        """

        channel = await self._get_channel()
        data = await self.app.rest.fetch_message(channel, id)
        return self._state.create_message(channel=channel, data=data)
