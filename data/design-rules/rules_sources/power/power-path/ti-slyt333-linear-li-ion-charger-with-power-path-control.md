---
source: "TI SLYT333 -- Linear Li-Ion Charger with Power-Path Control"
url: "https://www.ti.com/lit/an/slyt333/slyt333.pdf"
format: "PDF 9pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 17347
---

Designing a linear Li-Ion battery charger
with power-path control
By Charles Mauney
Senior Systems/Applications Engineer,
Battery Management and Charging Solutions
In theory, a linear battery charger with a sepa-
Figure 1. Power-path topology of battery charger
rate power path for the system is a fairly simple
design concept and can be built with an LDO
adjusted to 4.2 V; a current-limit resistor; three
Adapter or Internal to IC
p-channel FETs to switch the system load USB Input Q1
V
between the input power and the battery source; OUT
VIN
and some bias parts. In reality, there is much
more to a good design than the basic topology.
This article will discuss dynamic power-path Charger Q2 RSystem
management (DPPM) and explore safety features Control Loops,
Logic, and
that turn a basic topology into a complete design.
Drives
The DPPM topology is shown in Figure 1 and
has two power-source pins,V and V . The V
IN BAT Program Input for USB or BAT
charger can be programmed for either a USB
Adapter Current Sense
Battery
input or an adapter input. The design concept is on Input, Input Control Loops,
to always power the system if power is available, and Drives
either from V IN or V BAT , unless the system is pro- GND
GND
grammed to shut down. The input FET regulates
1
the output voltage and will also limit the input
current to the programmed level if the load is
excessive. The battery FET has control loops
associated with charging the
battery and allowing the
Figure 2. Discrete charger with battery-supplement mode
battery to power the system.
The input controls and bat-
tery controls act indepen- R
Limit 4.2 VDC
dently and are discussed in V V
IN OUT
more detail later.
LDO
Figure 2 shows a charger
Adj. R5
solution with a discrete
power path. The LDO pro-
vides the regulated output
Q2 Q3
voltage, and the input-
current-limit resistor limits
the maximum current that V IN+ R2
can be delivered to the bat-
Input R3
tery. D1, R1, R4, and Q1 Source D1
monitor the input voltage and
(VDC) Zener
turn on Q2 and Q3 if input GND Q4 R
System
source power is present,
R7
connecting the input to the R4 Q5
system load. If input source
Q1
power is not present, Q5 and
R6
Q4 are biased on so the bat-
R1 Battery
tery will provide power to the
system load. This state will
hereinafter be referred to as 1
“battery-supplement mode.”
This charger solution is simple and discrete
Figure 3. Typical integrated application with
but has many limitations and few safety features.
bq24075 charger
Adding any safety feature will quickly drive up
the solution cost but often may offset the liabil-
ity cost of an unprotected design. LDOs are typ- 1 k
ically not highly accurate regulators, especially 1 k
with external programmable resistors. If the
regulation was set lower to ensure that the maxi-
7 9
mum battery voltage was not exceeded, the typ-
PGOOD CHG
ical voltage and capacity would be lower. The bq24075
V to
crude current-limit resistor would allow more 13 IN OUT 10 S O y U s T tem
current at lower battery voltages and would not IN 11
provide a conditioning current to help recover 1 µF 4.7 µF
8 EN2 5
depleted cells or to prevent cell damage from VSS
excessive charging. V BAT 2
System 3
15
Typical integrated application On/Off SYSOFF 4.7 µF
Control
Figure 3 shows the Texas Instruments (TI) Temp Pack+
TS
bq24075, a charger with a highly integrated
CE TMR EN1 ILM ISET
+
power path in a 3 × 3-mm, 16-pin QFN package. 4 14 6 12 16 –
The only external components required are two
1.18 k 1.13 k Pack–
external programming resistors and three capaci-
tors for the power sources.
Programmed input-source protection
The input-current limit is programmed with the
EN1/2 pins to one of four states: 100 mA, 500 mA,
ILIM, or Suspend, as shown in Figure 4. A resistor can be
used to program ILIM at any level up to the device’s maxi-
mum input current. When current-limited, the input FET
restricts the current to the OUT pin, causing the system
voltage to drop to the DPPM threshold or to the battery
voltage where the charge current will be reduced. Assum-
ing that the protection was designed for the applied
bq24075
Q1
EN2
Short
–
Detect
USB 100 mA
USB 500 mA –
ILIM
USB Suspend
EN2
EN1
Charge Pump
–
source, this feature solves the problem of the system
overloading the adapter or the USB source, which could
potentially damage the source or device. More power-
management details are presented later under “DPPM
protection of output voltage.”
If a current-limited source such as a weak or wrong
adapter or USB is used, the adapter and system voltages
Figure 4. Input-FET control loops
IN_Low
REF_ILIM
OUT_Reg

