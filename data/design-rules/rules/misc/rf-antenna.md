# RF & Antenna Design

> Antenna selection, matching networks, keep-out zones, ground plane sizing, module placement, sub-GHz, GNSS, mmWave.

## Quick Reference

- **PCB trace antenna: free, tunable, but needs ground plane >= lambda/4 on longest edge.** 2.4 GHz IFA: ~15mm clear of ground. 915 MHz monopole: ~45mm clear of ground. Efficiency degrades sharply if ground plane is undersized.
- **Chip antenna: demands exact layout per vendor datasheet.** Johanson specifies >= 2mm from shorter edges, >= 4mm from longer (radiating) edge. Infineon/Cypress AN91445: 0.8mm minimum for over-ground-plane parts like 2450AT42B100E, but 2-3mm gives measurably better return loss. Always include pi-match network for tuning.
- **RF trace: 50 ohm GCPW, no vias, no layer changes.** Route on outer layer with continuous ground plane on adjacent layer. Keep < 20mm total. Via fences on both sides, spaced < lambda/20.
- **Matching network: always include pi-pad footprint even if values are 0-ohm/open.** VNA tuning on prototype is required -- simulation alone is insufficient. Use +/-0.1pF caps and +/-2% inductors (0402 minimum).
- **Module antenna placement: antenna edge overhangs or flush with base board edge.** If antenna cannot overhang, 15mm clearance in all directions on all layers -- no copper, no traces, no components.

## Design Rules

### Antenna Type Selection

| Antenna Type | Board Area | Efficiency | Best For |
|-------------|-----------|------------|----------|
| PCB trace IFA/MIFA | 15-25mm clear zone | 60-80% | Cost-sensitive, board space available |
| PCB meander monopole | 20-45mm clear zone | 50-70% | Sub-GHz, elongated boards |
| Chip antenna | 3-5mm + clearance zone | 40-65% | Space-constrained, multi-band |
| Helical PCB (sub-GHz) | 19x12mm | 65% | Compact 868/915 MHz |
| Wire/whip | External | 85-95% | Maximum range |
| Ceramic patch | 25x25mm (GNSS) | 70-85% | GNSS active antenna |

- **Silicon Labs AN1088 IFA reference: copy geometry exactly -- even 0.5mm changes detune by 50+ MHz.** IFA on 2-layer FR4, 1.6mm thick, ground clearance 5.2mm from feed. Achieves -1.5 dBi peak gain, 72% efficiency. 1" board width is optimized -- wider or narrower shifts resonance significantly.
- **Infineon/Cypress AN91445 MIFA: 7.2 x 11.1mm element, IFA: 4 x 20.5mm element.** Feed trace width = PCB thickness (1.6mm board = 1.6mm feed width). Table in AN91445 maps feed width to PCB thickness for each antenna variant.
- **Meander monopole: reduces length ~40% but narrows bandwidth by half.** Folded structure occupies ~60% of straight monopole area but bandwidth drops from ~90 MHz to ~40 MHz at 868 MHz. Re-matching required for each board variant.
- **Chip antenna selection:** Johanson 2450AT18x100 (2.4 GHz, 0402-size, -1 dBi peak gain, wide bandwidth). Abracon ACAG series (2.4 GHz, multiple sizes). For sub-GHz: Johanson 0868AT43A0020 (868 MHz, requires ground plane >= 50x30mm).
- **Chip antenna feed must be perpendicular to the microstripline direction** per Johanson layout guide. Parallel feed couples to the ground plane edge and shifts impedance.

### Ground Plane Requirements

- **Ground plane is half the antenna.** Monopole and IFA use the ground plane as the other radiating element. Undersized ground shifts resonant frequency, reduces efficiency, and skews radiation pattern.
- **2.4 GHz minimum ground plane: 30x20mm.** Increasing to 40x30mm adds ~1 dB gain. Diminishing returns above 50x40mm.
- **Sub-GHz (868/915 MHz) minimum ground plane: 50x30mm.** lambda/4 at 915 MHz = 82mm -- ground plane longest dimension should approach this. Below 50mm, efficiency drops below 50%.
- **Ground plane must be solid under RF trace and matching network.** No routing, no splits, no slots crossing under the RF path. Ground vias every 5mm minimum, every 2mm near RF traces.
- **Abracon testing: 10% ground plane area reduction from reference design shifted resonant frequency 30-50 MHz and degraded return loss by 3-5 dB.** Ground clearance zone sensitivity is not symmetric -- long (radiating) edge clearance matters 2x more than short edge.

