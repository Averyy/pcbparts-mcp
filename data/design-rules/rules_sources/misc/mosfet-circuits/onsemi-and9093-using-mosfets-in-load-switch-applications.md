---
source: "onsemi AND9093 -- Using MOSFETs in Load Switch Applications"
url: "https://www.onsemi.com/pub/collateral/and9093-d.pdf"
format: "PDF 8pp"
method: "fetchaller"
extracted: 2026-02-14
chars: 20941
---

# AND9093/D: Using MOSFETs in Load Switch Applications

## Introduction

In today's market, power management is more important than ever. Portable systems strive to extend battery life while meeting an ever increasing demand for higher performance. Load switches provide a simple and inexpensive method for the system to make the appropriate power management decisions based on which peripherals or sub-circuits are currently in use. Load switches are found in notebooks, cell phones, hand held gaming systems and many other portable devices.

The load switch is controlled by the system, and connects or disconnects a voltage rail to a specific load. By turning unused circuitry off, the system as a whole can run more efficiently. The load switch provides a simple means to power a load when it is in demand and allows the system to maximize performance.

## Load Switch Basics

A load switch is comprised of two main elements: the pass transistor and the on/off control block, as shown in Figure 1.

The pass transistor is most commonly a MOSFET (either N-channel or P-channel) that passes the voltage supply to a specified load when the transistor is on.

## N-channel and P-channel Considerations

The selection of a P-channel or N-channel load switch depends on the specific needs of the application. The N-channel MOSFET has several advantages over the P-channel MOSFET. For example, the N-channel majority carriers (electrons) have a higher mobility than the P-channel majority carriers (holes). Because of this, the N-channel transistor has lower R_DS(on) and gate capacitance for the same die area. Thus, for high current applications the N-channel transistor is preferred.

When using an N-channel MOSFET in a load switch circuit, the drain is connected directly to the input voltage rail and the source is connected to the load. The output voltage is defined as the voltage across the load, and therefore:

V_S = V_OUT (eq. 1)

In order for the N-channel MOSFET to turn on, the gate-to-source voltage must be greater than the threshold voltage of the device. This means that:

V_G > V_OUT + V_th (eq. 2)

In order to meet Equation 2, a second voltage rail is needed to control the gate. Therefore, the input voltage rail can be considered independently of the pass transistor. Because of this, the N-channel load switch can be used for very low input voltage rails or for higher voltage rails, as long as the gate-to-source voltage V_GS remains higher than the threshold voltage of the device. The designer must ensure that the device maximum ratings and the safe operating area of the MOSFET are not violated.

When using a P-channel MOSFET in a load switch circuit, the source is directly connected to the input voltage rail and the drain is connected to the load. In order for the P-channel load switch to turn on, the source-to-gate voltage must be greater than the threshold voltage. Therefore:

V_IN > V_G + V_th (eq. 3)

At minimum, the input voltage rail must be greater than the threshold voltage of the selected pass transistor (assuming the gate voltage is 0V when the load switch is turned on).

The P-channel MOSFET has a distinct advantage over the N-channel MOSFET, and that is in the simplicity of the on/off control block. The N-channel load switch requires an additional voltage rail for the gate; the P-channel load switch does not. As with the N-channel MOSFET, the designer must ensure that the device maximum ratings and the safe operating area of the P-channel MOSFET are not violated.

## Load Switch Control Circuit Considerations

There are multiple ways to implement the on/off control block in a load switch circuit. This section will cover one control circuit example for the N-channel and one for the P-channel load switch.

### N-channel

Figure 2 shows an example load switch control circuit for an N-channel pass transistor. A logic signal from the system power management control circuitry turns the load switch on and off via a small-signal NMOS transistor, Q1. When EN is LOW, Q1 is off and the pass transistor gate is pulled up to V_GATE to keep it turned on. When EN is HIGH, Q1 turns on, the pass transistor gate is pulled to ground, and the load switch turns off. Resistor R1 is selected so that milliamps of current or less flow through R1 when Q1 is on. A standard range is 1 kohm to 10 kohm.

An additional voltage source, V_GATE, is needed to keep the gate-to-source forward biased. As expressed in Equation 2, the gate voltage must be larger than the sum of the output voltage and the threshold voltage. This may be undesirable for systems that do not have an extra voltage rail available.

