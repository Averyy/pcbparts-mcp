---
source: "ADI AN-149 -- Loop Compensation Design"
url: "https://www.analog.com/en/resources/app-notes/an-149.html"
format: "HTML"
method: "readability"
extracted: 2026-02-16
chars: 37428
---

### Introduction

Today’s electronic systems are becoming more and more complex, with an increasing number of power rails and supplies. To achieve optimum power solution density, reliability and cost, often system designers need to design their own power solutions, instead of just using commercial power supply bricks. Designing and optimizing high performance switching mode power supplies is becoming a more frequent and challenging task.

Power supply loop compensation design is usually viewed as a difficult task, especially for inexperienced supply designers. Practical compensation design typically involves numerous iterations on the value adjustment of the compensation components. This is not only time consuming, but is also inaccurate in a complicated system whose supply bandwidth and stability margin can be affected by several factors. This application note explains the basic concepts and methods of small signal modeling of switching mode power supplies and their loop compensation design. The buck step-down converter is used as the typical example, but the concepts can be applied to other topologies. A user-friendly LTpowerCAD™ design tool is also introduced to ease the design and optimization.

### Identifying The Problem

A well-designed switching mode power supply (SMPS) must be quiet, both electrically and acoustically. An undercompensated system may result in unstable operations. Typical symptoms of an unstable power supply include: audible noise from the magnetic components or ceramic capacitors, jittering in the switching wave forms, oscillation of output voltage, overheating of power FETs and so on.

However, there are many reasons that can cause undesirable oscillation other than loop stability. Unfortunately, they all look the same on the oscilloscope to the inexperienced supply designer. Even for experienced engineers, sometimes identifying the reason that causes the instability can be difficult. Figure 1 shows typical output and switching node waveforms of an unstable buck supply. Adjusting the loop compensation may or may not fix the unstable supply because sometimes the oscillation is caused by other factors such as PCB noise. If you do not have a list of possibilities in your mind, uncovering the underlying cause of noisy operation can be very time-consuming and frustrating.

Figure 1. Typical Output Voltage and Switching Node Waveforms of an “Unstable” Buck Converter.

Figure 2. A Typical Buck Step-Down Converter (LTC3851, LTC3833, LTC3866, etc.).

For switching mode power converters, such as an [LTC3851](/en/products/ltc3851.html) or [LTC3833](/en/products/ltc3833.html) current-mode buck supply shown in Figure 2, a fast way to determine whether the unstable operation is caused by the loop compensation is to place a large, 0.1μF, capacitor on the feedback error amplifier output pin (ITH) to IC ground. (Or this capacitor can be placed between the amplifier output pin and feedback pin for a voltage mode supply.) This 0.1μF capacitor is usually considered large enough to bring down the loop bandwidth to low frequency, therefore ensuring voltage loop stability. If the supply becomes stable with this capacitor, the problem can likely be solved with loop compensation.

An over-compensated system is usually stable, however, with low bandwidth and slow transient response. Such design requires excessive output capacitance to meet the transient regulation requirement, increasing the overall supply cost and size. Figure 3 shows typical output voltage and inductor current waveforms of a buck converter during a load step up/down transient. Figure 3a is for a stable but low bandwidth (BW) over-compensated system, where there is large amount of VOUT undershoot/overshoot during transient. Figure 3b is for a high bandwidth under-compensated system, which has much less VOUT undershoot/overshoot but the waveforms are not stable in steady state. Figure 3c shows the load transient of a well-designed supply with a fast and stable loop.

Figure 3. Typical Load Transient Responses of a) An Over-Compensated System; b) An Under-Compensated System; c) Optimum Design with a Fast and Stable Loop.

### Small Signal Modeling of PWM Converter Power Stage

A switching mode power supply (SMPS), such as the buck step-down converter in Figure 4, usually has two operating modes, depending on the on/off state of its main control switch. Therefore, the supply is a time-variant, nonlinear system. To analyze and design the compensation with conventional linear control methods, an averaged, small signal linear model is developed by applying linearization techniques on the SMPS circuit around its steady state operating point.

