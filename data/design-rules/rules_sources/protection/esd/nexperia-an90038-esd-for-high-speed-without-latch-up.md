---
source: "Nexperia AN90038 -- ESD for High-Speed Without Latch-Up"
url: "https://assets.nexperia.com/documents/application-note/AN90038.pdf"
format: "PDF 24pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 36502
---

# ESD protection for high-speed interfaces without latch-up

**Keywords:** ESD protection, snapback, trigger voltage, TLP, dynamic resistance, signal integrity, latch-up

**Abstract:** This application note discusses ESD protection diodes under the aspect of achieving a high system level robustness. Snapback devices provide best clamping performance but the risk of latch-up needs to be evaluated. This document assesses the usage of deep snapback ESD protection for USB interfaces and other later generation super speed interfaces.

## 1. Introduction

With every new generation of data interfaces data rates increase accordingly. High-speed interfaces like USB3.x can be found in almost all end application areas, like in computing and consumer applications. Due to electrification and introduction of enhanced safety and multimedia functionality there is a growing usage of high-speed data communication in automotive products. Higher data rates require lower parasitic capacitances for the inputs of system chips which also implies higher sensitivity of these inputs to surge and ESD (ElectroStatic Discharge) events. Additionally, sensitivity of digital interfaces has increased due to ongoing further miniaturization of semiconductor structures.

For a design of robust systems withstanding incoming ESD strikes, it has become mandatory to add external ESD protection devices in a design. ESD protection diodes should be placed as close as possible to the entry point of an ESD strike. If the protection device is located close to the connector of an external interface, over-voltage pulses get shorted to ground directly at the connector. Less current can flow into the entire PCB and into the system chip or lead to malfunction by an unexpected current path on the board. Finally, the anyhow available line inductance will reduce the peak clamping voltage, while the line resistance will slightly limit the current flowing into the protected system if most of it is located between ESD protection device and protected system in the PCB layout.

To solve this problem, high performance ESD protection devices have to be selected which combine a very low capacitance for maintaining the signal integrity of the digital signals, together with a very good clamping capability that clips the residual voltage of a surge event into the allowed range of the interface to be protected.

ESD protection diodes with different topologies are offered on the market. This document explains these options and the related advantages or potential drawbacks.

## 2. Topologies of ESD protection devices

The simplest solution for clamping of ESD and surge events is to connect a Zener diode between ground and the signal to be protected as depicted in Fig. 1.

> Fig. 1. ESD and surge protection using a Zener diode

For negative voltages the Zener diode operates in forward conduction and incoming surge voltages get clamped. Fig. 2 shows the I-V characteristic of a Zener diode. Like for an ordinary pn-diode the IF-VF curve is quite steep in the first quadrant of the diagram, once VF is bigger than about 0.7 V. Signal 1 works in a positive voltage operating range. The Zener diode works in reverse mode, in the blocking area below VRWM. For VRWM leakage current, called IRM, is very small, this means in a league of typically a few nA only. VBR is the reverse voltage at which a defined current of normally 1 mA flows through the diode. From this point onwards, dynamic resistance becomes small, and the steepness of the I-V curve is high. The clamping voltage is quite stable even if high current is applied. It would be ideal to have a perpendicular curve above the breakdown voltage.

> Fig. 2. I-V characteristic of a Zener diode based unidirectional ESD-protection diode

If two Zener diodes are put in series with opposite polarity as depicted in Fig. 3, a so-called bi-directional ESD protection diode is created with a symmetrical I-V curve assuming that the single Zener diodes have the same characteristics.

> Fig. 3. ESD and Surge Protection using 2 Zener diodes in series with common anode

In Fig. 4 an example of an I-V curve of a bi-directional Zener diode is depicted. Often bi-directional ESD protection is applied into application where the signal to be protected uses positive voltage only. Reason for this is that customers do not need to take care of mounting direction for assembly. Another motivation is to avoid harmonic distortions if signal undershoots get clipped. For the manufacturer of ESD protection devices, bi-directional products have the advantage that it is easier to achieve a very low diode capacitance Cd. If two capacitors are put in series, overall capacitance gets smaller. Cd is half as big only if the capacitors are identical.

