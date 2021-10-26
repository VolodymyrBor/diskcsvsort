from pathlib import Path

import typer

from diskcsvsort.cli import CLIError, CSVSortCLI, ALL_COLUMNS


def run(
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


if __name__ == '__main__':
    typer.run(run)
