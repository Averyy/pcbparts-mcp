"""JLCPCB MCP Server - Search electronic components for PCB assembly."""

from pathlib import Path

def _get_version() -> str:
    """Get version from pyproject.toml or package metadata."""
    # First try importlib.metadata (works when pip installed)
    try:
        from importlib.metadata import version
        return version("jlcpcb-mcp")
    except Exception:
        pass

    # Fallback: read from pyproject.toml (works in Docker with PYTHONPATH)
    try:
        import tomllib
        pyproject = Path(__file__).parent.parent.parent / "pyproject.toml"
        if pyproject.exists():
            with open(pyproject, "rb") as f:
                data = tomllib.load(f)
            return data["project"]["version"]
    except Exception:
        pass

    return "0.0.0"  # Unknown version

__version__ = _get_version()
