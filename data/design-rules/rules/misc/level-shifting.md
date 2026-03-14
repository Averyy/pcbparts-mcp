# Level Shifting

> Voltage translation topology selection, specific ICs, speed limits, bidirectional gotchas.

## Quick Reference

- **I2C/SMBus: LSF0102 or PCA9306.** Pass-FET auto-direction, no one-shot, 0.65-5.5 V. Never use TXB/TXS on I2C -- active drive and slow edge false-triggering cause field failures.
- **SPI (fixed direction): SN74AXC4T774 or TXU0304.** Direction-controlled with per-pair DIR. Strongest drive, highest speed (up to 500 Mbps AXC, 200 Mbps TXU).
- **GPIO (bidirectional, push-pull): TXB0104.** 100 Mbps active drive, auto-direction. Cannot tri-state individual pins. Max 70 pF per channel.
- **BSS138 discrete: good to 400 kHz, minimum VDD_low ~2.7 V.** Won't work at 1.8 V (Vgs(th) max = 1.8 V equals VDD).
- **5 V tolerant inputs (LVC family) need no translator for 5 V -> 3.3 V.** Check VI max is independent of VCC. Duty cycle shifts with slow 0-5 V edges through 3.3 V device.

## Design Rules

### Topology Decision Table

| Interface | Topology | Recommended IC |
|-----------|----------|---------------|
| I2C / SMBus | Pass-FET auto-direction | LSF0102 (0.65-5.5 V), PCA9306 (1.0-5.5 V) |
| SPI (unidirectional) | Direction-controlled | SN74AXC4T774 (0.65-3.6 V), TXU0304 (1.1-5.5 V) |
| UART (fixed direction per line) | Direction-controlled | SN74AXC2T45 (0.65-3.6 V), SN74LXC2T45 (1.1-5.5 V) |
| GPIO (bidirectional, push-pull) | Auto-direction with active drive | TXB0104 (1.2-5.5 V) |
| JTAG | Direction-controlled | SN74AXC4T774, TXU0304 |
| QSPI / SDIO | FET switch or direction-controlled | CB3T3257 (QSPI), SN74AXC8T245 (SDIO) |
| Parallel bus (8/16-bit) | FET switch | CB3T3245, TVC (up to 32-bit) |
| 8-bit GPIO / RGMII | Direction-controlled | SN74AXC8T245 (0.65-3.6 V), SN74LXC8T245 (1.1-5.5 V, 420 Mbps) |
| Single-signal 5 V GPIO | Discrete FET | BSS138 / 2N7001T + pull-up |

### BSS138 Discrete Circuit

- **BSS138 specs:** Vgs(th) 0.4-1.8 V, Rds(on) 3.5 ohm at Vgs 2.5 V, Ciss 15 pF. BSN20 (SOT-23) equivalent.
- **Minimum VDD_low ~2.7 V.** VDD_low must exceed Vgs(th) max by >= 1 V. With Vgs(th) max 1.8 V, the FET barely turns off at 1.8 V VDD. For 1.8 V logic, use LSF0102.
- **Pull-up sizing:** match RC time constants on both sides for balanced rise times. Range 1K-10K. The original Philips AN97055 recommends keeping Rp * Cbus similar on each side.
- **Free powered-down isolation.** When VDD_low = 0 V, FET turns off, high side continues operating. Significant advantage for hot-swap or sleep-mode.

### Pass-FET Auto-Direction (LSF, NVT, PCA9306)

- **LSF0102 preferred over PCA9306 for new designs.** Lower Cio, higher ESD (4 kV HBM vs 2 kV). Both have Ron ~3.5 ohm. Functionally identical matched NMOS pass transistors with reference channel.
- **VCC(B) - VCC(A) >= 1 V: no A-side pull-ups needed.** Below 1 V delta, pull-ups required on BOTH sides -- parallel combination sets effective resistance when channel is on.
- **200K reference resistor: one per device, never shared.** Different packages have different transistor characteristics. Shared resistor causes incorrect gate bias. 0.1 uF cap on VREFB recommended but slows power-up to ~100 ms.
- **Push-pull drivers on LSF: possible on fixed-direction lines only.** Push-pull high fighting pass-FET low = 31 mA through 105 ohm path (50 ohm PMOS + 5 ohm LSF + 50 ohm NMOS). Only acceptable on UART TX, SPI MOSI where contention cannot occur.
- **Max frequency limited by pull-up RC, not IC.** With 1.8K pull-up and 30 pF bus: tr ~ 0.8 * 1800 * 30e-12 = 43 ns -> ~4 MHz. Max 15 mA per channel.

