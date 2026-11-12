# GNSS Module Integration

> When integrating a GNSS module -- antenna selection, ground plane sizing, RF path, LNA power, backup battery, PPS routing.

## Quick Reference

- **SAM-M8Q: center on a 50x50mm ground plane; below 40x40mm performance can decrease significantly.** This is module-specific, not a minimum for every patch [2, pp.11-12].
- **u-blox recommends an active antenna for cable lengths above about 10cm.** Typically 15dB LNA gain suffices for receivers supporting passive antennas; > 35dB with short cables risks overload on some receivers [1, p.7].
- **SAM-M8Q V_BCKP: 1.4-3.6V operating range.** Backup preserves RTC/BBR; valid retained time/orbit data is needed for hot/warm starts [2, p.5; 6, p.17].
- **SAM-M8Q: keep components 10mm from module edges; cover >= 5mm from antenna.** The manual specifically requires tall components (h > 3mm) >= 10mm away [2, pp.11-12].
- **NEO-M9N is multi-constellation L1, not multi-band.** SAM-M8Q integrates a patch in a 15.5x15.5mm footprint; L76-L is a 10.1x9.7mm option with an embedded LNA [6, p.1; 7, p.4; 3, pp.10,40].

## Design Rules

### Antenna Selection

- **Do not select a patch from size alone.** u-blox recommends allowing about 50x50 to 70x70mm ground plane for ceramic patches; optimum gain and axial ratio depend on the specific antenna/ground combination, rather than a universal 70x70mm optimum [1, pp.16-17].
- **Patches < 17x17mm tend to show moderate navigation performance in u-blox's comparison.** The source notes an exception for its SuperSense technology; performance also depends on ground plane. Amplification cannot recover antenna signal-to-noise loss [1, p.8].
- **Chip antennas incur approximately 3dB polarization loss for RHCP GNSS signals.** u-blox's measured examples average 43.4dBHz C/N0 on an 80x40mm PCB and 34.7dBHz on a 24x15mm PCB; those board sizes are examples, not generic minimum ground planes. Prefer patch/helix where navigation performance is central [1, pp.9-10,15].
- **Ceramic patch tuning depends on its dielectric environment and ground plane.** SAM-M8Q conformal coating or potting voids its warranty; do not generalize that warranty rule to unrelated modules [1, §5.3; 2, pp.15-16].

### Ground Plane Design

- **SAM-M8Q: use at least one solid ground layer under the module, with no signal traces below it.** Route signals away on the top layer; if a layer change is necessary, make it > 20mm from the module [2, p.12].
- **External RF feed: use a controlled 50 ohm trace.** Quectel's L76/L76-L passive-antenna reference design calls for a short 50 ohm RF trace; antenna matching still requires the selected antenna's reference design [3, p.39].

### Active Antenna Power (Bias-Tee)

- **Use antenna-specific bias voltage and current.** Quectel L76/L76-L VDD_RF follows VCC (2.8-4.3V recommended); verify the antenna's operating range. Its reference design uses a 10 ohm protection resistor and RF choke >= 47nH, not a guaranteed electronic current limiter or open/short detector [3, pp.37-38,45-46].
- **NXP BGU7004/BGU7008 coax-powered example: 100nH Murata LQG15HS RF choke and 1nF VCC decoupling.** These are the AN11420 evaluation circuit values, not universal active-antenna defaults [4, pp.4,6].
- **BGU7004/BGU7008: 1.5-2.85V supply, optimized at 1.8V.** AN11420 lists NF=0.9/0.85dB, gain=16.5/18.5dB and current=4.5/4.8mA respectively; current increases during strong jamming. Input matching uses 5.6nH Murata LQW15A; both RF ports have internal DC blocking [4, pp.3-6].
- **Limit total gain at the receiver input.** u-blox states no need for antenna LNA gain above 26dB for its receivers, and warns of possible overload above 35dB with short cables. Quectel L76/L76-L instead specifies active-antenna total gain < 18dB and NF < 1.5dB; use the selected receiver's conditions [1, p.7; 3, p.36].
- **PESD5V0F1BL is the optional ESD diode in NXP's BGU7004/BGU7008 example.** AN11420 reports increasing that circuit's ESD performance from 2kV to as much as 10kV; this is not an IEC system-level immunity rating for any GNSS input [4, pp.4,6].
- **Choose SAW placement from blocker tolerance and noise budget.** Filtering before an LNA protects it from strong blockers but adds pre-LNA loss; placing the LNA first reduces the filter's noise contribution but requires an LNA that tolerates the blocker. u-blox's dual-antenna example deliberately places the LNA before the SAW [1, pp.20-21].

### Module Integration

