---
source: "Abracon -- PCB Trace vs. Chip Antenna Design Considerations"
url: "https://abracon.com/downloads/PCB-Trace-vs-Chip-Antenna-PCB-Design-Considerations.pdf"
format: "PDF 8pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 11816
---

PCB Trace vs. Chip Antenna
Design Considerations
Roshni Prasad, MSEE
Associate Engineer | RF & Connectivity
Abracon LLC

PCB Trace vs Chip Antenna Design Considerations | Abracon LLC
Introduction
The modern urban environment poses a challenge to high-speed designs involving Cellular, GNSS, WiFi/
Bluetooth/BLE/ZigBee and LPWA protocols: the reflection, refraction, scattering, diffraction, polarization
and absorption of signals necessitates highly efficient RF chains. Of all components in the chain, the
antenna has the key role in establishing wireless connectivity.
A PCB trace antenna is given serious consideration when attempting to reduce the overall system cost;
however, chip antennas offer better overall performance in terms of size selectivity and efficiency in
most cases. The following information outlines the attributes of both chip and PCB trace antennas. It also
covers the design considerations required in selecting the right type of antenna to implement in your
design.
Which structures are typically employed in PCB trace antennas?
Inverted-F (IFA), Planar Inverted-F (PIFA) and Meandered Inverted-F (MIFA) structures are commonly
considered for trace antenna designs because they are ideally suited when board space is limited and
are also low-cost solutions.
How is the trace antenna designed?
The above-mentioned antennas are monopole designs with a quarter wavelength (λ/4) at the resonant
frequency. Monopoles require a ground plane, which forms the other quarter wavelength to radiate
efficiently. The antenna should be designed with no ground plane beneath the trace structure. The
electric performance depends on the dielectric substrate material (e.g., FR4), dielectric constant (εr) and
substrate thickness (h). The radiation pattern is nearly omni-directional.
How can we reduce the size? What are the trade-offs?
In order to reduce the size of trace antennas, quarter wavelength designs are preferred with arms short
to the ground plane. Figure 1 presents a typical PCB trace inverted-F antenna layout.
Short (Inductive Loading) Feed Line
λ/4 Antenna Trace
No copper Copper
(no ground plane) (ground plane)
Figure 1
Page | 2
5101 Hidden Creek Ln Spicewood TX 78669 | 512.371.6159 | www.abracon.com

It should be noted that loading increases the Q of the antenna, which consequently reduces the effective
bandwidth.
Q = F/BW
Where Q = Quality Factor, F = Resonant/Center Frequency and BW = Antenna Bandwidth
Furthermore, the overall radiation efficiency decreases as the surface area shrinks.
What are the disadvantages of having a PCB trace antenna?
The two common disadvantages associated with designing antennas are lower frequencies and with
wider bandwidths.
Lower-frequency trace antennas are challenging from a size perspective because the design demands
quarter wavelength structures with ground plane to support effective radiation characteristics. For
instance, the quarter wavelength (λ/4) of 433 MHz is 172.5 mm. PCB trace antennas at lower frequencies,
such as 433 MHz, become physically large when directly designed onto the PCB, as opposed to utilizing
a chip antenna.
For cellular designs, it is challenging to cover a wide frequency range of 698~960 MHz, 1710~2170 MHz,
and 2500~2700 MHz and still match the lowest LTE bands (698 MHz) with a PCB design.
In such cases, chip antennas serve as the best alternative
How do you implement a chip antenna into a design?
Several factors contribute to the performance and radiation characteristics while designing a chip antenna
onto a PCB: the PCB size, the PCB layout, the ground/clearance space dimensions, the tuned matching
circuit, the RF shielding and the housing. When implementing an off-the-shelf chip into a design, closely
follow the reference layout design to avoid any de-tuning or performance variation. Figure 2 illustrates
a typical chip antenna layout.
Chip antenna
No ground area
50 Ω Feed line (clearance space)
(π-type) matching
Ground area
Via holes
Figure 2 (Top View)
Page | 3

Abracon’s chip antennas utilize dielectric and LTCC multilayer technology, creating quarter-wave
monopole structures to serve as compact and lightweight solutions. The chip antennas provide an
optimal convergence in size, cost and performance. The range of form factors vary as a function of
gain and operating bandwidth. The Abracon chip antennas identified in Table 1 are designed to yield
desired range, optimal gain and suitable bandwidth, resulting in unsurpassed system-level sensitivity
and efficiency when compared to typical PCB trace antennas.
PART NUMBER ACAG0201-2450-T ACAG0301-15752450-T ACAG1204-433/868/915-T ACAR3705-S698
700~960, 1710~2170,
FREQUENCY (MHz) 2450 1575, 2450 433, 868, 915
2500~2700
SIZE (mm) 2 x 1.25 3.2 x 1.6 12 x 4 37 x 5
BW (MHz) -65 20, 100 10, 20, 15 260, 460, 200
EFFICIENCY (%) 72.7 57, 73 35, 52, 59 55, 70, 50
PEAK GAIN (dBi) 2.7 1.21, 3.18 -1.72, 2.63, 3.42 -1.13
GROUND PLANE
90 x 50 90 x 50 90 x 50 107 x 45
SIZE (mm)
Table 1
Where are the ideal chip placements?
Antenna orientation plays a primary role in defining the radiation characteristics. The suitable placement
for orienting a monopole design is on a corner of the PCB, as demonstrated in Figure 3. Avoid placements
near metals or other electronic components because coupling between the antenna and the surrounding
elements may degrade the chip antenna performance. Use the above guidelines and ground clearance
area dimension, as provided in the datasheet, when designing the chip onto a PCB design that is unable
to follow the overall reference design layout.
*
* Indicates bad antenna placement
Figure 3
Page | 4

