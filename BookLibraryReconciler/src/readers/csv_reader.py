"""
Reads the exported Calibre CSV file.
"""

import csv
from pathlib import Path


class CSVReader:

    def __init__(self, csv_path):

        self.csv_path = Path(csv_path)
        self.books = []

    def load(self):

        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found:\n{self.csv_path}")

        with open(
            self.csv_path,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as csv_file:

            reader = csv.DictReader(csv_file)

            self.books = list(reader)

        return self.books

    def column_names(self):

        if not self.books:
            return []

        return list(self.books[0].keys())

    def total_books(self):

        return len(self.books)