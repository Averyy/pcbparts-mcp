---
source: "Skyworks AN583 -- Safety Considerations and Layout Recommendations for Digital Isolators"
url: "https://www.skyworksinc.com/-/media/SkyWorks/SL/documents/public/application-notes/AN583.pdf"
format: "PDF 11pp"
method: "pdfplumber"
extracted: 2026-03-02
chars: 22365
---

AN583: Safety Considerations and Layout
Recommendations for Digital Isolators
This application note details the creepage and clearance requirements of an isolator
type component, such as a digital isolator, used to provide protection from electric
KEY POINTS
shock. It also details layout recommendations to enhance a design's robustness and
ensure compliance with end safety standards.
• Safety Considerations
To ensure safety in end-user applications, high voltage circuits (i.e., circuits with >30 • Key Term Definitions
VAC) must be physically separated from the safety extra-low voltage circuits (SELV is a • Guidelines for Proper Creepage and
circuit with <30 VAC) by a certain distance (creepage/clearance). If a component, such Clearance
as a digital isolator, straddles this isolation barrier, it must meet those creepage/clear- • Layout Recommendations
ance requirements and provide a sufficient high-voltage breakdown protection rating
(commonly referred to as working voltage protection). Refer to the end-system specifi-
cation (61010-1, 60950-1, 60601-1, etc.) requirements before starting any design that
uses a digital isolator. These standards dictate both the working voltage requirement
and the creepage/clearance distance spacing necessary to deem an end product safe
for end-customer use.
Skyworks Solutions, Inc. • Phone [781] 376-3000 • Fax [781] 376-3100 • sales@skyworksinc.com • www.skyworksinc.com
1 Rev. 0.3 • Skyworks Proprietary Information • Products and Product Information are Subject to Change Without Notice • December 10, 2021 1

AN583: Safety Considerations and Layout Recommendations for Digital Isolators • Key Term Definitions
1. Key Term Definitions
The following are key terms that should be understood before reading this application note:
Safety Extra-Low-Voltage—A voltage less than 30 VRMS (60 VDC)
Hazardous—A voltage greater than 30 VRMS (60 VDC)
Basic Insulation—A single-level of protection against electric shock. See Table 2.
Reinforced/Double Insulation—Two-levels of protection against electric shock. See Table 2. Rated (Proof) Isolation Voltage—The
maximum voltage an isolation barrier is rated to withstand. This is typically 2500, 3750, or 5000 VRMS for 1 minute.
Production Isolation Test Voltage—The voltage to which an isolation component manufacturer must test the component in order to
be compliant with a given standard. This test voltage is typically 1.2x the Rated Isolation Voltage for a test duration of 1 second. Each
standard has slightly different test voltage requirements. The most strenuous and inclusive requirement is chosen for this test.
Creepage—The shortest path between two conductive parts measured along the surface of the insulation.
Figure 1.1. Creepage
Clearance—The shortest path that an arc may travel through air.
Figure 1.2. Clearance
Time-Dependent Dielectric Breakdown—The amount of time it takes a component's isolation barrier to fail for a given voltage. In
general, the lower the voltage, the exponentially longer the time a safety component can survive.
Pollution Degree—The end environment in which an end system is used. Table 1 summarizes the different pollution degrees.
Skyworks Solutions digital isolators are rated to Pollution Degree 2.
• Pollution Degree 1: No pollution or only dry, nonconductive pollution occurs. The pollution has no effect.
• Pollution Degree 2: Normally, only nonconductive pollution occurs. Temporary conductivity caused by condensation is to be expec-
ted.
• Pollution Degree 3: Conductive pollution or dry nonconductive pollution that becomes conductive due to condensation. This is to be
found in industrial environments or construction sites (harsh environments).
• Pollution Degree 4: The pollution generates persistent conductivity caused by conductive dust, rain, or snow. The following table lists
pollution degree definitions.
Skyworks Solutions, Inc. • Phone [781] 376-3000 • Fax [781] 376-3100 • sales@skyworksinc.com • www.skyworksinc.com
2 Rev. 0.3 • Skyworks Proprietary Information • Products and Product Information are Subject to Change Without Notice • December 10, 2021 2

