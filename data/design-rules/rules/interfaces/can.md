# CAN Bus

> Physical layer design: transceiver selection, termination, CMC flyback hazard, ESD protection, isolated CAN.

## Quick Reference

- **Split termination: 2*60 ohm (1%) + 4.7 nF midpoint to GND at each bus end.** TI's 500 kHz square-wave test reduced CANH+CANL peak-to-peak from 344 mV to 138 mV after replacing one end's single termination with split termination; these are measured summed voltages, not a guaranteed emission reduction [2, Figures 3-4; 4, p.7].
- **CMC flyback can exceed the transceiver's bus rating during DC bus shorts.** Put the transient protectors between CMC and transceiver; TI measured up to 70.5 V in its 12 V short-circuit tests [5, pp.4-6].
- **ESD: ESD2CAN24-Q1 (TI, +/-24 V VRWM, 3 pF typical per line at 0 V bias/1 MHz/25 degrees C, SOT-23/SC70).** Its IEC contact rating is +/-30 kV; ISO 10605 contact is +/-30 kV at 150 pF/330 ohm or +/-27 kV at 330 pF/330 ohm [9, Sections 3, 5.3-5.4, 5.7].
- **3.3 V and 5 V high-speed CAN transceivers interoperate on the bus; MCU I/O still needs a voltage check.** >=1.5 V is the dominant driver-output specification, not the receiver threshold [1, pp.2,7].
- **Classical CAN bus length: 40 m at 1 Mbps; Rate(Mbps) * Length(m) <= 50 only for buses over 100 m.** TI gives the product rule as a conservative rule of thumb for lengths over 100 m; shorter buses use its cable-length table (40 m at 1 Mbps, the ISO 11898 figure) and 0.3 m unterminated stubs. Include controller/transceiver delay and cable loss in the actual timing budget [4, Section 4.1, Table 1, pp.5,9-11].

## Design Rules

### Transceiver Selection

- **3.3 V automotive CAN FD: TCAN3403-Q1/TCAN3404-Q1 (TI).** Both families pass IEC 62228-3:2019 in homogeneous and heterogeneous networks; both are automotive parts. The data sheet qualifies EMC operation up to 5 Mbps and allows 8 Mbps in simpler networks [1, p.3; 10, p.1].
- **Integrated controller: TCAN4550-Q1 (TI), SPI-to-CAN FD.** This is not a 3.3 V single-supply transceiver: VSUP requires 5.5-30 V and powers internal regulators, including the CAN supply, while VIO interfaces to a 3.3 V or 5 V MCU [11, pp.1,6,25-26].
- **Classical CAN parts: MCP2551 (Microchip, 5 V) or SN65HVD230 (TI, 3.3 V supply).** A bus that interoperates with 5 V transceivers does not make SN65HVD230 a 5 V-powered part [7, pp.2-3; 1, pp.2,6-7].
- **5 V CAN FD with separate logic supply: ATA6561 (Microchip).** The application circuit uses a dedicated 5 V VCC regulator and VIO tied to the MCU supply for 3 V-5 V logic. ATA6560 replaces VIO with NSIL for receive-only mode and uses VCC-referenced logic [8, pp.5-7].
- **Node capacitance is device-specific and must use the same differential definition as the cable.** SLLA270's examples are 10 pF for SN65HVD251 and 16 pF for SN65HVD230, with board traces adding 0.5-0.8 pF/cm; these are not universal 5 V/3.3 V values. Include connectors and protection devices [4, pp.11-13].
- **Supply-current comparison is a measurement, not a family guarantee.** In TI's two-node test, SN65HVD234 measured 7.1 mA recessive and 38.4 mA while it alone drove dominant; SN65HVD255 measured 18.6 mA and 61.8 mA under the corresponding conditions [1, p.7, Table 4-1].

### Termination

