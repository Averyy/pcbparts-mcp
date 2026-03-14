---
source: "ST AN2867 -- Oscillator Design Guide for STM8/STM32"
url: "https://www.st.com/resource/en/application_note/an2867-oscillator-design-guide-for-stm8af-al-s-and-stm32-microcontrollers-stmicroelectronics.pdf"
format: "PDF 59pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 24478
---
# Guidelines for oscillator design on STM8AF/AL/S and STM32 MCUs/MPUs

## Introduction

Many designers know oscillators based on Pierce-Gate topology (Pierce oscillators), but not all of them really understand how they operate, and only a few master their design. In practice, limited attention is paid to the oscillator design, until it is found that it does not operate properly (usually when the final product is already in production). A crystal not working as intended results in project delays, if not overall failure.

The oscillator must get the proper amount of attention during the design phase, well before moving to manufacturing, to avoid the nightmare scenario of products failing in application.

This document introduces the Pierce oscillator basics, and provides guidelines for its design. It also shows how to determine the external components, and provides guidelines for correct PCB design and for selecting crystals and external components.

To speed up the application development, the recommended crystals (HSE and LSE) for the applicable products are detailed in Section 5 (Recommended resonators for STM32 MCUs/MPUs) and Section 6 (Recommended crystals for STM8AF/AL/S MCUs).

**Applicable products:** STM8S series, STM8AF series, STM8AL series, STM32 32-bit Arm Cortex MCUs (Wireless, Ultra Low Power, High Performance), STM32 Arm Cortex MPUs.

## 1 Quartz crystal properties and model

A quartz crystal is a piezoelectric device converting electric energy into mechanical energy, and vice versa. The transformation occurs at the resonant frequency.

**Equivalent circuit model:**
- C0: shunt capacitance resulting from the capacitor formed by the electrodes
- Lm (motional inductance): represents the vibrating mass of the crystal
- Cm (motional capacitance): represents the elasticity of the crystal
- Rm (motional resistance): represents the circuit losses

*[Figure 1. Quartz crystal model]*

The impedance of the crystal (assuming Rm is negligible) is:

Z = (j/w) x (w^2 x Lm x Cm - 1) / ((C0 + Cm) - w^2 x Lm x Cm x C0)

*[Figure 2. Impedance in the frequency domain]*

**Fs** is the series resonant frequency when Z = 0:

Fs = 1 / (2pi x sqrt(Lm x Cm))

**Fa** is the antiresonant frequency when Z tends to infinity:

Fa = Fs x sqrt(1 + Cm/C0)

The region delimited by Fs and Fa is the area of parallel resonance. In this region, the crystal operates in parallel resonance and behaves as an inductance. Its frequency Fp (or FL: load frequency) has the following expression:

Fp = Fs x (1 + Cm / (2 x (C0 + CL)))

The oscillation frequency of the crystal can be tuned by varying the load capacitance CL. Crystal manufacturers indicate the exact CL required to make the crystal oscillate at the nominal frequency.

**Table 2. Example of equivalent circuit parameters (8 MHz crystal)**

| Equivalent component | Value |
|---|---|
| Rm | 8 ohm |
| Lm | 14.7 mH |
| Cm | 0.027 pF |
| C0 | 5.57 pF |

Using the equations above: Fs = 7988768 Hz, Fa = 8008102 Hz. If CL = 10 pF, the crystal oscillates at Fp = 7995695 Hz. To have exactly 8 MHz, CL must be 4.02 pF.

## 2 Oscillator theory

This section deals only with harmonic oscillators, with particular focus on Pierce oscillators. All the oscillators requiring external passive components covered by this document are of the Pierce type.

The harmonic oscillator family can be divided into two main subfamilies:
- Negative-resistance oscillators
- Positive-feedback oscillators

STM32 microcontrollers and microprocessors feature low-speed external (LSE) and high-speed external (HSE) oscillators designed according to the negative-resistance principle.