How critical is the ground plane?
In most applications, both chip and PCB trace antenna performances are sensitive to ground plane
length. Abracon recommends to keep the lowest frequency of the operating band(s) in mind while
considering the ground plane size.
PCB trace antennas’ susceptibility to various factors creates a high probability of compromise on
efficiency, especially with minimized ground plane sizes. On the other hand, both single and wide-band
chip antennas can still meet efficiency requirements with minimized impact from external factors.
Figure 4 displays the performance variation of Abracon’s ACAR4008-S698 chip antenna on various ground
plane lengths. The chart shows a significant impact of ground plane size on the antenna’s efficiency.
Excluding antenna designs involving an extremely small PCB area, such as wearable applications, the
reference ground plane dimensions should closely follow the datasheet to achieve maximum efficiency.
10
8 5 9 5 m m 5 m m
6
75
m
5 m
Figure 4
Page | 5

What challenges are related to antenna frequency detuning during system implementation or testing?
As the PCB layout greatly affects antenna performance, tuning is required to match the antenna for
optimal performance. Accurate impedance matching yields maximum power transfer in the desired band.
With PCB traces, as the antenna design is susceptible to the overall PCB design, it is difficult to perform
tuning and achieve the desired performance. Additionally, low dielectric permittivity of the PCB makes
the antenna highly sensitive to design changes and tolerance variations. In such scenarios, re-spinning
the PCB is required to achieve the desired antenna performance.
With chip antennas, matching elements can be varied to accommodate the in-system detuning. π-type
is the most preferred technique because it offers maximum flexibility in terms of tuning the operational
bandwidth. Other matching techniques include T-type, L-type and single series/shunt element. (See
Figure 5.)
Figure 5
When designing the suitable matching network, a Vector Network Analyzer (VNA) can probe the test
circuit on the board and determine the impedance at the antenna input. (See Figure 6.) Measuring the
S-parameter and VSWR bandwidth analyzes the on-board chip antenna performance. Tuning can further
improve antenna performance. Abracon’s “Antenna Impedance Matching – Simplified” white paper
offers additional information.
Antenna Matching network Ground area No ground
Chip
antenna
Network
Analyzer
Matching
network
Probe Probe tip
Test Measurement Using Network Analyzer Section of Evaluation Board
Figure 6
Page | 6

Abracon offers chip antenna optimization services in which RF engineers tune the matching network to
50-ohm real impedance using lumped elements for maximum efficiency. Matching helps optimize the
antenna performance for the desired band in the actual device environment. Abracon engineers also
review design layouts for effective usage of board space. The test requires shipping a fully functional
system to Abracon and typically takes 4 weeks to complete.
Cost-Benefit Analysis: PCB trace or chip antenna?
Table 2 summarizes the above discussed ideas and weighs the PCB design considerations for PCB trace
antennas versus chip antennas. Based on design requirements, you can choose the antenna type that
best fits the application.
PARAMETER PCB TRACE ANTENNA CHIP ANTENNA
IN-HOUSE RF EXPERTISE Required Not Required
DESIGN CHANGES Difficult Different design configurations possible
SENSITIVITY Highly sensitive to PCB changes Less sensitive
Can be achieved with input/output matching
SYSTEM LEVEL DE-TUNING Requires a PCB re-spin (cost)
optimization (change L & C values)
EFFICIENCY Poor Good
SELECTIVITY Poor Good
SYSTEM COST Cheapest Moderate
SYSTEM LEVEL
Not available Available from Abracon (see details below)
OPTIMIZATION SERVICE
Table 2
Author Information:
Roshni Prasad, MSEE
Associate Engineer | RF & Connectivity
Abracon LLC
12/19/2019
Page | 7

ANTENNA OPTIMIZATION SERVICE
OVERVIEW
OBTAIN OPTIMAL POWER, GAIN AND RANGE
Abracon off ers in-system tuning services for patch and chip
antennas. By characterizing the antenna performance in the
end system or product, this service takes the guess work
out of RF verifi cation while off ering corrective measures that
re-tune the system for center frequency and impedance
mismatch. This provides maximum system effi ciency
delivering many benefi ts including, extended RF range,
improved sensitivity and can reduce the required power
consumption for a given level of transmit range.
Orderable Part Number: ABAOS-5WK
Patch Antennas
This service is off ered for the APAE and APA series of passive patch antennas covering a
variety of RF bands from 800MHz to 6000MHz including applications such as RFID, GPS/
GNSS, WiFi, ISM radios, and Iridium. In most cases, tuning is required after the patch antenna
is mounted in the end-application, especially if the antenna operating bandwidth is narrow.
Passive patch antennas should be tuned to the ground plane to which they are mounted.
This compensates for the frequency shifts occurring due to the particular device environment
in which the antenna is placed. There are several methods to tune the patch antenna such
as moving the feed point, changing the shape of the top silver electrode, and removing the
corners or sides of the top silver plate.
Chip Antennas
This service also applies to the ACAG, ACAJ, ACAR and AMCA series of chip antennas.
For chip antennas, the effi ciency of the antenna depends mainly on the size and shape of
the ground plane to which it is mounted as well the impedance matching of the antenna to
the feed line. The antenna has to be tuned to center resonant frequency by matching the
impedance to the antenna using inductors and capacitors. Higher effi ciency guarantees more
radiated power and increased operating range for the antennas.
LEARN MORE AT
ABRACON.COM