Figure 4. A Buck Step-Down DC/DC Converter and Its Two Operating Modes within One Switching Period TS.

#### Modeling Step 1: Changing to a Time-Invariant System by Averaging over TS



All the SMPS power topologies, including buck, boost or buck/boost converters, have a typical 3-terminal PWM switching cell, which includes an active control switch Q and passive switch (diode) D. To improve efficiency, the diode D can be replaced by a synchronous FET, which is still a passive switch. The active terminal “a” is the active switch terminal. The passive terminal “p” is the passive switch terminal. In a converter, the terminals a and p are always connected to a voltage source, such as VIN and ground in the buck converter. The common terminal “c” is connected to a current source, which is the inductor in the buck converter.

To change the time-variant SMPS into a time-invariant system, the 3-terminalPWMcell average modeling method can be applied by changing the active switch Q to an averaged current source and the passive switch (diode) D to an averaged voltage source. The averaged switch Q current equals d • iL and the averaged switch D voltage equals d • vap, as shown in Figure 5. The averaging is applied over a switching period TS. Since the current and voltage sources are the products of two variables, the system is still a nonlinear system.

Figure 5. Modeling Step 1: Changing 3-Terminal PWM Switching Cell to Averaged Current and Voltage Sources.

#### Modeling Step 2: Linear Small Signal AC Modeling



The next step is to expand the product of variables to get the linear AC small signal model. For example, a variable x = X + xˆ, where X is the DC steady state operating point and xˆ is the AC small signal variation around X. Therefore, the product of two variables x • y can be rewritten as:

Figure 6. Expand the Product of Two Variables for Linear Small Signal AC Part and DC Operating Point.

Figure 6 shows that the linear small signal AC part can be separated from the DC operating point (OP) part. And the product of two AC small signal variations ( xˆ • yˆ ) can be ignored, since it is an even smaller value variable. Following this concept, the averaged PWM switching cell can be rewritten as shown in Figure 7.

Figure 7. Modeling Step 2: AC Small Signal Modeling by Expanding the Products of Variables.

By applying this two-step modeling technique to a buck converter, as shown in Figure 8, the buck converter power stage can be modeled as simple voltage source, dˆ • VIN, followed by an L/C 2nd-order filter network.

Based on the linear circuit in Figure 8, since the control signal is the duty cycle d and the output signal is vOUT, the buck converter can be described by the duty-to-output transfer function Gdv(s) in the frequency domain:

where,

Figure 8. Changing a Buck Converter into an Averaged, AC Small Signal Linear Circuit.

Function Gdv(s) shows that the buck converter power-stage is a 2nd-order system with two poles and one zero in the frequency domain. The zero sZ\_ESR is generated by the output capacitor C and its ESR rC. The resonant double poles ϖO are generated by the output filter inductor L and capacitor C.

Since the poles and zero frequencies are functions of the output capacitor and its ESR, the bode plots of function Gdv(s) varies with different choices of supply output capacitor, as shown in Figure 9. The small signal behavior of the buck converter power stage highly depends on the choice of output capacitors. If the supply has small output capacitance or very low-ESR output capacitors, the ESR zero frequency can be much higher than the resonant pole frequency. The power stage phase delay can be close to –180 degrees. As a result, it can be difficult to compensate the loop when the negative voltage feedback loop is closed.

Figure 9. COUT Capacitor Variation Causes Significant Power Stage Gdv(s) Phase Variation.

#### Small Signal Model of the Boost Step-Up Converter



Using the same 3-terminal PWM switching cell average small signal modeling method, the boost step-upconverter can be modeled too. Figure 10 shows how to model and convert the boost converter to its linear AC small signal model circuit.

Figure 10. AC Small Signal Modeling Circuit of a Boost Step-Up Converter.

