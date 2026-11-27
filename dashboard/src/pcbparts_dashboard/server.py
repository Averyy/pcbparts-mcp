"""Threaded HTTP serving and wall-clock-aligned background collection."""

import base64
import binascii
import gzip
import hashlib
import hmac
import ipaddress
import json
import logging
import math
import re
import socket
import sys
import threading
from datetime import UTC, date, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.parse import parse_qs, unquote, urlsplit

from .collector import collect
from .config import Settings
from .eastern import EASTERN
from .payload import build_payload
from .store import Store, utc_datetime

logger = logging.getLogger(__name__)
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": (
        "default-src 'self'; style-src 'self' https://fonts.googleapis.com; "
        "font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; "
        "frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
    ),
}
CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".woff2": "font/woff2",
    ".json": "application/json",
}
# Asset URLs get ?v=<hash of every static file>, so a browser loads new code after a deploy: the
# page's own references (/static/app.js) and the modules' imports of each other (from "./data.js").
PAGE_ASSET = re.compile(rb'(["\'])(/static/[\w.-]+\.(?:js|css|svg|png|woff2))(["\'])')
MODULE_IMPORT = re.compile(rb'(\bfrom\s*["\']\./[\w.-]+\.js)(["\'])')
LONG_CACHE = "private, max-age=31536000, immutable"
# Dismissed notices: a key names a notice's kind and subject ("failed:jlc_search:exception")
DISMISSAL_KEY = re.compile(r"[A-Za-z0-9_.:-]{1,200}", re.ASCII)
DISMISSAL_HEADER = "X-Dashboard-Request"
EASTERN_DATE = re.compile(r"\d{4}-\d{2}-\d{2}", re.ASCII)
MAX_DISMISSAL_BODY = 4096


def validate_bind(settings: Settings) -> None:
    if settings.password or settings.host.lower() == "localhost":
        return
    try:
        if ipaddress.ip_address(settings.host).is_loopback:
            return
    except ValueError:
        pass
    raise ValueError("DASHBOARD_PASSWORD is required when binding to a non-loopback host")


class CollectionRunner:
    """One gate for polling and refreshes, including their shared minimum interval."""

    def __init__(self, settings: Settings, store: Store, *, clock=None, collector=None):
        self.settings = settings
        self.store = store
        self.clock = clock or utc_datetime
        self.collector = collector or collect
        self.lock = threading.Lock()
        self.last_started: datetime | None = None

    def run(self, *, days=None) -> tuple[int, dict]:
        if not self.lock.acquire(blocking=False):
            return 429, {"error": "A collection is already running", "retry_after": 60}
        try:
            now = utc_datetime(self.clock())
            if self.last_started is not None:
                remaining = 60 - (now - self.last_started).total_seconds()
                if remaining > 0:
                    return 429, {"error": "Refresh is limited to once per 60 seconds", "retry_after": math.ceil(remaining)}
            self.last_started = now
            return 200, self.collector(self.settings, self.store, days=days, now=now)
        finally:
            self.lock.release()


def next_poll_at(now: datetime, minutes: int) -> datetime:
    """UTC slots are aligned multiples of the interval, offset by 30 seconds."""
    if minutes < 5:
        raise ValueError("POLL_MINUTES must be at least 5")
    period = minutes * 60
    slot = (math.floor((utc_datetime(now).timestamp() - 30) / period) + 1) * period + 30
    return datetime.fromtimestamp(slot, UTC)


RETRY_SECONDS = 300


class Poller(threading.Thread):
    def __init__(self, runner: CollectionRunner, *, clock=None, sleep=None):
        super().__init__(name="pcbparts-poller", daemon=True)
        self.runner = runner
        self.clock = clock or runner.clock
        self.stopped = threading.Event()
        self.sleep = sleep or self.stopped.wait

    def stop(self) -> None:
        self.stopped.set()

    def run(self) -> None:
        retry_left = True
        while not self.stopped.is_set():
            failed = False
            try:
                status, result = self.runner.run()
                # A 429 here only means a collection just ran (a refresh): its data is fresh
                failed = status == 200 and not result.get("ok")
            except Exception as exc:
                # Exception text can contain request details; log only its type.
                logger.error("Background collection failed (%s)", type(exc).__name__)
                failed = True
            if self.stopped.is_set():
                break
            now = utc_datetime(self.clock())
            delay = (next_poll_at(now, self.runner.settings.poll_minutes) - now).total_seconds()
            # One retry RETRY_SECONDS after a failed fetch (at a deploy the server can still be starting),
            # then the regular slots again
            if failed and retry_left:
                delay, retry_left = min(delay, RETRY_SECONDS), False
            else:
                retry_left = True
            self.sleep(delay)


