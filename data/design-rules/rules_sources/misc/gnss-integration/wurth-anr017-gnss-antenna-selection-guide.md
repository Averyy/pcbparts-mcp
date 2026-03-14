---
source: "Wurth ANR017 -- GNSS Antenna Selection Guide"
url: "https://www.we-online.com/components/media/o171079v410%20ANR017_GNSS_Antenna.pdf"
format: "PDF 44pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 54573
---

ANR017
GNSS ANTENNA SELECTION
VERSION 1.2
JULY 19, 2023

WIRELESS CONNECTIVITY & SENSORS
ANR017 - GNSS Antenna Selection
Revision history
Manual
Notes Date
version
1.0 March 2020
• Initial version
1.1 April 2020
• Effective dielectric constant formula corrected
1.2 July 2023
• Updated Important notes, meta data and document style
1
Version 1.2, July 2023 www.we-online.com/wcs

Abbreviations
Abbreviation Description
AR Axial Ratio
BDS BeiDou navigation System
CP Circular Polarization
FR4 Flame Retardant 4
GLONASS Global Navigation Satellite System
GNSS Global Navigation Satellite System
GPS Global Positioning System
LHCP Left Hand Circular Polarization
LNA Low Noise Amplifier
RF Radio frequency
RHCP Right Hand Circular Polarization
SAW Surface Acoustic Wave
SMD Surface Mounted Device
THT Through Hole Technology
TM Transverse Magnetic
VSWR Voltage Standing Wave Ratio
2

Contents
1 Introduction 4
2 Basic Antenna Theory 5
2.1 Antenna Radiation Pattern . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5
2.2 Efficiency . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6
2.3 Directivity . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6
2.4 Antenna gain . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
2.5 Bandwidth . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
2.6 Input impedance and VSWR . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
2.7 Polarization and Axial ratio . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9
3 General Antenna Consideration 12
3.1 Passive Antenna Types . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13
3.1.1 Wire Antennas . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14
3.1.2 Loop Antennas . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14
3.1.3 Helix Antennas . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16
3.1.4 Spiral Antennas . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17
3.1.5 Microstrip Patch Antenna . . . . . . . . . . . . . . . . . . . . . . . . . . 19
3.1.6 Slot Antenna . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23
3.1.7 Ceramic Antenna . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24
3.1.7.1 Ceramic Chip Antenna . . . . . . . . . . . . . . . . . . . . . . . . . 24
3.1.7.2 Ceramic Patch Antenna . . . . . . . . . . . . . . . . . . . . . . . . 25
4 Ceramic Patch Antenna Analysis 27
5 Practical Implementation 32
6 Summary 39
7 Important notes 40
3

1 Introduction
This application note provides an understanding of antenna theory, antenna design considera-
tions and implementation for GNSS solutions. The first chapter of the document covers basic
antenna theory to provide better understanding of the following chapters. The later chapters of
the document focus on
• Types of antenna
• Design considerations
• Requirements and specifications
• Simulated analysis
• Practical implementation
Information provided in this application note are intended for GNSS solutions.
4

2 Basic Antenna Theory
An antenna can be described as a device used to radiate and absorb electromagnetic waves. It
transforms the electromagnetic waves from the free space into electrical voltages and currents
in conductors and vice versa. The antenna is an essential component in any RF communica-
tion system.
In GNSS applications, signals from satellites have very low power level at the earth surface.
This imposes a significant importance in selection, design and implementation of an antenna.
2.1 Antenna Radiation Pattern
The radiation pattern is simply defined as the representation of the electromagnetic field or en-
ergy radiated from the antenna. All radiation characteristics of an antenna can be represented
by a function in 2D or 3D coordinate systems. These patterns are created by measuring the
fields radiated from the antenna. They are commonly used to investigate the radiation field
characteristics of the antenna in detail.
The radiation patterns vary based on the antenna types and specification such as isotropic,
omnidirectional and directional.
Isotropic radiation is exhibited by an ideal antenna that radiates equally on all directions, how-
ever these antennas do not practically exist. Omnidirectional and directional are commonly
found radiation patterns. Omnidirectional antennas radiate equally in all directions perpen-
dicular to an axis. They exhibit a radiation pattern shaped like a donut in three dimensional
representation.
Antennas radiating in a specific direction apart from omnidirectional antennas are referred as
directional antennas. The radiation pattern of a directional antenna varies according to the
power distribution in different directions.
The radiation pattern is used to describe most antenna parameters in graphical representa-
tion for better understanding and interpretation.
Figure 1: Isotropic, Omnidirectional and Unidirectional radiation pattern
5

The radiation performance of antenna can be described through some important antenna pa-
rameters as follows:
• Efficiency
• Directivity
• Gain
• Bandwidth
• Polarization
• Axial ratio
Some of these parameters are further explained below.
2.2 Efficiency
Antenna efficiency is defined as a combination of radiation, conduction and reflection. The
radiation efficiency is simply the ratio of the total power transmitted into space to the input
power of the antenna provided by the source. The non-radiated input power accepted by the
antenna is lost in form of heat dissipation, dielectric and ohmic losses.
P
rad
η = (1)
P
in
P = P + P (2)
in rad l
P = Radiated power
rad
P = Input power accepted by the antenna
P = Power loss
l
η = Radiation efficiency
The total efficiency takes the power losses as well as the effect of impedance matching into
account. Both total and radiation efficiency can be used to express antenna gain.
2.3 Directivity
Directivity of an antenna is given by the ratio of radiation field density of an antenna in a given
direction to the average field density in all other directions.
Depending on the antenna design, direction of the radiation changes. In some cases the
antenna radiation is high in one direction relative to other directions. The front to back ratio of
the radiation also varies depending on the antenna design. Similar to Gain, the directivity of
an antenna is expressed in dB and it can be also expressed in dBi if it is defined relative to an
isotropic radiator.
6

