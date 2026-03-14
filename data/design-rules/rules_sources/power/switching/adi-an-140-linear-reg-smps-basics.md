---
source: "ADI AN-140 -- Linear Reg & SMPS Basics"
url: "https://www.analog.com/en/resources/app-notes/an-140.html"
format: "HTML"
method: "readability"
extracted: 2026-02-16
chars: 42948
---

## Abstract

This article explains the basic concepts of linear regulators and switching mode power supplies (SMPS). It is aimed at system engineers who may not be very familiar with power supply designs and selection. The basic operating principles of linear regulators and SMPS are explained and the advantages and disadvantages of each solution are discussed. The buck step-down converter is used as an example to further explain the design considerations of a switching regulator.

### Introduction

Today’s designs require an increasing number of power rails and supply solutions in electronics systems, with loads ranging from a few mA for standby supplies to over 100A for ASIC voltage regulators. It is important to choose the appropriate solution for the targeted application and to meet specified performance requirements, such as high efficiency, tight printed circuit board (PCB) space, accurate output regulation, fast transient response, low solution cost, etc. Power management design is becoming a more frequent and challenging task for system designers, many of whom may not have strong power backgrounds.

A power converter generates output voltage and current for the load from a given input power source. It needs to meet the load voltage or current regulation requirement during steady-state and transient conditions. It also must protect the load and system in case of a component failure. Depending on the specific application, a designer can choose either a linear regulator (LR) or a switching mode power supply (SMPS) solution. To make the best choice of a solution, it is essential for designers to be familiar with the merits, drawbacks and design concerns of each approach.

This article focuses on nonisolated power supply applications and provides an introduction to their operation and design basics.

### Linear Regulators

#### How a Linear Regulator Works



Let’s start with a simple example. In an embedded system, a 12V bus rail is available from the front-end power supply. On the system board, a 3.3V voltage is needed to power an operational amplifier (op amp). The simplest approach to generate the 3.3V is to use a resistor divider from the 12V bus, as shown in Figure 1. Does it work well? The answer is usually no. The op amp’s VCC pin current may vary under different operating conditions. If a fixed resistor divider is used, the IC VCC voltage varies with load. Besides, the 12V bus input may not be well regulated. There may be many other loads in the same system sharing the 12V rail. Because of the bus impedance, the 12V bus voltage varies with the bus loading conditions. As a result, a resistor divider cannot provide a regulated 3.3V to the op amp to ensure its proper operation. Therefore, a dedicated voltage regulation loop is needed. As shown in Figure 2, the feedback loop needs to adjust the top resistor R1 value to dynamically regulate the 3.3V on VCC.



Figure 1. Resistor Divider Generates 3.3VDC from 12V Bus Input.



Figure 2. Feedback Loop Adjusts Series Resistor R1 Value to Regulate 3.3V.

This kind of variable resistor can be implemented with a linear regulator, as shown in Figure 3. A linear regulator operates a bipolar or field effect power transistor (FET) in its linear mode. So the transistor works as a variable resistor in series with the output load. To establish the feedback loop, conceptually, an error amplifier senses the DC output voltage via a sampling resistor network RA and RB, then compares the feedback voltage VFB with a reference voltage VREF. The error amplifier output voltage drives the base of the series power transistor via a current amplifier. When either the input VBUS voltage decreases or the load current increases, the VCC output voltage goes down. The feedback voltage VFB decreases as well. As a result, the feedback error amplifier and current amplifier generate more current into the base of the transistor Q1. This reduces the voltage drop VCE and hence brings back the VCC output voltage, so that VFB equals VREF. On the other hand, if the VCC output voltage goes up, in a similar way, the negative feedback circuit increases VCE to ensure the accurate regulation of the 3.3V output. In summary, any variation of VO is absorbed by the linear regulator transistor’s VCE voltage. So the output voltage VCC is always constant and well regulated.



Figure 3. A Linear Regulator Implements a Variable Resistor to Regulate Output Voltage.

#### Why Use Linear Regulators?



The linear regulator has been widely used by industry for a very long time. It was the basis for the power supply industry until switching mode power supplies became prevalent after the 1960s. Even today, linear regulators are still widely used in a wide range of applications.

In addition to their simplicity of use, linear regulators have other performance advantages. Power management suppliers have developed many integrated linear regulators. A typical integrated linear regulator needs only VIN, VOUT, FB and optional GND pins. Figure 4 shows a typical 3-pin linear regulator, the [LT1083](/en/products/lt1083.html), which was developed more than 20 years ago. It only needs an input capacitor, output capacitor and two feedback resistors to set the output voltage. Almost any electrical engineer can design a supply with these simple linear regulators.