### 2.1 Negative resistance

The term negative resistance is a misnomer of negative transresistance, defined as the ratio between a given voltage variation (delta-V) and the induced current variation (delta-I). Unlike the resistance (always positive), the transresistance (also known as differential resistance) can be either positive or negative.

*[Figure 3. I-V curve of a dipole showing a negative trans-resistance area]*

### 2.2 Transconductance

Similarly to the conductance (inverse of resistance), the transconductance is defined as the inverse of the transresistance. Transconductance can also be defined as the differential conductance, expressed as delta-I / delta-V.

### 2.3 Negative-resistance oscillator principles

An oscillation loop is made of two branches:
- **Active branch:** composed by the oscillator itself, provides energy to start and build up oscillation, and compensates for passive branch losses
- **Passive branch:** mainly composed by the resonator, the two load capacitors and all parasitic capacitances

*[Figure 4. Block diagram of a typical oscillation loop based on a crystal resonator]*

At startup, the oscillator transconductance must be higher than (multiple of) the conductance of the passive part to maximize the possibility to build up oscillation. An excessive transconductance can saturate the oscillation loop, and cause a startup failure.

To ensure successful oscillator start and maintain stable oscillation, the ratio between the negative resistance of the loop and the crystal maximal equivalent series resistance (ESR) is specified for STM32 and STM8 products. It is recommended to have a ratio higher than 5 for HSE oscillators, and higher than 3 for LSE oscillators.

## 3 Pierce oscillator design

### 3.1 Introduction to Pierce oscillators

Pierce oscillators are variants of Colpitts oscillators, widely used with crystal resonators. A Pierce oscillator requires a reduced set of external components, resulting in lower design cost. Known for stable oscillation frequency when paired with a crystal resonator.

*[Figure 5. Pierce oscillator circuitry]*

Components:
- **Inv:** internal inverter that works as an amplifier
- **Q:** crystal quartz or ceramic resonator
- **RF:** internal feedback resistor
- **RExt:** external resistor to limit the inverter output current
- **CL1, CL2:** two external load capacitances
- **Cs:** stray capacitance (sum of device pin OSC_IN/OSC_OUT and PCB parasitic capacitances)

### 3.2 Feedback resistor

In most MCUs/MPUs manufactured by ST, RF is embedded in the oscillator circuitry. Its role is to make the inverter act as an amplifier by biasing it at Vout = Vin, forcing operation in the linear region.

**Table 3. Typical feedback resistor values for given frequencies**

| Frequency | Feedback resistor range |
|---|---|
| 32.768 kHz | 10 to 25 Mohm |
| 1 MHz | 5 to 10 Mohm |
| 10 MHz | 1 to 5 Mohm |
| 20 MHz | 470 kohm to 5 Mohm |

### 3.3 Load capacitance

The load capacitance is the terminal capacitance of the circuit connected to the crystal oscillator, determined by CL1, CL2, and stray capacitance Cs. The CL value is specified by the crystal manufacturer.

CL = (CL1 x CL2) / (CL1 + CL2) + Cs

For example, with CL = 15 pF and Cs = 5 pF:
(CL1 x CL2) / (CL1 + CL2) = CL - Cs = 10 pF, hence CL1 = CL2 = 20 pF.

### 3.4 Oscillator transconductance

Two approaches to check if an STM32 oscillator can be paired with a given resonator:

**If Gm_crit_max is specified:** Ensure it is greater than the oscillation loop critical crystal gain (gmcrit).

**If gm is specified:** Ensure the gain margin ratio (gain_margin = gm / gmcrit) is bigger than 5.

Where gmcrit is the minimal transconductance required to maintain stable oscillation:

gmcrit = 4 x ESR x (2pi x F)^2 x (C0 + CL)^2