### P-channel

Figure 3 shows an example load switch control circuit for a P-channel pass transistor. As with the N-channel example, a logic signal from the system power management control circuitry turns the load switch on and off via a small-signal NMOS transistor, Q1. When EN is LOW, Q1 is off and the gate is pulled up to V_IN. When EN is HIGH, Q1 turns on, the pass transistor gate is pulled to ground, and the load switch turns on. As with the N-channel control circuit, resistor R1 is selected so that milliamps of current or less flow through R1 when Q1 is on. A standard range is 1 kohm to 10 kohm.

For both control circuit implementations, the small-signal NMOS transistor, Q1, can be integrated into the same package as the pass transistor.

## Efficiency Considerations

Efficiency is critical to the success of the overall power management of the system. In a load switch circuit, the load current flows directly through the pass transistor when it is turned on. Therefore, the main power loss is the conduction loss.

P_LOSS = I_LOAD^2 x R_DS(on) (eq. 4)

The R_DS(ON) of the pass transistor causes a voltage drop between the input voltage and the output voltage, as shown in Equation 5. For applications requiring high load currents or low voltage rails, this voltage drop becomes critical. The voltage drop will increase as the load current increases, and the voltage drop at maximum load must be taken into consideration when selecting the pass transistor.

V_OUT = V_IN - I_LOAD x R_DS(on) (eq. 5)

As discussed in previous sections, the N-channel MOSFET has an R_DS(on) advantage over the P-channel MOSFET for a given die size. The R_DS(on) of an N-channel device can be two times lower than the R_DS(on) of a P-channel device of similar die area. This difference is most prominent at higher currents, but the N-channel R_DS(on) advantage becomes less prominent at lower currents. For applications such as cell phones and other portable low power devices, higher efficiency can be attained using a P-channel pass transistor, with the advantage of a simpler control circuit.

To illustrate this, let's assume that a 30 mohm N-channel transistor and a 50 mohm P-channel transistor have similar die size. The efficiency impact of the two devices will be examined for a high current application and a low current application.

For the first example, consider an application that requires a maximum load current of 10 A. Using Equations 4 and 5, the power loss at the maximum load is calculated to be 3 W for the N-channel transistor, and the voltage drop across the transistor is 300 mV. The power loss at the maximum load is 5 W for the P-channel transistor, and the voltage drop across the transistor is 500 mV.

Now consider an application in which the maximum current is 2 A. The power loss at maximum load is 120 mW for the N-channel device and 200 mW for the P-channel device. The voltage drop for the N-channel transistor is 60 mV and is 100 mV for the P-channel transistor.

As a final example, consider an application with an 850 mA maximum load current. The 30 mohm N-channel transistor's power loss is 21.7 mW compared to the 36.1 mW power loss of the 50 mohm P-channel transistor of similar die size. For low current applications, the N-channel R_DS(ON) advantage becomes negligible. P-channel pass transistors can be designed to have R_DS(on) as low as 8 mohm. Low R_DS(on) is critical for maximizing the efficiency of the load switch circuit and minimizing the voltage drop across the pass transistor. The specific conditions of the load switch application must be considered to make the final decision to use a PMOS or NMOS pass transistor.

## Gate-to-Source Voltage Considerations

The applied gate-to-source voltage of the pass transistor directly affects the efficiency of the circuit because R_DS(on) is inversely proportional to the applied gate-to-source voltage. Figure 4 shows an example R_DS(on) curve over a V_GS range.

The available V_GS of the circuit must be considered when selecting the pass transistor. Operating too close to the knee of the R_DS(on) curve can lead to higher conduction losses. Any small change in the gate-to-source voltage could result in a large change in the R_DS(on).

## Turn-on Considerations

Proper turn-on of the load switch pass transistor is critical for maximizing circuit performance and maintaining safe operation of the individual components. Optimal turn-on speed depends on the needs of the specific application and the device parameters of the selected load switch. If the turn-on speed is too fast, a transient current spike occurs on the input voltage supply, known as inrush current.

### Inrush Current