Figure 4. Integrated Linear Regulator Example: 7.5A Linear Regulator with Only Three Pins.

#### One Drawback – A Linear Regulator Can Burn a Lot of Power



A major drawback of using linear regulators can be the excessive power dissipation of its series transistor Q1 operating in a linear mode. As explained previously, a linear regulator transistor is conceptually a variable resistor. Since all the load current must pass through the series transistor, its power dissipation is PLoss = (VIN – VO) • IO. In this case, the efficiency of a linear regulator can be quickly estimated by:

So in the Figure 1 example, when the input is 12V and output is 3.3V, the linear regulator efficiency is just 27.5%. In this case, 72.5% of the input power is just wasted and generates heat in the regulator. This means that the transistor must have the thermal capability to handle its power/heat dissipation at worst case at maximum VIN and full load. So the size of the linear regulator and its heat sink may be large, especially when VO is much less than VIN. Figure 5 shows that the maximum efficiency of the linear regulator is proportional to the VO/VIN ratio.



Figure 5. Maximum Linear Regulator Efficiency vs VO/VIN Ratio.

On the other hand, the linear regulator can be very efficient if VO is close to VIN. However, the linear regulator (LR) has another limitation, which is the minimum voltage difference between VIN and VO. The transistor in the LR must be operated in its linear mode. So it requires a certain minimum voltage drop across the collector to emitter of a bipolar transistor or drain to source of a FET. When VO is too close to VIN, the LR may be unable to regulate output voltage anymore. The linear regulators that can work with low headroom (VIN – VO) are called low dropout regulators (LDOs).

It is also clear that a linear regulator or an LDO can only provide step-down DC/DC conversion. In applications that require VO voltage to be higher than VIN voltage, or need negative VO voltage from a positive VIN voltage, linear regulators obviously do not work.

#### Linear Regulator with Current Sharing for High Power [8]



For applications that require more power, the regulator must be mounted separately on a heat sink to dissipate the heat. In all-surface-mount systems, this is not an option, so the limitation of power dissipation (1W for example) limits the output current. Unfortunately, it is not easy to directly parallel linear regulators to spread the generated heat.

Replacing the voltage reference shown in Figure 3 with a precision current source, allows the linear regulator to be directly paralleled to spread the current load and thus spread dissipated heat among the ICs. This makes it possible to use linear regulators in high output current, allsurface-mount applications, where only a limited amount of heat can be dissipated in any single spot on a board. The [LT3080](/en/products/lt3080.html) is the first adjustable linear regulator that can be used in parallel for higher current. As shown in Figure 6, it has a precision zero TC 10µA internal current source connected to the noninverting input of the operational amplifier. With an external single voltage setting resistor RSET, the linear regulator output voltage can be adjusted from 0V to (VIN – VDROPOUT).



Figure 6. Single Resistor Setting LDO LT3080 with a Precision Current Source Reference.

Figure 7 shows how easy it is to parallel LT3080s for current sharing. Simply tie the SET pins of the LT3080s together, the two regulators share the same reference voltage. Because the operational amplifiers are precisely trimmed, the offset voltage between the adjustment pin and the output is less than 2mV. In this case, only 10mΩ ballast resistance, which can be the sum of a small external resistor and PCB trace resistance, is needed to balance the load current with better than 80% equalized sharing. Need even more power? Even paralleling 5 to 10 devices is reasonable.



Figure 7. Paralleling of Two LT3080 Linear Regulators for Higher Output Current.

#### Applications Where Linear Regulators Are Preferable



There are many applications in which linear regulators or LDOs provide superior solutions to switching supplies, including:

1. Simple/low cost solutions. Linear regulator or LDO solutions are simple and easy to use, especially for low power applications with low output current where thermal stress is not critical. No external power inductor is required.
2. Low noise/low ripple applications. For noise-sensitive applications, such as communication and radio devices, minimizing the supply noise is very critical. Linear regulators have very low output voltage ripple because there are no elements switching on and off frequently and linear regulators can have very high bandwidth. So there is little EMI problem. Some special LDOs, such as Analog Devices [LT1761](/en/products/lt1761.html) LDO family, have as low as 20μVRMS noise voltage on the output. It is almost impossible for an SMPS to achieve this low noise level. An SMPS usually has mV of output ripple even with very low ESR capacitors.
3. Fast transient applications. The linear regulator feedback loop is usually internal, so no external compensation is required. Typically, linear regulators have wider control loop bandwidth and faster transient response than that of SMPS.
4. Low dropout applications. For applications where output voltage is close to the input voltage, LDOs may be more efficient than an SMPS. There are very low dropout LDOs (VLDO) such as Analog Devices [LTC1844](/en/products/ltc1844.html), [LT3020](/en/products/lt3020.html) and [LTC3025](/en/products/ltc3025.html) with from 20mV to 90mV dropout voltage and up to 150mA current. The minimum input voltage can be as low as 0.9V. Because there is no AC switching loss in an LR, the light load efficiency of an LR or an LDO is similar to its full load efficiency. An SMPS usually has lower light load efficiency because of its AC switching losses. In battery powered applications in which light load efficiency is also critical, an LDO can provide a better solution than an SMPS.