**Example:** For STM32F1 HSE oscillator (gm = 25 mA/V) with an 8 MHz crystal (C0 = 7 pF, CL = 10 pF, ESR = 80 ohm):
- gmcrit = 4 x 80 x (2pi x 8e6)^2 x (7e-12 + 10e-12)^2 = 0.23 mA/V
- gain_margin = 25 / 0.23 = 107 (sufficient, > 5)

If gain_margin < 5, select a crystal with lower ESR and/or lower CL.

The conversion between gm and Gm_crit_max is: Gm_crit_max = gm / 5.

> Note: Before any verification, the crystal chosen must vibrate at a frequency that respects the oscillator frequency range given in the STM32 datasheet.

After calculating RExt, recalculate the gain margin with RExt added to ESR:
gm >> gmcrit = 4 x (ESR + RExt) x (2pi x F)^2 x (C0 + CL)^2

### 3.5 Drive level and external resistor calculation

#### 3.5.1 Calculating the drive level

The drive level (DL) is the power dissipated in the crystal. It must be limited to prevent crystal failure from excessive mechanical vibrations. Maximum drive level is specified by the crystal manufacturer (usually in mW).

DL = ESR x IQ^2

Where ESR = Rm x (1 + C0/CL)^2 and IQ is the current flowing through the crystal in RMS.

Maximum peak-to-peak current: IQmax_PP = 2 x sqrt(2 x DLmax / ESR)

If IQ exceeds IQmax, an external resistor RExt is mandatory.

*[Figure 7. Current drive measurement with a current probe]*

#### 3.5.2 Another drive level measurement method

DL can be computed as DL = IQRMS^2 x ESR, where IQRMS = 2pi x F x VRMS x Ctot.

Ctot = CL1 + (Cs / 2) + Cprobe

DL = ESR x (pi x F x Ctot)^2 x (Vpp)^2 / 2

This value must not exceed the drive level specified by the crystal manufacturer.

> Note: Use special care when measuring voltage swing at LSE input, as it is very sensitive to load capacitance. Use a 0.1 pF input capacitance probe.

#### 3.5.3 Calculating the external resistor

The role of RExt is to limit the drive level of the crystal. With CL2, it forms a low-pass filter that forces the oscillator to start at the fundamental frequency.

If power dissipated is higher than manufacturer spec, RExt is mandatory. If lower, RExt = 0 ohm.

Initial estimation: RExt = 1 / (2pi x F x CL2)

Example: 8 MHz with CL2 = 15 pF gives RExt = 1326 ohm.

Recommended optimization: use a potentiometer initially set to the capacitive reactance of CL2, then adjust until acceptable output and crystal drive level are obtained.

> Caution: After calculating RExt, recalculate the gain margin to ensure RExt has no negative effect on the oscillation condition.

> Note: If RExt is too low, there is considerable increase of power dissipation by the crystal. If too high, there is no oscillation.

### 3.6 Startup time

The time required by the oscillation to start and build up until it reaches a stable phase. Depends on the Q-factor of the resonator. Quartz-crystal resonators have higher Q-factor (longer startup) than ceramic resonators. Also depends on external components CL1, CL2, and crystal frequency.

- Higher nominal frequency = lower startup time
- Few MHz crystal: typically starts up after a few ms
- 32.768 kHz crystal: startup time ranges between 1 and 5 s
- Startup problems usually arise from improperly dimensioned gain margin

### 3.7 Crystal pullability

Crystal pullability (sensitivity) measures the impact of small variations of load capacitance on oscillation frequency shifting. More important for low-speed oscillators (RTC clocking).

Pullability (PPM/pF) = (Cm x 10^6) / (2 x (C0 + CL)^2)

Higher load capacitance = lower pullability = more stable frequency.

Example: crystal with 45 PPM/pF pullability, CL1 = CL2 = 7 pF (C0G ceramic, +/-5% tolerance). The +/-5% tolerance on CL causes +/-0.175 pF variation, inducing:
0.175 pF x 45 PPM/pF = ~7.8 PPM (~0.7 s/day for RTC)