AN583: Safety Considerations and Layout Recommendations for Digital Isolators • Key Term Definitions
Table 1.1. Pollution Degree Definitions
Pollution Degree 1 Pollution Degree 2 Pollution Degree 3 Pollution Degree 4
Clean room environments Equipment being Electrical equipment in industrial Electrical equipment for outdoor
and farming areas use
evaluated at 60950
Inside sealed components Laboratories Unheated rooms
Test stations Boiler rooms
Office environments
The following table details some typical differences between basic and reinforced isolation requirements. See the specific standard for
your design, as creepage requirements will vary from one standard to another. The numbers listed below provide a good rule of thumb
for most standards.
Table 1.2. Typical Differences between Basic and Reinforced Isolation Requirements
Insulation Type Creepage/Clearance Proof (Rated) Test Production Test
Basic 3.2 mm 2500 V (1 min) 3000 V (1 sec)
RMS RMS
Reinforced/Double 6.4 mm 5000 V (1 min) 6000 V (1 sec)
RMS RMS
Skyworks Solutions, Inc. • Phone [781] 376-3000 • Fax [781] 376-3100 • sales@skyworksinc.com • www.skyworksinc.com
3 Rev. 0.3 • Skyworks Proprietary Information • Products and Product Information are Subject to Change Without Notice • December 10, 2021 3

AN583: Safety Considerations and Layout Recommendations for Digital Isolators • Selecting Adequate Creepage and Clearance for a Given Specifica-
tion
2. Selecting Adequate Creepage and Clearance for a Given Specification
The amount of creepage distance required for a given system depends on the end system’s certification standard. In general, this
distance is dictated by the Pollution Degree of the environment in which the system will be used and the highest working voltage
present in the system. For example, the IEC60950-1 regulates the requirements for Telecom Equipment, and the IEC61010-1 regulates
the requirements for Industrial and Test Equipment. The table below lists the Basic Insulation creepage requirements for IEC60950-1.
From this table, one can see that the Basic Insulation creepage distance required for a Pollution Degree 2, Material Group IIIa/b (the
most common material group), 250 V , system is 2.5 mm. A component whose package provides less is not adequate for the
RMS
design.
Table 2.1. IEC60950-1 MAINS Creepage Requirements
Working Voltage Functional, Basic, and Supplementary Insulation
(VRMS or VDC) Pollution Degree 2
Material Group
I II IIIa or IIIb
<50 0.6 0.9 1.2
100 0.7 1.0 1.4
150 0.8 1.1 1.6
250 1.3 1.8 2.5
400 2.0 2.8 4.0
Note:
1.The data in this table is for basic isolation. Double all the distances for reinforced insulation. Dimensions are in millimeters.
2.1 Creepage Distance Provided by Skyworks Packages
Skyworks offers numerous packages with various creepage distances. The following table details these differences.
Table 2.2. Typical Creepage Distances Offered by Skyworks Packages
Package Nominal Creepage (mm) Creepage in Air Per IEC60112 (mm)
QSOP-16 3.6 3.6
SOIC-8 4.01 3.9
NB SOIC-16 4.01 3.9
WB SOIC-16 8 7.6
DIP8 7 7
SDIP6 8.3 8.3
LGA8 10 10
For most of the packages listed above, the Nominal creepage and the creepage in air as determined by IEC60112 (the standard that
defines how to measure creepage) is the same. However, it should be noted that the JEDEC standard, 16 lead WB SOIC package has
7.6 mm of creepage. This is less than the nominal 8 mm of creepage listed due to the metal tabs left on the sides of the package during
manufacturing. This 7.6 mm is adequate for most applications; however, some 220–250 VAC medical and industrial systems require 8
mm to ensure safety. All isolation suppliers using typical, non-custom, JEDEC standard SOIC packages have this same restriction on
creepage (note that this condition is similar for the other SOIC packages listed above). To achieve the 4.01 and 8 mm of creepage for
these JEDEC SOIC packages, conformal coating is required to cover the metal tabs.
Skyworks Solutions, Inc. • Phone [781] 376-3000 • Fax [781] 376-3100 • sales@skyworksinc.com • www.skyworksinc.com
4 Rev. 0.3 • Skyworks Proprietary Information • Products and Product Information are Subject to Change Without Notice • December 10, 2021 4

