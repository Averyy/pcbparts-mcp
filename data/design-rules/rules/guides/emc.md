# EMC

> Filtering, shielding, PCB layout, SMPS hot loops, and component selection for electromagnetic compatibility.

## Quick Reference

- **Hot loop area determines SMPS emissions.** L2 ground plane at 0.13 mm reduces loop inductance 14x (187 nH -> 13 nH). Route VIN/return traces through filter cap pads, not around them.
- **Series resistors on every digital I/O pin.** 50-100 ohm on outputs, 35-50 ohm on inputs. Place at the driving IC. Single most cost-effective EMI reduction.
- **1 mV between two antenna parts** (cables, heatsinks) can fail CISPR 32 Class B. Threshold drops to 100 uV for stricter limits.
- **No Y-caps on LISN side of CM choke.** Y-caps between choke and cable bypass the choke entirely. Y-caps go on the board side only.
- **A single unfiltered wire through a shielded enclosure eliminates ALL shielding benefit.** Every cable penetration must be filtered or have a 360-degree shield connection.

## Design Rules

### PCB Layout for EMC

- **1000 pF bypass cap on any MCU pin with edge rate < 100 ns.** On outputs: cap on receiver side of series R. On inputs: cap on MCU side of series R. Wrong side of the resistor negates the filtering.
- **All I/O connectors on one edge of the board.** Connectors on opposite edges let cables form loop antennas with the board. Plane resistance is < 1 mohm/square -- digital return currents couple only millivolts of noise, but those millivolts drive cables as antennas.
- **Never gap the ground plane between analog and digital sections.** The gap forces return current to detour, creating a much larger loop. At frequencies above ~100 kHz, return currents are confined directly below the signal trace -- gapping provides zero benefit. Use routing partitions (separate trace zones on different layers), not copper gaps.
- **Power plane spacing < 0.25 mm** for closely-coupled plane pairs with 3+ IC power pins at a given voltage.
- **Never put a ferrite on a ground connection.** Ferrites go on VCC/power inputs only. PLLs and clock multipliers: ferrite on power per IC datasheet, never on ground.
- **Crystal is the #1 susceptibility vulnerability.** Harmonics of other signals (UART, SDIO, SMPS) coupling into the crystal loop corrupt the oscillator and degrade RF performance even when the crystal itself is spec-compliant. No unrelated components within 25 mm. No signal traces routed under the crystal on any layer. Guard ring with ground copper connected to ground plane.
- **Unused MCU pins:** configure as inputs, tie directly to ground. Floating pins couple noise from substrate capacitively. Enable watchdog to recover if a disturbance reconfigures the pin as a high output.
- **Slot antennas:** no slot > 100 mm in enclosures or ground planes. A 4x4 grid of 3 mm holes provides equivalent airflow to a single 12 mm hole with > 20 dB better shielding.
- **Filtering priority order:** (1) signals leaving the enclosure, (2) signals leaving the PCB to other boards, (3) on-board signals with high-impedance loads, (4) parallel I/O with fast edges. Remove filter components one at a time in pre-compliance to identify which are actually needed.
- **Cable ground return ratio:** minimum 1 ground wire per 9 signal wires. For cables > 300 mm, use 1:4. A single ground wire returning all RF energy from a second board creates a radiating antenna path.
- **Stripline traces (buried between planes) produce zero voltage at board edges.** Use for traces routed between connectors -> `guides/pcb-layout.md`.
- **DC power traces carry HF noise.** Clock-frequency currents drawn from power pins often exceed clock-frequency currents on clock traces. Filter every power pin with bypass caps and apply series R to I/O pins regardless of nominal switching rate.

### 2-Layer Board EMC

- **2-layer boards can approach 4-layer EMC performance with discipline:** expand all ground traces to maximum width, fill empty space with ground copper, stitch top/bottom ground at every crossing with vias.
- **Ground fill connection rule:** connected at 2+ points = part of return current grid. Connected at 1 point = floating shield (useless for return current, may resonate).
- **3:1 rule:** length-to-width ratio of power and ground traces between IC and voltage source must not exceed 3:1. Run power and ground directly over each other on opposite layers.
- **MCU ground island:** solid ground area on bottom layer under the MCU, extending ~6 mm beyond the IC outline. Tie bypass caps, oscillator caps, and ferrite bead grounds to this island.

