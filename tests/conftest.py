import csv
import operator
from pathlib import Path
from typing import Callable


def assert_sorted_csv(filepath: Path, reverse: bool, key: Callable):
    operator_ = operator.ge if reverse else operator.le
    with filepath.open(encoding='utf-8') as file:
        reader = csv.DictReader(file)
        pre_row_key = key(next(reader))
        for row in reader:
            row_key = key(row)
            assert operator_(pre_row_key, row_key)
            pre_row_key = row_key