- **Use 120 ohm at each physical end of a 120 ohm backbone.** Avoid making termination dependent on a removable node; disconnecting it removes that end's termination [4, p.5].
- **Split termination uses matched resistors; select capacitance for the transceiver/network.** SLLA270 uses 4.7 nF; ATA6560/61's application note recommends 4.7-47 nF and resistor matching <1%. The larger capacitor is on the common-mode midpoint, not directly across the differential signal [4, p.7; 8, p.5].
- **Biased split termination:** adds a VDD/2 divider to the midpoint to stabilize recessive common-mode voltage. Match both bias and termination resistors; use a transceiver's split-reference output only as its data sheet permits [7, p.10].
- **Software-controlled termination: ISOM8610 (TI opto-emulator) switches an external 120 ohm via GPIO.** Useful for modular systems where end nodes aren't fixed -- all nodes get identical hardware, software enables termination on the two endpoints [6, p.4, Figure 4-2].
- **Size termination resistors for the specified differential fault voltage and duration.** A 24 V difference across 120 ohm dissipates 4.8 W; a short of one bus line to supply does not by itself establish that full difference. A blanket 0.5 W or 1 W choice does not cover this sustained fault; check pulse overload as well as continuous rating [4, Section 4.5; power recalculated].

### Bus Topology and Stubs

- **Stub length at 1 Mbps: 0.3 m in TI's ISO 11898 summary.** Its transmission-line example gives 1.67 m for a 50 ns transition and 5 ns/m cable propagation; that simplified calculation does not override the 0.3 m network recommendation [4, pp.5,9].
- **Slew-rate control extends stubs only with reduced signaling rate and a timing check.** SLLA270's SN65HVD230 example uses 10 kohm on Rs, a 160 ns transition and a calculated 5.33 m stub; it is not a 1 Mbps allowance [4, p.9].
- **Loaded bus impedance guideline: >0.71*Z0 (85.2 ohm for a 120 ohm bus).** SLLA270 derives this for incident-wave switching during dominant-to-recessive transitions with distributed capacitive loading; use differential capacitance in its spacing calculation [4, pp.11-13].

### Common-Mode Choke Flyback Hazard

> WARNING: In SLLA271's 1 m cable tests, with 100 pF bus capacitors, local termination/protectors open and CANL shorted to 12 V at the far termination, Epcos B82789C0513 (51 uH I-bar) produced 68.7 V on CANL; B82789C0104 (100 uH I-bar) produced 70.1 V. Compare the resulting pin waveform against the exact transceiver's absolute maximum rating; these are fault-test measurements, not universal choke voltages [5, pp.3,5, Table 1].

- **Choose a choke from fault-test results, not core shape alone.** In the same CANL-short test, Epcos B82799C0104 (100 uH bifilar toroid) produced 31.6 V on CANL, but Bourns DR331-513BE (51 uH bifilar toroid) produced 48.8 V. Toroids generally performed better; they do not guarantee a 29-42 V ceiling [5, p.5, Table 1].
- **TVS placement with CMC: between CMC and transceiver.** This clamps the flyback generated on the transceiver side during a DC bus fault; a protector only at the connector does not clamp that node directly [5, p.4, Figure 6].
- **Start without a choke when the transceiver and system EMC requirements permit.** Add one only after checking its effect on fault transients and signal integrity. ATA6560/61's evaluation board provides an optional CMC footprint rather than requiring a choke [5, pp.2,5-6; 8, p.5].
- **CMC + TVS capacitance can ring.** SLLA271's example did not corrupt CAN data but could create high-frequency emissions; do not assume that result holds for an arbitrary choke/protector/network [5, p.4].

### ESD and Transient Protection

- **Select bidirectional TVS working voltage for the fault environment, and clamping voltage for the transceiver.** SLVAFC1 recommends 24 V VRWM for its 12 V double-battery jump-start case and 36 V for its described 24 V system; these are application cases, not protection against every battery transient [3, Section 3].
- **The <15 pF recommendation applies to the protection diode, not all node parasitics combined.** Recheck total loading against the transceiver, network size, cable and data rate [3, Section 3].
- **Bus-line capacitors to GND: matched pairs, below 100 pF at 1 Mbit/s and at most 470 pF at 125 kbit/s.** Microchip's ATA6560/61 note gives these limits from bit-timing requirements, citing SAE J2284 and ISO 11898, and places the capacitors between the common-mode choke (if fitted) and the ESD clamps; its example uses approximately 100 pF per line near the connector. The usable value also falls with node count, so include the capacitors in timing and node loading [8, Sections 3.1.4, 5.2.2.2].
- **For isolated-CAN surge designs, SLLA486B suggests approximately 10 ohm series resistance on each bus line.** These resistors attenuate the differential drive into the 60 ohm bus load; verify receiver margin and system surge performance rather than assuming the attenuation is negligible [6, p.5].
- General ESD design -> `protection/esd.md`.

### Isolated CAN