2.4 Antenna gain
Antenna gain is one of the important parameters used to describe antenna performance. In
general, antennas are passive components and do not possess gain by itself similar to an am-
plifier power gain. Antenna gain can also be stated as a factor of radiation efficiency multiplied
by directivity. In practice, no antenna can transfer input power completely into radiated output
power resulting in radiation efficiency always less than a hundred percent. This results in the
antenna gain being always lower than directivity. Gain of an antenna is expressed in dB and it
can be also expressed in dBi if it is defined relative to an isotropic radiator.
G = D × η (3)
G = Antenna gain
D = Directivity
η = Radiation efficiency
2.5 Bandwidth
Bandwidth is defined as a range of frequencies in which the antenna characteristics meets
certain specification. These specification are defined based on the end application.
Each characteristic of an antenna varies over the frequency in a different manner. This results
in several bandwidth definitions depending on antenna characteristics like Efficiency band-
width, polarization bandwidth, directivity bandwidth, gain bandwidth and impedance bandwidth.
Commonly the antenna bandwidth is referred to impedance bandwidth or return loss band-
width. The specification is to achieve pure resistive impedance at antenna resonant frequency
and to get a minimum of -10dB return loss for the specified bandwidth.
As all the satellites signals are circularly polarized, GNSS application requires maintaining
a axial ratio below 3dB in the operating bandwidth of an antenna.
2.6 Input impedance and VSWR
As already discussed an efficient antenna radiates most of its power and has minimum loss to
provide better efficiency. Some of the reasons for power loss include reflection of the waves
and impedance mismatch in the transmission line.
To maximize power transfer in an antenna, output impedance of the transmission line should
match the input impedance of the antenna. In this way, the transmission line maintains the
same level of impedance, which is usually the characteristic impedance of the transmission line.
This is achieved by the process called impedance matching. In practice, the input impedance
of an antenna is affected by many external factors like nearby objects, conducting materials
and other antennas. In theory, for purposes of simplification, an isolated antenna composed of
real and imaginary parts is considered.
Z = R + X (4)
in in in
7

R = Input Resistance
X = Capacitive or Inductive reactance
The characteristic impedance widely used in the coaxial cables is 50 Ω, which provides best
trade-off between loss dissipation and power handling in RF systems. For this reason RF sys-
tems commonly work with 50 Ω transmission line.
Transmission lines with improperly matched impedance results in loss of power. Reflection
in the transmission line and related phenomena are further defined by some parameters such
as reflection coefficient, Voltage Standing Wave Ratio (VSWR) and return loss.
Reflection Coefficient is defined as the ratio of reflected wave voltage to the incident wave volt-
age.
(Zin − Zout)
Γ = (5)
(Zin + Zout)
Zin - Input impedance of the antenna
Zout - Characteristic impedance of the transmission line
Return loss of the antenna is given by
RL = 20 log (|Γ|) (6)
10
VSWR is the ratio of maximum voltage to the minimum voltage on the transmission line.
(1 + |Γ|)
V SW R = (7)
(1 − |Γ|)
8

2.7 Polarization and Axial ratio
Unlike other parameters, polarization is one of the least explained parameters in antenna char-
acteristics. It is used to describe the vectorial nature of the electric fields radiated by an an-
tenna. Based on the orientation of the electric field expressed by the antennas, the polarization
of an antenna is classified into linear and circular and elliptical polarization.
In linear polarization, the electric and magnetic field vectors do not change their direction dur-
ing wave propagation. If the electric field vectors are perpendicular to earth surface, the wave
is vertically polarized. If the electric field vectors are parallel to earth surface, then the wave
is horizontally polarized. Figure 2 shows the linear vertically polarized wave propagating in
the direction Z. The electric field vectors are represented in straight lines and the magnetic
field vectors are represented in dashed lines. Figure 3 shows the direction of the electric field
vectors in horizontal and vertically polarized waves respectively. In figure 3, direction of propa-
gation is away from the reader.
Figure 2: Linear polarization
Figure 3: Horizontal and vertical linear polarization
9

In circular polarization the electric and magnetic vectors do not point in the same direction.
They rotate 360° per wavelength during wave propagation. The rotation is achieved by the
specific excitation of the orthogonal modes. If the phase delay between the two orthogonal
modes is 90°, then circular polarization is achieved. Depending on the direction of rotation,
right hand or left hand circular polarization is determined. Figure 4 shows the right hand cir-
cular polarized wave propagating in the direction Z. Figure 5 shows the direction of electric
field vector rotation in left and right hand circular polarized waves respectively. In the figure 5,
direction of propagation is away from the reader.
Due to the relative antenna orientation and high to multipath interference, satellite communica-
tion applications tend to use circular polarization.
In practice, it is impossible to obtain a perfect circular polarization, which mostly results el-
liptical polarization. The ratio of major to minor axis of the ellipse is called the axial ratio. In
case of proper circular polarization, the minor and major axis are equal which gives an axial
ratio of unity or 0dB. Therefore, it is recommended to design an antenna with an axial ratio
as close as possible to 0dB. Depending on the type of antennas various methods are used to
achieve circular polarization.
Figure 4: Circular polarization
10

Figure 5: Left hand and right hand circular polarization
11

3 General Antenna Consideration
Based on the antenna theory described in the previous section, important antenna parameters
influencing the performance of the antennas can be understood. The requirements for antenna
design and selection are defined by those parameters. In addition to the technical requirements
derived from antenna parameters, other factors have to be taken into account in the antenna
selection process, such as
• Antenna placement
• Ground plane size and design
• Interference on the application board
• Impedance matching to the system
• Antenna exposure to sky
• Noise factor
• Power consumption
• End application
Active Antenna Enclosure
GNSS Receiver
Board
50Ω Output GNSS
SAW
Matching
LNA Receiver
Filter Network
RF Frontend
Antenna
Bias
Figure 6: Active antenna implementation
12

