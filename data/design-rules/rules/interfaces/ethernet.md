# Ethernet

> PHY selection, magnetics, MDI routing, PoE PD input, EMC optimization for 10/100 and GbE.

## Quick Reference

- **MDI: 100 ohm differential +/-10%; TI's checklist recommends < 50.8mm (2000mil) per trace.** Intra-pair mismatch <= 0.508mm (20mil) for GbE or 1.27mm (50mil) for 10/100 [1, MDI Traces].
- **Center-tap bias is PHY-specific:** LAN8720 ties PHY-side TX/RX taps to VDDA; DP83867 keeps all PHY-side taps separate and capacitively grounded [3, p.4; 12, p.9].
- **Bob Smith for PoE needs DC blocking in each termination branch.** TI's TPS23750 example uses 75 ohm + 10nF per branch and a shared 1nF / 2kV capacitor to its shield plane [10, p.4].
- **LAN8720 VDDCR: 470pF + >= 1uF, bulk ESR <= 1 ohm, no external loads** when the internal regulator is enabled [3, p.7].
- **PoE detection-side capacitance: 120nF maximum, including the VDD-VSS bypass.** Bulk capacitance belongs on VDD-RTN, after the hot-swap switch [6, §§2-3].

## Design Rules

### PHY Selection

- **10/100 Mbps: LAN8720A (QFN-24, RMII).** Internal 1.2V regulator, 25MHz crystal -> 50MHz REFCLK on pin 14. Strap nINTSEL=0 during POR/nRST for REFCLK output mode; this sacrifices the interrupt output [3, pp.7-8,14].
- **W5500 MDI length: < 25mm recommended, 75mm worst case in WIZnet's guide.** With discrete magnetics, transformer-to-RJ45 spacing is > 2.5mm and < 25mm [5, Parts Placement, MDI].
- **Gigabit reference designs:** LAN7800 for USB-to-GbE; DP83867 for a MAC interface. Keep their magnetics bias networks distinct from LAN8720 [8, pp.1-4; 12, pp.2,9].
- **RBIAS resistor: 12.1 kohm 1% to ground (LAN8720A).** Noise on this trace causes failures; use a short, wide connection and route no traces under the resistor [3, p.11; 4, p.9].
- **VDDCR (LAN8720A pin 6): use the regulator-mode-specific connection.** With the internal regulator enabled, do not power other circuits from it; the routing checklist calls for a heavy, wide trace and multiple vias to its capacitors [3, p.7; 4, p.7; 11, pp.11,28].
- **LAN8720 crystal: 25MHz; no external 1 Mohm feedback resistor.** The schematic checklist gives 15-33pF load capacitors as a starting range, then requires frequency/stability validation on the assembled board; do not use a fixed stray-capacitance subtraction for every layout [3, p.8].

### Magnetics

- **Integrated RJ45+magnetics can couple shield-injected noise past the isolation network during ESD/EFT.** TI recommends discrete magnetics and RJ45 connectors as an EMC improvement, not a certification requirement [7, p.35].
- **10/100 magnetics recommendations are PHY-specific.** TI AN-1469 lists Bel Fuse S558-5999-U7 and Pulse H1102; H2019 for PoE; SI-60062-F and J0011D21B as integrated options for its PHYTER family [2, §10, Table 5].
- **Current-mode PHYs DP83822/DP83848: use 1% MDI termination resistors.** TI recommends ferrite filtering of the MDI pull-up supply for EMC; do not transfer this supply connection to a voltage-mode PHY [7, pp.31-32].
- **LAN8720 PHY-side center taps: tie TX and RX together to VDDA, with 22nF to digital ground.** DP83867 instead requires individually isolated PHY-side taps, each decoupled to ground; its reference schematic uses 100nF per tap. Shorting voltage-mode taps increases common-mode noise and crosstalk [3, pp.3-4; 12, p.9, Figure 2-8; 7, p.31].
- **TVS arrays belong on the PHY side of the transformer.** Connector-side common-mode voltage can damage protection intended for PHY-side levels; select the operating/clamping voltage for the PHY. Wurth RD016 uses WE-TVS 824014885; its low cross-line capacitance is not a universal < 0.1pF total-loading requirement [1, ESD Device Selection; 8, pp.7-8].

### MDI Routing

