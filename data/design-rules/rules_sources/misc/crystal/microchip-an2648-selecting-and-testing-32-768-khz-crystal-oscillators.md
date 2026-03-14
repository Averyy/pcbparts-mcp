---
source: "Microchip AN2648 -- Selecting and Testing 32.768 kHz Crystal Oscillators"
url: "https://ww1.microchip.com/downloads/aemDocuments/documents/MCU08/ApplicationNotes/ApplicationNotes/AN2648-Selecting_Testing-32KHz-Crystal-Osc-for-AVR-MCUs-00002648.pdf"
format: "PDF 28pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 18464
---
# Selecting and Testing 32.768 kHz Crystal Oscillators for AVR Microcontrollers

Microchip Technology AN2648 (Rev D, May 2022)

Authors: Torbjorn Kjorlaug and Amund Aune, Microchip Technology Inc.

## Introduction

This application note summarizes the crystal basics, PCB layout considerations, and how to test a crystal in your application. A crystal selection guide shows recommended crystals tested by experts and found suitable for various oscillator modules in different Microchip AVR families. Test firmware and test reports from various crystal vendors are included.

Features:
- Crystal Oscillator Basics
- PCB Design Considerations
- Testing Crystal Robustness
- Test Firmware Included
- Crystal Recommendation Guide

## 1. Crystal Oscillator Basics

### 1.1 Introduction

A crystal oscillator uses the mechanical resonance of a vibrating piezoelectric material to generate a very stable clock signal. The frequency is usually used to provide a stable clock signal or keep track of time; hence, crystal oscillators are widely used in Radio Frequency (RF) applications and time-sensitive digital circuits.

Crystals are available from various vendors in different shapes and sizes and can vary widely in performance and specifications. Understanding the parameters and the oscillator circuit is essential for a robust application stable over variations in temperature, humidity, power supply, and process.

All physical objects have a natural frequency of vibration, where the vibrating frequency is determined by its shape, size, elasticity, and speed of sound in the material. Piezoelectric material distorts when an electric field is applied and generates an electric field when it returns to its original shape. The most common piezoelectric material used in electronic circuits is a quartz crystal, but ceramic resonators are also used -- generally in low-cost or less timing-critical applications. 32.768 kHz crystals are usually cut in the shape of a tuning fork. With quartz crystals, very precise frequencies can be established.

### 1.2 The Oscillator

The Barkhausen stability criteria are two conditions used to determine when an electronic circuit will oscillate. They state that if A is the gain of the amplifying element and beta(jw) is the transfer function of the feedback path, steady-state oscillations will be sustained only at frequencies for which:

- The loop gain is equal to unity in absolute magnitude: |beta*A| = 1
- The phase shift around the loop is zero or an integer multiple of 2*pi: angle(beta*A) = 2*pi*n for n = 0, 1, 2, 3...

The first criterion will ensure a constant amplitude signal. A number less than 1 will attenuate the signal, and a number greater than 1 will amplify the signal to infinity. The second criterion will ensure a stable frequency.

The 32.768 kHz oscillator in Microchip AVR microcontrollers consists of an inverting amplifier (internal) and a crystal (external). Capacitors CL1 and CL2 represent internal parasitic capacitance. Some AVR devices also have selectable internal load capacitors, which may be used to reduce the need for external load capacitors, depending on the crystal used.

The inverting amplifier gives a pi radian (180 degree) phase shift. The remaining pi radian phase shift is provided by the crystal and the capacitive load at 32.768 kHz, causing a total phase shift of 2*pi radian. During start-up, the amplifier output will increase until steady-state oscillation is established with a loop gain of 1, causing the Barkhausen criteria to be fulfilled. This is controlled automatically by the AVR microcontroller oscillator circuitry.

### 1.3 Electrical Model

The equivalent electric circuit of a crystal consists of a series RLC network (the motional arm) giving an electrical description of the mechanical behavior:

- **C1** (motional capacitance): represents the elasticity of the quartz
- **L1** (motional inductance): represents the vibrating mass
- **R1** (motional resistance): represents losses due to damping
- **C0** (shunt/static capacitance): sum of electrical parasitic capacitance due to crystal housing and electrodes. If a capacitance meter is used to measure the crystal, only C0 will be measured.

Two resonant frequencies can be found:

**Series resonant frequency (fs):** depends only on C1 and L1.

    fs = 1 / (2*pi*sqrt(L1*C1))

**Parallel resonant frequency (fp):** also includes C0.

    fp = fs * sqrt(1 + C1/C0)

Crystals below 30 MHz can operate at any frequency between the series and parallel resonant frequencies (inductive region). High-frequency crystals above 30 MHz are usually operated at the series resonant frequency or overtone frequencies.

Adding a capacitive load CL to the crystal will cause a frequency shift:

    delta_f = fs * C1 / (2*(C0 + CL))