The boost power stage transfer function Gdv(s) can be derived in Equation (5). It is also a 2nd-order system with L/C resonance. Different from the buck converter, the boost converter has a right-half-plane zero (RHPZ) in addition to the COUT ESR zero. The RHPZ causes increased gain but reduced (negative) phase. Equation 6 also shows that the RHPZ varies with duty cycle and load resistance. Since the duty-cycle is a function of VIN, the boost power stage transfer function Gdv(s) varies with VIN and load current. At low VIN and heavy load IOUT\_MAX, the RHPZ is at its lowest frequency and causes significant phase lag. This makes it difficult to design a high-bandwidth boost converter. As a general design rule, to ensure loop stability, people design the boost converter bandwidth at less than 1/10 of its lowest RHPZ frequency. Several other topologies, such as the positive-to-negative buck/boost, flyback (isolated buck/boost), SEPIC and CUK converters, all have an undesirable RHPZ and cannot be designed for high bandwidth, fast transient solutions.

Figure 11. Boost Converter Power Stage Small Signal Duty-To-VO Transfer Function Varies with VIN and Load.

### Close The Feedback Loop with Voltage Mode Control

The output voltage can be regulated by a closed feedback loop system. For example in Figure 12, when the output voltage VOUT increases, the feedback voltage VFBincreases and the output of the negative feedback error amplifier decreases, so the duty cycle d decreases. As a result, VOUT is pulled back to make VFB = VREF. The compensation network of the error op amp can be a Type I, Type II or Type III feedback amplifier network. There is only one control loop to regulate the VOUT. This control scheme is referred to as voltage mode control. Linear Technology’s [LTC3861](/en/products/ltc3861.html) and [LTC3882](/en/products/ltc3882.html) are typical voltage mode buck controllers.

Figure 12. Voltage Mode Buck Converter Diagram with Closed Voltage Feedback Loop.

To optimize a voltage mode PWM converter, as shown in Figure 13, a complicated Type III compensation network is usually needed to design a fast loop with sufficient phase margin. As shown in Equation 7 and Figure 14, this compensation network has 3 poles and 2 zeros in the frequency domain: the low frequency integration pole (1/s) provides high DC gain to minimize DC regulation error, the double-zeros are placed around the system resonant frequency f0 to compensate the –180° phase delay caused by power stage L and C, the 1st high frequency pole is placed to cancel COUT ESR zero at fESR, and the 2nd high frequency pole is placed after the desired bandwidth fC to attenuate switching noise in the feedback loop. The Type III compensation is quite complicated, since it requires six R/C values. It is a time consuming task to find the optimum combination of these values.

Figure 13. A Type III Feedback Compensation Network for a Voltage Mode Converter.

Where:

Figure 14. Type III Compensation A(s) Provides 3 Poles and 2 Zeros to Achieve Optimum Total Loop Gain TV(s).

To simplify and automate the switching mode supply design, the LTpowerCAD design tool has been developed. This tool makes loop compensation design a much simpler task. LTpowerCAD is a free-download design tool available at [www.analog.com/LTpowerCAD](/en/lp/ltpowercad.html). It helps users to select a power solution, design power stage components, and optimize supply efficiency and loop compensation. As shown in the Figure 15 example, for a given Linear Technology® voltage mode controller such as the LTC3861, its loop parameters are modeled in the design tool. For a given power stage, users can place the pole and zero locations (frequencies), then follow the program guide to put in real R/C values and check the overall loop gain and load transient performance in real time. After that, the design can also be exported to an LTspice simulation circuit for a real time simulation.

Figure 15. LTpowerCAD Design Tool Eases the Type III Loop Design for Voltage Mode Converters (Free-download from www.analog.com/LTpowerCAD).

### Adding a Current Loop for Current Mode Control

The single loop voltage mode control has some limitations. It requires a fairly complicated Type III compensation network. The loop performance can vary significantly with output capacitor parameters and parasitics, especially the capacitor ESR and PCB trace impedance. A reliable supply also requires fast overcurrent protection, which requires a fast current sensing method and fast protection comparator. For high current solutions which require paralleling of many phases, an additional current sharing network/ loop is required.

