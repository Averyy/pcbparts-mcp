"""Database package for parametric component search.

Provides SQL-based search with attribute filtering that's impossible with the API:
- Range queries: "Vgs(th) < 2.5V", "Capacitance >= 10uF"
- Multi-attribute: "N-channel MOSFET with Id >= 5A AND Rds(on) < 50mOhm"

The database is built from scraped JSONL data on first use.
"""

import json
import logging
import os
import sqlite3
import threading
from pathlib import Path
from typing import Any, Callable, Literal

from ..db_worker import serialized
from ..config import DEFAULT_MIN_STOCK
from ..easyeda_store import FootprintAnswer
from ..search import SearchEngine, SpecFilter, expand_package, resolve_manufacturer, row_to_dict, get_attribute_names
from ..search.spec_filter import like_text
from .connection import build_database, load_caches
from .lookup import get_by_lcsc, get_by_lcsc_batch, get_by_mpn
from .categories import (
    get_subcategory_name,
    get_category_for_subcategory,
    get_categories_for_client,
    find_alternative_candidates,
)
from .attributes import list_attributes
from .stats import get_stats

logger = logging.getLogger(__name__)

__all__ = [
    "ComponentDatabase",
    "get_db",
    "close_db",
]

# Database paths - configurable via environment variables
_PACKAGE_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
DEFAULT_DATA_DIR = Path(os.environ.get("JLCPCB_DATA_DIR", str(_PACKAGE_DATA_DIR)))
DEFAULT_DB_PATH = Path(os.environ.get("JLCPCB_DB_PATH", str(DEFAULT_DATA_DIR / "components.db")))


