from typing import Literal
from typing import Optional
from typing import TypedDict

from .payloads import ChannelPayload
from .payloads import MemberPayload
from .payloads import MessagePayload
from .payloads import RelationType
from .payloads import RolePayload
from .payloads import ServerPayload
from .payloads import UserPayload


class Error(TypedDict):
    type: Literal[
        "LabelMe",
        "InternalError",
        "InvalidSession",
        "OnboardingNotFinished",
        "AlreadyAuthenticated",
    ]
    error: str


class Authenticated(TypedDict):
    type: Literal["Authenticated"]


class Pong(TypedDict):
    type: Literal["Pong"]
    time: int


class Ready(TypedDict):
    type: Literal["Ready"]
    users: list[UserPayload]
    servers: list[ServerPayload]
    channels: list[ChannelPayload]


class Message(MessagePayload):
    type: Literal["Message"]


class PartialMessage(MessagePayload, total=False):
    pass


class MessageUpdate(TypedDict):
    type: Literal["MessageUpdate"]
    id: str
    data: PartialMessage


class MessageDelete(TypedDict):
    type: Literal["MessageDelete"]
    id: str
    channel: str


class ChannelCreate(ChannelPayload):
    type: Literal["ChannelCreate"]
    server: str


class PartialChannel(ChannelPayload, total=False):
    pass


class ChannelUpdate(TypedDict):
    type: Literal["ChannelUpdate"]
    id: str
    data: PartialChannel
    clear: Optional[Literal["Icon", "Description"]]


class ChannelDelete(TypedDict):
    type: Literal["ChannelDelete"]
    id: str


class ChannelGroupJoin(TypedDict):
    type: Literal["ChannelGroupJoin"]
    id: str
    user: str


class ChannelGroupLeave(TypedDict):
    type: Literal["ChannelGroupLeave"]
    id: str
    user: str


class ChannelStartTyping(TypedDict):
    type: Literal["ChannelStartTyping"]
    id: str
    user: str


class ChannelStopTyping(TypedDict):
    type: Literal["ChannelStopTyping"]
    id: str
    user: str


class ChannelAck(TypedDict):
    type: Literal["ChannelAck"]
    id: str
    user: str
    message_id: str


class PartialServer(ServerPayload, total=False):
    pass


class ServerUpdate(TypedDict):
    type: Literal["ServerUpdate"]
    id: str
    data: PartialServer
    clear: Optional[Literal["Icon", "Description", "Bannerss"]]


class ServerDelete(TypedDict):
    type: Literal["ServerDelete"]
    id: str


class PartialServerMember(MemberPayload, total=False):
    pass


class ServerMemberUpdate(TypedDict):
    type: Literal["ServerMemberUpdate"]
    id: str
    data: PartialServerMember
    clear: Optional[Literal["Nickname", "Avatar"]]


class ServerMemberJoin(TypedDict):
    type: Literal["ServerMemberJoin"]
    id: str
    user: str


class ServerMemberLeave(TypedDict):
    type: Literal["ServerMemberLeave"]
    id: str
    user: str


class PartialServerRole(RolePayload, total=False):
    pass


class ServerRoleUpdate(TypedDict):
    type: Literal["ServerRoleUpdate"]
    id: str
    data: PartialServerRole
    clear: Optional[Literal["Colour"]]


class ServerRoleDelete(TypedDict):
    type: Literal["ServerRoleDelete"]
    id: str
    role_id: str


class PartialUser(UserPayload, total=False):
    pass


class UserUpdate(TypedDict):
    type: Literal["UserUpdate"]
    id: str
    data: PartialUser
    clear: Optional[
        Literal["ProfileContent", "ProfileBackground", "StatusText", "Avatar"]
    ]


class UserRelationship(TypedDict):
    type: Literal["UserRelationship"]
    id: str
    user: str
    type: RelationType
