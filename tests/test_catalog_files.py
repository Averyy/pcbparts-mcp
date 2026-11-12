"""Lossless, deterministic catalog storage and strict corruption detection."""

import json

import pytest

from pcbparts_mcp import catalog_files as catalog


def _part(code="C9", **fields):
    return {"l": code, "m": "10kΩ", "f": "制造商", "p": "0603", "s": 15,
            "t": "b", "c": 2, "$": 0.12345678901234567, "d": "125℃", "a": [], **fields}


def _write(directory, rows=None):
    rows = rows if rows is not None else [_part()]
    catalog.write_catalog(directory, {"resistors": rows}, {p["l"]: p["$"] for p in rows})


def _bytes(directory):
    return {p.relative_to(directory).as_posix(): p.read_bytes()
            for p in directory.rglob("*") if p.is_file()}


def test_exact_round_trip_and_deterministic_rewrite(tmp_path):
    rows = [_part("C10", s=None, **{"$": None, "x": 0, "n": 1}),
            _part("C9"), _part("C_unknown", c=10, x=None)]
    parts = {"resistors": rows, "empty": [], "capacitors": [_part("C1", c=9)]}
    prices = {p["l"]: p["$"] for rows in parts.values() for p in rows}
    assert catalog.write_catalog(tmp_path, parts, prices) == {"resistors": 3, "empty": 0, "capacitors": 1}
    before = _bytes(tmp_path)
    read = list(catalog.read_catalog(tmp_path))
    assert read == [("capacitors", parts["capacitors"][0]), ("resistors", parts["resistors"][1]),
                    ("resistors", parts["resistors"][0]), ("resistors", parts["resistors"][2])]
    assert not (tmp_path / "parts/empty").exists()
    assert b"\r" not in b"".join(before.values())
    assert all(raw.endswith(b"\n") for raw in before.values())
    assert "Ω".encode() in before["parts/resistors/2.jsonl"]
    assert "℃".encode() in before["parts/resistors/2.jsonl"]
    assert list(json.loads(before["parts/resistors/2.jsonl"].splitlines()[0])) == [
        "l", "m", "f", "p", "t", "c", "d", "a"]
    assert before["stock.tsv"].decode().splitlines() == ["C1\t15", "C9\t15", "C10\t", "C_unknown\t15"]
    assert catalog.read_prices(tmp_path) == prices
    # A rewrite also removes vanished subcategories and categories.
    (tmp_path / "parts/stale").mkdir()
    (tmp_path / "parts/stale/1.jsonl").write_text("obsolete\n", encoding="utf-8")
    catalog.write_catalog(tmp_path, dict(reversed(list(parts.items()))), prices)
    assert _bytes(tmp_path) == before


def test_numeric_subcategory_order_and_file_row_order(tmp_path):
    _write(tmp_path, [_part("C3", c=10), _part("C10"), _part("C9")])
    assert [p["l"] for _, p in catalog.read_catalog(tmp_path)] == ["C9", "C10", "C3"]
    path = tmp_path / "parts/resistors/2.jsonl"
    path.write_bytes(b"\n".join(reversed(path.read_bytes().splitlines())) + b"\n")
    assert [p["l"] for _, p in catalog.read_catalog(tmp_path)] == ["C10", "C9", "C3"]


@pytest.mark.parametrize("raw", [b"{bad json\n", b"\n", b"[]\n", b"null\n", b"{}\n",
                                  b'{"l":123,"c":2}\n', b'{"l":"C9","c":3}\n',
                                  b'{"l":"C9","c":2,"s":1}\n', b"\xff\n"])
def test_malformed_part_line_names_file_and_line(tmp_path, raw):
    _write(tmp_path)
    (tmp_path / "parts/resistors/2.jsonl").write_bytes(raw)
    with pytest.raises(ValueError, match=r"2.jsonl line 1"):
        list(catalog.read_catalog(tmp_path))


def test_duplicate_lcsc_across_files(tmp_path):
    _write(tmp_path)
    (tmp_path / "parts/another").mkdir()
    (tmp_path / "parts/another/2.jsonl").write_bytes((tmp_path / "parts/resistors/2.jsonl").read_bytes())
    with pytest.raises(ValueError, match=r"2.jsonl line 1: duplicate LCSC C9"):
        list(catalog.read_catalog(tmp_path))


@pytest.mark.parametrize("name", ["stock", "prices"])
def test_missing_tsv_row(tmp_path, name):
    _write(tmp_path)
    (tmp_path / f"{name}.tsv").write_bytes(b"")
    with pytest.raises(ValueError, match=rf"2.jsonl line 1: C9: missing row in {name}.tsv"):
        list(catalog.read_catalog(tmp_path))


