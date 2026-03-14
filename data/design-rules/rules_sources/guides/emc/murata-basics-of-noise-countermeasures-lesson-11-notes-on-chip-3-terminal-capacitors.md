---
source: "Murata -- Basics of Noise Countermeasures, Lesson 11: Notes on the Use of Chip 3-Terminal Capacitors"
url: "https://article.murata.com/en-us/article/basics-of-noise-countermeasures-lesson-11"
format: "HTML"
method: "fetchaller"
extracted: 2026-03-02
chars: 2051
---

# Basics of Noise Countermeasures [Lesson 11] Notes on the Use of Chip 3-Terminal Capacitors

## 1. Mounting on multilayer substrate — GND connection matters

The key to high-frequency noise suppression is the low impedance of the ground terminal. Pattern design for mounting must make the ground-side pattern as thick and short as possible.

Example A: 3-terminal capacitor mounted close to the GND layer (opposite side of MCU mounting surface) — short connection to GND layer, best noise suppression.

Example B: Power input/output pass through the same layer without clear separation — slightly higher noise level. Likely because entrance/exit vias are so close that noise bypasses the capacitor via capacitive coupling between vias.

Example C: 3-terminal capacitor mounted on same plane as MCU — longer distance to GND layer, significantly higher noise level.

**Key insight:** Not enough to think about planarity; must also account for via length. Route the input and output with clear separation to prevent noise bypass through capacitive coupling.

## 2. "Non-through" connections

**Conventional (through):** Cut the power supply pattern, insert the capacitor in series, connect ground terminal.

**Non-through:** Connect terminals to power supply line WITHOUT cutting the pattern (parallel connection). Benefits:
- Impedance of the bypass route is halved (parallel connection)
- Positioning GND-side and power-side vias adjacent creates magnetic flux cancellation, apparently halving inductance
- Good for stabilizing IC voltage fluctuations

**Trade-off:** Some noise passes through the power line without going through the capacitor, so the effect of reducing noise that escapes to the outside is significantly reduced compared to through connection.
