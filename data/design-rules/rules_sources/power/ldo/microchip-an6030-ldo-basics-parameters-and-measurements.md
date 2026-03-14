---
source: "Microchip AN6030 -- LDO Basics: Parameters and Measurements"
url: "https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ApplicationNotes/ApplicationNotes/AN6030-LDO-Basics-Parameter-Definitions-Measurements-and-Calculations-DS00006030.pdf"
format: "PDF 18pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 34420
---

LDO Basics – Parameter Definitions, Measurements and
Calculations

Purpose
Authors: Dinu-Paul Hurdubelea,
Silvia Pavel
Microchip Technology Inc.
The purpose of this application note is to explain the fundamental parameters of a Low Dropout Regulator
(LDO) and provide guidance on conducting necessary tests for measurement and calculation.
This document will briefly cover the following topics:
• How an LDO works
• The main parameters and functionalities of an LDO
• Test setups, measurements and calculations
• Board layout suggestions
• Conclusion
General Description
An LDO, or Low Dropout Regulator, is a type of linear voltage regulator that can operate with a small input-to-
output voltage difference. These devices are commonly used to provide a stable and precise output voltage,
despite variations in the input voltage or load conditions. They are particularly useful in applications where
maintaining a constant, low-ripple voltage is required. Typical applications where an LDO can be used include
battery-powered devices, audio equipment, communication systems and precision analog circuits.
The main parameters in which an LDO outperforms a switching regulator are its very low noise, the ripple
rejection ratio and the small quiescent current. Additionally, LDOs are a great solution because of their low
cost, simple design and the reduced number of components required for their configuration. However, they
are less efficient (the larger the input-output difference, the lower the efficiency), have limited heat dissipation
capabilities and they can only step down the input voltage.
Application Note DS00006030A - 1
© 2025 Microchip Technology Inc. and its subsidiaries

Diving Into LDO Basics
1. Diving Into LDO Basics
A basic LDO block diagram is presented in Figure 1-1. The LDO receives an input voltage that is
slightly higher than the desired output voltage, which is why it is referred to as "low dropout".
Inside the LDO, a stable reference voltage is generated, and the error amplifier compares the
output voltage (V ) with the reference voltage (V ). If there is any difference between the
OUT REF
two, the error amplifier generates an error signal that controls a pass element, which adjusts the
resistance between the input and output, thereby regulating the output voltage. The pass element
is typically either a bipolar junction transistor or a MOSFET. The output voltage is fed back into
the error amplifier through the resistor divider to continuously monitor and adjust the output,
ensuring it remains stable and at the desired level. An output capacitor is often used to improve the
stability and transient response of the regulator, while an input capacitor is also usually required to
attenuate the ripple passed on from the power source.
Figure 1-1. LDO Block Diagram
At the most basic level, an LDO requires only three connections: input, output and ground.
Furthermore, depending on the specific requirements of each application, other functions are
implemented in LDOs through additional pins:
• Bias Supply Voltage – V is an auxiliary voltage supply used to power the internal control
BIAS
circuitry of the LDO. Its purpose is to improve the performance of the LDO, particularly in terms
of efficiency, by keeping the input voltage close to the output voltage in cases where the output
voltage is low and the input voltage cannot be used to bias the internal circuitry (for example:
V = 0.8V, V = 1.2V, V = 3.3V).
OUT IN BIAS
• Enable/Shutdown – The shutdown functionality is often integrated into LDOs to help reduce
power consumption by lowering the quiescent current and keeping the device off. Many of
Microchip’s LDOs are equipped with this functionality, with the MCP1710 being a standout
performer, consuming only 20 nA of current during shutdown.
• Error Flag/Power Good – This is an open-drain connection that functions as a flag by asserting
high or low when the output voltage exceeds or drops certain thresholds. Some examples of
LDOs from our portfolio that include this functionality are the MCP1727, the MCP1824 and the
MIC37XXX series.
• Adjust – The connection to the error amplifier, along with the resistor divider can be moved
outside the package through the adjust pin available on some LDOs. This allows the end user
to set the desired output voltage using a pair of external resistors. From our portfolio, the
Application Note DS00006030A - 2

