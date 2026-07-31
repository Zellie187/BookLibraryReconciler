"""
Provider Configuration

Base URLs and API keys for external metadata providers.
"""

import os

OPEN_LIBRARY_BASE_URL = "https://openlibrary.org"
OPEN_LIBRARY_USER_AGENT = "BookLibraryReconciler/1.0 (+https://github.com/Zellie187/BookLibraryReconciler)"
OPEN_LIBRARY_TIMEOUT_SECONDS = 10
OPEN_LIBRARY_CACHE_TTL_SECONDS = 7 * 24 * 60 * 60  # 1 week
OPEN_LIBRARY_MIN_REQUEST_INTERVAL_SECONDS = 1.0

GOOGLE_BOOKS_BASE_URL = "https://www.googleapis.com/books/v1"
GOOGLE_BOOKS_API_KEY = os.environ.get("GOOGLE_BOOKS_API_KEY", "")

ISBNDB_BASE_URL = "https://api2.isbndb.com"
ISBNDB_API_KEY = os.environ.get("ISBNDB_API_KEY", "")
