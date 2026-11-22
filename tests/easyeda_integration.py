"""One EasyEDA allowance for a serial integration session, including wafer's hidden resends.

Only integration fixtures install these patches. Unit tests inject a clock and transport.
"""

import asyncio
from functools import wraps
import time
from urllib.parse import urlsplit

import pytest
import wafer
import wreq

from pcbparts_mcp.cache import SlidingWindowBudget
from pcbparts_mcp.client import JLCPCBClient

BLOCKED = "EasyEDA blocked this IP; stop and wait"


def _is_easyeda(url):
    host = (urlsplit(str(url)).hostname or "").rstrip(".").lower()
    return host == "easyeda.com" or host.endswith(".easyeda.com")


def _is_products(url):
    return urlsplit(str(url)).path.startswith("/api/products/")


class _TransportBudget:
    """Let client checks reach the waiting budget at the actual HTTP send."""

    def try_acquire(self):
        return True


class EasyEDAIntegrationPacer:
    def __init__(self, clock=time.monotonic, sleep=asyncio.sleep):
        self.budget = SlidingWindowBudget(4, 75.0, clock)
        self.sleep = sleep
        self.blocked = False
        self.footprints = {}
        self.client_budget = _TransportBudget()
        self._loop = None

    def check_blocked(self):
        if self.blocked:
            pytest.skip(BLOCKED)

    def _locks(self):
        # pytest-asyncio uses different loops across tests/classes. Keep the session's
        # timestamps and stop flag, but never reuse a contended lock from a closed loop.
        loop = asyncio.get_running_loop()
        if loop is not self._loop:
            self._loop = loop
            self._request_lock = asyncio.Lock()
            self._send_lock = asyncio.Lock()
        return self._request_lock, self._send_lock

    async def _wait(self):
        self.check_blocked()
        while delay := self.budget.wait_seconds():
            await self.sleep(delay)
            self.check_blocked()

    async def request(self, send, method, url, **kwargs):
        if not _is_easyeda(url):
            return await send(method, url, **kwargs)
        request_lock, _ = self._locks()
        async with request_lock:
            self.check_blocked()
            if _is_products(url):
                # Wait before wafer starts its 15s network timeout. The transport below
                # records the actual send, including Critical-CH resends and redirects.
                await self._wait()
            return await send(method, url, **kwargs)

    async def send(self, send, method, url, **kwargs):
        if not _is_easyeda(url):
            return await send(method, url, **kwargs)
        _, send_lock = self._locks()
        async with send_lock:
            self.check_blocked()
            if _is_products(url):
                while not self.budget.try_acquire():
                    await self._wait()
            response = await send(method, url, **kwargs)
            if response.status.as_int() == 403:
                self.blocked = True
                # pytest.skip is a BaseException: neither wafer nor the client's broad
                # except Exception may swallow it and send another request.
                pytest.skip(BLOCKED)
            return response

    def install(self, monkeypatch):
        request = wafer.AsyncSession.request
        transport = wreq.Client.request
        footprint = JLCPCBClient._check_easyeda_footprint

        async def paced_request(session, method, url, **kwargs):
            return await self.request(request.__get__(session), method, url, **kwargs)

        async def paced_send(client, method, url, **kwargs):
            return await self.send(transport.__get__(client), method, url, **kwargs)

        async def shared_footprint(client, lcsc):
            self.check_blocked()
            client._easyeda_products_budget = self.client_budget
            client._easyeda_cache = self.footprints
            return await footprint(client, lcsc)

        monkeypatch.setattr(wafer.AsyncSession, "request", paced_request)
        monkeypatch.setattr(wreq.Client, "request", paced_send)
        monkeypatch.setattr(JLCPCBClient, "_check_easyeda_footprint", shared_footprint)

        def guarded(method):
            @wraps(method)
            async def call(client, *args, **kwargs):
                self.check_blocked()
                return await method(client, *args, **kwargs)
            return call

        # Skip even when a later test could use a cached answer. get_part also guards
        # find_alternatives' original and the server's live get_part/pinout paths.
        for name in ("get_part", "get_easyeda_component", "footprint_pads"):
            monkeypatch.setattr(JLCPCBClient, name, guarded(getattr(JLCPCBClient, name)))