### 3.8 Safety factor

#### 3.8.1 Definition

The safety factor measures the oscillator's ability not to fail under operating conditions. It is the ratio between the oscillator negative resistance and the crystal ESR:

Sf = (RADD + Crystal ESR) / Crystal ESR

#### 3.8.2 Measurement methodology

A resistance is added in series to the resonator. The oscillator negative resistance is the value of the smallest series resistance RADD preventing the oscillator from starting up successfully. Found by incrementally increasing the series resistance until failure.

*[Figure 8. Negative resistance measurement methodology description]*

#### 3.8.3 Safety factor for STM32 and STM8 oscillators

**Table 4. Safety factor (Sf) for STM32 and STM8 oscillators**

| Safety factor (Sf) | HSE | LSE |
|---|---|---|
| Sf >= 5 | Safe | Very safe |
| 3 <= Sf < 5 | Not safe | Safe |
| Sf < 3 | Not safe | Not safe |

### 3.9 Oscillation modes

#### 3.9.1 What are fundamental and overtone modes?

A crystal can vibrate at the fundamental frequency Fp and at odd multiples (overtone modes). An AT-cut quartz crystal impedance reaches zero for the fundamental and its odd multiples.

*[Figure 9. Fundamental and overtone frequencies of an AT-cut quartz crystal]*

> Note: AT-cut quartz corresponds to most crystals used with HSE. For LSE, tuning fork crystals are used (different oscillation mode behavior).

#### 3.9.2 Third overtone mode: pros and cons

Crystals designed for high frequency fundamental mode are very expensive above ~50 MHz. Most high frequency crystals are designed for third overtone mode (cut for frequency 3x lower).

Third overtone characteristics:
- Rm approximately 3x higher, Cm 9x lower than fundamental mode
- Higher Q-factor (less energy loss, more stable, better jitter, lower pullability)
- Lower pullability = lower frequency shift in field, but lower tunability

#### 3.9.3 Considerations for STM32 products

The oscillators integrated in STM32 products have been validated for use in fundamental mode. If a third overtone crystal is used with the standard Pierce implementation, theory indicates it will not start at the third harmonic but at the fundamental.

> Note: The startup mode can involuntarily balance between modes if external components are not chosen properly.

## 4 Guidelines to select a suitable crystal and external components

### 4.1 Low-speed oscillators embedded in STM32 MCUs/MPUs

Resonator selection depends on:
- Crystal size or footprint
- Crystal load capacitance (CL)
- Oscillation frequency offset (PPM)
- Startup time

*[Figure 12. Classification of low-speed crystal resonators]*

**High CL (e.g. 12.5 pF):** More robust against noisy environments, lower pullability, but higher power consumption.

**Low CL (e.g. <= 6 pF):** Lower power consumption, but higher pullability.

Two types of LSE oscillators in STM32:
- **Constant gain:** Compatible with limited crystal range. E.g. STM32F2/L1 (low power targets), STM32F1.
- **Configurable gain:** Compatible with large range of crystals. Can be dynamically or statically modifiable.

> Caution: In STM32F0 and STM32F3, High drive mode (gm = 25 uA/V) must only be used with 12.5 pF crystals to avoid saturating the oscillation loop. Low CL crystals (e.g. 6 pF) will cause frequency jitter and duty cycle distortion.

**Table 5. LSE oscillators embedded into STM32 MCUs/MPUs**

