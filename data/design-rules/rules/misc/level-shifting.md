# Level Shifting

> Voltage translation topology selection, specific ICs, speed limits, bidirectional gotchas.

## Quick Reference

- **I2C/SMBus: LSF0102 or PCA9306; TXS also supports open-drain buses.** TXB requires push-pull drivers and is unsuitable for I2C [7, §7.3.5; 8, §7.1; 9-10].
- **SPI: SN74AXC4T774 has independent DIR per channel; TXU0304 has fixed 3-forward/1-reverse directions.** AXC4T774 supports up to 310Mbps at 1.8V -> 3.3V; TXU0304 up to 200Mbps at 3.3V -> 5V, subject to datasheet loading/timing [11-12, p.1].
- **TXB0104: drivers must supply at least +/-2mA; load <= 70pF.** External pull-ups/pull-downs must be > 50K; OE disables all channels together [7, §7.3].
- **BSS138: select by the exact manufacturer's low-VGS specifications.** Threshold voltage alone does not guarantee a valid LOW at the bus sink current; use LSF0102 for characterized low-voltage translation [3, pp.2-3; 9; 13, p.2].
- **5V -> 3.3V with LVC: verify the selected part's recommended VI range and power-off tolerance.** A family name or an absolute-maximum rating alone is insufficient [1, §5].

## Design Rules

### Topology Decision Table

| Interface | Topology | Recommended IC |
|-----------|----------|---------------|
| I2C / SMBus | Pass-FET auto-direction | TI LSF0102 (0.95V translation examples), TI PCA9306 (VREF1 >= 1.2V); verify bias circuit [9-10] |
| SPI | Direction-controlled or fixed direction | SN74AXC4T774 (0.65-3.6V), TXU0304 (1.1-5.5V) [11-12] |
| UART (fixed direction per line) | Direction-controlled | SN74AXC2T45 or SN74LXC2T45 [2, Table 1-1] |
| GPIO (bidirectional, push-pull) | Auto-direction with weak DC drive | TXB0104: VCCA=1.2-3.6V, VCCB=1.65-5.5V, VCCA <= VCCB [7, p.1] |
| JTAG | Direction-controlled or fixed direction | SN74AXC4T774, TXU0304 [2, Table 1-1] |
| QSPI / SDIO | Protocol-specific auto-direction | TXB0106 (Quad-SPI), TXS0206 / TWL1200 (SDIO/SD/MMC); check the selected part's timing [2, Table 1-1] |
| Parallel bus | FET switch when buffering is unnecessary | CB3T or TVC; check clamp level and direction requirements [1, §4] |
| 8-bit GPIO / RGMII | Direction-controlled | SN74AXC8T245 or SN74LXC8T245 [2, Table 1-1] |

### BSS138 Discrete Circuit

- **Do not combine BSS138 specifications from different manufacturers.** At 25 degrees C, onsemi BSS138 has VGS(th)=0.8-1.5V at ID=1mA, and maximum RDS(on)=3.5 ohm at VGS=10V or 6 ohm at 4.5V, both at ID=0.22A; neither rating establishes operation at 1.8V [13, p.2].
- **Gate to the low-side supply, source to the low-side bus, drain to the high-side bus.** AN10441 covers Standard-mode and Fast-mode I2C, with VDD_high >= VDD_low in normal operation; its example uses 3.3V and 5V [3, pp.2-3].
- **Size both pull-ups for rise time and the combined LOW-state sink current.** AN97055 recommends similar Rp * Cbus on each side; a universal 1K-10K range does not establish compliance -> `interfaces/i2c.md` [4, p.13].
- **Powered-down isolation is directional.** With the low-side supply at 0V the FET isolates that side; this does not establish arbitrary hot-swap or high-side-power-off isolation [3, p.3; 4, pp.11-12].

### Pass-FET Auto-Direction (LSF, NVT, PCA9306)

