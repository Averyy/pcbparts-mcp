# ADC/DAC Signal Conditioning and Layout

> When designing the analog front-end for ADCs or the output stage for DACs -- filter design, grounding, and part selection.

## Quick Reference

- **ADS1274: connect AGND and DGND using a single plane.** Separate analog and digital by component placement and routing direction; follow the selected converter's grounding requirements [7, p.6].
- **Anti-alias filter corner: 10x signal BW is the SLYT626 example, not a universal rule.** Its implemented fourth-order 10kHz filter reaches about 1-LSB gain error for 12 bits at 1.04kHz; verify the actual circuit's passband error and stopband attenuation [6, pp.7-9].
- **Use NP0/C0G signal-path capacitors for low distortion.** ADI compares 1nF 0603 NP0 and X7R capacitors on EVAL-AD7960FMCZ at 10kHz; this is a distortion comparison, not an AD7960 functional requirement [2, Figure 6].
- **AD7685 reference pin: 22uF ceramic with minimal trace inductance in ADI's example.** This is not a universal SAR bypass value; the article pairs this ADC with ADR421/ADR431 [1, Step 3].

## Design Rules

### Signal Chain Architecture

- **Budget added noise at a common reference point and bandwidth.** ADI's gain-of-10 AD7685/AD8641 example targets added conditioning noise at one-tenth the sensor noise; include amplifier voltage/current noise, resistor noise, and ADC noise referred through the gain. This is an example budget, not a requirement for every sensor [1, Steps 2-6].
- **Resistor noise can defeat a low-noise amplifier.** At room temperature, 1K contributes about 4nV/rtHz and 100K about 40nV/rtHz; include their actual transfer functions in the noise budget [1, Step 5].

### Anti-Aliasing Filter Design

- **Check passband error, corner frequency, full-power bandwidth, sample rate, and GBW separately.** SLYT626's frequency ordering describes its example; it is not a necessary ordering for every DAQ architecture. Its 1.04/1.47/1.82/2.11kHz error points are SPICE results for the implemented filter, not the ideal fourth-order Butterworth response [6, pp.7-8, Table 1].
- **Do not increase the SAR input RC resistance just to match signal bandwidth.** ADI's AD7980 example has a 3.11MHz RC corner for a 100kHz input signal. Increasing R to 590 ohm gives a 100kHz corner, about 30% signal attenuation near that frequency, and inadequate acquisition settling; put additional narrow filtering before the driver [2, Analog Filter Considerations, Figure 3].
- **Active-filter GBW: use the stage Q, gain, and corner frequency.** SLYT626 uses fGBW >= 100 * Q * G * fc; its 10kHz fourth-order design requires 1.31MHz and uses OPA2314 at 2.7MHz. Also check slew rate: at 5.5V supply and 5.46Vpp, the 1.5V/us specification predicts 87.5kHz full-power bandwidth, while the article reports about 70kHz on the bench with RL=10K and CL=10pF [6, p.9].
- **Use MFB topology for the single-supply filter in SLYT626.** It holds amplifier input common-mode at mid-supply; output swing still needs checking. Generate values with a filter design tool and verify the complete circuit [6, p.8].
- **Multiplexed ADC settling:** a single post-mux filter must recharge to the new channel voltage on every switch; worst case is a full-scale step. For fast throughput, use per-channel filters before the mux [2, Analog Filter Considerations, Figure 4].
- **Oversampling relaxes analog filtering only with adequate rejection.** SLYT626's fourth-order 10kHz filter is down approximately 50dB at the 50kHz Nyquist frequency of its 100kSPS ADC. Choose rejection from the interferer/noise budget rather than assuming that this attenuation is always sufficient [6, p.9].

### DAC Output Considerations

