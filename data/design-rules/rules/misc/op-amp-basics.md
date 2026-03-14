# Op Amp Selection and Application

> When selecting an op amp for a specific circuit, avoiding common stability and biasing pitfalls.

## Quick Reference

- **Single-supply biasing: bypass the resistor divider with >= 10uF.** A 100K/100K divider with 0.1uF has a 32Hz pole -- PSR is only 6dB below 32Hz and motor-boating results. ADI AN-581 measured this directly.
- **Bias-current-compensated op amps: do NOT match source impedances.** Bias currents can flow in opposite directions -- adding a balancing resistor makes offset worse. Check if offset current spec equals bias current spec (ADI MT-035).
- **Capacitive load stability: every 100pF on the output adds a pole at f = 1/(2*pi*Ro*CL).** A 100pF load shifted TL03x from 80 deg phase margin to ~10% overshoot. Even "unity gain stable" op amps ring with cable capacitance (50-80pF/m coax).
- **Never use an op amp open-loop as a comparator.** Recovery time from saturation is unspecified and unbounded -- some rail-to-rail devices draw destructive current when saturated (TI SBOA067).
- **Recommended op amps:** OPAx388 (precision, 0.25uV offset), AD8641 (JFET low-power, 1pA Ib), MCP6V92 (auto-zero, ~500kHz chop), OPA2314 (low-cost single-supply), AD8605 (general RR I/O).

## Design Rules

### Op Amp Selection by Application

| Application | Key Spec | Recommended Part | Why |
|-------------|----------|-----------------|-----|
| Precision DC (strain, RTD) | Offset < 5uV, drift < 0.05uV/C | OPAx388, AD8551 (auto-zero) | Chopper/auto-zero eliminates drift |
| Low-power sensor (battery) | Iq < 20uA, JFET input | AD8641 (28.5nV/rtHz, 1pA Ib) | JFET: Ib stays low across temp |
| Fast transimpedance (photodiode) | Low Cin, high GBW | OPA380 (90MHz GBW, TIA-optimized) | Internal feedback network option |
| Single-supply audio/general | Rail-to-rail I/O, unity stable | AD8605/AD8606/AD8608, MCP6002 | Low cost, wide availability |
| Instrumentation front-end | High CMRR, matched Ib | AD8422 (in-amp), INA826 | Integrated in-amp avoids resistor matching |

- **Auto-zero/chopper op amps inject ripple at the chopping frequency.** MCP6V92 chops at ~500kHz -- output contains spectral artifacts at f_chop and its harmonics. At unity gain with 100K source impedance, ripple can be 10-50uV p-p. If signal bandwidth overlaps f_chop or its aliases (after ADC sampling), use a post-filter or choose a non-chopper precision part (OPAx388). Artifacts worsen with higher source impedance and higher closed-loop gain.
- **JFET Ib doubles every 10C.** At 125C, JFET bias current is 1000x higher than 25C spec. For >85C, bipolar with internal compensation may be safer despite higher room-temp Ib.
- **Decompensated op amps trade minimum stable gain for bandwidth.** ADI MT-033 measured: AD847 stable at G>=1, 50MHz BW. AD848 stable at G>=5, 175MHz BW. AD849 stable at G>=25, 725MHz BW. Use decompensated parts when your closed-loop gain exceeds the minimum -- free bandwidth.
- **Rail-to-rail input stages have a CM crossover.** Two differential pairs (PNP + NPN) with different offsets -- offset voltage and CMRR shift at the crossover threshold (typically ~1V below V+). OP184/OP284 family keeps both pairs active across the full range, avoiding the crossover glitch. Avoid RRI if signal stays within one pair's range.
- **Rail-to-rail output: "almost" rail-to-rail.** Common-emitter output at 50mA load saturates 200-500mV from the rail. At < 100uA, Vcesat drops to 5-10mV. Check output swing at your actual load current, not no-load spec (ADI MT-035).

### Single-Supply Biasing

