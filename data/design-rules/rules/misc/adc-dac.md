# ADC/DAC Signal Conditioning and Layout

> When designing the analog front-end for ADCs or the output stage for DACs -- filter design, grounding, and part selection.

## Quick Reference

- **Do NOT split the ground plane.** Use a single solid ground plane; separate analog and digital by component placement and routing direction, not by copper cuts. ADS1274 datasheet: "AGND: connect to DGND using a single plane."
- **Anti-alias filter corner: set fc >= 10x signal BW.** At fc the filter is already -3 dB. A 4th-order Butterworth at fc = 10kHz reaches 1-LSB error (12-bit) at only 1.04kHz. If your signal BW is 1kHz and you need < 1 LSB error, fc >= 10kHz.
- **NP0/C0G caps only in the signal path.** X7R caps add measurable harmonic distortion -- verified on AD7960 eval board: X7R degraded THD by several dB vs NP0 at 10kHz.
- **SAR ADC reference pin: decouple with 22uF ceramic, minimal trace inductance.** Dynamic impedance on the reference input causes gain errors if not properly bypassed. Pair AD7685 with ADR421/ADR431.
- **Recommended ADCs:** AD7685 (16-bit 250kSPS SAR), ADS1220 (24-bit 2kSPS, integrated PGA + ref), AD7606 (16-bit simultaneous 8-ch), AD7960 (18-bit 5MSPS, requires NP0 input caps).

## Design Rules

### Signal Chain Architecture

- **7-step methodology for sensor-to-ADC design (ADI Seven Steps):**
  1. Characterize sensor output (amplitude, bandwidth, noise floor)
  2. Calculate required ADC ENOB from input SNR: ENOB = (SNR - 1.76) / 6.02
  3. Select ADC + reference that exceeds this ENOB
  4. Calculate max front-end gain to fill ADC input range
  5. Select driver op amp with noise < 1/10 of sensor noise (referred to input)
  6. Verify total noise budget: op amp + resistors + ADC < sensor noise
  7. Simulate and prototype

- **Driver amplifier noise budget:** total noise at op amp input must be < 1/10 of sensor noise floor. After gain, op amp noise is amplified equally with signal -- pick an op amp where en * gain << sensor noise. ADI recommends AD8641 for high-impedance sensors (1pA Ib, 28.5nV/rtHz).
- **Resistor noise matters.** A 1K resistor = 4 nV/rtHz. A 100K resistor = 40 nV/rtHz. Using a "low noise" op amp (3 nV/rtHz) with 100K feedback resistors wastes the op amp's noise advantage. ADI Seven Steps calls this "the most common signal chain mistake."

### Anti-Aliasing Filter Design

- **Six frequencies define the AAF design** (in ascending order per TI SLYT626): fSIGNAL (signal BW), fLSB (frequency where filter gain error = 1 LSB), fC (filter -3dB corner), fPEAK (op amp max full-scale output), fS (ADC sample rate), fGBW (op amp unity-gain BW). All six must be in this order or the design is broken.
- **fc should be ~10x signal BW, not equal to it.** TI SLYT626 table: 4th-order Butterworth at fc = 10kHz reaches 1-LSB error (-2mdB for 12-bit) at 1.04kHz, 2 LSB at 1.47kHz, 3 LSB at 1.82kHz, 4 LSB at 2.11kHz.
- **RC filter in front of SAR ADC: do NOT reduce R to narrow bandwidth.** ADI practical filter paper: a 590 ohm resistor giving 100kHz BW on AD7980 causes 30% amplitude attenuation and prevents the internal S/H from charging within the acquisition window. Use the datasheet-recommended RC values.
- **Filter GBW requirement:** fGBW >= 100 * Q * G * fc. For 10kHz 4th-order Butterworth, worst-case stage Q = 1.31, G = 1: fGBW >= 1.31 MHz. OPA2314 at 2.7MHz works. Also verify op amp slew rate: fPEAK = SR / (Vpp * pi). OPA2314 at 1.5V/us with 5.46Vpp -> 87.5kHz calculated, ~70kHz measured (-> `misc/op-amp-basics.md` for amplifier stability).
- **Use MFB (multiple feedback) topology for single-supply active filters.** MFB exercises the op amp at mid-supply DC bias, avoiding rail-to-rail output limitations. TI SLYT626 recommends WEBENCH Filter Designer or ADI Filter Wizard to generate component values.
- **Multiplexed ADC settling:** a single post-mux filter must recharge to new channel voltage on every switch. Worst case = full-scale step. For fast throughput, use per-channel filters before the mux.
- **Oversampling relaxes the anti-alias filter.** Sampling at 100kHz with a 1kHz signal puts Nyquist at 50kHz -- the filter only needs -50dB at 50kHz, easily achieved with a 2nd-order filter at 10kHz corner.

