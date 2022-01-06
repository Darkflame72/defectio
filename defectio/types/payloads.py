from typing import Any
from typing import Literal
from typing import Optional
from typing import Tuple
from typing import Type
from typing import TYPE_CHECKING
from typing import TypedDict

from defectio.types.base import AttachmentPayload
from defectio.types.base import MemberIdPayload
from defectio.types.base import MemberPayload
from defectio.types.base import MessagePayload
from defectio.types.base import RelationType
from defectio.types.base import ServerPayload
from defectio.types.base import UserPayload


ChannelType = Literal[
    "SavedMessage", "DirectMessage", "Group", "TextChannel", "VoiceChannel"
]
MutualFriends = TypedDict("MutualFriends", {"users": list[str]})


class AccountPayload(TypedDict):
    _id: str
    email: str


class JoinVoice:
    token: str


class LoginPayload(TypedDict):
    _id: str
    user_id: str
    token: str
    name: str
    subscription: str


class ApiInfoFeaturePayload(TypedDict):
    captcha: dict[str, Any]
    email: bool
    invite_only: str
    autumn: dict[str, Any]
    january: dict[str, Any]
    voso: dict[str, Any]


class ApiInfoPayload(TypedDict):
    revolt: str
    features: ApiInfoFeaturePayload
    ws: str
    app: str
    vapid: str


class SessionPayload(TypedDict):
    _id: str
    friendly_name: str


class ProfilePayload(TypedDict):
    content: str
    background: AttachmentPayload


class LastMessagePayload(TypedDict):
    _id: str
    author: str
    short: str


class DMChannelPayload(TypedDict):
    _id: str
    channel_type: Literal["DirectMessage"]
    active: bool
    recipients: list[str]
    last_message: LastMessagePayload


class RelationshipStatusPayload(TypedDict):
    status: RelationType


class EditChannelPayload(TypedDict):
    name: str
    description: str
    icon: str
    remove: Literal["Description", "Icon"]


ChannelInvite = TypedDict("ChannelInvite", {"code": str})


class BasicMemberPayload(TypedDict):
    _id: str
    nickname: str


class FetchMessagePayload(TypedDict):
    messages: list[MessagePayload]
    users: list[UserPayload]
    members: list[BasicMemberPayload]
    avatar: AttachmentPayload
    roles: list[str]


class MessagePollPayload(TypedDict):
    changed: list[MessagePayload]
    deleted: list[str]


class SearchMessagePayload(TypedDict):
    messages: list[MessagePayload]
    users: list[UserPayload]
    members: list[BasicMemberPayload]


class GroupPayload(TypedDict):
    _id: str
    channel_type: Literal["Group"]
    recipients: list[str]
    name: str
    owner: str
    description: str
    last_message: LastMessagePayload
    icon: AttachmentPayload
    permissions: int


JoinCall = TypedDict("JoinCall", {"token": str})


class ChannelPayload(TypedDict):
    _id: str
    channel_type: ChannelType
    name: str
    description: str
    nonce: Optional[str]


class ServerMembersPayload(TypedDict):
    members: list[MemberPayload]
    users: list[UserPayload]


class BanPayload(TypedDict):
    _id: MemberIdPayload
    reason: str


class BansPayload(TypedDict):
    users: list[UserPayload]
    bans: list[BanPayload]


class CreateRole(Type):
    _id: str
    permissions: list[int]


class BotPayload(TypedDict):
    _id: str
    owner: str
    token: str
    public: bool
    interactiosURL: str


class PublicBotPayload(TypedDict):
    _id: str
    username: str
    avatar: AttachmentPayload
    description: str


class InvitePayload(TypedDict):
    type: Literal["Server"]
    server_id: str
    server_name: str
    server_icon: AttachmentPayload
    server_banner: AttachmentPayload
    channel_id: str
    channel_name: str
    channel_description: str
    user_avatar: AttachmentPayload
    member_count: int


class InviteChannelPayload(TypedDict):
    _id: str
    channel_type: Literal["SavedMessages"]
    user: str
    nonce: str


class JoinInvitePayload(TypedDict):
    type: Literal["Server"]
    channel: InviteChannelPayload
    server: ServerPayload


Settings = dict[str, Tuple[int, str]]


class UnreadsPayload(TypedDict):
    _id: MemberIdPayload
    last_id: str
    mentions: list[str]
