---
source: "Infineon/Cypress AN91445 -- Antenna Design and RF Layout Guidelines"
url: "https://www.infineon.com/dgdl/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf?fileId=8ac78c8c7cdc391c017d073e054f6227"
format: "PDF 60pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 108791
---

Antenna Design and RF Layout Guidelines
Authors: Tapan Pattnayak, Guhapriyan Thanikachalam
Associated Part Family: CY8C4XXX-BL, CYBL1XXXX, CY8C6XXXXX-BL
Related Application Notes: For the complete list, click here
To get the latest version of this application note and the associated Gerber file, please visit
http://www.cypress.com/go/AN91445
This application note is for informational purposes. Antenna design requires suitable test equipment and know-how for
optimal performance. It is strongly advised that the professional services of firms specializing in the design and placement
of antennas be sought out. Cypress can provide a list of suitable antenna design specialists, if requested.
AN91445 explains antenna design in simple terms and provides guidelines for RF component selection, matching network
design, and layout design. This application note also recommends two Cypress-tested PCB antennas that can be implemented
at a very low cost for use with the Bluetooth Low Energy (BLE) solutions that are part of Cypress’s PSoC® and PRoC™ families.
For information on WICED Smart BLE solutions, see the WICED community product guide page. The PRoC BLE, PSoC 4 BLE,
and PSoC 6 MCU with Bluetooth Low Energy (BLE) Connectivity 2.4-GHz radio must be carefully matched to its antenna for
optimum performance.
Contents
1 Introduction .................................................................. 2 16 RF Transmission Lines .............................................. 43
2 Antenna Basics ............................................................ 3 16.1 Microstrip Line .................................................. 43
3 Antenna Types ............................................................ 4 16.2 CPWG (with Bottom Ground) ............................ 44
4 Choosing an Antenna .................................................. 5 16.3 RF Trace Layout Considerations ...................... 44
5 Antenna Parameters .................................................... 6 17 PCB Stackup ............................................................. 46
6 Antennas for Cypress PRoC/PSoC BLE ..................... 9 17.1 Four-Layer PCB ................................................ 46
7 Cypress-Proprietary PCB Antennas ............................ 9 17.2 Two-Layer PCB ................................................ 46
7.1 Meandered Inverted-F Antenna (MIFA) ............ 10 18 Ground Plane ............................................................ 47
7.2 Antenna Feed Consideration ............................ 11 18.1 Ground Plane Considerations ........................... 47
7.3 Antenna Length Considerations ........................ 14 19 Power Supply Decoupling ......................................... 47
7.4 Inverted-F Antenna (IFA) .................................. 15 19.1 Power Supply Decoupling
8 Chip Antennas ........................................................... 17 Layout Considerations ...................................... 48
9 Wire Antennas ........................................................... 19 20 Vias .......................................................................... 48
10 Antenna Comparison ................................................. 20 21 Capacitors and Inductors........................................... 49
11 Effect of Enclosure and Ground Plane 21.1 Capacitors ......................................................... 49
on Antenna Performance ........................................... 21 21.2 Inductors ........................................................... 51
11.1 Effect of Ground Plane ...................................... 21 22 Design for Testability ................................................. 52
11.2 Effect of Enclosure ............................................ 22 23 Support for External Power Amplifier/
12 Guidelines for Antenna Placement, Low-Noise Amplifier/RF Front End ............................ 53
Enclosure, and Ground Plane.................................... 23 24 Support for Coexistence with Wi-Fi ........................... 53
13 RF Concepts and Terminologies ............................... 24 24.1 Spatial Isolation ................................................ 53
13.1 Smith Chart ....................................................... 27 24.2 Frequency Isolation .......................................... 54
14 Impedance Matching ................................................. 29 24.3 Temporal Isolation ............................................ 55
14.1 Matching Network Topology .............................. 31 25 Summary ................................................................... 55
14.2 Tips for Matching Network ................................ 35 26 Related Application Notes ......................................... 56
15 Antenna Tuning ......................................................... 35 Appendix A. Checklist ............................................... 57
15.1 Tuning Procedure ............................................. 36 Appendix B. References ........................................... 58
www.cypress.com Document No. 001-91445 Rev. *H 1

1 Introduction
Antenna design and RF layout are critical in a wireless system that transmits and receives electromagnetic radiation in
free space. The wireless range that an end-customer gets out of an RF product with a current-limited power source
such as a coin-cell battery depends greatly on the antenna design, the enclosure, and a good PCB layout.
It is not uncommon to have a wide variation in RF ranges for designs that use the same silicon and the same power
but a different layout and antenna-design practice. This application note describes the best practices, layout guidelines,
and an antenna-tuning procedure to get the widest range with a given amount of power. Other important general layout
considerations for RF trace, power supply decoupling, via holes, PCB stackup, and antenna and grounding are also
explored. The selection of RF passives such as inductors and capacitors is covered in detail. Each topic ends with tips
or a checklist of design items related to the topic.
Figure 1 shows the critical components of a wireless system, both at the Transmitter (TX) and Receiver (RX).
Figure 1. Typical Short-Range Wireless System
Antenna
Radio MN
Transmission
Line (50Ω)
Matching
Network
Antenna
MN Radio
Transmission
Line (50Ω)
www.cypress.com Document No. 001-91445 Rev. *H 2
tf
03
TX
RX
A well-designed antenna ensures optimum operating distance of the wireless product. The more power it can transmit
from the radio, the larger the distance it can cover for a given packet error rate (PER) and receiver sensitivity. Similarly,
a well-tuned radio at the receiver side can work with minimal radiation incident at the antenna. The RF layout together
with the radio matching network needs to be properly designed to ensure that most of the power from the radio reaches
the antenna and vice versa.

2 Antenna Basics
An antenna is basically a conductor exposed in space. If the length of the conductor is a certain ratio or multiple of the
wavelength of the signal1, it becomes an antenna. This condition is called “resonance”, as the electrical energy fed to
antenna is radiated into free space.
Figure 2. Dipole Antenna Basic
In Figure 2, the conductor has a length λ/2, where λ is the wave length of the electric signal. The signal generator feeds
the antenna at its center point by a transmission line known as “antenna feed”. At this length, the voltage and current
standing waves are formed across the length of the conductor, as shown in Figure 2.
The electrical energy input to the antenna is radiated in the form of electromagnetic radiation of that frequency to free
space. The antenna is fed by an antenna feed that has an impedance of, say, 50 Ω, and transmits to the free space,
which has an impendence of 377 Ω2.
Thus, the antenna geometry has two most important considerations:
1. Antenna length
2. Antenna feed
The λ/2-length antenna shown in Figure 2 is called a dipole antenna. However, most antennas in printed circuit boards
achieve the same performance by having a λ/4-length conductor in a particular way. See Figure 3.
By having a ground at some distance below the conductor, an image is created of the same length (λ/4). When
combined, these legs work like a dipole antenna. This type of antenna is called the quarter-wave (λ/4) monopole
antenna. Most antennas on the PCB are implemented as quarter-wave antennas on a copper ground plane. Note that
the signal is now fed single-ended and that the ground plane acts as the return path.3
1 See “harmonic antenna operation”
2 Impedance of Free Space if there is no material nearby
3 The effect of this return path is discussed later. This is a very important aspect in PCB layout of the antenna and the antenna feed.
www.cypress.com Document No. 001-91445 Rev. *H 3

Figure 3. Quarter-Wave Antenna
Antenna on a Ground
plane
Signal
Generator
Return Current
Image
Conductor
GND Plane
www.cypress.com Document No. 001-91445 Rev. *H 4
htgneL
htgneL
4/λ
4/λ
For a quarter-wave antenna that is used in most PCBs, the important considerations are:
1. Antenna length
2. Antenna feed
3. Shape and size of the ground plane and the return path
3 Antenna Types
As described in the previous section, any conductor of length λ/4 exposed in free space, over a ground plane with a
proper feed can be an effective antenna. Depending on the wavelength, the antenna can be as long as the FM antenna
of a car or a tiny trace on a beacon. For 2.4-GHz applications, most PCB antennas fall into the following types:
1. Wire Antenna: This is a piece of wire extending over the PCB in free space with its length matched to λ/4 over a
ground plane. This is generally fed by a 50-Ω4 transmission line. The wire antenna gives the best performance and
RF range because of its dimensions and three-dimensional exposure. The wire can be a straight wire, helix, or
loop. This is a three-dimensional (3D) structure, with the antenna over a height of 4-5 mm over the PCB plane,
protruding into space.
Figure 4: Wire Antenna
4 The feed is generally of 50 ohm in most RF PCB catering to low-power wireless applications. However, other impedance values are
possible.

2. PCB Antenna: This is a trace drawn on the PCB. This can be a straight trace, inverted F-type trace, meandered
trace, circular trace, or a curve with wiggles depending on the antenna type and space constraints. In a PCB
antenna, the antenna becomes a two-dimensional (2D) structure in the same plane of the PCB; see Figure 5.
There are guidelines5 that must be followed as the 3D antenna exposed in free space is brought to the PCB plane
as a 2D PCB trace. A PCB antenna requires more PCB area, has a lower efficiency than the wire antenna, but is
cheaper. It has easy manufacturability and has the wireless range acceptable for a BLE application.
Figure 5. PCB Antenna
3. Chip Antenna: This is an antenna in a small form-factor IC that has a conductor packed inside. This is useful when
there is limited space to print a PCB antenna or support a 3D wire antenna. Refer to Figure 6 for a Bluetooth
module containing a chip antenna. The size of the antenna and the module in comparison with a one-cent is coin
is given below.
Figure 6. Cypress EZ BLE Module (10 mm × 10 mm) with Chip Antenna
4 Choosing an Antenna
The selection of an antenna depends on the application, the available board size, cost, RF range, and directivity.
Bluetooth Low energy (BLE) applications such as a wireless mouse requires an RF range of only 10 feet and a data
rate of a few kbps. However, for a remote control application with voice recognition, an antenna should have a range
around 20 ft in an indoor setup and a data rate of 64 kbps.
5 Please refer to the section on MIFA and IFA on page 9
www.cypress.com Document No. 001-91445 Rev. *H 5

5 Antenna Parameters
The following section gives some key antenna performance parameters.
 Return loss: The return loss of an antenna signifies how well the antenna is matched to the 50-Ω transmission line
(TL), shown as a signal feed in Figure 7. The TL characteristic impedance is typically 50 Ω, although it could be a
different value. The industry standard for commercial antennas and testing equipment is 50-Ω impedance, so it is
most convenient to use this value.
Return loss indicates how much of the incident power is reflected by the antenna due to mismatch (Equation 1). An
ideal antenna when perfectly matched will radiate the entire energy without any reflection.
If the return loss is infinite, the antenna is said to be perfectly matched to the TL, as shown in Figure 7. S11 is the
negative of return loss expressed in decibels. In most cases, a return loss ≥ 10 dB (equivalently, S11 ≤ –10 dB) is
considered sufficient. Table 1 relates the return loss (dB) to the power reflected from the antenna (percent). A return
loss of 10 dB signifies that the 90% of the incident power goes into the antenna for radiation.
Equation 1
𝑃𝑃𝑖𝑖𝑖𝑖𝑐𝑐𝑖𝑖𝑖𝑖𝑖𝑖𝑖𝑖𝑖𝑖
𝑅𝑅𝑅𝑅F𝑅𝑅i𝑅𝑅gu𝑅𝑅r𝑅𝑅e 𝐿𝐿7.𝐿𝐿 R𝐿𝐿𝐿𝐿et u(𝑑𝑑rn𝑑𝑑 L)os=s 10log�𝑃𝑃𝑟𝑟𝑖𝑖𝑟𝑟𝑟𝑟𝑖𝑖𝑐𝑐𝑖𝑖𝑖𝑖𝑖𝑖�
Table 1. Return Loss and Power Reflected from Antenna
S11 (dB) Return Preflected / Pradiated /
Loss (dB) Pincident (%) Pincident (%)
–20 20 1 99
–10 10 10 90
–3 3 50 50
–1 1 79 21
www.cypress.com Document No. 001-91445 Rev. *H 6

 Bandwidth: Bandwidth indicates the frequency response of an antenna. It signifies how well the antenna is
