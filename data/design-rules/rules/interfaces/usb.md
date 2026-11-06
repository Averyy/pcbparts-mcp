# USB

> USB 2.0 D+/D- routing, USB-C CC configuration, PD controller selection, VBUS power path, ESD protection.

## Quick Reference

- **USB-C sink: 5.1 kohm 1% Rd on EACH CC pin to GND.** Never short CC1 to CC2 -- e-marked cables put 1 kohm Ra on the second CC, paralleling to 840 ohm total, which the source reads as invalid and provides 0V on VBUS.
- **ESD TVS array closest to connector, before CMC.** NXP IP4220CZ6 (< 1 pF/line, SOT-457) or an SRV05-4 clone listing <= 1 pF (SOT-23-6); Semtech's own SRV05-4 is 3 pF typ. Max 1.5 pF external capacitance per D+/D- line total for high-speed.
- **D+/D- length match within 1.27 mm (50 mil), 0.5 mm (20 mil) preferred.** Optimal trace length 50 mm, max 75 mm (USB 2.0 HS). Total trace length < 100 mm to preserve eye diagram.
- **USB-C 2.0-only connector: Korean Hroparts TYPE-C-31-M-12 (LCSC C165948).** 16 contacts on 12 SMD pads in one row (A1/B12, A4/B9, B4/A9 and B1/A12 share pads), easily hand-solderable. Power-only alternative: TYPE-C-31-M-17 (C283540, 6 contacts).
- **VBUS ferrite bead: 47-1000 ohm at 100 MHz.** 10 nF cap from VBUS to chassis GND after ferrite, before bulk decoupling.

## Design Rules

### USB-C CC Configuration

- **Sink: 5.1 kohm on each CC pin to GND; the spec allows ±10% (±20%, or a 1.1 V clamp, if the sink ignores the advertised current).** Max voltage on the pin: 2.04 V at ±10%, 2.18 V at ±20% (Type-C R2.5 Table 4-28).
- **Sink CC windows are the spec's worked example for a ±10% Rd, not fixed limits.** Type-C R2.5 Table 4-36 (same numbering in R2.4): Default 0.277-0.612 V, 1.5 A 0.746-1.164 V, 3.0 A 1.369-2.042 V; the sink puts its Default/1.5 A threshold anywhere in 0.613-0.745 V and its 1.5 A/3.0 A threshold in 1.165-1.368 V, and reads disconnect below 0.276 V. R2.x computes these from its section 4.11.3.1.1 equations (Rp/current-source tolerance, 250 mV cable ground offset); R1.x tabled 0.25-0.61 / 0.70-1.16 / 1.31-2.04 V with fixed 0.66 V and 1.23 V thresholds. A 1% Rd only widens the margins.
- **Ra (0.8-1.2 kohm) is nowhere near an Rd.** A -5% Rd against Default Rp gives 0.40 V; a source sets its Ra/Rd threshold in 0.144-0.271 V (Rp to 5 V) or 0.116-0.260 V (current source) (R2.5 Tables 4-37, 4-38).
- **Source: Rp pull-up to 4.75-5.5 V on each CC pin.** 56 kohm = default USB (500/900 mA), 22 kohm = 1.5 A, 10 kohm = 3 A. Spec tolerance: 56 kohm ±20%, but ±5% in legacy A-to-C cables, adapters and captive host cables (allows for VBUS/GND drop); 22 and 10 kohm ±5% (Type-C R2.0 Table 4-24).
- **USB-C plug (cable-end, not receptacle): only ONE CC pull-down.** Populating both 5.1 kohm pull-downs on a plug makes a debug mode adapter -- Framework laptops expose EC UART on SBU pins when they see dual pull-downs.

> WARNING: The Raspberry Pi 4 shipped with CC1/CC2 shorted through a single Rd. E-marked cables (every MacBook cable since 2016) put Ra (800-1200 ohm) on the unused CC, paralleling with 5.1 kohm to ~840 ohm. Source sees this as invalid attachment and provides 0V. Always use two separate resistors.

