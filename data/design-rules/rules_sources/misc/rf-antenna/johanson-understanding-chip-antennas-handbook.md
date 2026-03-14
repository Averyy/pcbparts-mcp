---
source: "Johanson -- Understanding Chip Antennas Handbook"
url: "https://www.johansontechnology.com/docs/4469/johanson-understanding-chip-antennas-handbook.pdf"
format: "PDF 27pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 52284
---

UNDERSTANDING
CHIP H igh Frequency
Ceramic Solution
ANTENNAS
Handbook

About
Johanson Technology, Inc.
Welcome to
Johanson Technology, Inc.
We are a technology based company in Camarillo, With a strong focus on research and development,
California, that specializes in the design and Johanson Technology employs a team of
manufacturing of high-frequency ceramic engineers and scientists who work on new
components, including Antennas, Capacitors, materials, designs, and manufacturing processes
Inductors, and frequency control devices. The to continuously improve their products. Johanson
company was founded in 1989 by Eric Johanson Technology Inc. also has a commitment to
and John Petrinec and has since become a sustainability, using environmentally friendly
leading supplier of these components to the global manufacturing practices and materials wherever
electronics industry. possible.
Johanson Technology Inc. offers a wide range of Johanson Technology Inc. has a reputation for
ceramic components for applications in various high-quality products, technical expertise, and
industries, including telecommunications, medical, exceptional customer service.
aerospace, defense, and consumer electronics.
Each component is designed to provide high
performance, reliability, and durability in various
challenging environments and conditions.
2 RESOURCE https://www.johansontechnology.com/our-history
Understanding Chip Antennas Handbook

Antennas (Chips)
Table of Contents
04 ANTENNA CHIP OVERVIEW 19 ANTENNA (CHIP) SELECTION GUIDE
05 Technology Discussion (LTCC) 19 Mounting Guidelines
06 When to Use Antenna Chips and 19 GNSS
PCB "No-Ground" Areas 19 Selection Information
07 "Unique Solution - Chip Antenna 19 Optmization Process
Over Ground Plane!" 20 Antenna Selection Guide Tool. . .
08 Manufacturing Process (Application, Frequency, Mount Location,
Part Number & Description)
09 FREQUENCY RANGE OVERVIEW
23 TECHNICAL ASSISTANCE
09 Current Offering
DOCUMENT, LAYOUT, TUNING OPTIONS,
09 Why Not Lower Than 433MHz
& HARDWARE REVIEW
10 Why Not Higher Than 10GHz
23 Document & Layout Reviews
23 Option A: Quick Tune Antenna Matching
10 BANDWIDTH DEFINITION
23 Option B: Thorough Tuning & Performance
10 Typical Bandwidth for Chip Antennas Verification in Anechoic Chamber
10 Wide-band vs. Multi-band 24 Testing & Recommendations
11 GAIN DEFINITION 25 CUSTOM CHIP ANTENNAS
11 Isotropic Radiator DISCUSSION
12 Typical Performance 25 Contact Johanson's Technical Team
12 Causes of Variation From Spec
26 GLOSSARY
12 RADIATION PATTERNS DEFINITION 26 Antenna Terminology
13 Typical Performance 26 Types of Antenna Chips
14 Causes of Variation From Spec
14 IMPEDANCE & MATCHING DEFINITION
World Leader in
15 50-Ohm Typical Provided (& Measured)
Chip Antenna Design
as S-Parameters
15 Other Impedances Like 75-Ohm? Why not?
16 Chip Antenna Matching Process
16 Causes of Variation from Spec
17 P ERFORMANCE ISSUES
SYSTEM EFFECTS OF A POOR MATCH
AND LOW GAIN
17 Effects of Low Gain
18 Degraded Radiation Patterns
18 Solder Joint Failure – CTE: PCB v. Ceramic
RESOURCE https://www.johansontechnology.com/antennas 3

Welcome to Johanson's Technology Smallest Form Factor
Antenna Chip Overview - Using This Guide
Chip Available
Johanson Technology, a global leader in chip antenna design, manufacturing, implementation, and
technical support, has prepared this technical handbook, with the aim of educating and informing
customers and newcomers about chip antennas. This booklet includes the types of ceramic chip antennas
and their applications that Johanson offers, advantages of Johanson's antennas over other types,
considerations when choosing chip antennas and how to properly install and tune each antenna for
impressive high-frequency ceramic solutions.
"Wide
range
of
Chip
Antennas
available!"
T
E
o
IA
u
0
lt
4
r
0
a
2
-s
A
m
n
te
ll
n na
From relatively large 433 MHz low frequency
9820 Antenna 10 GHz high frequency
Johanson Technology offers a wide range of The circuit designer must recognize that all of the
chip antenna products that operate in various following seven factors influence the antenna's
bands from around 433 MHz to 10 GHz. These final performance. . .
antenna chips are available in numerous sizes,
from ultra-small EIA 0402 to relatively large EIA 1. The Chip Antenna, 5. Conductive components
9820. Each optimized for its intended application with its associated placed very close to the
where PCB antenna placement location, size, internal circuitry. "No-Ground" area
performance, and cost are considered. (especially if tall in Z axis).
2. The PCB "No-Ground"
or “Metal Keep-Out” 6. The matching network.
Typical uses for Johanson chip antennas include
area & the geometry If possible, a matching
nearly all small battery-operated wireless
defined on the data Pi-network is recom-
applications including: IoT, Bluetooth, WiFi,
sheet. mended although some
UWB, GPS/Glonass, LoRa, NB-IoT as well as Antennas will work with
other ISM band applications. Other uses include 3. The Chip Antenna a T-network. Accurate
placement relative
wearable healthcare monitoring devices, portable values can only be
to the edge of the
devices, weight constrained devices, low profile determined with bench-
circuit board.
devices and many more applications where the top tuning.
antenna must be mounted on a PCB. 4. The specified Vias.
7. The Enclosure.
Most chip antennas are designed to have omni-
It is vital to note that making improper alterations
directional radiation patterns and peak gain near
to the no-ground area or chip locations relative
0dBi. Average gain may be a few dBi lower. To
to the edge of the circuit board may lead to
achieve this omni-directional radiation pattern,
substandard performance.
the antenna requires a specific ground. When the
antenna is a monopole structure, it uses the top Also, violating any of the previously mentioned
layer of the PCB ground as the other monopole points can cause a degradation in antenna
to complete the dipole. This is why the PCB top performance.
RF ground plane is so critical.
Johanson antennas are constructed using a
While Johanson's chip antennas may appear variety of techniques, including monopole, dipole,
similar externally, their internal structures vary folded loop, inverted-F, and inverted-L designs.
significantly. As a result, certain critical parameters
must be taken into account to achieve optimal In addition, when it is not possible to have the
performance. required no-ground area for an antenna, we've
developed a solution. A chip antenna that can be
placed directly over a ground plane. This design
is unique in the industry.
4 RESOURCE https://www.johansontechnology.com/antennas

