---
source: "onsemi AND90146 -- MOSFET Selection for Reverse Polarity Protection"
url: "https://www.onsemi.com/download/application-notes/pdf/and90146-d.pdf"
format: "PDF 11pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 11915
---

# MOSFET Selection for Reverse Polarity Protection

onsemi Application Note AND90146/D

## Overview

When the vehicle's battery is damaged and needs replacement the probability of connecting the new battery in reverse is high. Since many electronic control units (ECU) in the vehicle are connected to the vehicle's battery, such an event could lead to numerous ECU failures.

Additionally, automotive standards like ISO (International Organization for Standardization) define the testing methods, voltage levels, limits for electromagnetic emission for electrical and electronic devices to ensure the safe and rugged operation of the system. One such standard related to reverse polarity protection (RPP) is ISO 7637-2:2011 which replicates the various voltage scenarios like in the real application and the system needs to withstand such voltages to showcase the robustness against failures. This made reverse polarity protection a crucial building block that is required by all automotive vehicle manufacturers for any battery connected ECU/system.

This application note will first address the ISO pulses that are commonly used to replicate the voltage transients that could appear in real applications. It will then give details about several protection techniques that could be used, before helping to guide the reader to select an external N-Channel MOSFET, that will provide RPP and help reduce the power losses of the system. Finally, a list of recommended N-Channel MOSFETs to be used along with an ideal diode controller, based on the battery current will be provided.

## ISO Pulses

ISO 7637-2:2011 is an international standard which specifies test methods and procedures to ensure the compatibility to conducted electrical transients of equipment installed on passenger cars and commercial vehicles fitted with 12 V or 24 V electrical systems.

Under this standard there are several types of test pulses:

- **Pulse 1**: Transients due to supply disconnection of inductive loads
- **Pulse 2a**: Transients due to sudden interruption of currents in a device connected in parallel with the DUT, due to the inductance of the wiring harness
- **Pulse 3a and 3b**: Transients which occur as a result of switching processes. Pulse 3b simulates the switching noise in the real application, such as relay and switch contact bouncing which can produce a short burst of high frequency pulses.

### Parameters of Test Pulse 3b

| Parameter | Nominal 12 V System | Nominal 24 V System |
|-----------|---------------------|---------------------|
| US | +75 V to +150 V | +150 V to +300 V |
| Ri | 50 ohm | 50 ohm |
| td | 150 ns +/- 45 ns | 150 ns +/- 45 ns |
| tr | 5 ns +/- 1.5 ns | 5 ns +/- 1.5 ns |
| t1 | 100 us | 100 us |
| t4 | 10 ms | 10 ms |
| t5 | 90 ms | 90 ms |

## Reverse Polarity Protection Techniques

### Diode

The simplest way to protect a system from a reverse battery is by using a diode. A diode will only conduct current when the correct polarity is applied to its terminals (i.e., forward biased). The forward voltage drop VF for a standard diode is around 0.7 V, while for a Schottky diode it can be as low as 0.3 V. As a result, most applications use a Schottky diode to reduce system losses.

Example: The NRVBSS24NT3G Schottky diode shows that if the diode current increases from 0.5 A to 1.0 A (100% increase), VF increases from 0.35 V to 0.40 V (15% increase) at a junction temperature TJ of 25 degrees C.

### P-Channel MOSFET

As all MOSFETs, a P-Channel MOSFET has an intrinsic body diode between the source and the drain. When the battery is properly connected, the intrinsic body diode is conductive until the MOSFET's channel is turned ON. To turn ON a P-Channel MOSFET, the gate voltage needs to be lower than the source voltage by at least the threshold voltage VT. When the battery is reversely connected, the body diode is reverse biased, gate and source have the same voltage thus turning OFF the P-Channel MOSFET. An additional Zener diode is used to clamp the gate and protect it in the case of a too high voltage.

### N-Channel MOSFET

It is also possible to use an N-Channel MOSFET for reverse polarity protection. When the battery is properly connected (source is connected to VBAT), to turn ON the MOSFET, the gate-source voltage has to be higher than the threshold voltage (VGS > VTH). Given that the source is connected to VBAT, the gate voltage needs to be higher than VBAT by at least VT. Hence a dedicated driver is used to drive the gate voltage of the N-Channel MOSFET higher than the source voltage. When the battery is reverse connected, the body diode is reverse biased and the driver is disabled (source and gate are shorted), turning the N-Channel MOSFET OFF.

