"""
Application Bootstrap

The single place that wires the layers together:

    Database  ->  Repositories (gateways)  ->  Services

Callers depend on Application, not on DatabaseManager or any repository
directly - that keeps the wiring in one place and makes each layer easy
to swap out or mock in tests.
"""

from config.settings import LIBRARY_ROOT, METADATA_DB
from core.database import DatabaseManager
from repositories.book_repository import BookRepository
from services.library_service import LibraryService


class Application:

    def __init__(self, library_root=None, database_path=None):

        self.library_root = library_root or LIBRARY_ROOT
        self.database_path = database_path or METADATA_DB

        self.database = None
        self.book_repository = None
        self.library_service = None

    # ---------------------------------------------------------

    def start(self):

        self.database = DatabaseManager(self.database_path)
        self.database.connect()

        self.book_repository = BookRepository(self.database)
        self.library_service = LibraryService(self.book_repository)

        return self

    # ---------------------------------------------------------

    def stop(self):

        if self.database:
            self.database.close()

    # ---------------------------------------------------------

    def __enter__(self):

        return self.start()

    def __exit__(self, exc_type, exc_value, traceback):

        self.stop()
