from defectio.models.member import Member
from defectio.types.websocket import PartialUser
from defectio.models.message import Message
from typing import Any
from typing import Literal
from typing import Optional
from typing import Tuple
from typing import Type
from typing import TypedDict

RelationType = Literal[
    "Blocked", "BlockedOther", "Friend", "Incoming", "None", "Outgoing", "User"
]
ChannelType = Literal[
    "SavedMessage", "DirectMessage", "Group", "TextChannel", "VoiceChannel"
]


class Messages:
    messages: list[Message]
    users: Optional[list[PartialUser]]
    members: Optional[list[Member]]


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


class MetadataPayload(TypedDict):
    type: Literal["File", "Text", "Audio", "Image", "Video"]


class RelationshipPayload(TypedDict):
    status: RelationType
    _id: str


class StatusPayload(TypedDict):
    text: str
    presence: Literal["Busy", "Idle", "Invisible", "Online", "Offline"]


class UserBotInfoPayload(TypedDict):
    owner: str


class AttachmentPayload(TypedDict):
    _id: str
    tag: Literal["attachments"]
    size: int
    filename: str
    metadata: MetadataPayload
    content_type: str


class UserPayload(TypedDict):
    _id: str
    username: str
    avatar: AttachmentPayload
    relations: list[RelationshipPayload]
    badges: int
    status: StatusPayload
    relationship: RelationType
    online: bool
    flags: int
    bot: UserBotInfoPayload


class ProfilePayload(TypedDict):
    content: str
    background: AttachmentPayload


MutualFriends = TypedDict("MutualFriends", {"users": list[str]})


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


class IconPayload(TypedDict):
    _id: str
    tag: str
    size: int
    filename: str
    content_type: str
    metadata: MetadataPayload


class ChannelPayload(TypedDict):
    _id: str
    server: str
    name: str
    description: str
    icon: IconPayload
    default_permissions: int
    role_permissions: dict[str, int]
    channel_type: ChannelType


class EditChannelPayload(TypedDict):
    name: str
    description: str
    icon: str
    remove: Literal["Description", "Icon"]


ChannelInvite = TypedDict("ChannelInvite", {"code": str})


class ContentPayload(TypedDict):
    type: str
    content: str


Edited = TypedDict("Edited", {"con$datatent": str})

Embed = TypedDict("Embed", {"type": str})


class MessagePayload(TypedDict):
    _id: str
    nonce: Optional[str]
    channel: str
    author: str
    content: ContentPayload
    attachments: list[AttachmentPayload]
    edited: Edited
    embeds: list[Embed]
    mentions: list[str]
    replies: list[str]


class MemberIdPayload(TypedDict):
    server: str
    user: str


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
    icon: IconPayload
    permissions: int


JoinCall = TypedDict("JoinCall", {"token": str})


class CategoryPayload(TypedDict):
    _id: str
    title: str
    channels: list[str]


class SystemMessagePayload(TypedDict):
    user_joined: str
    user_left: str
    user_kicked: str
    user_banned: str


class RolePayload(TypedDict):
    name: str
    colour: str
    hoist: Optional[bool]
    rank: int
    permissions: list[int]


class BannerPayload(TypedDict):
    _id: str
    tag: Literal["attachments"]
    size: int
    filename: str
    content_type: str
    metadata: MetadataPayload


class ServerPayload(TypedDict):
    _id: str
    nonce: Optional[str]
    owner: str
    name: str
    description: Optional[str]
    channels: list[str]
    categories: list[CategoryPayload]
    system_message: SystemMessagePayload
    roles: dict[str, RolePayload]
    default_permissions: list[int]
    icon: IconPayload
    banner: BannerPayload


class ChannelPayload(TypedDict):
    _id: str
    channel_type: ChannelType
    name: str
    description: str
    nonce: Optional[str]


class MemberPayload(TypedDict):
    _id: MemberIdPayload
    nickname: str
    avatar: AttachmentPayload
    roles: list[str]


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
    server_banner: BannerPayload
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
