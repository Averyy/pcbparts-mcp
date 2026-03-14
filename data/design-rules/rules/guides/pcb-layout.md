# PCB Layout

> Stackup selection, ground planes, via design, trace sizing, and layer assignment for EMC and signal integrity.

## Quick Reference

- **4-layer with thin prepreg (< 0.25 mm / 10 mil) gives 10+ dB less radiation than equal-spaced layers.** This is the single cheapest EMC improvement on a 4-layer board.
- **Never split a ground plane.** Partition routing into analog/digital zones instead. Henry Ott tested jumpered split planes -- connecting them together improved both functional and EMC performance in nearly all cases.
- **Every signal via needs an adjacent ground return via.** Without it, return current forms a large radiating loop. Do not rely on randomly placed stitching vias.
- **50-ohm microstrip: W/H ~ 2:1 on FR4 (Er ~ 4.0).** 50-ohm stripline: B/W ~ 2-2.2:1. IPC-2141A equations are ~5-6% accurate between 50-100 ohm; less accurate outside that range.
- **IPC-2152 replaces IPC-2221B for trace current.** The old "internal = half external" rule is wrong -- FR4 dielectric has 10x better thermal conductivity than air. Same copper cross-section applies to all layers.

## Design Rules

### Stackup Design

- **Five stackup objectives (Henry Ott):** (1) Every signal layer adjacent to a plane. (2) Signal layers tightly coupled to adjacent planes (< 0.25 mm / 10 mil). (3) Power and ground planes closely coupled. (4) High-speed signals buried between planes. (5) Multiple ground planes.
- **When forced to choose #2 vs #3: always choose tight signal-to-plane coupling.** Interplane capacitance is insufficient below ~500 MHz for decoupling -- use discrete caps instead.
- **8-layer is the minimum to satisfy all five objectives simultaneously.** 4-layer and 6-layer boards require compromises. Above 8 layers, additional layers are for routing density only.
- **Stackup must be symmetrical** (balanced) to prevent warping during fabrication.
- **Request your fab's standard stackup table before designing custom layer spacing.** Standard total thicknesses: 1.6 mm (most common), 1.0 mm, 2.0 mm. Fab standard 4-layer: typically 0.2 mm prepreg / 1.0 mm core / 0.2 mm prepreg at 1.6 mm total. Deviating adds cost and lead time.

#### 2-Layer Boards

- **2-layer boards rarely pass EMC unshielded above 20-25 MHz.** Use only for low-speed designs (GPIO, I2C, UART) or cost-constrained products with shielded enclosures.
- **Fill all empty space with ground copper on both layers.** Connect top and bottom fills with stitching vias at every intersection (max 5 mm pitch). A ground fill connected at only 1 point is a floating island -- parasitic antenna, not a ground plane.
- **Place all ICs on one side, connectors on one edge.** Reduces layer transitions and simplifies return paths.

#### 4-Layer Stackups

| Stackup | Objectives Met | Notes |
|---------|---------------|-------|
| Sig/GND/PWR/Sig | #1, #2 (with thin prepreg) | Most common. Standard fab: 0.2 mm prepreg, 1.0 mm core. 10+ dB vs equal spacing |
| GND/Sig+Pwr/Sig+Pwr/GND | #1, #2, #4, #5 | Best 4-layer EMC. Two GND planes can stitch into Faraday cage. Power routed as wide traces. Rework difficult |
| Sig+Pwr/GND/GND/Sig+Pwr | #1, #2, #5 | Outer signals allow rework. Two GND planes but no shielding of signal layers |

- **A dedicated power plane is not required on a 4-layer board.** Wide power traces on signal layers can free a layer for a second ground plane -- lower ground impedance, better shielding, stitchable for Faraday cage around board periphery.

#### 6-Layer Stackups

