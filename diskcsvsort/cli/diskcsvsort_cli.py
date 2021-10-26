from pathlib import Path
from typing import Iterable, Any

import typer

from .columns import BaseColumn, get_column
from diskcsvsort import CSVSort, errors
from diskcsvsort.infany import infany, InfAny

ALL_COLUMNS = ('*', )


class CLIError(Exception):
    pass


def get_all_values(row: dict) -> tuple:
    return tuple(row.values())


class CSVSortCLI:

    def __init__(
        self,
        src: Path,
        encoding: str,
        reverse: bool,
        memory_limit: float,
        by: Iterable[str],
    ):
        self._by = tuple(by)
        self._memory_limit = memory_limit
        self._src = src
        self._encoding = encoding
        self._reverse = reverse
        try:
            self._columns = None if self._by == ALL_COLUMNS else self._parse_columns()
        except ValueError as err:
            raise CLIError(err)

    def run(self):
        key = get_all_values if self._by == ALL_COLUMNS else self._key
        csvsort = CSVSort(
            src=self._src,
            key=key,
            memory_limit=self._memory_limit,
            reverse=self._reverse,
            encoding=self._encoding,
        )

        try:
            csvsort.apply()
        except errors.CSVSortError as err:
            raise CLIError(err)

    def _parse_columns(self) -> dict[str, BaseColumn]:
        columns = {}
        for item in self._by:
            name, strtype = item.split(':')
            columns[name] = get_column(strtype)
        return columns

    @staticmethod
    def _to_python_or_default(value: str, col: BaseColumn) -> Any | InfAny:
        try:
            return col.to_python(value)
        except ValueError:
            return -infany

    def _key(self, row: dict) -> tuple:
        return tuple(
            self._to_python_or_default(row[name], col)
            for name, col in self._columns.items()
        )


def cli_run(
    src: Path = typer.Argument(..., exists=True, help='CSV file path.'),
    encoding: str = typer.Option('utf-8', help='File encoding.'),
    reverse: bool = typer.Option(False, help='use DSC.'),
    memory_limit: float = typer.Option(300 * 1024 * 1024, help='Memory limit. Default is 300 MB.'),
    by: list[str] = typer.Option(ALL_COLUMNS, help='Columns for sorting. Coma separated.'),
):

    try:
        cli = CSVSortCLI(
            src=src,
            encoding=encoding,
            reverse=reverse,
            memory_limit=memory_limit,
            by=by,
        )
        cli.run()
    except CLIError as err:
        print(f'Error: {err}')
    else:
        print(f'CSV file has been sorted: {src}')
