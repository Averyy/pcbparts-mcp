# Op Amp Selection and Application

> When selecting an op amp for a specific circuit, avoiding common stability and biasing pitfalls.

## Quick Reference

- **Single-supply biasing: 100K/100K with 10uF gives a 0.3Hz pole, not 3Hz.** A 0.1uF bypass gives 32Hz and inadequate rejection below that frequency; choose the pole below the lowest signal frequency [2, Decoupling the Biasing Network; 3, Decoupling Single-Supply Op-Amp Circuits].
- **Bias-current-compensated bipolar op amps: do not add a balancing resistor by habit.** Residual currents can flow in opposite directions; an offset-current specification comparable to bias current is a clue [1, pp.3-4].
- **Unity-gain stability does not guarantee capacitive-load stability.** TI's TL03x example compares an 80-degree phase-margin plot at 25pF with about 10% overshoot at 100pF [6, p.8].
- **Use a comparator for open-loop threshold detection.** Op-amp overload recovery is not generally guaranteed; some rail-to-rail output stages consume excessive current or fail in saturation [4, Section 4.1].
- **MCP6V92 chops at 100kHz, not 500kHz.** OPAx388 also uses internal chopping; it is not a non-chopper alternative [9, p.18; 10, Section 7.3.4].

## Design Rules

### Op Amp Selection by Application

| Application | Recommended Part | Verified Selection Conditions |
|-------------|------------------|-------------------------------|
| Precision DC | OPAx388 | Zero-drift, 2.5-5.5V supply; OPA388/OPA2388 have 0.25uV typical offset at 25 degrees C, not a maximum [10, Features, Electrical Characteristics] |
| High-impedance sensor | AD8641 | At 5V, VCM=2.5V and 25 degrees C: 195uA typical supply current, 1pA maximum Ib, 28.5nV/rtHz typical at 1kHz [11, p.3] |
| Fast transimpedance | OPA380 | 90MHz GBW typical; external feedback resistor and capacitor set gain/stability [12, pp.1, 10-11] |
| Single-supply general | AD8605/AD8606/AD8608 | Rail-to-rail I/O, unity-gain stable, 2.7-5.5V supply [13, p.1] |
| Instrumentation front-end | INA826 | 3-36V supply; check input common-mode versus output swing at the chosen gain [14, pp.1, 21-23] |

- **Chopper artifacts require an actual source-impedance/filter check.** MCP6V92 generates clock/IMD tones; its datasheet recommends low, matched input resistances at high frequency. Do not apply the bias-compensated-bipolar rule to this chopper's switching-current errors [9, pp.18-20].
- **FET bias-current temperature scaling is an estimate, not a device limit.** MT-035's leakage model doubles per 10 degrees C (about 1000x from 25 to 125 degrees C); use actual temperature limits. At +/-13V and VCM=0V, AD8641 specifies up to 260pA over -40 to +125 degrees C versus 1pA at 25 degrees C [1, p.5; 11, pp.3-4].
- **Decompensated op amps trade minimum stable noise gain for bandwidth.** MT-033's +/-15V examples: AD847 G>=1, GBW 50MHz; AD848 G>=5, GBW 175MHz; AD849 G>=25, GBW 725MHz. These are gain-bandwidth products, not closed-loop bandwidths at those gains [7, pp.6-7].
- **Rail-to-rail input crossover is architecture-specific.** OP191/OP291/OP491 and OP279 transition about 1V below V+; OP184/OP284/OP484 keep both pairs active through most of the common-mode range without a discrete crossover threshold. Check offset, bias current, CMRR, and noise across the actual input range [1, pp.6-7].
- **Rail-to-rail output swing depends on load.** MT-035's common-emitter example gives 5-10mV saturation at currents below 100uA, but about 500mV at 50mA; these are illustrative values, not limits for every RR-output amplifier [1, pp.8-9].

### Single-Supply Biasing