### RF Trace Routing

- **GCPW preferred over microstrip.** Better isolation, less sensitive to board thickness variation. Ground copper on both sides of center conductor with via fences connecting to ground plane below.
- **50 ohm GCPW dimensions (FR4, Er=4.4, 1.6mm board):** 2-layer: trace width ~1.2mm, gap to ground ~0.25mm. 4-layer (0.26mm prepreg): trace width ~0.45mm, gap ~0.64mm. ADI RF layout guide provides impedance table: at h=0.2mm, w=0.3mm, gap=0.15mm gives 50 ohm; at h=1.5mm, w=2.8mm, gap=0.2mm gives 50 ohm. Use impedance calculator with actual stackup -- Er varies 3.8-4.6.
- **No vias in RF trace.** Layer changes add 0.1-0.5nH inductance per via. If unavoidable, use 2+ vias in parallel (cuts inductance ~50%) with largest possible drill diameter.
- **Bends: radius >= 3x trace width.** If 90-degree bend unavoidable, use mitered corner (cut corner at 45 degrees).
- **RF trace length: every 10mm of 50 ohm trace adds ~0.05 dB loss at 2.4 GHz on FR4.** At 5.8 GHz: ~0.12 dB/cm. Keep total RF path < 20mm.
- **Isolation between RF traces:** parallel microstrip coupling reaches -20 dB at 1mm spacing over 10mm length at 2.4 GHz. GCPW with via fences achieves -45 dB isolation minimum.
- **Silicon Labs AN629: via curtain spacing < lambda/10 of the highest harmonic of concern.** At 2.4 GHz (10th harmonic = 24 GHz): via spacing < 1.25mm. At 915 MHz: < 3.3mm. This is more aggressive than most generic guidelines.

### Matching Network

- **Always include a 3-element pi-network footprint** between IC/module and antenna feed, even if initial values are 0-ohm series / open shunt. Every antenna needs tuning on the final board.
- **Component placement: matching network first, then 50 ohm trace to antenna.** Placing match at antenna end means the trace transforms the impedance again -- both IC and antenna end up mismatched.
- **Shunt capacitor grounding: thermal pad with multiple vias directly to ground plane.** Each via adds ~0.1nH. Two vias per shunt cap pad minimum. Use 0201 components to keep matching network compact.
- **Adjacent inductors placed perpendicular to each other reduce magnetic coupling by 20+ dB.** Same orientation causes filter performance degradation. Silicon Labs AN629 explicitly requires this.
- **Keep 0.5mm minimum clearance between matching network pads and ground pour.** Parasitic capacitance from ground pour detunes the match -- especially significant for sub-GHz where component values are already small.
- **Matching network values from reference design are starting points.** Board size, enclosure, nearby components, and copper all shift impedance. Budget for 2-3 VNA tuning iterations.

### Module Placement (ESP32, nRF52, etc.)

- **Antenna end of module must overhang or be flush with base board edge.** Base board copper under the module antenna area couples to the antenna and degrades performance by 3-10 dB.
- **If overhang not possible: 15mm clearance in all directions around antenna.** No copper on any layer, no components, no traces. Cut out base board under antenna if needed.
- **ESP32 specific (Espressif HW design guidelines):** 4-layer preferred. CLC pi-match network using 0201 components between RF pin and antenna. Add 5.6nH shunt inductor as stub for 2nd harmonic suppression. IPEX connector: 1mm keep-out ring around connector pad on all layers.
- **Nordic nRF52 (general PCB guidelines): copy reference design exactly.** Matching network doubles as harmonic filter -- changing values to "improve match" often degrades regulatory compliance. 50 ohm CPWG mandatory from IC to matching network.

### Sub-GHz (LoRa/ISM 868/915 MHz)

