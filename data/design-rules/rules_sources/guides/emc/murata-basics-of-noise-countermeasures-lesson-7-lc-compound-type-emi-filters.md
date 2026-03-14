---
source: "Murata -- Basics of Noise Countermeasures, Lesson 7: LC Compound-type EMI Filters"
url: "https://article.murata.com/en-us/article/basics-of-noise-countermeasures-lesson-7"
format: "HTML"
method: "fetchaller"
extracted: 2026-03-02
chars: 1905
---

# Basics of Noise Countermeasures [Lesson 7] LC Compound-type EMI Filters

## Combining C and L results in a steep insertion loss curve

Using a combination of a capacitor and an inductor results in a steeper insertion loss curve than when using only a capacitor or an inductor. The slope becomes steeper as the number of filter elements increases.

## Signal and noise selectivity

A steeper filter insertion loss slope helps prevent the signal from being adversely affected when signal and noise frequencies are near each other. When both frequencies are close and a filter with a gentle slope is used, selecting constants that sufficiently reduce noise also attenuates higher harmonic components of the signal, corrupting the signal waveform. LC compound filters can selectively separate signal and noise in high-speed signal lines.

## Selecting the filter circuit type

Various types exist: C-L-C (pi-type), L-C-L (T-type), C-L or L-C (L-type). The key decision factor is input/output impedance:
- Capacitors: effects increase near high-impedance areas (bypass high frequencies to ground)
- Inductors: effects increase near low-impedance areas (reject high frequencies)

Place capacitors near high-impedance areas and inductors near low-impedance areas.

## LC compound filter products

Often used when signal frequency is comparatively high and near the noise frequency. Commonly used in LCD module and camera module interface lines inside mobile phones. Array-type filters incorporate four circuits into a single package. Filters with multiple self-resonant frequencies are available for covering multiple frequency bands simultaneously.
