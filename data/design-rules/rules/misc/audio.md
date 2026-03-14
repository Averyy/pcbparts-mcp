# Audio

> I2S interface, audio codec integration, Class-D amplifier layout, MEMS microphones, headphone driver design, mixed-signal grounding for audio. General grounding -> `guides/pcb-layout.md`. ADC/DAC precision -> `misc/adc-dac.md`.

## Quick Reference

- **Codec AGND and DGND pins: tie together, return to analog ground plane.** DGND label refers to internal connection, not system digital ground. Separating them to different planes injects switching noise directly between the pins.
- **Class-D output traces: >= 0.76 mm (30 mil) wide per layer, two layers minimum (1.52 mm effective).** Length-match OUT_P/OUT_N for THD+N. EMI filter at device pins, not at speaker.
- **MEMS mic PCB hole >= 0.25mm diameter.** 0.5-1.0mm typical. Avoid Helmholtz resonance: gasket cavity diameter must be close to or smaller than vent opening.
- **MAX98357A: I2S DAC + 3.2W Class-D, no MCLK required.** 2.5-5.5V, filterless output, built-in click/pop reduction. Channel select via SD pin logic level.
- **TLV320AIC3204: stereo codec, I2C/SPI config, PowerTune 4 modes.** PTM_P4/PTM_R4 highest SNR (100 dB at 32 ohm), PTM_P1 lowest power. 20+ bit word length required for PTM_P4.

## Design Rules

### I2S Interface

- **Two PDM microphones share one data line.** Each mic outputs on opposite clock edge. L/R SELECT pin assigns channel. Maximum intrachannel time difference = half clock period (~167ns at 3 MHz PDM clock).
- **Source termination 20-100 ohm on PDM/I2S clock for traces > 15cm.** Matches trace characteristic impedance, eliminates ringing. For shorter traces at lower clock rates, direct connection acceptable.

### Audio Codec Integration

- **TLV320AIC3204 clock strategy: start from bottom up.** Select AOSR/DOSR first (Filter A: AOSR=128 for <= 48kHz, Filter B: AOSR=64 for 96kHz, Filter C: AOSR=32 for 192kHz). Then MADC/MDAC, then NADC/NDAC. Verify (MDAC * DOSR) / 32 >= resource class of selected processing block.
- **CODEC_CLKIN range: 512kHz to 50MHz without PLL.** With PLL: up to 137MHz (NADC/NDAC both even). PLL needed when integer dividers cannot yield target sample rate from available master clock.
- **WM8960: I2C-configured stereo codec with 1W Class-D speaker drivers + headphone drivers.** I2C address: 0x1A (7-bit). Datasheet shows 0x34 = left-shifted write address. Requires MCLK input (256*fs typical): 12.288 MHz for 48 kHz, 11.2896 MHz for 44.1 kHz. Internal PLL can derive MCLK from BCLK if no dedicated oscillator available. On-chip ALC, PGA, pop/click suppression.
- **Power sequencing (TLV320AIC3204): IOVDD first (or simultaneous with others), hold RESET low until all supplies stable.** AVDD last. LDO_SELECT pin must see correct logic level at boot -- pull to IOVDD for internal LDO, tie to IOVSS for external supply.
- **Separate analog ground plane shorted at one point near codec.** AIC32x4 pinout organized with digital pins on one side, analog on the other -- orient layout to maintain separation.

### Class-D Amplifier Layout

- **TAS2xxx ground: short all GND pins (BGND, GND, PGND, GNDD) on top layer directly under package.** Stitch to dedicated ground layer (layer 2) through multiple vias on device pads. No ground loops between different GND pins.
- **Decoupling cap parasitic budget (TAS2562):** total loop inductance from pin through cap and back:

| Net | Max pin-pin inductance (pH) | Max cap ESL (pH) | Max total (pH) |
|-----|---------------------------|-------------------|-----------------
| VBST-BGND | 250 | 500 | 750 |
| GREG-PVDD | 300 | 500 | 800 |
| VDD-GND | 350 | 500 | 850 |
| VBAT-GND | 650 | 500 | 1150 |

