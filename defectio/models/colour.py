import colorsys
import random
from typing import Any
from typing import Optional
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

__all__ = (
    "Colour",
    "Color",
)

CT = TypeVar("CT", bound="Colour")


class Colour:
    __slots__ = ("value",)

    def __init__(self, value: int):
        if not isinstance(value, int):
            raise TypeError(
                f"Expected int parameter, received {value.__class__.__name__} instead."
            )

        self.value: int = value

    def _get_byte(self, byte: int) -> int:
        return (self.value >> (8 * byte)) & 0xFF

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Colour) and self.value == other.value

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return f"#{self.value:0>6x}"

    def __int__(self) -> int:
        return self.value

    def __repr__(self) -> str:
        return f"<Colour value={self.value}>"

    def __hash__(self) -> int:
        return hash(self.value)

    @property
    def r(self) -> int:
        """:class:`int`: Returns the red component of the colour."""
        return self._get_byte(2)

    @property
    def g(self) -> int:
        """:class:`int`: Returns the green component of the colour."""
        return self._get_byte(1)

    @property
    def b(self) -> int:
        """:class:`int`: Returns the blue component of the colour."""
        return self._get_byte(0)

    def to_rgb(self) -> Tuple[int, int, int]:
        """Tuple[:class:`int`, :class:`int`, :class:`int`]: Returns an (r, g, b) tuple representing the colour."""
        return (self.r, self.g, self.b)

    def to_hex(self) -> str:
        """str: returns a str representing the hex code."""
        rgb = self.to_rgb()
        f"#{self.value:0>6x}"

    @classmethod
    def from_rgb(cls: Type[CT], r: int, g: int, b: int) -> CT:
        """Constructs a :class:`Colour` from an RGB tuple."""
        return cls((r << 16) + (g << 8) + b)

    @classmethod
    def from_hsv(cls: Type[CT], h: float, s: float, v: float) -> CT:
        """Constructs a :class:`Colour` from an HSV tuple."""
        rgb = colorsys.hsv_to_rgb(h, s, v)
        return cls.from_rgb(*(int(x * 255) for x in rgb))

    @classmethod
    def from_hex(cls: Type[CT], value: str) -> CT:
        """Constructs a :class:`Colour` from a HEX code."""
        code = value.lstrip("#")
        return cls.from_rgb(*tuple(int(code[i : i + 2], 16) for i in (0, 2, 4)))

    @classmethod
    def default(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0``."""
        return cls(0)

    @classmethod
    def random(
        cls: Type[CT],
        *,
        seed: Optional[Union[int, str, float, bytes, bytearray]] = None,
    ) -> CT:
        """A factory method that returns a :class:`Colour` with a random hue.

        .. note::

            The random algorithm works by choosing a colour with a random hue but
            with maxed out saturation and value.

        Parameters
        ------------
        seed: Optional[Union[:class:`int`, :class:`str`, :class:`float`, :class:`bytes`, :class:`bytearray`]]
            The seed to initialize the RNG with. If ``None`` is passed the default RNG is used.
        """
        rand = random if seed is None else random.Random(seed)
        return cls.from_hsv(rand.random(), 1, 1)

    @classmethod
    def teal(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0x1abc9c``."""
        return cls(0x1ABC9C)

    @classmethod
    def dark_teal(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0x11806a``."""
        return cls(0x11806A)

    @classmethod
    def green(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0x2ecc71``."""
        return cls(0x2ECC71)

    @classmethod
    def dark_green(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0x1f8b4c``."""
        return cls(0x1F8B4C)

    @classmethod
    def blue(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0x3498db``."""
        return cls(0x3498DB)

    @classmethod
    def dark_blue(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0x206694``."""
        return cls(0x206694)

    @classmethod
    def purple(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0x9b59b6``."""
        return cls(0x9B59B6)

    @classmethod
    def dark_purple(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0x71368a``."""
        return cls(0x71368A)

    @classmethod
    def magenta(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0xe91e63``."""
        return cls(0xE91E63)

    @classmethod
    def dark_magenta(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0xad1457``."""
        return cls(0xAD1457)

    @classmethod
    def gold(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0xf1c40f``."""
        return cls(0xF1C40F)

    @classmethod
    def dark_gold(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0xc27c0e``."""
        return cls(0xC27C0E)

    @classmethod
    def orange(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0xe67e22``."""
        return cls(0xE67E22)

    @classmethod
    def dark_orange(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0xa84300``."""
        return cls(0xA84300)

    @classmethod
    def red(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0xe74c3c``."""
        return cls(0xE74C3C)

    @classmethod
    def dark_red(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0x992d22``."""
        return cls(0x992D22)

    @classmethod
    def lighter_grey(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0x95a5a6``."""
        return cls(0x95A5A6)

    lighter_gray = lighter_grey

    @classmethod
    def dark_grey(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0x607d8b``."""
        return cls(0x607D8B)

    dark_gray = dark_grey

    @classmethod
    def light_grey(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0x979c9f``."""
        return cls(0x979C9F)

    light_gray = light_grey

    @classmethod
    def darker_grey(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0x546e7a``."""
        return cls(0x546E7A)

    darker_gray = darker_grey

    @classmethod
    def yellow(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0xFEE75C``."""
        return cls(0xFEE75C)


Color = Colour
