from __future__ import annotations
from defectio.models.objects import Unique

from typing import Any
from typing import Optional
from typing import Type
from typing import TYPE_CHECKING
from typing import TypeVar

from .. import utils
from .abc import Messageable
from .attachment import Attachment
from .mixins import Hashable

if TYPE_CHECKING:
    from ..state import ConnectionState
    from ..types.payloads import UserPayload
    from ..types.websocket import UserUpdate
    from ..types.websocket import Message
    from ..types.payloads import RelationshipPayload
    from ..types.payloads import StatusPayload
    from .channel import DMChannel
    from ..types.payloads import DMChannelPayload, ProfilePayload


__all__ = ("User", "ClientUser", "Status", "Relationship", "PartialUser", "BaseUser")

BU = TypeVar("BU", bound="BaseUser")


class Bot:
    __slots__ = ("id", "owner", "token", "public", "interactions_url")


class Status:
    def __init__(self, status: StatusPayload):
        self.text = status.get("text")
        self.presence = status.get("presence", "Online")

    def __str__(self):
        return f"{self.text} ({self.presence})"

    def __repr__(self) -> str:
        return f"<Status: {self}>"


class Relationship:
    def __init__(self, *, state: ConnectionState, data: RelationshipPayload):
        self._state = state
        self.other_user_id = data.get("_id")
        self.status = data.get("status")

    def __str__(self):
        return f"{self.other_user_id} ({self.status})"

    def __repr__(self) -> str:
        return f"<Relationship: {self}>"

    def _update(self, payload: RelationshipPayload) -> None:
        self.status = payload.get("status")

    async def friend_request(self) -> None:
        """Send or accept a friend request to the user."""
        res = self._state.http.friend_request(self.other_user_id)
        self.status = res

    async def remove_friend(self) -> None:
        """Deny or remove friend."""
        res = self._state.http.remove_friend(self.other_user_id)
        self.status = res

    async def unblock(self) -> None:
        """Unblock user."""
        res = self._state.http.unblock_user(self.other_user_id)
        self.status = res

    async def block(self) -> None:
        """Block user."""
        res = self._state.http.block_user(self.other_user_id)
        self.status = res


class Profile:
    def __init__(
        self, *, state: ConnectionState, user_id: str, data: ProfilePayload
    ) -> None:
        self._state = state
        self.user_id = user_id
        self.content = data.get("content")
        self.background = Attachment(data=data.get("background"), state=state)

    def __str__(self):
        return f"{self.user_id} ({self.content})"

    def __repr__(self) -> str:
        return f"<Profile: {self}>"


class _UserTag:
    __slots__ = "id"
    id: int


class UserBot:
    def __init__(self, data, state) -> None:
        if data is None:
            self.bot = False
            self.owner_id = False
        else:
            self.bot = True
            self.owner_id = data["owner"]
        self._state = state

    def __bool__(self) -> bool:
        return self.bot

    @property
    def owner(self):
        if self.bot:
            return self._state.get_user(self.owner_id)
        return None


class PartialUser(Unique, _UserTag, Messageable):
    def __init__(
        self,
        id: str,
    ) -> None:
        self.id = id
        self.status = Status({"presense": "Offline"})

    def __repr__(self) -> str:
        return f"<PartialUser id={self.id!r}>"

    def __str__(self) -> str:
        return self.id