- **Uncompensated zero-order-hold DAC sinc rolloff is -2.42dB at 80% of Nyquist.** Its 0.1dB flatness extends only to about 17% of Nyquist, before reconstruction-filter errors [3, Understanding DAC Frequency Response].
- **Pre-equalization results depend on the FIR design.** ADI's example computes 800 coefficients, truncates to 100 taps, and applies a Blackman window to extend 0.1dB flatness to about 96% of Nyquist; attenuate the input to prevent clipping from high-frequency boost [3, Pre-Equalizing].
- **Post-equalization trades noise for flatness.** ADI's analog equalizer example extends 0.1dB flatness to about 50% of Nyquist; 1+R1/R2 is its maximum gain, not the complete frequency response [3, Post-Equalizing].
- **MAX5895's 8x interpolation pushes the sinc null out by 8x relative to the input data rate.** The DAC core must update at that higher rate [3, Interpolate].

### Voltage Reference Selection

- **Separate reference accuracy/drift from ADC ENOB.** Reference errors affect gain accuracy; ENOB alone does not establish absolute accuracy [1, Steps 3-6; 8, Specifications].
- **REF5025 high-grade:** 2.5V, 3ppm/degrees C maximum drift over -40 to +125 degrees C and 0.05% maximum initial error at 25 degrees C; standard-grade limits are different. Verify reference drive and output capacitance for the chosen ADC [9, Features, Electrical Characteristics].
- **ADR4540B:** 4.096V, 2ppm/degrees C maximum box-method drift over -40 to +125 degrees C; package is SOIC-8, not MSOP-8. Other grades and the bowtie drift method have different limits [10, pp.1, 7-8].
- **ADR421/ADR431 are the references recommended in ADI's AD7685 example.** ADR431 is 2.500V; ADR430 is the 2.048V member. Choose bypass capacitance from the reference and ADC requirements rather than applying a universal 10uF + 0.1uF rule [1, Step 3; 11, pp.1, 5].

### ADC Part Selection

| Application | Part | Key Specs and Conditions | Notes |
|-------------|------|--------------------------|-------|
| General 16-bit SAR | AD7685 | 250kSPS, SPI-compatible [8, p.1] | 22uF reference bypass in ADI's example [1] |
| Sensor front-end | ADS1220 | 24-bit, up to 2kSPS turbo mode, PGA 1-128, 2.048V reference [12] | Check PGA common-mode limits |
| Multi-channel precision | ADS1274 | 4-ch, 24-bit; 128kSPS at 32.768MHz clock in high-speed mode [7, p.3] | 111dB SNR belongs to high-resolution mode, not high-speed mode [7, p.1] |
| 8-ch simultaneous | AD7606 | 16-bit, 200kSPS/ch [13, p.1] | Integrated oversampling filter |
| High-speed 18-bit | AD7960 | 5MSPS, 99dB SNR typical at 1kHz, -0.5dBFS input and VREF=5V [14, pp.1, 3] | NP0/X7R distortion comparison -> above |
| Low-power 12-bit | ADS7138 | 8-ch, I2C; internal conversion timing up to 1MSPS [15, Table 5] | Do not equate internal conversion rate with I2C read throughput |
| High-impedance input | ADAS3022 | 16-bit, 1MSPS; >500Mohm input impedance [22, p.1] | Reduces external buffering requirements |

- **Oversampling gain assumes noise that averages down.** Ideal quantization-noise-limited SNR = 6.02 * N + 1.76 + 10 * log10(OSR) dB for a full-scale sine, OSR = fS/(2 * BW), with filtering before decimation. Thus 4x gives 1 bit and 256x gives 4 bits; correlated noise, distortion, and drift do not follow this improvement. ADI measured 123dB dynamic range on AD7960 at OSR=256, 1-2dB below its extrapolation [2, Digital Filter Considerations].
- **Sigma-delta multiplexing penalty:** flush the digital filter after switching channels. AD7175-x sinc5+sinc1 achieves single-cycle settling at output rates of 10kSPS and lower [2, Digital Filter Considerations].

### DAC Part Selection

