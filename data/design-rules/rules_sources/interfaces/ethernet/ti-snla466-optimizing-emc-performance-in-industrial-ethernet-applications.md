---
source: "TI SNLA466 -- Optimizing EMC Performance in Industrial Ethernet Applications"
url: "https://www.ti.com/document-viewer/lit/html/SNLA466"
format: "HTML"
method: "pdfplumber"
extracted: 2026-02-16
chars: 77576
---

Application Note
Optimizing EMC Performance in Industrial Ethernet
Application
Hillman Lin
ABSTRACT
This article provides an overview to each EMC/EMI test, debug procedures if these tests fail, and guidance for
optimizing schematic and layout design to improve EMI/EMC test performance.
Table of Contents
1 Abbreviation............................................................................................................................................................................2
2 Introduction.............................................................................................................................................................................2
3 EMC Emission.........................................................................................................................................................................4
3.1 Radiated Emission.............................................................................................................................................................5
3.2 Conducted Emission..........................................................................................................................................................6
3.3 Debug Procedure on EMC Emission.................................................................................................................................7
4 EMC Immunity Test...............................................................................................................................................................10
4.1 EMI Passing Criteria........................................................................................................................................................10
4.2 Common EMI Knowledge.................................................................................................................................................11
4.3 IEC61000 4-2 ESD...........................................................................................................................................................12
4.4 IEC 61000 4-3 RI.............................................................................................................................................................16
4.5 IEC 61000 4-4 EFT..........................................................................................................................................................18
4.6 IEC 61000 4-5 Surge.......................................................................................................................................................22
4.7 IEC 61000 4-6 CI.............................................................................................................................................................27
5 Schematic and Layout Recommendation for All EMC, EMI Tests....................................................................................31
5.1 Schematic Recommendation...........................................................................................................................................31
5.2 Layout Recommendation.................................................................................................................................................34
6 Summary...............................................................................................................................................................................42
7 References............................................................................................................................................................................42
8 Revision History...................................................................................................................................................................43

SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 1

1 Abbreviation
DUT Device Under Test
LP Link Partner
CDN Coupling De-coupling Network
EMC Electromagnetic Compatibility
EMI Electromagnetic Interference
RE Radiated Emission
CE Conducted Emission
ESD Electrostatic Discharge
RI RF Electromagnetic Field Immunity
EFT Electrical Fast Transient
CI Conducted Immunity
MDI Media Dependent Interface
MAC Medium Access Control
CMC Common Mode Choke
2 Introduction
As industrial applications require new topologies to meet faster cycle times, higher throughput, wider bandwidth,
and smaller system architectures, real time Ethernet protocols such as Ethernet/IP, EtherCAT, Profinet, and
so on are introduced to minimize latency. However, the protocols mentioned above all contain daisy chain
architectures in real time systems. Therefore, a higher tolerance and immunity to external noise injected into the
system is required to prevent information loss in the system. As another example, if any information is distorted,
or link is broken in the early stage of the daisy chain network, all the remaining stages in the daisy chain
network are also impacted. For example, if servo motors are connected to each stage of a daisy chain network,
any signal loss in an early stage can prevent the remaining servo motors from functioning until commands
are received from the earlier network stage. As a result, EMC in industrial applications has become a critical
performance criterion for Ethernet.
Figure 2-1. Daisy Chain Topology
Electromagnetic compatibility (EMC) is defined into two main categories: Emission and Immunity
• EMC Emission test is defined when the device or system functions properly without introducing unwanted or
intolerable disturbance to the electromagnetic environment
• EMC Immunity test or Electromagnetic Interference (EMI) is defined as the degradation in performance of
devices due to unwanted disturbances created by the electromagnetic environment
2 Optimizing EMC Performance in Industrial Ethernet Application SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024

In real time applications, there is always noise coupling to and from surrounding systems. This noise coupling is
typically separated into four categories:
• Conductive or Common impedance coupling
• Inductive or Magnetic coupling
• Capacitive or Electric coupling
• Radiative coupling
Figure 2-2. Noise Coupling Path
Understanding these noise coupling paths in the system or in the test setup are key to debugging EMC issues.
This article provides an overview to each EMC/EMI test, debug procedures if theses fail, and schematic/layout
recommendations to improve remove performance.
SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 3

3 EMC Emission
EMC emission testing is based on the electromagnetic emission from the system to the surroundings. The
most common standard for EMC emission testing is defined by CISPR 32. CISPR 32 is an international radio
disturbance standard for multimedia equipment. CISPR 32 establishes a standard to make sure the protocol and
equipment does not negatively affect the performance of other electronic systems and networks.
The standard defines two classes depending on end-use environments:
• Class B performance, a higher standard in CISPR 32 tests, is the main requirement enclosed systems need
to meet. For example: automotive, robotic, and so on
• Class A performance is a more relaxed requirement compared to Class B performance. Most industrial
applications desire Class A performance
Figure 3-1. CISPR 32 RE Passing Criteria
Figure 3-2. CISPR 32 CE Passing Criteria
EMC emission testing is separated into two main categories:
1. Radiated Emission
2. Conducted Emission
The following section specifies details on test setup, common emission sources in failing cases, and common
debug procedure or designs for both radiated emission and conducted emission tests.
4 Optimizing EMC Performance in Industrial Ethernet Application SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024

3.1 Radiated Emission
Radiated Emission (RE) tests mainly check the non-metallic path noise (air) effect of the device to the
environment. Radiated emissions are measured over the frequency range of 30MHz to 6GHz.
Note
Ethernet PHY application normally focus on 30MHz to 1GHz frequency region
3.1.1 Test Setup for Radiated Emission Test
• Distance between DUT and Antenna is 3m/10m away
– The passing emission threshold depends on distance tested
– CISPR 32 supports both 3m and 10m setup with various passing threshold level
– CISPR 22 only supports 10m for the frequency less than 1GHz and 3m for frequency greater than 1GHz
• DUT and LP separated by 10cm
• DUT and LP are 80cm above earth ground on an insulating surface
• Various antennas are required for the full frequency range
Figure 3-3. RE Test Setup
Please refer to CISPR 32 standard for further information on test setup.
3.1.2 Main Radiated Emission Sources
1. Clock source
• Crystal or Oscillator
• Reference clock on MAC/MDI interface
• Output clock of Ethernet PHY or other ICs
2. Signal path
• Exposed pad on the signal path
• Large component size on the signal path
• Long signal path
• Number of vias on the signal path
3. Cable stacking and looping
• Ethernet cables stacked or looped close to each other
4. Cable type
• Shielded cable is highly recommended as its ground shield covers the twisted pair to prevent radiation
from the cable
SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 5

3.2 Conducted Emission
Conductive Emission (CE) tests are mainly checking the metallic path (cable) noise effect of the device to the
environment. Conductive Emission is measured over 0.1MHz to 30MHz.
3.2.1 Test Setup for Conducted Emission Test
• DUT and LP separated by 10cm
• DUT and LP are 80cm above earth ground on an insulating surface
• LISN is 80cm away from DUT and LP
Figure 3-4. CE Test Setup
3.2.2 Main Conducted Emission Sources
1. Signal and cable path
• Non-MDI signal traces and clock sources near the connector or MDI lines
• Interconnection distance between the MDI lines is too close
– Interconnection distance is the distance between differential pair
• External noise sources near cable
2. Cable type mismatch
• Mismatch between DUT and LP cable type
• Mismatch between DUT/LP and CDN cable type
6 Optimizing EMC Performance in Industrial Ethernet Application SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024

