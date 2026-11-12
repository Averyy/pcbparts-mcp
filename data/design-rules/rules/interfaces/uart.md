# UART

> Baud rate tolerance, RS-232/RS-485 implementation, USB-UART bridges, auto-reset circuits, flow control.

## Quick Reference

- **UART mismatch is receiver-dependent:** ADI's 16x-sampling, 8N1 model allows about 3.3% for a middle-75% sampling window, or 2% for a middle-50% window; include both clocks and baud-divider errors [7, Timing Accuracy].
- **Parallel-terminated half-duplex RS-485: match the cable, commonly 120 ohm at both trunk ends.** SN65HVD3082E is 1/8 UL (up to 256 nodes before extra loading); MAX3485E is 1 UL (32 nodes) [6, pp.3-4; 11, p.1; 12, p.3].
- **RS-232 pump capacitors are part/supply-specific:** TI MAX232 uses 1uF; TI MAX3232 uses four 100nF at 3.3V +/-0.3V, but other values for 5V operation [9, §1; 10, Table 9-1].
- **CH340N has an internal clock but no DTR output.** Use a bridge exposing both DTR and RTS for Espressif's two-transistor automatic boot circuit [16, §§3-4; 8, Automatic Bootloader].

## Design Rules

### RS-232 Level Translation

- **Do not substitute MAX232 and MAX3232 pump networks.** TI MAX3232 Table 9-1 gives C1=47nF and C2/C3/C4=330nF at 5V +/-0.5V, or C1=100nF and C2/C3/C4=470nF for the full 3-5.5V range. Equal values/dielectrics in all four positions are not a universal requirement [9, §1; 10, Table 9-1].
- **Unused TRS3232 receiver inputs can float; transmitter logic inputs need defined levels.** The receiver inputs have nominal 5 kohm resistors to ground; RIN, ROUT and DOUT can be left open in TI's unused-channel example [3, §1.6].
- **Separate RS-232 line levels from MCU UART levels.** TI's FAQ gives driver levels of +/-5V to +/-15V and valid received magnitudes from 3V; these are inverted relative to UART logic, not direct MCU connections [3, §1.1; 1, Electrical Characteristics].
- **Do not infer high-rate compliance from a blanket 20kbps limit.** TI MAX3232 specifies up to 250kbit/s with <= 30V/us driver slew; use its load/test conditions. Cable capacitance and the selected transceiver determine usable rate and length [10, §§3,6.7-6.8].

### RS-485 / RS-422

- **TI's external failsafe example calculates 528 ohm and selects 523 ohm for each bias resistor.** It assumes VBUS(min)=4.75V, VAB=250mV, two 120 ohm end terminations and the guide's 375 ohm common-mode loading model: 4.75 / (0.25 * (1/375 + 4/120)) = 527.8 ohm. Recalculate for supply, receiver loading, resistor tolerances and required noise margin [6, p.4, Figure 7-1].
- **True failsafe eliminates external bias for specified open/short/idle conditions.** AN-960 describes a -200mV to -30mV threshold range, but it is not universal to all parts. SN65HVD3082E specifies failsafe for open, shorted and idle bus; add external bias only when additional noise margin is needed [5, True Fail-Safe Receivers; 11, §§1,9.2.1.4].
- **Failsafe bias loading is circuit-dependent, up to 20 UL in TI's example.** Its 32-UL budget then leaves (32 - 20) / 0.125 = 96 receivers, rather than 256; include protection leakage and every other bus load [6, p.4].
- **Rate * Length < 10^7 is TI's conservative transition-region rule of thumb, not a failure boundary.** The current guide explicitly says modern cable performance exceeds it. Its approximately 1200m DC-loss example assumes 22AWG, 120 ohm UTP [6, pp.4-5].
- **Stub limits depend on output rise time, not baud alone.** TI's criterion is one-way stub delay < t_rise/10; its SN65HVD3082E example uses 500ns, not 100ns. Use the selected driver's fastest edge and the cable's velocity [6, p.3].
- **Split termination needs the capacitor as well as two resistors.** TI Figure 6-1 uses two 60 ohm resistors with a 220pF midpoint capacitor to ground instead of one 120 ohm resistor; match resistors to 1% to limit common-mode conversion [6, p.3].
- **RS-422 is single-driver per pair, not necessarily a simplex system.** AN-960 permits up to 10 receivers and shows full duplex using separate transmit/receive pairs; terminate at the receiving end of each unidirectional pair [5, RS-422, Termination].
- **ADM2485 integrates a transformer driver, not the power transformer.** Its 2.5kVrms / 1-minute isolation still requires an external transformer, rectifier and regulator for isolated bus power. ISO3082 is also 2.5kVrms / 60s per UL1577, not 5kVrms, and needs a separate bus-side supply [13, pp.1,15; 14, §§1,3,9.2].
- **AN-960's transient circuit places the TVS ahead of 10-20 ohm series resistors on the bus side.** Verify clamp voltage and pulse energy against the transceiver, and include the resistance in the differential load budget -> `protection/esd.md` [5, Transient Overvoltage Stress Protection, Figures 15-16].