- **Keep manufacturer-specific bias limits.** TI LSF0102's standard bias circuit requires the high supply >= low reference + 0.8V; TI PCA9306 specifies VREF1 >= 1.2V and VREF2 >= VREF1 + 0.6V. LSF0102 Vref_A must be the lowest signal/reference voltage; EN/VREFB are biased nodes, not simply a second supply pin [9, §8.2.1.1; 10, §6.3].
- **NXP NVT20xx/PCA9306: A-side pull-ups can be omitted when VCC(B) - VCC(A) >= 1V.** Below 1V delta, both sides need pull-ups; include both currents when the switch is ON. Nexperia AN90033 specifies pull-ups on both sides for its open-drain LSF examples [5, §5.1; 6, §3.1].
- **200K reference resistor: use one per NVT device.** Tie EN to VREFB and pull that node up through the resistor. NXP recommends 0.1uF from VREFB to GND but notes approximately 100ms power-up with that filter [5, pp.7,20].
- **Push-pull on LSF requires fixed direction or controlled tri-state turnaround.** Opposing HIGH/LOW drivers cause contention: AN90033's illustrative 3.3V / (50 + 5 + 50 ohm) = 31.4mA, not an acceptable operating point [6, §3.2; 9, §8.2.1.2.1].
- **15mA is a pull-up-sizing guideline, not a universal channel absolute maximum.** TI LSF0102's sizing procedure targets about 15mA through the switch for a 260-350mV drop; the external driver must also sink any local pull-up current. Data rate depends on voltages, drive and capacitance, not just propagation delay [9, §§8.1,8.2.1.2.2].

### Auto-Direction with Edge Accelerators (TXB, TXS)

- **TXB0104: weak DC buffers with one-shots.** Its 100Mbps figure applies at VCCA=3.3V with the specified test loading; lower voltages have different timing limits. Check the timing table for the exact package and rails [7, §§5.12-5.21,7.3].
- **TXS0108E: pass-FET with edge accelerators for open-drain or push-pull.** Headline limits are 110Mbps push-pull and 1.2Mbps open-drain; use the corresponding voltage/load timing table. Internal pull-ups are 40K while LOW and 4K while HIGH, disabled with OE LOW [8, §§1,5.10-5.13,7.3.5].
- **Reflection round-trip delay must fit inside the one-shot duration.** TI gives 10-30ns across TXB/TXS and recommends < 70pF unless the selected datasheet says otherwise; neither a universal 50mm trace limit nor a wire-length guarantee follows [2, pp.3,6-8].
- **External resistors have different effects on TXB and TXS.** TXB needs > 50K pull-ups/pull-downs. TXS accepts additional pull-ups if LOW-state current/VOL and timing remain valid; SCEA054A recommends < 1mA sink current for TXS0108E and >= 50K if a pull-down is necessary [7, §7.3.5; 14, pp.2,8-13].
- **Check input transition times in the voltage-specific datasheet table.** SCEA135's slow-edge failure example is 2.4us/V; it is not a universal 1V/us limit or evidence that TXS cannot translate I2C [2, pp.4-5].

### Direction-Controlled Translators

- **SN74LXC8T245: up to 420Mbps with Schmitt-trigger inputs and dynamic I/O pull-downs.** This is a device capability subject to its supply/load timing, not a blanket speed for every translation voltage [2, Table 5-1].
- **SN74AXC4T774 DIR and active-LOW OE are referenced to VCCA.** Set each DIR to the intended channel direction, and pull OE to VCCA to keep ports high impedance during power transitions; resistor sizing depends on the control driver [11, pp.1,3].
- **SN74AXC4T774 for SPI:** SCLK/MOSI/CS master-to-slave, MISO slave-to-master. TXU0304 implements those directions without DIR pins [11-12].

### FET-Switch Translators (CB3T, CBT, TVC)

- **Choose the actual clamp architecture.** CB3T, CBT and TVC are not interchangeable transmission gates: CB3T clamps near its supply, CBT translation needs the specified bias arrangement, and TVC uses a reference transistor plus pull-ups for up-translation [1, §4].
- **CB3T up-translates to about 2.8V only at VCC=3V, TA=25 degrees C, IO=1uA.** This suits 5V TTL thresholds but not 5V CMOS. Use HCT/AHCT for a full 5V CMOS output from a compatible 3.3V input [1, §§4,6].

### 5V Tolerant Inputs (No Translator Needed)

- **For 3.3V -> 5V CMOS, HCT/AHCT accepts TTL-compatible inputs.** Verify VOH at the actual driver load and the receiving VIH; do not assume every 3.3V output meets a 5V input [1, §§1,6].
- **5V -> 3.3V: check the selected LVC part's VI limit independently of VCC.** Transceiver I/Os need their own overvoltage/power-off check; do not assign a 5.5V limit to every AUC/AVC part [1, §5].
- **Slow-edge duty-cycle distortion is device-dependent.** SCEA035A illustrates a 50% -> 60% change; the switching point is not equal to VCC, and that example is not a guaranteed correction factor [1, §5].