3.3 Debug Procedure on EMC Emission
If the failure is observed during RE/CE testing, please follow the following debug procedure to isolate the root
cause:
3.3.1 General Debug Procedure
1. Follow the test setup for both RE test and CE test.
• At least 10cm distance between DUT and link partner to prevent noise coupling
• No sources of noise between DUT and Link Partner
• Check on background noise and verify background noise is low (RE testing)
• Tested radiated equipment does not need to be present on the test bench (RE testing)
• Power supply needs to always be shielded during the test (RE testing)
• Verify Coupling De-coupling Network (CDN) is properly grounded (CE testing)
– CDN and cable mismatch (especially shielded/unshielded combination) can increase emissions due to
discontinuous ground in the signal lines
2. Cable in CE and RE test recommendation:
• Shielded cable is preferred to reduce emissions by the Ethernet cable
• Prefer no cable loops are present during test. Cable loops can enhance the crosstalk effect and increase
emissions.
• Verify the Ethernet cable is not close to any external noise sources
– Power supply, test equipment, and another electrical device are the possible external noise sources
• If possible, orient the cable farther away from the antenna
• Verify the cables type on both side of Coupling De-coupling Network (CDN) match (CE testing)
• Verify the cable type matches with CDN specification (CE testing)
SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 7

3.3.2 RE Specific Debug
1. General configuration to optimize PHY’s Radiated Emission
• Turn off the CLK_OUT pins or any unused clock sources for both DUT and Link Partner during the test.
TI's PHY CLK_OUT pin can always generate 25MHz or 50MHz clock signal on the pins, resulting in
unnecessary emissions to the surrounding when this feature is not used.
• Turn off TX/RX activity on the DUT/LP's LED pins. Verify none of the LED pins are configured in RX or
TX activity mode. Constant LED blinking during TX/RX activity can result in extra radiated emissions for
lower frequency ranges
2. Remove external factors on cable or link partner on RE test
• Use shorted cable lengths to minimize the effect of the cable
• Change the link partner board to the same as DUT board to factor out the issue on Link Partner board
• Shield both Link Partner and Ethernet cable with earth ground to eliminate the radiation effect of the non
DUT board
• Enable loopback and remove the cable to isolate any radiated emission effects from the cable
If the above suggestions do not resolve RE test failure, the main emission source is likely the DUT.
Reference the points below to investigate and address the root cause with schematic/layout optimizations.
3. Read the failure frequency range on RE test
• If the lower frequency ranges are failing, check the emission due to power rail circuitry, such as the
switching frequency
• If the failing frequency borders 25MHz or the harmonics, the cause is likely the crystal or oscillator path
• If the failing frequency matches the MAC to PHY clock frequency, the cause is likely the MAC interface
path
• If the failing frequency is close to the MDI frequency, the root cause is likely with the MDI interface path
The next section details how to isolate each of the above root causes from the DUT, depending on the failing
frequency range.
4. Isolate other ICs on the DUT board from the PHY to minimize potential effect
• Configure Ethernet PHY in reset stage or low power mode.
– Verify if the main emission are coming from external components on the board
• Disable or power off all other ICs. Only enable PRBS test on DUT and reverse loopback on the Link
Partner side
– This helps isolate noise generated by other components on the DUT board. Packets are still
generated between the two PHYs when PRBS is enabled
• Enable MAC isolation to reduce the effect on the MAC side
– MAC isolation is enabled with register 0x0[10], defined by the IEEE standard
– This helps isolate emission sources between the MAC and PHY interface
5. Use copper tape to isolate the main emission area around the PHY.
• Cover possible emission sources with copper tape to isolate the root cause on DUT board:
– Copper tape needs to be strongly connected to earth ground to absorb most of the emission noise.
If the copper tape is not connected to earth ground properly, the copper tape can act as an antenna
source , further amplifying the signals from the covered area
– Verify there is an insulator between the copper tape and board components to prevent shorting
between the parts
• Use copper tape to cover the area around the PHY’s IC only to see if PHY’s IC are the main radiated
source
• Use copper tape to cover the clock signals (Crystal, Oscillator, RMII clock, MDC, and so on) to see if the
clock sources are the main emission source
– Impedance matching on signal ended clock signal can help with the emission on the clock signal lines.
• Use copper tape to cover the area around MDI lines to see if MDI lines are the main emission source
– Reduce the length of MDI line and prevent the sharp turn on the MDI lines can reduce the emission on
MDI lines
• Use copper tape to cover the area around the MAC to PHY interface trace to see if the MAC interface is
the main emission source
– Slew rate control can help to reduce the emission on the MAC interface
8 Optimizing EMC Performance in Industrial Ethernet Application SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024

– Bury MAC traces can also further reduce the emission on MAC interface
6. Schematic and layout recommendations
• After performing the debug procedures above to isolate the main emission source, please follow the
schematic and layout recommendations to further optimize EMC/EMI performance of the design.
3.3.3 CE Specific Debug
1. Remove external factors on the cable or link partner on CE test
• Change the link partner board to the same as DUT board to factor out possible issues on the Link Partner
board
• Put ferrite beads between CDN and link partner to isolate noise sources from the Link Partner
If the tests above fail, the issue is most likely with the DUT board. Reading the failure frequency range can
provide some indication on the failing region on the board.
2. Read the failure frequency range on CE test
• If CE is failing at lower frequencies, check the power plane/lines to see if they are interfering with the MDI
lines
– If current mode driver PHY is used during the EMC test, ferrite beads need to be added on the power
supply connections to the MDI lines.
– Check the power ground on the board to verify the power ground is clean. Noise from power ground
can couple from the shield to the CDN and worsen CE performance
• If a CE is failing at specific frequencies (for example, 25MHz or the harmonics), verify the other signal or
clock traces near the MDI lines are not causing interference
3. Schematic and layout recommendations
• After performing the previous debug procedure to isolate the main emission source, please follow the
schematic and layout recommendations to further optimize the EMC/EMI performance of the design.
SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 9

4 EMC Immunity Test
EMC Immunity test, also known as Electromagnetic Interference (EMI), is a test standard defining the tolerance
of the device to disturbance in electrical circuits caused by external sources. EMI can cause packet interrupts,
degradation, or even link loss in the system due to surrounding interference. To verify electronic devices are
protected against external noise sources in real time applications, meeting EMI testing requirements is typically
required before device production.
EMI can cause by both humans made and natural source including cellar network, lighting, radio environment,
etc… One of the common humans made examples is ESD noise generate by humans contact with the device
cause a potential disturbance on the electrical device. An example of a natural source is cell phones; calls can
potentially interfere with sensitive equipment on the plane. In Industrial applications, most electronic devices are
directly exposed to the environment. As a result, higher standards of EMI testing are required in non-enclosed
architectures.
The EMI test standard is mainly defined by IEC61000 4-X. IEC61000-4-X is used to test system-level immunity.
Many system designs are specified to comply with one or more of the tests listed within the IEC 61000-4-X
specification. The below sections cover the five most common tests for Ethernet applications:
• ESD (IEC61000 4-2)
• RI (IEC61000 4-3)
• EFT (IEC61000 4-4)
• Surge (IEC61000 4-5)
• CI (IEC61000 4-6)
4.1 EMI Passing Criteria
• Class A performance
– No link loss and/or Packet error and Packet loss during EMI testing
• Class B performance
– Link loss is allowed, but the PHY must recover link without any configuration during EMI tests
• Class C performance
– Link loss is allowed during EMI tests, given the PHY can recover link with a hardware reset or power cycle
Performance (Acceptance Criteria)(1) Description
Class A Module shall continue to operate as intended. No loss of function or performance during
the test
Class B Temporary degradation of performance during the test is accepted. After the test, module
continue to operate as intended without manual intervention
Class C During test, loss of functions accepted, but no destruction of hardware or software. After the
test, the module shall continue to operate as intended automatically, after manual restart, or
power off, or power on. No self-recovery
(1) Table is referenced from IEC standard.
Unlike EMC emission tests, Class A performance for EMI tests has a higher standard than Class B. The
standard is not yet fully defined for Class A performance for Ethernet ESD tests. There are different ways to
define Class A performance in EMI testing, depending on the customer's requirements:
• No link drops during EMI tests for Class A performance
• No link drop and no consecutive packets errors within a defined time interval
In most industrial applications, the absence of link drops during EMI tests is defined as Class A performance.
Real-time applications, however, often have stricter definitions for Class A performance. For example, EtherCAT
application required no more than three consecutive packets errors within 10us during EMI testing are define as
Class A performance.
10 Optimizing EMC Performance in Industrial Ethernet Application SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024