In summary, designers use linear regulators or LDOs because they are simple, low noise, low cost, easy to use and provide fast transient response. If VO is close to VIN, an LDO may be more efficient than an SMPS.

### Switching Mode Power Supply Basics

#### Why Use a Switching Mode Supply?



A quick answer is high efficiency. In an SMPS, the transistors are operated in switching mode instead of linear mode. This means that when the transistor is on and conducting current, the voltage drop across its power path is minimal. When the transistor is off and blocking high voltage, there is almost no current through its power path. So the semiconductor transistor is like an ideal switch. The power loss in the transistor is therefore minimized. High efficiency, low power dissipation and high power density (small size) are the main reasons for designers to use SMPS instead of linear regulators or LDOs, especially in high current applications. For example, nowadays a 12VIN, 3.3VOUT switching mode synchronous buck stepdown supply can usually achieve >90% efficiency vs less than 27.5% from a linear regulator. This means a power loss or size reduction of at least eight times.

The Most Popular Switching Supply—the Buck Converter

Figure 8 shows the simplest and most popular switching regulator, the buck DC/DC converter. It has two operating modes, depending on if the transistor Q1 is turned on or off. To simplify the discussion, all the power devices are assumed to be ideal. When switch (transistor) Q1 is turned on, the switching node voltage VSW = VIN and inductor L current is being charged up by (VIN – VO). Figure 8(a) shows the equivalent circuit in this inductor charging mode. When switch Q1 is turned off, inductor current goes through the freewheeling diode D1, as shown in Figure 8(b). The switching node voltage VSW = 0V and inductor L current is discharged by the VO load. Since the ideal inductor cannot have DC voltage in the steady state, the average output voltage VO can be given as:

where TON is the on-time interval within the switching period TS. If the ratio of TON/TS is defined as duty cycle D, the output voltage VO is:

When the filter inductor L and output capacitor CO values are sufficiently high, the output voltage VO is a DC voltage with only mV ripple. In this case, for a 12V input buck supply, conceptually, a 27.5% duty cycle provides a 3.3V output voltage.



Figure 8. Buck Converter Operating Modes and Typical Waveforms.

Other than the above averaging approach, there is another way to derive the duty cycle equation. The ideal inductor cannot have DC voltage in steady state. So it must maintain inductor volt-second balance within a switching period. According to the inductor voltage waveform in Figure 8, volt-second balance requires:

Equation (5) is the same as Equation (3). The same volt-second balance approach can be used for other DC/DC topologies to derive the duty cycle vs VIN and VO equations.

### Power Losses In A Buck Converter

#### DC Conduction Losses



With ideal components (zero voltage drop in the ON state and zero switching loss), an ideal buck converter is 100% efficient. In reality, power dissipation is always associated with every power component. There are two types of losses in an SMPS: DC conduction losses and AC switching losses.

The conduction losses of a buck converter primarily result from voltage drops across transistor Q1, diode D1 and inductor L when they conduct current. To simplify the discussion, the AC ripple of inductor current is neglected in the following conduction loss calculation. If a MOSFET is used as the power transistor, the conduction loss of the MOSFET equals IO2 • RDS(ON) • D, where RDS(ON) is the on-resistance of MOSFET Q1. The conduction power loss of the diode equals IO • VD • (1 – D), where VD is the forward voltage drop of the diode D1. The conduction loss of the inductor equals IO2 • RDCR, where RDCR is the copper resistance of the inductor winding. Therefore, the conduction loss of the buck converter is approximately:

For example, a 12V input, 3.3V/10AMAX output buck supply can use following components: MOSFET RDS(ON) = 10mΩ, inductor RDCR = 2 mΩ, diode forward voltage VD = 0.5V. Therefore, the conduction loss at full load is:

Considering only conduction loss, the converter efficiency is:

