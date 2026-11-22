"""Settings loaded relative to the checkout, never the working directory."""

import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Mapping


def find_project_root() -> Path:
    for directory in Path(__file__).resolve().parents:
        if (directory / "pyproject.toml").is_file():
            return directory
    raise RuntimeError("Cannot find the project root containing pyproject.toml")


@dataclass(frozen=True)
class Settings:
    project_root: Path = field(default_factory=find_project_root)
    stats_token: str | None = field(default=None, repr=False)
    stats_url: str = "https://pcbparts.dev/mcp/stats"
    health_url: str = "https://pcbparts.dev/health"
    db_path: Path = Path("data/dashboard.db")
    poll_minutes: int = 60
    host: str = "127.0.0.1"
    port: int = 8050
    password: str | None = field(default=None, repr=False)
    username: str = "admin"
    problems_since: str | None = None
    problems_version: str | None = None

    def __post_init__(self) -> None:
        root = Path(self.project_root).resolve()
        object.__setattr__(self, "project_root", root)
        object.__setattr__(self, "db_path", (root / self.db_path).resolve())
        if self.poll_minutes < 5:
            raise ValueError("POLL_MINUTES must be at least 5")
        if not 0 <= self.port <= 65535:
            raise ValueError("DASHBOARD_PORT must be between 0 and 65535")
        if self.problems_since is not None:
            try:
                moment = datetime.fromisoformat(self.problems_since)
                if moment.tzinfo is None:
                    raise ValueError
            except (TypeError, ValueError):
                raise ValueError("PROBLEMS_SINCE must be an ISO timestamp with a timezone") from None
            object.__setattr__(self, "problems_since", moment.astimezone(UTC).isoformat(
                timespec="seconds"
            ).replace("+00:00", "Z"))


def load_settings(
    *, project_root: Path | None = None, environ: Mapping[str, str] | None = None
) -> Settings:
    root = project_root if project_root is not None else find_project_root()
    values: dict[str, str] = {}
    local_file = root / "secrets.local"
    if local_file.is_file():
        for number, line in enumerate(local_file.read_text().splitlines(), 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, separator, value = line.partition("=")
            if not separator or not key.strip():
                raise ValueError(f"Invalid settings line {number} in secrets.local")
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            values[key.strip()] = value
    values.update(os.environ if environ is None else environ)

    def integer(name: str, default: int) -> int:
        try:
            return int(values.get(name, str(default)))
        except ValueError:
            raise ValueError(f"{name} must be an integer") from None

    return Settings(
        project_root=root,
        stats_token=values.get("STATS_TOKEN") or None,
        stats_url=values.get("STATS_URL", Settings.stats_url),
        health_url=values.get("HEALTH_URL", Settings.health_url),
        db_path=Path(values.get("DASHBOARD_DB", "data/dashboard.db")),
        poll_minutes=integer("POLL_MINUTES", 60),
        host=values.get("DASHBOARD_HOST", "127.0.0.1"),
        port=integer("DASHBOARD_PORT", 8050),
        password=values.get("DASHBOARD_PASSWORD") or None,
        username=values.get("DASHBOARD_USER", "admin"),
        problems_since=values.get("PROBLEMS_SINCE") or None,
        problems_version=values.get("PROBLEMS_VERSION") or None,
    )
