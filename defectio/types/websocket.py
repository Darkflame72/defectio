from typing import Literal
from typing import Optional
from typing import TypedDict

from defectio.types.base import ChannelPayload
from .base import MemberPayload
from .base import MessagePayload
from .base import RelationType
from .base import RolePayload
from .base import ServerPayload
from .base import UserPayload


class ErrorPayload(TypedDict):
    type: Literal[
        "LabelMe",
        "InternalError",
        "InvalidSession",
        "OnboardingNotFinished",
        "AlreadyAuthenticated",
    ]
    error: str


class AuthenticatedPayload(TypedDict):
    type: Literal["Authenticated"]


class PongPayload(TypedDict):
    type: Literal["Pong"]
    time: int


class ReadyPayload(TypedDict):
    type: Literal["Ready"]
    users: list[UserPayload]
    servers: list[ServerPayload]
    channels: list[ChannelPayload]


class MessagePayload(MessagePayload):
    type: Literal["Message"]


class PartialMessagePayload(MessagePayload, total=False):
    pass


class MessageUpdatePayload(TypedDict):
    type: Literal["MessageUpdate"]
    id: str
    data: PartialMessagePayload


class MessageDeletePayload(TypedDict):
    type: Literal["MessageDelete"]
    id: str
    channel: str


class ChannelCreatePayload(ChannelPayload):
    type: Literal["ChannelCreate"]


class PartialChannelPayload(ChannelPayload, total=False):
    pass


class ChannelUpdatePayload(TypedDict):
    type: Literal["ChannelUpdate"]
    id: str
    data: PartialChannelPayload
    clear: Optional[Literal["Icon", "Description"]]


class ChannelDeletePayload(TypedDict):
    type: Literal["ChannelDelete"]
    id: str


class ChannelGroupJoinPayload(TypedDict):
    type: Literal["ChannelGroupJoin"]
    id: str
    user: str


class ChannelGroupLeavePayload(TypedDict):
    type: Literal["ChannelGroupLeave"]
    id: str
    user: str


class ChannelStartTypingPayload(TypedDict):
    type: Literal["ChannelStartTyping"]
    id: str
    user: str


class ChannelStopTypingPayload(TypedDict):
    type: Literal["ChannelStopTyping"]
    id: str
    user: str


class ChannelAckPayload(TypedDict):
    type: Literal["ChannelAck"]
    id: str
    user: str
    message_id: str


class PartialServerPayload(ServerPayload, total=False):
    pass


class ServerUpdatePayload(TypedDict):
    type: Literal["ServerUpdate"]
    id: str
    data: PartialServerPayload
    clear: Optional[Literal["Icon", "Description", "Bannerss"]]


class ServerDeletePayload(TypedDict):
    type: Literal["ServerDelete"]
    id: str


class PartialServerMemberPayload(MemberPayload, total=False):
    pass


class ServerMemberUpdatePayload(TypedDict):
    type: Literal["ServerMemberUpdate"]
    id: str
    data: PartialServerMemberPayload
    clear: Optional[Literal["Nickname", "Avatar"]]


class ServerMemberJoinPayload(TypedDict):
    type: Literal["ServerMemberJoin"]
    id: str
    user: str


class ServerMemberLeavePayload(TypedDict):
    type: Literal["ServerMemberLeave"]
    id: str
    user: str


class PartialServerRolePayload(RolePayload, total=False):
    pass


class ServerRoleUpdatePayload(TypedDict):
    type: Literal["ServerRoleUpdate"]
    id: str
    data: PartialServerRolePayload
    clear: Optional[Literal["Colour"]]


class ServerRoleDeletePayload(TypedDict):
    type: Literal["ServerRoleDelete"]
    id: str
    role_id: str


class PartialUserPayload(UserPayload, total=False):
    pass


class UserUpdatePayload(TypedDict):
    type: Literal["UserUpdate"]
    id: str
    data: PartialUserPayload
    clear: Optional[
        Literal["ProfileContent", "ProfileBackground", "StatusText", "Avatar"]
    ]


class UserRelationshipPayload(TypedDict):
    type: Literal["UserRelationship"]
    id: str
    user: str
    type: RelationType
