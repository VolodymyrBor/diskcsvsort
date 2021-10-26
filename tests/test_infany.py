import math
import operator

import pytest

from diskcsvsort.infany import InfAny, infany


class TestInfAny:

    _values = (
        None,
        100,
        100.5,
        ['item'],
        {'item'},
        {'key': 'item'},
        ('item', ),
        math.inf,
        -math.inf,
    )

    def test_singleton(self):
        assert infany is InfAny()
        assert -infany is InfAny(is_negative=True)

    @pytest.mark.parametrize(['operator_', 'value', 'result'], (
        *((operator.ge, value, True) for value in _values),
        *((operator.gt, value, True) for value in _values),
        *((operator.eq, value, False) for value in _values),
        *((operator.le, value, False) for value in _values),
        *((operator.lt, value, False) for value in _values),
    ))
    def test_positive_infany(self, operator_, value, result):
        assert operator_(infany, value) == result

    @pytest.mark.parametrize(['operator_', 'value', 'result'], (
        *((operator.ge, value, False) for value in _values),
        *((operator.gt, value, False) for value in _values),
        *((operator.eq, value, False) for value in _values),
        *((operator.le, value, True) for value in _values),
        *((operator.lt, value, True) for value in _values),
    ))
    def test_negative_infany(self, operator_, value, result):
        assert operator_(-infany, value) == result