class ComponentDatabase:
    """SQLite database for parametric component search.

    Thread safety: One connection, serialized by a reentrant lock for the full
    operation, initialization and close. Runtime queries are read-only; WAL is
    configured at initialization, after the optional build of a missing database.
    """

    def __init__(self, db_path: Path | None = None, data_dir: Path | None = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.data_dir = data_dir or DEFAULT_DATA_DIR
        self._conn: sqlite3.Connection | None = None
        self._conn_lock = threading.RLock()  # Protects connection use, initialization and close
        self._subcategories: dict[int, dict[str, Any]] = {}  # id -> {name, category_id, category_name}
        self._categories: dict[int, dict[str, Any]] = {}  # id -> {name, slug}
        # Reverse lookups for name -> id resolution
        self._subcategory_name_to_id: dict[str, int] = {}  # lowercase name -> id
        self._category_name_to_id: dict[str, int] = {}  # lowercase name -> id
        self._category_to_subcategories: dict[int, list[int]] = {}  # category_id -> [subcategory_ids]
        self._search_engine: SearchEngine | None = None
        self._attribute_shares: dict[tuple[tuple[int, ...], tuple[str, ...]], float] = {}
        self._attribute_names: dict[int, set[str]] = {}

    @serialized
    def _ensure_db(self) -> None:
        """Ensure database exists, build if missing. Thread-safe."""
        if self._conn is not None:
            return

        with self._conn_lock:
            # Double-check after acquiring lock
            if self._conn is not None:
                return

            if not self.db_path.exists():
                # Ensure parent directory exists
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
                logger.info(f"Database not found at {self.db_path}, building...")
                build_database(self.data_dir, self.db_path)

            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.execute("PRAGMA journal_mode=WAL")  # match sensor_db/boards_db; docstring guarantee
            self._conn.execute("PRAGMA query_only=ON")
            self._conn.row_factory = sqlite3.Row

            if not self._conn.execute("SELECT 1 FROM sqlite_master WHERE type = 'index' AND name = 'idx_mpn_lower'").fetchone():
                logger.warning(
                    "Component database %s predates this version: some quiescent-current filters miss parts "
                    "and MPN lookups are slow. Rebuild with .venv/bin/python scripts/build_database.py",
                    self.db_path,
                )

            # Load caches
            (
                self._subcategories,
                self._categories,
                self._subcategory_name_to_id,
                self._category_name_to_id,
                self._category_to_subcategories,
            ) = load_caches(self._conn)

            # Initialize search engine after caches are loaded
            self._search_engine = SearchEngine(
                conn=self._conn,
                subcategories=self._subcategories,
                categories=self._categories,
                subcategory_name_to_id=self._subcategory_name_to_id,
                category_name_to_id=self._category_name_to_id,
                category_to_subcategories=self._category_to_subcategories,
            )

    @serialized
    def close(self) -> None:
        """Close database connection. Thread-safe."""
        with self._conn_lock:
            if self._conn:
                self._conn.close()
                self._conn = None
                self._search_engine = None

    def _get_attribute_names(self, name: str) -> list[str]:
        """Get all possible attribute names for a given name (including aliases)."""
        return get_attribute_names(name)

    @serialized
    def get_subcategory_name(self, subcategory_id: int) -> str | None:
        """Get subcategory name by ID."""
        self._ensure_db()
        return get_subcategory_name(subcategory_id, self._subcategories)

    @serialized
    def get_category_for_subcategory(self, subcategory_id: int) -> tuple[int, str] | None:
        """Get category (id, name) for a subcategory."""
        self._ensure_db()
        return get_category_for_subcategory(subcategory_id, self._subcategories)

    @serialized
    def resolve_subcategory_name(self, name: str) -> int | None:
        """Resolve subcategory name to ID. Case-insensitive, supports partial match."""
        self._ensure_db()
        if self._search_engine:
            return self._search_engine.resolve_subcategory_name(name)
        return None

    @serialized
    def resolve_category_name(self, name: str) -> int | None:
        """Resolve category name to ID. Case-insensitive, supports partial match."""
        self._ensure_db()
        if self._search_engine:
            return self._search_engine.resolve_category_name(name)
        return None

    @serialized
    def _find_similar_subcategories(self, name: str, limit: int = 5) -> list[dict[str, Any]]:
        """Find subcategories similar to the given name (for error suggestions)."""
        self._ensure_db()
        if self._search_engine:
            return self._search_engine._find_similar_subcategories(name, limit)
        return []

    def _expand_package(self, package: str) -> list[str]:
        """Expand package name to include family variants."""
        return expand_package(package)

    def _resolve_manufacturer(self, name: str) -> str:
        """Resolve manufacturer alias to canonical name."""
        return resolve_manufacturer(name)

    @serialized
    def search(
        self,
        query: str | None = None,
        subcategory_id: int | None = None,
        subcategory_name: str | None = None,
        category_id: int | None = None,
        category_name: str | None = None,
        spec_filters: list[SpecFilter] | None = None,
        library_type: str | None = None,
        prefer_no_fee: bool = True,
        min_stock: int = DEFAULT_MIN_STOCK,
        package: str | None = None,
        packages: list[str] | None = None,
        manufacturer: str | None = None,
        mounting_type: str | None = None,
        match_all_terms: bool = True,
        sort_by: Literal["stock", "price", "relevance"] = "stock",
        limit: int = 50,
        offset: int = 0,
        subcategory_ids: list[int] | None = None,
    ) -> dict[str, Any]:
        """
        Search components with parametric filtering.

        Args:
            query: Text search (FTS) for lcsc, mpn, manufacturer, description
            subcategory_id: Filter by subcategory ID (takes precedence over subcategory_name)
            subcategory_name: Filter by subcategory name (case-insensitive, partial match)
            category_id: Filter by category ID (takes precedence over category_name)
            category_name: Filter by category name (case-insensitive, partial match)
            spec_filters: List of SpecFilter for attribute-based filtering
            library_type: Filter by library type - "basic", "preferred", or "extended"
            prefer_no_fee: Sort preference (default True)
            min_stock: Minimum stock quantity
            package: Package filter (exact match, single value)
            packages: Package filter (exact match, multiple values with OR logic)
            manufacturer: Manufacturer filter (exact match)
            mounting_type: Mounting type filter ("Through Hole" or "SMD")
            match_all_terms: FTS matching mode (default True)
            sort_by: "stock" (default), "price", or "relevance" (requires query)
            limit: Max results (default 50)
            offset: Pagination offset
            subcategory_ids: Several subcategories (OR), when neither subcategory_id nor
                subcategory_name is given (the smart parser's "inductor" covers four)

        Returns:
            Search results with metadata
        """
        self._ensure_db()
        if not self._search_engine:
            return {"error": "Database not available", "results": [], "total": 0}

        # Clamp min_stock to match database reality (database only has parts with stock >= DEFAULT_MIN_STOCK)
        # This prevents misleading searches where users think they can find 0-stock parts
        original_min_stock = min_stock
        min_stock = max(min_stock, DEFAULT_MIN_STOCK)

        result = self._search_engine.search(
            query=query,
            subcategory_id=subcategory_id,
            subcategory_name=subcategory_name,
            category_id=category_id,
            category_name=category_name,
            spec_filters=spec_filters,
            library_type=library_type,
            prefer_no_fee=prefer_no_fee,
            min_stock=min_stock,
            package=package,
            packages=packages,
            manufacturer=manufacturer,
            mounting_type=mounting_type,
            match_all_terms=match_all_terms,
            sort_by=sort_by,
            limit=limit,
            offset=offset,
            subcategory_ids=subcategory_ids,
        )

        # Add warning if min_stock was clamped
        if original_min_stock < DEFAULT_MIN_STOCK:
            result["warning"] = (
                f"Database only contains parts with stock >= {DEFAULT_MIN_STOCK}. "
                f"Requested min_stock={original_min_stock} was increased to {DEFAULT_MIN_STOCK}. "
                f"Use jlc_stock_check tool for low-stock or out-of-stock parts."
            )

        return result

    @serialized
    def attribute_share(self, subcategory_ids: list[int], names: list[str]) -> float:
        """Share of the parts in these subcategories (0-1) that state one of these attributes
        (not "-"). Cached: the data only changes with a new database."""
        self._ensure_db()
        key = (tuple(sorted(subcategory_ids)), tuple(sorted(names)))
        if key not in self._attribute_shares:
            if not self._conn or not subcategory_ids or not names:
                return 0.0
            for subcategory_id in subcategory_ids:
                if subcategory_id not in self._attribute_names:
                    self._attribute_names[subcategory_id] = {
                        name.casefold()
                        for row in self._conn.execute(
                            "SELECT attributes FROM components WHERE subcategory_id = ?", (subcategory_id,),
                        )
                        for name, value in json.loads(row[0] or "[]") if value != "-"
                    }
            if not any(name.casefold() in self._attribute_names[i] for i in subcategory_ids for name in names):
                return 0.0
            stated = " OR ".join("(attributes LIKE ? ESCAPE '\\' AND attributes NOT LIKE ? ESCAPE '\\')" for _ in names)
            params: list[Any] = []
            for name in names:
                params += [f'%"{like_text(name)}", "%', f'%"{like_text(name)}", "-"]%']
            row = self._conn.execute(
                f"SELECT COUNT(*), SUM(CASE WHEN {stated} THEN 1 ELSE 0 END) FROM components "
                f"WHERE subcategory_id IN ({','.join('?' * len(subcategory_ids))})",
                [*params, *subcategory_ids],
            ).fetchone()
            self._attribute_shares[key] = (row[1] or 0) / row[0] if row[0] else 0.0
        return self._attribute_shares[key]

    @serialized
    def get_by_lcsc(self, lcsc: str) -> dict[str, Any] | None:
        """Get a single component by LCSC code."""
        self._ensure_db()
        if not self._conn:
            return None
        return get_by_lcsc(self._conn, lcsc, self._subcategories)

    @serialized
    def get_easyeda_seed(self, lcsc: str) -> FootprintAnswer | None:
        """Seeded EasyEDA footprint answer for a part (data/easyeda/footprints.csv), or None."""
        self._ensure_db()
        if not self._conn:
            return None
        try:
            row = self._conn.execute(
                "SELECT has_footprint, symbol_uuid, footprint_uuid, checked_at FROM easyeda_footprints WHERE lcsc = ?",
                (lcsc,),
            ).fetchone()
        except sqlite3.OperationalError:  # a DB built before 0.6.0 has no seed table
            return None
        if row is None:
            return None
        return FootprintAnswer(bool(row["has_footprint"]), row["symbol_uuid"], row["footprint_uuid"], row["checked_at"])

    @serialized
    def easyeda_seed_size(self) -> int:
        """Rows in the seeded EasyEDA footprint table (0 for a DB built before 0.6.0)."""
        self._ensure_db()
        if not self._conn:
            return 0
        try:
            return self._conn.execute("SELECT COUNT(*) FROM easyeda_footprints").fetchone()[0]
        except sqlite3.OperationalError:
            return 0

    @serialized
    def get_by_mpn(self, mpn: str) -> list[dict[str, Any]]:
        """Find components by manufacturer part number.

        Tries exact match, then normalized variants, then FTS fallback.
        """
        self._ensure_db()
        if not self._conn:
            return []
        return get_by_mpn(self._conn, mpn, self._subcategories)

    @serialized
    def get_by_lcsc_batch(self, lcsc_codes: list[str]) -> dict[str, dict[str, Any] | None]:
        """Get multiple components by LCSC codes in a single query."""
        self._ensure_db()
        if not self._conn:
            return {}
        return get_by_lcsc_batch(self._conn, lcsc_codes, self._subcategories)

    @serialized
    def find_alternative_candidates(
        self,
        original: dict[str, Any],
        subcategory: str,
        subcategory_id: int,
        min_stock: int = DEFAULT_MIN_STOCK,
        library_type: str | None = None,
        accept: Callable[[dict[str, Any]], bool] | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Parts that can meet the original's compatibility rules, no-fee first, then by stock.

        find_alternatives adds these to its live search; on a database error it gets none.
        """
        self._ensure_db()
        if not self._conn:
            return []
        try:
            return find_alternative_candidates(
                conn=self._conn,
                subcategories=self._subcategories,
                original=original,
                subcategory=subcategory,
                subcategory_id=subcategory_id,
                min_stock=min_stock,
                library_type=library_type,
                accept=accept,
                limit=limit,
            )
        except sqlite3.Error:
            logger.warning("Alternative candidates query failed for %s", original.get("lcsc"), exc_info=True)
            return []

    def _row_to_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        """Convert a database row to a component dict."""
        return row_to_dict(row, self._subcategories)

    @serialized
    def get_categories_for_client(self) -> list[dict[str, Any]]:
        """Export categories in format expected by JLCPCBClient.set_categories()."""
        self._ensure_db()
        if not self._conn:
            return []
        return get_categories_for_client(self._conn, self._subcategories)

    @serialized
    def list_attributes(
        self,
        subcategory_id: int | None = None,
        subcategory_name: str | None = None,
        sample_size: int = 1000,
    ) -> dict[str, Any]:
        """List available filterable attributes for a subcategory."""
        self._ensure_db()
        if not self._conn:
            return {"error": "Database not available"}
        return list_attributes(
            conn=self._conn,
            subcategories=self._subcategories,
            subcategory_name_to_id=self._subcategory_name_to_id,
            subcategory_id=subcategory_id,
            subcategory_name=subcategory_name,
            sample_size=sample_size,
        )

    @serialized
    def get_stats(self) -> dict[str, Any]:
        """Get database statistics."""
        self._ensure_db()
        if not self._conn:
            return {"error": "Database not available"}
        return get_stats(self._conn, self._categories, self._subcategories)


# Global instance with thread safety
_db: ComponentDatabase | None = None
_db_lock = threading.Lock()


def get_db() -> ComponentDatabase:
    """Get or create the global database instance (thread-safe)."""
    global _db
    if _db is None:
        with _db_lock:
            # Double-check locking pattern
            if _db is None:
                _db = ComponentDatabase()
    return _db


def close_db() -> None:
    """Close the global database instance (thread-safe)."""
    global _db
    with _db_lock:
        if _db:
            _db.close()
            _db = None