4.2 Common EMI Knowledge
EMI noise can potentially couple to the system in multiple ways: Conductive coupling, Radiative coupling, and
so on. Not the importance to understand the types of noise coupled into the system to effectively debug EMI
failure and improve the design. The following section outlines potential noise coupling sources in each EMI test,
in addition to design suggestions to improve performance.
Some common knowledge and misunderstandings on EMI testing:
Cable type:
Cable types play a significant role in EMI testing. The recommended Ethernet cable type for EMI tests is outlined
below:
• Shielded vs unshielded cable:
– Shielded cables are often necessary for high-speed digital data transmission in electromagnetic
environments. Shielded cables have ground conducted shield wrap around each of the twisted pairs.
With shielded cable, most noise coming from external wires can flow through the ground connected
shield directly to earth ground, instead of coupling into the signal line. Shielded cable also improves the
protection against cross talk, EMI tests, and reduces emissions from the cable.
Figure 4-1. Shielded Cable Example
Double shielded cable have layer of aluminum foil wrap around each pair of cable and a layer of metal
mesh grid which typically have better EMI performance than single shielded cable with only aluminum
foil wrap around each pair of cable.
• CAT 5 vs CAT 6 cable:
– CAT 6 cable is preferred for better EMI performance. Compared to CAT5E, CAT6 has plastic insulation in
the center to isolate each of the twisted pairs. The ground shield around each twisted pair of CAT6 is also
thicker than CAT5E.
• ESD diodes:
– ESD diodes are often useful to protect the device from being damaged during EMI testing. However, ESD
diodes are not a useful approach when Class A performance is required. When the ESD diodes trigger,
the MDI lines can clamp to a certain voltage and result in link drop or packet errors. This results in Class
B performance. When ESD diodes are implemented during normal applications, they act as capacitors
on the MDI lines. If the ESD diodes are not tuned properly, the signal can face attenuation or impedance
mismatch on the MDI lines.
The following sections detail the setup and debug procedure for each EMI test, including possible schematic/
layout suggestions for improved performance.
SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 11

4.3 IEC61000 4-2 ESD
IEC61000-4-2 tests the device's immunity to electrostatic discharge (ESD). This test simulates the effect of
electrostatic discharge in direct or near contact with electronic equipment. There are three different ways of
performing this ESD test:
• Direct contact discharge
• Air contact discharge
• Capacitive coupling discharge
Direct contact discharge test uses an ESD generator tip in contact with the system. In most industrial
applications, the RJ45 or connector shield is exposed to the surrounding system. As the user is likely to touch
this shield and introduce ESD noise in the system, direct contact ESD tests are often performed directly on
the connector shield. However, specific applications require a direct injection on the protocol conducted shield
exposed to the surroundings. The standard does not define the specific point of injection for ESD testing.
Therefore, the point of injection can vary with each application.
Air contact discharge is an indirect coupling discharge to the system. The round tip of the ESD gun acts as
an antenna source, with the noise coupling through air to the system. The noise source from air can couple
anywhere to the system. Therefore, this test is normally done near the PHY.
Capacitive coupling discharge is another indirect coupling discharge to the system, with the ESD noise injected
on the metal plane around the system. In this test, the metal plate acts as an antenna coupling noise into the
system directly. Capacitive coupling discharge tests require the system's orientation to rotate for the ESD test.
ESD test level:
• Level 4: ± 8kV (contact discharge), ±12KV (capacitive coupling), ±15kV (air discharge)
• Level 3: ± 6kV (contact discharge), ±8kV (capacitive coupling), ±12kV (air discharge)
• Level 2: ± 4kV (contact discharge), ±6kV (capacitive coupling), ±8kV (air discharge)
• Level 1: ± 2kV (contact discharge), ±4kV (capacitive coupling), ±6kV (air discharge)
Note: Class A, Class B, and Class C performance depends on system requirements
ESD injection waveform:
ESD testing is the process of injecting a high voltage signal (kV) with nano-second pulse width. This is repeated
10 times, with a one second interval between each ESD strike.
Figure 4-2. ESD test waveform
12 Optimizing EMC Performance in Industrial Ethernet Application SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024

4.3.1 ESD Test Setup
• Discharge network of ESD gun: 150pF and 330ohms
• DUT and LP need to be 80cm above earth ground
• DUT and LP are separated by 10cm
• Insulator sheet is required between DUT and LP to table ground
• 1Mohms connection between table ground and earth ground
Figure 4-3. ESD Test Setup
Further information on ESD test setup and waveform can be found in the IEC 61000 4-2 standard.
4.3.2 Possible Root Cause of Failure
In ESD tests, especially contact discharge tests, most of the ESD noise is directly injected into the connector
shield. As this is also the system's connector ground, ground bounce is a likely effect. This results in common
noise injected into the system. Therefore providing a low impedance path to ground for the ESD noise is crucial
to minimize impact on the signal lines and improve ESD performance.
In both direct and indirect contact ESD tests, there is potential radiative ESD noise coupling to the system.
Therefore, verifying minimum conducted exposure of the signal lines is also crucial for improved ESD
performance.
SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 13

4.3.3 Debug Procedure
If failures are observed during ESD testing, the following debug procedure needs to be used to isolate the root
cause:
4.3.3.1 Follow the Test Setup
• Confirm the earth ground connection of the ESD test setup
– Verify the ESD gun is properly connected to earth ground
– Verify the power supply is connected to earth ground
– Verify table ground is properly connected to earth ground through a 1MOhm termination
• Verify there is a connection between connector ground and earth ground on both DUT and LP boards
– Provide a return path for each ESD strike to flow to earth ground, preventing the connector ground from
capacitively charging. Without a good return path for ESD noise, the connector ground can gain charge
and worsen ESD performance. This is also dangerous for ESD testing, as significant charge can build and
discharge to testers.
Figure 4-4. Low Impedance Ground Path
– If the application prevents the RJ45 shield from connecting to earth ground, the recommendation is to
connect the shield to a metal or conducted case (bigger conducted area) to provide a better radiated path
for ESD noise to flow
• Verify the PHYs, power supply, and Ethernet cable are placed on top of the insulator
– This prevents noise from earth ground directly interfering with the system
• Use a shielded cable for improved EMI performance
– CAT6 cables have better performance than CAT 5E cables
4.3.3.2 Remove External Factors on Cable or Link Partner
• Change the link partner board to the same as DUT board
– This isolates the root cause on the Link Partner side
• Remove the cable, enable loopback (analog loopback is preferred) on the PHY, and perform the ESD test to
eliminate the effect of cable and link partner
– Analog Loopback can connect the Transmitter and Receiver on the MDI side together inside the PHY
and causing the PHY to link to itself. The MDI lines can still receive ESD noise externally after loopback
configuration.
– If a passing result is observed after loopback configuration, the issue is most likely on the cable or link
partner side.
4.3.3.3 Areas to Explore to Improve ESD Performance
If ESD test failures are still seen after performing the above tests, the issue is most likely on the DUT board.
Please follow the following debug procedure and recommendations for each ESD test.
14 Optimizing EMC Performance in Industrial Ethernet Application SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024

