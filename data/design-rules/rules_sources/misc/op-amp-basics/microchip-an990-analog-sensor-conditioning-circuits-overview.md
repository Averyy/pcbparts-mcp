---
source: "Microchip AN990 -- Analog Sensor Conditioning Circuits Overview"
url: "https://ww1.microchip.com/downloads/en/appnotes/00990a.pdf"
format: "PDF 16pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 18106
---
# AN990: Analog Sensor Conditioning Circuits -- An Overview

*Author: Kumen Blake, Microchip Technology Inc.*

## INTRODUCTION

### Target Audience

This application note is intended for hardware design engineers that need to condition the output of common analog sensors.

### Goals

- Review sensor applications (e.g., temperature)
- Review sensor types (e.g., voltage output)
- Show various conditioning circuits
- Give technical references

### Description

Analog sensors produce a change in an electrical property to indicate a change in its environment. This change in electrical property needs to be conditioned by an analog circuit before conversion to digital. Further processing occurs in the digital domain but is not addressed in this application note. Emphasis is placed on the electrical behavior of the various sensors.

The applications mentioned are: Electrical, Magnetic, Temperature, Humidity, Force/Weight/Torque/Pressure, Motion/Vibration, Flow, Fluid Level/Volume, Light/Infrared (IR), Chemistry.

For each type of electrical property, commonly used conditioning circuits are shown. Each circuit has an accompanying list of advantages and disadvantages, and a list of sensor types appropriate for that circuit. The electrical properties covered are: Voltage, Current, Resistance, Capacitance, Charge.

In addition, circuit and firmware concerns common to many embedded designs are briefly mentioned: Input Protection, Sensor Failure Detection, Filtering, Analog-to-Digital (A-to-D) Conversion, Correction of Results.

## SENSOR APPLICATIONS

### Electrical

These applications measure the state at some point in an electrical circuit, including monitoring the condition of a crucial electrical circuit or power source.

| Sensor | Electrical Parameter |
|--------|---------------------|
| Voltage | Voltage |
| Current | Current |
| Charge | Charge |

### Magnetic

Used to detect magnetic field strength and/or direction. Commonly used in compasses and motor control.

| Sensor | Electrical Parameter |
|--------|---------------------|
| Hall effect | Voltage |
| Magneto-resistive | Resistance |

### Temperature

The most common sensor application is temperature measurement.

| Sensor | Electrical Parameter |
|--------|---------------------|
| Thermocouple | Voltage |
| RTD | Resistance |
| Thermistor | Resistance |
| IC Voltage | Voltage |
| IR Thermal Sensor | Current |
| Thermo Piles | Voltage |

### Humidity

| Sensor | Electrical Parameter |
|--------|---------------------|
| Capacitive | Capacitance |
| Infrared (IR) | Current |

### Force, Weight, Torque, and Pressure

| Sensor | Electrical Parameter |
|--------|---------------------|
| Strain Gage | Resistance |
| Load Cell | Resistance |
| Piezo-electric | Voltage or Charge |
| Mechanical Transducer | Resistance, Voltage, ... |

### Motion and Vibration

| Sensor | Electrical Parameter |
|--------|---------------------|
| LVDT | AC Voltage |
| Piezo-electric | Voltage or Charge |
| Microphone | Voltage |
| Motor Sensors | Voltage, Resistance, Current, ... |
| Ultrasonic Distance | Time |
| IC Accelerometers | Voltage |

### Flow

| Sensor | Electrical Parameter |
|--------|---------------------|
| Magnetic Flow Meter | AC Voltage |
| Mass Flow Meter | Resistance (temperature) |
| Ultrasound/Doppler | Frequency |
| Hot-wire Anemometer | Resistance |
| Mechanical Transducer | Voltage, ... |

### Fluid Level and Volume

| Sensor | Electrical Parameter |
|--------|---------------------|
| Ultrasound | Time |
| Mechanical Transducer | Resistance, Voltage, ... |
| Capacitive | Capacitance |
| Switch (e.g., vibrating) | On/Off |

### Light and Infrared (IR)

Used to detect the presence of objects and reduction in visibility (smoke and turbidity detectors).

| Sensor | Electrical Parameter |
|--------|---------------------|
| Photodiode | Current |

### Chemistry

| Sensor | Electrical Parameter |
|--------|---------------------|
| pH Electrode | Voltage (high output impedance) |
| Solution Conductivity | Resistance |
| CO Sensor | Voltage or Charge |
| Turbidity (photodiode) | Current |
| Colorimeter (photodiode) | Current |

## BASIC SIGNAL CONDITIONING CIRCUITS

### Voltage Sensors