### Active-Drive Auto-Direction (TXB, TXS)

- **TXB0104: push-pull outputs, 100 Mbps.** Internal inverter pair detects direction. Cannot tri-state individual pins -- OE disables entire chip.
- **TXS0104: pass-FET + one-shot rising edge accelerator, 24 Mbps push-pull / 2 Mbps open-drain.** 10K internal pull-ups. Individual signals can tri-state (pull-up holds high, FET turns off). Better than TXB for mixed open-drain/push-pull.
- **TXS0108 oscillation is well-documented.** One-shot duration 10-30 ns; round-trip reflections longer than one-shot cause retriggering. SparkFun confirmed: even 15 cm (6 inch) jumper wires cause oscillation. Restrict to PCB-only traces < 50 mm with < 70 pF load. Prefer TXS0104 (no falling-edge one-shot) or LSF for anything with wires/connectors.
- **Do not add external pull-ups to TXB/TXS.** Pull-ups fight the weak auto-direction sensing, causing DC contention and increased Iq.

> WARNING: TXB/TXS with slow input edges (> 1 V/us) false-trigger the one-shot. Open-drain buses with pull-ups (I2C, SMBus) inherently have slow edges. This is the #1 cause of TXB0108 field failures.

### Direction-Controlled Translators

- **Strongest output drive, highest speed.** SN74LXC8T245: 420 Mbps. Schmitt-trigger inputs tolerate noisy signals. Integrated pull-downs prevent floating.
- **DIR pin must be driven -- never float.** Floating DIR causes bus contention (both sides driving). Add 10K pull-down to set default direction.
- **SN74AXC4T774 for SPI:** 4 channels with per-pair direction control, purpose-built. SCLK/MOSI/CS master-to-slave, MISO slave-to-master.

### FET-Switch Translators (CB3T, CBT, TVC)

- **Analog transmission gates: ~5 ohm Ron, ~6 pF Cio, 200+ MHz bandwidth.** Pass signal level directly (attenuated by Ron / (Ron + Rdriver) divider). No pull-ups needed or wanted.
- **CB3T family for parallel buses.** CB3T3245 (8-bit), CB3T3257 (1:2 mux), CB3T3384 (10-bit). Used on SDIO, parallel NAND, LCD data, QSPI.
- **VOH reduced by Ron drop.** With 5 ohm Ron and 10 mA: VOH drops 50 mV. At 1.8 V with VIH = 0.65 * VCC = 1.17 V, verify reduced swing meets receiver thresholds.
- **Do not use FET switches on I2C.** They are transmission gates, not open-drain. Cannot isolate bus segments or limit voltage to VCC(A).
- **CB3T up-translates to ~2.8 V only (VCC = 3 V).** Valid for 5 V TTL (VIH = 2.0 V) but NOT for 5 V CMOS (VIH = 3.5 V). Use HCT/AHCT for 3.3 V -> 5 V CMOS.

### 5 V Tolerant Inputs (No Translator Needed)

- **3.3 V -> 5 V TTL works natively.** 3.3 V LVCMOS VOH = 2.4 V exceeds 5 V TTL VIH = 2.0 V. Does NOT work for 5 V CMOS (VIH = 0.7 * VCC = 3.5 V). Use HCT/AHCT family (TTL-compatible inputs accept 2.4 V as valid high).
- **5 V -> 3.3 V: LVC, AUC, AVC families.** Overvoltage-tolerant inputs (VI max = 5.5 V regardless of VCC). How to verify: check IIK spec -- only negative clamp current (no VCC clamp diode). AHC does NOT have IOFF feature -- I/Os not overvoltage-tolerant on transceivers.
- **Duty cycle warning with slow edges.** 0-5 V signal through 3.3 V LVC device switches at 3.3 V threshold, not 2.5 V. Output: 50% input -> ~60% output. Not suitable for clocks requiring symmetric duty cycle.

