---
source: "TI SLUA400A -- Dynamic Power-Path Management and DPM"
url: "https://www.ti.com/lit/an/slua400a/slua400a.pdf"
format: "PDF 8pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 14423
---

Application Report

Dynamic Power-Path Management and Dynamic Power
Management
Manuel Diaz-Corrada .............................................................................. BMS Battery Charging Products
ABSTRACT
Dynamic power-path management (DPPM) and dynamic power management (DPM) are two similar
features within the battery charger. Dynamic power-path management uses power path, which is the part
of the charger IC that separates the system from the battery, allowing for simultaneous battery charging
and system power delivery. Both features reduce the battery charging current to give the system priority
when the adapter has reached its output current rating. The bq2512x family uses both the DPM and
DPPM technology.
Contents
1 DPM Discussion ............................................................................................................. 1
2 DPPM Discussion............................................................................................................ 4
3 Power Transfer Issues ...................................................................................................... 5
4 Frequently Asked Questions About the bq25120A and DPM or DPPM.............................................. 5
List of Figures
1 Dynamic Power Management - Manages Battery Current Based on Input Current ................................ 2
2 V in Action, Preventing an Adaptor Crash........................................................................... 3
INDPM
3 DPPM – Manages Battery Current Based on Output Voltage (control loops not shown for regulating
battery constant current/voltage or battery supplement mode)........................................................ 4
1 DPM Discussion
Dynamic power management (DPM) is an input current limit routine, which monitors and controls the input
current going to the system (ILIM or IINDPM) or an input voltage limit routine, which monitors and controls
the input voltage (VINDPM) by using a resistor divider between R and R and comparing it with
1 2
V , which is set by V _DAC. Both are useful for different situations but both accomplish their
REF_VINDPM INDPM
task by establishing a max current level on the input.

Charge
Pump
+
±
VINDPM_DAC<2:0> DAC
± +
± +
VIIN_SNS
MUX
IIIN_SNS

EN_ILIM
VIN
Q1
1
N
VINDPM LOOP
R1
Q2
AVAO
R2
PMID
VIN_REF
RSNS
Kelvin Connection
IINDPM LOOP
Figure 1. Dynamic Power Management - Manages Battery Current Based on Input Current
The most common use case for the input current limit routine is when the adapter current limit is known
and fixed. This means that when input is higher than the level set by I _DAC (set by I2C) then the system
LIM
reduces the input current to prevent overloading the adapter. The IC performs this by sensing the input
current and comparing it to the programmable reference level set by I _DAC. This allows for the system
LIM
to act pre-emptively and precisely.
However, in the world of universal standards, knowing the current limits of the adapter is almost
impossible because different manufacturers set different capacities for their products. There can be two
USB wall charger adapters that look identical but have current limits of 500 mA and 900 mA - a significant
difference. V is used to determine the current limits of an adapter and regulate the system to adhere
to those limits.
The basic framework of V is based around monitoring the input voltage and comparing a scaled down
version (R1, R2 resistor divider in Figure 2) of it to V . This comparison is to prevent the V from
REF_VINDPM PMID
dropping below the required threshold voltage to charge the battery. If this threshold is reached due to the
combined load of the system and battery charger current on the adapter, then charging current is reduced
as necessary to keep the input current from increasing further.
The pros of DPM are:
• Allows selection of a lower cost adaptor.
• System voltage remains constant during DPM operation.
• Better efficiency
A lower cost adapter may be chosen based on the average load (average system load of 0.5 A plus a
fast-charge load of 1 A) instead of a peak load. If a peak system load requires an additional 0.75 A above
the average load, then the charging current is reduced by this amount during the peak load transient. This
is the case for both DPM and DPPM