4.3.3.3.1 Air or Capacitive Coupling Discharge ESD Recommendations
1. The Rbias pin is the internal current reference for the PHY. If Rbias picks up significant noise, the PHY link
and functionality can be impacted.
• Verify the Rbias resistors are small footprint size (0805/1206 is recommended)
• Verify the Rbias traces are short or buried in an inner layer
2. Short trace length on the clock signal
3. Minimize component and exposed pads on the MDI lines
4.3.3.3.2 Direct Contact Discharge ESD Recommendation
In direct contact ESD tests, ESD noise is injected directly into the ground. This results in common mode noise
injected into the PHY, often resulting in link down. Therefore, reducing the common mode noise injection in
the design is crucial for ESD performance. Please refer to the following recommendations to minimize common
mode noise injection:
• Verify there is ground separation between connector ground and digital ground to prevent any noise injection
directly into the system. This minimizes the ground bounce effect on the system
• No shorted center taps on the transformer
– Reduces the crosstalk
– Reduces chance of mode conversion
– Help with link recovery during the ESD test. Prevent most of the class C performance
• Reduce the affect on Auto-MDIX (conversion between reciever and transmitter) during ESD test
• Discrete magnetics and RJ45 connectors reduce the injection area of ESD noise, improving the transformer
performance during ESD tests
• Optimize the layout of MDI lines to reduce the common noise picked up from surroundings, ground bounce,
and other signals on PCB
– Refer to schematic and layout recommendation
• Optimize PCB connector ground to provide better a better ground path and minimize the coupling effect on
– Refer to schematic and layout recommendation
4.3.3.4 Schematic and Layout Recommendations
After performing the above debug procedure to better isolate the root cause, please follow the schematic and
layout recommendation below to further optimize EMC/EMI performance of the design.
SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 15

4.4 IEC 61000 4-3 RI
IEC 61000-4-3, also known as RF Electromagnetic Field Immunity tests, mainly evaluate the immunity of
electrical equipment when subject to radiated or electromagnetic fields. Most electronic equipment is affected by
electromagnetic radiation in both industrial and automotive applications. RI evaluates device immunity over the
full 80-1000MHz frequency range. There are three basic levels for Ethernet applications:
• Test mode 1: Field strength 1V/m
• Test mode 2: Field strength 3V/m
• Test mode 3: Field strength 10V/m
Class A, Class B, and Class C depends on customer’s requirements
4.4.1 RI Test Setup
• Field generating antenna needs to be 2m away from the DUT
• DUT and LP needs to be placed 80cm above earth ground, on an insulating (non-metallic) table
• Non-testing electrical equipment needs to be properly shielded with earth ground
• Various antennas are required for the full frequency range
• DUT and LP are separated by at least 10cm
Figure 4-5. RI test setup
Further information on RI test setup and waveform can be found in the IEC 61000 4-3 standard.
4.4.2 Possible Root Cause of Failure
• RF Electromagnetic noise disturbance on the clock signal, such as the oscillator or crystal, can result in a
poor clock reference internal to the PHY
• RF Electromagnetic noise disturbance on the Rbias trace or pin, which can result in a noisy current reference
inside the PHY
• RF Electromagnetic noise disturbance on the MAC interface, through exposed conductors or pads, can result
in degraded signal quality between the MAC and PHY
• RF Electromagnetic noise disturbance on the MDI interface, through exposed conductors or pads, can result
in degraded signal quality and link drop for the PHY
16 Optimizing EMC Performance in Industrial Ethernet Application SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024

4.4.3 Debug Procedure
If failures are observed during RI testing, please follow the following debug procedure to isolate the root cause:
4.4.3.1 Follow RI Test Setup
• Aside from the antenna, verify there are no external radiated sources
• Avoid Ethernet cable loops, these can act as an external radiated noise source
• Use Shielded cable for better EMI performance
4.4.3.2 Remove External Factor on Cable or Link Partner
• Change the Link Partner to the same model as DUT and perform a test
• Use a conducted model box or plate that are connected to earth ground for strong shielding on Link Partner
board (isolates effect of the Link Partner)
• Use a conducted model box or plate that are connected to earth ground for strong shielding on the cable and
Link Partner (isolates effect of both cable and Link Partner)
• Disconnect the cable and program the Ethernet PHY into loopback, noting any link down or failure
– Further confirms if DUT is the root cause of RI failure
4.4.3.3 Found out Main Emission Area
After performing the above tests and failures are still observed, the issue is most likely on the DUT boards.
Further action is to use copper tape to cover or shield the area on the boards that is suspected to be most
sensitive. Copper tape needs to be strongly connected to earth ground so that the copper tape can absorb most
of the emission noise. If the copper tape is not connected to earth ground properly, the copper take can act as an
antenna source, amplifying the signals from the covered area:
• Shield around MAC pins to minimize the exposure of MAC pins to the radiation source if the MAC is not used
for testing
• Shield area around the MDI lines with earth ground. If covering MDI lines helps with RI testing performance,
here are some recommendations for further improvement on MDI lines:
– Minimize vias around MDI lines
– Minimize components or exposed pads on the MDI lines
– If possible, bury the MDI traces during RI tests
– Symmetry on the MDI lines
• Shield area around the Rbias pin and traces. If covering Rbias pin and traces helps with RI performance,
please follow the recommendations below:
– Rbias is the reference current to drive the PHY internally. Having the optimal layout around Rbias area
can help with RI testing performance
– Bury Rbias trace in inner layer
– Minimize vias around Rbias
– Minimize Rbias component size
• Shield the oscillator or clock signal to see if that helps with RI performance
• Shield around the power lines to see if that helps with RI performance
4.4.3.4 Schematic and Layout Recommendation
After performing the above debug procedure to further isolate potential issues, please follow the schematic and
layout recommendation to further optimize EMC/EMI performance of the design.
SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 17

4.5 IEC 61000 4-4 EFT
IEC 61000-4-4 is also known as Electrical Fast Transient (EFT) EMC Burst Immunity Test Standard. EFT mainly
tests the immunity of electrical equipment when subjected to fast transient/burst electrical signals. In EFT tests,
a common mode burst signal from a burst generator is sent to the Ethernet cable through capacitive clamping.
This clamping is 1 meter long, directly mounted to earth ground. Unlike ESD testing which has a one second
interval between each pulse, EFT testing has a pulse interval in the microsecond range. Therefore, optimizing
the design for noise discharge is crucial for EFT testing. Shielded and non-shielded cables play a significant
role in EFT performance. Since EFT tests are based on clamping the Ethernet cable using capacitive coupling
equipment, the noise normally injects from the equipment and directly couples inside the Ethernet cable. If the
customer is using a shielded cable, most of the noise can flow to the connector ground instead of the signal
lines, since the shield is normally connected to earth ground. This can significantly improve EFT performance.
Therefore, shielded cables are highly recommended for EMC applications.
In the IEC 61000 4-4 standard, EFT tests also define power port testing. In addition to power EMC tests relying
on not only Ethernet PHY, but also rely on system-level power ICs (Buck converters, LDOs, power switches,
etc). Therefore, this section can focus on how to debug EMC failures in Ethernet applications on signal ports.
There are layout recommendation for the power ports around the PHY side, but the below sections focuses on
signal port EFT testing.
EFT test level:
• Test level 1: ±0.5kV
• Test level 2: ± 1kV
• Test level 3: ±2kV
• Test level 4: ±4kV
Class A, Class B, and Class C depend on customer’s requirement
EFT test waveform:
Two frequency burst signals need to be tested for IEC61000 4-4 EFT:
• 5kHz burst signals have a periodic of 200us for each pulse and total 15ms for the whole burst duration.
• 100kHz burst signal have a period of 10us for each pulse and total 0.75ms for the whole burst duration.
• Both 5kHz and 100kHz have a burst period of 300ms.
Figure 4-6. EFT Test Waveform
18 Optimizing EMC Performance in Industrial Ethernet Application SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024

