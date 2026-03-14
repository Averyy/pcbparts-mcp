---
source: "FixturFab -- Basic PCBA Design for Test (DFT) Guide"
url: "https://www.fixturfab.com/articles/basic-pcba-design-test-dft-guide"
format: "HTML"
method: "readability"
extracted: 2026-03-02
chars: 2928
---

Building a test fixture can be a difficult and costly process, especially if the PCB wasn't designed with test in mind. The following tips can help make testing your PCB much easier when using a bed-of-nails style test fixture.

## Single-sided probing

All test points should be placed on a single side of the PCB, preferably the side with fewer components. This will greatly reduce the cost and complexity of the test fixture required to test the PCB.

## Test Point Grid Spacing

A common term in the PCBA testing world is *Test Point Grid Spacing*. This means the minimum space between test points on the PCB and is defined using either *mil* (a thousandth of an inch) or *mm*.

Test probes come in a variety of grid spacings, with the most common being:

* P100 (100mil or 2.54mm spacing)
* P75 (75mil or 1.91mm spacing)
* P50 (50mil or 1.27mm spacing)

You should design your PCB's to use the largest test point spacing possible. The larger the test probe is, the more durable it is, and larger probes are also less expensive.

We prefer 100mil and 75mil spacings.

## Test Probe and Test Point Types

While different types of test points and probes can be used, we recommend using regular pads with a minimum diameter of 0.8mm. These can easily be accessed by most probe types, and increasing the pad diameter to 1mm will help improve the reliability of the tester.

Different test point types and the test probes that should be used are described below.

### Leads

A Lead test point is created by the lead from a through-hole component that is soldered to the PCB. Serrated probe tips typically have the longest life, but cupped probe tips can also be used.

### Terminals and Posts

A Terminal or Post is created by a component with a square terminal or post that is soldered to the PCB. These types of test points are best contacted by slotted (self-cleaning) cups when used facing upwards. Serrated or flat tips will also work, however, the cup tips will self align to the terminal or post.

### Pads

Pad test points are simple pads on the PCB that are not covered with solder (no solder paste). Using the largest diameter pad that is possible in your design will help increase the reliability of the probes contacting the pads, we recommend using a minimum pad diameter of 0.8mm. Crown tips are great for contacting clean flat solder pads but require frequent maintenance. Spear, Chisel, or Needle tips are great for reliably testing flux-coated solder pads.

## In Summary

Use the following checklist to help ensure that your PCB designs are testable:

* At least 1 test point is available on each net that you would like to test
* Use 1mm or greater diameter pads that are not covered with solder paste for each test point
* Place test points at a distance of > 1.91mm from each other
* Place all test points on either the top or bottom of the PCB. Preferably, place them on the least populated side of the PCB.