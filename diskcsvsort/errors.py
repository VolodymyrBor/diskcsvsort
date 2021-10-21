"""Disk CSV sort errors"""
from pathlib import Path


class CSVSortError(Exception):
    pass


class CSVFileEmptyError(CSVSortError):

    def __init__(self, filepath: Path):
        self.filepath = filepath

    def __str__(self) -> str:
        return f'CSV file is empty: {self.filepath}'
