from __future__ import annotations

import io
import os
from typing import Optional
from typing import Union
import attr

__all__ = ["File"]


class File:
    """Respresents a file about to be uploaded to revolt."""

    __slots__ = ("fp", "_original_pos", "_owner", "_closer", "filename", "spoiler")

    def __init__(
        self,
        file: Union[str, bytes, os.PathLike, io.BufferedIOBase],
        *,
        filename: Optional[str] = None,
        spoiler: bool = False,
    ):
        if isinstance(file, io.IOBase):
            if not (file.seekable() and file.readable()):
                raise ValueError(f"File buffer {file!r} must be seekable and readable")
            self.fp = file
            self._original_pos = file.tell()
            self._owner = False
        if isinstance(file, bytes):
            self.fp = io.BytesIO(file)
            self._original_pos = 0
            self._owner = True
        else:
            self.fp = open(file, "rb")
            self._original_pos = 0
            self._owner = True

        # aiohttp only uses two methods from IOBase
        # read and close, since I want to control when the files
        # close, I need to stub it so it doesn't close unless
        # I tell it to
        self._closer = self.fp.close
        self.fp.close = lambda: None

        if filename is None:
            if isinstance(file, str):
                _, self.filename = os.path.split(file)
            else:
                self.filename = getattr(file, "name", None)
        else:
            self.filename = filename

        if (
            spoiler
            and self.filename is not None
            and not self.filename.startswith("SPOILER_")
        ):
            self.filename = "SPOILER_" + self.filename

        self.spoiler = spoiler or (
            self.filename is not None and self.filename.startswith("SPOILER_")
        )

    def reset(self, *, seek: Union[int, bool] = True) -> None:
        # The `seek` parameter is needed because
        # the retry-loop is iterated over multiple times
        # starting from 0, as an implementation quirk
        # the resetting must be done at the beginning
        # before a request is done, since the first index
        # is 0, and thus false, then this prevents an
        # unnecessary seek since it's the first request
        # done.
        if seek:
            self.fp.seek(self._original_pos)

    def close(self) -> None:
        self.fp.close = self._closer
        if self._owner:
            self._closer()