- **Switching nets (Class-D output, SW node, Vsense) must not run parallel to any other signal on adjacent layers without ground shielding between.** Route on different layers with ground plane separating. Cross at right angles if overlap unavoidable.
- **Charge pump cap (GREG to PVDD): star-connect at PVDD pin, not to PVDD plane.** Thick traces, route on top layer or immediately below. Multiple vias for layer transitions.
- **VBST to PVDD: connect on top layer directly under device.** Via parasitic inductance causes ringing and efficiency loss if routed through inner layers.
- **Vsense traces: route differentially, as close to speaker terminals as possible.** 0.15 mm (6 mil) width sufficient. Speaker protection algorithm accuracy depends on sensing actual terminal voltage, not PCB voltage.

### Click and Pop Noise

- **TAS2780/TAS2781: 0.8mV typical click and pop (-62 dBV).** TAS2764: 1mV typical. Measured A-weighted, filter-free, with 4 ohm + 15uH load.
- **Noise gate: Class-D auto-shuts down when input < threshold for > 50ms.** Default threshold -120 dBFs on TAS27xx. Each noise gate entry/exit produces regulated pop. Setting threshold higher than default increases pop amplitude.
- **High pop triggers: software/hardware reset, fault conditions (OCP, OTP, clock error), supply dips/overshoots.** These cause abrupt shutdown -- uncontrolled pop, potentially much larger than normal operation.
- **TAS2764 pop optimization: force device into idle channel mode before shutdown** (register 0x64 = 0x04), then software shutdown. Exit idle channel mode after power-up. TAS2780/TAS2781 handle this internally.
- **Y-bridge mode (TAS27xx): switches on VBAT instead of PVDD for low-level signals.** Reduces switching losses and minimizes differential error buildup during power transitions -- directly reduces pop.

### MEMS Microphone Integration

- **Analog MEMS mic: Knowles SPH8878LR5H-1 (bottom-port, low noise), TDK/InvenSense ICS-40180 (wide bandwidth, low distortion).** Both ~200 ohm output impedance, 1.8-3.3V supply.
- **Digital MEMS mic (I2S output): Knowles SPH0645LM4H.** Integrated decimation filter, connects directly to MCU/DSP without codec. 3.76 x 4.72 x 1.0 mm.
- **Digital MEMS mic (PDM output): TDK/InvenSense ICS-41350 (low noise, SNR 65 dB).** PDM is most common digital mic interface. Requires codec or DSP with PDM input for decimation.
- **Bottom-port mounting: PCB hole admits sound through board.** Align package hole with PCB hole. Performance unaffected by PCB thickness. Flexible PCB mounting with adhesive provides reliable seal and shortest acoustic path.
- **Helmholtz resonance from gasket cavity:** wide gasket between PCB and device case creates resonant cavity. Fix: gasket as small as possible, or effective path diameter close to vent size. Multiple small holes replace single large vent if needed.
- **Analog MEMS output impedance ~200 ohm.** PGA input impedance at high gain can drop to 2 kohm -- 200 ohm source into 2 kohm load attenuates signal ~10%. Verify codec input impedance at operating gain setting.
- **Balanced routing for analog MEMS: add 200 ohm resistor at mic ground reference.** Route reference trace in parallel with signal to differential codec input (LINN/LINP). Rejects RF interference even with imperfect matching.
- **AC coupling: 1.0uF minimum for 100 Hz mic rolloff into 10 kohm input impedance.** Corner at 16 Hz -- well below mic natural rolloff. Smaller caps risk audible low-frequency attenuation.
- **PDM clock typically ~3 MHz.** Two mics on one data line, each valid on opposite clock edge. Separate 0.1uF VDD bypass per microphone if distance between mics is significant.

### Headphone Driver Design

