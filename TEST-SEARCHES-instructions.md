# JLCPCB MCP BOM Search Test

Test the board specified below against the local JLCPCB database. Component lists are in TEST-SEARCHES.md.

## Search Strategy (try in order)
1. **Exact MPN** - search the full part number
2. **Partial MPN** - manufacturer prefix (e.g., "STM32L4" not "STM32L4R5ZIY6")
3. **Specs** - category + key parameters (e.g., "10uF 0402 X5R 10V")
4. **find_alternatives** - for common parts (resistors, caps, ICs)

## For "NOT FOUND" parts
Before marking as unavailable, verify by:
- Searching JLCPCB.com directly (is it actually stocked?)
- Trying generic description (e.g., "USB-C 16 pin" instead of exact MPN)
- Checking if it's a module/connector JLCPCB doesn't typically stock

## Output

| Ref | Component | Search Used | Found? | LCSC# | Basic/Ext | Notes |
|-----|-----------|-------------|--------|-------|-----------|-------|

## Summary
- Coverage: X/Y parts found (Z%)
- Basic: N parts | Extended: M parts (+$3×M assembly fee)
- Search issues to fix: (log to todo-database-enhancements.md)
- Genuinely unavailable: (list with reason)