- **CC TVS: rate it for a short to VBUS, not for CC's 5 V.** CC1/CC2 sit next to VBUS in the receptacle (A4/A5, B4/B5); a twisted plug, debris or moisture shorts them directly, and non-compliant adapters start at 20 V even into a 5 V-only port, so TI requires CC protection at least 22 V DC tolerant, 24 V recommended (TPD2S300 datasheet 7.1). A 5.5 V clamp (ESD441, TI's CC pick for a 5 V-only port in SLVAF82B Table 7-1) survives VBUS through a cable's 56 kohm Rp (0.26 mA at 20 V) but conducts amps on a direct short and fails. Use a 24 V clamp (ESD752, ESD2CAN24: SLVAF82B Table 8-2) or a short-to-VBUS protector (TPD2S300, TPD4S311).
- **Never put CC on a spare channel of the D+/D- ESD array.** On a short to VBUS the shared array fails and takes the data lines with it.
- **A sink with only Rd on CC needs no CC TVS.** Nothing on the net but a 5.1 kohm resistor to GND; Adafruit QT Py ESP32-S3, Seeed XIAO ESP32-S3 Sense and SparkFun Thing Plus ESP32-S3 put none there. Protect CC when a CC/PD controller pin is on it.
- **CC receiver capacitance: 200-600 pF per PD spec.** TVS on CC contributes to this -- choose TVS capacitance that keeps total within range. Can eliminate the need for extra CC capacitors.

### USB-C PD Controllers

- **Sink-only PD, no MCU: STUSB4500 (ST, QFN-24).** NVM-configurable 5/9/15/20V profiles. Connect VBUS_EN output to load switch.
- **Sink PD, no MCU, simpler: IP2721.** Hardware-only PD parsing via CC, auto-requests matching voltage. Less flexible than STUSB4500 but fewer external components.
- **Sink PD with MCU: FUSB302B (ON Semi, WLCSP-9 or QFN-14).** I2C-controlled PD PHY requiring firmware policy engine. Most flexible, highest development effort. Used in MNT Pocket Reform charger port.
- **Source PD: TPS65987D (TI, BGA-56).** Dual-port USB-C PD controller with integrated back-to-back VBUS FETs (25 mohm Rds_on each at 25C). Internal flash for configuration -- no external MCU for basic operation. Power duo mode parallels both internal FETs for 12.5 mohm total, enabling >5A source.
- **CC logic only (no PD): TUSB320 (TI) or WUSB3801 (WillSemi).** DFP/UFP/DRP detection, cable orientation. WUSB3801 has internal Rp/Rd, I2C status output, and can limit charger current based on CC advertisement. TUSB320LA adds I2C role configuration.

### Dead Battery Provision

- **TPS6598x boots from VBUS when VIN_3V3 is absent.** Internal high-voltage LDO converts up to 22V VBUS to 3.3V. Presents Rd on CC even without local power, so a dead device can negotiate charging. Required for battery-powered USB-C devices that may fully discharge.
- **VIN_3V3 takes precedence.** When VIN_3V3 becomes available, clearing the Dead Battery Flag switches LDO_3V3 supply from VBUS LDO to VIN_3V3 without brown-out. If VIN_3V3 drops below 2.85V, firmware hard-resets and reboots in dead battery mode.
- **Dual VBUS inputs (TPS65988): reverse-current blocking between ports.** Path from each VBUS to internal LDO blocks reverse current -- power on one VBUS won't leak to the other.

### VBUS Power Path

- **Sink VBUS capacitance: 10 uF max equivalent.** Not a hard cap limit -- the spec limits the inrush charge to 50 uC at 5V. More capacitance is fine behind a current-limiting switch (e.g., Diodes AP2162/AP2172).
- **Host/source VBUS decoupling: >= 96 uF near connector.** Source must handle load transient dI/dt up to 150 mA/us without unacceptable VBUS droop.
- **Ferrite bead on VBUS: 47-1000 ohm at 100 MHz, resistive to ~1 GHz.** Place between connector VBUS pin and downstream regulator. Taiyo-Yuden BK0603HS330-T is a proven choice for FTDI designs.
- **10 nF Y-cap from VBUS to chassis GND, after ferrite bead.** Shunts CM noise to chassis. Do not exceed 10 nF -- leakage current violates USB spec.
- **No power back-feed into VBUS under any circumstance.** Self-powered devices must isolate local supply from VBUS when cable is disconnected. FTDI FT-series: use PWREN# with P-FET soft-start (IRLML6402TRPBF + RC circuit). SiLabs EFM32: FDC6420C dual N/P-FET switches between VBUS and battery power.