matched to the 50-Ω transmission line over the entire band of interest, that is, between 2.40 GHz and 2.48 GHz
for BLE applications.
Figure 8. Bandwidth
As Figure 8 shows, the return loss is greater than 10 dB from 2.33 GHz to 2.55 GHz. Therefore, the bandwidth of
interest is around 200 MHz. Wider bandwidth is preferred in most cases, because it minimizes the effect of detuning
resulting from the changes in the environments around the antenna in actual uses of the product (e.g. mouse placed
on wood/metal/plastic table, hand kept around the mouse, etc.)
 Radiation efficiency: A portion of the non-reflected power (see Figure 7) gets dissipated as heat or as thermal
loss in the antenna. Thermal loss is due to the dielectric loss in the FR4 substrate and the conductor loss in the
copper trace. This information is characterized as radiation efficiency. A radiation efficiency of 100 percent indicates
that all non-reflected power is radiated to free space. For a small-form-factor PCB, the heat loss is minimal.
 Radiation pattern: Radiation pattern indicates the directional property of radiation, that is, which directions have
more radiation and which have less. This information helps to orient the antenna properly in an application.
www.cypress.com Document No. 001-91445 Rev. *H 7

An isotropic dipole antenna radiates equally in all directions in the plane perpendicular to the antenna axis. However,
most antennas deviate from this ideal behavior. See the radiation pattern of a PCB antenna shown in Figure 9 as an
illustration. Each data point represents RF field strength, measured by the received signal strength indicator (RSSI) in
the receiver. As expected, the contours are not exactly circle, as the antenna is not isotropic.
Figure 9. Radiation Pattern
0
345 12 15
330 30
10
315 45
8
300 6 60
4
285 75
2
270 0 90
255 105
240 120
225 135
210 150
195 165
180
 Gain: Gain indicates the radiation in the direction of interest compared to the isotropic antenna, which radiates
uniformly in all directions. This is expressed in terms of dBi—how strong the radiation field is compared to an ideal
isotropic antenna.
www.cypress.com Document No. 001-91445 Rev. *H 8

6 Antennas for Cypress PRoC/PSoC BLE
One of the objectives for Cypress BLE products is to have an antenna design within the tight area that requires no more
than two external components for tuning. Tuning is the process that ensures that near-maximum power is sent to the
antenna while transmitting over the working band of frequencies. This is ensured by making the return loss in the band
of interest greater than 10 dB. When the impedance seen looking into the antenna and the chip output impedance are
the same, maximum power is transferred to the antenna; the same rule holds true for receiving too. Antenna tuning
ensures that the antenna impedance is matched to 50 Ω looking towards the antenna. Radio tuning ensures that the
impedance looks 50 Ω, looking towards the chip, when the chip is in the receive mode.
The integrated balun inside PRoC/PSoC BLE is not exactly 50-Ω impedance and may require two components for
tuning. For a low-data-rate and low-RF-range application, the PCB antenna Cypress recommends does not require any
component for antenna tuning.
For high-data-rate applications like voice recognition over remote control, at least four components for the matching
network are recommended. Two of these will be used for radio tuning and two will be used for antenna tuning. It may
be possible to do the tuning with two components if the resulting bandwidth is acceptable. Having an 6extra component
footprint is a wise design choice for future mitigation of 7EMI radiation in a new product. Filters can be implemented for
out-of-band operation using those components.
Cypress PRoC/PSoC devices can also be employed in applications such as indoor positioning, smart home, smart
appliances, and sensor hub. Because these applications may not have space constraints, you can employ an antenna
with a better RF range and radiation pattern. The wire antenna can be a perfect fit for such an application where the
ID (Industrial Design) can have some height to fit a wire.
In some application like wearable ultra-small form factor is required. The chip antenna usually takes less space
compared to a PCB antenna; it is more popular in this application category. Cypress recommends a few guidelines for
using the ultra-compact chip antennas.
There are many applications that directly embed a Cypress module in the host PCB for wireless connectivity. For such
applications, a very-low-cost, FCC-passed, tiny module is desired. Cypress has come up with EZ-BLE module for such
application. The Cypress EZ-BLE module uses Johansson chip antenna 2450AT18B100E.
Though there are multiple antennas for the 2.4-GHz band, most BLE applications are catered by two Cypress-
Proprietary PCB Antennas. Cypress recommends using two proprietary PCB antennas, meandered inverted-F antenna
(MIFA) and inverted-F antenna (IFA), which are characterized and simulated extensively for BLE applications. MIFA in
particular is useful to most of the applications.
However, you can choose any antenna described in this document to suit your application requirements.
7 Cypress-Proprietary PCB Antennas
Cypress recommends IFA and MIFA types of PCB antennas. The low data rate and typical range requirement in a BLE
application make these antennas extremely useful. These antennas are inexpensive and easy to design, because they
are a part of the PCB, and provide good performance in the 150-250 MHz bandwidth range.
MIFA is recommended for applications that require a minimum PCB area such as a wireless mouse and presenter. IFA
is recommended for applications where one of the antenna dimensions is required to be much shorter than the other
such as a heart-rate monitor. Most BLE applications are catered by MIFA antennas.
6 Extra components before the antenna is a recommended practice that helps in implementing filters for EMI reduction in future.
7 EMI is electro-magnetic interference regulation that sets limit for radiated power for public health.
www.cypress.com Document No. 001-91445 Rev. *H 9

7.1 Meandered Inverted-F Antenna (MIFA)
The MIFA is a popular antenna widely used in human interface devices (HIDs) because it occupies a small PCB area.
Cypress has designed a robust MIFA that offers an excellent performance with a small form factor. The antenna size
is 7.2 mm × 11.1 mm (284 mils × 437 mils), making it suitable for HID applications such as a wireless mouse, keyboard,
or presenter. Figure 10 shows the layout details of the recommended MIFA, both top layer and bottom layer in a two-
layer PCB. The antenna trace-width is 20 mils throughout. The main parameter that would change, depending on the
PCB stack spacing, is the value of “W,” the RF trace (transmission line) width.
Figure 10. MIFA Layout
Top Layer (Antenna Layer)
Transmission line 50 ohm to matching Orange: Top Layer
network Light Blue: Bottom Layer
All dimensions are in mils
Bottom Layer (RF Ground Layer)
Light Blue: Bottom Layer
All dimension are in mils
Note: The Gerber and .brd files of MIFA for a FR4 PCB with 1.6-mm thickness are provided in the AN91445.zip file at
www.cypress.com/go/AN91445.
Note: The flipping of the Antenna pattern (along with ground and keep out area) is fine. The only impact is the rotation
of the radiation pattern.
www.cypress.com Document No. 001-91445 Rev. *H 10

7.2 Antenna Feed Consideration
Table 2 provides the “W” value for different PCB thicknesses between the top and bottom layers for a two-layer FR4
substrate (relative dielectric constant = 4.3) for coplanar waveguide model. The top layer contains the antenna trace;
the bottom layer is the immediate next layer containing the solid RF ground plane. The remaining PCB area of the
bottom layer can be used as a signal ground plane (for the PRoC/ PSoC and other circuitry). Figure 11 relates the PCB
thickness to “W” for a typical two-layer PCB.1
Table 2. Value of “W” for FR4 PCB: Thickness Between Antenna Layer and Adjacent RF Ground Layer
Thickness (mils) W (mils)
60 65
50 59
40 52
30 44
20 33
Figure 11. Clarification of PCB Thickness
Layer 1
Thickness Antenna Layer
(used in Table 2) Layer 2
Ground Layer
Typical two-layer
For the small length of PCB trace that feeds the antenna, the width requirement can be relaxed. Ensure that the antenna
trace width and the antenna feed connection have the same width. Figure 12 shows one such case where the trace
width feeding the antenna is not as wide as recommended in Table 2.
Figure 12. Antenna Feed Width for Short Trace
Only 3 mm trace to
Antenna. Transmission
line width is not critical
However, if it is a long transmission line approximately 1 cm from the matching network to antenna or back to the ANT
pin of the PRoC/PSoC BLE device, Cypress recommends a transmission line (TLine) type of layout, having a specific
width “W” over a bottom ground plane for the feed.
Note: See the coplanar wave guide calculator in Appendix B for the calculation of width for Coplanar transmission line.
www.cypress.com Document No. 001-91445 Rev. *H 11

Figure 13 plots S11 of the MIFA. The MIFA has a bandwidth (S11 ≤ –10 dB) of 230 MHz around 2.44 GHz.
Figure 13. S11 of the MIFA (Return Loss = –S11)
Figure 14 shows the complete 3D radiation-gain pattern of the MIFA at 2.44 GHz. This information is helpful in placing
the MIFA for custom applications to maximize the radiation in the desired direction. In this diagram, the antenna is in
the XY plane; the Z-axis is vertical to it.
Figure 14. 3D Radiation-Gain Pattern for MIFA
www.cypress.com Document No. 001-91445 Rev. *H 12

The radiation pattern is tested with a 30-degree angular resolution on a Pioneer Board carrying a module with a MIFA
antenna. The connecting headers are metals. In a bare board, the radiation pattern is different than what is shown;
this is for illustration only to show how to position the antenna in a PCB. You are encouraged to measure similar pattern
in your final product assembly to determine the best place for the antenna.
www.cypress.com Document No. 001-91445 Rev. *H 13

7.3 Antenna Length Considerations
Depending on the PCB thickness, the MIFA antenna should be length-adjusted to adjust the antenna radiation
impedance and frequency selectivity. Cypress recommends the values listed in Table 3 for antenna lengths for various
board thicknesses.
Figure 15. Length of MIFA
Table 3. Leg and Tip length
PCB Thickness Antenna L_Tip /
L_leg
16 mils L_tip= 353 Mils
31 mils L_tip= 165 Mils
47 mils L_tip= 125 Mils
62 mils L_leg= 115 Mils
Figure 15 shows two MIFA antennas for two different board thicknesses. Antenna designers should refer to Table 3 for
adjusting the length of the MIFA antennas for a specific board thickness.
Please note that the original antenna should start with the full length of antenna. Depending on board thickness the
antenna needs to be length adjusted. You cannot increase length as easily in a board than cutting the length. Table 3
should be taken as a guideline to check final length of the antenna for a given board thickness than an exact figure.
The length cutting is a quick method to tune the antenna. If the customer has space to put matching network component
and competency for antenna tuning, Cypress recommends putting matching network instead of length adjusting.
www.cypress.com Document No. 001-91445 Rev. *H 14

7.4 Inverted-F Antenna (IFA)
IFA is a better antenna compared to MIFA for radiation. Given space availability IFA antenna is a better antenna than
a MIFA antenna. It has better efficiency. However, it requires more area compared to MIFA.
The IFA is recommended for applications in which one of the antenna dimensions is constrained, such as in a heart
rate monitor. Figure 16 shows the layout details of the recommended IFA, both top layer and bottom layer, in a two-
layer PCB. The trace width is 24 mils. The IFA is designed with a size of 4 mm × 20.5 mm (157.5 mils × 807 mils) for
an FR4 PCB with a 1.6-mm thickness. The IFA has a larger aspect ratio (width to height) than the MIFA.
Figure 16. IFA Layout
Top Layer (Antenna Layer)
40 40
12
Bottom Layer (RF Ground Layer)
Orange: Top Layer
Light Blue: Bottom Layer
All dimension are in mils
Note: The Gerber file (as well as the .brd file) for an FR4 PCB with 1.6-mm thickness is provided in the AN91445.zip
file at www.cypress.com/go/AN91445.
www.cypress.com Document No. 001-91445 Rev. *H 15