| Series | Drive level | gm (min) (uA/V) | Gm_crit_max (uA/V) |
|---|---|---|---|
| C0 | Medium high / High | 8.5 / 13.5 | 1.7 / 2.7 |
| F0, F3 | Low / Medium low / Medium high / High | 5 / 8 / 15 / 25 | 1.0 / 1.6 / 3 / 5 |
| F1, T | (not available) | 5 | 1 |
| F2, F4_g1 | (not available) | 2.8 | 0.56 |
| F4_g2 | Low / High | 2.8 / 7.5 | 0.56 / 1.5 |
| F7 | Low / Medium low / Medium high / High | 2.4 / 3.75 / 8.5 / 13.5 | 0.48 / 0.75 / 1.7 / 2.7 |
| L1 | (not available) | 3 | 0.6 |
| G0, G4, H7 | Low / Medium low | 2.5 / 3.75 | 0.5 / 0.75 |
| L0, L4, L4+, L5, MP1, MP2 | Medium low / Medium high | 3.75 / 8.5 | 0.75 / 1.7 |
| N6, U0, U3, U5 | Medium high / High | 8.5 / 13.5 | 1.7 / 2.7 |
| WB, WB0, WBA, WL | Medium high / High | 8.5 / 13.5 | 1.7 / 2.7 |
| H5 | Medium low / Medium high / High | 3.75 / 8.5 / 13.5 | 0.75 / 1.7 / 2.7 |

Notes:
- F4_g1 = STM32F401/405/407/415/417/427/429/437/439xx (non-modifiable transconductance)
- F4_g2 = STM32F410/411/412/413/423/446/469/479xx (statically modifiable)
- STM32U575/585 rev. X do not support low drive mode
- STM32WBA devices do not support low drive mode

### 4.2 How to select an STM32-compatible crystal

**Step 0:** Choose a fundamental mode designed resonator (STM32 oscillators are validated for fundamental mode with Pierce oscillator circuitry).

**Step 1:** Check resonator compatibility with selected STM32. Use either gm or Gm_crit_max procedure from Section 3.4. Gain margin ratio must be > 5.

**Step 2:** Determine CL1 and CL2 values using formula from Section 3.3. Fine-tune experimentally using a standard crystal with known PPM drift. Iterate: if frequency slower than target, decrease capacitance; if faster, increase capacitance.

**Step 3:** Check the safety factor (Section 3.8) to ensure safe oscillation under operating conditions.

**Step 4:** Calculate drive level (Section 3.5). If DL > DLcrystal, calculate RExt. Recalculate gain margin with RExt. If gain margin > 5, crystal is suitable. Otherwise, choose a different crystal.

**Step 5 (optional):** Calculate PPM accuracy budget:
PPM_Budget = PPM_crystal + Deviation(CL) x Pullability_crystal

> Note: The PPM budget does not account for temperature variation.

> Note: Many crystal manufacturers can check device/crystal pairing compatibility upon request and provide a report with recommended CL1, CL2 values and oscillator negative resistance measurement.

## 5 Recommended resonators for STM32 MCUs/MPUs

### 5.1 STM32-compatible high-speed resonators

The HSE oscillator embedded in STM32 products is compatible with almost all resonators available on the market. Recommended resonator manufacturers include: ABRACON, ECS, EPSON, KYOCERA, Micro Crystal, muRata, NDK, RIVER.

Several tools are available: STM32 Crystal Selection Tool from ECS, IC Matching Information from NDK.

> Note: Not applicable for STM32WB, STM32WB0, STM32WBA, STM32WL series due to RF constraints. Refer to AN5042 for those devices.

**Table 6. HSE oscillators embedded in STM32 MCUs/MPUs**

| Parameter | F0/F1/F3/T | F2/F4 | F7 | L0/L1 | C0/G0/G4/L4/L4+/L5/U0 | H7/U3/U5/MP1 | H5/MP2 | N6 |
|---|---|---|---|---|---|---|---|---|
| Frequency range (MHz) | 4-32 | 4-16 | 4-25 | 1-25 | 4-26 | 4-48 | 4-50 | 16-48 |
| gm min (mA/V) | 10 | 25 | 5 | 3.5 | 5 | 7.5 | 7.5 | 12.5 |
| Gm_crit_max (mA/V) | 2 | 5 | 1 | 0.7 | 1 | 1.5 | 1.5 | 2.5 |