Different GNSS systems are used worldwide for positioning and navigation applications. In
general, the GNSS signal has a signal power level of -120dBm to -140dBm at the earth sur-
face, which implies that the GNSS receiver needs minimum carrier to noise ratio approximately
in the range from 35dBHz to 50dBHz for optimal performance.
A standard active antenna used for GNSS purpose commonly integrated with a LNA, SAW
filter along with 50 Ω matched input connection. So it provides higher gain, sensitivity and
reduced noise figure for an optimal performance to the receiver.
However, integration of an active antenna might be critical in applications with low power con-
sumption requirements. A proper gain selection of an active antenna is also necessary as an
antenna gain higher than receiver input specification might overload some GNSS receivers.
In the following chapters, this application note focuses on passive antenna types and related
considerations.
3.1 Passive Antenna Types
The typical technical antenna requirements of a passive antenna preferred for GNSS applica-
tion include
• High Gain towards zenith
• Low Noise Figure
• Axial Ratio close to unit
• LHCP signal rejection
• RHCP signal susception
• Properly matched impedance
As the GNSS signals are circular polarized, only circularly polarized antennas are described. It
is important for the passive antenna to use circular polarization. This demands RF expertise for
design and implementation. The circulation polarization can be obtained in passive antennas
through different methods based on the types of antenna.
13

Common passive antenna types which can provide circular polarization and can be used in
GNSS applications are
• Wire Antenna
• Loop Antenna
• Helix Antenna
• Spiral Antenna
• Slot Antenna
• Microstrip Patch Antenna
• Ceramic Antenna
Antennas listed here are originally linearly polarized. Their base designs can be modified to
achieve circular polarization.
3.1.1 Wire Antennas
Basic form of commonly used wire antennas are dipole wire antennas which support linear
polarization.
Designing a crossed dipole antenna using normal dipole wire antenna is a common method
used to obtain circular polarization. The crossed dipole is created by placing two dipole anten-
nas perpendicular to each other. Each dipole antenna is fed with 90° phase shift which results
in circular polarization. The crossed dipole antenna is large in size and radiation pattern of the
antenna is mostly omnidirectional due to the dipole antenna behaviour.
A crossed dipole to operate at frequency of 1.575GHz has the dimension:
• Dipole length = 71.2mm
• Width = 1.8mm
• Feed gap = 1.8mm
• Ground plane = 142mm x 142mm
It has a RHCP gain of -0.6dBi and Return loss of -13.4dB. Because of the omnidirectional ra-
diation and large dimension of the antenna, it is commonly not preferred for GNSS application.
3.1.2 Loop Antennas
A loop antenna is implemented generally by a bent metallic conductor to form different
shapes. Depending on the shapes, number of turns in the loop, structures as well as feed-
ing techniques the performance can be altered to achieve circular polarization.
Loop antennas are commonly used for its directional radiation pattern. The circular polar-
ization in loop antennas is achieved using different methods such as parasitic loop, dual loops
14

Figure 7: Normal dipole and cross dipole wire antenna
and different types of feeds.
Figure 8 shows a circular loop antenna with two concentric circular loops, among which the
inner loop is parasitic loop and the outer loop is a driven loop which is excited by a probe feed.
There are gaps in the loops, gap1 and gap2 placed at an angle 45° and 60° respectively.
Gap1 of outer loop produces circular polarized fields which is coupled with the inner loop to
provide circular polarization. The antenna is designed on an 40x40mm2 ground plane at a
height of 13mm and provides unidirectional radiation pattern. The gain of this antenna is about
7 to 8dBi and VSWR of 3 over the operating frequency at 1.5GHz.
All the parameters of the antenna can be altered to manipulate the antenna characteristics
to achieve best performance.
In case of figure 9, a dual rectangular loop antenna is designed on a ground plane of
200mm x 150mm at an height of 53mm excited at the middle through dipole antenna in se-
ries. The gaps in the loops are situated symmetrically with respect to the feed. In comparison
with single loop antennas, a dual loop antenna significantly increases the AR Bandwidth.
Similar to parasitic loop, all antenna parameters can be optimized for specific performance.
The optimized parameters values are x=48.3mm, y=96.7mm, g=5.9mm, L=157.4mm, d=10mm
and t=2mm.
At the operating frequency of 1.5GHz and with the optimized parameters the VSWR is 1.07,
15

Figure 8: Parasitic loop antenna
Figure 9: Dual rectangular loop antenna
with minimum AR of 0.03dB and similar gain as parasitic loop antenna.
3.1.3 Helix Antennas
Helix Antenna is a widely preferred antenna structure for the circular polarization. It is designed
by a metallic wire wound to form a screw thread like structure. The major parameters to design
16

the helix antenna which significantly influences the antenna performance are
• Number of turns (N)
• Pitch angle (α)
• Separation between turns (S)
• Diameter (D)
• Length of the antenna (L)
• Circumference of one turn (C)
The circumference of the turns defines the mode of operation. If the circumference of one
turn (C) is small compared to the wavelength then the mode of operation is referred as normal
mode. In normal mode the antenna exhibits linear polarization. If the circumference of one turn
is same or nearly equal to the wavelength then the mode of operation is referred as Axial mode.
Axial mode is the preferred operation mode because of its circular polarization and unidirec-
tional gain. One other mode of operation called higher-order radiation mode occurs when the
circumference exceeds the wavelength. This results in splitting the major lobe of the radiation
pattern.
For optimal performance in axial mode, the design equations of the key parameters are given
by
3 4
< C < λ (8)
4 3
S ≈ (9)
4
12◦ ≤ α ≤ 14◦ (10)
An axial mode helical antenna with minimal possible dimension to operate at 1.575GHz is given
as: L=19.3cm, C=21.2cm, D=6cm, S=4.2cm and N=4. The antenna is designed on a ground
plane of 21.5cm x 21.5cm. It has a RHCP gain of 11.6dBi and return loss of -13.8dB. Despite
having good characteristics, these antennas have some limitations such as high dimension
and complex integration. Ceramic helical antenna are also designed in order to reduce an-
tenna size.
3.1.4 Spiral Antennas
Spiral antennas provide frequency-independent performance in terms of radiation pattern,
impedance and polarization which is independent of frequency. This behaviour allows to oper-
ate over a wide range of frequencies.
Figure 11 shows different types of planar spiral antennas like sinusoidal log and archimedean
spiral antenna respectively. The antenna has two conducting arms flaring outwards from the
center. The structure of the arms flaring out depends on the type of spiral. For instance a
typical planar archimedean spiral antenna arm is defined by the equation
17