> WARNING: Digital decimation can re-introduce aliasing. ADI practical filter paper: if you oversample at 200kSPS then decimate to 6.25kSPS, a 3.5kHz input signal aliases to 2.75kHz (6.25k - 3.5k). The analog anti-alias filter must satisfy Nyquist for the DECIMATED rate, not the original sample rate.

### DAC Output Considerations

- **Sinc rolloff: -2.42dB at 80% of Nyquist (ADI equalizing techniques).** Zero-order hold creates sin(x)/x envelope. 0.1dB flatness extends only to 17% of fNyquist without compensation.
- **Pre-equalization (digital FIR inverse-sinc):** extends 0.1dB flatness to 96% of fNyquist. ADI method: N=800 coefficient computation, truncate to 100 taps, apply Blackman window. Trade-off: must attenuate input to prevent clipping at high-frequency boost.
- **Post-equalization (analog):** simple active filter with (1+R1/R2) gain shape extends 0.1dB flatness to 50% of fNyquist. Amplifies high-frequency noise.
- **Interpolating DACs (e.g., MAX5895 with 8x):** push the sinc null out by the interpolation factor, relaxing the reconstruction filter. Best approach when available.
### Voltage Reference Selection

- **For 16-bit+ SAR ADCs, the reference dominates system accuracy.** At 16 bits with 5V range, 1 LSB = 76uV -- a 15ppm/C ref drifts 75uV per degree C (1 LSB per degree). The ADC ENOB is meaningless if the reference drifts more.
- **REF5025** (2.5V, 3ppm/C, 0.05% initial accuracy): workhorse for 16-bit SAR. Low output impedance drives SAR reference pins directly. SOIC-8.
- **ADR4540** (4.096V, 2ppm/C, 4.8uVpp 0.1-10Hz noise): best-in-class for 18-bit+ SAR. The 4.096V output gives clean binary LSB scaling (1 LSB = 4.096V / 2^N). MSOP-8.
- **LM4040** (shunt reference, multiple voltages, 0.1% grade): use for ratiometric bridge sensors where the excitation voltage IS the reference. Shunt topology means near-zero AC output impedance. Budget option for 12-14 bit systems.
- **ADR421/ADR431** (2.5V/2.048V XFET): recommended by ADI for AD7685 and similar PulSAR ADCs (ADI Seven Steps). Low 1/f noise, excellent long-term stability. Use when drift over months matters (calibration-free instruments).
- **Bypass the reference output with 10uF ceramic + 0.1uF ceramic.** SAR ADCs draw transient current from the reference during each conversion. Insufficient bypassing causes gain errors proportional to the reference impedance at the conversion frequency.

### ADC Part Selection

| Application | Part | Key Specs | Notes |
|-------------|------|-----------|-------|
| General 16-bit SAR | AD7685 | 250kSPS, 90dB SNR, SPI | 22uF ceramic on VREF; pair with ADR421/ADR431 |
| Sensor front-end (thermocouple, load cell, RTD) | ADS1220 | 24-bit, 2kSPS, integrated PGA (1-128x) + 2.048V ref | Internal ref + PGA eliminates external amp + ref in many cases |
| 24-bit multi-ch precision | ADS1274 | 4-ch, 128kSPS, 111dB SNR | Single ground plane per datasheet |
| 8-ch simultaneous | AD7606 | 16-bit, 200kSPS/ch, integrated OSR | Onboard sinc filter, OS pins |
| High-speed 18-bit | AD7960 | 5MSPS, 99dB SNR | Requires NP0 input caps -- X7R degraded THD by several dB |
| Low-power 12-bit | ADS7138 | 8-ch, I2C, 1MSPS | Single GND pin -- no split possible |
| High-impedance input | ADAS3022 | 16-bit, 1MSPS, 500M input Z | No external buffer needed |

