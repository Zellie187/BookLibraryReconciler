"""
Format File Model

Represents a single on-disk file for a book (one per format/extension).
"""

from dataclasses import dataclass


@dataclass
class FormatFile:

    format: str = ""

    name: str = ""

    size: int = 0

    @property
    def filename(self):

        return f"{self.name}.{self.format.lower()}"

    def __str__(self):

        return self.filename