### USB-UART Bridges

- **CH340N: SOP-8, internal clock, up to 2Mbps.** CH340C is SOP-16 with internal clock; verify the modem-control pins for the exact variant before copying an auto-reset schematic [16, §§2-4].
- **CP2102N: QFN-20/24/28, internal oscillator, up to 3Mbaud.** VCP operation requires a suitable host driver; the datasheet supplies drivers for Windows/Mac/Linux, not a blanket driver-free guarantee. USB descriptors and serial number are customizable in internal nonvolatile memory [15, pp.1-2,24-26].
- **FT232RN: FT232RNL is SSOP-28; FT232RNQ is QFN-32.** Internal oscillator, up to 3Mbaud, EEPROM for descriptors/configuration [17, pp.1-2].
- USB-side ESD protection -> `protection/esd.md`; use each bridge's supply/application circuit rather than one universal decoupling network [15, §4.1; 17, §6].

### Auto-Reset Circuit (ESP32 / Arduino)

- **Original ESP32 automatic boot: RTS controls EN; DTR controls GPIO0.** Follow Espressif's two-transistor circuit and truth table: both asserted together must not hold the chip in reset. Do not substitute N-MOSFETs into the NPN circuit without rechecking the truth table [8, Automatic Bootloader].
- **EN capacitor: 1-10uF to ground for Espressif's automatic reset circuit.** Espressif identifies missing EN capacitance as a cause of unreliable automatic reset. GPIO0 must be low when reset releases; it has an internal pull-up [8, GPIO0, Automatic Bootloader].

### Flow Control

- **Size RTS/CTS buffer headroom for data already in flight.** Deassert RTS before the receive buffer fills: the remote transmit registers and line still contain data. AN0059 gives no universal baud threshold where software flow control stops working [2, §3.1].

### Level Translation

- **2N7001T (SC-70/X2SON):** single-bit unidirectional translator, 1.65-3.6V supplies, up to 100Mbps. Use separate opposite-direction channels for UART TX/RX [4, pp.2,5].
- **SN74AXC4T245: 4-bit, direction-controlled, 0.65-3.6V on both supplies.** It does not translate to 5V; select another family for a 5V UART [18, §§1,3].
- General level-shifting topology selection -> `misc/level-shifting.md`.

### Baud Rate Error

- **Include baud-divider error as well as oscillator tolerance at both ends.** The 8MHz/115200 calculation depends on the MCU's oversampling/divider architecture; use the actual UART register formula and min/max clock accuracy across temperature and life [7, Timing Accuracy].
- **ADI's ceramic-resonator example budgets +/-0.5% initial plus +/-0.5% temperature/life drift per end.** That consumes the entire 2% narrow-window allowance before baud-divider error; it is not safe for every baud rate or MCU [7, Timing Accuracy].

## Common Mistakes

- **Putting a termination at every RS-485 node.** Extra parallel loads reduce differential drive; AN-960 limits the network to two parallel terminations. Its full-duplex example terminates the master receiver and most remote slave receiver, rather than every receiver [5, Parallel Termination].

## Formulas