will drop, causing the IC to enter DPPM mode or battery- be restricted by the source, the V loop, or the input-
supplement mode. Basing DPPM on the output voltage current-limit setting of the IC. If the output voltage drops
solves most loading issues by reducing the charge current, to the DPPM threshold, the charge current will be reduced
giving priority to the system load, and allowing operation to keep the voltage from further decay. This allows the use
with a weak power source or minor AC brownouts. Other of a less expensive adapter because the charging current
input-current-management solutions without DPPM would is reduced during peak loads.
not detect the weak source or reduce the charging current, If the system current exceeds the available input current,
and the system would crash. the output voltage will drop to the battery voltage and
The V input loop provides additional protection for enter battery-supplement mode, in which the battery FET
a weak source when in USB 100/500-mA mode. This loop turns on and supplements the input current going to the
monitors the voltage on the USB input pin; and, if it drops system. This allows use of the battery to supplement large
to ~4.5 V, Q2 enters its linear range to keep the USB input current pulses to the system, which the charger is not
voltage from dropping any further, as shown in Figure 5. capable of supplying. Figures 6 through 8 show the wave-
This voltage loop is independent of the input-current-limit forms of the TI bq24072/3/4/5 where the output voltage
loop. This feature adds protection for the USB host in the drops first into DPPM mode and then into battery-
event that it cannot deliver the load current because of a supplement mode.
weak source or failed communication. In Figure 5, I Figure 6 shows the waveforms of the bq24072 with V
OUT OUT
starts with no load and, at ~250 mA, the current limit of initially regulated to about 225 mV above the battery volt-
the weak source causes the source voltage to fall to 4.5 V, age. Upon reaching the input-current limit after the first
where the V loop kicks in and the system output load step, the IC enters DPPM mode, which reduces the
voltage drops about 100 mV to the DPPM threshold. The charge current to keep the output voltage from dropping
charge current is reduced as the load is increased to main- below the DPPM threshold. After the second load step,
tain the input at 4.5 V. As the load is reduced, the system the system load is greater than the input limit. The output
returns to normal operation. voltage drops to just below the battery voltage, and the
battery FET turns on and supplements the input current to
DPPM protection of output voltage
The output voltage powering the system will drop if the the system load. Note that the voltage transitions between
system load current and the battery charge current modes are very small and are best for applications that are
exceed the available input current. The input current can sensitive to voltage changes.
Figure 5. V USB protection with source- Figure 6. bq24072 DPPM and battery-
current limit at 250 mA supplement modes with V ≈ 3.1 V
BAT
VIN (1 V/div) VIN (1 V/div)
DPPM Mode
VOUT (1 V/div)
Su
B
p
a
t
l
t
e
m
ry
-
nt
Mode
DPPM Mode VOUT
(1 V/div)
IBAT (1A/div)
IBAT (1A/div) IOUT (1A/div)
1 1
VOUT = 3.325 V
3 IOUT (1A/div) VBAT ~~ 3.1 V
DPPM at 3.225 V
Time (100 ms/div) Time (200 ms/div)

