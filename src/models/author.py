"""
Author Model

Represents a single author.
"""

from dataclasses import dataclass


@dataclass
class Author:

    id: int = 0

    name: str = ""

    sort: str = ""

    link: str = ""

    def __str__(self):

        return self.name
