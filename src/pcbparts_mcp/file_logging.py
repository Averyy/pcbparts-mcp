"""Optional UTC application log, kept across container replacements on the cache volume."""

import contextlib
import copy
import datetime
import logging
import os
import sys
import time
from dataclasses import dataclass
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from .config import LOG_MAX_BYTES_PER_DAY
from .private_files import private_open

logger = logging.getLogger(__name__)
MAX_MESSAGE_CHARS = 2000
FILE_LOCK_TIMEOUT_SECONDS = 0.25


def _expired_logs(base: Path, keep_days: int, *, include_active: bool = False) -> list[str]:
    # Age matters even if the server has missed rollovers. Without a writer, the closed
    # active file expires by its mtime's UTC day, just as it would after a startup rollover.
    cutoff = datetime.datetime.fromtimestamp(time.time(), datetime.timezone.utc).date() - datetime.timedelta(
        days=keep_days)
    dated, expired = [], set()
    for path in base.parent.iterdir():
        if path.is_symlink() or not path.is_file():
            continue
        if path == base:
            if not include_active:
                continue
            date = datetime.datetime.fromtimestamp(path.stat().st_mtime, datetime.timezone.utc).date()
        else:
            if not path.name.startswith(base.name + "."):
                continue
            suffix = path.name[len(base.name) + 1:]
            try:
                date = datetime.date.fromisoformat(suffix)
            except ValueError:
                continue
            if date.isoformat() != suffix:
                continue
            dated.append(str(path))
        if date < cutoff:
            expired.add(str(path))
    if keep_days > 0:
        expired.update(sorted(dated)[:-keep_days])
    return sorted(expired)


class _UTCFormatter(logging.Formatter):
    converter = time.gmtime

    def format(self, record: logging.LogRecord) -> str:
        # Format a copy: console handlers keep the full message/traceback and original args.
        message = super().format(copy.copy(record))
        if len(message) > MAX_MESSAGE_CHARS:
            marker = "… [truncated]"
            message = message[:MAX_MESSAGE_CHARS - len(marker)] + marker
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
        self.lock_dropped_records = 0
        self._reported_lock_dropped_records = 0
        self.max_bytes = LOG_MAX_BYTES_PER_DAY
        self.dropped_lines = 0
        super().__init__(path, when="midnight", utc=True, backupCount=keep_days, encoding="utf-8")
        self.rotator = os.replace  # replace a dated collision without deleting it under the lock
        self._written_bytes = Path(self.baseFilename).stat().st_size
        self.setFormatter(_UTCFormatter("%(message)s"))
        self.setLevel(logging.INFO)
        self.addFilter(_ApplicationFilter())

    def _open(self):
        return private_open(Path(self.baseFilename), self.mode, encoding="utf-8", errors="backslashreplace", newline="")

    def doRollover(self) -> None:
        dropped = self.dropped_lines
        lock_dropped = self.lock_dropped_records
        date = datetime.datetime.fromtimestamp(self.rolloverAt - self.interval, datetime.timezone.utc).date()
        # Rollover runs under the handler lock. Retention deletes belong to startup/hourly
        # maintenance outside that lock, or a stalled unlink can block every logging caller.
        if self.stream is not None:
            self.stream.close()
            self.stream = None
        if os.path.exists(self.baseFilename):
            self.rotate(self.baseFilename, self.rotation_filename(self.baseFilename + "." + date.isoformat()))
        self.rolloverAt = self.computeRollover(int(time.time()))
        if self.failed:
            return  # still rotate private data for retention, without reopening a failed writer
        self.stream = self._open()
        self._written_bytes = Path(self.baseFilename).stat().st_size
        self.dropped_lines = 0
        if dropped:
            self._write_record(logging.LogRecord(__name__, logging.WARNING, __file__, 0,
                                                "Application log: %s: %d lines dropped", (date, dropped), None))
        if lock_dropped > self._reported_lock_dropped_records:
            self._write_record(logging.LogRecord(
                __name__, logging.WARNING, __file__, 0,
                "Application log: %s: %d records dropped waiting for the file lock",
                (date, lock_dropped - self._reported_lock_dropped_records), None))
            # Keep the total cumulative: timeouts during rollover belong to the next notice.
            self._reported_lock_dropped_records = lock_dropped

    def _write_record(self, record: logging.LogRecord) -> None:
        message = self.format(record) + self.terminator
        size = len(message.encode("utf-8", "backslashreplace"))
        if self._written_bytes + size > self.max_bytes:
            first = self.dropped_lines == 0
            self.dropped_lines += message.count("\n")
            if first:
                # The full file cannot hold this notice; send it to the console once per day.
                logger.warning("Application log: daily byte budget reached; excess lines dropped",
                               extra={"_file_budget_notice": self})
            return
        if self.stream is None:
            self.stream = self._open()
        self.stream.write(message)
        self.flush()
        self._written_bytes += size

    def getFilesToDelete(self) -> list[str]:
        return _expired_logs(Path(self.baseFilename), self.backupCount)

    def emit(self, record: logging.LogRecord) -> None:
        if self.failed or getattr(record, "_file_budget_notice", None) is self:
            return
        try:
            if self.shouldRollover(record):
                self.doRollover()
            self._write_record(record)
        except Exception:
            self.handleError(record)

    def handle(self, record: logging.LogRecord) -> bool:
        # Allow ordinary concurrent writes to finish, but bound minute/task callers' wait
        # behind a stalled rollover/write. Other handlers still receive timed-out records.
        accepted = self.filter(record)
        if not accepted:
            return False
        if isinstance(accepted, logging.LogRecord):
            record = accepted
        if not self.lock.acquire(timeout=FILE_LOCK_TIMEOUT_SECONDS):
            self.lock_dropped_records += 1
            return False
        try:
            self.emit(record)
        finally:
            self.release()
        return True

    def handleError(self, record: logging.LogRecord) -> None:
        # StreamHandler catches write/flush errors here. Disable permanently, without logging's
        # default stderr traceback or a warning on every later record (including this warning).
        self.failed = True
        error = sys.exc_info()[1]
        with contextlib.suppress(Exception):
            self.close()
        logger.warning("Application log %s not writable (%s); continuing without the file", self.baseFilename, error)


