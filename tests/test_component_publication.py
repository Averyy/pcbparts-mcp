"""Replay real subcategory records through scrape failure/retry/publication boundaries."""
import gzip
import json
from pathlib import Path
import sys
from datetime import datetime, timedelta, timezone
import pytest

from conftest import write_catalog_category
from pcbparts_mcp.catalog_files import read_catalog
from pcbparts_mcp.catalog_files import read_prices

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
import scrape_components as scrape
from check_component_scrape import validate_manifest
from build_history_db import build_history_db

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
@pytest.mark.parametrize('stock_change', [False, True])
async def test_real_records_retry_before_history_and_publish(tmp_path, monkeypatch, failures, stock_change):
    # Use a real entire subcategory, not invented components or API data.
    all_parts = [p for slug, p in read_catalog(ROOT / 'data/catalog') if slug == 'inductors-coils-chokes']
    sub_id = all_parts[0]['c']
    parts = [p for p in all_parts if p['c'] == sub_id]
    old_parts = parts
    if stock_change:
        parts = [dict(p) for p in parts]
        # A real part crossing into the recorded range, through the full publication path.
        parts[0]['s'] = 25 if abs(old_parts[0]['s'] - 25) > 10 else 50
        (tmp_path/'history').mkdir()
        with gzip.open(tmp_path/'history'/'2026-01.jsonl.gz', 'wt') as stream:
            stream.write(json.dumps({'l': parts[0]['l'], 'd': '2026-01-01', 's': 100})+'\n')
        legacy_history = (tmp_path/'history'/'2026-01.jsonl.gz').read_bytes()
    sub = json.loads((ROOT / 'data/subcategories.json').read_text(encoding="utf-8"))[str(sub_id)]
    slug = 'inductors-coils-chokes'
    write_catalog_category(tmp_path, slug, old_parts)
    target = tmp_path/'catalog'/'stock.tsv'
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
        if stock_change:
            assert list((tmp_path/'history').iterdir()) == [tmp_path/'history'/'2026-01.jsonl.gz']
            assert (tmp_path/'history'/'2026-01.jsonl.gz').read_bytes() == legacy_history
        else:
            assert not (tmp_path/'history').exists()
        assert (tmp_path/'.scrape-staging/progress.json').exists()
        await scrape.run_scraper(tmp_path, num_workers=1, resume=True)
    else:
        await scrape.run_scraper(tmp_path, num_workers=1)
    assert attempts == failures + 1
    loaded = [p for _, p in read_catalog(tmp_path/'catalog')]
    assert sorted(loaded, key=lambda p: p['l']) == sorted(parts, key=lambda p: p['l'])
    if stock_change:
        history_files = [p for p in (tmp_path/'history').rglob('*.jsonl.gz') if p.name != '2026-01.jsonl.gz']
        assert len(history_files) == 1
        with gzip.open(history_files[0], 'rt') as stream:
            events = [json.loads(line) for line in stream]
        assert len(events) == 1
        assert events[0]['before'] == old_parts[0]['s']
        assert events[0]['s'] == parts[0]['s']
        # Publication preserves older compressed event files alongside new before-values.
        assert (tmp_path/'history'/'2026-01.jsonl.gz').read_bytes() == legacy_history
        db_path = tmp_path/'stock_history.db'
        assert build_history_db(tmp_path, db_path, verbose=False)['total_events'] == 2
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            assert conn.execute('SELECT stock_before FROM stock_events ORDER BY date').fetchall() == [
                (None,), (old_parts[0]['s'],)]
    else:
        # Unchanged inventory, even after a failed attempt, must not emit gone/new events.
        assert not list((tmp_path/'history').rglob('*.jsonl.gz')) if (tmp_path/'history').exists() else True
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


def _small_part(code, stock=50, price=0.1, **fields):
    return {"l": code, "c": 2, "s": stock, "$": price, "t": "b", "d": "10Ω", **fields}


