---
source: "Semtech AN1200.40 -- SX1261/SX1262 Reference Design Explanation"
url: "https://cdn-reichelt.de/documents/datenblatt/A200/SX1262REFERENCE.pdf"
format: "PDF 25pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 24358
---

SX1261/2
WIRELESS & SENSING PRODUCTS
Application Note:
Reference Design Explanation
www.semtech.com
AN1200.40
Rev 1.1
May 2018

Table of Contents
1. Introduction ....................................................................................................................................................................... 4
2. Reference Design Versions ........................................................................................................................................... 5
2.1 SX1261 PCB_E406V03A ........................................................................................................................................... 5
2.1.1 E406V03A Schematic ....................................................................................................................................... 5
2.1.2 E406V03A PCB .................................................................................................................................................... 7
2.2 SX1262 PCB_E428V03A ........................................................................................................................................... 9
2.2.1 E428V03A Schematic ....................................................................................................................................... 9
2.2.2 E428V03A PCB .................................................................................................................................................. 10
2.3 SX1262 PCB_E449V01A ......................................................................................................................................... 13
2.3.1 E449V01A Schematic ..................................................................................................................................... 13
2.3.2 E449V01A PCB .................................................................................................................................................. 14
3. Transmitter Impedance Matching and Filter Designs ...................................................................................... 17
3.1 Impedance Matching Stage ................................................................................................................................. 17
3.1.1 Load-Pull ............................................................................................................................................................ 18
3.1.2 Impedance Matching .................................................................................................................................... 19
3.1.3 Harmonic Filtering .......................................................................................................................................... 20
4. Receiver Balun and Impedance Matching ............................................................................................................ 21
5. Conclusion ........................................................................................................................................................................ 22
6. Revision History .............................................................................................................................................................. 23
7. Glossary ............................................................................................................................................................................. 24
Wireless & Sensing Products
SX1261/2 Reference Design Explanation Page 2 of 25
AN1200.40 Rev 1.1 May 2018 Semtech

List of Figures
Figure 1: SX1261 Reference Design Schematic (PCB_E406V03A) ........................................................................... 6
Figure 2: SX1261 Reference Design Layout – Top Layer (PCB_E406V03A) .......................................................... 7
Figure 3: SX1261 Reference Design Layout – Top Layer RF only (PCB_E406V03A) ........................................... 8
Figure 4: SX1261 Reference Design Layout – Bottom Layer (PCB_E406V03A) ................................................... 8
Figure 5: SX1262 Reference Design Schematic (PCB_ E428V03A) .......................................................................... 9
Figure 6: SX1262 Reference Design Layout – Top Layer (PCB_ E428V03A) ....................................................... 10
Figure 7: SX1262 Reference Design Layout – Layer 2 (PCB_ E428V03A) ............................................................. 11
Figure 8: SX1262 Reference Design Layout – Layer 3 (PCB_ E428V03A) ............................................................. 11
Figure 9: SX1262 Reference Design Layout – Bottom Layer (PCB_ E428V03A) ................................................ 12
Figure 10: SX1262 Reference Design Schematic (PCB_ E449V01A) ...................................................................... 13
Figure 11: SX1262 Reference Design Layout – Top Layer (PCB_ E449V01A) ..................................................... 14
Figure 12: SX1262 Reference Design Layout – Layer 2 (PCB_ E449V01A) .......................................................... 15
Figure 13: SX1262 Reference Design Layout – Layer 3 (PCB_ E449V01A) .......................................................... 15
Figure 14: SX1262 Reference Design Layout – Bottom Layer (PCB_ E449V01A) .............................................. 16
Figure 15: SX1261 Transmitter and Receiver Matching/Filtering Topologies ................................................... 17
Figure 16: Load-Pull Data of SX1261 at 915 MHz ......................................................................................................... 18
Figure 17: Simulation of Transmitter Matching Network ......................................................................................... 19
Figure 18: SX1261 Source Pull Data at 915 MHz .......................................................................................................... 21
SX1261/2 Reference Design Explanation Page 3 of 25

1. Introduction
The purpose of this application note is to assist engineers with the selection of optimal reference
design and understanding of the key components and design methodology deployed in each
design of the SX1261 and SX1262.
It is recommended to read this application note in conjunction with the following documents which
can be found on www.semtech.com:
• Application Note AN1200.37 “Recommendations for Best Performance”
• SX1261/2 Datasheet
SX1261/2 Reference Design Explanation Page 4 of 25