IEC61000 4-6 EFT standard only require one passing frequency (5kHz or 100kHz). However, most of
the industrial application currently require both 5kHz and 100kHz to consider as passing criteria.
4.5.1 EFT Test Setup
• 1m capacitive coupling clamp shield are connected to earth ground
• Ethernet cable length needs to be greater than 1m
• DUT and LP need to be on an insulating surface, 10cm above earth ground
• DUT and LP need to be at least10cm apart
• Verify the Ethernet cable is placed on top of the insulator
• Ethernet cable is routed straight in the capacitive coupling clamp, without any loops
Figure 4-7. EFT Test Setup
Further information on EFT test setup and waveform can be found in the IEC 61000 4-4 standard.
4.5.2 Possible Root Cause of Failure
• If shielded cable are used for EFT testing, the main concern is the low impedance path between the
connector ground to earth ground. Similar to ESD testing, a good ground path can reduce the potential
ground bounce and reduce the common mode voltage injected into the system.
SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 19

4.5.3 Debug Procedure
If failures are observed during EFT testing, please follow the debug procedure in the following section to isolate
the root cause:
4.5.3.1 Follow EFT Test Setup
• Verify the capacitive coupling clamp shield is properly connected to ground
• Verify the cable is straight without any loop when clamping the cable
• Verify DUT and LP is far away from the capacitive coupling clamp
• Use Shielded cable for better EMI performance
• Similar to ESD test, verify both DUT and Link partner’s connector ground have clean or low impedance return
paths to earth ground
– Most of the noise is directly injected into cable ground during EFT testing. The cables shield ground is in
contact with the RJ45 shield. Therefore, a clean return path between RJ45 shield to earth ground can help
with EFT performance
– If the RJ45 shield is not able to connected to earth ground for the application, connect the shield or
connector ground directly to a metal or conducted case to provide a better path for EMI noise to flow and
radiate outwards
4.5.3.2 Remove External Factor on Cable or Link Parnter
• Change the link partner to the same as DUT and perform EFT test
• Place ferrite beads on the link partner side of cable and note any improvement
– Ferrite need to filter either 5kHz or 100kHz depending on the failure case
• Enable loopback (analog loopback is preferred) on the DUT and perform EFT test
4.5.3.3 Areas to Explore to Improve EFT Performance
If EFT test failures are observed after trying the above steps, the issue is most likely on the DUT side. Similar
to ESD testing, EFT tests can also introduce a burst of common mode noise into the system. Here are some
recommendations to reduce common mode noise and mode conversion on the DUT side:
• Remove bob smith termination on unused pair
– Having a bob smith termination on the unused pair can provide a smaller impedance path to earth ground.
This results in higher common mode noise flow to the unused pair and couples the noise to the used pair
– On the used pair, common mode impedance is generally large due to the common mode choke
• Solid earth ground path on the connector ground of DUT
• Solidground plane under the MDI lines for better impedance matching
• Verify ground isolation is present to reduce ground bounce in the system
– Reduces cross talk
• Discrete magnetic and RJ45 connector reduces the injection area of ESD noise, improving the transformer
• Optimize MDI lines layout to reduce the common mode noise picked up from surroundings, ground bounce,
and other signals on the PCB.
• Optimize PCB connector ground to provide a better ground path and minimize the effect of coupling to the
20 Optimizing EMC Performance in Industrial Ethernet Application SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024

4.5.3.4 Schematic and Layout Recommendation
After performing the previous debug procedure to further isolate possible root causes, please follow the
schematic and layout recommendation to further optimize EMC/EMI performance of the design.
SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 21

4.6 IEC 61000 4-5 Surge
IEC61000-4-5 is also known as the surge immunity test. This mainly tests the immunity of electrical equipment
to a unidirectional surge caused by overvoltage from switching or transients. Unlike ESD and EFT tests, Surge
test involves an injection of high energy or power pulses into the system. These pulses are in the millisecond
range, unlike the nanosecond pulse range for ESD and EFT tests. The surge test is defined by the ability of
electrical equipment to withstand high energy pulses without any damage in the device or system application.
The system needs to recover automatically without any power cycle or hardware reset after the surge injection.
Unlike other EMI tests, where no packet errors or loss is allowed in the system, surge tests mainly look for Class
B performance. For this, packet errors or loss is allowed, but the PHY must automatically recover by itself.
Within IEC61000 4-5 Surge test, there are different tests defined for: Open circuit, Short circuit, and Telecom
ports. Both Open and Short circuit testing is mainly used for power surge tests. There are Section 5 tests that
can improve the power circuitry performance. However, power EMC tests depend on power ICs other than
Ethernet. Therefore, we can mainly focus on the signal ports' surge test.
In signal or telecom port surge tests, there are different test setups for Shielded and Unshielded cables. Here are
the differences between the two test setups:
• For unshielded cable applications, surge test involves a direct noise injection through the coupling decoupling
network (CDN) to the cable. Since unshielded cable does not have ground shield cover around the cable,
there are more possibilities for differential noise injected into the system. As a result, both differential mode
noise injection line to line and common mode noise injection line to ground surge test need to be perform.
• For shielded cable applications, noise is directly injected to the cable shield or earth ground. Therefore,
only "line to ground" need to be tested since most of the noise is acting as common mode noise. Here are
common ways the surge pulse is injected for shielded cable applications:
– Direct surge noise injection cable shield through clamp or direct contact
– CDN has a solid connection to earth ground, with the Ethernet cable connected to each side. The noise is
directly injected on the shield of the CDN
Both types of surge test setups noted above simulate real life scenarios. Compared to shielded cable surge
tests, unshielded cable surge tests normally give worse performance. This is due to the noise directly injecting
into the cable. Again, Surge test is a high power noise injection into the system. Having a potential path for high
power noise to inject into the signal lines is not always recommended for the design. In industrial applications,
most customers use shielded cables. The following section focus on shielded cables or line to ground surge
tests.
Surge Test level:
• Level 1: ±0.5kV (line to line), ±1kV (line to ground)
• Level 2: ±1kV (line to line), ±2kV (line to ground)
• Level 3: ±2kV (line to line), ±4kV (line to ground)
Class A, Class B, and Class C depends on the customer's requirements. Normally, engineers are
looking for Class B performance for surge test. The purpose of surge test is to verify the system is
able to recover automatically after huge energy is injected into the system.
Normally line to ground surge test have higher passing level than line to line surge test.
22 Optimizing EMC Performance in Industrial Ethernet Application SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024

Surge waveform:
For Signal and Telecom port surge tests, the pulse width is 1.4ms with 10us Front time. The pulse is a
high-power pulse injected into the system:
Figure 4-8. Surge Test Waveform
SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 23

4.6.1 Surge Test Setup
• DUT and LP need to be at least 10cm apart
• Verify the Ethernet cable is placed on top of the insulator
• Verify sure the surge injection point is properly connected to the shield
• Verify there are no discontinuities on the cable shield
Figure 4-9. Surge Test Setup for Direct Noise Injection on Cable Shield
Figure 4-10. Surge Test Setup on Noise Injection on CDN
Further details on the Surge test setup and injection waveform and test setup can be found in the IEC
41000 4-5 standard.
4.6.2 Possible Root Cause of Failure
• The surge test involves multiple high-power noise injections to the signal lines. This high-power injection
charges up the PHY IC's internal circuitry, resulting clamp stages within the PHY. Including a good path for
common mode noise to discharge from the signal lines to the connector ground is recommended to improve
the surge test performance. Good isolation between the connector/system, as well as a good discharge path
from connector to earth ground is crucial for surge test performance with shielded cables.
24 Optimizing EMC Performance in Industrial Ethernet Application SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024