SMALL_CATEGORIES = [{"id": 1, "name": "Resistors"}, {"id": 2, "name": "Empty"}]


@pytest.mark.parametrize("age,missing_timestamp,refresh", [(6, False, False), (7, False, True),
                                                          (8, False, True), (1, True, True)])
def test_weekly_price_policy(tmp_path, age, missing_timestamp, refresh):
    first = datetime(2026, 10, 1, 23, 59, tzinfo=timezone.utc)
    previous = {"resistors": [_small_part("C1"), _small_part("C2", price=None),
                              _small_part("C3"), _small_part("C5", price=0.0)]}
    initial = scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, previous, scrape.ScrapeProgress(), now=first)
    assert initial["prices_updated_at"] == first.isoformat()
    if missing_timestamp:
        del initial["prices_updated_at"]
        (tmp_path / "manifest.json").write_text(json.dumps(initial), encoding="utf-8")
    # Date boundaries, not elapsed 24-hour intervals, govern weekly refresh.
    today = (first + timedelta(days=age)).replace(hour=0, minute=1)
    rows = [_small_part("C1", stock=20, price=0.2), _small_part("C2", price=0.3),
            _small_part("C4", price=0.4), _small_part("C5", price=0.5)]
    progress = scrape.ScrapeProgress()
    manifest = scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, {"resistors": rows}, progress, now=today)
    assert read_prices(tmp_path / "catalog") == {"C1": 0.2 if refresh else 0.1, "C2": 0.3,
                                                "C4": 0.4, "C5": 0.5 if refresh else 0.0}
    assert manifest["prices_updated_at"] == (today if refresh else first).isoformat()
    assert progress.category_counts == {"resistors": 4, "empty": 0}
    assert manifest["total_parts"] == progress.total_parts == 4
    assert manifest["categories"]["empty"]["status"] == "empty"
    daily = tmp_path / "history" / today.strftime("%Y-%m") / f"{today:%Y-%m-%d}.jsonl.gz"
    assert daily.exists()
    with gzip.open(daily, "rt", encoding="utf-8") as stream:
        events = [json.loads(line) for line in stream]
    change = next(e for e in events if e["l"] == "C1")
    assert change["$"] == 0.2  # History keeps scraped prices even when catalog prices stay frozen.
    assert change["before"] == 50
    assert next(e for e in events if e["l"] == "C3")["e"] == "gone"


def test_no_previous_prices_refreshes_even_with_timestamp(tmp_path):
    previous = "2026-10-01T00:00:00+00:00"
    (tmp_path / "manifest.json").write_text(json.dumps({"prices_updated_at": previous}), encoding="utf-8")
    now = datetime(2026, 10, 2, tzinfo=timezone.utc)
    result = scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES,
        {"resistors": [_small_part("C1")]}, scrape.ScrapeProgress(), now=now)
    assert result["prices_updated_at"] == now.isoformat()
    assert read_prices(tmp_path / "catalog") == {"C1": 0.1}


def test_missing_prices_file_is_rebuilt_not_fatal(tmp_path):
    """A catalog whose prices.tsv is missing (stock.tsv and parts intact) is repaired by the next
    scrape: it used to fail every day in history generation, before prices were rebuilt."""
    first = datetime(2026, 10, 1, 20, tzinfo=timezone.utc)
    scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, {"resistors": [_small_part("C1"), _small_part("C3")]},
                                scrape.ScrapeProgress(), now=first)
    (tmp_path / "catalog" / "prices.tsv").unlink()
    with pytest.raises(ValueError, match="prices.tsv"):
        list(read_catalog(tmp_path / "catalog"))  # what the database build would hit
    now = first + timedelta(days=1)
    manifest = scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES,
        {"resistors": [_small_part("C1", stock=20, price=0.2)]}, scrape.ScrapeProgress(), now=now)
    assert manifest["prices_updated_at"] == now.isoformat()
    assert read_prices(tmp_path / "catalog") == {"C1": 0.2}
    assert [p for _, p in read_catalog(tmp_path / "catalog")][0]["s"] == 20
    with gzip.open(tmp_path / "history" / "2026-10" / "2026-10-02.jsonl.gz", "rt", encoding="utf-8") as stream:
        events = {e["l"]: e for e in map(json.loads, stream)}
    assert events["C1"]["before"] == 50 and events["C1"]["s"] == 20
    assert events["C3"]["e"] == "gone" and events["C3"]["$"] is None