The above analysis shows that the freewheeling diode consumes 3.62W power loss, which is much higher than the conduction losses of the MOSFET Q1 and the inductor L. To further improve efficiency, diode D1 can be replaced with a MOSFET Q2, as shown in Figure 9. This converter is referred to as a synchronous buck converter. Q2’s gate requires signals complementary to the Q1 gate, i.e., Q2 is only on when Q1 is off. The conduction loss of the synchronous buck converter is:

If a 10mΩ RDS(ON) MOSFET is used for Q2 as well, the conduction loss and efficiency of the synchronous buck converter are:

The above example shows that the synchronous buck is more efficient than a conventional buck converter, especially for low output voltage applications where the duty cycle is small and the conduction time of the diode D1 is long.



Figure 9. Synchronous Buck Converter and Its Transistor Gate Signals.

#### AC Switching Losses



In addition to the DC conduction losses, there are other AC/switching related power losses due to the nonideal power components:

1. MOSFET switching losses. A real transistor requires time to be turned on or off. So there are voltage and current overlaps during the turn-on and turn-off transients, which generate AC switching losses. Figure 10 shows the typical switching waveforms of the MOSFET Q1 in the synchronous buck converter. The charging and discharging of the top FET Q1’s parasitic capacitor CGD with charge QGD determine most of the Q1 switching time and related losses. In the synchronous buck, the bottom FET Q2 switching loss is small, because Q2 is always turned on after its body diode conducts and is turned off before its body diode conducts, while the voltage drop across the body diode is low. However, the body diode reverse recovery charge of Q2 can also increase the switching loss of the top FET Q1 and can generate switching voltage ringing and EMI noise. Equation (12) shows that the control FET Q1 switching loss is proportional to the converter switching frequency fS. The accurate calculation of the energy losses EON and EOFF for Q1 is not simple but can be found from MOSFET vendors’ application notes.
2. Inductor core loss PSW\_CORE. A real inductor also has AC loss that is a function of switching frequency. Inductor AC loss is primarily from the magnetic core loss. In a high frequency SMPS, the core material may be powdered iron or ferrite. In general, powdered iron cores saturate softly but have high core loss, while ferrite material saturates more sharply but has less core loss. Ferrites are ceramic ferromagnetic materials that have a crystalline structure consisting of mixtures of iron oxide with either manganese or zinc oxide. Core losses are due mainly to magnetic hysteresis loss. The core or inductor manufacturer usually provide the core loss data for power supply designers to estimate the AC inductor loss.
3. Other AC related losses. Other AC related losses include the gate driver loss PSW\_GATE, which equals VDRV • QG • fS, and the dead time (when both top FET Q1 and bottom FET Q2 are off) body diode conduction loss, which is equal to (ΔTON + ΔTOFF) • VD(Q2) • fS. In summary, the switching-related loss includes:The calculation of switching related losses is usually not easy. The switching related losses are proportional to switching frequency fS. In the 12VIN, 3.3VO/10AMAX synchronous buck converter, the AC loss causes about 2% to 5% efficiency loss with 200kHz – 500kHz switching frequency. So the overall efficiency is about 93% at full load, much better than that of an LR or LDO supply. The heat or size reduction can be close to 10x.



Figure 10. Typical Switching Waveform and Losses in the Top FET Q1 in the Buck Converter.

### Design Considerations Of The Switching Power Components

#### Switching Frequency Optimization



In general, higher switching frequency means smaller size output filter components L and CO. As a result, the size and cost of the power supply can be reduced. Higher bandwidth can also improve load transient response. However, higher switching frequency also means higher AC-related power loss, which requires larger board space or a heat sink to limit the thermal stress. Currently, for ≥10A output current applications, most step-down supplies operate in the range of 100kHz to 1MHz ~ 2MHz. For < 10A load current, the switching frequency can be up to several MHz. The optimum frequency for each design is a result of careful trade-offs in size, cost, efficiency and other performance parameters.

#### Output Inductor Selection



In a synchronous buck converter, the inductor peak-topeak ripple current can be calculated as:

With a given switching frequency, a low inductance gives large ripple current and results in large output ripple voltage. Large ripple current also increases MOSFET RMS current and conduction losses. On the other hand, high inductance means large inductor size and possible high inductor DCR and conduction losses. In general, 10% ~ 60% peak-to-peak ripple current is chosen over the maximum DC current ratio when selecting an inductor. The inductor vendors usually specify the DCR, RMS (heating) current and saturation current ratings. It is important to design the maximum DC current and peak current of the inductor within the vendor’s maximum ratings.

#### Power MOSFET Selection