- **I-to-V stage: maximize gain in first stage for lowest noise.** RF = VOUT_max / IOUT_max (typically 4 kohm for 1mA DAC output). CF = 1/(2*pi*RF*fc), RS = 100 ohm for stability. ADA4841-2 or ADA4896-2 recommended.
- **Output stage op-amp: must achieve < -100 dB THD+N at 32 ohm load.** ADA4841-2 (29.1 mA into 32 ohm at < -100 dB THD+N, low cost), ADA4807-2 (42.1 mA into 32 ohm, 1.2 mA Iq, RRIO with disable), AD8397 (125 mA max output, 250 mW into 16 ohm, highest current).
- **Output series resistor RS sets damping factor (RL/RS).** Lower RS = better distortion. But RS protects amp from output short during hot-plug. RS = 10 ohm minimum if short-circuit current > 200 mA.
- **Keep all resistors in audio path <= 1 kohm.** 1 kohm contributes 4 nV/sqrt(Hz) noise -- comparable to op-amp voltage noise. Higher values dominate noise floor.
- **NP0/C0G ceramics in audio signal path.** Better distortion than X5R/X7R due to zero piezoelectric effect. Thin film resistors for optimum THD; metal film acceptable.
- **LDO power supply for headphone op-amps.** Decouple with 0.1uF + 4.7uF at op-amp power pins. Solder exposed pad to board, connect via array to ground/power plane for thermal dissipation.

### Mixed-Signal Grounding for Audio

- **AGND/DGND pin names describe internal IC connections, not system ground assignment.** Both pins of a low-digital-current converter (most audio codecs) go to analog ground plane. Extra impedance on DGND path couples more digital noise into analog via internal stray capacitance.
- **Isolate converter VD pin with ferrite bead, decouple to analog ground.** Digital transient currents flow in small loop: VD -> decoupling cap -> DGND. Loop stays local, does not contaminate analog ground plane. Use low-Q non-resonant ferrite bead.
- **Buffer register at ADC digital output isolates converter from bus noise.** Acts as Faraday shield. Series 500 ohm resistors between ADC output and buffer input limit transient current to ~10 mA and form RC low-pass with ~10pF gate capacitance (t_rise ~11 ns).
- **Sampling clock: treat as analog signal.** Ground and decouple clock oscillator to analog ground plane. Phase noise directly degrades SNR: SNR = -20*log10(2*pi*f*tj). At 100 kHz input, 50 ps jitter = 90 dB SNR ceiling.
- **Ground potential between AGND and DGND planes must stay < 300 mV** or IC damage possible. Back-to-back Schottky diodes between planes as safety clamp. Alternative: ferrite bead DC connection (but may create ground loop in high-resolution systems).

## Common Mistakes

- **Codec DGND pin connected to digital ground plane.** Injects full system digital noise between AGND and DGND pins. Both should go to analog ground plane with ferrite bead on VD supply pin.
- **Charge pump cap routed to PVDD plane instead of star-connected at pin.** Parasitic inductance from plane routing causes voltage ringing on GREG/VREG, degrading charge pump performance and audio quality.
- **MEMS mic gasket creates Helmholtz resonator.** Wide cavity with narrow vent produces high-frequency peak. Redesign gasket to minimize cavity volume or match cavity diameter to vent diameter.
- **Noise gate threshold set higher than default on TAS27xx.** Increases click and pop amplitude on every gate entry/exit. Keep at -120 dBFs default unless application specifically requires otherwise.
- **MCLK routed near analog input traces on codec.** MCLK (12.288 MHz typical) couples into high-impedance mic/line inputs via crosstalk, appearing as a fixed-pitch whine above the noise floor. Route MCLK on inner layer shielded by ground, or on opposite board side from analog inputs with >= 5mm separation.
- **Ferrite bead on Class-D PVDD resonates with bulk cap.** Ferrite impedance peaks at 100-300 MHz but its inductance (~1uH) resonates with the 10-22uF PVDD bypass cap at 30-50 kHz, amplifying switching noise in the audible band. Use direct low-impedance connection to battery/supply; EMI filtering belongs at the speaker output, not the supply input.

