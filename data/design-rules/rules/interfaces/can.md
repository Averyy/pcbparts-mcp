# CAN Bus

> Physical layer design: transceiver selection, termination, CMC flyback hazard, ESD protection, isolated CAN.

## Quick Reference

- **Split termination: 2x 60 ohm (1%) + 4.7 nF to GND.** Reduces CM emissions >2x (344 mV -> 138 mV peak-to-peak in TI measurements). Resistor mismatch >1% degrades CM rejection ~10 dB.
- **CMC flyback kills transceivers during DC bus shorts.** Bifilar I-bar CMCs generate 65-70V transients -- exceeds +/-58V abs max. Place TVS between CMC and transceiver, not at connector.
- **ESD: ESD2CAN24-Q1 (TI, 24V VRWM, 30 kV, 3 pF, SOT-23).** Bidirectional. Keep total parasitic capacitance <15 pF per line. 24V VRWM covers double-battery jumpstart scenario (12V systems).
- **3.3V and 5V transceivers interoperate without level translation.** Differential threshold is the same (>=1.5V). Recessive CM differs by ~0.2V (2.3V vs 2.5V) -- within receiver tolerance.
- **Bus length rule of thumb: Rate(Mbps) * Length(m) <= 50.** 40 m at 1 Mbps, 500 m at 100 kbps, 1000 m at 50 kbps.

## Design Rules

### Transceiver Selection

- **3.3V CAN FD (automotive): TCAN3404-Q1 (TI).** Passes IEC 62228-3:2019 under both homogeneous and heterogeneous network conditions -- legacy 3.3V parts (SN65HVD23x) failed strict automotive EMC. TCAN3403-Q1 for non-automotive. Both support CAN FD up to 8 Mbps.
- **3.3V CAN FD with integrated controller: TCAN4550-Q1 (TI).** SPI-to-CAN FD -- no MCU CAN peripheral needed.
- **5V CAN 2.0: MCP2551 (Microchip), SN65HVD230 (TI, 3.3V I/O with 5V bus), TJA1051 (NXP).** All 8-SOIC pin-compatible.
- **3.3V CAN FD with VIO pin (non-automotive): ATA6561 (Microchip).** VIO pin allows direct interfacing to 3V-5V MCUs without level shifting. ATA6560 variant has silent (receive-only) mode via NSIL pin.
- **Node capacitance budget matters at high baud rates.** 5V transceivers: ~10 pF/node. 3.3V transceivers: ~16 pF/node. Board traces add 0.5-0.8 pF/cm.
- **Power savings with 3.3V transceivers are significant.** SN65HVD234 (3.3V): 7.1 mA recessive, 38.4 mA dominant. SN65HVD255 (5V): 18.6 mA recessive, 61.8 mA dominant. If 5V is only needed for CAN, switching to 3.3V eliminates that power rail entirely.

### Termination

- **Standard: 120 ohm at each physical end of the backbone.** Never at a mid-bus node -- disconnecting a terminating node kills the bus.
- **Split termination: 2x 60 ohm (1% matched) + 4.7 nF cap to GND.** The cap shunts CM noise. 4.7 nF gives -3 dB at ~560 kHz (1 Mbps fundamental). Range in sources: 4.7 nF to 47 nF -- use 4.7 nF default, larger values interfere with signal at higher bit rates.
- **Biased split termination:** Same as split but adds a VDD/2 voltage divider to the midpoint. Maintains constant recessive CM voltage for better EMC. Transceivers with VREF/VSPLIT pin (e.g., SN65HVD1050) stabilize this natively.
- **Software-controlled termination: ISOM8610 (TI opto-emulator) switches external 120 ohm via GPIO.** Useful for modular systems where end nodes aren't fixed -- all nodes get identical hardware, software enables termination on the two endpoints.
- **Termination resistor power rating: consider bus short to supply.** A 24V short through 120 ohm = 4.8W. Use 1/2W minimum in 12V systems; 1W in 24V systems.

### Bus Topology and Stubs

