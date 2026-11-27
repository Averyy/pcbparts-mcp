"""Optional deployment-specific extensions; none ship with this repository.

An importable ``pcbparts_extensions`` module may define ``digikey_ext(context)``.
The synchronous factory returns a DigiKeyExt or None. The server awaits start()
before accepting calls; DigiKeyClient owns close(). A broken extension never takes the
server down: an error importing the module, calling the factory or starting it is logged
as one ERROR naming only its exception type, and the server runs without it (DigiKey's
API only). A module that isn't installed at all is skipped silently.
"""

from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass
from typing import Any, Callable, Protocol

from .cache import AddressDailyQuota
from .distributor_store import DistributorStore

logger = logging.getLogger(__name__)

LifecycleStatus = tuple[str, str, str | None, str | None]


class AddressCapReached(Exception):
    """charge() refused a number before its first request; nothing was sent for it."""


class ExtFailed(Exception):
    """A lookup failed; DigiKeyClient supplies the existing distributor error reply."""


class ExtUnavailable(Exception):
    """A lookup is paused or busy. Timing and send state survive a stopped batch."""

    def __init__(self, retry_after: int, paused: bool, sent: bool = False, refused: bool = False):
        super().__init__("paused" if paused else "busy")
        self.retry_after = retry_after
        self.paused = paused
        self.sent = sent
        self.refused = refused


class Charge(Protocol):
    def __call__(self, number: str, check: bool = False) -> bool:
        """Check eligibility only with check=True; otherwise charge once before the first send."""
        ...


class ExtAnswer(Protocol):
    @property
    def results(self) -> list[dict[str, Any]]:
        """DigiKey result dictionaries; an empty list means not listed."""
        ...

    @property
    def statuses(self) -> list[LifecycleStatus]:
        """MPN, manufacturer, status text and last-buy date for each exact match."""
        ...


class DigiKeyExt(Protocol):
    """Optional DigiKey provider, sharing the client's answers and per-address allowance.

    lookup/statuses call charge(number) immediately before each number's first send,
    with no intervening await, then add it to sent. A false charge sends nothing and
    raises/returns AddressCapReached. Further requests for that number do not charge
    again. Keep sent populated on exceptions/cancellation. A batch's held callback
    reports an unsent number's ExtUnavailable immediately, once per number.
    Requests and refusals use the public client/stats counting helpers, its HTTP
    requests and their outcomes under the digikey_ext upstream source (from 0.10.11;
    the API's stay under digikey). charge already counts a sent lookup (sent and
    distributors.digikey.ext_sent) and its address allowance; held counts an unsent
    lookup as rate_limited and held back.
    """

    async def start(self) -> None: ...
    async def close(self) -> None: ...

    @property
    def unmetered(self) -> bool: ...
    def can_answer_now(self) -> bool: ...
    def status(self) -> dict[str, Any]:
        """Existing stats fields: paused_until (UTC text or None)."""
        ...
    def paused_for(self) -> int: ...
    def retry_after(self) -> int: ...

    async def lookup(self, number: str, sent: set[str] | None = None,
                     charge: Charge | None = None) -> ExtAnswer:
        """Return an answer or raise AddressCapReached/ExtUnavailable/ExtFailed."""
        ...

    async def statuses(self, numbers: list[str], sent: set[str] | None = None,
                       charge: Charge | None = None,
                       held: Callable[[str, ExtUnavailable], None] | None = None
                       ) -> dict[str, list[LifecycleStatus] | Exception]:
        """Per-number readings/errors; a shared failure may raise as lookup() does."""
        ...


@dataclass(frozen=True)
class ExtensionContext:
    address_daily: AddressDailyQuota
    store: DistributorStore
    store_path: str


def extension_failed(exc: BaseException) -> None:
    """The one ERROR for a broken extension: its exception type only, since the message could
    carry paths or other deployment details."""
    logger.error("Optional deployment extension failed to load (%s); continuing without it", type(exc).__name__)


def load_digikey_ext(context: ExtensionContext) -> DigiKeyExt | None:
    """Load the optional factory, if supplied. None when there's no module or no provider, or when
    importing the module or calling its factory fails (logged by extension_failed)."""
    try:
        module = importlib.import_module("pcbparts_extensions")
    except ModuleNotFoundError as exc:
        if exc.name == "pcbparts_extensions":  # not installed: nothing to say
            return None
        extension_failed(exc)  # one of its own imports is missing
        return None
    except Exception as exc:
        extension_failed(exc)
        return None
    factory = getattr(module, "digikey_ext", None)
    if factory is None:
        logger.info("Optional deployment extension has no DigiKey provider")
        return None
    try:
        ext = factory(context)
    except Exception as exc:
        extension_failed(exc)
        return None
    if ext is not None:
        logger.info("Optional deployment extension loaded")
    return ext
