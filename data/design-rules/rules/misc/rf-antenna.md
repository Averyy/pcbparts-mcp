# RF & Antenna Design

> Antenna selection, matching networks, keep-out zones, ground plane sizing, module placement, sub-GHz, GNSS, mmWave.

## Quick Reference

- **PCB antenna dimensions are reference-design-specific:** AN91445 MIFA: 7.2 * 11.1mm; IFA: 4 * 20.5mm on the documented 1.6mm FR4 board. These are element dimensions, not universal clearance zones [1, pp.10, 15].
- **Chip antenna clearance is part- and orientation-specific.** AN91445 gives 0.8mm minimum antenna-edge-to-ground clearance for 2450AT42B100E, with better return loss at 2-3mm [1, pp.17-18].
- **ESP32 RF trace: outer layer, no vias or layer changes, continuous adjacent ground.** Calculate the 50 ohm geometry for the actual stackup [4, RF].
- **Reserve antenna tuning footprints:** AN1088 recommends a 3-element pi-network for its IFA; Johanson 2450AT18B0100001E specifies a T-network. Tune on the final board [7, p.6; 13, p.3].
- **ESP32 module: place the PCB antenna outside the base board, feed point near its edge.** Otherwise provide >= 15mm clearance in all directions around the antenna area, with no copper, routing, or components [4, Positioning a Module on a Base Board].

## Design Rules

### Antenna Type Selection

- **Silicon Labs AN1088 IFA: copy the reference geometry and stackup, then tune for the application board.** Its legacy test designs are four-layer boards, 1.575mm (62mil) or 0.8mm thick, optimized for a 25.4mm (1in) board width. Changing the ground-plane size detunes the match [7, pp.2-6].
- **AN91445 antenna feed width depends on separation to the RF ground layer and coplanar geometry.** Tables 2 and 4 use Er = 4.3 and give W = 1.651mm (65mil) for 1.524mm (60mil) separation; calculate width for the actual stackup and gap [1, pp.11, 16].
- **Chip antenna selection:** Johanson 2450AT18B0100001E (legacy 2450AT18B100): 2.4-2.5 GHz, EIA 1206, 3.2 * 1.6 * 1.3mm, typical peak gain 1.5 dBi at 25 degrees C on evaluation board 2450AT18B0100001CE1. Abracon ACAG includes 2.4 GHz parts such as ACAG0201-2450-T. For 868 MHz: Johanson 0868AT43A0020001E (legacy 0868AT43A0020), 858-878 MHz; reproduce the ground and clearance geometry of its specified mounting configuration [13, pp.1-3; 8, p.4; 14, pp.1-4].
- **Johanson's 2450AT45A100 horizontal-mount example needs > 2mm ground clearance at the short edges and > 4mm at the long edge facing ground.** Its alternate horizontal mounting permits > 1mm at the short end nearest ground; these are layout-specific dimensions [5, guideline 4].
- **The feeder into the antenna's microstrip must be perpendicular to that microstrip** in Johanson's layout example, so the feeder does not become part of the resonant system. This applies to the coaxial/stripline feeder into the microstrip [5, guideline 5].

### Ground Plane Requirements

- **Use the antenna vendor's reference ground geometry.** Abracon's ground-length comparison is for ACAR4008-S698; changing ground length changes efficiency, with dependence on the operating band [8, p.5].
- **For nRF52, keep the RF reference ground solid and free of routing beneath the RF path.** On boards with more than two layers, Nordic also specifies inner-layer keep-outs below the RF path to reduce stray capacitance; preserve the reference ground when reproducing that stackup. Stitch larger ground areas at least every 5mm and place vias beside the RF path [3, Typical mistakes; Ground planes].

### RF Trace Routing

