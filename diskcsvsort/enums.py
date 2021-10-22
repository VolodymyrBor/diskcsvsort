from enum import Enum


class StrEnum(str, Enum):

    @classmethod
    def values(cls) -> tuple[str, ...]:
        return tuple(item.value for item in cls)


class OS(StrEnum):
    WINDOWS = 'Windows'
    LINUX = 'Linux'