- **Semtech SX1261/SX1262: copy reference design RF section exactly -- component values AND layout geometry.** Even trace lengths between components are tuned. Load-pull optimum impedance: Zopt = 11.7 + j4.8 ohm at 915 MHz. CLE (Class-E) matching topology is frequency-band-specific.
- **SX1262 2-layer vs 4-layer:** 2-layer reference uses wider traces and different matching values than 4-layer. Do not mix matching component values across stackup variants.
- **TI DN038 helical PCB antenna: 19x12mm, 65% efficiency at 868 MHz.** Requires 2-component match (1.0pF series cap + 12nH shunt inductor). Bandwidth 40 MHz at VSWR 2. Re-match required if PCB thickness changes from 0.8mm reference.
- **IFA for 915 MHz: ~45mm element length on FR4.** Folded/meander versions reduce to ~25-30mm but with bandwidth tradeoff. Ground plane >= lambda/4 (82mm) on longest axis for full efficiency.
- **Harmonic suppression for regulatory compliance:** FCC Part 15.247 and ETSI EN 300 220 require harmonics < -20 dBc (FCC) or absolute power limits (ETSI). Add LC low-pass filter after matching network. For +20 dBm transmitters (SX1262), shield can may be required over RF section.

### 24 GHz mmWave

- **Patch antenna arrays integrated on PCB.** At 24 GHz, lambda = 12.5mm -- antenna elements are small enough for PCB integration. ADI ADF4159 + ADF5901 + ADF5904 chipset for FMCW radar.
- **Rogers 4003C or similar low-loss substrate required.** FR4 loss tangent (0.02) causes ~3 dB/cm loss at 24 GHz -- unusable for feed networks. RO4003C (tan_d = 0.0027) or RO3003 (tan_d = 0.0013) needed.
- **Feed network symmetry is critical.** Wilkinson dividers for power splitting must have equal-length arms to within 0.1mm. Amplitude and phase imbalance cause beam squint and sidelobe degradation.
- **VCO/PLL phase noise directly sets radar range resolution.** Isolate VCO from digital sections with ground moat and via wall.

### GNSS Antenna Integration

- **Active antenna: bias-tee for LNA power.** 3.3V through 100nH inductor to antenna center conductor. DC blocking cap (100pF-1nF) on receiver side. Verify LNA current draw (10-20mA typical) against inductor current rating.
- **Ground plane sizing for passive GNSS patch: >= 70x70mm.** Below this, RHCP axial ratio degrades, reducing multipath rejection. L-shaped ground plane (GNSS at corner) is acceptable if total area meets minimum.
- **Antenna placement: unobstructed sky view.** No components taller than antenna within 15mm. GPS/GNSS reception through plastic enclosure: add 0.5-1 dB link budget margin for plastic cover.
- GNSS module integration details -> `misc/gnss-integration.md`.

### Bypass and Decoupling for RF ICs

- **ADI RF layout guide: bypass cap SRF must exceed the operating frequency.** A 100nF 0402 ceramic has SRF around 400 MHz -- useless at 2.4 GHz. Use 100pF (SRF ~1.5 GHz) or 10pF (SRF ~5 GHz) for GHz-range bypass. Parallel 100nF + 100pF covers both low and high frequency.
- **IC exposed paddle: minimum 9 ground vias in 3x3 grid directly under the paddle.** ADI recommends via drill 0.3mm, pitch 1mm. Incomplete paddle grounding adds inductance to the die ground -- 1nH shifts the RF match by several dB at 2.4 GHz.

## Common Mistakes

- **Routing digital traces under antenna clearance zone.** Even on inner layers, copper traces couple to the antenna and shift resonance by 50-200 MHz. The antenna clearance zone must be copper-free on ALL layers. Ground plane is required under the RF trace but NOT under the antenna element.
- **Using FR4 Er = 4.4 for all layers.** Outer prepreg layers have Er ~3.8, inner core has Er ~4.2-4.6. Using wrong Er for impedance calculation gives 10-15% trace width error, shifting impedance to 40-45 ohm. Get actual stackup Er from fab house.
- **Ground pour too close to matching network pads.** Parasitic capacitance from ground copper within 0.3mm of shunt component pads shifts the effective match by 5-15%, especially at sub-GHz where component values are already small (0.5-2pF). VNA shows good return loss on bare board, then production boards with tighter ground pour rules fail -> enforce 0.5mm minimum clearance in gerber review.
- **Enclosure effects ignored during antenna design.** Plastic housing detunes antenna by 2-5% (lowers resonant frequency due to increased effective Er). Metal housing requires antenna window or external antenna. Tune matching network with final enclosure in place, not on bare board.
- **Shared ground plane split between analog and RF sections.** Ground plane splits force return currents through narrow bridges, increasing inductance and creating slot antennas. Use solid ground plane everywhere -- isolate with via fences and component placement, not copper cuts.
- **Silicon Labs AN1088: substituting "equivalent" chip antenna for reference IFA without re-matching.** Different antenna types present different impedances -- a chip antenna matched for one board is not interchangeable with an IFA even at the same frequency. Full VNA characterization required.

