# UART

> Baud rate tolerance, RS-232/RS-485 implementation, USB-UART bridges, auto-reset circuits, flow control.

## Quick Reference

- **Baud rate tolerance: +/-3.3% total mismatch** between TX and RX (8N1, 10-bit frame). Each side should contribute <1.6%. Ceramic resonators (+/-0.5% + 0.5% drift) are fine. Two internal RC oscillators (2-5% each) will fail.
- **RS-485 termination: 120 ohm at each end of the bus.** No more, no less. Use 1/8 unit load transceivers (MAX3485E, SN65HVD3082E) for up to 256 nodes.
- **RS-232 charge pump caps: X5R or X7R ceramic, 100 nF, >=10V.** Z5U/Y5V lose 50-80% capacitance at operating voltage -- charge pump fails to reach +/-5V.
- **USB-UART bridge: CH340N for cost, CP2102N for driver-free, FT232RN for industrial.**

## Design Rules

### RS-232 Level Translation

- **MAX232 charge pump caps: all four must match value and dielectric.** Mismatched caps -> asymmetric voltage rails -> TX output clips on one polarity. Use 100 nF X5R or X7R for all four positions.
- **Unused receiver inputs can float.** Internal 5 kohm pull-down to GND holds output in defined state.
- **Unused transmitter inputs: tie to VCC or GND.** Floating inputs cause erratic charge pump oscillation, increasing supply current and conducted emissions.
- **Cable capacitance limit: 2500 pF.** At ~20 pF/ft mutual capacitance (typical unshielded cable) + ~10 pF/ft stray: ~30 pF/ft total -> max ~80 ft. Shielded cable has higher capacitance per foot -> shorter max distance.
- **Standard max data rate: 20 kbps (EIA/TIA-232-F, 30 V/us slew rate limit).** Modern transceivers support 250 kbps-1 Mbps by exceeding the slew limit. Both ends must support the higher rate.

### RS-485 / RS-422

- **Failsafe biasing: 528 ohm pull-up on A, 528 ohm pull-down on B** (calculated for 120 ohm terminated bus, VCC = 4.75V, VAB = 250 mV including noise margin). Without bias, a floating bus (all transmitters tri-stated) produces 0V differential -> receiver output is undefined -> random data to UART -> false start bits and framing errors.
- **True failsafe receivers (MAX3430, ISL3170E):** threshold offset shifted to -200 mV to -30 mV so 0V differential reads as logic high. Still need external bias resistors for open-circuit and short-circuit bus conditions.
- **Failsafe bias adds ~20 unit loads.** With standard 32 UL drivers and 1/8 UL transceivers: max devices = (32 - 20) / 0.125 = 96. Plan bus loading budget accordingly.
- **Rate * Length product: <=10^7.** 115200 bps * 86 m = ~10^7. Above this limit, cable attenuation causes bit errors. At low rates, DC resistance of cable limits length: 22 AWG, 120 ohm UTP reaches ~1200 m before cable resistance matches termination (6 dB loss).
- **Stub length: proportional to driver rise time.** L_stub_max = (t_rise / 10) * v * c. Typical: <0.3 m at 1 Mbps (t_rise ~10 ns), <3 m at 100 kbps. Long stubs create reflections at 2x stub delay.
- **Noisy environment: replace 120 ohm termination with two 60 ohm low-pass filters.** Match resistor values to 1% -- tolerance mismatch causes unequal filter rolloff and converts common-mode noise to differential noise.
- **RS-422 is simplex: one driver, up to 10 receivers, single termination.** RS-485 is multipoint: up to 32 UL (or 256 with 1/8 UL). Do not confuse them.
- **Galvanic isolation:** ADM2485 (ADI, 2.5 kV RMS, integrated isoPower). ISO3082 (TI, 5 kV RMS, needs external isolated supply). TVS goes on the bus side of the isolator, not the logic side.
- **TVS protection:** bidirectional TVS between A/B and GND. Add 10-20 ohm series resistors between connector and transceiver for higher-energy transients (industrial/outdoor). ESD design rules -> `protection/esd.md`.

### USB-UART Bridges

- **CH340N:** SOIC-8, needs 12 MHz external crystal. 2 Mbps max. No EEPROM -- all units enumerate with same VID/PID. CH340C variant: SOIC-16, internal oscillator (no crystal).
- **CP2102N:** QFN-28/QFN-24, internal oscillator, 3 Mbps max. Built-in kernel driver on Windows/Mac/Linux since ~2012. Internal EEPROM for custom VID/PID/serial number. Best cost/feature balance.
- **FT232RN:** SSOP-28, internal oscillator, 3 Mbps max. EEPROM for custom PID/VID. Mature drivers but historical issues (2014 driver bricking clones). Best driver support on legacy/industrial OSes.
- **All three: 100 nF on each VCC/VDDIO pin.** USB-side ESD protection between connector and bridge IC -> `protection/esd.md`.

### Auto-Reset Circuit (ESP32 / Arduino)

- **DTR/RTS cross-coupled through two NPN transistors (MMBT3904) or N-MOSFETs (2N7002).** DTR controls EN (reset via Q1 collector-emitter), RTS controls IO0 (boot mode via Q2 collector-emitter). Cross-coupling ensures both DTR=low and RTS=low simultaneously results in neither EN nor IO0 pulled down -- prevents accidental reset during normal serial traffic.
- **EN pin: 10 kohm pull-up + 1 uF cap to GND.** The cap creates an RC delay so that when switching from (DTR=1,RTS=0) to (DTR=0,RTS=1), EN rises slower than IO0 falls. This creates a transient (EN=0, IO0=0) state that the bootloader detects as program-download request. Without the cap, EN and IO0 transition simultaneously and bootloader entry fails.
- **Cap value: 1-10 uF.** Espressif DevKitC uses 0.1 uF but recommends >=1 uF for reliable boot entry. Larger caps (>10 uF) delay reset release excessively.
- **IO0: 10 kohm pull-up only, no cap.** IO0 has an internal pull-up in ESP32. A cap on IO0 would delay the boot mode signal and cause missed boot entry.