2. Reference Design Versions
There are currently three versions of SX1261/2 reference designs which cover the majority of the sub-
GHz ISM frequency bands around the world. The reference designs are available upon request to
your Semtech representative.
Table 1: SX1261/2 Reference Designs & Sub-GHz ISM Frequency Bands around the World
PCB # Part PCB Layer Reference Region Band [MHz]
Europe 863 – 870
PCB_E406V03A SX1261 2 XTAL Rest of Asia 923
South Korea 920 - 923
PCB_E428V03A SX1262 4 XTAL USA, Canada 902 - 928
Australia 915 - 928
PCB_E449V01A SX1262 4 TCXO
India 865 - 867
2.1 SX1261 PCB_E406V03A
The SX1261 reference design (E406V03A) is optimized to support all sub-GHz ISM frequency bands.
It’s designed to deliver +14 dBm of output power with only 25.5 mA of current consumption at 3.3V.
It can even be programmed to deliver up to +15 dBm of output power for applications where
antenna loss is expected. Each region has its dedicated bill of materials.
2.1.1 E406V03A Schematic
The SX1261 E406V03A schematic is illustrated below in Figure 1. From the schematic, it can be
observed that the transmit and receive paths are combined by a Peregrine PE4259 RF switch. The use
of the RF switch facilitates the optimization of transmitter and receiver matching networks and
filtering, which ultimately improves receive sensitivity and transmit output power and harmonic
performance.
The power amplifier output stage (RFO) of the SX1261 is biased by an internal regulator output
(VR_PA) through an external pull-up inductor. In turn, the VR_PA regulator is powered by either an
internal LDO or a DC - DC converter through the VDD_IN pin. The choice between using the internal
LDO or the DC - DC converter ultimately comes down to the tradeoffs between PCB size, component
cost, and power efficiency. On one hand the internal LDO offers the benefits of smaller size, and
lower cost through the elimination of a large inductor between pins 7 and 9, but at the expense of
power efficiency. On the other hand, the DC - DC converter offers higher power efficiency, but at the
expense of size and cost. Output power varies with changing VR_PA, but is kept relatively constant
SX1261/2 Reference Design Explanation Page 5 of 25

over the entire main supply voltage of 1.8 to 3.7 V. The current consumption however changes
inversely with main supply voltage.
Despite smaller size and lower cost, the default configuration of the SX1261 E406V03A reference
design is powered by DC - DC. The benefit of lower power consumption, along with the deployment
of thermal relief, enables the use of a low-cost crystal as reference instead of a TCXO.
To choose the LDO regulator, the inductor between pin VDD_IN and pin VREG is replaced by a short
and the inductor between VREG and DCC_SW is removed.
Figure 1: SX1261 Reference Design Schematic (PCB_E406V03A)
SX1261/2 Reference Design Explanation Page 6 of 25

2.1.2 E406V03A PCB
This SX1261 reference design (PCB_E406V03A) was designed on a low-cost, standard two-layer FR-4
substrate. The top layer houses all of the components and critical RF layout. The bottom layer serves
as ground and control routing.
To mitigate the impact of reference frequency drift on receive performance due to high heat
dissipation of the SX1261, extra precautions were taken to isolate the crystal from the rest of the PCB
on all layers. As shown in Figures 2 and 3, a copper void around the reference was implemented on
all layers.
Figure 2: SX1261 Reference Design Layout – Top Layer (PCB_E406V03A)
SX1261/2 Reference Design Explanation Page 7 of 25

Figure 3: SX1261 Reference Design Layout – Top Layer RF only (PCB_E406V03A)
Figure 4: SX1261 Reference Design Layout – Bottom Layer (PCB_E406V03A)
SX1261/2 Reference Design Explanation Page 8 of 25