| Application | Part | Key Specs | Notes |
|-------------|------|-----------|-------|
| General-purpose control | MCP4728 | 4-ch, 12-bit, I2C, internal 2.048V ref [16, p.1] | Buffered outputs |
| Precision voltage output | DAC8562 | 2-ch, 16-bit, SPI, internal 2.5V ref [17, p.1] | 4-LSB INL; reference disabled by default |
| High-speed waveform | AD9744 | 14-bit, 210MSPS, current output [18, p.1] | Size termination for compliance voltage |
| Multi-channel setpoint | DAC7578 | 8-ch, 12-bit, I2C [19, p.1] | TSSOP resets to zero; QFN supports zero or midscale |
| Low-power single | MCP4725 | 1-ch, 12-bit, I2C, EEPROM [20, p.1] | Restores EEPROM-programmed code/configuration, not every volatile write |
| Precision bipolar | AD5761R | 1-ch, 16-bit, SPI, programmable ranges including +/-10V [21, p.1] | Requires analog supplies appropriate to the output range |

- **AD9744 supports resistive current-to-voltage conversion.** Select load resistance so both outputs remain inside compliance limits; an op amp or transformer is an alternative, not mandatory [18, Analog Outputs, Output Configurations].
- **A buffered DAC still has a capacitive-load limit.** Check the chosen output amplifier's stability and settling conditions; an integrated buffer is not permission to attach arbitrary cable/filter capacitance -> `misc/op-amp-basics.md` [17, Output Amplifier].

### Mixed-Signal PCB Layout

- **Use a unified ground plane for the low-digital-current ADC/DAC case in ADI's guidance.** Complex high-current mixed-signal systems require an explicit return-path plan; follow device grounding requirements [4, Ground Plane; 7, p.6].
- **TI's layout exercise starts with a split, then removes it.** Keep analog and digital routing in their respective zones; the low-inductance return-under-trace argument applies at high frequency, not universally at DC [5, PCB Layout Process; 4, Single Ground Plane].
- **Four or more layers are ADI's recommendation for high-performance acquisition, not a universal minimum.** Stackup and general routing -> `guides/pcb-layout.md` [4, Board Layers].
- **Match differential-path thermal junctions.** TI shows feedthrough-count asymmetry creating temperature-dependent offsets; its separate trace-drop example is 25.4mm (1 inch) of 0.18mm (7mil), half-ounce copper carrying 10uA, giving 1.3uV, about 4 LSB at 24 bits with a 5V span [5, High Resolution Measurements, Offset Voltages].
- Power-pin bypassing and ferrite/decoupling resonance -> `power/decoupling.md`; do not substitute a precision voltage reference for a supply rail [4, Power Supply Block, Decoupling Techniques].

### Component Selection for Low Distortion

- **Thin-film or metal-film resistors reduce passive-component distortion in demanding signal chains.** Evaluate voltage and power coefficients; ADI does not establish a universal 14-bit threshold for rejecting thick film [2, Component Selection Challenges].
- **RC thermal-noise lookup, integrated over the complete single-pole response at 25 degrees C:** sqrt(k * T / C) gives about 6.4uVrms for 100pF, 2.0uVrms for 1nF, and 0.64uVrms for 10nF. This is the resistor's filtered equilibrium noise, not an additional independent capacitor-noise source [2, Component Selection Challenges].

## Common Mistakes

- **Discarding samples before sufficient digital filtering.** ADI's AD7606 example converts at 200kSPS and decimates by 32 to 6.25kSPS; a 3.5kHz input produces a 2.75kHz alias. Reject it before downsampling with adequate digital filtering or analog filtering; the analog filter must also prevent aliases at the original ADC sampling rate [2, Avoid Aliasing by Decimation].

## Formulas

**Active-filter amplifier selection [6, p.9]:**
**Rule of thumb:** Apply the 100 * Q * G factor to each active filter stage, not to an arbitrary ADC input buffer.
**Formula:** fGBW >= 100 * Q * G * fc; verify settling, noise, and slew rate separately.
**Example:** SLYT626's fourth-order 10kHz filter uses worst-stage Q about 1.31 and G=1 -> fGBW >= 1.31MHz. OPA2314 at 2.7MHz provides about 2.1x margin.

