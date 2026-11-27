"""In-memory provider for extension contract tests. No upstream requests."""

from types import SimpleNamespace

from pcbparts_mcp.extensions import AddressCapReached, ExtUnavailable


class FakeExt:
    unmetered = True

    def __init__(self):
        self.lookups = []
        self.batches = []
        self.started = False
        self.closed = False
        self.paused = False
        self.available = True

    async def start(self):
        self.started = True

    async def close(self):
        self.closed = True

    def pause(self):
        self.paused = True

    def can_answer_now(self):
        return self.available and not self.paused and not self.closed

    def status(self):
        return {"paused_until": "2026-11-15 00:00 UTC" if self.paused else None}

    def paused_for(self):
        return 60 if self.paused else 0

    def retry_after(self):
        return 60

    @staticmethod
    def _charge(number, sent, charge):
        if charge is not None and not charge(number):
            raise AddressCapReached()
        if sent is not None:
            sent.add(number)

    async def lookup(self, number, sent=None, charge=None):
        if not self.can_answer_now():
            raise ExtUnavailable(self.retry_after(), paused=self.paused)
        self._charge(number, sent, charge)
        self.lookups.append(number)
        found = number != "TP4056"
        return SimpleNamespace(
            results=[{"mfr_part_number": number, "manufacturer": "Maker", "lifecycle": "Active",
                      "lifecycle_status": "active"}] if found else [],
            statuses=[(number, "Maker", "Active", None)] if found else [])

    async def statuses(self, numbers, sent=None, charge=None, held=None):
        if not self.can_answer_now():
            raise ExtUnavailable(self.retry_after(), paused=self.paused)
        self.batches.append(list(numbers))
        answers = {}
        for number in numbers:
            try:
                self._charge(number, sent, charge)
            except AddressCapReached as exc:
                answers[number] = exc
            else:
                answers[number] = [(number, "Maker", "Active", None)]
        return answers