- **Resistor-divider defaults in AN-581:** RA=RB=100K for 12-15V, 42K for 5V, 27K for 3.3V, subject to input bias-current errors. Put the bypass pole at one-tenth the input high-pass corner (the lowest passband edge), not one-tenth the upper signal bandwidth [2, Decoupling the Biasing Network].
- **Zener biasing restores PSR only within the Zener's regulated operating range.** Output bias sits at Vzener rather than Vs/2, causing asymmetric clipping if the supply falls. AN-581's Table 3 uses 500uA or 5mA for its named Zeners; use the selected diode's specified current and noise conditions [2, Zener Diode Biasing, Table 3].
- **A 3.3V circuit needs a bias source that actually works at 3.3V.** Do not carry AN-581's ADM663A example into a design without checking regulator minimum input and dropout, as well as amplifier common-mode/output range [2, Op Amp Biasing Using a Linear Voltage Regulator].
- **DC-coupled battery circuits:** a phantom-ground buffer must source/sink the return current of the downstream load circuit, with stability checked for its capacitance [2, DC-Coupled Battery-Powered Circuits; 8].
- **AD8061 common-mode headroom is asymmetric.** AN-581 specifies input operation only to V+ minus 1.8V: on 5V, that is 3.2V. The article's 1.5V input-bias example allows a 3Vpp input; independently verify output bias, output swing, and gain rather than applying its gain>=2.5 shortcut [2, Input Headroom Considerations].

### Stability and Compensation

- **Increase noise gain at the inverting summing node, not at the noninverting input.** MT-033's inverting circuit adds a resistor from the inverting node to ground; signal gain stays -Rf/Rg while noise gain becomes 1+Rf/(Rg||Rextra), increasing output noise and offset [7, pp.2-3, Figure 2C].
- **Compensate inverting-input stray capacitance using the actual feedback network.** SLOA020A's compensated-attenuator condition is Rf * Cf = Rg * Cstray. Its printed 318kHz example for Rf=Rg=1M and Cstray=10pF is inconsistent with Equation 34; do not use that frequency for sizing [6, pp.21-23].
- **Practical Cf trim:** SLOA020A forms a small capacitance with a copper strip from the output under Rf, trims until peaking disappears, then copies the measured geometry to the PCB [6, pp.22-23].
- **Lead compensation (Cf across Rf):** introduces a loop-gain zero at 1/(2 * pi * Rf * Cf); select it from the loop response. Unlike matched attenuator compensation, it reduces high-frequency signal gain in the inverting stage [6, pp.18-21].
- **Lead-lag compensation:** use the series RC shunt at the inverting virtual-ground node shown in SLOA020A Figure 25. Ideal signal gain is preserved only while loop gain remains large; verify the actual loop response [6, pp.23-25].
- **Increasing noise gain reduces crossover frequency and can improve stability.** A doubling is a 6dB gain change, not a fixed increase in phase margin [6, p.18; 7, Phase Margin].

### Driving Capacitive Loads

- **Out-of-loop Rx isolates the output from CL.** ADI's method places the zero 1/(2 * pi * Rx * CL) at least a decade below closed-loop bandwidth; the load sees added Rx output resistance and any resistive load forms a divider. Choose transmission-line termination from driver and line impedance rather than assuming 50 or 75 ohm always applies [8, Method 2].
- **In-loop compensation (Rx + Cf):** sense after Rx for low DC output impedance and use the article's feedback-capacitor network for high-frequency feedback. Cancellation needs a known CL; prototype because output impedance is poorly captured by many models [8, Method 3].
- **AD817, AD826, AD827, and AD847 are listed for unlimited capacitive-load drive.** This is not unchanged dynamic performance: large CL reduces slew rate and needs adequate output current [8, Table and concluding discussion].
- **For current-feedback amplifiers, use the manufacturer's feedback network.** Do not add the VFB shunt feedback capacitor as a generic load-compensation method; ADI recommends out-of-loop Rx because increasing noise gain does not provide the VFB stability benefit [8, Current Feedback discussion].

### Sensor Signal Conditioning

- **OPA380 transimpedance compensation includes all input capacitance.** Size feedback capacitance for photodiode, amplifier, and PCB capacitance, including feedback-resistor stray capacitance; use the datasheet's Butterworth equation/curves rather than a universal formula using diode Cj alone [12, pp.8, 10-11].
- **Bridge front-end:** INA826 avoids external difference-amplifier resistor matching; source and REF impedances still affect common-mode rejection. Check the selected gain and common-mode/output range together [14, Application Information].
- **RTD current excitation:** AN990's floating Howland circuit depends on resistor-ratio matching and load/compliance conditions. Set current from the sensor's self-heating limit rather than imposing 1mA or a universal 0.1% resistor requirement [5, Figure 14].
- **Drive a three-op-amp in-amp REF pin from low impedance.** A divider alone changes the internal subtractor ratio and degrades CMRR/gain accuracy; use a buffer as in AN-937 Figure 9 [3, Correctly Providing In-Amp Reference Voltage].