4.6.3 Debug Procedure
If failures are observed during surge tests, please follow the debug procedure in the following topic to isolate the
root cause:
4.6.3.1 Follow Surge Test Setup
Shielded cable surge test with direct contact on cable shield:
• Verify the surge injection point is properly connected to the shield
• Verify there is no discontinuity on the shield of the cables
• Point of noise injection needs to be at least 10cm away from the DUT and LP
Shielded cable surge test with CDN connector:
• Verify both side of the Ethernet cable matches
• Verify the CDN and Ethernet cable type match
– Using unshielded cable CDN with shielded cable mismatch can potentially increase reflective noise due to
the discontinuous ground in the signal lines.
– Using unshielded cable CDN with shielded cable can also increase the impedance of the return path
between signal lines and earth ground which can increase the noise ratio done by surge test
• Verify the Noise injection CDN is properly connected to the earth ground
• Verify both DUT and LP are away from the CDN connector
• Longer cable is preferred on the link partner side
– Longer cable on the link partner side can reduce some effect of surge noise done to the link partner
General test setup procedure:
• Verify surge noise injection cable is straight, without loops
• Verify the Ethernet cable is placed properly on the insulator, and does not contact earth ground
• Verify the Ethernet cable is placed away from any noise sources
• Add a good return path from the RJ45 shield to earth ground
• Verify there are no loops on the Ethernet cable to reduce cross talk
• Use shielded cable for better EMI performance:
– Having a shielded cable is better than non-shielded cable, as the shielded cable provides a path from MDI
lines to ground through cable shield or decoupling capacitors inside shielded cable CDN
– For non-shielded cables, all noise can go directly to signal lines with minimal or no noise coupling to
ground
4.6.3.2 Remove External Factor on Cable or Link Partner
• Change the link partner to the same as DUT and perform a test
• Add low frequency ferrite beads on the link partner side
• Remove the cable on link partner side and write loopback on the DUT. Perform the surge test after DUT is
configured for loopback.
4.6.3.3 Area to Explore to Improve Surge Performance
If failures are still observed after trying the debug procedure above, the issue is most likely on the DUT side.
Most test criteria for the surge test verify the PHY is able to self-recover after a huge power injection. Reducing
the noise injection to the system is the main objective. Here are some recommendations to improve the design
on the DUT side:
• Verify there is ground separation between connector ground and digital ground to prevent huge energy
injected to the system ground
– Reduces crosstalk
• Discrete magnetic and RJ45 connector reduces the injection area of ESD noise, improving the transformer
• Power supply ICs and power plane needs to be separated from the connector ground
– Prevents any disturbance on the power source due to the ground bounced
SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 25

• Optimize layout of MDI lines to reduce the common mode noise picked up from the surroundings, ground
bounce, and other signals on the PCB.
• Optimize PCB connector ground to provide better ground path and minimize the effect coupled to MDI lines.
4.6.3.4 Schematic and Layout Recommendation
After performing the above debug procedure to further isolate potential issues, please follow the schematic and
26 Optimizing EMC Performance in Industrial Ethernet Application SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024

4.7 IEC 61000 4-6 CI
The IEC 61000 4-6 is also known as Conducted Immunity Testing. Conducted immunity refers to a electrical
device’s ability to resist unwanted RF disturbance voltages and currents that get coupled through external wires.
The main source of disturbance comes from electromagnetic fields due to equipment with RF transmission,
with this disturbance injected into the Coupling Decoupling Network (CDN) and flowing to the Ethernet cable.
Unlike ESD and EFT tests, most of the noise are flow through the shield and directly to connector ground. CI
testing involves electromagnetic noise injected directly into the cable communication lines to disturb the system.
Therefore, both the common mode and differential mode impedance of the device are crucial for CI testing. In CI
testing, the disturbance has the frequency range of 9kHz to 80MHz with 80% Amplitude modulation at 1kHz.
CI test level:
• Level 1: 1Vrms
• Level 2: 3Vrms
• Level 3: 10Vrms
Note: Class A, Class B, and Class C depend on the customer’s requirements. For the Class A requirement,
customers typically look for no link drop as opposed to no consecutive packet errors, as CI testing involves static
constant high frequency noise injection. Most of the packet errors occur at the same time and frequency range
(most likely on communication frequency)
4.7.1 CI Test Setup
• The CDN needs to have 0.1 - 0.3m separation to the DUT and LP
• Cable needs to be 30-50mm above earth ground
• CDN needs to match corresponding cable types
• Attenuator between the test equipment and CDN
– Verify the cable before the attenuator does not have any contact with the system such as DUT, LP,
Ethernet cable, cable after attenuator. This can result in high amplitude noise direct injected into the
system without attenuation
Figure 4-11. CI Test Setup
• Further details on the CI test setup and waveform and test setup can be found in the IEC 41000
4-6 standard.
• Capacitive clamping is also allow for CI testing if CDN is not available.
4.7.2 Possible Root Cause of Failure
• CI testing is a high frequency noise injection into the system. CI testing can inject noise into the signal lines
of the PHY's system, sweeping over a wide frequency. The frequency sweep can interfere with some digital
blocks inside the PHY, resulting in failure or link loss. There is importance to have a good common mode
SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 27

noise path from the signal lines to connector ground to reduce the amplitude of the noise. A good path for the
noise to flow directly to earth ground can also help with CI testing for the shielded cables.
28 Optimizing EMC Performance in Industrial Ethernet Application SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024

4.7.3 Debug Procedure
If failures are observed during CI testing, please follow the debug procedure to isolate the root cause:
4.7.3.1 Follow CI Test Setup
• Verify the cable before the attenuator (cable between function generator and attenuator) is isolated and not
touching the cable after attenuator, DUT, LP, and Ethernet Cable
– Normally the cable before the attenuator carries noise with huge amplitudes, easily disturbing other signal
• Verify the link partner’s RJ45 shield is connected to earth ground
– Normally the long cable is on the link partner side. There can be higher impedance between shield
and earth ground if the only connection between cable shield to earth ground is within CDN. Therefore,
providing a small impedance path to ground helps with CI testing
– If the RJ45 shield is not able to connect to earth ground for the application, connect the RJ45 shield or
connector ground directly to a metal or conducted case to provide a better radiated path for EMI noise to
flow and radiate to the surrounding area.
• Longer cable is preferred on the link partner side to reduce the effect on link partner
• Verify the cable type matches on both sides of the CDN
• Verify the CDN type matches with the cable types used
– Mismatching unshielded cable CDN with a shielded cable can potentially increase reflective noise due to
the discontinuous of ground in the signal lines
– Using unshielded cable CDN with shielded cable can also increase the impedance of the return path
between signal lines and earth ground, introducing higher amplitude noise on the signal lines
• Verify the CDN is connected to the earth ground
• Prevent any cable looping that can increase crosstalk
• Verify the cable is not touching any noise source
• Shielded cable is recommended. (CAT 6 cable preferred)
– Having a shielded cable is better than non-shielded cable since the shielded cable provides a path from
MDI lines to ground inside the CDN for through capacitors
– For unshielded cables, all noise can go directly to the signal lines, with no noise coupling to ground
4.7.3.2 Remove External Factors on Cable or Link Partner
• Change the link partner to the same as DUT and perform a test
• Check the failing frequencies for CI tests, adding Ferrite beads on the link partner side to isolate issues
based on the link partner for the failing frequency
• Remove the cable on the link partner side, and enable loopback on the DUT. Perform a CI test after loopback
is enabled.
4.7.3.3 Areas to Explore to Improve CI Performance
If CI test failures are still observed after trying the steps above, the issue is most likely on the DUT side. Here are
some recommendations to further improve CI test performance:
• Check the CI failing frequency:
– If CI tests are failing at lower frequency ranges, check the power lines, power plane, and power supplies
on the boards near the connector ground or MDI lines. Also verify the power supply is not close to any
noise sources
– If CI tests are failing around the clock frequency, check the clock trace or clock source on the board. Verify
they are not close to the connector ground or MDI lines
– If CI frequency failing around 10MHz to 80MHz, normal PHY operating frequency, please try the following
recommendations below
• Remove bob smith terminations on unused pairs to help with CI tests
– Having a bob smith termination on the unused pair can provide a smaller impedance path to earth ground.
This can result in higher common mode noise flowing on the unused pair, further coupling noise to the
used pair
– On the used pair, common mode impedance is generally large due to the common choke
SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 29