Inrush current occurs when the load switch is first turned on and is connected to a capacitive load, as shown in Figure 5. The capacitive load could be a battery, a DC:DC circuit, or other sub-circuit. The turn-on speed of the pass transistor directly influences the amount of inrush current seen on the input of the load switch.

Inrush current causes a dip in the input supply voltage that can adversely impact the functionality of the entire system. Likewise, inrush current spikes can potentially damage the load switch circuit components or reduce the lifetime of the components.

When the load switch is first turned on, an inrush current event occurs on the input as the C_LOAD is charged. This can be seen in Equation 6:

I_inrush = C_LOAD x dV/dt (eq. 6)

The faster the device switches on, the higher the inrush current will be. This potentially harmful inrush current can be reduced by controlling the load switch turn-on characteristics.

Figure 6 shows the simplified MOSFET turn-on transfer curves. There are four main regions for device turn-on, and each will be briefly addressed.

During Region 1, V_SG increases until it reaches V_TH. Because the device is off, V_SD remains at V_DD. During Region 2, V_SG rises above the V_TH and the device begins to turn on. Additionally, I_D increases to the final load current and C_GS charges.

In Region 3, V_SG remains constant as V_SD decreases to its saturation level, and C_GD charges. During Region 4, both C_GS and C_GD are fully charged, the device is fully on, and V_SG rises to its final drive voltage, V_DR. The plateau voltage, V_PL, is defined as:

V_PL = V_th + I_LOAD / g_fs (eq. 7)

### Inrush Current Limiting Circuit

In order to control the turn-on speed of the load switch, an external resistor R1 and external capacitor C1 are added to the load switch circuit as shown in Figure 7.

The selection of R1, R2 and C1 is very important to the performance of the load switch circuit. C1 must be much larger than the C_GD of the load switch device so this capacitance will dominate over C_GD. By placing C1 between the drain and source of the pass transistor, Region 3 of the V_SD curve becomes linear and the MOSFET slew-rate, dV_SD/dt, can be controlled.

R1 and R2 form a voltage divider that determines the voltage seen at the gate of the pass transistor. R1 and R2 can be calculated by using Equation 8 when the small-signal N-channel device is on.

R1 / (R1 + R2) = 1 - V_SG,MAX / V_IN (eq. 8)

In order to ensure that V_SG does not exceed the maximum rating of the device, V_SG,MAX is used. V_SG,MAX can be found in the device datasheet. R2 is the pull-up resistor described in previous sections, and is recommended to be between 1 kohm and 10 kohm.

R1 and C1 determine the turn-on speed of the pass transistor. C1 can be calculated by using Equation 9, where I_INRUSH is the desired maximum inrush current for the load switch circuit.

C1 = [(V_IN + V_PL) / (R1 * R2) - (V_PL / R2)] x (C_LOAD / I_INRUSH) (eq. 9)

Plugging Equation 7 into Equation 9, C1 becomes:

C1 = [(V_IN - V_th - I_LOAD/g_fs) / (R1 * R2) - (V_th + I_LOAD/g_fs) / R2] x (C_LOAD / I_INRUSH) (eq. 10)

### Estimating C_LOAD

For many designs, the equivalent C_LOAD may be an unknown. If this is the case, C_LOAD can be estimated from the measured inrush current waveform of the circuit without the addition of R1 and C1. Figure 9 shows an example inrush current waveform for a load switch circuit similar to Figure 5.

The load capacitance, C_LOAD, can be estimated using the following equation:

C_LOAD = 1/2 x dt x dI (eq. 11)

For the example current waveform shown in Figure 9, C_LOAD is estimated as:

C_LOAD = 1/2 x 1.6 us x 18 A = 1.28 uF

### Inrush Current Example

Consider the P-channel load switch circuit shown in Figure 7 with the following parameters:

**Table 1. Load Switch Circuit Example**

| Circuit Parameters | | PMOS Parameters | |
|---|---|---|---|
| V_IN = 10 V | V_SD,MAX = 20 V |
| I_LOAD,MAX = 5 A | V_SG,MAX = 8 V |
| I_IN,MAX = 8 A | V_TH = -0.67 V |
| C_LOAD = 1 uF | g_fs = 5.9 S |

First, R1 and R2 must be selected. For this example, a 1 kohm resistor was selected for R2. R1 was calculated by rearranging Equation 8 and solving for R1:

R1 = R2 x (V_IN - V_SG,MAX) / V_SG,MAX = 250 ohm

Next, C1 is calculated using Equation 10 and the parameters in Table 1.

C1 = [(10 - 0.67 - 5/5.9) / (250 x 1000) - (-0.67 - 5/5.9) / 1000] x (1 uF / 3)

C1 = 10.8 nF

Therefore, for the example circuit, the inrush current will be limited to 3 A by selecting a 1 kohm pull-up resistor (R1), a 250 ohm resistor for R2 and a 10 nF capacitor for C1.

## Turn-on Speed

Turn-on speed plays an important role in the behavior of the load switch. As mentioned, a fast device turn-on creates an inrush current. A softer turn-on reduces this current spike. However, caution must be taken when slowing down the MOSFET turn-on.

Figure 10 shows a standard load switch datasheet transfer curve. Drain current versus gate-to-source voltage is plotted at three different temperatures.

All three temperature curves will intersect at a specific V_GS. This point is known as the inflection point. For a V_GS above the inflection point, R_DS(on) increases as temperature increases. Thus, as the device heats up, a cell carrying higher current will become more resistive and current will be shared with cells carrying lower current. This MOSFET property creates a uniform current sharing across all the cells. Below the inflection point, the MOSFET behaves more like a bipolar transistor. As the device heats up, a cell with higher current than the surrounding cells will continue to take more current. If the device remains within this transition region for too long, thermal runaway can occur.

The load switch should be operated with a V_GS above the inflection point to ensure proper device function. The threshold voltage for the example device shown in Figure 10 is around 0.8 V. The inflection point occurs around 1.75 V. For the example device, it is recommended to operate at a V_GS of 1.8 V or higher.

## Safe Operating Area

The Safe Operating Area (SOA) defines the safe operating conditions of the load switch. Operation outside of this region can degrade the performance, reliability and lifetime of the device, and can potentially damage other components within the system.

The load switch must have a continuous current rating greater than the maximum load current of the application. Likewise, the MOSFET must not be operated outside of the maximum V_DS and V_GS specifications. The device datasheet specifies the absolute maximum ratings and also contains a figure showing the Safe Operating Area (SOA).

Figure 11 shows an example MOSFET SOA for an N-channel device. The outer boundaries of the safe operating area are determined by: the R_DS(on) at maximum junction temperature, the maximum drain current I_DM, and the rated breakdown voltage V_DSS of the device. I_DM is limited by the package, source wires, gate wires and die characteristics.

The basic power and current equations used to generate the SOA curve are:

V_DS = P_D / I_D  or  I_D = P_D / V_DS (eq. 12)

I_D = sqrt(V_DS / R_DS(on),MAX@TJMAX) (eq. 13)

First, the outer boundaries of the SOA are drawn: the maximum I_D and V_DS lines. Next, the R_DS(on) boundary is drawn by using Equations 12 and 13 to determine the end points, and the slope of the R_DS(on) boundary line is R_DS(on),MAX@TJMAX.

The DC line is determined by the maximum continuous power the device can dissipate. The continuous power dissipation is specified in the device datasheet. The DC line intersects the outer SOA boundaries in two places: at the R_DS(on) limit and at the V_DS limit. Additional lines are plotted for a single pulse of 10 ms, 1 ms, 100 us and 10 us duration. The safe operation region is located within the outer I_DMAX and V_DSMAX limits, and underneath the calculated R_DS(on), DC and single pulse lines.

### SOA Example

The example MOSFET device from Figure 11 has the following datasheet specifications:

**Table 2. Example MOSFET Datasheet Specs**

| Datasheet Parameter | Datasheet Value |
|---|---|
| BV_DSS | 30 V |
| P_D,CONTINUOUS | 1 W |
| I_D,MAX | 45 A |
| R_DS(ON)@TJMAX | 33.5 mohm |

The R_DS(on) line for the Figure 11 example MOSFET can be drawn using Equations 12, 13 and the values presented in Table 2. The first end-point is located at a V_DS of 0.1 V, and the second end point is located at the I_D limit of 45 A.