2.2 SX1262 PCB_E428V03A
The SX1262 reference design (PCB_ E428V03A) is designed for regions that support higher output,
while still tolerating the use of a crystal as clock reference thanks to the maximum packet duration of
less than 400 milliseconds. The optimized bill of materials for the supported regions (USA and
Canada) enable the reference design to deliver up to +22 dBm, while maintaining a current
consumption of around 118 mA at 3.3 V.
2.2.1 E428V03A Schematic
The schematic as shown in Figure 5 is almost identical to the SX1261 two-layer reference design
(PCB_E406V03A). The key difference is that VDD_IN, source of the internal regulator VR_PA, is
powered directly from the battery VBAT pin instead of VREG. This is still a DC - DC supplied
configuration, where the DC - DC is used for the chip core only.
Figure 5: SX1262 Reference Design Schematic (PCB_ E428V03A)
SX1261/2 Reference Design Explanation Page 9 of 25

2.2.2 E428V03A PCB
The key difference between this SX1262 PCB design versus the SX1261 two-layer design is that the
former deploys a four-layer FR-4 substrate instead of a two-layer substrate. The primary reasons are
that it is intended to deliver output powers of up to +22 dBm, thermal dissipation is more critical, and
it’s not as cost-sensitive as the other applications.
In this design, the top layer remains dedicated to all components and critical RF routing. Layer 2
serves as reference ground for all RF circuitries, layer 3 is used for control routing, and layer 4 is solid
ground.
In a similar way to the SX1261 two-layer design, a copper void was created around the crystal
reference, on all layers, to mitigate the thermal effects on frequency drift.
Figure 6: SX1262 Reference Design Layout – Top Layer (PCB_ E428V03A)
SX1261/2 Reference Design Explanation Page 10 of 25

Figure 7: SX1262 Reference Design Layout – Layer 2 (PCB_ E428V03A)
Figure 8: SX1262 Reference Design Layout – Layer 3 (PCB_ E428V03A)
SX1261/2 Reference Design Explanation Page 11 of 25

Figure 9: SX1262 Reference Design Layout – Bottom Layer (PCB_ E428V03A)
SX1261/2 Reference Design Explanation Page 12 of 25

2.3 SX1262 PCB_E449V01A
The SX1262 reference design (PCB_ E449V01A) is designed for regions that support high output and
maximum packet durations beyond 400 milliseconds; thus requiring the use of a four-layer board
PCB and TCXO as clock reference. The optimized bill of materials for the supported regions (Australia
and India) enable the reference design to deliver up to +22 dBm, while maintaining currently
consumption of around 118 mA at 3.3V.
2.3.1 E449V01A Schematic
The schematic as shown in Figure 10 is almost identical to the SX1262 four-layer reference design
(PCB_ E428V03A). The key difference is in the use of a TCXO as clock reference instead of a crystal. It
was experimentally proven that two- and four-layer boards equipped with crystal and thermal
insulation similar to PCB_E406V03A and PCB_E428V03A were still exceeding the tolerable frequency
drifts in regions where maximum packet duration could be as high as 2.8 seconds.
Figure 10: SX1262 Reference Design Schematic (PCB_ E449V01A)
SX1261/2 Reference Design Explanation Page 13 of 25

2.3.2 E449V01A PCB
The only difference between this SX1262 PCB versus the other SX1262 four-layer reference design
PCB (PCB_ E428V03A) is the lack of thermal isolation around the reference, through all layers.
Figure 11: SX1262 Reference Design Layout – Top Layer (PCB_ E449V01A)
SX1261/2 Reference Design Explanation Page 14 of 25

Figure 12: SX1262 Reference Design Layout – Layer 2 (PCB_ E449V01A)
Figure 13: SX1262 Reference Design Layout – Layer 3 (PCB_ E449V01A)
SX1261/2 Reference Design Explanation Page 15 of 25

Figure 14: SX1262 Reference Design Layout – Bottom Layer (PCB_ E449V01A)
SX1261/2 Reference Design Explanation Page 16 of 25