async def test_run_scraper_copies_weekly_timestamp_and_nested_history(tmp_path, monkeypatch):
    first = datetime(2026, 10, 1, tzinfo=timezone.utc)
    scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES,
        {"resistors": [_small_part("C1")]}, scrape.ScrapeProgress(), now=first)
    older = tmp_path / "history/2026-09/2026-09-30.jsonl.gz"
    older.parent.mkdir(parents=True)
    with gzip.open(older, "wt", encoding="utf-8") as stream:
        stream.write(json.dumps({"l": "C1", "d": "2026-09-30", "s": 60}) + "\n")
    old_history = older.read_bytes()
    async def prepare(staging, num_workers, resume):
        assert (staging / "history/2026-09/2026-09-30.jsonl.gz").read_bytes() == old_history
        assert json.loads((staging / "manifest.json").read_text(encoding="utf-8"))["prices_updated_at"] == first.isoformat()
        (staging / "subcategories.json").write_text("{}", encoding="utf-8")
        scrape.write_scrape_outputs(staging, SMALL_CATEGORIES,
            {"resistors": [_small_part("C1", stock=20, price=0.2)]}, scrape.ScrapeProgress(),
            now=first + timedelta(days=1))
    monkeypatch.setattr(scrape, "_run_scraper_staged", prepare)
    await scrape.run_scraper(tmp_path)
    assert read_prices(tmp_path / "catalog") == {"C1": 0.1}
    assert older.read_bytes() == old_history
    assert (tmp_path / "history/2026-10/2026-10-02.jsonl.gz").exists()


async def test_resume_after_failed_catalog_write_rebuilds_from_published(tmp_path, monkeypatch):
    """A write failure after history was appended and part files replaced (stock.tsv not yet
    written) left a staging catalog whose files disagree; --resume reused it and history failed."""
    first = datetime(2026, 10, 1, tzinfo=timezone.utc)
    scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES,
        {"resistors": [_small_part("C1"), _small_part("C3")]}, scrape.ScrapeProgress(), now=first)
    published = {p: p.read_bytes() for p in (tmp_path / "catalog").rglob("*") if p.is_file()}
    today = first + timedelta(days=1)
    rows = [_small_part("C1", stock=20), _small_part("C2", stock=40)]
    async def prepare(staging, num_workers, resume):
        (staging / "subcategories.json").write_text("{}", encoding="utf-8")
        scrape.write_scrape_outputs(staging, SMALL_CATEGORIES, {"resistors": rows},
                                    scrape.ScrapeProgress(), now=today)
    open_ = Path.open
    failed = False
    def fail_once(path, mode="r", *args, **kwargs):
        nonlocal failed
        if path.name == "stock.tsv" and mode.startswith("w") and not failed:
            failed = True
            raise OSError("injected catalog write failure")
        return open_(path, mode, *args, **kwargs)
    monkeypatch.setattr(scrape, "_run_scraper_staged", prepare)
    monkeypatch.setattr(Path, "open", fail_once)
    with pytest.raises(OSError, match="injected"):
        await scrape.run_scraper(tmp_path)
    assert {p: p.read_bytes() for p in (tmp_path / "catalog").rglob("*") if p.is_file()} == published
    await scrape.run_scraper(tmp_path, resume=True)
    assert {p["l"]: p["s"] for _, p in read_catalog(tmp_path / "catalog")} == {"C1": 20, "C2": 40}
    with gzip.open(tmp_path / "history/2026-10/2026-10-02.jsonl.gz", "rt", encoding="utf-8") as stream:
        events = [(e["l"], e.get("e", "change"), e["before"]) for e in map(json.loads, stream)]
    # Compared with the published catalog, and recorded once.
    assert sorted(events) == [("C1", "change", 50), ("C2", "new", None), ("C3", "gone", 50)]
    assert not (tmp_path / ".scrape-staging").exists()


