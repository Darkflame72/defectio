from __future__ import annotations

import asyncio
import io
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from defectio.models.user import PartialUser

from .embed import Embed
from .abc import Messageable
from .mixins import Hashable


if TYPE_CHECKING:
    from ..state import ConnectionState
    from ..types.payloads import MessagePayload, AttachmentPayload
    from ..types.websocket import MessageUpdate
    from .channel import MessageableChannel


class Attachment:
    def __init__(self, state: ConnectionState, data: AttachmentPayload):
        self._state: ConnectionState = state
        self.id = data.get("_id")
        self.tag = data.get("tag")
        self.size = data.get("size")
        self.filename = data.get("filename")
        self.content_type = data.get("content_type")
        self.metadata_type = data.get("metadata").get("type")

    @property
    def url(self) -> str:
        base_url = self._state.api_info["features"]["autumn"]["url"]

        return f"{base_url}/{self.tag}/{self.id}"


class Reply:
    def __init__(self, message: Message, mention: Optional[bool] = True):
        self.message: Message = message
        self.mention: Optional[bool] = mention

    def __repr__(self):
        return "<Reply message={0!r} mention={1}>".format(self.message, self.mention)


class File:
    """Respresents a file about to be uploaded to revolt

    Parameters
    -----------
    file: Union[str, bytes]
        The name of the file or the content of the file in bytes, text files will be need to be encoded
    filename: Optional[str]
        The filename of the file when being uploaded, this will default to the name of the file if one exists
    spoiler: bool
        Determines if the file will be a spoiler, this prefexes the filename with `SPOILER_`
    """

    def __init__(
        self,
        file: Union[str, bytes],
        *,
        filename: Optional[str] = None,
        spoiler: bool = False,
    ):
        if isinstance(file, str):
            self.f = open(file, "rb")
        elif isinstance(file, bytes):
            self.f = io.BytesIO(file)

        if filename is None and isinstance(file, str):
            filename = self.f.name

        if spoiler or (filename and filename.startswith("SPOILER_")):
            self.spoiler = True
        else:
            self.spoiler = False

        if self.spoiler and (filename and not filename.startswith("SPOILER_")):
            filename = f"SPOILER_{filename}"

        self.filename = filename


class Message(Hashable):
    def __init__(
        self, state: ConnectionState, channel: MessageableChannel, data: MessagePayload
    ):
        self._state: ConnectionState = state
        self.id = data.get("_id")
        self.channel = channel
        self.content = data.get("content")
        self.author_id = data.get("author")
        self.replies = [state.get_message(r) for r in data.get("replies", [])]
        self.attachments = [Attachment(state, a) for a in data.get("attachments", [])]
        self.embeds = [Embed.from_dict(e) for e in data.get("embeds", [])]

    def __repr__(self) -> str:
        name = self.__class__.__name__
        return f"<{name} id={self.id} channel={self.channel!r} author={self.author!r}"

    @property
    def server(self) -> str:
        return self.channel.server

    @property
    def author(self) -> PartialUser:
        return self._state.get_user(self.author_id) or PartialUser(self.author_id)

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
        return await self.channel.send(
            content,
            file=file,
            files=files,
            delete_after=delete_after,
            nonce=nonce,
            replies=[Reply(self, mention)],
        )

    async def delete(self, *, delay: Optional[float] = None) -> None:
        if delay is not None:

            async def delete(delay: float):
                await asyncio.sleep(delay)
                await self._state.http.delete_message(self.channel.id, self.id)

            asyncio.create_task(delete(delay))
        else:
            await self._state.http.delete_message(self.channel.id, self.id)

    async def edit(self, content: str) -> Message:
        await self._state.http.edit_message(self.channel.id, self.id, content=content)
        self.content = content

        return self

    def _update(self, data: MessageUpdate) -> None:
        if "content" in data["data"]:
            self.content = data.get("data").get("content")