def _allows_gzip(header: str) -> bool:
    encodings = {}
    for item in header.lower().split(","):
        name, *parameters = item.strip().split(";")
        quality = 1.0
        for parameter in parameters:
            key, _, value = parameter.strip().partition("=")
            if key == "q":
                try:
                    quality = float(value)
                except ValueError:
                    quality = 0.0
        encodings[name.strip()] = quality if 0 <= quality <= 1 else 0.0
    return encodings.get("gzip", encodings.get("*", 0)) > 0


class DashboardHTTPServer(ThreadingHTTPServer):
    settings: Settings
    store: Store
    runner: CollectionRunner
    static_dir: Path
    polling: bool = False

    def asset_version(self) -> bytes:
        """A short hash of every file in the static directory, recomputed when one changes."""
        files = sorted(path for path in self.static_dir.iterdir() if path.is_file())
        signature = tuple((path.name, path.stat().st_mtime_ns, path.stat().st_size) for path in files)
        with self._asset_lock:
            if self._asset_cache is None or self._asset_cache[0] != signature:
                digest = hashlib.sha256()
                for path in files:
                    digest.update(path.name.encode() + b"\0" + path.read_bytes() + b"\0")
                self._asset_cache = (signature, digest.hexdigest()[:12].encode())
            return self._asset_cache[1]

    def data_reply(self, now: datetime) -> tuple[bytes, bytes]:
        # Serialize cache fills as well as store reads; simultaneous page loads share one build.
        with self._data_lock, self.store.lock:
            key = (self.store.revision(), now.astimezone(EASTERN).date(), self.polling)
            if self._data_cache is not None and self._data_cache[0] == key:
                return self._data_cache[1:]
            next_poll = next_poll_at(now, self.settings.poll_minutes) if self.polling else None
            payload = build_payload(self.store, self.settings, now, next_poll=next_poll)
            body = json.dumps(payload, separators=(",", ":")).encode()
            compressed = gzip.compress(body, compresslevel=1, mtime=0)
            # Keep the starting revision: an external commit during the build must invalidate it.
            self._data_cache = (key, body, compressed)
            return body, compressed