- **Resistor divider + bypass cap (standard approach):** RA = RB = 100K for 12-15V supply; 42K for 5V; 27K for 3.3V. C2 pole must be 10x below signal bandwidth -- use >= 10uF for audio (3Hz pole). ADI AN-581: a 0.1uF bypass creates a 32Hz pole that passes 50/60Hz hum directly through.
- **Zener biasing restores full PSR** but output sits at Vzener, not Vs/2. Nonsymmetric clipping on large signals if supply dips. Use low-power Zener (250mW) at 500uA-5mA. Bypass with >= 10uF to suppress Zener noise.
- **For 3.3V operation:** Zeners not available below 2.4V. Use a linear voltage regulator (ADM663A or similar) to generate Vs/2 bias -- lower drift and noise than Zener.
- **DC-coupled battery circuits:** use a "phantom ground" -- op amp buffers Vs/2 divider, supplies it as circuit ground. Op amp must source/sink the full load current of downstream circuits.

> WARNING: AD8061 on 5V single-supply biased at Vs/2 (2.5V): input CM only reaches within 1.8V of V+, so positive swing clips at 3.2V while negative goes to 0V. At gain < 2.5, bias at 1.5V instead of 2.5V for symmetric headroom. ADI AN-581 documents this specific failure.

### Stability and Compensation