Diving Into LDO Basics
MIC2951/4 provides the largest value for voltage adjustability, allowing up to a 29V output
voltage, while the lowest output voltage value can be achieved at 0.4V with the MIC47050/3.
• Bypass – This provides an external connection to the voltage reference, enabling it to be filtered
by using a small-value capacitor. This technique improves output noise, transient response and
Power Supply Rejection Ratio (PSRR). The MIC5305, MIC5309 and MIC5323 are some LDOs with
great performance regarding the output noise level, facilitated by the small external capacitor
that can be connected to the LDO through the bypass pin.
Application Note DS00006030A - 3

Main Parameters of an LDO and How to Measure Them
2. Main Parameters of an LDO and How to Measure Them
When choosing the appropriate LDO for an application, it is necessary to understand the conditions
and environment in which it will be used. To select the device that will perform optimally in the
designated application, it is important to understand the main parameters and functions of LDOs
and how they impact the overall system functionality.
Before presenting the main parameters and their respective test setups, it is important to
prepare the test equipment and make sure that everything is calibrated and compatible with the
measurements to be performed. When testing LDOs, the following equipment should be available: a
power supply with enough channels and voltage/current capability, multiple voltmeters (including at
least one highly accurate for line and load regulation measurements), an oscilloscope (with a current
probe), a signal generator and appropriate cables. An electronic load or resistors can be used to
set the desired load currents, and a programmable electronic load or a board/device capable of
generating load steps is necessary to perform transient tests. The spectrum analyzer facilitates the
PSRR and noise measurements.
2.1. DC Parameters
Line regulation refers to the LDO's ability to maintain a constant output voltage despite changes
in the input voltage, while load regulation measures the LDO's ability to maintain the output
voltage as the output current varies. Good line and load regulation are essential for ensuring stable
operation under various conditions. Line regulation is generally expressed as the percentage change
in output voltage per volt change in input voltage (%/V), while load regulation is expressed as the
percentage change in output voltage per change in load current (%). Both parameters are crucial for
applications that require precise voltage levels under different operating conditions.
Testing line regulation and load regulation involves a straightforward setup. The required
equipment includes a power supply, a multimeter and an electronic load. Connect the power supply
to the input of the LDO and connect the electronic load and multimeter to the output.
Before beginning the measurements, it is important to determine the nominal output voltage (V )
NOM
of the LDO. To obtain this value, measure the output voltage while supplying the device with the
minimum operating input voltage (relative to the set output voltage) and the minimum operating
load current.
Figure 2-1. Line and Load Regulation Test Setup
To measure line regulation, set a constant output current using either the electronic load or
resistors. Increment the input voltage from the minimum input voltage to the maximum value.
At each step of the input voltage, measure the output voltage and record all data in a table. The
formula to calculate the line regulation of the MCP devices is as follows:
ΔVOUT
Lineregulation=
ΔVIN×VNOM
Application Note DS00006030A - 4

