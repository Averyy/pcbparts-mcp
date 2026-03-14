---
source: "Murata -- Basics of Noise Countermeasures, Lesson 10: Precautions for Using Chip Ferrite Beads"
url: "https://article.murata.com/en-us/article/basics-of-noise-countermeasures-lesson-10"
format: "HTML"
method: "fetchaller"
extracted: 2026-03-02
chars: 1864
---

# Basics of Noise Countermeasures [Lesson 10] Precautions for Using Chip Ferrite Beads

## 1. Superimposed DC characteristics

Chip ferrite beads are types of inductors that use ferrites. Their performance changes depending on magnetic saturation when high currents flow. The impedance value decreases when high currents flow, meaning expected results will not always be obtained in high-current applications.

Solutions: select parts with leeway in rated current, or choose those with high initial impedance. Magnetic saturation occurs only when high currents flow — once current is reduced, original performance is restored. Sometimes no problems in circuits where current increases only momentarily (but magnetic saturation in that moment may still cause problems).

## 2. Overshoot and undershoot in signal waveforms

Overshoot and undershoot sometimes appear when ferrite beads are used in digital circuits. This is caused by resonance between the inductance of the ferrite beads and the static capacitance (input capacitance of ICs, etc.) of the circuit. It tends to occur with ferrite beads that have a sharp impedance curve.

**Solution:** Insert damping resistors in series with ferrite beads. The resistors absorb resonance energy, reducing both overshoot and undershoot. However, damping resistors cause voltage drop — verify the reduced wave height doesn't cause problems.

**Prevention:** Refrain from using ferrite beads with a curve sharper than necessary. Sharper impedance curve = lower internal loss = more likely resonance. More gentle curve = less likely resonance.