Antenna Chip Overview
Technology Discussion (LTCC)
Johanson Technology chip antennas are produced using Low Temperature Co-Fired Ceramic (LTCC)
technology. LTCC technology is a type of multi-layer ceramic process that allows for the integration of
very small passive components such as capacitors and inductors into a single package. LTCC technology
enables the production of miniaturized and highly functional electronic components, modules, or systems
with improved performance, reliability, and cost-effectiveness.
Some of the key features
of LTCC technology include
but are not limited to:
• Miniaturization: LTCC technology enables the mass
production/fabrication of compact and highly func-
tional electronic components and modules.
• High-frequency operation: LTCC technology
This LTCC technology involves the fabrication of provides excellent electrical properties for RF and
a multi-layer ceramic substrate by screen-printing microwave applications.
ceramic green tapes with conductive, resistive,
• Highly repeatable & consistent process for volume
or dielectric inks. The LTCC process enables the
applications that provides high yields of RF circuits
integration of multiple layers of circuitry, similar to
a multi-layer PCB, which can be interconnected and components.
through vias, to form complex three-dimensional
• Thermal stability: LTCC technology offers high ther-
structures.
mal conductivity, low thermal expansion, and high
The advantages of LTCC technology include resistance to thermal shocks, making it suitable
a consistent dielectric constant around the for high-temperature and temperature swinging
antenna elements near field, size, capacitive applications.
coupling resiliency, SMT for high-speed volume
manufacturing, high reliability and stability at high • Integration: LTCC technology allows the integration
temperatures, excellent electrical properties, low of multiple components and circuits into a single
signal loss, and high dimensional accuracy. LTCC package, reducing the need for external compo-
technology is widely used in various applications, nents and improving system performance.
including RF and microwave communication
systems, automotive electronics, medical devices, • Customization: LTCC technology offers flexibility in
and industrial automation. These chip antennas design and manufacturing, enabling customization
are designed to be compact and can be integrated for specific applications and requirements.
into a wide range of electronic devices such as
• Reduction of time-to-market: Due to the aforemen-
IoT sensors, mobile phones, laptops, Bluetooth
headsets, and other small, typically portable, tioned, LTCC reduces the number of prototype
wireless devices. spins and iteration, effectively reducing the prod-
uct’s development lead-time.
RESOURCE https://www.johansontechnology.com/antennas 5

Antennas Chip Overview
When To Use Antenna Chips & PCB "No Ground" Areas
When to use Antenna Chips VS When not to use Antenna Chips
Antenna Chips are highly effective and Antennas Chips are often not the best solution
commercially attractive when system when system requirements include one or more
requirements include one or more of the of the following:
following:
Higher than 4 watts (CW – Continuous
Small compact packages Wave) output power at the antenna
is required.
Large volumes The antenna needs to be physically
located away from the circuit board.
The operational frequency band
Replacing whip antenna while still
is above 433MHz
requiring the same gain.
4 watts (CW – Continuous Wave) or
less of transmit power at the antenna. The system requires directional antenna
performance or an effective antenna
average gain of 3dBi or more.
The antenna can be located directly
on the circuit board.
Omni directional radiation pattern
performance is preferred.
"No-Ground" or "Keep-Out" Areas Antenna (Chip) Overview
A ground plane is typically used with an antenna
desired axis, the designers at Johanson use a
chip to provide a reference plane for the antenna
"no-ground" area and its geometry on the PCB
and to improve its performance. For Johanson
as one of the key features to optimize radiation
antennas, a ground plane must be included.
pattern performance. This "no-ground" area is
The ground plane is an integral part of the overall
critical to the final antenna performance.
antenna system design. The size of the ground
plane can vary. For example, if a customer only It is important to note that the "no-ground" or
needs one cm of range, then the ground plane “keep-out” area must extend down through
can be minimal. If the customer requires 30m, all layers of a multilayer PCB.
then the ground size and fluidness are critical.
However, it's important to note that while Johanson
When Johanson designs antenna ceramic chips, antenna chips may function with changes to the
there are some basic requirements established "no-ground" area, their performance may be
prior to conception. Some of these requirements less predictable and less efficient compared to the
include the size of the PCB and clearance area, same antenna chips with a specified "no-ground"
gain, radiation pattern, efficiency and the area. Therefore, it's important to carefully consider
type/amount of ground required. the requirements of your specific application and
consult with the Johanson's technical team when
During the optimization process which typically
considering changes to the "no-ground" area.
includes creating a uniform radiation in the
6 RESOURCE https://www.johansontechnology.com/antennas