## Sources

### Related Rules

- `misc/op-amp-basics.md` -- Amplifier stability and compensation for ADC driver stages
- `power/decoupling.md` -- ADC/DAC power bypassing and ferrite resonance
- `guides/pcb-layout.md` -- Stackup and mixed-signal routing

### References

1. ADI -- Seven Steps to Successful Analog-to-Digital Signal Conversion (HTML, Steps 1-7): https://www.analog.com/en/resources/technical-articles/seven-steps-to-successful-analog-to-digital-signal-conversion.html
2. ADI -- Practical Filter Design Challenges for Precision ADCs (HTML, Analog/Digital Filter Considerations): https://www.analog.com/en/resources/analog-dialogue/articles/practical-filter-design-precision-adcs.html
3. ADI -- Equalizing Techniques Flatten DAC Frequency Response (2006, HTML): https://www.analog.com/en/resources/technical-articles/equalizing-techniques-flatten-dac-frequency-response.html
4. ADI -- Basic Guidelines for Layout Design of Mixed-Signal PCBs (HTML): https://www.analog.com/en/resources/analog-dialogue/articles/what-are-the-basic-guidelines-for-layout-design-of-mixed-signal-pcbs.html
5. TI SLYP167 -- PCB Layout Tips for High Resolution (Precision Analog Seminar): https://www.ti.com/lit/ml/slyp167/slyp167.pdf
6. TI SLYT626 (2Q 2015, pp.7-9) -- Designing an Anti-Aliasing Filter for ADCs in the Frequency Domain: https://www.ti.com/lit/an/slyt626/slyt626.pdf
7. TI ADS1274/ADS1278 datasheet (SBAS367F, February 2011): https://www.ti.com/lit/ds/symlink/ads1274.pdf
8. ADI AD7685 datasheet (Rev D): https://www.analog.com/media/en/technical-documentation/data-sheets/AD7685.pdf
9. TI REF50xx datasheet (SBOS410, Features and Applications): https://www.ti.com/lit/ds/symlink/ref50.pdf
10. ADI ADR45xx datasheet (Rev G): https://www.analog.com/media/en/technical-documentation/data-sheets/adr4520_4525_4530_4533_4540_4550.pdf
11. ADI ADR43x datasheet (Rev N, February 2018): https://www.analog.com/media/en/technical-documentation/data-sheets/ADR430_431_433_434_435.pdf
12. TI ADS1220 -- datasheet and product specifications: https://www.ti.com/product/ADS1220
13. ADI AD7606 family datasheet (Rev G): https://www.analog.com/media/en/technical-documentation/data-sheets/AD7606_7606-6_7606-4.pdf
14. ADI AD7960 datasheet (Rev C): https://www.analog.com/media/en/technical-documentation/data-sheets/AD7960.pdf
15. TI ADS7138 datasheet (SBAS976A, May 2020): https://www.ti.com/lit/ds/symlink/ads7138.pdf
16. Microchip MCP4728 datasheet (DS22187E): https://ww1.microchip.com/downloads/en/DeviceDoc/22187E.pdf
17. TI DACxx6x datasheet (SLAS719E, June 2015): https://www.ti.com/lit/ds/symlink/dac8562.pdf
18. ADI AD9744 datasheet (Rev C): https://www.analog.com/media/en/technical-documentation/data-sheets/AD9744.pdf
19. TI DAC5578/6578/7578 datasheet (SBAS496B, August 2012): https://www.ti.com/lit/ds/symlink/dac7578.pdf
20. Microchip MCP4725 datasheet (DS22039D): https://ww1.microchip.com/downloads/en/DeviceDoc/22039d.pdf
21. ADI AD5761R/AD5721R datasheet (Rev C): https://www.analog.com/media/en/technical-documentation/data-sheets/AD5761R_5721R.pdf
22. ADI ADAS3022 datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/ADAS3022.pdf
