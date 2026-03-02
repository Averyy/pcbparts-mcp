"""Integration tests for sensor_recommend tool — requires real sensor.db.

Run with: pytest -m integration tests/test_sensor_recommend.py -v
"""

from pathlib import Path

import pytest

from pcbparts_mcp.sensor_db import SensorDatabase

DB_PATH = Path(__file__).parent.parent / "data" / "sensor.db"

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def sensor_db():
    if not DB_PATH.exists():
        pytest.skip("sensor.db not found — run scripts/build_sensor_db.py first")
    db = SensorDatabase(db_path=DB_PATH)
    db._ensure_db()
    yield db
    db.close()


class TestSensorRecommendIntegration:
    def test_temperature_sensors(self, sensor_db):
        result = sensor_db.search(measure="temperature", limit=10)
        assert result["total"] > 50
        ids = {r["id"] for r in result["results"]}
        # Well-known temperature sensors should appear
        assert "bme280" in ids or "ds18b20" in ids or "sht3x" in ids

    def test_combo_temp_pressure(self, sensor_db):
        result = sensor_db.search(measure=["temperature", "pressure"])
        assert result["total"] >= 5
        # All results should have both measures
        for r in result["results"]:
            assert "temperature" in r["measures"]
            assert "pressure" in r["measures"]

    def test_co2_sensors(self, sensor_db):
        result = sensor_db.search(measure="co2")
        assert result["total"] >= 10
        ids = {r["id"] for r in result["results"]}
        assert "scd4x" in ids or "scd30" in ids

    def test_imu_expansion(self, sensor_db):
        result = sensor_db.search(measure="imu")
        assert result["total"] >= 10
        # MPU6050 should be in results
        ids = {r["id"] for r in result["results"]}
        assert "mpu6050" in ids

    def test_platform_filter(self, sensor_db):
        result = sensor_db.search(measure="temperature", platform="esphome")
        assert result["total"] >= 20
        for r in result["results"]:
            assert "esphome" in r["platforms"]

    def test_protocol_filter(self, sensor_db):
        result = sensor_db.search(measure="co2", protocol="uart")
        assert result["total"] >= 5
        for r in result["results"]:
            assert "uart" in r["protocols"]

    def test_type_filter_ndir(self, sensor_db):
        result = sensor_db.search(type="ndir")
        assert result["total"] >= 5
        for r in result["results"]:
            assert r["type"] == "ndir"

    def test_fts_search(self, sensor_db):
        result = sensor_db.search(query="BME280")
        assert result["total"] >= 1
        assert result["results"][0]["id"] == "bme280"
        assert result["results"][0]["manufacturer"] == "Bosch"

    def test_sort_by_platform_count(self, sensor_db):
        result = sensor_db.search(measure="temperature", limit=20)
        counts = [r["platform_count"] for r in result["results"]]
        assert counts == sorted(counts, reverse=True)

    def test_result_structure(self, sensor_db):
        result = sensor_db.search(query="SCD4X")
        assert result["total"] >= 1
        r = result["results"][0]
        assert "id" in r
        assert "name" in r
        assert "manufacturer" in r
        assert "type" in r
        assert "voltage" in r
        assert "platform_count" in r
        assert "measures" in r and isinstance(r["measures"], list)
        assert "protocols" in r and isinstance(r["protocols"], list)
        assert "platforms" in r and isinstance(r["platforms"], list)
        assert "urls" in r and isinstance(r["urls"], list)
        assert "source_tier" in r

    def test_no_params_returns_all(self, sensor_db):
        result = sensor_db.search(limit=5)
        # Should return sensors sorted by platform_count
        assert result["total"] > 100
        assert len(result["results"]) == 5

    def test_stats(self, sensor_db):
        stats = sensor_db.get_stats()
        assert stats["total_sensors"] > 1000
        assert "arduino" in stats["platforms"]
        assert "esphome" in stats["platforms"]
        assert "temperature" in stats["top_measures"]
