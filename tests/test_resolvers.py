"""Tests for search resolvers including MPN normalization."""

import pytest
from jlcpcb_mcp.search.mpn import normalize_mpn, looks_like_mpn


class TestLooksLikeMpn:
    """Tests for MPN detection."""

    def test_typical_ic_mpn(self):
        assert looks_like_mpn("STM32F103C8T6") is True
        assert looks_like_mpn("MCP73831-2ACI/MC") is True
        assert looks_like_mpn("ESP32-C3") is True

    def test_with_suffixes(self):
        assert looks_like_mpn("STM32F103C8T6-TR") is True
        assert looks_like_mpn("LM1117-3.3#PBF") is True

    def test_short_mpn(self):
        assert looks_like_mpn("NE555") is True
        assert looks_like_mpn("1N4148") is True  # Diode-style: digit + letter + digits
        assert looks_like_mpn("2N2222") is True  # Transistor-style

    def test_not_mpn(self):
        assert looks_like_mpn("resistor") is False
        assert looks_like_mpn("10k") is False
        assert looks_like_mpn("") is False
        assert looks_like_mpn("abc") is False

    def test_case_insensitive(self):
        """MPN detection should work with any case."""
        assert looks_like_mpn("stm32f103c8t6") is True
        assert looks_like_mpn("Stm32F103c8T6") is True
        assert looks_like_mpn("mcp73831-2aci/mc") is True


class TestNormalizeMpn:
    """Tests for MPN normalization."""

    def test_no_change_needed(self):
        """Parts without suffixes return just the original."""
        result = normalize_mpn("LM1117-3.3")
        assert result[0] == "LM1117-3.3"
        assert len(result) == 1  # No additional variants

    def test_strip_tr_suffix(self):
        """Tape & reel suffix -TR should be stripped."""
        result = normalize_mpn("STM32F103C8T6-TR")
        assert "STM32F103C8T6-TR" in result
        assert "STM32F103C8T6" in result

    def test_strip_pbf_suffix(self):
        """Lead-free suffix #PBF should be stripped."""
        result = normalize_mpn("LM1117-3.3#PBF")
        assert "LM1117-3.3#PBF" in result
        assert "LM1117-3.3" in result

    def test_insert_t_for_tape_reel(self):
        """Microchip-style T insertion: MCP73831-2ACI -> MCP73831T-2ACI."""
        result = normalize_mpn("MCP73831-2ACI/MC")
        assert "MCP73831-2ACI/MC" in result
        assert "MCP73831T-2ACI/MC" in result

    def test_already_has_t(self):
        """Don't double-insert T if already present."""
        result = normalize_mpn("MCP73831T-2ACI/MC")
        # Should not have duplicated T
        assert "MCP73831TT-2ACI/MC" not in result

    def test_original_always_first(self):
        """Original query should always be first in the list."""
        result = normalize_mpn("MCP73831-2ACI/MC")
        assert result[0] == "MCP73831-2ACI/MC"

    def test_combined_strip_and_insert(self):
        """Strip suffix AND try T insertion."""
        result = normalize_mpn("MCP73831-2ACI-TR")
        # Original
        assert "MCP73831-2ACI-TR" in result
        # Stripped
        assert "MCP73831-2ACI" in result
        # With T inserted after stripping
        assert "MCP73831T-2ACI" in result

    def test_lowercase_input(self):
        """Lowercase MPN should work correctly."""
        result = normalize_mpn("stm32f103c8t6-tr")
        assert result[0] == "stm32f103c8t6-tr"  # Original preserved
        # Should have uppercase stripped variant
        assert any("STM32F103C8T6" in v.upper() for v in result)

    def test_mixed_case_input(self):
        """Mixed case MPN should work correctly."""
        result = normalize_mpn("Stm32F103C8T6-TR")
        assert result[0] == "Stm32F103C8T6-TR"  # Original preserved
        # Should have stripped variant
        assert len(result) >= 2

    def test_no_duplicate_variants(self):
        """Variants should not be duplicated (case-insensitive deduplication)."""
        result = normalize_mpn("stm32f103c8t6-tr")
        # Check for case-insensitive duplicates
        seen_upper = set()
        for v in result:
            v_upper = v.upper()
            assert v_upper not in seen_upper, f"Duplicate variant: {v}"
            seen_upper.add(v_upper)
