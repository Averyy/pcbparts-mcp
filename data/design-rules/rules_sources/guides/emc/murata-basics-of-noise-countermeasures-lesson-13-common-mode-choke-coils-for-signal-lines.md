---
source: "Murata -- Basics of Noise Countermeasures, Lesson 13: Using Common Mode Choke Coils for Signal Lines"
url: "https://article.murata.com/en-us/article/basics-of-noise-countermeasures-lesson-13"
format: "HTML"
method: "fetchaller"
extracted: 2026-03-02
chars: 1392
---

# Basics of Noise Countermeasures [Lesson 13] Using Common Mode Choke Coils for Signal Lines

## 1. Skew-improvement function

The main reason CMCs are used in signal lines is to eliminate common mode noise, but since they utilize transformer principles, they also provide a skew correction function in differential transmission circuits.

Both lines of a differential circuit should be balanced, but manufacturing inconsistency causes imbalance — creating gaps in signal arrival times (skew). Inserting a CMC reduces skew because it generates induced electromotive force on the opposite side when rising/falling edge timing is unbalanced, aligning the differential signals.

## 2. Equivalent circuit diagram — the dot convention

The black dots in the CMC equivalent circuit diagram indicate the directionality of magnetic coupling, not the winding start. When dots are aligned on the same side, magnetic coupling functions as a common mode choke coil. When dots are on different sides, the coils do NOT function as a CMC.

The original purpose of the dots was to indicate voltage polarity in transformers.