- **Oversampling ENOB gain:** 4x oversampling = +1 bit. 256x = +4 bits. Measured on AD7960: 256x OSR achieved 123dB dynamic range (theory: 125dB, 1-2dB degraded by 1/f noise from signal chain).
- **Sigma-delta multiplexing penalty:** digital filter must flush on channel switch. AD7175 sinc5+sinc1 filter achieves single-cycle settling at <= 10kSPS -- designed specifically for muxed applications (ADI practical filter paper).

### DAC Part Selection

| Application | Part | Key Specs | Notes |
|-------------|------|-----------|-------|
| General-purpose audio/control | MCP4728 | 4-ch, 12-bit, I2C, internal 2.048V ref | No external ref needed |
| Precision voltage output | DAC8562 | 2-ch, 16-bit, SPI, internal 2.5V ref | 1 LSB INL, rail-to-rail output with integrated buffer |
| High-speed waveform | AD9744 | 14-bit, 210MSPS, current output | Requires external I-to-V or transformer; 0.1dB flat to 17% fNyquist without equalization |
| Multi-channel setpoint | DAC7578 | 8-ch, 12-bit, I2C | Power-on reset to zero or mid-scale selectable |
| Low-power single | MCP4725 | 1-ch, 12-bit, I2C, EEPROM | Stores last setting -- output restores on power-up |
| Precision 16-bit | AD5761R | 1-ch, 16-bit, SPI, +/-10V output | Bipolar output for industrial control, integrated output clamp |

- **Current-output DACs (AD9744, AD9767) need an external op amp or transformer for voltage output.** Do not resistively terminate -- the compliance voltage range is limited and nonlinearity increases.
- **For DACs driving capacitive loads (long cables, filter caps >1nF):** select a DAC with integrated output buffer or add an external buffer. Unbuffered R-2R DAC outputs have code-dependent output impedance that interacts with load capacitance to create settling tails and DNL errors.

### Mixed-Signal PCB Layout

- **Single ground plane, no split.** ADI mixed-signal layout guidelines: modern ADCs with low digital current work best on a unified ground. Splitting creates return current detours that increase noise. Altium grounding article confirms: ADS1274 datasheet explicitly says "AGND: connect to DGND using a single plane."
- **Start with a split during layout, then remove it.** Route analog signals over the "analog" zone, digital over the "digital" zone, then delete the split. Return currents naturally stay under their signal traces (lowest inductance path) even on a continuous plane. Both ADI and TI precision layout guides recommend this technique.
- **4-layer minimum for precision systems:** L1 = signals, L2 = ground, L3 = power, L4 = aux signals. L2 ground adjacent to L1 gives tight return path coupling.

> WARNING: Ferrite bead between analog and digital power rails with separated ground planes is the worst common advice (Altium grounding article). It creates a ground loop where return currents have no low-impedance path. If you need isolated analog power, use a separate precision reference with its own RC filter -- not a ferrite on a shared rail with split grounds.

- **Thermocouple effects in precision layouts (TI SLYP167).** A PCB via creates a copper-solder junction. Different numbers of vias on + and - differential traces create a temperature-dependent offset. For 24-bit ADCs, 1 inch of 0.5oz trace carrying 10uA drops 1.3uV -- 4 LSBs. Route differential pairs symmetrically with equal via counts.
- **Decoupling:** 0.01-0.1uF ceramic as close as physically possible to each power pin. 10-100uF electrolytic within 25mm. Connect through via to ground plane, not through a trace (-> `power/decoupling.md`).

### Component Selection for Low Distortion

- **NP0/C0G ceramic or polystyrene for signal path capacitors.** X7R dielectric is voltage-dependent (piezoelectric effect) and introduces harmonic distortion. Measured on AD7960 eval board: swapping 1nF 0603 X7R for NP0 improved THD by several dB at 10kHz (ADI practical filter paper).
- **Thin film or metal film resistors for precision signal paths.** Standard thick film resistors have voltage coefficient and power coefficient nonlinearity that contribute distortion in high-resolution (>14-bit) signal chains.

## Common Mistakes

