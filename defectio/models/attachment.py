from __future__ import annotations
from defectio.models.objects import Unique

import io
import os
from typing import Literal
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from defectio.models.mixins import Hashable

from ..errors import DefectioException

if TYPE_CHECKING:
    from ..state import ConnectionState
    from ..types.payloads import AttachmentPayload


class AutumnID(Unique):
    """
    Attributes
    ------------
    id: :class:`int`
        The atumn file ID.
    """

    __slots__ = "id"

    def __init__(self, *, data):
        self.id: str = data["id"]

    def __str__(self) -> str:
        return self.id or ""


class Attachment(Unique):
    def __init__(self, *, data: AttachmentPayload, state: ConnectionState):
        self.id: int = data["_id"]
        self.tag: Literal["attachments"] = data["tag"]
        self.filename: str = data["filename"]
        self.width: Optional[int] = data["metadata"].get("width")
        self.height: Optional[int] = data["metadata"].get("height")
        self.content_type: Optional[str] = data.get("content_type")
        self.size: int = data["size"]
        self._state: ConnectionState = state

    @property
    def url(self) -> str:
        """:class:`str`: URL of the attachment"""
        base_url = self._state.api_info.features.autumn["url"]

        return f"{base_url}/{self.tag}/{self.id}"

    @property
    def is_spoiler(self) -> bool:
        """:class:`bool`: Whether this attachment contains a spoiler."""
        return self.filename.startswith("SPOILER_")

    def __repr__(self) -> str:
        return f"<Attachment id={self.id} filename={self.filename!r} url={self.url!r}>"

    def __str__(self) -> str:
        return self.url or ""

    def to_dict(self) -> dict:
        result: dict = {
            "filename": self.filename,
            "id": self.id,
            "tag": self.tag,
            "size": self.size,
            "url": self.url,
            "spoiler": self.is_spoiler(),
        }
        if self.width:
            result["width"] = self.width
        if self.height:
            result["height"] = self.height
        if self.content_type:
            result["content_type"] = self.content_type
        return result

    async def read(self) -> bytes:
        """|coro|

        Retrieves the content of this asset as a :class:`bytes` object.

        Raises
        ------
        DefectioException
            There was no internal connection state.
        HTTPException
            Downloading the asset failed.
        NotFound
            The asset was deleted.

        Returns
        -------
        :class:`bytes`
            The content of the asset.
        """
        if self._state is None:
            raise DefectioException("Invalid state (no ConnectionState provided)")

        return await self._state.http.get_from_cdn(self.url)

    async def save(
        self,
        fp: Union[str, bytes, os.PathLike, io.BufferedIOBase],
        *,
        seek_begin: bool = True,
    ) -> int:
        """|coro|

        Saves this asset into a file-like object.

        Parameters
        ----------
        fp: Union[:class:`io.BufferedIOBase`, :class:`os.PathLike`]
            The file-like object to save this attachment to or the filename
            to use. If a filename is passed then a file is created with that
            filename and used instead.
        seek_begin: :class:`bool`
            Whether to seek to the beginning of the file after saving is
            successfully done.

        Raises
        ------
        DiscordException
            There was no internal connection state.
        HTTPException
            Downloading the asset failed.
        NotFound
            The asset was deleted.

        Returns
        --------
        :class:`int`
            The number of bytes written.
        """

        data = await self.read()
        if isinstance(fp, io.BufferedIOBase):
            written = fp.write(data)
            if seek_begin:
                fp.seek(0)
            return written
        else:
            async with open(fp, "wb") as f:
                return await f.write(data)
