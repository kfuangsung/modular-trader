import enum

from typing_extensions import Self


class CaseInsensitiveEnum(enum.StrEnum):
    """Enum class that provides case insensitive value mapping.

    When an enum value is not found in the class, this class tries to find a
    matching enum value by converting the given value to upper case.

    Attributes:
        _missing_: The class method that is called when an enum value is not
            found in the class. This method is used to implement the case
            insensitive mapping.
    """

    @classmethod
    def _missing_(cls, value: str) -> Self | None:
        """Try to find a matching enum value by converting the given value to
        upper case.

        Args:
            value: The value to look up in the class.

        Returns:
            The enum value if found, otherwise None.
        """
        # for case insensitive input mapping
        return cls.__members__.get(value.upper(), None)


class TradingMode(CaseInsensitiveEnum):
    """The mode of trading.

    Attributes:
        LIVE: Live trading mode.
        PAPER: Paper trading mode.
    """

    LIVE = enum.auto()
    PAPER = enum.auto()


class AssetClass(CaseInsensitiveEnum):
    """
    The class of an asset.

    Attributes:
        STOCK: Stock asset class.
        CRYPTO: Cryptocurrency asset class.
        OPTION: Option asset class.
    """

    STOCK = enum.auto()
    CRYPTO = enum.auto()
    OPTION = enum.auto()