## Common Mistakes

- **Unused op amp sections left floating.** Noise-driven saturation causes extra dissipation. For a unity-gain-stable section, connect output to inverting input and noninverting input to a valid common-mode/output voltage; use a legal noise gain for a decompensated section [4, Section 4.2.1; 7, Stability Criteria].
- **AC-coupled input without a DC bias return path.** AN-937's 1pA into 0.1uF charges at 10uV/s; gain 100 gives 0.06V/min output drift. Its 100K-1M bias-return examples trade input impedance against offset and noise [3, Missing DC Bias Current Return Path].
- **Transformer-coupled in-amp without bias resistors.** Return each input to a valid common-mode voltage, or use the secondary center tap. AN-937's optional bridging resistor is about one-tenth each return resistor but must remain large compared with differential source resistance [3, Figures 5-6].
- **Current-source load unplugged from a connector.** The topology in SBOA067 loses its intended feedback and drives to a rail; preserve a controlled feedback/protection path under an open load rather than assuming a dummy load or clamp always fixes it [4, Section 4.2.3].

## Formulas

**Compensated attenuator [6, pp.21-23]:**
**Rule of thumb:** Match the two RC time constants in the source's compensated-attenuator topology; do not apply it to every TIA or capacitive-load circuit.
**Formula:** Cf = Rg * Cstray / Rf
**Example:** Rf=1M, Rg=100K, Cstray=5pF -> Cf=0.5pF. Include PCB/feedback parasitics and verify peaking before choosing the fitted capacitor.

## Sources

### Related Rules

- `misc/adc-dac.md` -- ADC drivers, active-filter GBW selection, and anti-aliasing

### References

1. ADI MT-035 (Rev 0, 2008) -- Op Amp Inputs, Outputs, Single-Supply, Rail-to-Rail: https://www.analog.com/media/en/training-seminars/tutorials/MT-035.pdf
2. ADI AN-581 -- Biasing and Decoupling Op Amps in Single Supply (HTML sections): https://www.analog.com/en/resources/app-notes/an-581.html
3. ADI AN-937 -- Designing Amplifier Circuits: How to Avoid Common Problems (HTML sections): https://www.analog.com/en/resources/app-notes/an-937.html
4. TI SBOA067 -- Op Amps and Comparators: Don't Confuse Them: https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/14/op-amp-vs-comparators.pdf
5. Microchip AN990 (DS00990A) -- Analog Sensor Conditioning Circuits Overview: https://ww1.microchip.com/downloads/en/appnotes/00990a.pdf
6. TI SLOA020A (March 2001) -- Stability Analysis of VFB Op Amps Including Compensation: https://www.ti.com/lit/an/sloa020a/sloa020a.pdf
7. ADI MT-033 -- Voltage Feedback Op Amp Gain and Bandwidth: https://www.analog.com/media/en/training-seminars/tutorials/MT-033.pdf
8. ADI -- Op Amps Driving Capacitive Loads (Ask the Applications Engineer-25, HTML): https://www.analog.com/en/resources/analog-dialogue/articles/ask-the-applications-engineer-25.html
9. Microchip MCP6V91/1U/2/4 datasheet (DS20005434B, 2016): https://ww1.microchip.com/downloads/en/DeviceDoc/20005434B.pdf
10. TI OPAx388 datasheet (SBOS777D): https://www.ti.com/lit/ds/symlink/opa388.pdf
11. ADI AD8641/AD8642/AD8643 datasheet (Rev F): https://www.analog.com/media/en/technical-documentation/data-sheets/AD8641_8642_8643.pdf
12. TI OPA380/OPA2380 datasheet (SBOS291G, September 2007): https://www.ti.com/lit/ds/symlink/opa380.pdf
13. ADI AD8605/AD8606/AD8608 datasheet (Rev O): https://www.analog.com/media/en/technical-documentation/data-sheets/AD8605_8606_8608.pdf
14. TI INA826 datasheet (SBOS562G, June 2020): https://www.ti.com/lit/ds/symlink/ina826.pdf
