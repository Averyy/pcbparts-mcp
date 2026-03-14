---
source: "EDN -- Low-Cost Driver for Thermoelectric Coolers (TECs)"
url: "https://www.edn.com/low-cost-driver-for-thermoelectric-coolers-tecs/"
format: "HTML"
method: "readability"
extracted: 2026-02-16
chars: 20697
---

Thermoelectric coolers (TECs), also called Peltier-coolers, are used for stabilizing optical benches, filters, lenses, laser diodes, photodiodes, and other parts in electro-optical systems. TECs are often integrated into the off-the-shelf parts like pump laser diodes [1].

Typical TECs used in these modules have 2 connections, the maximum voltages across these connections and the maximum currents through the TECs are around +/- 2-3 V and +/- 1.5-3 A. Depending upon the direction of the current, heat is moved from one side of the TEC to the other side. The absolute value of the current determines the cooling power or the heating power.

The impedance of the TEC, roughly looks like a resistor with a value of 1-2 Ω. In order to build a temperature controller, one needs a temperature sensor (typically an NTC), a temperature controller (either analog or digital) and a two-quadrant current driver (or voltage driver) that is able to deliver the aforementioned current of up to +/- 3 A at voltages of up to +/- 3 V. The output of the temperature controller steers the input of the driver stage. (It is also possible, and makes sense at least for small thermal loads, to operate the TEC steadily in cooling mode only and to use a heater resistor for heating against the cold side [2].) This driver stage is the subject of this article.

Some ten years ago, a TEC driver was built, at least in principle, from two buck converters working in an H-bridge mode. The TEC was connected between the half-bridges, so that the voltage difference between the half-bridge outputs determined the direction of the TEC current. Examples for this are the LTC1923 [3] and the DRV592 [4].

These older TEC drivers used two storage inductors, as shown in **Figure 1**. Inductors of this kind are relatively pricey, lossy, heavy and they consume quite a lot of board space, so it made sense to look for a solution that allowed one to save a storage inductor.

**Figure 1** Classical TEC power stage with two buck converters in an H-bridge arrangement, using two power inductors.

One of these solutions comprises an H-bridge, where one side operates in a pure switch mode and the other side in a linear mode. Only the switch mode side requires an inductor. Some parts that use this principle are the MP8833 [5] and the ADN8834 [6].

Another possibility is to use a buck-boost-converter. Instead of connecting the TEC to the output of the converter, the TEC is connected between input and output. Depending on the height of the output voltage, the difference between the input voltage and output voltage can be positive or negative and the current through the TEC flows in one direction or the other.

Examples of suitable buck-boost converters are the TPS63020 (Application Report SLVA677 [7]) or the TPS63070 (PMP9796 Test Report TIDUCA8 [8]). Here, too, only one storage inductor is required.

The following circuit also requires only one storage inductor and does not require any special components whatsoever. In this circuit, a commercially available adjustable step-down converter produces an adjustable output voltage by intervening in the feedback network.

The direction of current flow in the TEC is controlled by a downstream H-bridge, in the middle of which the TEC is located: when the top left switch and the bottom right switch are on and the other two switches of the H-bridge are off, then the current flows from left to right (or vice versa from right to left when the other diagonal pair of switches is on or off).

But there is a problem: The buck converters that are common today—which can be found in practically all products and are manufactured in massive quantities by countless companies—have minimum output voltages of around 0.6 to 1.25 V. The modern types usually have the smaller minimum output voltages.

To regulate a TEC precisely, however, you need voltages down to 0 V. There are two different approaches to bridge this gap between the minimum output voltage of the buck converter and 0 V:

