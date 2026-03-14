# Ethernet

> PHY selection, magnetics, MDI routing, PoE PD input, EMC optimization for 10/100 and GbE.

## Quick Reference

- **MDI traces: 100 ohm differential, < 50mm total, matched within 0.5mm (GbE) or 1.3mm (10/100).** Route on component layer with solid ground on L2. No vias on MDI if possible.
- **Bob Smith: 75 ohm + 1000 pF / 2 kV cap to chassis ground per pair center tap.** Not used in PoE -- shorts power to chassis through low-impedance AC path.
- **Chassis-to-signal ground: >= 2mm (80 mil) separation on all layers.** Connect with 1 Mohm || 1-2 nF / 2 kV cap. Use 1206 footprint -- swap component during EMC testing.
- **No metal under magnetics on any layer.** Clear power and ground planes under magnetics and between magnetics and RJ45. Component-to-void-edge: >= 0.5mm (20 mil).
- **PoE input capacitance: 120 nF max between VDD and VSS.** IEEE 802.3 detection is impedance-based -- exceeding 120 nF prevents detection. The 0.1 uF bypass cap counts toward this limit.

## Design Rules

### PHY Selection

- **10/100 Mbps: LAN8720A (QFN-24, RMII) is the de facto standard.** Internal 1.2 V regulator, 25 MHz crystal -> internal 50 MHz REFCLK on pin 14. Use nINTSEL=0 for REFCLK output mode. Alternative: DP83848 family for MII.
- **SPI-to-Ethernet: W5500.** Hardwired TCP/IP stack, no PHY expertise needed. Transformer-to-RJ45 distance < 25mm. MDI max routing 75mm worst case.
- **Gigabit: LAN7800 (USB-to-GbE), DP83867 (RGMII), KSZ9031 (RGMII).** All four differential pairs active simultaneously -- far more layout-critical than 10/100.
- **RBIAS resistor: 12.1 kohm 1% to ground (LAN8720A).** Place close to PHY. Noise on this trace causes link failures -- no traces routed underneath, bury in inner layer if possible. Use 0805 or smaller footprint to reduce noise pickup.
- **VDDCR (1.2 V core, LAN8720A pin 6): 470 pF + 1 uF low-ESR ceramic, no other loads.** Route with heavy wide trace and multiple vias to decoupling. This supply is internal logic only -- do not power external circuits.
- **Crystal: 25 MHz, +/-50 ppm, AT-cut, parallel resonance.** Never share between PHY and another device. No external 1 Mohm feedback resistor needed (integrated in LAN8720A). Load caps: 2 * crystal load spec - 7 pF as starting point.

### Magnetics

- **Integrated RJ45+magnetics for simple designs:** fewer solder joints, better EMC shielding. Disadvantage: smaller cores degrade crosstalk and CMRR, harder to rework. During ESD/EFT testing, noise injected onto RJ45 shield can bypass isolation network and couple directly to system ground.
- **Discrete magnetics for better EMC and higher isolation (up to 6 kV).** Required when PHY is more than a few cm from connector, or for industrial EMC certification. Discrete RJ45 + magnetics reduces injection area during ESD events, improving transformer performance.
- **10/100 discrete: Bel Fuse S558-5999-U7, Pulse H1102.** PoE: Pulse H2019. Integrated: Bel Fuse SI-60062-F, Pulse J0011D21B.
- **GbE discrete: Wurth 7499011222A (4-port, integrated CMC+transformer).** Verify return loss flatness within 3 dB up to 40-50 MHz -- non-flat return loss indicates impedance mismatch degrading link margin. Magnetics should have >= 2 dB return loss margin versus IEEE 802.3 spec at MDI.
- **Voltage-mode PHYs (most modern designs) generate common-mode EMI.** Use magnetics with 2-wire or 3-wire CMC. Current-mode PHYs (DP83822, DP83848) generate differential-mode EMI -- require 1% termination resistors on MDI and ferrite beads on the pull-up resistors to VDDA.
- **No shorted center taps on voltage-mode drivers.** Shorted center taps increase common-mode noise, crosstalk between TX and RX, and affect TX bias voltage. Also prevents current leakage during Auto-MDIX.
- **TVS diode arrays on secondary (PHY) side of transformer.** Transients appear as common-mode after transformer. Use arrays with < 0.1 pF parasitic capacitance (Wurth WE-TVS 824014885, Ccross = 0.08 pF). Connect directly into signal path with low-impedance ground -- parasitic inductance in TVS ground negates protection.

### MDI Routing

