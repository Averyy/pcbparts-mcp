"""Runs the page's data-module checks under Node; skipped where Node isn't installed."""

import shutil
import subprocess
from pathlib import Path

import pytest

TESTS = Path(__file__).with_name("frontend")


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_frontend_data_module():
    result = subprocess.run(
        ["node", "--test", *sorted(str(path) for path in TESTS.glob("*.test.mjs"))],
        capture_output=True, text=True, encoding="utf-8", timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
