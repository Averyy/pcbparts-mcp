---
source: "TI SNVA559C -- Switching Regulator Fundamentals"
url: "https://www.ti.com/lit/an/snva559c/snva559c.pdf"
format: "PDF 29pp"
method: "ti-html"
extracted: 2026-02-16
chars: 57668
---

## Switching regulator fundamentals

[Switching regulators](http://www.ti.com/power-management/non-isolated-dc-dc-switching-regulators/overview.html) are increasing in popularity because they offer the advantages of higher power conversion efficiency and increased design flexibility (multiple output voltages of different polarities can be generated from a single input voltage).

This paper will detail the operating principles of the four most commonly used switching converter types:

[Buck](http://www.ti.com/power-management/non-isolated-dc-dc-switching-regulators/step-down-buck/overview.html)used to reduce a DC voltage to a lower DC voltage.

[Boost](http://www.ti.com/power-management/non-isolated-dc-dc-switching-regulators/step-up-boost/overview.html)provides an output voltage that is higher than the input.

[Buck-Boost (invert)](http://www.ti.com/power-management/non-isolated-dc-dc-switching-regulators/buck-boost-inverting/overview.html)an output voltage that is generated opposite in polarity to the input.

[Flyback](http://www.ti.com/power-management/offline-isolated-dcdc-controllers-converters/flyback-controllers/overview.html)an output voltage that is less than or greater than the input can be generated, as well as multiple outputs.

Also, some multiple-transistor converter topologies will be presented:

Push-PullA two-transistor converter that is especially efficient at low input voltages.

[Half-Bridge](http://www.ti.com/power-management/gate-drivers/half-bridge-drivers/overview.html)A two-transistor converter used in many offline applications.

[Full-Bridge](http://www.ti.com/product/sm72295)A four-transistor converter (usually used in offline designs) that can generate the highest output power of all the types listed.

Application information will be provided along with circuit examples that illustrate some applications of Buck, Boost, and Flyback regulators.

### 1 Switching Fundamentals

Before beginning explanations of converter theory, some basic elements of power conversion will be presented:

#### 1.1 The Law of Inductance

If a voltage is forced across an inductor, a current will flow through that inductor (and this current will vary with time).

NOTE

The current flowing in an inductor will be time-varying even if the forcing voltage is constant.

It is equally correct to say that if a time-varying current is forced to flow in an inductor, a voltage across the inductor will result.

The fundamental law that defines the relationship between the voltage and current in an inductor is given by [Equation 1](#t4589915-5):

Equation 1. v = L (di/dt)

Two important characteristics of an inductor that follow directly from the law of inductance are:

1. A voltage across an inductor results only from a current that changes with time. A steady (DC) current flowing in an inductor causes no voltage across it (except for the tiny voltage drop across the copper used in the windings).
2. A current flowing in an inductor can not change value instantly (in zero time), as this would require infinite voltage to force it to happen. However, the faster the current is changed in an inductor, the larger the resulting voltage will be.

NOTE

Unlike the current flowing in the inductor, the voltage across it can change instantly (in zero time).

The principles of inductance are illustrated by the information contained in [Figure 1](#x9547).

Figure 1. Inductor Voltage/Current Relationship

The important parameter is the di/dt term, which is simply a measure of how the current changes with time. When the current is plotted versus time, the value of di/dt is defined as the slope of the current plot at any given point.

The graph on the left shows that current which is constant with time has a di/dt value of zero, and results in no voltage across the inductor.

The center graph shows that a current which is increasing with time has a positive di/dt value, resulting in a positive inductor voltage.

Current that decreases with time (shown in the right-hand graph) gives a negative value for di/dt and inductor voltage.

It is important to note that a linear current ramp in an inductor (either up or down) occurs only when it has a constant voltage across it.

#### 1.2 Transformer Operation

A transformer is a device that has two or more magnetically-coupled windings. The basic operation is shown in [Figure 2](#x9597).

Figure 2. Transformer Theory

The action of a transformer is such that a time-varying (AC) voltage or current is transformed to a higher or lower value, as set by the transformer turns ratio. The transformer does not add power, so it follows that the power (V X I) on either side must be constant. That is the reason that the winding with more turns has higher voltage but lower current, while the winding with less turns has lower voltage but higher current.

The dot on a transformer winding identifies its polarity with respect to another winding, and reversing the dot results in inverting the polarity.

**Example of Transformer Operation:**

An excellent example of how a transformer works can be found under the hood of your car, where a transformer is used to generate the 40 kV that fires your car's spark plugs (see [Figure 3](#x4017)).

Figure 3. Spark Firing Circuit

The *coil* used to generate the spark voltage is actually a transformer, with a very high secondary-to-primary turns ratio.

When the points first close, current starts to flow in the primary winding and eventually reaches the final value set by the 12-V battery and the current-limiting resistor. At this time, the current flow is a fixed DC value, which means no voltage is generated across either winding of the transformer.

When the points open, the current in the primary winding collapses very quickly, causing a large voltage to appear across this winding. This voltage on the primary is magnetically coupled to (and stepped up by) the secondary winding, generating a voltage of 30 kV to 40 kV on the secondary side.

As explained previously, the law of inductance says that it is not possible to instantly break the current flowing in an inductor (because an infinite voltage would be required to make it happen).

This principle is what causes the arcing across the contacts used in switches that are in circuits with highly inductive loads. When the switch just begins to open, the high voltage generated allows electrons to jump the air gap so that the current flow does not actually stop instantly. Placing a capacitor across the contacts helps to reduce this arcing effect.

In the automobile ignition, a capacitor is placed across the points to minimize damage due to arcing when the points *break* the current flowing in the low-voltage coil winding (in car manuals, this capacitor is referred to as a *condenser*).

#### 1.3 Pulse Width Modulation (PWM)

All of the switching converters that will be covered in this paper use a form of output voltage regulation known as pulse width modulation (PWM). Put simply, the feedback loop adjusts (corrects) the output voltage by changing the ON time of the switching element in the converter.

As an example of how PWM works, we will examine the result of applying a series of square wave pulses to an L-C filter (see [Figure 4](#x6752)).

Figure 4. Basic Principles of PWM

The series of square wave pulses is filtered and provides a DC output voltage that is equal to the peak pulse amplitude multiplied times the duty cycle (duty cycle is defined as the switch ON time divided by the total period). This relationship explains how the output voltage can be directly controlled by changing the ON time of the switch.

### 2 Switching Converter Topologies

The most commonly used [DC/DC](http://www.ti.com/lsds/ti/power-management/non-isolated-dc-dc-switching-regulator-overview.page) converter circuits will now be presented along with the basic principles of operation.

#### 2.1 Buck Regulator

The most commonly used switching converter is the [Buck](http://www.ti.com/lsds/ti/power-management/step-down-buck-overview.page), which is used to down-convert a DC voltage to a lower DC voltage of the same polarity. This is essential in systems that use distributed power rails (like 24 V to 48 V), which must be locally converted to 15 V, 12 V or 5 V with very little power loss.

The buck converter uses a transistor as a switch that alternately connects and disconnects the input voltage to an inductor (see [Figure 5](#x8629)).

Figure 5. Buck Regulator

The lower diagrams show the current flow paths (shown as the heavy lines) when the switch is on and off.

When the switch turns on, the input voltage is connected to the inductor. The difference between the input and output voltages is then forced across the inductor, causing current through the inductor to increase.

During the ON time, the inductor current flows into both the load and the output capacitor (the capacitor charges during this time).

When the switch is turned off, the input voltage applied to the inductor is removed. However, because the current in an inductor can not change instantly, the voltage across the inductor will adjust to hold the current constant.

The input end of the inductor is forced negative in voltage by the decreasing current, eventually reaching the point where the diode is turned on. The inductor current then flows through the load and back through the diode.

The capacitor discharges into the load during the OFF time, contributing to the total current being supplied to the load (the total load current during the switch OFF time is the sum of the inductor and capacitor current).

The shape of the current flowing in the inductor is similar to [Figure 6](#x2748).

Figure 6. Buck Regulator Inductor Current

As explained, the current through the inductor ramps up when the switch is on, and ramps down when the switch is off. The DC load current from the regulated output is the average value of the inductor current.

The peak-to-peak difference in the inductor current waveform is referred to as the inductor ripple current, and the inductor is typically selected large enough to keep this ripple current less than 20% to 30% of the rated DC current.

#### 2.2 Continuous vs Discontinuous Operation

In most Buck regulator applications, the inductor current never drops to zero during full-load operation (this is defined as continuous mode operation). Overall performance is usually better using continuous mode, and it allows maximum output power to be obtained from a given input voltage and switch current rating.

In applications where the maximum load current is fairly low, it can be advantageous to design for discontinuous mode operation. In these cases, operating in discontinuous mode can result in a smaller overall converter size (because a smaller inductor can be used).

Discontinuous mode operation at lower load current values is generally harmless, and even converters designed for continuous mode operation at full load will become discontinuous as the load current is decreased (usually causing no problems).

#### 2.3 Boost Regulator

The [Boost](http://www.ti.com/lsds/ti/power-management/step-up-boost-overview.page) regulator takes a DC input voltage and produces a DC output voltage that is higher in value than the input (but of the same polarity). The boost regulator is shown in [Figure 7](#x828), along with details showing the path of current flow during the switch ON and OFF time.

Figure 7. Boost Regulator

Whenever the switch is on, the input voltage is forced across the inductor which causes the current through it to increase (ramp up).

When the switch is off, the decreasing inductor current forces the *switch* end of the inductor to swing positive. This forward biases the diode, allowing the capacitor to charge up to a voltage that is higher than the input voltage.

During steady-state operation, the inductor current flows into both the output capacitor and the load during the switch OFF time. When the switch is on, the load current is supplied only by the capacitor.

#### 2.4 Output Current and Load Power

An important design consideration in the Boost regulator is that the output load current and the switch current are not equal, and the maximum available load current is always less than the current rating of the switch transistor.

It should be noted that the maximum total power available for conversion in any regulator is equal to the input voltage multiplied times the maximum average input current (which is less than the current rating of the switch transistor).

Becuase the output voltage of the Boost is higher than the input voltage, it follows that the output current must be lower than the input current.

#### 2.5 Buck-Boost (Inverting) Regulator

The [Buck-Boost or Inverting](http://www.ti.com/lsds/ti/power-management/buck-boost-inverting-or-split-rail-overview.page) regulator takes a DC input voltage and produces a DC output voltage that is opposite in polarity to the input. The negative output voltage can be either larger or smaller in magnitude than the input voltage.

The Inverting regulator is shown in [Figure 8](#x1473).

Figure 8. Buck-Boost (Inverting) Regulator

When the switch is on, the input voltage is forced across the inductor, causing an increasing current flow through it. During the ON time, the discharge of the output capacitor is the only source of load current.

This requires that the charge lost from the output capacitor during the on time be replenished during the OFF time.

When the switch turns off, the decreasing current flow in the inductor causes the voltage at the diode end to swing negative. This action turns on the diode, allowing the current in the inductor to supply both the output capacitor and the load.

As shown, the load current is supplied by inductor when the switch is off, and by the output capacitor when the switch is on.

#### 2.6 Flyback Regulator

The [Flyback](http://www.ti.com/lsds/ti/power-management/flyback-controller-products.page) is the most versatile of all the topologies, allowing the designer to create one or more output voltages, some of which may be opposite in polarity. Flyback converters have gained popularity in battery-powered systems, where a single voltage must be converted into the required system voltages (for example, +5 V, +12 V and –12 V) with very high power conversion efficiency. The basic single-output flyback converter is shown in [Figure 9](#x5416).

Figure 9. Single-Output Flyback Regulator

The most important feature of the Flyback regulator is the transformer phasing, as shown by the dots on the primary and secondary windings.

When the switch is on, the input voltage is forced across the transformer primary which causes an increasing flow of current through it.

Note that the polarity of the voltage on the primary is dot-negative (more negative at the dotted end), causing a voltage with the same polarity to appear at the transformer secondary (the magnitude of the secondary voltage is set by the transformer secondary-to-primary turns ratio).

The dot-negative voltage appearing across the secondary winding turns off the diode, preventing current flow in the secondary winding during the switch on time. During this time, the load current must be supplied by the output capacitor alone.

When the switch turns off, the decreasing current flow in the primary causes the voltage at the dot end to swing positive. At the same time, the primary voltage is reflected to the secondary with the same polarity. The dot-positive voltage occurring across the secondary winding turns on the diode, allowing current to flow into both the load and the output capacitor. The output capacitor charge lost to the load during the switch on time is replenished during the switch OFF time.

Flyback converters operate in either continuous mode (where the secondary current is always > 0) or discontinuous mode (where the secondary current falls to zero on each cycle).

#### 2.7 Generating Multiple Outputs

Another big advantage of a flyback is the capability of providing multiple outputs (see [Figure 10](#x7701)). In such applications, one of the outputs (usually the highest current) is selected to provide PWM feedback to the control loop, which means this output is directly regulated.

The other secondary winding(s) are indirectly regulated, as their pulse widths will follow the regulated winding. The load regulation on the unregulated secondaries is not great (typically 5% to 10%), but is adequate for many applications.

If tighter regulation is needed on the lower current secondaries, an LDO post-regulator is an excellent solution. The secondary voltage is set about 1 V above the desired output voltage, and the LDO provides excellent output regulation with very little loss of efficiency.

Figure 10. Typical Multiple-Output Flyback

#### 2.8 Push-Pull Converter

The Push-Pull converter uses two to transistors perform DC/DC conversion (see [Figure 11](#x2159)).

Figure 11. Push-Pull Converter

The converter operates by turning on each transistor on alternate cycles (the two transistors are never on at the same time). Transformer secondary current flows at the same time as primary current (when either of the switches is on).

For example, when transistor *A* is turned on, the input voltage is forced across the upper primary winding with dot-negative polarity. On the secondary side, a dot-negative voltage will appear across the winding which turns on the bottom diode. This allows current to flow into the inductor to supply both the output capacitor and the load.

When transistor *B* is on, the input voltage is forced across the lower primary winding with dot-positive polarity. The same voltage polarity on the secondary turns on the top diode, and current flows into the output capacitor and the load.

An important characteristic of a Push-Pull converter is that the switch transistors have to be able the stand off more than twice the input voltage: when one transistor is on (and the input voltage is forced across one primary winding) the same magnitude voltage is induced across the other primary winding, but it is *floating* on top of the input voltage. This puts the collector of the turned-off transistor at twice the input voltage with respect to ground.

The *double input voltage* rating requirement of the switch transistors means the Push-Pull converter is best suited for lower input voltage applications. It has been widely used in converters operating in 12-V and 24-V battery-powered systems.

Figure 12. Timing Diagram for Push-Pull Converter

[Figure 12](#x4782) shows a timing diagram which details the relationship of the input and output pulses.

It is important to note that frequency of the secondary side voltage pulses is twice the frequency of operation of the PWM controller driving the two transistors. For example, if the PWM control chip was set up to operate at 50 kHz on the primary side, the frequency of the secondary pulses would be 100 kHz.

The DC output voltage is given by [Equation 2](#t4589915-32):

Equation 2. VOUT = VPK × (TON / TPER)

The peak amplitude of the secondary pulses (VPK) is given by [Equation 3](#t4589915-33):

Equation 3. VPK = (VIN – VSWITCH) × (NS / NP) – VRECT

This highlights why the Push-Pull converter is well-suited for low voltage converters. The voltage forced across each primary winding (which provides the power for conversion) is the full input voltage minus only the saturation voltage of the switch.

If MOSFET power switches are used, the voltage drop across the switches can be made extremely small, resulting in very high utilization of the available input voltage.

Another advantage of the Push-Pull converter is that it can also generate multiple output voltages (by adding more secondary windings), some of which may be negative in polarity. This allows a power supply operated from a single battery to provide all of the voltages necessary for system operation.

A disadvantage of Push-Pull converters is that they require very good matching of the switch transistors to prevent unequal ON times, because this will result in saturation of the transformer core (and failure of the converter).

#### 2.9 Half-Bridge Converter

The [Half-Bridge](http://www.ti.com/lsds/ti/power-management/half-bridge-driver-products.page) is a two-transistor converter frequently used in high-power designs. It is well-suited for applications requiring load power in the range of 50 0W to 1500 W, and is almost always operated directly from the AC line.

Offline operation means that no large 60-Hz power transformer is used, eliminating the heaviest and costliest component of a typical transformer-powered supply. All of the transformers in the half-bridge used for power conversion operate at the switching frequency (typically 50 kHz or higher) which means they can be very small and efficient.

A very important advantage of the half-bridge is input-to-output isolation (the regulated DC output is electrically isolated from the AC line). But, this means that all of the PWM control circuitry must be referenced to the DC output ground.

The voltage to run the control circuits is usually generated from a DC rail that is powered by a small 60-Hz transformer feeding a three-terminal regulator. In some designs requiring extremely high efficiency, the switcher output takes over and provides internal power after the start-up period.

The switch transistor drive circuitry must be isolated from the transistors, requiring the use of base drive transformers. The added complexity of the base drive circuitry is a disadvantage of using the half-bridge design.

If a 230 VAC line voltage is rectified by a full-wave bridge and filtered by a capacitor, an unregulated DC voltage of about 300 V will be available for DC/DC conversion. If 115 VAC is used, a voltage doubler circuit is typically used to generate the 300-V rail.

Figure 13. Half-Bridge Converter

The basic half-bridge converter is shown in [Figure 13](#x2328). A capacitive divider is tied directly across the unregulated DC input voltage, providing a reference voltage of 1/2 VIN for one end of the transformer primary winding. The other end of the primary is actively driven up and down as the transistors alternately turn on and off.

The switch transistors force one-half of the input voltage across the primary winding during the switch on time, reversing polarity as the transistors alternate. The switching transistors are never on at the same time, or they would be destroyed (because they are tied directly across VIN). The timing diagram for the half-bridge converter is shown in [Figure 14](#x5093) (it is the same as the push-pull).

When the *A* transistor is on, a dot-positive voltage is forced across the primary winding and reflected on the secondary side (with the magnitude being set by the transformer turns ratio). The dot-positive secondary voltage turns on the upper rectifier diode, supplying current to both the output capacitor and the load.

When the *A* transistor turns off and the *B* transistor turns on, the polarity of the primary voltage is reversed. The secondary voltage polarity is also reversed, turning on the lower diode (which supplies current to the output capacitor and the load).

In a Half-Bridge converter, primary and secondary current flow in the transformer at the same time (when either transistor is on), supplying the load current and charging the output capacitor. The output capacitor discharges into the load only during the time when both transistors are off.

Figure 14. Timing Diagram for Half-Bridge Converter

It can be seen that the voltage pulses on the transformer secondary side (applied to the L-C filter) are occurring at twice the frequency of the PWM converter which supplies the drive pulses for the switching transistors.

The output voltage is again given by [Equation 4](#t4589915-34):

Equation 4. VOUT = VPK × (TON / TPER)

The peak amplitude of the secondary pulses (VPK) is given by [Equation 5](#x8209):

Equation 5. VPK = (1/2 VIN – VSWITCH) × (NS / NP) – VRECT

#### 2.10 Full-Bridge Converter

The [Full-Bridge](http://www.ti.com/product/sm72295) converter requires a total of four switching transistors to perform DC/DC conversion. The full bridge is most often seen in applications that are powered directly from the AC line, providing load power of 1 kW to 3 kW.

Operating offline, the full bridge converter typically uses about 300 V of unregulated DC voltage for power conversion (the voltage that is obtained when a standard 230 VAC line is rectified and filtered).

An important feature of this design is the isolation from the AC line provided by the switching transformer. The PWM control circuitry is referenced to the the output ground, requiring a dedicated voltage rail (usually powered from a small 60-Hz transformer) to run the control circuits.

The base drive voltages for the switch transistors (which are provided by the PWM chip) have to be transformer-coupled because of the required isolation.

[Figure 15](#x8689) shows a simplified schematic diagram of a Full-Bridge converter.

Figure 15. Full-Bridge Converter

The transformer primary is driven by the full voltage VIN when either of the transistor sets (*A* set or *B* set) turns on. The full input voltage utilization means the Full-Bridge can produce the most load power of all the converter types. The timing diagram is identical to the Half-Bridge, as shown in [Figure 14](half-bridge-converter-t4589915-21.html#x5093).

Primary and secondary current flows in the transformer during the switch on times, while the output capacitor discharges into the load when both transistors are off.

[Equation 6](#t4589915-36) is the equation for the output voltage (see [Figure 14](half-bridge-converter-t4589915-21.html#x5093)):

Equation 6. VOUT = VPK × (TON / TPER)

The peak voltage of the transformer secondary pulses (VPK) is given by [Equation 7](#t4589915-37):

Equation 7. VPK = (VIN – 2VSWITCH) × (NS / NP) – VRECT

### 3 Application Hints for Switching Regulators

The most commonly used DC/DC converter circuits will now be presented along with the basic principles of operation.

#### 3.1 Capacitor Parasitics Affecting Switching Regulator Performance

All capacitors contain parasitic elements which make their performance less than ideal (see [Figure 16](#x9621)).

Figure 16. Capacitor Parasitics

Summary of Effects of Parasitics:

* **ESR:** The equivalent series resistance (ESR) causes internal heating due to power dissipation as the ripple current flows into and out of the capacitor. The capacitor can fail if ripple current exceeds maximum ratings.

Excessive output voltage ripple will result from high ESR, and regulator loop instability is also possible. ESR is highly dependent on temperature, increasing very quickly at temperatures below about 10°C.

* **ESL:** The effective series inductance (ESL) limits the high frequency effectiveness of the capacitor. High ESL is the reason electrolytic capacitors need to be bypassed by film or ceramic capacitors to provide good high-frequency performance.

The ESR, ESL, and C within the capacitor form a resonant circuit, whose frequency of resonance should be as high as possible. Switching regulators generate ripple voltages on their outputs with very high frequency (>10 MHz) components, which can cause ringing on the output voltage if the capacitor resonant frequency is low enough to be near these frequencies.

#### 3.1.1 Input Capacitors

All of the switching converters in this paper (and the vast majority in use) operate as DC/DC converters that *chop* a DC input voltage at a very high frequency. As the converter switches, it has to draw current pulses from the input source. The source impedance is extremely important, as even a small amount of inductance can cause significant ringing and spiking on the voltage at the input of the converter.

The best practice is to always provide adequate capacitive bypass as near as possible to the switching converter input. For best results, an electrolytic is used with a film capacitor (and possibly a ceramic capacitor) in parallel for optimum high frequency bypassing.

#### 3.1.2 Output Capacitor ESR Effects

The primary function of the output capacitor in a switching regulator is filtering. As the converter operates, current must flow into and out of the output filter capacitor.

The ESR of the output capacitor directly affects the performance of the switching regulator. ESR is specified by the manufacturer on good quality capacitors, but be certain that it is specified at the frequency of intended operation.

General-purpose electrolytics usually only specify ESR at 120 Hz, but capacitors intended for high-frequency switching applications will have the ESR guaranteed at high frequency (like 20 kHz to 100 kHz).

Some ESR dependent parameters are:

* **Ripple Voltage:** In most cases, the majority of the output ripple voltage results from the ESR of the output capacitor. If the ESR increases (as it will at low operating temperatures) the output ripple voltage will increase accordingly.
* **Efficiency:** As the switching current flows into and out of the capacitor (through the ESR), power is dissipated internally. This *wasted* power reduces overall regulator efficiency, and can also cause the capacitor to fail if the ripple current exceeds the maximum allowable specification for the capacitor.
* **Loop Stability:** The ESR of the output capacitor can affect regulator loop stability. Products such as the LM2575 and LM2577 are compensated for stability assuming the ESR of the output capacitor will stay within a specified range.

Keeping the ESR within the *stable* range is not always simple in designs that must operate over a wide temperature range. The ESR of a typical aluminum electrolytic may increase by 40X as the temperature drops from 25°C to –40°C.

In these cases, an aluminum electrolytic must be paralleled by another type of capacitor with a flatter ESR curve (like Tantalum or Film) so that the effective ESR (which is the parallel value of the two ESR's) stays within the allowable range.

NOTE

If operation below –40°C is necessary, aluminum electrolytics are probably not feasible for use.

#### 3.1.3 Bypass Capacitors

High-frequency bypass capacitors are always recommended on the supply pins of IC devices, but if the devices are used in assemblies near switching converters bypass capacitors are absolutely required.

The components which perform the high-speed switching (transistors and rectifiers) generate significant EMI that easily radiates into PCB traces and wire leads.

To assure proper circuit operation, all IC supply pins must be bypassed to a clean, low-inductance ground (for details on grounding, see [Section 3.2](proper-grounding-x9023.html#x9023)).

#### 3.2 Proper Grounding

The *ground* in a circuit is supposed to be at one potential, but in real life it is not. When ground currents flow through traces which have non-zero resistance, voltage differences will result at different points along the ground path.

In DC or low-frequency circuits, *ground management* is comparatively simple: the only parameter of critical importance is the DC resistance of a conductor, because that defines the voltage drop across it for a given current. In high-frequency circuits, it is the inductance of a trace or conductor that is much more important.

In switching converters, peak currents flow in high-frequency (> 50 kHz) pulses, which can cause severe problems if trace inductance is high. Much of the *ringing* and *spiking* seen on voltage waveforms in switching converters is the result of high current being switched through parasitic trace (or wire) inductance.

Current switching at high frequencies tends to flow near the surface of a conductor (this is called *skin effect*), which means that ground traces must be very wide on a PCB to avoid problems. It is usually best (when possible) to use one side of the PCB as a ground plane. [Figure 17](#x1769) illustrates an example of a terrible layout:

Figure 17. Example of Poor Grounding

The layout shown has the high-power switch return current passing through a trace that also provides the return for the PWM chip and the logic circuits. The switching current pulses flowing through the trace will cause a voltage spike (positive and negative) to occur as a result of the rising and falling edge of the switch current. This voltage spike follows directly from the v = L (di/dt) law of inductance.

It is important to note that the magnitude of the spike will be different at all points along the trace, being largest near the power switch. Taking the ground symbol as a point of reference, this shows how all three circuits would be bouncing up and down with respect to ground. More important, they would also be moving with respect to each other.

Misoperation often occurs when sensitive parts of the circuit *rattle* up and down due to ground switching currents. This can induce noise into the reference used to set the output voltage, resulting in excessive output ripple. Very often, regulators that suffer from ground noise problems appear to be unstable, and break into oscillations as the load current is increased (which increases ground currents). A much better layout is shown in [Figure 18](#x6557).

Figure 18. Example of Good Grounding

A big improvement is made by using single-point grounding. A good high-frequency electrolytic capacitor (like solid Tantalum) is used near the input voltage source to provide a good ground point.

All of the individual circuit elements are returned to this point using separate ground traces. This prevents high current ground pulses from bouncing the logic circuits up and down.

Another important improvement is that the power switch (which has the highest ground pin current) is placed as close as possible to the input capacitor. This minimizes the trace inductance along its ground path.

It should also be pointed out that all of the individual circuit blocks have *local* bypass capacitors tied directly across them. The purpose of this capacitor is RF bypass, so it must be a ceramic or film capacitor (or both).

A good value for bypassing logic devices would be 0.01-μF ceramic capacitor(s), distributed as required.

If the circuit to be bypassed generates large current pulses (like the power switch), more capacitance is required. A good choice would be an aluminum electrolytic bypassed with a film and ceramic capacitor. Exact size depends on peak current, but the more capacitance used, the better the result.

#### 3.3 Transformer/Inductor Cores and Radiated Noise

The type of core used in an inductor or transformer directly affects its cost, size, and radiated noise characteristics. Electrical noise radiated by a transformer is extremely important, as it may require shielding to prevent erratic operation of sensitive circuits located near the switching regulator.

The most commonly used core types will be presented, listing the advantages and disadvantages of each.

The important consideration in evaluating the electrical noise that an inductor or transformer is likely to generate is the magnetic flux path. In [Figure 19](#x3421), the slug core and toroidal core types are compared.

Figure 19. Flux Paths in Slug and Toroid Cores

The flux in the slug core leaves one end, travels through the air, and returns to the other end. The slug core is the highest (worst) for radiated flux noise. In most cases, the slug core device will give the smallest, cheapest component for a given inductor size (it is very cheap to manufacture).

The magnetic flux path in the toroid is completely contained within the core. For this reason it has the lowest (best) radiated flux noise. Toroid core components are typically larger and more expensive compared to other core types. Winding a toroid is fairly difficult (and requires special equipment), driving up the finished cost of the manufactured transformer.

There is another class of cores commonly used in magnetic design which have radiated flux properties that are much better than the slug core, but not as good as the toroid.

These cores are two-piece assemblies, and are assembled by gluing the core pieces together around the bobbin that holds the winding(s). The cores shown are frequently *gapped* to prevent saturation of the Ferrite core material. The air gap is installed by grinding away a small amount of the core (the gap may be only a few thousandths of an inch).

[Figure 20](#x8838) shows the popular E-I, E-E and Pot cores often used in switching regulator transformers. The cores show the locations where an air gap is placed (if required), but the bobbins and windings are omitted for clarity.

Figure 20. Flux Paths in E-I, E-E and Pot Cores

The air gap can emit flux noise because there is a high flux density in the vicinity of the gap, as the flux passing through the core has to jump the air gap to reach the other core piece.

The E-E and E-I cores are fairly cheap and easy to manufacture, and are very common in switching applications up to about 1 kW. There is a wide variety of sizes and shapes available, made from different Ferrite *blends* optimized for excellent switching performance. The radiated flux from this type of core is still reasonably low, and can usually be managed by good board layout.

The Pot core (which is difficult to accurately show in a single view drawing), benefits from the shielding effect of the core sides (which are not gapped). This tends to keep the radiated flux contained better than an E-E or E-I core, making the Pot core second best only to the toroid core in minimizing flux noise.

Pot cores are typically more expensive than E-E or E-I cores of comparable power rating, but they have the advantage of being less noisy. Pot core transformers are much easier to manufacture than toroid transformers because the windings are placed on a standard bobbin and then the core is assembled around it.

#### 3.4 Measuring Output Ripple Voltage

The ripple appearing on the output of the switching regulator can be important to the circuits under power. Getting an accurate measurement of the output ripple voltage is not always simple.

If the output voltage waveform is measured using an oscilloscope, an accurate result can only be obtained using a differential measurement method (see [Figure 21](#x1372)).

Figure 21. Differential Output Ripple Measurement

The differential measurement shown uses the second channel of the oscilloscope to *cancel out* the signal that is common to both channels (by inverting the B channel signal and adding it to the A channel).

The reason this method must be used is because the fast-switching components in a switching regulator generate voltage spikes that have significant energy at very high frequencies. These signals can be picked up very easily by *antennas* as small as the 3-inch ground lead on the scope probe.

Assuming the probes are reasonably well matched, the B channel probe will pick up the same radiated signal as the A channel probe, which allows this *common-mode* signal to be eliminated by adding the inverted channel B signal to channel A.

It is often necessary to measure the RMS output ripple voltage, and this is usually done with some type of digital voltmeter. If the reading obtained is to be meaningful, the following must be considered:

1. The meter must be true-RMS reading, because the waveforms to be measured are very non-sinusoidal.
2. The 3-dB bandwidth of the meter should be at least 3X the bandwidth of the measured signal (the output voltage ripple frequency will typically be > 100 kHz).
3. Subtract the *noise floor* from the measurement. Connect both meter leads to the negative regulator output and record this value. Move the positive meter lead to positive regulator output and record this value. The actual RMS ripple voltage is the difference between these two readings.

#### 3.5 Measuring Regulator Efficiency of DC/DC Converters

The efficiency (η) of a switching regulator is defined as:

Equation 8. η = PLOAD / PTOTAL

In determining converter efficiency, the first thing that must be measured is the total consumed power (PTOTAL). Assuming a DC input voltage, PTOTAL is defined as the total power drawn from the source, which is equal to:

Equation 9. PTOTAL = VIN × IIN (AVE)

It must be noted that the input current value used in the calculation must be the average value of the waveform (the input current will not be DC or sinusoidal).

Because the total power dissipated must be constant from input to output, PTOTAL is also equal to the load power plus the internal regulator power losses:

Equation 10. PTOTAL = PLOAD + PLOSSES

Measuring (or calculating) the power to the load is very simple, because the output voltage and current are both DC. The load power is found by:

Equation 11. PLOAD = VOUT × ILOAD

Measuring the input power drawn from the source is not simple. Although the input voltage to the regulator is DC, the current drawn at the input of a switching regulator is not. If a typical *clip-on* current meter is used to measure the input current, the taken data will be essentially meaningless.

The average input current to the regulator can be measured with reasonable accuracy by using a wide-bandwidth current probe connected to an oscilloscope.

The average value of input current can be closely estimated by drawing a horizontal line that divides the waveform in such a way that the area of the figure above the line will equal the *missing* area below the line (see [Figure 22](#x2189)). In this way, the *average* current shown is equivalent to the value of DC current that would produce the same input power.

Figure 22. Average Value of Typical Input Current Waveform

If more exact measurements are needed, it is possible to force the current in the line going to the input of the DC/DC converter to be DC by using an L-C filter between the power source and the input of the converter (see [Figure 23](#x1425)).

Figure 23. L-C Filter Used in DC Input Current Measurement

If the L-C filter components are adequate, the current coming from the output of the DC power supply will be DC current (with no high-frequency switching component) which means it can be accurately measured with a cheap clip-on ammeter and digital volt meter. It is essential that a large, low-ESR capacitor be placed at CIN to support the input of the switching converter. The L-C filter that the converter sees looking back into the source presents a high impedance for switching current, which means CIN is necessary to provide the switching current required at the input of the converter.

#### 3.6 Measuring Regulator Efficiency of Offline Converters

Offline converters are powered directly from the AC line, by using a bridge rectifier and capacitive filter to generate an unregulated DC voltage for conversion (see [Figure 13](half-bridge-converter-t4589915-21.html#x2328) and [Figure 14](half-bridge-converter-t4589915-21.html#x5093)).

Measuring the total power drawn from the AC source is fairly difficult because of the power factor. If both the voltage and current are sinusoidal, power factor is defined as the cosine of the phase angle between the voltage and current waveforms.

The capacitive-input filter in an offline converter causes the input current to be very non-sinusoidal. The current flows in narrow, high-amplitude pulses (called Haversine pulses) which requires that the power factor be redefined in such cases.

For capacitive-input filter converters, power factor is defined as:

Equation 12. P.F. = PREAL / PAPPARENT

The real power drawn from the source (PREAL) is the power (in Watts) which equals the sum of the load power and regulator internal losses.

The apparent power (PAPPARENT) is equal to the RMS input current times the RMS input voltage. Rewritten, the importance of power factor is shown

Equation 13.  IIN (RMS) = PREAL / (VIN (RMS) × PF)

The RMS input current that the AC line must supply (for a given real power in Watts) increases directly as the power factor reduces from unity. Power factor for single-phase AC-powered converters is typically about 0.6. If three-phase power is used, the power factor is about 0.9.

If the efficiency of an offline converter is to be measured, power analyzers are available which will measure and display input voltage, input power, and power factor. These are fairly expensive, so they may not be available to the designer.

Another method which will give good results is to measure the power after the rectifier bridge and input capacitor (where the voltage and current are DC). This method is shown in [Figure 24](#x1587).

Figure 24. Measuring Input Power in Offline Converter

The current flowing from CIN to the converter should be very nearly DC, and the average value can be readily measured or approximated (see previous section).

The total power drawn from the AC source is the sum of the power supplied by CIN (which is VIN × IDC) and the power dissipated in the input bridge rectifier. The power in the bridge rectifier is easily estimated, and is actually negligible in most offline designs.

### 4 Application Circuits

Application circuits will be detailed which will demonstrate some examples of switching regulator designs.

#### 4.1 LM2577: A Complete Flyback/Boost Regulator IC

The [LM2577](http://www.ti.com/product/LM2577) is an IC developed as part of the SIMPLE SWITCHER® product family. It is a current-mode control switching regulator, with a built-in NPN switch rated for 3-A switch current and 65-V breakdown voltage.

The most commonly used applications are for Flyback or Boost regulators (see [Figure 25](#x6879)). In the Boost regulator, the output is always greater than the input. In the Flyback, the output may be greater than, less than, or equal to the input voltage.

Figure 25. Basic Application Circuits for the LM2577

The theory of operation of the flyback and boost converters has been previously covered, and will not be repeated here.

The LM2577 is targeted for applications with load power requirements up to a maximum of about 25 Watts, and can be used to implement boost or flyback regulators (with multiple output voltages available if flyback is selected).

The next sections will show the LM2577 being used in circuits which are more advanced than the typical applications (these circuits were generated as solutions for specific customer requirements).

#### 4.1.1 Increasing Available Load Power in an LM2577 Boost Regulator

One of the most frequently requested circuits is a method to squeeze more power out of a boost converter. The maximum load power available at the output is directly related to the input power available to the DC/DC converter.

When the input voltage is a low value (like 5 V), this greatly reduces the amount of power that can be drawn from the source (because the maximum input current is limited by what the switch can handle). In the case of the LM2577, the maximum switch current is 3-A (peak).

Increased load power can be obtained with the LM2577 by paralleling two devices (see [Figure 26](#x1034)). Because current-mode control is used in the LM2577, the two converters will automatically share the load current demand.

Figure 26. Dual LM2577 Boost Circuit

The right-hand regulator (which is a fixed 12-V version) is the master that sets the duty cycle of both regulators (tying the Compensation pins together forces the duty cycles to track).

The master regulator has direct feedback from the output, while the other regulator has its Feedback pin grounded. Grounding the Feedback pin makes the regulator attempt to run *wide open* (at maximum duty cycle), but the master regulator controls the voltage at both Compensation pins, which adjusts the pulse widths as required to hold the output voltage at 12 V.

#### 4.2 LM2577 Negative Buck Regulator

The LM2577 can be used in a Buck regulator configuration that takes a negative input voltage and produces a regulated negative output voltage (see [Figure 27](#x8145)).

Figure 27. Negative Buck Regulator

The LM2577 is referenced to the negative input, which means the feedback signal coming from the regulated output must be DC level shifted. R1, D1, and Q1 form a current source that sets a current through R2 that is directly proportional to the output voltage (D1 is included to cancel out the VBE of Q1).

Neglecting the base current error of Q1, the current through R2 is equal to:

Equation 14. IR2 = VOUT / R1 (which is 300 μA for this example.)

The voltage across R2 provides the 1.23-V feedback signal which the LM2577 requires for its feedback loop.

The operation of the power converter is similar to what was previously described for the Buck regulator:

* When the switch is ON, current flows from ground through the load, into the regulator output, through the inductor, and down through the switch to return to the negative input. The output capacitor also charges during the switch ON time.
* When the switch turns OFF, the voltage at the diode end of the inductor flies positive until the Schottky diode turns on (this allows the inductor current to continue to flow through the load during the OFF time). The output capacitor also discharges through the load during the OFF time, providing part of the load current.

#### 4.3 LM2577 Three-Output, Isolated Flyback Regulator

Many applications require electrical isolation between the input and output terminals of the power supply (for example, medical monitoring instruments require isolation to assure patient safety).

[Figure 28](#x8694) shows an example of a three-output flyback regulator 2 built using the LM2577 that has electrical isolation between the input and output voltages.

Figure 28. Three-Output Isolated Flyback Regulator

Three output voltages are obtained from three separate transformer secondary windings, with voltage feedback being taken from the 5-V output.

To maintain electrical isolation, the feedback path uses a 4N27 opto-coupler to transfer the feedback signal across the isolation barrier.

The 5-V output is regulated using an LM385 adjustable reference, whose voltage is set by R1 and R2. The LM385 operates by forcing a 1.24-V reference voltage between the positive terminal and the feedback pin, so the set voltage across the LM385 is given by:

Equation 15.  VREF = 1.24 × (R2/R1 + 1)

For the values shown in this example, the voltage will be 5 V.

The function of the LM385 in the circuit can be described as an *ideal* Zener diode, because the current flowing through the LM385 is very small until the voltage at its positive terminal reaches 5 V with respect to ground. At that point, it tries to regulate its positive terminal to 5 V by conducting current (which flows out of the negative terminal of the LM385 and through the 470-Ω resistor into the diode side of the opto-coupler).

When the LM385 starts conducting current through the opto-coupler diode, the collector of the transistor in the opto-coupler pulls down on the compensation pin of the LM2577, which reduces the duty cycle (pulse widths) of the switching converter. In this way, a negative feedback loop is established which holds the output at 5 V.

The feedback signal from the collector of the opto-coupler is fed into the compensation pin (not the feedback pin) of the LM2577 in order to bypass the internal error amplifier of the LM2577. The gain of the LM385 is so high that using the error amplifier inside the loop would make it difficult to stabilize (and is not necessary for good performance).

Test data taken with the input voltage set to 26 V and all outputs fully loaded showed the frequency response of the control loop had a 0-dB crossover point of 1 kHz with a phase margin of 90°.

The 7.5-V and –7.5-V outputs are not directly regulated, which means their voltages are set by the pulse width of the regulated (5 V) winding. As a result, the load regulation of these two outputs is not quite as good as the 5-V output.

### Table 1. Summary of Test Performance Data

| OUTPUT VOLTAGES | LINE REGULATION   (AT FULL LOAD) | LOAD REGULATION   (VIN = 26 V) | OUTPUT RIPPLE VOLTAGE (25°C) |
| --- | --- | --- | --- |
| 5 V | 0.2% | 0.04% (30 mA - 150 mA) | 50 mV |
| 7.5 V | 0.3% | 3% (20 mA - 100 mA) | 50 mV |
| –7.5 V | 0.3% | 2% (12 mA - 70 mA) | 50 mV |

#### 4.4 LM2575 and LM2576 Buck Regulators

The [LM2575](http://www.ti.com/product/LM2575) and [LM2576](http://www.ti.com/product/LM2576) products are buck regulators developed as part of the SIMPLE SWITCHER product family.

The LM2575 is rated for 1 A of continuous load current, while the LM2576 can supply 3 A. The maximum input voltage for the parts is 40 V (60 V for the *HV* versions), with both adjustable and fixed output voltages available.

The basic buck regulator application circuit is shown in [Figure 29](#x6564).

Figure 29. LM2575 and LM2576 Buck Regulator Application

The LM2575 and LM2576 can also be used in an inverting (buck-boost) configuration which allows a positive input voltage to be converted to a negative regulated output voltage (see [Figure 30](#x7289)).

Figure 30. LM2575 and LM2576 Inverting Application

#### 4.5 Low Dropout, High Efficiency 5-V/3-A Buck Regulator

A circuit was developed which provides a 5-V/3-A regulated output voltage with very high efficiency and very low dropout voltage (see [Figure 31](#x3613)). The customer required that the circuit be able to operate with an input voltage range of 6 V to 12 V, allowing only 1 V of dropout at the lowest input voltage.

Figure 31. Low-Dropout 5-V/3-A regulator

An unusual feature of this circuit is that it can stay in regulation with only 300 mV across the regulator. Also, the efficiency is highest (89%) at the lowest input voltage (buck converters are typically more efficient at higher input voltages).

The low (< 300 mV) dropout voltage is achieved by using an external PNP power transistor (Q2) as the main switching transistor (the other transistors in the circuit are drivers for Q2). With components values shown, Q2 has a saturation voltage of 200 mV at 3 A, which allows the 300 mV input-output differential requirement for the regulator to be met.

The switch inside the LM2575 drives the base of Q1 through R2. Note that the maximum collector current of Q1 (and the maximum base drive available for Q2) is limited by Z1 and R4. When Z1 clamps at 5V, the maximum current through Q1 is:

Equation 16. IQ1 (MAX) = (5 – VBE) / R4 = 215 mA

The maximum Q1 current (215 mA) limits the amount of base drive available to Q2, forcing the collector current of Q2 to *beta limit* as the output is overloaded (this means the maximum collector current of Q2 will be limited by the gain of the transistor and the base drive provided). Although this is not a precise current limiter, it is adequate to protect Q2 from damage during an overload placed on the output.

If the regulator output is shorted to ground, the output short-circuit current flows from the output of the LM2575 (through D1 and the inductor), which means the regulator short-circuit current is limited to the value set internally to the LM2575 (which is about 2 A).

Note also that when the regulator output is shorted to ground, the cathode of D1 will also be near ground. This allows D1 to clamp off the base drive to Q1 off, preventing current flow in the switch transistor Q2.

If the input voltage does not exceed 8 V, R2 and Z1 are not required in the circuit.

This circuit was tested with 6-V input and was able to deliver more than 4 A of load current with 5 Vout. Other test data taken are:

### Table 2. Summary of Performance Data

| MEASURED PERFORMANCE DATA | |
| --- | --- |
| **LINE REGULATION** | |
| 5.3 V to 12 V at 1 A | 32 mV |
| 5.3 V to 12 V at 3 A | 45 mV |
| **LOAD REGULATION** | |
| 0.3 A to 3 A at 5.3-V Input | 10 mV |
| 0.3 A to 3 A at 12-V Input | 17 m |
| **EFFICIENCY AT 3-A LOAD** | |
| VIN = 5.3 V | 89% |
| VIN = 12 V | 80% |
| **OUTPUT RIPPLE VOLTAGE** | |
| VIN = 7.2 V, IL = 3 A | 35 mV(p-p) |

### 5 References and Related Products

* [DC/DC Switching regulator ICs for any application](http://www.ti.com/lsds/ti/power-management/non-isolated-dc-dc-switching-regulator-overview.page)
* [Overview for step-down (buck)](http://www.ti.com/lsds/ti/power-management/step-down-buck-overview.page)
* [Overview for step-up (boost)](http://www.ti.com/lsds/ti/power-management/step-up-boost-overview.page)
* [Overview for buck/boost, inverting or split-rail](http://www.ti.com/lsds/ti/power-management/buck-boost-inverting-or-split-rail-overview.page)
* [Products for flyback controller](http://www.ti.com/lsds/ti/power-management/flyback-controller-products.page)
* [Products for half-bridge](http://www.ti.com/lsds/ti/power-management/half-bridge-driver-products.page)
* [SM72295 3A Full bridge gate driver with integrated current sense amplifier SM72295](http://www.ti.com/product/sm72295)
* [LM2577 SIMPLE SWITCHER® 3.5V to 40V, 3A low component count step-up regulator](http://www.ti.com/product/LM2577)
* [LM2575 1-A SIMPLE SWITCHER® step-down adjustable voltage switching regulator with output enable](http://www.ti.com/product/LM2575)
* [LM2576 SIMPLE SWITCHER® 40V, 3A low component count step-down regulator](http://www.ti.com/product/LM2576)