Figure 10: Helix antenna normal and axial mode
( )
r = r aφ b (11)
0
r- Inner radius
a - Expansion Coefficient
b - Spiral Coefficient
φ - Angle at radius linearly increase
The arms are excited in balanced mode with equal amplitude and with phase difference of
180°. This design results in the radiation of circularly polarized waves.
The characteristics of different planar spiral antenna types with minimum possible dimension
to operate at frequency 1.575GHz are displayed in the Table 1.
18

Figure 11: Different types of spiral antenna
Patch type RHCP Return Antenna Dimension
Gain(dBi) Loss(dB)
Planar Spiral-Log 2.1 -5.56 90mm x 90mm
Planar Spiral-Archimedean 0.92 -2.86 70mm x 70mm
Planar Spiral-Sinuous 4.8 -3.92 120mm x 120mm
Table 1: Spiral antenna characteristics
3.1.5 Microstrip Patch Antenna
Microstrip patch is one of the popular PCB antennas. It is well known for its low profile, low cost,
compact design and easy implementation. Patch antennas provide many design possibilities
to manipulate antenna behaviour. The required performance of the antenna can be achieved
by modifying the
• Structure
• Feed technique
• Patch design
During the design process, very common shapes of patch considered are rectangular and
circular patches. Depending on the dimensions of base patch, the shape further changes.
Some of basic shapes are shown in the figure 12
Figure 12: Microstrip patch antenna shapes
19

Once the shape of the patch is decided, the next important step is the feeding type to be used.
Generally, there are four types of feeds used for the excitation. These feed types are
1. Edge feed
2. Inset feed
3. Probe feed
4. Slot Feed
The above listed feed types are shown in the figure 13 respectively.
Figure 13: Feed types in microstrip patch antenna
A specific performance can be achieved using different designs, producing different patch an-
tenna solutions. During the design process, all requirements of the end application shall be
taken into account. Design considerations relevant to circular polarization shall also be taken
into account. Centre operating frequency depends on the dimension of the patch.
The width of the patch is determined approximately by the equation.
c
W ≈ (12)
(cid:114)
ε + 1
r
2fc
2
The effective dielectric constant is given by the equation
ε + 1 ε − 1 1
r r
ε = + ( ) (13)
eff (cid:114)
2 2 12h
1 +
W
Effective length of the patch is given as
c
L ≈ √ (14)
eff
2fc ε
Actual length of the patch is
L = L − 2∆L (15)
From the equation it can be seen that the length and width of the patch are inversely propor-
tional to the relative permittivity of the substrate. If size of the patch decreases, the relative
20

permittivity increases.
In case of circular patch the approximate radius is given by the equation
F
r ≈ (16)
(cid:114)
200h πh
1 + [ln( ) + 1.7726]
πε F 200h
8.791 × 109
F = √ (17)
fc ε
c - Velocity of light in vacuum
fc - Centre operating frequency
ε - Relative Permittivity of the substrate
h - Thickness of substrate
∆L - Length extension of patch during operation
r - Radius of the Patch
Even though the circular patch antenna has the advantage of wider bandwidth compared to
rectangular patch, the fabrication of circular patch is more challenging compared to the rectan-
gular patch. Therefore rectangular patch is preferred in practical application.
Antenna characteristics of different Microstrip patch antenna types with minimal possible patch
dimension without optimization to operate at frequency of 1.575GHz are given in the Table 2.
Further optimization and impedance matching is possible in the end application.
Patch type RHCP Return Patch Dimension Ground Dimension
Gain(dBi) Loss(dB)
Rectangular-Probe fed 2.7 -6.26 58mm x 45mm 97mm x 77mm
Rectangular-Inset fed 1.87 -10.32 58mm x 45mm 97mm x 138.7mm
Rectangular-Edge fed 1.7 -3.25 58mm x 45mm 97mm x 196.2mm
Circular-Probe fed 0.1 -0.3 45mm x 45mm 55mm x 55mm
Elliptical-Inset fed -4.2 -0.72 58mm x 45mmm 97mm x 138.7mm
Elliptical-Edge fed -4.3 -0.74 58mm x 45mmm 97mm x 196.2mm
Table 2: Microstrip patch antenna characteristics
After creating the basic design, the tuning of an antenna to achieve optimal performance is
made by further detailed design process. This tuning optimizes the antenna characteristics. As
already discussed, the basic concept of circular polarization is the excitation of two orthogonal
modes (TM01,TM10) equally but with a 90° phase difference. In case of microstrip patch an-
tenna, circular polarization phenomena is obtained by means of several feeding techniques and
combinations. One important condition to be always considered is to maintain 50 Ω impedance
microstrip lines in the feed networks.
21

Figure 14: Circular polarization feed techniques
22

The feeding techniques include
• Single feed with different excitations
• Excitation at specific angles
• Combination with slots
• Corner truncation
• Perturbation
• Dual or multi feeds
• Different feed network
Few of these feed techniques are shown in figure 14
3.1.6 Slot Antenna
Slot antennas are very simple PCB-based antennas. Their design is based on the concept of
microstrip patch antenna. Generally the slot antenna has a microstrip feed on bottom layer of
the PCB and a slot above on the top layer. The electromagnetic energy is coupled to the slot
through micro strip which enables the slot to radiate as an antenna. They are simpler to design
and can be easily integrated along with other active and passive devices. A broader bandwidth
relative to a normal microstrip patch can be achieved.
Figure 15: Different types of slot antennas
Circular polarization in the slot antenna is achieved by modifying the feed. Typical feed tech-
nique is to design a power divider in the microstrip line, so that two feeds with a quarter wave-
length excited at two orthogonal modes with a phase shift of 90°. To operate at 1.575GHz, a
microstrip fed slot antenna has a length=89mm, width=4.5mm and designed on a 134mm x
178mm ground plane. It provides a RHCP Gain of 2.1dBi and Return loss of -17.6dB.
The slots and feed shapes as well as structures can be varied in numerous ways to achieve
circular polarization. Some of such slot antenna types are shown in the figure 15
23