### SMPS Hot Loops

- **Quantified shielding plane benefit (ADI AN-139, 10x10 cm loop at 27 MHz):**

| Configuration | Loop Inductance |
|--------------|----------------|
| Single-layer, no plane | 187 nH |
| L2 at 1.5 mm (2-layer typical) | 42 nH (4.5x reduction) |
| L2 at 0.5 mm | 23 nH |
| L2 at 0.13 mm | 13 nH (14x reduction) |

- **Recommended 4-layer EMC stackup:** L1 signal + components, L2 solid ground, L3 power, L4 signal. L2 provides continuous return path for L1 traces and shields from L3/L4 noise.
- **Keep L2 solid in the hot loop area.** No signal vias punching through. Eddy currents in L2 create HF voltage that couples through nearby vias to other layers.
- **Capacitor ESL:** use short/reverse-geometry caps (0402 preferred). Route VIN/return traces **through** filter cap pads -- any trace between cap pad and power path adds hundreds of pH, negating low-ESL advantage. Stack multiple 0402s closest for lowest combined ESL, larger cases further away for bulk.
- **Complete GND ring** with via fence around SMPS section. Filter cap GND return connects where VIN current crosses the ring -- filtering inductance must remain between ring crossing and hot loop.
- **Keep filtering inductors away from the main power inductor.** Transformer coupling bypasses the filter entirely. Orient perpendicular, place outside the GND ring/via fence.
- **Switch node copper area:** minimize surface area. Large switch node copper is a broadband E-field source. Keep as small as current rating allows.
- **Sense lines** (FB, SENSE+, SENSE-): sub-millivolt noise causes duty cycle jitter. Route on opposite side of shielding plane from hot loops. Gap between SENSE+ and SENSE- traces as small as possible.
- **INTVCC decoupling loop:** RF energy is > 20 dB lower than main hot loop. Still route carefully, but prioritize the main switch node loop.
- **External gate drive loops:** gate currents are single-digit amps with single-digit ns edges. Bottom FET gate loop is supplied from INTVCC cap -- source-GND and cap-GND must share a short, direct connection.
- **Flyback CM emissions:** electric field (not magnetic) dominates across the isolation barrier. Minimize primary-side switch node copper area. Use a Faraday shield in the transformer. CM chokes on primary input are standard.
- **Buck-boost and SEPIC:** two hot loops (buck-side and boost-side) may share a current-sense resistor. Split into two parallel resistors to separate loop GND connections.
- Integrated-switch ICs outperform external Schottky, which outperform external MOSFETs for EMI.
- SMPS topology selection and inductor sizing -> `power/switching.md`.

### Common-Mode Filtering

- **Unbalanced inputs** (e.g., buck converter with VBATT- shorted to ground): do NOT use a CM choke. Filter the driven conductor to chassis ground directly. Make it very unbalanced and filter the high-impedance side.
- **Isolated DC inputs (no chassis ground):** add capacitors between circuit ground plane and chassis ground plane under the connector to emphasize the imbalance, enabling effective unbalanced filtering on the driven conductor only.
- **Balanced systems need balanced filters.** An unbalanced filter on a balanced system forces mode conversion -- DM noise becomes CM, making emissions worse, not better.
- **CM choke core material:** ferrite for broadband (100 kHz - 100 MHz). Nanocrystalline for lower-frequency conducted (10 kHz - 10 MHz) -- higher mu_i but physically larger.
- **AC mains CM filtering:** CMC rated AC 250V + X-cap (100 nF - 1 uF) + Y-caps (2.2 nF per line). Y-cap total limited to ~4.7 nF per line-to-ground (safety leakage at 60 Hz/250V). CMC covers the low-frequency range Y-caps cannot reach.
- **Products without a metal chassis:** use lossy CM choke (resistance, not just inductance). Pure inductance creates resonances with the capacitive return path through stray capacitance. Y-caps give power wires low-impedance path to board ground.
- **Small plastic enclosures** with all wires on one edge: DM filtering (pi-filter to board ground) is usually sufficient. CM filtering needed only if cables act as antennas.

