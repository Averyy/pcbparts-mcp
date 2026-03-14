---
source: "TI SLUA456 -- Single Cell Gas Gauge Circuit Design"
url: "https://www.ti.com/lit/pdf/slua456"
format: "PDF 6pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 10891
---

Application Report

Single Cell Gas Gauge Circuit Design
Michael Vega and Ming Yu........................................... Battery Management
ABSTRACT
Components included in single-cell gas gauge circuit designs are explained in this
application report. Design analysis and suggested tradeoffs are provided, where
appropriate.
Contents
1 Introduction ............................................. 1
2 High-Current Path ......................................... 1
3 Gas Gauge Circuit.......................................... 3
4 Current and Voltage Protection.................................. 5
5 Reference Design Schematic ................................... 5
List of Figures
1 Protection FETs........................................... 2
2 Sense Resistor............................................ 3
3 Differential Filter .......................................... 3
4 ESD Protection for Communication Using Zener Diodes ................... 4
1 Introduction
The Single-Cell Gas Gauge circuit has approximately 15-20 components in the reference design for a
1-thermistor, 1-cell application. For clarity, these chipsets are grouped into the following classifications:
High-Current Path, Gas Gauge Circuit, Current and Voltage Protection.
The discussion is based on the single-cell reference design for the bq275xx chipset. A complete
schematic is available on the last page of this document.
2 High-Current Path
The high-current path begins at the PACK+ terminal of the battery pack. As charge current travels through
the pack, it finds its way through the lithium-ion cell and cell connections, the sense resistor, protection
FETs and then returns to the PACK– terminal (see the reference design schematic at the end of this
document). In addition, some components are placed across the PACK+ and PACK– terminals to reduce
effects from electrostatic discharge.
2.1 Protection FETs
The N-channel charge and discharge FETs should be selected for a given application. Most portable
battery applications are a good match for the Si6926ADQ or equivalent.
The Vishay Si6926ADQ is packaged with two 4.1-A , 20-V devices with Rds(on) of 33mW when the gate
drive voltage is 3V.
Impedance Track is a trademark of Texas Instruments.

High-Current Path
Capacitors C2 and C3 help to protect the FETs during an ESD event. The use of two devices ensures
normal operation if one of them becomes shorted. In order to have good ESD protection, the copper trace
inductance of the capacitor leads must be designed to be as short and wide as possible. Ensure that the
voltage rating of both C2 and C3 are adequate to hold off the applied voltage if one of the capacitors
becomes shorted.
R1
0.01 W
4 5
2 1 8 6
3 7
Q4:A Q4:B
SI6926ADQ SI6926ADQ
C2 C3
0.1 mF 0.1 mF
Figure 1. Protection FETs
2.2 Lithium-Ion Cell Connections
The important thing to remember about the cell connections is that high current flows through the top and
bottom connections, and therefore the voltage sense leads at these points must be made with a Kelvin
connection to avoid any errors due to a drop in the high-current copper trace. This is critical for gauging
accuracy in the Impedance Track™ gauges.
2.3 Sense Resistor
As with the cell connections, the quality of the Kelvin connections at the sense resistor is critical. Not only
the sense lines, but the single-point connection to the low-current ground system must be made here in a
careful manner.
The sense resistor should have a temperature coefficient no greater than 100 ppm in order to minimize
current measurement drift with temperature. The sense resistor value should be sized to accurately
integrate the charge and discharge current that the system draws in its ON state. The maximum
sense-resistor voltage that can be measured accurately by the coulomb counter is – 125 mV. The designer
should ensure that the voltage across the sense resistor at maximum currents is less than this limit. It is
often the power dissipation in the resistor at maximum load currents that sets the maximum acceptable
sense-resistor value, particularly when space considerations restrict the maximum size allowable for the
resistor. The physical size, power dissipation, and insertion loss (voltage drop) considerations of the sense
resistor dictate that the smallest possible sense-resistor value be used. This has to be balanced against
the accuracy requirements at low currents (slightly above the SLEEP threshold), where the sense-resistor
voltage at minimum load currents might not be much larger than the measurement offset error if the
sense-resistor value is too small. For a single-cell application, 10 mW is generally ideal .

