"""Database build delegation for boards database."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def build_boards_database(data_dir: Path, db_path: Path) -> None:
    """Build the boards database from parsed YAML data.

    Uses importlib to dynamically load scripts/build_boards_db.py and call its
    build() function. Same pattern as sensor_db/connection.py.

    Args:
        data_dir: Directory containing boards/ subdirectory with YAML files
        db_path: Output database path
    """
    import importlib.util

    script_path = Path(__file__).parent.parent.parent.parent / "scripts" / "build_boards_db.py"

    if not script_path.exists():
        raise FileNotFoundError(
            f"Build script not found: {script_path}\n"
            f"The build_boards_db.py script is required to create the boards database."
        )

    try:
        spec = importlib.util.spec_from_file_location("build_boards_db", script_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot create module spec for {script_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except SyntaxError as e:
        logger.error(f"Syntax error in build script: {e}")
        raise ImportError(f"Syntax error in {script_path}: {e}") from e
    except ModuleNotFoundError as e:
        if "yaml" in str(e):
            raise ImportError(
                "pyyaml is required to build the boards database. "
                "Install it with: pip install pyyaml"
            ) from e
        raise
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
        logger.error(f"Boards database build failed: {e}")
        raise RuntimeError(
            f"Failed to build boards database from {data_dir}: {e}"
        ) from e