- **Noise gain, not signal gain, determines stability.** An inverting amplifier with signal gain = -1 has noise gain = 2. Adding a resistor from (+) to ground increases noise gain without changing signal gain -- stabilizes capacitive loads at the cost of more output noise and offset (TI SLOA020A).
- **Stray capacitance on the inverting input causes instability.** Rf = 1M, Rg = 1M, Cstray = 10pF creates a pole at 318kHz. Fix: add Cf across Rf such that Rf * Cf = Rg * Cstray. This is the compensated attenuator technique -- bandwidth is unaffected when matched.
- **Practical Cf trim (TI SLOA020A):** run a wide copper strip from output over ground plane under Rf (don't connect far end). Trim with razor until peaking disappears, measure, put on final PCB.
- **Lead compensation (Cf across Rf):** introduces a zero at 1/(2 * pi * Rf * Cf) that cancels a problematic pole. Sacrifices high-frequency closed-loop gain. Use when you need bandwidth limiting anyway.
- **Lead-lag compensation:** series RC from input to Rg. Closed-loop gain is unaffected (RC sits across virtual ground). Best bandwidth of all external compensation methods -- TI SLOA020A recommends this as the first choice.
- **Gain compensation:** if you can increase closed-loop gain, do it -- simplest stability fix. Each doubling of noise gain adds 6dB of phase margin.

### Driving Capacitive Loads

- **Out-of-loop isolation resistor (Rx between output and CL):** introduces a zero that restores phase margin. Set fz = 1/(2 * pi * Rx * CL) at least a decade below closed-loop BW. Also serves as transmission line termination (50 or 75 ohm). Doubles output impedance seen by load.
- **In-loop compensation (Rx + Cf):** Rx inside the feedback loop, Cf across Rf cancels the CL pole. DC output impedance stays low. Requires known, fixed CL -- SPICE models don't accurately model Ro, so prototype (ADI Ask the Apps Engineer #25).
- **Op amps rated for unlimited capacitive load:** AD817, AD826, AD827, AD847 (50MHz GBW class). They tolerate any CL but slew rate degrades with large loads.
- **Current feedback op amps: never put a capacitor in the feedback path.** Use out-of-loop Rx only. Noise gain manipulation does not work because CFB bandwidth is not gain-dependent (ADI Ask the Apps Engineer #25).

### Sensor Signal Conditioning

- **Transimpedance (photodiode):** Cf across Rf is mandatory to stabilize against diode junction capacitance. Without Cf, the circuit oscillates. Start with Cf = sqrt(Cj / (2 * pi * Rf * GBW)) -- see Formulas.
- **Wheatstone bridge + instrumentation amp:** use INA826 or AD8422. Single difference amp (4 matched resistors) fails if source impedances are high or mismatched (ADI AN-937).
- **RTD excitation:** use a floating current source (1mA typical). Howland current pump gives best linearity but requires matched resistors (0.1% or better) per Microchip AN990.
- **In-amp reference pin is LOW impedance internally** (on 3-op-amp topology). Driving it from a resistor divider unbalances the subtractor -- use an op amp buffer on the reference (ADI AN-937).

## Common Mistakes

- **Unused op amp sections left floating.** Inputs pick up noise, output slams rail-to-rail at unpredictable frequencies. Self-heating increases package power dissipation and shifts offset of the used sections. Fix: connect output to inverting input, tie noninverting to mid-supply.
- **AC-coupled input without DC bias return path.** FET-input op amp with 1pA bias, 0.1uF cap: charges at 10uV/s. At gain 100, output drifts 0.06V/min -- passes initial bench test, fails hours later (ADI AN-937). Fix: 100K-1M resistor to ground (or bias voltage).
- **Transformer-coupled in-amp without bias resistors.** Same failure mode as AC coupling -- no DC path for bias current. Fix: RA, RB to ground on each input; a third resistor (1/10 their value) between inputs minimizes mismatch error (ADI AN-937).
- **Confusing offset current spec with bias current.** If offset current is the same magnitude as bias current, the op amp uses internal bias compensation -- source impedance matching makes things worse, not better. Check the datasheet footnotes for "bias compensated" (ADI MT-035).
- **Op amp current source with load on a connector.** When cable unplugs, feedback loop opens, op amp gets positive feedback and slams to rail. Fix: include a dummy load inside the feedback path, or add clamp diodes.

## Formulas

**GBW selection for amplifier stage:**
**Rule of thumb:** GBW >= 100 * signal_BW * noise_gain for < 0.1% gain error.
**Formula:** GBW_min = 100 * Q * G * fc (for active filters with Q > 0.5)
**Example:** 10kHz Butterworth, Q = 0.707, G = 1 -> GBW >= 707kHz. OPA2314 at 2.7MHz gives 4x margin.

**Compensated attenuator (cancel stray capacitance):**
**Rule of thumb:** Add Cf across Rf to match Rg * Cstray.
**Formula:** Cf = Rg * Cstray / Rf
**Example:** Rf = 1M, Rg = 100K, Cstray = 5pF -> Cf = 100K * 5pF / 1M = 0.5pF. Use 0.5pF C0G or copper trace trim.

**Transimpedance feedback capacitor:**
**Rule of thumb:** Start with Cf that places the noise gain zero at the geometric mean of fc and GBW.
**Formula:** Cf = sqrt(Cj / (2 * pi * Rf * GBW))
**Example:** Rf = 1M, Cj = 20pF, GBW = 10MHz -> Cf = sqrt(20e-12 / (6.28 * 1e6 * 10e6)) = 0.56pF

## Sources

### Related Rules

- `misc/adc-dac.md` -- ADC driver circuits, anti-aliasing filter design

### References

1. ADI MT-035 -- Op Amp Inputs, Outputs, Single-Supply, Rail-to-Rail: https://www.analog.com/media/en/training-seminars/tutorials/MT-035.pdf
2. ADI AN-581 -- Biasing and Decoupling Op Amps in Single Supply: https://www.analog.com/en/resources/app-notes/an-581.html
3. ADI AN-937 -- Designing Amplifier Circuits: How to Avoid Common Problems: https://www.analog.com/en/resources/app-notes/an-937.html
4. TI SBOA067 -- Op Amps and Comparators: Don't Confuse Them: https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/14/op-amp-vs-comparators.pdf
5. Microchip AN682 -- Using Single Supply Op Amps in Embedded Systems: https://ww1.microchip.com/downloads/en/AppNotes/00682c.pdf
6. Microchip AN990 -- Analog Sensor Conditioning Circuits Overview: https://ww1.microchip.com/downloads/en/appnotes/00990a.pdf
7. TI SLOA020A -- Stability Analysis of VFB Op Amps Including Compensation: https://www.ti.com/lit/an/sloa020a/sloa020a.pdf
8. ADI MT-033 -- Voltage Feedback Op Amp Gain and Bandwidth: https://www.analog.com/media/en/training-seminars/tutorials/MT-033.pdf
9. ADI -- Op Amps Driving Capacitive Loads (Ask the Applications Engineer-25): https://www.analog.com/en/resources/analog-dialogue/articles/ask-the-applications-engineer-25.html
