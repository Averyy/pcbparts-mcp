"""Tests for EasyEDA pinout parsing."""

import pytest
from pcbparts_mcp.pinout import parse_easyeda_pins


class TestParsePins:
    """Test pin parsing from EasyEDA data."""

    def test_parse_simple_mosfet_pins(self):
        """Test parsing 3-pin MOSFET with named pins."""
        data = {
            "dataStr": {
                "shape": [
                    "P~show~0~1~100~100~180~gge1~0^^100~100^^M100,100h10~#880000^^1~110~105~0~G~start~~~#880000^^1~100~100~0~1~end~~~#0000FF",
                    "P~show~0~2~100~120~180~gge2~0^^100~120^^M100,120h10~#880000^^1~110~125~0~S~start~~~#880000^^1~100~120~0~2~end~~~#0000FF",
                    "P~show~0~3~100~140~180~gge3~0^^100~140^^M100,140h10~#880000^^1~110~145~0~D~start~~~#880000^^1~100~140~0~3~end~~~#0000FF",
                ]
            }
        }
        pins = parse_easyeda_pins(data)
        assert len(pins) == 3
        assert pins[0]["number"] == "1"
        assert pins[0]["name"] == "G"
        assert "electrical" not in pins[0]  # undefined is omitted
        assert pins[1]["name"] == "S"
        assert pins[2]["name"] == "D"

    def test_parse_numbered_only_pins(self):
        """Test parsing component with numbered-only pins."""
        data = {
            "dataStr": {
                "shape": [
                    "P~show~0~1~100~100~180~gge1~0^^100~100^^M100,100h10~#0000FF^^1~110~105~0~1~start~~~#0000FF^^1~100~100~0~1~end~~~#0000FF",
                    "P~show~0~2~100~120~180~gge2~0^^100~120^^M100,120h10~#0000FF^^1~110~125~0~2~start~~~#0000FF^^1~100~120~0~2~end~~~#0000FF",
                ]
            }
        }
        pins = parse_easyeda_pins(data)
        assert len(pins) == 2
        assert pins[0]["number"] == "1"
        assert pins[0]["name"] == "1"  # Falls back to pin number
        assert "electrical" not in pins[0]  # undefined is omitted

    def test_parse_with_electrical_types(self):
        """Test parsing pins with electrical types set."""
        data = {
            "dataStr": {
                "shape": [
                    # Type 3 = bidirectional
                    "P~show~3~1~100~100~180~gge1~0^^100~100^^M100,100h10~#880000^^1~110~105~0~1~start~~~#880000^^1~100~100~0~1~end~~~#0000FF",
                    # Type 1 = input
                    "P~show~1~2~100~120~180~gge2~0^^100~120^^M100,120h10~#880000^^1~110~125~0~2~start~~~#880000^^1~100~120~0~2~end~~~#0000FF",
                    # Type 2 = output
                    "P~show~2~3~100~140~180~gge3~0^^100~140^^M100,140h10~#880000^^1~110~145~0~3~start~~~#880000^^1~100~140~0~3~end~~~#0000FF",
                    # Type 4 = power
                    "P~show~4~4~100~160~180~gge4~0^^100~160^^M100,160h10~#880000^^1~110~165~0~4~start~~~#880000^^1~100~160~0~4~end~~~#0000FF",
                ]
            }
        }
        pins = parse_easyeda_pins(data)
        assert len(pins) == 4
        assert pins[0]["electrical"] == "bidirectional"
        assert pins[1]["electrical"] == "input"
        assert pins[2]["electrical"] == "output"
        assert pins[3]["electrical"] == "power"

    def test_parse_named_pins(self):
        """Test parsing pins with proper names."""
        data = {
            "dataStr": {
                "shape": [
                    "P~show~0~1~100~100~180~gge1~0^^100~100^^M100,100h10~#FF0000^^1~110~105~0~VDD~start~~~#FF0000^^1~100~100~0~1~end~~~#0000FF",
                    "P~show~0~2~100~120~180~gge2~0^^100~120^^M100,120h10~#000000^^1~110~125~0~GND~start~~~#000000^^1~100~120~0~2~end~~~#0000FF",
                    "P~show~0~3~100~140~180~gge3~0^^100~140^^M100,140h10~#880000^^1~110~145~0~PA0~start~~~#880000^^1~100~140~0~3~end~~~#0000FF",
                ]
            }
        }
        pins = parse_easyeda_pins(data)
        assert len(pins) == 3
        assert pins[0]["name"] == "VDD"
        assert pins[1]["name"] == "GND"
        assert pins[2]["name"] == "PA0"

    def test_parse_complex_stm32_name(self):
        """Test that complex STM32 names are returned as-is."""
        data = {
            "dataStr": {
                "shape": [
                    "P~show~0~1~100~100~180~gge1~0^^100~100^^M100,100h10~#880000^^1~110~105~0~PC13-TAMPER-RTC~start~~~#880000^^1~100~100~0~1~end~~~#0000FF",
                ]
            }
        }
        pins = parse_easyeda_pins(data)
        assert len(pins) == 1
        assert pins[0]["name"] == "PC13-TAMPER-RTC"  # Raw, not split

    def test_parse_empty_shape(self):
        """Test parsing empty shape array."""
        data = {"dataStr": {"shape": []}}
        pins = parse_easyeda_pins(data)
        assert pins == []

    def test_parse_missing_datastr(self):
        """Test parsing data without dataStr."""
        data = {}
        pins = parse_easyeda_pins(data)
        assert pins == []

    def test_parse_string_datastr(self):
        """Test parsing when dataStr is a JSON string."""
        import json
        data = {
            "dataStr": json.dumps({
                "shape": [
                    "P~show~0~1~100~100~180~gge1~0^^100~100^^M100,100h10~#880000^^1~110~105~0~VCC~start~~~#880000^^1~100~100~0~1~end~~~#0000FF",
                ]
            })
        }
        pins = parse_easyeda_pins(data)
        assert len(pins) == 1
        assert pins[0]["name"] == "VCC"

    def test_parse_pins_sorted_by_number(self):
        """Test that pins are sorted by number."""
        data = {
            "dataStr": {
                "shape": [
                    "P~show~0~3~100~100~180~gge1~0^^100~100^^M100,100h10~#880000^^1~110~105~0~C~start~~~#880000^^1~100~100~0~3~end~~~#0000FF",
                    "P~show~0~1~100~120~180~gge2~0^^100~120^^M100,120h10~#880000^^1~110~125~0~A~start~~~#880000^^1~100~120~0~1~end~~~#0000FF",
                    "P~show~0~2~100~140~180~gge3~0^^100~140^^M100,140h10~#880000^^1~110~145~0~B~start~~~#880000^^1~100~140~0~2~end~~~#0000FF",
                ]
            }
        }
        pins = parse_easyeda_pins(data)
        assert [p["number"] for p in pins] == ["1", "2", "3"]
        assert [p["name"] for p in pins] == ["A", "B", "C"]