Adding an inner current sensing path and feedback loop to the voltage-mode converter makes it a current mode controlled converter. Figures 16 and 17 show the typical peak current-mode buck converter and how it works. The internal clock turns on the topside control FET. After that, as soon as the sensed peak inductor current signal reaches the amplifier ITH pin voltage VC, the top FET is turned off. Conceptually, the current loop makes the inductor a controlled current source. Therefore, the power stage with closed current loop becomes a 1st-order system, instead of a 2nd-order system with L/C resonance. As a result, the phase lag caused by the power stage poles decreases from 180 degrees to about 90 degrees. Less phase delay makes it much easier to compensate the outer voltage loop. This also makes the power supply less sensitive to output capacitor or inductance variation, as shown in Figure 18.

Figure 16. Block Diagram of Current-Mode Converter with an Inner Current Loop and Outer Voltage Feedback Loop.

Figure 17. Peak Current Mode Control Signal Waveforms.

Figure 18. New Power Stage Transfer Function GCV(s) with Closed Current Loop.

The inductor current signal can be sensed directly with an additional RSENSE, or indirectly via the inductor winding DCR or FET RDS(ON). All provide several other important benefits from current mode control. As shown in Figure 17, since the inductor current is sensed and limited by the amplifier output voltage in a cycle-by-cycle fashion, the system has a more accurate and faster current limit under overload or inductor current saturation. The inrush inductor current is also tightly controlled during power-up or input voltage transients. When multiple converters/phases are paralleled, with current mode control, it is very easy to share current among supplies by tying the amplifier ITH pins together to implement a reliable PolyPhase design. Typical current mode controllers include Linear Technology’s [LTC3851A](/en/products/ltc3851a.html), LTC3833 and [LTC3855](/en/products/ltc3855.html), etc.



#### Peak vs. Valley Current Mode Control Methods



The current mode control method shown in Figures 16 and 17 is peak inductor current mode control. The converter operates with a fixed switching frequency fSW, making it easy for clock synchronization and phase interleaving, especially for paralleled converters. However, if the load step-up transient occurs just after the control FET gate is turned off, the converter has to wait the FET off-time TOFF until the next clock cycle to respond to the transient. This TOFF delay is usually not a problem, but it matters for a really fast transient system. Besides, the control FET minimum on-time (TON\_min) cannot be really small since the current comparator needs noise blanking time to avoid false triggering. This limits the maximum switching frequency fSW for high VIN/VOUT step-down ratio applications. In addition, peak current mode control also requires certain slope compensation to keep the current loop stable when the duty-cycle is over 50%. This is not a problem for Linear Technology’s controllers which usually have built-in adaptive slope compensation to ensure current loop stability over the full duty-cycle range. The LTC3851A and LTC3855 are typical peak current mode controllers.

Valley current mode controllers generate a controlled FET on-time and wait till the inductor valley current reaches its valley limit (VITH) to turn on the control FET again. Therefore, the supply can respond to load step-up transients during the control FET TOFF. Besides, since the on-time is fixed, the control FET TON\_min can be smaller than with peak current mode control to allow higher fSW for high stepdown ratio applications. Valley current mode control also does not need additional slope compensation for current loop stability. However, since the switching period TS is allowed to vary, the switching node waveform may look more jittery on the scope with valley current mode control. The LTC3833 and LTC3838 are typical valley current mode controllers.

### Modeling New Power Stage with Closed Current Loop

Figure 19 shows a simplified 1st order model of the buck converter power stage with inner current loop by just treating the inductor as a current source controlled by amplifier ITH pin voltage υC. A similar method can be used for other topologies with inductor current mode control. How good is this simple model? Figure 20 shows the comparison of transfer function GCV(s) = vOUT/vC between the 1st order model and a more complicated but accurate model. It is for a current mode buck converter running at 500kHz switching frequency. In this example, the 1st order model is accurate up to 10kHz, ~1/50 of the switching frequency fSW. After that, the phase plot of the 1st order model is no longer accurate. So this simplified model is only good for a design with low bandwidth.

Figure 19. A Simple, 1st Order Model for a Current Mode Buck Converter.

Figure 20. GCV(s) Comparison Between the 1st Order Model and Accurate Model for a Current Mode Buck.