> Fig. 4. I-V characteristic of a Zener diode based bi-directional ESD-protection diode

ESD protection with Zener diode structure does not provide a sufficiently low clamping voltage for higher surge current IPP. Clamping voltage roughly follows the equation:

V_clamp = V_BR + R_dyn x I_PP

Rdyn should be as small as possible in the area where an ESD device is supposed to clamp incoming surge events. Rdyn is normally a positive value for high current exposure, so there is an increase for the clamping voltage with higher current flowing through the ESD diode. To achieve a lower clamping voltage, modern ESD protection devices have a snap-back characteristic. These devices show a very low leakage current below the stated operating voltage VRWM. If the voltage is increased further current becomes higher. At a specific voltage called Vt1, the component turns on and voltage across the device drops down significantly. With further increase of current the clamping voltage goes up with a preferably steep I-V curve, so a low dynamic resistance. If current through the diode is reduced, the device snaps back into a high-ohmic state if a specific hold current or hold voltage is fallen below. In Fig. 5 a typical I-V characteristic of a deep snapback ESD protection diode is depicted. At about 7.7 V the device turns on and jumps down to about 1.3 V. If current becomes smaller than the hold current IHOLD of about 22 mA the device goes back to off-state. VHOLD is about 2.4 V. Like a thyristor such ESD protection shows a hysteresis in the I-V curve, so turn-on happens at a higher voltage and current compared to the turn-off. The depicted device in Fig. 5 has a symmetrical I-V characteristic, the positive polarity region is shown here only. For the clamping voltage the equation below can be applied above the snapback voltage:

V_clamp = V_snapback + R_dyn x I_PP

> Fig. 5. I-V characteristic of a deep snapback ESD protection device

The snapback characteristic can also be seen in a TLP (Transmission Line Pulse) curve. In Fig. 6 the TLP curve of the same component as depicted in Fig. 5. The hold current cannot be derived from a TLP curve but from the test results of an I-V curve tracer or a similar test approach. In a TLP curve test, pairs of voltage and current from several TLP pulse shots with increasing voltage are noted down as a special I-V curve. A TLP curve shows the snapback voltage accurately but neither an exact hold voltage nor the hold current. For a device with a quite high trigger voltage, TLP current at the snapback can be quite high, much higher than the hold current with:

I_trigger = (12.8 V - 7.5 V) / 50 ohm = 106 mA

The hold current IHOLD for a DC condition can be derived from the left bottom corner of the hysteresis curve depicted in Fig. 5 only. In this application note we will show in Section 4 that the hold current, required to keep the protection device in on-state for an AC-operating mode, can be significantly higher than the DC-value.

> Fig. 6. TLP curve of a deep snapback ESD protection device

## 3. Load line analysis approach

For deep snapback devices the application has to be reviewed if there is a risk that the ESD protection device remains in on-state after a surge event is gone. This would be a so-called latch-up condition where a circuit does not get back into the normal operation mode after a trigger event has happened.

Deep snapback devices are not applicable for DC supply lines. DC supplies can easily provide hold currents of typical deep snapback ESD diodes. After a deep snapback ESD diode has been triggered, a DC-supply would drive the maximum output current through the ESD diode, and it is very likely that the protection device will be damaged by an EOS (Electrical Overstress) failure because the maximum allowed junction temperature will be exceeded.

For data interfaces the situation needs to be evaluated in more detail. The current drive capability of the driver stages is limited to lower currents compared to the above discussed supply voltage scenario. Maximum current is the result of the open-loop source voltage and the driver output resistance which is often predefined by the standard termination of a discussed interface.

With a load line analysis latch-up scenarios can be evaluated with a graphical approach. In Fig. 7 the load line of an output is depicted in red for a voltage source or a driver stage with a voltage of VBUS and an output resistance of RS. Maximum output current is present if the output is shorted. If no current must be provided the open loop voltage VBUS is present at the driver output.

> Fig. 7. Load line principle, output load line in red, Zener diode characteristic in blue

The load line is a linear curve (red line) starting from ISHORT and VOUT = 0 V, going down to the point with IOUT = 0 A and VOUT = VBUS.

