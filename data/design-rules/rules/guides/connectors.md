# Connectors

> Connector family selection -- JST series, barrel jacks, USB power, terminal blocks, FFC/FPC, pin headers, RF.

## Quick Reference

- **Always specify exact series + position count.** "JST connector" is meaningless -- JST makes hundreds of types. Use "JST PH 2-pin" or "JST SH 4-pin".
- **Barrel jacks: 5.5 mm outer / 2.1 mm inner, center-positive** is SparkFun's convention and the common one; verify the target device. A plug made for a 2.5 mm pin fits a 2.1 mm jack but makes only intermittent contact [1].
- **USB-C power-only: GCT USB4125. USB 2.0 with data: GCT USB4085** (details below). USB data routing -> `interfaces/usb.md`.
- **Terminal blocks: pick the soldering process by exact series.** Many are wave-only and reflow damages them; THR and SMT series are made for reflow [4, 7].
- **FFC orientation: match the straight or reverse cable to the connector's contact side** (details below).

## Design Rules

### JST Wire-to-Board Families

| Series | Pitch | Typical Use | Selection Note |
|--------|-------|-------------|----------------|
| XH | 2.5 mm | Stepper motors, LiPo balance | NOT 0.1" (2.54 mm) -- cumulative error over 6+ pins |
| PH | 2.0 mm | LiPo battery (SparkFun standard) | Extremely hard to disconnect -- good for reliability, bad for servicing |
| ZH | 1.5 mm | Compact I/O | Thinner wires |
| GH | 1.25 mm | Compact sensor/I/O | Easily confused with Molex PicoBlade |
| SH | 1.0 mm | Ultra-compact | Optional grip protrusions [6] |

- **JST GH vs Molex PicoBlade: both 1.25 mm pitch but NOT interchangeable.** Surplus inventory is frequently mislabeled. Measure pitch first, then compare housing features to specific series datasheet.
- **JST PH battery connector: S2B-PH-SM4-TB** (2-pin, right-angle SMD). Through-hole variant: S2B-PH-K-S.

### Barrel Connectors

- **3.5 mm outer / 1.3 mm inner** for smaller devices.
- **Pin-size mismatch:** the outer sleeve spring tolerates a loose plug, the inner pin doesn't, so a 2.5 mm plug on a 2.1 mm pin contacts intermittently [1]. Always verify the inner diameter match.
- **Switched jacks:** some models have a third contact that switches with the sleeve, for auto-switching between battery and wall adapter; follow the datasheet's switch topology [2].
- **Don't use audio jacks for power.** Many lack voltage and current ratings, exposed contacts can short during insertion, and they invite plugging in the wrong cable [2].
- **Insertion depth through a panel:** check the plug's engagement through the actual chassis thickness on the jack and plug mating drawings; a short barrel won't reach the inner contact [2].

### USB Power Connectors

- **USB-C power-only: GCT USB4125,** 6 contacts (power and CC), SMT top-mount, 3 A [9]. **USB 2.0 with data: GCT USB4085,** 16 contacts, through-hole top-mount, 5 A [8].
- **Some USB-C cables only break out USB 2.0** (4 wires, not full 24). Do not assume full cable capability in your test setup.
- USB-C CC resistors, data line routing, and VBUS protection -> `interfaces/usb.md`.

### Terminal Blocks