@pytest.fixture(scope="module")
async def client():
    """Create a shared client for integration tests.

    Module-scoped so all tests share one wafer session (accumulated cookies,
    proper rate limiting).
    """
    from pcbparts_mcp.client import JLCPCBClient
    client = JLCPCBClient()
    yield client
    await client.close()


@pytest.mark.integration
class TestPinoutIntegration:
    """Integration tests that hit the real EasyEDA API."""

    @pytest.mark.asyncio
    async def test_get_easyeda_component_stm32(self, client):
        """Test fetching STM32 component data from EasyEDA."""
        part = await client.get_part("C8304")  # STM32F103C8T6
        assert part is not None
        assert part.get("has_easyeda_footprint") is True

        uuid = part.get("easyeda_symbol_uuid")
        data = await client.get_easyeda_component(uuid)
        pins = parse_easyeda_pins(data)

        assert len(pins) == 48  # LQFP-48
        # Check we have the expected fields
        assert all("number" in p for p in pins)
        assert all("name" in p for p in pins)
        # STM32 has named pins (electrical omitted since undefined)
        assert any(p["name"] == "VBAT" for p in pins)
        assert "electrical" not in pins[0]  # STM32 symbols don't set electrical type

    @pytest.mark.asyncio
    async def test_get_easyeda_component_mosfet(self, client):
        """Test fetching MOSFET component data from EasyEDA."""
        part = await client.get_part("C20917")  # AO3400
        assert part is not None
        assert part.get("has_easyeda_footprint") is True

        uuid = part.get("easyeda_symbol_uuid")
        data = await client.get_easyeda_component(uuid)
        pins = parse_easyeda_pins(data)

        assert len(pins) == 3
        pin_names = {p["name"] for p in pins}
        assert pin_names == {"G", "S", "D"}

    @pytest.mark.asyncio
    async def test_get_easyeda_component_capacitor(self, client):
        """Test fetching capacitor component data from EasyEDA."""
        part = await client.get_part("C14663")  # 100nF capacitor
        assert part is not None
        assert part.get("has_easyeda_footprint") is True

        uuid = part.get("easyeda_symbol_uuid")
        data = await client.get_easyeda_component(uuid)
        pins = parse_easyeda_pins(data)

        assert len(pins) == 2
        # Capacitor has numbered-only pins
        assert pins[0]["name"] in ("1", "2")

    @pytest.mark.asyncio
    async def test_get_easyeda_component_lm358(self, client):
        """Test fetching LM358 op-amp component data."""
        part = await client.get_part("C328566")  # LM358
        assert part is not None
        assert part.get("has_easyeda_footprint") is True

        uuid = part.get("easyeda_symbol_uuid")
        data = await client.get_easyeda_component(uuid)
        pins = parse_easyeda_pins(data)

        assert len(pins) == 8
        # LM358 should have named pins
        pin_names = {p["name"] for p in pins}
        assert "VCC" in pin_names or "VEE" in pin_names

    @pytest.mark.asyncio
    async def test_get_easyeda_component_rp2040(self, client):
        """Test fetching RP2040 - has electrical types but no names."""
        part = await client.get_part("C2040")  # RP2040
        assert part is not None

        uuid = part.get("easyeda_symbol_uuid")
        data = await client.get_easyeda_component(uuid)
        pins = parse_easyeda_pins(data)

        assert len(pins) == 57
        # RP2040 has electrical types set (mostly bidirectional)
        electrical_types = {p.get("electrical") for p in pins if "electrical" in p}
        assert "bidirectional" in electrical_types

    @pytest.mark.asyncio
    async def test_get_easyeda_component_esp32_s3(self, client):
        """Test fetching ESP32-S3 component data."""
        part = await client.get_part("C2913194")  # ESP32-S3
        assert part is not None
        assert part.get("has_easyeda_footprint") is True

        uuid = part.get("easyeda_symbol_uuid")
        data = await client.get_easyeda_component(uuid)
        pins = parse_easyeda_pins(data)

        assert len(pins) == 57
        # ESP32-S3 has named pins
        pin_names = {p["name"] for p in pins}
        assert "GND" in pin_names

    @pytest.mark.asyncio
    async def test_get_easyeda_component_invalid_uuid(self, client):
        """Test fetching with invalid UUID raises ValueError."""
        with pytest.raises(ValueError, match="Invalid UUID format"):
            await client.get_easyeda_component("invalid-uuid-12345")

    @pytest.mark.asyncio
    async def test_get_easyeda_component_empty_uuid(self, client):
        """Test fetching with empty UUID raises ValueError."""
        with pytest.raises(ValueError, match="UUID is required"):
            await client.get_easyeda_component("")

    @pytest.mark.asyncio
    async def test_get_easyeda_component_nonexistent_uuid(self, client):
        """Test fetching with nonexistent but valid-format UUID raises ValueError."""
        with pytest.raises(ValueError, match="Failed to fetch component data"):
            await client.get_easyeda_component("00000000000000000000000000000000")