• Verify there is ground separation between the connector ground and digital ground to prevent any noise
injected directly into the system. This can reduce the ground bounce effect on the system
– Reduces crosstalk
• Discrete magnetics and RJ45 connector helps reduce the injection area of ESD noise and improve the
performance of the transformer during ESD tests
• Optimize the layout of MDI lines to reduce the common mode noise picked up from surroundings, ground
bounce, and other signals on the PCB.
• Optimize the PCB connector ground to provide a better ground path and minimize the effect coupled to the
4.7.3.4 Schematic and Layout Recommendation
After performing the above debug procedure to further isolate potential issues, please follow the schematic and
30 Optimizing EMC Performance in Industrial Ethernet Application SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024

5 Schematic and Layout Recommendation for All EMC, EMI Tests
5.1 Schematic Recommendation
Relevant Test Recommendation Explanation
No test point is
General EMC Immunity and recommended on the MDI • Prevents any noise captured to or from the surroundings
Emission test
• Shorted center taps can increase the common mode noise on the MDI
• Shorted center taps can increase cross talk between TX and RX
• Shorted center taps can also affect the bias voltage point on TX
• Prevents current leakage between transmitter and reciever during
Auto-MDIX
No shorted center taps
General EMI test
(voltage mode driver only)
Galvanic isolation • Greatly reduces the common mode noise going into the PHY or
General EMI test (transformer) is highly system
recommended instead of
• Improves isolation between the connector and PHY
capacitive coupling
• More precise terminations can reduce the impedance mismatch and
prevent reflections on the MDI lines
Termination on MDI lines
General EMI need to be 1% tolerance for
current mode driver
SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 31

• Ferrite beads on the pull up resistor on MDI lines (current mode
driver). Filters out noise from the power supply, improving CE tests
and other power supply EMI test.
Ferrite beads on the pull
up resistor on MDI lines
General EMI
for current mode driver PHY
(DP83822 and DP83848)
• Prevents direct high voltage noise injection on the system ground
• R//C is recommended to prevent connector ground charging up
Ground isolation between significantly after multiple ESD/EFT strikes.
system ground and – Capacitor provides limited noise flow to the system ground while
ESD and EFT
connector ground using R//C preventing sudden high voltage jumps on the system ground
connection – Resistor is used to discharge the capacitor after clamping due to
multiple ESD/EFT events
Make sure the R//C connection is not near any signal or clock traces
In typical applications, the CMC is placed between the transformer and
RJ45 connector. This filters out most of the common mode noise coming
from the cable.
Add additional Common
ESD and EFT Mode Choke (CMC) near the • Adding an external CMC near the PHY side can prevent any further
PHY side noise picked up from the ground to MDI lines, or noise picked up from
the surroundings to the MDI lines between the PHY and transformer
area
Replace existing center
• Provides a path for common mode noise to discharge at different
tap with 0.1uF // 1uF on
the PHY's side transformer frequencies
center tap
32 Optimizing EMC Performance in Industrial Ethernet Application SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024

• Prevents any noise from VDDIO from having a direct effect on VDDA
• Buck converter can generate high frequency due to the harmonics of
the switching frequency
Power surge and RI Add Ferrite beads on VDDA • Input decoupling capacitors are able to filter out the most of the
and VDDIO
frequencies, but not the higher ranges
– Placing a ferrite bead close to the noise source can greatly help
with this high frequency noise
• Pi filter on the system can eliminate the noise due to the power cable
in for lower frequencies
Add Pi-filter on the power
Power surge
side – Take into account the resonance of the Pi filter. Capacitors with
significant ESR is a good choice to reduce the resonance
• Common mode choke on the power supply is also recommended to
Common mode choke on the
Power Surge
power side prevent any common mode noise
SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 33