#### Non-Inverting Gain Amplifier

Figure 1 shows a non-inverting gain amplifier using an op amp. It presents a high impedance to the sensor (at V_SEN) and produces a positive gain from V_SEN to V_OUT.

- **Advantages:** High input impedance, low bias current (CMOS op amps), positive gain, simplicity
- **Disadvantages:** Limited input voltage range, input stage distortion, amplifies common mode noise
- **Sensor Examples:** Thermocouple, thermo pile, piezo-electric film

#### Buffer for High Impedance Voltage Source

Figure 2: This circuit requires a FET input op amp (e.g., CMOS input) for very high input impedance and very low input bias current.

- **Advantages:** Very high input impedance, very low bias current (CMOS op amps), positive gain, simplicity
- **Disadvantages:** Limited input voltage range, input stage distortion, amplifies common mode noise
- **Sensor Example:** pH electrode

#### Inverting Gain Amplifier

Figure 3: Presents an impedance of R1 to the sensor and produces a negative gain from V_SEN to V_OUT.

- **Advantages:** Resistive isolation from the source, large input voltage range, virtually no input stage distortion, simplicity
- **Disadvantages:** Resistive loading of the source, inverting gain, amplifies common mode noise
- **Sensor Examples:** Thermo pile, high-side (V_DD) voltage sensor

#### Difference Amplifier

Figure 4: Presents an impedance of R1 to each end of the sensor and amplifies the input difference voltage (V_SEN+ - V_SEN-).

- **Advantages:** Resistive isolation from the source, large input voltage range, rejects common mode noise (good for remote sensors), simplicity
- **Disadvantages:** Resistive loading of the source, input stage distortion
- **Sensor Examples:** Remote thermocouple, Wheatstone bridge

#### Instrumentation Amplifier

Figure 5: Amplifies the input difference voltage and rejects common mode noise. Input resistors provide isolation and detection of sensor open-circuit failure.

- **Advantages:** Excellent rejection of common mode noise (great for remote sensors), resistive isolation from the source, detection of sensor failure
- **Disadvantages:** Resistive loading of the source, cost
- **Sensor Examples:** Remote thermocouple, remote RTD (with current source or voltage divider), Wheatstone bridge (strain gage, pressure sensor)

#### Variable Gain for Wide Dynamic Range and Non-Linear Sensors

Figure 6: A Programmable Gain Amplifier (PGA, e.g., MCP6S22) allows the user to select an input sensor and gain with the SPI bus. It can also help linearize non-linear sensors (e.g., thermistor).

- **Advantages:** Multiple sensors (input MUX), CMOS input, digital control (SPI) of input and gain, linearization of non-linear sources
- **Disadvantages:** Input stage distortion, amplifies common mode noise, needs MCU and firmware
- **Sensor Examples:** Thermistor (with voltage divider), thermo pile, piezo-electric film

### Current Sensors

#### Resistive Detector

Figure 7: A resistor (R1) converts the sensor current (I_SEN) to a voltage, and a difference amplifier amplifies the voltage across the resistor while rejecting common mode noise.

- **Advantages:** Good rejection of common mode noise, resistive isolation from the source, wide input voltage range
- **Disadvantages:** Resistive loading of the source, input stage distortion
- **Sensor Examples:** High-side (V_DD) current sensor, AC mains (line) current

#### Transimpedance Amplifier

Figure 8: Converts the sensor current (I_SEN) to a voltage. The capacitor C1 is sometimes needed to stabilize the amplifier when the source has a large capacitance.

- **Advantages:** Good impedance buffering of source, simplicity
- **Disadvantages:** Design may need to be stabilized
- **Sensor Examples:** IR smoke detector, photodiode, photodetector

#### Logarithmic Amplifier (Log Amp)

Figure 9: Converts the sensor current (I_SEN) to a voltage proportional to the logarithm of the current. D1A is used with a matched D1B for temperature compensation.

- **Advantages:** Wide dynamic range of currents, good impedance buffering of source, simplicity
- **Disadvantages:** Needs temperature correction
- **Sensor Example:** Photodiode (e.g., PWM encoded digital signal)

### Resistive Sensors

Four basic strategies for converting resistance into a measurable electrical quantity:

#### Resistance-to-Voltage Conversion

**Voltage Divider (Figure 10):** R_SEN and R1 form a voltage divider, buffered by an op amp.

- **Advantages:** Simplicity, ratiometric output (with ADC using V_DD as reference), detection of open sensor (failure)
- **Disadvantages:** Poor common mode noise rejection, voltage is a non-linear function of resistance
- **Sensor Examples:** Thermistor, RTD, magneto-resistive compass