### VBUS Protection (Source)

- **TPS65987DDH: internal FET opens in <15 us on VBUS short to GND at 5V.** External discrete FET paths typically take >150 us -- internal paths protect before the 5V rail browns out. At 20V, current spikes to ~35A before the 30A hardware comparator opens the FET in <7 us.
- **OCP trip point is dynamic: 10A default, 20A during voltage transitions.** When VBUS transitions from 5V to higher voltage, TPS65987DDH widens HW OCP from 10A to 20A for ~100 ms to handle non-compliant device inrush, then returns to 10A.
- **Overcurrent clamping at 5V is separate from OCP.** OCC regulates internal FET Rds_on to clamp current at a programmable level (see IOCC table in SLVA994), holds for 640 us deglitch, then opens. Protects shared 5V rail from browning out other system loads.
- **OVP: set to 5% of negotiated max voltage.** Configurable via Application Customization Tool. Do NOT use fixed OVP trip point when sourcing 5V -- a 24V fixed OVP would let 20V through on a 5V contract.
- **Reverse current protection for multi-port systems.** Two ports closing onto same SYSPWR rail: if port 2 has 5V adapter and port 1 has 20V, port 2 must enable RCP (blocking FET) to prevent back-feeding 20V into the 5V adapter. TPS65987DDH handles this with internal back-to-back FETs.

### D+/D- Routing

- **Series resistors depend on PHY family.** FTDI FT2xxB/FT2xxX/FT12x/FT31xD: 27 ohm required. FTDI FT2xxR/FT313H: 0 ohm (internal). SiLabs EFM32: 15 ohm. Most integrated-PHY MCUs: check datasheet -- many need no external resistor.
- **Optimum trace length for HS: 50 mm.** TI TUSB121x guideline: 0.5 ns one-way delay max = 75 mm in FR4. Eye diagram degrades noticeably above 100 mm. At 50 mm (2 inches), eye is clean; at 250 mm (10 inches), eye is nearly closed.
- **Max external capacitance on D+/D-: 1.5 pF per line (typical).** TI TUSB121x allows up to 4 pF including discrete components (excludes trace capacitance). Budget: TVS array + test pad + connector parasitics. TVS with >0.75 pF/line eats half the budget.
- **Crosstalk spacing: >= 4x dielectric height from USB pair to other high-speed traces.** If adjacent signals have faster edges or larger swings, increase to >= 0.75 mm (30 mil). TI AM335x guide: 5x trace width isolation from other signals, 3x width between D+/D- (3W rule).
- **D+/D- length mismatch budget: 150 mil max (spec includes cable).** USB 2.0 HS skew limit is 100 ps. At ~6 ns/inch propagation, that's 15.2 mm (600 mil) total for the entire link including cable (100 ps cable budget per spec). After cable and guard band, PCB budget is ~3.8 mm (150 mil). Target 1.27 mm (50 mil), 0.5 mm (20 mil) is best.
- **No stubs.** Test points must be fly-by (signal routes through the pad). TI AM335x: test points of any kind are NOT permitted on D+/D- pair. If stubs are unavoidable, keep under 0.5 cm.
- **USB 2.0 mux for Type-C receptacle is optional but improves SI.** Spec allows shorting D+ to D+ and D- to D- across both orientations. The resulting stub can degrade HS signal quality. A USB 2.0 mux eliminates the stub but adds cost and complexity -- usually not needed for FS or LS.

### ESD Protection

- **Component order from connector inward: TVS -> CMC -> series resistors -> PHY.** TVS must clamp before the transient reaches the CMC. CMC saturates on full ESD and passes the pulse through if placed first.
- **IP4220CZ6 (NXP): <1 pF/line, SOT-457.** Max output voltage 9V during ESD -- higher than most PHY tolerance ratings, but most energy is dissipated in the TVS. Tested to IEC 61000-4-2 8 kV contact on EFM32GG-STK3700.
- **SRV05-4: one name, different silicon.** Semtech's original (SOT-23-6) is 3 pF typ (datasheet 2018-12-15; JLC lists C13612 at 3 pF): fine for full-speed, over the 1.5 pF high-speed budget. Suggested by FTDI for all their USB IC families alongside Littelfuse PGB1010603. Most JLC parts sold as SRV05-4 are clones listing 0.3-1 pF (hongjiacheng C7420376 1 pF, MSKSEMI C2836319 0.6 pF); read the clone's own datasheet, not Semtech's.
- **USB 2.0 CMC: Murata DLW21HN900SQ2 (0805 inch / 2.0 x 1.2 mm, 90 ohm CM at 100 MHz) [20, 21].** CMCs degrade signal quality -- TI TUSB121x: "should only be used if EMI enhancement is absolutely necessary." Place after ESD TVS, before PHY. Do NOT use USB 2.0 CMCs on USB 3.x: Murata lists this part for USB 2.0 only, and its chart wants >= 2.5 GHz differential cutoff for 5 Gbps even with an equalizing receiver [21] -> `guides/emc.md`.
- **Ferrite beads on D+/D- are prohibited by USB spec.** Only allowed on VBUS.

