"""Static URLs carry a hash of the static files, so browsers load new code after a deploy."""

import os
import re
from pathlib import Path

import pcbparts_dashboard

from test_server import request, start_server  # noqa: F401 (start_server is a fixture)

PAGE = (b'<!doctype html><link rel="stylesheet" href="/static/style.css">'
        b'<script type="module" src="/static/app.js"></script><img src="/static/favicon.svg">')
APP = b'import { a } from "./format.js";\nimport {\n  b,\n} from \'./data.js\';\nconst url = "/api/data";\n'


def version_of(body):
    found = set(re.findall(rb"\?v=([0-9a-f]+)", body))
    assert len(found) == 1, body
    return found.pop().decode()


def test_page_and_module_urls_carry_one_version(start_server):
    start, static = start_server
    (static / "index.html").write_bytes(PAGE)
    (static / "app.js").write_bytes(APP)
    (static / "style.css").write_bytes(b"body{}")
    server = start()
    status, headers, page = request(server, "/")
    assert status == 200 and headers["Cache-Control"] == "no-cache"
    version = version_of(page)
    assert page == PAGE.replace(b'.css"', f'.css?v={version}"'.encode()).replace(
        b'.js"', f'.js?v={version}"'.encode()).replace(b'.svg"', f'.svg?v={version}"'.encode())
    status, headers, app = request(server, f"/static/app.js?v={version}")
    assert status == 200 and headers["Cache-Control"] == "private, max-age=31536000, immutable"
    assert app == (b'import { a } from "./format.js?v=' + version.encode() + b'";\nimport {\n  b,\n} from \'./data.js?v='
                   + version.encode() + b'\';\nconst url = "/api/data";\n')
    # an old or missing version is checked again each time rather than kept
    for path in ("/static/style.css", "/static/style.css?v=000000000000"):
        status, headers, body = request(server, path)
        assert (status, body, headers["Cache-Control"]) == (200, b"body{}", "no-cache")


def test_any_changed_file_changes_the_version(start_server):
    start, static = start_server
    (static / "index.html").write_bytes(PAGE)
    (static / "data.js").write_bytes(b"export const a = 1;\n")
    server = start()
    first = version_of(request(server, "/")[2])
    (static / "data.js").write_bytes(b"export const a = 22;\n")
    stat = (static / "data.js").stat()
    os.utime(static / "data.js", ns=(stat.st_atime_ns, stat.st_mtime_ns + 10**9))
    second = version_of(request(server, "/")[2])
    assert first != second
    assert request(server, f"/static/data.js?v={first}")[1]["Cache-Control"] == "no-cache"
    assert request(server, f"/static/data.js?v={second}")[1]["Cache-Control"] == "private, max-age=31536000, immutable"


def test_the_shipped_page_references_only_versioned_assets():
    from pcbparts_dashboard.server import MODULE_IMPORT

    static = Path(pcbparts_dashboard.__file__).with_name("static")
    page = (static / "index.html").read_bytes()
    assert b"/static/app.js" in page and b"/static/style.css" in page
    modules = sorted(static.glob("*.js"))
    assert {path.name for path in modules} >= {"app.js", "data.js", "charts.js", "format.js", "labels.js"}
    for path in modules:
        source = path.read_bytes()
        # every module import, in either quote style, is relative, so the version reaches it
        imports = re.findall(rb"""\bfrom\s*(["'])([^"']*)\1""", source)
        assert all(re.fullmatch(rb"\./[\w.-]+\.js", target) for _, target in imports), path.name
        assert len(MODULE_IMPORT.findall(source)) == len(imports), path.name


def test_both_quote_styles_of_an_import_get_the_version():
    from pcbparts_dashboard.server import MODULE_IMPORT

    source = b"""import { a } from "./a.js";\nimport { b } from './b.js';\nimport {c}from"./c.js";\n"""
    assert MODULE_IMPORT.sub(lambda m: m[1] + b"?v=1" + m[2], source) == (
        b"""import { a } from "./a.js?v=1";\nimport { b } from './b.js?v=1';\nimport {c}from"./c.js?v=1";\n""")