"Unique Solution - Chip Antenna Over Ground Plane!"
e
Pl Zero Clearance
d
u Required.
G
Chip
Antenna
P/N 2450AT42E01001E
"No-Ground" or "Keep-Out" Areas
Antenna (Chip) Overview
The only chip antenna over ground plane! The chip antenna mounts directly above or below the metal
layer of PCB (Printed Circuit Board). No antenna clearance required ever again!
Johanson Technology has developed this unique chip antenna solution that eliminates the need for
“No-Ground” area around the antenna. In this solution, the antenna is designed to have a solid ground
plane directly underneath the antenna. This is a novel solution and used when the system configuration
does not allow for the necessary “No-Ground” area or regional clearance of metal required by most chip
antennas.
Common Applications:
• Wearable devices • Home Automation/RF Locks • WiFi Access Points
• Portable Audio • Advanced Thermostats • Chipset Specific FEMs
• Sensors • POS/Payment Systems • Portable Positioning Modules
• Tag, Tracers, iBeacon • In-Vehicle WiFi • Vehicle/Insurance Tracking
RESOURCE https://www.johansontechnology.com/antennas?option=com_products&id=2450AT42E0100001E 7

The Manufacturing Process
The Manufacturing Process
The LTCC manufacturing process typically involves the following steps:
The LTCC process starts with the preparation Firing: The green body is then fired in a furnace
of the ceramic powder and other materials. The at a low temperature (typically between 850°C
ceramic powder is mixed with organic binders and and 1000°C) to remove the organic binders and
solvents to form a homogeneous slurry, which is sinter the ceramic particles, resulting in a dense
then processed into ceramic green tapes of the and co-fired ceramic substrate. The conductive,
desired thickness and dimensions. resistive, and dielectric inks are also fired, creating
the desired electrical properties.
Screen printing: The green tapes are then screen
printed with conductive, resistive, or dielectric Termination: The fired ceramic components are
inks to form the desired circuit pattern. The ink is inspected for defects and then the termination
deposited onto the green tape using a fine mesh paste is applied in the form of dipped termination
screen, which is pressed against the tape and or printed land pattern terminations. These
moved along its surface. The ink is then dried to terminations, also called solder pads, perform the
remove the solvent and binder. electrical connections to the circuit board.
Finally, at Johanson, antenna chips undergo
Step 1 Ceramic Powder rigorous RF testing to ensure that only fully
LTCC Process Ceramic Slurry functional parts are delivered to our valued
S customers.
1) Green Ceramic
tart
Electronde Metal Power
Tapes
Termination
Step 2
Electrode Ink Metal Powder
LTCC Process
2) Screen Printing 3) Stacking
Termination Ink
1) Firing
4) Lamination
5) Laminated 2) Termination Dipping
"Green Body" (Solder Pads)
6) Via Formation
3) Termination
7) Cutting Firing
4) Plating
Lamination: Multiple layers of green tapes with
5) Testing
i
f
ff
re
ch
n t
c
t
h
rc
p
a t
l
m
rn
s
n a
t h
to
g
th
ta
c
k
in
g
t op Done
6) Finished MLCC
combination of heat and pressure. The resulting
laminated structure is called a "green body".
The LTCC process can be modified and
Via Formation: Vias are then created in the green customized to suit specific applications and
requirements. For example, different materials with
body to interconnect the different layers of circuitry.
various dielectric properties can be used for the
This is typically done by drilling or punching small
ceramic powder, and the firing temperature can be
holes through the green body and filling them with
adjusted to achieve specific electrical and thermal
conductive paste.
properties. These different powders provide
Cutting: The substrate is then cut, singulation of various k and loss tangent values allowing our
the individual components. component designers to achieve unique solutions.
8 RESOURCE https://www.johansontechnology.com/antennas

Frequency Range Overview
Current Offering and Why Not Lower Than 433MHz
Frequency Range (Overview)
The frequency range is described as the upper and lower frequencies where acceptable radiation pattern,
gain, and return loss performance is achieved. Typically, Johanson Technology antennas are optimized
with the associated ground-plane to exhibit the desired radiation pattern performance and a typical 9.5dB
return-loss over the band in question.
Current Offering
(Frequency Range Overview)
The frequency range of chip antennas can vary depending on their design and construction. Generally,
Johanson chip antennas are designed to operate in narrow frequency ranges from 433 MHz to 10 GHz.
Most Johanson Technology chip antennas operate in ultra-high-frequency (UHF) chip antennas: Typically
operate in the range of 300 MHz to 3 GHz, which are often used in applications such as mobile devices,
Bluetooth earbuds, smart meters, wireless routers, and RFID systems. Or the low end of super-high-
frequency (SHF) chip antennas: Typically operate in the range of 3 GHz to 30 GHz, which are often used
in applications such as Industrial Scientific and Medical (ISM) bands, and Ultra-Wide Band (UWB) bands.
The specific frequency range of a chip antenna will depend on factors such as its size, shape, and
matching as well as the application for which it is designed.
Why Not Lower Than 433MHz This means that at a lower frequency, the
(Frequency Range Overview) wavelength is longer, and a larger antenna
is required to efficiently receive or radiate the
With current design approaches and frequencies intended signal. Conversely, at a higher frequency,
below 433MHz, the physical size of the antenna the wavelength is shorter, and a smaller antenna
becomes relatively large and thus, cost prohibitive. can be used.
At the higher costs, these chip antenna solutions
For example, a half-wave dipole antenna
below 433MHz lose commercial appeal.
(a simple type of antenna) has a length of half the
The lower band is also constrained by the wavelength it is designed to operate at. A dipole
wavelength when limiting the package dimensions. antenna designed to operate at a frequency of
For lower frequencies to propagate efficiently, 1 MHz would have a length of approximately
certain elements such as the physical inductance 150 meters, while a dipole antenna designed
cannot be effectively replaced by an inductor to operate at a frequency of 1 GHz would have
having an equivalent physical length. Although a length of only 15 centimeters. This size
these designs have shown to resonant effectively, difference is significant and can limit the use
the lack of physical elements resulted in of lower frequency antennas in certain applications
unacceptable radiation performance. where size constraints are important.
Lower frequency antennas require larger sizes In addition to size considerations, lower frequency
than higher frequency antennas because the antennas may also suffer from lower efficiency
size of the antenna is directly proportional to due to losses caused by the ground and other
the wavelength of the electromagnetic wave it is obstacles. These losses increase with the size
designed to transmit or receive. The wavelength is of the antenna and can further limit the range and
inversely proportional to the frequency, according performance of the antenna. Designers must take
to the formula: wavelength = speed of light / these factors into account when selecting
frequency. an antenna for a particular application.
RESOURCE https://www.johansontechnology.com/antennas 9