### 5.2 STM32-compatible low-speed resonators

Table 7 contains a non-exhaustive list of 32.768 kHz resonators compatible with STM32 products, checked by ST. Multiple footprint sizes are provided (1.2x1.0, 1.6x1.0, 2.0x1.2, 3.2x1.5 mm).

**Key manufacturers and example part numbers:**

**1.2 x 1.0 mm:**
- RIVER TFX-05X (ESR 90 kohm, C0 1.5 pF, CL 5-12.5 pF)
- SII SC-12S (ESR 90 kohm, C0 1.4 pF, CL 6-12.5 pF)
- ECS ECS-.327-x-1210-TR (ESR 90 kohm, C0 1.1 pF, CL 6-12.5 pF)
- ECS ECS-.327-x-1210B-N-TR (ESR 80 kohm, C0 1.5 pF, CL 5-12.5 pF)
- ABRACON ABS04W-32.768kHz (ESR 80 kohm, C0 1.5 pF, CL 4-12.5 pF)

**1.6 x 1.0 mm:**
- Micro Crystal CM9V-T1A (ESR 90 kohm, C0 1.4 pF, CL 4-12.5 pF)
- ECS ECS-.327-x-16-TR (ESR 90 kohm, C0 1.3 pF, CL 6-12.5 pF)
- NDK NX1610SA/NX1610SE (ESR 60-80 kohm, C0 1.3-1.55 pF, CL 6-12.5 pF)
- ABRACON ABS05 series (ESR 70-80 kohm, CL 4-12.5 pF)

**2.0 x 1.2 mm:**
- Micro Crystal CM8V-T1A / CC8V-T1A (ESR 70-90 kohm, C0 1.2 pF, CL 4-12.5 pF)
- NDK NX2012SA/NX2012SE (ESR 50-80 kohm, C0 1.3-1.7 pF, CL 6-12.5 pF)
- EPSON FC-12M/FC-12D (ESR 75-90 kohm, C0 0.8-1.3 pF, CL 7-12.5 pF)
- CITIZEN CM2012H (ESR 70 kohm, C0 1.3 pF, CL 6-12.5 pF)

**3.2 x 1.5 mm:**
- ABRACON ABS07 series (ESR 50-80 kohm, CL 3-12.5 pF)
- Micro Crystal CM7V-T1A / CC7V-T1A (ESR 50-70 kohm, CL 6-12.5 pF)
- CITIZEN CM315D/CM315DL/CM315E (ESR 50-70 kohm, CL 4-12.5 pF)
- EPSON FC-135/FC-13A/FC-135R (ESR 50-70 kohm, CL 7-12.5 pF)
- ECS ECS-.327-x-34 series (ESR 60-70 kohm, CL 6-12.5 pF)
- RIVER TFX-03/TFX-03C (ESR 60-90 kohm, CL 5-12.5 pF)

**Compatibility notes:**
- CL 4-5 pF crystals: compatible with most STM32 series including F1, F2, F4, L1
- CL 6-7 pF crystals: compatible with most except F2, F4_g1, L1 (need low gmcrit)
- CL 9 pF crystals: compatible with C0, F0, F3, L0, L4, L4+, L5, G0, G4, F7, H5, H7, N6, WB, WBA, WL, MP1, MP2, U0, U3, U5
- CL 12.5 pF crystals: compatible with F0, F3 only (need high drive)

## 6 Recommended crystals for STM8AF/AL/S MCUs

### 6.1 Part numbers of recommended crystal oscillators

**KYOCERA compatible crystals:**
- 16.000 MHz: CX3225SB16000D0FLJC1 (CL 9 pF)
- 8.000 MHz: CX3225SB8000D0FLJCC (CL 10 pF)

**NDK compatible crystals:**
- 16.000 MHz: NX3225SA-16.000000MHz-G1 (CL 8 pF)
- 8.000 MHz: NX3225SA-8.000000MHz-B3 (CL 8 pF)

