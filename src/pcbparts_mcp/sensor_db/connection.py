"""Database build delegation for sensor database."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def build_sensor_database(data_dir: Path, db_path: Path) -> None:
    """Build the sensor database from scraped JSON data.

    Uses importlib to dynamically load scripts/build_sensor_db.py and call its
    build() function. Same pattern as db/connection.py.

    Args:
        data_dir: Directory containing sensors/ subdirectory with JSON files
        db_path: Output database path
    """
    import importlib.util

    script_path = Path(__file__).parent.parent.parent.parent / "scripts" / "build_sensor_db.py"

    if not script_path.exists():
        raise FileNotFoundError(
            f"Build script not found: {script_path}\n"
            f"The build_sensor_db.py script is required to create the sensor database."
        )

    try:
        spec = importlib.util.spec_from_file_location("build_sensor_db", script_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot create module spec for {script_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except SyntaxError as e:
        logger.error(f"Syntax error in build script: {e}")
        raise ImportError(f"Syntax error in {script_path}: {e}") from e
    except ImportError as e:
        logger.error(f"Failed to load build script: {e}")
        raise

    try:
        if not hasattr(module, "build"):
            raise AttributeError(
                f"build() function not found in {script_path}\n"
                f"The script must define a build(data_dir, output, verbose) function."
            )
        module.build(data_dir, db_path, verbose=True)
    except Exception as e:
        logger.error(f"Sensor database build failed: {e}")
        raise RuntimeError(
            f"Failed to build sensor database from {data_dir}: {e}"
        ) from e
