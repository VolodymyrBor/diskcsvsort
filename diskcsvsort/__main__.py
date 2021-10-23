from pathlib import Path
from typing import Callable, Any, Iterable

import typer

from diskcsvsort import CSVSort, errors, columns


ALL_COLUMNS = ('*', )


def get_values(dict_: dict) -> tuple:
    return tuple(dict_.values())


def to_python_or_default(value: str, col: columns.BaseColumn) -> Any | None:
    try:
        return col.to_python(value)
    except ValueError:
        return None  # TODO return come inf object


def get_key(columns_: dict[str, columns.BaseColumn]) -> Callable[[dict], tuple[Any, ...]]:

    def _key(dict_: dict) -> tuple[Any, ...]:
        return tuple(
            to_python_or_default(dict_[name], col)
            for name, col in columns_.items()
        )

    return _key


def parse_columns(by: Iterable[str]) -> dict[str, str]:
    columns_ = {}
    for item in by:
        name, strtype = item.split(':')
        columns_[name] = strtype
    return columns_


def run(
    src: Path = typer.Argument(..., exists=True, help='CSV file path.'),
    encoding: str = typer.Option('utf-8', help='File encoding.'),
    reverse: bool = typer.Option(False, help='use DSC.'),
    memory_limit: float = typer.Option(300 * 1024 * 1024, help='Memory limit. Default is 300 MB.'),
    by: list[str] = typer.Option(ALL_COLUMNS, help='Columns for sorting. Coma separated.'),
):
    key = get_values if by == ALL_COLUMNS else get_key(columns.get_columns(parse_columns(by)))
    csvsort = CSVSort(
        src=src,
        encoding=encoding,
        reverse=reverse,
        memory_limit=memory_limit,
        key=key,
    )
    try:
        csvsort.apply()
    except errors.CSVSortError as err:
        print(f'Error: {err}')
    else:
        print(f'CSV file has been sorted: {src}')


if __name__ == '__main__':
    typer.run(run)