### Comparison of Techniques

| Technique | Advantages | Disadvantages |
|-----------|-----------|---------------|
| Schottky Diode | Low cost, Simple | Higher power dissipation, Higher voltage drop |
| P-Channel MOSFET | Flexibility (various RDS,ON options) | High cost for low RDS,ON |
| N-Channel MOSFET | Higher power dissipation, Lower operating voltage drop | Higher total solution cost, Higher complexity (gate drive and protection) |

P-Channel MOSFET operation depends upon the mobility of holes, while an N-Channel MOSFET depends upon the mobility of electrons. The mobility of holes is almost 2.5x lower than the mobility of electrons, so for the same drain current, a P-Channel MOSFET will have a bigger die size and higher cost compared to an N-Channel MOSFET to achieve the same on-resistance. This makes N-Channel MOSFETs preferable compared to P-Channel MOSFETs in such applications.

## MOSFET Selection Criteria

There are various parameters to consider when selecting an N-Channel MOSFET for reverse polarity protection:

- **Maximum Breakdown Voltage (VDS,MAX)**:
  - For 12 V board net (vehicle): VDS,MAX = 40 V is preferred
  - For 24 V board net (truck): VDS,MAX = 60 V is preferred
- **Maximum Operating Junction Temperature (TJ,MAX)**: For vehicle and truck applications, 175 degrees C is recommended given the harsh environment
- **Gate Level**: Logic Level is preferred over standard level since they have a lower RDS,ON for the same gate-source voltage VGS
- **Package**: 3.30 x 3.30 mm (e.g., LFPAK33/WDFN8) and 5.00 x 6.00 mm (e.g., SO8-FL/LFPAK56) packages with exposed pad for optimized power dissipation
- **Total Gate Charge (QG,TOT)**: Lower QG,TOT means lesser gate voltage and current needed to turn ON the MOSFET (faster turn ON)
- **Drain-Source Resistance (RDS,ON)**: Higher RDS,ON for a given load current leads to higher power dissipation and higher TJ. Choose the right device with required RDS,ON for optimal performance.

## NCV68061 Ideal Diode Controller

The combination of NCV68061 and an external N-Channel MOSFET replicates an ideal diode which acts like a perfect conductor when forward biased and like a perfect insulator when reverse biased. The NCV68061 provides a typical gate voltage of 11.4 V to the external N-Channel MOSFET. Hence RDS,ON @ 10 V VGS has been used in all calculations.

### Ideal Diode Application

- **Conduction Mode**: As the source voltage becomes greater than the drain voltage, the forward current flows through the body diode. Once this forward voltage drop exceeds the source-to-drain gate charge voltage threshold level (typ. 140 mV), the charge pump turns ON and the N-Channel MOSFET becomes fully conductive.
- **Reverse Current Blocking Mode**: When the source voltage becomes less than the drain voltage, reverse current initially flows through the conductive channel. When the voltage drops below the source-to-drain gate discharge voltage threshold (typ. -10 mV), the charge pump is disabled and the MOSFET is turned OFF.

### Reverse Polarity Protection Mode

By connecting the drain pin to GND potential, the NCV68061 does not allow a falling input voltage to discharge the output below GND potential but does allow the output to follow any positive input voltage above the under-voltage lockout (UVLO) threshold (typ. 3.3 V).

## Thermal Measurements

### MOSFETs Under Evaluation

| Battery Current | Part Number | Package | Max RDS,ON @ 10V VGS (mOhm) | Max Losses PD (mW) | RthJA (deg C/W) | TCASE (deg C) |
|----------------|-------------|---------|------------------------------|--------------------|--------------------|----------------|
| 6 A | NVTFS5C478NLWFTAG | 3x3 | 14.0 | 504.0 | 51.0 | 47.3 |
| 6 A | NVMFS5C468NLAFT1G | SO-8FL | 10.3 | 370.8 | 43.0 | 40.1 |
| 8 A | NVTFS5C466NLWFTAG | 3x3 | 7.3 | 467.2 | 48.0 | 47.4 |
| 8 A | NVMFS5C466NLWFT1G | SO-8FL | 7.3 | 467.2 | 43.0 | 45.3 |
| 10 A | NVTYS005N04CLTWG | LFPAK8 | 4.8 | 480.0 | 47.7 | 52.8 |
| 10 A | NVMYS4D6N04CLTWG | LFPAK4 | 4.5 | 450.0 | 40.0 | 47.5 |

