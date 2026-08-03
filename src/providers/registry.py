"""
Provider Registry

The single source of truth mapping a `--provider` CLI value to its
display label and class. Kept separate from main.py so both the CLI
and the GUI (src/gui/) can import it without a circular dependency -
main.py imports gui.main_window, so gui code can't import back from
main.py.
"""

from providers.googlebooks.googlebooks_provider import GoogleBooksProvider
from providers.internetarchive.internetarchive_provider import InternetArchiveProvider
from providers.openlibrary.openlibrary_provider import OpenLibraryProvider

PROVIDERS = {
    "openlibrary": ("Open Library", OpenLibraryProvider),
    "googlebooks": ("Google Books", GoogleBooksProvider),
    "internetarchive": ("Internet Archive", InternetArchiveProvider),
}