- **49.9 ohm 1% pull-ups on TXP/TXN/RXP/RXN to VDDA are required for LAN8720.** They are not a universal PHY termination network [3, p.2].
- **Same-layer ground clearance: >= 3*w minimum, 5*w preferred** (w = MDI trace width). TI recommends inter-pair spacing >= 0.762mm (30mil); use the actual stackup to obtain the differential impedance [1, MDI Traces, Signal Routing].
- **Wurth RD016's 0.154mm width, 0.125mm gap and 0.2mm prepreg are one board's geometry.** Do not copy those dimensions without checking the stackup [8, pp.9-10].
- **LAN8720 routing keeps the ground reference under PHY-side MDI but clears planes under cable-side MDI.** The plane-clear boundary is usually halfway through the magnetics; preserve this isolation boundary when adding TVS footprints or integrated magnetics [4, pp.2,5].
- **No test points on MDI lines.** Exposed pads increase radiated pickup and emission [7, p.31].

### RMII/MII Interface

- **LAN8720's routing checklist recommends 68 ohm RMII traces; TI's general checklist recommends 50 ohm +/-10% MII traces.** These are device/design recommendations, not one universal IEEE impedance. For PHYTER MII outputs, AN-1469 recommends 50 ohm series resistors; DP83849/DP83640 integrate them [4, p.9; 1, MII Traces; 2, §5.1].
- **LAN8720 RMII: 10 ohm is a starting value, not a required termination.** Validate RXD0, RXD1, RX_ER and CRS_DV in-system. MDIO requires a 1.5 kohm pull-up to VDDIO [3, pp.11-12].
- **LAN8720 REFCLKO timing in REF_CLK Out mode is not RMII-compliant.** Some MACs need 500ps-1ns delay on RXD/CRS_DV; determine any added delay from timing analysis, rather than adding serpentine unconditionally [3, p.8].
- **LAN8720 external 50MHz oscillator: use two source-series branches, initially 33 ohm each, to MAC and PHY.** Place the oscillator approximately midway; the routing checklist recommends branch matching within 2.54mm (100mil), each < 152.4mm (6000mil). Strap nINTSEL=1 for external REFCLK input [3, p.9; 4, p.9].

### Bob Smith Termination

- **Non-PoE LAN8720: each cable-side TX/RX center tap gets 75 ohm to a common node, then one shared 1000pF / 2kV capacitor to chassis.** Do not put these resistors on the PHY-side bias taps [3, p.4].
- **PoE: retain a PoE-compatible AC-coupled termination.** The 10nF series capacitor in each branch of TI's example prevents DC loading between powered pairsets; the shared chassis capacitor alone does not block current between branches [10, p.4, Figure 1-1].
- **For non-PoE 10/100 EFT/CI failures, test removal of termination on unused pairs.** TI identifies it as a common-mode coupling path; this debugging change is not a general instruction to remove PoE terminations [7, §§4.4.3,4.7.3; 6, §2].

### PoE PD Design

- **Bridge selection in TI's PD guide:** discrete diodes are a cost default at 13W; assess diode losses at 25W; 51W TPS23730EVM-093 uses a hybrid bridge. FETs/integrated bridges reduce high-power losses, but are not mandatory solely from the wattage [6, §2].
- **TI's 100V-absolute-maximum PD input example recommends the SMAJ58 family.** The approximately 92V clamp is a pulse-current-dependent value, not a fixed ceiling; verify the chosen TVS and surge current against the exact controller's limits [6, §2, Figure 2-8].
- **DEN on TI PD examples: 24.9 kohm with diode bridges; 25.5-27 kohm with hybrid/integrated rectifiers as needed.** Check the exact PD controller and bridge detection signature instead of applying one value to every PD [6, §2.2, p.7].
- **TI's VDD-RTN bulk-capacitor starting ranges:** 13W: 10-22uF; 25W: 33-47uF; 50W: 68-100uF; 70W: 100-200uF. These are after the hot-swap switch, outside the detection-side 120nF budget. For ceramic banks TI recommends 1 ohm between the bank and RTN for startup [6, §3, Figure 3-5].
- **PD69201 PSE reference design: 1500Vrms isolation from switch/chassis circuitry.** AN3580 recommends 0.381mm (15mil) FR-4 interlayer insulation for hi-pot margin and shows ADuM1251 for host I2C; this is not a universal insulation qualification -> `protection/isolation.md` [9, §§2.1-2.2,4.2,5.1].
- **PSE reference resistor (PD69201): 240 kohm 1% to AGND.** AN3580's minimum port-trace widths depend on copper and layer: 0.381mm (15mil), 2oz external, for 10 degrees C rise; 1.397mm (55mil), 0.5oz internal, is for 20 degrees C rise [9, §§2.6,5.3, pp.4,14].