**Voltage Divider with PGA (Figure 11):** Added programmable gain for non-linear sensor linearization.

- **Advantages:** Linearization of non-linear sensors, ratiometric output, multiplexing several sensors, detection of open sensor
- **Disadvantages:** Poor common mode noise rejection, needs controller and firmware, non-linear function
- **Sensor Example:** Thermistor

**Wheatstone Bridge -- Single Op Amp (Figure 12):**

- **Advantages:** Good rejection of common mode noise, ratiometric output, simplicity, detection of open sensor
- **Disadvantages:** Gain is a function of R_SEN, needs firmware to correct, non-linear function
- **Sensor Examples:** Strain gage, pressure sensor, magneto-resistive compass

**Wheatstone Bridge -- Instrumentation Amplifier (Figure 13):**

- **Advantages:** Excellent common mode noise rejection, ratiometric output, detection of open sensor
- **Disadvantages:** Cost, non-linear function
- **Sensor Examples:** Strain gage, pressure sensor, magneto-resistive compass

**Floating Current Source / Howland Current Pump (Figure 14):**

- **Advantages:** Linearity of resistance to voltage conversion, ratiometric output
- **Disadvantages:** Cost, requires accurate resistors
- **Sensor Examples:** Thermistor, RTD, hot-wire anemometer

#### Resistance-to-Current Conversion (Figure 15)

- **Advantages:** Ratiometric output, simplicity
- **Disadvantages:** Inverting gain
- **Sensor Example:** Thermistor

#### RC Decay (Figure 16)

Uses a MCU circuit that measures time for voltage to decay to a threshold, measuring both R1 and R_SEN separately to correct for errors.

- **Advantages:** Ratiometric correction of V_DD, C1 and temperature errors, accurate, simple timing measurement
- **Disadvantages:** MCU timing resolution, digital noise, threshold must be ratiometric
- **Sensor Example:** Thermistor

#### Oscillator Frequency (Figure 17)

A state variable oscillator using resistors, capacitors, op amps and a comparator.

- **Advantages:** Accuracy (with calibration), good startup, easy processing using MCU
- **Disadvantages:** Cost, design complexity
- **Sensor Examples:** RTD, hot-wire anemometer

### Capacitive Sensors

Four basic strategies:

#### RC Decay (Figure 18)

Similar to resistive RC decay but measuring capacitance.

- **Advantages:** Ratiometric correction of V_DD and temperature errors, accurate, simple timing measurement
- **Disadvantages:** MCU timing resolution, digital noise, threshold must be ratiometric
- **Sensor Examples:** Capacitive humidity sensor, capacitive touch sensor, capacitive tank level sensor

#### Oscillator Frequency (Figure 19)

Multi-vibrator oscillator with frequency as a function of capacitance.

- **Advantages:** Cost, ratiometric operation, easy processing using MCU
- **Disadvantages:** Reduced accuracy
- **Sensor Examples:** Capacitive humidity sensor, capacitive touch sensor, capacitive tank level sensor

#### Single Slope Integrating Detector (Figure 20)

Integrates current and measures elapsed time to reach a voltage threshold.

- **Advantages:** Easy processing using MCU, accuracy depends on V_REF and R1
- **Disadvantages:** Cost
- **Sensor Examples:** Capacitive humidity sensor, capacitive touch sensor, capacitive tank level sensor

#### Capacitive Wheatstone Bridge (Figure 21)

Converts impedance at a specific frequency to a voltage using a Wheatstone bridge driven by an AC voltage source.

- **Advantages:** Excellent common mode noise rejection, ratiometric output, detection of open or shorted sensor
- **Disadvantages:** Needs AC stimulus, power dissipation
- **Sensor Examples:** Remote capacitive sensors (humidity, touch, tank level)

### Charge Sensors

**Charge Amplifier (Figure 23):** C1 and the op amp convert the sensor energy (charge) to an output voltage. R1 provides a bias path and creates a high-pass filter pole.

- **Advantages:** Excellent common mode noise rejection, ratiometric output, detection of open or shorted sensor
- **Disadvantages:** Needs AC stimulus, power dissipation
- **Sensor Example:** Piezo-electric film

## ADDITIONAL SIGNAL CONDITIONING

### Input Protection

Sensor inputs need to be protected against Electrostatic Discharge (ESD), overvoltage and overcurrent events; especially if they are remote from the conditioning circuit.

### Sensor Failure Detection

Some of the circuits in this application note provide means to detect sensor failure.

### Filtering