As explained for the MIFA antenna, the feed trace width “W” is dependent on the PCB stack of the product. Table 4
provides the “W” value for different PCB thicknesses between the top layer (antenna layer) and bottom layer (adjacent
RF ground layer) for an FR4 substrate (relative dielectric constant = 4.3) for coplanar waveguide model.
Table 4. Value of “W” for FR4 PCB: Thickness between Antenna Layer and Adjacent RF Ground Layer for 50-ohm
Impedance
Thickness (mils) W (mils)
60 65
50 59
40 52
30 44
20 33
For short traces less than 3 mm, the width of the trace for antenna feed can be relaxed. The antenna feed can be of
the same width as the antenna trace; see Figure 12. Please refer to coplanar wave guide calculator in Appendix B for
the calculation of width for Coplanar transmission line.
The bandwidth (S11 ≤ –10 dB) of the IFA is 220 MHz around 2.44 GHz, as shown in Figure 17.
Figure 17. S11 of the IFA (Return Loss = -S11)
Figure 18 shows the qualitative radiation pattern of an IFA in the XY plane. This information is helpful in placing the IFA
suitably for custom applications to maximize the radiation in the desired direction. For the sake of brevity, only a
qualitative radiation direction is shown. For detailed radiation patterns in all XY, YZ, and ZX planes, contact Cypress
Technical Support.
Figure 18. Qualitative 2D Radiation Gain Pattern for IFA
Y
Z
X
www.cypress.com Document No. 001-91445 Rev. *H 16

8 Chip Antennas
For applications where the PCB size is extremely small, chip antennas are a good solution (Figure 19). They are off-
the-shelf antennas that take up minimal PCB area and offer reasonable performance. However, chip antennas increase
the BOM and assembly expense, as they are external components that need to be purchased and assembled.
Typically, the price of chip antennas ranges from 10 to 50 cents, depending on the dimension and performance.
Figure 19. Chip Antenna
Another important factor to consider when using chip antennas is that they are sensitive to RF ground size. The
manufacturer’s recommendations must be followed for ground-size considerations. Unlike PCB antennas, chip
antennas cannot be tuned by changing the antenna length. They require an additional matching network for antenna
tuning, increasing the BOM expense even further.
Cypress suggests chip antennas only for specialized applications that demand an extremely small PCB area. For such
applications, Cypress recommends the Johansson Technology antennas mentioned below.
1. 2450AT18B100E
2. 2450AT42B100E
The 2450AT18B100E has dimensions of 63 mils × 126 mils; the 2450AT42B100E has bigger dimensions of 118
mils × 196 mils but provides a better RF performance.
The Cypress BLE module CYBLE-022001-00 uses the 2450AT18B100E antenna and has gone through extensive
characterization for RF performance and pre-compliance testing. Both the chip antenna requires a few layout guidelines
for an optimal RF performance. The following are the major considerations for a chip antenna placement, layout, and
RF performance:
1. Ground clearance around the antenna
2. Antenna placement for optimal radiation
3. Antenna feed consideration
4. Antenna matching network for bandwidth extension
Figure 20 and Figure 21 show the layout guidelines for the chip antenna from Johanson Technology 2450AT42B100E.
See their website for detailed guidelines for these antennas.
www.cypress.com Document No. 001-91445 Rev. *H 17

Figure 20. Layout Guideline for Johanson 2450AT42B100E Chip Antenna
This layout also shows the 50-Ω transmission-line feed and the matching components. The width of the transmission-
line feed depends on the board thickness. The exact width is determined from Table 4.
Figure 21. Johanson Antenna Layout Guideline for 24AT42B100E
The chip antenna performance depends on the ground plane. Generally, these antennas require much bigger ground
plane and larger spacing. The minimum ground clearance shown in Figure 21 is 0.8 mm from the antenna edge to the
ground edge for the 2450AT42B100E part. A better return loss is observed if the clearance is of the order of 2-3 mm.
The chip antenna is not exactly isotropic. There is some preferred direction of radiation. The direction of maximum
radiation varies with the ground clearance and plastic assembly. See Figure 22 for the general directivity of the
Johanson chip antenna (2450AT42B100E).
www.cypress.com Document No. 001-91445 Rev. *H 18

Figure 22. Radiation Pattern from Chip Antenna
Y
axis
Z axis
More X
axis
Average
Le
More ss
Tline
IC paddle
Cypress suggests chip antennas only for specialized applications that demand an extremely small PCB area such as
a nano Bluetooth dongle or an ultra-small module. The Johansson antenna is characterized for RF performance and
pre-compliance in Cypress for Cypress EZ-BLE module. You can use other chip antennas from vendors such as
Murata, Vishay, Pulse, and Taoglas.8
9 Wire Antennas
Wire Antennas are the classical antennas that are conductors of quarter-wave length. They are fixed on the PCB but
rise from the PCB plane and protrude to free space over a ground plane.
They have excellent RF performance as they are exposed to space as a 3D antenna. They have the best range and
have the most isotropic radiation pattern.
For BLE applications requiring a small form factor, they are not preferred as they take a lot of space and vertical height.
However, if space is not a constraint, they can be the best antenna to use in terms of RF range, directivity and radiation
pattern. In general applications such as a smart home controller that plugs into a wall can use this type of antenna.
The wire shape and size need to be optimized for a particular industrial design (ID). The wire can be bent according to
the enclosure. Special care should be taken for manufacturing of the wire antenna as they can be of various shapes
according to the enclosure.
Figure 23. Wire Antenna Layout
Al Wire
No GND
GND Silk Screen
Orange:
Top Layer
Matching Network
Blue:
Bottom Layer
Antenna Feed
8 Only Johansson antenna is characterized; others are not.
www.cypress.com Document No. 001-91445 Rev. *H 19

A wire antenna is the best in RF performance. They have the best antenna efficiency and directivity compared to other
antennas. See Figure 24 for the qualitative radiation pattern out of wire antenna.
Figure 24. Qualitative Radiation Pattern Out of Wire Antenna
10 Antenna Comparison
Use Table 5 as a quick reference to select the appropriate antenna for your application.
Table 5. Comparison of MIFA, IFA, Chip, and Wire Antennas
Properties at 2.44 GHz MIFA IFA Chip Antenna Wire Antenna
Appearance
Recommended Less Area (Mouse, Height Constrain Small Area More Height (6
Applications Keyboard, (Heart Rate (Nano Dongle, BLE mm)
Presenter) Monitor) Module) (3D)
(Sensor Hub)
Dimensions (mm) 7.2 × 11.1 4 × 20.5 3.2 × 1.6 6 × 30
Dimensions (mils) 284 × 437 157.5 × 807 126 × 63 250 × 1200
Gerber File Web Web Refer to datasheet
Cost (US$) Minimal Minimal 0.1–0.5 0.1
Bandwidth (MHz) 230 220 200 200
(S ≤ –10 dB)
11
Gain (dBi) 1.6 1.1 0.5 2
www.cypress.com Document No. 001-91445 Rev. *H 20

11 Effect of Enclosure and Ground Plane on Antenna Performance
Antennas used in consumer products are sensitive to PCB RF ground size and the product’s plastic casing. The
antenna can be modeled as an LC resonator whose resonant frequency decreases when either L (inductance) or
C (capacitance) increases. A larger RF ground plane and plastic casing increase the effective capacitance and thus
reduce the resonant frequency.
11.1 Effect of Ground Plane
As explained before, a monopole PCB antenna requires a ground plane for proper operation.
Figure 25 shows an example where a MIFA is placed on a PCB with a different ground plane size. The PCB size varies
from 20 mm × 20 mm to 50 mm × 50 mm.
The curves show that larger RF ground planes decrease the resonant frequency and better grounding provides better
return loss. This is the key for a good PCB layout. The better the ground provided for the quarter-wave antenna, the
better it will correlate with the theoretical behavior. This is a key concept in antenna design for small modules where
there is hardly enough space for ground clearance.
Figure 25. Effect of PCB Ground Plane Size
www.cypress.com Document No. 001-91445 Rev. *H 21

11.2 Effect of Enclosure
Similar to the effect of the ground plane, to quantify antenna sensitivity to the product’s plastic casing, experiments
were performed on a wireless mouse as shown in Figure 26. The Cypress MIFA is placed inside the plastic casing of
the wireless mouse, and then measurements are made for radiation pattern and return loss.
Figure 26. Effect of Plastic Casing
Both Figure 25 and Figure 26 reveal some important observations:
 The resonant frequency shifts to a lower frequency when the antenna is placed near the plastic casing.
 The shift in resonant frequency is observed to be about 100 MHz to 200 MHz. The antenna must be tuned again
to bring it to the desired band. For antenna tuning, see Guidelines for Antenna Placement, Enclosure, and Ground
Plane.
In conclusion, increasing the ground plane size and plastic casing tends to decrease the resonant frequency of the
antenna by approximately 100 MHz to 200 MHz.
www.cypress.com Document No. 001-91445 Rev. *H 22

12 Guidelines for Antenna Placement, Enclosure, and Ground Plane
 Always place the antenna in a corner of the PCB with sufficient clearance from the rest of the circuit.
 Always follow the antenna designer’s/manufacturer’s recommended ground pattern for the antenna. Commonly
used PCB antennas are variants of a monopole antenna. Monopole antennas need solid ground for proper
operation.
 Never place any component, planes, mounting screws, or traces in the antenna keep-out area across all layers.
The actual keep-out area depends on the antenna used.
 Do not place the antenna close to the plastic in the industrial design. Plastic has a higher dielectric constant than
air. Proximity of the plastic to the antenna results in the antenna’s seeing a higher effective dielectric constant. This
increases the electrical length of the antenna trace and reduces the resonant frequency.
 The battery cable or mic cable must not cross the antenna trace.
 The antenna must not be covered by a metallic enclosure completely. If the product has a metallic casing or a
shield, the casing must not cover the antenna. No metal is allowed in the antenna near-field.
 The orientation of the antenna should be in line with the final product orientation so that the radiation is maximized
in the desired direction.
 There must not be any ground directly below the antenna. See Figure 14.
 There must be enough ground at a distance (ground clearance) from the antenna and this ground plane must have
a minimum width. See Figure 10, Figure 15, and Figure 20.
 Plan to have a provision for an antenna matching network because a lot of parameters in the antenna’s proximity
(plastic, ground variation, substrate differences, and other components) can vary its impedance, and therefore, the
antenna may need retuning. If the impedance of the antenna is unknown, it is preferable to have a provision for a
PI or T network of three components, with 0 ohms populated in series components and no load for shunt
components. This helps you to populate any topology needed for a matching network later.
 When using the matching network values provided by the antenna manufacturer, ensure that you use the trace
length from the antenna to the matching network specified in the manufacturer datasheet or reference design.
 Always verify the antenna matching network with the final plastic enclosure in place and the product placed in
typical use case scenarios. For example, verify a mouse with its plastic held on the hand and placed on a mouse
pad, plastic, wood, metal, or floor.
www.cypress.com Document No. 001-91445 Rev. *H 23

13 RF Concepts and Terminologies
RF layout and antenna tuning require an understanding of RF-specific concepts and demand more attention than
conventional circuit layout. This section introduces the basics of RF design, transmission lines, and characteristic
impedance.
The following concepts and terminologies need to be understood to design an effective RF layout.
• Transmission lines
• Characteristic impedance
• Return loss
• Insertion loss
• Impedance matching
The key element that influences the RF design as against analog design is the impedance of the RF circuit. At low
frequencies, the impedance of a load remains the same when measured at different distances on the trace from the
load. There is also no dependency on the trace width or its uniformity for most applications. Therefore, traces are
represented as just nodes at low frequency. But at high frequencies, the impedance (Z) of an RF circuit changes when
measured at different distances from the load. The change also depends on the substrate used and the dimensions of
the RF trace. Therefore, the trace also becomes a design element in RF schematics.
Transmission lines are media that carry electromagnetic energy through a defined path. Coaxial cables, waveguides,
and the RF trace between the RF pin and the antenna are transmission lines. Most RF traces are transmission lines of
type such as microstrip line and coplanar waveguides.
The key property of a transmission is its characteristic impedance (Z0), which is the ratio of amplitudes of voltage and
current of a wave propagating through a lossless transmission line. For applications at 2.45 GHz such as BLE, a 50-ohm
characteristic impedance is widely used for RF traces.
Figure 27. Equivalent Model of a Transmission Line
Even though Z0 is a real number, it is not the resistance of the RF trace. An ideal transmission does not dissipate energy
or have any loss because of its characteristic impedance. The equivalent model of a transmission line is shown in
Figure 27. It is an attribute representing the ratio of distributed series inductance to distributed shunt capacitance of the
transmission line.
𝐿𝐿
𝑍𝑍0=�
Where L and C are distributed inductance and distributed ca𝐶𝐶pacitance respectively along an arbitrary length of the
transmission line.
The characteristic impedance (Z0) depends on the PCB material, thickness of the substrate, width of the trace, thickness
of the trace, and clearance between the RF trace and ground fill. These parameters are often ignored in conventional
layout and design, but they play a major role in RF design.
www.cypress.com Document No. 001-91445 Rev. *H 24

