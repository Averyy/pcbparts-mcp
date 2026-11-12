# USB

> USB 2.0 D+/D- routing, USB-C CC configuration, PD controller selection, VBUS power path, ESD protection.

## Quick Reference

- **USB-C sink receptacle: separate 5.1 kohm 1% Rd on EACH CC pin to GND.** Shorting CC1 to CC2 lets a powered cable's Ra parallel the shared Rd and defeats valid attachment detection [1, Sections 4.5.1, 4.11.1].
- **ESD TVS array closest to connector, before CMC.** For TUSB121x, TI recommends <=4 pF total external discrete capacitance per D+/D- line, excluding PCB trace capacitance; use the selected PHY's budget [4, p.2, items 1.06-1.09].
- **TUSB121x HS routing: 90 ohm differential, 50 mm (1.97 in) optimum, <=0.5 ns one-way delay.** TI equates that delay to about 75 mm (2.95 in) at 67 ps/cm and allows <=3.81 mm (150 mil) pair mismatch; these are PHY board guidelines, not universal USB limits [4, p.2, items 2.03-2.05].
- **CC protection for a 20 V short-to-VBUS environment: use a DC-tolerant protector.** TPD2S300 requires at least 22 V-tolerant ESD protection and recommends 24 V; a TVS's working voltage and clamping voltage are different specifications [10, p.12].

## Design Rules

### USB-C CC Configuration

- **Sink: 5.1 kohm on each CC pin to GND; the spec allows +/-10% (+/-20%, or a 1.1 V +/-20% clamp, if the sink ignores advertised current).** The resistor implementations give maximum normal CC voltages of 2.04 V and 2.18 V respectively; these are not controller absolute maximum ratings. A voltage-clamp Rd inhibits PD communication until switched to a resistor [1, p.244, Table 4-28].
- **Sink current-detection windows are a worked example for +/-10% Rd, not fixed limits.** Type-C R2.4 Table 4-36 gives Default 0.277-0.612 V, 1.5 A 0.746-1.164 V, 3.0 A 1.369-2.042 V, with threshold windows 0.613-0.745 V and 1.165-1.368 V. Recalculate using Section 4.11.3.1.1 for actual termination tolerances and cable ground offset; do not infer a disconnect threshold below 0.276 V from this table [1, pp.247-252].
- **Ra is 800-1200 ohm when VCONN is applied; it can be lower before power is applied.** For Default advertisement, the example source Ra/Rd threshold is 0.144-0.271 V with Rp to 5 V or 0.116-0.260 V with a current source; these source-side thresholds are not sink current-advertisement thresholds [1, pp.244,253-254, Tables 4-29, 4-37, 4-38].
- **Source Rp depends on its pull-up voltage.** At 4.75-5.5 V: 56 kohm +/-20% = Default USB Power, 22 kohm +/-5% = 1.5 A, 10 kohm +/-5% = 3 A. At 3.3 V +/-5% the corresponding values are 36 kohm +/-20%, 12 kohm +/-5%, 4.7 kohm +/-5%. Legacy A-to-C cables/adapters and captive host cables require 56 kohm +/-5%; Default advertisement alone does not authorize an unenumerated USB device to draw 500/900 mA [1, pp.225-227,243, Table 4-27].
- **A sink built with a Type-C plug exposes one CC pin, unlike a receptacle's CC1/CC2.** Do not treat the plug's VCONN contact as a second CC pull-down; two Rd terminations are the source's debug-accessory signature [1, Section 3.2.2, Table 4-10].

> WARNING: With CC1/CC2 shorted to one Rd, nominal 1 kohm Ra in parallel with 5.1 kohm gives 836 ohm, rather than a valid Rd. Keep the two receptacle CC terminations independent [1, Sections 4.5.1, 4.11.1; parallel resistance recalculated].

- **For 20 V short-to-VBUS protection, select both DC withstand and controller-side clamping/isolation.** CC1/CC2 are adjacent to VBUS in the receptacle. TI lists ESD752/ESD2CAN24-Q1 with 24 V working voltage for this case, or use a short-to-VBUS isolator such as TPD2S300. A 24 V-working TVS alone does not hold a low-voltage controller pin below its absolute maximum during a sustained short [10, Section 7.1; 11, pp.16-17].
- **Never put CC on a spare channel of the D+/D- ESD array.** A channel rated for 5 V data lines does not meet the at least 22 V DC tolerance CC needs for a short to VBUS [10, p.12].
- **CC receiver capacitance is part of the PD circuit, not just a TVS selection number.** FUSB302B's reference schematic specifies 200-600 pF CCx receiver capacitance; include the protection capacitance when selecting the receiver network [9, Reference Schematic, Table 43].

