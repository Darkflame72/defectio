"""
Revolt API Wrapper
~~~~~~~~~~~~~~~~~~~

A python wrapper for the Revolt API.

:copyright: (c) 2021-present Darkflame72.
:license: MIT, see LICENSE for more details.

"""

__title__ = "defectio"
__author__ = "Darkflame72"
__license__ = "MIT"
__copyright__ = "Copyright 2021-present Darkflame72"
__version__ = "0.2.0a"

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

import logging
from typing import NamedTuple, Literal

from defectio.client import Client

# expose all models at the top level
from defectio.models.apiinfo import *
from defectio.models.attachment import *
from defectio.models.auth import *
from defectio.models.channel import *
from defectio.models.colour import *
from defectio.models.file import *
from defectio.models.member import *
from defectio.models.message import *
from defectio.models.objects import *
from defectio.models.permission import *
from defectio.models.server import *
from defectio.models.user import *
from defectio.models.raw_models import *

__all__ = (
    "__title__",
    "__author__",
    "__license__",
    "__copyright__",
    "__version__",
    "version_info",
    "Client",
)


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"]
    serial: int


version_info: VersionInfo = VersionInfo(
    major=0, minor=2, micro=0, releaselevel="alpha", serial=0
)

logging.getLogger(__name__).addHandler(logging.NullHandler())