> WARNING: CMC dot convention determines whether the coil functions as a CM choke or a normal-mode inductor.
> Dots on the same side = CM choke (flux reinforces for CM, cancels for DM). Dots on opposite sides = NOT a CMC --
> acts as a coupled inductor that blocks differential signals. Verify dot placement against the
> datasheet equivalent circuit for every CMC in the design.

### Shielding

- **Apertures determine real-world shielding**, not material thickness. 2-mil copper at 100 MHz gives 66 dB absorption + 88 dB reflection -- any solid copper is effectively perfect above a few MHz.
- **A shielded enclosure can have SE < 0 dB** (worse than no shield) if poorly placed apertures couple energy to the enclosure, which becomes a better antenna than the original source. Sealed metallic enclosure with no apertures: >= 40 dB. Add one unfiltered cable: 0 dB.
- **Depth-to-width ratio of 3:1 gives ~90 dB attenuation per aperture** (waveguide below cutoff). Does not apply if a wire penetrates the opening (TEM mode propagates regardless).
- **Cable shield 360-degree contact** to enclosure. Pigtail connections provide negligible shielding above a few MHz.
- **Seams** are worse than apertures due to length. A half-wavelength seam radiates as a dipole. Conductive adhesive tape is not adequate for seams > ~25 mm -- use finger stock or conductive gaskets with continuous contact.
- **Paint/anodize heatsink surfaces** -- radiation accounts for ~25% of natural convection heat transfer, and painted surfaces reduce EMI reflections from internal sources.
- **Magnetic shielding below ~kHz:** conductive shields fail (eddy currents too weak). Use mu-metal or steel. Must divert flux all the way around the object; a plate above/below provides zero magnetic shielding.
- **Near-field magnetic shielding:** a conductive plate between source and victim redirects flux via eddy currents. Effective above ~100 kHz.
- **Galvanic corrosion at shield bonds:** anodic index difference > 0.95V requires plating or conductive gaskets. Aluminum-to-steel is the common offender.
- **Board-level shielding cans:** required when SMPS or clock circuitry is near an RF receiver (GPS, BLE, Wi-Fi). Can must solder to continuous ground ring with multiple vias. Apertures follow same rules -- many small holes, no slots.

### Filter Component Selection

- **3-terminal capacitors** maintain insertion loss to ~100 MHz (vs 2-terminal SRF at ~10 MHz). Route input/output vias on opposite sides of the cap body -- adjacent vias couple capacitively and bypass the filter (performance drops from ~100 MHz to ~10 MHz).
- **3-terminal cap mounting:** "through" connection (pattern cut, cap in series) for best I/O filtering. "Non-through" (parallel, pattern intact) for IC supply decoupling -- halves bypass impedance but some noise passes unfiltered.
- **3-terminal cap families:** Murata NFM series (0402-1210, feed-through, to 100 MHz). TDK YFF series (4-terminal, improved HF).
- **LC composite EMI filters:** Murata NFE61P (0603, LC pi-filter, broadband). TDK MAF series (0402-0805, integrated LC, USB/HDMI). Key advantage: no PCB parasitics between L and C elements. Array-type (4 circuits/package) for LCD/camera interfaces.
- **Ferrite bead LC resonance** -> `guides/passives.md`. Key rule: beads rated >= 5x load current. Prefer lossy impedance curve to avoid resonance; sharp-curve beads need a series damping resistor.
- **CMC saturation risk:** CMCs with intentional DM impedance can saturate under high DC load. Symptom: filter works at low load, fails at full load. Verify CMC impedance at rated DC current.
- **CMC differential-mode leakage:** all CM chokes have some DM inductance. For USB 3.0/DisplayPort, verify DM insertion loss does not degrade signal integrity above 5 GHz.

### CM Choke and EMI Component Recommendations

- **Signal-line CMCs (USB 2.0, HDMI, MIPI):** Murata DLW21SN series (0805, 90 ohm CM at 100 MHz). Provides skew correction -- transformer coupling realigns edge timing, reducing jitter from trace imbalance.
- **Signal-line CMCs (USB 3.x, DP HBR):** Murata DLW21HN (optimized for > 5 Gbps). TDK ACM series (low DM loss to 10 GHz).
- **Power-line CMCs (DC bus, SMPS input):** If DC bus > 6A or need nanocrystalline for low-frequency CM noise: Wurth WE-CMB (through-hole, 1-30A, MnZn or nanocrystalline). If SMD and <= 6A: TDK ACT series (ferrite, smaller footprint).
- **AC mains line filters (integrated CMC + X/Y caps):** If pre-certified module needed to skip filter compliance iteration: Schaffner FN series (widest range of current/voltage ratings). If space-constrained or need board-mount IEC inlet combo: Schurter 5500 series (integrated inlet + fuse + filter).

### Interface-Specific EMI Filtering

- **USB 2.0:** CM choke (90 ohm at 100 MHz, Murata DLW21SN) within 10 mm of connector. Add 47 pF caps from each data line to ground after the CMC for HF emissions above 500 MHz. ESD TVS on VBUS and data lines -> `protection/esd.md`.
- **USB hub ports:** one CMC per port. Shared CMCs degrade inter-port isolation and create ground loops.
- **USB 3.x:** standard USB 2.0 CMCs destroy SuperSpeed signal integrity. Use Murata DLW21HN or TDK ACM2012H within 15 mm of connector. Separate 2.0 and 3.x pairs with independent CMCs.
- **HDMI / DisplayPort:** CMC on each TMDS/ML lane pair, 90 ohm CM at 100 MHz, DM insertion loss < 0.5 dB at signal frequency. TDK MAF for space-constrained designs.
- **Camera MIPI CSI-2:** LC composite filters (Murata NFE61P) on each data lane pair. Place at receiver end (SoC side) to prevent noise coupling along flex cable. 4-circuit array filters for 4-lane CSI.
- **SPI/I2C off-board:** ferrite bead + TVS on each line. SPI clock > 10 MHz: add 33-100 pF cap after the ferrite -> `interfaces/spi.md`, `interfaces/i2c.md`.
- **General rule for high-speed differential:** always verify DM insertion loss at actual data rate. A CMC that fixes EMI at 200 MHz but adds 3 dB loss at 5 GHz will cause bit errors.

### Compliance Testing

- **Pre-compliance scanning saves weeks.** Scan at 1-5 mm distance -- H-field probes localize current loops, E-field probes localize voltage nodes. Lab compliance testing costs $5K-15K per round.
- **Clock harmonics dominate radiated emissions.** 25 MHz crystal has significant energy at 75, 125, 175 MHz. SSC reduces peaks ~6-10 dB but SSC is incompatible with USB (<500 ppm clock accuracy) -- SSC only on internal clocks.
- **Via fence around board edges and I/O connectors:** ground vias at <= lambda/20 spacing (at 1 GHz: <= 15 mm). Additional stitching vias from top-layer ground to ground plane within 5 mm of every connector.
- **Design for rework:** on first prototypes, add unpopulated footprints for series resistors on clock outputs, ferrite beads on power inputs, CM chokes at connectors. 0-ohm pads cost nothing but save a board respin.
- **Near-field probe sets:** Langer RF-B 3-2 (H-field 1-25 mm + E-field, ~$800). Beehive Electronics 100 series (~$300).
- **Pre-compliance spectrum analyzers:** tinySA Ultra (100 kHz - 5.3 GHz, ~$130, not calibrated -- relative comparisons only). Rigol DSA815-TG (9 kHz - 1.5 GHz, ~$1200, CISPR QP detector). Siglent SSA3021X (9 kHz - 2.1 GHz, ~$1500, built-in EMI detector).

## Common Mistakes

- **Unbalanced filter on a balanced system.** Forces mode conversion -- DM noise becomes CM, making emissions worse. The fix seems counterintuitive: balance the filter, not the source.
- **3-terminal cap with vias too close together.** Capacitive coupling across cap body bypasses the filter -- performance drops from ~100 MHz to ~10 MHz. Fix: input/output vias on opposite sides of the cap body.
- **Heatsink acting as antenna.** E-field coupling from IC package drives the heatsink; 1 mV at resonance can fail radiated emissions. Grounding the heatsink needs very low-impedance bond at GHz -- often harder than just minimizing heatsink size and routing signals below top ground plane.
- **Filter inductor too close to SMPS power inductor.** Transformer coupling bypasses filter attenuation. Symptom: conducted emissions show no improvement despite adding pi-filter. Fix: orient perpendicular, place outside GND ring.
- **Near-field probe scan at wrong distance.** H-field probes must be within 1-5 mm. At 10 mm+ resolution is too poor to identify hot loops. Fix: smallest H-field loop (Langer RF-B 3-2) at 1-2 mm, board at full load.
- **CMC dot convention reversed in schematic.** Dots on opposite sides makes the coil block differential signals instead of common-mode noise. On USB/HDMI this kills the data link entirely. Fix: dots on the same side for both windings; verify against datasheet equivalent circuit.
- **Ground plane gap "between analog and digital."** 50-year-old rule that no longer applies on multilayer boards. At > 100 kHz return currents are confined directly below the signal trace -- the gap forces them to detour, creating the very coupling it was supposed to prevent.

## Formulas

**Shielding absorption loss:**
**Rule of thumb:** 1 skin depth = 8.7 dB absorption. 2-mil copper > 60 dB at 100 MHz.
**Formula:** A(dB) = 8.7 * (t / delta), where delta = 1 / sqrt(pi * f * mu * sigma)
**Example:** 2-mil copper (50.8 um) at 100 MHz (delta = 6.7 um) -> A = 8.7 * (50.8 / 6.7) = 66 dB.

**Waveguide below cutoff (aperture attenuation):**
**Rule of thumb:** Depth-to-width ratio of 3:1 gives ~90 dB attenuation per aperture.
**Formula:** Attenuation(dB) ~ 30 * (d/a) * sqrt(1 - (f/fc)^2), where d = depth, a = max dimension, fc = v/(2a). Does not apply if a wire penetrates the opening (TEM mode propagates).
**Example:** 5 mm deep, 2 mm wide hole at 1 GHz: fc = 75 GHz >> 1 GHz, attenuation ~ 30 * (5/2) * 1 = 75 dB.

## Sources

### Related Rules

- `guides/pcb-layout.md` -- Stripline routing, stackup design, ground plane rules
- `power/switching.md` -- SMPS topology selection, inductor sizing, hot loop components
- `guides/passives.md` -- Ferrite bead LC resonance, impedance curves
- `protection/esd.md` -- ESD TVS on USB, VBUS, and data lines
- `interfaces/spi.md` -- SPI off-board filtering with ferrite and cap
- `interfaces/i2c.md` -- I2C off-board filtering with ferrite and TVS

### References

1. LearnEMC -- Introduction to Printed Circuit Board Layout for EMC: https://learnemc.com/pcb-layout
2. LearnEMC -- Introduction to Electromagnetic Compatibility: https://learnemc.com/introduction-to-emc
3. LearnEMC -- An Introduction to Grounding for EMC: https://learnemc.com/grounding
4. LearnEMC -- Introduction to Common-Mode Filtering: https://learnemc.com/cm-filtering
5. LearnEMC -- Plane-Wave Shielding Theory: https://learnemc.com/shielding-theory
6. LearnEMC -- Practical Electromagnetic Shielding: https://learnemc.com/practical-em-shielding
7. TI SZZA009 -- PCB Design Guidelines for Reduced EMI: https://www.ti.com/lit/an/szza009/szza009.pdf
8. ADI AN-139 -- Power Supply Layout and EMI: https://www.analog.com/en/resources/app-notes/an-139.html