### USB-C PD Controllers

- **Sink-only PD, no MCU: STUSB4500 (ST, QFN-24 or WLCSP-25).** NVM stores up to three sink PDO profiles, up to 20 V/5 A. VBUS_EN_SNK is an active-low open-drain enable for the external sink power path; observe the reference circuit's polarity [8, pp.1-4,6].
- **Sink PD with MCU: FUSB302B (onsemi, WLCSP-9 or WQFN-14).** I2C-controlled PD PHY requiring software policy control, rather than a standalone automatic voltage requester [9, pp.1-2].
- **Source/sink PD: TPS65987D (TI, QFN-56), single port with two internal power paths.** Each integrated path is rated 20 V/5 A, with 25 mohm typical (33 mohm maximum) resistance at TJ=25 degrees C; the 5 A capability requires TJ < 150 degrees C. Configuration/patches can load from external SPI flash; do not assume internal configuration flash or two Type-C ports [12, Sections 6.7,8.3.3,8.3.13].
- **TPS65987D power duo mode is a custom high-current arrangement.** Parallel paths reduce effective resistance, but >5 A requires compatible configuration at both ends and cabling rated for the desired current; it is not an ordinary USB PD current contract [13, Power Duo Mode].
- **CC logic only (no PD): TUSB320 (TI).** DFP/UFP/DRP and orientation detection with I2C or GPIO reporting; system circuitry must enforce the detected current limit [14, Sections 7.3.1-7.3.3].

### Dead Battery Provision

- **TPS6598x boots from VBUS when VIN_3V3 is absent.** SLVAE65 describes an internal LDO converting up to 22 V VBUS to 3.3 V and hardware configured to present Rd even without local power; verify the selected part's dead-battery wiring [7, pp.1-2,5].
- **VIN_3V3 takes precedence.** When VIN_3V3 becomes available, clearing the Dead Battery Flag switches LDO_3V3 from the VBUS LDO without brown-out. In the opposite transition, VIN_3V3 below 2.85 V initiates a firmware hard reset and renegotiation; this is not an uninterrupted system-power handover [7, pp.3-4].
- **Dual VBUS inputs (TPS65988): reverse-current blocking in the LDO input paths.** Power on one VBUS does not leak to the other through those paths; this does not replace protection in the main system power paths [7, p.2].

### VBUS Power Path

- **USB 2.0 peripheral inrush is specified as a load equivalent to 10 uF in parallel with 44 ohm.** Larger bulk capacitance needs a soft-start path that meets the inrush requirement; a current-limiting switch alone is not proof. FTDI shows a PWREN#-controlled IRLML6402TRPBF soft-start circuit [5, Section 2.4.2].
- **EFM32 USB host example: >=96 uF VBUS decoupling near its Type-A connector.** This is the AN0046 host checklist; do not apply it indiscriminately to Type-C sink or dual-role ports [2, Section 2.2].
- **VBUS ferrite example: 47-1000 ohm at 100 MHz, resistive to approximately 1 GHz.** This is TI's AM335x/AM43xx filtering recommendation, not a universal required bead. FTDI names BK0603HS330-T for its USB peripheral filter; check load current and DC voltage drop [3, Section 2.4; 5, Section 2.4.4, Appendix A].
- **No power back-feed into upstream VBUS from a USB peripheral.** FTDI's PWREN# soft-start example is not a general reverse-current blocker; select isolation for the actual local-supply/VBUS power paths [5, Sections 2.4.1-2.4.2].

### VBUS Protection (Source)

- **TPS65987DDH short-circuit timing is measured on the TPS65987DEVM.** SLVA994 reports <15 us opening at 5 V and <7 us at 20 V, where current exceeds the 30 A hardware-interrupt threshold. Do not treat these EVM waveforms as universal maximum response times for arbitrary supplies and layouts [6, pp.10-12].
- **TPS65987DDH hardware OCP changes from 10 A to 20 A during a voltage transition.** SLVA994 returns it to 10 A approximately 100 ms after the Request message; this hardware threshold is separate from the negotiated operating current and firmware OCP [6, pp.3-4,10].
- **Overcurrent clamping at 5 V is separate from OCP.** TPS65987DDH regulates the internal FET to the selected clamp setting, then opens after a 640 us deglitch if overcurrent persists. Check the selected IOCC setting's minimum/maximum, not just the GUI's nominal current [6, pp.5-9].
- **TPS65987DDH OVP: use the GUI setting "5% of expected max," not 5% of negotiated voltage as an absolute threshold.** It tracks the contract; SLVA994 warns that a fixed 24 V trip point also applies during a 5 V contract and would pass a damaging overvoltage [6, pp.17-20].
- **Reverse current protection for multi-port systems.** If separate ports close onto the same system rail at 5 V and 20 V, the 5 V port must block reverse current. TPS65987DDH uses its internal back-to-back FETs for this case [6, pp.13-16].