All of the circuits also need output filters. Analog filters are used to improve ADC performance. When properly designed, they prevent interference from aliasing (even to DC) and can reduce the sample frequency requirements (saving power and MCU overhead). A simple RC filter is good enough for many applications. More difficult analog filters need to be implemented with active RC filters. Microchip Technology Inc.'s FilterLab software is an innovative tool that simplifies analog active-filter design.

### A-to-D Conversion

Many times, the conditioned sensor output is converted to digital format by an ADC. Many of the circuits in this application note are ratiometric so that variations in power supply are corrected at the ADC. Others use an absolute reference.

### Correction of Results

Sensor errors can be corrected by calibrating each system. This can be accomplished in hardware (e.g., digital potentiometer) or firmware (e.g., calibration constants in non-volatile memory). Non-linear sensors need additional correction using polynomials or linear interpolation tables in the MCU.

## SUMMARY

This application note is intended to assist circuit designers select a circuit topology for common sensor types. Common sensor applications are listed and described. Many basic signal-conditioning circuits are shown. Sensor-conditioning circuitry, and firmware common to many embedded designs, are briefly mentioned.

## REFERENCES

### General References
1. "The OMEGA Made in the USA Handbook," Vol.1, OMEGA Engineering, Inc., 2002.
2. "The OMEGA Made in the USA Handbook," Vol.2, OMEGA Engineering, Inc., 2002.
3. AN682, "Using Single Supply Operational Amplifiers in Embedded Systems," Bonnie Baker; Microchip Technology Inc.
4. AN866, "Designing Operational Amplifier Oscillator Circuits For Sensor Applications," Jim Lepkowski; Microchip Technology Inc.

### Current Sensors
5. AN951, "Amplifying High-Impedance Sensors -- Photodiode Example," Kumen Blake and Steven Bible; Microchip Technology Inc.
6. AN894, "Motor Control Sensor Feedback Circuits," Jim Lepkowski; Microchip Technology Inc.

### Resistor Sensors
7. AN863, "A Comparator Based Slope ADC," Joseph Julicher; Microchip Technology Inc.
8. AN251, "Bridge Sensing with the MCP6S2X PGAs," Bonnie C. Baker; Microchip Technology Inc.
9. AN717, "Building a 10-bit Bridge Sensing Circuit using the PIC16C6XX and MCP601 Operational Amplifier," Bonnie C. Baker; Microchip Technology Inc.
10. AN695, "Interfacing Pressure Sensors to Microchip's Analog Peripherals," Bonnie Baker; Microchip Technology Inc.
11. AN512, "Implementing Ohmmeter/Temperature Sensor," Doug Cox; Microchip Technology Inc.
12. AN895, "Oscillator Circuits For RTD Temperature Sensors," Ezana Haile and Jim Lepkowski; Microchip Technology Inc.

### Capacitance Sensors
13. AN611, "Resistance and Capacitance Meter Using a PIC16C622," Rodger Richie; Microchip Technology Inc.

### Temperature Sensors
14. AN929, "Temperature Measurement Circuits for Embedded Applications," Jim Lepkowski; Microchip Technology Inc.
15. AN679, "Temperature Sensing Technologies," Bonnie C. Baker; Microchip Technology Inc.
16. AN897, "Thermistor Temperature Sensing with MCP6SX2 PGAs," Kumen Blake and Steven Bible; Microchip Technology Inc.
17. AN685, "Thermistors in Single Supply Temperature Sensing Circuits," Bonnie C. Baker; Microchip Technology Inc.
18. AN687, "Precision Temperature-Sensing With RTD Circuits," Bonnie C. Baker; Microchip Technology Inc.
19. AN684, "Single Supply Temperature Sensing with Thermocouples," Bonnie C. Baker; Microchip Technology Inc.
20. AN844, "Simplified Thermocouple Interfaces and PICmicro MCUs," Joseph Julicher; Microchip Technology Inc.
21. AN867, "Temperature Sensing With A Programmable Gain Amplifier," Bonnie C. Baker; Microchip Technology Inc.

### Other Sensors
22. AN865, "Sensing Light with a Programmable Gain Amplifier," Bonnie C. Baker; Microchip Technology Inc.
23. AN692, "Using a Digital Potentiometer to Optimize a Precision Single-Supply Photo Detection Circuit," Bonnie C. Baker; Microchip Technology Inc.
24. TB044, "Sensing Air Flow with the PIC16C781," Ward Brown; Microchip Technology Inc.
25. AN597, "Implementing Ultrasonic Ranging," Robert Schreiber; Microchip Technology Inc.

### Signal Conditioning
26. FilterLab 2.0 User's Guide; Microchip Technology Inc.
27. AN942, "Piecewise Linear Interpolation on PIC12/14/16 Series Microcontrollers," John Day and Steven Bible; Microchip Technology Inc.
