"""
Provider Configuration

Base URLs and API keys for external metadata providers. None of these
providers make live calls yet (see src/providers/) - this exists so
that work can be wired up without another config pass later.
"""

import os

OPEN_LIBRARY_BASE_URL = "https://openlibrary.org"

GOOGLE_BOOKS_BASE_URL = "https://www.googleapis.com/books/v1"
GOOGLE_BOOKS_API_KEY = os.environ.get("GOOGLE_BOOKS_API_KEY", "")

ISBNDB_BASE_URL = "https://api2.isbndb.com"
ISBNDB_API_KEY = os.environ.get("ISBNDB_API_KEY", "")
