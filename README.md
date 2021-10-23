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
`col1` will be converted to python `str` and `col2` will be converted to python `int`.

    python -m diskcsvsort path/to/file.csv --by col1:str --by col2:int

#### Available types:
 - str
 - int
 - float
 - datetime
 - date
 - time

#### Types usage:
- str: `column:str` 
- int: `column:int` 
- float: `column:float` 
- datetime: `column:datetime[%Y-%m-%d %H:%M:%S]`
- date: `column:datetime[%Y-%m-%d]`
- time: `column:datetime[%H:%M:%S]`


## Algorithm
TODO
