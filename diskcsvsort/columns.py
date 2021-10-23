import re
import datetime as dt
from abc import abstractmethod, ABC
from typing import Pattern, Any, Type


class BaseColumn(ABC):
    _strtype_re: Pattern = NotImplemented

    _has_parameter: bool = False
    _parameter_re: Pattern = re.compile('\[.*]')

    __columns__: dict[Pattern, Type['BaseColumn']] = {}

    def __init__(self, parameter: str | None = None):
        self._parameter = parameter

    @classmethod
    def from_strtype(cls, strtype: str):
        return cls(parameter=cls._fetch_parameter(strtype)) if cls._has_parameter else cls()

    @abstractmethod
    def to_python(self, value: str) -> Any:
        pass

    @classmethod
    def _fetch_parameter(cls, strtype: str) -> str:
        search = cls._parameter_re.search(strtype)
        return search.group(0).strip('[]')

    def __init_subclass__(cls, **kwargs):
        cls.__columns__[cls._strtype_re] = cls


def get_column(strtype: str) -> BaseColumn:
    for strtype_re, col in BaseColumn.__columns__.items():
        if strtype_re.match(strtype):
            return col.from_strtype(strtype)
    else:
        raise ValueError(f'Not supported column type: {strtype}')


def get_columns(columns: dict[str, str]) -> dict[str, BaseColumn]:
    return {
        name: get_column(strtype)
        for name, strtype in columns.items()
    }


class StrColumn(BaseColumn):
    _strtype_re = re.compile('str')

    def to_python(self, value: str) -> str:
        return value


class IntColumn(BaseColumn):
    _strtype_re = re.compile('int')

    def to_python(self, value: str) -> int:
        return int(value)


class FloatColumn(BaseColumn):
    _strtype_re = re.compile('float')

    def to_python(self, value: str) -> float:
        return float(value)


class DateTimeColumn(BaseColumn):
    _has_parameter = True
    _strtype_re = re.compile('datetime\[.*]')

    def to_python(self, value: str) -> dt.datetime:
        return dt.datetime.strptime(value, self._parameter)


class DateColumn(DateTimeColumn):
    _has_parameter = True
    _strtype_re = re.compile('date\[.*]')

    def to_python(self, value: str) -> dt.date:
        return super().to_python(value).date()


class TimeColumn(DateTimeColumn):
    _has_parameter = True
    _strtype_re = re.compile('time\[.*]')

    def to_python(self, value: str) -> dt.time:
        return super().to_python(value).time()