The system’s voltage remains constant because the adapter does not hit a current limit. This supply is
connected directly to the system; so, the only change in system voltage is due to the IR drop across Q1,
which is associated with the load change.
Because this system voltage remains relatively high, the power dissipation between the input and output is
minimized, and, thus, the efficiency remains high.
Programmed Charge Current Higher Than Adapter Capability
IIN
Device hits VINDPM threshold and input current is reduced to limit sag on VIN
Figure 2. V in Action, Preventing an Adaptor Crash
The cons of DPM are:
• Wrong adaptor (too low of current rating) may crash system.
• Power grid brown-outs may cause system to crash.
If an adapter is used which has a lower current limit threshold than the programmed ILIM level, then,
during peak loads, the adapter’s voltage and system voltage drop, causing a crash due to the adapter
hitting the current limit. When this crash occurs, the DPM circuit (if V is not turned on) does not detect
voltage drops and does not reduce the charging current.
Similarly, if the AC power grid experiences a voltage drop and causes the adapter to drop out of
regulation, the DPM routine will not reduce the charging current, and the system will likely crash.

2 DPPM Discussion
Q1,Q2 Internal IC
Input FETs
In (DC+)
Control
Loops
Rload
± Q3
VDPPM +
Battery FETs 1-cell
Vbat
Li-ion
Battery
GND
1
Figure 3. DPPM – Manages Battery Current Based on Output Voltage (control loops not shown for
regulating battery constant current/voltage or battery supplement mode)
Dynamic power-path management (DPPM) is a current management routine based on the system voltage;
if the system voltage drops below a preprogrammed threshold, due to loss of power or a current-limit
threshold, the battery charging current is sufficiently reduced to prevent any further drop in the system
voltage. If the charge current drops to zero, then a partially charged battery can enter into supplement
mode. This means that the battery aids in providing power to the system once the voltage drops below
V .
BSUP1
The pros of DPPM are:
• Allows selection of a lower cost adaptor.
• Better protection from system crashes due to low-power adaptors and power grid brown-outs.
• Better efficiency than running off a battery.
A lower cost adapter may be chosen based on the average load (average system load of 0.5 A plus a
fast-charge load of 1 A) instead of a peak load. If a peak system load requires an additional 0.75 A, which
is above the average load, then the charging current is reduced by this amount during the peak load
transient, preventing a brown out condition and maintaining normal operation.
The DPPM system voltage based routine detects a current-limited adapter or brown-out condition when
the system voltage drops to the detection threshold V . By reducing the charging current, DPPM helps
DPPM
to keep the system from crashing as long as the system load current alone does not exceed the input
current limit of the adapter. Note that this assumes that the battery is absent or fully depleted; otherwise,
the battery would provide the necessary power to the system, further extending system function.
The cons of DPPM are:
• System output voltage transients may affect sensitive circuits like audio amplifiers
• Slightly lower charging efficiency than DPM
The system output voltage drops due to the system and charging load exceeding the current limit of the
input adapter. The lower the DPPM threshold is set, the more the output can fall when the adapter
reaches current limit. This sudden change in system voltage may inject noise into sensitive circuitry such
as audio circuits. The best way to minimize this noise is setting the DPPM threshold as high as possible to
minimize the output voltage transient. The supply tolerances, IR drops, and tolerances of the DPPM
threshold are factors to consider when programming this threshold.
The efficiency is slightly lower during DPPM than DPM in in general, but negligible if the system rarely
enters DPPM.

