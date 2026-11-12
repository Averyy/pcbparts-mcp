"""The Docker image copies each database build script into /app/scripts on its own (see the
Dockerfile), so a build script that imports another module from scripts/ works locally and breaks
the image build. 0.9.0's sensor build briefly imported scripts/scrapers and failed in Docker."""

import ast
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"
COPIED_ALONE = re.findall(r"COPY\s+\S+\s+scripts/(\w+\.py)\s+/app/scripts/", (ROOT / "Dockerfile").read_text())
LOCAL_MODULES = {p.stem for p in SCRIPTS.glob("*.py")} | {p.name for p in SCRIPTS.iterdir() if p.is_dir()}

sys.path.insert(0, str(SCRIPTS))


def _imported_modules(path: Path) -> set[str]:
    names = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return names


def test_dockerfile_still_copies_the_build_scripts():
    assert {"build_database.py", "build_history_db.py", "build_sensor_db.py", "build_boards_db.py"} <= set(COPIED_ALONE)


@pytest.mark.parametrize("script", COPIED_ALONE)
def test_build_script_needs_no_other_scripts_module(script):
    local = (_imported_modules(SCRIPTS / script) & LOCAL_MODULES) - {Path(script).stem}
    assert not local, f"{script} imports {sorted(local)} from scripts/, which the image doesn't copy"


def test_sensor_build_runs_from_its_own_file(tmp_path):
    """As the image does: only the script and data/sensors, run from the app directory."""
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "build_sensor_db.py").write_text((SCRIPTS / "build_sensor_db.py").read_text(encoding="utf-8"), encoding="utf-8")
    shutil.copytree(ROOT / "data" / "sensors", tmp_path / "data" / "sensors")  # no symlinks: CI runs on Windows too
    done = subprocess.run(
        [sys.executable, "scripts/build_sensor_db.py", "--data-dir", str(tmp_path / "data"),
         "--output", str(tmp_path / "data" / "sensor.db"), "--quiet"],
        cwd=tmp_path, capture_output=True, text=True, timeout=300)
    assert done.returncode == 0, done.stderr[-2000:]
    assert (tmp_path / "data" / "sensor.db").stat().st_size > 100_000


@pytest.mark.parametrize("raw", ["7SemiBME68x", "7semi_sht2x", "MyLD2410", "myld2410b", "Microfire_SHT3x", "IoTy coind4",
                                 "HLK-LD2410", "Omron D6F-PH", "mysensor", "My_BME280", "BME280", "hlk", "7semi",
                                 "MAX30102", "omron", "Myriad5", "7Semi24GHzRadar", "MyA02YYUW",
                                 "Adafruit_CircuitPython_MyA02YYUW", "SparkFun24GHzRadar"])
@pytest.mark.parametrize("known_ids", [(), {"24ghzradar", "a02yyuw", "ld2410", "bme280"}])
def test_identity_prefix_rule_matches_the_scrapers(raw, known_ids):
    from build_sensor_db import strip_identity_prefixes as build_rule
    from scrapers.common import strip_identity_prefixes as scraper_rule
    assert build_rule(raw, known_ids) == scraper_rule(raw, known_ids)
