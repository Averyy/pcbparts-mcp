"""wafer 0.7.18+ compatibility at the application boundary; fake transports only."""

from pathlib import Path
import sys

import pytest
import wreq
import wreq.blocking

from pcbparts_mcp.client import JLCPCBClient, JLCPCBUnavailable
from pcbparts_mcp.config import JLCPCB_SEARCH_URL
from test_easyeda_critical_ch import _Reply, _Transport

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scrape_components import create_scraper_session, make_request
from scrapers import common


DENIALS = [
    pytest.param({}, '<html>Forbidden<script src="/cdn-cgi/scripts/abc/cloudflare-static/email-decode.min.js">'
                    '</script></html>', None, id="cf-injected"),
    pytest.param({}, '<html><link rel="stylesheet" href="/cdn-cgi/styles/cf.errors.css">Access denied</html>',
                 "cloudflare_block", id="cf-block"),
    pytest.param({"server": "AkamaiGHost", "x-reference-error": "offline-reference"},
                 '<html><title>Access to this page has been denied.</title></html>', "akamai_denied", id="akamai-denied"),
]


def offline_session(session, reply, monkeypatch, *, terminal=True):
    transport = _Transport(reply)
    monkeypatch.setattr(wreq, "Client", lambda **kwargs: transport)
    monkeypatch.setattr(wreq.blocking, "Client", lambda **kwargs: transport)
    session._client = transport
    session._rate_limiter = None

    def no_rebuild(*args, **kwargs):
        # JLCPCB rotates before each new request (rotate_every=1), but must stop on a denial.
        if terminal and transport.sent:
            pytest.fail("A terminal response must not rotate or build a real transport")

    monkeypatch.setattr(session, "_rebuild_client", no_rebuild)
    return transport


@pytest.mark.parametrize("headers, body, challenge", DENIALS)
async def test_easyeda_pauses_on_every_403_regardless_of_challenge_label(monkeypatch, headers, body, challenge):
    client = JLCPCBClient()
    session = client._get_easyeda_products_session()
    transport = offline_session(session, _Reply(403, {"content-type": "text/html", **headers}, body), monkeypatch)
    get = session.get
    responses = []

    async def record_get(*args, **kwargs):
        response = await get(*args, **kwargs)
        responses.append(response)
        return response

    monkeypatch.setattr(session, "get", record_get)
    try:
        result, status = await client._check_easyeda_footprint("C2040")
        assert result["has_easyeda_footprint"] is None and status == "blocked"
        assert responses[0].challenge_type == challenge and transport.sent == 1
        assert client._easyeda_products_cooldown.active
        assert (await client._check_easyeda_footprint("C8734"))[1] == "cooldown"
        assert transport.sent == 1
    finally:
        await client.close()


# An injected script alone is unclassified: wafer may rotate a bare 403 (covered below).
@pytest.mark.parametrize("headers, body, challenge", DENIALS[1:])
async def test_jlcpcb_terminal_denials_do_not_rotate(monkeypatch, headers, body, challenge):
    client = JLCPCBClient()
    transport = offline_session(client._get_jlcpcb_session(),
                                _Reply(403, {"content-type": "text/html", **headers}, body), monkeypatch)
    try:
        with pytest.raises(JLCPCBUnavailable, match="WAF challenge"):
            await client._request(JLCPCB_SEARCH_URL, {"keyword": "LM358DR"})
        assert transport.sent == 1
    finally:
        await client.close()


async def test_jlcpcb_unclassified_403_retirement_stays_offline(monkeypatch):
    client = JLCPCBClient()
    session = client._get_jlcpcb_session()
    _, body, _ = DENIALS[0].values
    transport = offline_session(session, _Reply(403, {"content-type": "text/html"}, body),
                                monkeypatch, terminal=False)
    monkeypatch.setattr(session, "_rotation_delay", lambda: 0)
    retire = session._retire_session
    retired = []

    async def record_retirement(domain):
        await retire(domain)
        retired.append(domain)
        assert session._client is transport

    monkeypatch.setattr(session, "_retire_session", record_retirement)
    try:
        with pytest.raises(JLCPCBUnavailable):
            await client._request(JLCPCB_SEARCH_URL, {"keyword": "LM358DR"})
        assert transport.sent == session.max_rotations + 1
        assert retired
    finally:
        await client.close()


@pytest.mark.parametrize("consumer", ["jlcpcb", "easyeda", "scraper"])
async def test_bad_redirect_is_handled_as_a_request_error(monkeypatch, consumer):
    client = JLCPCBClient()
    session = (client._get_jlcpcb_session() if consumer == "jlcpcb" else
               client._get_easyeda_products_session() if consumer == "easyeda" else create_scraper_session())
    transport = offline_session(session, _Reply(302, {"location": "https://[broken"}, ""), monkeypatch)
    try:
        if consumer == "jlcpcb":
            with pytest.raises(JLCPCBUnavailable, match="connection failed"):
                await client._request(JLCPCB_SEARCH_URL, {"keyword": "LM358DR"})
        elif consumer == "easyeda":
            result, status = await client._check_easyeda_footprint("C2040")
            assert result["has_easyeda_footprint"] is None and status == "error"
            assert not client._easyeda_products_cooldown.active
        else:
            with pytest.raises(ValueError, match="connection failed"):
                await make_request({"keyword": "LM358DR"}, session)
        assert transport.sent == 1
    finally:
        await client.close()


def test_malformed_sensor_link_is_not_evidence_the_sensor_is_gone(monkeypatch):
    session = common.make_session(15, rate_limit=0)
    assert session.attempt_timeout.total_seconds() == common.attempt_cap(15) == 5
    transport = offline_session(session, None, monkeypatch)
    with pytest.raises(ValueError, match="not a URL"):
        session.get("https://[broken", timeout=15)
    monkeypatch.setattr(common.wafer, "SyncSession", lambda **kwargs: session)
    assert common._links_gone(["https://[broken"]) is False
    assert transport.sent == 0


async def test_user_input_stays_in_jlcpcb_json_and_invalid_easyeda_ids_are_not_sent(monkeypatch):
    client = JLCPCBClient()
    session = client._get_jlcpcb_session()
    transport = offline_session(session, _Reply(200, {"content-type": "application/json"}, '{"code": 200}'), monkeypatch)
    request = transport.request
    sent = []

    async def record_request(method, url, **kwargs):
        sent.append((url, kwargs))
        return await request(method, url, **kwargs)

    monkeypatch.setattr(transport, "request", record_request)
    number = "https://[bad/MPN?#&\n"
    try:
        await client._request(JLCPCB_SEARCH_URL, {"keyword": number})
        assert sent[0][0] == JLCPCB_SEARCH_URL and sent[0][1]["json"]["keyword"] == number
        assert (await client._check_easyeda_footprint(number))[1] == "invalid"
        with pytest.raises(ValueError, match="Invalid UUID"):
            await client.get_easyeda_component(number)
        assert transport.sent == 1
    finally:
        await client.close()