### Junction Temperature Estimation

Using measured TCASE and actual power dissipation:

    TJ = TCASE + PD * RthJT

Where RthJT is assumed to be 1 deg C/W for 3x3 and 5x6 packages (conservative assumption). RthJT is small (<1 deg C/W) as most heat flows from junction to PCB via the exposed pad.

**Example calculation for NVTFS5C478NLWFTAG at 6 A:**

    PD = (6.0 A)^2 * 14.0 mOhm = 504.0 mW
    TJ = 47.3 deg C + (504.0 mW * 1.0 deg C/W) = 47.8 deg C

**Theoretical calculation using RthJA from datasheet:**

    TJ = PD * RthJA + TA = 500.0 mW * 51.0 deg C/W + 24.0 deg C = 49.5 deg C

The difference between estimated and theoretically calculated TJ is minor at 1.7 deg C (49.5 deg C vs. 47.8 deg C).

### Key Thermal Findings

- At 6 A load current: approximately 5.8% higher headroom for TJ with 5x6 than 3x3 package
- At 8 A load: approximately 1.6% higher headroom with 5x6 than 3x3 (same die in different packages)
- At 10 A: approximately 4.3% higher headroom with 5x6 than 3x3
- RthJA in the datasheet is a realistic value for thermal analysis
- Larger packages dissipate heat more efficiently; suitable for higher load current applications and higher ambient temperatures

### Maximum Ambient Temperature Estimation

At 175 deg C junction temperature, RDS,ON is approximately 1.85x higher compared to 25 deg C. For NVTFS5C478NLWFTAG at 6 A:

    RDS,ON @ 175 deg C = 1.85 * 14 mOhm = 25.9 mOhm
    PD = (6.0 A)^2 * 25.9 mOhm = 932.4 mW
    Temperature difference = 51.0 deg C/W * 932.4 mW = 47.5 deg C
    Maximum TA = 175.0 deg C - 47.5 deg C = 127.5 deg C

### Estimated Maximum Ambient Temperature for Various MOSFETs

| Battery Current | Part Number | Package | Max RDS,ON @ 175 deg C (mOhm) | Max Losses PD (mW) | RthJA (deg C/W) | Max TAMB (deg C) |
|----------------|-------------|---------|-------------------------------|--------------------|--------------------|------------------|
| 6 A | NVTFS5C478NLWFTAG | 3x3 | 25.9 | 932.4 | 51.0 | 127.5 |
| 6 A | NVMFS5C468NLAFT1G | SO-8FL | 19.6 | 705.6 | 43.0 | 144.6 |
| 8 A | NVTFS5C466NLWFTAG | 3x3 | 14.4 | 921.6 | 48.0 | 130.7 |
| 8 A | NVMFS5C466NLWFT1G | SO-8FL | 13.2 | 844.8 | 43.0 | 138.6 |
| 10 A | NVTYS005N04CLTWG | LFPAK8 | 8.8 | 880.0 | 47.7 | 133.0 |
| 10 A | NVMYS4D6N04CLTWG | LFPAK4 | 8.3 | 830.0 | 40.0 | 141.8 |

## Conclusion

Reverse polarity protection circuits are one of the core building blocks of any ECU in a vehicle. Several techniques were discussed including diodes, P-Channel MOSFETs and N-Channel MOSFETs. N-Channel MOSFETs are preferable due to lower RDS,ON for a given die size.

Thermal measurements show that 5x6 packages perform well from a thermal point of view, due to the larger package and bigger die. Without significant difference between theoretically calculated and practically estimated junction temperature TJ, RthJA given in the datasheet is a realistic value to perform thermal analysis in real applications.