Frequency Range Overview
Why Not Higher Than 10GHz
The capability exists to design and produce chip antennas above 10GHz. These products will be
designed/developed and produced when a compelling business case is presented but are not typically
offered as off-the-shelf products.
Bandwidth Definitions
Typical Bandwidth for Chip Antennas & Wide-band Multi-band
VS
The bandwidth of an antenna is affected by many
factors, including the ground plane, the tuning
NB network, the size and shape of the antenna, the
material used to construct it, and the operating
frequency.
The bandwidth of a Johanson chip antenna can
be measured in terms of percentage bandwidth
or absolute bandwidth. Percentage bandwidth
SS
is the ratio of the bandwidth to the center frequency
of the antenna, expressed as a percentage.
Absolute bandwidth is the difference between
UWB
the upper and lower frequencies within which
the antenna can operate effectively, expressed
in megahertz (MHz) or gigahertz (GHz).
Frequency Range
SS - Spread Spectrum
Typical Bandwidth for Chip Antennas
NB- Narrowband
UWB - Ultra Wideband (Bandwidth Definitions)
The typical bandwidth is determined by the
Bandwidth (Definitions) application. Many of Johanson's chip antennas are
designed for ISM band frequencies, which include
In an antenna, bandwidth refers to the range of BLE and WiFi, are also optimized to operate over
frequencies over which the antenna can operate a relatively narrow band from 2.4GHz to 2.5GHz,
effectively. Specifically, it is the difference between 4% bandwidth. Our UWB antennas operate
the highest and lowest frequencies within which over much wider bands. For example, Johanson
the antenna can transmit or receive a signal with Technology’s unique Ultra-Wide-band antenna,
acceptable radiation patterns, gain, and return- P/N 3100AT51A7200, operates from 3.1GHz to
loss performance. 10.3GHz which is 107% bandwidth.
A wide bandwidth is desirable for an antenna as Wide-band VS Multi-band
it enables the antenna to operate over a larger
(Bandwidth Definitions)
range of frequencies, making it more versatile
and useful in a variety of applications. A narrow
Some antennas are multi-band designs while
bandwidth, on the other hand, limits the range
others are wide-band designs.
of frequencies over which the antenna can be
used. Bandwidth is also critical in applications Multi-band designs work only in the prescribed
where capacitive coupling may shift the antenna bands and not between those bands.
resonance. Wide-band designs function over the entire
band of operation.
10 RESOURCE https://www.johansontechnology.com/antennas
tuptuO
ygrenE

Definitions
Gain and Isotropic Radiator
Gain (Definitions)
Antenna gain is a measure of the effectiveness Antenna gain is usually expressed in decibels
of an antenna in radiating or receiving (dB), and the unit of measurement is referred to as
electromagnetic waves in a particular direction. It dBi (decibels relative to an isotropic radiator).
is the ratio of the radiation intensity of an antenna
Antenna gain is an important factor in the design
in a given direction to the radiation intensity that
and selection of antennas for specific applications.
would be produced by an ideal isotropic radiator (a
Antennas with high gain are typically used
hypothetical point source that radiates uniformly in
in long-range communication systems, while
all directions) radiating the same total power.
low-gain antennas are used for short-range
In simpler terms, antenna gain describes the communications or in situations where a more
degree to which an antenna focuses energy in omni-directional radiation pattern is desired.
a particular direction. An antenna with a higher
gain will concentrate more energy in a particular
direction than one with a lower gain.
Isotropic Radiator (Gain Definitions)
An isotropic radiator is a hypothetical point source
of electromagnetic waves that radiates uniformly
in all directions without any directional preference.
In other words, it emits energy with equal intensity
in all directions, creating a spherical pattern of
Figure 1: Radiation Pattern of an isotropic radiator
radiation.
gain versus direction, the gain constant in all directions.
The plot a perfect circle.
The concept of an isotropic radiator is used as
a reference to compare the performance of other
antennas or radiating elements. The gain of an As you can see, the gain (expressed in dBi) is the
antenna is usually measured with respect to the same in all directions, represented by the circular/
gain of an isotropic radiator, expressed in decibels semi-spherical shape of the plot.
(dB), and is referred to as dBi (decibels relative to
The gain in dBi (decibels relative to isotropic) of an
isotropic).
isotropic radiator is always 0 dBi. This is because
While an isotropic radiator is an idealized concept an isotropic radiator is a theoretical point source
and cannot be physically realized, it provides a of electromagnetic radiation that radiates equally
useful reference for evaluating the performance of in all directions, and there is no direction in which
real-world antennas and other radiating elements. it is "better" than any other direction. Therefore,
by definition, its gain relative to itself is 0 dBi.
Since an isotropic radiator radiates energy
uniformly in all directions, its radiation pattern is It's worth noting that while a perfect isotropic
a perfect sphere. However, it is difficult to visualize radiator doesn't actually exist in the real world,
a perfect sphere in a 2-dimensional image. it is a useful reference point for measuring the gain
of antennas and other radiating structures. The
Instead, the radiation pattern of an isotropic gain of an antenna is typically measured relative
radiator is often shown as a simple plot of gain to an isotropic radiator, with positive values
versus direction, with the gain being constant in all indicating that the antenna radiates more power
directions. The plot would be a perfect circle, as in a particular direction than an isotropic radiator
shown in the image Figure 1: would.
RESOURCE https://www.johansontechnology.com/antennas 11