1. Set the minimum output voltage of the buck converter and use the H-bridge as a switch to set an *average voltage* on the TEC between 0 V and the minimum buck converter voltage via pulse width modulation (PWM) with adjustable duty cycle. (Contrary to some statements that you can read about TECs over and over again, PWM operation does not harm a TEC as long as you [operate it within its specifications](https://www.ti.com/lit/an/slua979a/slua979a.pdf). In our case, the TEC is only operated with PWM in the lower current range anyway. It remains important that the PWM frequency is sufficiently large so that the TEC itself does not experience any significant thermal expansion or contraction during the on and off times of the pulses and thus becomes mechanically fatigued.) The low-pass effect on the heat capacity of the object that is temperature-controlled ensures that the temperature remains smooth.
   If larger TEC voltages are requested, the PWM operation of the half-bridge is switched off and the half-bridge again functions as a simple pole-changing circuit.
2. One can also set the minimum output voltage of the step-down converter and use a low-dropout linear regulator (LDO), i.e., a linear regulator with a low minimum voltage difference between input and output, to bridge the gap down to 0 V. The TEC is thus supplied with an unpulsed DC voltage in all operating states. For higher output voltages, the LDO is set to minimum dropout and causes only minimal losses.

**Version 1**

The first version is extremely simple and requires no additional power components (**Figure 2**). The existing H-bridge transistors are also used for PWM operation. If the components had ideal properties, then this variant would have an efficiency of 100% due to the pure switching operation of the components.

**Figure 2** Version 1 of the circuit described in the text, using only one power inductor and PWM control of the H-bridge.

Because the PWM frequencies at the bridge do not have to be particularly high—at least compared to the switching frequency of the buck converter—you do not need high drive powers at the gates of these transistors either. PWM frequencies in the kHz range should be sufficient for most applications! (However, very small thermal masses such as laser diodes could be influenced (e.g., a laser diode could be frequency modulated) by small temperature fluctuations up to the kHz range. Of course, whether this is relevant depends on the application.)

One could object that the pulsed currents cause high interference voltages on the input voltage and require extra buffer capacitors or filters there. However, a small calculation shows that the situation is relatively harmless: With a minimum output voltage of the step-down controller of, for example, 1 V and a TEC impedance of 1 Ω, peak values of 1000 mA result through the TEC. At input to step-down controller with a voltage of 12 V, the current is only 83.3 mA (ideally calculated to 1V/12V x 1000 mA = 83.3 mA)!

However, in very sensitive applications, for example when stabilizing laser diodes or photodiodes, a pulsed current of a few hundred milliamps can induce interference in the photocurrents or in the laser currents, despite the twisted-pair cable to the TEC. In these sensitive applications it is much better to drive the TEC with a DC voltage or DC current over the entire operating range. (Whether a TEC should be operated with a constant current or a constant voltage is always a point of discussion. In electro-optical applications, one tends to deal with small temperature differences between the hot and cold sides, which means that the Seebeck effect is small, and the series resistance dominates. In these applications, the difference between current and voltage control is therefore negligibly small.)

**Version 2**

In the second version, an LDO is used in addition to the H-bridge (**Figure 3**). This LDO is inserted between the output of the buck converter and the supply voltage of the H-bridge and provides an appropriate voltage drop to allow the TEC to be DC powered over its entire operating range.

**Figure 3** Version 2 of the circuit described in the text, using only one power inductor and an LDO for bridging the gap at low voltages.

If the TEC voltage is to be higher than the minimum output voltage U1(min) of the buck converter, then the LDO is set to minimum voltage drop and the TEC voltage is set via the control voltage Vctrl1. The sign of the TEC voltage is determined by the H-bridge and is set via a (digital) control input.

If, on the other hand, the TEC should have a lower voltage than U1(min), the LDO comes into action and generates the necessary voltage drop between U1 and U2 up to U1(min). In contrast to version 1, this voltage drop will no longer be lossless because of the LDO.

However, as the example calculation should show, the actual losses are quite small. So, which is the operating state with the greatest loss due to the LDO? That’s easy to answer, because the greatest loss of a source on a resistive load occurs when the source resistance is equal to the load resistance. With a minimum output voltage of the buck regulator of, for example, 1 V and a TEC impedance of 1 Ω, the greatest loss would be achieved if the LDO and the TEC each dropped 0.5 V.

In this case, a TEC current of 0.5V/1 Ω = 0.5 A flows, which of course also flows through the LDO. The power loss in the LDO is then 0.5 V x 0.5 A = 250 mW. This is a value that is easy to master.

In practice, however, step-down converters with smaller minimum output voltages will be used. For instance, with a converter that has a minimum output voltage of 0.8 V, the maximum power loss in the LDO with a 1 Ω TEC is only 0.4 V x 0.4 V / 1 Ω = 160 mW and with a converter with U1(min) = 0 .6 V it is even only 0.3 V x 0.3 V / 1 Ω = 90 mW.

In total, however, the maximum power dissipation of the circuit is not determined by the LDO, but by the buck converter: If you use a good buck converter with 90% efficiency at an output current of, say, 3 A, then a 1 Ω TEC is a power load of 3A x 3A x 1 Ω = 9 W and the power loss in the step-down converter is 9 W x (1/0.9 – 1) = 1 W which is converted into heat. At a TEC voltage of 3.3 V, the LDO is in short-circuit mode and ideally does not produce a voltage drop. If you assume a practical Rds(on) value of the LDO MOSFET of 20 mΩ, for example, then the losses are 3A x 3A x 20 mΩ = 180 mW and thus contribute relatively little to the total losses.

The measured curve of the power loss of a test circuit is shown in **Figure 4**.

**Figure 4** Comparison of the power losses caused by the buck converter and the total power losses of the whole circuit of Version 2 at different load currents.

The blue curve shows the power dissipation of the entire circuit and the red curve shows the power dissipation of the buck converter alone. Because of the resistive load, the overall shapes of the curves are roughly parabolic.

What is striking is the small difference between the two curves. The blue curve is not far above the red curve, which means that the circuit parts (LDO and H-bridge) connected to the buck converter cause relatively small losses. The relative difference is only slightly larger in the lower left part: There you can see a second, smaller parabolic piece superimposed, whose apex is at 0.3 V and which points downwards. This parabola stems from the previously described power loss of the LDO, which comes into action in the range below 0.6 V.

The schematic of the test circuit on which these measurements were made is shown in **Figure 5**.

**Figure 5** Schematic of the Version 2 test circuit that was used for measuring the loss curves in Figure 4.

In this example circuit, an attempt was made to keep the number of components as small as possible. For this reason, a four-pack (QQUAD) instead of individual transistors was used for the H-bridge. An integrated MOS driver (U5) was used to drive the gates.

**Buck Converter**

The buck regulator can be selected from a plethora of products. Suitable buck regulators with integrated MOSFETs for a 12 V input voltage and 3 A output current are available from around US$/€ 0.20. The matching storage inductors are usually significantly more expensive.

A step-down regulator module with an integrated storage choke was used in the test circuit (MUN12AD03-SH), which is a bit more expensive than a construction from individual parts, but also much more compact because the choke and the silicon are placed on top of each other. There are modules from different manufacturers with compatible footprints.

In order to influence the buck regulator via a control voltage, an intervention in the feedback network must be made. The easiest way to do this is with an additional resistor that is connected to the controller’s feedback input and connected to a DAC output on the other side. The necessary resistor values can be found by solving a system of equations, or you can just get them with the following few lines of this Python script:

Ufb = 0.6 # Voltage at feedback node (internal reference voltage of the regulator)
Uomin = 0.6 # Minimum output voltage of the regulator at a DAC voltage of Udmax
Uomax = 3.3 # Maximum output voltage of the regulator at a DAC voltage of Udmin
Udmin = 0.0 # Minimum output voltage of the DAC
Udmax = 2.7 # Maximum output voltage of the DAC
D = -Ufb\*(Uomax+Udmax-Udmin-Uomin) + Uomax\*Udmax – Uomin\*Udmin
Rfb1 =  D / (Ufb\*(Udmax-Udmin))
Rfb3 =  D / (Ufb\*(Uomax-Uomin))
Rfb2=100/3.5 # Scale factor for all resistances
Rfb1\*=Rfb2
Rfb3\*=Rfb2
print(“Rfb1 = “, Rfb1)
print(“Rfb2 = “, Rfb2)
print(“Rfb3 = “, Rfb3)

The variable settings in the code above give the following output:

Rfb1 =  99.99999999999999
Rfb2 =  28.571428571428573
Rfb3 =  100.0

**LDO**

The LDO consists of only 3 components: U2, RG and QLDO. The operational amplifier ensures that the output voltage of the LDO mirrors the control voltage. If it can no longer do this because a higher output voltage is required than is available at the drain of QLDO, then the output of the operational amplifier goes to the full operating voltage (in this case to 12 V) and switches QLDO on completely.

The requirements for U2 are low: It should be an op-amp whose maximum operating voltage range is at least as high as the maximum operating voltage of the circuit; the input voltage range should reach down to GND and the maximum output voltage should be as close as possible to the operating voltage so that QLDO can become as low-impedance as possible.

The demands on the MOSFET QLDO are also manageable: The Rds(on) should be significantly smaller than the Rds(on) of the sync FET in the buck regulator so that the overall efficiency does not suffer significantly. The maximum allowable gate-source voltage should be at least as high as the maximum operating voltage. If this were not the case, you would need additional protection of the gate with a Zener diode. The IRFHS8242 was used in the test circuit, whose Rds(on) is specified as 13 mΩ at 10 V gate-source voltage. Don’t forget to look at the SOA curves, but with maximum drain-source voltages of 0.6 V and currents of 3 A, this is well within the safe range.

**H-bridge**

The H-bridge can be built from single transistors or as shown in Figure 5, from a four-pack of MOSFETs in one package (DMHT3006LFJ). To control the gates, you can use a MOS driver or simply 2 smaller MOSFETs (e.g., 2N7002, BSS138) with relatively high-impedance pull-up resistors. If you connect the gate of one MOSFET to the drain of the other MOSFET, you also have an inverter function for “free”, which prevents all four bridge MOSFETs from conducting at the same time. The H-bridge does not need to be switched quickly; it only serves to select the polarity.

If you want to keep the circuit flexible and use as many alternative components as possible, then of course the use of individual semiconductors in the most common packages would generally be preferable to the use of rather less common components such as QUAD MOSFETs or MOS drivers. Sufficiently high values of the maximum permissible gate-source voltages must be ensured.

**Control of the output stage**

The power stage can be controlled with 2 DAC outputs and a digital output for switching from heating to cooling mode. If you have a microcontroller with a sufficient number of DAC outputs, such as an STM32G4x4 (7×12-bit DACs) or AduCM320 (8×12-bit DACs), then direct control via these DACs makes sense. If you are short on DACs, you can also use the clamp circuit with U3 and U4: The control voltage goes to U3, is limited there, inverted by U4 and goes to the buck converter. At the same time, the control voltage also goes to pin 3 of U2, the LDO input. The transition between fully driven inactive LDO and LDO operation is then automatic and seamless. A potentiometer was also included in the test circuit to check the full operating range without connecting a DAC.

**Figure 6** shows the layout of the test circuit. The TEC driver with the specified components needs a PCB area of 14 x 10 mm². The clamp circuit mentioned above is at the upper left of this board and could of course be made with smaller components if necessary.

**Figure 6** Version 2 test board. The actual power stage fits into an area of 14×10 mm² in the center of the PCB.

Lower operating voltages (<12V):

If you want to use the circuit for lower operating voltages or if you want to generate TEC voltages that are closer to the operating voltages, then it must be ensured that both the op-amp for the LDO and the MOS drivers are supplied with a sufficiently high voltage, to entirely turn on the upper three NMOS transistors.

For example, when operating at 5 V, you should provide a voltage doubler that can power the op-amp and MOS driver. Alternatively, you can also use a PWM output of the microcontroller and thus generate a 3.3 V square-wave signal to generate a voltage of about 8 V via a booster capacitor and two diodes.

Larger operating voltages (>12V):

With larger operating voltages, care must be taken not to exceed the maximum permissible gate-source voltages of the MOSFETs. This also applies to lower voltages, because the dielectric strength of the gates of modern MOSFETs is sometimes well below +/-20 V. In this case, Zener diodes should be used to limit the voltage.

Higher currents:

The circuit is easily scalable to higher currents. It should be sufficient to use a higher rated buck-converter and lower-resistance MOSFETs if one wants to go to twice the maximum current or even more than that. In some cases, especially when one wants to go to the limits, it may be wise to measure the TEC current with some high-side or low-side current monitor in order to limit the current precisely to the value given in the data sheet of the TEC.

*Christian Rausch is a director of R&D for TOPTICA AG, a laser photonics company that develops high-end laser systems for scientific and industrial applications.*

**Related Content**

**References**

1. “460 mW Fiber Bragg Grating Stabilized 980 nm Pump Modules.” Lumentum, n.d. Web. <https://www.lumentum.com/en/products/460-mw-fiber-bragg-grating-stabilized-980-nm-pump-modules>.
2. Rausch, Christian. “LED Driver Controls Thermoelectric Cooling.” Electronic Design, 6 May 2008. Web. <https://www.electronicdesign.com/power-management/article/21792076/led-driver-controls-thermoelectric-cooling>.
3. Analog Devices. LTC1923 – High Efficiency Thermoelectric Cooler Controller, from <https://www.analog.com/en/products/ltc1923.html>.
4. Texas Instruments. DV592 – High-Efficiency H-Bridge (Requires External PWM), from <https://www.ti.com/product/DRV592>.
5. Monolithic Power Systems. MP8833 – 1.5A Thermoelectric Cooler Controller, from <https://www.monolithicpower.com/en/mp8833.html>.
6. Analog Devices. ADN8834 – Ultracompact 1.5 A Thermoelectric Cooler (TEC) Controller, from <https://www.analog.com/en/products/adn8834.html>.
7. Neuhaeusler, Juergen. “Application Report: Low-Power TEC Driver” Texas Instruments, 2014, [ti.com/lit/an/slva677/slva677.pdf](www.ti.com/lit/an/slva677/slva677.pdf).
8. Neuhaeusler, Juergen and Michael Helmlinger. ” PMP9796 – 5V Low-Power TEC Driver Reference Design ” Texas Instruments, 2016, <https://www.ti.com/lit/ug/tiduca8/tiduca8.pdf>.