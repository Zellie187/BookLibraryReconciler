"""
Calibre Provider

Wraps a book's own existing Calibre metadata as a MetadataProvider, so
it can be compared side-by-side with external providers through the
same interface (see providers/base/provider.py).
"""

from providers.base.provider import MetadataCandidate, MetadataProvider


class CalibreProvider(MetadataProvider):

    name = "calibre"

    def find_candidates(self, book):

        return [
            MetadataCandidate(
                source=self.name,
                title=book.title,
                authors=[author.name for author in book.authors],
                isbn=book.isbn,
                publisher=book.publisher,
                description=book.comments,
            )
        ]