The crystal frequency can be tuned by varying the load capacitance (frequency pulling).

### 1.4 Equivalent Series Resistance (ESR)

The ESR is an electrical representation of the crystal mechanical losses. At the series resonant frequency fs, it is equal to R1 in the electrical model. ESR is an important parameter found in the crystal data sheet. The ESR will usually be dependent on the crystal physical size, where smaller crystals (especially SMD crystals) typically have higher losses and ESR values than larger crystals.

Higher ESR values put a higher load on the inverting amplifier. Too high ESR may cause unstable oscillator operation. Unity gain can, in such cases, not be achieved, and the Barkhausen criterion may not be fulfilled.

### 1.5 Q-Factor and Stability

The crystal frequency stability is given by the Q-factor. The Q-factor is the ratio between the energy stored in the crystal and the sum of all energy losses. Typically, quartz crystals have Q in the range of 10,000 to 100,000, compared to perhaps 100 for an LC oscillator. Ceramic resonators have lower Q than quartz crystals and are more sensitive to changes in capacitive load.

    Q = E_stored / sum(E_losses)

Several factors can affect the frequency stability: Mechanical stress induced by mounting, shock or vibration stress, variations in power supply, load impedance, temperature, magnetic and electric fields, and crystal aging. Crystal vendors usually list such parameters in their data sheets.

### 1.6 Start-Up Time

During start-up, the inverting amplifier amplifies noise. The crystal will act as a bandpass filter and feed back only the crystal resonance frequency component, which is then amplified. Before achieving steady-state oscillation, the loop gain is greater than 1 and the signal amplitude will increase. At steady-state oscillation, the loop gain fulfills the Barkhausen criteria with a loop gain of 1 and constant amplitude.

Factors affecting the start-up time:
- High-ESR crystals will start more slowly than low-ESR crystals
- High Q-factor crystals will start more slowly than low Q-factor crystals
- High load capacitance will increase start-up time
- Oscillator amplifier drive capabilities (see negative resistance test and safety factor)
- Crystal frequency (faster crystals start faster), but this is fixed for 32.768 kHz

### 1.7 Temperature Tolerance

Typical tuning fork crystals are usually cut to center the nominal frequency at 25 deg C. Above and below 25 deg C, the frequency will decrease with a parabolic characteristic:

    f = f0 * (1 + B*(T - T0)^2)

Where f0 is the target frequency at T0 (typically 32.768 kHz at 25 deg C) and B is the temperature coefficient given by the crystal data sheet (typically a negative number).

### 1.8 Drive Strength

The strength of the crystal driver circuit determines the characteristics of the sine wave output. The sine wave is the direct input into the digital clock input pin. This sine wave must span the input minimum and maximum voltage levels while not being clipped, flattened or distorted at the peaks. A too low amplitude shows that the crystal circuit load is too heavy for the driver, leading to potential oscillation failure. Too high amplitude means that the loop gain is too high and may lead to the crystal jumping to a higher harmonic level or permanent damage.

Select a crystal with lower ESR or capacitive load if the loop gain is too low. If the loop gain is too high, a series resistor RS may be added to the circuit to attenuate the output signal.

The loop gain is negatively affected by temperature and positively by voltage (VDD). The drive characteristics must be measured at the highest temperature and lowest VDD, and the lowest temperature and highest VDD at which the application is specified to operate.

## 2. PCB Layout and Design Considerations

Even the best performing oscillator circuits and high-quality crystals will not perform well if not carefully considering the layout and materials used during assembly. Ultra-low power 32.768 kHz oscillators typically dissipate significantly below 1 uW, so the current flowing in the circuit is extremely small. The crystal frequency is highly dependent on the capacitive load.

To ensure the robustness of the oscillator, these guidelines are recommended during PCB layout:

- Signal lines from XTAL1/TOSC1 and XTAL2/TOSC2 to the crystal must be as short as possible to reduce parasitic capacitance and increase noise and crosstalk immunity. Do not use sockets.
- Shield the crystal and signal lines by surrounding it with a ground plane and guard ring.
- Do not route digital lines, especially clock lines, close to the crystal lines. For multilayer PCB boards, avoid routing signals below the crystal lines.
- Use high-quality PCB and soldering materials.
- Dust and humidity will increase parasitic capacitance and reduce signal isolation, so protective coating is recommended.

## 3. Testing Crystal Oscillation Robustness

### 3.1 Introduction

The AVR microcontroller 32.768 kHz crystal oscillator driver is optimized for low power consumption, and thus the crystal driver strength is limited. Overloading the crystal driver may cause the oscillator not to start, or it may be affected (stopped temporarily) due to a noise spike or increased capacitive load caused by contamination or proximity of a hand.

