import enum

from typing_extensions import Self


class CaseInsensitiveEnum(enum.StrEnum):
    @classmethod
    def _missing_(cls, value: str) -> Self | None:
        # for case insensitive input mapping
        return cls.__members__.get(value.upper(), None)


class TradingMode(CaseInsensitiveEnum):
    LIVE = enum.auto()
    PAPER = enum.auto()


class AssetClass(CaseInsensitiveEnum):
    STOCK = enum.auto()
    CRYPTO = enum.auto()
    OPTION = enum.auto()