3 Power Transfer Issues
The designer has to consider the timing issues associated with switching between the sources. The
battery FET typically takes a small amount of time to be driven on after the output drops to the battery
voltage. If the battery has sufficient capacity to handle the system load, then this prevents any system
glitches since the battery can provide all power to the load during the switch. If the battery is missing, it
can take up to ten times as long, after the lost input drops to within 125 mV of the battery voltage, for the
new source to be connected. This requires the system capacitance to provide the system load during this
time. A 100-µF capacitor can deliver 100 mA for 100 µs and will discharge by 100 mV [C=i/(dv/dt)].
4 Frequently Asked Questions About the bq25120A and DPM or DPPM
• How do you set V ?
– This is a fixed non-programmable value that set to 0.2 V above V .
BATREG
• How is V triggered?
– Current is shared between charging the battery and powering the system at PMID, SYS, and
LS/LDO. If the sum of the charging current and system current is greater than the current the
adapter can support, the V loop reduces the current going through PMID through the input
blocking FETs. When the detected PMID voltage drops below Vbatreg + VDPPM then the control
loop is triggered and the charge current is reduced. This point is known as the DPPM threshold
point
• Why do I need DPPM?
– DPPM provides protection looking at the charger’s output voltage. In this case, if the system
voltage drops below V , the charge current is reduced and redirected to the system load, thus
preventing a system crash.
– If further power is needed to prevent a system crash, DPPM mode allows a partially charged
battery to supplement the system load.
• Why do I need V ?
– V prevents an adapter from crashing by reducing current instead of voltage. This allows for
charging to continue, albeit at a slower pace.
– V provides protection at the input of the charger (output of the adapter). If a system is requiring
more power than the adapter can provide, V keeps the adapter from trying to provide that
power by reducing the charge current. When the supply voltage reaches V threshold, the DPM
loop reduces the charging current to prevent overloading of the adapter. Through these actions,
DPM allows the user to select any adapter for charging and avoid hiccups from overloading.
• How do you set V ?
– V is programmable with I2C from 4.2 V – 4.9 V in 100-mV steps. The default setting is VINDPM
= 4.6 V. Setting the VINDPM_ON register (B7) to 0 enables the V register and 1 disables
V . See table 24 on the data sheet.
• What are the benefits of software controlled V ?
– The benefit of software controlled V is its flexibility. Any customer can change it after
production to suit their applications, including factoring in increased resistance of a cable, more
headroom, or even different combinations of lithium ion chemistries that require more or less
headroom.
• What do they have in common?
– Both methods give priority to the system by reducing the charging current when the adapter
reaches its maximum limit, thus improving the safety of the system and providing a more consistent
user experience.
• How do safety timers extend and why do they extend in DPM?
– The charge safety timer (t ) and precharge safety timer (t ) are programmable with I2C.
maxchg prechg
T can be set from 2 to 540 minutes, and t is 10% of t . The device’s 2X timer prevents
maxchg prechg maxchg
the safety timer from expiring too early when the charge current is reduced in V mode.
Therefore, the safety time is extended while V is active if the 2X timer is set, and the timer runs
at half speed.

– The reason for this extension is because V slows down the charge rate, if the timer did not
extend then it would be possible for the timer to trigger even when everything was working as
intended.
• How is termination affected by DPM and DPPM?
– For both DPPM and DPM battery termination is disabled.
• What do I need to keep in mind when designing a system in relation to DPPM or DPM?
– When designing a system in relation to DPM you need to consider that the DPM loop could reduce
current going to PMID through input blocking FETs, causing a drop in PMID voltage. Therefore a
low enough VIN could be reduced to a voltage below the battery voltage due to losses within the
system, preventing full charge of a battery.
– One of the reasons for these losses is R . R is the resistances of the two FETs to turn on.
DSON DSON
The higher the resistance, the higher the voltage drops, based on power loss (resistance x
current2). When calculating the necessary headroom, a higher R would require a higher starting
DSON
VIN. This is called headroom, and it needs to be taken into account when designing the lowest
voltage you allow before DPM goes into effect.
– The specific formula for calculating headroom is VIN= VBAT+VDO(IN-PMID) + RDS(BAT-FET)*I
CHG
– Since DPPM is only related to the output, there are no considerations to be taken in relation to
charging the system.

Revision History
NOTE: Page numbers for previous revisions may differ from page numbers in the current version.
Changes from Original (January 2007) to A Revision .................................................................................................... Page
• Changed organization of document..................................................................................................... 1
• Added Frequently Asked Questions About the bq25120A and DPM or DPPM section ......................................... 5
• Deleted Design Example for Setting the DPPM Threshold Using the bq24032A IC section.................................... 6