Take care when selecting and testing the crystal to ensure proper robustness. The crystal two most important parameters are Equivalent Series Resistance (ESR) and Load Capacitance (CL).

When measuring crystals, the crystal must be placed as close as possible to the 32.768 kHz oscillator pins to reduce parasitic capacitance. Always recommend doing the measurement in your final application.

Do not connect the crystal to XTAL/TOSC output headers at the end of a development board, as the signal path will be very sensitive to noise and add extra capacitive load. Soldering the crystal directly to the leads gives good results. Bend the XTAL/TOSC leads upwards so they do not touch the socket to avoid extra capacitive load from the socket and routing.

A standard 10X oscilloscope probe imposes a loading of 10-15 pF and will have a high impact on measurements. Touching the pins of a crystal with a finger or a 10X probe can be sufficient to start or stop oscillations or give false results. Use firmware to output the clock signal to a standard I/O pin; I/O pins configured as buffered outputs can be probed with standard 10X probes without affecting the measurements.

### 3.2 Negative Resistance Test and Safety Factor

The negative resistance test finds the margin between the crystal amplifier load used in your application and the maximum load. At max load, the amplifier will choke and oscillations will stop. This point is called the oscillator allowance (OA).

Find the oscillator allowance by temporarily adding a variable series resistor between the amplifier output (XTAL2/TOSC2) lead and the crystal. Increase the series resistor until the crystal stops oscillating.

    OA = R_MAX + ESR

Finding a correct R_MAX value can be tricky because no exact oscillator allowance point exists. Before the oscillator stops, you may observe a gradual frequency reduction, and there may be start-stop hysteresis. After the oscillator stops, you will need to reduce R_MAX by 10-50 kOhm before oscillations resume. A power cycling must be performed each time after the variable resistor is increased. R_MAX is the resistor value where the oscillator does not start after a power cycling. Start-up times will be quite long at the oscillator allowance point, so be patient.

The safety factor is calculated from:

    SF = OA / ESR = (R_MAX + ESR) / ESR

**Safety Factor Recommendations:**

| Safety Factor | Recommendation |
|---|---|
| > 5 | Excellent |
| 4 | Very good |
| 3 | Good |
| < 3 | Not recommended |

### 3.3 Measuring Effective Load Capacitance

The crystal frequency is dependent on the capacitive load applied. Applying the capacitive load specified in the data sheet will provide a frequency very close to the nominal frequency of 32.768 kHz. If other capacitive loads are applied, the frequency will change: the frequency will increase if load is decreased, and decrease if load is increased.

The frequency pullability (bandwidth) is given by the nominal frequency divided by the Q-factor. For high-Q quartz crystals, the usable bandwidth is limited. If the measured frequency deviates from the nominal, the oscillator will be less robust due to higher attenuation in the feedback loop.

    BW = f_resonant / Q

Total load capacitance without external capacitors:

    CL = (CL1 + CP1) * (CL2 + CP2) / (CL1 + CP1 + CL2 + CP2)

Total load capacitance with external capacitors:

    CL = (CL1 + CP1 + CEL1) * (CL2 + CP2 + CEL2) / (CL1 + CP1 + CEL1 + CL2 + CP2 + CEL2)

## 4. Test Firmware

Test firmware for outputting the clock signal to an I/O port that may be loaded with a standard 10X probe is included. Do not measure the crystal electrodes directly if you do not have very high impedance probes.

Output pins and frequency division by device:

| Device | Output Pin | Frequency Division | Expected Output |
|---|---|---|---|
| ATmega128 | PB4 | / 2 | 16.384 kHz |
| ATmega328P | PD6 | / 2 | 16.384 kHz |
| ATtiny817 | PB5 | None | 32.768 kHz |
| ATtiny85 | PB1 | / 2 | 16.384 kHz |
| ATxmega128A1 | PC7 | None | 32.768 kHz |
| ATxmega256A3B | PC7 | None | 32.768 kHz |
| PIC18F25Q10 | RA6 | / 4 | 8.192 kHz |

Note: The PIC18F25Q10 was used as a representative of an AVR Dx series device when testing crystals. It uses the OSC_LP_v10 oscillator module, the same as used by the AVR Dx series.

## 5. Crystal Recommendations

The following table shows crystals tested and found suitable for various AVR microcontrollers. Using crystal-MCU combinations from this table ensures good compatibility.

**Oscillator Modules in AVR Devices:**

