"""
Open Library Provider

Not implemented yet (planned v1.2.0) - conforms to the MetadataProvider
interface so the Metadata Engine can already be written against it.
"""

from config.providers import OPEN_LIBRARY_BASE_URL
from providers.base.provider import MetadataProvider


class OpenLibraryProvider(MetadataProvider):

    name = "openlibrary"

    base_url = OPEN_LIBRARY_BASE_URL

    def find_candidates(self, book):

        raise NotImplementedError("Open Library support is planned for v1.2.0")