- **49.9 ohm 1% pull-up resistors on TXP/TXN/RXP/RXN to VDDA (LAN8720A).** Place resistors and 0.1 uF decoupling cap close to PHY pins, via directly to VDD plane.
- **Same-layer ground plane spacing from MDI traces: >= 3*w minimum, 5*w preferred** (w = trace width). Closer ground plane capacitively shifts impedance.
- **Inter-pair spacing: >= 0.76mm (30 mil).** Intra-pair match within 0.5mm for GbE, 1.3mm for 10/100.
- **GbE trace dimensions (Wurth RD016): width 0.154mm, spacing 0.125mm, prepreg 0.2mm** for 100 ohm differential impedance. Inter-pair offset < 1.3mm over full length. Smallest trace spacing gives highest coupling -- adjust width to achieve target impedance.
- **W5500 MDI: max 25mm recommended, 75mm worst case.** Trace width 6-12 mil, inter-signal distance >= 20 mil (30 mil preferred). No vias or layer changes on TX/RX.
- **Signal vias: place ground return vias adjacent to every signal via.** If a pair must change layers, verify continuous reference plane on both sides.
- **No test points on MDI lines.** Exposed pads act as antennas, degrading both EMC emission and immunity.

### RMII/MII Interface

- **MII: 68 ohm impedance per IEEE spec.** Traces < 150mm (6000 mil), matched within 50mm. 50 ohm series termination on all MII outputs (RXCLK, TXCLK, RX data). DP83849/DP83640 have integrated 50 ohm terminations -- external resistors unnecessary.
- **RMII: 68 ohm impedance.** 10 ohm series termination on RXD0, RXD1, RX_ER, CRS_DV outputs. MDIO requires 1.5 kohm pull-up to VDDIO.
- **REFCLKO timing in REF_CLK Out mode is not RMII-compliant.** Some MACs need 500 ps - 1 ns delay on RXD/CRS_DV. Fix: serpentine delay on RX signals from PHY to MAC. Perform timing analysis of MAC and LAN8720A before committing to this clock mode.
- **50 MHz REFCLK distribution:** when using external oscillator for RMII, place oscillator midway between PHY and MAC. Series 33 ohm termination at oscillator output, matched clock trace lengths within 2.5mm.

### Bob Smith Termination

- **75 ohm per pair center tap on cable side, through 1000 pF / 2 kV cap to chassis ground.** Single shared cap between TX and RX center taps is acceptable.
- **Unused RJ45 pairs (pins 4-5, 7-8 for 10/100): each pair terminated 75 ohm to chassis through cap.** Alternative: two 49.9 ohm in parallel at center tap (24.95 ohm) + 49.9 ohm series = 74.9 ohm equivalent.
- **Remove Bob Smith on unused pairs for EFT/CI testing.** Having Bob Smith on unused pairs provides a low-impedance path to earth ground, causing higher common-mode noise flow on unused pairs that couples to used pairs. On used pairs, the CMC already provides high common-mode impedance.

### PoE PD Design

- **Input diode bridge by power level:** 13 W -> discrete diode bridge (lowest cost). 25 W -> hybrid option. 51 W+ -> FET bridge required (thermal). 71 W -> integrated solution optimal.
- **TVS on VDD-VSS: SMAJ58A (58 V).** Clamps at ~92 V. Do NOT use SMAJ64A or higher -- 98 V clamp is too close to 100 V abs max. Field damage observed with higher ratings.
- **Detection resistor (DEN): 24.9 kohm for diode bridge.** 25.5-27 kohm for hybrid/integrated FET rectifier (lower MOSFET drop requires higher resistance to maintain detection signature).
- **Input bulk capacitor by power level:** 13 W: 10-22 uF, 25 W: 33-47 uF, 50 W: 68-100 uF, 70 W: 100-200 uF. Electrolytic preferred for ESR. If ceramic, add 1 ohm series resistor for startup inrush limiting.
- **PSE isolation: 1500 Vrms between PoE circuitry and switch/chassis ground.** For multi-layer FR-4, minimum 15 mil isolation thickness between adjacent layers for hi-pot margin. I2C to host must cross through opto-isolator or digital isolator (ADUM1251 for I2C). Isolation design details -> `protection/isolation.md`.
- **PSE reference resistor (PD69201): 240 kohm 1% to AGND.** Connect directly to exposed pad GND. Port output traces: 45 mil wide for max current, minimum 15 mil (2 oz external) to 55 mil (0.5 oz internal) for 10 degrees C rise.

### EMC