### 6.2 Recommended ceramic resonators

**Consumer applications (recommended conditions):**
- 16 MHz ceramic resonator: CL1 = CL2 = 15 pF
- 8 MHz ceramic resonator: CL1 = CL2 = 22 pF

**CAN-BUS applications (recommended conditions):**
- 16 MHz crystal: CL = manufacturer specified
- Tighter frequency tolerance required for CAN communication

## 7 Tips for improving oscillator stability

### 7.1 PCB design guidelines

To guarantee stable and reliable oscillation, follow these PCB design guidelines:

1. **Crystal placement:** Place the crystal and load capacitors as close as possible to the oscillator pins (OSC_IN and OSC_OUT). This minimizes stray capacitance and reduces the susceptibility to noise coupling.

2. **Guard ring:** Place a ground guard ring around the oscillator circuit to shield it from external noise. The guard ring should be connected to the ground plane through vias.

3. **Separate ground plane:** Use a separate (isolated) ground area for the oscillator circuit, connected to the main ground plane at a single point. This prevents noisy return currents from flowing under the oscillator.

4. **No signal routing:** Do not route any signal traces (especially high-speed or noisy signals) near the crystal, load capacitors, or oscillator pins. This includes power supply traces.

5. **Short symmetric traces:** Keep the traces between the crystal pads and the MCU oscillator pins as short and symmetric as possible.

6. **Same layer routing:** Route the crystal traces on the same PCB layer as the crystal. Avoid using vias in the oscillator circuit path.

7. **No copper under crystal:** Avoid routing copper traces (signal or power) under the crystal. If the crystal has a metallic case, connect it to ground.

8. **Load capacitor grounding:** Connect the ground terminals of the load capacitors directly to the oscillator ground, not to a general ground.

*[Figure 13. Recommended layout for an oscillator circuit]*

*[Figure 14. PCB with separated GND plane and guard ring around the oscillator]*

### 7.2 PCB design examples

Several examples are provided showing preliminary (non-compliant) vs. final (compliant) PCB layouts:

*[Figure 15. GND plane]*

*[Figure 16. Signals around the oscillator]*

*[Figure 17. Preliminary design (PCB design guidelines not respected)]*

*[Figure 18. Final design (following guidelines)]*

*[Figure 19. GND plane]*

*[Figure 20. Top layer view]*

*[Figure 21. PCB guidelines not respected]*

*[Figure 22. PCB guidelines respected]*

### 7.3 Soldering guidelines

The crystal must be soldered correctly to ensure reliable operation. Follow the soldering profile recommended by the crystal manufacturer. Excessive heat or prolonged soldering time can damage the crystal or shift its parameters.

### 7.4 LSE sensitivity to PC13 activity

On some STM32 devices, the PC13 GPIO pin is physically close to the LSE oscillator pins (OSC32_IN, OSC32_OUT). High-frequency toggling of PC13 can inject noise into the LSE oscillator, potentially causing frequency instability or even oscillation failure.

**Recommendations:**
- Avoid using PC13 as a high-frequency output when the LSE is active
- If PC13 must toggle, use the lowest possible output speed setting
- Keep PC13 trace routing away from the LSE circuit

## 8 Reference documents

- [1] Negative resistance model (referenced in oscillator theory section)

## 9 FAQs

Common questions about oscillator design for STM32/STM8 are addressed in this section, covering topics such as crystal selection, load capacitor sizing, startup issues, and PCB layout considerations. Refer to the full document for detailed FAQ content.

## 10 Conclusion

This application note provides the oscillator design guidelines for STM8AF/AL/S and STM32 MCUs/MPUs. It covers the Pierce oscillator fundamentals (negative resistance model, transconductance, gain margin, safety factor, drive level), the procedure for selecting crystals and external components, comprehensive recommended resonator lists, and PCB design guidelines for reliable oscillator operation.