3. Transmitter Impedance Matching and Filter Designs
The primary objective of impedance matching and harmonic filtering is to achieve the maximum
power transfer from the PA output to the antenna, while consuming the least amount of power and
emitting the lowest level emissions in order to meet the regulatory requirements. Here we take as
example the SX1261 at 915 MHz. The methodology used is applicable to both SX1261 and SX1262, at
all frequencies.
The transmitter impedance matching/filtering can be split into 3 sections: the impedance matching
stage, the second harmonic filtering stage, and the higher order harmonic filtering stage.
As shown in Figure 15, the chosen matching topology consists of L3 and C5, the second order
harmonic filter consists of L3 and C4, and the higher order harmonic filter consisting of C5, L4 and C7.
C6 serves as a DC block to protect the input of the RF switch. The expected input impedance to the
RF switch is 50 ohms. The network at the output of the RF switch is primarily there to offer optimal
matching to the antenna, but additional filtering can also be achieved through such network.
2nd Harmonic
Filter
High Order
Harmonic Filter
Impedance Antenna Matching & Filtering
Matching
Figure 15: SX1261 Transmitter and Receiver Matching/Filtering Topologies
3.1 Impedance Matching Stage
In order to maximize power transfer and minimize power consumption, an optimal impedance Zopt
must be presented to the output of the power amplifier. Although L3 and C5 have been identified as
the primary impedance matching components, the remaining filtering components C4/L3 and
C6/L4/C7 will also contribute to the effective load impedance seen by the power amplifier.
Therefore, it’s important to include all three stages of impedance transformation and filtering when
designing the network which represents the Zopt. The load-pull data and impedance matching
components shown below may not be the most up-to-date. Contact your Semtech representative
for the latest information per reference design.
SX1261/2 Reference Design Explanation Page 17 of 25

3.1.1 Load-Pull
To obtain Zopt, a load-pull analysis is typically conducted using an impedance tuner and network
analyzer, referenced to the PA output pad (RFO) of SX1261/2. During this process, the load presented
to the PA output is swept in magnitude and phase while recording the output power and current
consumption. The results are then plotted on a Smith chart in the Figure 16, the highest output
power of 14.6 dBm at 915 MHz was identified to be at an impedance of 11.7 + j4.8 ohms, while 13.5 +
j7.6 ohms offers lower output power but with higher efficiency.
Note: the configuration explained here is meant to obtain an optimal +14 dBm power output at the
end of the chain consisting of matching, filtering and RF switch, anticipating losses due to these last
stages.
Figure 16: Load-Pull Data of SX1261 at 915 MHz
To ensure that the peak power impedance point has been identified, data at a power level roughly
lower than 1 dB were also plotted. If this is implemented correctly, the peak power impedance on
SX1261/2 Reference Design Explanation Page 18 of 25

the graphic would be somewhere near the center of all the points. With this information, the
designer can then choose the appropriate Zopt based on desired output power and power
consumption.
3.1.2 Impedance Matching
Once the Zopt and the impedance matching have been identified, the next steps would be to come
up with a practical matching and filtering topology, and simulate the theoretical values by using
tools such as Agilent ADS and Ansoft Designer.
The goal of the impedance matching stage is to present the optimum load impedance to the
SX1261/SX1262 PA when matched to 50 ohms. In order to minimize the number of components for
the matching network, this will be done using L3 and C5 of the TX stage.
Figure 17: Simulation of Transmitter Matching Network
In reality, it’s often necessary to fine-tune the simulated values to account to PCB parasitic and
practical component values.
SX1261/2 Reference Design Explanation Page 19 of 25

3.1.3 Harmonic Filtering
Harmonic filtering is implemented in two stages: the second harmonic notch filter and the higher
order harmonic low-pass filter.
The notch filter is implemented by replacing the original L3 with a parallel LC filter. As a general rule
of thumb, the new inductor value is chosen to be 3/4 of the original L3, and C4 is calculated to
resonate out the second harmonic of the carrier frequency.
The higher order harmonic filter is a 50-ohm to 50-ohm pi filter, realized on C5, L4, C6, and C7. C5 is
therefore used for both the impedance matching and the harmonic filtering, and its value will be the
sum of the two values obtained separately.
Again, it’s often necessary to fine-tune the simulated values to account for PCB parasitic and practical
component values.
The last step would be to add the PE4259 RF switch and redo the measurements. Additional filtering
and impedance matching to any non-50-ohm antenna can be accommodated by utilizing C8, C9, L5,
and C10.
SX1261/2 Reference Design Explanation Page 20 of 25

