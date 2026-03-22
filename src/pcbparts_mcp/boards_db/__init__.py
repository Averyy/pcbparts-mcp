"""Boards database package for reference board search.

Provides search across ~285 OSHW reference board schematics with:
- FTS5 full-text search (name, description, key_coverage, ICs, org)
- Parametric filters (tag, org, layers, component search)
- Ranked by component count (more complex boards = more useful references)

The database is built from parsed YAML data on first use.
"""

import logging
import os
import sqlite3
import threading
from pathlib import Path
from typing import Any

from .connection import build_boards_database
from .detail import (
    get_board as _get_board,
    get_consensus as _get_consensus,
    get_tag_consensus as _get_tag_consensus,
    get_stats as _get_stats,
)
from .search import search_boards

logger = logging.getLogger(__name__)

__all__ = [
    "BoardsDatabase",
    "get_boards_db",
    "close_boards_db",
]

# Database paths - configurable via environment variables
_PACKAGE_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
DEFAULT_DATA_DIR = Path(os.environ.get("BOARDS_DATA_DIR", str(_PACKAGE_DATA_DIR)))
DEFAULT_DB_PATH = Path(os.environ.get("BOARDS_DB_PATH", str(DEFAULT_DATA_DIR / "boards.db")))


class BoardsDatabase:
    """SQLite database for reference board search.

    Thread safety: Uses WAL mode + check_same_thread=False.
    Concurrent reads are safe; writes are serialized by SQLite.
    The _conn_lock protects lazy initialization of the connection.
    """

    def __init__(self, db_path: Path | None = None, data_dir: Path | None = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.data_dir = data_dir or DEFAULT_DATA_DIR
        self._conn: sqlite3.Connection | None = None
        self._conn_lock = threading.Lock()

    def _ensure_db(self) -> None:
        """Ensure database exists, build if missing. Thread-safe."""
        if self._conn is not None:
            return

        with self._conn_lock:
            # Double-check after acquiring lock
            if self._conn is not None:
                return

            if not self.db_path.exists():
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
                logger.info(f"Boards database not found at {self.db_path}, building...")
                build_boards_database(self.data_dir, self.db_path)

            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.execute("PRAGMA journal_mode=WAL")

    def close(self) -> None:
        """Close database connection. Thread-safe."""
        with self._conn_lock:
            if self._conn:
                self._conn.close()
                self._conn = None

    def search(
        self,
        query: str | None = None,
        component: str | None = None,
        tag: str | list[str] | None = None,
        org: str | None = None,
        layers: int | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search boards with FTS5 + parametric filters."""
        self._ensure_db()
        if not self._conn:
            return {"error": "Boards database not available", "results": [], "total": 0}

        return search_boards(
            conn=self._conn,
            query=query,
            component=component,
            tag=tag,
            org=org,
            layers=layers,
            limit=limit,
        )

    def get_board(
        self,
        slug: str,
        include_raw: bool = False,
        include_bom: bool = False,
        focus: str | None = None,
    ) -> dict[str, Any] | None:
        """Get board detail by slug."""
        self._ensure_db()
        if not self._conn:
            return {"error": "Boards database not available"}

        return _get_board(
            self._conn, slug,
            include_raw=include_raw, include_bom=include_bom,
            focus=focus, get_consensus_fn=self.get_consensus,
        )

    def get_consensus(self, ic_name: str) -> dict[str, Any] | None:
        """Get cross-board consensus for how an IC is used across all boards."""
        self._ensure_db()
        if not self._conn:
            return None

        return _get_consensus(self._conn, ic_name)

    def get_tag_consensus(self, tag: str) -> dict[str, Any] | None:
        """Get IC consensus across all boards with a given tag."""
        self._ensure_db()
        if not self._conn:
            return None

        return _get_tag_consensus(self._conn, tag)

    def get_stats(self) -> dict[str, Any]:
        """Get database statistics."""
        self._ensure_db()
        if not self._conn:
            return {"error": "Boards database not available"}

        return _get_stats(self._conn)


# Global singleton with thread safety
_db: BoardsDatabase | None = None
_db_lock = threading.Lock()


def get_boards_db() -> BoardsDatabase:
    """Get or create the global boards database instance (thread-safe)."""
    global _db
    if _db is None:
        with _db_lock:
            if _db is None:
                _db = BoardsDatabase()
    return _db


def close_boards_db() -> None:
    """Close the global boards database instance (thread-safe)."""
    global _db
    with _db_lock:
        if _db:
            _db.close()
            _db = None