class BaseUser(PartialUser):
    __slots__ = (
        "name",
        "id",
        "_badges",
        "_state",
        "online",
        "_bot",
        "status",
        "our_relation",
        "relationships",
        "flags",
        "_profile",
    )

    if TYPE_CHECKING:
        name: str
        id: int
        _state: ConnectionState
        _badges: int
        online: bool
        _bot: Optional[UserBot]
        status: Status
        our_relation: Relationship
        relationships: list[Relationship]
        flags: int
        _profile: Optional[Profile]

    def __init__(self, *, state: ConnectionState, data: UserPayload) -> None:
        self._state = state
        self._create(data)

    def __repr__(self) -> str:
        return f"<BaseUser id={self.id} name={self.name!r} bot={self.bot!r}>"

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, _UserTag) and other.id == self.id

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def _create(self, data: UserPayload):
        self.name = data.get("username")
        self.id = data.get("_id")
        self._badges = data.get("badges")
        self.online = data.get("online")
        self._bot = UserBot(data.get("bot"), self._state)
        self.status = Status(data.get("status", {"presense": "Offline"}))
        self.flags = data.get("flags")
        self._profile: Optional[Profile] = None
        self.our_relation = Relationship(
            state=self._state, data={"status": data.get("relationship"), "_id": self.id}
        )
        self.relationships: list[Relationship] = []
        for relationship in data.get("relationships", []):
            self.relationships.append(
                Relationship(state=self._state, data=relationship)
            )

    def _update(self, data: UserUpdate) -> None:
        self.name = data.get("username", self.name)
        self._badges = data.get("badges", self._badges)
        self.online = data.get("online", self.online)
        if "status" in data:
            self.status = Status(data.get("status"))
        if "relationships" in data:
            for relationship in data["relationships"]:
                rel = utils.find(
                    lambda r: r.other_user_id == relationship.get("_id"),
                    self.relationships,
                )
                if rel:
                    rel._update(relationship)
                else:
                    self.relationships.append(Relationship(relationship))
        if "relationship" in data:
            self.our_relation = Relationship(
                {"status": data.get("relationship"), "_id": self.id}
            )
        if "profile.content" in data:
            self._profile.content = data.get("profile.content")
        if "profile.background" in data:
            self._profile.background = Attachment(data=data.get("profile.background"))

    @classmethod
    def _copy(cls: Type[BU], user: BU) -> BU:
        self = cls.__new__(cls)

        self.name = user.name
        self.id = user.id
        self._badges = user._badges
        self._state = user._state
        self.online = user.online

        return self

    @property
    def mention(self) -> str:
        """:class:`str`: Returns a string that allows you to mention the given user."""
        return f"#{self.id}"

    @property
    def display_name(self) -> str:
        """:class:`str`: Returns the user's display name.

        For regular users this is just their username, but
        if they have a server specific nickname then that
        is returned instead.
        """
        return self.name

    @property
    def bot(self) -> bool:
        return bool(self._bot)

    def get_relationship(self, user_id: str) -> Optional[Relationship]:
        """Get the relationship with a user

        Parameters
        ----------
        user_id : str
            User ID

        Returns
        -------
        Optional[Relationship]
            Our relationship with them
        """
        rel = utils.find(
            lambda r: r.other_user_id == User,
            self.relationships,
        )
        return rel

    def mentioned_in(self, message: Message) -> bool:
        """Checks if the user is mentioned in the specified message.

        Parameters
        -----------
        message: :class:`Message`
            The message to check if you're mentioned in.

        Returns
        -------
        :class:`bool`
            Indicates if the user is mentioned in the message.
        """

        return any(user.id == self.id for user in message.mentions)

    async def get_profile(self) -> Profile:
        if self._profile is None:
            profile_data = await self._state.http.get_user_profile(self.id)
            self._profile = Profile(
                data=profile_data, state=self._state, user_id=self.id
            )
        return self._profile


class ClientUser(BaseUser):
    def __init__(self, *, state: ConnectionState, data: UserPayload) -> None:
        super().__init__(state=state, data=data)

    def __repr__(self) -> str:
        return f"<ClientUser id={self.id} name={self.name!r}  bot={self.bot}>"

    def _update(self, data: UserPayload) -> None:
        super()._update(data)

    async def edit(self, *, status: Optional[str] = None) -> ClientUser:
        payload = {}

        if status is not None:
            payload["status"] = {"text": status}
        else:
            payload["delete"] = "StatusText"
        await self._state.http.edit_self(payload)


class User(BaseUser, Messageable):
    def __init__(self, data: UserPayload, state: ConnectionState):
        super().__init__(state=state, data=data)

    def __repr__(self) -> str:
        return f"<User id={self.id!r} name={self.name!r}>"

    def __str__(self) -> str:
        return self.name

    @classmethod
    def _copy(cls, user: User):
        self = super()._copy(user)
        self._stored = False
        return self

    async def _get_channel(self) -> DMChannel:
        ch = await self.create_dm()
        return ch

    @property
    def dm_channel(self) -> Optional[DMChannel]:
        """Optional[:class:`DMChannel`]: Returns the channel associated with this user if it exists.

        If this returns ``None``, you can create a DM channel by calling the
        :meth:`create_dm` coroutine function.
        """
        return self._state.get_channel(self.id)

    async def create_dm(self) -> DMChannel:
        """|coro|
        Creates a :class:`DMChannel` with this user.

        Returns
        -------
        :class:`.DMChannel`
            The channel that was created.
        """
        found = self.dm_channel
        if found is not None:
            return found

        state = self._state
        data: DMChannelPayload = await state.http.open_dm(self.id)
        return state._add_channel_from_data(data)