### Flow Control

- **At >=921600 baud, use hardware flow control.** Software flow control cannot react fast enough -- buffer overruns before XOFF is processed.

### Level Translation

- **BSS138 N-MOSFET (SOT-23) for 3.3V-to-5V UART.** Gate to 3.3V VDD, source to 3.3V side with 10 kohm pull-up, drain to 5V side with 10 kohm pull-up. One FET per signal. Works down to ~1.5V Vgs.
- **2N7001T (SC-70):** single-bit unidirectional, 1.65-3.6V, 100 Mbps. Better option for 1.8V-to-3.3V than BSS138.
- **Multi-channel: SN74AXC4T245** (4-bit, 1.65-5.5V both sides, direction-controlled).
- General level-shifting topology selection -> `misc/level-shifting.md`.

### Baud Rate Error

- **MCU baud rate generators introduce quantization error.** Error = (actual_baud - target_baud) / target_baud.
- **Common pitfall: 115200 from 8 MHz clock.** 8000000 / 115200 = 69.44 -> divisor 69 -> 115942 baud = +0.64% error. Fine alone, but stacks with the other end's error.
- **Ceramic resonators (~1% total):** +/-0.5% initial + 0.5% drift over temp. Leaves 2.3% margin for the other end. Safe for all standard baud rates.
- **Internal RC oscillators: 2-5% typical.** Two RC-clocked devices can exceed 3.3% budget. Fix: crystal/resonator on at least one side, or calibrate RC against USB SOF if a USB connection exists.

## Common Mistakes

- **RS-485 terminated at one end only.** A single 120 ohm at one end reflects the signal at the unterminated far end. At 115200 bps on 50 m cable, reflections cause ~10% BER. Fix: 120 ohm at BOTH ends. Remove termination from mid-bus nodes.
- **Auto-reset missing EN capacitor.** Without the RC delay, the reset pulse is too short for the bootloader to detect IO0 state. Chip resets but enters normal mode instead of download mode. Fix: 1 uF cap on EN to GND.
- **Two RC-oscillator MCUs via UART at temperature extremes.** Combined error of 4-6% exceeds 3.3% tolerance. Works on bench at 25C, fails in the field at -20C or +70C. Fix: crystal/resonator on at least one side.

## Formulas

**Baud rate tolerance:**
**Rule of thumb:** +/-3.3% total (8N1). Each side <1.6%. For long/capacitive RS-232 links: total <=2.0%.
**Formula:** error_total = |error_TX| + |error_RX|. Sampling window: +/-5 of 152 internal clocks for "normal" link (75% reliable sampling window), +/-3 of 152 for "nasty" link (50% window).
**Example:** TX crystal = +0.5%, RX ceramic resonator = +1.0% -> total = 1.5%. Safe for both normal and nasty links.

**RS-485 stub length:**
**Rule of thumb:** <0.3 m at 1 Mbps, <3 m at 100 kbps.
**Formula:** L_stub_max = (t_rise * v * c) / 10
  - v ~ 0.66 (twisted pair), c = 3 * 10^8 m/s
  - Simplified: L_stub_max ~ t_rise(ns) * 0.02 m/ns
**Example:** t_rise = 100 ns (SN65HVD3082E) -> L_stub_max = 100 * 0.02 = 2.0 m.

**RS-485 max bus length:**
**Rule of thumb:** Rate(bps) * Length(m) <= 10^7.
**Formula:** L_max = 10^7 / baud_rate
**Example:** 115200 bps -> L_max = 86 m. 9600 bps -> 1041 m (use repeater beyond 1200 m due to cable DC resistance).

## Sources

### Related Rules

- `misc/level-shifting.md` -- level-shifting topology selection for UART and other interfaces
- `protection/esd.md` -- ESD protection for USB-UART bridges and RS-485 bus connections

### References

1. ADI -- Fundamentals of RS-232 Serial Communications: https://www.analog.com/en/resources/technical-articles/fundamentals-of-rs232-serial-communications.html
2. Silicon Labs AN0059 -- UART Flow Control: https://www.silabs.com/documents/public/application-notes/an0059.0-uart-flow-control.pdf
3. TI SLLA544 -- RS-232 FAQ: https://www.ti.com/lit/an/slla544/slla544.pdf
4. SparkFun -- Serial Communication Tutorial: https://learn.sparkfun.com/tutorials/serial-communication
5. TI SCEA064A -- Level Translation for SPI, UART, JTAG: https://www.ti.com/lit/pdf/scea064
6. ADI AN-960 -- RS-485/RS-422 Circuit Implementation Guide: https://www.analog.com/en/resources/app-notes/an-960.html
7. TI SLLA272 -- The RS-485 Design Guide: https://www.ti.com/lit/pdf/slla272
8. ADI -- Clock Accuracy Requirements for UART: https://www.analog.com/en/resources/technical-articles/determining-clock-accuracy-requirements-for-uart-communications.html
9. FTDI AN_146 -- USB Hardware Design Guidelines for FTDI ICs: https://ftdichip.com/wp-content/uploads/2020/08/AN_146_USB_Hardware_Design_Guidelines_for_FTDI_ICs.pdf
10. Kazulog -- ESP32 Auto Bootloader Mechanism and Truth Table: https://kazulog.fun/en/dev-en/esp32-auto-bootloader/