- **Recommended:** Sig/GND/Sig/PWR/GND/Sig. Both outer signal layers tightly coupled to adjacent ground planes. Inner signal layer (L3) references PWR -- adequate for low-speed only.
- **Step up from 4 to 6 when:** routing density exceeds 2 signal layers, or USB/Ethernet/DDR requires buried differential pairs.

### Ground Planes & Mixed-Signal

- **Connect AGND and DGND pins of ADCs to the same solid ground plane.** Plane resistance is < 1 mohm/square -- coupling between regions is millivolts worst-case at DC. A/D datasheets that recommend split planes are wrong; their own fine print says "connect AGND and DGND to the same low-impedance ground."
- **ADC ground noise budget (1V reference):** 8-bit = 4 mV, 10-bit = 1 mV, 12-bit = 240 uV, 16-bit = 15 uV, 24-bit = 60 nV. Single solid plane adequate for 8/10/12-bit. For 14+ bit, use isolated routing zones but still a connected plane.
- **Routing discipline is the solution, not plane splits.** Route digital signals only in the digital section, analog only in the analog section, on all layers. HF return currents self-confine in a narrow band directly beneath their signal trace -- they have no desire to flow through the analog region.

### Microstrip vs Stripline

- **Microstrip (surface layer):** propagation delay ~136 ps/in (5.4 ns/100mm) on FR4. Higher radiation, lower dielectric loss. Trace width ~2x stripline for same impedance.
- **Stripline (buried between planes):** propagation delay ~170 ps/in (6.7 ns/100mm) on FR4. ~25% slower than microstrip. Better shielding, lower radiation. Required for high-speed signals that must be contained.
- **Propagation delay depends only on dielectric constant, not trace dimensions.** All impedance variants on the same layer have identical delay -- useful for length matching.
- **Termination rule:** if one-way propagation delay >= half the signal rise/fall time, terminate in characteristic impedance. Conservative: 2-inch/nanosecond rule. Example: 5 ns rise time -> terminate traces >= 10 inches.

### Trace Width & Current Capacity

- **IPC-2152 unified formula** (valid for dT = 2-100C, I up to 30A):
  `Ac (sq.mil) = (117.555 * dT^-0.913 + 1.15) * I^(0.84 * dT^-0.108 + 1.159)`
  `Width (mil) = Ac / thickness (mil)` where `thickness = oz * 1.37`
- **Nearby copper planes reduce actual temperature rise** substantially below the generic chart prediction. IPC-2152 provides correction factors for plane proximity.
- **Parallel traces spaced < 1 inch apart interact thermally** -- use combined current for sizing.

### Vias

- **Via current capacity:** model as copper cylinder -- circumference (pi * d) is analogous to trace width. A 0.25/0.5 mm (10/20 mil) via: R ~ 1.5 mohm, thermal resistance ~ 180 C/W. A single via carrying 20A dissipates 600 mW (108C rise). 10 vias in parallel: 2A each, 1.08C rise. Always use via arrays for high-current connections.
- **Return vias:** at every signal layer transition, place a ground via adjacent to signal via within 2-3x the via-to-plane distance. For high-speed/RF, use purposefully designed stitching via arrays -- randomly placed stitching vias do not guarantee signal integrity.
- **Stitching via pitch for shielding:** center-to-center < lambda/10 at target frequency. Example: 0.5 mm (20 mil) pitch -> effective shielding to ~43 GHz.
- **Single-ended via impedance** is dominated by stitching via placement and antipad size. **Differential via impedance** is more sensitive to signal via-to-via spacing and antipad than to stitching vias -- stitching mainly affects field confinement (localization frequency).
- **Via-in-pad required for:** fine-pitch BGAs (< 0.8 mm pitch) and thermal pads needing via arrays. Adds cost: epoxy fill + planarization + cap plate. Not needed for 0805+ passives or QFP/QFN with accessible pads.
- **Via aspect ratio <= 10:1** (board thickness : hole diameter) for reliable plating. Preferred <= 8:1. A 1.6 mm board needs >= 0.2 mm drill.
- **Blind via aspect ratio: 1:1 max.** Deeper holes trap air during plating -> open circuits. When exceeded, use stacked microvias (2-3x standard process cost).
- **Staggered vias** are cheaper and more reliable than stacked -- less precision required, lower stress. Use staggered unless vertical alignment is physically required.
- Thermal via sizing for exposed pads -> `guides/thermal.md`. Full DFM constraints -> `guides/dfm.md`.

### Annular Ring & Thermal Relief

- **Annular ring vs breakout probability:** 0.05 mm (2 mil) = 98% breakout. 0.13 mm (5 mil) = 5% breakout. >= 0.15 mm (6 mil) = ~0% breakout. Design for 0.13 mm+ minimum.
- **Teardrop pads** required for traces < 0.5 mm (20 mil) wide. Also recommended for flex PCBs where shear and vibration stress trace-pad junctions.
- **Thermal relief:** 0.2 mm spoke width, 0.25 mm clearance. Apply on SMD pads connected to large copper pours and through-hole pins connected to planes.
- **DO NOT use thermal relief on:** vias connecting to planes (put relief on the SMD pad instead), die-attach/exposed pads, thermal pads of ICs. A thermal relief on a via has no value -- confine heat at the SMD pad, not at the via.

### Component Placement

- **Decoupling caps within 2 mm of IC power pins.** Via to ground within 1 mm of cap ground pad. Full strategy -> `power/decoupling.md`.
- **Crystal oscillators within 5 mm of MCU clock pins.** Inner layers preferred, no vias on clock traces. Full crystal design -> `misc/crystal.md`.
- **All connectors on one board edge** (two edges acceptable if opposite). Signals entering/exiting through different edges create large CM current loops -> `guides/emc.md`.

## Common Mistakes

- **Splitting the ground plane between analog and digital.** Manufacturers' own datasheets recommend it -- ignore this. Henry Ott tested boards with jumpered split planes: connecting them together improved both functional performance and EMC in nearly all cases. Fix: single solid plane with partitioned routing zones.
- **4-layer stackup with equally spaced layers.** Signal-to-plane distance ~0.5 mm instead of < 0.25 mm. Costs 10+ dB radiation. Fix: thin prepreg (< 0.25 mm) for signal-to-plane, thick core (> 1 mm) for plane-to-plane. Ask fab for their standard stackup -- it already uses this spacing.
- **Using a power plane on a 4-layer board when a second ground plane would be better.** Two GND planes can be stitched around the board periphery to form a Faraday cage enclosing all signal traces -- impossible with only one GND plane. Route power as wide traces instead.
- **20-H rule applied when power plane is sandwiched between two ground planes.** The full 20-H pullback is unnecessary and wastes board area. 2-3H is sufficient if pullback is needed at all; sandwiched power planes are not a radiation problem.
- **Ground fill on 2-layer board connected at only one point.** Acts as parasitic antenna rather than ground plane. Fix: connect ground fill at multiple points with stitching vias, max 5 mm pitch.
- **Trace width sized by IPC-2221B "internal = half external."** Wrong -- IPC-2152 shows same copper cross-section for all layers. FR4 dielectric conducts heat 10x better than air; internal layers may actually run cooler.
- **Slowing risetimes ignored in favor of matched termination.** Matched terminations make risetimes faster and pull more current. First impulse should be to slow the risetime. Unless building very high-speed digital boards, few traces should require matched termination.

## Formulas

**Microstrip impedance (IPC-2141A / ADI MT-094):**
**Rule of thumb:** W/H ~ 2:1 gives ~50 ohm on FR4 (Er ~ 4.0). W/H ~ 1:1 gives ~75 ohm.
**Formula:** Zo = (87 / sqrt(Er + 1.41)) * ln(5.98H / (0.8W + T)) -- dimensions in mils
**Example:** Er = 4.0, H = 10 mil, W = 20 mil, T = 1.4 mil -> Zo = (87 / sqrt(5.41)) * ln(59.8 / 17.4) = 37.4 * 1.23 = 46 ohm. Equation predicts ~5% low for 50-ohm target; decrease W to 18 mil.