### Connector and Shield Grounding

- **Connector shell to chassis GND, not signal GND.** Multiple vias from shell pads to chassis ground pour. If chassis and signal ground are unified, connect to ground plane nearest connector.
- **RC between shield and signal GND: 1 Mohm + 4.7 nF in parallel.** Provides controlled DC reference and AC coupling. Alternative: 0 ohm direct -- depends on system grounding architecture. FTDI: provide pads for zero-ohm or capacitor between shield and signal GND for flexibility during EMC testing.
- **Connector shell makes first contact on cable insertion.** USB connector pin length: power/GND leads longer than signal leads. Shield of cable contacts outer shell before any signal pins engage. This discharges ESD to chassis before it reaches D+/D-.

### USB-C Connector Manufacturing

- **Hybrid (SMT + THR) connectors need special stencil parameters.** Solder paste grain size 5 (not standard 4), print speed 20 mm/s (not 40), squeegee force 70 N (not 50), 45-degree plastic squeegee angle, two print cycles. Target 75% minimum hole fill depth.
- **Mid-mount connectors: increase milling edge distance from 0.80 mm to 1.00 mm (center of lowest pin row to milling contour center).** This gives 425 um routing width instead of 225 um for B2/B3 and B10/B11 differential pairs. Requires +/- 50 um pick-and-place accuracy -- discuss with EMS.
- **Reflow direction: connector face or pin row enters oven first.** Prevents bending from non-simultaneous solder melting across pin rows.

## Common Mistakes

- **ESD TVS placed after CMC.** The CMC sees the full ESD transient, saturates, and passes the pulse to the PHY. TI AM335x and TUSB121x guides both specify: ESD device closest to connector, CMC after.
- **VBUS capacitance exceeds 10 uF equivalent without current limiting.** Host overcurrent protection trips on inrush, causing repeated connect/disconnect cycles. The 10 uF limit is charge-equivalent (50 uC at 5V) -- larger caps are fine behind a soft-start switch like AP2162.
- **Missing D+ pull-up on full-speed device.** FS requires 1.5 kohm pull-up on D+ to 3.3V for host detection. Most MCU USB peripherals handle this internally -- but EFM32 low-speed mode has an internal pull-up of ~2.2 kohm (out of spec), requiring an external 4.7 kohm in parallel to D- via USB_DMPU pin.
- **Non-standard charger pulls CC high when Rd disabled.** Legacy A-to-C cables have 56 kohm Rp inside the cable. If the charger pushes VBUS above 5V (Quick Charge, etc.) and Rd is not active, CC gets pulled to VBUS voltage. Without a zener/TVS on CC, this can damage the CC controller. V_CC = V_BUS * 0.0835 with Rd enabled (safe at 20V = 1.67V), but with Rd disabled, CC = VBUS.
- **Crossing reference plane splits with D+/D- traces.** Return current detours around the split, creating a radiating loop. If unavoidable, stitch with 100 nF 0603 cap per trace near the crossing point. Cross at 90 degrees to minimize coupling.

## Formulas

**Maximum trace length from rise time:**
**Rule of thumb:** 75 mm max for USB 2.0 HS. 50 mm optimal. FS tolerant to ~600 mm.
**Formula:** L_max = t_rise * v_prop * 0.1, where v_prop ~ 150 mm/ns (FR4 stripline)
**Example:** USB 2.0 HS rise time ~4 ns -> L_max = 4 * 150 * 0.1 = 60 mm. Conservative -- allows margin for connector and via parasitics. TI recommends 75 mm practical max.