def test_offline_outputs_deduplicate_and_append_daily_history(tmp_path):
    first = datetime(2026, 10, 31, tzinfo=timezone.utc)
    cats = [{"id": 1, "name": "A"}, {"id": 2, "name": "Z"}, {"id": 3, "name": "Empty"}]
    initial = {"z": [_small_part("C1", stock=30)],
               "a": [_small_part("C1", stock=50), _small_part("C1", stock=90)]}
    progress = scrape.ScrapeProgress(category_counts={"stale": 999})
    scrape.write_scrape_outputs(tmp_path, cats, initial, progress, now=first)
    assert progress.category_counts == {"a": 1, "z": 0, "empty": 0}
    assert list(read_catalog(tmp_path / "catalog")) == [("a", _small_part("C1", stock=50))]
    second = first + timedelta(days=1)
    result = {"a": [_small_part("C1", stock=20, price=0.2)]}
    scrape.write_scrape_outputs(tmp_path, cats, result, progress, now=second)
    daily = tmp_path / "history/2026-11/2026-11-01.jsonl.gz"
    original = daily.read_bytes()
    result["a"][0]["s"] = 40
    scrape.write_scrape_outputs(tmp_path, cats, result, progress, now=second)
    assert daily.read_bytes().startswith(original)
    with gzip.open(daily, "rt", encoding="utf-8") as stream:
        events = [json.loads(line) for line in stream]
    assert [(e["s"], e["before"]) for e in events] == [(20, 50), (40, 20)]
    assert all(e["d"] == "2026-11-01" and e["$"] == 0.2 for e in events)


def _snapshot(directory):
    return {p.relative_to(directory).as_posix(): p.read_bytes()
            for p in directory.rglob("*") if p.is_file()}


def test_publication_removes_stale_subcategory_and_empty_directories(tmp_path):
    write_catalog_category(tmp_path, "resistors", [_small_part("C1"), _small_part("C2", c=10)])
    write_catalog_category(tmp_path, "vanished", [_small_part("C3", c=3)])
    staging = tmp_path / ".scrape-staging"
    write_catalog_category(staging, "resistors", [_small_part("C1")])
    files = sorted(p for p in (staging / "catalog").rglob("*") if p.is_file())
    scrape.publish_staged_files(tmp_path, staging, files)
    assert not (tmp_path / "catalog/parts/resistors/10.jsonl").exists()
    assert not (tmp_path / "catalog/parts/vanished").exists()
    assert list(read_catalog(tmp_path / "catalog")) == [("resistors", _small_part("C1"))]


@pytest.mark.parametrize("operation", ["replace", "unlink", "rmdir"])
def test_publication_catalog_io_failure_rolls_back(tmp_path, monkeypatch, operation):
    write_catalog_category(tmp_path, "resistors", [_small_part("C1")])
    write_catalog_category(tmp_path, "vanished", [_small_part("C2", c=3)])
    staging = tmp_path / ".scrape-staging"
    write_catalog_category(staging, "resistors", [_small_part("C1", stock=20)])
    before = _snapshot(tmp_path / "catalog")
    prepared = _snapshot(staging / "catalog")
    target = {"replace": staging / "catalog/stock.tsv", "unlink": tmp_path / "catalog/parts/vanished/3.jsonl",
              "rmdir": tmp_path / "catalog/parts/vanished"}[operation]
    original = getattr(Path, operation)
    failed = False
    def fail_once(path, *args, **kwargs):
        nonlocal failed
        if path == target and not failed:
            failed = True
            raise OSError("injected catalog publication failure")
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, operation, fail_once)
    files = sorted(p for p in (staging / "catalog").rglob("*") if p.is_file())
    with pytest.raises(OSError, match="injected"):
        scrape.publish_staged_files(tmp_path, staging, files)
    assert _snapshot(tmp_path / "catalog") == before
    assert _snapshot(staging / "catalog") == prepared