5.2 Layout Recommendation
1. MDI lines recommendation:
Both PHY side and RJ45 connector side MDI recommendations
Symmetry and same pad
General EMI footprints and position of • Reduces mode conversion effect on EMI testing
differential pairs on MDI
General EMI Impedance match of MDI • Reduces reflections on the signal lines
Continuous ground layer under MDI lines can provide constant impedance
matching on MDI lines
• Impedance discontinuities cause unwanted signal reflections.
• Signal crossing over a plane split can cause unpredictable return path
currents and can likely impact signal quality as well, potentially creating
Continuous ground layer EMI problems.
General EMI
under MDI lines
When matching the intra pair length of high-speed signals. The serpentine
routing need to be as close as possible to the mismatched ends
• Reduces the effect of differential mode noise
General EMI Length Matching
Limiting the MDI trace bending can minimize the effect of cross talk
between different sections of the MDI trace.
• Reduces the noise introduced on the MDI traces
General EMI Minimize MDI trace bending
Reduces the emission point with round turns on MDI line (ESD Protection
General EMC No sharp turns on MDI lines
Layout Guide
34 Optimizing EMC Performance in Industrial Ethernet Application SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024

• Prevents noise injected directly to the transformer through the ground
polygon pour during EMI events.
• Polygon pours under the transformer can decrease the transformer's
isolation functionality
Avoid polygon pours (keep
ESD and EFT out region) under/near
transformer
• Integrated RJ45 magnetics have an isolation network inside the RJ45
shield. If any noise is injected onto the RJ45 shield, the transformer's
performance can degrade significantly. Some of the noise can bypass
the isolation network and directly couple to system ground or the MDI
lines.
• Discrete magnetics can minimize the injection noise on the RJ45 shield
and have a direct impact on the digital ground or MDI lines, improving
Discrete magnetic and RJ45 the transformer performance
connector is recommended
• Shorter MDI lines can shorten the exposed path to the surroundings
EMC, ESD and possibly RI Short length on MDI lines
and reduce the radiated coupling noise
• Reduce number of vias on MDI lines to reduce the noise picked up
from the surroundings, as well as emission to the surroundings
ESD and possibly RI Minimum vias on MDI lines
• Vias on MDI lines can result in impedance discontinuities, causing
unwanted signal reflections
• Minimize exposed area on MDI lines to reduce the emissions and
General EMC Emission and Minimize exposed area on
Immunity MDI lines radiative noise picked up on the MDI lines
SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 35

Prevent any signal wire
• Signal wire crossing on consecutive layers can result in larger
crossing with MDI lines
General EMC Emission
without any ground plane emissions
separation
RJ45 connector layout recommendation
• Vias around the MDI lines can create a better path for ESD/EFT
noise current to flow between MDI lines, increasing the chance of
interference with MDI signal lines
Minimize vias around the
ESD and EFT MDI lines on the connector
ground
No ground polygon pour
of connector ground around • Reduces the ground bounce interference from the connector ground to
the MDI lines on the the MDI lines during ESD/EFT events
same layer
Clean ground layer under • Better impedance matching
ESD and EFT MDI lines (No vias and other
• Reduces the effect of ground bounce to the MDI lines
power or signal lines)
• Prevents any power or other signal trace disturbance during EMI
No power plane and non-
General EMI MDI trace under RJ45 testing
connector • Isolates other external noise injected into the MDI lines
R//C Ground isolation or
other earth ground path • Makes sure most of the EMI noise can flow on the opposite side of the
ESD and EFT circuitry need to be on the
MDI lines and minimize ground noise interference to the MDI lines.
opposite layer as the MDI
Large component size
ESD and EFT with R//C ground isolation • Supports large current to prevent any damage during EMI event
network
No vias and ground polygon • Minimizes the noise interference going into bob smith termination and
ESD and EFT pours around the bob smith
affecting the signal during EMI testing
termination
• Allowing some EMI noise to flow between connector ground to power
R//C ground connection
ESD placed near the power ground, routing away from any sensitive circuits
supply – Minimizes the noise path to the PHY or other ICs
RJ45 module with LEDs are • Prevents EMI noise source flowing through the LED lines directly into
ESD and EFT not recommended for better
the PHYs
EMI performance
36 Optimizing EMC Performance in Industrial Ethernet Application SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024

PHY side MDI recommendation
• Reduces the mode conversion
Single differential pair need • Reduces the chance of picking up sources of differential noise
General EMI to be routed as close as
• Crosstalk between differential pairs isn't a significant concern
possible
• Smallest trace spacing is normally selected (5 to 6 mils)
• Prevents cross talk between the differential pairs
General EMI Keep some distance • Reduces the common mode noise interference between differential
between differential pairs
pairs
• Reduces the mode conversion due to ground bounced during EMI
General EMI Keep the differential pair on testing
the same reference ground
• Better impedance matching between differential pairs
SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 37

2. General Layout recommendation around the PHY:
Prevent any signal wires,
• Prevents cross talk between the signal lines and reduces EMC
clock, and power signals
General EMC Emission
crossing without any ground emission
plane separation
• Prevents cross talk between the signal lines and reduces EMC
General EMC Emission and No signal lines next to each
Immunity other emission
General EMC Emission No sharp turns of clock and • Prevents EMC emission
signal traces
Rbias pin is the internal current reference for the PHY.
• Short Rbias traces can reduce the radiated noise picked upfrom the
surroundings
• Possible bury the Rbias trace to inner layer if there are layout
Short or buried traces constraints that can also reduce noise picked up from the surroundings
RI and indirect ESD between Rbias pin and
resistor
• Minimize components size of Rbias resistor to reduce the noise picked
Minimize component size of
RI and indirect ESD
Rbias resistor up by the Rbias resistor
38 Optimizing EMC Performance in Industrial Ethernet Application SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024

3. Crystal Layout recommendation
• Makes sure crystal components are referenced to the same ground,
Keep all crystal components
on the same layer reducing the ground bounce effect
General EMI and EMC Isolate crystal and crystal lines • Prevents clock signal disturbance by other signal line
with other signal lines
• The ground connection for the load capacitors need to be short and
separated from the power line
• Prevent any effect EMI test effect directly into the clock from either
Isolate crystal ground from
Power surge, ESD and EFT MDI and power ground power or MDI lines EMC testing
(Ground island) • Keeps the noise away from the system ground
• Verify there are ground vias connected to the ground on other layer to
prevent high frequency ringing due to the floating ground
Short crystal traces and • Reduces the radiated emission
General EMC length matching on the crystal
• Improves the clock performance and reduces the ground bounce effect
capacitor
• C1 and C2 are important to use C0G/NP0 capacitors for proper
General EMC Small footprint on crystal performance in the system
capacitor
• Small footprint on crystal capacitor can reduce the emission
SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 39

4. Oscillator Layout recommendation
General EMI/EMC Impedance matching on the Using an oscillator or a clock buffer as a clock source typically expressed
oscillator traces Adding 50Ω
as a single ended signal. The oscillator clock trace is matched with a 50Ω
termination on the oscillator
termination
traces
• Series termination and parallel termination are recommended on the
oscillator for impedance matching and to minimize the reflection on the
clock signal
• This can give better clock performance or tolerance for EMI, as well as a
smaller emission factor
General EMI/EMC Verify PHY's voltage level If the clock signal does not meet the PHY's specified voltage level, the PHY
specification matches with the can have less tolerance for EMI performance
oscillator clock signals • Voltage or capacitor divider can be implemented on the oscillator to
reduce oscillator clock signal level to improve EMC emission performance
General EMC Small capacitor footprint for • Small footprint (C0G/NP0 is recommended) to reduce emissions
oscillator
40 Optimizing EMC Performance in Industrial Ethernet Application SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024

5. Power Layout recommendation
Power Surge or General The total decoupling capacitance need to be greater than the load capacitance
Total decoupling capacitance
EMI for current mode presented to the digital output buffers to prevent noise from being introduced
> load capacitance
driver device into the supply
• Decoupling caps: Smaller package size is recommend for high frequency
caps
• The physical size makes a difference with smaller footprints having lower
series inductance for better high frequency performance. Also, avoid
Power Surge or General Decoupling capacitor size
EMI for current mode selection (small caps to filter through hole or electrolytic cap footprints for filtering in this case.
driver device higher frequency noise) • Capacitor changes over frequency and has parasitics. Typically small
capacitance values are designed for filtering high frequency values
• Small capacitor need to be place closest to the PHY with incremental
values
• All decoupling capacitors must be connected directly to a low impedance
Power Surge or General ground plane (vias to ground plane)
Ground vias near decoupling
EMI for current mode
caps – Strongly consider connecting the ground of all bypass capacitors with
driver device
two vias to greatly reduce the inductance of that connection.
Power Surge or General • Provides a good low impedance return path for the power supply current
Solid ground plane on power
supply (especially for high frequency ripple) to go through the decoupling caps.
Power Surge or General • Trace connections need to be as wide as possible to lower inductance and
Wide and short power traces
are recommended reduce the noise and electromagnetic interference
Power Surge or General • Pi filter need to be near the input connector to prevent the low frequency
Pi filter need to be placed near
the input connector noise
• Common mode choke is recommended for isolation between the power
supply. If there is a voltage offset between the power supply and system,
the common mode choke can prevent or slow the transition in between.
• Make sure the common mode choke has a cut out ground plane or empty
Power Surge or General
Common mode choke on the
EMI for current mode ground plane
power supply is recommended
driver device • Typical path for common mode noise in the supply is through decoupling
caps from ground bounce to supply or the inverse. Therefore, it is crucial
to make sure no ground noise is interfering or coupling with the common
mode choke.
SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 41

6 Summary
Poor system or board design and variations with the test setup can result in EMI/EMC test failures. This article
provides details on the proper test setup, common mistakes encountered during EMI/EMC tests, and guidance
for optimizing schematic and layout design to improve EMI/EMC test performance.
7 References
• Texas Instruments, High-Speed Interface Layout Guidelines, application note.
• Texas Instruments, EMC/EMI Compliant Design for Single Pair Ethernet, application note.
• Texas Instruments, ESD Protection Layout Guide, application note.
• International Electrotechnical Commission, Generic EMC Standards.
42 Optimizing EMC Performance in Industrial Ethernet Application SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024

8 Revision History
Changes from Revision * (August 2024) to Revision A (October 2024) Page
• Updated the numbering format for tables, figures, and cross-references throughout the document.................1
• Added additional steps.......................................................................................................................................8
• Added additional note on test method..............................................................................................................22
• Added additional note.......................................................................................................................................27
SNLA466A – AUGUST 2024 – REVISED OCTOBER 2024 Optimizing EMC Performance in Industrial Ethernet Application 43