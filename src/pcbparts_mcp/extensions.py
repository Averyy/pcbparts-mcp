"""Optional deployment-specific extensions; none ship with this repository.

An importable ``pcbparts_extensions`` module may define ``digikey_backup(context)``.
The synchronous factory returns a DigiKeyBackup or None. The server awaits start()
before accepting calls; DigiKeyClient owns close(). Import or factory errors propagate
so a misconfigured deployment is not silently treated as an absent extension.
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


class BackupFailed(Exception):
    """A lookup failed; DigiKeyClient supplies the existing distributor error reply."""


class BackupUnavailable(Exception):
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


class BackupAnswer(Protocol):
    @property
    def results(self) -> list[dict[str, Any]]:
        """DigiKey result dictionaries; an empty list means not listed."""
        ...

    @property
    def statuses(self) -> list[LifecycleStatus]:
        """MPN, manufacturer, status text and last-buy date for each exact match."""
        ...


class DigiKeyBackup(Protocol):
    """Optional DigiKey provider, sharing the client's answers and per-address allowance.

    lookup/statuses call charge(number) immediately before each number's first send,
    with no intervening await, then add it to sent. A false charge sends nothing and
    raises/returns AddressCapReached. Further requests for that number do not charge
    again. Keep sent populated on exceptions/cancellation. A batch's held callback
    reports an unsent number's BackupUnavailable immediately, once per number.
    Requests and refusals use the public client/stats counting helpers; charge and
    held already count the lookup and its address allowance.
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
                     charge: Charge | None = None) -> BackupAnswer:
        """Return an answer or raise AddressCapReached/BackupUnavailable/BackupFailed."""
        ...

    async def statuses(self, numbers: list[str], sent: set[str] | None = None,
                       charge: Charge | None = None,
                       held: Callable[[str, BackupUnavailable], None] | None = None
                       ) -> dict[str, list[LifecycleStatus] | Exception]:
        """Per-number readings/errors; a shared failure may raise as lookup() does."""
        ...


@dataclass(frozen=True)
class ExtensionContext:
    address_daily: AddressDailyQuota
    store: DistributorStore
    store_path: str


def load_digikey_backup(context: ExtensionContext) -> DigiKeyBackup | None:
    """Load the optional factory, if supplied; import and factory errors propagate."""
    try:
        module = importlib.import_module("pcbparts_extensions")
    except ModuleNotFoundError as exc:
        if exc.name != "pcbparts_extensions":
            raise
        return None
    factory = getattr(module, "digikey_backup", None)
    if factory is None:
        logger.info("Optional deployment extension has no DigiKey provider")
        return None
    backup = factory(context)
    if backup is not None:
        logger.info("Optional deployment extension loaded")
    return backup
