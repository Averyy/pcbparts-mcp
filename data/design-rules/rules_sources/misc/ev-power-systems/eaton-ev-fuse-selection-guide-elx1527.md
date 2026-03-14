---
source: "Eaton -- EV Fuse Selection Guide ELX1527"
url: "https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/technical/eaton-ev-fuse-selection-guide-elx1527-en.pdf"
format: "PDF 4pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 10716
---

Technical Note ELX1527
Effective June 2025 EV fuse selection guide
EV fuse selection guide
Introduction
As the automotive industry advances towards electrification,
ensuring the safety and reliability of EV systems is crucial. The
purpose of this document is to provide detailed application
guidelines for selecting and properly sizing the current and voltage
ratings of electric vehicle (EV) fuses used in automotive applications.
This document outlines the key factors and considerations involved
in choosing the appropriate EV fuses, with a focus on adequately
sizing the fuse based on the ambient temperature and current load
profiles of the end application.
Global fuse standards related to EV
Multiple global standards exist related to EV fuses. Eaton designs
and tests its EV fuses according to a combination of the standards
below depending on the fuse rating and mounting conditions:
• AEC-Q200
• JASO D622 – Japan
• ISO 8820
Key challenges:
Traditional fuses are designed for industrial purposes and are not
suitable for the harsh environment of a vehicle or the expected
operating life requirements. Industrial fuse standards do not account
for these challenges in their test criteria, hence the need for
automotive specific standards which test for:
• Thermal shock
• Mechanical shock and vibration
• High inrush withstand capability
• Cyclic loading and thermal fatigue
• Sustained high and low temperature operation

Technical Note ELX1527 EV fuse selection guide
Effective June 2025
EV fuse applications Calculating nominal rated current In
The high voltage battery pack within an electric vehicle can pose a In is the nominal rated current of the fuse. This is the rated current
serious safety risk due to the high voltage and available fault current. listed on the fuse label and datasheet. In is calculated based on a
The system should be protected by installing downstream circuit derating calculation intended to ensure that the actual RMS
protection that is sized appropriately to protect each load. steady-state load current passing through the fuse should be equal
to or lower than the maximum permissible load current Ib. Overload
and cyclic loading are not accounted for in this In calculation and
must be considered separately in subsequent steps.
Ib = In x Kt x Ke x Kv x Kf x Ka x Kx
Convert to: In≥ Ib / (Kt x Ke x Kv x Kf x Ka x Kx)
Where:
In: Current rating of fuse
Ib: Maximum permissible continuous load current*
Kt: Ambient temperature correction factor
Ke: Thermal connection factor
Kv: Cooling air correction factor
Kf: Frequency correction factor
Ka: High altitude correction factor
Kx: enclose space correction factor
*Note: For any periods of 10 minutes duration or more, the RMS value of the load
current should not exceed this.
Figure 1: Example system configuration with a battery pack and HV power distribution
fuse box
Determining the ambient temperature correction factor
1. Battery pack: Kt: Ambient temperature correction factor
• Contains the BMS (battery management system) responsible
for monitoring the health of the system, state of charge, EV fuses are derated for ambient temperatures above +20 °C to
temperature, etc. account for the elevated ambient temperature’s impact on the fuse’s
ability to dissipate heat by convection. Kt should be chosen based on
• Traction motor / inverter circuit protection the maximum ambient operating temperature of the application.
• Fast charging circuit protection
2. Power Distribution Unit (HV fuse box):
• On board charger
• Auxiliary circuit protection: A/C, DC/DC, pumps,
PTC / heater, etc.
Basic sizing requirements
1. Determine the rated voltage:
• The voltage rating of the fuse should exceed the maximum
system voltage which is determined by the voltage of the
battery at its maximum state of charge
Example of an ambient temperature re-rating curve
• If the fuse has separate AC and DC voltage ratings, then the Note: Refer to specific datasheet
corresponding voltage rating should be chosen based on
the application
Determining the cooling air correction factor
2. Determine the nominal rated current (In):
Kv: Cooling air correction factor
• The nominal rated current is calculated according to the
maximum permissible continuous load current and the
The curve on the next page shows the influence of forced air cooling
application specific correction (derating) factors
on the fuse. Kt is equal to 1 for sealed enclosures and enclosures
• Apply the appropriate derating factors explained below without active cooling.
according to the application specific requirements
3. Determine the physical size and mounting configuration:
• Bolt down terminals for mating with bus bars or
wire connectors
• PCB thru-hole terminals for mounting on PCB
2 www.eaton.com/electronics