- **Stub length at 1 Mbps: 0.3 m max (ISO 11898 recommendation).** Calculated from: stub must be <1/3 of critical length. Critical length = t_rise / (2 * 5 ns/m). With 50 ns driver transition: 5 m critical, 1.67 m max stub -- but ISO spec is conservative at 0.3 m.
- **Slew-rate control extends allowable stub length.** SN65HVD230 with 10 kohm Rs slope control: 160 ns transition time -> 16/3 m (5.3 m) max stub. Trade-off: reduced maximum bus speed.
- **CAN FD at 5 Mbps: bus length drops to 10-15 m.** Edge rates ~20 ns. Point-to-point (2 nodes) is most reliable for CAN FD >2 Mbps.
- **Loaded bus impedance must stay above 0.71 * Z0 (85 ohm for 120 ohm bus).** Below this, incident-wave switching fails and the dominant-to-recessive transition may not cross the 0.5V recessive threshold.

### Common-Mode Choke Flyback Hazard

> WARNING: Bifilar I-bar CMCs generate flyback transients of 65-70V during DC bus shorts. Measured values from TI SLLA271: Epcos B82789C0513 (51 uH I-bar) hit 68.7V on CANL; Epcos B82789C0104 (100 uH I-bar) hit 70.1V. Most transceivers have +/-58V to +/-70V abs max. Board works fine until a bus fault -- then transceiver fails silently.

- **Toroid-core CMCs generate much lower transients (29-42V) vs I-bar (37-70V).** Best measured: Epcos B82799C0104 (100 uH bifilar toroid) at 31.6V. Sector-wound toroids also acceptable (34-50V range).
- **TVS placement with CMC: between CMC and transceiver, not at connector.** If TVS is on the bus side of the CMC, the choke's stray inductance (~500 nH+) delays clamping -- transceiver sees the full spike first.
- **Stray inductance between CMC output and TVS: keep below 500 nH.** Short, wide traces, no vias in that path.
- **Modern transceivers (ATA6560/61, TCAN series) are optimized for choke-less operation.** Output stage symmetry meets automotive EMC without a CMC. Only add a CMC if system-level EMC testing requires it.
- **CMC + bus parasitic capacitance can resonate.** Creates emission peaks at specific frequencies that vary with cable length and proximity to grounded surfaces. Unpredictable in the field.

### ESD and Transient Protection

- **ESD2CAN24-Q1 (TI): 24V VRWM, 30 kV contact (ISO 10605 and IEC 61000-4-2), 3 pF, SOT-23/SC70.** Bidirectional -- required because CAN signals swing above and below ground during faults. 24V VRWM sized for double-battery jumpstart in 12V automotive. For 24V systems (two 12V cells charged individually): use 36V VRWM device.
- **100 pF caps on CANH/CANL to GND at connector improve transient immunity.** Max 100 pF at 1 Mbps, 470 pF at 125 kbps. Include in node capacitance budget. Match the two caps tightly (<1% tolerance) -- asymmetry degrades CM rejection.
- **For harsh environments: 10-20 ohm series resistors on CANH/CANL.** Limits peak current during ESD/EFT/surge. Place between TVS and transceiver. Forms voltage divider with 60 ohm bus load -- attenuates differential signal slightly.
- **ESD protection capacitance + CMC inductance can ring.** Doesn't corrupt CAN data but creates high-frequency emission peaks. Select low-capacitance TVS. General ESD design -> `protection/esd.md`.

### Isolated CAN

- **ISO1042 (TI): reinforced isolation, +/-30V CM range, +/-70V bus fault tolerance.** Best for industrial with large ground potential differences or 48V systems. Requires external isolated DC-DC.
- **ISOW1044 (TI): integrated isolated DC-DC + CAN FD transceiver.** +/-12V CM, +/-58V bus fault. No external isolated supply needed -- simplest solution for space-constrained isolation.
- **ISO1044 (TI): +/-12V CM, +/-58V bus fault, no integrated power.** Use with external isolated supply (SN6505B + transformer, or field-side 24V in DeviceNet).
- **Maximum theoretical nodes with ISO1044/ISOW1044: ~222.** R_ID min = 40 kohm. 40000/222 = 180 ohm. 180 ohm || (2 * 120 ohm) = 45 ohm = minimum driver load for 1.4V differential output. Practical systems will have fewer.
- **Isolated supply noise: keep ripple <50 mV.** Noisy DC-DC modulates transceiver supply and increases jitter. Add LC filtering on isolated output. Isolation topology -> `protection/isolation.md`.

## Common Mistakes