An I-V characteristic of a Zener diode is overlaid in blue. For the circuit shown in Fig. 8 which is a Zener diode with the assumed blue non-linear I-V curve connected to the voltage source VBUS and the output resistance RS, the intersecting of the two curves is the operating point.

There is one operating point or intersection possible only. A latch-up is impossible with an ESD protection like a Zener diode. Leakage current in the working voltage area is very low and the breakdown voltage is not exceeded in normal operation (VBR > VBUS).

> Fig. 8. Voltage source with series resistor RS and Zener diode ZD1 as load

In Fig. 9 the I-V curve of a snapback ESD protection device is overlaid with the linear load line of a voltage source and a series output resistor as depicted in Fig. 8. There are now two intersections between the two curves or in other words two possible stable operating points. In normal operation an interface stays below the trigger voltage like the operating point OP1. If an ESD strike is applied the operating point OP2 can be obtained. The voltage VOP2 is very low because of the deep snapback voltage in on-state of the ESD protection. If the interface driver keeps on working with the red load line set-up the interface is stuck in a latch-up condition. The signal line cannot change the single-ended state anymore.

> Fig. 9. Load line of a voltage source with series resistor RS and an overlaid I-V curve of a snapback ESD protection

The scenario depicted in Fig. 10 has no risk of latch-up. After a surge event the hold current of the snapback ESD diode cannot be provided, the interface can recover normal operation. To safeguard this there are several options. An ESD diode with a suitable hold current can be selected. Another solution is to make the load line flat enough to avoid multiple intersections. This can be achieved with a smaller ISHORT addressed with a higher resistance in the output of the driver stage or a smaller single-ended high state drive voltage. The latter mentioned options are more of a theoretical nature because standard high-speed interfaces have fixed electrical definitions in terms of termination and voltage levels.

> Fig. 10. Snapback device combined with a latch-up free load line situation

DC-supplies have usually a very low RS which means that the output keeps an almost constant voltage with no dependency on the output current in the ideal case. For VOP1 bigger than VHOLD a latch-up will happen and the ESD protection device will be damaged with an EOS (Electrical Over Stress) very likely. For a safe operation the relation VHOLD > VDC must be obeyed.

> Fig. 11. Snapback device combined with a latch-up free load line situation

An example for an AC signal protected with a bi-directional snapback ESD protection is shown in Fig. 12. The ESD protection device turns off again after a polarity change and normal operation can continue in the voltage area below the trigger thresholds within the stated VRWM range where leakage current is extremely low.

> Fig. 12. Bidirectional snapback device applied to an AC signal line. Recovery from on-state to high-ohmic off-state after a negative ESD event (dotted red line) followed by a signal polarity change

For high-speed data signals the drivers do not output a constant logical state. Modern interfaces are coded such that the digital 0 and 1 states appear for an identical number of clock cycles. This has the big advantage that the signal is DC-free and can be coupled via capacitors.

According to the load line approach a snapback ESD diode should turn off with the next single ended low state for an ideal component. In Fig. 13 it is assumed that the low state voltage is 0 V.

> Fig. 13. Example of High to low state change of a single-ended data line

## 4. Turn on and turn off behavior at a high frequent signal line

For deep snapback devices the application has to be reviewed if there is a risk that the ESD protection stays in on-state or a latch-up condition.

If a snapback ESD diode is connected to a function generator which outputs a rectangular signal with a frequency equal or higher than 5 MHz at a duty cycle of 50 %, the signal level can be increased until the protection device turns on once the trigger level is reached or exceeded. The simple test set-up is shown in Fig. 14. Snapback ESD protection components are designed such that they turn on extremely fast. A low clamping voltage is required almost instantaneously to protect against incoming surge events effectively. If the generator is adjusted to 12.8 V output voltage, the snapback device is turned on and stays in on-state because it gets a rather high average hold current. The part does not turn on and off with every clock cycle. The pulses applied are clamped down to about 1.4 V as shown in Fig. 15. This snapback voltage could also be seen in Fig. 5 and Fig. 6 in Section 2 for the example device already. The voltage at the DUT is about 7.5 V before the device snaps back. The pulse trigger current is:

I_trigger = (12.8 V - 7.5 V) / 50 ohm = 106 mA

