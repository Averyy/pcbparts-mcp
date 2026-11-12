# Audio

> I2S interface, audio codec integration, Class-D amplifier layout, MEMS microphones, headphone driver design, mixed-signal grounding for audio. General grounding -> `guides/pcb-layout.md`. ADC/DAC precision -> `misc/adc-dac.md`.

## Quick Reference

- **For converters with low internal digital currents, join AGND/DGND locally to the analog ground plane.** This is ADI's stated case, not a rule to split every codec board; use the selected codec's grounding guidance [5, Grounding and Decoupling Mixed-Signal ICs with Low Digital Currents].
- **TAS2xxx boosted-amplifier layout recommendation: >= 0.76mm (30mil) output width on each of two layers.** Match OUT_P/OUT_N routing resistance; place any output EMI filter near device pins. This is SLAA896's device-family recommendation, not a universal Class-D trace minimum [3, p.7].
- **InvenSense MEMS mic PCB hole >= 0.25mm diameter; 0.5-1.0mm typical.** Keep the effective gasket path diameter close to or smaller than the case vent to avoid an acoustic resonance [1, p.2].
- **MAX98357A: I2S DAC + Class-D, no MCLK required.** 3.2W is typical at 5V, 25 degrees C, 48kHz sample rate and 12dB gain into 4 ohm + 33uH with 10% THD+N; supply 2.5-5.5V. Filterless operation requires speaker series inductance > 10uH [8, pp.4-5,33].
- **TLV320AIC3204: four ADC/DAC PowerTune modes.** PTM_P4/PTM_R4 gives highest performance, PTM_P1 lowest playback power; >= 20-bit data is needed to fully benefit from PTM_P4 SNR, not to enable the mode [4, pp.10-12].

## Design Rules

### I2S Interface

- **Two compatible PDM microphones share one data line using opposite clock edges.** L/R SELECT assigns the channel. Half a clock period at 3MHz is 167ns (recalculated) [6, p.5].
- **For PDM evaluation wires > 15cm, AN-1003 recommends 20-100 ohm source termination at the codec clock output.** Select for the actual line/driver impedance and check ringing; excessively long wires can also require a clock buffer. The 15cm figure is not an I2S PCB routing threshold [1, pp.4-5].

### Audio Codec Integration

- **TLV320AIC3204 clock strategy: start from bottom up.** Select AOSR/DOSR first: ADC Filter A permits AOSR=128 or 64 (typically <= 48kHz), B uses 64 (typically 96kHz), C uses 32 (typically 192kHz); DOSR has separate filter constraints. Then MADC/MDAC and NADC/NDAC; verify both (MADC * AOSR) / 32 and (MDAC * DOSR) / 32 against their processing-block resource classes [4, pp.5-6].
- **AIC32x4 CODEC_CLKIN: 512kHz-50MHz from an external clock without PLL.** The 137MHz internal limit requires DVDD > 1.65V and even NADC/NDAC; other parity combinations limit it to 112MHz or 110MHz, and DVDD < 1.65V limits it to 50MHz. Check ADC/DAC clock and PLL constraints as well [4, pp.5-6].
- **WM8960: 1W per channel into 8 ohm at 5V speaker supply, with separate headphone drivers.** I2C address is 0x1A (7-bit), write address byte 0x34. Both direct SYSCLK and the PLL reference come from MCLK, not BCLK; 12.288MHz/11.2896MHz SYSCLK supports 48kHz/44.1kHz with the corresponding dividers [9, pp.1,60-62,65].
- **Power sequencing (TLV320AIC3204): IOVDD first (or simultaneous with others), hold RESET low until all supplies stabilize; AVDD can be applied last.** Pull LDO_SELECT to IOVDD to enable the digital LDO, or tie to IOVSS for external DVDD; the analog LDO is enabled separately by register [4, pp.9-10].
- **AIC32x4 layout: SLAA404C recommends a separate analog ground plane joined at one point near the codec.** Its pinout separates analog and digital sections; do not transfer that specific layout prescription to every audio IC -> `guides/pcb-layout.md` [4, p.3].

### Class-D Amplifier Layout

- **TAS2xxx ground: short BGND, GND, PGND and GNDD beneath the package.** SLAA896's TAS2562 example stitches the top-layer connection to a dedicated layer-2 ground plane through multiple vias at device pads [3, pp.3-4].
- **SLAA896 TAS2562 decoupling-loop recommendations:** the pin-to-pin column includes both PCB connections; capacitor ESL is added once. These are layout targets for optimum performance, not guaranteed component ratings [3, p.4, Table 2]:

| Net | PCB pin-pin inductance (pH) | Cap ESL (pH) | Total (pH) |
|-----|---------------------------|-------------|------------|
| VBST-BGND | 250 | 500 | 750 |
| GREG-PVDD | 300 | 500 | 800 |
| VDD-GND | 350 | 500 | 850 |
| VBAT-GND | 650 | 500 | 1150 |