In fact, it is quite complicated to develop an accurate small signal model for current mode converters for the full frequency range. R. Ridley’s current mode model [3] is the most popular one used by the power supply industry for both peak current mode and valley current mode controls. Most recently, Jian Li developed a more intuitive circuit model [4] for current mode control, which can also be used for other current mode control methods. To make it easy, the LTpowerCAD design tool implements these accurate models, so even an inexperienced user can easily design a current mode power supply, without much knowledge of Ridley or Jian Li’s models.

### Loop Compensation Design of a Current Mode Converter

In Figures 16 and 21, the power stage Gcv(s) with closed current loop is determined by the selection of power stage components, which are mainly decided by the DC specifications/performances of the power supply. The outer voltage loop gain T(s) = GCV(s) • A(s) • KREF(s) is therefore determined by the voltage feedback stage Kref(s) and compensation stage A(s). The designs of these two stages will largely decide the supply stability and transient response.

Figure 21. Control Block Diagram for Feedback Loop Design.

In general, the performance of the closed voltage loop T(s) is evaluated by two important values: the loop bandwidth and the loop stability margin. The loop bandwidth is quantified by the crossover frequency fC, at which the loop gain T(s) equals one (0dB). The loop stability margin is typically quantified by the phase margin or gain margin. The loop phase margin φm is defined as the difference between the overall T(s) phase delay and –180° at the crossover frequency. A 45-degree or 60-degree minimum phase margin is usually needed to ensure stability. For current mode control, to attenuate switching noise in the current loop, the loop gain margin is defined as the attenuation at ½ • fSW. In general, a minimum 8dB attenuation (–8dB loop gain) at ½ • fSW is desired.



#### Select Desired Voltage-Loop Crossover Frequency fC



Higher bandwidth helps obtain fast transient response. However, increasing the bandwidth usually reduces the stability margin and makes the control loop more sensitive to switching noise. An optimum design usually achieves a good trade-off between the bandwidth (transient response) and stability margin. In fact, current mode control also introduces a pair of double-poles ϖn by the sampling effect of the current signal at 1/2 • fSW [3]. These double poles introduce an undesirable phase delay around ½ • fSW. In general, to obtain sufficient phase margin and PCB noise attenuation, the crossover frequency is selected to be less than 1/10–1/6 of the phase switching frequency fSW.

#### Design of the Feedback Divider Network Kref(s) with R1, R2, C1 and C2



In Figure 16, the DC gain KREF of Kref(s) is the ratio between the internal reference voltage VREF and the desired DC output voltage Vo. Resistors R1 and R2 are used to set the desired output DC voltage.

where,

The optional capacitor C2 can be added to improve the dynamic response of the feedback loop. Conceptually, at high frequency, C2 provides a low impedance feed-forward path for the output voltage AC signal and therefore, speeds up transient responses. But C2 may also bring undesirable switching noise into the control loop. Therefore, an optional C1 filter capacitor may be added to attenuate the switching noise. As shown in Equation 11, the overall resistor divider transfer function KREF(s) with C1 and C2 has one zero and one pole. Figure 22 shows the bode plot of KREF(s). By designing fz\_ref < fp\_ref, C1 and C2 together with R1 and R2 introduce a phase boost in a frequency band centered at fCENTER, which is given in equation (14). If fCENTER is placed at the targeted crossover frequency fC, Kref(s) provides phase lead to the voltage loop and increases the phase margin. On the other hand, Figure 22 also shows that C1 and C2 increase the divider gain at high frequency. This is undesirable because a gain increase at high frequency makes the control loop more sensitive to switching noise. The increase in high-frequency gain by C1 and C2 is given by Equation 15.

where:

and,

Figure 22. Transfer Function Bode Plot of Resistor Divider Gain KREF(s).

For a given C1 and C2, the increased phase ϕREF from the divider network can be calculated by Equation 16. Further, the maximum possible phase boost for a given output voltage is given by Equation 17, for C2 >> C1. As shown, the maximum phase boost ϕREF\_max is determined by the divider ratio KREF = VREF/VO. Since VREF is fixed for a given controller, higher phase boost can be achieved with higher output voltage VO.