The waveforms of the bq24073/4 in Figure 7 were gen- 90 mA to the output via the input control loop; and,
erated under the same conditions as for the bq24072 in approximately every 64 ms, the battery FET is turned on
Figure 6, except that the bq24073/4 regulates V at for 250 µs to check whether the short is still present.
OUT
4.4 V and the DPPM threshold at 4.3 V. Upon entering
Picking the right charger IC
battery-supplement mode, the output voltage drops to just The bq24072/3/4/5 ICs all charge a single-cell Li-Ion battery
below the battery voltage; so the lower the battery voltage properly, but they have various values for the overvoltage-
is, the larger the drop. For an application sensitive to sys- protection (OVP) threshold, the V regulation, and the
tem voltage drops, the system load should not exceed the DPPM threshold (see Table 1). Each IC also has an
available input current in order to stay out of battery-
supplement mode. An alternative is to use the bq24072.
The bq24075 waveforms in Figure 8 were generated Figure 8. bq24075 DPPM and battery-
under the same conditions as for the bq24072 in Figure 6, supplement modes with V OUT = 5.5 V
except that the bq24075 regulates V at 5.5 V and the
DPPM threshold at 4.3 V. The transition between modes is VOUT (2 V/div)
larger and dependent on the input voltage and battery volt-
age. If the input voltage is less than 5.5 V, then the regula-
tor is switched fully on to deliver what voltage is available. (2 V V B / A d T iv) Su B p a p t l t e e m ry e - nt
Protection from shorting system V
OUT 1 DPPM Mode
Shorting the V pin can cause excessive current from
the battery or the V power source. Battery short-circuit
IN
protection disables the battery FET if the voltage drop
from V BAT to V OUT is greater than 250 mV for a duration IBAT (1A/div) IOUT (1A/div)
longer than the specified deglitch time. The battery FET is
3
turned on periodically to check whether the short is still
present, and this hiccup mode will continue until the short
VOUT = 5.5 V
is removed. This prevents damage to the IC and solves DPPM at 4.3 V
reliability issues.
Time (100 ms/div)
For V protection, the input FET limits the input current
to 100 mA when the output voltage is less than 1 V. Once
the excessive load is removed, the output will charge above
1 V and start delivering the programmed input current. Figure 9. Output short-circuit protection
This feature reduces the power dissipation during the out-
put short, which also improves reliability. Figure 9 shows
the waveforms of an output short and the IC’s recovery.
Figure 9 shows the waveforms that occur when the VOUT (2 V/div) VBAT (2 V/div)
bq24072’s output is shorted, causing the battery FET and
input FET to turn off. The input source supplies about
Figure 7. bq24073/4 DPPM and battery- V C O ir U c T u S it h S o t r a t rts H St ic a c tu u s p
Check
supplement modes with V = 4.4 V
VBAT (2 V/div)
3 IOUT (1A/div)
VOUT
(2 V/div)
Battery-Supplement
DPPM Mode Time (20 ms/div)
Table 1. Differences between bq24072/3/4/5 ICs
IOUT (1A/div)
DEVICE V V V
OPTIONAL
OVP OUT DPPM FUNCTION
3
bq24072 6 .6 V V + 225 mV V – 100 mV TD
BAT O(REG)
VOUT = 4.4 V
bq24073 6 .6 V 4 .4 V V – 100 mV TD
DPPM at 4.3 V O(REG)
bq24074 10 .5 V 4 .4 V V – 100 mV ITERM
O(REG)
Time (100 ms/div)
bq24075 6 .6 V 5 .5 V 4 .3 V SYSOFF

