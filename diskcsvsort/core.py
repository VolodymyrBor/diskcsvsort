import sys
import csv
import operator
import tempfile
from pathlib import Path
from typing import Callable, TypeAlias, Any, NoReturn, Iterable, Sequence

from . import errors
from .temp import get_path_tempfile

_ROW: TypeAlias = dict[str, str]


class CSVSort:

    _operators = [
        operator.lt,
        operator.eq,
        operator.gt,
    ]

    def __init__(
        self,
        src: Path,
        *,
        key: Callable[[_ROW], Any],
        workdir: Path = Path(tempfile.gettempdir()),
        memory_limit: float = 300 * 1024 * 1024,  # 300 mb
        reverse: bool = False,
        encoding: str = 'utf-8',
    ):
        self._encoding = encoding
        self._src = src
        self._key = key
        self._workdir = workdir
        self._memory_limit = memory_limit
        self._reverse = reverse

        self._workdir.mkdir(parents=True, exist_ok=True)

    def apply(self) -> NoReturn:
        try:
            return self._hybrid_sort(self._src)
        except RecursionError as err:
            raise errors.CSVSortError(err)

    def _csv_is_sorted(self, src: Path) -> bool:
        operator_ = operator.ge if self._reverse else operator.le
        with src.open('r', encoding=self._encoding) as file:
            reader = csv.DictReader(file)
            try:
                base_key = self._key(next(reader))
            except StopIteration:
                return False

            for row in reader:
                row_key = self._key(row)
                if not operator_(base_key, row_key):
                    return False
                base_key = row_key
        return True

    def _reached_memory_limit(self, src: Path) -> bool:
        memory_usage = 0
        with src.open('r', encoding=self._encoding) as file:
            for i, row in enumerate(csv.DictReader(file)):
                row_memory_usage = sys.getsizeof(row)
                if row_memory_usage > self._memory_limit:
                    raise errors.CSVSortError(f'Row #{i} use memory {row_memory_usage}'
                                              f'more than memory_limit: {self._memory_limit}')
                memory_usage += row_memory_usage
                if memory_usage > self._memory_limit:
                    return True
        return False

    def _hybrid_sort(self, src: Path) -> Path:
        if self._csv_is_sorted(src):
            return src

        if self._reached_memory_limit(src):
            return self._disk_sort(src)
        else:
            return self._memory_sort(src)

    def _disk_sort(self, src: Path) -> Path:
        files_to_sort: list[Path] = []
        files_to_close = []

        with src.open('r', encoding=self._encoding) as src_file:
            reader = csv.DictReader(src_file)
            if reader.fieldnames is None:
                raise errors.CSVFileEmptyError(src)

            # filter rows to 3 channels:
            #   - rows < base
            #   - rows = base
            #   - rows > base
            channels = []
            for operator_ in self._operators:
                with get_path_tempfile(
                    suffix='.csv',
                    directory=self._workdir,
                    delete=False,
                ) as path_tempfile:
                    temp_file = path_tempfile.open(
                        mode='w',
                        encoding=self._encoding,
                        newline='',
                    )
                    files_to_sort.append(path_tempfile)
                    files_to_close.append(temp_file)
                    writer = csv.DictWriter(temp_file, fieldnames=reader.fieldnames)
                    writer.writeheader()
                    channels.append((writer, operator_))

            try:
                base_row = next(reader)
            except StopIteration:
                raise errors.CSVFileEmptyError(src)

            base_key = self._key(base_row)

            for writer, operator_ in channels:
                if operator_(base_key, base_key):
                    writer.writerow(base_row)
                    break

            for row in reader:
                for writer, operator_ in channels:
                    if operator_(self._key(row), base_key):
                        writer.writerow(row)
                        break

            for file in files_to_close:
                file.close()

            if self._reverse:
                files_to_sort.reverse()

            files_to_merge = map(self._hybrid_sort, files_to_sort)
            self._merge_csvs(src, *files_to_merge, delete=True)
        return src

    def _merge_csvs(self, dest: Path, *csvfiles: Path, delete: bool = False) -> NoReturn:
        need_header = True
        with dest.open('w', encoding=self._encoding, newline='') as dst_file:
            writer = csv.writer(dst_file)
            for csvfile in csvfiles:
                with csvfile.open('r', encoding=self._encoding) as file:
                    reader = csv.reader(file)
                    try:
                        header = next(reader)
                    except StopIteration:
                        raise errors.CSVFileEmptyError(csvfile)
                    if need_header:
                        writer.writerow(header)
                        need_header = False
                    writer.writerows(reader)

                if delete:
                    csvfile.unlink(missing_ok=True)

    def _memory_sort(self, src: Path) -> Path:
        with src.open('r', encoding=self._encoding) as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None:
                raise errors.CSVFileEmptyError(src)
            sorted_rows = sorted(reader, key=self._key, reverse=self._reverse)
        self._save_csv(sorted_rows, filepath=src, header=reader.fieldnames)
        return src

    def _save_csv(self, rows: Iterable[_ROW], filepath: Path, header: Sequence[str]) -> NoReturn:
        with filepath.open('w', encoding=self._encoding, newline='') as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()
            writer.writerows(rows)