When selecting a MOSFET for a buck converter, first make sure its maximum VDS rating is higher than the supply VIN(MAX) with sufficient margin. However, do not select a FET with an excessively high voltage rating. For example, for a 16VIN(MAX) supply, a 25V or 30V rated FET is a good fit. A 60V rated FET can be excessive, because the FET on-resistance usually increases with rated voltage. Next, the FET’s on-resistance RDS(ON) and gate charge QG (or QGD) are two most critical parameters. There is usually a trade-off between the gate charge QG and on-resistance RDS(ON). In general, a FET with small silicon die size has low QG but high on-resistance RDS(ON), while a FET with a large silicon die has low RDS(ON) but large QG. In a buck converter, the top MOSFET Q1 takes both conduction loss and AC switching loss. A low QG FET is usually needed for Q1, especially in applications with low output voltage and small duty cycle. The lower side synchronous FET Q2 has small AC loss because it is usually turned on or off when its VDS voltage is near zero. In this case, low RDS(ON) is more important than QG for synchronous FET Q2. When a single FET cannot handle the total power, several MOSFETs can be used in parallel.

#### Input and Output Capacitor Selection



First, the capacitors should be selected with sufficient voltage derating.

The input capacitor of a buck converter has pulsating switching current with large ripple. Therefore, the input capacitor should be selected with sufficient RMS ripple current rating to ensure its lifetime. Aluminum electrolytic capacitors and low ESR ceramic capacitors are usually used in parallel at the input.

The output capacitor determines not only the output voltage ripple, but also the load transient performance. The output voltage ripple can be calculated by Equation (15). For high performance applications, both the ESR and total capacitance are important to minimize output ripple voltage and to optimize load transient response. Usually, low ESR tantalum, low ESR polymer capacitors and multilayer ceramic capacitors (MLCC) are good choices.

#### Close the Feedback Regulation Loop



There is another important design stage for a switching mode supply—closing the regulation loop with a negative feedback control scheme. This is usually a much more challenging task than using an LR or LDO. It requires good understanding of loop behavior and compensation design to optimize dynamic performance with a stable loop.

#### Small Signal Model of the Buck Converter



As explained above, a switching converter changes its operation mode as a function of the switch ON or OFF state. It is a discrete and nonlinear system. To analyze the feedback loop with the linear control method, linear small signal modeling is needed [1][3]. Because of the output L-C filter, the linear small signal transfer function of duty cycle D to output VO is actually a second-order system with two poles and one zero, as shown in Equation (16). There are double poles located at the resonant frequency of the output inductor and capacitor. There is a zero determined by the output capacitance and the capacitor ESR.

#### Voltage Mode Control vs Current Mode Control



The output voltage can be regulated by a closed loop system shown in Figure 11. For example, when the output voltage increases, the feedback voltage VFB increases and the output of the negative feedback error amplifier decreases. So the duty cycle decreases. As a result, the output voltage is pulled back to make VFB = VREF. The compensation network of the error op amp can be a type I, type II or type III feedback amplifier network [3][4]. There is only one control loop to regulate the output. This scheme is referred to as voltage mode control. Analog Devices LTC3775 and LTC3861 are typical voltage mode buck controllers.



Figure 11. Block Diagram of a Voltage Mode-Controlled Buck Converter.

Figure 12 shows a 5V to 26V input, 1.2V/15A output synchronous buck supply using the [LTC3775](/en/products/ltc3775.html) voltage mode buck controller. Due to the LTC3775’s leading-edge PWM modulation architecture and very low (30ns) minimum on-time, the supply operates well for applications that converts a high voltage automotive or industrial power supply down to the 1.2V low voltage required by today’s microprocessors and programmable logic chips. High power applications require multiphase buck converters with current sharing. With voltage mode control, an additional current sharing loop is required to balance current among parallel buck channels. A typical current sharing method for voltage mode control is the masterslave method. The [LTC3861](/en/products/ltc3861.html) is such a PolyPhase® voltage mode controller. Its very low, ±1.25mV, current sense offset makes current sharing between paralleled phases very accurate to balance the thermal stress. [10]



Figure 12. The LTC3775 Voltage Mode Synchronous Buck Supply Offers a High Step-Down Ratio.

Current mode control uses two feedback loops: an outer voltage loop similar to the control loop of voltage mode-controlled converters, and an inner current loop that feeds back the current signal into the control loop. Figure 13 shows the conceptual block diagram of a peak current mode control buck converter that directly senses the output inductor current. With current mode control, the inductor current is determined by the error op amp output voltage. The inductor becomes a current source. Therefore, the transfer function from op amp output, VC, to supply output voltage VO becomes a single pole system. This makes loop compensation much easier. The control loop compensation has less dependency on the output capacitor ESR zero, so it is possible to use all ceramic output capacitors.



