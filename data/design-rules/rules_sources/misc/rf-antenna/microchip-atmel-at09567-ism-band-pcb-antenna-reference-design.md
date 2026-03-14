---
source: "Microchip/Atmel AT09567 -- ISM Band PCB Antenna Reference Design"
url: "https://ww1.microchip.com/downloads/en/Appnotes/Atmel-42332-ISM-Band-Antenna-Reference-Design_Application-Note_AT09567.pdf"
format: "PDF 10pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 14604
---

APPLICATION NOTE
AT09567: ISM Band PCB Antenna Reference Design
Atmel Wireless
Features
 Compact PCB antennas for 915MHz and 2.4GHz ISM bands
 Easy to integrate Altium® design files and gerber files
 Return Loss, Radiation Pattern, Gain, and Efficiency measurement results
 Guidelines to integrate antenna board with RF board
Description
Scope of this application note is to guide customers to design ISM band antenna for
915MHz/2.4GHz ISM bands and use them in applications based on
AT86RF212B/AT86RF233 transceivers.
This application note contains some ISM band antennas, brief design note, and
integration challenges. The accompanying zip file contains detailed application notes,
PCB Gerber files, and the results of antenna measurement.
Atmel-42332B-WIRELESS-12/2014

Table of Contents
1. Introduction ........................................................................................ 3
2. Compact ISM Band Antennas ............................................................ 3
2.1 λ/4 Antennas ..................................................................................................... 3
2.1.2 Monopole Antenna .............................................................................. 4
2.1.3 Inverted-F Antenna ............................................................................. 4
2.2 PCB Antenna EVKs for ISM Band ..................................................................... 4
3. Antenna Measurement ....................................................................... 6
3.1 Return Loss Measurement ................................................................................ 6
3.2 Radiation Pattern, Gain, and Efficiency Measurement ...................................... 6
3.3 Guidelines for Antenna Integration with RF Transceiver ................................... 6
4. Abbreviations and Acronyms .............................................................. 7
5. References ........................................................................................ 8
6. Revision History ................................................................................. 9
AT09567: ISM Band PCB Antenna Reference Design [APPLICATION NOTE] 2

1. Introduction
This application note guides in designing a new ISM band PCB antenna based on system requirements, available board
space, and layer stack up.
These antenna reference designs can be easily integrated with corresponding ISM band transceivers (915MHz/2.4GHz)
to verify their prototypes quickly and it is a better reference for designing a new antenna.
2. Compact ISM Band Antennas
The 915MHz ISM band (902MHz ~ 928MHz) is a commonly used unlicensed band in the United States of America and
2.4GHz ISM band (2.402GHz ~ 2.484GHz) is the most commonly used unlicensed band worldwide for industrial, scientific,
and medical applications. Demand for compact antennas operating in ISM bands is increasing day by day. PCB antennas
are compact and cost effective for frequencies above 700MHz. Many reference designs are available for designing
standard PCB antennas. A few standard antennas are Dipole, Patch, Loop, etc. But, these standard antennas are not
suitable for handheld / mobile applications due to their large dimension.
2.1 λ/4 Antennas
The λ/4 antennas are smaller compared to the standard antennas and they are very popular. Well known λ/4 antennas
are monopole antenna and Inverted-F antenna which are discussed in Section 2.1.2 and 2.1.3. When the size of the
standard λ/4 antennas is large at some frequencies and the antenna cannot be accommodated in the available space on
the PCB, the designer can apply some miniaturization techniques to fit the antenna into the available board space,
although this might cause some slight degradation in performance.
Table 2-1. PCB Characteristic
PCB Material - Parameter Value
PCB substrate FR-4
Dielectric constant ( εr ) 4.4
Loss tangent (tanδ) 0.02
Substrate thickness 1.6mm
Cu thickness 35µm
Figure 2-1. PCB Layer Stack up
AT09567: ISM Band PCB Antenna Reference Design [APPLICATION NOTE] 3

