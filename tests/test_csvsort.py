import csv
import sys
import random
import operator
from pathlib import Path
from unittest import mock
from itertools import zip_longest, chain, permutations

import pytest

from tests.conftest import assert_sorted_csv
from diskcsvsort import CSVSort
from diskcsvsort.temp import get_path_tempfile
from diskcsvsort.errors import CSVSortError, CSVFileEmptyError


class TestCSVSort:

    def test_save_csv(self, tmp_path):
        header = ['A', 'B', 'C']
        rows = [
            {col: str(i) for col in header}
            for i in range(5)
        ]
        csvsort = CSVSort(
            src=Path('path/folder'),
            workdir=tmp_path,
            key=lambda x: x,
        )
        with get_path_tempfile(suffix='.csv', directory=tmp_path) as path_tempfile:
            csvsort._save_csv(rows=rows, filepath=path_tempfile, header=header)
            with path_tempfile.open('r', encoding='utf-8') as tmpfile:
                reader = csv.DictReader(tmpfile)
                assert reader.fieldnames == header
                for row, expected in zip_longest(reader, rows):
                    assert row == expected

    def test_reached_memory_limit(self, tmp_path):
        header = ['A', 'B', 'C']
        rows = [
            {col: str(i) for col in header}
            for i in range(5)
        ]

        memory_usage = sum(sys.getsizeof(row) for row in rows)

        csvsort = CSVSort(
            src=Path('path/folder'),
            workdir=tmp_path,
            key=lambda x: x,
            memory_limit=memory_usage / 2,
        )
        with get_path_tempfile(suffix='.csv', directory=tmp_path) as path:
            csvsort._save_csv(rows=rows, filepath=path, header=header)
            assert csvsort._reached_memory_limit(path)

            csvsort._memory_limit = memory_usage
            assert not csvsort._reached_memory_limit(path)

    def test_merge_csv(self, tmp_path):
        header = ['A', 'B', 'C']
        rows1 = [
            {col: str(i) for col in header}
            for i in range(5)
        ]
        rows2 = [
            {col: str(i) for col in header}
            for i in range(5, 10)
        ]

        csvsort = CSVSort(
            src=Path('path/folder'),
            workdir=tmp_path,
            key=lambda x: x,
        )
        with (
            get_path_tempfile(suffix='.csv', directory=tmp_path) as path1,
            get_path_tempfile(suffix='.csv', directory=tmp_path) as path2,
            get_path_tempfile(suffix='.csv', directory=tmp_path) as tmp_dest,
        ):
            csvsort._save_csv(rows=rows1, filepath=path1, header=header)
            csvsort._save_csv(rows=rows2, filepath=path2, header=header)
            csvsort._merge_csvs(tmp_dest, path1, path2)

            with tmp_dest.open('r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                assert reader.fieldnames == header
                for row, expected in zip_longest(reader, chain(rows1, rows2)):
                    assert row == expected

    def test_merge_csv_with_deleting(self, tmp_path):
        header = ['A', 'B', 'C']
        rows1 = [
            {col: str(i) for col in header}
            for i in range(5)
        ]
        rows2 = [
            {col: str(i) for col in header}
            for i in range(5, 10)
        ]

        csvsort = CSVSort(
            src=Path('path/folder'),
            workdir=tmp_path,
            key=lambda x: x,
        )
        with (
            get_path_tempfile(suffix='.csv', directory=tmp_path) as tmp_dest,
            get_path_tempfile(suffix='.csv', directory=tmp_path, delete=False) as path_tmpfile1,
            get_path_tempfile(suffix='.csv', directory=tmp_path, delete=False) as path_tmpfile2,
        ):
            csvsort._save_csv(rows=rows1, filepath=path_tmpfile1, header=header)
            csvsort._save_csv(rows=rows2, filepath=path_tmpfile2, header=header)
            csvsort._merge_csvs(tmp_dest, path_tmpfile1, path_tmpfile2, delete=True)

            with tmp_dest.open('r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                assert reader.fieldnames == header
                for row, expected in zip_longest(reader, chain(rows1, rows2)):
                    assert row == expected

                assert not path_tmpfile1.exists()
                assert not path_tmpfile2.exists()

    @pytest.mark.parametrize(['key', 'reverse'], (
        *[(operator.itemgetter(*comb), False) for comb in permutations('ABC', 1)],
        *[(operator.itemgetter(*comb), False) for comb in permutations('ABC', 2)],
        *[(operator.itemgetter(*comb), False) for comb in permutations('ABC', 3)],
        *[(operator.itemgetter(*comb), True) for comb in permutations('ABC', 1)],
        *[(operator.itemgetter(*comb), True) for comb in permutations('ABC', 2)],
        *[(operator.itemgetter(*comb), True) for comb in permutations('ABC', 3)],
    ))
    def test_memory_sort(self, key, reverse, tmp_path):
        header = ['A', 'B', 'C']
        rows = [
            {col: str(random.randint(0, 100)) for col in header}
            for _ in range(5)
        ]

        def _int_key(row: dict):
            value = key(row)
            if isinstance(value, tuple):
                return tuple(map(int, value))
            else:
                return int(value)

        csvsort = CSVSort(
            src=Path('path/folder'),
            workdir=tmp_path,
            key=_int_key,
            reverse=reverse,
        )
        with get_path_tempfile(suffix='.csv', directory=tmp_path) as filepath:
            csvsort._save_csv(rows=rows, filepath=filepath, header=header)
            csvsort._memory_sort(filepath)
            assert_sorted_csv(filepath, reverse=reverse, key=_int_key)

    @pytest.mark.parametrize(['key', 'reverse'], (
        *[(operator.itemgetter(*comb), False) for comb in permutations('ABC', 1)],
        *[(operator.itemgetter(*comb), False) for comb in permutations('ABC', 2)],
        *[(operator.itemgetter(*comb), False) for comb in permutations('ABC', 3)],
        *[(operator.itemgetter(*comb), True) for comb in permutations('ABC', 1)],
        *[(operator.itemgetter(*comb), True) for comb in permutations('ABC', 2)],
        *[(operator.itemgetter(*comb), True) for comb in permutations('ABC', 3)],
    ))
    def test_sort(self, key, reverse, tmp_path):
        header = ['A', 'B', 'C']
        rows = [
            {col: str(random.randint(0, 100)) for col in header}
            for _ in range(1000)
        ]

        memory_usage = sum(sys.getsizeof(row) for row in rows)

        def _int_key(row: dict):
            value = key(row)
            if isinstance(value, tuple):
                return tuple(map(int, value))
            else:
                return int(value)

        with get_path_tempfile(suffix='.csv', directory=tmp_path) as filepath:
            csvsort = CSVSort(
                src=filepath,
                workdir=tmp_path,
                key=_int_key,
                reverse=reverse,
                memory_limit=memory_usage / 5,
            )
            csvsort._save_csv(rows=rows, filepath=filepath, header=header)
            csvsort.apply()
            assert_sorted_csv(filepath, reverse=reverse, key=_int_key)

    def test_merge_empty_csv(self, tmp_path):
        csvsort = CSVSort(
            src=Path('path/folder'),
            workdir=tmp_path,
            key=lambda x: x,
        )
        with (
            get_path_tempfile(suffix='.csv', directory=tmp_path) as path_tmpfile1,
            get_path_tempfile(suffix='.csv', directory=tmp_path) as path_tmpfile2,
            get_path_tempfile(suffix='.csv', directory=tmp_path) as tmp_dest,
        ):
            with pytest.raises(CSVFileEmptyError):
                csvsort._merge_csvs(tmp_dest, path_tmpfile1, path_tmpfile2)

    def test_sort_empty_csv(self, tmp_path):
        with get_path_tempfile(suffix='.csv', directory=tmp_path) as src:
            csvsort = CSVSort(
                src=src,
                workdir=tmp_path,
                key=lambda x: x,
            )
            with pytest.raises(CSVFileEmptyError):
                csvsort.apply()

    def test_disk_sort_empty_csv(self, tmp_path):
        csvsort = CSVSort(
            src=Path('path/folder'),
            workdir=tmp_path,
            key=lambda x: x,
        )
        with get_path_tempfile(suffix='.csv', directory=tmp_path) as filepath:
            with pytest.raises(CSVFileEmptyError):
                csvsort._disk_sort(filepath)

    def test_disk_sort_csv_only_header(self, tmp_path):
        csvsort = CSVSort(
            src=Path('path/folder'),
            workdir=tmp_path,
            key=lambda x: x,
        )
        with get_path_tempfile(suffix='.csv', directory=tmp_path) as filepath:
            csvsort._save_csv({}, filepath, header=['A', 'B', 'C'])
            with pytest.raises(CSVFileEmptyError):
                csvsort._disk_sort(filepath)

    def test_disk_tiny_memory_limit(self, tmp_path):
        with get_path_tempfile(suffix='.csv', directory=tmp_path) as filepath:
            csvsort = CSVSort(
                src=filepath,
                workdir=tmp_path,
                key=operator.itemgetter('A'),
                memory_limit=1,  # 1 Byte
            )

            csvsort._save_csv([{'A': 'B'}, {'A': 'A'}], filepath, header=['A'])  # tiny memory usage

            with pytest.raises(CSVSortError):
                csvsort.apply()

    def test_recursion_err(self, tmp_path):
        csvsort = CSVSort(
            src=Path('file'),
            workdir=tmp_path,
            key=lambda x: x,
            memory_limit=1,
        )
        csvsort._disk_sort = mock.MagicMock(side_effect=RecursionError)
        csvsort._reached_memory_limit = mock.MagicMock(return_value=True)
        csvsort._csv_is_sorted = mock.MagicMock(return_value=None)
        with pytest.raises(CSVSortError):
            csvsort.apply()

    def test_memory_sort_empty_csv(self, tmp_path):
        with get_path_tempfile(suffix='.csv', directory=tmp_path) as filepath:
            csvsort = CSVSort(
                src=filepath,
                workdir=tmp_path,
                key=lambda x: x,
                memory_limit=1,
            )
            csvsort._reached_memory_limit = mock.MagicMock(return_value=False)
            csvsort._csv_is_sorted = mock.MagicMock(return_value=None)
            with pytest.raises(CSVSortError):
                csvsort.apply()
