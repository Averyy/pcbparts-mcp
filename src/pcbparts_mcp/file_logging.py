"""Optional UTC application log, kept across container replacements on the cache volume."""

import contextlib
import datetime
import logging
import sys
import time
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

logger = logging.getLogger(__name__)


class _UTCFormatter(logging.Formatter):
    converter = time.gmtime

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        prefix = f"{self.formatTime(record, '%Y-%m-%dT%H:%M:%SZ')} {record.levelname} {record.name}: "
        return "\n".join(prefix + line for line in message.split("\n"))


class _ApplicationFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return (not (record.name == "uvicorn.access" or record.name.startswith("uvicorn.access."))
                and (record.levelno >= logging.WARNING
                     or record.name == "pcbparts_mcp" or record.name.startswith("pcbparts_mcp.")))


class _DailyFileHandler(TimedRotatingFileHandler):
    def __init__(self, path: str, keep_days: int):
        self.failed = False
        super().__init__(path, when="midnight", utc=True, backupCount=keep_days, encoding="utf-8")
        self.setFormatter(_UTCFormatter("%(message)s"))
        self.setLevel(logging.INFO)
        self.addFilter(_ApplicationFilter())

    def getFilesToDelete(self) -> list[str]:
        # backupCount alone retains old files indefinitely if the server misses rollovers.
        cutoff = datetime.datetime.fromtimestamp(time.time(), datetime.timezone.utc).date() - datetime.timedelta(
            days=self.backupCount)
        expired = set(super().getFilesToDelete())
        base = Path(self.baseFilename)
        for path in base.parent.iterdir():
            if not path.name.startswith(base.name + "."):
                continue
            suffix = path.name[len(base.name) + 1:]
            if self.extMatch.fullmatch(suffix):
                try:
                    date = datetime.date.fromisoformat(suffix)
                except ValueError:
                    continue
                if date < cutoff:
                    expired.add(str(path))
        return sorted(expired)

    def emit(self, record: logging.LogRecord) -> None:
        if not self.failed:
            super().emit(record)

    def handleError(self, record: logging.LogRecord) -> None:
        # StreamHandler catches write/flush errors here. Disable permanently, without logging's
        # default stderr traceback or a warning on every later record (including this warning).
        self.failed = True
        error = sys.exc_info()[1]
        with contextlib.suppress(Exception):
            self.close()
        logger.warning("Application log %s not writable (%s); continuing without the file", self.baseFilename, error)


def configure_file_logging(path: str, keep_days: int) -> _DailyFileHandler | None:
    """Call after uvicorn configures its loggers; leave all stdout handlers and levels alone."""
    if not path:
        return None
    handler = None
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        handler = _DailyFileHandler(path, keep_days)
        if handler.shouldRollover(None):
            handler.doRollover()
        for expired in handler.getFilesToDelete():
            Path(expired).unlink()
    except Exception as error:
        if handler is not None:
            with contextlib.suppress(Exception):
                handler.close()
        logger.warning("Application log %s unavailable (%s); continuing without the file", path, error)
        return None

    logging.getLogger().addHandler(handler)
    # uvicorn.error reaches uvicorn, which doesn't propagate; fastmcp also owns its handlers.
    # Attach at each propagation boundary, so every record is written once, including tracebacks.
    for item in list(logging.root.manager.loggerDict.values()):
        if isinstance(item, logging.Logger) and not item.propagate and item.name != "uvicorn.access":
            item.addHandler(handler)
    return handler