Figure 13. Block Diagram of a Current Mode-Controlled Buck Converter.

There are many other benefits from current mode control. As shown in Figure 13, since the peak inductor current is limited by the op amp VC in a cycle-by-cycle fashion, the current mode-controlled system provides a more accurate and faster current limit under overload conditions. The in-rush inductor current is well controlled during start-up, too. Also, the inductor current does not change quickly when the input voltage changes, so the supply has good line transient performance. When multiple converters are paralleled, with current mode control, it is also very easy to share current among supplies, which is important for reliable high current applications using PolyPhase buck converters. In general, a current mode-controlled converter is more reliable than a voltage mode-controlled converter.

The current mode control scheme solution needs to sense the current precisely. The current sensing signal is usually a small signal at a level of tens of millivolts that is sensitive to switching noise. Therefore, proper and careful PCB layout is needed. The current loop can be closed by sensing the inductor current through a sensing resistor, the inductor DCR voltage drop, or the MOSFET conduction voltage drop. Typical current mode controllers include Analog Devices [LTC3851A](/en/products/ltc3851a.html), [LTC3855](/en/products/ltc3855.html), [LTC3774](/en/products/ltc3774.html) and [LTC3875](/en/products/ltc3875.html).

#### Constant Frequency vs Constant On-Time Control



Typical voltage mode and current mode schemes in the Voltage Mode Control vs Current Mode Control section have constant switching frequency generated by controller internal clocks. These constant switching frequency controllers can be easily synchronized, an important feature for high current, PolyPhase buck controllers. However, if the load step-up transient occurs just after the control FET Q1 gate is turned off, the converter must wait the entire Q1 off-time until the next cycle to respond to the transient. In applications with small duty cycles, the worst case delay is close to one switching cycle.

In such low duty cycle applications, constant on-time valley current mode control has shorter latency to respond to load step-up transients. In steady state operation, the switching frequency of constant on-time buck converters is nearly fixed. In the event of a transient, the switching frequency can vary quickly to speed up the transient response. As a result, the supply has improved transient performance and output capacitance and its related cost can be reduced.

However, with constant on-time control, the switching frequency may vary with line or load. The [LTC3833](/en/products/ltc3833.html) is a valley current mode buck controller with a more sophisticated controlled-on-time architecture—a variant of the constant on-time control architecture with the distinction that the on-time is controlled so that the switching frequency remains constant over steady stage conditions under line and load. With this architecture, the LTC3833 controller has 20ns minimum on-time and allows step-down applications from up to 38VIN to 0.6VO. The controller can be synchronized to an external clock in the 200kHz to 2MHz frequency range. Figure 14 shows a typical LTC3833 supply with 4.5V to 14V input and 1.5V/20A output. [11] Figure 15 shows that the supply can respond quickly to sudden, high slew rate load transients. During the load step-up transient, the switching frequency increases to provide faster transient response. During the load stepdown transient, the duty-cycle drops to zero. Therefore only the output inductor limits the current slew rate. In addition to the LTC3833, for multiple outputs or PolyPhase applications, the [LTC3838](/en/products/ltc3838.html) and [LTC3839](/en/products/ltc3839.html) controllers provide fast transient, multiphase solutions.



Figure 14. Fast, Controlled-On-Time Current Mode Supply Using the LTC3833.



Figure 15. LTC3833 Supply Offers Fast Response During Rapid Load Step Transients.

#### Loop Bandwidth and Stability



A well designed SMPS is quiet, both electrically and acoustically. This is not the case with an undercompensated system, which tends to be unstable. Typical symptoms of an undercompensated power supply include: audible noise from the magnetic components or ceramic capacitors, jitter in the switching waveforms, oscillation of output voltage, and so on. An overcompensated system can be very stable and quiet, but at the cost of a slow transient response. Such a system has a loop crossover frequency at very low frequencies, typically below 10kHz. Slow transient response designs require excessive output capacitance to meet transient regulation requirements, increasing the overall supply cost and size. An optimum loop compensation design is stable and quiet, but is not overcompensated, so it also has a fast response to minimize output capacitance. Analog Devices AN149 article explains concepts and methods for power circuit modeling and loop designs in details [3]. Small signal modeling and loop compensation design can be difficult for inexperienced power supply designers. Analog Devices LTpowerCAD™ design tool handles the complicated equations and makes power supply design especially loop compensation a much simpler task [5] [6]. The LTspice® simulation tool integrates all of Analog Devices part models and provides additional time domain simulations to optimize the design. However, bench test/verification of loop stability and transient performance is usually necessary in the prototype stage.