3.1.7 Ceramic Antenna
Ceramic antenna as indicated by the name itself, is an antenna created using ceramic as its
core material. The main reason of using ceramic material is strict size requirements in some
applications. As ceramic has higher relative permittivity compared to commonly used FR4 PCB
substrate, size of the ceramic antenna is relatively small. The size reduction also results in re-
duced gain, directivity and bandwidth of the antenna. Nevertheless, comparing to the similar
antenna design in FR4 substrates of same dimension, ceramic antennas provide the better
gain and directivity.
There are three major types of ceramic antennas. The first is the ceramic resonator or dielec-
tric resonator antenna which is commonly a ceramic cuboid or cylinder block used to radiate
energy. A single ceramic block cannot produce efficient results in all required antenna applica-
tions, they need to be adapted to the end application.
The second type is the ceramic patch antenna which is widely used for GNSS application
The third type is ceramic chip antenna which is well known for the small size and high efficiency.
3.1.7.1 Ceramic Chip Antenna
Ceramic chip antenna presents advantages in size, high gain and ease of implementation. It
is therefore one of the good choices of antenna for GNSS solutions. This type of antenna is
mostly used in relatively small like mobile applications.
Ceramic chip antenna provides relatively high gain in comparison to other antennas of similar
size, but does not provide optimal circular polarization and its performance is highly affected
by the ground plane. Commonly chip antenna comes under the monopole antenna classifi-
cation. In this classification, antenna together with the ground plane exhibit a dipole antenna
characteristic. The high gain of the chip antenna is achieved by a sufficiently large ground
plane. Some ceramic chip antenna manufacturers represent antennas with no ground plane
requirement which is not exactly true.
The linear polarization characteristics, ground plane influence, design consideration like iso-
lation distance, footprint and mounting of ceramic chip antenna shall be always taken into
consideration during design. To achieve much higher performance, the size of the antenna is
relatively increased which leads to further increase in ground plane size. Due to these difficul-
ties, chip antennas are only considered for suitable applications.
Some of the ceramic chip antennas available in the market and their typical characteristics are
given in the Table 3. All antennas listed in the table are linearly polarized and have own specific
layout recommendations. Impedance matching is possible in the end application.
24

Figure 16: Ceramic chip antenna
Dimension Gain(dBi) Bandwidth(MHz) Return Loss(dB) Ground Plane
3.2x1.6x0.5mm -2 10 < -10 80mm x 40mm
10x3.2x1.5mm -1.6 20 < -10 80mm x 37mm
10x10x0.9mm 1.2 45 < -10 70mm X 40mm
12x3mm x 2.4mm 1.6 45 < -10 70mm x 50mm
15x4mm x 3.2mm 1.6 45 < -9.5 100mm x 50mm
Table 3: Ceramic chip antenna characteristics
3.1.7.2 Ceramic Patch Antenna
Ceramic patch antenna is a patch antenna designed on ceramic substrate instead of the com-
mon printed circuit board. Due to nature of the ceramic material and flexible design solution
of microstrip patch antenna, Ceramic patch antennas provide optimal performance and are
suitable for GNSS application. As discussed in the section 3.1.5, possible microstrip patch
antenna designs apply to ceramic patch antennas as well. Because of the implementation of
the patch design on the ceramic substrate, the size of antenna can be reduced depending on
the ceramic material.
A typical dimension of microstrip patch for GNSS application is approximately 60mm x 40mm,
whereas ceramic patch antennas are available from dimension of 10mm x 10mm. Although
the characteristics change depending on size, they can be optimized by tuning the antenna.
Usage of ceramic substrate supports size reduction of the antenna.
If properly implemented, a ceramic patch antenna is circularly polarized and possess a hemi-
spherical radiation pattern. This leads to directivity almost twice the directivity of omnidirec-
tional antenna.
The high directivity from radiation pattern allows higher antenna visibility to sky and reduces
the interference from other devices nearby. Although the peak gain of the antenna even with
small ground plane would be high, the bandwidth reduces and also the Axial ratio gets affected.
The flexible design possibilities of the patch allow fine tuning of the antenna.
As of a very small ceramic patch, the performance reduces considerably. The typical preferred
size of the ceramic patch antenna range from 10 to 35mm.
Some of the typical characteristics of ceramic chip antennas for different sizes are given in
25

Figure 17: Ceramic patch antenna
Table 4. All antennas listed in the table are right hand circularly polarized with an axial ratio of
1-2.5 dB and the characteristics are displayed for the ground plane size of 75mm x 75mm.
The antenna tuning and impedance matching can be done in the end application for further
improvement in the characteristics.
Dimension RHCP Gain(dBic) Bandwidth(MHz) Return Loss(dB) Efficiency
10x10x4mm 2 10 < -10 45%
13x13x4mm 3 15 < -10 50%
15x15x4mm 3-4 15 < -10 70%
18x18mm x 4mm 4.5-5.5 20 < -10 70%
25x25mm x 4mm 5.5 25 < -9.5 80%
Table 4: Ceramic patch antenna characteristics
26

4 Ceramic Patch Antenna Analysis
As described in the previous section, the ceramic patch antenna is one of the most suitable
antenna for GNSS application and provides flexible designing to optimize the antenna perfor-
mance. This section allows to understand the antenna behaviour and design considerations to
be taken care before implementation of the antenna in practical application.
The smallest and most suitable ceramic patch antenna dimension is 18mm x 18mm, as this an-
tenna size has a bandwidth to provide required performance at all the interested frequency of
the GNSS application with the same design optimization. If the size of the antenna is smaller,
complex optimization is needed for different operating frequency.
There are two types of common mountings used in the ceramic patch antenna: SMD and
THT. The typical ground plane size of the 18mm x 18mm ceramic patch antenna for optimal
performance is 75mm x 75mm. Although by designing the patch the antenna performance can
be tuned, it has to be done by antenna design engineers and requires RF expertise. For an
already designed antenna the performance can also be manipulated by the ground plane size,
positioning and impedance matching.
To get a general overview and observe the behaviour of the already designed antenna, an
18mm x 18mm through hole mount antenna is simulated with two different conditions.
Firstly the antenna ground plane is varied from 20 mm2 to 75 mm2 throughout the simula-
tion. In the second setup, the position of the antenna is varied based on distance between the
edge of the ceramic patch antenna and the edge of the ground plane.
For a 75 mm2 standard ground plane shown in figure 18 the value of L is varied from 0mm
to 28.5mm, moving the antenna in a diagonal path from the corner to the center of the ground
plane.
The antenna is already tuned to the center frequency of 1576MHz and due to the change
in the size of the ground plane, the center frequency is shifted which results in detuning of
antenna. Although results for the antenna with different dimensions are subjected to change,
the behaviour of the antenna remains similar.
The analysis shows the importance of understanding the behaviour, design consideration and
implementation of the ceramic patch antenna. Figure 19 shows that, if the condition of antenna
implementation changes, the characteristics like center frequency, bandwidth, gain and axial
ratio change as well. The size of the ground plane is modified by the parameter G.
27