@pytest.mark.parametrize("name", ["stock", "prices"])
def test_missing_tsv_file(tmp_path, name):
    _write(tmp_path)
    (tmp_path / f"{name}.tsv").unlink()
    with pytest.raises(ValueError, match=rf"{name}.tsv: missing catalog file"):
        list(catalog.read_catalog(tmp_path))


@pytest.mark.parametrize("name", ["stock", "prices"])
def test_orphan_tsv_row(tmp_path, name):
    _write(tmp_path)
    with (tmp_path / f"{name}.tsv").open("a", encoding="utf-8", newline="\n") as stream:
        stream.write("C100\t1\n")
    with pytest.raises(ValueError, match=rf"{name}.tsv: C100 has no part"):
        list(catalog.read_catalog(tmp_path))


@pytest.mark.parametrize("name,raw", [
    ("stock", b"C9\t1.5\n"), ("stock", b"C9\t1\textra\n"), ("prices", b"C9\n"),
    ("prices", b"C9\tnull\n"), ("prices", b"C9\tNaN\n"), ("prices", b"C9\ttrue\n"),
    ("prices", b"C9\tbad\n"), ("stock", b"\t1\n"), ("prices", b"C9\t1\r\n"),
    ("stock", b"C9\t1\nC9\t2\n"), ("prices", b"C9\t1\nC9\t2\n"),
])
def test_malformed_tsv(tmp_path, name, raw):
    _write(tmp_path)
    (tmp_path / f"{name}.tsv").write_bytes(raw)
    with pytest.raises(ValueError, match=rf"{name}.tsv line [12]: malformed TSV"):
        list(catalog.read_catalog(tmp_path))


def test_invalid_subcategory_filename(tmp_path):
    _write(tmp_path)
    (tmp_path / "parts/resistors/2.jsonl").rename(tmp_path / "parts/resistors/bad.jsonl")
    with pytest.raises(ValueError, match="bad.jsonl: invalid numeric subcategory"):
        list(catalog.read_catalog(tmp_path))


def test_duplicate_lcsc_write_error(tmp_path):
    with pytest.raises(ValueError, match="Duplicate LCSC C9"):
        catalog.write_catalog(tmp_path, {"a": [_part()], "b": [_part()]}, {"C9": 1.0})


@pytest.mark.parametrize("name", ["parts/resistors/2.jsonl", "stock.tsv", "prices.tsv"])
def test_size_guard_checks_every_file(tmp_path, monkeypatch, name):
    # Isolate each target's apparent size without allocating 95 MB fixtures.
    check = catalog._check_size
    def check_target(path):
        if path.relative_to(tmp_path).as_posix() == name:
            monkeypatch.setattr(catalog, "MAX_FILE_BYTES", 1)
            check(path)
    monkeypatch.setattr(catalog, "_check_size", check_target)
    with pytest.raises(ValueError, match="exceeds catalog file limit"):
        _write(tmp_path)


def test_size_warning(tmp_path, monkeypatch, caplog):
    monkeypatch.setattr(catalog, "WARN_FILE_BYTES", 1)
    _write(tmp_path)
    assert "GitHub's 50 MB warning size" in caplog.text


def test_read_without_prices(tmp_path):
    """The scraper reads a previous catalog whose prices.tsv is missing with prices=False."""
    catalog.write_catalog(tmp_path, {"resistors": [{"l": "C1", "c": 2, "s": 5, "$": 0.1, "t": "b"}]}, {"C1": 0.1})
    (tmp_path / "prices.tsv").unlink()
    assert [p for _, p in catalog.read_catalog(tmp_path, prices=False)] == [{"l": "C1", "c": 2, "t": "b", "s": 5, "$": None}]
    with pytest.raises(ValueError, match="prices.tsv"):
        list(catalog.read_catalog(tmp_path))


def test_git_ignores_no_catalog_file():
    """git add skips ignored files without a word: the Python template's `parts/` rule once hid
    every data/catalog/parts file, so a commit would have kept only stock.tsv and prices.tsv."""
    import shutil
    import subprocess
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    git = shutil.which("git")
    if git is None or not (root / ".git").exists():
        pytest.skip("needs a git checkout")
    paths = [p.relative_to(root).as_posix() for p in (root / "data/catalog").rglob("*") if p.is_file()]
    # Category directories are named after JLCPCB categories: every directory pattern in
    # .gitignore must leave a same-named category alone.
    for line in (root / ".gitignore").read_text(encoding="utf-8").splitlines():
        name = line.strip().rstrip("/")
        if line.strip().endswith("/") and name and "/" not in name and "*" not in name:
            paths += [f"data/catalog/parts/{name}/1.jsonl", f"data/catalog/{name}/1.jsonl"]
    assert any(path.startswith("data/catalog/parts/") for path in paths)
    result = subprocess.run([git, "check-ignore", "--no-index", "--stdin"], input="\n".join(paths),
                            cwd=root, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 1 and result.stdout == "", result.stdout