- **GCPW preferred over microstrip for isolation and reduced sensitivity to PCB thickness variation.** Ground copper on both sides of the center conductor needs via fences connecting to the ground plane below [2, Coplanar Waveguide (Grounded); 9, p.9].
- **Calculated GCPW examples (FR4, unmasked, approximate impedance from a 2-D field solve; closed-form conductor-backed CPW models with and without the copper-thickness correction agree within about 4 ohm):** 2-layer (1.5mm to the bottom ground, Er 4.4-4.5, 0.035mm copper): trace 1.2mm, gap 0.25mm = 50 ohm. 4-layer (0.26mm to reference ground, Er 4.4, 0.018mm copper): trace 0.45mm, gap 0.64mm = 51 ohm. AN629 Table 1 gives reference geometries with Er 4.6, copper 0.018-0.035mm, W = 1.26mm / 0.45mm at those respective heights and gaps; the preceding values are calculated examples, not ADI table entries [9, p.9].
- **Include solder mask in the impedance calculation.** In the 1.2/0.25mm example, 25um of mask takes about 3 ohm off (about 47 ohm); the shift depends on mask properties. A 2.8mm trace is approximately the plain-microstrip 50 ohm width on 1.5mm FR4; with coplanar ground 0.2mm away it is 35 ohm in the 2-D field-solve example. Recalculate for the actual dielectric, copper, and mask stackup [2, Characteristic Impedance; 9, p.9, reference geometry].
- **If an RF layer transition is unavoidable, ADI recommends >= 2 parallel signal vias and the largest diameter compatible with the trace width.** ADI estimates a pair halves transition inductance [2, Layer Changes for Transmission Lines].
- **Bends: radius >= 3 * trace width.** If a curved bend is impossible, use a compensated mitered right-angle bend; determine the miter from the geometry [2, Transmission Line Bends and Corner Compensation].
- **Isolation between RF traces:** GCPW with via fences isolates best, but ADI puts the practical limit on a small PCB at about -45 dB between RF lines: don't budget for more [2, Signal Line Isolation].
- **Silicon Labs AN629 via curtain: spacing < lambda/10 at the 10th harmonic.** This recommendation covers the PCB edges and internal ground-pour edges of its Si446x layouts; calculate pitch below [9, p.3].

### Matching Network

- **Separate radio matching from antenna matching.** Put the chip match at the RF pin and the antenna tuning network near the antenna; the intervening transmission line connects their 50 ohm reference points. Espressif explicitly recommends an additional antenna CLC near the PCB antenna [3, RF path; 4, RF].
- **Shunt capacitor grounding: ADI recommends >= 2 grounding vias per component.** For nRF52 QFN radio matching, the shunt capacitor nearest ANT returns through the nearest VSS pin as shown in the reference layout; preserve that harmonic-filtering path [2, Bypass Capacitor Layout Considerations; 3, Matching the radio to 50 ohms].
- **For AN629's Si446x matching networks, keep >= 0.5mm between traces/pads and adjacent ground pour.** If space allows, place nearby TX inductors perpendicular to each other, and the RX shunt inductor perpendicular to nearby TX inductors, to reduce detuning and coupling [9, p.6].
- **Matching network values from the reference design are starting points.** Board size, enclosure, nearby components, and copper shift impedance. Measure antenna S11 and tune with the final enclosure and nearby objects in place [5, matching procedure; 7, p.6].

### Module Placement (ESP32, nRF52, etc.)

- **If an ESP32 module antenna cannot overhang, cut away the base board beneath it where possible.** The clearance rule above applies to the antenna area; validate throughput and range in the assembled product, including its housing [4, Positioning a Module on a Base Board].
- **ESP32 specific (Espressif HW design guidelines):** Four-layer preferred. CLC pi-match network of 0201 parts close to the RF pin, the two capacitors not facing the same way. For the 2nd harmonic, a stub trace on the ground pad of the first grounding capacitor at the chip: 0.381mm (15mil long, 100 ohm +/-10%); connect the stub via to layer 3 and keep layers 1 and 2 clear around it as shown in the reference. Not needed with 0402 or larger parts. IPEX connector: keep all layers clear under the connector [4, General Principles; RF].
- **Nordic nRF52: copy radio matching values, geometry, placement, and trace lengths from the reference design.** The chip match also suppresses 2nd and 3rd harmonics; tuning must measure both fundamental output power and harmonics. The 50 ohm coplanar line belongs after the chip match, at reference point B toward the antenna network [3, RF path; Matching network; Not having a 50 ohms coplanar waveguide].