The selections of ϕREF, C1 and C2 are a trade-off between desired phase boost and undesired high frequency gain increase. The overall loop gain needs to be checked later for optimized values.



#### Design Type II Compensation Network of Voltage Loop ITH Error Amplifier



The ITH compensation A(s) is most critical to the loop compensation design because it determines the DC gain, crossover frequency (bandwidth) and the phase/gain margins of the supply voltage loop. For a current source output, gm transconductance-type amplifier, its transfer function A(s) is given by Equation 18:

where, gm is the gain of the transconductance error amplifier. Zith(s) is the impedance of the compensation network at the amplifier output ITH pin.

From the control block diagram in Fig.21, the voltage loop regulation error can be quantified by:

Therefore, to minimize the DC regulation error, a large DC gain of A(s) is very desirable. To maximize the DC gain of A(s), a capacitor Cth is first placed at the amplifier output ITH pin to form an integrator. In this case, the A(s) transfer gain is:

Figure 23 shows the schematic diagram of A(s) and its Bode plot. As shown, capacitor Cth creates an integration term in A(s) with an infinitely high DC gain. Unfortunately, in addition to the original –180 degrees of negative feedback, Cth adds another –90 degrees phase lag. Including the –90 degree phase of the 1st-order system power stage GCV(s), the total voltage loop phase is close to –360 degrees at the crossover frequency fC and the loop is close to being unstable.

Figure 23. Step 1: Simple Capacitor Compensation Network A(s) and Its Bode Plot.

In reality, the output impedance of the current source gm amplifier is not an infinite value. In Figure 24, Ro is the internal output resistance of the gm amplifier ITH pin. Linear Technology controllers’ Ro is usually high, in the 500kΩ – 1MΩ range. Therefore, the single capacitor A(s) transfer function becomes Equation (21). It has a low frequency pole fpo determined by RO • Cth. So the DC gain of A(s) is actually gm • RO. As shown in Figure 24, A(s) still has –90 degree phase lag at the expected crossover frequency fC\_exp.

where,

Figure 24. One-Pole A(s) That Includes gm Amplifier Output Impedance RO.

To increase the phase at fC, a resistor Rth is added in series with Cth to create a zero, as shown in Equation 23 and Figure 25. The zero contributes up to +90 degree phase lead. As shown in Figure 25, if the zero sthz is placed before the crossover frequency fC, A(s)’s phase at fC can be significantly increased. As a result, it increases the phase margin of the voltage loop.

Figure 25 Step 2: Adding RTH Zero to Boost Phase — One-Pole, One-Zero Compensation A(s).

where,

Unfortunately, there is a penalty of adding the zero sthz—the gain of A(s) is significantly increased at high frequency beyond fC. So the switching noise is more likely to come into the control loop with less A(s) attenuation at the switching frequency. To compensate this gain increase and attenuate PCB noise, it is necessary to add another small ceramic capacitor Cthp from the ITH pin to IC signal ground, as shown in Figure 26. Typically, choose Cthp << Cth. In the PCB layout, filter capacitor Cthp should be placed as close to the ITH pin as possible. By adding Cthp, the final compensation transfer function A(s) is given in Equation 25 and Equation 26 and its Bode plot is shown in Figure 26. Cthp introduces a high-frequency pole sthp, which should be located between the crossover frequency fC and the switching frequency fS. Cthp reduces A(s) gain at fS, but may also decrease the phase at fC. The location of sthp is a trade-off between the phase margin and supply PCB noise immunity.

Figure 26. Step 3: Adding High Frequency Decoupling Cthp - Two-Pole, One-Zero Compensation A(S).

where,

Since the current mode power stage is a quasi-single-pole system, the two-pole and one-zero compensation network in Figure 26 is generally sufficient to provide the needed phase margin.

This two-pole, one-zero compensation network on the amplifier ITH pin is also called a Type II compensation network. In summary, there are two capacitors CTH and CTHP, and one resistor RTH. This R/C network together with the amplifier output resistance Ro, generates a typical transfer function shown in Figure 27, with one zero at fz1 and two poles at fpo and fp2.