In general, the performance of the closed voltage regulation loop is evaluated by two important values: the loop bandwidth and the loop stability margin. The loop bandwidth is quantified by the crossover frequency fC, at which the loop gain T(s) equals one (0dB). The loop stability margin is typically quantified by the phase margin or gain margin. The loop phase margin Φm is defined as the difference between the overall T(s) phase delay and –180° at the crossover frequency. The gain margin is defined by the difference between T(s) gain and 0dB at the frequency where overall T(s) phase equals –180°. For a buck converter, typically 45 degree phase margin and 10dB gain margin is considered sufficient. Figure 16 shows a typical Bode plot of loop gain for a current mode [LTC3829](/en/products/ltc3829.html) 12VIN to 1VO/60A 3-phase buck converter. In this example, the crossover frequency is 45kHz and the phase margin is 64 degrees. The gain margin is close to 20dB.



Figure 16. LTpowerCAD Design Tool Provides an Easy Way to Optimize the Loop Compensation and Load Transient Response (3-Phase, Single-Output LTC3829 Buck Converter Example).

#### PolyPhase Buck Converter for High Current Applications



As data processing systems become faster and larger, their processor and memory units demand more current at ever decreasing voltages. At these high currents, the demands on power supplies are multiplied. In recent years, PolyPhase (multiphase) synchronous buck converters have been widely used for high current, low voltage power supply solutions, due to their high efficiency and even thermal distribution. Besides, with interleaved multiple buck converter phases, the ripple current on both input and output sides can be significantly reduced, resulting in reduction of input and output capacitors and related board space and cost.

In PolyPhase buck converters, precise current sensing and sharing become extremely important. Good current sharing ensures even thermal distribution and high system reliability. Because of their inherent current sharing capability in steady state and during transients, current mode-controlled bucks are usually preferred. Analog Devices [LTC3856](/en/products/ltc3856.html) and LTC3829 are typical PolyPhase buck controllers with precise current sensing and sharing. Multiple controllers can be connected in a daisy chain fashion for 2-, 3-, 4-, 6- and 12-phase systems with output current from 20A to over 200A.



Figure 17. A 3-Phase, Single VO High Current Buck Converter Using the LTC3829.

#### Other Requirements of a High Performance Controller



Many other important features are required of a high performance buck controller. Soft-start is usually needed to control the inrush current during start-up. Overcurrent limit and short-circuit latchoff can protect the supply when the output is overloaded or shorted. Overvoltage protection safeguards the expensive load devices in the system. To minimize system EMI noise, sometimes the controller must be synchronized to an external clock signal. For low voltage, high current applications, remote differential voltage sensing compensates for the PCB resistance voltage drop and accurately regulates output voltage at the remote load. In a complicated system with many output voltage rails, sequencing and tracking among different voltage rails is also necessary.

#### PCB Layout



Component selection and schematic design is only half of the supply design process. Proper PCB layout of a switching supply design is always critical. In fact, its importance can not be overstated. Good layout design optimizes supply efficiency, alleviates thermal stress, and most importantly, minimizes noise and interactions among traces and components. To achieve this, it is important for the designer to understand the current conduction paths and signal flows in the switching power supply. It usually requires significant effort to gain the necessary experience. See Analog Devices Application Note 136 and 139 for detailed discussions. [7][9]

#### Selection of Various Solutions – Discrete, Monolithic and Integrated Supplies



At the integration level, system engineers can decide whether to choose a discrete, monolithic or fully integrated power module solution.Figure 18 shows examples of discrete and power module solutions for typical point-of-load supply applications. The discrete solution uses a controller IC, external MOSFETs and passive components to build the power supply on the system board. A major reason to choose a discrete solution is low component bill of materials (BOM) cost. However, this requires good power supply design skills and relatively long development time. A monolithic solution uses an IC with integrated power MOSFETs to further reduce the solution size and component count. It requires similar design skills and time. A fully integrated power module solution can significantly reduce design effort, development time, solution size and design risk, but usually with a higher component BOM cost.



Figure 18. Examples of (a) a Discrete 12VIN to 3.3V/10A LTC3778 Supply; (b) a Fully Integrated 16VIN, Dual 13A or Single 26A LTM4620 µModule® Step-Down Regulator.

#### Other Basic Nonisolated DC/DC SMPS Topologies