Figure 28. Representation of an Impedance Measurement Setup
Figure 28 depicts a typical measurement setup for measuring the impedance of an RF circuit. The impedance at a
given point on the RF trace is related to the characteristic impedance of the trace, its distance from the load, and load
impedance; this is summarized in the following equation:
Z = Z0
(𝑍𝑍𝐿𝐿+𝑗𝑗𝑍𝑍0𝑡𝑡𝑡𝑡𝑡𝑡𝑡𝑡𝑡𝑡)
Where Z
(
i
𝑍𝑍
s
th
+
e
𝑗𝑗
im
𝑍𝑍
p
𝐿𝐿
𝑡𝑡
d
a
nc
m
)
easured at a distance l from the load, ZL is the impedance measured at the load (l = 0),
Z0, is the characteristic impedance of the transmission line, and β is the phase constant. J is the reactive part of the
impedance.
Let’s check how the impedance changes in certain special scenarios.
When measured at the load, l = 0, so Z becomes equal to ZL.
When ZL = 0 and l = λ/4, Z = ∞.
When ZL = ∞ and l = λ/4, Z = 0
So, even a short circuit, when measured at a distance of one-quarter of a wavelength (λ/4), is seen as an open circuit
and vice versa. In conventional circuit design, the trace lengths never approach λ/4, so this behavior is not seen.
When ZL= Z0, Z = Z0 for any value of l.
Therefore, when the load impedance (ZL) is equal to the characteristic impedance (Z0), the impedance (Z) measured
remains equal to Z0 when measured at any distance (l) from the load. For this reason, it is a common practice to
transform the impedance of any RF device to Z0 using a matching network before taking an RF trace to other devices.
A matching network is a passive circuit used to transform any given impedance to (usually) the characteristic impedance
of the RF trace. To ensure maximum power transfer from the source to load through RF circuits, the source impedance
and load impedance should be matched.
As the impedance of a circuit changes with the distance from the circuit, the placement of the components for
impedance matching is also dependent on the distance from the circuit to be matched. Even small stubs across the RF
trace act as capacitors or inductors and can change the impedance. Refer to Figure 29 for an example of stub.
Figure 29. Examples for Stubs
www.cypress.com Document No. 001-91445 Rev. *H 25

An open-circuited stub of a length less than λ/4 is equivalent to a capacitor and a short-circuited stub of a length less
than λ/4 is equivalent to an inductor. So stubs can be used in place of components for narrow-band applications at RF
frequencies. However, unless intentionally designed, the stubs or branches in RF traces affect the impedance matching,
resulting in a low RF performance.
Figure 30. Representation of Source Load and transmission line in an RF circuit
The effectiveness of the matching network is measured by using the parameters return loss and insertion loss.
Figure 30 shows a typical RF circuit with a source transmitting RF power and a load taking most of the RF power and
reflecting some of the RF power. Return loss is the ratio of incident power to the reflected power. Insertion loss indicates
the fraction of power lost through the circuit before reaching the next stage.
Return Loss (dB) = 10 * log ( )
𝐼𝐼𝑡𝑡𝐼𝐼𝐼𝐼𝐼𝐼𝐼𝐼𝑡𝑡𝑡𝑡 𝑃𝑃𝑃𝑃𝑃𝑃𝐼𝐼𝑃𝑃
Insertion Loss (dB) = 10 * log𝑅𝑅 ( 𝐼𝐼𝑅𝑅𝑡𝑡𝐼𝐼𝐼𝐼𝑡𝑡𝐼𝐼𝐼𝐼 𝑃𝑃𝑃𝑃𝑃𝑃𝐼𝐼𝑃𝑃 )
𝐼𝐼𝑅𝑅𝐿𝐿𝑅𝑅𝑅𝑅𝑅𝑅𝑅𝑅𝑑𝑑 𝑃𝑃𝐿𝐿𝑃𝑃𝑅𝑅𝑅𝑅
In an ideal matching network, a ll the power is transferred to the next stage, and no power is reflected. This would result
𝐼𝐼𝑅𝑅𝐼𝐼𝐼𝐼𝑑𝑑𝑅𝑅𝑅𝑅𝑅𝑅 𝑃𝑃𝐿𝐿𝑃𝑃𝑅𝑅𝑅𝑅
in zero insertion loss and infinite return loss. In practical circuits, the desired return loss could be anywhere from 6 dB
to 30 dB, depending on the application and the use case. In a matching network, the return loss translates to insertion
loss, as indicated in Table 6.
Table 6. Return Loss versus Insertion Loss
Return Percent of Percent of Insertion
Loss(dB) Power Reflected Power Inserted Loss(dB)
0.01 99.77 0.23 26.38
0.1 97.72 2.28 16.42
1 79.43 20.57 6.87
2 63.1 36.9 4.33
3 50.12 49.88 3.02
4 39.81 60.19 2.2
5 31.62 68.38 1.65
6 25.12 74.88 1.26
7 19.95 80.05 0.97
8 15.85 84.15 0.75
9 12.59 87.41 0.58
10 10 90 0.46
15 3.16 96.84 0.14
20 1 99 0.04
30 0.1 99.9 0
www.cypress.com Document No. 001-91445 Rev. *H 26

13.1 Smith Chart
In RF design, it is also important to understand and use the Smith chart (Figure 31), a graphical tool to plot the complex
impedance, which is also useful in designing a matching network. The tool enables you to quickly calculate many
parameters, such as admittance, return loss, insertion loss, reflection coefficient, Voltage Standing Wave Ratio
(VSWR), and transmission coefficient from the complex impedance. It also lets you calculate the impedance with
changes in distance from load. Using Smith Chart, you can quickly design a matching network using RF stubs or RF
passives.
Note the following in the diagram:
1. The left corner of the Smith chart indicates zero ohms and the right corner indicates open circuit.
2. The circles touching the right corner are constant-resistance circles.
3. The real part of the impedance is constant across all points in a constant-resistance circle.
4. The curves between the right corners and the periphery of the Smith chart are constant-reactance circles.
5. The imaginary part of the impedance is constant at all points along a constant-reactance curve.
6. The circles in Smith chart that touch the left corner are constant-conductance circles.
7. The real part of the admittance is constant along a constant-conductance circle.
8. The curves between the left corner of the Smith chart and periphery of the Smith chart are constant-susceptance
curves.
9. The imaginary part of the admittance is constant along a constant-susceptance curve.
10. The center of the circle is the Z0 point. In this case, Z0 = 50 ohms. This is also the 20-millisiemens (mS) point.
11. Two special circles are the 50-ohm circle and 20-mS circle.
The first step in the impedance matching is to transform the impedance such that it falls on either the 50-ohm circle or
the 20-ms circle. The second step is to move the impedance from either of this circle to the 50-ohm point. The matching
network topology also depends on whether the impedance falls inside or outside these circles.
This application note explains how to design a matching network using Smith charts in the section about matching
network. For more information on the Smith chart, refer to the user guides and tutorials available online. Links to some
of them are given below:
 http://www.microwaves101.com/encyclopedias/smith-chart-basics
 https://www.youtube.com/watch?v=vDU5XnvZXwc
www.cypress.com Document No. 001-91445 Rev. *H 27

Figure 31. Smith Chart with Impedance and Admittance Circles
www.cypress.com Document No. 001-91445 Rev. *H 28

14 Impedance Matching
Impedance matching is required to ensure most of the power from the RF source is delivered to the load. In a typical
example using PRoC BLE/PSoC BLE, during transmission, the PSoC BLE is the source while the antenna is the load.
During reception, the antenna is the source and the PSoC BLE is the load. When the impedance of the PSoC BLE and
antenna are not 50 ohms, they need to be matched to 50 ohm. AT RF frequencies, the impedance measured changes
with the distance from the load/source (impedance rotates around the characteristic impedance of the RF trace in a
Smith chart clockwise when moving away from the load/source). Figure 32 depicts the impedance change with trace
length.
Figure 32. Smith Chart Depicting Impedance Change with Trace Length
Therefore, the matching network also would need to change with the distance from the source/load. When the
impedance measured is equal to the characteristic impedance, it does not change with distance from the source/load.
So, the recommended technique is to match the complex source impedance to the characteristic impedance using a
matching network near the source and to match the load impedance to the characteristic impedance using a matching
network near the load. This ensures that the matching network component values do not change with length of the
trace as long as the source matching network is kept close to the source and the load matching network is kept close
to the load.
For 2.4 GHz, most of the devices available are matched for 50-ohm impedance. For this reason, Cypress uses and
recommends a 50-ohm characteristic impedance for the RF trace.
Any given impedance (except short and open) can be matched to 50 ohms with two reactive passives components
(inductors or capacitors). While it is possible to achieve inductance and capacitance using RF stubs, they usually take
up an additional space in the PCB. Because of the size constraints, it is preferable to use capacitors and inductors for
impedance matching.
Adding a series inductor moves the impedance along the constant resistance circle clockwise, as shown in Figure 33.
The inductor value needed to move the reactance on the Smith chart by a factor of XL is given by the following equation:
L =
XL
Adding a series capacitor moves the impedance along the constant resistance circle in a counterclockwise direction.
2𝜋𝜋f
The capacitor value needed to move the reactance on the Smith chart by a factor of XC is
C =
−1
Adding a shunt inductor moves the impedance along the constant conductance circle in an anticlockwise direction. The
2𝜋𝜋fXC
inductor value needed to move the conductance by YL is
www.cypress.com Document No. 001-91445 Rev. *H 29

L =
−1
Adding a shunt capacitor moves the impedance along the constant conductance circle in a clockwise direction. The
2𝜋𝜋fYL
capacitor value needed to move the conductance by YC is
C =
YC
The first step would be to bring the impedance to the 50-ohm circle or 20-mS circle. The next step is to move the
2𝜋𝜋f
impedance to the 50-ohm point. With this basic information, you can use the Smith chart to design a matching circuit
by using capacitors and inductors to move the impedance to the 50-ohm point.
Figure 33. Smith Charts Depicting Impedance Changes with Addition of Reactance
www.cypress.com Document No. 001-91445 Rev. *H 30

14.1 Matching Network Topology
The topology of the components needed to transform any given impedance to 50 ohms depends on the measured
impedance. Impedance can be measured using a vector network analyzer. The impedance has to be measured at a
point very close to the matching network.
When the impedance measured falls within the 50-ohm circle in the Smith chart, it needs either a shunt inductor followed
by a series capacitor or a shunt capacitor followed by a series inductor from the load, as shown in Figure 34. The shunt
element can bring the impedance on the 50-ohm circle. The series element can then be used to move the impedance
to the 50-ohm point.
Figure 34. Matching Network Topologies to Use When Impedance Is Within 50-Ohm Circle
www.cypress.com Document No. 001-91445 Rev. *H 31

When the impedance measured falls within the 20-mS (millisiemens) circle in the Smith chart, it needs a series capacitor
followed by a shunt inductor or a series inductor followed by a shunt capacitor from the load, as shown in Figure 35.
Using the series component, the impedance can be brought on the 20-mS circle. Then, using the shunt component, it
can be brought to the 20-mS (50-ohm) point.
Figure 35. Matching Network Topologies to Use When Impedance Is Within 20-mS Circle
www.cypress.com Document No. 001-91445 Rev. *H 32

When the impedance measured falls outside these two circles, on the positive half of the Smith chart, it can be matched
either by using a series capacitor followed by a shunt inductor or capacitor or by using a shunt capacitor followed by a
series inductor or capacitor from the load, as shown in Figure 36.
Figure 36. Matching Network Topologies to Use When Impedance Is Outside the Two Circles, on Positive Half of
Smith Chart
www.cypress.com Document No. 001-91445 Rev. *H 33