Where ∆V is the output voltage variation, ∆V is the input voltage variation and V is the
OUT IN NOM
nominal output voltage.
Alternatively, the variation in output voltage compared to the input voltage can be illustrated
graphically by plotting the recorded data from the measurements.
Figure 2-2. Output Voltage vs. Input Voltage at Different Ambient Temperatures (MCP1792)
(cid:22)(cid:17)(cid:22)(cid:19)(cid:19)
(cid:22)(cid:17)(cid:21)(cid:28)(cid:24)
(cid:22)(cid:17)(cid:21)(cid:28)(cid:19)
(cid:22)(cid:17)(cid:21)(cid:27)(cid:24)
(cid:22)(cid:17)(cid:21)(cid:27)(cid:19)
(cid:22)(cid:17)(cid:21)(cid:26)(cid:24)
(cid:22)(cid:17)(cid:21)(cid:26)(cid:19)
(cid:23)(cid:17)(cid:24) (cid:20)(cid:23)(cid:17)(cid:25) (cid:21)(cid:23)(cid:17)(cid:26) (cid:22)(cid:23)(cid:17)(cid:27) (cid:23)(cid:23)(cid:17)(cid:28) (cid:24)(cid:24)(cid:17)(cid:19)
Application Note DS00006030A - 5
(cid:12)(cid:57)(cid:11)(cid:3)(cid:72)(cid:74)(cid:68)(cid:87)(cid:79)(cid:82)(cid:57)(cid:3)(cid:87)(cid:88)(cid:83)(cid:87)(cid:88)(cid:50)
(cid:57) (cid:32)(cid:3)(cid:22)(cid:17)(cid:22)(cid:57)
(cid:53)
(cid:44) (cid:50)(cid:56)(cid:55) (cid:32)(cid:3)(cid:20)(cid:3)(cid:80)(cid:36) (cid:55) (cid:36) (cid:32)(cid:3)(cid:14)(cid:21)(cid:24)(cid:131)(cid:38)
(cid:55) (cid:32)(cid:3)(cid:16)(cid:23)(cid:19)(cid:131)(cid:38)
(cid:36)
(cid:55) (cid:32)(cid:3)(cid:14)(cid:20)(cid:24)(cid:19)(cid:131)(cid:38)
(cid:44)(cid:81)(cid:83)(cid:88)(cid:87)(cid:3)(cid:57)(cid:82)(cid:79)(cid:87)(cid:68)(cid:74)(cid:72)(cid:3)(cid:11)(cid:57)(cid:12)
In contrast, to assess load regulation, maintain a constant input voltage while adjusting the load
current from the minimum required load current to the maximum specified load current. At each
step of the load current, measure the output voltage and record the data in a table. The formula for
calculating the load regulation of the device is as follows:
ΔVOUT
Loadregulation=
VNOM
Where ∆V is the output voltage variation.
OUT
The variation in output voltage relative to the load current can be presented as a graph similar to
the one below:

Figure 2-3. Output Voltage vs. Output Current at Different Ambient Temperatures (MCP1792)
(cid:22)(cid:17)(cid:22)(cid:21)(cid:19)
(cid:22)(cid:17)(cid:22)(cid:20)(cid:19)
(cid:22)(cid:17)(cid:22)(cid:19)(cid:19)
(cid:22)(cid:17)(cid:21)(cid:28)(cid:19)
(cid:22)(cid:17)(cid:21)(cid:27)(cid:19)
(cid:22)(cid:17)(cid:21)(cid:26)(cid:19)
(cid:22)(cid:17)(cid:21)(cid:25)(cid:19)
(cid:19) (cid:21)(cid:19) (cid:23)(cid:19) (cid:25)(cid:19) (cid:27)(cid:19) (cid:20)(cid:19)(cid:19)
Application Note DS00006030A - 6
(cid:12)(cid:57)(cid:11)(cid:3)(cid:72)(cid:74)(cid:68)(cid:87)(cid:79)(cid:82)(cid:57)(cid:3)(cid:87)(cid:88)(cid:83)(cid:87)(cid:88)(cid:50)
(cid:57) (cid:32)(cid:3)(cid:23)(cid:17)(cid:24)(cid:57) (cid:44)(cid:49)
(cid:55) (cid:32)(cid:3)(cid:14)(cid:21)(cid:24)(cid:131)(cid:38)
(cid:55) (cid:32)(cid:3)(cid:14)(cid:20)(cid:24)(cid:19)(cid:131)(cid:38)
(cid:50)(cid:88)(cid:87)(cid:83)(cid:88)(cid:87)(cid:3)(cid:38)(cid:88)(cid:85)(cid:85)(cid:72)(cid:81)(cid:87)(cid:3)(cid:11)(cid:80)(cid:36)(cid:12)
For both line and load regulation, the measurements are generally carried out at 10-20
measurement points.
Ground current (I ) is the difference between the input current and the load current in a Low
GND
Dropout (LDO) regulator. It represents the current consumed internally by the LDO to maintain its
regulation and operation. Minimizing ground current is crucial for battery-powered applications to
extend battery life. A low ground current ensures that most of the input power is delivered to the
load rather than being wasted within the regulator itself. This parameter is particularly important in
low-power and portable devices, where energy efficiency is a primary concern.
Ground current is the term used to describe the device’s current consumption depending on the
load current, while quiescent current (I ) is used to show the current consumption when no load is
Q
connected to the LDO’s output.
To measure the quiescent current and ground current, connect an ammeter between the ground
pin of the LDO and the ground of the test board or evaluation board, as illustrated in the figure
below:
Figure 2-4. Ground and Quiescent Current Test Setup
For applications where the LDO is not always used and it is desirable to avoid wasting energy,
a good practice is to select an LDO that includes the enable/shutdown functionality to minimize
power consumption. In these cases, the quiescent current in shutdown mode (I ) is also an
Q_SHDN

