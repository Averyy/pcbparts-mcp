---
source: "Wurth ANP121 -- Filter and Surge Protection for I2C Bus"
url: "https://www.we-online.com/components/media/o734709v410%20ANP121a%20%20Filter%20and%20surge%20protection%20for%20I2C%20Bus%20EN.pdf"
format: "PDF 7pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 10218
---

APPLICATION NOTE
ANP121 | Filter and surge protection for I2C Bus
Andreas Nadler
INTRODUCTION OVERVIEW I²C SPECIFICATIONS
The I²C (Inter-Integrated Circuit) bus is a popular serial Max. Rise
Max. Data Max. Bus Max.
communication interface on many circuit boards. It is mainly Mode CLK Time
Rate Capacitance Current
used to connect microcontrollers with peripheral ICs 0.3 – 0.7 VCC
(e.g. sensors or memory). The bus uses a bidirectional data
Standard 100 kHz 100 kBit/s 1000 ns 400 pF 3 mA
line (SCL) and clock line (SDA) respectively. However, the I²C
Fast 400 kHz 400 kBit/s 300 ns 400 pF 3 mA
bus is not only used on circuit boards. In many applications,
the I²C bus is extended into other areas using various Fast + 1 MHz 1 MBit/s 120 ns 550 pF 20 mA
connectors and cables. This makes the I²C bus potentially High
3.4 MHz 3.4 MBit/s 10 ns 100 pF 3 mA
more susceptible to external interference such as ESD, burst Speed
and radiated RF. The goal of this application note is to show
Table 1: Overview I2C bus specifications
the reader a suitable filter and protection circuit that increases
the noise immunity of the I²C bus without sacrificing the PULL-UP RESISTORS, BUS CAPACITANCE
signal quality of the data and clock lines. For this purpose, AND RISE TIME
simulation models were created in LTspice and a real
All ICs that participate in the I²C bus have open collector
application was measured to verify the simulation results.
outputs. These switch the pull-up resistors alternately to
OVERVIEW I2C BUS reference ground and thus generate the logical states
"1"(VCC) and "0"(GND). As can be seen in Table 1, the
maximum permissible edge rise times decrease as the data
rate increases. The mathematical relationship of the
min./max. values for the pull-up resistors is as follows:
(V CC - V L ) (1)
R =
Pullup_min I
Pullup
t
r (2)
R =
Pullup_max (0.8473 · C )
Bus
: Simplified block diagram I2C bus VCC = Reference voltage level of the I²C-Bus (Volt)
The I²C operates according to the "master-slave" principle,
VL = Maximum logic „0“ threshold level
whereby the master always initiates the data transfer. Due to
(e.g. 0.4 V at VCC > 2 V) (Volt)
its low complexity, the bus has achieved a wide distribution.
CBus = Maximum parasitic bus capacitance of the
application (Farad)
However, the protocol is very simple, and the physical
topology is only single-ended. In practice, both of these
tr = Maximum allowed rise time (depending on data rate)
(seconds)
factors mean that the bus can be very susceptible to external
interference (e.g. during EMC tests).
IPullup = Maximum possible current through the open
collector pins (Amps)
ANP121a | 2023/02/03 1 | 7
WÜRTH ELEKTRONIK eiSos www.we-online.com

The pull-up resistors in combination with the parasitic bus During an ESD test, for example, a current of more than 10 A
capacitance form an RC element. This leads to a delay of the can flow briefly, which then leaves a voltage of about 10 V at
edge rise time of the square signal. In many applications, this this diode. All other ICs on the I²C bus must then withstand
RC element is often the limiting factor regarding the this voltage. This only works if a low-impedance ground (e.g.
maximum possible data rate and cable length. As shown in large copper area in an inner layer) is provided to avoid a
Table 1, the I²C specification therefore results in a maximum further voltage drop.
bus capacitance of 400 pF at 3 mA current for the most
commonly used data rates (100 kBit/s & 400 kBit/s). The
LTSPICE SIMULATION WITH 400 KHZ
CLOCK RATE
smaller the pull-up values are selected, the shorter the edge
rise time can become. As can be seen in equation (1), the
With the help of the free simulation program LTspice it is
lower limit determines the maximum logic low threshold, the
relatively easy to investigate the influence of the parasitic bus
voltage reference level and the maximum possible current.
capacitance in combination with the selected pull-up
resistors. In order to generate the desired useful signals, it is
The parasitic bus capacitance depends on, among other
advisable to use a voltage-controlled switch. With the help of
things:
the voltage source practically any periodic signal can be
 Component capacitance generated. For this purpose, the "Pulse" function is selected
 Length and width of traces (approx. 0.5 pF/cm) and the desired bandwidth is determined on the basis of the
 Length, type of cable and connectors desired I²C specification. For the widely used 400 kBit/s
 Layer structure and dielectric constant of the PCBs variant, a period duration of 2.5 µs is selected. For a 50% duty