## Common Mistakes

- **Using TXB0108 on I2C bus.** Active drive fights open-drain pull-ups, slow I2C edges false-trigger one-shot, external pull-ups further degrade performance. Fix: LSF0102 or PCA9306.
- **BSS138 on 1.8 V logic.** Vgs(th) max = VDD, FET never fully turns off. High-side signal floats at VDD_low + Vdiode instead of reaching VDD_high. Fix: LSF0102 (operates down to 0.65 V).
- **Forgetting VCC sequencing on LSF/NVT/PCA9306.** VCCA must not exceed VCCB. If VCCA powers up first, pass transistors conduct uncontrolled. Fix: ensure VCCB rises before or with VCCA, or use TXU/AXC families with glitch-free power-up.
- **Adding external pull-ups to TXB channels.** DC contention between pull-up and weak auto-direction output. Manifests as increased Iq and degraded switching thresholds. Fix: remove all external pull-ups, or switch to LSF.
- **Temperature-induced TXB/TXS oscillation.** Output impedance changes with temperature, causing mismatched impedance -> reflections -> one-shot false triggers -> sustained oscillation. Appears only at temperature extremes during qualification. Fix: 100 nF bypass on VCCA and VCCB close to pins, or switch to direction-controlled family.

## Formulas

**Pull-up resistor for pass-FET translators (LSF, NVT, PCA9306):**
**Rule of thumb:** 2.2K for fast signals (> 1 MHz), 4.7K for slow signals (< 400 kHz). Max 15 mA per channel.
**Formula (VCC(B) - VCC(A) >= 1V, B-side only):** Rpu_min = (VCC(B) - VOL) / IO_max
**Example:** VCC(A) = 1.8 V, VCC(B) = 3.3 V, IO_max = 3 mA, VOL = 0.4 V -> Rpu_min = (3.3 - 0.4) / 0.003 = 967 ohm -> use 1K.

**Maximum frequency for pass-FET translator:**
**Rule of thumb:** 4 MHz with 1.8K pull-ups and 30 pF bus. 400 kHz with 4.7K and 200 pF.
**Formula:** t_rise ~ 0.8 * Rpu * (Cbus + Cio), f_max ~ 1 / (2 * t_rise + t_low_min)
**Example:** Rpu = 2.2K, Cbus = 50 pF, Cio = 4 pF -> t_rise = 0.8 * 2200 * 54e-12 = 95 ns -> supports ~2 MHz.

## Sources

### Related Rules

- `interfaces/i2c.md` -- I2C pull-up design, bus capacitance, speed modes
- `interfaces/spi.md` -- SPI interface timing and layout
- `interfaces/uart.md` -- UART level requirements, RS-232/RS-485 voltage levels

### References

1. TI SCEA035A -- Selecting the Right Level-Translation Solution: https://www.ti.com/lit/pdf/scea035
2. TI SCEA135 -- Do's and Don'ts for TXB/TXS Level-Shifters: https://www.ti.com/lit/pdf/scea135
3. Nexperia AN10441 Rev.2 -- Level Shifting in I2C-Bus Design: https://assets.nexperia.com/documents/application-note/AN10441.pdf
4. NXP (originally Philips) AN97055 -- Bidirectional Level Shifter for I2C-Bus: https://cdn-shop.adafruit.com/datasheets/an97055.pdf
5. NXP AN11127 -- Bidirectional Voltage Translators NVT20xx/PCA9306: https://www.nxp.com/docs/en/application-note/AN11127.pdf
6. Nexperia AN90033 -- LSF010x Auto-Sense Applications: https://assets.nexperia.com/documents/application-note/AN90033.pdf
7. Big Mess o' Wires -- Tale of Three Level Shifters: https://www.bigmessowires.com/2023/08/22/a-tale-of-three-bidirectional-level-shifters/