Gain Definitions
Typical Performance & Cause of Variation From Spec
Typical Performance (Gain Definitions)
It is helpful for designers to know the typical chip performance for calculating initial link budget estimates.
Chip antennas average gain ranges from -6dBi to +1.0dBi. -2.0dBi could be used for initial estimates.
However, once the final chip antenna selection has been made, the link budget should be recalculated
using the average gain of the selected antenna.
Causes of Variation From Spec (Gain Definitions)
Common Causes of Low Gain are:
• Poorly matched chip antenna – specifically the • The enclosure was made of conductive material
antenna return-loss is lower than the specification. or coated with a metal loaded paint, effectively
blocking some or all radiation.
• The no-ground specified on the data-sheet was not
followed in the design. • The enclosure was made with a high loss or high
absorption material like carbon fiber.
Definition
Radiation Patterns
Antenna radiation pattern refers to the directional dependence of the electromagnetic field radiated by an
antenna. It describes how the antenna radiates electromagnetic energy into the surrounding space as a
function of direction.
The radiation pattern is typically measured in three dimensions, often using a polar coordinate system.
In the azimuth plane, the pattern is measured as a function of the angle around the antenna, while in the
elevation plane, the pattern is measured as a function of the angle above or below the antenna's axis.
The radiation pattern of an antenna can be described mathematically, and it is often displayed as a
graph or diagram that shows the intensity of the radiated energy as a function of direction. The pattern
can be expressed in terms of gain, directivity, or other parameters that describe the antenna's radiation
properties.
Different types of antennas can have different radiation patterns, depending on their design and the
frequency of operation. Some antennas, such as directional antennas, radiate more energy in certain
directions, while others, such as omni-directional antennas, radiate energy uniformly in all directions.
Johanson chip antennas are omni-directional devices.
12 RESOURCE https://www.johansontechnology.com/antennas

Radiation Patterns Definition
Typical Performance
Typical Performance (Radiation Patterns Definitions)
Typical radiation pattern performance for Johanson chip antennas is similar to the following:
Typical Radiation Patterns
+X
+Y (90°)
-X
-Y +Y
+X (0°)
-Y
+Z (0°) +Z
-X +X
+X (90°)
-Z
+Z
+Z (0°)
+Y (90°)
-Y +Y
-Z -Z
RESOURCE https://www.johansontechnology.com/antennas 13

Radiation Patterns Definition
Causes of Variation From Spec
Common causes of poor radiation pattern performance are:
• Large deviation from the geometry of the • Tall conductive components placed immediately
layout on the data-sheet specification. adjacent to the no ground area such as batteries,
shielding, or metal screws.
• Broken up top RF ground pour (sections
of ground vs fluid unobstructed ground). • Presence of LCD displays, button, and other
conductive objects in the encasement directly
• No or poor via stitch.
above or adjacent to the chip antenna.
• Very small PCB footprint with respect to the
antenna (poor ground).
Definition
Impedance & Matching
Matching refers to the process of optimizing the impedance of an antenna to ensure maximum power
transfer between the antenna and the transmitter or receiver. The energy of the RF signal is converted
from conducted electromagnetic energy to radiated energy via the antennas as a matched radiating
reactive load. Matching is measured in Return Loss in dB.
Johanson chip antennas are typically matched with 1 to 3 capacitors and or inductors. Below is an
example of the matching that should be optimized on a fully populated PCB with the enclosure in place.
In this example, the matching components are a 1pF capacitor, 2.7nH inductor and a 3.9nH inductor.
The match is optimized by varying the values of those 3 components.
14 RESOURCE Additional information on antenna tuning - https://www.johansontechnology.com/tuning

Impedance & Matching Definition
50-Ohm Typical Provided (& Measured) as S-Parameters
Typical return loss for Johanson Chip Antennas is 9.5dB
Other Impedances Like 75-Ohm? Why Not?
It is possible to provide other impedances, but. . . not recommended!
Two primary reasons not to
provide other impedances
Compatibility Signal Loss
50-Ohm circuits are the standard 50-Ohm circuits also have lower
for most microwave components, signal loss than 75-Ohm circuits,
such as cables, connectors, and which makes them more suitable
terminations. Using 50-Ohm circuits for high-frequency applications.
allows for easy compatibility and The lower resistance of 50-Ohm
interchangeability of components circuits results in less signal
between different systems and attenuation and distortion, which is
manufacturers. especially important for microwave
communications and data transfer.
Systems which use 75-Ohm coax are typically much cheaper and commoditized. They also do not have
to have a high withstanding voltage. For this reason, 75-Ohm cables are made with less expensive
materials and tend to be much cheaper than 50-Ohm cables.
Overall, the use of 50-Ohm circuits is a well-established convention in microwave engineering that offers
several advantages in terms of signal transmission, compatibility, power handling, signal loss, and design
simplicity.
RESOURCE https://www.johansontechnology.com/ask-a-question 15

Chip Antenna Matching Process & Causes of Variation From Spec
Impedance Matching Process (Impedance & Matching Definition)
Typical Steps for Antenna Matching:
1. Populate the final PCB with all components 5. Using a network analyzer,
2. Cut the antenna feed trace on the PCB to separate it 6. One-port (S11) calibration for N.A.
from the filters and transceiver. (Network Analyzer) Open-Short-Load for
desired operating bandwidth
3. Use a probe or attach a semi-rigid cable to the
antenna side of the cur trace 7. Mount probe (semi-rigid RF cable for our example)
onto PCB and connect to N.A.
4. Modify the enclosure to allow the semi-rigid cable to
exit the enclosure opposite the antenna 8. Measure S11 of test board without antenna or any
matching components and save as: →S11_open
→save trace to memory of N.A.
GND 50 Ω Feed line 9. Measure S11 of test board with antenna and series
0Ω resistor mounted and save as: →S11_antenna
No GND
Probe or
10. Set N.A. to data/memory mode (S11_antenna/
semi-rigid
S11_open) and display/save as: →S11_match
RF cable
11. Match the trace of S11_match to 50Ω (center of
Soldering to: π-type Smith chart at the desired frequency) by varying the
Calibration Plane of Connect Probe Matching Pads
values of the passive devices.
Network Analyzer (NA) GND & PCB GND (scheme) preferred
Causes of Variation From Spec (Impedance & Matching Definition)
Antenna mismatches can occur due to various factors, some of the common causes include:
• The dielectric loading aka “capacitive loading" • The complete assembly was never matched.
of the enclosure shifts the frequency response
• Unknown inner ground layers intersecting
requiring a re-tuning.
the antenna clearance region (defective PCB).
• Large conductive components placed
• Antenna is out of band.
immediately adjacent the no-ground area.
• Variations in PCB impedance due to
fabrication or co-planar waveguide CPWG
improper calculation.
16 RESOURCE Antenna tuning more information - https://www.johansontechnology.com/tuning

