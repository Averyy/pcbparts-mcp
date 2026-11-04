"""0.8.12: the RF antenna rule's GCPW, isolation, bypass and ESP32 lines checked against their sources
and a 2-D field solve (design-session report, 2026-11-04: an "ADI" 50 ohm GCPW row was a microstrip
width, about 35 ohm as GCPW)."""

from pcbparts_mcp.design_rules import get_design_rules


def _rf() -> str:
    return get_design_rules(topic="rf-antenna")["content"]


class TestRfRule:
    def test_gcpw_rows(self):
        content = _rf()
        assert "trace 1.2mm, gap 0.25mm = 50 ohm" in content and "trace 0.45mm, gap 0.64mm = 51 ohm" in content
        assert "with coplanar ground 0.2mm away it is 35 ohm" in content and "about 3 ohm off" in content
        # ADI's article has no such rows
        assert "w=2.8mm, gap=0.2mm gives 50 ohm" not in content and "h=0.2mm, w=0.3mm" not in content

    def test_isolation_is_a_limit(self):
        content = _rf()
        assert "practical limit on a small PCB at about -45 dB" in content
        assert "achieves -45 dB isolation minimum" not in content

    def test_bypass_srf_from_adis_table(self):
        content = _rf()
        assert "20pF 2.5 GHz, 100pF 800 MHz" in content and "100pF and 100nF are both inductive" in content
        assert "SRF ~1.5 GHz" not in content and "SRF around 400 MHz" not in content

    def test_esp32_line_as_espressif_writes_it(self):
        content = _rf()
        assert "15mil long, 100 ohm +/-10%" in content and "keep all layers clear under the connector" in content
        assert "5.6nH shunt inductor" not in content and "1mm keep-out ring" not in content
