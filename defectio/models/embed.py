from __future__ import annotations

from typing import Any, Dict, Final, Protocol, TYPE_CHECKING, TypeVar, Union, Mapping

__all__ = (
    'Embed',
)


class _EmptyEmbed:
    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return 'Embed.Empty'

    def __len__(self) -> int:
        return 0


EmptyEmbed: Final = _EmptyEmbed()


class EmbedProxy:
    def __init__(self, layer: Dict[str, Any]):
        self.__dict__.update(layer)

    def __len__(self) -> int:
        return len(self.__dict__)

    def __repr__(self) -> str:
        inner = ', '.join((f'{k}={v!r}' for k, v in self.__dict__.items() if not k.startswith('_')))
        return f'EmbedProxy({inner})'

    def __getattr__(self, attr: str) -> _EmptyEmbed:
        return EmptyEmbed


E = TypeVar('E', bound='Embed')

if TYPE_CHECKING:
    from defectio.types.embed import EmbedType

    T = TypeVar('T')
    
    MaybeEmpty = Union[T, _EmptyEmbed]

    class _EmbedFooterProxy(Protocol):
        text: MaybeEmpty[str]
        icon_url: MaybeEmpty[str]


    class _EmbedFieldProxy(Protocol):
        name: MaybeEmpty[str]
        value: MaybeEmpty[str]
        inline: bool


    class _EmbedMediaProxy(Protocol):
        url: MaybeEmpty[str]
        proxy_url: MaybeEmpty[str]
        height: MaybeEmpty[int]
        width: MaybeEmpty[int]


    class _EmbedVideoProxy(Protocol):
        url: MaybeEmpty[str]
        height: MaybeEmpty[int]
        width: MaybeEmpty[int]


    class _EmbedProviderProxy(Protocol):
        name: MaybeEmpty[str]
        url: MaybeEmpty[str]


    class _EmbedAuthorProxy(Protocol):
        name: MaybeEmpty[str]
        url: MaybeEmpty[str]
        icon_url: MaybeEmpty[str]
        proxy_icon_url: MaybeEmpty[str]


class Embed:
    """Represents a Defectio embed.

    For ease of use, all parameters that expect a :class:`str` are implicitly
    casted to :class:`str` for you.

    Attributes
    -----------
    title: :class:`str`
        The title of the embed.
        This can be set during initialisation.
    type: :class:`str`
        The type of embed. Usually "text".
        This can be set during initialisation.
    description: :class:`str`
        The description of the embed.
        This can be set during initialisation.
    Empty
        A special sentinel value used by ``EmbedProxy`` and this class
        to denote that the value or attribute is empty.
    """

    __slots__ = (
        'title',
        'type',
        'description',
    )

    Empty: Final = EmptyEmbed

    def __init__(
        self,
        *,
        title: MaybeEmpty[Any] = EmptyEmbed,
        type: EmbedType = 'text',
        description: MaybeEmpty[Any] = EmptyEmbed
    ):

        self.title = title if title is EmptyEmbed else str(title)
        self.type = type if type is EmptyEmbed else str(type)
        self.description = description if description is EmptyEmbed else str(description)

    def copy(self: E) -> E:
        """Returns a shallow copy of the embed."""
        return self.__class__.from_dict(self.to_dict())

    def to_dict(self):
        """Converts this embed object into a dict."""
        
        result = {'type': self.type}

        if self.description: result['description'] = self.description

        if self.title: result['title'] = self.title
        
        return result
    
    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> E:
        """Converts a :class:`dict` to a :class:`Embed` provided it is in the
        format that Defectio expects it to be in.
        Parameters
        -----------
        data: :class:`dict`
            The dictionary to convert into an embed.
        """
        
        # we are bypassing __init__ here since it doesn't apply here
        self: E = cls.__new__(cls)

        title = data.get('title', EmptyEmbed)
        description = data.get('description', EmptyEmbed)
        
        self.type = data["type"]        
        self.title = title if title is EmptyEmbed else str(title)
        self.type = type if type is EmptyEmbed else str(type)
        self.description = description if description is EmptyEmbed else str(description)

        return self