If a standard λ/4 antenna is used for the above PCB layer stack up, it requires a λ /4 length of 45mm for 915MHz and
g
17mm for 2.4GHz excluding ground plane size. Also, the length of the ground plane must be >= λ /4. Any modifications
to the size of the ground plane, affects the performance of antenna. The designer should be careful about the ground
plane size during the design and it must be fixed to the actual board size of the application.
C
λ =
√ε f
r
Where,
λ = Guided wavelength
C = Velocity of light
f = Frequency of operation
ε = Relative permittivity of dielectric material
r
Using Folded/Meander miniaturization technique, the size of the antenna can be reduced to fit the available board size
with a small degradation in antenna efficiency and radiation characteristics when compared with a standard antenna.
Folded/Meander structure actually requires longer trace length (in multiple bends) than λ/4 for its operation. However, it
occupies lesser space.
Return Loss, Gain, Directivity, Efficiency, and Far-Filed Pattern Cuts are tuned in simulation before creating the prototype.
PCB parameters are specified in Table 2-1. PCB layer stackup is shown in Figure 2-1.
2.1.2 Monopole Antenna
A standard λ/4 Printed Monopole Antenna (λ=wavelength) is widely used in many applications due to its small size and
good radiation characteristics. So, it can be used for ISM band application. The operation of monopole is similar to dipole.
The ground plane of the Monopole acts as the second arm to perform a dipole operation [1]. Example monopole structures
are shown in Figure 2-2 and Figure 2-3.
2.1.3 Inverted-F Antenna
Another example for λ/4 antenna is Printed Inverted-F antenna. One end of the λ/4 arm of the IFA is short circuited
and other end is open circuited. Short circuited end acts as a shunt inductor and open circuited end acts as a shunt
capacitor. These shunt inductor and capacitor forms a parallel resonant circuit and decides the resonant frequency.
By varying these inductor and capacitor values through trace adjustment, its resonant frequency can be varied.
Example Inverted-F structures are shown in Figure 2-4.
2.2 PCB Antenna EVKs for ISM Band
The following small size PCB antenna EVK reference designs are available for ISM band application. The accompanying
zip file contains application notes, PCB files, and test reports for the following EVKs:
1. 915MHz ISM band Printed Folded Monopole Antenna (ATEVK-900-ANT-FM)
2. 915MHz ISM band Printed Meander Monopole Antenna (ATEVK-900-ANT-M)
3. 915MHz ISM band Printed Inverted-F Antenna (ATEVK-900-ANT-IFA)
4. 2.4GHz ISM band Printed Folded Monopole Antenna (ATEVK-2400-ANT-FM)
5. 2.4GHz ISM band Printed Meander Monopole Antenna (ATEVK-2400-ANT-M)
6. 2.4GHz ISM band Printed Inverted-F Antenna (ATEVK-2400-ANT-IFA)
AT09567: ISM Band PCB Antenna Reference Design [APPLICATION NOTE] 4

The structures of ISM band Printed Folded Monopoles are shown in Figure 2-2 Meander antennas are shown in Figure
2-3 and Inverted-F antennas are shown in Figure 2-4.
Figure 2-2. 900MHz and 2.4GHz ISM band Printed Folded Monopole Antenna EVKs
Figure 2-3. 900MHz and 2.4GHz ISM band Printed Meander Monopole Antenna EVKs
Figure 2-4. 900MHz and 2.4GHz ISM band Printed Inverted-F Antenna EVKs
AT09567: ISM Band PCB Antenna Reference Design [APPLICATION NOTE] 5

3. Antenna Measurement
3.1 Return Loss Measurement
Return Loss (S11) can be directly measured in a Calibrated Vector Network Analyzer.
The antenna can be fine-tuned in the prototype to operate in the desired band by achieving better Return Loss. Increasing
the length of the antenna trace reduces the resonant frequency of the antenna and decreasing the length increases the
resonant frequency. Length can be increased using copper foil. Increasing the width of the line will improve the bandwidth.
Another way of tuning is to use lumped elements to match the antenna impedance to characteristic impedance for the
desired centre frequency [2].
3.2 Radiation Pattern, Gain, and Efficiency Measurement
Radiation Pattern, Gain, and Efficiency are measured in anechoic chamber. The 2D Radiation Pattern-cuts (Azimuth and
Elevation) which describe the radiation characteristics of the antenna by measuring power density in different directions
in an anechoic chamber. Test antenna is usually configured in receive mode for pattern measurement.
Peak Gain of the test antenna is measured with respect to standard transmit antenna in the main beam/maximum radiation
direction. Gain varies from direction to direction in association with Radiation Pattern.
Efficiency of the PCB antennas depends on the available board space for antenna placement, antenna type, and ground
plane size. The reference designs use very small ground plane and hence the efficiency might be slightly less when
compared with standard antennas. If the ground plane is large enough in the final application board, the efficiency might
be higher.
3.3 Guidelines for Antenna Integration with RF Transceiver
 Although, the discussed reference boards contain only two layers, these reference designs can be used for
multilayer application. In multilayer application, antenna can be placed either on top layer or bottom layer based
on the available space. Any change in dielectric constant or tangent loss of the PCB material or PCB thickness
will shift the resonant frequency and change radiation characteristics. These factors must be considered while
designing the application.
 It is a good practice to have transceiver and antenna on the same layer without having any via-hole in RF path.
Via holes create discontinuity and loss of signal which will require proper impedance matching to reduce loss.
 Copper clearance must be provided in all layers beneath the antenna except patch antenna. Because, conductor