cycle, the "high" time is set to 1.25 µs. In order to determine
SELECTION OF THE FILTER AND OVER
the edge steepness of the signal, one needs to get the rise
VOLTAGE PROTECTION COMPONENTS
times from the datasheets of the ICs being used on the bus.
To be able to use the maximum allowed 400 pF parasitic bus
capacitance, the pull-ups were set to 1 kΩ. Three channels
(may represent SCL or SDA in practice) are simulated:
 Without parasitic bus capacitance
 400 pF parasitic bus capacitance
 400 pF + wideband multilayer SMT ferrite (742792693)
: I²C bus including interface protection for improved noise
immunity and reduced interference emission
To increase immunity to ESD, burst and radiated RF, a
combination of SMT ferrites plus TVS diodes can be used.
Wideband SMT ferrites (e.g. 742792693) continuously build
up impedance above 10 MHz and are therefore able to
protect the bus against high-frequency interference.
Overvoltages can also be effectively diverted to reference
ground by the TVS diodes.
Since the values of the pull-up resistors are often in the kΩ
range, the RDC as well as the impedance of SMT ferrites
below 10 MHz only play a minor role here. Thus, in a first
consideration, it can be assumed that the edge rise time of
the useful signal is hardly influenced in practice. If suitable
: Schematic LTspice simulation with 3 channels  0 pF,
TVS diodes with low capacitance (e.g. 824012823 - 0.18 pF)
400 pF & 400 pF + Multilayer SMT Ferrite
are selected, their component capacitance also has no
relevant influence on the signal quality.
ANP121a | 2023/02/03 2 | 7

: LTspice simulation result time domain 0 pF (Turquoise), 400 pF (Blue) & 400 pF+ Multilayer SMT Ferrite (Red)
The simulation result shows that practically no influence on This kit consists of a master board, which contains the
the rise time of the signal can be expected from the multilayer microcontroller. The other two contain a WE Bluetooth
SMT ferrite. Because each multilayer SMT ferrite also has an module and various WE sensors (3-axis acceleration,
inductance component, minor oscillations are visible in temperature, humidity, pressure). The master board
combination with the bus capacitance. However, these are communicates with the other two via I²C bus at a maximum
not critical because their amplitudes are less than 10% of the data rate of 400 kBit/s. The sensor data can then be
actual useful signal. In the real measurements, these visualized with a suitable smartphone app (WE-SensorBLE).
oscillations are significantly lower. A parasitic capacitance of 400 pF with respect to GND was
simulated using MLCCs. The same multilayer SMT ferrite
MEASUREMENT OF A REAL
(742792693) was used as in the simulation, plus a TVS diode
APPLICATION WITH 400 KHZ CLOCK RATE
array (824012823). In addition, 20 cm of cable was used to
connect the sensor board to the rest of the I²C. Such an
To verify the relatively simple LTspice simulation, additional
arrangement can be observed in many applications in
measurements were performed on a Würth Elektronik
practice.
SensorBLE FeatherWing Kit. (Figure 5)
: Block diagram test setup with Würth Elektronik SensorBLE
FeatherWing Kit
The voltage curve on the SCL line was always measured.
: Würth Elektronik SensorBLE FeatherWing Kit
ANP121a | 2023/02/03 3 | 7

: Reference measurement with 1 kΩ pull-ups without further changes of the used FeatherWing hardware (= 46 ns rise time).
: Reference measurement with 1 kΩ pull-ups + multilayer SMT ferrite + TVS diode array + 20 cm cable (= 46 ns rise time)
ANP121a | 2023/02/03 4 | 7

: Reference measurement with 1 kΩ pull-ups + multilayer SMT ferrite + TVS diode array + 20 cm cable + 400 pF MLCCs
(= 344 ns rise time)
The measurements show practically identical results to the SUMMARY
simulation. The rise time and signal quality are not
In this application note it was shown by simulation and
negatively affected by the multilayer SMT ferrite in
measurement that SMT multilayer ferrites in combination
combination with the TVS diode. The rise time of the high
with ESD protection diodes practically do not influence the
signal, which is critical for the timing, depends only on the
data signal (SDA) and clock signal (SCL) of the I²C bus. The
bus capacitance in combination with the selected pull-up
edge steepness of the signals is mostly influenced by the
resistors. Using the smartphone app (WE-SensorBLE), error-
pull-up resistors in combination with the parasitic bus
free operation could be verified in all three tested scenarios.
capacitance. In return, this component combination of ESD
protection diode and broadband SMT ferrite increases the
noise immunity of the I²C bus. In practice, this means a
higher immunity to ESD, burst and radiated RF.
ANP121a | 2023/02/03 5 | 7

A Appendix
A.1 Bill of material (BOM)
Index Description Value Size Order code
L WE-CBF Wide Band SMT Ferrite Z = 2.2 kΩ @ 100 MHz 0603 742792693
WE-TVS Super Speed TVS Diode Array,
D VCC = 3.3 V DFN1210 824012823
2 channel ESD Protection,
A.2 Relevant standards
ESD Test: DIN EN 61000-4-2 / IEC 61000-4-2
Burst Test: DIN EN 61000-4-4 / IEC 61000-4-4
Eingestrahlte HF: DIN EN 61000-4-3 / IEC 61000-4-3
A.3 References
SLVA689 – I2C Bus Pull-up Resistor Calculation
ANP121a | 2023/02/03 6 | 7