> Fig. 14. Test set-up with rectangular signal applied to a DUT

The green trace shows a reference signal which is not clamped. The red trace is the clamped signal at the ESD protection diode.

> Fig. 15. Turn on of snapback ESD protection in 5 MHz signal

If the generator voltage is decreased step by step, the protection device turns off at an adjusted generator voltage of about 9.3 V. This operating point is the hold condition where the device leaves the deep snapback.

For I_pulse(hold) it can be stated:

I_pulse(hold) = (9.3 V - 1.4 V) / 50 ohm = 158 mA

From this hold condition operating point, the clamping voltage jumps up from the snapback voltage to about 7.1 V, which is roughly the bottom right corner of the hysteresis curve shown in Fig. 5. The pulse current can be calculated with the formula:

I_pulse = (9.3 V - 7.1 V) / 50 ohm = 44 mA

This scenario, where the device has just turned off is depicted in Fig. 16.

With the turn-off and the jump back to a higher clamping voltage, 7.1 V for the device discussed here, the through-put current goes down and the generator voltage needs to be increased like for the turn-on experiment to get back into a snapback again. So a significant hysteresis can be observed in the experiment performed. The operating point seen after the snapback is released would not be reached in a real high-speed interface normally because of the about 7.1 V drive voltage. So the ESD diode would go back into the full high-ohmic state directly which means the interface would return into the VRWM voltage range after an ESD strike.

> Fig. 16. Turn off

With further reduction of the generator voltage, finally almost no current flows, as to be expected from an I-V curve like depicted in Fig. 5. From a generator voltage of 7 V and further down this high-ohmic state is reached. The diode voltage is identical with the adjusted generator voltage.

In Fig. 17 a hysteresis curve is shown which is valid for the described 5 MHz test. The hold current for the pulses is much higher compared to DC-Test hysteresis curve shown in Fig. 5. The pulses need a higher current to create a sufficient average current to keep the snapback device in on-state.

> Fig. 17. I-V-Hysteresis Curve of a Treos ESD protection device (5 MHz test signal with 50 % duty cycle and 50 ohm output resistance of the signal generator)

The takeaway for the experiment performed is that the risk of a latch up can be significantly reduced for deep snapback devices if a high-speed digital data signal is applied. From about 5 MHz upwards snapback protection devices can be kept in a constant on-state if the pulse amplitude is high enough. This means that the devices do not turn off after each high state of a data signal. For keeping a latch-up active, the high state pulses need a higher hold current than the I-V curves would let expect. The hold current needed per pulse was in the league of the trigger current. The described test has been performed with applying ground level as low state of the signal. The effect of a relaxed latch-up risk gets fully effective if there is no bias voltage overlay. This means USB legacy mode signals means USB LS and FS modes or open drain bus signals can profit a lot from the finding.

## 5. Latch-up considerations for major data interfaces

### 5.1. USB Interfaces

For USB interfaces the USB2.0 data lines D+/D- work in half-duplex mode. This means the direction of data may change sequentially on one differential pair. For USB3.x and USB4 there are separate signal pairs for data flow directions allowing a full-duplex operation of the interface. The D+/D- lines for USB2.0 and the super-speed data lines RX+/RX- and TX-/TX+ have a different realization in hardware and need to be discussed separately with respect to a risk of latch-up in combination with SCR-based ESD protection devices.

#### 5.1.1. USB2.0 data lines

In Fig. 18 a block diagram of an USB2.0 transceiver is shown. There are two driver stages connected to the data lines. The LS/FS driver supports the legacy Low-speed (LS) and Fast-speed (FS) modes of USB1.1.

> Fig. 18. USB2.0 Transceiver block diagram with LS/FS and HS Drivers

The detection of data speed capability of a device connected to a host is performed such that a 1.5 kohm pull-up resistor Rpu is connected to the D- line for LS mode as shown in Fig. 19 but to the D+ line for FS mode as depicted in Fig. 20. An USB2.0 capable device must have a pull-up resistor at the D+ line. The bitrate is 1.5 Mbit/s for the Low-speed and 12 Mbit/s for Fast-speed Mode.

