import csv
import random
from pathlib import Path

import typer
from typer.testing import CliRunner

from tests.conftest import assert_sorted_csv
from diskcsvsort.cli import cli_run


class TestCSVSortCLI:

    app = typer.Typer()
    app.command()(cli_run)
    runner = CliRunner()

    DATE_FMT = '%Y-%m-%d'

    @staticmethod
    def _fill_csv(path: Path):
        fieldnames = ['A', 'B', 'C']
        with path.open('w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for _ in range(50):
                writer.writerow({
                    field: random.randint(0, 100)
                    for field in fieldnames
                })

    def test_sort_ok(self, tmp_csv):
        self._fill_csv(tmp_csv)
        result = self.runner.invoke(self.app, [str(tmp_csv)])
        assert result.stdout.strip(' \n') == f'CSV file has been sorted: {tmp_csv}'
        assert_sorted_csv(tmp_csv, key=lambda row: tuple(row.values()), reverse=False)

    def test_sort_by_columns(self, tmp_csv):
        self._fill_csv(tmp_csv)
        result = self.runner.invoke(self.app, [str(tmp_csv), '--by', 'A:int', '--by', 'B:int'])
        assert result.stdout.strip(' \n') == f'CSV file has been sorted: {tmp_csv}'
        assert_sorted_csv(tmp_csv, key=lambda row: (int(row['A']), int(row['B'])), reverse=False)

    def test_sort_by_columns_reverse(self, tmp_csv):
        self._fill_csv(tmp_csv)
        result = self.runner.invoke(self.app, [str(tmp_csv), '--by', 'A:int', '--by', 'B:int', '--reverse'])
        assert result.stdout.strip(' \n') == f'CSV file has been sorted: {tmp_csv}'
        assert_sorted_csv(tmp_csv, key=lambda row: (int(row['A']), int(row['B'])), reverse=True)