- **ISO1042 (TI): +/-30 V common-mode range, +/-70 V bus fault rating.** Requires external bus-side power; a 48 V bus short within the fault rating does not imply communication at that common-mode voltage [6, pp.3,5].
- **ISOW1044 (TI): integrated isolated DC-DC + CAN FD transceiver.** +/-12 V common-mode range, +/-58 V bus fault rating; no external isolated supply needed [6, pp.3,5].
- **ISO1044 (TI): +/-12 V common-mode range, +/-58 V bus fault rating, no integrated power.** Use an isolated supply such as SN6505B + transformer; DeviceNet's available field-side 24 V requires a regulator, not direct connection to VCC2 [6, pp.3,5, Figures 3-1 to 3-3].
- **The ~222-node ISO1044/ISOW1044 limit is resistive only.** With 40 kohm minimum differential resistance per receiver, 222 nodes present 180.18 ohm; in parallel with two 120 ohm terminations this is 45.01 ohm, near the 45 ohm load used for the 1.4 V minimum output specification. Capacitance and timing reduce the practical count [6, p.7, Section 9; recalculated].
- Isolation topology -> `protection/isolation.md`.

## Common Mistakes

- **Assuming an SOIC-8 footprint makes transceivers pin-compatible.** ATA6560 uses pin 5 for NSIL, ATA6561 for VIO; replacing one without checking pin functions can connect a control signal to a supply [8, pp.3-5].
- **Treating an RC capacitance estimate as a cable-length guarantee.** SLLA486B's 3*R_eff*C_total <= 0.75*T_bit assumes sampling at about 75% of the bit and effective differential capacitance. It omits cable propagation and other timing limits; include equal line-to-ground capacitors as half their individual value in the differential budget [6, p.8].

## Formulas

**Minimum node spacing for SLLA270's distributed-loading model [4, pp.11-13]:**
**Rule of thumb:** Derive spacing from the actual node and cable differential capacitances; there is no universal 0.2 m minimum.
**Formula:** d_min > C_node / (0.98 * C_cable_per_m), based on loaded impedance >0.71*Z0. C_node includes the transceiver, connector, PCB and protection; use differential capacitance consistently.
**Example:** C_node = 16 pF, C_cable = 50 pF/m -> d_min > 16 / (0.98 * 50) = 0.327 m. Extra protection capacitance increases the required spacing in this model.

## Sources

### Related Rules

- `protection/esd.md` -- ESD protection design for bus connectors
- `protection/isolation.md` -- isolated CAN topology and isolated supply design

### References

1. TI SLLA337A (May 2025) -- Overview of 3.3V CAN Transceivers: https://www.ti.com/lit/pdf/slla337
2. TI SSZTAM0 (November 2016) -- How Termination CAN Improve EMC Performance: https://www.ti.com/document-viewer/lit/html/SSZTAM0
3. TI SLVAFC1 (April 2022) -- CAN Bus ESD Protection: https://www.ti.com/document-viewer/lit/html/SLVAFC1
4. TI SLLA270 (January 2008) -- Controller Area Network Physical Layer Requirements: https://www.ti.com/lit/pdf/slla270
5. TI SLLA271 (January 2008) -- Common-Mode Chokes in CAN Networks: Source of Unexpected Transients: https://www.ti.com/lit/pdf/slla271
6. TI SLLA486B (October 2024) -- Top Design Questions About Isolated CAN Bus Design: https://www.ti.com/lit/pdf/slla486
7. Microchip AN228 (DS00228A, 2002) -- A CAN Physical Layer Discussion: https://ww1.microchip.com/downloads/en/appnotes/00228a.pdf
8. Microchip ATAN0103 (9310E, October 2016) -- ATA6560/ATA6561 CAN FD Transceiver Application Note: https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ApplicationNotes/ApplicationNotes/Atmel-9310-ATA6560-EK-ATA6561-EK_Application-Note.pdf
9. TI ESD2CANxx24-Q1 (SLVSFW5D) -- Automotive 24V, 2-Channel ESD Protection Diode: https://www.ti.com/lit/ds/symlink/esd2can24-q1.pdf
10. TI TCAN340x-Q1 (SLLSFQ6A, June 2024) -- 3.3V Automotive CAN FD Transceivers: https://www.ti.com/lit/ds/symlink/tcan3404-q1.pdf
11. TI TCAN4550-Q1 (SLLSEZ5D, June 2022): https://www.ti.com/lit/ds/symlink/tcan4550-q1.pdf