Figure 18: Ceramic patch antenna simulation - different ground plane
As from the results, it can be observed that the change in the ground plane influences all the
important parameters. Once the ground plane size decreases from the required size G=75mm
to 20mm, the antenna gets detuned to lower frequency. The rapid drop in center frequency
occurs around G=28mm, when the ground plane size becomes very small. On a typical ceramic
patch antenna implementation, it is better to have at least a ground size 10mm larger than the
antenna size, so that all sides of the antenna edge have distance of 5mm to the edge of the
ground plane.
Figure 19: Antenna performance for different ground plane
28

Design or implementation of other components in the near 5mm distance
around the antenna can affect the antenna performance. So generally, a min-
imum of 5mm keep out distance from antenna to other components is recom-
mended in layout design
The bandwidth becomes narrower with reduction in ground size reduction. The most affected
parameters are the RHCP Gain and Axial ratio, as seen in the results there is a phenomenal
change by the ground plane size reduction.
29

Similar to the size of the ground, the position of antenna on the ground plane also changes
the antenna characteristics. This is due to the change in the asymmetrical distribution of the
ground plane created by the change in antenna position. To observe the changes in antenna
characteristics in response to the change in antenna position on ground plane, a simulation
is executed. On the standard ground plane of 75x75 mm2 size, the position of the antenna is
moved from the corner to the center of the ground plane in a diagonal path by varying the value
of the parameter L from 28.5mm to 0mm. This setup can be seen in figure 20. The simulation
results are shown in figure 21.
Figure 20: Ceramic patch antenna simulation - different antenna position
Figure 21: Antenna performance for different antenna position
In the results, the center frequency, bandwidth and RHCP gain show small variation until the
antenna approaches the corner of the ground plane. Once the antenna moves very near ap-
proximately 5mm to the corner, the center frequency and RHCP gain are affected significantly
30

which is seen by the reduced antenna performance. Although the bandwidth increases ap-
proaching the corner, other parameters are drastically affected with the antenna positioned
near the corner of the ground plane. Most significantly the axial ratio is affected with the
change in position resulting in depolarization. This indicates that during the design process,
the antenna shall not be positioned near the edges or corner of the ground plane, as it results
in antenna performance degradation.
31

5 Practical Implementation
From the previous chapters, it can be understood that to implement the ceramic patch antenna
on a printed circuit board, certain design considerations should be taken into account. In order
to understand the antenna behaviour in real life scenario, the practical implementation of a ce-
ramic patch antenna is further explained in this section.
A ceramic patch antenna of size 18mm x 18mm with the through hole mount is designed on two
different Boards. PCB-A is a four layer PCB with dimension 60mm x 90mm. The ground plane
in PCB-A is distributed on layer 2 and layer 4. Layer 1 and layer 3 of the PCB are dedicated
for signal and power traces. Antenna feed is connected to the coplanar stripline on the bottom
layer.
PCB-B is also a four layer PCB with dimension 60mm x 118mm. The ground plane in PCB-B
is separated between the antenna and main ground plane. The main ground plane of the PCB
has a dimension of 60mm x 90mm distributed on the layer 2 and layer 4. Layer 1 and layer 3
of the PCB are dedicated for signal and power plane. The ceramic patch antenna has a dedi-
cated ground plane underneath on all the four layers with a dimension of 24mm x 24mm. The
antenna ground plane is connected to the main ground plane on layer 3 and layer 4. This con-
nection also supports the coplanar strip line feed connection to the antenna pin on the bottom
layer.
Figure 22: PCB-A
32

Figure 23: PCB-B
33

As described already, tuning an antenna for a specified ground can be done on the ceramic
patch antenna through the modification handled on the patch. Apart from tuning the antenna
through the patch modification, the impedance matching method is the most commonly used
tuning method which allows to a set the antenna in optimal performance for certain frequency
range. Impedance matching allows to match the antenna input impedance to a characteristic
impedance of the transmission line. Using impedance matching the antenna can be set into
resonance at operating frequency, achieve low return loss and better signal reception.
To have a 50 Ω impedance matched coplanar line from the receiver output to antenna input,
the input impedance of the antenna should be known. It can be seen from figure 24 that four
different through hole ceramic patch antennas (A1, A2, A3, A4) of dimension 18mm x 18mm
are soldered on both PCB-A and PCB-B.
Figure 24: Antennas assembled on PCB-A and PCB-B
34

The antennas are from different manufacturers and have similar characteristics. Firstly, the
impedance characteristics and return loss of the antenna on two PCB variants are observed
using a network analyzer which is shown in the figure 25.
In figure 25, there can also be seen the markers are placed on the frequencies represent-
ing the important GNSS systems as GPS, Galileo, GLONASS and BeiDou.
• Marker 1: 1.561 GHz (BeiDou)
• Marker 5: 1.609 GHz (GLONASS)
• Marker 6: 1.575 GHz (GPS, Galileo)
The green markers are used in the impedance trace and the yellow markers are used in return
loss trace.
As per the technical data from manufacturers, the antennas have an input impedance of 50 Ω.
However, the input impedance varies according to the ground plane which can be observed
from network analyzer measurment in figure 25. It can be seen the green markers in figure 25
changes between PCB-A and PCB-B, exhibiting different input impedance.
PCB-A provides input impedance close to 50 Ω. PCB-A is also less susceptible to external
influence than PCB-B.
Figure 25 also denotes that the operating frequency range of the different GNSS systems
vary and not all the frequencies can be covered for the optimal performance, thus resulting in a
trade-off between the performance and operating frequency. Based on the navigation system
on the end application, impedance matching is done for a particular system or favouring some
systems over other.
35

