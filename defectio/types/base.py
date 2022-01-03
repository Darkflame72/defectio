from typing import Literal
from typing import TypedDict
from typing import Optional


ChannelType = Literal[
    "SavedMessage", "DirectMessage", "Group", "TextChannel", "VoiceChannel"
]
RelationType = Literal[
    "Blocked", "BlockedOther", "Friend", "Incoming", "None", "Outgoing", "User"
]
Edited = TypedDict("Edited", {"con$datatent": str})
Embed = TypedDict("Embed", {"type": str})
StatusType = Literal["Busy", "Idle", "Invisible", "Online", "Offline"]
MetatDataType = Literal["File", "Text", "Audio", "Image", "Video"]


class MetadataPayload(TypedDict):
    type: MetatDataType


class AttachmentPayload(TypedDict):
    _id: str
    tag: Literal["attachments"]
    size: int
    filename: str
    metadata: MetadataPayload
    content_type: str


class ChannelPayload(TypedDict):
    _id: str
    server: str
    name: str
    description: str
    icon: AttachmentPayload
    default_permissions: int
    role_permissions: dict[str, int]
    channel_type: ChannelType


class MemberIdPayload(TypedDict):
    server: str
    user: str


class MemberPayload(TypedDict):
    _id: MemberIdPayload
    nickname: str
    avatar: AttachmentPayload
    roles: list[str]


class ContentPayload(TypedDict):
    type: str
    content: str


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


class RolePayload(TypedDict):
    name: str
    colour: str
    hoist: Optional[bool]
    rank: int
    permissions: list[int]


class CategoryPayload(TypedDict):
    _id: str
    title: str
    channels: list[str]


class SystemMessagePayload(TypedDict):
    user_joined: str
    user_left: str
    user_kicked: str
    user_banned: str


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
    icon: AttachmentPayload
    banner: AttachmentPayload


class RelationshipPayload(TypedDict):
    status: RelationType
    _id: str


class StatusPayload(TypedDict):
    text: str
    presence: StatusType


class UserBotInfoPayload(TypedDict):
    owner: str


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
