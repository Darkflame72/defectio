from __future__ import annotations

import attr
from typing import TYPE_CHECKING
from defectio.models import objects


if TYPE_CHECKING:
    from defectio import traits
    from defectio.types.base import MetatDataType


__all__ = ["Attachment", "MetaData"]


@attr.define(hash=False, kw_only=True, weakref_slot=False)
class MetaData:
    """Metadata for a attachment."""

    type: MetatDataType = attr.ib(eq=False, hash=False, repr=True)
    """Type of metadata."""


@attr.define(hash=True, kw_only=True, weakref_slot=False)
class Attachment(objects.Unique):
    """An attachment to a message."""

    app: traits.RESTAware = attr.ib(eq=False, hash=False, repr=True)
    """The application instance."""

    id: objects.Object = attr.ib(eq=False, hash=False, repr=True)
    """The ID of the attachment."""

    tag: str = attr.ib(eq=False, hash=False, repr=True)
    """The tag of the attachment."""

    size: int = attr.ib(eq=False, hash=False, repr=True)
    """The size of the attachment."""

    filename: str = attr.ib(eq=False, hash=False, repr=True)
    """The filename of the attachment."""

    content_type: str = attr.ib(eq=False, hash=False, repr=True)
    """The content type of the attachment."""

    metadata: MetaData = attr.ib(eq=False, hash=False, repr=True)
    """The metadata type of the attachment."""

    @property
    def url(self) -> str:
        """The URL of the attachment."""
        base_url = self.app.api_info["features"]["autumn"]["url"]

        return f"{base_url}/{self.tag}/{self.id}"