> Fig. 19. Low-speed system, Rpu placement at D- line (Rpd = 15 kohm +/- 5%, Rpu = 1.5 kohm +/- 5% nominal, slow slew rate buffers)

> Fig. 20. Full-speed system, Rpu placement at D+ line (Z0 = 90 ohm +/- 15%, Rpd = 15 kohm +/- 5%, Rpu = 1.5 kohm +/- 5%)

A USB2.0 host tries with a so-called chirp sequence if the connected device can communicate in High-Speed (HS) Mode. In Fig. 21 the procedure is shown in detail. The host starts a reset with the LS/FS drivers terminating both series resistors Rs to ground. HS drivers work with 17.78 mA current sources for generating a high state on a signal line. After the host's grounding of both signal lines, a connected device which is capable of USB2.0, sends a K-state with its HS-driver for at least 1 ms. The high level is 800 mV. The hub then answers with K_J chirps. After this the device disconnects the pull-up resistors and connects the Rs series resistor to GND. The level of the single ended signals is decreased to 400 mV nominal with the final USB2.0 termination scheme.

> Fig. 21. USB2.0 "Chirp" sequence

For the calculation of the maximum latch-up current supplied from an LS/FS driver, a simplified schematics is shown in Fig. 22. The 15 kohm pull-down resistors are present at downstream facing transceivers only on both signal lines of the D+/D- lane. Whereas the pull-up resistors are placed at one signal line only as explained above. These pull-down and pull-up resistors can be neglected for the latch-up current calculation because the series resistor Rs is much smaller with a value range from 28 ohm to 44 ohm for a device without USB2.0 capability. The nominal high state voltage at the driver is 3.3 V. The maximum allowed voltage is 3.6 V. For the latch up risk assessment the worst-case scenario must be considered with 3.6 V drive and the smallest allowed series resistance of 28 ohm. For a system which is capable of USB2.0 the series resistors need to fulfill the requirement for Rs of 45 ohm +/- 10 %. The worst-case is 40.5 ohm accordingly.

The maximum current through a snapback ESD protection device in on-state to be considered in an LS/FS system is:

**Formula 1:** I_max(LS/FS) = (3.6 V - V_snapback) / 28 ohm

For a USB2.0 capable device, the formula to be applied is:

I_max(USB2.0_LS/FS) = (3.6 V - V_snapback) / 40.5 ohm

The USB LS/FS modes profit from the finding discussed in Section 4 that deep snapback devices require a higher hold current for data signals with more than about 10 MBit/s compared to hold currents derived from a DC based I-V curve measurement. This fact relaxes the latch-up risk significantly.

> Fig. 22. LS and FS driver schematics with termination and ESD protection diode. Rpd is present at downstream facing transceivers, Rpu at upstream facing transceivers

In Fig. 23 a simplified schematic diagram for a connected USB2.0 system in HS mode is depicted. The driver stage is a switched current source with 17.78 mA nominal high state current. Host and USB device are connected via an USB cable. The parasitic components of the cable are neglected. On both sides there is a 45 ohm termination to ground provided via the LS/FS drivers (see Fig. 18).

> Fig. 23. HS driver schematic diagram with 45 ohm termination at host and device side and a switched current source as driver output stage

The nominal single-ended high state voltage is then VOH = 17.78 mA x 22.5 ohm = 400 mV

As worst case for the latch-up risk the maximum driver current combined with the maximum resistance must be considered. The USB2.0 specification allows a 10% tolerance. Rs(max) is 49.5 ohm and the maximum current is 19.56 mA, means that the maximum high state voltage about 500 mV.

> Fig. 24. Equivalent HS driver with converted voltage source for latch-up evaluation

Based on the above discussed facts it can be concluded that a latch-up in LS and FS mode could happen in a connected condition with a shielded USB cable only, because the LS/FS drivers get active after connecting and after the location of Rpu has been sensed. It is very unlikely that an ESD strike can enter the system after connection is established. This means the risk for a latch-up issue for D+/D- data lines is very small in general.

For the residual surge risk at a connected link in a USB1.1 system, a hold voltage above 3.6 V is safe or if hold current is above the maximum possible high-state current for the ESD diode according to Formula 1. If we assume a Vsnapback of 2 V as an example, IHOLD should be bigger than 39.5 mA.

