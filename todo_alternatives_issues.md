# find_alternatives and search Issues - Status

## find_alternatives Issues

### Issue 1: Motor Driver H-bridge mismatch - FIXED
Added `must_match: ["Number of H-bridges"]` rule for "Brushed DC Motor Drivers"

### Issue 2: Audio Amplifiers missing rules - FIXED
Added `must_match: ["Class"]` rule for "Audio Amplifiers"

### Issue 3: Current Sense Amplifiers - digital vs analog - DOCUMENTED
Known limitation - JLCPCB doesn't distinguish digital vs analog interfaces

### Issue 4: LDO find_alternatives returns wrong packages - FIXED
Added `package_warning` field when package differs from original

### Issue 5: "M4" package not recognized - FIXED
Added M4/M7→SMA, M8→SMB package alias mapping

---

## Search Parser Issues

### Issue 6: Radial electrolytic capacitor search fails - FIXED
Added aliases and post-processing for "radial"/"through hole"/"pth" keywords

### Issue 7: Trimmer/Potentiometer search fails - FIXED
Added aliases and post-processing for "trimmer"/"potentiometer" keywords

### Issue 8: Inductance spec filter returns 0 results - FIXED
**Problem**: "NRS3015 2.2uH" routed to "Inductors (SMD)" but parts were in "Power Inductors"
**Fix**: Inductance values no longer infer a specific subcategory, allowing text search to work across all inductor categories

### Issue 9: USB-C package filter returns 0 results - FIXED
**Problem**: Parser extracted "USB-C" as a package filter, but JLCPCB uses "SMD" as package
**Fix**: USB connector types (USB-C, TYPE-C, etc.) no longer extracted as package filters. They remain in query for text search.

### Issue 10: USB pin count uses wrong spec name - FIXED
**Problem**: Parser used "Number of Pins" but USB connectors use "Number of Contacts"
**Fix**: Added category-aware spec mapping that uses "Number of Contacts" for USB connectors

### Issue 11: "- -F" garbage in remaining text - FIXED
**Problem**: "USB-C-16P-F" left "- -F" as remaining text after parsing
**Fix**: Added cleanup to remove orphaned hyphens and single letters from remaining text

### Issue 12: Pin count not parsed from "X pin header" pattern - FIXED
**Problem**: "8 pin header 2.54mm PTH" left "8" in remaining_text instead of extracting as pin count
**Fix**: Added post-processing to detect standalone numbers before connector keywords (header, connector, terminal, socket) and treat them as pin counts

### Issue 13: Pin count format normalization - FIXED
**Problem**: Parser normalized pin counts to "8 pin" but database uses "8P" format
**Fix**: Changed pin_count normalization from "X pin" to "XP" format

### Issue 14: "PTH" mounting type not recognized - FIXED
**Problem**: "PTH" was left in remaining text, causing search failures
**Fix**: Added mounting type extraction (PTH/THT→"Through Hole", SMD/SMT→"SMD") with removal from remaining text

---

## Files Modified

- `src/jlcpcb_mcp/alternatives.py` - COMPATIBILITY_RULES, STRING_MATCH_SPECS, package warnings
- `src/jlcpcb_mcp/smart_parser.py` - Multiple parser fixes (packages, USB handling, pin counts, mounting type)
- `src/jlcpcb_mcp/subcategory_aliases.py` - Added aliases for leaded electrolytic, potentiometers
- `src/jlcpcb_mcp/server.py` - Added mounting_type to parsed query info

## Testing

All 417 unit tests pass.