| # | Module | Description |
|---|---|---|
| 1 | X32K_2v7 | 2.7-5.5V oscillator used in megaAVR devices |
| 2 | X32K_1v8 | 1.8-5.5V oscillator used in megaAVR/tinyAVR devices |
| 3 | X32K_1v8_ULP | 1.8-3.6V ultra-low power oscillator used in megaAVR/tinyAVR picoPower devices |
| 4 | X32K_XMEGA (normal) | 1.6-3.6V ultra-low power oscillator used in XMEGA devices, normal mode |
| 5 | X32K_XMEGA (low-power) | 1.6-3.6V ultra-low power oscillator used in XMEGA devices, low-power mode |
| 6 | X32K_XRTC32 | 1.6-3.6V ultra-low power RTC oscillator used in XMEGA devices with battery backup |
| 7 | X32K_1v8_5v5_ULP | 1.8-5.5V ultra-low power oscillator used in tinyAVR 0/1/2-series and megaAVR 0-series |
| 8 | OSC_LP_v10 (normal) | 1.8-5.5V ultra-low power oscillator used in AVR Dx series, normal mode |
| 9 | OSC_LP_v10 (low-power) | 1.8-5.5V ultra-low power oscillator used in AVR Dx series, low-power mode |

**Recommended 32.768 kHz Crystals:**

| Vendor | Type | Mount | Modules | Tol (ppm) | CL (pF) | ESR (kOhm) |
|---|---|---|---|---|---|---|
| Microcrystal | CC7V-T1A | SMD | 1,2,3,4,5 | 20/100 | 7.0/9.0/12.5 | 50/70 |
| Abracon | ABS06 | SMD | 2 | 20 | 12.5 | 90 |
| Cardinal | CPFB | SMD | 2,3,4,5 | 20 | 12.5 | 50 |
| Cardinal | CTF6 | TH | 2,3,4,5 | 20 | 12.5 | 50 |
| Cardinal | CTF8 | TH | 2,3,4,5 | 20 | 12.5 | 50 |
| Endrich Citizen | CFS206 | TH | 1,2,3,4 | 20 | 12.5 | 35 |
| Endrich Citizen | CM315 | SMD | 1,2,3,4 | 20 | 12.5 | 70 |
| Epson Toyocom | MC-306 | SMD | 1,2,3 | 20/50 | 12.5 | 50 |
| Fox | FSXLF | SMD | 2,3,4,5 | 20 | 12.5 | 65 |
| Fox | FX135 | SMD | 2,3,4,5 | 20 | 12.5 | 70 |
| Fox | FX122 | SMD | 2,3,4 | 20 | 12.5 | 90 |
| Fox | FSRLF | SMD | 1,2,3,4,5 | 20 | 12.5 | 50 |
| NDK | NX3215SA | SMD | 1,2,3 | 20 | 12.5 | 80 |
| NDK | NX1610SE | SMD | 1,2,4,5,6,7,8,9 | 20 | 6 | 50 |
| NDK | NX2012SE | SMD | 1,2,4,5,6,8,9 | 20 | 6 | 50 |
| SII | SSP-T7-FL | SMD | 2,3,5 | 20 | 4.4/6/12.5 | 65 |
| SII | SSP-T7-F | SMD | 1,2,4,6,7,8,9 | 20 | 7/12.5 | 65 |
| SII | SC-32S | SMD | 1,2,4,6,7,8,9 | 20 | 7 | 70 |
| SII | SC-32L | SMD | 4 | 20 | 7 | 40 |
| SII | SC-20S | SMD | 1,2,4,6,7,8,9 | 20 | 7 | 70 |
| SII | SC-12S | SMD | 1,2,6,7,8,9 | 20 | 7 | 90 |

Note: Crystals may be available with multiple load capacitance and frequency tolerance options. Contact the crystal vendor for more information.

## 6. Oscillator Module Overview

### megaAVR Devices

The X32K_2v7 module is used in older megaAVR devices (ATmega8/16/32/64/128 A-variants). The X32K_1v8 module covers ATmega162/168/328/640/1280/1281/2560/2561 and similar. The X32K_1v8_ULP module covers ATmega48P/88P/168P/328P/164/165/169/324/325/329/644/645/649/1284P and variants. The X32K_1v8_5v5_ULP module covers the megaAVR 0-series (ATmega808/809/1608/1609/3208/3209/4808/4809) and ATmega406.

### tinyAVR Devices

The X32K_1v8 module is used in older tinyAVR devices (ATtiny24/25/44/45/84/85/261/461/861 and A-variants, ATtiny2313A/4313). The X32K_1v8_5v5_ULP module covers the tinyAVR 0/1/2-series (ATtiny202/204/212/214/402/404/406/412/414/416/417/424/426/427/804/806/807/814/816/817/824/826/827/1604/1606/1607/1614/1616/1617/1624/1626/1627/3216/3217/3224/3226/3227).

### AVR Dx Devices

All AVR Dx devices (AVR128DA/DB/DD series, AVR64DA/DB/DD series, AVR32DA/DB/DD series) use the OSC_LP_v10 module.

### AVR XMEGA Devices

All XMEGA devices use X32K_XMEGA, except ATxmega256A3B which uses X32K_XRTC32.
