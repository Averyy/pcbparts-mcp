---
source: "Infineon -- OptiMOS Datasheet Explanation"
url: "https://www.infineon.com/assets/row/public/documents/24/42/infineon-mosfet-optimos-datasheet-explanation-an-en.pdf"
format: "PDF 30pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 13479
---

# Infineon OptiMOS Power MOSFET Datasheet Explanation

Application Note AN 2012-03, V1.1 March 2012
Author: Alan Huang, Power Management & Multimarket, Infineon Technologies Austria AG

## 1. Introduction

A datasheet is the most important tool for the electronics engineer to understand a Power MOSFET device and to fully appreciate its intended functionalities. Due to a great amount of information a datasheet offers, it is sometimes deemed to be complicated and a difficult document to comprehend. Furthermore important parameters can be often missed. This could lead to numerous problems, for example, device failure, PCB re-design, project delay, etc.

This application note describes Infineon's OptiMOS Power MOSFET datasheets in detail. OptiMOS is the trademark for Infineon's low voltage (up to 300 V) Power MOSFET product line. This document provides background information on each specification parameter and explanation on each of the specification diagrams. It aims to help the designer to acquire a better understanding of the data sheet.

The parameters and diagrams mentioned in the datasheet provide a complete picture of a MOSFET. With such information, the designer should be able to understand the device's intended operation, to determine the operational limits of the device, and to compare quantitatively against different devices.

Note: This document uses diagrams and parameters from IPP029N06N datasheet rev2.0 as examples.

## 2. Datasheet Parameters

### 2.1 Power Dissipation

The first diagram included in the datasheet is the power dissipation versus case temperature chart. At a certain case temperature, the maximum allowable power dissipation is governed as illustrated.

There are two power dissipation parameters listed in the datasheet -- total junction-to-case and total junction-to-ambient power dissipation. These two numbers can be obtained using:

    Ptot(TC) = (Tj - TC) / RthJC        ... (1)
    Ptot(TA) = (Tj - TA) / RthJA        ... (2)

Using these examples, the maximum power dissipation with the highest allowable temperature increase can be calculated:

    Ptot(TC,max) = (175 - 25) K / (1.1 K/W) = 136 W
    Ptot(TA,max) = (175 - 25) K / (50 K/W) = 3.0 W

Note: The junction-to-ambient thermal resistance is layout dependent; therefore, in most cases, a footnote regarding the junction-to-ambient thermal resistance is included, specifying the condition where the specified RthJA rating is estimated (e.g., device on 40 mm x 40 mm x 1.5 mm epoxy PCB FR4 with 6 cm2 copper area for drain connection).

### 2.2 Drain Current

The datasheet specifies the maximum continuous drain current (ID) under different operating conditions and the pulsed drain current (ID,pulse). The maximum pulsed drain current is specified at 4x the maximum continuous drain current. As the pulse width increases, the pulsed drain current rating decreases due to the thermal characteristics of the device.

When the maximum continuous drain current depends solely on the maximum power dissipation, the maximum ID would be defined by the rearranged Power Law (P = I^2 * R):

    ID(TC) = sqrt((Tj - TC) / (RthJC * RDS(on),Tj(max)))     ... (4)
    ID(25 deg C) = sqrt((175 - 25) K / (0.8 K/W * 0.0066 ohm)) = 169 A

However, in reality, additional boundary conditions, governed by bond wire diameter, chip design and assembly, limit the maximum continuous drain current. At TC = 25 deg C, ID is capped at 100 A instead of 169 A. At low TC, maximum ID stays constant; at high TC, it rolls off with acceleration until reaching zero at TC = Tj(max).

### 2.3 Safe Operating Area (SOA)

The SOA diagram shows drain current (ID) as a function of drain-source voltage (VDS) with different pulse lengths. This is one of the most complicated but important figures that should not be ignored in the datasheet.

There are several limitations in this diagram (using the 100 us curve as an example):

**A) Maximum pulsed drain current** -- the top line limit.

**B) RDS(on) limit** -- this area is limited by the on-state resistance at maximum junction temperature.

**C) Constant power line** -- at fixed TC, the device is limited by the constant power line. Depending on the applied power pulse width, the maximum power loss varies according to the thermal impedance variation.

