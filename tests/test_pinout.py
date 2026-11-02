"""Tests for EasyEDA pinout parsing."""

import pytest
from pcbparts_mcp.client import EasyEDAComponentNotFound
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

    def test_number_is_the_number_text_not_the_spice_pin(self):
        """SIM7080G (C2943992): 58 of 77 pins have SPICE pin 0 and 4 reuse low numbers."""
        data = {"dataStr": {"shape": [
            # VBAT: spice 0, pin 35
            "P~show~0~0~430~360~180~gge892~0^^430~360^^M 430 360 h 20~#880000^^1~452~363~0~VBAT~start~~~#0000FF^^1~445~359~0~35~end~~~#0000FF^^0~447~360^^0~M 450 363 L 453 360 L 450 357",
            # GNSS_ANT, right side (name anchored at end): spice 0, pin 68
            "P~show~0~0~650~230~0~gge283~0^^650~230^^M 650 230 h -20~#880000^^1~628~233~0~GNSS_ANT~end~~~#0000FF^^1~635~229~0~68~start~~~#0000FF^^0~633~230^^0~M 630 227 L 627 230 L 630 233",
            # UART3_TXD: spice 5, pin 61
            "P~show~0~5~430~570~180~gge409~0^^430~570^^M 430 570 h 20~#880000^^1~452~573~0~UART3_TXD~start~~~#0000FF^^1~445~569~0~61~end~~~#0000FF^^0~447~570^^0~M 450 573 L 453 570 L 450 567",
            "P~show~0~1~430~540~180~gge1606~0^^430~540^^M 430 540 h 20~#880000^^1~452~543~0~UART1_TXD~start~~~#0000FF^^1~445~539~0~1~end~~~#0000FF^^0~447~540^^0~M 450 543 L 453 540 L 450 537",
        ]}}
        pins = parse_easyeda_pins(data)
        assert [(p["number"], p["name"]) for p in pins] == [
            ("1", "UART1_TXD"), ("35", "VBAT"), ("61", "UART3_TXD"), ("68", "GNSS_ANT")]

    def test_hidden_numeric_name(self):
        """PJ-320B (C18594): name text hidden and equal to the number."""
        data = {"dataStr": {"shape": [
            "P~show~0~1~430~290~~gge6~0^^430~290^^M 430 290 h -20~#880000^^0~408~293~0~1~end~~~#0000FF^^1~415~289~0~1~start~~~#0000FF^^0~413~290^^0~M 410 287 L 407 290 L 410 293",
        ]}}
        assert parse_easyeda_pins(data) == [{"number": "1", "name": "1"}]


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
        """RP2040's labels carry a font (~end~Tahoma~5.8pt~), which hid every pin name before 0.8.0."""
        part = await client.get_part("C2040")  # RP2040
        assert part is not None

        uuid = part.get("easyeda_symbol_uuid")
        data = await client.get_easyeda_component(uuid)
        pins = parse_easyeda_pins(data)

        assert len(pins) == 57
        # RP2040 has electrical types set (mostly bidirectional)
        electrical_types = {p.get("electrical") for p in pins if "electrical" in p}
        assert "bidirectional" in electrical_types
        by_number = {p["number"]: p["name"] for p in pins}
        assert by_number["2"] == "GPIO0" and by_number["9"] == "GPIO7"

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
        """A nonexistent but valid-format UUID raises EasyEDAComponentNotFound (a ValueError): what
        EasyEDA really answers for a missing symbol, which the pinout self-heal relies on (0.6.0)."""
        with pytest.raises(EasyEDAComponentNotFound, match="EasyEDA has no symbol 0{32}"):
            await client.get_easyeda_component("00000000000000000000000000000000")