PCB-A PCB-B
↑
↓
1 A1
↑ 6 ↑ 5
↑ 5 1 3
↑ 6 ↑ 1 ↑ 5
A2
↓
6 ↑
5 ↓ ↑ 6 ↑ 6
↑ 1 ↑ 5 ↑
A3
1 ↑
5 ↓ 6 ↑ 5
A4
↑ 1 ↑ 6 5 ↓ ↑ 1 ↑ 6 ↑ 5
Figure 25: Input impedance of antennas on PCB-A and PCB-B 36

Impedance matching can be done using different methods. Most common method is using
Π-filter matching circuit composed of capacitive and inductive elements. Along with the help of
the Smith chart, the values of components in the pi filter are modified to determine the proper
impedance matching circuit. On both PCB-A and PCB-B, a pi filter circuit is designed using a
coplanar strip on the bottom layer where the components can be assembled to provide 50 Ω
matched output for the antenna feed pin.
Figure 26: Pi-filter on PCB
PCB-A providing the better antenna input impedance is used for further experimentation. The
antennas along with the other circuitry are assembled on PCB-A and taken into operation.
All the boards are tuned to have optimal 50 Ω matched impedance from output of the GNSS
receiver to antenna input. To compare antenna performance, the GNSS signals which are re-
ceived by the GNSS receiver through the implemented antenna are analysed and the mean
carrier to noise ratio of four strong satellite signals are plotted over time, which can be seen in
the figure 27.
The antenna A2 shows better signal reception for all the important frequencies and systems in
comparison to other antennas. Based on the result from the figure 27, antenna variant ’A2’, an
18mm x 18mm through hole ceramic patch antenna from the manufacturer Abracon, is selected
as the most suitable option for implementation on our GNSS Evaluation boards.
37