- **TAS2xxx switching nets (Class-D output, SW node, Vsense): avoid parallel overlap with other signals on adjacent layers without ground shielding.** SLAA896 shows a ground layer between overlapping nets or routing that avoids coupling area [3, pp.5-6].
- **TAS2xxx charge-pump cap (GREG to PVDD): star-connect at PVDD pin, not to PVDD plane.** Thick traces, route on top layer or immediately below. Multiple vias for layer transitions [3, pp.6-7].
- **TAS2xxx VBST to PVDD: connect strongly on top layer directly under device.** The source identifies IR drop and via-inductance ringing as reasons for this connection [3, p.3].
- **TAS2xxx Vsense: take differential sense connections near the speaker terminals.** SLAA896 recommends 0.15mm (6mil) width; speaker protection needs the terminal voltage, including the output-path voltage drop [3, p.6].

### Click and Pop Noise

- **TAS2780/TAS2781: 0.8mV typical click/pop (-62dBV); TAS2764: 1mV typical.** SLAAED0 Table 5-1 uses 25 degrees C, 48kHz, gain=21dBV, VBAT1S=3.8V, AVDD=1.8V, SDZ=1, NG_EN=0 and PWR_MODE1: TAS2780/81 use PVDD=18V, IOVDD=1.8V, EN_LLSR=0, 4 ohm + 15uH; TAS2764 uses PVDD=12V, IOVDD=1.2V, EDGE_RATE=00, EN_LLSR=1, 4 ohm + 16uH. Measurements are A-weighted with the stated filter-free setup [7, pp.3-5].
- **TAS27xx noise gate: SLAAED0 illustrates shutdown with input below -120dBFS for > 50ms.** Entry/exit produces regulated pop; the note identifies -120dBFS as the default threshold, and a higher threshold increases pop amplitude [7, pp.4,15].
- **TAS27xx high-pop triggers include reset, OCP/OTP/clock faults, and supply dips/overshoots.** Abrupt shutdown bypasses the normal regulated transition [7, p.4].
- **TAS2764 pop optimization requires the full register sequence.** Write 0x00=0xFD, 0x0D=0x0D, then 0x64=0x04; return to page 0 with 0x00=0x00 and write 0x02=0x02 for software shutdown. To exit idle mode, repeat 0x00=0xFD and 0x0D=0x0D before 0x64=0x00; TAS2780/81 implement this optimization internally [7, p.16].
- **Y-bridge mode (TAS27xx): switches on VBAT instead of PVDD for low-level signals.** Reduces switching losses and differential error buildup during power transitions, reducing pop [7, p.4].

### MEMS Microphone Integration

- **Digital MEMS mic (I2S output): Knowles SPH0645LM4H-B.** Integrated conversion/decimation, direct connection to a compatible MCU/DSP; package 3.50x2.65x0.98mm [10, pp.1,9].
- **InvenSense bottom-port mounting: align the package port and PCB hole without blocking either opening.** AN-1003 states PCB thickness does not affect its microphones' performance and describes adhesive-mounted flex for a sealed short acoustic path [1, p.2].
- **Helmholtz resonance from gasket cavity:** minimize the wide cavity or put the board against the case; for a longer path keep its diameter close to or smaller than the vent. AN-1003 also permits multiple small case holes [1, pp.2-3].
- **InvenSense example: 200 ohm microphone output into a 2K PGA input loses about 9.1% amplitude.** Check the codec input impedance at the selected gain; these impedances are examples, not all MEMS microphones' specifications [6, p.4].
- **For an analog mic with 200 ohm output impedance, AN-1003 adds 200 ohm in a separate reference conductor.** Route it with the signal into a differential codec input; do not insert this resistor in the microphone's power-ground return [1, p.7, Figure 9].
- **AC-coupling example: 1uF into 10K gives approximately 16Hz corner for a mic with 100Hz natural rolloff.** This is not a universal minimum: AN-1003 shows 2.2uF minimum for its codec connection and 1uF for its 10K op-amp input [6, p.4; 1, p.6].
- **InvenSense PDM example: bypass each microphone with 0.1uF near its VDD pin.** Use the selected microphone's supported clock range rather than assuming every part accepts 3MHz [1, pp.4-5].

### Headphone Driver Design

- **I-to-V stage: maximize first-stage gain within the amplifier's linear output range.** AN-1429's 4K feedback/100 ohm series-with-feedback-cap example assumes +/-5V supplies, +/-4V linear output and 1mA DAC current. ADA4841-2/ADA4896-2 are recommended candidates; this 100 ohm resistor is not the headphone output resistor [2, p.3].
- **AN-1429 measures < -100dB THD+N current capability into 16 ohm, not 32 ohm.** ADA4841-2: 29.1mA RMS; ADA4807-2: 42.1mA RMS; AD8397: 125mA RMS (250mW). These are 1kHz measurements at +/-3.3V, gain about 0.243 and 22kHz analyzer bandwidth, not absolute current ratings [2, p.7].
- **Size output RS for hot-plug short-circuit dissipation as well as damping.** AN-1429's >= 10 ohm recommendation for amplifiers with > 200mA short-circuit current comes from its +/-5V, 2V RMS output thermal example; verify the actual part, package, board and ambient instead of applying 10 ohm universally [2, p.6].
- **AN-1429 recommends <= 1K resistors in its low-noise output-stage design.** Its 1K noise example is approximately 4nV/sqrt(Hz); this does not prohibit the same note's 4K I-to-V feedback resistor [2, pp.3,7].
- **AN-1429 recommends NP0/C0G signal-path capacitors for low distortion.** Use thin-film resistors for optimum THD; metal-film is also suitable [2, p.8].
- **AN-1429 recommends an LDO and 0.1uF + 4.7uF near headphone op-amp supplies.** For exposed-pad packages, use the exact part's specified pad potential; the thermal plane is not arbitrarily ground or power [2, p.8].