### Sub-GHz (LoRa/ISM 868/915 MHz)

- **Semtech SX1261/SX1262: select the reference design for the device, band, power, and stackup.** AN1200.40 compares two-layer SX1261 PCB_E406V03A with four-layer SX1262 PCB_E428V03A/PCB_E449V01A [10, pp.5, 7, 9-13].
- **Zopt = 11.7 + j4.8 ohm at 915 MHz is Semtech's SX1261 load-pull example at the RFO pad, producing 14.6 dBm there to target +14 dBm after matching/filter/switch losses.** Semtech warns that the illustrated load-pull data and matching values are not necessarily the latest for each reference design [10, pp.17-19].
- **TI DN038 helical PCB antenna: Table 1 gives 19 * 12mm geometry on the 0.8mm CC110L EM reference board.** At 868 MHz its demonstrated match uses 1.0pF series + 12nH shunt, with 40 MHz bandwidth at VSWR 2 and 65.55% measured efficiency on the TRXEB platform. Recalculate the match when PCB thickness changes [11, pp.3-7].
- **Treat matching, harmonic filtering, and the RF switch as one network.** In Semtech's SX1261/2 design, the second-harmonic notch and higher-order low-pass stages contribute to the PA load; add the switch and repeat measurements before tuning the antenna network [10, pp.17, 20].

### 24 GHz mmWave

- **ADI ADF4159 + ADF5901 + ADF5904 support the documented 24 GHz FMCW radar with PCB patch antennas.** ADF4159's input limit is 13 GHz, so the ADF5901 VCO divide-by-2 output supplies PLL feedback [12, Ramp Generation; Transmit Stage; Antenna Design].
- **For low-loss feed networks, RO4003C and RO3003 are material options.** Rogers gives typical tan_d = 0.0027 for RO4003C and 0.0010 for RO3003, both at 10 GHz and 23 degrees C; use loss data at the operating frequency when calculating feed loss [15, p.3; 16, p.2].

### GNSS Antenna Integration

- GNSS bias-tee component selection, patch ground-plane sizing, and enclosure effects -> `misc/gnss-integration.md`.

### Bypass and Decoupling for RF ICs

- **ADI RF layout guide: select RF bypass capacitors using the manufacturer's SRF.** ADI's illustrative 0402 SRFs: 2pF 4 GHz, 20pF 2.5 GHz, 100pF 800 MHz, 1000pF 250 MHz, 1uF 60 MHz; above its SRF a cap is inductive. In that table, 20pF covers 2.4 GHz; 100pF and 100nF are both inductive at 2.4 GHz for comparable package parasitics, so verify the actual part rather than choosing by capacitance alone. Parallel capacitors of increasing value provide broadband bypass [2, Selection of Decoupling or Bypass Capacitors, Table 2].
- **RF IC exposed paddle: use the device reference footprint's via array.** AN629's Si446x reference uses 9 vias of 0.305mm (12mil) diameter; ADI illustrates a 5 * 5 array and recommends as many plated through-vias as the layout allows [9, p.6; 2, IC Ground Plane (Paddle)].

## Common Mistakes

- **Treating all chip antennas as ground-free or over-ground parts.** Johanson's specified no-ground region extends through every PCB layer; its separately designed over-ground-plane antennas require ground beneath them. Use the exact part's mounting drawing before assigning copper keep-outs [6, pp.6-7].
- **Using one FR4 Er for every layer.** ADI gives example values of 4.2 for core and 3.8 for outer prepreg; obtain the layer-specific dielectric properties before fixing RF trace geometry [2, Characteristic Impedance].
- **Ground-plane splits used to isolate RF circuitry.** In AN629's Si446x layouts, keep an unobstructed bottom-ground return between the TX low-pass/matching-network ground vias and the RFIC paddle ground vias; fill gaps with ground and stitch to the other ground layers [9, p.7].

## Formulas

