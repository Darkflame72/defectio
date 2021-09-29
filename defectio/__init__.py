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
__version__ = "0.3.0"

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

import logging
from typing import NamedTuple, Literal

# expose all models at the top level
from defectio.models import *
from defectio.api.bot import Client

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
    major=0, minor=3, micro=0, releaselevel="alpha", serial=0
)

logging.getLogger(__name__).addHandler(logging.NullHandler())