For a USB2.0 system the low maximum drive voltage eliminates the risk of a latch-up if the snapback voltage is higher than 0.5 V. This is the case for all known ESD devices in the market.

#### 5.1.2. USB3.2 and USB4 data lines

With the super-speed USB interface, signals are transmitted via at least one pair of separate RX and TX lanes. This allows full-duplex operation which means that sending and receiving data at the same time is supported. The USB Type-C connector is becoming the mainstream connector type and replaces the older connectors like Type-A, mini and micro connectors more and more. The Type-C connector provides two TX signal pairs as well as two RX pairs. In Table 1 the evolutionary increase of the data rate can be seen with the introduction of new modes. The mode names have been changed to a common nomenclature and now indicate more clearly which lane speed is applied and how many lanes are used.

**Table 1. Overview of USB super-speed modes**

| Mode Name | Old name | Number of lanes | Lane Speed (Gbit/s) | Nominal interface speed (Gbit/s) |
|---|---|---|---|---|
| USB3.2 Gen 1x1 | USB3.0 or USB3.1 Gen 1 | 1 | 5 | 5 |
| USB3.2 Gen 1x2 | | 2 | 5 | 10 |
| USB3.2 Gen 2x1 | USB3.1 Gen 2 | 1 | 10 | 10 |
| USB3.2 Gen 2x2 | | 2 | 10 | 20 |
| USB4 Gen 2x1 | | 1 | 10 | 10 |
| USB4 Gen 2x2 | | 2 | 10 | 20 |
| USB4 Gen 3x1 | | 1 | 20 | 20 |
| USB4 Gen 3x2 | | 2 | 20 | 40 |
| USB4 Gen 4x1 | | 1 | 40 | 40 |
| USB4 Gen 4x2 | | 2 | 40 | 80 |

There is USB3.2 Generation 1 (Gen 1) and Generation 2 (Gen 2). Gen 1 supports 5 Gbit/s whereas Gen 2 offers 10 Gbit/s. The number of lanes is added behind the x in the mode name. With 2 lanes the overall data rate of the interface gets doubled nominally. With USB4 even higher data rate is introduced. In the naming Gen 3 is associated with 20 Gbit/s lane speed and Gen 4 with 40 Gbit/s. The maximum nominal interface data rate in combination of Gen 4 and 2 lanes is 80 Gbit/s.

> Fig. 25. Interface topology for USB super-speed signals RX and TX

From USB3.2 Gen 2 x1 (old name USB3.1 Gen2) onwards the receiver inputs are AC-coupled with 330 nF capacitors. The signal lines in the cable have no bias voltage provided from the SoC inputs. In case of short circuits to VBUS at the connectors or in the cables, the DC voltage cannot become present constantly at the RX input pins but stress the input for a limited time while the coupling capacitor is charged.

With the ESD protection placed as depicted in Fig. 25 there is no risk of latch up at all because no DC bias is possible due to the coupling capacitors if there are no short-circuits to VBUS as a severe fault condition. The placement of the ESD protection at the connectors has the additional advantage that the capacitors are protected against ESD strikes. This can be important for small package capacitors which can be sensitive to very high current from ESD events. The charge from surge events increases the voltage of the capacitors which can exceed the specified limit if multiple strikes are applied.

If ESD protection is placed directly at the TX Phy-Output the possible voltages and currents have to be evaluated for this scenario. In the USB3.2 revision 1.1 specification document waveforms for single-ended and differential signal on the TX-lines are depicted as shown in Fig. 26. For the maximum possible single-ended voltage the maximum differential voltage as well as the maximum common mode or bias voltage must be considered. VTX-DIFF-PP(max) is 1.2 V. VCM(max) is 2.2 V.

As maximum single-ended voltage V_SE(max) = VCM(max) + VTX-DIFF-PP(max)/2 = 2.2 V + 0.6 V = 2.8 V has to be expected as worst case. The nominal termination is 45 ohm. The termination ranges from 36 ohm to 60 ohm. For latch-up considerations the minimum resistance of 36 ohm defines the worst-case scenario.

> Fig. 26. Single-ended and differential voltage waveforms for TX lines