### Mixed-Signal Grounding for Audio

- **Apply the low-digital-current grounding scheme only to devices that meet that condition.** ADI's scheme joins AGND/DGND locally and filters VD with a low-Q ferrite when it comes from a noisy digital supply; high digital-current devices require their own grounding strategy -> `misc/adc-dac.md` [5, Grounding and Decoupling Mixed-Signal ICs with Low Digital Currents].
- **Sampling-clock jitter limits use analog input frequency, not sample rate.** ADI's example uses 100kHz input and 50ps RMS jitter for approximately 90dB jitter-only SNR; this is not an I2S BCLK-jitter specification for a codec [5, Sampling Clock Considerations; 8, p.16].

## Common Mistakes

- **Using an arbitrary resistor as the microphone's balanced reference.** The reference impedance should match the microphone output impedance; a 200 ohm value belongs to AN-1003's 200 ohm microphone example [1, p.7].
- **Reading AN-1429's headphone-voltage table as sinusoidal peak headroom.** Its SE215 example obtains 0.632V from sqrt(19.953mW * 20 ohm): that is an RMS-equivalent sine voltage. A sine wave needs sqrt(2) times that voltage/current for instantaneous peak headroom [2, pp.4-5].
- **Assuming filterless means any speaker or cable.** MAX98357A requires > 10uH speaker series inductance; WM8960 recommends additional passive output filtering for speaker connections longer than about 100mm, positioned near the codec [8, p.33; 9, p.43].

## Formulas

**Helmholtz resonance estimate for the AN-1003 cavity geometry [1, p.3]:**
**Rule of thumb:** Minimize cavity volume and avoid a narrow vent feeding a wide gasket cavity; the estimate is not a guaranteed resonance frequency because flexible walls and leakage change the result.
**Formula:** f_b = (c * D) / (4 * sqrt(pi * V * (L + pi * D / 2))), with c in m/s, D and L in m, V in m^3, f_b in Hz.
**Example:** c=340m/s, D=0.001m, V=5e-9m^3, L=0.001m -> f_b=13.38kHz. This is within the audio band; reduce cavity volume or widen the vent, then verify the acoustic response.

## Sources

### Related Rules

- `guides/pcb-layout.md` -- General grounding and layout practices
- `misc/adc-dac.md` -- ADC/DAC precision, mixed-signal grounding, anti-aliasing

### References

1. TDK InvenSense AN-1003-00 (Rev.1.0, December 2013) -- Recommendations for Mounting and Connecting MEMS Microphones: https://invensense.tdk.com/wp-content/uploads/2015/02/Recommendations-for-Mounting-and-Connecting-InvenSense-MEMS-Microphones.pdf
2. ADI AN-1429 (Rev.0, October 2016) -- Design Considerations for Headphone Drivers in Mobile Phones: https://www.analog.com/media/en/technical-documentation/application-notes/AN-1429.pdf
3. TI SLAA896 (January 2020) -- PCB Layout Guidelines for TAS2xxx Class-D Boosted Audio Amplifier: https://www.ti.com/lit/an/slaa896/slaa896.pdf
4. TI SLAA404C (April 2010) -- Design and Configuration Guide for TLV320AIC3204/AIC3254 Audio Codecs: https://www.ti.com/lit/an/slaa404c/slaa404c.pdf
5. ADI -- Staying Well Grounded (Analog Dialogue 46-06, June 2012): https://www.analog.com/en/resources/analog-dialogue/articles/staying-well-grounded.html
6. TDK InvenSense -- Analog and Digital MEMS Microphone Design Considerations: https://invensense.tdk.com/wp-content/uploads/2015/02/Analog-and-Digital-MEMS-Microphone-Design-Considerations.pdf
7. TI SLAAED0 (March 2024) -- Introduction to Click and Pop Noise Measurement in Class-D Audio Amplifiers: https://www.ti.com/lit/pdf/slaaed0
8. ADI MAX98357A/MAX98357B (19-6779 Rev.16, February 2026) -- Datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/max98357a-max98357b.pdf
9. Cirrus Logic WM8960 (Rev.4.4) -- Datasheet (manufacturer document mirrored by Adafruit): https://cdn-learn.adafruit.com/assets/assets/000/096/503/original/WM8960_v4.4.pdf
10. Knowles SPH0645LM4H-B (Rev.B) -- Datasheet (manufacturer document mirrored by Adafruit): https://cdn-shop.adafruit.com/product-files/3421/i2S+Datasheet.PDF
