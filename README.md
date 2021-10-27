# Disk CSV Sort

[![Supported Versions](https://img.shields.io/badge/python-3.10%2B-blue)](https://shields.io/)

## Description

Sort huge CSV files using disk space and RAM together.

For now support only CSV files with **header**.

## Usage

### For example

---

#### CSV file with movies

| name              | year |
|-------------------|------|
| Batman Begins     | 2005 |
| Blade Runner 2049 | 2017 |
| Dune              | 2021 |
| Snatch            | 2000 |

Sort this CSV file that stored in `movies.csv` by `year` and `name`.

**Note**: _order of columns is matter during sorting._

---

### Using diskcsvsort package
```python
from pathlib import Path
from diskcsvsort import CSVSort

csvsort = CSVSort(
    src=Path('movies.csv'),
    key=lambda row: (int(row['year']), row['name']),
)
csvsort.apply()

```

### Using diskcsvsort CLI

    python -m diskcsvsort movies.csv --by year:int --by name:str

**Note**: columns `year` and `name` will be converted to `int` and `str`, respectively.

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
- datetime: `column:datetime(%Y-%m-%d %H:%M:%S)`
- date: `column:datetime(%Y-%m-%d)`
- time: `column:datetime(%H:%M:%S)`


## Algorithm
TODO


## Metrics
TODO