Maximum latch-up current at the SoC TX pin can then be:

I_max = (2.8 V - V_snapback) / 36 ohm

Placing the protection behind the coupling capacitors is not inherent safe against a potential latch-up.

As stated above placing the ESD protection at the cable connectors is completely safe regarding latch-up if two capacitors per data signal is present like shown in Fig. 26. If there is no coupling capacitor at the super-speed inputs at the Phy in a legacy implementation of USB 3 there is one more scenario to be discussed.

> Fig. 27. Equivalent circuit diagram for Super-Speed signal path from TX to RX input without capacitive coupling at RX SoC pin (Rs(nom) = 45 ohm, 100 nF coupling cap, Rss cable, RDC termination > 10 kohm, RI(nom) = 45 ohm)

Fig. 27 shows the equivalent circuit diagram. Via Rs the data signal is driven. ESD protection is assumed at the transmitter as well as at the receiver side. The receiver input has a DC termination of more than 10 kohm. Therefore, no significant and constant latch-up current can flow. The discussed scenario has no latch-up risk.

In conclusion of the above discussion of different protection scenarios, USB3 and USB4 is safe against latch-up risk, only a protection of the TX-pins at the SoC behind the coupling capacitors requires some attention.

### 5.2. HDMI Interface

HDMI (High-Definition Multimedia Interface) is the major digital interface in the market for audio/video connections. Later generations include Ethernet and 3D features. CEC (Consumer Electronics control) allow that connected devices can control each other, for example that a TV starts a connected media player once the related input has been chosen. HDMI also supports a copy protection called HDCP which protects content against non-authorized copying. Resolution has been increased continuously in terms of quantization as well as in supported color spaces. This has led to an increase of data rate like for the USB interface as discussed in the prior chapter. 7680 x 4320 progressive with 60 Hz frame rate is the highest resolution for HDMI 2.1 with 48 Gbit/s total data rate. The additional clock signal channel was removed, and this lane is used as additional data channel. Table 2 gives an overview for the different versions of HDMI.

**Table 2. Overview of HDMI standards**

| HDMI version | 1.0 | 1.1 | 1.2 | 1.3 | 1.4 | 2.0 | 2.1 |
|---|---|---|---|---|---|---|---|
| Max pixel clock rate (MHz) | 165 | 165 | 165 | 340 | 340 | 600 | no extra clock channel |
| Max TMDS bit rate per lane incl. 8b/10b overhead (Gbit/s) | 1.65 | 1.65 | 1.65 | 3.4 | 3.4 | 6 | 12 |
| Max total TMDS throughput incl. 8b/10b overhead (Gbit/s) | 4.95 | 4.95 | 4.95 | 10.2 | 10.2 | 18 | 48 |
| Max audio throughput bit rate (Mbit/s) | 36.86 | 36.86 | 36.86 | 36.86 | 36.86 | 49.152 | 49.152 |
| Max video resolution over 24 bit/pixel single link | 1920x1200 p/60Hz | 1920x1200 p/60Hz | 1920x1200 p/60Hz | 2560x1600 p/60Hz | 4096x2160 p/30Hz | 4096x2160 p/60Hz | 7680x4320 p/60Hz |
| Max color depth (bit/pixel) | 24 | 24 | 24 | 48 | 48 | 48 | 48 |

#### 5.2.1. HDMI TMDS lines

The signal lanes of HDMI are called TMDS the abbreviation for Transition-Minimized Differential Signaling. A current source driving 10 mA is connected alternatively to the TMDS+ or TMDS- line. At the receiver side 50 ohm pull-up resistors are connected to 3.3 V. The nominal differential termination is 100 ohm.

> Fig. 28. Structure of TMDS signal path from transmitter to receiver (V1 = V2 = 3.3 V, R1 = R2 = 26 kohm, R3 = R4 = 50 ohm, I1 = 10 mA, NPN transistors Q1/Q2)

DVI interfaces have the same structure and the conclusions in this chapter are valid for DVI as well. For the evaluation of a latch-up risk the minimum resistance of the receiver termination must be considered. The nominal 50 ohm may deviate by +/- 10 %. The pull-up resistors have a minimum resistance of 45 ohm. The supply for the pull-up resistor can be 10 % higher than nominal which is a worst-case condition.