class DashboardHandler(BaseHTTPRequestHandler):
    server: DashboardHTTPServer
    # http.server waits for a request line forever by default, and every connection holds a
    # thread before any password is asked for. This is a socket timeout: it bounds a stalled
    # read or write, not how long a collection may take.
    timeout = 30

    def end_headers(self) -> None:
        for key, value in SECURITY_HEADERS.items():
            self.send_header(key, value)
        if getattr(self, "path", "").split("?", 1)[0].startswith("/api/"):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_request(self, code="-", size="-") -> None:
        path = getattr(self, "path", "").split("?", 1)[0]
        # Escape control characters rather than letting a request forge log lines.
        print(f"{self.command} {json.dumps(path, ensure_ascii=True)} {code}", file=sys.stderr)

    def log_message(self, *_args) -> None:
        # BaseHTTPRequestHandler otherwise logs arbitrary parse errors as well.
        pass

    def _send(self, status: int, body: bytes, content_type: str, headers=None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, status: int, value, *, compress=False, headers=None) -> None:
        body = json.dumps(value, separators=(",", ":")).encode()
        extra_headers = dict(headers or {})
        if compress:
            extra_headers["Vary"] = "Accept-Encoding"
            if _allows_gzip(self.headers.get("Accept-Encoding", "")):
                body = gzip.compress(body, mtime=0)
                extra_headers["Content-Encoding"] = "gzip"
        self._send(status, body, "application/json; charset=utf-8", extra_headers)

    def _loopback_host(self) -> bool:
        """The request names this computer. Without a password the server only listens on a loopback
        address, but a page whose name resolves there (DNS rebinding) could still reach it."""
        host = self.headers.get("Host")
        if host is None:
            return True  # not a browser: every browser request names its host
        host = host.strip().lower()
        name = host[1:host.find("]")] if host.startswith("[") and "]" in host else host.rsplit(":", 1)[0] if host.count(":") == 1 else host
        if name == "localhost":
            return True
        try:
            return ipaddress.ip_address(name).is_loopback
        except ValueError:
            return False

    def _authorized(self) -> bool:
        settings = self.server.settings
        if not settings.password and not self._loopback_host():
            self._json(403, {"error": "Without a password, this dashboard answers only to localhost"})
            return False
        if not settings.password or self.path.split("?", 1)[0] == "/healthz":
            return True
        authorization = self.headers.get("Authorization", "")
        scheme, _, credentials = authorization.partition(" ")
        if scheme.lower() == "basic":
            try:
                decoded = base64.b64decode(credentials, validate=True)
                user, separator, password = decoded.partition(b":")
                valid_user = hmac.compare_digest(user, settings.username.encode())
                valid_password = hmac.compare_digest(password, settings.password.encode())
                if separator and valid_user and valid_password:
                    return True
            except (ValueError, binascii.Error):
                pass
        self._json(401, {"error": "Authentication required"}, headers={
            "WWW-Authenticate": 'Basic realm="pcbparts dashboard"',
        })
        return False

    def _same_origin(self) -> bool:
        """False for a request a browser made on behalf of another site.

        Basic auth credentials ride along with any request the browser sends here, so without
        this any page the user visits could start collections (each one calls the stats server,
        and holds the poller's cooldown). Clients that send neither header are not browsers.
        """
        site = self.headers.get("Sec-Fetch-Site")
        if site is not None:
            return site.strip().lower() in ("same-origin", "none")
        origin = self.headers.get("Origin")
        if origin is None:
            return True
        return urlsplit(origin).netloc.lower() == self.headers.get("Host", "").strip().lower()

    def _static(self, name: str, query: str = "") -> None:
        relative = PurePosixPath(name)
        if not name or relative.is_absolute() or ".." in relative.parts or "\\" in name or "\x00" in name:
            self._json(404, {"error": "Not found"})
            return
        try:
            target = (self.server.static_dir / name).resolve()
            if not target.is_relative_to(self.server.static_dir) or not target.is_file():
                self._json(404, {"error": "Not found"})
                return
            body = target.read_bytes()
            version = self.server.asset_version()
        except (OSError, RuntimeError, ValueError):
            self._json(404, {"error": "Not found"})
            return
        suffix = target.suffix.lower()
        if suffix == ".html":
            body = PAGE_ASSET.sub(lambda m: m[1] + m[2] + b"?v=" + version + m[3], body)
        elif suffix == ".js":
            body = MODULE_IMPORT.sub(lambda m: m[1] + b"?v=" + version + m[2], body)
        # A versioned URL never changes; the page and unversioned URLs are checked each time
        asked = parse_qs(query).get("v", [None])[0]
        cache = LONG_CACHE if suffix != ".html" and asked == version.decode() else "no-cache"
        self._send(200, body, CONTENT_TYPES.get(suffix, "application/octet-stream"), {"Cache-Control": cache})

    def do_GET(self) -> None:
        if not self._authorized():
            return
        path = urlsplit(self.path).path
        if path == "/healthz":
            self._json(200, {"ok": True})
        elif path == "/api/data":
            now = utc_datetime(self.server.runner.clock())
            body, compressed = self.server.data_reply(now)
            headers = {"Vary": "Accept-Encoding"}
            if _allows_gzip(self.headers.get("Accept-Encoding", "")):
                body = compressed
                headers["Content-Encoding"] = "gzip"
            self._send(200, body, "application/json; charset=utf-8", headers)
        elif path == "/api/dismissals":
            self._json(200, {"dismissals": self.server.store.dismissals()})
        elif path in ("/", "/index.html"):
            self._static("index.html")
        elif path.startswith("/static/"):
            self._static(unquote(path[len("/static/"):]), urlsplit(self.path).query)
        else:
            self._json(404, {"error": "Not found"})

    do_HEAD = do_GET

    def _dismissal_request(self) -> bool:
        """A change to the dismissals must come from this dashboard's own page: same origin, and a
        header a browser sends cross-site only after a preflight this server never approves."""
        if not self._same_origin():
            self._json(403, {"error": "Cross-site requests are not accepted"})
            return False
        if self.headers.get(DISMISSAL_HEADER) != "1":
            self._json(403, {"error": f"Missing {DISMISSAL_HEADER} header"})
            return False
        return True

    def _dismiss(self) -> None:
        if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
            self._json(415, {"error": "Send JSON"})
            return
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self._json(411, {"error": "Content-Length required"})
            return
        if not 0 < length <= MAX_DISMISSAL_BODY:
            self._json(413 if length > 0 else 400, {"error": "Body too large" if length > 0 else "Empty body"})
            return
        try:
            body = json.loads(self.rfile.read(length))
        except (ValueError, RecursionError):
            self._json(400, {"error": "Invalid JSON"})
            return
        key = body.get("key") if isinstance(body, dict) else None
        count = body.get("count") if isinstance(body, dict) else None
        day = body.get("day") if isinstance(body, dict) else None
        if not isinstance(key, str) or not DISMISSAL_KEY.fullmatch(key):
            self._json(400, {"error": "key must be 1-200 letters, digits or _.:-"})
            return
        if type(count) is not int or not 0 <= count <= 10**12:
            self._json(400, {"error": "count must be a whole number from 0"})
            return
        try:
            valid_day = isinstance(day, str) and bool(EASTERN_DATE.fullmatch(day)) and date.fromisoformat(day).isoformat() == day
        except ValueError:
            valid_day = False
        if not valid_day:
            self._json(400, {"error": "day must be a date, YYYY-MM-DD"})
            return
        at = utc_datetime(self.server.runner.clock()).isoformat(timespec="seconds").replace("+00:00", "Z")
        self.server.store.dismiss(key, count, at, day)
        self._json(200, {"dismissals": self.server.store.dismissals()})

    def do_DELETE(self) -> None:
        if not self._authorized():
            return
        target = urlsplit(self.path)
        if target.path != "/api/dismissals":
            self._json(404, {"error": "Not found"})
            return
        if not self._dismissal_request():
            return
        key = parse_qs(target.query).get("key", [None])[0]
        if not isinstance(key, str) or not DISMISSAL_KEY.fullmatch(key):
            self._json(400, {"error": "key must be 1-200 letters, digits or _.:-"})
            return
        self.server.store.undismiss(key)
        self._json(200, {"dismissals": self.server.store.dismissals()})

    def do_POST(self) -> None:
        if not self._authorized():
            return
        target = urlsplit(self.path)
        if target.path == "/api/dismissals":
            if self._dismissal_request():
                self._dismiss()
            return
        if target.path != "/api/refresh":
            self._json(404, {"error": "Not found"})
            return
        if not self._same_origin():
            self._json(403, {"error": "Cross-site requests are not accepted"})
            return
        full = parse_qs(target.query).get("full", [None])[0] == "1"
        try:
            status, result = self.server.runner.run(days=365 if full else None)
        except Exception as exc:
            logger.error("Manual collection failed (%s)", type(exc).__name__)
            self._json(500, {"error": "Collection failed"})
            return
        headers = {"Retry-After": str(result["retry_after"])} if status == 429 else None
        self._json(status, result, headers=headers)

    def send_error(self, code, message=None, explain=None) -> None:
        if code == 501:
            if self._authorized():
                self._json(404, {"error": "Not found"})
        else:
            self._json(code, {"error": self.responses.get(code, ("Request error",))[0]})


def create_server(settings: Settings, store: Store, *, clock=None, collector=None, static_dir=None) -> DashboardHTTPServer:
    validate_bind(settings)
    server_class = DashboardHTTPServer
    if ":" in settings.host:
        class IPv6DashboardHTTPServer(DashboardHTTPServer):
            address_family = socket.AF_INET6
        server_class = IPv6DashboardHTTPServer
    server = server_class((settings.host, settings.port), DashboardHandler)
    server.settings = settings
    server.store = store
    server.runner = CollectionRunner(settings, store, clock=clock, collector=collector)
    server.static_dir = Path(static_dir or Path(__file__).with_name("static")).resolve()
    server._data_lock = threading.Lock()
    server._data_cache = None
    server._asset_lock = threading.Lock()
    server._asset_cache = None
    return server


def serve(settings: Settings, store: Store, *, no_poll=False) -> None:
    server = create_server(settings, store)
    poller = None if no_poll else Poller(server.runner)
    server.polling = poller is not None
    host = f"[{settings.host}]" if ":" in settings.host else settings.host
    print(f"http://{host}:{server.server_port}", flush=True)
    try:
        if poller:
            poller.start()
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if poller:
            poller.stop()
            poller.join()
        server.server_close()