Performance Issues
System Effects of a Poor Match and Low Gain
System Effects of Poor Match
A poor match can significantly degrade system performance.
Low receiver Lower than
Low gain
sensitivity expected link
budget
Some effects
Reduced Short transmit Low receiver
caused by a
signal-to-noise recive distance sensitivity
poor match ratio
System Effects of Low Gain
Like a poor match, low gain can cause the following system performance issues:
• Reduced signal-to-noise ratio • Enclosure is conductive
• Low receiver sensitivity • A customer used a type of “shiny” paint which
contains metal particulates effectively blocking
• Lower than expected link budget
RF signals.
• Short transmit receive distance
• The enclosure housed a replaceable battery that
• The enclosure is made of, coated with, or contains was located directly over or below the antenna
a non-compatible material
• The reflection from the battery disrupted the gain
• Enclosure is very lossy at operational frequency. and the radiation patterns
• A customer made an enclosure out of carbon fiber
and the loss of the carbon fiber cause very low gain
RESOURCE https://www.johansontechnology.com/antennas 17

Performance Issues
Degraded Radiation Patterns and Solder Joint Failure
System Effects of Degraded Radiation
(Performance Issues)
Issues with radiation pattern performance can be more subtle and harder to detect. Radiation pattern
problems can cause low system performance:
• Inconsistent connectivity depending on antenna orientation.
• Possibly no connectivity (represented as nulls in a radiation pattern)
System Effects of Solder Joint Failure – CTE: PCB v. Ceramic
(Performance Issues)
The antenna products have an operational temperature range of -40C to +85C. In some cases, the upper
range is +125C.
Although the ceramic body and terminations can tolerate extreme temperatures, they cannot tolerate too
much thermal shock. If the assemblies are exposed to numerous temperature excursions outside of this
range, the solder joint or substrate can become stressed and eventually fail as a fracture due to constant
expansion and contractions.
This is caused by the difference in CTE between the Ceramic antenna and the PCB.
The coefficient of thermal expansion (CTE) is a measure of how much a material expands or contracts
when its temperature changes. The CTE of a material is typically expressed in parts per million per
degree Celsius (ppm/°C).
LTCC (Low Temperature Co-Fired Ceramic) and FR4 (Flame Retardant 4) are two commonly used
materials for printed circuit boards (PCBs).
The CTE of LTCC ceramic is typically in the range of 3.5-5.5 ppm/°C, depending on the specific
composition of the ceramic. The CTE of FR4 PCB material is typically around 13-18 ppm/°C.
Therefore, there is a significant difference in the CTE between LTCC ceramic and FR4 PCB material.
This difference can lead to issues such as warping or cracking of the PCB during thermal cycling
or temperature changes. It is important to take this difference into account when designing and
manufacturing PCBs that use these materials.
18 RESOURCE https://www.johansontechnology.com/ask-a-question

Antenna Chip Selection
Mounting Guidelines, Selection Info, & Optimization Process
Mounting
Guidelines
PCB End Mounting PCB Corner Mounting
Legend
Antenna Chip Mounting Area PCB Circular Mounting
PCB Center-Edge Mounting
PC Board
Selection Guide Information:
Note: Refer to the website for latest version of selection guide
Antenna Chip Selection Guide is a useful tool All four of these features work together to
early in the design process when a decision on determine the final system performance. As such,
which Johanson antenna chip/s will be selected. changes to the no-ground area or chip locations
relative to the edge of the circuit board can result
First, the designer must choose what type in substandard performance.
of layout is desired based on the product shape
and remove allowable antenna chip placement. Once the layout type has been selected, then
determine the application type and associated
The mounting plays a critical role in antenna operational frequency.
chip selection.
In some cases, the selection guide will provide
It is important that the designer understands two antenna chip options. We have identified
that the "Antenna Optimization Process" features that should lead the designer to a
is composed of the following: specific selection.
1 2 3 4
Optimization
Chip's associated the top RF geometry of the and the edge of
Process internal circuitry ground plane no-ground area the circuit board
RESOURCE https://www.johansontechnology.com/chip-antenna-selection 19

Antenna Chip Selection: Application, frequency, physical size, mount location, part number & description
Application Legend - Bluetooth, Wi-Fi, & Zigbee Applications
Antenna Selection Legend
Guide Tool
Application Type
Frequency
1. Bluetooth / Wi-Fi / Zigbee
An easy to use, step-by-step
tool to help you get the correct 2. Wi-Fi / UNII 1-3 Mounting Location
antenna chip part number, for
3. Sub-GHz ISM
your project design.
4. Dual-Band Physical Size
Small / Medium / Large
5. Ultra Wide-Band
Part Number
Description
1.
Bluetooth,
Wi-Fi, & Zigbee Note: Refer to the website for latest
version of selection guide. See the
resource link at bottom of this page.
2.4 GHz
Center-Edge Circular Patch
End Mount /
Mount Mount Antenna
Corner Mount
2450AT07A0100001T 2450AT07A0100001T 2440AT62A0085001E
Low profile, high gain, Low profile, high gain, Does not require
resistant to capacitive resistant to capacitive PCB edge
de-tuning de-tuning
Small Medium Large
2450AT18D0100001E 2450AT18D0100001E
2450AT14A0100001T 2450AT42B0100001E 2450AT42A0100001E High gain, resistant to High gain, resistant to
Ultra-low profile, Exceptional gain for Great performance, capacitive de-tuning capacitive de-tuning
smallest corner mount medium size large size
2450AT42E010B001E 2450AT42E010B001E
Mounts directly above Mounts directly above
2450AT18B0100001E 2450AT43B0100001E 2450AT43F0100001E
GND/metal GND/metal
Great small monopole Larger size, higher gain Wide Band
antenna
2450AT45A0100001E
High gain, largest
antenna
20 RESOURCE https://www.johansontechnology.com/chip-antenna-selection