**D) Linear mode / hot spot limit** -- in linear mode operation, there is a risk of getting hot spots at low gate-source voltages due to thermal runaway. This effect becomes more important for latest trench technologies with high current densities, where the "zero temperature coefficient" point of the transfer characteristic is shifted to higher drain currents.

    ID(VDS) = (Tj - TC) / (VDS * ZthJC)     ... (5)

**E) Maximum breakdown voltage** -- determined by the technology, limits the SOA curve on the right hand side.

Note: The SOA diagram is defined for single pulses. Mathematically, the duty cycle of a single pulse is equivalent to zero (D=0) as the period (T) is infinite.

### 2.4 Maximum Transient Thermal Impedance ZthJC

RthJC is the thermal resistance from the junction of the die to the case. Transient thermal impedance (ZthJC) takes also the heat capacity (CthJC) of the device into account. It is used to estimate the temperature resulted from transient power loss.

The increase of the junction temperature can be calculated as:

    Tj = Tj,start + dT = Tj,start + ZthJC(tp, D) * Ptot     ... (6)

### 2.5 Typical Output Characteristics

The typical output characteristics graph illustrates the drain current ID as a function of the drain-source voltage VDS at given gate-source voltages VGS and chip temperature Tj of 25 deg C.

For optimal efficiency, the MOSFET should be operated in the "ohmic" region. The boundary line between ohmic and saturation region is defined by VDS = VGS - VGS(th). At any given gate-source voltage, the drain current of the MOSFET saturates beyond the ohmic region. As the operating point goes into the saturation region, any further increase in drain current leads to a significant rise in drain-source voltage (linear operation mode) and as a result conduction loss increases.

Gate-source voltage (VGS) is deterministic to the MOSFET's output characteristics. The allowable range is typically +/- 20 V.

### 2.6 Drain-source On-state Resistance vs. Drain Current

For each gate-source voltage, the drain source on-state resistance over drain current curve is directly calculated from the typical output characteristic diagram using Ohm's Law:

    RDS(on)(ID) = VDS / ID     ... (7)

VGS plays an important role. To fully turn on a device, a VGS of 10 V is required. For normal level devices, 10 V is recommended for efficiency-optimized low drain-source on-state resistance. For logic level devices, shifted RDS(on) curves make a lower-than-10 V VGS acceptable for fast switching applications, whereas the conduction loss due to higher RDS(on) is less critical.

### 2.7 Transfer Characteristics

This diagram shows the typical drain current as a function of the applied gate-source voltage at different junction temperatures. All the graphs should intersect at one point, the so-called **temperature stable operating point** (zero temperature coefficient point).

- Below this point (e.g., VGS < 5.2 V): positive temperature coefficient -- with increasing junction temperature the drain current will also increase. Operating at this condition with constant VGS should be avoided due to the possibility of thermal runaway.
- Beyond this point: negative temperature coefficient -- with increasing junction temperature the drain current decreases. The MOSFET self-limits its current handling capability at high temperatures. Operating in this region is generally safe as long as the junction temperature stays within specification.

### 2.8 Forward Transconductance

Transconductance (gfs) is a measure of sensitivity of the drain current to the variation of the gate-source voltage:

    gfs(ID) = dID / dVGS     ... (8)

### 2.9 Drain-source On-state Resistance

The drain-source on-state resistance is one of the key parameters of a MOSFET. For a surface-mount device (SMD), the resistance is measured between the source pin and the backside drain contact. For a through-hole package, the RDS(on) is specified between the drain and source pins at a defined soldering point (approx. 4.5 mm lead lengths for TO-220), which results in an additional 0.3 mOhm of parasitic resistance.

The higher the junction temperature, the higher the RDS(on) will be. Due to this positive temperature coefficient, it is possible to use multiple devices in parallel.

To calculate the dependency of the junction temperature:

    RDS(on)(Tj) = RDS(on),25 deg C * (1 + alpha/100)^(Tj - 25 deg C)     ... (9)

For OptiMOS Power MOSFETs, alpha value of 0.4 can be used for RDS(on) approximation.

### 2.10 Gate Threshold Voltage

