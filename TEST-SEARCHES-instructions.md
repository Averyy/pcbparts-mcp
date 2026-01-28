# JLCPCB MCP Search Test

Test the board specified below against the jlcmcp. The purpose of this exercise is to test and improve the mcp server. We want to find edge cases or common searches/components that it SHOULD find but it doesn't. Try to focus on the main search tool and avoid using search_api unless its to verify a failure in the search tool.

## Search Strategy (try all)
1. **Exact MPN** - search the full part number
2. **Partial MPN** - manufacturer prefix (e.g., "STM32L4" not "STM32L4R5ZIY6")
3. **Specs** - category + key parameters (e.g., "10uF 0402 X5R 10V")
4. **find_alternatives** - for common parts (resistors, caps, ICs)
5. **If all above searches are successful** - pretend the desired part isn't available and find a suitable replacement

## For "NOT FOUND" parts document:
- Is it a problem with the search query (ie mcp is having trouble - if so log it)
- Trying generic description (e.g., "USB-C 16 pin" instead of exact MPN) or suitable alternative, but still log the failure to find the original
- What SHOULD the mcp have returned but didn't?

## Output

Keep output short and concise to only what helps us improve the mcp. dont give code or solutions just explain the problem (what we searched, what results we got, and what results we should have gotten). DONT GIVE COMPLIMENTS, DONT GIVE WHAT WORKS WELL, ETC.