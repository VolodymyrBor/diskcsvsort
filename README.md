# Disk CSV Sort

[![Supported Versions](https://img.shields.io/badge/python-3.10%2B-blue)](https://shields.io/)

## Description

Sort huge CSV files using disk space and RAM together.

For now support only CSV files with **header**.

## Usage

Sort CSV file `path/to/file.csv` by column `Some Column`.

```python
from pathlib import Path
from diskcsvsort import CSVSort

csvsort = CSVSort(
    src=Path('path/to/file.csv'),
    key=lambda row: row['Some Column'],
)
csvsort.apply()

```

### CLI
Sort CSV file `path/to/file.csv` by columns `col1` and `col2`.

    python -m diskcsvsort path/to/file.csv --by col1,col2


## Algorithm
TODO