def _day_events(root, day):
    path = root / "history" / day[:7] / f"{day}.jsonl.gz"
    if not path.exists():
        return {}
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return {(e["l"], e.get("e", "change")): e for e in map(json.loads, stream)}


def _gap_rows(size, missing=0, stock=50, sub=2, start=1):
    return [_small_part(f"C{n}", stock=stock, c=sub) for n in range(start, start + size - missing)]


def _subs(sizes, missing=None, stock=50):
    """Subcategories 2, 3, ... of the given sizes with disjoint codes, minus `missing` rows each."""
    rows, start = [], 1
    for index, size in enumerate(sizes):
        rows += _gap_rows(size, (missing or [0] * len(sizes))[index], stock=stock, sub=2 + index, start=start)
        start += size
    return {"resistors": rows}


def _gone(root, day):
    return [key for key in _day_events(root, day) if key[1] == "gone"]


FIRST = datetime(2026, 10, 1, 20, tzinfo=timezone.utc)


def test_gap_day_is_carried_for_two_days_then_accepted(tmp_path):
    """Several subcategories losing bulk at once (as on 2026-03-18 and 05-15, 97-100% back the next
    day) keep the previous rows, so history records no false gone events; after GAP_MAX_DAYS the
    loss is accepted."""
    lost = scrape.GAP_MIN_LOST
    sizes = [lost * 2] * scrape.GAP_MIN_SUBCATEGORIES + [50]
    missing = [lost] * scrape.GAP_MIN_SUBCATEGORIES + [0]
    scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, _subs(sizes), scrape.ScrapeProgress(), now=FIRST)
    short = _subs(sizes, missing, stock=20)
    since = (FIRST + timedelta(days=1)).date().isoformat()
    for offset in range(scrape.GAP_MAX_DAYS):
        now = FIRST + timedelta(days=1 + offset)
        manifest = scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, short, scrape.ScrapeProgress(), now=now)
        assert manifest["carried_forward"] == {
            str(2 + i): {"category": "resistors", "parts": lost, "of": lost * 2, "since": since}
            for i in range(scrape.GAP_MIN_SUBCATEGORIES)}
        assert manifest["total_parts"] == sum(sizes)
        stocks = {p["l"]: p["s"] for _, p in read_catalog(tmp_path / "catalog")}
        assert stocks["C1"] == 20 and stocks[f"C{lost * 2}"] == 50  # carried rows keep their last stock
        assert not _gone(tmp_path, now.date().isoformat())
    now = FIRST + timedelta(days=1 + scrape.GAP_MAX_DAYS)
    manifest = scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, short, scrape.ScrapeProgress(), now=now)
    assert "carried_forward" not in manifest
    assert manifest["total_parts"] == sum(sizes) - sum(missing)
    assert len(_gone(tmp_path, now.date().isoformat())) == sum(missing)


def test_one_very_large_loss_is_a_gap_alone(tmp_path):
    """2026-05-15: subcategory 3128 lost all 5,983 parts; 99.8% were back the next day."""
    size = scrape.GAP_SURE_LOST
    scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, _subs([size, 50]), scrape.ScrapeProgress(), now=FIRST)
    manifest = scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, _subs([size, 50], [size, 0]),
                                           scrape.ScrapeProgress(), now=FIRST + timedelta(days=1))
    assert manifest["carried_forward"]["2"]["parts"] == size
    assert not _gone(tmp_path, "2026-10-02")