will reflect RF signal and change the radiation characteristics of the antenna.
 RF trace connecting Transceiver output (Balun output for Differential output Transceivers) and antenna feed
point must be 50Ω controlled impedance line. It is highly preferred to have a provision for Pi-pad matching network
to improve the matching between Transceiver output and antenna input. It will avoid board re-spin during
mismatched circumstances. Many combinations of lumped element matching methods are available [2].
 Mechanical enclosure of the product must not have any conductive material. Plastic enclosure is preferred; but,
it might also detune the antenna from the desired band. So, tuning the antenna with lumped components must
be performed by placing it within the enclosure.
 RF and antenna board can be placed seperately. If space is not a constraint, SMA cables can be used to connect
RF board with antenna board. Most ISM band applications are designed on small sized boards. A small board
mount RF connector such as U.FL and mating flexible RF cables can also be used to connect RF board with
antenna board.
AT09567: ISM Band PCB Antenna Reference Design [APPLICATION NOTE] 6

4. Abbreviations and Acronyms
BW : Bandwidth
CPW : Coplanar Waveguide
GND : Ground
GHz : Giga Hertz
ISM : Industrial, Scientific and Medical
MHz : Mega Hertz
mm : milli-meter
PCB : Printed Circuit Board
RF : Radio Frequency
SMA : SubMiniature version A
µm : micro-meter
AT09567: ISM Band PCB Antenna Reference Design [APPLICATION NOTE] 7

5. References
[1] “Antenna Theory: Analysis and Design”, Third Edition, Constantine A. Balanis
[2] “Microwave Engineering”, Fourth Edition, David M.Pozar
AT09567: ISM Band PCB Antenna Reference Design [APPLICATION NOTE] 8

6. Revision History
Doc. Rev. Date Comments
42332B 12/2014 Inverted-F antennas added.
42332A 07/2014 Initial document release.
AT09567: ISM Band PCB Antenna Reference Design [APPLICATION NOTE] 9

Atmel Corporation Atmel Asia Limited Atmel Munich GmbH Atmel Japan G.K.
1600 Technology Drive Unit 01-5 & 16, 19F Business Campus 16F Shin-Osaki Kangyo Bldg.
San Jose, CA 95110 BEA Tower, Millennium City 5 Parkring 4 1-6-4 Osaki, Shinagawa-ku
USA 418 Kwun Tong Road D-85748 Garching b. Munich Tokyo 141-0032
Tel: (+1)(408) 441-0311 Kwun Tong, Kowloon GERMANY JAPAN
Fax: (+1)(408) 487-2600 HONG KONG Tel: (+49) 89-31970-0 Tel: (+81)(3) 6417-0300
www.atmel.com Tel: (+852) 2245-6100 Fax: (+49) 89-3194621 Fax: (+81)(3) 6417-0370
Fax: (+852) 2722-1369
© 2014 Atmel Corporation. All rights reserved. / Rev.: Atmel-42332B-WIRELESS-12/2014
Atmel®, Atmel logo and combinations thereof, Enabling Unlimited Possibilities®, and others are registered trademarks or trademarks of Atmel Corporation or its
subsidiaries. Altium® is a registered trademark of Altium Limited. Other terms and product names may be trademarks of others.
Disclaimer: The information in this document is provided in connection with Atmel products. No license, express or implied, by estoppel or otherwise, to any intellectual property right is granted by this
document or in connection with the sale of Atmel products. EXCEPT AS SET FORTH IN THE ATMEL TERMS AND CONDITIONS OF SALES LOCATED ON THE ATMEL WEBSITE, ATMEL ASSUMES
NO LIABILITY WHATSOEVER AND DISCLAIMS ANY EXPRESS, IMPLIED OR STATUTORY WARRANTY RELATING TO ITS PRODUCTS INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT. IN NO EVENT SHALL ATMEL BE LIABLE FOR ANY DIRECT, INDIRECT,
CONSEQUENTIAL, PUNITIVE, SPECIAL OR INCIDENTAL DAMAGES (INCLUDING, WITHOUT LIMITATION, DAMAGES FOR LOSS AND PROFITS, BUSINESS INTERRUPTION, OR LOSS OF
INFORMATION) ARISING OUT OF THE USE OR INABILITY TO USE THIS DOCUMENT, EVEN IF ATMEL HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES. Atmel makes no
representations or warranties with respect to the accuracy or completeness of the contents of this document and reserves the right to make changes to specifications and products descriptions at any time
without notice. Atmel does not make any commitment to update the information contained herein. Unless specifically provided otherwise, Atmel products are not suitable for, and shall not be used in,
automotive applications. Atmel products are not intended, authorized, or warranted for use as components in applications intended to support or sustain life.