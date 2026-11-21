"""wafer 0.7 resends a request once, on its own, when the reply's Critical-CH names a client hint the
origin asked for (Accept-CH) and the request lacked; it does so whatever the status, and the resend
isn't counted in retries. EasyEDA's /api/products guard stops on its first 403 (max_retries=0,
max_rotations=0): this pins how many requests one footprint check can send when such a 403 comes,
so a wafer upgrade that resends more often fails here. A real wafer session over a fake transport;
no network."""

import json

import pytest

from pcbparts_mcp.client import JLCPCBClient


def _view(data: bytes) -> memoryview:
    return memoryview(data).toreadonly()  # wreq 0.13 hands back read-only memoryviews


class _Headers:
    """wreq's HeaderMap as wafer reads it."""

    def __init__(self, data: dict[str, str]):
        self._raw = {name.lower().encode("ascii"): [value.encode("utf-8")] for name, value in data.items()}

    def keys(self):
        return [_view(name) for name in self._raw]

    def __getitem__(self, name):
        name = name.lower().encode("ascii") if isinstance(name, str) else bytes(name)
        return _view(self._raw[name][0])

    def get(self, name):
        try:
            return self[name]
        except KeyError:
            return None

    def get_all(self, name):
        name = name.lower().encode("ascii") if isinstance(name, str) else bytes(name)
        return [_view(value) for value in self._raw.get(name, [])]


class _Status:
    def __init__(self, code: int):
        self._code = code

    def as_int(self) -> int:
        return self._code

    def is_success(self) -> bool:
        return 200 <= self._code < 300


class _Stream:
    def __init__(self, data: bytes):
        self._data = data

    def __aiter__(self):
        async def chunks():
            if self._data:
                yield _view(self._data)
        return chunks()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _Reply:
    def __init__(self, status: int, headers: dict[str, str], body: str):
        self.status = _Status(status)
        self.headers = _Headers(headers)
        self._body = body.encode("utf-8")
        self.content_length = None

    async def text(self):
        return self._body.decode("utf-8")

    async def bytes(self):
        return _view(self._body)

    def stream(self):
        return _Stream(self._body)


class _Jar:
    def get_all(self):
        return []

    def __getattr__(self, name):  # anything else a jar does: nothing to store here
        return lambda *args, **kwargs: None


class _Transport:
    """Stands in for wafer's wreq client: every request gets the same reply."""

    def __init__(self, reply: _Reply):
        self.reply = reply
        self.sent = 0
        self.cookie_jar = _Jar()

    async def request(self, method, url, **kwargs):
        self.sent += 1
        return self.reply

    async def get(self, url, **kwargs):
        return await self.request("GET", url, **kwargs)


@pytest.fixture
async def client():
    c = JLCPCBClient()
    yield c
    await c.close()


async def test_a_403_asking_for_critical_hints_costs_at_most_one_more_request(client, monkeypatch):
    blocked = _Reply(403, {"accept-ch": "Sec-CH-UA-Full-Version-List",
                           "critical-ch": "Sec-CH-UA-Full-Version-List",
                           "content-type": "application/json"}, json.dumps({"message": "Forbidden"}))
    transport = _Transport(blocked)
    session = client._get_easyeda_products_session()
    session._client = transport
    # A retired identity would build a real client: none may be built here
    monkeypatch.setattr(session, "_rebuild_client", lambda *args, **kwargs: None)

    result = await client.check_easyeda_footprint("C2040")
    assert result["has_easyeda_footprint"] is None  # unknown: the check was refused
    assert transport.sent == 2, transport.sent  # the request, and wafer's one Critical-CH resend
    assert client._easyeda_products_cooldown.active  # the guard paused on that first 403

    sent = transport.sent
    await client.check_easyeda_footprint("C8734")
    assert transport.sent == sent  # nothing more goes out while paused