EV fuse selection guide Technical Note ELX1527
Determining the high-altitude correction factor
Ka: High altitude correction factor
When fuses are used at high altitudes, the atmosphere’s lower
density reduces the cooling effect on the fuse. An altitude correction
factor (Ka) should be applied to the fuse’s continuous rating when
used above 2000 m.
Note: Must be air speed surrounding the fuse, not speed out of the fan.
Determining the thermal correction factor
Ke: Thermal connection factor
Busbar and wire size are important factors to consider when sizing
EV fuses, as they help conduct heat away from the fuse allowing
it to operate cooler. The nominal busbar or wire current density on
which the fuses are mounted should be 1.3 A / mm2 (based on IEC
60269 Part 4 which defines a range from 1.0 A to 1.6 A / mm2). If
the busbar carries a current density greater than this, then the fuse
should be derated.
Determining the enclosure correction factor
Kx: Enclosure correction factor
In automotive applications, the fuse is often mounted in a small
enclosure with no ventilation. For these conditions a correction factor
of 0.8 is applied to ensure the fuse does not run too hot.
Example: Calculating nominal current rating In
An EV fuse is required to protect an EV auxiliary load such as a PTC
heater. The continuous current load profile is determined to be 30 A.
The maximum ambient air temperature is defined as +60 °C and the
fuse is mounted in a small enclosure with no ventilation. It is decided
that the cabling used to connect the fuse will be 15 mm2. It is also
Determining the frequency correction factor specified that the vehicle needs to function up to 2500 m above sea
level.
Kf: Frequency correction factor
Insertion of the derating factors into the nominal current rating
Not applicable for DC current. equation and solving for In:
In≥ Ib/(Kt x Ke x Kv x Kf x Ka x Kx ) , In ≥1.89 Ib
Derating factors based on the example application:
Ib: the continuous current is specified as 30 A (for applications with
variable current, use RMS current)
Kt: the maximum ambient temperature is specified as +60 °C, thus
Kt = 0.8
Ke: in this example with 30 A current and 20 mm2 wire diameter,
the current density is 1.5 A / mm2. The recommended wire diameter
based on our 1.3 A / mm2 guideline is 28.7 mm2 (30 A ÷ 1.3 A / mm2)
therefore the 15 mm2 wire diameter in the example is 52% of the
recommended size, and we define Ke = 0.85
Kv: no air cooling specified, Kv = 1.0
Kf: DC current, Kf = 1.0
www.eaton.com/electronics 3

Technical Note ELX1527 EV fuse selection guide
Ka: maximum altitude is specified as 2500 m, in which case Ka =
0.97
Kx: considering the fuse being installed in a closed and small space,
we would like to apply an additional de-rating factor Kx = 0.8
Finally we get In ≥1.89 Ib, which means that the fuse rating should
be greater than 1.89 x 30 A = 57 A. We then round up to the
nearest available fuse rating, that being 60 A in this example.
Optimizing the selection
Variable loads with non-continuous load profiles may require
additional derating to buffer against thermal fatigue due to irregular
current profiles. In such cases an additional derating factor of 0.8
should be applied for cyclic loading. Figure 2: The webinar session titled "Specifying high voltage fuses for EV
applications", held on May, 2025. Click to access.
Sustained overloads greater than 80% of the fuse rating for longer
than 1 second should be avoided. If such overloads cannot be
avoided then additional derating may be necessary to prevent the
fuse from blowing prematurely due to thermal fatigue.
For help or technical assistance with these more complicated load
profiles please contact Eaton application engineering:
ELXtech@eaton.com.
Additional considerations
After making the initial fuse rating selection, there are other
considerations that need to be addressed to ensure the fuse is sized
appropriately to adequately protect the rest of the system:
Check for coordination with downstream components. Determine
the available fault current and check that the fuse will blow in time to
prevent damage downstream. Examples of downstream
components which may need to coordinate with the fuse: cables,
headers, connectors, relays, contactors, etc.
Make sure the fuse can protect against all intended fault currents.
Many EV fuses provide short circuit protection only and are specified
with a minimum breaking capacity. The minimum breaking
Figure 3: Eaton's wide range of xEV fuses for demanding applications.
capacity is the lowest current that the fuse will reliably protect
against. Overload faults below the fuse’s minimum breaking capacity
will not be protected by the fuse and may require another protection
mechanism.
Consider choosing a fuse size which has higher available ratings
in the same package size to give yourself flexibility if you need to
increase the fuse rating in the future. This can be a benefit later
if the fuse rating needs to be increased, since doing so will be
possible without having to change the physical package.
System level and vehicle level qualification is always recommended
and should be performed as a means to validate system reliability
and proper design implementation.
Eaton
Electronics Division
1000 Eaton Boulevard
Cleveland, OH 44122
United States
www.eaton.com/electronics
© 2025 Eaton Follow us on social media to get the
All Rights Reserved Eaton is a registered trademark. latest product and support information.
Printed in USA
Publication No. ELX1527 BU-ELX22423 All other trademarks are property
June 2025 of their respective owners.