**Stripline impedance:**
**Rule of thumb:** B/W ~ 2-2.2:1 for 50 ohm (B = plane-to-plane spacing).
**Formula:** Zo = (60 / sqrt(Er)) * ln(1.9B / (0.8W + T)) -- dimensions in mils
**Example:** Er = 4.0, B = 20 mil, W = 8 mil, T = 1.4 mil -> Zo = 30 * ln(38 / 7.8) = 30 * 1.58 = 47.5 ohm.

**IPC-2152 trace current capacity:**
**Rule of thumb:** 1A per 0.25 mm (10 mil) width at 1 oz copper with 10C rise (conservative).
**Formula:** Ac (sq.mil) = (117.555 * dT^-0.913 + 1.15) * I^(0.84 * dT^-0.108 + 1.159)
**Example:** I = 3A, dT = 10C, 1 oz Cu (1.37 mil) -> Ac ~ 114 sq.mil -> Width = 114 / 1.37 = 83 mil (2.1 mm).

## Sources

### Related Rules

- `guides/thermal.md` -- Thermal via sizing for exposed pads, PCB copper as heatsink
- `guides/dfm.md` -- Fab tolerances, annular ring, via aspect ratio constraints
- `power/decoupling.md` -- Decoupling cap placement within 2 mm of IC power pins
- `misc/crystal.md` -- Crystal placement within 5 mm of MCU clock pins
- `guides/emc.md` -- Connector placement, stripline for EMC, ground plane rules

### References

1. LearnEMC -- Identifying Current Paths: https://learnemc.com/identifying-current-paths
2. LearnEMC -- Some of the Worst EMC Design Guidelines: https://learnemc.com/some-of-the-worst-emc-design-guidelines
3. Henry Ott -- Grounding of Mixed Signal PCBs: https://hott.shielddigitaldesign.com/techtips/split-gnd-plane.html
4. Henry Ott -- PCB Stack-Up Part 1: Introduction: https://hott.shielddigitaldesign.com/techtips/pcb-stack-up-1.html
5. Henry Ott -- PCB Stack-Up Part 2: Four-Layer Boards: https://hott.shielddigitaldesign.com/techtips/pcb-stack-up-2.html
6. Altium -- How to Design the Best 4-Layer PCB Stackup: https://resources.altium.com/p/4-layer-pcb-stackup
7. ADI MT-094 -- Microstrip and Stripline Design: https://www.analog.com/media/en/training-seminars/tutorials/mt-094.pdf
8. Altium -- Stripline vs Microstrip: Differences and Routing Guidelines: https://resources.altium.com/p/stripline-vs-microstrip-understanding-their-differences-and-their-pcb-routing-guidelines
9. SMPS.us -- IPC-2152 Trace Width Calculator and Equations: https://www.smps.us/pcb-calculator.html
10. Sierra Circuits -- How to Design a Via with Current Carrying Capacity: https://www.protoexpress.com/blog/how-to-design-via-with-current-carrying-capacity/
11. San Francisco Circuits -- PCB Via Types Guide (8 Types): https://www.sfcircuits.com/pcb-school/pcb-via-types
12. Altium -- Everything You Need to Know About Stitching Vias: https://resources.altium.com/p/everything-you-need-know-about-stitching-vias
13. Sierra Circuits -- Annular Ring Explained by a PCB Manufacturer: https://www.protoexpress.com/blog/dont-let-annular-rings-drive-you-crazy/
14. Altium -- Thermal Relief Design Guide: https://resources.altium.com/p/thermal-relief-design