important parameter to consider when selecting the appropriate device. The measurement setup is
similar to that for ground or quiescent current, except that the enable pin is connected to ground.
To plot the dependence of ground current on load current, adjust the load current from the
minimum output current to the maximum current capability of the LDO. This will help the user
determine the current consumption based on the intended application's current requirements. Use
a voltmeter to ensure that the device is functioning properly during the measurement process.
Figure 2-5. Ground Current vs. Load Current at Different Ambient Temperatures (MCP1792)
(cid:27)(cid:19)
(cid:26)(cid:19)
(cid:25)(cid:19)
(cid:24)(cid:19)
(cid:23)(cid:19)
(cid:22)(cid:19)
(cid:21)(cid:19)
(cid:19) (cid:20)(cid:19) (cid:21)(cid:19) (cid:22)(cid:19) (cid:23)(cid:19) (cid:24)(cid:19) (cid:25)(cid:19) (cid:26)(cid:19) (cid:27)(cid:19) (cid:28)(cid:19) (cid:20)(cid:19)(cid:19)
Application Note DS00006030A - 7
 2019-2022 Microchip Technology Inc. and its subsidiaries DS20006229D-page 8
(cid:12)(cid:36)(cid:151)(cid:11)(cid:3)(cid:87)(cid:81)(cid:72)(cid:85)(cid:85)(cid:88)(cid:38)(cid:3)(cid:71)(cid:81)(cid:88)(cid:82)(cid:85)(cid:42)
(cid:55) (cid:32)(cid:3)(cid:20)(cid:24)(cid:19)(cid:131)(cid:38)
(cid:55) (cid:32)(cid:3)(cid:21)(cid:24)(cid:131)(cid:38)
(cid:50)(cid:88)(cid:87)(cid:83)(cid:88)(cid:87)(cid:3)(cid:47)(cid:82)(cid:68)(cid:71)(cid:3)(cid:11)(cid:80)(cid:36)(cid:12)
Dropout voltage is the minimum difference between the input voltage and the output voltage
at which the LDO can still regulate the output effectively. When the input voltage approaches
the output voltage, the LDO enters dropout mode, causing the output voltage to fall below the
desired level. A low dropout voltage is desirable, as it allows the LDO to maintain regulation with a
smaller input-output voltage differential, which is beneficial in applications with limited input voltage
headroom, such as battery-operated devices nearing the end of their charge. For Microchip’s LDOs,
the parts are considered to be in dropout when the output voltage drops 2% below the nominal
output voltage (V ) for the desired load.
NOM
Figure 2-6. Dropout Voltage Test Setup
To properly measure the dropout voltage, a power source, an electronic load and two voltmeters
are required. As shown in Figure 2-6, after the input voltage and load current have been set,
voltmeter V will measure the output voltage while V is being reduced. When V drops 2% below
2 IN OUT
V , V will be used to measure the dropout voltage. The test will be performed at multiple load
NOM 1