## Formulas

**Helmholtz resonance frequency (MEMS mic cavity):**
**Rule of thumb:** Keep resonance above 20 kHz by minimizing cavity volume and maximizing vent diameter.
**Formula:** f_b = (c * D) / (4 * sqrt(pi * V * (L + pi*D/2)))
**Example:** c=340 m/s, D=1 mm vent, V=5 mm^3 cavity, L=1 mm vent length -> f_b ~ 340*0.001 / (4*sqrt(3.14 * 5e-9 * (0.001+0.00157))) = ~13.4 kHz. Below 20 kHz -- reduce cavity volume or widen vent.

**Headphone driver power requirement:**
**Rule of thumb:** 2 mW average sufficient for most headphones. Peak power 10-100x higher for live recording dynamics.
**Formula:** P_peak = 10^((RequiredSPL - Sensitivity) / 10), in mW
**Example:** 120 dB SPL target, Shure SE215 (107 dB/mW sensitivity, 20 ohm) -> P_peak = 10^(13/10) = 20.0 mW. V_peak = sqrt(P * R) = sqrt(0.020 * 20) = 0.63V. I_peak = V/R = 31.6 mA.

**Sampling clock jitter SNR ceiling:**
**Rule of thumb:** 50 ps jitter limits dynamic range to ~90 dB at 100 kHz input frequency.
**Formula:** SNR = -20 * log10(2 * pi * f * tj)
**Example:** f = 48 kHz (full audio band), tj = 50 ps -> SNR = -20*log10(2*3.14*48000*50e-12) = 100.4 dB. At f = 192 kHz: SNR = 88.3 dB -- jitter becomes the bottleneck for high sample rates.

## Sources

### Related Rules

- `guides/pcb-layout.md` -- General grounding and layout practices
- `misc/adc-dac.md` -- ADC/DAC precision, mixed-signal grounding, anti-aliasing

### References

1. AllAboutCircuits -- Introduction to the I2S Interface: https://www.allaboutcircuits.com/technical-articles/introduction-to-the-i2s-interface/
2. SparkFun -- Audio Codec Breakout WM8960 Hookup Guide: https://learn.sparkfun.com/tutorials/audio-codec-breakout---wm8960-hookup-guide/all
3. SparkFun -- I2S Audio Breakout Hookup Guide (MAX98357A): https://learn.sparkfun.com/tutorials/i2s-audio-breakout-hookup-guide
4. TDK InvenSense -- AN-1003: Recommendations for Mounting and Connecting MEMS Microphones: https://invensense.tdk.com/wp-content/uploads/2015/02/Recommendations-for-Mounting-and-Connecting-InvenSense-MEMS-Microphones.pdf
5. ADI -- AN-1429: Design Considerations for Headphone Drivers in Mobile Phones: https://www.analog.com/media/en/technical-documentation/application-notes/AN-1429.pdf
6. TI SLAA896 -- PCB Layout Guidelines for TAS2xxx Class-D Boosted Audio Amplifier: https://www.ti.com/lit/an/slaa896/slaa896.pdf
7. TI SLAA404C -- Design and Configuration Guide for TLV320AIC3204/AIC3254 Audio Codecs: https://www.ti.com/lit/an/slaa404c/slaa404c.pdf
8. ADI -- Staying Well Grounded (Hank Zumbahlen, Analog Dialogue): https://www.analog.com/en/resources/analog-dialogue/articles/staying-well-grounded.html
9. TI SLYT499 -- Grounding in Mixed-Signal Systems Demystified, Part 1: https://www.ti.com/lit/an/slyt499/slyt499.pdf
10. TDK InvenSense -- Analog and Digital MEMS Microphone Design Considerations: https://invensense.tdk.com/wp-content/uploads/2015/02/Analog-and-Digital-MEMS-Microphone-Design-Considerations.pdf
11. TI SLAAED0 -- Introduction to Click and Pop Noise Measurement in Class-D Audio Amplifiers: https://www.ti.com/lit/pdf/slaaed0