- **CMC flyback destroys transceiver during bus short -- but only during faults.** Board passes all bench testing. First field bus-fault event kills the transceiver. Failure mode: transceiver may pass self-test but produce corrupted bus communication. Root cause only found with oscilloscope capturing the fault event. Fix: toroid-core CMC, or TVS between CMC and transceiver.
- **Split termination with 5% resistors.** 57 ohm and 63 ohm (5% band) degrades CM rejection by ~10 dB, negating most benefit over standard termination. Fix: 1% resistors from same reel.
- **Termination at interior node on multi-node bus.** Creates impedance discontinuity. Reflections corrupt data above 500 kbps. Particularly bad on modular systems where "every node gets a termination resistor." Fix: only the two physical endpoints. Use ISOM8610 for software-switchable termination if topology is dynamic.
- **Forgetting the dominant-to-recessive transition is passive (RC decay).** Unlike RS-485, CAN doesn't actively drive the recessive state. Without termination, the bus may never reach recessive threshold. This is why CAN requires termination for basic functionality, not just signal integrity.
- **Double-battery jumpstart exceeding TVS working voltage.** 12V system with series-connected jumpstart batteries = 24V on bus. A 12V VRWM TVS conducts continuously and overheats. Fix: use 24V VRWM (ESD2CAN24-Q1) for 12V systems, 36V for 24V systems.

## Formulas

**Maximum bus length:**
**Rule of thumb:** 40 m at 1 Mbps, 500 m at 100 kbps.
**Formula:** L_max(m) = 50 / Rate(Mbps)
**Example:** 250 kbps -> L_max = 50 / 0.25 = 200 m.

**Maximum stub length:**
**Rule of thumb:** 0.3 m at 1 Mbps (ISO 11898 spec).
**Formula:** L_stub = t_rise / (6 * t_prop_per_m), where t_prop ~ 5 ns/m (twisted pair, down-and-back = 10 ns/m)
**Example:** 50 ns driver transition -> critical length = 50/10 = 5 m -> max stub = 5/3 = 1.67 m. ISO spec uses 0.3 m as conservative value.

**Minimum node spacing:**
**Rule of thumb:** >0.2 m between nodes at 1 Mbps with typical twisted pair.
**Formula:** d_min = C_node / (0.98 * C_cable_per_m)
**Example:** C_node = 16 pF (3.3V transceiver), C_cable = 50 pF/m -> d_min = 16 / (0.98 * 50) = 0.33 m.

**Maximum bus capacitance (dominant-to-recessive timing):**
**Formula:** 3 * R_eff * C_total <= 0.75 * T_bit
  - R_eff: effective differential resistance (~60 ohm = two 120 ohm terminations in parallel)
  - C_total: cable capacitance + (N * C_node) + protection device capacitance
**Example:** 1 Mbps (T_bit = 1 us), R_eff = 60 ohm -> C_max = 0.75 * 1000 ns / (3 * 60) = 4167 pF. At 50 pF/m cable: ~80 m of cable alone would consume this budget.

## Sources

### Related Rules

- `protection/esd.md` -- ESD protection design for bus connectors
- `protection/isolation.md` -- isolated CAN topology and isolated supply design

### References

1. TI SLLA337 -- Overview of 3.3V CAN Transceivers: https://www.ti.com/document-viewer/lit/html/SLLA337
2. TI SSZTAM0 -- How Termination CAN Improve EMC Performance: https://www.ti.com/document-viewer/lit/html/SSZTAM0
3. TI SLVAFC1 -- CAN Bus ESD Protection: https://www.ti.com/document-viewer/lit/html/SLVAFC1
4. TI SLLA270 -- Controller Area Network Physical Layer Requirements: https://www.ti.com/lit/pdf/SLLA270
5. TI SLLA271 -- Common-Mode Chokes in CAN Networks: Source of Unexpected Transients: https://www.ti.com/lit/pdf/SLLA271
6. TI SLLA486 -- Top Design Questions About Isolated CAN Bus Design: https://www.ti.com/document-viewer/lit/html/SLLA486
7. Microchip AN228 -- A CAN Physical Layer Discussion: https://ww1.microchip.com/downloads/en/appnotes/00228a.pdf
8. Altium -- Designing CAN-Bus Circuitry: CAN-Bus PCB Layout Guidelines: https://resources.altium.com/p/can-bus-designing-can-bus-circuitry
9. Microchip ATAN0103 -- ATA6560/ATA6561 CAN FD Transceiver Application Note: https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ApplicationNotes/ApplicationNotes/Atmel-9310-ATA6560-EK-ATA6561-EK_Application-Note.pdf
