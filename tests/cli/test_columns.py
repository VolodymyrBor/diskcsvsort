import datetime as dt

import pytest

from diskcsvsort.cli import columns


class TestColumns:

    @pytest.mark.parametrize(['strtype', 'parameter', 'column_cls'], (
        ('str', None, columns.StrColumn),
        ('int', None, columns.IntColumn),
        ('float', None, columns.FloatColumn),
        ('date(%Y-%m-%d)', '%Y-%m-%d', columns.DateColumn),
        ('time(%H:%M:%S)', '%H:%M:%S', columns.TimeColumn),
        ('datetime(%Y-%m-%d %H:%M:%S)', '%Y-%m-%d %H:%M:%S', columns.DateTimeColumn),
    ))
    def test_get_column(self, strtype, parameter, column_cls):
        column = columns.get_column(strtype)
        assert isinstance(column, column_cls)
        assert column._parameter == parameter

    def test_get_not_exit_column(self):
        with pytest.raises(ValueError):
            columns.get_column('not_exist_column')

    @pytest.mark.parametrize(['strtype', 'value', 'result'], (
        ('int', '5', 5),
        ('float', '10.5', 10.5),
        ('str', 'word word', 'word word'),
        (
            'date(%Y-%m-%d)',
            '2022-08-26',
            dt.datetime.strptime('2022-08-26', '%Y-%m-%d').date()
        ),
        (
            'time(%H:%M:%S)',
            '18:05:25',
            dt.datetime.strptime('18:05:25', '%H:%M:%S').time()
        ),
        (
            'datetime(%Y-%m-%d %H:%M:%S)',
            '2022-08-26 18:05:25',
            dt.datetime.strptime('2022-08-26 18:05:25', '%Y-%m-%d %H:%M:%S')
        ),
    ))
    def test_ok_col_to_python(self, strtype, value, result):
        column = columns.get_column(strtype)
        assert column.to_python(value) == result

    @pytest.mark.parametrize(['strtype', 'value'], (
        ('int', 'string'),
        ('float', 'string'),
        ('date(%Y-%m-%d)', '2022:08-26'),  # bad format
        ('date(%Y-%m-%d)', 'string'),  # not dated
        ('time(%H:%M:%S)', '2022:08-26'),  # bad format
        ('datetime(%Y-%m-%d %H:%M:%S)', '2022-08-26T18:05:25'),  # bad format
        ('datetime(%Y-%m-%d %H:%M:%S)', 'string'),  # not date
    ))
    def test_bad_col_to_python(self, strtype, value):
        column = columns.get_column(strtype)
        with pytest.raises(ValueError):
            column.to_python(value)