Similarly, the DC line can be drawn using Equations 12 and 13 to calculate the end points. The first DC line end-point is at a V_DS of 30 V. Using Equation 12 and the P_D value presented in Table 2, the current at 30 V is calculated to be 0.03 A. The second end-point is where the DC line intersects the R_DS(on) boundary. Therefore, the current can be calculated using Equation 13 and then plugging the calculated drain current into Equation 12 to determine the corresponding voltage. For this example MOSFET, the DC line intersects the R_DS(on) boundary at 0.18 V and 5.5 A. The calculated V_DS and I_D values can be verified with Figure 11.

The single-pulse lines are calculated using the same methodology and equations as for the DC line, but using the power dissipation for a single pulse of: 10 ms, 1 ms, 100 us and 10 us.

## ON Semiconductor Load Switches

ON Semiconductor has a large portfolio of P-channel and N-channel load switches in a wide variety of packages. ON Semiconductor load switches are offered in the following configurations: single, dual, and complementary.

**Table 3. ON Semiconductor Load Switches**

| Package | Dimension (mm) | Part Number | Configuration | Pol | V_DS (V) | V_GS (V) | I_D (A) | R_DS(on) @ 4.5 V | @ 2.5 V | @ 1.8 V | @ 1.5 V |
|---|---|---|---|---|---|---|---|---|---|---|---|
| XLLGA-3 | 0.6 x 0.6 x 0.4 | NTNS3A91PZ | Single | P | -20 | +/-8 | 0.214 | 1.6 ohm | 2.4 ohm | 3.3 ohm | 4.5 ohm |
| XLLGA-3 | 0.6 x 0.6 x 0.4 | NTNS3190NZ | Single | N | -20 | +/-8 | 0.229 | 1.4 ohm | 1.9 ohm | 2.7 ohm | 4.3 ohm |
| SOT-883 | 1.0 x 0.6 x 0.4 | NTNS3A65PZ | Single | P | -20 | +/-8 | 0.235 | 1.6 ohm | 2.4 ohm | 3.3 ohm | 4.5 ohm |
| SOT-883 | 1.0 x 0.6 x 0.4 | NTNS3164NZ | Single | N | -20 | +/-8 | 0.245 | 1.5 ohm | 2.0 ohm | 4.0 ohm | 6.8 ohm |
| SOT-963 | 1.0 x 1.0 x 0.5 | NTUD3170NZ | Dual | N | 20 | +/-8 | 0.22 | 1.5 ohm | 2.0 ohm | 3.0 ohm | 4.5 ohm |
| SOT-963 | 1.0 x 1.0 x 0.5 | NTUD3169CZ | Comp | N/P | +/-20 | +/-8 | 0.22/0.25 | 1.5/5.0 | 2.0/6.0 | 3.0/7.0 | 4.5/10.0 |
| SOT-723 | 1.2 x 1.2 x 0.5 | NTK3139P | Single | P | -20 | +/-6 | 0.78 | 0.48 ohm | 0.67 ohm | 0.95 ohm | 2.2 ohm |
| SOT-723 | 1.2 x 1.2 x 0.5 | NTK3134N | Single | N | 20 | +/-6 | 0.89 | 0.35 ohm | 0.45 ohm | 0.65 ohm | 1.2 ohm |
| UDFN | 2.0 x 2.0 x 0.55 | NTLUS3A18PZ | Single | P | -20 | +/-8 | 8.2 | 18 mohm | 28 mohm | 50 mohm | 90 mohm |
| UDFN | 2.0 x 2.0 x 0.55 | NTLUS3A39PZ | Single | P | 20 | +/-8 | 5.2 | 39 mohm | 50 mohm | 81 mohm | 147 mohm |
| WDFN | 3.3 x 3.3 x 0.8 | NTTFS3A08PZ | Single | P | 20 | +/-8 | 14 | 6.7 mohm | 9.0 mohm | -- | -- |

## References

1. C. S. Mitter. "Active Inrush Current Limiting Using MOSFETS." Application Note #AN1542. Motorola.
2. P. H. Wilson. "Controlling 'Inrush' Current for Load Switches in Battery Power Applications." EE Times Asia, July 2001.
3. Q. Deng. "A Primer on High-Side FET Load Switches." EE Times, May 2007.