currents, from the minimum value up to the maximum value, generating a graphic that will illustrate
how the dropout voltage increases with the load current. It is important that, while the input voltage
is decreasing, V does not drop below the minimum input voltage of the LDO; otherwise, the results
IN
will not be considered valid.
The MIC5309 will be used as an example. This is a 300 mA Microchip LDO with very low dropout
voltage (typically 100 mV at maximum load), output voltage range between 0.8V to 2.0V and input
voltage range between 1.7V to 5.5V. The test cannot be performed for the 1.2V output version
because, while reducing the V , we would drop below the minimum input voltage rating (1.7V).
Therefore, the 1.8V output version was selected. After conducting the measurements as previously
described across various loads, ranging from 1 mA to 300 mA, the resulting data will be plotted to
illustrate the dropout voltage versus output current dependency.
Figure 2-7. Dropout Voltage vs. Output Current (MIC5309)
2.2. Transient Tests
Line step response characterizes how quickly and accurately an LDO can respond to sudden
changes in the input voltage. This measures the transient performance of the regulator when the
input voltage experiences a step change, such as a sudden increase or decrease. A good line step
response ensures that the output voltage remains stable and within acceptable limits during such
transients, which is important in systems where the input power supply may be subject to rapid
fluctuations. The line step response is typically evaluated by observing the output voltage deviation
and recovery time following a step change in the input voltage.
The voltage step to the input of the LDO can be created using a signal generator together with a
power amplifier (so that the input signal has enough current and voltage capability). On the signal
generator, the voltage step can be configured for multiple amplitudes, period times and rising or
falling rates. The steeper the rising or falling slopes are, the larger the undershoots or overshoots
that will appear on the output voltage. To set the load for the LDO, resistors should be used rather
than an electronic load. This is because the active circuitry in the electronic load can introduce noise
and potential instability into the circuit - factors that can affect the accuracy of the measurement
and make it harder to isolate the LDO's behavior from the characteristics of the electronic load itself.
To capture these waveforms, an oscilloscope should be used, with one probe connected to the input
of the LDO and another to the output. The complete test set up is illustrated in Figure 2-8 and an
example of how the oscilloscope capture should look is presented in Figure 2-9.
Application Note DS00006030A - 8

Figure 2-8. Line Step and Start-up Test Setup
Figure 2-9. Line Step Oscilloscope Capture (MCP1792)
I = 10 mA
Step from 6V to 14V
V
IN Rise and Fall
2V/div
Slope = 1V/µs
BW = 20 MHz
6V DC Offset
6V
100 mV/div, BW = 20 MHz
5.0V DC Offset
100 µs/div
The soft start-up feature gradually increases the output voltage when the LDO is first powered on.
By controlling the rate at which the output voltage rises, the soft-start feature helps prevent inrush
current, which can cause voltage drops or damage sensitive components in the circuit. Additionally,
it helps avoid overshoots, where the output voltage temporarily exceeds the desired level. The test
setup to check this functionality is identical to the one used for the line step tests if the start-up
is performed when the enable pin is tied together with the input pin. In this case, the oscilloscope
capture should include the input voltage curve and the output voltage signal, which should smoothly
rise to the desired voltage level, as shown in Figure 2-10. The start-up test can also be performed
using the shutdown functionality. While the supply is connected and turned on only at the VIN pin,
the signal generator is used to create a signal on the enable pin, from 0V up to the input voltage.
Using the oscilloscope, the enable and output signals should be observed.
Application Note DS00006030A - 9
 2019-2022 Microchip Technology Inc. and its subsidiaries DS20006229D-page 10

Figure 2-10. Start-up Oscilloscope Capture (MCP1792)
I = 10 mA
14V
Rise Slope = 1V/µs
2V/div
1V/Div
200 µs/div
A Load step describes how an LDO regulator reacts to sudden changes in the load current. This
parameter is important for assessing the transient performance of the LDO when the load demand
changes abruptly, such as when a device switches between different operating modes. A good
load step response is characterized by minimal output voltage deviation and quick recovery to the
nominal voltage. This ensures that the output voltage remains stable and within specified limits,
even during rapid changes in load conditions, which is critical for maintaining the performance and
reliability of the powered device.
To create a step in the load current, a programmable electronic load or a resistive load step board
can be used. An oscilloscope equipped with a current probe is required to record the output
current. In Figure 2-11, when performing the current step, the probe connected to CH1 will capture
the output voltage waveform, and the current probe on CH2 will capture the load current. In Figure
2-12, the transient response of MCP1792 is showcased.
Figure 2-11. Load Step Test Setup
Application Note DS00006030A - 10

