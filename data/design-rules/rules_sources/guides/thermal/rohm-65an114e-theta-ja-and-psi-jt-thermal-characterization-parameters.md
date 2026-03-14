---
source: "ROHM 65AN114E -- theta-JA and psi-JT (Thermal Characterization Parameters)"
url: "https://fscdn.rohm.com/en/products/databook/applinote/common/theta_ja_and_psi_jt_an-e.pdf"
format: "PDF 7pp"
method: "pdfplumber"
extracted: 2026-03-02
chars: 18031
---

Application Note
Thermal Design
θ and Ψ
JA JT
θJA and ΨJT indicate how difficult it is for heat to be conducted. Although both of these are indicators of heat, there may be
questions about what their differences are and how they are used in different situations. This application note explains the
differences between θJA and ΨJT and how to use them correctly.
Definition of θ
JA
Implement the measurement environment and method in
θJA is defined in the JEDEC Standards JESD51-1 and
accordance with JESD51-1 and JESD51-2A. The description
JESD51-2A. In the definition, θJA is described as follows:
here provides an overview. Refer to Reference [5] and [6] for
Thermal resistance from junction to ambient: Thermal
details.
resistance from the moving part of the semiconductor device
to the natural convection (still air) environment surrounding the As shown in Figure 2, the measurement environment consists
device. The symbol is RθJA (alternative θJA). of a PCB-mounted IC fixed in a predetermined position, which
is placed in an enclosure (box) made of a material with low
For θJA, mount the device on a PCB created to conform to the
thermal conductivity and completely sealed to prevent air flow
JESD51-3, JESD51-5, and JESD51-7 standards and measure
to and from the outside.
the temperature under the measurement environment of
JESD51-2A. The ambient temperature is measured with a thermocouple in
accordance with the specifications specified in JESD51-2A
Figure 1 shows an example of a four-layer PCB for surface-
fixed in a predetermined position (i.e., a position unaffected by
mounted ICs. For details on JEDEC Standard, refer to
the heat source).
References [1], [2], and [3] on the last page. These documents
contain detailed instructions on PCB dimensions and
materials, device mounting positions, copper foil thickness
and size, lead wire dimensions, thermal via dimensions, and
so on. For an example of the specifications, refer to Reference
[4].
76.2mm
m
m
3
.4
1
1
Figure 7. Example of a four-layer PCB for surface-mounted
ICs created to conform to the JESD51-3, JESD51-5, and
JESD51-7 standards

1/6
FEBRUARY 2023
T h e r m o c o u p le
mm
392
Figure 2. Schematic diagram of the test fixture and enclosure

