---
source: "Murata -- Basics of Noise Countermeasures, Lesson 5: Chip 3 Terminal Capacitors"
url: "https://article.murata.com/en-us/article/basics-of-noise-countermeasures-lesson-5"
format: "HTML"
method: "fetchaller"
extracted: 2026-03-02
chars: 3144
---

# Basics of Noise Countermeasures [Lesson 5] Chip 3 Terminal Capacitors

## Lead-type ceramic capacitors

In lead-type ceramic capacitors, electrodes on both sides of a single panel dielectric are coated and lead terminals are attached. The lead terminal parts have minimal inductance (residual inductance), so when this capacitor is used as a bypass capacitor, there is inductance between it and the ground terminal.

Impedance normally decreases proportionately to increasing frequency in capacitors, so in high-frequency regions, insertion loss should continue to increase. However, capacitors have residual inductance, and this minimal inductance interferes, causing a decrease in performance at high frequencies represented by the V-shaped insertion loss curve.

## 3 terminal capacitors

3 terminal capacitors are ceramic capacitors in which the shape of the lead terminals is altered to improve the high-frequency characteristics of 2 terminal capacitors. One lead has two projections. The projections of the 2 terminal lead are connected to input and output of power sources or signal lines, and the other lead is connected to the ground terminal. The 2 terminal lead inductance does not enter the ground side, making the ground impedance extremely small. Also, as the inductance of the 2 terminal lead works similar to a T-type filter inductor, it works in the direction of reducing noise.

## Multilayer ceramic chip-type capacitors and chip 3 terminal capacitors

A ground terminal is attached to each side of the chip, the dielectric is placed between the plates, and feed through electrodes and ground electrodes are alternately stacked up to create a feed through capacitor-like structure. The inductance of the feed through electrodes works like a T-type filter inductor. The distance to the ground side is shorter, resulting in minimal inductance. As the ground side is connected to both ends, they become connected in series, and inductance becomes apparently cut in half.

The performance of the 2 terminal capacitor begins to drop as it exceeds 10 MHz, while the 3 terminal capacitor maintains its performance until the vicinity of 100 MHz.

## Chip 3 terminal capacitors actually have 4 terminals

Even though we say chip 3 terminal capacitors have 3 terminals, they actually have four. They are still called '3 terminal' because electrically all terminals have the same potential and because the original lead-type had 3 terminals.

## Mounting method

When mounting a 3 terminal chip-type capacitor as a bypass capacitor, cut the signal or power pattern and connect a feed through electrode in between, and prepare and connect a ground pattern at the ground terminal. The ground pattern must be connected with the shortest possible connection to a stable ground plane. When using a double-sided or multilayer board, connect to the ground plane via a through hole.