When the impedance measured falls outside these two circles, on the negative half of the Smith chart, it can be matched
either by using a series inductor followed by a shunt inductor or shunt capacitor or by using a shunt inductor followed
by a series inductor or capacitor from the load, as shown in Figure 37.
Figure 37. Matching Network Topologies to Use When Impedance Is Outside the Two Circles, on Negative Half of
Smith Chart
www.cypress.com Document No. 001-91445 Rev. *H 34

14.2 Tips for Matching Network
Use the following tips to minimize the gap between theory and practice in the matching network design:
 Measure the impedance at the same point where components have to be placed.
 Calibrate the network analyzer setup with cables and connectors until the impedance measurement point.
 Place the shunt components on the RF trace itself. Do not use long traces to connect to the shunt components.
 Choose capacitors that have a series resonant frequency at least twice the frequency of operation.
 Choose inductors that have a self-resonant frequency at least twice the frequency of operation.
 If the parasitic impedance data is available in the datasheet, use it to derive the actual reactance achievable with
that component.
 Use only high-Q components for both capacitors and inductors.
Because the impedance is typically unknown during design time, a design with three components in a П or T fashion
allows you to use all the possible topologies later.
15 Antenna Tuning
Antenna tuning is the process of ensuring that the return loss is greater than 10 dB for the antenna, when looking from
the chip output towards antenna, in the desired frequency band. The same tuning procedure should be followed when
looking into the radio and making sure that impedance is 50 Ω in the receive mode. A return loss greater than 10 dB,
ensures that 90% of the power output of the chip is transmitted to the antenna. Similarly, in receive mode, it is ensured
that 90% of the received power is transferred to the radio. Both antenna tuning and radio tuning are referred to as
antenna tuning.
The power transfer is maximized by ensuring the output impedance of the radio is complex conjugate of the antenna
impedance. In most antenna tuning this is achieved by transforming the antenna impedance to 50 ohm and balun to
50 ohm, by passive components known as matching network components. For a small primer on matching network
design refer to Section 14. Please refer to Appendix B for more references on matching network design.
Figure 38. Reference for Tuning and Matching Network
The 50-Ω reference point is connected to the network analyzer port. When tuning the antenna, the chip side is
disconnected by removing the balun-matching components. When performing tuning of the radio the antenna-matching
components are disconnected. Having a 50 ohm reference point is a convenience as most standard instruments are
suited for 50 ohm port impedance.
www.cypress.com Document No. 001-91445 Rev. *H 35

In Figure 38 even though six components are shown, you can tune the antenna using only two components. The
antenna tuned by PCB length design does not need any component. The radio side requires only two components to
attain 50-ohm impedance. In most applications using Cypress MIFA the antenna is made 50 ohm by correct length.
The radio side uses 2 components at most for getting to 50 ohm in receive mode. For application using a non-50-ohm
chip antenna, two or more components may be required for the antenna to get to 50 ohm (follow the recommendations
of the chip Antenna manufacturer). For the radio, two components are required to get to 50 ohm.
The following section describes the step-by-step procedure for antenna tuning by using a network analyzer. For antenna
tuning, you need to look towards the antenna.
15.1 Tuning Procedure
As explained in Section 11, the effect of enclosure and ground detunes the antenna from the desired band and affects
the return loss. Thus, antenna tuning is a two-step process where the bare PCB is tuned for the desired band first, and
then in the second phase after the industrial design is finalized, the tuning is checked with the plastic enclosure and
human body contact.
A basic familiarity with Smith Chart is required for antenna tuning by Network Analyzer. Without loss of generality the
readers are encouraged to read about Smith chart. The antenna tuning is checked with a network analyzer. A network
analyzer is an instrument which characterizes the s parameter, such as S11 and S21. The S11 is an indication of return
loss and S21 is the forward transmission ratio. Interested readers are encouraged to refer any of the links provided
below.
As the first step, the network analyzer is calibrated, and then the antenna is tuned by adjusting the matching network
components and verifying the tuning in the Smith chart.
The tuning procedure uses the following:
 Agilent 8714ES network analyzer (calibrated)
 Cypress CY5682 kit mouse as DUT
 A semi-rigid cable with 50-ohm characteristic impedance up to 5 GHz
 A high-Q RF component (this example uses Johanson kit P/N: L402DC)
The following major steps are required to tune the antenna:
1. Prepare the ID
2. Set up and Calibrate Network Analyzer
3. Tune the Bare PCB Antenna
4. Adjust Tuning with Plastic and Human Body Contact for Antenna
5. Tune the Radio Side by Putting the Chip in Receive Mode
15.1.1 Prepare the ID
This is a very important step as the placement of the coaxial cable can show variations in S11 by up to 3 dB. The ground
connection of the coaxial cable shield should be as close to the transmission line return path as possible. The basic
steps of ID preparation are given below.
1. Open the plastic casing and remove the batteries or power supplies.
2. Connect the coaxial cable close to the RF out pin from the chip. Remove the connection from the chip. If not, the
balun will load the coaxial cable in addition to the antenna. See Figure 39.
3. Ensure that there is an exposed ground near to the tip of the coaxial cable. Connect the sheath or the shield of the
cable to ground.
While connecting the shield/sheath to ground, ensure that it is as short as possible. The shorter the distance, the
better the tuning accuracy. There can be 3-dB differences in return-loss measurement depending on where the
coaxial cable is connected to ground.
4. Connect a 10-pF capacitor from the first pad going from the 50-Ω reference point to the antenna tip.
There should always be a capacitor between the coaxial cable and the antenna. This blocks the DC to and from
the network analyzer.
www.cypress.com Document No. 001-91445 Rev. *H 36

Figure 39. Coax Connection Point
15.1.2 Set up and Calibrate Network Analyzer
1. Connect the 3.5-mm calibration kit for calibration and then press the ‘cal’ button on the Agilent 8714ES network
analyzer after setting the calibration kit option from the network analyzer to 3.5 mm. You can use any other
calibration kit such as a type N calibration kit.
2. Press the frequency button and set the start and stop frequency to 2 GHz and 3 GHz respectively, and then set
the format to Smith chart.
3. Press the marker button and set markers to 2.402 GHz, 2.44 GHz and 2.48 GHz.
4. Press the cal button, select S11 on the network analyzer and then set it to ‘user 1 port calibration’.
5. When prompted to connect the ‘open’ load, connect the “Open fixture” to the VNA and press ‘measure standard’.
6. Connect the “Short Fixture” and press measure standard.
7. Connect the “Broadband load” fixture and press ‘measure standard’. After this, the network analyzer will calculate
the coefficient and display the 50-Ω load as a point on the Smith chart exactly marked “50, 0.”
8. Connect the tuning coaxial cable and set the electrical delay by pressing the ‘scale’ button and setting the electrical
delay correctly.
15.1.3 Tune the Bare PCB Antenna
There are two methods to tune the antenna to bring it near 50 ohm.
1. Length adjustment of the antenna if it is a PCB trace or a wire antenna, by cutting off the extra length
2. Use of a matching network (recommended practice)
www.cypress.com Document No. 001-91445 Rev. *H 37

For PCB trace antennas or wire antennas, it is often easier to adjust the length of the PCB trace antenna by scrapping
off the extra length at the end of the antenna trace. For this, it is advised to keep the length of the antenna a little longer
than the Cypress-recommended length and later cut the length to get the resonance around 2.4 GHz. This is a crude
method and does not require any additional components.
However, the matching network method is the most widely used method as it gives the flexibility in future to implement
additional filtering for passing EMI/EMC and has a better repeatability. However, the matching network method requires
expertise. Contact Cypress Technical support for tuning support for high-volume manufacturing. Use the following
procedure to tune the bare PCB using matching network method.
Appendix B provides a systematic method to design matching network once the impedance is measured. This section
below describes an example of antenna or radio tuning using matching network components. The reader is assumed
to have some familiarity with Smith Chart.
1. Connect an 8.2-pF or 10-pF capacitor in series with the antenna. In the band of interest, it acts as 0 Ω. This gives
the antenna impedance. The impedance of antenna is at (100.36 –j34.82), shown as a dot in the Smith chart.
Figure 40. Smith Chart of Antenna Only
2. After determining the antenna impedance, use L-C components to bring it to 50-Ω impedance by performing an
impedance transformation.
3. Impedance transformation networks are networks that transform one impedance value to the required impedance
without consuming any power. Refer to the impedance transformation property of the L and C resonating networks.
Without going to the detail of the matching networks, you can see that most of the matching networks (Figure 41)
for Cypress MIFA or IFA can be met by two components.
www.cypress.com Document No. 001-91445 Rev. *H 38

Figure 41. Matching Network
Chip Ant Chip Ant
Chip Ant Chip Ant
The matching network components can be simulated in a standard open-source tool like Smith V3.10 from Bern
Institute. By putting a shunt capacitor of 0.45 pF with the antenna and a series inductor of 3.6 NH, the impedance is
transformed to 50 Ω, and the imaginary part is cancelled out mostly in the band of interest. Because the exact values
are not available, a 0.5-pF shunt capacitor and a 3.6-nH series inductance are chosen.
Figure 42. Moving to 50 Ω in Smith chart
The final schematic of the matching network is shown below. Z represents the impedance of the antenna alone when
L
seen through a 0-ohm resistor. Zin is the impedance seen by a network analyzer with a 50-ohm output impedance.
www.cypress.com Document No. 001-91445 Rev. *H 39

Figure 43. Theoretical Matching Network
The simulation software gives us an idea of what the component values should be. However, the real component values
differ significantly from the simulated values. This is because at 2.4 GHz, the lead inductance of the capacitance, the
parasitic loading of pads and the ground return path create extra parasitic that completely change the Smith chart. For
this application, choose 0.7-pF capacitor and a series 1.2-pF capacitor to attain resonance. This is very common in
the 2.4-GHz RF tuning with standard components.
Figure 44. Real Matching Network
An explanation of this behavior follows:
The antenna impedance was seen through an 8.2-pF capacitor that was assumed to be 0 ohm. However, the parasitic
of the lead inductance at 2.4 GHz is added to this number. In addition, the ground return was immediate after the
antenna. However, with the matching component populated, the ground return path adds an extra parasitic. Therefore,
the antenna already sees enough inductance. To tune it, some capacitance is added. This is a classical problem in
antenna tuning where the theory and practice differ: you add a capacitance, but it results in the Smith chart moving in
the direction as if adding an inductance. Figure 45 shows the final Smith chart with the real components.
www.cypress.com Document No. 001-91445 Rev. *H 40

Figure 45. Smith Chart with Real Components
From Figure 45, it is clear that all the marker point 1, 2, 3 representing 2402 MHz, 2440 MHz, and 2480 MHz are close
to the (50,0) point on the Smith chart. This shows a good match.
The return loss is plotted for the following component values. A return loss greater than 15 dB is good enough for this
application.
Figure 46. Return Loss with Real Components
As seen Figure 46, the return loss is greater than 15 dB for the marker 1, 2 and 3.
www.cypress.com Document No. 001-91445 Rev. *H 41

15.1.4 Adjust Tuning with Plastic and Human Body Contact for Antenna
A plastic casing on the PCB changes the antenna tuning. Any antenna can be affected because of objects in near field.
The near field is the region close to the antenna where the fields have not formed yet. The magnetic field and the
electric fields are not orthogonal to each other. It takes up to 4-mm distance from the antenna to have radiated electric
and magnetic fields formed properly. After this distance, the far field starts. In the far field region, the electric and
magnetic fields are orthogonal to each other. The radiation pattern in a far field region remains same with respect to
angular position. Near-field obstructions detune the antenna and may kill the antenna radiation. If it is a narrow-band
antenna, there are very high chances of objects in its near field disturbing the antenna.
A plastic casing or a battery cable running nearby can completely detune the antenna and in the band of interest from
2.402 GHz to 2.482 GHz, it can exhibit a return loss less than 10 dB. Therefore, after the bare PCB is tuned, it is
essential that the PCB is kept in the plastic casing and checked for the tuning again with a hand on the device. This is
cumbersome to do, especially with the coaxial cable coming out of the plastic assembly. The coaxial can be brought
out by drilling a small hole in the ID. Finally, the tuning is checked with plastic and also a by placing a hand on the
plastic, simulating a user’s operation of the device. The effect on return loss was observed to be minimal.
Figure 47. Smith Chart with Plastic Assembly, Illustration of Connecting with ID
15.1.5 Tune the Radio Side by Putting the Chip in Receive Mode
The radio tuning is similar to bare PCB tuning as explained in section 13.1.3. For radio tuning the antenna side is
disconnected and network analyzer is connected to the 50-ohm reference point. The chip is powered and put in
continuous receive mode. The matching component is adjusted to get a 50 ohm looking into the chip from network
Analyzer by the use of Smith Chart.
At the end, you have a 50 ohm looking towards the antenna at the reference point and 50 ohm looking into the chip
from the reference point. Thus, you ensure the maximum power transfer by ensuring that the two sides are complex
conjugate of each other.
www.cypress.com Document No. 001-91445 Rev. *H 42