Figure 2-12. Load Step Oscilloscope Capture (MCP1792)
100 mV/div, BW = 20 MHz
5V DC Offset
Step from 1 mA to 50 mA
I
20 mA/div
400 µs/div
2.3. AC Performance
Power Supply Rejection Ratio (PSRR) measures an LDO regulator's ability to suppress variations
in the input voltage from affecting the output voltage. It is typically expressed in decibels (dB) and
indicates how well the LDO can filter out noise and fluctuations from the power supply. High PSRR is
essential in sensitive analog and RF applications, where power supply noise can affect performance.
A high PSRR ensures that the output remains stable and clean, even when the input voltage is noisy
or fluctuating. Because LDOs typically have a good PSRR, they are often used to filter noise from
switching converters.
To test and measure this parameter, a sinusoidal signal is superimposed on the DC power supply
of the LDO, while a spectrum analyzer connected to both the input and the output of the LDO
measures and calculates how well the device can attenuate the induced signal. More information
about PSRR measurement, test setup and calculations can be found in the AN3018 Application Note.
Noise, in the context of LDO regulators, refers to unwanted electrical fluctuations or disturbances
in the output voltage. These can originate from various sources within the LDO, such as the voltage
reference, the resistive divider or the pass transistor. Low output noise is critical in applications like
precision analog circuits, audio equipment, and RF systems, where even small amounts of noise can
significantly impact performance. LDOs designed for low-noise applications often include features
like noise reduction capacitors and special internal design techniques to minimize output noise.
The AN5604 Application Note provides a comprehensive explanation of noise, including detailed
guidance on accurate measurement techniques. In the aforementioned paper, the MIC5319 is
used as an example to demonstrate how to measure and calculate noise in an LDO. This high-
performance device produces only 47 µVrms of noise in the 10 Hz-100 kHz frequency spectrum, a
value that is significantly improved with the use of a bypass capacitor that filters the internal voltage
reference of the device.
Application Note DS00006030A - 11

