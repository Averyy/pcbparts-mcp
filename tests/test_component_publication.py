"""Replay real subcategory records through scrape failure/retry/publication boundaries."""
import gzip
import json
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
import scrape_components as scrape
from check_component_scrape import validate_manifest

ROOT = Path(__file__).parent.parent


def test_manifest_gate_uses_real_manifest():
    previous = json.loads((ROOT / 'data/manifest.json').read_text(encoding="utf-8"))
    assert not validate_manifest(previous, previous)
    failed = {**previous, 'failed_subcategories': [3050]}
    assert 'failed subcategories remain' in validate_manifest(previous, failed, allow_count_drop=True)
    dropped = json.loads(json.dumps(previous))
    slug = next(k for k,v in dropped['categories'].items() if v['count'] >= 1000)
    lost = dropped['categories'][slug]['count']
    dropped['categories'][slug]['count'] = 0
    dropped['total_parts'] -= lost
    assert any(slug in error for error in validate_manifest(previous, dropped))
    assert not validate_manifest(previous, dropped, allow_count_drop=True)


@pytest.mark.parametrize('failures', [0, 1, 2])
async def test_real_records_retry_before_history_and_publish(tmp_path, monkeypatch, failures):
    # Use a real entire subcategory, not invented components or API data.
    with gzip.open(ROOT / 'data/categories/inductors-coils-chokes.jsonl.gz', 'rt') as stream:
        all_parts = [json.loads(line) for line in stream]
    sub_id = all_parts[0]['c']
    parts = [p for p in all_parts if p['c'] == sub_id]
    sub = json.loads((ROOT / 'data/subcategories.json').read_text(encoding="utf-8"))[str(sub_id)]
    slug = 'inductors-coils-chokes'
    (tmp_path/'categories').mkdir()
    target = tmp_path/'categories'/f'{slug}.jsonl.gz'
    with gzip.open(target, 'wt') as stream:
        for part in parts:
            stream.write(json.dumps(part)+'\n')
    manifest = {'total_parts':len(parts),'categories':{slug:{'id':sub['category_id'],'name':sub['category_name'],'count':len(parts)}}}
    (tmp_path/'manifest.json').write_text(json.dumps(manifest),encoding="utf-8")
    original = target.read_bytes()
    attempts = 0
    class ReplaySession:
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
    async def categories(session):
        return [{'id':sub['category_id'],'name':sub['category_name'],
                 'subcategories':[{'id':sub_id,'name':sub['name'],'count':len(parts)}]}]
    async def recorded(subcategory, session):
        nonlocal attempts
        attempts += 1
        if attempts <= failures:
            raise RuntimeError('injected transport failure replaying real records')
        return parts, len(parts)
    monkeypatch.setattr(scrape, 'create_scraper_session', ReplaySession)
    monkeypatch.setattr(scrape, 'fetch_categories', categories)
    monkeypatch.setattr(scrape, 'scrape_subcategory', recorded)
    monkeypatch.setattr(scrape, 'WORKER_STAGGER', 0)
    if failures == 2:
        with pytest.raises(RuntimeError, match='incomplete'):
            await scrape.run_scraper(tmp_path, num_workers=1)
        assert target.read_bytes() == original
        assert not (tmp_path/'history').exists()
        assert (tmp_path/'.scrape-staging/progress.json').exists()
        await scrape.run_scraper(tmp_path, num_workers=1, resume=True)
    else:
        await scrape.run_scraper(tmp_path, num_workers=1)
    assert attempts == failures + 1
    with gzip.open(target, 'rt') as stream:
        assert [json.loads(line) for line in stream] == parts
    # Unchanged real inventory, even after a failed first attempt, must not emit gone/new events.
    assert not list((tmp_path/'history').glob('*.jsonl.gz')) if (tmp_path/'history').exists() else True
    assert not (tmp_path/'.scrape-staging').exists()


def test_publication_io_failure_rolls_back_real_metadata(tmp_path, monkeypatch):
    staging = tmp_path/'.scrape-staging'
    staging.mkdir()
    before, prepared = {}, {}
    for name in ('manifest.json','subcategories.json'):
        raw = (ROOT/'data'/name).read_bytes()
        (tmp_path/name).write_bytes(raw)
        before[name] = raw
        prepared[name] = json.dumps(json.loads(raw),indent=4).encode()
        (staging/name).write_bytes(prepared[name])
    replace = Path.replace
    failed = False
    def fail_once(path, target):
        nonlocal failed
        if path == staging/'subcategories.json' and not failed:
            failed = True
            raise OSError('injected publication failure')
        return replace(path,target)
    monkeypatch.setattr(Path,'replace',fail_once)
    with pytest.raises(OSError, match='injected'):
        scrape.publish_staged_files(tmp_path,staging,[staging/'manifest.json',staging/'subcategories.json'])
    assert all((tmp_path/name).read_bytes()==raw for name,raw in before.items())
    assert all((staging/name).read_bytes()==raw for name,raw in prepared.items())