Antenna Chip Selection: Application, frequency, mount location, part number & description
Wi-Fi / UNII 1-3 and Sub-GHz ISM Applications
2.
Wi-Fi / UNII 1-3
5.5 GHz
Center-Edge End Mount / Circular
Mount Corner Mount Mount
5500AT07A0900001T 5400AT18A1000001E 5500AT07A0900001T
Miniature 5.5 GHz Small form factor, Miniature 5.5 GHz
antenna wide-band antenna
Note: Refer to the website for latest
3.
Sub-GHz ISM
900 MHz
400 MHz 783 MHz 868 MHz 915 MHz
(868 + 915 MHz)
End End Mount / End Mount / End Mount / End Mount /
Mount Corner Mount Corner Mount Corner Mount Corner Mount
0433AT62A0020001U 0783AT43A0008001E 0868AT43A0020001E 0915AT43A0026001E 0900AT43A0070001E
433/403MHz Center Small antenna for Small antenna for Small antenna for Wide-band, larger
frequency single-band operation single-band operation single-band operation keep-out area
RESOURCE https://www.johansontechnology.com/chip-antenna-selection 21

Note: Refer to the website for latest
830 MHz / 2.2 GHz 900 MHz / 2.4 GHz GNSS / 2.4 GHz 2.4 GHz / UWB 2.4 / 5.5 GHz
End End Corner-edge Corner Corner
Mount Mount Mount Mount Mount
0830AT54A2200001E 0900AD47A2450001E
ISM + cellular LTE 900 MHz ISM + 2.4
bands, single-feed GHz BLE / WiFi bands,
dual-feed
Corner-Edge
Mount
22 RESOURCE https://www.johansontechnology.com/chip-antenna-selection
52/30_GSA_02
Antenna Chip Selection: Application, frequency, mount location, part number & description
Dual-Band and Ultra Wide-Band Selections Applications
4.
Dual-Band
2450AD47A1590001E 2450AD18A7250001E 2450AD46A5400001E
Large, dual-feed Single-feed antenna, Large, dual-feed
2.4 GHz + UWB dual-band antenna
channels 5-9, small
2450AD18A6050001E
2.4 GHz + 4.9-7.2 GHz
single-feed 2450AD14A5500001T
Low profile, miniature,
single-feed
5.
Ultra
Wide-Band
6.2 - 8.24 GHz 3.1 - 10.3 GHz
Corner Corner
Mount Mount
7000AT18A1600001E 3100AT51A7200001E
UWB channels 5-9 UWB antenna

Technical Assistance
Document, Layout, Tuning Options, & Hardware Review
Document Review (Technical Assistance)
When necessary, an non-disclosure agreement (NDA) can be put in place to facilitate close and detailed
technical communication. Johanson takes customer IP very seriously and we are constantly improving
our systems to keep all customer details confidential. Most of our design layout reviews are performed in
California, USA. Our facility is also equipped to handle secure server communication covered by our ITAR
procedures.
Step 1: Layout Review (Technical Assistance)
Johanson offers JTI manufactured ceramic chip antenna customers 2 complimentary RF layout reviews
of your PCB by a Johanson Technology (JTI) RF engineer before fabrication to ensure optimum
performance. Our engineering team will provide prefab board layout (antenna footprint) suggestions such
as, antenna selection, location, and grounding recommendations. Our lab is equipped with calibrated
network analyzers and state-of-the-art anechoic test chambers for radiation pattern characterization
based on measured data on the client’s PCB.
Option A: Quick Tune Antenna Matching Service (Technical Assistance)
Step 2: Layout Review (Technical Assistance)
Once the layout review and prototype manufacturing has occurred, the only requirement is that clients
send Johanson a fully populated PCB: all SMDs including batteries, connectors, and encasements
(as they may affect RF resonance) antenna performance mounted and installed. Customers can leave
the antenna (optional) and antenna matching components’ slots empty as Johanson will be solder
mounting them. The system does not need to be functional. Johanson will feed passive 0dBm signal
directly into the antenna-1 for proper isotropic radiation measurements.
This “Quick Tune” service where the antenna on your circuit board (along with all components),
is matched for return-loss by calculating the values and part numbers of the inductors and capacitors
(Ls & Cs) in the antenna matching network. No gain or radiation patter measurement is taken in this
type of service. It will ensure the antenna match is operational at the intended frequencies.
Option B: Thorough Tuning & Performance Varification in Anechoic Chamber
(Technical Assistance)
Two complimentary RF layout reviews of your PCB by a Johanson Technology (JTI) engineer before
fabrication to ensure optimum radiated performance. Our engineering team will produce prefab board
layout (antenna footprint) suggestions, antenna selection, location, and grounding recommendations.
We have available state-of-the-art anechoic test chambers for radiation pattern characterization based
on measured data on the client’s PCB.
Once the layout review recommendations are implemented and prototype manufacturing has occurred,
the only requirement is that clients send us a fully populated PCB: all SMDs including batteries,
connectors, and encasements (they affect RF resonance) mounted and installed. The customer can leave
the antenna (optional) and antenna matching components’ slots empty as we will be mounting/soldering
them ourselves. The balance of the system electronics do not need to be functional; we feed our own
passive 0dBm signal directly into the antenna for proper isotropic radiation measurements.
RESOURCE https://www.johansontechnology.com/ask-a-question 23