16 RF Transmission Lines
RF transmission lines are media that carry RF power from a source to a load through a structured path. Transmission
lines need to follow a certain discipline to enable power delivery from source to load with minimal loss. While there are
several types of transmission lines, on PCBs, the two most popular types of transmission line are:
 Microstrip line
 Coplanar waveguide (CPWG)
Both of these are PCB traces differing in how they are constructed. These transmission lines are popular at high
frequency because they are simple, cost-effective, and have plenty of tools to calculate their electrical parameters. In
transmission lines, the transmission of RF power happens as an electromagnetic field as opposed to the electrical
current at low frequencies. In both of these transmission lines, a part of the electromagnetic field exists in the air and
a part in the substrate. The dielectric constant of Air is 1 while that of the substrate >1. As a result, the effective
dielectric constant for the transmission line is less than the dielectric constant of the substrate itself.
As the PCB designer, you should ensure that the RF trace the transmission lines use has a 50-ohm characteristic
impedance. Several layout and design software packages include impedance-calculation tools. There are also several
free tools, such as AppCAD and Qucs that can calculate the characteristic impedance from PCB parameters. The
following are links to some free online tools for impedance calculation:
 http://www.eeweb.com/toolbox/microstrip-impedance
 http://www.mantaro.com/resources/impedance_calculator.htm
16.1 Microstrip Line
A microstrip line has a signal trace on top of a substrate with a ground plane beneath the substrate. Figure 48 shows
a snapshot of the cross-section of the microstrip line. The following major factors affect the characteristic impedance
of a microstrip line:
 Substrate height (H)
 Dielectric constant of the substrate (εr)
 Width of the trace (W)
 Thickness of the RF trace (T)
Figure 48. Cross-Sectional View of Microstrip Line
A microstrip is simple to construct, simulate, and fabricate. The effective dielectric constant of a microstrip is larger than
that of a coplanar waveguide for a given substrate. These result in a relatively compact layout compared to a coplanar
waveguide.
www.cypress.com Document No. 001-91445 Rev. *H 43

16.2 CPWG (with Bottom Ground)
A CPWG is similar to a microstrip, but it has copper filling on either side of the RF trace with a gap between them, as
shown in Figure 49.
Figure 49. Cross-Sectional View of a CPWG with Bottom Ground Plane
The characteristic impedance of a CPWG depends on the following factors:
 Substrate height (H)
 Dielectric constant of the substrate (εr)
 Width of the trace (W)
 The gap between the trace and the adjacent ground fill (G)
 Thickness of the RF trace (T)
CPWG may be preferred over microstrip for the following reasons:
 It provides a better isolation for RF traces and a better EMI performance.
 It makes it easier to support the grounding of shunt elements on an RF trace.
 It reduces cross-talk with other traces.
 It has a low loss at very high frequencies compared to a microstrip line.
16.3 RF Trace Layout Considerations
The following are the guidelines for RF trace design:
 Choose the right kind of transmission line (microstrip or CPWG) when calculating the trace width needed for a
50-ohm characteristic impedance.
 Ensure that the RF trace has a 50-ohm characteristic impedance. Use impedance calculators to calculate the trace
width and gap needed for a given stackup.
 The characteristic impedance must be constant throughout the trace. Therefore, maintain a constant width for the
RF trace. For the CPWG, maintain a constant gap between the RF trace and the adjacent ground.
 For the CPWG, ensure that the gap between the grounds in the top layer is less than the height of the substrate;
otherwise, the trace will be predominantly microstrip.
 For the CPWG, ensure that the ground pour area on either side of the trace is wider than the gap between the
grounds.
www.cypress.com Document No. 001-91445 Rev. *H 44

Some of the commonly made mistakes in the design of RF trace and the correct way to do them are represented
in Figure 50 and Figure 52.
Figure 50. Common Mistakes in RF Trace
 Ensure a clean, uninterrupted ground beneath the RF trace without any other traces crossing the RF trace to allow
a proper return path for the RF currents.
 Maintain the shortest possible length for the RF trace because the traces and the substrate below attenuate the
RF signal proportionate to the length.
 Avoid bends in the RF trace. If bends are unavoidable, make a curved bend instead of a sharp bend to maintain a