4. Receiver Balun and Impedance Matching
The low-noise amplifier (LNA) of the SX1261/2 is designed with differential inputs for the benefit of
common mode rejection and immunity against noise and interferers.
The LC network in front of the differential inputs serves both functions of a balun to convert the single-
ended to differential signals and impedance transformation. As shown in Figure 15, this network
consists of two capacitors (C11, C12) and one inductor (L6). C13 is an optional element which could be
used to provide additional rejection against undesired interferers.
In a similar way to the transmitter, the primary objective of impedance matching on the receiver front-
end is to transform the ideally 50-ohm impedance at the RF switch output to the desired optimal
impedance (Zopt) of the SX1261/2 differential LNA inputs.
The steps to identify the optimal source impedance and simulating/implementing the matching
network are similar to the ones deployed on the transmitter. A source pull was first conducted to
identify the optimal impedance which delivers the lowest noise figure, as shown in Figure 18. In the
case of SX1261 at 915 MHz, the optimal differential source impedance is 74 + j134.
Figure 18: SX1261 Source Pull Data at 915 MHz
SX1261/2 Reference Design Explanation Page 21 of 25

5. Conclusion
In summary, this application note clarified some of the key differences between the available
reference designs, and the major advantages and disadvantages between 2-layer versus 4-layer
substrates, LDO regulator versus DC - DC converter, and XTAL versus TCXO. It also explained the
methodology on how the transmit and receive performances were optimized.
SX1261/2 Reference Design Explanation Page 22 of 25

6. Revision History
Version Date Modifications
1.0 December 2017 First Release
1.1 May 2018 Update of PCB part numbers and schematics
SX1261/2 Reference Design Explanation Page 23 of 25

7. Glossary
DC -DC Direct Current to Direct Current (power conversion)
ISM Industrial, Scientific and Medical applications
LDO Low Dropout
LNA Low-Noise Amplifier
LoRa® LOng RAnge modulation technique
LoRaWAN™ LoRa® low power Wide Area Network protocol
PA Power Amplifier
PCB Printed Circuit Board
RF Radio-Frequency
RFO Radio Frequency Output
RX Receiver
SW Software
TCXO Temperature-Compensated Crystal Oscillator
TX Transmitter
VDD Voltage Drain Drain
VREG Voltage Regulator
XTAL Crystal
SX1261/2 Reference Design Explanation Page 24 of 25

Important Notice
Information relating to this product and the application or design described herein is believed to be reliable, however such information
is provided as a guide only and Semtech assumes no liability for any errors in this document, or for the application or design described
herein. Semtech reserves the right to make changes to the product or this document at any time without notice. Buyers should obtain
the latest relevant information before placing orders and should verify that such information is current and complete. Semtech warrants
performance of its products to the specifications applicable at the time of sale, and all sales are made in accordance with Semtech’s
standard terms and conditions of sale.
SEMTECH PRODUCTS ARE NOT DESIGNED, INTENDED, AUTHORIZED OR WARRANTED TO BE SUITABLE FOR USE IN LIFE-SUPPORT
APPLICATIONS, DEVICES OR SYSTEMS, OR IN NUCLEAR APPLICATIONS IN WHICH THE FAILURE COULD BE REASONABLY EXPECTED TO
RESULT IN PERSONAL INJURY, LOSS OF LIFE OR SEVERE PROPERTY OR ENVIRONMENTAL DAMAGE. INCLUSION OF SEMTECH PRODUCTS
IN SUCH APPLICATIONS IS UNDERSTOOD TO BE UNDERTAKEN SOLELY AT THE CUSTOMER’S OWN RISK. Should a customer purchase or
use Semtech products for any such unauthorized application, the customer shall indemnify and hold Semtech and its officers,
employees, subsidiaries, affiliates, and distributors harmless against all claims, costs damages and attorney fees which could arise.
The Semtech name and logo are registered trademarks of the Semtech Corporation. The LoRa® Mark is a registered trademark of the
Semtech Corporation. All other trademarks and trade names mentioned may be marks and names of Semtech or their respective
companies. Semtech reserves the right to make changes to, or discontinue any products described in this document without further
notice. Semtech makes no warranty, representation or guarantee, express or implied, regarding the suitability of its products for any
particular purpose. All rights reserved.
© Semtech 2018
Contact Information
Semtech Corporation
200 Flynn Road, Camarillo, CA 93012
E-mail: sales@semtech.com
Phone: (805) 498-2111, Fax: (805) 498-3804
www.semtech.com
SX1261/2 Reference Design Explanation Page 25 of 25