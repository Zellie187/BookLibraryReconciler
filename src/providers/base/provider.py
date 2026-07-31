"""
Metadata Provider Interface

Every metadata source (Calibre itself, Open Library, Google Books, ...)
implements this same interface, so the Metadata Engine and Repair
Engine can work with any of them interchangeably.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class MetadataCandidate:
    """
    One provider's version of a book's metadata, for comparison against
    what the library already has.
    """

    source: str = ""
    title: str = ""
    authors: list[str] = field(default_factory=list)
    isbn: str = ""
    publisher: str = ""
    description: str = ""
    cover_url: str = ""


class ProviderUnavailableError(Exception):
    """
    Raised when a provider couldn't be reached or its response
    couldn't be understood (network failure, timeout, malformed
    response) - distinct from a confirmed "not found", which returns
    an empty list instead of raising.
    """


class MetadataProvider(ABC):

    name = "base"

    @abstractmethod
    def find_candidates(self, book):
        """
        Return a list of MetadataCandidate for the given Book, best
        match first. Return an empty list when nothing is found.
        Raise ProviderUnavailableError when the provider itself
        couldn't be reached or its response was unusable.
        """

        raise NotImplementedError