This application note uses buck converters as a simple example to demonstrate the design considerations of SMPS. However, there are at least five other basic nonisolated converter topologies (boost, buck/boost, Cuk, SEPIC and Zeta converters) and at least five basic isolated converter topologies (flyback, forward, push-pull, half-bridge and full-bridge) which are not covered in this application note. Each topology has unique properties that make it suited for specific applications. Figure 19 shows simplified schematics for the other nonisolated SMPS topologies.



Figure 19. Other Basic Nonisolated DC/DC Converter Topologies.

There are other nonisolated SMPS topologies which are combinations of the basic topologies. For example, Figure 20 shows a high efficiency, 4-switch synchronous buck/boost converter based on the [LTC3789](/en/products/ltc3789.html) current mode controller. It can operate with input voltages below, equal, or above the output voltage. For example, the input can be in the range of 5V to 36V, and the output can be a regulated 12V. This topology is a combination of a synchronous buck converter and a synchronous boost converter, sharing a single inductor. When VIN > VOUT, switches A and B operate as an active synchronous buck converter, while the switch C is always off and switch D is always on. When VIN < VOUT, switches C and D operate as an active synchronous boost converter, while switch A is always on and switch B is always off. When VIN is close to VOUT, all four switches operate actively. As a result, this converter can be very efficient, with up to 98% efficiency for a typical 12V output application. [12] The [LT8705](/en/products/lt8705.html) controller further extends the input voltage range up to 80V. To simplify the design and increase power density, the [LTM4605](/en/products/ltm4605.html)/[4607](/en/products/ltm4607.html)/[4609](/en/products/ltm4609.html) further integrate a complicated buck/boost converter into a high density, easy-to-use power module. [13] They can be easily paralleled with load sharing for high power applications.



Figure 20. High Efficiency 4-Switch Buck-Boost Converter Operates with Input Voltage Below, Equal or Above the Output Voltage.

### Summary

In summary, linear regulators are simple and easy to use. Since their series regulation transistors are operated in a linear mode, supply efficiency is usually low when output voltage is much lower than input voltage. In general, linear regulators (or LDOs) have low voltage ripple and fast transient response. On the other hand, SMPS operate the transistor as a switch, and therefore are usually much more efficient than linear regulators. However, the design and optimization of SMPS are more challenging and require more background and experience. Each solution has its own advantages and drawbacks for specific applications.

## References

[1] V. Vorperian, “Simplified Analysis of PWM Converters Using the Model of the PWM Switch: Parts I and II,” IEEE Transactions on Aerospace and Electronic Systems, Mar. 1990, Vol. 26, No.2.

[2] R. B. Ridley, B. H. Cho, F. C. Lee, “Analysis and Interpretation of Loop Gains of Multi-Loop-Controlled Switching Regulators,” IEEE Transactions on Power Electronics, pp. 489-498, Oct. 1988.

[3] H. Zhang, “Modeling and Loop Compensation Design of Switching Mode Power Supplies,” Linear Technology Application Note AN149, 2015.

[4] H. Dean Venable, “Optimum Feedback Amplifier Design for Control Systems,” Venable Technical Paper.

[5] H. Zhang, “Designing Power Supplies in Five Simple Steps with the LTpowerCAD Design Tool,” Linear Technology Application Note AN158, 2015.

[6] LTpowerCAD™ design tool at www.linear.com/LTpowerCAD.

[7] H. Zhang, “PCB Layout Considerations for NonIsolated Switching Power Supplies,” Application Note 136, Linear Technology Corp., 2012.

[8] R. Dobbkin, “Low Dropout Regulator Can be Directly Paralleled to Spread the Heat,” LT Journal of Analog Innovation, Oct. 2007.

[9] C. Kueck, “Power Supply Layout and EMI,” Linear Technology Application Note AN139, 2013.

[10] M. Subramanian, T. Nguyen and T. Phillips, “SubMilliohm DCR Current Sensing with Accurate Multiphase Current Sharing for High Current Power Supplies,” LT Journal, Jan. 2013.

[11] B. Abesingha, “Fast, Accurate Step-Down DC/DC Controller Converts 24V Directly to 1.8V at 2MHz,” LT Journal, Oct. 2011.

[12] T. Bjorklund, “High Efficiency 4-Switch Buck-Boost Controller Provides Accurate Output Current Limit,” Linear Technology Design Note 499.

[13] J. Sun, S. Young and H. Zhang, “µModule Regulator Fits a (Nearly) Complete Buck-Boost Solution in 15mm × 15mm × 2.8mm for 4.5V-36Vin to 0.8V-34V VOUT,” LT Journal, Mar. 2009.