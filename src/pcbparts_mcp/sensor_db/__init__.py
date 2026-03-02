"""Sensor database package for sensor IC/module recommendation.

Provides search across ~1,500 sensor ICs and modules with:
- FTS5 full-text search (name, description, manufacturer)
- Parametric filters (measure, type, protocol, platform)
- Ranked by platform support count

The database is built from scraped JSON data on first use.
"""

import logging
import os
import sqlite3
import threading
from pathlib import Path
from typing import Any

from .connection import build_sensor_database
from .search import search_sensors

logger = logging.getLogger(__name__)

__all__ = [
    "SensorDatabase",
    "get_sensor_db",
    "close_sensor_db",
]

# Database paths - configurable via environment variables
_PACKAGE_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
DEFAULT_DATA_DIR = Path(os.environ.get("SENSOR_DATA_DIR", str(_PACKAGE_DATA_DIR)))
DEFAULT_DB_PATH = Path(os.environ.get("SENSOR_DB_PATH", str(DEFAULT_DATA_DIR / "sensor.db")))


class SensorDatabase:
    """SQLite database for sensor IC/module recommendation.

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
                logger.info(f"Sensor database not found at {self.db_path}, building...")
                build_sensor_database(self.data_dir, self.db_path)

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
        measure: str | list[str] | None = None,
        type: str | None = None,
        protocol: str | None = None,
        platform: str | None = None,
        limit: int = 15,
    ) -> dict[str, Any]:
        """Search sensors with FTS5 + parametric filters.

        Args:
            query: Free-text search (name, description, manufacturer)
            measure: What to measure (single or list for AND)
            type: Sensing technology filter
            protocol: Interface protocol filter
            platform: Platform support filter
            limit: Max results (default 15)

        Returns:
            {"total": N, "results": [...]}
        """
        self._ensure_db()
        if not self._conn:
            return {"error": "Sensor database not available", "results": [], "total": 0}

        return search_sensors(
            conn=self._conn,
            query=query,
            measure=measure,
            type=type,
            protocol=protocol,
            platform=platform,
            limit=limit,
        )

    def get_stats(self) -> dict[str, Any]:
        """Get database statistics."""
        self._ensure_db()
        if not self._conn:
            return {"error": "Sensor database not available"}

        total = self._conn.execute("SELECT COUNT(*) FROM sensors").fetchone()[0]

        platforms = {
            row[0]: row[1]
            for row in self._conn.execute(
                "SELECT platform, COUNT(*) FROM sensor_platforms GROUP BY platform ORDER BY 2 DESC"
            )
        }

        measures = {
            row[0]: row[1]
            for row in self._conn.execute(
                "SELECT measure, COUNT(*) FROM sensor_measures GROUP BY measure ORDER BY 2 DESC LIMIT 20"
            )
        }

        return {
            "total_sensors": total,
            "platforms": platforms,
            "top_measures": measures,
        }


# Global singleton with thread safety
_db: SensorDatabase | None = None
_db_lock = threading.Lock()


def get_sensor_db() -> SensorDatabase:
    """Get or create the global sensor database instance (thread-safe)."""
    global _db
    if _db is None:
        with _db_lock:
            if _db is None:
                _db = SensorDatabase()
    return _db


def close_sensor_db() -> None:
    """Close the global sensor database instance (thread-safe)."""
    global _db
    with _db_lock:
        if _db:
            _db.close()
            _db = None