## Formulas

**Guided wavelength on PCB:**
**Rule of thumb:** 2.4 GHz on FR4: lambda_g ~ 76 mm. 915 MHz: ~160 mm. 868 MHz: ~168 mm.
**Formula:** lambda_g = c / (f * sqrt(Er_eff)), where Er_eff ~ (Er + 1) / 2 for microstrip
**Example:** 2.4 GHz, FR4 Er=4.4 -> Er_eff ~ 2.7 -> lambda_g = 3e8 / (2.4e9 * 1.64) = 76 mm. Quarter-wave = 19 mm.

**Pi-network matching (L-section cascade):**
**Rule of thumb:** Start with reference design values. Adjust by +/-10% per iteration during VNA tuning.
**Formula:** For L-to-high impedance: L_shunt = R_high / (2 * pi * f), C_series = 1 / (2 * pi * f * sqrt(R_high * R_low))
**Example:** Match 25+j30 ohm antenna to 50 ohm at 2.4 GHz: first cancel j30 with series -j30 (2.2pF cap), then L-match remaining 25 ohm to 50 ohm: L=1.3nH shunt, C=1.3pF series. Verify with Smith chart tool.

## Sources

### Related Rules

- `misc/gnss-integration.md` -- GNSS module integration, antenna selection, ground plane sizing, RF path details

### References

1. Infineon/Cypress AN91445 -- Antenna Design and RF Layout Guidelines: https://www.infineon.com/dgdl/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf?fileId=8ac78c8c7cdc391c017d073e054f6227
2. ADI -- PCBs Layout Guidelines for RF & Mixed-Signal: https://www.analog.com/en/resources/technical-articles/pcbs-layout-guidelines-for-rf--mixedsignal.html
3. Nordic -- General PCB Design Guidelines for nRF52 Series: https://devzone.nordicsemi.com/guides/hardware-design-test-and-measuring/b/nrf5x/posts/general-pcb-design-guidelines-for-nrf52-series
4. Espressif ESP32 HW Design Guidelines -- PCB Layout: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/pcb-layout-design.html
5. Johanson -- Chip Antenna Layout for BLE/802.11/Zigbee: https://www.johansontechnology.com/tech-notes/chip-antenna-layout-considerations-for-ble-80211-and-24g-zigbee/
6. Johanson -- Understanding Chip Antennas Handbook: https://www.johansontechnology.com/docs/4469/johanson-understanding-chip-antennas-handbook.pdf
7. Silicon Labs AN1088 -- Designing with Inverted-F 2.4 GHz PCB Antenna: https://www.silabs.com/documents/public/application-notes/an1088-designing-with-pcb-antenna.pdf
8. Abracon -- PCB Trace vs. Chip Antenna Design Considerations: https://abracon.com/downloads/PCB-Trace-vs-Chip-Antenna-PCB-Design-Considerations.pdf
9. Silicon Labs AN629 -- RF IC Layout Design Guide: https://www.silabs.com/documents/public/application-notes/AN629.pdf
10. TI SWRA640H -- CC13xx/CC26xx HW Config and PCB Design: https://www.ti.com/lit/an/swra640h/swra640h.pdf
11. Microchip/Atmel AT09567 -- ISM Band PCB Antenna Reference Design: https://ww1.microchip.com/downloads/en/Appnotes/Atmel-42332-ISM-Band-Antenna-Reference-Design_Application-Note_AT09567.pdf
12. Semtech AN1200.40 -- SX1261/SX1262 Reference Design Explanation: https://cdn-reichelt.de/documents/datenblatt/A200/SX1262REFERENCE.pdf
13. TI SWRA416 -- Miniature Helical PCB Antenna for 868/915 MHz: https://www.ti.com/lit/an/swra416/swra416.pdf
14. ADI -- How to Build a 24 GHz FMCW Radar System: https://www.analog.com/en/resources/technical-articles/how-to-build-a-24-ghz-fmcw-radar-system.html