Figure 27. Conceptual Plot of Type II Compensation Network Transfer Function.

#### Compensation R/C Values vs. Load Step Transient Response



The previous section explained the frequency domain behavior of the Type II compensation network. In a closed loop supply design, one important performance parameter is the supply’s output voltage undershoot (or overshoot) during a load step-up (or load step-down) transient, which is usually directly impacted by loop compensation design.

**1) CTH’s effects on a load step transient.** The CTH affects the location of low frequency pole fpo and zero fz1. As shown in Figure 28, a smaller CTH can increase the low to-mid frequency gain of transfer function A(s). As a result, it can reduce the load transient response settling time without much impact on the VOUT undershoot (or overshoot) amplitude. On the other hand, a smaller CTH means higher fz1 frequency. This may reduce the phase boost by fz1 at the targeted crossover frequency fC.

Figure 28. CTH’s Effects on Transfer Function and Load Transient.

**2) RTH’s effects on load step transient.** Figure 29 shows that the RTH affects the location of zero fz1 and pole fp2. More importantly, a larger RTH increases the A(s) gain between fz1 and fp2. As a result, a larger RTH directly increases the supply bandwidth fc and reduces the VOUT undershoot/overshoot at load transient. However, if RTH is too large, the supply bandwidth fc can be too high with insufficient phase margin.

Figure 29. RTH’s Effects on Transfer Function and Load Transient.

**3) CTHP’s effects on load step transient.** Figure 30 shows that CTHP affects the location of pole fp2. CTHP is used as a decoupling capacitor to reduce switching noise on the ITH pin to minimize switching jitter. If the supply bandwidth fc > fp2, CTHP does not impact load transient response much. If CTHP is overdesigned so that fp2 is close to fc, it can reduce the bandwidth and phase margin, resulting in increased transient undershoot/overshoot.

Figure 30. CTHP’s Effects on Transfer Function and Load Transient.

### Design a Current Mode Supply With the LTpowerCAD Design Tool

With the LTpowerCAD design tool, users can easily design and optimize loop compensation and load transient performance of Linear Technology’s current mode supplies. Many Linear products have been accurately modeled with their loop parameters. First, users need to design the power stage, in which they need to design the current sensing network and ensure a sufficient AC sensing signal to the IC. After that, on the loop design page, they can adjust the loop compensation R/C values by simply moving the sliding bars and observing the overall loop bandwidth, phase margin and corresponding load transient performance. For a buck converter, users usually need to design a bandwidth below 1/6 fSW, have at least 45 degrees (or 60 degrees) of phase margin and have at least 8dB total loop gain attenuation at ½ fSW. For a boost converter, because of the right-half-plane zero (RHPZ), users need to design the supply bandwidth below 1/10 of the worst case RHPZ frequency. The LTpowerCAD design file can be exported to LTspice for real-time simulation to check detailed supply dynamic performance, such as load transient, power-up/ down, overcurrent protection, etc.

Figure 31. LTpowerCAD Design Tool Eases Loop Compensation Design and Transient Optimization.

### Measure the Supply Loop Gain

The LTpowerCAD and LTspice programs are not intended to replace final bench loop gain measurement of the real power supply. It is always necessary to make a measurement before releasing the design for final production. Though the models of power supplies are theoretically correct, they cannot take full account of circuit parasitics and component nonlinearity, such as the ESR variations of output capacitors, the non linearity of inductors and capacitors, etc. Also, circuit PCB noise and limited measurement accuracy may also cause measurement errors. That’s why, sometimes, the theoretical model and measurement can diverge considerably. If this happens, a load transient test can be used to further confirm the loop stability.

Figure 32 shows the typical supply loop gain measurement setup of a non isolated power supply using a frequency analyzer system. To measure the loop gain, a 50Ω to 100Ω resistor is inserted into the voltage feedback loop and a 50mV isolated AC signal is applied on this resistor. Channel 2 is connected to the output voltage and Channel 1 is connected to the other side of this resistor. The loop gain is calculated as Ch2/Ch1 by the frequency analyzer system. Figure 33 shows the measured and LTpowerCAD calculated loop Bode plot of a typical LTC3851A current mode supply. They have good matching in the critical frequency range from 1kHz to 100kHz.

