# Connectors

> Connector family selection -- JST series, barrel jacks, USB power, terminal blocks, FFC/FPC, pin headers, RF.

## Quick Reference

- **Always specify exact series + position count.** "JST connector" is meaningless -- JST makes hundreds of types. Use "JST PH 2-pin" or "JST SH 4-pin".
- **Barrel jacks: 5.5 mm outer / 2.1 mm inner, center-positive** is the de facto standard. A 2.5 mm plug fits a 2.1 mm jack but makes only intermittent contact.
- **USB-C power-only: GCT USB4125 (6-pin, top-mount).** USB 2.0 with data: GCT USB4085 (16-pin, mid-mount). USB data routing -> `interfaces/usb.md`.
- **Terminal blocks: wave solder only.** Reflow melts housings. Spring terminals over screw for vibration environments.
- **FFC orientation: straight vs reverse.** Wrong choice gives reversed pinout. Swap bottom-contact for top-contact connector instead of replacing the cable.

## Design Rules

### JST Wire-to-Board Families

| Series | Pitch | Typical Use | Selection Note |
|--------|-------|-------------|----------------|
| XH | 2.5 mm | Stepper motors, LiPo balance | NOT 0.1" (2.54 mm) -- cumulative error over 6+ pins |
| PH | 2.0 mm | LiPo battery (SparkFun standard) | Extremely hard to disconnect -- good for reliability, bad for servicing |
| ZH | 1.5 mm | Compact I/O | Thinner wires |
| GH | 1.25 mm | Compact sensor/I/O | Easily confused with Molex PicoBlade |
| SH | 1.0 mm | Ultra-compact | Optional grip protrusions; pins dislodge easily at 0.5 mm FFC pitch |

- **JST GH vs Molex PicoBlade: both 1.25 mm pitch but NOT interchangeable.** Surplus inventory is frequently mislabeled. Measure pitch first, then compare housing features to specific series datasheet.
- **JST PH battery connector: S2B-PH-SM4-TB** (2-pin, right-angle SMD). Through-hole variant: S2B-PH-K-S.

### Barrel Connectors

- **De facto standard: 5.5 mm outer / 2.1 mm inner, center-positive.** SparkFun, most consumer devices use this. 3.5 mm outer / 1.3 mm inner for smaller devices.
- **2.5 mm plug in 2.1 mm jack: passes bench test, fails under vibration or thermal cycling.** The cantilevered spring contact on the outer sleeve tolerates this -- the inner pin does not. Always verify inner diameter match.
- **Third-pin switching:** spring contact shorts to sleeve when no plug inserted. Use for auto-switching between battery and wall adapter.
- **Never use audio jacks for power.** Tip and sleeve momentarily short during insertion. Audio connectors also lack rated voltage/current specs from many manufacturers.
- **Insertion depth: jack depth < plug barrel length.** Account for chassis wall thickness. If plug barrel is too short, it won't reach the inner contact through the panel cutout.

### USB Power Connectors

- **USB-C receptacle (power-only): GCT USB4125** (6-pin, top-mount, cheaper). **USB 2.0 with data: GCT USB4085** (16-pin, mid-mount).
- **Some USB-C cables only break out USB 2.0** (4 wires, not full 24). Do not assume full cable capability in your test setup.
- USB-C CC resistors, data line routing, and VBUS protection -> `interfaces/usb.md`.

### Terminal Blocks

- **Spring terminals over screw terminals for vibration.** Spring terminals auto-adjust tension with temperature cycling. Screw terminals loosen -- apply hot glue dab for retention if screw type is required.
- **Reflow soldering destroys terminal blocks.** Wave solder: peak 235-260 C (SnPb), 10 s max per wave. Manual solder: 350 C iron for 4-5 s.
- **UL 1059 vs IEC 60947-7 current ratings differ.** UL defines by heat rise at rated current; IEC defines by power dissipated at rated current. Always check which standard the datasheet references -- same block gets different numbers.
- **Inrush and surge: derate.** Terminal block ratings are steady-state. Frequent surges require oversizing.

**UL 1059 voltage/spacing classes (151-300 V range):**

| Class | Application | Min Air Gap | Min Surface |
|-------|------------|-------------|-------------|
| A | Service equipment | 19.1 mm (0.75") | 31.8 mm (1.25") |
| B | Commercial/IT | 2.3 mm (0.09") | 2.3 mm (0.09") |
| C | Industrial (UL 508) | 6.4 mm (0.25") | 9.7 mm (0.38") |

- **IEC creepage at 250 V, Pollution Degree 3:** 3.2 mm (Material Group I, CTI >= 600 V) to 5.0 mm (Group IIIb, CTI 100-175 V).

### FFC/FPC

