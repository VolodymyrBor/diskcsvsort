import csv
import sys
import random
import tempfile
import operator
from pathlib import Path
from unittest import mock
from itertools import zip_longest, chain, permutations

import pytest

from tests.conftest import assert_sorted_csv
from diskcsvsort import CSVSort
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
        with tempfile.NamedTemporaryFile('w+', suffix='.csv', dir=tmp_path) as tmpfile:
            csvsort._save_csv(rows=rows, filepath=Path(tmpfile.name), header=header)
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
        with tempfile.NamedTemporaryFile('w+', suffix='.csv', dir=tmp_path) as tmpfile:
            csvsort._save_csv(rows=rows, filepath=Path(tmpfile.name), header=header)
            assert csvsort._reached_memory_limit(Path(tmpfile.name))

            csvsort.memory_limit = memory_usage
            assert not csvsort._reached_memory_limit(Path(tmpfile.name))

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
        with tempfile.NamedTemporaryFile('w+', suffix='.csv', dir=tmp_path) as tmpfile1, \
                tempfile.NamedTemporaryFile('w+', suffix='.csv', dir=tmp_path) as tmpfile2, \
                tempfile.NamedTemporaryFile('w+', suffix='.csv', dir=tmp_path) as tmp_dest:
            csvsort._save_csv(rows=rows1, filepath=Path(tmpfile1.name), header=header)
            csvsort._save_csv(rows=rows2, filepath=Path(tmpfile2.name), header=header)
            csvsort._merge_csvs(Path(tmp_dest.name), Path(tmpfile1.name), Path(tmpfile2.name))

            tmp_dest.seek(0)
            reader = csv.DictReader(tmp_dest)
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
        with tempfile.NamedTemporaryFile('w+', suffix='.csv', dir=tmp_path) as tmp_dest:
            tmpfile1 = tempfile.NamedTemporaryFile('w+', suffix='.csv', dir=tmp_path, delete=False)
            tmpfile2 = tempfile.NamedTemporaryFile('w+', suffix='.csv', dir=tmp_path, delete=False)
            csvsort._save_csv(rows=rows1, filepath=Path(tmpfile1.name), header=header)
            csvsort._save_csv(rows=rows2, filepath=Path(tmpfile2.name), header=header)
            csvsort._merge_csvs(Path(tmp_dest.name), Path(tmpfile1.name), Path(tmpfile2.name), delete=True)

            tmp_dest.seek(0)
            reader = csv.DictReader(tmp_dest)
            assert reader.fieldnames == header
            for row, expected in zip_longest(reader, chain(rows1, rows2)):
                assert row == expected

            assert not Path(tmpfile1.name).exists()
            assert not Path(tmpfile2.name).exists()

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
        with tempfile.NamedTemporaryFile('w+', suffix='.csv', dir=tmp_path) as tmpfile:
            filepath = Path(tmpfile.name)
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
        counter = 0

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
            memory_limit=memory_usage / 5,
        )
        with tempfile.NamedTemporaryFile('w+', suffix='.csv', dir=tmp_path) as tmpfile:
            filepath = Path(tmpfile.name)
            csvsort._save_csv(rows=rows, filepath=filepath, header=header)
            csvsort.filepath = filepath
            csvsort.apply()
            assert_sorted_csv(filepath, reverse=reverse, key=_int_key)

            assert counter == len(rows)

    def test_merge_empty_csv(self, tmp_path):
        csvsort = CSVSort(
            src=Path('path/folder'),
            workdir=tmp_path,
            key=lambda x: x,
        )
        with tempfile.NamedTemporaryFile('w+', suffix='.csv', dir=tmp_path) as tmpfile1, \
                tempfile.NamedTemporaryFile('w+', suffix='.csv', dir=tmp_path) as tmpfile2, \
                tempfile.NamedTemporaryFile('w+', suffix='.csv', dir=tmp_path) as tmp_dest:

            with pytest.raises(CSVFileEmptyError):
                csvsort._merge_csvs(Path(tmp_dest.name), Path(tmpfile1.name), Path(tmpfile2.name))

    def test_sort_empty_csv(self, tmp_path):
        csvsort = CSVSort(
            src=Path('path/folder'),
            workdir=tmp_path,
            key=lambda x: x,
        )
        with tempfile.NamedTemporaryFile('w+', suffix='.csv', dir=tmp_path, delete=False) as tmpfile:
            filepath = Path(tmpfile.name)
            csvsort.filepath = filepath

        csvsort.apply()

    def test_disk_sort_empty_csv(self, tmp_path):
        csvsort = CSVSort(
            src=Path('path/folder'),
            workdir=tmp_path,
            key=lambda x: x,
        )
        with tempfile.NamedTemporaryFile('w+', suffix='.csv', dir=tmp_path, delete=False) as tmpfile:
            filepath = Path(tmpfile.name)
        # empty file
        with pytest.raises(CSVFileEmptyError):
            csvsort._disk_sort(filepath)

    def test_disk_sort_csv_only_header(self, tmp_path):
        csvsort = CSVSort(
            src=Path('path/folder'),
            workdir=tmp_path,
            key=lambda x: x,
        )
        with tempfile.NamedTemporaryFile('w+', suffix='.csv', dir=tmp_path, delete=False) as tmpfile:
            filepath = Path(tmpfile.name)
            csvsort._save_csv({}, filepath, header=['A', 'B', 'C'])
        with pytest.raises(CSVFileEmptyError):
            csvsort._disk_sort(filepath)

    def test_disk_tiny_memory_limit(self, tmp_path):
        with tempfile.NamedTemporaryFile('w+', suffix='.csv', dir=tmp_path, delete=False) as tmpfile:
            filepath = Path(tmpfile.name)
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
        with tempfile.NamedTemporaryFile('w+', suffix='.csv', dir=tmp_path) as tmpfile:
            csvsort = CSVSort(
                src=Path(tmpfile.name),
                workdir=tmp_path,
                key=lambda x: x,
                memory_limit=1,
            )
            csvsort._reached_memory_limit = mock.MagicMock(return_value=False)
            csvsort._csv_is_sorted = mock.MagicMock(return_value=None)
            with pytest.raises(CSVSortError):
                csvsort.apply()