**UART sampling budget (ADI's model) [7, Timing Accuracy]:**
**Rule of thumb:** For 8N1, 16x sampling, negligible jitter and <= 1 oversampling-clock uncertainty at the start edge, use the actual reliable sampling window; the 3.3% figure assumes the middle 75% is usable.
**Formula:** mismatch_limit = remaining_sampling_clocks / (16 * 9.5). A middle-75% window leaves 6 - 1 = 5 clocks: 5/152 = 3.29%; a middle-50% window leaves 4 - 1 = 3 clocks: 3/152 = 1.97%. Worst-case endpoint budgets add when their errors oppose; measured same-sign errors need not add.

**RS-485 stub budget [6, p.3]:**
**Rule of thumb:** Stub one-way delay < one tenth of the driver's fastest 10%-90% rise time, independent of baud alone.
**Formula:** L_stub < t_rise * v * c / 10; v is the cable velocity factor, c = 0.2998m/ns.
**Example:** TI's SN65HVD3082E example uses t_rise=500ns and v=0.78 (Belden 3109A): 500 * 0.78 * 0.2998 / 10 = 11.69m. This is the app-note example, not a guaranteed minimum rise time; shorten the limit if the selected driver's fastest edge is faster.

## Sources

### Related Rules

- `misc/level-shifting.md` -- level-shifting topology selection for UART and other interfaces
- `protection/esd.md` -- ESD protection for USB-UART bridges and RS-485 bus connections

### References

1. ADI -- Fundamentals of RS-232 Serial Communications (HTML, no revision stated; local snapshot February 2026): https://www.analog.com/en/resources/technical-articles/fundamentals-of-rs232-serial-communications.html
2. Silicon Labs AN0059.0 (Rev 1.03, January 2017) -- UART Flow Control: https://www.silabs.com/documents/public/application-notes/an0059.0-uart-flow-control.pdf
3. TI SLLA544 (January 2021) -- RS-232 Frequently Asked Questions: https://www.ti.com/lit/an/slla544/slla544.pdf
4. TI SCEA064A (March 2021), pp.2,5 -- Voltage Level Translation for SPI, UART, and JTAG Interfaces With Focus On 2N7001T: https://www.ti.com/lit/pdf/scea064
5. ADI AN-960 (Rev 0) -- RS-485/RS-422 Circuit Implementation Guide: https://www.analog.com/en/resources/app-notes/an-960.html
6. TI SLLA272D (May 2021) -- The RS-485 Design Guide: https://www.ti.com/lit/pdf/slla272
7. ADI -- Determining Clock Accuracy Requirements for UART Communications (HTML, no revision stated; local snapshot February 2026): https://www.analog.com/en/resources/technical-articles/determining-clock-accuracy-requirements-for-uart-communications.html
8. Espressif esptool -- Boot Mode Selection (ESP32), Automatic Bootloader (HTML, accessed November 2026): https://docs.espressif.com/projects/esptool/en/latest/esp32/advanced-topics/boot-mode-selection.html
9. TI MAX232 datasheet (SLLS047N), section 1: https://www.ti.com/lit/ds/symlink/max232.pdf
10. TI MAX3232 datasheet (SLLS410O, June 2021), Table 9-1: https://www.ti.com/lit/ds/symlink/max3232.pdf
11. TI SN65HVD3082E datasheet (SLLS562O, July 2023): https://www.ti.com/lit/ds/symlink/sn65hvd3082e.pdf
12. ADI MAX3483E-MAX3491E datasheet (19-1474 Rev 1, May 2019), p.3: https://www.analog.com/media/en/technical-documentation/data-sheets/MAX3483E-MAX3491E.pdf
13. ADI ADM2485 datasheet (Rev B, November 2024), pp.1,15: https://www.analog.com/media/en/technical-documentation/data-sheets/ADM2485.pdf
14. TI ISO308x datasheet (SLOS581J, August 2023): https://www.ti.com/lit/ds/symlink/iso3082.pdf
15. Silicon Labs CP2102N datasheet (Rev 1.5), pp.1-2,24-26: https://www.silabs.com/documents/public/data-sheets/cp2102n-datasheet.pdf
16. WCH CH340 datasheet (Version 3B), sections 2-4, manufacturer PDF mirrored by SparkFun: https://cdn.sparkfun.com/assets/5/0/a/8/5/CH340DS1.PDF
17. FTDI FT232RN datasheet (Version 1.5, FT_001521), pp.1-2: https://ftdichip.com/wp-content/uploads/2024/12/DS_FT232RN.pdf
18. TI SN74AXC4T245 datasheet (SCES877B, April 2024), sections 1,3: https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf
