from typing import Any


class InfAny:
    """InfAny always bigger than another object during the comparison.
    Like math.inf but for any object."""

    _pos_inst: 'InfAny' | None = None
    _neg_inst: 'InfAny' | None = None

    def __new__(cls, is_negative: bool = False):
        if is_negative:
            if not cls._neg_inst:
                cls._neg_inst = super().__new__(cls)
            return cls._neg_inst
        else:
            if not cls._pos_inst:
                cls._pos_inst = super().__new__(cls)
            return cls._pos_inst

    def __init__(self, is_negative: bool = False):
        self._is_negative = is_negative

    def __repr__(self):
        sign = '-' if self._is_negative else '+'
        return f'{sign}{type(self).__name__}'

    def __gt__(self, other: Any):
        return not self._is_negative

    def __lt__(self, other: Any):
        return self._is_negative

    def __ge__(self, other: Any):
        return not self._is_negative

    def __le__(self, other: Any):
        return self._is_negative

    def __eq__(self, other: Any):
        return False

    def __neg__(self) -> 'InfAny':
        return InfAny(is_negative=not self._is_negative)


infany = InfAny()
