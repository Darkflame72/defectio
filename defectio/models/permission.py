from __future__ import annotations

from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Dict
from typing import Iterator
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Type
from typing import TYPE_CHECKING
from typing import TypeVar


class Permission:
    def __init__(self, value: int) -> None:
        self.value = value


class UserPermission(Permission):
    def __init__(self, value: int) -> None:
        super().__init__(value)
        self._access_pos = 0
        self._view_profile_pos = 1
        self._send_message_pos = 2
        self._invite_user_pos = 3

    @property
    def access(self) -> bool:
        return bool(self.value >> self._access_pos & 1)

    @access.setter
    def access(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._access_pos)) | (
            1 << self._access_pos if value else 0
        )

    @property
    def view_profile(self) -> bool:
        return bool(self.value >> self._view_profile_pos & 1)

    @view_profile.setter
    def view_profile(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._view_profile_pos)) | (
            1 << self._view_profile_pos if value else 0
        )

    @property
    def send_message(self) -> bool:
        return bool(self.value >> self._send_message_pos & 1)

    @send_message.setter
    def send_message(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._send_message_pos)) | (
            1 << self._send_message_pos if value else 0
        )

    @property
    def invite_user(self) -> bool:
        return bool(self.value >> self._invite_user_pos & 1)

    @invite_user.setter
    def invite_user(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._invite_user_pos)) | (
            1 << self._invite_user_pos if value else 0
        )


class ChannelPermission(Permission):
    def __init__(self, value: int) -> None:
        super().__init__(value)
        self._view_channel_pos = 0
        self._send_message_pos = 1
        self._manage_messages_pos = 2
        self._manage_channel_pos = 3
        self._voice_call_pos = 4
        self._invite_others_pos = 5
        self._embed_links_pos = 6
        self._upload_files_pos = 7

    @property
    def view(self) -> bool:
        return bool(self.value >> self._view_channel_pos & 1)

    @view.setter
    def view(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._view_channel_pos)) | (
            1 << self._view_channel_pos if value else 0
        )

    @property
    def send_message(self) -> bool:
        return bool(self.value >> self._send_message_pos & 1)

    @send_message.setter
    def send_message(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._send_message_pos)) | (
            1 << self._send_message_pos if value else 0
        )

    @property
    def manage_messages(self) -> bool:
        return bool(self.value >> self._manage_messages_pos & 1)

    @manage_messages.setter
    def manage_messages(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._manage_messages_pos)) | (
            1 << self._manage_messages_pos if value else 0
        )

    @property
    def manage_channel(self) -> bool:
        return bool(self.value >> self._manage_channel_pos & 1)

    @manage_channel.setter
    def manage_channel(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._manage_channel_pos)) | (
            1 << self._manage_channel_pos if value else 0
        )

    @property
    def voice_call(self) -> bool:
        return bool(self.value >> self._voice_call_pos & 1)

    @voice_call.setter
    def voice_call(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._voice_call_pos)) | (
            1 << self._voice_call_pos if value else 0
        )

    @property
    def invite_others(self) -> bool:
        return bool(self.value >> self._invite_others_pos & 1)

    @invite_others.setter
    def invite_others(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._invite_others_pos)) | (
            1 << self._invite_others_pos if value else 0
        )

    @property
    def embed_links(self) -> bool:
        return bool(self.value >> self._embed_links_pos & 1)

    @embed_links.setter
    def embed_links(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._embed_links_pos)) | (
            1 << self._embed_links_pos if value else 0
        )

    @property
    def upload_files(self) -> bool:
        return bool(self.value >> self._upload_files_pos & 1)

    @upload_files.setter
    def upload_files(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._upload_files_pos)) | (
            1 << self._upload_files_pos if value else 0
        )


class ServerPermission(Permission):
    def __init__(self, value: int) -> None:
        super().__init__(value)
        self._view_server_pos = 0
        self._manage_roles_pos = 1
        self._manage_channels_pos = 2
        self._manage_server_pos = 3
        self._kick_members_pos = 4
        self._ban_members_pos = 5
        self._change_nickname_pos = 12
        self._manage_nicknames_pos = 13
        self._change_avatar_pos = 14
        self._manage_avatars_pos = 15

    @property
    def view_server(self) -> bool:
        return bool(self.value >> self._view_server_pos & 1)

    @view_server.setter
    def view_server(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._view_server_pos)) | (
            1 << self._view_server_pos if value else 0
        )

    @property
    def manage_roles(self) -> bool:
        return bool(self.value >> self._manage_roles_pos & 1)

    @manage_roles.setter
    def manage_roles(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._manage_roles_pos)) | (
            1 << self._manage_roles_pos if value else 0
        )

    @property
    def manage_channels(self) -> bool:
        return bool(self.value >> self._manage_channels_pos & 1)

    @manage_channels.setter
    def manage_channels(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._manage_channels_pos)) | (
            1 << self._manage_channels_pos if value else 0
        )

    @property
    def manage_server(self) -> bool:
        return bool(self.value >> self._manage_server_pos & 1)

    @manage_server.setter
    def manage_server(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._manage_server_pos)) | (
            1 << self._manage_server_pos if value else 0
        )

    @property
    def kick_members(self) -> bool:
        return bool(self.value >> self._kick_members_pos & 1)

    @kick_members.setter
    def kick_members(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._kick_members_pos)) | (
            1 << self._kick_members_pos if value else 0
        )

    @property
    def ban_members(self) -> bool:
        return bool(self.value >> self._ban_members_pos & 1)

    @ban_members.setter
    def ban_members(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._ban_members_pos)) | (
            1 << self._ban_members_pos if value else 0
        )

    @property
    def change_nickname(self) -> bool:
        return bool(self.value >> self._change_nickname_pos & 1)

    @change_nickname.setter
    def change_nickname(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._change_nickname_pos)) | (
            1 << self._change_nickname_pos if value else 0
        )

    @property
    def manage_nicknames(self) -> bool:
        return bool(self.value >> self._manage_nicknames_pos & 1)

    @manage_nicknames.setter
    def manage_nicknames(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._manage_nicknames_pos)) | (
            1 << self._manage_nicknames_pos if value else 0
        )

    @property
    def change_avatar(self) -> bool:
        return bool(self.value >> self._change_avatar_pos & 1)

    @change_avatar.setter
    def change_avatar(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._change_avatar_pos)) | (
            1 << self._change_avatar_pos if value else 0
        )

    @property
    def remove_avatars(self) -> bool:
        return bool(self.value >> self._change_avatar_pos & 1)

    @remove_avatars.setter
    def remove_avatars(self, value: bool) -> None:
        self.value = (self.value & ~(1 << self._change_avatar_pos)) | (
            1 << self._change_avatar_pos if value else 0
        )