Gas Gauge Circuit
R1
100 ppm
.010
Figure 2. Sense Resistor
2.4 ESD Mitigation
A pair of series 0.1-m F ceramic capacitors is placed across the PACK+ and PACK– terminals to help in
the mitigation of external electrostatic discharges. The two devices in series ensure continued operation of
the pack if one of the capacitors should become shorted.
3 Gas Gauge Circuit
The Gas Gauge Circuit includes the bq275xx and its peripheral components. These components are
divided into the following groups: Differential Low Pass Filter, Power Supply Decoupling/ and I2C
Communication.
3.1 Differential Low Pass Filter
As shown in Figure 3, a differential filter should precede the current sense inputs of the gas gauge. This
filter eliminates the effect of unwanted digital noise, which could cause offset in the measured current.
Even the best differential amplifier has less common-mode rejection at high frequencies. Without a filter,
the amplifier input stage may rectify a strong RF signal, which then may appear as a dc offset error.
Five percent tolerance of the components is adequate because capacitor C6 shunts C3/C7 and reduces
AC common-mode arising from component mismatch. It is important to locate C6 as close as possible to
the gas gauge pins. The other components also should be relatively close to the IC. The ground
connection of C3 and C7 should be close to the IC.
Figure 3. Differential Filter
3.2 Power Supply Decoupling
Power supply decoupling is important for optimal operation of the single cell gas gauges. A single 0.1-m F
ceramic decoupling capacitor from V to V must be placed adjacent to the IC pins.
CC SS

Gas Gauge Circuit
3.3 I2C Communication
The I2C clock and data signals interface to the outside world on the pack connector. With pack-side gas
gauge implementation, each signal employs an ESD protection scheme consisting of a zener diode with
it's anode connected to PACK–. A resistor is placed between the Zener diode and the external
communication pin. Another resistor is placed between the IC's communication pin and the Zener diode.
These two resistors limit the current that goes through the Zener in the event of ESD. It should be noted,
however, that the Zener diodes must have nominal capacitance below 150 pF in order to meet the I2C
specifications. The AZ23C5V6 is a recommended device. Also, the resistor on the pack side is only 100 W
to maintain signal integrity. Note that the Zener diode will not survive a long-term short to a high voltage. If
it is desirable to provide increased protection with a larger input resistor and/or Zener diode; carefully
investigate the signal quality of the I2C signals under worst-case communication conditions.
Resistors R22 and R23 provide pulldown for the communication lines. When the gas gauge senses that
both lines are low (such as during removal of the pack), the device performs auto offset calibration and
then goes into sleep mode to conserve power.
For the I2C clock signal, R19 and part of D8 provide clamping for positive ESD pulses, while R18 limits the
current coming out of the IC (in parallel with the current through D8) for negative ESD pulses.
Figure 4. ESD Protection for Communication Using Zener Diodes
Some designers may want to use capacitors instead of Zener diodes to save board space or part cost.
This can be acomplished by replacing the Zener diodes with a pair of 150-pF capacitors. If using the
capacitors, R18 and R20 should be replaced with 300W resistors.
3.4 Cell and Battery Input
Also, as described previously in the High Current Path section, the top and bottom nodes of the cells must
be sensed at the battery connections with a Kelvin connection to prevent voltage sensing errors caused by
a drop in the high-current PCB copper.
3.5 BAT Pin Input
The BAT pin which is the input to the A/D converter that measures battery voltage, only requires a 0.1m F
ceramic capacitor due to that adding a resistor in series with the pin will cause errors on the measurment.
The pin actually gives access to a voltage divider before reaching the actual A/D input. Any additional
resistance to the pin will alter the voltage divider ratio and lead to measurement errors.
3.6 Regulator Output
A low dropout regulator whether external or internal to gas gauge IC, requires capacitive compensation on
their outputs. The 2.5V REG output should have a 0.47-m F ceramic capacitor placed close to the IC
terminal.

Current and Voltage Protection
3.7 Temperature Output
TOUT provides thermistor drive under program control. The reference design includes one NTC103AT
10-kW thermistor, RT1. Because these thermistors are normally external to the board, the ceramic
capacitors are provided for ESD protection and measurement smoothing.
4 Current and Voltage Protection
The current and voltage protection is done by a circuit consisting of a cell protector IC and two NFETs.
The protector drives one FET to enable a discharge path and drives the second FET to enable a charge
path. The protector monitors the cell voltage through its Vdd pin and disables the charge FET whenever
the voltage is greater than the Over-Voltage threshold. If the voltage is below the Under-Voltage threshold
it will disable the discharge FET. The protector monitors current by measuring voltage across the two
FETs with respect to protector's Vss. If it detects voltages surpassing the Over-Current thresholds it will
disable the corresponding FET depending on the polarity of the voltage with respect to Vss. The protector
will recover from a fault when opposing conditions are present. For example if under voltage is detected
(over discharge condition) then it will not recover until a charger is applied to the pack.
Design considerations for the protector circuit is based on the protector being used. Given that
over-current conditions are really dependent on voltage across the FET, then the actual current thresholds
will depend on the Rds on of the NFETs used in design. See the reference design for an example of a
protector IC design.
5 Reference Design Schematic