## Common Mistakes

- **Power sequencing inferred from the family name.** TXS0108E permits either supply to ramp first while requiring VCCA <= VCCB for operation; keep OE LOW until supplies are ready. LSF/NVT reference bias and any disconnected rail need a circuit-specific check [8, §§1,8.3; 9, §8.2.1.1; 5, §8].
- **Treating NVT as an I2C capacitance-isolating buffer.** Its ON channels connect the bus capacitances; adding the translator does not reset the bus-capacitance budget [5, §9].
- **Temperature-induced ringing treated as a decoupling-only problem.** Output impedance changes with temperature; one-shots can amplify reflections into oscillation. Check trace/load behavior across temperature, or use TXU/LXC for suitable fixed-direction signals [2, p.7].

## Formulas

**Pull-up current budget for pass-FET translators:**
**Rule of thumb:** Use the weakest driver's guaranteed sink current and receiver LOW threshold; include pull-ups on both sides and switch voltage drop [5, §6; 6, §4].
**Formula:** I_sink = (VCC(A) - VOL) / Rpu_A + (VCC(B) - VOL) / Rpu_B (first-order, neglecting switch drop). With B-side pull-up only, Rpu_min = (VCC(B) - VOL) / IO_max.
**Example:** B-side-only NVT configuration, VCC(A)=1.8V, VCC(B)=3.3V, IO_max=3mA, VOL=0.4V -> Rpu_min = (3.3 - 0.4) / 0.003 = 967 ohm -> use 1K nominal. This is only a current-budget example: add tolerances, switch drop, both directions' LOW thresholds and rise-time checks before selecting the final value [5, §§6.1-6.2].

## Sources

### Related Rules

- `interfaces/i2c.md` -- I2C pull-up design, bus capacitance, speed modes
- `interfaces/spi.md` -- SPI interface timing and layout
- `interfaces/uart.md` -- UART level requirements, RS-232/RS-485 voltage levels

### References

1. TI SCEA035A (June 2004) -- Selecting the Right Level-Translation Solution: https://www.ti.com/lit/pdf/scea035
2. TI SCEA135 (June 2023) -- Do's and Don'ts for TXB/TXS Level-Shifters: https://www.ti.com/lit/pdf/scea135
3. Nexperia AN10441 (Rev.2, February 2020) -- Level Shifting in I2C-Bus Design: https://assets.nexperia.com/documents/application-note/AN10441.pdf
4. Philips AN97055 (4 August 1997) -- Bidirectional Level Shifter for I2C-Bus: https://cdn-shop.adafruit.com/datasheets/an97055.pdf
5. NXP AN11127 (Rev.2.0, January 2023) -- Bidirectional Voltage Translators NVT20xx/PCA9306: https://www.nxp.com/docs/en/application-note/AN11127.pdf
6. Nexperia AN90033 (Rev.1, August 2022) -- LSF010x Auto-Sense Applications: https://assets.nexperia.com/documents/application-note/AN90033.pdf
7. TI TXB0104 (SCES650K) -- Datasheet: https://www.ti.com/lit/gpn/txb0104
8. TI TXS0108E (SCES642L) -- Datasheet: https://www.ti.com/lit/gpn/txs0108e
9. TI LSF0102 (SDLS972B) -- Datasheet: https://www.ti.com/lit/gpn/lsf0102
10. TI PCA9306 (SCPS113O, September 2023) -- Datasheet: https://www.ti.com/lit/gpn/pca9306
11. TI SN74AXC4T774 (SCES898C) -- Datasheet: https://www.ti.com/lit/gpn/sn74axc4t774
12. TI TXU0304 (SCES935A, October 2021) -- Datasheet: https://www.ti.com/lit/gpn/txu0304
13. onsemi BSS138 (BSS138/D Rev.7, April 2024) -- Datasheet: https://www.onsemi.com/pdf/datasheet/bss138-d.pdf
14. TI SCEA054A (March 2018) -- Effects of External Pullup and Pulldown Resistors on TXS and TXB Devices: https://www.ti.com/lit/pdf/scea054