**Rule of thumb:** AN629 requires via-curtain pitch below one tenth of the free-space wavelength at the 10th harmonic [9, p.3].
**Formula:** pitch < c / (10 * 10 * f_carrier), with c = 299792458 m/s.
**Example:** 915 MHz carrier -> pitch < 299792458 / (100 * 915e6) = 0.0032764m = 3.276mm. This is the AN629 edge-radiation criterion.

## Sources

### Related Rules

- `misc/gnss-integration.md` -- GNSS module integration, antenna selection, ground plane sizing, RF path details

### References

1. Infineon/Cypress AN91445, document 001-91445 Rev. *H -- Antenna Design and RF Layout Guidelines: https://www.infineon.com/dgdl/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf?fileId=8ac78c8c7cdc391c017d073e054f6227
2. ADI -- PCBs Layout Guidelines for RF & Mixed-Signal (unpaginated web article, sections and Tables 1-2): https://www.analog.com/en/resources/technical-articles/pcbs-layout-guidelines-for-rf--mixedsignal.html
3. Nordic -- General PCB Design Guidelines for nRF52 Series (unpaginated web guide): https://devzone.nordicsemi.com/guides/hardware-design-test-and-measuring/b/nrf5x/posts/general-pcb-design-guidelines-for-nrf52-series
4. Espressif -- ESP32 Hardware Design Guidelines, PCB Layout Design (web edition, RF and module-positioning sections): https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/pcb-layout-design.html
5. Johanson -- Chip Antenna Layout for BLE/802.11/Zigbee (unpaginated web note, guidelines 1-5): https://www.johansontechnology.com/tech-notes/chip-antenna-layout-considerations-for-ble-80211-and-24g-zigbee/
6. Johanson -- Understanding Chip Antennas Handbook (unversioned edition), pp.6-7: https://www.johansontechnology.com/docs/4469/johanson-understanding-chip-antennas-handbook.pdf
7. Silicon Labs AN1088 Rev. 0.1 -- Designing with an Inverted-F 2.4 GHz PCB Antenna: https://www.silabs.com/documents/public/application-notes/an1088-designing-with-pcb-antenna.pdf
8. Abracon (December 19, 2019) -- PCB Trace vs. Chip Antenna Design Considerations: https://abracon.com/downloads/PCB-Trace-vs-Chip-Antenna-PCB-Design-Considerations.pdf
9. Silicon Labs AN629 Rev. 0.3 (2014) -- RF IC Layout Design Guide: https://www.silabs.com/documents/public/application-notes/AN629.pdf
10. Semtech AN1200.40 Rev. 1.1 (May 2018) -- SX1261/SX1262 Reference Design Explanation: https://cdn-reichelt.de/documents/datenblatt/A200/SX1262REFERENCE.pdf
11. TI DN038 / SWRA416 (November 27, 2012) -- Miniature Helical PCB Antenna for 868/915 MHz: https://www.ti.com/lit/an/swra416/swra416.pdf
12. ADI -- How to Build a 24 GHz FMCW Radar System (unpaginated web article): https://www.analog.com/en/resources/technical-articles/how-to-build-a-24-ghz-fmcw-radar-system.html
13. Johanson 2450AT18B0100001E datasheet, Doc# 36S0021A Rev. 5.0 (2024): https://www.johansontechnology.com/docs/3770/Antenna-2450AT18B0100001E-Rev5.0.pdf
14. Johanson 0868AT43A0020001E datasheet, Rev. 2.0 (2023): https://www.johansontechnology.com/docs/4384/Antenna-0868AT43A0020001E-2.0.pdf
15. Rogers RO4000 Series datasheet, Publication 92-004, revised 080322: https://www.rogerscorp.com/-/media/project/rogerscorp/documents/advanced-electronics-solutions/english/data-sheets/ro4000-laminates-ro4003c-and-ro4350b---data-sheet.pdf
16. Rogers RO3000 Series datasheet, Publication 92-130, revised 013024: https://www.rogerscorp.com/-/media/project/rogerscorp/documents/advanced-electronics-solutions/english/data-sheets/ro3000-laminate-data-sheet-ro3003----ro3006----ro3010----ro3035.pdf