- **Orientation: straight vs reverse.** Wrong orientation gives reversed pinout or no connection. If you picked wrong, swap bottom-contact for top-contact connector instead of replacing the cable.
- **Standard pitches: 1 mm (hand-solderable), 0.5 mm (reflow with stencil).** 0.8 mm rare. 0.35 mm uses staggered pins (usually FPC-produced, dark orange).
- **FFC connectors melt under hot air rework.** Cover with kapton tape before rework. IR oven reflow is OK for the initial assembly.
- **Latch from center or both sides simultaneously.** One-sided prying snaps the latch permanently. At 0.5 mm pitch, careless insertion shorts pins to neighbors.
- **Same pitch/pin count FFCs can vary in overall width.** Some (especially laptop keyboards) have "ears" for extra-secure mating. Verify connector datasheet accepts the cable width before ordering.
- **Do not solder directly to white-plastic FFCs** -- solder melts the plastic covering. Kapton-backed FPCs tolerate soldering.

### Pin Headers and Debug

- **Tag-Connect TC2030-IDC** for space-constrained debug: 6-pin pogo pads, zero board-side height. Standard SWD: 2x5 1.27 mm pitch header (ARM 10-pin).
- **Machine-pin headers vs stamped:** better contact, longer life, but not always compatible with stamped-pin mates. Verify before mixing.
- ESD protection on connector pins -> `protection/esd.md`.

### Molex Power Connectors

- **Molex 8981 series: up to 11 A per pin.** Press-fit, very tight. Common in CNC and 3D printer stepper driver boards.
- **Designed for very few mating cycles.** Do not use where frequent connect/disconnect is expected.

### RF Connectors (SMA)

- **SMA vs RP-SMA: center pin gender is swapped.** Convention: SMA for GPS/cellular (sub-2 GHz). RP-SMA for 2.4 GHz (WiFi, BT, ZigBee).
- **All antennas/cables: inner thread (outer nut). All boards/devices: outer thread.**
- Antenna placement, matching, and keep-out zones -> `misc/rf-antenna.md`.

## Common Mistakes

- **2.5 mm barrel plug in 2.1 mm jack passes bench test, fails in the field.** Intermittent under vibration or thermal cycling. The outer sleeve spring compensates but the inner pin connection is unreliable. Fix: verify inner pin diameter match between plug and jack.
- **Terminal block reflow-soldered -> deformed housing.** Cage clamps no longer grip wire properly even though connections appear OK visually. Fix: wave solder only; hand solder at 350 C for 4-5 s max.
- **FFC latch opened from one side -> broken latch.** 0.5 mm pitch latch tabs snap from one-sided prying. Connector can no longer retain cable. Fix: open from center or both sides. Budget spare connectors for prototyping.
- **JST GH (1.25 mm) mislabeled as Molex PicoBlade.** Surplus inventory is frequently wrong. Housings look similar but latch geometry differs. Fix: measure pitch, compare housing features to series datasheet.
- **DC power connected to standard Ethernet port.** Signal transformers in standard jacks are damaged by DC. Fix: use jacks without built-in transformers if passing DC, or use dedicated power connectors.
- **Low mating-cycle connector in a user-accessible port.** Molex 8981 (tens of cycles) or board-to-board connectors in a position where users plug/unplug daily guarantees field failures. Fix: match connector mating-cycle rating to expected use frequency.

## Formulas

**Terminal block dielectric withstand (UL 1059):**
**Rule of thumb:** Test voltage is always well above rated voltage.
**Formula:** V_test = 1000 V + 2 * V_rated
**Example:** 300 V rated terminal block -> V_test = 1000 + 2 * 300 = 1600 V applied for 1 minute.

## Sources

### Related Rules
- `interfaces/usb.md` -- USB-C CC resistors, data line routing, VBUS protection
- `protection/esd.md` -- ESD protection on connector pins
- `misc/rf-antenna.md` -- antenna placement, matching, keep-out zones

### References
1. SparkFun -- Connector Basics Tutorial: https://learn.sparkfun.com/tutorials/connector-basics
2. AllAboutCircuits -- How to Select DC Power Connectors: https://www.allaboutcircuits.com/industry-articles/how-to-select-dc-power-connectors-the-basics/
3. TE Connectivity -- Terminal Blocks Selection Guide: https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=1654690_TBlocks_Selection_Guide&DocType=DS&DocLang=English
4. Eaton -- How to Select a Terminal Block: https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/brochure/eaton-how-to-select-terminal-block-white-paper.pdf
5. Hackaday -- Friendly Flexible Circuits: The Cables: https://hackaday.com/2024/02/07/friendly-flexible-circuits-the-cables/
6. Hackaday -- JST Is Not A Connector: https://hackaday.com/2017/12/27/jst-is-not-a-connector/