Testing, & Recommendations
RF Lab Testing
SMD Antenna
915MHz Chip Antenna tuning
and characterization service
example:
The RF lab will need to prepare the SMD antenna on the assembly shipped to Johanson. The preparation
begins by identifying where the antenna is located. If the module is shipped assembled, the lab might
ask for disassembly instructions. The next step is to determine the injection point of our calibrated signal.
This process is destructive because in most cases the feed trace to the antenna will need to be isolated
from the RF source on the PCB. Since the signal is being injected using a probe, additional holes may
be drilled in any casings. The goal is to measure the antenna while the module is fully assembled. Once
the probe is in place, our technicians use a Smith chart and one of Johanson’s tuning kits (e.g., EIA
0402 kit S402DS, L402DC, L402W, S402TS, L/C_402DS) to get the impedance at 50-Ohms. Note: most
Johanson chip antennas do not naturally have a 50 Ohm impedance.
The specific, order-able part numbers of these matching Inductors and capacitors (L & Cs) are provided in
the report.
Once the antenna is confirmed to be tuned to the data-sheet specification, the next step is to measure the
radiated performance in an anechoic chamber. This measurement takes data which provides 2D
cuts at specified reference planes and a 3D plot representing the Johanson chip antenna on the customer
module.
Client is then sent copies of the new matching
circuit schematic with their corresponding values
and part numbers, measured radiated data,
and patterns with their corresponding radiated
efficiency and gain figures on your PCB.
Sometimes this process may require Johanson
Technology to modify your board in their lab,
and to add probes through your enclosure/
housing.
Assemblies may be returned to customers at
their request.
24 RESOURCE https://www.johansontechnology.com/ask-a-question

Testing, & Recommendations
+X +Z +Z
-Y +Y -X +X -Y +Y
-X -Z -Z
Please confirm with an engineer prior to sending Shipping address for prototypes to be
your module. Sending modules without a tuned & characterized is:
confirmation risks them getting misplaced.
Johanson Technology, Inc
The ultimate goal is to optimize “Over-The-Air” Attention: Name of the project engineer
performance of your design using Johanson’s 4001 Calle Tecate
extensive design knowledge and application Camarillo, CA 93012
optimization expertise for market success, this USA
entire process takes 2 to 3 weeks, depending on
the complexity of the design and environment.
Discussion
Custom Chip Antennas
Johanson welcomes any inquiry related to LTCC The Johanson Technical team will review your
antenna specifications which may not be in the specification or requirements document.
catalog and will consider your needs for a unique/
Contact our technical team
custom antenna solution.
https://www.johansontechnology.com/ask-a-question
The design and tooling costs for a new antenna
can be substantial. Thus, it is important that
we also understand your anticipated demand . .
Team
for this new product. Although not an absolute
. . . Johanson
requirement, an approximate minimum annual
quantity of 1,000,000 pieces and a minimum of here to help.
3 years of production should be used to estimate
the feasibility of developing a new chip antenna.
Don't miss the opportunity to work with our
outstanding design engineers.
Visit our website for more information. We look
forward to assisting you with your unique design
requirements See "RESOURCE" below.
RESOURCE https://www.johansontechnology.com/ask-a-question 25

Glossary
Antennas Terminology
Bandwidth: Polarization:
The range of frequencies over which an antenna The orientation of the electric field of the radiated
can operate with good performance. wave with respect to the ground plane.
Beam-width: the angular width of the main lobe Radiation Pattern:
of an antenna radiation pattern. The directional distribution of radiated energy
from an antenna in three-dimensional space.
Directivity:
A measure of how well an antenna concentrates Return Loss:
energy in a particular direction, expressed as a A measure of the amount of power reflected back
ratio of the power radiated in a specific direction towards the source when a signal is transmitted
to the total power radiated. through a transmission line or antenna. It is usually
expressed in decibels (dB) and is a measure of the
Gain:
impedance mismatch between the source and the
The measure of the ability of an antenna to direct load.
energy in a particular direction compared to an
isotropic radiator. Resonance:
The condition when an antenna is perfectly
Impedance:
matched to the frequency of the applied signal.
The opposition of an antenna to the flow of
alternating current (AC), measured in ohms. VSWR (Voltage Standing Wave Ratio):
The ratio of the maximum voltage to minimum
Isotropic Radiator: an idealized antenna that voltage along the transmission line connected
radiates energy equally in all directions. to the antenna.
Glossary
Types of Antenna Chips
Planar Inverted-F Antenna (PIFA): An antenna Slot Antenna: An antenna chip that uses a slot
chip that has a rectangular or square radiating in the ground plane as the radiating element.
element connected to the feedline by a shorting Often used in applications that require a high
pin. Widely used in mobile phones and other radiation efficiency and low profile.
portable devices due to its compact size and low
profile. Ceramic Patch Antenna: An antenna chip that
uses a ceramic material as the substrate. Often
Meander Line Antenna: An antenna chip that used in applications that require a high radiation
uses a zigzag or meandering line as the radiating efficiency and low loss.
element. Often used in applications that require
a narrow bandwidth. Inverted-L Antenna: An antenna chip that has
a vertical wire that is connected to a horizontal
Monopole Antenna: An antenna chip that wire, creating an "L" shape.
is constructed using a simple, single-element
structure. Often used in applications that require
a broad bandwidth and high gain.
Dipole or Folded Dipole Antenna: An antenna
chip that consists of two identical conductive
elements that are parallel to each other and
oriented in the same direction.
26 RESOURCE https://www.johansontechnology.com/ask-a-question

HIGH FREQUENCY
CERAMIC SOLUTIONS
Antennas
EXPLORE
SISTER PRODUCTS
Integrated Passive
Components:
• Band Pass Filters
• Baluns Thin Film Substrates
• Couplers
• Diplexers
• Triplexers
• High Pass Filters
• Low Pass Filters
• Power Dividers
Single Layer
Capacitors
High-Q Capacitors
LaserTrim® Tuning
Capacitors
RF Inductors:
Ceramic and
Wirewound
www.johansondielectrics.com
52/40_koobdnaH
annetnA_02
EXCELLENCE IN COMPONENT DESIGN
www.johansontechnology.com
POWER ELECTRONIC SOLUTIONS