### D+/D- Routing

- **Series resistors depend on PHY family.** FTDI AN_146 specifies 27 ohm/1% for FT2xxB, FT2xxX, FT2232D, FT12x, FT31xD and VNC2; 0 ohm for FT2xxR/FT313H; 0-10 ohm for FTx232H. AN0046's EFM32 circuits use 15 ohm. Do not copy these onto another PHY without its data sheet [5, Section 2.3; 2, Sections 2.2-2.4].
- **Length matching and spacing come from the selected PHY board guide.** TUSB121x permits 3.81 mm (150 mil) mismatch and <5.08 mm (200 mil) unavoidable stubs. AM335x/AM43xx prohibits test points of any kind on D+/D-; generic fly-by-pad advice does not override that restriction [4, p.2; 3, Section 2.6].
- **USB 2.0 mux for a Type-C receptacle is optional.** D+ to D+ and D- to D- ties are allowed across receptacle orientations; a mux removes that branch but adds its own parasitics. Follow the selected PHY's stub and capacitance limits [15, USB Type-C UFP Sink].
- General differential routing and return-plane guidance -> `guides/signal-integrity.md`.

### ESD Protection

- **Component order from connector inward: TVS -> optional CMC -> PHY termination network.** Follow the PHY reference circuit for series resistor placement; TI specifies the TVS before all other external D+/D- devices [4, p.2, items 1.07-1.09; 5, Sections 2.2-2.3].
- **IP4220CZ6: 1 pF typical per input at VI=0 V, VP=3 V, 1 MHz and 25 degrees C; SOT457/SC-74.** This is a typical value, not a <1 pF maximum. AN0046 reports an 8 kV contact pass on EFM32GG-STK3700; its 9 V residual-output discussion does not establish safe clamping for another PHY [16, pp.1-3; 2, Section 6.2].
- **SRV05-4: one name, different silicon.** Semtech specifies 3 pF typical in SOT-23-6; FTDI lists it and Littelfuse PGB1010603 as candidates. Verify the exact manufacturer's capacitance against the PHY budget instead of substituting a same-named clone [21; 5, Appendix A; 4, item 1.06].
- **USB 2.0 CMC: Murata DLW21HN900SQ2 (0805 inch / 2.0 * 1.2 mm, 90 ohm CM at 100 MHz) [17, 18].** Use only when EMI testing requires it: TI warns that CMCs degrade signal quality. Murata lists this part for USB 2.0; select a USB 3.x-rated part for a SuperSpeed pair [4, item 1.08; 18] -> `guides/emc.md`.
- **Do not substitute separate ferrite beads on D+/D- for a USB-rated CMC.** FTDI explicitly prohibits individual data-line beads and recommends the power-line bead on VBUS [5, Sections 2.2.3, 2.4.4].

### Connector and Shield Grounding

- **Provide shield-to-signal-GND tuning pads rather than a universal RC value.** FTDI recommends pads for a zero-ohm resistor or capacitor during EMC tuning; TI's AM335x design bonds the shell to a local chassis-ground region while keeping signal GND under the connector pins [5, Section 2.2.2; 3, Section 2.4].

### USB-C Connector Manufacturing

- **Wurth's horizontal THR/SMT and mid-mount receptacle process uses special stencil parameters.** ANE009 specifies type-5 paste, 20 mm/s print speed, 70 N squeegee force, 45-degree plastic squeegee and two print cycles for its listed parts; these are not universal settings for every hybrid connector [19, p.2].
- **Wurth 632723130112 mid-mount example: 0.80 mm -> 1.00 mm pin-row-to-milling-contour distance.** With the note's 0.50 mm (20 mil) milling cutter, this increases routing width from 0.225 mm (8.86 mil) to 0.425 mm (16.73 mil). It requires +/-50 um placement accuracy and EMS agreement; do not transplant the footprint change to another connector [19, pp.8-9].

## Common Mistakes