optional control function such as termination
Figure 10. Output voltage with changes in operational mode
disable (TD), programmable termination
and part number (V = 5 V)
current (ITERM), or system off (SYSOFF). IN
The 10.5-V OVP is for a nonregulated 5-V
adapter where the unloaded source is above
5
6.6 V. To minimize power dissipation, during
Normal Mode
fast charge the optimum input voltage 4.8
DPPM Mode
should be between 4.5 and 5.5 V.
The bar chart in Figure 10 shows graphi- 4.6
cally how the charger output voltage changes
4.4
from one operational mode to another for )V
each charger. If the system is sensitive to (
e 4.2
g
changes in the output voltage and the peak a
system load exceeds the input current, the V
olt
4
bq24072 minimizes these changes since it ut
regulates the output voltage to within 225 mV ut 3.8
O
of the battery voltage. The bq24073/4 regu-
3.6
lates the output voltage to 4.4 V and the
DPPM threshold to 4.3 V. Depend ing on the
3.4
battery voltage, the voltage drop can be large
when the charger enters battery-supplement 3.2
mode. The bq24075 regulates the output
voltage to 5.5 V for inputs greater than 5.5 V 3
bq24072 bq24073/4 bq24075
and passes through lower voltages. If the
charger output current plus the charge
current exceed the input current, the output
voltage will drop much more than 100 mV,
as shown in Figure 10. A further increase in
Figure 11. System efficiency with changes in operational
output current may put the device in mode and part number (V = 5 V. For V , see Figure 10.)
battery-supplement mode, where another
large drop will occur.
Figure 11 shows the efficiency of the 100
power topology. Efficiency for a linear Normal Mode
topology is 90 DPPM Mode
η = V IN − V OUT ×100. 80 Mode
70
Each charger mode has an efficiency factor.
For the bq24072/3/4/5, the efficiency during (
)%
60
y
battery-supplement mode is the same given c
the same input voltage and battery voltage. ci e n 50
The bq24072 has the least change in
Effi
40
output voltage between modes, but the
effic iency drops as the battery discharges. 30
The bq24073/4 is more efficient in normal
20
and DPPM modes but may have a larger
internal voltage drop upon entering battery-
10
supplement mode. The bq24075 has high
efficiency in normal mode and good effi- 0
ciency in DPPM mode, but it may have a bq24072 bq24073/4 bq24075
large change in output voltage after switch-
ing from normal to DPPM to battery-
supplement mode.
The decision for the designer is whether the charger the modes with large voltage steps? Because of the low
should be sensitive to system voltage changes, have lower power drain from the adapter or USB source, efficiency is
efficiency, or both. If the charger is sensitive to voltage not typically a cost concern, but it can be a heat-dissipation
changes, will the system operations cause changes between issue in the device.

Simple, single-cell, integrated Li-Ion chargers been given of the safety features of a simple charger,
followed by a more detailed description of DPPM. The
For designs where power-path control is not necessary,
bq24072/3/4/5 chargers provide three levels of input-
the TI bq2401x, bq2402x, and bq2406x families of single-
current-limiting protection that can be programmed to
cell Li-Ion chargers perform complete charging with all the
protect the specified source. The USB V loop pro-
necessary safety features. IN_Low
vides additional protection by detecting weak USB sources
The bq2406x family incorporates many of the same
and restricting the input current. The output DPPM loop
features found in the bq24072/3/4/5 family, but without the
reduces the charging current at the first sign of a drop in
power-path management. The bq2406x performs standard
the system voltage and enters battery-supplement mode if
three-phase charging—battery conditioning, constant
the system load exceeds what the adapter can handle.
current, and voltage regulation—followed by termination.
This article has also discussed how the IC protects against
The safety features include input OVP, a precharge safety
a system short circuit and then recovers. Finally, for each
timer, a fast-charge safety timer, and IC thermal regulation.
part number in the bq24072/3/4/5 family, changes in out-
The OVP circuit disables the input pass FET if the input
put voltage and efficiency that occur with changes in oper-
voltage exceeds the OVP threshold. This helps to protect
ational mode were compared.
against wrong or damaged power sources. The safety
The bq24072/3/4/5 family of Li-Ion battery chargers is a
timers, once expired, will disable charging. Typically, if the
fully integrated solution that performs Li-Ion charging and
design is done properly, a good battery will exit precharge
DPPM and reduces application size. It solves many issues
or reach termination long before the safety timers declare
with power sources by allowing use of less expensive
a fault. Typically intended for operation in extremely hot
adapte rs, managing loading, giving priority to the system,
environments where the IC junction temperature reaches
increasing reliability, and incorporating many safety fea-
125°C, the thermal-regulation loop reduces the charge
tures for a lower total system price.
level to prevent further heating of the charger IC. Further
details on these features can be found in the data sheet. Related Web sites
Conclusion power.ti.com
www.ti.com/sc/device/partnumber
An inexpensive discrete charger can be implemented that
Replace partnumber with bq24010, bq24020, bq24060,
performs the charging and manages basic power-path
bq24072, bq24073, bq24074, or bq24075
connections but does not address any of the safety and
reliability issues that may occur. A brief description has