Figure 2-13. Noise vs. Frequency With and Without Bypass Capacitor (MIC5319)
10
1
0.1
0.01
0.001
0.01 0.1 1 10 100 1000 10000
Application Note DS00006030A - 12
)zH√/Vµ(
esioN
Without Cbypass
With Cbypass
V = 2.8V
V = 1.8V
I = 100 mA
LOAD
e (10 Hz-100 kHz) = 246 µVrms (Without C )
N BYPASS
e (10 Hz-100 kHz) = 47 µVrms (With C = 0.1 µF)
N BYPASS
Frequency (kHz)

Protections
3. Protections
In terms of protection, most of Microchip’s LDOs are equipped with thermal protection, short-circuit
protection (current-limit or foldback) and/or Undervoltage Lockout (UVLO).
Short-circuit protection in LDO regulators is designed to safeguard the device and the load from
excessive current that can occur during a short-circuit condition. This protection typically includes
a current-limit feature, which restricts the maximum output current to a safe level. Some LDOs
also incorporate foldback current-limiting, which further reduces the output current as the output
voltage drops, thereby minimizing power dissipation and thermal stress during a short-circuit.
These mechanisms ensure that the LDO can withstand fault conditions without sustaining damage,
enhancing the overall safety and robustness of the power supply system.
When checking the functionality of the short-circuit protection, the two principal parameters that
are measured are the peak short-circuit current (the maximum current value that flows through the
LDO for a fraction of a second before the protection activates) and the current-limit (the amount of
current that the LDO allows to pass throughout the entire duration of the short-circuit event) – also
called foldback current in the case of foldback current protection.
Thermal protection is a critical function in Low Dropout (LDO) regulators, designed to prevent
damage due to excessive heat. When the internal temperature of the LDO exceeds a certain
threshold, the thermal protection mechanism activates by shutting down the regulator entirely.
This function prevents the LDO from overheating, which could otherwise lead to permanent damage
or failure. Thermal protection is essential for maintaining the reliability and longevity of the LDO,
especially in applications where the regulator may be subjected to high power dissipation or
adverse thermal conditions.
Undervoltage Lockout (UVLO) is a protective feature in LDO regulators that prevents the device
from operating when the input voltage is too low. UVLO ensures that the LDO only turns on when
the input voltage exceeds a certain threshold, which is necessary for proper regulation. If the input
voltage falls below this threshold, the UVLO circuit disables the LDO to prevent erratic operation
and potential damage to both the regulator and the load. This function is crucial for maintaining
stable and reliable performance, particularly in applications where the input voltage may vary or
drop unexpectedly.
Application Note DS00006030A - 13

Board Layout Considerations
4. Board Layout Considerations
Designing a PCB layout for LDOs is as important as choosing the proper device for the intended
application. This process requires consideration of various factors to ensure optimal performance
and reliability. Proper PCB layout practices are essential to minimize noise, enhance stability and
ensure efficient thermal management.
The input and output capacitors should be placed as close as possible to the LDO. This proximity
minimizes the parasitic inductance and resistance in the traces, which can otherwise lead to
instability and degraded performance. The capacitors help filter out noise and provide a stable
voltage supply, ensuring the LDO operates efficiently. Placing these capacitors near the LDO
minimizes the risk of voltage drops and transient spikes, which could negatively impact the
regulated output.
The width of the routes and traces on the PCB should be appropriately sized to handle the current
rating of the LDO. Traces that are too narrow can lead to excessive heat buildup and potential
failure due to overheating or excessive voltage drops. Using wider traces helps to distribute the
current more effectively and reduces the resistance, ensuring that the LDO can deliver the required
current without significant losses. It is also important to consider the copper thickness of the PCB, as
thicker copper can carry higher current levels and improve overall thermal performance.
For adjustable versions of LDOs, the feedback divider should be kept as short as possible. The
feedback loop is critical for maintaining the desired output voltage. Any unnecessary length can
introduce noise and delay, leading to instability and inaccurate voltage regulation. By minimizing the
distance between the device and feedback resistors, you ensure that the feedback signal is clean
and responsive, which is essential for the precise operation of the LDO. Additionally, using a ground
plane can help to shield the feedback loop from external noise sources.
Heat dissipation is another important consideration when designing the PCB layout for LDOs. LDOs
can generate significant heat, especially when there is a large voltage drop between the input and
output. To manage this heat, it is essential to provide adequate thermal vias and copper areas
to dissipate the heat into the board. Placing the LDO on a large copper plane or using thermal
vias to connect to other layers can effectively dissipate heat, prevent hot spots and ensure reliable
operation.
Application Note DS00006030A - 14

Conclusions
5. Conclusions
This application note offers an in-depth analysis of the key parameters and functions of Low
Dropout Regulators (LDOs). The document includes detailed test configurations for measuring these
parameters and provides illustrative examples of expected results. The document outlines the
various aspects of LDO performance, such as line and load regulation, dropout voltage, quiescent
and ground current, transient response, power supply rejection ratio and noise, among others. By
presenting clear and structured methodologies for testing, it ensures that users can replicate the
procedures and obtain reliable data.
Furthermore, the application note emphasizes the critical importance of employing proper
measurement techniques and board layout considerations to ensure accurate assessment of the
device's performance.
Application Note DS00006030A - 15

References
6. References
Document Title Literature Available
Number
MCP1725 - Data Sheet DS20002026 www.microchip.com/en-us/product/MCP1725
MCP1754 - Data Sheet DS20002276 www.microchip.com/en-us/product/MCP1754
MCP1792 - Data Sheet DS20006229 www.microchip.com/en-us/product/MCP1792
MCP1824 - Data Sheet DS20002070 www.microchip.com/en-us/product/MCP1824
MIC5309 - Data Sheet DS20006741 www.microchip.com/en-us/product/MIC5309
MIC5319 - Data Sheet DS20005876 www.microchip.com/en-us/product/MIC5319
Designing With Low-Dropout Voltage — ww1.microchip.com/downloads/en/devicedoc/ldobk.pdf
Regulators
AN3018 - MIC47050 - Power Supply DS00003018A www.microchip.com/en-us/application-notes/an3018
Rejection Ratio of Low Dropout Voltage
Regulators
AN5604 - Strategies for Noise Reduction DS00005604A www.microchip.com/en-us/application-notes/an5604
in Fixed and Adjustable LDOs
Application Note DS00006030A - 16

Revision History
7. Revision History
The revision history describes the changes that have been implemented in the document. The
changes are listed by revision, starting with the most current publication.
Revision Date Section Description
A 06/2025 Initial Revision
Application Note DS00006030A - 17

Microchip Information
Trademarks
The “Microchip” name and logo, the “M” logo, and other names, logos, and brands are registered
and unregistered trademarks of Microchip Technology Incorporated or its affiliates and/or
subsidiaries in the United States and/or other countries (“Microchip Trademarks”). Information
regarding Microchip Trademarks can be found at https://www.microchip.com/en-us/about/legal-
information/microchip-trademarks.
ISBN: 979-8-3371-1398-2
Legal Notice
This publication and the information herein may be used only with Microchip products, including
to design, test, and integrate Microchip products with your application. Use of this information
in any other manner violates these terms. Information regarding device applications is provided
only for your convenience and may be superseded by updates. It is your responsibility to ensure
that your application meets with your specifications. Contact your local Microchip sales office for
additional support or, obtain additional support at www.microchip.com/en-us/support/design-help/
client-support-services.
THIS INFORMATION IS PROVIDED BY MICROCHIP “AS IS”. MICROCHIP MAKES NO REPRESENTATIONS
OR WARRANTIES OF ANY KIND WHETHER EXPRESS OR IMPLIED, WRITTEN OR ORAL, STATUTORY
OR OTHERWISE, RELATED TO THE INFORMATION INCLUDING BUT NOT LIMITED TO ANY IMPLIED
WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A PARTICULAR
PURPOSE, OR WARRANTIES RELATED TO ITS CONDITION, QUALITY, OR PERFORMANCE.
IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE, INCIDENTAL, OR
CONSEQUENTIAL LOSS, DAMAGE, COST, OR EXPENSE OF ANY KIND WHATSOEVER RELATED TO THE
INFORMATION OR ITS USE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS BEEN ADVISED OF THE
POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE FULLEST EXTENT ALLOWED BY LAW,
MICROCHIP’S TOTAL LIABILITY ON ALL CLAIMS IN ANY WAY RELATED TO THE INFORMATION OR
ITS USE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY, THAT YOU HAVE PAID DIRECTLY TO
MICROCHIP FOR THE INFORMATION.
Use of Microchip devices in life support and/or safety applications is entirely at the buyer’s risk,
and the buyer agrees to defend, indemnify and hold harmless Microchip from any and all damages,
claims, suits, or expenses resulting from such use. No licenses are conveyed, implicitly or otherwise,
under any Microchip intellectual property rights unless otherwise stated.
Microchip Devices Code Protection Feature
Note the following details of the code protection feature on Microchip products:
• Microchip products meet the specifications contained in their particular Microchip Data Sheet.
• Microchip believes that its family of products is secure when used in the intended manner, within
operating specifications, and under normal conditions.
• Microchip values and aggressively protects its intellectual property rights. Attempts to breach the
code protection features of Microchip products are strictly prohibited and may violate the Digital
Millennium Copyright Act.
• Neither Microchip nor any other semiconductor manufacturer can guarantee the security of its
code. Code protection does not mean that we are guaranteeing the product is “unbreakable”.
Code protection is constantly evolving. Microchip is committed to continuously improving the
code protection features of our products.
Application Note DS00006030A - 18