AN583: Safety Considerations and Layout Recommendations for Digital Isolators • Selecting Adequate Creepage and Clearance for a Given Specifica-
2.1.1 Using PTI and CTI to Reduce Creepage Distance Requirements
The required creepage distance can be reduced if an isolation component has been qualified to a higher proof tracking index (PTI)
rating or comparative tracking index (CTI) rating. In many cases, the distance can be cut in half if the component is rated to Material
Group I instead of Material Group IIIa or IIIb (the most common ratings for components). For example, from Table 2.1 IEC60950-1
MAINS Creepage Requirements on page 4, the end user can reduce the required creepage from 4 to 2 mm (for a 400 V based
system) if the component is rated to material group I. Skyworks Solutions isolator packages are all rated to Material Group I and
Pollution Degree 2. Additional certification paperwork might be necessary to accommodate this creepage distance reduction. IEC60112
details the CTI/PTI testing standard.
2.1.2 Using Grooves to Extend Effective Creepage Distance for a Given Package
PCB grooves can be used to increase the creepage distance for a given package in a given system. See the figure below; clearance is
not affected since it is line-of-sight. When using grooves, ensure that the groove does not weaken the PCB to the point that the board
fails standard mechanical tests.
Figure 2.1. PCB Grooves Used to Increase Creepage Distance
Skyworks Solutions, Inc. • Phone [781] 376-3000 • Fax [781] 376-3100 • sales@skyworksinc.com • www.skyworksinc.com
5 Rev. 0.3 • Skyworks Proprietary Information • Products and Product Information are Subject to Change Without Notice • December 10, 2021 5

AN583: Safety Considerations and Layout Recommendations for Digital Isolators • Selecting Adequate Creepage and Clearance for a Given Specifica-
2.2 Ensuring an Adequate Withstand Rating
The second requirement of a safety component is its voltage withstand rating. Every safety component has a Time Dependent
Dielectric breakdown profile. Time-dependent breakdown is unique to each component. Manufacturers of safety components usually
provide these profiles in their data sheets. The following figures illustrate the profiles for the Si86xxxx family.
Figure 2.2. Si86xxxB Time-Dependent Dielectric Breakdown
Figure 2.3. Si86xxxD Time-Dependent Dielectric Breakdown
Skyworks Solutions, Inc. • Phone [781] 376-3000 • Fax [781] 376-3100 • sales@skyworksinc.com • www.skyworksinc.com
6 Rev. 0.3 • Skyworks Proprietary Information • Products and Product Information are Subject to Change Without Notice • December 10, 2021 6

AN583: Safety Considerations and Layout Recommendations for Digital Isolators • Selecting Adequate Creepage and Clearance for a Given Specifica-
Table 2.3. Test Voltages for Electric Strength Tests for Each Working Voltage Range
Grade of Insulation Working Voltage
<184 Vpk or dc 184 < U < 354 Vpk or dc 354 < U < 1414 Vpk or dc
Test Voltage
Basic (V ) 1000 1500 3000
Reinforced (V )1 2000 (3200) 3000 (4800) 3000 (4800)
Note:
1.For isolation components with non-homogeneous construction, such as the Si8xxx devices, reinforced insulation requires a 1.6x
multiplier.
2.3 Choosing a Component with Adequate Creepage
Assume a designer is designing telecom equipment (e.g., a blade server) whose electronic board is used in a Pollution Degree 2
environment. Also assume the server's control board powers from the main line and is universally powered (up to 250 VAC).
Q: What type of isolation components are required by IEC60950-1 for this system?
A: The answer is found by going to the IEC60950-1 specification. For convenience, refer to Table 2.1 IEC60950-1 MAINS Creepage
Requirements on page 4 and Table 2.3 Test Voltages for Electric Strength Tests for Each Working Voltage Range on page 7 in this
document. From Table 2.1 IEC60950-1 MAINS Creepage Requirements on page 4, the component must have a creepage of 5 mm
(assumes Material group IIIa; only 2.6 mm is required for a component in Material group I). Also, from Table 2.3 Test Voltages for
Electric Strength Tests for Each Working Voltage Range on page 7, the component must pass a 4800 V 1–minute qualification test
and be rated for 250 V reinforced insulation. A glance at these tables may suggest that the requirements are larger than necessary.
However, since the system is powered from a 250 V mains power source, reinforced insulation is in fact required. This reinforced
insulation requirement increases the overall required creepage distance and 1–minute sustained voltage requirements of the system as
dictated by IEC60950-1. From Table 2.2 Typical Creepage Distances Offered by Skyworks Packages on page 4, one can see that the
WB SOIC-16, DIP8, SDIP6 or LGA8 package could be used for this application. CTI/PTI documentation would need to be submitted if a
smaller package was necessary.
Skyworks Solutions, Inc. • Phone [781] 376-3000 • Fax [781] 376-3100 • sales@skyworksinc.com • www.skyworksinc.com
7 Rev. 0.3 • Skyworks Proprietary Information • Products and Product Information are Subject to Change Without Notice • December 10, 2021 7