- **SAM-M8Q VCC supply: low impedance, < 0.2 ohm.** Its manual prohibits series resistors, ferrite beads and coils in VCC; startup/backup-to-normal current can exceed steady-state current [2, pp.4,8].
- **SAM-M8Q V_BCKP: connect to VCC_IO if no backup source is available.** Avoid high resistance because switchover current spikes can cause malfunction; VCC_IO supplies RTC/BBR while present, with V_BCKP taking over below 1.4V [2, p.5].
- **SAM-M8Q VCC_IO must be supplied or the module remains in reset.** VCC_IO requires >= 2.7V and <= min(VCC + 0.3V, 3.6V); connect to VCC for a single-supply design, rather than a low-voltage host I/O rail [2, p.4; 6, p.17].
- **Quectel L76/L76-L V_BCKP: 1.5-4.5V, 3.3V typical.** Do not transfer SAM-M8Q's backup limits or VCC_IO wiring to this module [3, pp.23,45].
- **SAM-M8Q RESET_N: leave open if unused, do not drive HIGH or add capacitance to GND.** Use it for reset, not power control; capacitance can cause startup reset problems [2, pp.6,8].
- **SAM-M8Q unshielded I/O > approximately 3mm can pick up interference.** The manual proposes > 20 ohm series resistors or BLM15HD102SN1 ferrites near affected I/O; check bus rise time/loading before applying the filter [2, pp.7,18].

### PPS (Pulse Per Second) Signal

- **LEA-6T timing: 30ns RMS without compensation, 15ns with quantization-error compensation.** UBX-TIM-TP provides the next pulse's error, valid for a 1Hz time pulse in this u-blox 6 application note; these values are not specifications for every GNSS module [5, pp.4-7].
- **u-blox 6 time pulse is derived from 48MHz.** Integer division (8MHz = 48MHz / 6) avoids the additional quantization jitter seen at 10MHz. SAM-M8Q specifies a 0.25Hz-10MHz TIMEPULSE output; its 500kHz limit applies to the EXTINT frequency-aiding input [5, pp.10-11; 6, p.5; 2, p.6].
- **For improved phase noise, add an external PLL.** The u-blox 6 note recommends an external oscillator, with an OCXO instead of a TCXO when additional holdover is required [5, p.9].
- **Compensate antenna cable delay separately from arbitrary user delay.** u-blox 6's UBX-CFG-TP5 supports cable and user corrections; derive delay from the actual cable specification or calibration, not a universal RG174/RG316 velocity [5, pp.4-5].

### Interference Management

- **Assess GSM isolation using the receiver/filter combination.** u-blox's general antenna note plans >= 40dB isolation for GSM; approximately 20dB achievable in handheld layouts is insufficient without additional input filtering. Its SAM-M8Q manual separately calls for extra filtering if approximately 20dB cannot be achieved; do not treat either as a universal cellular rule [1, p.20; 2, pp.18-19].
- **A GNSS-band SAW cannot remove in-band interference.** Use shielding/layout measures for in-band sources and input filtering for out-of-band transmitters; a clock harmonic example is 315MHz * 5 = 1575MHz, not a fractional harmonic of 26MHz [1, pp.29-30].
- **Shield penetrations need filtering at the boundary.** SAM-M8Q lists Murata NFL18SP157X1A3 feed-through filtering with 34pF data-line loading; account for that capacitance on the interface [2, pp.18,21].

## Common Mistakes

- **Treating 44dBHz C/N0 as a receiver acquisition threshold.** u-blox uses average strong/high-elevation satellite C/N0 of 44-50dBHz as an integration-quality target. Designs whose strongest signals remain below 40dBHz generally have degraded TTFF/coverage/accuracy; this does not mean they cannot navigate [1, pp.5,32].
- **Expecting hot start solely because a battery is fitted.** It requires valid retained time/orbit data; SAM-M8Q can also retain RTC/BBR through VCC_IO without a separate battery [2, p.5].
- **Ultrasonic cleaning or welding near SAM-M8Q.** Its manual warns that ultrasonic processes risk damage to the receiver and excludes that damage from warranty; use the documented assembly/cleaning process [2, pp.15-16].

## Sources

### Related Rules

- `misc/rf-antenna.md` -- General RF antenna design, impedance matching, keep-out zones

### References

1. u-blox UBX-15030289 (R03, October 2019) -- GNSS Antennas Application Note: https://content.u-blox.com/sites/default/files/products/documents/GNSS-Antennas_AppNote_%28UBX-15030289%29.pdf
2. u-blox UBX-16018358 (R07, May 2020) -- SAM-M8Q Hardware Integration Manual: https://content.u-blox.com/sites/default/files/SAM-M8Q_HardwareIntegrationManual_%28UBX-16018358%29.pdf
3. Quectel L76 Hardware Design V3.3: https://centerclick.com/ntp/docs/Quectel_L76L76-L_Hardware_Design_V3.3.pdf
4. NXP AN11420 (Rev.1, October 2013) -- GPS LNA Voltage Supply via Coax Cable: https://www.nxp.com/docs/en/application-note/AN11420.pdf
5. u-blox GPS.G6-X-11007 (initial release, March 2011, preliminary) -- GPS-based Timing Application Note: https://content.u-blox.com/sites/default/files/products/documents/Timing_AppNote_%28GPS.G6-X-11007%29.pdf
6. u-blox UBX-16012619 (R07, September 2024) -- SAM-M8Q Data Sheet: https://content.u-blox.com/sites/default/files/documents/SAM-M8Q_DataSheet_UBX-16012619.pdf
7. u-blox UBX-19014285 (R08, October 2025) -- NEO-M9N-00B Data Sheet: https://content.u-blox.com/sites/default/files/NEO-M9N-00B_DataSheet_UBX-19014285.pdf