- **Omitting the external low-speed pull-up on the EFM32 family covered by AN0046.** Its approximately 2.2 kohm internal pull-up needs an external 4.7 kohm in parallel on D- to meet the 1.5 kohm identification value. Use USB_DMPU when VDD is 3.3 V; AN0046 requires a separately switched USB_VREGO connection if VDD is lower [2, Section 2.3.3].
- **A legacy A-to-C cable pulls CC toward VBUS when Rd is disabled.** With a non-USB charging protocol that raises VBUS above 5 V, the cable's 56 kohm Rp exposes an unprotected CC controller to excess voltage. Protection must cover this disabled-Rd case as well as a direct short to VBUS [20, pp.2-3].

## Sources

### Related Rules

- `protection/esd.md` -- ESD protection placement and design for USB connectors
- `guides/signal-integrity.md` -- differential routing and continuous return paths

### References

1. USB-IF -- USB Type-C Cable and Connector Specification Release 2.4 (October 2024), published specification mirrored by TI: https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/USB-Type_2D00_C-Spec-R2.4-_2D00_-October-2024.pdf
2. Silicon Labs AN0046 (Rev.1.02) -- USB Hardware Design Guidelines (EFM32 Giant/Leopard Gecko): https://www.silabs.com/documents/public/application-notes/an0046-efm32-usb-hardware-design-guidelines.pdf
3. TI SPRABT8A (November 2014) -- AM335x and AM43xx USB Layout Guidelines: https://www.ti.com/lit/pdf/sprabt8
4. TI SWCA124 (October 2011) -- TUSB121x USB 2.0 Board Guidelines: https://www.ti.com/lit/pdf/swca124
5. FTDI AN_146 (Version 1.1, November 2013) -- USB Hardware Design Guidelines for FTDI ICs: https://ftdichip.com/wp-content/uploads/2020/08/AN_146_USB_Hardware_Design_Guidelines_for_FTDI_ICs.pdf
6. TI SLVA994 (June 2018) -- TPS65987DDH Power Path Performance and Protection: https://www.ti.com/lit/pdf/slva994
7. TI SLVAE65 (February 2019) -- TPS6598x Dead Battery Application Note: https://www.ti.com/lit/pdf/slvae65
8. ST STUSB4500 (DS12499 Rev.8, November 2022): https://www.st.com/resource/en/datasheet/stusb4500.pdf
9. onsemi FUSB302B (Rev.5, August 2021): https://www.onsemi.com/pdf/datasheet/fusb302b-d.pdf
10. TI TPD2S300 (SLVSDL1, April 2017): https://www.ti.com/lit/ds/symlink/tpd2s300.pdf
11. TI SLVAF82B (January 2024) -- ESD and Surge Protection for USB Interfaces: https://www.ti.com/lit/pdf/slvaf82
12. TI TPS65987D (SLVSES1D, October 2022): https://www.ti.com/lit/ds/symlink/tps65987d.pdf
13. TI SLYY145A (June 2019) -- USB Type-C and USB PD Power Path Design Considerations: https://www.ti.com/lit/pdf/slyy145
14. TI TUSB320 (SLLSEN9F) -- USB Type-C Configuration Channel Logic and Port Control: https://www.ti.com/lit/ds/symlink/tusb320.pdf
15. TI SLYY109 -- A Primer on USB Type-C and USB Power Delivery Applications and Requirements: https://www.ti.com/lit/pdf/slyy109
16. NXP IP4220CZ6 (Rev.5, July 2011): https://assets.nexperia.com/documents/data-sheet/IP4220CZ6.pdf
17. Murata -- DLW21HN900SQ2 data sheet (June 2022): https://www.murata.com/en-us/products/productdetail?partno=DLW21HN900SQ2%23
18. Murata -- Common Mode Choke Coil / Noise Filter selection chart, USB 2.0/3.0/3.1: https://www.murata.com/-/media/webrenewal/products/emc/emifil/cmcc/pdf/usb.ashx
19. Wurth ANE009 (May 2020) -- Production Guide USB 3.1 Type C: https://www.we-online.com/components/media/o563289v410%20ANE009a_EN.pdf
20. onsemi AN-5086 (Rev.2, September 2017) -- USB Type-C CC Pin Design Considerations: https://www.onsemi.com/pub/Collateral/AN-5086-D.PDF
21. Semtech -- SRV05-4 product specifications and datasheet listing (December 2018): https://www.semtech.com/products/circuit-protection/low-capacitance/srv05-4
