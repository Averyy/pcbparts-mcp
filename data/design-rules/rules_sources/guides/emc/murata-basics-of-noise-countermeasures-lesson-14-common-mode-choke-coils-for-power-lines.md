---
source: "Murata -- Basics of Noise Countermeasures, Lesson 14: Using Common Mode Choke Coils for Power Supply Lines"
url: "https://article.murata.com/en-us/article/basics-of-noise-countermeasures-lesson-14"
format: "HTML"
method: "fetchaller"
extracted: 2026-03-02
chars: 1990
---

# Basics of Noise Countermeasures [Lesson 14] Using Common Mode Choke Coils for Power Supply Lines

## 1. Magnetic saturation in CMCs with differential mode impedance

Some CMCs are designed to also reduce differential mode noise — they intentionally allow some magnetic flux leakage, creating differential mode impedance. This makes them effective against both common mode and differential mode noise on power lines (where high-speed signals aren't a concern).

**Caution:** Differential mode magnetic flux remains, so increasing differential mode current increases flux leakage and can cause magnetic saturation. Large differential mode currents flow in power supply lines, so this effect is amplified. Use within the range that doesn't cause performance drop from saturation.

If a CMC doesn't noticeably reduce power supply line noise, check whether magnetic saturation from large differential mode impedance is the cause.

## 2. CMCs for AC power supply lines (line filters)

CMCs for AC power supply primary sides (switching power supplies) are called "line filters." Used together with:
- **X-capacitors (across-the-line):** Remove differential mode noise
- **Y-capacitors (line bypass):** Remove common mode noise
- **CMCs:** Remove common mode noise

Purpose: prevent noise from secondary side leaking to primary, and prevent power supply noise from escaping via power cord.

Increasing Y-capacitor capacitance enables removal of lower-frequency common mode noise, but risk of current leaking to ground increases. CMCs handle the low-frequency range that Y-capacitors can't cover.

CMCs for AC power lines must support high voltages. Products rated AC 250V generally satisfy safety standards.