### EMC

- **Chassis-to-signal clearance differs between guides:** WIZnet recommends > 2.032mm (80mil), while TI SNLA387 gives >= 0.508mm (20mil). Neither replaces the product's isolation requirements [5, Other Considerations; 1, Earth Ground Isolation].
- **LAN8720's checklist uses a 1210 footprint for a configurable chassis-to-digital-ground link.** TI recommends R||C for ESD/EFT, away from signal/clock traces and near the supply; SNLA387 recommends >= 1 Mohm. Select the capacitor voltage rating for the required isolation rather than copying a universal R/C network [3, p.16; 1, Earth Ground Isolation; 7, pp.32,36].
- **Turn off unused CLK_OUT and TX/RX activity LED modes during radiated-emissions diagnosis.** TI identifies both as extra emission sources; clock-output reset defaults depend on the PHY [7, §3.3.2].
- **Additional PHY-side CMC is an ESD/EFT tuning option.** It filters noise coupled into the PHY-to-transformer section; validate it with the selected PHY/magnetics [7, p.32].
- **RJ45-integrated LED wiring is an ESD/EFT injection path into the PHY.** TI recommends avoiding integrated LEDs when optimizing immunity [7, p.36].

## Common Mistakes

- **Using an RC-only LAN8720 reset.** Its checklist calls for a hardware reset after power-up and recommends a reset generator or controllable push-pull output for a sharp monotonic release; apply the current datasheet's reset timing [3, p.16].
- **Copying optocoupler CTR suffixes across manufacturers.** TI's PD feedback example targets 80-160% CTR rather than a broad 80-600% bin; check the actual part's CTR bin and loop compensation, not a universal "-A" suffix [6, §3.4, p.26].
- **Connector-ground copper/vias near MDI can inject ESD/EFT current between the pair traces.** TI distinguishes this connector-side noise path from the PHY-side reference plane; preserve the isolation-zone clearances [7, p.36].
- **Adding a second 100nF capacitor directly across VDD-VSS.** Two nominal 100nF capacitors already total 200nF, above the 120nF detection-side maximum; include tolerances and all pre-switch filtering in that budget [6, §2].

## Sources

### Related Rules

- `protection/isolation.md` -- PoE isolation design and I2C isolation across power domains

### References

1. TI SNLA387 (June 2021) -- Ethernet PHY PCB Design Layout Checklist: https://www.ti.com/document-viewer/lit/html/SNLA387
2. TI SNLA079D (AN-1469, April 2013) -- PHYTER Design and Layout Guide: https://www.ti.com/lit/pdf/snla079
3. Microchip SC471228 Rev D (July 2012) -- LAN8720 QFN Schematic Checklist: https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/SupportingCollateral/LAN8720AQFNRevDSchematicChecklist.pdf
4. Microchip RC614946 Rev A (July 2012) -- LAN8720 QFN Routing Checklist: https://ww1.microchip.com/downloads/en/DeviceDoc/LAN8720_QFN_Rev_A_Routing_Checklist.pdf
5. WIZnet -- Hardware Design Guide (HTML, no revision stated; local snapshot February 2026): https://docs.wiznet.io/Design-Guide/hardware_design_guide
6. TI SLVAF59 (April 2021) -- PoE PD Schematic Review Guidelines: https://www.ti.com/document-viewer/lit/html/SLVAF59
7. TI SNLA466A (October 2024) -- Optimizing EMC Performance in Industrial Ethernet Applications: https://www.ti.com/lit/pdf/snla466
8. Wurth Elektronik RD016a (September 2022) -- Gigabit-Ethernet Front End Reference Design: https://www.we-online.com/components/media/o721295v410%20RD016a%20EN.pdf
9. Microchip AN3580 (DS00003580E) -- Designing 1-port PoE System Using PD69201: https://ww1.microchip.com/downloads/aemDocuments/documents/POE/ApplicationNotes/ApplicationNotes/AN3580-Designing_1-port_PoE_System_Using_PD69201.pdf
10. TI SLUA469 (July 2008), p.4 -- Practical Guidelines to Designing an EMI Compliant PoE Powered Device with Isolated Flyback: https://www.ti.com/lit/pdf/slua469
11. Microchip LAN8720A/LAN8720AI datasheet (DS00002165B, 2016): https://ww1.microchip.com/downloads/en/DeviceDoc/00002165B.pdf
12. TI SNLA246D (May 2026), p.9 -- DP83867 Troubleshooting Guide: https://www.ti.com/lit/pdf/snla246