Figure 32. Test Setup of the Power Supply Loop Gain Measurement.

Figure 33. Measured and LTpowerCAD Modeled Loop Gain of a Current Mode Buck Converter.

### Other Reasons That Cause Instability

#### Operating Conditions:



If the supply switching or output voltage waveform looks unstable or jittery on the oscilloscope, first, users need to make sure the supply is operated in a steady state condition, without load or input voltage transients. For very small or very large duty cycle applications, if pulse-skipping operation happens, check whether the minimum on-time or off-time limitation has been reached. For supplies that require an external synchronization signal, make sure the signal is clean and within the linear range given by controller data sheet. Sometimes it is also necessary to adjust the phase-locked-loop (PLL) filter network.



#### Current Sensing Signal and Noise:



To minimize the sensing resistor power loss, in a current mode supply, the maximum current sensing voltage is typically very low. For example, LTC3851A may have 50mV maximum sensing voltage. It is possible for PCB noise to disturb the current sensing loop and cause an unstable switching behavior. To debug whether the problem is indeed a loop compensation problem, a large 0.1µF capacitor can be placed from ITH pin to IC ground. If the supply is still unstable with this capacitor, the next step is to review the design. In general, the inductor and current sensing network should be designed to have at least 10mV to 15mV peak-to-peak AC inductor current signal on the IC current sensing pin. Besides, the current sensing traces can be rerouted with a pair of twisted jumper wires to check if it solves the problem.

There are some important considerations for PCB layout [6]. In general, Kelvin sensing is usually required with a pair of closely routed current sensing traces back to SENSE+ and SENSE– pins. If a PCB via is used in the SENSE– net, make sure this via does not contact other VOUT planes. The filter capacitor across SENSE+ and SENSE– should be placed as close to the IC pins as possible with a direct trace connection. Sometimes, filter resistors are needed and these resistors must be close to the IC too.



#### Control Chip Component Placement and Layout:



Placement and layout of components around the control IC are also critical [6]. All the ceramic decoupling capacitors should be close to their pins, if possible. It is especially important for the ITH pin capacitor Cthp to be as close to the ITH and IC signal ground pins as possible. The control IC should have a separate signal ground (SGND) island from the power supply power ground (PGND). The switching nodes, such as SW, BOOST, TG and BG, should be kept away from sensitive small signal nodes, such as current sensing, feedback and ITH compensation traces.

### Summary

Loop compensation design is often viewed as a challenging task for switching mode power supplies. For applications with fast transient requirements, it is very important to design the supply with high bandwidth and sufficient stability margin. This is typically a time consuming process. This article explains the key concepts to help system engineers understand this task. The LTpowerCAD design tool can be used to make supply loop design and optimization a much simpler task.

## References

[1] J. Seago, “Opti-Loop Architecture Reduces Output Capacitance and Improves Transient Response,” Application Note 76, Linear Technology Corp., May 1999.

[2] V. Vorperian, “Simplified Analysis of PWM Converters Using the Model of the PWM Switch: Parts I and II,” IEEE Transactions on Aerospace and Electronic Systems, Mar. 1990, Vol. 26, No.2.

[3] R. B. Ridley, “An Accurate and Practical SmallSignal Model for Current-Mode Control,” [www.ridleyengineering.com](https://ridleyengineering.com/).

[4] J. Li, “Current-Mode Control: Modeling and its Digital Application,” Ph.D. Dissertation, Virginia Tech, Apr. 2009.

[5] LTpowerCADTM design tool and user guide at [www.analog.com/LTpowerCAD](/en/lp/ltpowercad.html).

[6] H. Zhang, “PCBLayoutConsiderationsforNon-Isolated Switching Power Supplies,” AN136, www.analog.com.

[7] H. Zhang, “Basic Concepts of Linear Regulator and Switching Mode Power Supplies,” AN140, [www.analog.com](/en/resources/app-notes/an-140.html).