Latch-up current can be calculated then with the equation:

I_latchup(max) = (3.3 V * 1.1 - V_snapback) / 45 ohm = (3.63 V - V_snapback) / 45 ohm

An HDMI interface requires some attention with respect to possible latch-up conditions. Many HDMI input circuits are designed with active silicon circuits for the 50 ohm pull-up resistors. HDMI interfaces have to be safe for short-circuits on the TMDS lines according to HDMI standard requirements. To avoid overheating of active pull-up resistors, the pull-up voltage is shortly removed whenever a short is detected at the TMDS lines. This mechanism releases a latch-up condition. Please note that Transmission Minimized Differential Signal (TMDS) lines begin data transfer after connection is established. The risk of ESD strikes is much higher during the connecting process of a cable, and very unlikely to happen at a cable with fully established connection. In practice, no known field returns are caused by latch-up failures with HDMI interfaces. If the formula for the maximum possible latch-up current is taken into consideration using an ESD diode with a higher IHOLD any small residual risk for a hang-up is avoided.

#### 5.2.2. Display Port (DP)

Display port is very popular in computing applications as digital interface between a computer and a monitor. DP connections are offered as option together with HDMI interfaces. Like for HDMI, data rate is increasing with newer standards. DP2.0 can support up to 77.73 Gbit/s on 4 parallel data pairs. As video standard this is 7680 x 4320 pixels with 60 Hz frame repetition rate and 12-bit resolution. Fig. 29 shows the topology of a single data lane. At the TX- and RX-side the single lines are terminated with nominal 50 ohm against bias voltage supplies (Vbias-TX and Vbias-RX). The transmitter side is AC-coupled, whereas the receiver input pins are DC-connected to the DP-cable. The bias voltage can range from 0 V up to 2 V.

> Fig. 29. Structure of Display Port data lane (4 times present per data link, 50 ohm terminations to Vbias-TX and Vbias-RX)

Fig. 30 shows an equivalent circuit for a single line of a DP interface. ESD protection is placed at the connectors of the DP-source as well as the DP-receiver. Without a connection, the RX side has no risk of a latch-up because of the AC-coupling via capacitors. With a connected cable however the receiver side stand-alone has to be evaluated regarding a latch-up risk.

With ESD diodes that have a hold voltage above 2 V, the Display Port is safe against latch-up risk.

> Fig. 30. Equivalent circuit of a single data line of Display Port (50 ohm terminations, Rcable, AC coupling on TX side)

## 6. Conclusions

Modern high-speed interfaces require high performance ESD protection. A low clamping voltage must be achieved for incoming surge pulses. Dependent on the data rate of the target interface the capacitance of the protection diodes must be very small in a league 0.1 pF to 0.45 pF to avoid a big impact on signal integrity and the signal eye diagram. Snapback topology ESD protection has become the first-choice solution for sensitive interfaces. In the application note it was shown that the risk of latch-up can be managed well. For many scenarios like a USB4 super-speed lane there is no latch-up risk because of capacitive coupling and the absence of a DC path to provide a hold current. In the other cases the selection of a suitable snapback voltage, hold voltage and current can eliminate the risk of latch-up. Very often there is a potential latch-up risk for an established data connection only. In normal handling of an interface, risk of a surge or ESD event is present when the connection gets established with connecting a cable where the interface pin does not have a bias voltage yet to keep a snapback device in snapback mode. For higher signal frequency the effective hold current from the interface is not the same as for in a DC experiment due to an averaging effect. This reduces risk of latch-up compared to a simple calculation of maximum single ended signal voltage. Consequently, snapback devices can be recommended as the most effective ESD protection solution for modern generation high-speed interfaces which can be found in retimers, redrivers, CPUs or PCI bridges for interface extensions.

## 7. Revision history

| Document ID | Date | Description |
|---|---|---|
| AN90038 v.3 | 2023-07-10 | Several updates and additions throughout the Application note. |
| AN90038 v.2 | 2023-05-11 | Several updates and additions throughout the Application note. |
| AN90038 v.1 | 2023-03-02 | Initial release. |
