"""
Series Model
"""

from dataclasses import dataclass


@dataclass
class Series:

    id: int = 0

    name: str = ""

    sort: str = ""

    link: str = ""

    def __str__(self):

        return self.name