- **RJ45 shield: if no earth ground, connect to largest available conductive surface** (metal enclosure). Lack of a low-impedance chassis path is the #1 cause of Ethernet radiated emission failures in plastic-enclosure products.
- **Chassis-to-signal ground options (1206 footprint for swapping during EMC test):** (a) open for fully isolated planes, (b) 0 ohm short, (c) 1-2 nF / 2 kV cap, (d) ferrite bead. R||C recommended for ESD/EFT: capacitor limits noise flow while preventing ground charging; resistor discharges cap between ESD/EFT events. Place R||C connection away from signal and clock traces, near power supply.
- **Turn off CLK_OUT pins and TX/RX activity LED modes during RE testing.** TI PHYs default-enable 25/50 MHz clock output on unused pins. LED blinking in TX/RX activity mode adds low-frequency radiated emissions.
- **Additional CMC near PHY side** (beyond the one in magnetics) filters noise picked up from ground bounce and surrounding traces between PHY and transformer. Improves ESD/EFT margin.
- **Crystal ground isolation:** keep crystal load cap grounds on a local ground island, separate from power and MDI ground. Connect island to main ground with vias to prevent HF ringing on floating ground. Use C0G/NP0 for crystal load caps. Small footprint reduces emission.
- **RJ45 modules with integrated LEDs degrade ESD/EFT performance.** EMI noise flows through LED lines directly into PHY. Use discrete LED connections or modules without LEDs for industrial EMC.

## Common Mistakes

- **Using RC circuit for PHY reset instead of proper reset IC.** LAN8720A requires monotonic, sharp low-to-high transition on nRST. RC circuits produce slow rise times that fail to latch strap pins correctly. Fix: push-pull reset generator or GPIO reset with sharp edges. Not open-drain -- must be push-pull for monotonic rise.
- **Optocoupler CTR variation kills PoE feedback loop.** CTR range of 80-600% (-G suffix) causes some boards to work and others to oscillate. Fix: always use -A suffix (80-160% CTR). The -G part is cheaper because it's untested over the full range. Verify CTR suffix before production.
- **Copper fill encroaches on MDI microstrip.** Ground polygon pour within 3*w of 50 ohm microstrip detunes impedance. Vias in connector ground area near MDI lines create paths for ESD/EFT noise current to flow between MDI lines. Fix: >= 3*w clearance, no vias or polygon pours near MDI on connector ground layer.
- **Bob Smith termination left populated on PoE design.** Bob Smith shorts center taps (carrying PoE power) to chassis ground through low-impedance AC path. Also degrades EFT/CI performance even on non-PoE designs by providing a noise coupling path on unused pairs.
- **VDD-VSS bypass cap exceeds PoE detection budget.** The 0.1 uF bypass cap on VDD-VSS counts toward the 120 nF max. Adding a second 0.1 uF input filter cap prevents PSE detection entirely. Fix: use smaller filter caps and verify total is < 120 nF.

## Formulas

**Bob Smith termination impedance:**
**Rule of thumb:** 75 ohm per pair, ~145 ohm effective per wire pair to chassis.
**Formula:** Z_BS = (R_pair / 2) + R_series, where R_pair = 49.9 ohm per wire, two in parallel at center tap
**Example:** Pins 4+5: two 49.9 ohm in parallel (24.95 ohm) + 49.9 ohm series = 74.9 ohm -> use single 75 ohm for lower component count.

**Length-matching skew budget:**
**Rule of thumb:** 1 mm offset = ~7 ps skew on FR-4.
**Example:** 1.3 mm inter-pair offset at ~146 mm/ns propagation (FR-4, epsilon_r ~ 4.2) = 8.9 ps skew.

## Sources

### Related Rules

- `protection/isolation.md` -- PoE isolation design and I2C isolation across power domains

### References

1. TI SNLA387 -- Ethernet PHY Design Checklist: https://www.ti.com/document-viewer/lit/html/SNLA387
2. TI SNLA079 (AN-1469) -- PHYTER Design and Layout Guide: https://www.ti.com/lit/pdf/snla079
3. Microchip -- LAN8720A QFN Schematic Checklist: https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/SupportingCollateral/LAN8720AQFNRevDSchematicChecklist.pdf
4. Microchip -- LAN8720 QFN Routing Checklist: https://ww1.microchip.com/downloads/en/DeviceDoc/LAN8720_QFN_Rev_A_Routing_Checklist.pdf
5. WIZnet -- W5500 Hardware Design Guide: https://docs.wiznet.io/Design-Guide/hardware_design_guide
6. TI SLVAF59 -- PoE PD Schematic Review Guidelines: https://www.ti.com/document-viewer/lit/html/SLVAF59
7. TI SNLA466 -- Optimizing EMC Performance in Industrial Ethernet Applications: https://www.ti.com/document-viewer/lit/html/SNLA466
8. Embedded Hardware Design -- Selecting the Right Ethernet Magnetics: https://embeddedhardwaredesign.com/selecting-the-right-ethernet-magnetics/
9. Wurth Elektronik RD016 -- Gigabit-Ethernet Front End Reference Design: https://www.we-online.com/components/media/o721295v410%20RD016a%20EN.pdf
10. Microchip AN3580 -- Designing 1-port PoE System Using PD69201 (PSE): https://ww1.microchip.com/downloads/aemDocuments/documents/POE/ApplicationNotes/ApplicationNotes/AN3580-Designing_1-port_PoE_System_Using_PD69201.pdf
