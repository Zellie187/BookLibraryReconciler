"""
ISBNdb Provider

Not implemented yet (planned v1.2.0) - conforms to the MetadataProvider
interface so the Metadata Engine can already be written against it.
"""

from config.providers import ISBNDB_API_KEY, ISBNDB_BASE_URL
from providers.base.provider import MetadataProvider


class IsbndbProvider(MetadataProvider):

    name = "isbndb"

    base_url = ISBNDB_BASE_URL
    api_key = ISBNDB_API_KEY

    def find_candidates(self, book):

        raise NotImplementedError("ISBNdb support is planned for v1.2.0")