AN583: Safety Considerations and Layout Recommendations for Digital Isolators • Layout Recommendations
3. Layout Recommendations
The following guidelines can be used to enhance the layout design of systems using digital isolators. Refer to the family data sheets for
more details concerning specific devices.
3.1 PCB Material
For safety reasons, it is recommended that standard epoxy-glass PCB material Flame Retardant 4 (FR-4) be used in all designs
since it meets the requirements of Underwriters Laboratories UL94-V0. Cheaper alternatives have higher dielectric losses at high
frequencies, absorb more moisture, and provide less strength and stiffness. Moreover, FR-4 exhibits flammability characteristics that
are self-extinguishing. Assuming a rise/fall time >1 ns, trace lengths up to 10 inches can be supported for data rate of 150 Mbps.
3.1.1 Use Four-Layer Designs
Four layers of metal are required to achieve a low EMI PCB design.
• To avoid issues caused by stray impedances from vias, route the high-speed traces on the top layer.
• To establish controlled impedances and provide low-inductance current return paths for high-speed signals, place a solid ground
plane next to the high-speed signal layer.
• To increase high-frequency bypass capacitance, place the power plane next to the ground.
• Since slower speed signals radiate less energy, route these signals on the bottom layer. These signals usually have fewer critical
layout requirements when EMI is an issue.
The above order can be reversed if it facilitates the design.
3.1.2 Use Conformal Coating to Reduce Creepage Requirements
As discussed earlier, a higher CTI/PTI rated device reduces the creepage/clearance requirements for most end systems. Conformal
coating is also an alternative to higher CTI/PTI and grooves can be used to reduce creepage/clearance requirements. Since the typical
voltage breakdown in air is approximately 1100 V/mm, a 4 mm creepage rate component (not including the internal barrier's isolation)
will break (arc) down at approximately 4400 V. The breakdown of a component with conformal coating is significantly higher than that of
air (usually 5x). Refer to standards requirements when supplementary isolation, such as conformal coating, is used.
3.1.3 Use these Routing Guidelines
Use the following guidelines to avoid noise pickup and lower EMI. See the reference section for additional layout recommendations.
1.Use appropriate bypass capacitors (usually 0.1 µF, 1 µF) between VDD and GND. The capacitors should be placed as close as
possible to the package. See the data sheet for exact details.
2.Place bulk capacitors (10 µF) close to power components.
3.Use 45° bends instead of right-angle (90°) bends for signals. This enhances impedance matching.
4.To reduce inductances, avoid changing layers with signals.
5.Use power and ground planes to control impedances and minimize noise from power components.
6.Use short trace lengths between the isolator and connecting circuits.
7.To enhance the robustness of a design, it is further recommended that the user also add 1 µF bypass capacitors and include 100
W resistors in series with the inputs and outputs if the system is excessively noisy.
Skyworks Solutions, Inc. • Phone [781] 376-3000 • Fax [781] 376-3100 • sales@skyworksinc.com • www.skyworksinc.com
8 Rev. 0.3 • Skyworks Proprietary Information • Products and Product Information are Subject to Change Without Notice • December 10, 2021 8

AN583: Safety Considerations and Layout Recommendations for Digital Isolators • References
4. References
• High-speed Digital Design, Johnson/Graham, 1993.
• Eliminating the Myths About Printed Circuit Board Power/ground Plane Decoupling, Archambeault, 2001.
• Noise Reduction Techniques in Electronic Systems, Ott, 1988.
Skyworks Solutions, Inc. • Phone [781] 376-3000 • Fax [781] 376-3100 • sales@skyworksinc.com • www.skyworksinc.com
9 Rev. 0.3 • Skyworks Proprietary Information • Products and Product Information are Subject to Change Without Notice • December 10, 2021 9

AN583: Safety Considerations and Layout Recommendations for Digital Isolators • Document Change List
5. Document Change List
Revision 0.1 to Revision 0.2
• Rewrote "4. Selecting Adequate Creepage and Clearance for a Given Specification" on page 3.
• Removed “5.1. Supply Pins”, “5.2. Input Pin”, and “5.3. Output Pin Termination” subsections from "5. Layout Recommendations" on
page 6.
Revision 0.2 to Revision 0.3
• Updated 2.2 Ensuring an Adequate Withstand Rating.
• Updated Figure 2.2 Si86xxxB Time-Dependent Dielectric Breakdown on page 6.
• Added Figure 2.3 Si86xxxD Time-Dependent Dielectric Breakdown on page 6.
• Updated Table 2.3 Test Voltages for Electric Strength Tests for Each Working Voltage Range on page 7.
Skyworks Solutions, Inc. • Phone [781] 376-3000 • Fax [781] 376-3100 • sales@skyworksinc.com • www.skyworksinc.com
10 Rev. 0.3 • Skyworks Proprietary Information • Products and Product Information are Subject to Change Without Notice • December 10, 2021 10

Connecting Everyone
and Everything,
All the Time
Portfolio Quality Support & Resources
www.skyworksinc.com www.skyworksinc.com/quality www.skyworksinc.com/support
Copyright © 2021 Skyworks Solutions, Inc. All Rights Reserved.
Information in this document is provided in connection with Skyworks Solutions, Inc. (“Skyworks”) products or services. These materials, including the
information contained herein, are provided by Skyworks as a service to its customers and may be used for informational purposes only by the customer.
Skyworks assumes no responsibility for errors or omissions in these materials or the information contained herein. Skyworks may change its documentation,
products, services, specifications or product descriptions at any time, without notice. Skyworks makes no commitment to update the materials or
information and shall have no responsibility whatsoever for conflicts, incompatibilities, or other difficulties arising from any future changes.
No license, whether express, implied, by estoppel or otherwise, is granted to any intellectual property rights by this document. Skyworks assumes no liability
for any materials, products or information provided hereunder, including the sale, distribution, reproduction or use of Skyworks products, information or
materials, except as may be provided in Skyworks’ Terms and Conditions of Sale.
THE MATERIALS, PRODUCTS AND INFORMATION ARE PROVIDED “AS IS” WITHOUT WARRANTY OF ANY KIND, WHETHER EXPRESS, IMPLIED, STATUTORY, OR
OTHERWISE, INCLUDING FITNESS FOR A PARTICULAR PURPOSE OR USE, MERCHANTABILITY, PERFORMANCE, QUALITY OR NON-INFRINGEMENT OF ANY
INTELLECTUAL PROPERTY RIGHT; ALL SUCH WARRANTIES ARE HEREBY EXPRESSLY DISCLAIMED. SKYWORKS DOES NOT WARRANT THE ACCURACY OR
COMPLETENESS OF THE INFORMATION, TEXT, GRAPHICS OR OTHER ITEMS CONTAINED WITHIN THESE MATERIALS. SKYWORKS SHALL NOT BE LIABLE FOR
ANY DAMAGES, INCLUDING BUT NOT LIMITED TO ANY SPECIAL, INDIRECT, INCIDENTAL, STATUTORY, OR CONSEQUENTIAL DAMAGES, INCLUDING WITHOUT
LIMITATION, LOST REVENUES OR LOST PROFITS THAT MAY RESULT FROM THE USE OF THE MATERIALS OR INFORMATION, WHETHER OR NOT THE RECIPIENT
OF MATERIALS HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
Skyworks products are not intended for use in medical, lifesaving or life-sustaining applications, or other equipment in which the failure of the Skyworks
products could lead to personal injury, death, physical or environmental damage. Skyworks customers using or selling Skyworks products for use in such
applications do so at their own risk and agree to fully indemnify Skyworks for any damages resulting from such improper use or sale.
Customers are responsible for their products and applications using Skyworks products, which may deviate from published specifications as a result of
design defects, errors, or operation of products outside of published parameters or design specifications. Customers should include design and operating
safeguards to minimize these and other risks. Skyworks assumes no liability for applications assistance, customer product design, or damage to any
equipment resulting from the use of Skyworks products outside of Skyworks’ published specifications or parameters.
Skyworks, the Skyworks symbol, Sky5®, SkyOne®, SkyBlue™, Skyworks Green™, Clockbuilder®, DSPLL®, ISOmodem®, ProSLIC®, and SiPHY® are trademarks or
registered trademarks of Skyworks Solutions, Inc. or its subsidiaries in the United States and other countries. Third-party brands and names are for
identification purposes only and are the property of their respective owners. Additional information, including relevant terms and conditions, posted at
www.skyworksinc.com, are incorporated by reference.
Skyworks Solutions, Inc. | Nasdaq: SWKS | sales@skyworksinc.com | www.skyworksinc.com
USA: 781-376-3000 | Asia: 886-2-2735 0399 | Europe: 33 (0)1 43548540 |