@pytest.mark.parametrize("missing", [
    [128, 0],                                     # 2026-04-02: sub 2008 lost all 128, none came back
    [scrape.GAP_SURE_LOST - 1, 0],                # one bulk loss below the single-loss size
    [scrape.GAP_MIN_LOST, scrape.GAP_MIN_LOST],   # 2026-06-22: two bulk losses (112 and 100), delistings
])
def test_delistings_leave_the_same_day(tmp_path, missing):
    sizes = [max(m, scrape.GAP_MIN_LOST) * 2 if m else 50 for m in missing]
    scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, _subs(sizes), scrape.ScrapeProgress(), now=FIRST)
    manifest = scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, _subs(sizes, missing),
                                           scrape.ScrapeProgress(), now=FIRST + timedelta(days=1))
    assert "carried_forward" not in manifest
    assert len(_gone(tmp_path, "2026-10-02")) == sum(missing)


def test_gap_that_recovers_records_no_gone_or_new_events(tmp_path):
    sizes = [scrape.GAP_MIN_LOST * 2] * scrape.GAP_MIN_SUBCATEGORIES
    scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, _subs(sizes), scrape.ScrapeProgress(), now=FIRST)
    scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, _subs(sizes, [s // 2 for s in sizes]),
                                scrape.ScrapeProgress(), now=FIRST + timedelta(days=1))
    manifest = scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, _subs(sizes, stock=30),
                                           scrape.ScrapeProgress(), now=FIRST + timedelta(days=2))
    assert "carried_forward" not in manifest
    events = _day_events(tmp_path, "2026-10-03")
    assert {kind for _, kind in events} == {"change"} and len(events) == sum(sizes)
    assert all(e["before"] == 50 and e["s"] == 30 for e in events.values())


def test_new_loss_on_the_second_gap_day_is_judged_alone(tmp_path):
    """Subcategories still carried from yesterday don't make today's new loss a gap: one new bulk
    loss is a delisting and leaves the same day, while the carried ones keep their first day."""
    lost = scrape.GAP_MIN_LOST
    sizes = [lost * 2] * 4
    scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, _subs(sizes), scrape.ScrapeProgress(), now=FIRST)
    scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, _subs(sizes, [lost, lost, lost, 0]),
                                scrape.ScrapeProgress(), now=FIRST + timedelta(days=1))
    manifest = scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, _subs(sizes, [lost, lost, 0, lost]),
                                           scrape.ScrapeProgress(), now=FIRST + timedelta(days=2))
    assert {sub: entry["since"] for sub, entry in manifest["carried_forward"].items()} == {
        "2": "2026-10-02", "3": "2026-10-02"}
    gone = _gone(tmp_path, "2026-10-03")
    assert len(gone) == lost and {code for code, _ in gone} == {f"C{n}" for n in range(3 * lost * 2 + lost + 1, 4 * lost * 2 + 1)}


def test_gap_partly_back_next_day_keeps_the_rest_for_its_second_day(tmp_path):
    """A gap subcategory still missing when the others are back is carried for the gap's second
    day too (no gone events), then accepted."""
    lost = scrape.GAP_MIN_LOST
    sizes = [lost * 2] * scrape.GAP_MIN_SUBCATEGORIES
    scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, _subs(sizes), scrape.ScrapeProgress(), now=FIRST)
    scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, _subs(sizes, [lost] * len(sizes)),
                                scrape.ScrapeProgress(), now=FIRST + timedelta(days=1))
    rest = [lost] + [0] * (len(sizes) - 1)
    manifest = scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, _subs(sizes, rest),
                                           scrape.ScrapeProgress(), now=FIRST + timedelta(days=2))
    assert manifest["carried_forward"] == {"2": {"category": "resistors", "parts": lost, "of": lost * 2,
                                                 "since": "2026-10-02"}}
    assert not _gone(tmp_path, "2026-10-03")
    manifest = scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, _subs(sizes, rest),
                                           scrape.ScrapeProgress(), now=FIRST + timedelta(days=3))
    assert "carried_forward" not in manifest
    assert len(_gone(tmp_path, "2026-10-04")) == lost


