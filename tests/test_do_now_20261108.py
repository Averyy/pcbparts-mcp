"""Real-data regressions for the consolidated do-now queue."""
import sys
from pathlib import Path

from fastmcp import Client
import pytest
import pcbparts_mcp.server as server
from pcbparts_mcp.parsers import parse_impedance_at_freq

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from search_baseline import offline


@pytest.fixture
async def local_client():
    with offline():
        async with Client(server.mcp) as client:
            yield client


async def call(client, name='jlc_search', **kwargs):
    return (await client.call_tool(name, kwargs)).structured_content


@pytest.mark.parametrize('args', [
    {'query': '-5V LDO'}, {'query': 'negative 5V LDO'},
    {'subcategory_name': 'Voltage Regulators - Linear, Low Drop Out (LDO) Regulators',
     'spec_filters': [{'name': 'Vout', 'op': '=', 'value': '-5V'}]},
])
async def test_negative_output(local_client, args):
    r = await call(local_client, **args, limit=100)
    assert r['results']
    for p in r['results']:
        assert (p['specs'].get('Output Configuration') == 'Negative'
                or p['specs'].get('Output Voltage', '').startswith('-')), p


async def test_impedance_condition(local_client):
    base = dict(subcategory_name='Ferrite Beads', package='0603', limit=100)
    for freq in ('100MHz', '1GHz'):
        r = await call(local_client, **base, spec_filters=[{'name':'Impedance @ Frequency','op':'=','value':f'600Ohm@{freq}'}])
        if freq == '100MHz':
            assert r['results']
        for p in r['results']:
            assert parse_impedance_at_freq(p['specs']['Impedance @ Frequency'])[1] == (1e8 if freq == '100MHz' else 1e9)
    r = await call(local_client, query='ferrite bead 600ohm at 1GHz 0603', limit=100)
    assert not r['results'] or all(parse_impedance_at_freq(p['specs']['Impedance @ Frequency'])[1] == 1e9 for p in r['results'])


async def test_negation_not_positive_identity(local_client):
    r = await call(local_client, query='3.3V LDO not AMS1117')
    assert r['results'] == [] and 'exclusions' in r['error']
    assert (await call(local_client, query='AMS1117 3.3V', library_type='all'))['results']
    assert (await call(local_client, query='10k resistor no fee'))['results']


async def test_bounded_empty_diagnostics(local_client):
    r = await call(local_client, query='usb-c', library_type='no_fee')
    assert r['results'] == []
    why = r['why_empty']
    suggestion = next(b for b in why['blocking'] if b['constraint'] == 'library_type')
    assert suggestion['matches_without'] > 0
    recovered = await call(local_client, **suggestion['next_call']['arguments'])
    assert recovered['results']
    assert all(p['specs']['Connector Type'] == 'Type-C' for p in recovered['results'])
    r = await call(local_client, query='BME280', package='0402', strict=True)
    assert any(b['constraint']=='package' for b in r['why_empty']['blocking'])
    r = await call(local_client, query='10k resistor', package='QFN-999', min_stock=2_000_000_000, strict=True)
    assert not r['results'] and not r['why_empty']['blocking']
    assert r['why_empty']['extra_queries'] <= 3
    assert 'why_empty' not in await call(local_client, query='10k resistor')


async def test_diagnostic_budget_does_not_interrupt_regular_search(local_client, monkeypatch):
    from pcbparts_mcp.search import diagnostics
    monkeypatch.setattr(diagnostics, 'DIAGNOSTIC_SECONDS', 0)
    r = await call(local_client, query='BME280', package='0402', strict=True)
    assert r['why_empty']['diagnostics_complete'] is False
    assert (await call(local_client, query='BME280'))['results']


async def test_snapshot_provenance_and_explicit_live_next_step(local_client):
    hit = await call(local_client, 'jlc_get_part', mpn='BAV99,215')
    assert hit['data_as_of']
    assert all(p['data_source']['kind']=='snapshot' and p['data_source']['observed_at']==hit['data_as_of'] for p in hit['results'])
    miss = await call(local_client, 'jlc_get_part', mpn='LC709203F')
    assert not miss['results']
    assert 'snapshot' in miss['error']
    assert miss['availability']=='unknown_outside_snapshot'
    assert miss['next_call']=={'tool':'jlc_stock_check','arguments':{'query':'LC709203F','min_stock':0,'limit':10}}
    # Offline fixture would fail if the handler executed the suggested live request.


async def test_physical_sensor_identity_and_capabilities(local_client):
    rotation = await call(local_client,'sensor_recommend',measure='rotation',protocol='i2c',limit=50)
    assert rotation['results'] and all(p['id']!='rp2040' for p in rotation['results'])
    direct = await call(local_client,'sensor_recommend',measure='co2',limit=50)
    assert all(p['id']!='ccs811' for p in direct['results'])
    estimated = await call(local_client,'sensor_recommend',measure='eco2',limit=50)
    ccs = next(p for p in estimated['results'] if p['id']=='ccs811')
    assert ccs['voltage']=='1.8-3.3'
    assert not {'co2','temperature','humidity'} & set(ccs['measures'])
    assert ccs['compensation_inputs']==['humidity','temperature']
    assert ccs['voltage_evidence']['absolute_maximum']=='3.6V'
    scd = (await call(local_client,'sensor_recommend',query='SCD4X'))['results'][0]
    assert not any(term in scd['description'].lower() for term in ('particulate','nox','no x','multi-gas'))
    assert {'co2','temperature','humidity'} <= set(scd['measures'])
    assert scd['urls']


async def test_fee_savings_are_explicit_estimates(local_client):
    from search_baseline import local_alternatives
    from pcbparts_mcp.db import get_db
    with local_alternatives(server._client, get_db()):
        r = await call(local_client,'jlc_find_alternatives',lcsc='C2930027',library_type='no_fee',same_package=True,limit=3)
    savings = r['comparison']['savings']
    assert savings['is_estimate'] is True
    assert savings['assembly_service_assumption']=='Economic'
    assert savings['loading_fee_per_extended_type_estimate_usd']==3.0
    assert savings['assembly_fee']==3.0
    assert 'estimate' in r['summary']['message']
    assert 'Standard' in savings['note']
