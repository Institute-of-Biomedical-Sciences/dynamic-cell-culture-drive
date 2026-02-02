"""Database connection and operations."""

import contextlib
from typing import Optional

import psycopg
from app.config import settings
from psycopg.rows import dict_row


class Database:
    """Database connection manager."""

    def __init__(self):
        """Initialize database connection."""
        self._conn: Optional[psycopg.Connection] = None

    def connect(self):
        """Connect to the database."""
        if self._conn is None or self._conn.closed:
            self._conn = psycopg.connect(settings.database_url, row_factory=dict_row)
        return self._conn

    def close(self):
        """Close database connection."""
        if self._conn and not self._conn.closed:
            self._conn.close()
            self._conn = None

    @contextlib.contextmanager
    def get_connection(self):
        """Get database connection context manager."""
        conn = self.connect()
        try:
            yield conn
        finally:
            pass  # Don't close, reuse connection

    @contextlib.contextmanager
    def get_cursor(self):
        """Get database cursor context manager."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                yield cur
                conn.commit()


# Global database instance
db = Database()