def test_moved_parts_are_not_lost(tmp_path):
    size = scrape.GAP_SURE_LOST
    scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, _subs([size]), scrape.ScrapeProgress(), now=FIRST)
    moved = {"resistors": _gap_rows(size, sub=7)}  # every part moved to another subcategory
    manifest = scrape.write_scrape_outputs(tmp_path, SMALL_CATEGORIES, moved, scrape.ScrapeProgress(),
                                           now=FIRST + timedelta(days=1))
    assert "carried_forward" not in manifest
    assert {p["c"] for _, p in read_catalog(tmp_path / "catalog")} == {7}
    assert not _gone(tmp_path, "2026-10-02")


def test_gate_judges_scraped_counts_not_carried_rows():
    previous = {"total_parts": 2000, "categories": {"resistors": {"count": 2000}}}
    current = {"total_parts": 2000, "categories": {"resistors": {"count": 2000}},
               "carried_forward": {"2": {"category": "resistors", "parts": 50, "of": 60, "since": "2026-10-02"}}}
    assert validate_manifest(previous, current) == []
    current["carried_forward"]["2"]["parts"] = 700
    failures = validate_manifest(previous, current)
    assert "total part count dropped more than 5%" in failures
    assert "resistors: part count dropped more than 30%" in failures
    assert validate_manifest(previous, current, allow_count_drop=True) == []


@pytest.mark.parametrize("empty_pages,collected", [(1, 250), (scrape.EMPTY_PAGE_RETRIES + 1, 100)])
async def test_empty_page_before_listed_total_is_retried(monkeypatch, caplog, empty_pages, collected):
    sub = scrape.Subcategory(id=2, name="Chip Resistor", category_id=1, category_name="Resistors",
                             category_slug="resistors")
    calls = []
    async def fake_request(params, session):
        page = params["currentPage"]
        calls.append(page)
        if page == 2 and calls.count(2) <= empty_pages:
            return {"data": {"componentPageInfo": {"list": [], "total": 250}}}
        start = (page - 1) * scrape.PAGE_SIZE
        items = [{"componentCode": f"C{n}", "stockCount": 50, "componentLibraryType": "base"}
                 for n in range(start + 1, min(start + scrape.PAGE_SIZE, 250) + 1)]
        return {"data": {"componentPageInfo": {"list": items, "total": 250}}}
    monkeypatch.setattr(scrape, "make_request", fake_request)
    with caplog.at_level("WARNING"):
        parts, count = await scrape.scrape_subcategory(sub, session=None)
    assert count == len(parts) == collected
    assert calls.count(2) == min(empty_pages + 1, scrape.EMPTY_PAGE_RETRIES + 1)
    assert "empty page 2 with 100 of 250" in caplog.text
    if collected < 250:
        assert "collected 100 of 250 listed parts" in caplog.text


async def test_every_page_gets_its_own_empty_page_retries(monkeypatch):
    sub = scrape.Subcategory(id=2, name="Chip Resistor", category_id=1, category_name="Resistors",
                             category_slug="resistors")
    total, calls = 350, []
    async def fake_request(params, session):
        page = params["currentPage"]
        calls.append(page)
        if page in (2, 3) and calls.count(page) <= scrape.EMPTY_PAGE_RETRIES:
            return {"data": {"componentPageInfo": {"list": [], "total": total}}}
        start = (page - 1) * scrape.PAGE_SIZE
        items = [{"componentCode": f"C{n}", "stockCount": 50, "componentLibraryType": "base"}
                 for n in range(start + 1, min(start + scrape.PAGE_SIZE, total) + 1)]
        return {"data": {"componentPageInfo": {"list": items, "total": total}}}
    monkeypatch.setattr(scrape, "make_request", fake_request)
    parts, count = await scrape.scrape_subcategory(sub, session=None)
    assert count == total