**FS skew budget allocation:**
**Rule of thumb:** Match D+/D- within 50 mil (1.27 mm) on PCB.
**Formula:** Total skew budget = t_rise / 10 = 20 ns / 10 = 2 ns (FS). At 6 ns/inch -> 8.5 mm (333 mil) total link budget. Subtract 100 ps cable skew (per spec) -> 5.9 mm (233 mil) for host + device combined.
**Example:** Two boards at 2.5 mm (100 mil) each + cable at 0.84 mm (33 mil) = 5.9 mm (233 mil) total. Comfortable margin at 1.27 mm (50 mil) per board.

## Sources

### Related Rules

- `protection/esd.md` -- ESD protection placement and design for USB connectors

### References

1. Embedded Hardware Design -- USB 2.0 PCB Layout Guidelines: https://embeddedhardwaredesign.com/usb2-0-pcb-layout-guidelines/
2. Silicon Labs AN0046 -- USB Hardware Design Guidelines: https://www.silabs.com/documents/public/application-notes/an0046-efm32-usb-hardware-design-guidelines.pdf
3. TI SPRABT8A -- AM335x USB Layout Guidelines: https://www.ti.com/lit/an/sprabt8a/sprabt8a.pdf
4. TI SWCA124 -- TUSB121x USB 2.0 Board Guidelines: https://www.ti.com/lit/pdf/swca124
5. FTDI AN_146 -- USB Hardware Design Guidelines for FTDI ICs: https://ftdichip.com/wp-content/uploads/2020/08/AN_146_USB_Hardware_Design_Guidelines_for_FTDI_ICs.pdf
6. Espressif -- USB Type-C Hardware Design Guide: https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_overview/usb_typec_hardware_guide.html
7. TI SLYY109 -- USB Type-C Primer: https://www.ti.com/lit/pdf/slyy109
8. Benson Leung -- How to Design a Proper USB-C Power Sink: https://medium.com/@leung.benson/how-to-design-a-proper-usb-c-power-sink-hint-not-the-way-raspberry-pi-4-did-it-f470d7a5910
9. Dubious Creations -- Designing with USB-C: Lessons Learned: https://dubiouscreations.com/2021/04/06/designing-with-usb-c-lessons-learned/
10. Hackaday -- All About USB-C: Resistors and Emarkers: https://hackaday.com/2023/01/04/all-about-usb-c-resistors-and-emarkers/
11. Hackaday -- All About USB-C: Example Circuits: https://hackaday.com/2023/08/07/all-about-usb-c-example-circuits/
12. onsemi AN-5086 -- USB Type-C CC Pin Design Considerations: https://www.onsemi.com/pub/Collateral/AN-5086-D.PDF
13. TI SLYY145 -- USB Type-C and USB PD Power Path Design Considerations: https://www.ti.com/lit/slyy145
14. TI SLVA994 -- USB PD Power Path Performance and Protection: https://www.ti.com/lit/an/slva994/slva994.pdf
15. Wurth ANE009 -- Production Guide USB 3.1 Type C (Connector Footprint): https://www.we-online.com/components/media/o563289v410%20ANE009a_EN.pdf
16. TI SLVAE65 -- Dead Battery Application (TPS6598x): https://www.ti.com/lit/an/slvae65/slvae65.pdf
17. USB-IF -- USB Type-C Cable and Connector Specification Release 2.5 (March 2026), Tables 4-28, 4-35 to 4-38: https://www.usb.org/document-library/usb-type-cr-cable-and-connector-specification-release-25
18. TI SLVSDL1 -- TPD2S300 USB Type-C Short-to-VBUS and IEC ESD Protector for the CC Pins: https://www.ti.com/lit/ds/symlink/tpd2s300.pdf
19. TI SLVAF82B -- ESD and Surge Protection for USB Interfaces: https://www.ti.com/lit/an/slvaf82b/slvaf82b.pdf
20. Murata -- DLW21HN900SQ2 data sheet (2022-06-13): https://www.murata.com/en-us/products/productdetail?partno=DLW21HN900SQ2%23
21. Murata -- Common Mode Choke Coil / Noise Filter selection chart, USB 2.0/3.0/3.1 (read 2026-11-06): https://www.murata.com/-/media/webrenewal/products/emc/emifil/cmcc/pdf/usb.ashx