- **Vibration:** pick a terminal series rated for it (spring-clamp types keep their grip as screws can loosen), torque screws to spec and test under the real conditions [1, 4]. SparkFun's hot-glue dab is a hobby fix, not a qualified retention.
- **Soldering (Eaton's blocks):** reflow not recommended; SnPb wave peak 235-260 C, <= 10 s total and <= 5 s per wave, per EN 61760-1 [4, p.6]. Phoenix Contact's THR and SMT terminal blocks are made for reflow [7].
- **UL 1059 vs IEC 60947-7 ratings use different methods:** UL by heat rise at rated current, IEC by power dissipated at rated current. Check which standard the datasheet's numbers come from [4, p.2].
- **Inrush and surge: derate.** Terminal block ratings are steady-state; Eaton recommends extra margin for repeated inrush or overvoltage. Validate the real duty cycle [4, pp.2-3].

**UL 1059 voltage/spacing classes, 151-300 V (Eaton's summary) [4, p.4]:**

| Class | Application | Min Air Gap | Min Surface |
|-------|------------|-------------|-------------|
| A | Service equipment | 19.1 mm (0.75") | 31.8 mm (1.25") |
| B | Commercial/IT | 2.3 mm (0.09") | 2.3 mm (0.09") |
| C | Industrial (UL 508) | 6.4 mm (0.25") | 9.7 mm (0.38") |

- **IEC 60947-7-1 creepage at 250 V working voltage (AC rms or DC), Pollution Degree 3 at the insulation:** 3.2 mm (Material Group I, CTI >= 600) to 5.0 mm (Group IIIb, CTI 100 to < 175) [4, p.5].

### FFC/FPC

- **Orientation: straight vs reverse.** The wrong one gives a reversed pinout or no connection. Fix it with the other cable type or a footprint-compatible top/bottom-contact connector; verify the pin numbering and cable dimensions [5].
- **Pitches:** Hackaday prefers 1 mm FFC for hand soldering and 0.5 mm for stencil reflow; 0.8 mm is rare; 0.35 mm cables use staggered pins (usually FPC, dark orange) [5].
- **Use the FFC connector's specified reflow and rework profile** (Hirose FH12 gives one); shield the plastic with Kapton tape during hot-air rework [5, 10].
- **Flip-lock actuators: operate them evenly, as the series instructs.** One-sided prying can snap the latch; a misinserted 0.5 mm cable can bend conductors into their neighbours [5, 10].
- **Same pitch/pin count FFCs can vary in overall width.** Some (laptop keyboards) have "ears" for extra-secure mating. Match width, thickness and ears to the connector drawing [5].
- **Don't solder directly to white-plastic FFCs** -- solder melts the plastic (low-temperature solder is the exception); Kapton-backed FPCs tolerate it. Check the cable's rating [5].

### Pin Headers and Debug

- **Tag-Connect TC2030-IDC** for space-constrained debug: 6-pin pogo pads, zero board-side height. Standard SWD: 2x5 1.27 mm pitch header (ARM 10-pin).
- **Machine-pin headers vs stamped:** better contact, longer life, but some combinations don't mate. Verify before mixing [1].
- ESD protection on connector pins -> `protection/esd.md`.

### Molex Power Connectors

- **Molex 8981 series (SparkFun: up to 11 A per pin):** very tight friction fit, made for few mating cycles; common in CNC and 3D printer stepper driver boards. Check the exact part's current and mating-cycle ratings [1].

### RF Connectors (SMA)

- **SMA vs RP-SMA: center pin gender is swapped.** SparkFun commonly uses SMA for GPS/cellular and RP-SMA for 2.4 GHz (WiFi, BT, ZigBee); check the antenna's connector [1].
- **Threads:** SparkFun's boards use outer threads, its antennas an outer nut with inner threads [1].
- Antenna placement, matching, and keep-out zones -> `misc/rf-antenna.md`.

## Common Mistakes

- **Wave-only terminal block reflow-soldered -> damaged housing.** Fix: use the exact series' approved process and profile, or a THR/SMT-rated block where it must go through reflow [4, 7].
- **JST GH (1.25 mm) mislabeled as Molex PicoBlade.** Surplus inventory is frequently wrong. Housings look similar but latch geometry differs. Fix: measure pitch, compare housing features to series datasheet.
- **Low mating-cycle connector in a user-accessible port.** Molex 8981 or board-to-board connectors where users plug in daily wear out. Fix: match the exact connector's rated mating life to expected use [1].

## Formulas

**Terminal block dielectric withstand (UL 1059, Eaton's summary) [4, p.4]:**
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
7. Phoenix Contact -- PCB terminal blocks (wave, THR and SMT soldering): https://www.phoenixcontact.com/en-us/products/pcb-terminal-blocks-and-pcb-connectors/pcb-terminal-blocks
8. GCT -- USB4085 Type C USB 2.0 Connector (read 2026-11-06): https://gct.co/connector/usb4085
9. GCT -- USB4125 Type C USB Charging Connector (read 2026-11-06): https://gct.co/connector/usb4125
10. Hirose -- FH12 Series FPC/FFC Connectors catalog: https://www.hirose.com/en/product/series/FH12