uniform width. For a right-angled turn, mitering can be done, as shown in Figure 51.
This ensures that the impedance is
Figure 51. Mitering of a Right-Angled Turn
continuous across the bends.
)
𝑊𝑊
where −1.35𝐻𝐻
𝑀𝑀 =𝑊𝑊(1.04+1.3∗𝑅𝑅
M is the width of mitering.
W is the width of the RF trace.
H is the height of the substrate.
 Avoid stubs or branching in the RF trace. Stubs have reactive impedance and affect impedance matching. While
following the reference design, ensure that components are placed on the RF traces in an exact manner as shown
in the reference designs. For example, taking a branch from the RF trace to place a shunt component would alter
impedance matching; in that case, using the same component value as the one in the reference design may not
work in the new design.
 Do not place any other traces close to and parallel to the RF trace. This causes mutual coupling of the signals
between traces.
 Do not place test points on the RF trace. They act as stubs and affect impedance matching.
www.cypress.com Document No. 001-91445 Rev. *H 45

Figure 52. Stubs, Test Points, and Parallel Traces
17 PCB Stackup
17.1 Four-Layer PCB
Cypress strongly recommends the use of four-layer boards for all RF designs. Four-layer PCBs offer a complete ground
and power plane and simpler signal routing. Use the following stackup for four-layer PCBs:
Top layer RF IC and components, RF trace, antenna, decoupling capacitors, and other signals
Layer 2 Ground plane
Layer 3 Power plane
Bottom layer Non-RF components and signals
A complete layer of power plane offers a low resistance and a distributed decoupling capacitance along with the ground
plane. The RF trace width for a 50-ohm characteristic impedance depends on the thickness of the substrate between
the RF trace and the ground plane beneath it. PCBs of the same board thickness may come with different spacing
between the metal layers, which may differ from one manufacturer to another. It is recommended that you consult the
PCB vendor and obtain the stackup before design. When changing the PCB vendor, if the new vendor does not offer
the same stackup, the RF trace width needed to get a 50-ohm impedance needs to be calculated with the new stackup,
and the RF trace in the layout needs to be modified to the new width.
17.2 Two-Layer PCB
Two-layer boards are typically chosen for simpler and cost-sensitive applications. When used, they should be as thin
as possible because the RF trace width for a given characteristic impedance is directly proportionate to the substrate
height. Therefore, thick PCBs (greater than 0.8 mm) result in wider RF traces and make signal routing difficult. Wider
RF traces also trigger spurious parasitic wave modes.
For routing the power supply, use thick traces on the top layer only.
Use the following plan for two-layer boards:
Top layer RF IC, all components, RF trace, antenna, decoupling capacitors, power, and other signals
Bottom layer Solid ground plane
If it is not possible to have a complete ground plane at the bottom, try to ensure a complete ground plane below the
entire radio section.
www.cypress.com Document No. 001-91445 Rev. *H 46

18 Ground Plane
The ground layer is extremely important in RF PCB design. The return path for the RF signal is in the ground plane
beneath the RF trace. For good RF performance, the return path should be uninterrupted and as wide as possible. If
the ground plane is interrupted, return currents find the next smallest path around the interruption. This forms a current
loop, adding undesired inductance, affecting the impedance match between the radio and antenna, and attenuating
the RF signal significantly. If the ground plane beneath the RF trace is narrow, it does not behave like a microstrip and
may have more signal leakage.
18.1 Ground Plane Considerations
 Do not have traces running across the RF trace in the ground plane. It is better to keep a layer completely dedicated
for ground, even for two-layer PCBs.
 Fill the unused area in the top and bottom layers with ground and connect it with the ground plane with many vias
spaced not more than one-twentieth of the wavelength of the operating frequency.
 It is not recommended to use two-layer boards for the CSP package, as the signals need to be brought out through
the second layer. This makes the design of an uninterrupted ground plane difficult for RF signals.
 Do not have split grounds unless you can ensure that no current loops are formed in the ground for the current in
the return path.
 Allow a wide ground plane beneath the RF trace. Narrow ground planes permit parasitic modes of transmission
and increase leakage.
 The bottom ground plane, together with the top ground plane and vias between the two ground planes, ensures
that all traces are well shielded. This arrangement significantly improves the EMI and EMC performance.
 It is recommended to cover the corners of the power plane with via holes connecting ground planes on either side
of the power plane. This helps to arrest any unwanted EMI emitted from the power plane through board edges.
19 Power Supply Decoupling
The power supply needs decoupling capacitors to filter out noise from the IC to prevent it from reaching the other
devices and vice versa. Power supply noise in the radio can increase the phase noise of the frequency synthesizer,
resulting in poor signal quality. It could cause instabilities in the RF output resulting in undesired interference and
spurious radiations exceeding the regulatory limits. In the receiver, it increases the packet error and reduces the
sensitivity.
Several capacitors in parallel may be required to filter out the noise at different frequencies. The capacitor has the least
impedance at its self-resonant frequency (SRF). Therefore, capacitors are most effective around their SRF. To provide
the best noise isolation, it is better to identify all noise-frequency components, consult the capacitor datasheet, and pick
capacitors that have an SRF close to those frequencies.
In addition, it is better to provide a large capacitor that can meet the sudden in-rush current needs of the IC (such as at
the beginning of an RF transmission or reception). The value of the capacitor depends on the in-rush current and the
amount of voltage drop allowed. The capacitance (C) needed to support an in-rush current of ‘I’ for duration of dt for a
voltage drop of dV can be calculated using the following formula:
C = I / (dV/dt)
For example, to support an in-rush current of 20 mA for 15 µs for a maximum 300-mV drop from 3.3 V, the capacitance
needed is 1 µF.
For PSoC 4 BLE / PRoC BLE, it is recommended to use a 0.1-µF capacitor on all power supply pins and a 1-µF bulk
capacitor for each net (one for VDDD, one for VDDA, and one for VDDR). In addition, it is recommended that you have
a 10-pF decoupling capacitor on pin 15 for the QFN package and pin J6 for the CSP package to filter any PLL noise
on the power supply.
For PSoC 6 MCU with Bluetooth Low Energy (BLE) Connectivity, it is recommended to use a 3.3-µF capacitor for VRF,
2.2 µF for VDCDC, 4.7 µF for VBUCK1 and a 0.1 µF with 10-µF decoupling capacitors for VDD_NS. For all other power
supply pins of PSoC 6 MCU with Bluetooth Low Energy (BLE) Connectivity, it is recommended to have a 1-µF and 0.1-
µF capacitor. Use low ESR capacitors for effective decoupling.
www.cypress.com Document No. 001-91445 Rev. *H 47

19.1 Power Supply Decoupling Layout Considerations
Note the following best practices when laying out the power supply traces:
 Place the components as close to the supply pin as possible.
 Place the smallest-value capacitor closest to the power supply pin.
 Place the decoupling capacitor on the same layer as the IC. If it is not possible to place all the capacitors on the
same layer, give priority to smaller values.
 The power supply should flow through the decoupling capacitors to the power supply pin of the IC. Avoid using
supply vias between the component and the pin.
 Use separate vias to ground for each decoupling capacitor. Do not share vias.
 For four-layer boards with a separate power plane, use separate vias for each power supply pin to the power plane.
It is recommended not to share the vias.
 Some of the commonly made layout issues related to power supply decoupling are shown in Figure 53.
Figure 53. Power Supply Decoupling Mistakes
20 Vias
Vias are critical in enabling signal connectivity across layers in multilayer boards. However, they are highly parasitic
and can cause havoc at the RF frequency if not properly used. For example, sharing a via between two different
sections of the circuit increases the common-mode noise between them. A ground via placed far from a shunt
component changes the impedance of the component seen at the trace, resulting in an impedance mismatch. At high
frequency, the parasitic inductance will result in the via having a considerable impedance.
The following guidelines help ensure a proper RF layout:
 Use plenty of vias spaced not more than one-twentieth of the wavelength of the RF signals between ground fillings
at the top layer and inner ground layer.
 Place ground vias immediately next to pins/pads in the top layer. Place more vias whenever feasible. More vias in
parallel reduce the parasitic inductance.
 Never share a via with multiple pins or pads. Allow separate vias for each pin or pad.
 Avoid using vias to route the RF trace to a different layer.
 Allow a good number of vias for the central ground pad in the QFN package. This minimizes the parasitic
inductance and makes the IC see the same ground as the rest of the board.
 Whenever possible, use vias to form a ground fencing around the RF section to isolate it from the rest of the circuit.
www.cypress.com Document No. 001-91445 Rev. *H 48

21 Capacitors and Inductors
This section explains the non-ideal behavior of capacitors and inductors at high frequency and helps you choose the
right capacitors and inductors for applications such as matching networks, DC blocks, crystals, and power supply
decoupling.
21.1 Capacitors
All capacitors contain parasitic resistance, parasitic capacitance, and parasitic inductance apart from the intended
capacitance. Figure 54 shows the theoretical model of a typical capacitor.
Figure 54. Capacitor Model
C is the capacitance for which the capacitor is designed. The reactance (Xc) because of the capacitance (C) and the
reactance (XCp) because of the parasitic capacitance (Cp) are
XC = ; XCp = ;
−1 −1
As you can see from the equations, the reactance of a capacitance decreases with an increase in frequency. Cp is the
2πfC 2πfCp
parasitic capacitance that is usually very low. As a result, the reactance of this component is very high at low
frequencies. Since this component is in parallel with the main capacitance, at low frequencies, Cp has no impact.
A change in current through the capacitor causes a change in the magnetic field around the capacitor, part of which
gets induced by the conductors, introducing an EMF that opposes the change in current resulting in the parasitic
inductance. The reactance of this parasitic inductance is
XL =
The reactance of the parasitic inductance increases with frequency. Usually L is a very small value in capacitors; so,
2πfL
at low frequencies, XL is negligible.
R is the effective series resistance of the capacitor. It is usually a very low value.
The effective impedance of the capacitor is
Xeff =
((XL+ XC + R) ∗ XCp)
At low f(rXeqLu+e nXcCie +s, RX+Cp XisC vpe)ry high and the effective impedance is
Xeff = XL+XC+R
At low frequencies, the circuit is predominantly capacitive. Xeff is almost same as XC. But as the frequency increases,
XC keeps decreasing and XL keeps increasing. Eventually, at some frequency, XL becomes equal to XC and the
impedance of the capacitor becomes equal to R. This frequency is the series resonant frequency (SRF) of the capacitor.
When choosing capacitors for impedance-matching purposes, make sure that the SRF is much higher than the
frequency of operation. This ensures that the reactance of the capacitor is as predominantly because of the published
capacitance value, and the effective reactance is not reduced by the parasitic inductance.
When choosing capacitors for decoupling purposes, it is better to choose values that have an SRF close to the noise
frequency to be decoupled. This ensures that the noise sees a low-impedance path to ground.
www.cypress.com Document No. 001-91445 Rev. *H 49

At a higher frequency, the reactance XCp becomes equal to the reactance of the other arm (which is mostly equal to
XL now). At this frequency, the capacitors behave like an open circuit. This frequency is the parallel resonant
frequency. Avoid using capacitors at their parallel resonant frequency.
Q Factor of Capacitors
The quality factor (Q) of a capacitor (C) is the ratio of the reactance of the capacitor to its resistance (R) at a given
frequency (f).
Q =
1
High-Q capacitors have less undesired resistance. Ensure that you use capacitors with a high Q at the operating
2πfCR
frequency for RF circuits; otherwise, RF energy can be wasted as heat in the resistance of the capacitor.
21.1.1 Recommendations for Capacitors
 Use only C0G/NP0 capacitors for components of the matching network. This ensures that the matching network
does not change across temperatures.
 For the crystal load, use only C0G/NP0 capacitors. This ensures that the clock timing and RF frequency do not
change across temperatures. For more details on crystals, see AN95089 – PSoC 4/PRoC BLE Crystal Oscillator
Selection and Tuning Techniques.
 For the matching network, choose capacitors that operate well below their SRF.
 Use only high-Q capacitors for the RF circuit.
 For decoupling capacitors, the accuracy of the C0G capacitors may not be needed. It is typical to use X5R or X7R
capacitors (depending on the temperature range). Use low ESR capacitors for effective decoupling
 For decoupling capacitors, choose the component values that have an SRF at the noise frequencies.
 It is recommended to use smaller components (0402 or 0201), as they have less parasitic reactance.
 When adding a DC block to an RF trace that is already matched, it is better to use a capacitor that has an SRF
close to the frequency of operation and a low ESR, as the capacitor’s effective reactance becomes zero at SRF.
So it does not alter the impedance matching.
www.cypress.com Document No. 001-91445 Rev. *H 50

21.2 Inductors
Inductors also contain parasitic capacitance and parasitic resistance apart from inductance. Figure 55 depicts a model
of a real inductor.
Figure 55. Inductor Model
Rdc is the ohmic resistance because of the finite conductivity of the inductor. Rac is the frequency-dependent resistance
that represents the loss in the inductor core. The parasitic capacitance is a result of the capacitance between the
windings in the inductor. Rac is very high at low frequencies and is usually ignored. The effective impedance of the
inductor is
Xeff =
XCp∗(XL+Rdc)
The parasitic capacitance has very high impedance at low frequencies and little impact on the overall impedance as it
XCp+XL+Rdc
is parallel to the inductor. As frequency increases, the impedance resulting from the capacitance (XCp ) decreases, and
the impedance resulting from the inductance increases(XL). XL and XCp eventually become equal in magnitude at some
frequency. This frequency is the self resonant frequency (SRF) of the inductor. As Rdc is typically very low, the inductor
behaves like an open circuit or high impedance at this frequency.
Inductors used in the matching network (where inductance value is very important) should have an SRF much above
the operating frequencies. When inductors are used for power supply filtering, it is wise to choose inductor values with
an SRF close to the noise frequency.
Q Factor of Inductors
The quality factor (Q) of an inductor (L) is the ratio of the reactance of an inductor to its resistance (R) at a given
frequency (f).
Q =
2πfL
It is important to ensure that that the Q factor is high at the operating frequency for use in matching networks. Inductors
with a Rlower Q have a lot of resistance. In matching networks when low-Q components are used, one may be mislead
to see a good S11, even when the impedance matching is not good, because much of the energy does not pass to the
load, but gets wasted in the resistance as heat.
www.cypress.com Document No. 001-91445 Rev. *H 51

21.2.1 Recommendation for Inductors
 For matching networks, use only high-Q inductors with an SRF well above the operating frequency.
 For power supply filtering, use inductors with an SRF close to the noise frequency.
 Do not place inductors parallel and close to each other. The mutual inductance between them causes cross-talk.
Place inductors or unrelated sections orthogonal to each other.
 RF ceramic inductors are cost-effective and have a high SRF, but have a lower Q and current capacity, especially
with higher value inductors. See the inductor datasheet and determine if the Q is good enough at 2.4 GHz before
using it.
 Wire-wound inductors have low DC resistance, so they have a high Q and current capacity. Prefer wire-wound
inductors over ceramic inductors for high-value inductors.
22 Design for Testability
RF parameters such as transmit-power level, receiver sensitivity, or packet error rate (PER) are measured to verify the
correctness of component assembly. However, RF section cannot be tested using conventional test methods such as
in-circuit testing, as it is not recommended to place a test point on the RF trace.
 The entire radio path can be indirectly tested by measuring the RF parameters using BLE testers such as the
Anritsu MT8852B or R&S CBT tester.
 A cheaper alternative is to use a golden board (GB) as a tester and measure the PER at a pre-calibrated attenuation
that brings the receive power level to the acceptable sensitivity limit. Performing the PER in both directions (DUT
to GB and GB to DUT) ensures that both the receiver and transmitter are good.
 For all radiated tests, it is recommended to keep the transmitter and receiver in a controlled environment like a
Faraday cage or shielded room. The loss over the air and through the cable should be configured in the test
equipment. The distance between the transmitter and receiver and their orientation to each other must be
maintained for all devices.
 Regulatory tests include conducted tests, and it may help if a connector (U-FL, MMCX, or SMA) is provided. This
connector need not be populated in the final manufacture. With proper planning, the connector can also help in
verifying the matching networks.
 When taking branches for the RF connector, lay out the trace going to the antenna and the trace going to the
branch such that when isolating one, the other trace does not act as a stub. An example is given in Figure 56.
Figure 56. Example of Branching
www.cypress.com Document No. 001-91445 Rev. *H 52

23 Support for External Power Amplifier/Low-Noise Amplifier/RF Front End
Some applications may need a range higher than that is typically supported by the chipset. In such cases, either an
external power amplifier and/or a low-noise amplifier can be used to boost the link budget. At 2.4 GHz, there are plenty
of front-end ICs that include the power amplifier, low-noise amplifier and switches and controls needed to control them.
These controls need to be precisely timed based on the actual transmit and receive timing. If the product has to remain
BLE-compliant, ensure that the transmit power level does not exceed 20 dBm.
PSoC 4 BLE/ PRoC BLE has a control signal to control an external power amplifier for applications requiring extra
range. The Signal EXT_PA_EN, available on Port 5.0, is active HIGH during transmission and LOW otherwise. This
signal can be used to enable the power amplifier and choose between the transmit path and receive path. This can be
enabled in the 'Advanced' tab of the BLE Component.
Figure 57. Enabling External PA/LNA Control Signals in BLE Component
For configuration details of External Power Amplifier/Low Noise amplifier support for PSoC 6 MCU with Bluetooth Low
Energy (BLE) Connectivity, see the application note AN218241 – PSoC 6 MCU Hardware Design Considerations.
24 Support for Coexistence with Wi-Fi
The ability to survive interference from other radios depends on how well the radios are isolated from each other and
the radio’s blocking characteristics.
To achieve the best performance with coexistent radios, try to achieve the highest possible isolation in space,
frequency, and time.
24.1 Spatial Isolation
Antennas are the transmitting/receiving elements in radios. For minimum interference between coexisting radios, it is
necessary to isolate the antennas as much as possible. To increase the isolation between the antennas, use the
following guidelines. You need to have some knowledge of the antenna to achieve this goal.
 Keep the BLE antenna and Wi-Fi antenna as far apart as possible.
 For antennas with linear polarization, orient the antennas such that they are electrically orthogonal to each other.
 If possible, orient the antennas such that the direction of the nulls of the antennas is collinear.
 Place via fencing between the BLE and Wi-Fi sections of the board to minimize leakage through the PCB.
www.cypress.com Document No. 001-91445 Rev. *H 53

24.2 Frequency Isolation
BLE performs adaptive frequency hopping. Frequency hopping ensures that BLE packets are transmitted at different
channels at different times and achieve better immunity against radios that operate in single channels (such as Wi-Fi,
ZigBee). Adaptive frequency hopping ensures that channels with a higher interference are avoided, and frequency
hopping happens only in the subset of channels with low interference.
Adaptive frequency hopping is effective only when the receiver of the BLE radio has good selectivity/blocking within
the 2.4-GHz band. PRoC BLE/ PSoC 4 BLE offers among the best blocking specifications in the BLE market, resulting
in the best performance with interference or in coexistence with other radios. See Figure 58 for a comparison with
popular BLE ICs.
Figure 58. C/I Performance of PSoC 4 BLE/ PRoC BLE Versus Other BLE Chipsets
30
20
10
-4 -2 0 2 4
-10
-20
-30
-40
-50
-60
PSoC 4 BLE / PRoC BLE also has among the Lowest n-band spurious emissions in the BLE market. Low in-band
spurious emission ensures that the reception in coexisting Wi-Fi is affected the least because of a BLE transmission.
See Figure 59 for a comparison with other products.
www.cypress.com Document No. 001-91445 Rev. *H 54
I/C
Spec
TI CC2541
Nordic nRF51
CY PSoC4-BLE
Offset

Figure 59. In-Band Spurious Emission of BLE PSoC 4 BLE/PRoC BLE versus Other BLE Chipsets
24.3 Temporal Isolation
Most Wi-Fi chipsets support controls for coexistence with other radios through certain control signals. PSoC 4 BLE/
PRoC BLE can generate these control signals to control and coexist with an on-board Wi-Fi radio. An example project
for Wi-Fi coexistence using a three-wire interface compliant with Part 15.2 of the IEEE 802.15.2-2003 standard
(Coexistence of Wireless Personal Area Networks with Other Wireless Devices Operating in Unlicensed Frequency
Bands). The three signals used are the following:
BT_REQ: Output pin – request Wi-Fi to allow Bluetooth transmission or reception.
BT_PRI: Output pin – indicate priority of the Bluetooth transmission or reception.
WL_ACT: Input pin – response from the Wi-Fi chipset for BT_REQ.
The project is available at https://github.com/yourskp/BLE/tree/master/BLE%20Coexistence.
25 Summary
This application note described how one can easily design an optimal antenna for a custom product using PSoC BLE /
PRoC BLE. The application note also provides introduction to RF concepts along with design and layout checklists to
promote a successful board design for PSoC BLE / PRoC BLE. In addition, it documents the design considerations for
some of the system level requirements like design for testability, Use of an external Power Amplifier and coexistence
with Wi-Fi in the same system.
www.cypress.com Document No. 001-91445 Rev. *H 55

26 Related Application Notes
 AN48610 – Design and Layout Guidelines for Matching Network and Antenna for WirelessUSB™ LP Family
 AN64285 – WirelessUSB NL Low Power Radio Recommended Usage and PCB Layout
 AN5033 – WirelessUSB Dual Antenna Design Layout Guidelines
 AN48399 – WirelessUSB LP/LPstar Transceiver PCB Layout Guidelines
 AN91267 – Getting Started with PSoC 4 BLE
 AN88619 – PSoC 4 Hardware Design Considerations
 AN91184 – PSoC 4 BLE – Designing BLE Applications
 AN95089 – PSoC 4/PRoC BLE Crystal Oscillator Selection and Tuning Techniques
 AN218241 – PSoC 6 MCU Hardware Design Considerations
 AN210781 – Getting Started with PSoC 6 MCU with Bluetooth Low Energy (BLE) Connectivity
About the Authors
Name: Tapan Pattnayak
Title: Sr. Staff Systems Engineer
Background: Tapan received his B. Tech degree in Electrical Engineering from Indian Institute of Technology
Kharagpur (IIT Kharagpur) in 2002. Currently, he is working at Cypress Semiconductor Technology,
San Jose, USA.
Name: Guhapriyan Thanikachalam
Title: Sr. Staff Application Engineer
Background: Guhapriyan graduated from Regional Engineering College, Trichy, in 2002 with a BE degree in
Electronics and Communication Engineering. He is currently working on Cypress’s BLE products.
www.cypress.com Document No. 001-91445 Rev. *H 56

Appendix A. Checklist
You can use the checklist in Table 7 while designing the antenna to track your progress.
Table 7. Checklist for Optimal Antenna Design
Check Step
Decide on the PCB antenna type based on the application at hand: MIFA, IFA, wire antenna, or chip antenna.
See Table 5.
Note the chosen antenna layout (dimension). Download the Gerber files from www.cypress.com/go/AN91445.
Orient the antenna suitably for maximum radiation in the desired direction.
For MIFA, see Figure 14.
For IFA, see Figure 18.
Determine the “W” value to be used in the antenna layout, based on the PCB thickness (stack).
See Table 2 and Table 4.
Select the antenna tip length or leg length for MIFA, Figure 15.
Check Ground! This is the Key. . Check the Ground clearance for MIFA, IFA or Chip antenna. Check the bottom layer
minimum Ground width for better s11. Please look at the layout pictures.
Make sure that Antenna feed has a solid Gnd plane below it. Make sure that the RF output of the chip is routed like a Tline.
Do the ID preparation steps for antenna
Calibrate the VNA (one-port calibration is sufficient).
Measure S
(dB) with the complete product casing present.
See Figure 46.
Tune by matching network S (dip) shifts to the desired 2.44 GHz with the bare PCB and with complete product casing
present.
See Figure 47.
Note the final matching network components of the antenna and use them for volume production.
www.cypress.com Document No. 001-91445 Rev. *H 57

Appendix B. References
The following references provide further detailed information:
Antenna Basics
 Constantine A. Balanis, Antenna Theory: Analysis and Design, 3rd edition. Wiley - Interscience, 2005 (Chapters 2
and 5).
 Antenna with multiple fold, Philip Pak-Lin Kwan, Paul Beard, US Patent 7936318 B2
 AN48610, Cypress Semiconductor, Design and Layout Guidelines for Matching Network and Antenna for
WirelessUSB LP Family
Smith Chart Basics
 David M. Pozar, Microwave Engineering, 4th edition, Wiley, 2011 (Chapters 2, 4, and 5).
 Christopher Bowick, John Blyler, Cheryl Ajluni, RF Circuit Design, 2nd edition, Newnes, 2007 (Chapter 4).
 Smith v3.10, Bern Institute
Useful Free Online Software
 Transmission line calculator: Grounded CPW (air gap = 12 mil, ε r = 4.3 for FR4):
www1.sphere.ne.jp/i-lab/ilab/tool/cpw_g_e.htm
 Smith Chart-based matching: L or Pi matching:
http://cgi.www.telestrian.co.uk/cgi-bin/www.telestrian.co.uk/smiths.pl
 Smith Chart Bern Institute
http://www.fritz.dellsperger.net/
Chip Antenna Layout
 http://www.johansontechnology.com/datasheets/antennas/2450AT42B100.pdf
www.cypress.com Document No. 001-91445 Rev. *H 58

Document History
Document Title: AN91445 – Antenna Design and RF Layout Guidelines
Document Number: 001-91445
Revision ECN Orig. of Submission Description of Change
Change Date
** 4468573 GOWB 08/07/2014 New Spec
*A 4565905 TAPI 11/10/2014 Updated all figures and sections. Corrected sections. De-prioritized length
cutting. Added Chip antenna layout guideline
*B 4768767 TAPI 06/18/2015 Module characterization results with chip antenna referred.
Added the following sections: Chip antenna layout, wire antenna layout,
antenna length cutting for a quick churn, description about far field and near
field
Edits throughout the document
Updated to new template.
Completing Sunset Review.
*C 4935700 TAPI/GUHA 09/24/2015 Added additional sections on RF layout design and component selection
*D 5096520 TAPI 02/02/2016 Updated associated product family
*E 5563095 GUHA 12/28/2016 Added PSOC6 part numbers, decoupling capacitor recommendation for PSoC
6 BLE, BLE Component support for external PA/LNA and other edits for PSoC
6 BLE
Updated to new template.
*F 5652974 PTRC 03/07/2017 Updated to new template.
*G 5860573 GUHA 09/01/2017 Updated referenced app note titles
*H 6226538 PTRC 08/30/2018 Updated template
www.cypress.com Document No. 001-91445 Rev. *H 59

Worldwide Sales and Design Support
Cypress maintains a worldwide network of offices, solution centers, manufacturer’s representatives, and distributors. To find the
office closest to you, visit us at Cypress Locations.
Products PSoC® Solutions
Arm® Cortex® Microcontrollers cypress.com/arm PSoC 1 | PSoC 3 | PSoC 4 | PSoC 5LP | PSoC 6 MCU
Automotive cypress.com/automotive
Cypress Developer Community
Clocks & Buffers cypress.com/clocks
Community Forums | Projects | Videos | Blogs | Training |
Interface cypress.com/interface
Components
Internet of Things cypress.com/iot
Memory cypress.com/memory Technical Support
Microcontrollers cypress.com/mcu cypress.com/support
PSoC cypress.com/psoc
Power Management ICs cypress.com/pmic
Touch Sensing cypress.com/touch
USB Controllers cypress.com/usb
Wireless Connectivity cypress.com/wireless
All other trademarks or registered trademarks referenced herein are the property of their respective owners.
Cypress Semiconductor
198 Champion Court
San Jose, CA 95134-1709
© Cypress Semiconductor Corporation, 2014-2018. This document is the property of Cypress Semiconductor Corporation and its subsidiaries, including
Spansion LLC (“Cypress”). This document, including any software or firmware included or referenced in this document (“Software”), is owned by Cypress
under the intellectual property laws and treaties of the United States and other countries worldwide. Cypress reserves all rights under such laws and
treaties and does not, except as specifically stated in this paragraph, grant any license under its patents, copyrights, trademarks, or other intellectual
property rights. If the Software is not accompanied by a license agreement and you do not otherwise have a written agreement with Cypress governing
the use of the Software, then Cypress hereby grants you a personal, non-exclusive, nontransferable license (without the right to sublicense) (1) under its
copyright rights in the Software (a) for Software provided in source code form, to modify and reproduce the Software solely for use with Cypress hardware
products, only internally within your organization, and (b) to distribute the Software in binary code form externally to end users (either directly or indirectly
through resellers and distributors), solely for use on Cypress hardware product units, and (2) under those claims of Cypress’s patents that are infringed
by the Software (as provided by Cypress, unmodified) to make, use, distribute, and import the Software solely for use with Cypress hardware products.
Any other use, reproduction, modification, translation, or compilation of the Software is prohibited.
TO THE EXTENT PERMITTED BY APPLICABLE LAW, CYPRESS MAKES NO WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, WITH REGARD
TO THIS DOCUMENT OR ANY SOFTWARE OR ACCOMPANYING HARDWARE, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. No computing device can be absolutely secure. Therefore, despite security
measures implemented in Cypress hardware or software products, Cypress does not assume any liability arising out of any security breach, such as
unauthorized access to or use of a Cypress product. In addition, the products described in these materials may contain design defects or errors known
as errata which may cause the product to deviate from published specifications. To the extent permitted by applicable law, Cypress reserves the right to
make changes to this document without further notice. Cypress does not assume any liability arising out of the application or use of any product or circuit
described in this document. Any information provided in this document, including any sample design information or programming code, is provided only
for reference purposes. It is the responsibility of the user of this document to properly design, program, and test the functionality and safety of any
application made of this information and any resulting product. Cypress products are not designed, intended, or authorized for use as critical components
in systems designed or intended for the operation of weapons, weapons systems, nuclear installations, life-support devices or systems, other medical
devices or systems (including resuscitation equipment and surgical implants), pollution control or hazardous substances management, or other uses
where the failure of the device or system could cause personal injury, death, or property damage (“Unintended Uses”). A critical component is any
component of a device or system whose failure to perform can be reasonably expected to cause the failure of the device or system, or to affect its safety
or effectiveness. Cypress is not liable, in whole or in part, and you shall and hereby do release Cypress from any claim, damage, or other liability arising
from or related to all Unintended Uses of Cypress products. You shall indemnify and hold Cypress harmless from and against all claims, costs, damages,
and other liabilities, including claims for personal injury or death, arising from or related to any Unintended Uses of Cypress products.
Cypress, the Cypress logo, Spansion, the Spansion logo, and combinations thereof, WICED, PSoC, CapSense, EZ-USB, F-RAM, and Traveo are
trademarks or registered trademarks of Cypress in the United States and other countries. For a more complete list of Cypress trademarks, visit
cypress.com. Other names and brands may be claimed as property of their respective owners.
www.cypress.com Document No. 001-91445 Rev.*H 60