48
46
44
42
40
38
36
34
32
01:00:00 04:10:00 01:30:00 04:40:00 01:60:00 04:70:00 01:90:00 04:01:00 01:21:00 04:31:00 01:51:00 04:61:00 01:81:00 04:91:00 01:12:00 04:22:00 01:42:00 04:52:00 01:72:00 04:82:00 01:03:00 04:13:00 01:33:00 04:43:00 01:63:00 04:73:00 01:93:00 04:04:00 01:24:00 04:34:00 01:54:00 04:64:00 01:84:00 04:94:00 01:15:00 04:25:00 01:45:00 04:55:00 01:75:00 04:85:00 01:00:10 04:10:10 01:30:10 04:40:10
ANTENNA PERFORMANCE ANALYSIS
A1 A2
A3 A4
)zH-Bd(
oN/C
Time (S)
Figure 27: Antenna performance analysis
38

6 Summary
This application note provides recommendations and guidelines for GNSS antenna selection
as well as implementation.
An introduction section covers fundamentals of antenna theory (Chapter 2). Chapter 2 provides
the necessary basics to understand concepts, terms and details of the rest of the analysis.
Followed by that, challenges of antenna selection, design and implementation for GNSS an-
tennas are discussed. Advantages and disadvantage of the different antenna solutions are
highlighted.
Critical steps of the integration, such as:
• Tuning the patch
• Optimized antenna dimension
• Implementation
and their impact on the end application are explained in detail and shown with several ex-
amples. Provided examples also shows the change in characteristics for different antenna
implementations of same type.
Being one of the most used antennas, a simulated analysis of ceramic patch antennas was
performed and described for different test conditions. The results explains the effect of external
influence on the ceramic patch antenna implementation. The guidelines for practical imple-
mentation are also discussed based on analysis.
Discussing the practical implementation of different ceramic patch antennas in real life
scenarios emphasized major design challenges, such as:
• Antenna detuning
• Influence of ground plane
• Influence of antenna position
• Change in performance
In the last part of the application note, the performance analysis of the different antennas are
represented graphically. The results display the signal reception capabilities of the antenna.
Although the antennas used have similar characteristics, the performance on the implemented
PCB is different. Based on the performance of the antennas, the antenna with best signal
reception is selected for the end application. The end application in this case is the evaluation
boards of our GNSS modules Elara − II and Erinome − II.
Considerations and outcomes of this work concerning antenna selection, design, and
integration are decisive for the performance of the GNSS end application.
39

7 Important notes
The Application Note and its containing information ("Information") is based on Würth Elek-
tronik eiSos GmbH & Co. KG and its subsidiaries and affiliates ("WE eiSos") knowledge and
experience of typical requirements concerning these areas. It serves as general guidance and
shall not be construed as a commitment for the suitability for customer applications by WE
eiSos. While WE eiSos has used reasonable efforts to ensure the accuracy of the Information,
WE eiSos does not guarantee that the Information is error-free, nor makes any other repre-
sentation, warranty or guarantee that the Information is completely accurate or up-to-date. The
Information is subject to change without notice. To the extent permitted by law, the Information
shall not be reproduced or copied without WE eiSos’ prior written permission. In any case,
the Information, in full or in parts, may not be altered, falsified or distorted nor be used for any
unauthorized purpose.
WE eiSos is not liable for application assistance of any kind. Customer may use WE eiSos’
assistance and product recommendations for customer’s applications and design. No oral or
written Information given by WE eiSos or its distributors, agents or employees will operate to
create any warranty or guarantee or vary any official documentation of the product e.g. data
sheets and user manuals towards customer and customer shall not rely on any provided Infor-
mation. THE INFORMATION IS PROVIDED "AS IS". CUSTOMER ACKNOWLEDGES THAT
WE EISOS MAKES NO REPRESENTATIONS AND WARRANTIES OF ANY KIND RELATED
TO, BUT NOT LIMITED TO THE NON-INFRINGEMENT OF THIRD PARTIES’ INTELLEC-
TUAL PROPERTY RIGHTS OR THE MERCHANTABILITY OR FITNESS FOR A PURPOSE
OR USAGE. WE EISOS DOES NOT WARRANT OR REPRESENT THAT ANY LICENSE, EI-
THER EXPRESS OR IMPLIED, IS GRANTED UNDER ANY PATENT RIGHT, COPYRIGHT,
MASK WORK RIGHT, OR OTHER INTELLECTUAL PROPERTY RIGHT RELATING TO ANY
COMBINATION, MACHINE, OR PROCESS IN WHICH WE EISOS INFORMATION IS USED.
INFORMATION PUBLISHED BY WE EISOS REGARDING THIRD-PARTY PRODUCTS OR
SERVICES DOES NOT CONSTITUTE A LICENSE FROM WE eiSos TO USE SUCH PROD-
UCTS OR SERVICES OR A WARRANTY OR ENDORSEMENT THEREOF.
The responsibility for the applicability and use of WE eiSos’ components in a particular cus-
tomer design is always solely within the authority of the customer. Due to this fact it is up
to the customer to evaluate and investigate, where appropriate, and decide whether the de-
vice with the specific characteristics described in the specification is valid and suitable for the
respective customer application or not. The technical specifications are stated in the current
data sheet and user manual of the component. Therefore the customers shall use the data
sheets and user manuals and are cautioned to verify that they are current. The data sheets
and user manuals can be downloaded at www.we-online.com. Customers shall strictly observe
any product-specific notes, cautions and warnings. WE eiSos reserves the right to make cor-
rections, modifications, enhancements, improvements, and other changes to its products and
services at any time without notice.
WE eiSos will in no case be liable for customer’s use, or the results of the use, of the com-
ponents or any accompanying written materials. IT IS CUSTOMER’S RESPONSIBILITY TO
VERIFY THE RESULTS OF THE USE OF THIS INFORMATION IN IT’S OWN PARTICULAR
ENGINEERING AND PRODUCT ENVIRONMENT AND CUSTOMER ASSUMES THE ENTIRE
RISK OF DOING SO OR FAILING TO DO SO. IN NO CASE WILL WE EISOS BE LIABLE FOR
40

CUSTOMER’S USE, OR THE RESULTS OF IT’S USE OF THE COMPONENTS OR ANY AC-
COMPANYING WRITTEN MATERIAL IF CUSTOMER TRANSLATES, ALTERS, ARRANGES,
TRANSFORMS, OR OTHERWISE MODIFIES THE INFORMATION IN ANY WAY, SHAPE OR
FORM.
If customer determines that the components are valid and suitable for a particular design and
wants to order the corresponding components, customer acknowledges to minimize the risk of
loss and harm to individuals and bears the risk for failure leading to personal injury or death
due to customers usage of the components. The components have been designed and devel-
oped for usage in general electronic equipment only. The components are not authorized for
use in equipment where a higher safety standard and reliability standard is especially required
or where a failure of the components is reasonably expected to cause severe personal injury
or death, unless WE eiSos and customer have executed an agreement specifically governing
such use. Moreover WE eiSos components are neither designed nor intended for use in areas
such as military, aerospace, aviation, nuclear control, submarine, transportation, transporta-
tion signal, disaster prevention, medical, public information network etc. WE eiSos must be
informed about the intent of such usage before the design-in stage. In addition, sufficient re-
liability evaluation checks for safety must be performed on every component which is used in
electrical circuits that require high safety and reliability functions or performance. COSTUMER
SHALL INDEMNIFY WE EISOS AGAINST ANY DAMAGES ARISING OUT OF THE USE OF
THE COMPONENTS IN SUCH SAFETY-CRITICAL APPLICATIONS.
41

List of Figures
1 Isotropic, Omnidirectional and Unidirectional radiation pattern . . . . . . . . . . . 5
2 Linear polarization . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9
3 Horizontal and vertical linear polarization . . . . . . . . . . . . . . . . . . . . . . 9
4 Circular polarization . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10
5 Left hand and right hand circular polarization . . . . . . . . . . . . . . . . . . . . 11
6 Active antenna implementation . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12
7 Normal dipole and cross dipole wire antenna . . . . . . . . . . . . . . . . . . . . 15
8 Parasitic loop antenna . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16
9 Dual rectangular loop antenna . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16
10 Helix antenna normal and axial mode . . . . . . . . . . . . . . . . . . . . . . . . 18
11 Different types of spiral antenna . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19
12 Microstrip patch antenna shapes . . . . . . . . . . . . . . . . . . . . . . . . . . . 19
13 Feed types in microstrip patch antenna . . . . . . . . . . . . . . . . . . . . . . . 20
14 Circular polarization feed techniques . . . . . . . . . . . . . . . . . . . . . . . . . 22
15 Different types of slot antennas . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23
16 Ceramic chip antenna . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25
17 Ceramic patch antenna . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 26
18 Ceramic patch antenna simulation - different ground plane . . . . . . . . . . . . . 28
19 Antenna performance for different ground plane . . . . . . . . . . . . . . . . . . . 28
20 Ceramic patch antenna simulation - different antenna position . . . . . . . . . . . 30
21 Antenna performance for different antenna position . . . . . . . . . . . . . . . . . 30
22 PCB-A . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 32
23 PCB-B . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33
24 Antennas assembled on PCB-A and PCB-B . . . . . . . . . . . . . . . . . . . . . 34
25 Input impedance of antennas on PCB-A and PCB-B . . . . . . . . . . . . . . . . 36
26 Pi-filter on PCB . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 37
27 Antenna performance analysis . . . . . . . . . . . . . . . . . . . . . . . . . . . . 38
List of Tables
1 Spiral antenna characteristics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19
2 Microstrip patch antenna characteristics . . . . . . . . . . . . . . . . . . . . . . . 21
3 Ceramic chip antenna characteristics . . . . . . . . . . . . . . . . . . . . . . . . . 25
4 Ceramic patch antenna characteristics . . . . . . . . . . . . . . . . . . . . . . . . 26
42

Contact
Würth Elektronik eiSos GmbH & Co. KG
Division Wireless Connectivity & Sensors
Max-Eyth-Straße 1
74638 Waldenburg
Germany
Tel.: +49 651 99355-0
Fax.: +49 651 99355-69
www.we-online.com/wireless-connectivity