The gate threshold voltage defines the required gate-source voltage at a specified drain current. During production, the threshold voltage is measured at room temperature with VDS = VGS and test drain currents in the uA range.

The threshold voltage decreases with increasing junction temperature.

### 2.11 Capacitances

The gate-source, gate-drain, and drain-source capacitances cannot be measured directly; however, they can be calculated from the measurable input, output, and reverse transfer capacitances:

    Ciss = CGS + CGD
    Coss = CDS + CGD
    Crss = CGD

Clear dependencies of the voltages are shown for reverse (Crss) and output (Coss) capacitances due to the change in the space charge region during the switching transition.

### 2.12 Reverse Diode Characteristics

Key parameters:

- **Diode continuous forward current (IS)**: Maximum permissible DC forward current of the body diode at TC = 25 deg C, normally equal to the MOSFET's continuous current limit.
- **Diode pulse current (IS,pulse)**: Maximum permissible pulsed forward current at TC = 25 deg C.
- **Diode forward voltage (VSD)**: Source-to-drain voltage during diode's on-state (MOSFET off-state).
- **Reverse recovery time (trr)**: The time needed for the reverse recovery charge to be removed.
- **Reverse recovery charge (Qrr)**: The charge stored in the diode during its on-state. This charge needs to be completely removed before the diode's blocking capability resumes. The higher the switching rate of the current (di/dt on the order of 100 A/us or more), the higher the reverse recovery charge.

### 2.13 Avalanche Characteristics

The dependence of the pulsed avalanche current IAS on the time in avalanche tAV shows that operating the MOSFET under the conditions below the curve is allowed with consideration of the maximum junction temperature. The longer the avalanche pulse, the lower the maximum allowed avalanche current. With higher temperature, the avalanche capability decreases.

### 2.14 Drain-source Breakdown Voltage

The diagram shows the linear temperature dependence of the typical minimum value of the drain-to-source breakdown voltage over the complete allowable temperature range (-55 deg C to +175 deg C).

### 2.15 Typical Gate Charge

The gate charge (Qg) comprises the gate-source charge (Qgs), the gate-drain charge (Qgd), and the charge required to increase VGS from the plateau to the desired VGS level.

- **Qgs**: Charge required for charging the gate-source capacitance (CGS) to the plateau level. During this period, the drain current (ID) rises up to the load value after the gate threshold voltage (VGS(th)) has been reached.
- **Qgd**: Before the voltage VDS falls to its on-state value (VDS = RDS(on) * ID), the gate-to-drain capacitance (CGD), the Miller capacitance, has to be discharged.
- **Full turn-on**: Qgs and Qgd are not sufficient to fully switch on the transistor. Only with a charge corresponding to a full gate-source voltage (typically VGS = 10 V), the full turn-on resistance is reached, and thus static loss is optimized.

Note: The plateau level is not fixed. It varies with load conditions.

The complete gate-charge waveform changes with the drain-source voltage level (or the supply voltage level). The parameters are listed in the datasheet including Qgs, Qg(th), Qgd, Qsw, Qg total, Vplateau, Qg(sync), and Qoss.

### 2.16 Leakage Currents

Two types of leakage currents:

1. **IDSS**: Drain-source leakage current at a specified drain-source voltage (typically the minimum drain-source breakdown voltage) and at VGS = 0 V.
2. **IGSS**: Gate-source leakage current at a specified gate-source voltage (typically the maximum gate-source voltage) and at VDS = 0 V.

### 2.17 Other Important Parameters

#### 2.17.1 Switching Times

- **Turn-on time (ton)**: Sum of the turn-on delay time (td(on)) and the rise time (tr).
  - td(on): measured between 10% of VGS and 90% of VDS
  - tr: measured between 90% and 10% of VDS
- **Turn-off time (toff)**: Sum of the turn-off delay time (td(off)) and the fall time (tf).
  - td(off): measured between 90% of VGS and 10% of VDS
  - tf: measured between 10% and 90% of VDS

#### 2.17.2 Gate Resistance

Internal gate resistance (RG) is listed in the datasheet.

#### 2.17.3 Additional Maximum Ratings

Operating and storage temperature range: -55 to 175 deg C.
