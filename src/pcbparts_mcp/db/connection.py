"""Database connection management for component database."""

import logging
import sqlite3
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def build_database(data_dir: Path, db_path: Path) -> None:
    """Build the database from scraped data.

    Args:
        data_dir: Directory containing component data files
        db_path: Output database path
    """
    import importlib.util
    script_path = Path(__file__).parent.parent.parent.parent / "scripts" / "build_database.py"

    # Validate script path exists
    if not script_path.exists():
        raise FileNotFoundError(
            f"Build script not found: {script_path}\n"
            f"The build_database.py script is required to create the component database."
        )

    # Load the build script module
    try:
        spec = importlib.util.spec_from_file_location("build_database", script_path)
        if spec is None or spec.loader is None:
            raise ImportError(
                f"Cannot create module spec for {script_path}\n"
                f"The script may have syntax errors or missing dependencies."
            )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except SyntaxError as e:
        logger.error(f"Syntax error in build script: {e}")
        raise ImportError(f"Syntax error in {script_path}: {e}") from e
    except ImportError as e:
        logger.error(f"Failed to load build script: {e}")
        raise

    # Execute the build function
    try:
        if not hasattr(module, "build_database"):
            raise AttributeError(
                f"build_database function not found in {script_path}\n"
                f"The script must define a build_database(data_dir, output, verbose) function."
            )
        module.build_database(data_dir, db_path, verbose=True)
    except Exception as e:
        logger.error(f"Database build failed: {e}")
        raise RuntimeError(
            f"Failed to build database from {data_dir}: {e}\n"
            f"Check that the data directory contains valid component data files."
        ) from e


def load_caches(
    conn: sqlite3.Connection,
) -> tuple[
    dict[int, dict[str, Any]],  # subcategories
    dict[int, dict[str, Any]],  # categories
    dict[str, int],  # subcategory_name_to_id
    dict[str, int],  # category_name_to_id
    dict[int, list[int]],  # category_to_subcategories
]:
    """Load subcategory and category caches with reverse name lookups.

    Args:
        conn: SQLite connection

    Returns:
        Tuple of (subcategories, categories, subcategory_name_to_id, category_name_to_id, category_to_subcategories)
    """
    subcategories: dict[int, dict[str, Any]] = {}
    categories: dict[int, dict[str, Any]] = {}
    subcategory_name_to_id: dict[str, int] = {}
    category_name_to_id: dict[str, int] = {}
    category_to_subcategories: dict[int, list[int]] = {}

    # Load subcategories
    for row in conn.execute("SELECT * FROM subcategories"):
        subcat_id = row["id"]
        cat_id = row["category_id"]
        subcategories[subcat_id] = {
            "name": row["name"],
            "category_id": cat_id,
            "category_name": row["category_name"],
        }
        # Build reverse lookup (lowercase for case-insensitive matching)
        subcategory_name_to_id[row["name"].lower()] = subcat_id
        # Build category -> subcategories mapping
        if cat_id not in category_to_subcategories:
            category_to_subcategories[cat_id] = []
        category_to_subcategories[cat_id].append(subcat_id)

    # Load categories
    for row in conn.execute("SELECT * FROM categories"):
        categories[row["id"]] = {
            "name": row["name"],
            "slug": row["slug"],
        }
        # Build reverse lookup
        category_name_to_id[row["name"].lower()] = row["id"]

    return subcategories, categories, subcategory_name_to_id, category_name_to_id, category_to_subcategories