- **Ferrite bead between analog and digital power rails (whether split or unified ground).** The ferrite's inductance (~1uH) resonates with decoupling caps (typically 1-10 MHz), amplifying noise at the resonant frequency by 10-20 dB. Worse than either a full split or a unified plane. Same failure when using the same supply for ADC analog and digital rails with a ferrite between them. Use a direct connection with adequate local decoupling, or a truly separate precision LDO for the analog rail with its own RC filter.
- **Narrowing RC anti-alias filter bandwidth to match signal BW.** A 100kHz SAR ADC with 100kHz signal does not need a 100kHz filter -- it needs the recommended ~3MHz filter to allow S/H acquisition settling (ADI practical filter paper: 590 ohm on AD7980 caused 30% amplitude attenuation). Tighter filtering belongs before the driver amplifier where input impedance is high.
- **Trusting oversampling to fix aliasing.** Oversampling spreads quantization noise but does not prevent out-of-band signals from aliasing. A strong interferer at 0.8*fS aliases in-band regardless of OSR. The analog filter must reject signals relative to the Nyquist frequency of the final decimated rate.
- **Using the power supply as the ADC reference.** A 3.3V LDO with 1% accuracy and 50uV/rtHz noise is 10-bit performance at best. Even "clean" LDOs have load transients from other circuits. Use a dedicated voltage reference IC for anything above 10-bit.
- **Ignoring DAC sinc rolloff in waveform generation.** An uncompensated DAC is only 0.1dB flat to 17% of fNyquist. At 80% of fNyquist, output is down 2.42dB. For broadband applications: interpolating DAC (MAX5895, 8x interpolation pushes null out 8x), digital pre-equalization (FIR inverse-sinc, 100-tap Blackman-windowed -> 0.1dB flat to 96% fNyquist), or post-equalization analog filter (~50% fNyquist but amplifies HF noise).

## Formulas

**Oversampling SNR improvement:**
**Rule of thumb:** 4x oversampling = +6dB (+1 bit). 16x = +12dB (+2 bits).
**Formula:** SNR_improvement = 10 * log10(OSR), where OSR = fS / (2 * BW)
**Example:** 12-bit ADC at 5.12MSPS, signal BW = 10kHz -> OSR = 256 -> +24dB -> effective 16-bit noise performance

**Anti-alias filter GBW requirement:**
**Rule of thumb:** Op amp GBW >= 100 * fc for unity-gain buffer driving the filter.
**Formula:** fGBW >= 100 * Q * G * fc
**Example:** 4th-order Butterworth at 10kHz, Q = 1.31 (stage 2), G = 1 -> fGBW >= 1.31MHz. OPA2314 (2.7MHz) provides 2x margin.

**RC thermal noise (quick lookup):**
**Rule of thumb:** 100pF = 6.4uVrms, 1nF = 2uVrms, 10nF = 0.64uVrms (at 25C).

## Sources

### Related Rules

- `misc/op-amp-basics.md` -- Amplifier stability and compensation for ADC driver stages
- `power/decoupling.md` -- Decoupling strategy for ADC/DAC power pins

### References

1. ADI -- Seven Steps to Successful Analog-to-Digital Signal Conversion: https://www.analog.com/en/resources/technical-articles/seven-steps-to-successful-analog-to-digital-signal-conversion.html
2. ADI -- Practical Filter Design Challenges for Precision ADCs: https://www.analog.com/en/resources/analog-dialogue/articles/practical-filter-design-precision-adcs.html
3. ADI -- Filter Basics: Anti-Aliasing: https://www.analog.com/en/resources/technical-articles/guide-to-antialiasing-filter-basics.html
4. ADI -- Equalizing Techniques Flatten DAC Frequency Response: https://www.analog.com/en/resources/technical-articles/equalizing-techniques-flatten-dac-frequency-response.html
5. ADI -- Basic Guidelines for Layout Design of Mixed-Signal PCBs: https://www.analog.com/en/resources/analog-dialogue/articles/what-are-the-basic-guidelines-for-layout-design-of-mixed-signal-pcbs.html
6. Altium -- How to Properly Ground ADCs: https://resources.altium.com/p/how-properly-ground-adcs
7. TI SLYP167 -- PCB Layout Tips for High Resolution (Precision Analog Seminar): https://www.ti.com/lit/ml/slyp167/slyp167.pdf
8. TI SLYT626 -- Designing an Anti-Aliasing Filter for ADCs in the Frequency Domain: https://www.ti.com/lit/an/slyt626/slyt626.pdf