θ and Ψ Application Note
As a preparation for the measurement, measure the forward Start measuring θJA from here. Apply a large current to the
voltage so as to use a diode in the IC as the sensing diode to body diode in Figure 3 to heat the IC so as to raise the junction
determine the junction temperature. For this diode, as shown temperature by 30°C - 60°C. Then, switch to a minute current,
in Figure 3, use the body diode of the MOSFET, which measure the forward voltage, and convert it to the junction
becomes the heat source while the IC is operated. Place the temperature using the graph in Figure 4. When the
IC in a thermostatic chamber and measure the forward voltage temperature change is stabilized, record the junction
at each temperature by applying a minute current that does temperature and ambient temperature. Use the following
not cause the diode to get hot. An example of the equation to calculate θJA from the measured value.
measurement result is shown in Figure 4. Now it is possible to
determine the junction temperature by measuring the forward 𝑇 −𝑇
𝜃 = 𝐽𝑠𝑠 𝐴𝑠𝑠 [°𝐶/𝑊] (1)
voltage. 𝐽𝐴 𝑃 𝐻
𝑇 : Junction temperature when the device reaches the
𝐽𝑠𝑠
steady state after Power PH is applied [°C]
Heat source Body diode
𝑇 : Ambient temperature when the device reaches the
while the IC is 𝐴𝑠𝑠
operated steady state [°C]
𝑃 : Consumption power that causes the change in the
Constant 𝐻
current junction temperature [W]
I
The thermal resistance θJA is the temperature difference
between the junction temperature and the ambient
temperature divided by the consumption power.
Figure 3. Using the body diode of the heat source MOSFET Figure 5 shows the heat radiation path when θJA is measured.
as the sensing diode to determine the junction temperature Heat is transferred from the junction through various paths.
Therefore, changes in board conditions and space
environment cause changes in the thermal resistance.
800
700 I F =1mA The purpose of measuring θJA is only to compare the thermal
]V m 600 performance of one package with another in a standardized
[
V
F
500
environment. θJA is neither intended nor able to predict
e
g package performance in application-specific environments.
a 400
tlo
v
d 300
ra
w ro 200 Thermal
F conduction
100 TJ
Convection
0
25 50 75 100 125 150
Ambient temperature T [ºC]
A
Radiation
Figure 4. Example of the forward voltage temperature
θJA
TA
characteristic of the body diode
Figure 5. Heat dissipation path when θJA is measured
2/6

How to use θ JA Figure 6 shows the change in θJA when the copper foil area is
varied, where the HTSOP-J8 package is mounted on the
The following shows how to use θJA.
JEDEC 4-layer PCB. θJA listed in the data sheet is located at
Example 1: the right end of the curve, which shows that only the difference
Comparing θJA between different products to select the one in copper foil area among many environmental conditions
with better heat dissipation performance (lower θJA). causes such a change. In addition to this, there are many
environmental conditions that should be considered, such as
Example 2: board thickness, number of layers, copper foil thickness,
Comparing θJA between different products to roughly thermal via placement, and enclosure space capacity.
estimate how many degrees C the junction temperature will
change relative to each other. Definition of Ψ JT
Δ𝑇
𝐽
=(𝜃
𝐽𝐴2
−𝜃
𝐽𝐴1
)×𝑃
𝐷
[℃] (2) ΨJT is defined in JEDEC Standard JESD51-2A In the definition,
ΨJT is described as follows: 「The thermal characterization
𝜃 : Thermal resistance of Product 1 [°C/W]
𝐽𝐴1
parameter to report the difference between junction
𝜃 : Thermal resistance of Product 2 [°C/W]
𝐽𝐴2
temperature and the temperature at the top center of the
𝑃 : Power loss [W]
outside surface of the component package, divided by the
power applied to the component.」.
Misuse of θ
Measure ΨJT in the same environment as θJA described earlier.
A common type of misuse is to use θJA listed in the data sheet
To measure the temperature at the center of the package
and the following equation to calculate the junction
surface, fix a thermocouple in the center of the package with
temperature.
thermally conductive epoxy adhesive as shown in Figure 7.
𝑇 =𝜃 ×𝑃 +𝑇 [℃] (3)
𝐽 𝐽𝐴 𝐷 𝐴
𝑇 :Ambient temperature [°C]
𝐴
Since θJA listed in the data sheet is measured in an
environment standardized by JEDEC, it is not possible to
estimate the junction temperature in unique applications with
different environments.
100
90
80
Figure 7. Fixing a thermocouple in the center of the package
70
surface with thermally conductive epoxy adhesive
)W 60
/C
º(
50
Next, apply a large current to the body diode in Figure 3 to
θJ 40
heat the IC so as to raise the junction temperature by 30°C -
30
60°C. Then, switch to a minute current, measure the forward
20
voltage, and convert it to the junction temperature using the
10
graph in Figure 4. When the temperature change is stabilized,
0
0 1000 2000 3000 4000 5000 6000 record the junction temperature and thermocouple
Middle 1, 2 and Bottom Layer Copper Foil Area (mm2)
temperature. Use the following equation to calculate ΨJT from
the measured value.
Figure 6. Change in θJA when the copper foil area is varied
(HTSOP-J8 package, JEDEC 4-layer PCB)
3/6

𝑇 −𝑇
𝜓 = 𝐽𝑠𝑠 𝑇𝑠𝑠 [°𝐶/𝑊] (4)
𝐽𝑇 𝑃
𝐻
𝑇 : Junction temperature during the steady operation
𝐽𝑠𝑠
[°C]
𝑇 : Temperature at the center of the package surface
𝑇𝑠𝑠
during the steady operation [°C]
𝑃 : Consumption power that causes the change in the
𝐻
junction temperature [W]
The thermal characteristics parameter ΨJT is the temperature
difference between the package surface and the junction
temperature divided by the consumption power. If the transfer
rate of heat flow from the junction to the package surface is
constant, ΨJT is proportional to the temperature difference
between the package surface and the junction temperature.
Therefore, it is possible to estimate the junction temperature
by measuring the package temperature of the device in the
actual environment if the temperature characteristics
parameters are measured under similar conditions.
4/6
Ψ JT
T T
T
J
T h e rm a l
c o n d u c tio n
C o n v e c tio n
R a d ia tio n
Figure 8 shows the heat dissipation path when ΨJT is
measured. Heat is dissipated from the junction in the three-
dimensional direction, where thermal conduction is the largest
form of heat transfer. Since SMDs (Surface Mount Devices)
dissipate most of their heat to the PCB, the heat flow between
the junction and the package surface is very small. Therefore,
it is found that the temperature difference between TJ and TT
is very small and the value of ΨJT is also small. When the value
of ΨJT is small, the error in estimating the junction temperature
is also small, even if there are differences between the JEDEC
board and the actual equipment board.
Figure 9 shows the change in ΨJT when the copper foil area is
varied, where the HTSOP-J8 package is mounted on the
JEDEC 4-layer PCB. ΨJT listed in the data sheet is located at
the right end of the curve, which shows that the change is very
small compared with θJA marked with a dotted line (the same
curve as in Figure 6).
How to use Ψ
JT
The following shows how to use ΨJT.
Measure the temperature of the package surface and estimate
the junction temperature using ΨJT that is listed in the data
sheet.
Use the following equation to calculate the junction
temperature.
𝑇 =𝛹 ×𝑃 +𝑇 [℃] (5)
𝐽 𝐽𝑇 𝐷 𝑇
Figure 8. Heat dissipation path when ΨJT is measured
𝛹 : Thermal characteristics parameter from the junction to
𝐽𝑇
the package surface [°C/W]
100
90
𝑇 : Temperature at the center of the package surface [°C]
80 𝑇
70
)W 60 Prepare the parameter values required for the calculation.
/C
° 50
(
(θ
) 1. From among the ΨJT data listed in the data sheet or the
ΨJ 40
thermal resistance application note, select the PCB
30
condition value closest to that of the actual equipment.
20
Ψ
10 JT 2. PD is the power loss while the applicable device is operated.
0 Determine this by actual measurement or by calculation.
0 1000 2000 3000 4000 5000 6000
Middle 1, 2 and Bottom Layer Copper Foil Area (mm2) 3. Measure TT by fixing a thermocouple in the center of the
package surface with thermally conductive epoxy adhesive.
Figure 9. Change in ΨJT when the copper foil area is varied
For precautions for the measurement, refer to Reference [7].
(HTSOP-J8 package, JEDEC 4-layer PCB)

Summary
ΨJT is the temperature difference from the junction to the
θJA is the temperature difference from the junction to the
center of the package surface divided by the heat flow (power
surrounding environment divided by the heat flow between the
loss) generated by the device. Since ΨJT is measured in the
two points (power loss). Since there are multiple paths
same JEDEC environment as θJA, ΨJT changes in other
between two points as shown in Figure 10 and the heat flow
applications as in the case of θJA. However, most of the heat
for each path is different in applications other than the JEDEC
is dissipated toward the board in the SMD application, so the
measurement environment, θJA also changes. Although it is
heat flow between the two points, the junction and the package
possible to compare θJA values measured in the JEDEC
surface, is very small. Therefore, since the value of ΨJT is also
environment to each other to select a product with better heat
smaller, the error in estimating the junction temperature is
dissipation performance and estimate how many degrees C
small even if there are differences between the JEDEC
the junction temperature will change relatively, it is impossible
environment and the application.
estimate the junction temperature for an application that differs
from the JEDEC environment.
θJA ΨJT
Standard JEDEC Standard JESD51-1, 51-2A JEDEC Standard JESD51-2A
Definition Thermal resistance from junction to ambient: Thermal characteristics parameter indicating the
Thermal resistance from the moving part of the difference between the junction temperature and
semiconductor device to the natural convection (still the temperature at the center of the outer surface of
air) environment surrounding the device the component package divided by the power
applied to the component
Ambient Measured with a thermocouple in the position
temperature specified by JESD51-2A
measurement
method
Package Measurement of the center of the package surface
temperature with a thermocouple
measurement
method
Measurement Thermal resistance including the board, when heat Thermal characteristics including the board, when
environment is dissipated from the junction in the three- heat is dissipated from the junction in the 3-
dimensional direction with the device mounted on a dimensional direction with the device mounted on a
(Figure 10)
board conforming to JEDEC board conforming to JEDEC
Applications • Comparing θJA between different products to • Thermal design of SMD applications
select one with better heat dissipation
• Measuring the temperature of the package
performance
surface and estimating the junction temperature
• Comparing θJA between different products to
roughly estimate how many degrees C the junction
temperature will change relative to each other
Junction Not possible 𝑇 =𝛹 ×𝑃 +𝑇
𝐽 𝐽𝑇 𝐷 𝑇
temperature
estimation 𝑃 𝐷 : Power loss [W]
𝑇 : Temperature at the center of the package
𝑇
surface [°C]
Thermal
conduction
Ψ J
JT
Convection
Radiation
θ
JA T
Figure 10. Schematic diagram of the measurement environment for θJA and ΨJT
5/6

References
[1] JESD51-3, Low Effective Thermal Conductivity Test Board for Leaded Surface Mount Packages, 1996
[2] JESD51-5, Extension of Thermal Test Board Standards for Packages with Direct Thermal Attachment Mechanisms, 1999
[3] JESD51-7, High Effective Thermal Conductivity Test Board for Leaded Surface Mount Packages, 1999
[4] Application Note “HTSOP-J8 Package Thermal Resistance Information” page 3 to 4, ROHM CO., LTD., 2022
[5] JESD51-1, Integrated Circuits Thermal Measurement Method – Electrical Test Method (Single Semiconductor Device),
December 1995
[6] JESD51-2A, Integrated Circuits Thermal Test Method Environmental Conditions - Natural Convection (Still Air), January 2008
[7] Application Note “Notes for Temperature Measurement Using Thermocouples” , ROHM CO., LTD., 2020
6/6

Notice
Notes
1) The information contained herein is subject to change without notice.
2) Before you use our Products, please contact our sales representativeand verify the latest specifica-
tions :
3) Although ROHM is continuously working to improve product reliability and quality, semicon-
ductors can break down and malfunction due to various factors.
Therefore, in order to prevent personal injury or fire arising from failure, please take safety
measures such as complying with the derating characteristics, implementing redundant and
fire prevention designs, and utilizing backups and fail-safe procedures. ROHM shall have no
responsibility for any damages arising out of the use of our Poducts beyond the rating specified by
ROHM.
4) Examples of application circuits, circuit constants and any other information contained herein are
provided only to illustrate the standard usage and operations of the Products. The peripheral
conditions must be taken into account when designing circuits for mass production.
5) The technical information specified herein is intended only to show the typical functions of and
examples of application circuits for the Products. ROHM does not grant you, explicitly or implicitly,
any license to use or exercise intellectual property or other rights held by ROHM or any other
parties. ROHM shall have no responsibility whatsoever for any dispute arising out of the use of
such technical information.
6) The Products specified in this document are not designed to be radiation tolerant.
7) For use of our Products in applications requiring a high degree of reliability (as exemplified
below), please contact and consult with a ROHM representative : transportation equipment (i.e.
cars, ships, trains), primary communication equipment, traffic lights, fire/crime prevention, safety
equipment, medical systems, servers, solar cells, and power transmission systems.
8) Do not use our Products in applications requiring extremely high reliability, such as aerospace
equipment, nuclear power control systems, and submarine repeaters.
9) ROHM shall have no responsibility for any damages or injury arising from non-compliance with
the recommended usage conditions and specifications contained herein.
10) ROHM has used reasonable care to ensure the accuracy of the information contained in this
document. However, ROHM does not warrants that such information is error-free, and ROHM
shall have no responsibility for any damages arising from any inaccuracy or misprint of such
information.
11) Please use the Products in accordance with any applicable environmental laws and regulations,
such as the RoHS Directive. For more details, including RoHS compatibility, please contact a
ROHM sales office. ROHM shall have no responsibility for any damages or losses resulting
non-compliance with any applicable laws or regulations.
12) When providing our Products and technologies contained in this document to other countries,
you must abide by the procedures and provisions stipulated in all applicable export laws and
regulations, including without limitation the US Export Administration Regulations and the Foreign
Exchange and Foreign Trade Act.
13) This document, in part or in whole, may not be reprinted or reproduced without prior consent of
ROHM.
Thank you for your accessing to ROHM product informations.
More detail product informations and catalogs are available, please contact us.
ROHM Customer Support System
http://www.rohm.com/contact/
www.rohm.com
R1102B
© 2016 ROHM Co., Ltd. All rights reserved.