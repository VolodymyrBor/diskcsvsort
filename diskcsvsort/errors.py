"""Disk CSV sort errors"""
from pathlib import Path


class CSVSortError(Exception):
    """Base expression of disk CSV sorting"""


class CSVFileEmptyError(CSVSortError):
    """Exception for case when CSV file is empty"""

    def __init__(self, filepath: Path):
        self.filepath = filepath

    def __str__(self) -> str:
        return f'CSV file is empty: {self.filepath}'
