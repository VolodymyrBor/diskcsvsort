from pathlib import Path
from operator import itemgetter

import typer

from diskcsvsort import CSVSort, errors


ALL_COLUMNS = '*'


def get_values(dict_: dict) -> tuple:
    return tuple(dict_.values())


def run(
    src: Path = typer.Argument(..., exists=True, help='CSV file path.'),
    encoding: str = typer.Option('utf-8', help='File encoding.'),
    reverse: bool = typer.Option(False, help='use DSC.'),
    memory_limit: float = typer.Option(300 * 1024 * 1024, help='Memory limit. Default is 300 MB.'),
    by: str = typer.Option(ALL_COLUMNS, help='Columns for sorting. Coma separated.'),
):
    key = get_values if by == ALL_COLUMNS else itemgetter(*by.split(','))
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
