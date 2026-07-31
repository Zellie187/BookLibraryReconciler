"""
Google Books Provider

Not implemented yet (planned v1.2.0) - conforms to the MetadataProvider
interface so the Metadata Engine can already be written against it.
"""

from config.providers import GOOGLE_BOOKS_API_KEY, GOOGLE_BOOKS_BASE_URL
from providers.base.provider import MetadataProvider


class GoogleBooksProvider(MetadataProvider):

    name = "googlebooks"

    base_url = GOOGLE_BOOKS_BASE_URL
    api_key = GOOGLE_BOOKS_API_KEY

    def find_candidates(self, book):

        raise NotImplementedError("Google Books support is planned for v1.2.0")