@dataclass
class _LogRetention:
    keep_days: int
    handler: _DailyFileHandler | None = None
    failed: bool = False


_retention: dict[Path, _LogRetention] = {}


def configure_file_logging(path: str, keep_days: int) -> _DailyFileHandler | None:
    """Call after uvicorn configures its loggers; leave all stdout handlers and levels alone."""
    if not path:
        return None
    base = Path(path).absolute()
    retention = _retention[base] = _LogRetention(keep_days)
    handler = None
    try:
        base.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        base.parent.chmod(0o700)
        for source in base.parent.iterdir():
            if source.is_symlink() or not source.is_file():
                continue
            if source != base:
                if not source.name.startswith(base.name + "."):
                    continue
                suffix = source.name[len(base.name) + 1:]
                try:
                    if datetime.date.fromisoformat(suffix).isoformat() != suffix:
                        continue
                except ValueError:
                    continue
            source.chmod(0o600)
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

    retention.handler = handler
    logging.getLogger().addHandler(handler)
    # uvicorn.error reaches uvicorn, which doesn't propagate; fastmcp also owns its handlers.
    # Attach at each propagation boundary, so every record is written once, including tracebacks.
    for item in list(logging.root.manager.loggerDict.values()):
        if isinstance(item, logging.Logger) and not item.propagate and item.name != "uvicorn.access":
            item.addHandler(handler)
    return handler


def prune_file_logs() -> None:
    """Hourly maintenance, including an idle active file that has not emitted since midnight."""
    for base, retention in list(_retention.items()):
        handler = retention.handler
        expired, error = [], None
        if handler is not None:
            handler.acquire()
            try:
                if handler.shouldRollover(None):
                    handler.doRollover()  # close the active stream before renaming it
            except Exception as exc:
                error = exc
            finally:
                handler.release()
        try:
            expired = (handler.getFilesToDelete() if handler is not None
                       else _expired_logs(base, retention.keep_days, include_active=True))
        except Exception as exc:
            error = exc
        for source in expired:
            try:
                Path(source).unlink(missing_ok=True)
            except Exception as exc:
                error = exc
        # Retention retries independently of writing, including after a transient failure.
        if error is not None and not retention.failed:
            logger.warning("Application log pruning failed (%s); will retry", type(error).__name__)
        retention.failed = error is not None
