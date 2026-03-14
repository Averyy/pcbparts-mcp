---
source: "ST AN4694 -- EMC Design Guides for Motor Control Applications"
url: "https://www.st.com/resource/en/application_note/an4694-emc-design-guides-for-motor-control-applications-stmicroelectronics.pdf"
format: "PDF 51pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 69677
---

EMC design guides for motor control applications
Alessio Corsaro, Carmelo Parisi and Craig Rotay
Introduction
In recent years, continuous demand for efficient, compact and low cost applications in the motor control
industry has led to a boom in inverter-based solutions driven by MCUs. These applications involve high
switching frequencies and high power levels and must function compatibly with severe electromagnetic
environments (EMC). The implementation of transient immunity protections (EMS) to prevent appliance
malfunction and the design of countermeasures to limit application emissions (EMI) is therefore a
becoming a growing concern for appliance designers.
Best practices regarding EMC control through PCB layout, circuit design and component selection can
greatly improve EMC performance, especially when they are an integral part of the entire design cycle.
This application note discusses the effects of EMC on motor control applications and suggests some
practical hardware guidelines to provide cost-effective protection against electrical fast transients (EFT),
electrostatic discharge (ESD) and to limit the conducted and radiated emissions (EMI) in appliance
applications.
June 2015 DocID027840 Rev 1 1/51
www.st.com

Contents AN4694
Contents
1 EMC definitions ............................................................................... 5
1.1 EMC environments ............................................................................ 5
2 EMC phenomena and testing ......................................................... 7
2.1 ESD immunity test ............................................................................. 7
2.1.1 Human body model (HBM) testing ..................................................... 7
2.1.2 Charged device model (CDM) testing ................................................ 8
2.1.3 Machine model (MM) testing .............................................................. 9
2.1.4 ESD severity levels ........................................................................... 10
2.2 EFT immunity test ........................................................................... 10
2.3 Immunity test (ESD, EFT) behavior classes .................................... 12
2.4 Emissions ........................................................................................ 12
2.4.1 Conducted emissions: standards and testing .................................. 12
2.4.2 Radiated emissions: standards and testing...................................... 14
3 Impact on motor control operation .............................................. 16
4 PCB design and layout guidelines ............................................... 18
4.1 EMC Overview ................................................................................ 19
4.2 Segmentation strategy .................................................................... 20
4.3 Segmentation .................................................................................. 21
4.4 Physical layout and EMI: PCB selection and layout guidelines ....... 21
4.4.1 The PCB ........................................................................................... 22
4.4.2 Grounding ......................................................................................... 24
4.4.3 Signals .............................................................................................. 31
4.4.4 Coupling paths (crosstalk) ................................................................ 31
4.4.5 Component orientation and placement ............................................ 34
4.4.6 Shielding ........................................................................................... 34
5 Layouts .......................................................................................... 35
6 Practice case studies .................................................................... 37
6.1 Ground ............................................................................................ 37
6.2 Power .............................................................................................. 38
6.3 Signal .............................................................................................. 39
6.4 PCB ................................................................................................. 39
6.5 Case study 1 ................................................................................... 41
6.6 Case study 2 ................................................................................... 43
2/51 DocID027840 Rev 1

AN4694 Contents
6.7 Case study 3 ................................................................................... 45
6.8 Case study 4 ................................................................................... 45
6.9 Case study 5 ................................................................................... 46
6.10 Case study 6 ................................................................................... 47
7 References ..................................................................................... 49
8 Revision history ............................................................................ 50
DocID027840 Rev 1 3/51

List of figures AN4694
List of figures
Figure 1: Electromagnetic compatibility diagram ........................................................................................ 5
Figure 2: Human body model (HBM) ESDS device sensitivity test circuit .................................................. 7
Figure 3: ESD waveform ............................................................................................................................. 8
Figure 4: Typical charge device model test ................................................................................................ 9
Figure 5: Machine model (MM) ESDS device sensitivity test circuit ........................................................ 10
Figure 6: EFT waveform ........................................................................................................................... 11
Figure 7: Conducted emission limits ......................................................................................................... 13
Figure 8: LISN layout ................................................................................................................................ 14
Figure 9: Disturbance power limits for household .................................................................................... 14
Figure 10: Block diagram of motor control inverter ................................................................................... 16
Figure 11: Typical motor control schematic .............................................................................................. 18
Figure 12: EMI model................................................................................................................................ 19
Figure 13: Segmentation model ................................................................................................................ 21
Figure 14: Single-layer PCB cross section ............................................................................................... 22
Figure 15: Single-layer PCB with copper pour ......................................................................................... 23
Figure 16: Two-layer PCB cross section .................................................................................................. 23
Figure 17: Through-hole component mounting ........................................................................................ 23
Figure 18: Four layer PCB cross section .................................................................................................. 24
Figure 19: A multilayer PCB layout (taken from IEC 61967-1) ................................................................. 25
Figure 20: Ground loop minimization ........................................................................................................ 26
Figure 21: Example ground grid layout ..................................................................................................... 29
Figure 22: Improved ground loop .............................................................................................................. 30
Figure 23: Stub connections ..................................................................................................................... 33
Figure 24: Suggested layout for a three-phase power system ................................................................. 35
Figure 25: Filled copper areas connected to ground plane ...................................................................... 37
Figure 26: Routing supply and return traces ............................................................................................ 38
Figure 27: Example decoupling capacitor placement ............................................................................... 39
Figure 28: Example angled track .............................................................................................................. 40
Figure 29: Case 1 ..................................................................................................................................... 41
Figure 30: Case 1 improved layout ........................................................................................................... 42
Figure 31: Case 2 ..................................................................................................................................... 43
Figure 32: Case 2 improved layout ........................................................................................................... 44
Figure 33: Case 3 ..................................................................................................................................... 45
Figure 34: Case 4 ..................................................................................................................................... 45
Figure 35: Case 5 ..................................................................................................................................... 46
Figure 36: Case 6 ..................................................................................................................................... 47
4/51 DocID027840 Rev 1

AN4694 EMC definitions
1 EMC definitions
Electromagnetic Compatibility (EMC) is the ability of electrical and electronic systems,
equipment and devices to operate in their intended electromagnetic environment within a
defined safety margin, without suffering or causing unacceptable degradation as a result of
electromagnetic interference (ANSI C64.14-1992). EMC is classified into electromagnetic
interference (EMI) and electromagnetic susceptibility (EMS), as shown in Figure 1:
"Electromagnetic compatibility diagram"
Electromagnetic Interference (EMI) refers to disruptive electromagnetic energy transmitted
from one electronic device or equipment to another, it can be:
• conducted emission when it is propagated along a power line
• radiated emission when it transmitted through free space
Electromagnetic Susceptibility (EMS) represents performance immunity against
disturbances like electrostatic discharge (ESD), electrical fast transient or burst (EFT),
lightning surges and electromagnetic waves.
Figure 1: Electromagnetic compatibility diagram
1.1 EMC environments
OEM appliances are governed by different standards for both EMI and EMS, based on their
intended application. These standards contain test methods to satisfy product
specifications and regulatory requirements, and define transient sources, entry paths into a
system and severity levels.
The principal international standards for immunity testing are:
• IEC61000-4-2: the ESD waveform simulates the discharge from a human operator
and is injected at any location that the operator is likely to touch, including all user
accessible controls and external connectors. The test levels for ESD vary widely
depending on the application.
• IEC 61000-4-4: the EFT waveform simulates the transients created by the switching of
relays or the interruption of inductive loads on power mains. It is applied as a specific
burst waveform, usually introduced along the application’s AC power cord. The EFT
waveform can also be injected in signal and control lines to only simulate the
conducted coupling of the EFT in these lines.
DocID027840 Rev 1 5/51

EMC definitions AN4694
EN55014-1 and EN55014-2 are, respectively, the principal European emissions and
immunity standards for household appliances and power tools.
This standard establishes uniform requirements for radio disturbance levels applicable to
the conduction and radiation of radio-frequency disturbances from appliances mainly
governed by motors and switching. AC motors generate harmonic signals at the power
input and output side, creating electromagnetic interference with surrounding electrical
devices and mains power networks. AC drives can both cause and be affected by such
disturbances.
6/51 DocID027840 Rev 1

AN4694 EMC phenomena and testing
2 EMC phenomena and testing
The following section introduces the most common EMC phenomena in electrical system
designs and the tests used to emulate them.
2.1 ESD immunity test
Electrostatic discharge (ESD) is the exchange of electrons resulting from the field
accumulation between two objects with different charges and the damage to a device
depends on its ESD sensitivity and its ability to dissipate the discharge energy
The test procedures are based on the principal ESD-event models below.
2.1.1 Human body model (HBM) testing
The HBM testing model (ref. ANSI/ESDA-JEDEC JS-001-2010: Electrostatic Discharge
Sensitivity Testing - Human Body Model) represents the discharge that the fingertip of a
standing individual delivers to the device. It is modeled by the circuit shown in Figure 2:
"Human body model (HBM) ESDS device sensitivity test circuit", featuring a 100 pF storage
capacitor (C ) discharging through a switching component and a 1.5 kΩ series resistor, R .
S D
Figure 2: Human body model (HBM) ESDS device sensitivity test circuit
C and R represent the capacitance and the discharge resistance of the human body
S D
respectively. R is the series resistance of the DC high-voltage power supply. When switch
S is connected to RC , the capacitor is charged.
S
The human body can store electrostatic energy to potentials in the order of several
thousand Volts (8 kV to 10 kV is common) and peak currents in the order of a hundred
Amperes.
The IEC 61000-4-2 standard specifies an ESD waveform with characteristics similar to a
typical human body discharge pulse, but with far greater energy (Figure 3: "ESD
waveform")
DocID027840 Rev 1 7/51

EMC phenomena and testing AN4694
Figure 3: ESD waveform
The HBM sensitivity test is usually an automatic system which delivers ESD pulses and
signals device failure when datasheet parameters are not satisfied.
2.1.2 Charged device model (CDM) testing
Another ESD event is the transfer of energy from a charged ESDS (electrostatic discharge
sensitive) device, perhaps due to the contact with a conductive surface. This event is
known as the CDM model event (ref. ANSI/ESD STM5.3.1: Electrostatic Discharge
Sensitivity Testing - Charged Device Model) and the associated high current peak can be
even more destructive than the HBM. A typical CDM model test circuit is shown in Figure 4:
"Typical charge device model test".
8/51 DocID027840 Rev 1

Figure 4: Typical charge device model test
2.1.3 Machine model (MM) testing
Discharge events from conductive surfaces such as automatic equipment and ESDS
devices are covered by the MM model (ref. ESD STM5.2: Electrostatic Discharge
Sensitivity Testing - Machine Model).
The machine model consists of a 200 pF capacitor discharging into the DUT with no series
resistor (Figure 5: "Machine model (MM) ESDS device sensitivity test circuit"). The series
inductance L creates the oscillating machine model waveform and is defined by the peak
MM
current, rise time and period of the waveform.
DocID027840 Rev 1 9/51

Figure 5: Machine model (MM) ESDS device sensitivity test circuit
2.1.4 ESD severity levels
The ESD threat in IEC 61000-4-2 is divided into four severity levels, depending on the
operating environment of the device, with the corresponding test pulse peak voltage (Table
1: "IEC 61000-4-2 severity levels"):
• levels 1 and 2 are reserved for controlled environments with anti-static materials
• level 3 is for lightly handled equipment
• level 4 is for continuously handled equipment
Table 1: IEC 61000-4-2 severity levels
Test voltage, kV Test voltage, kV
Severity level
contact discharge air discharge
1 2 2
2 4 4
3 6 8
4 8 15
2.2 EFT immunity test
Electrical fast transient disturbances or bursts are common in all applications, including
electrical switches and inductive loads. They are generally power line phenomena, but can
also cause problems on signal lines due to inductive or capacitive coupling. They can occur
during the commutation of inductive loads, when the current is disconnected and a series
of small sparks delivers high-voltage spikes to power lines.
The IEC 61000-4-4 standard specifies the EFT-sensitivity test for electrical components .
The disturbance is described in terms of a series of 2 to 5 kHz high voltage spikes, with 15
ms burst lengths at 300 ms intervals. The test circuit has a 50 Ω load driven by a voltage
generator with a dynamic source impedance of 50 Ω. Each individual burst pulse is a 50 ns
double exponential waveform with a 5 ns rise time (Figure 6: "EFT waveform").
10/51 DocID027840 Rev 1

Figure 6: EFT waveform
Based on the susceptibility of the application, the following four severity levels are defined
as a function of the installation environment:
1. well protected
2. protected
3. typical industrial
4. severe industrial
IEC 61000-4-4 stipulates the open-circuit test voltages for each threat level and the burst
series frequency, as a function of the test level (Table 2: "Table 2: IEC 61000-4-4 severity
levels").
DocID027840 Rev 1 11/51

Table 2: Table 2: IEC 61000-4-4 severity levels
Severity level EFT peak amplitude (kV) Repetition frequency (kHz)
1 0.5 5
2 1 5
3 2 5
4 4 2.5
2.3 Immunity test (ESD, EFT) behavior classes
ESD and EFT results are classified in terms of the loss of function or degradation of the
tested equipment:
• Class A: normal performance within limits specified by the manufacturer, requestor or
purchaser
• Class B: temporary loss of function or degradation of performance which disappears
when the disturbance ceases, and from which the equipment under test recovers its
normal performance without operator intervention
• Class C: temporary loss of function or degradation of performance, the correction of
which requires operator intervention
• Class D: loss of function or degradation of performance which is not recoverable,
owing to damage to hardware or software, or loss of data
2.4 Emissions
2.4.1 Conducted emissions: standards and testing
Any electronic device is a potential source of noise currents both on the power network of
the installation and the overall power grid. This disturbance can affect other devices
connected to the power grid through conductive coupling and the electrical length of the
conductors may effectively allow this noise to radiate.
The CEI EN 55022 standard specifies the limits for both class A (products marketed for
commercial or industrial use) and class B (product marketed for residential or domestic
use) devices in the 150 kHz to 30 MHz frequency range. The conducted quasi-peak and
average value emission limits are provided (Figure 7: "Conducted emission limits").
Although the conducted emissions are expressed as noise currents, they are measured in
terms of proportional noise voltages and the standard limits are therefore expressed in
dBµV.
12/51 DocID027840 Rev 1

Figure 7: Conducted emission limits
DocID027840 Rev 1 13/51

Conducted emissions are measured using a line impedance stabilization network (LISN), in
series with a power cord (Figure 8: "LISN layout"). The LISN provides constant impedance
for the DUT over the given frequency range, rendering the measurement independent of
the position of the power network connection point, and filters power network noise
currents which could affect the test.
Figure 8: LISN layout
2.4.2 Radiated emissions: standards and testing
Any electronic device can generate and emit electromagnetic fields. The release of
electromagnetic energy in the form of radiated emissions may interfere with the normal
operation of the device itself or nearby devices.
The radiated emissions are measured in terms of disturbance power, defined as the power
that the appliance could supply to its leads. The standard CEI EN 55014-1 standard
specifies the limits (in dBpW) and the measurement methods (art.6) of the disturbance
power in the 30 MHz to 300 MHz frequency range for both quasi-peak and average values
(Figure 9: "Disturbance power limits for household").
Figure 9: Disturbance power limits for household
14/51 DocID027840 Rev 1

For frequencies above 30 MHz, the disturbance energy is mostly radiated by the mains
leads, so the disturbance power can be measured via the power supplied by the appliance
to a suitable absorbing device placed around these leads at the position of maximum
absorption. Consequently, the standard specifies the measurement by an absorbing clamp
placed around a power cord of length based on the wavelength of the lowest frequency.
DocID027840 Rev 1 15/51

Impact on motor control operation AN4694
3 Impact on motor control operation
EMC compliance must be a primary consideration when designing new applications in
order to reduce cycle times and project costs and avoid wasting resources to
retrospectively solve EMC issues. Furthermore, while good PCB layouts will involve similar
production costs to bad ones, the costs associated with remedial activities can be high.
Precautions should therefore be taken during the hardware system design implementation
phase to control the impact of EFT, ESD and emissions.
An inverter-based motor control application (Figure 10: "Block diagram of motor control
inverter ") generally consists of a digital part (microcontroller), a control part (IC gate driver,
comparator for protection, op-amps for current sensing and other current and temperature
sensors), a power stage (based on IGBT or MOSFET devices), a low voltage power supply
and some voltage regulators.
Figure 10: Block diagram of motor control inverter
Mains Bridge rectifier
Gate driver
D U ea V d L O tim / e L S e h v i e ft l Bo d o io ts d t e rap Half bridge
Comparator Sh S u m t D a o rt wn Op-Amp
Microcontroller D U ea V d L O tim / e L S e h v i e ft l Bo d o io ts d t e rap Half bridge M
UVLO / Level Bootstrap Half bridge
Dead time Shift diode
NTC
temperature
monitoring
SLLIMM
Feedback
As the application manages high currents and voltages, the power stage configuration is
critical and the board layout must include several aspects, such as track lengths and
widths, circuit areas, as well as the proper routing of the traces and the optimized
reciprocal arrangement of the various system elements and power sources in the PCB
area.
Designers must first aim to reduce the EMI issues and over-voltage spikes due to parasitic
inductances along the PCB traces.
The designer must also ensure that the EFT noise injected through the supply lines of the
system is properly conducted, via external ground or via supply voltage, away from
sensitive devices like microcontrollers or IC gate drivers, since it can cause bit errors in
digital circuits and cause poor signal integrity in analog circuits.
16/51 DocID027840 Rev 1

AN4694 Impact on motor control operation
Failure to do so can result in abnormal input PWM signals, undesired fault signals,
insufficient protection, false current readings and overvoltage signals. All of these issues
may lead to temporary loss of normal operation and even permanent device damage.
Finally, designers must prevent ESD-provoking conditions which can permanently damage
components by implementing hardware solutions like low-pass filters, protection and clamp
diodes as well as optimized PCB layouts.
DocID027840 Rev 1 17/51

PCB design and layout guidelines AN4694
4 PCB design and layout guidelines
In designing motor control circuits to meet EMC standards, the EMC requirements must be
part of the product definition followed by target reductions for EMI emissions and
susceptibility improvements during the circuit design, component selection and PCB layout
phases.
A generic circuit topology of a highly integrated motor control design is illustrated in Figure
11: "Typical motor control schematic". Here, we can visualize its various functional blocks
and consider which functions might generate or be susceptible to EMI as well as the
coupling paths that might exist between these sections.
Figure 11: Typical motor control schematic
18/51 DocID027840 Rev 1

AN4694 PCB design and layout guidelines
4.1 EMC Overview
A simple EMI model consists of the following elements (Figure 12: "EMI model"):
• EMI source
• Coupling path of EMI
• Victim or receptor of EMI
Figure 12: EMI model
EMI sources include microcontrollers, electronic discharges, transmitters, transient power
components such as electromechanical relays, switching power supplies and lighting. In a
microcontroller-based system, the clock circuitry is usually generates the most wide-band
noise.
Although all electronic circuits are receptive to EMI transmissions, the most critical signals
are the reset, interrupt, fault, protection and control lines. Analog amplifiers, control circuits
and power regulators also are susceptible noise interference.
The coupling path between the source and the receptor can be:
• conductive - where the coupling path between the source and the receptor is formed
by direct contact like a wire, cable or track connection.
• capacitive - where a varying electrical field exists between two adjacent conductors or
tracks typically less than a wavelength apart, inducing a change in voltage across the
gap.
• inductive or magnetic - where a varying magnetic field exists between two parallel
conductors or tracks typically less than a wavelength apart, inducing a change in
voltage along the receiving conductor
• radiative - where the source and receptor are separated by a large distance, typically
more than a wavelength. The source and receptor act as radio antennas with the
source emitting or radiating electromagnetic waves which propagate through open air.
The switch-mode power supply is usually a major source of EMI in motor control
applications. It manages transient high current and voltages in the form of square pulses
with high rates of di/dt and dv/dt. The waveforms are highly nonlinear and thus have high
DocID027840 Rev 1 19/51

harmonics content. With so many frequency components present, the signals contain what
is often referred to as noise, which can easily be conducted or radiated into other motor
control circuits, causing them to malfunction.
Designers often use snubbers and soft switching techniques to minimize the EMI from the
SMPS.
Surprisingly, since today’s power transistors are often capable of switching at frequencies
far above what is required by the application, certain sections of the circuit can unwittingly
amplify the noise and harmonic content and further compound the EMI problem. These
unwanted frequency components can be high enough to be classified as Radio Frequency
Interference, or RFI.
Inverter and driver circuits are also potential generators of EMI, and designers must focus
on the turn-on and turn-off characteristics of the power transistor components to minimize
EMI in these circuits. When the design is based on discrete IGBT or MOSFET components,
the designers have more flexibility in tuning the turn-on and turn-off behavior using
appropriate gate resistors to set the best trade-off between EMI and power loss.
When an IPM (Intelligent Power Module) is used, the driving network is internally set and
already optimized for both EMI and power loss behavior.
Motor control designs also have sections that provide control or sense functions. These
circuits are often susceptible to EMI, so design strategies such as bypassing, filtering and
buffering are essential to avoid their malfunction.
Once the EMI sources and susceptible components have been identified, the best circuit
topology can be chosen within the performance and cost constraints.
Finally, with the initial circuit design frozen and its schematic captured, attention can be
focused on what often lies at the heart of the EMC source and control problem: the physical
realization of the PCB. This phase of the design may be considered a “segmentation
strategy”, because it takes into account how the layout and routing of various three
dimensional structures and components may impact EMI on the final product. Many EMC
obstacles are often found and dealt with during the segmentation and layout phases of the
design.
The main phases in which EMC requirements should be addressed are:
1. circuit definition phase: identification of the appropriate EMC standard on which the
design is based
2. circuit design phase: during the schematic capture the engineers should:
a. identify circuits and components that are potential EMI Sources
b. identify circuits and components that are sensitive to EMI (susceptors)
c. identify potential conductive and radiated paths between EMI sources and
susceptors
3. develop a circuit segmentation strategy for efficient layout and routing planning
4.2 Segmentation strategy
The critical layout structure/topology aspects which have a significant impact on EMI are:
1. PCB: determine the type of PCB, its size and the number of layers (often cost driven)
2. grounding: determine the grounding topology which is directly related to the PCB
selection
3. signals: decide what types control, power and ground signaling will be present for the
desired motor control functionality
4. coupling paths (crosstalk): determine the preferred method for exchanging signals
between functional blocks (routing) and whether the majority of lumped components
will be SMT or through-hole
20/51 DocID027840 Rev 1

5. component orientation and placement: identify large components or ones that require
heat sinks as these may have placement restrictions and require special treatment
6. shielding: if other methods for controlling EMI do not satisfy your EMC goals or limits,
consider how shielding may be applied to the PCB
4.3 Segmentation
After thorough planning, the actual segmentation process should be logical and
straightforward. The block diagram in Figure 13: "Segmentation model" shows the result of
a segmentation plan which that takes into account all the major contributors to EMI. It
shows an overview of:
• how circuit functions should be compartmentalized into blocks
• how the blocks will be arranged
• how the blocks are to be separated by a grounding scheme
In addition, it is a graphical tool for the efficient planning and routing of the PCB.
Within each functional block, each EMI contributor is identified directly from the schematic.
Since the grounding scheme is so important to the success of EMC, it is shown clearly
separating the blocks. Of course, this is merely an ideal arrangement for the blocks and the
grounding scheme, serving as a constant reminder to keep the design as close to the ideal
as possible.
Figure 13: Segmentation model
So far, we have described a top-down approach to EMC considerations in which the global
contributors to EMI are identified, a segmentation strategy is applied and the foundation for
an EMI friendly layout is established.
4.4 Physical layout and EMI: PCB selection and layout
guidelines
In this section, we switch to a bottom-up approach for managing EMC objectives via an
intelligent layout, involving the efficient placement of EMI contributors and corresponding
interconnections and interactions.
DocID027840 Rev 1 21/51

4.4.1 The PCB
Since the design is based on the PCB, we must consider the numerous factors regarding
PCB selection for an EMI-friendly product.
Conductors that are electrically long with respect to the physical wavelength of the
associated signal (λ), have a greater potential to be affected by EMI sources or to become
EMI sources, so designers should choose PCB materials with the lowest possible εr
(dielectric constant of the substrate material).
FR4 is commonly used for low frequency designs, with its εr of approximately four owing to
the insulating layers in glass-filled epoxy resin.
The thickness of the substrate layer is significant because it influences the degree of
coupling between different conductive layers and between adjacent conductors. The width
of a conductor compared to the thickness (height) of the isolating layer (w/h) governs the
amount of coupling between conductors, and is therefore important for effective EMI
control.
The most significant factor in the final EMC performance of a particular design is probably
the specification of the number of available layers for the PCB. This decision is so
important because it relates to the intended grounding topology, which determines the
overall EMI behavior. Access to ground and the shielding offered by the grounding
structures is the key to EMI management.
Figure 14: "Single-layer PCB cross section" shows a low-cost single-layer PCB, where
particular attention must be paid to the grounding scheme as power, control and ground
circuitry are all confined to a single plane. This adds considerable complexity to the layout
and increases the risk of EMC problems as there are more opportunities for circuitry to
interact and access to grounding structures is limited.
Figure 14: Single-layer PCB cross section
On this type of PCB, as much of the board perimeter should be dedicated to ground as
possible, with frequent short and wide connections to this feature. All areas not requiring
interconnecting traces should utilize a copper pour (Figure 15: "Single-layer PCB with
copper pour") and connect these areas to ground. The copper pour should, however, be
removed from areas isolated from ground.
Single-layer PCBs do not therefore provide sufficient flexibility for a robust EMC solution.
22/51 DocID027840 Rev 1

Figure 15: Single-layer PCB with copper pour
A two-layer board (Figure 16: "Two-layer PCB cross section") allows for a dedicated
grounding layer, lower layout complexity and shielding at a slightly higher cost. However,
the possibility that control and power blocks influence each other persists, so it remains
critical to separate EMI sources and susceptors.
Figure 16: Two-layer PCB cross section
Figure 17: "Through-hole component mounting" shows how components mounted through
the board can be placed on the side which is mostly ground, which can be an effective
shield between the component side and the side with the traces.
Figure 17: Through-hole component mounting
The four-layer PCBs in Figure 18: "Four layer PCB cross section" show two very different,
more costly solutions. The board on the left has better self-shielding thanks to a dedicated
ground layer sandwiched between a control signal layer on top and a power signal layer
below. It is also possible to place the components on the top or bottom of the PCB and go
through the board where needed. The power layer, however, cannot benefit from air
cooling and may cause interference to the bottom signal layer; both signal layers can also
be affected by external EMI sources.
The PCB on the right has external ground layers providing self-shielding from off-board or
board-generated EMI. Unfortunately, it mixes signals on the same layers and has no
provision for placing components.
DocID027840 Rev 1 23/51

In any case, the challenges associated with EMC control are greatly reduced with four
conductive layers thanks to the increased availability and access to ground.
Figure 18: Four layer PCB cross section
A minimum of one dedicated grounding layer strongly benefits EMC control and any EMC-
friendly design should therefore consist of at least two conductive layers.
4.4.2 Grounding
Many sources of and susceptors to EMI can be readily managed by a good grounding
strategy.
The design team must first decide where on the PCB to locate the definitive ground
reference for all signals. This is often a single physical point on the board; possibly where
the PCB is attached to a chassis or metallic housing. The connection of this point to a
dedicated layer on the PCB helps maintain this reference.
It is then important to ensure that ground paths to this point take the shortest route
possible, even if tradeoffs are often inevitable, including limited available areas for ground:
• a single-sided board has no dedicated ground layer, so grounding topologies are very
limited.
• a two-sided board has only one layer that can be dedicated to ground, with the power
and signals sharing the second layer.
• boards with more than two layers have more flexibility for ground placement and
therefore a greater potential for EMI control.
Figure 19: "A multilayer PCB layout (taken from IEC 61967-1)" provides an overview of a
multilayer (in this case, four) PCB. It features a grounding shield around the perimeter of
the top layer, with many periodic via connections to a dedicated bottom ground layer.
Layers two and three are designated for power and signal traces, respectively. This
configuration allows quick access to ground for the power and signal traces and a high
degree of shielding between critical functional areas.
24/51 DocID027840 Rev 1

Figure 19: A multilayer PCB layout (taken from IEC 61967-1)
Actual layout planning can begin once segmentation and PCB selection processes based
on grounding have been completed. To recap, the basic grounding objectives are:
1. to allow electric charge and current to flow from source to load and back to the source
via a return path
2. to provide a stable reference potential of 0 Volts
3. to control electromagnetic interference due to electric and magnetic field coupling, i.e.,
provide adequate isolation
The following EMC-friendly layout guidelines will help achieve the basic goals of grounding
and take full advantage of grounding related to EMC.
DocID027840 Rev 1 25/51

4.4.2.1 Minimizing ground impedance
Dedicating large areas of the PCB to ground and connecting components to these areas
along the shortest routes possible minimizes impedance to current flow, thus minimizing
ground impedance. Inductance and resistance are minimized by using wide, short traces
when immediate connection to the ground plane is not possible. Figure 20: "Ground loop
minimization" illustrates the principle for reducing ground impedance.
Figure 20: Ground loop minimization
26/51 DocID027840 Rev 1

DocID027840 Rev 1 27/51

4.4.2.2 Signal and power ground connections
Special care must be taken on the connection between the signal and power grounds.
It is preferable to connect signal circuit grounds to power grounds at a single point because
the transient voltage drops along power grounds can be substantial due to high values of
di/dt flowing through finite inductance.
If signal processing circuit returns are connected to power ground a multiple points, these
transients appear as return voltage differences at different points in the signal processing
circuitry.
As signal processing circuitry seldom has the noise immunity to handle power ground
transients, it is generally necessary to tie the signal ground to the power ground at only one
point.
This rule can also be extended to use of ground planes. For power circuits, it is important to
have either separate ground planes or to ensure that the high current path on the ground
plane does not traverse sensitive signal ground areas on the same plane.
4.4.2.3 Identify high current and voltage (power) blocks
To decrease the likelihood of unwanted emissions, locate power elements as close as
possible to ground. This includes blocks which don’t only have the highest
currents/voltages, but also the highest rates-of-change (di/dt, dv/dt). Such blocks are:
• clocks
• bus buffers/drivers
• power oscillators
Remember that the same high currents and voltages must also flow through the ground
path to the actual ground and are thus ground signals. It is important to physically separate
the ground signals of these high-power blocks from the ground currents that exist in the
lower power or sensitive circuitry blocks.
4.4.2.4 Identify sensitive circuits
Sensitive circuits are the next priority for placement in proximity to a ground plane (but
away from the power elements). These blocks are therefore situated further from the actual
ground than the power blocks.
It is good practice not to locate sensitive blocks near the edge of the board to decreases
the likelihood that these are affected by EMI (susceptibility) from sources of the board. One
solution is to arrange the ground between the edge of the board and the sensitive blocks.
Sensitive blocks can be:
• low-level analog or DC signals like current sensing, fault signals and protections
• high-speed digital data
4.4.2.5 Prioritize ground over all routes
When possible, separate all functional blocks from one another with a path to ground. The
ground paths should form periodic connections with the actual ground layer as frequently
as possible.
The layout designer might accomplish this prioritization by imagining the PCB as starting
with a complete conductive copper layer into which all interconnecting traces must be
pushed. This perspective ensures that paths to ground are always as short as possible,
and blocks are as separate as possible.
28/51 DocID027840 Rev 1

4.4.2.6 Types of grounding structures
A ground plane is preferable to ground traces because:
• it reduces common impedance coupling and promotes return current to flow as near to
the source current as possible
• it has much lower partial self-inductance and resistance with respect to ground traces,
vastly reducing the common impedance effect
By dedicating an entire layer or plane of the PCB to the grounding function, any node of the
circuit requiring grounding is simply connected through the board to the dedicated layer,
which is the shortest possible path.
Ground grids can approximate the underlying properties and benifits of PCB ground layers
when the latter are too costly or impractical for a particular application, and thus represent
the next best solution.
Multiple paths for the signal current are formed across the PCB layers and joined between
layers using vias. This allows the return current to follow multiple paths to the common
grounding reference, thus providing the path of lowest impedance.
The higher the grid density, the more closely a continuous ground plane is approximated,
but the density may be adjusted to make room for components or completely removed from
areas where higher component concentrations are required. By maintaining a surrounding
grid, there is no drastic change to the low impedance ground path.
Note that schematic groups surrounded by a ground grid are inherently shielded between
segments as well as between board layers.
Figure 21: Example ground grid layout
When neither a continuous ground plane nor a ground grid approach is feasible, the path
length for return current to reach the ground structure is increased. If the path length is
excessive or the trace is too narrow, a ground loop may be formed.
DocID027840 Rev 1 29/51

Ground loops are not examples of minimum ground impedance and must be avoided.
Current flowing through ground loops can radiate energy from the PCB to sensitive
components. External magnetic fields inducted into the loop can cause fluctuation of the
true ground reference potential and stray current can flow into the circuit (common-mode
current).
As the layout effort progresses, it is best EMC design practice to continuously monitor for
ground loops and take actions to eliminate them. For example, ground loop hazards
frequently develop near power components since the current flowing through them is high.
Referring back to Figure 20: "Ground loop minimization", the recommended practice
illustrates that the return current path, and hence the ground loop impedance, is minimized
by re-locating the power source closer to the physical ground reference and connecting the
loads using the shortest and widest route.
Examine each power source to ensure its supply and return traces are laid out near each
other and in the smallest possible area. This ensures the minimum inductance between
different current loops. If a ground loop is unavoidable, it is best to use capacitive
bypassing between the offending source and return traces.
Figure 22: "Improved ground loop" shows a small section of a high density PCB with a
potential ground loop problem. As circuit density increases, it becomes more difficult to
identify ground loops and layout tools may sometimes choose trace routings that are not
ideal.
Here, the layout designer identified a large loop while reviewing the layout for critical
ground nodes and re-routed non-critical traces to give priority to the ground trace, thus
significantly reducing the ground loop impedance.
Figure 22: Improved ground loop
30/51 DocID027840 Rev 1

4.4.3 Signals
The types of signals to be conducted by the traces on the application board are control,
power and ground. Each type of signal has a unique influence on EMI behavior, so it is
best to apply the appropriate set of design guidelines to the traces of each signal type.
For example, control signals may have low amplitude voltages or current, so the
conductors dedicated to routing these signals can be narrower. On the other hand, these
control signals may be high-speed complex waveforms rich in harmonics, so longer traces
may emit higher EMI, or their traces may be susceptible to sources of EMI.
The ground currents associated with these control signals behave similarly and should be
treated together.
Power signals have high voltages or currents, and might require very wide isolations
between traces for regulatory constraints, or to avoid excessive resistive voltage drops.
The ground currents associated with these power signals behave similarly and should be
treated together.
As both control and power signals have corresponding ground signals, these should also
be isolated along with the control and power signals themselves.
Finally, place sensitive and high frequency tracks away from high-noise power tracks
(current sensing, fault signals and protections), avoiding the use of wire jumpers and
minimizing layer transitions. Where necessary, keep the same number of vias on each
signal track.
4.4.4 Coupling paths (crosstalk)
One of the more effective means of achieving EMC requirements is to focus on coupling
paths from EMI sources to EMI sensitive components.
A coupling is a connection between two or more elements and, in electronics, it refers to
the influence of one or more circuit elements on other elements. It is even possible for a
circuit element to be coupled with itself via a parasitic or undesired path.
When dealing with so many coupling paths, it is helpful to first categorize them as
described below.
4.4.4.1 Conductive path: direct connection of energy between points
A conductive path can be:
• intentional - such as to conduct a required signal from one function to another; an
example of this would be any ordinary transmission line/trace
• unintentional - resulting in one type of signal interfering with another or even the same
signal
Normally, conductive paths are those formed by copper traces on the board.
4.4.4.2 Radiated path: indirect connection of energy between points
A radiated path can be:
• intentional - such as a trace which is designed specifically to resonate in such a way
that the conducted signal transmits (directionally or omni-directionally) into the air; an
example of this is an ordinary antenna
• unintentional - such as a conductor being an inopportune fraction of a signal’s
wavelength resulting in an undesired transfer of energy to the air; an example of this
might occur when “jumping” from one location on a PCB to another with a wire,
unintentionally forming a dipole antenna
DocID027840 Rev 1 31/51

Remember that radiated paths are often efficient sources of EMI as well as efficient
susceptors of EMI.
It is of utmost importance to consider not only the fundamental frequency of the signals, but
also their harmonic components. Often overlooked, a source of EMI at the 2nd, 3rd or 10th
harmonic can be nearly as high in amplitude as the fundamental.
While PCB traces often form efficient radiators of and susceptors to electromagnetic
signals, so too do many lumped component elements such as long leads, transformer
windings, etc.
A few of the rather well-known coupling paths, most often associated with lumped
component elements, are discussed below. It is however important to note that the layout
of traces on a PCB, depending on the frequency of operation, can intentionally or
unintentionally behave similarly to lumped components.
4.4.4.3 Capacitive coupling path
This is the coupling of an alternating signal through a dielectric medium to route it from one
function to another, while blocking the flow of direct current.
A capacitive path can be:
• intentional - such as the intentional de-coupling or bypassing of a transient signal from
a conductor to ground using a capacitor, thereby preventing the signal from traversing
into other circuitry and possible malfunction
• unintentional - such as choosing a capacitor with good conductive properties
regarding the fundamental (design) frequency, but poor properties with respect to
passing harmonic frequencies, thereby allowing the harmonic energy to traverse into
other circuitry, possibly resulting in malfunction
When filtering an alternating signal, consider that the modification of a signal depends on
the circuit topology, such as:
• whether or not the capacitance is in series with or parallel to the circuit, and
• the reactance to the signal from the capacitance is 1/2 pifC, and
• the impedance to the harmonic components of the signal
4.4.4.4 Inductive coupling path
The blocking of an alternating signal caused by the presence of an opposing magnetic field
in an electrical conductor, while passing the flow of direct current.
An inductive path can be:
• intentional - such as when an inductor is positioned between circuit functions and
designed to present an open-circuit to a transient signal, thereby preventing signal
passage
• unintentional - such as a condition where the chosen inductor does not exhibit open-
circuit performance at harmonic frequencies of a transient signal, thus allowing the
harmonics to pass as noise
As many inductors are physically large and/or above the board, unintended behavior could
include antenna-like phenomena at certain unanticipated frequencies.
When filtering an alternating signal, consider that the modification of a signal depends on
the circuit topology, such as:
• whether or not the inductor is in series with or parallel to the circuit, and
• the reactance to the signal from the inductance is 2 pifL, and
• the impedance to the harmonic components of the signal
32/51 DocID027840 Rev 1

4.4.4.5 Resistive coupling path
Resistances can be introduced to modify the amplitude and routing of any signal.
A resistive path can be:
• intentional - such as introducing a required 50 Ω termination to minimize reflections on
a trace
• unintentional - such as using a narrow trace to conduct a signal over a long distance,
thereby resulting in a weak signal or high voltage drop
Any practical or physical connection between nodes or components involves a resistive
coupling path, even the copper traces on the PCB and the terminations (leads) of individual
lumped component elements can be resistive coupling paths. The design team must
determine the impact these resistance coupling paths have on EMC objectives.
Resistors in bias/supply lines from a common power source form potential coupling paths
for EMI. In such cases, the supply lines may need to be decoupled.
4.4.4.6 Traces, the primary conductive paths
It is important to make a distinction between the above mentioned coupling paths and a
primary conductive path. We define conductive paths as the primary means by which
signals are conducted and all the coupling paths above conduct signals by one means or
another.
As traces are direct conductive paths used to route signals from one function to another on
a PCB, understanding the behavior of traces and how they are routed into paths is key to
the successful control of EMI.
4.4.4.7 Discontinuities
Consider how the components in Figure 23: "Stub connections" are joined to a main trace
by a short trace segment, or stub. Stubs should be kept as short as possible and
frequency-based rules are often applied to limit their length.
Software layout tools often allow the layout designer to limit the maximum length of stubs to
fractions of wavelengths, thereby minimizing the potential for EMI radiation from one
section of the PCB to another.
Consider how multiple components are connected to a conductive path. Each of these
connections represents a discontinuity which can cause signals to be reflected into
unknown paths and cause interference. It is preferable to join all the components to the
conductor at a single location (star connection).
Figure 23: Stub connections
DocID027840 Rev 1 33/51

4.4.5 Component orientation and placement
4.4.5.1 Lumped elements
Resistors, capacitors, inductors and transformers are physical entities often referred to as
lumped elements. Lumped elements possess parasitic features which can unknowingly
couple EMI signals. While it is generally known that positions and orientations of lumped
elements influence specific coupling phenomena, it may be less evident to consider the
impact on EMC of side-effects due to parasitic elements of any component.
It is often beneficial to research and possibly characterize lumped elements in advance if
this information is not already included in the designers’ component database. Such
characterization includes the component behavior at the design frequency, temperature
ranges, operational voltage and current, as well as other component behavior and
harmonic frequencies.
4.4.5.2 Orientation and placement
The strategic placement and orientation of SMT and leaded capacitors, inductors and
resistors can significantly reduce EMI generation. Some components have higher magnetic
fields in one orientation versus another.
In general, SMT and leaded components should be mounted to achieve the lowest possible
profile on the PCB to minimize magnetic fields. Therefore rectangular-shaped SMT
components should be orientated with longest side parallel to PCB and leaded components
should be positioned as close to the PCB as possible with minimum lead length. When
connecting one terminal of an SMT or leaded component to ground, the component should
be placed on the PCB so the ground connection is made to the lowest impedance ground
point in that area of the PCB.
4.4.6 Shielding
When access to preferable grounding techniques is limited, discrete shielding solutions
such as Faraday cages may be required. Specific components or even regions of the board
may be shielded by a metallic case.
34/51 DocID027840 Rev 1

AN4694 Layouts
5 Layouts
The main objectives regarding the layout of the power stage are:
• to control the noise to the IC gate drivers and, for example, ensure the proper turn-on
and -off state for the IGBTs
• to minimize the radiated noise and spike voltages
Using a discrete approach, the motor control designer has a higher degree of freedom in
achieving the above objectives even if this implies greater complexity in routing the PCB
layout.
Conversely, using an IPM approach, several of the high power and low power three-phase
power system connections are inside the module (dashed line in Figure 24: "Suggested
layout for a three-phase power system") and this aids application design as the internal
stray inductances are already optimized by the device manufacturer.
Figure 24: "Suggested layout for a three-phase power system" shows a set of parasitic
inductances related to the different circuit tracks of a three-phase power system. The
various groups of inductances may have undesired effects which should be minimized.
Whatever the device approach (discrete or IPM), layout optimization is paramount and the
following guidelines will help minimize stray inductances and noise.
Figure 24: Suggested layout for a three-phase power system
1. The gate driving PCB traces should be as short as possible and the area of the
circuits should be minimized to avoid the sensitivity of such structures to the
surrounding noise. This also helps reduce gate driver impedance and prevent
dv/dt-induced turn-ons. A possible solution is to route the gate drive signal either
directly above or beneath its return.
DocID027840 Rev 1 35/51

Layouts AN4694
Typically, a good power system layout keeps the power IGBTs (or MOSFETs) of
each half-bridge as close as possible to the corresponding gate driver.
2. We suggest using a separate gate return from the common power ground. If the
return track is relatively wide (2.5 mm or greater) it forms a miniature ground plane.
3. Stray inductances in the DC side of the loop (Lp1 and Lp8) should be decreased to
limit the voltage transients on the bus. The effects of these inductances can be
reduced with a low-ESR decoupling capacitor connected as close as possible to
the IGBT terminals.
4. Residual inductances in the DC loop (Lp2, Lp5, Lp6 and Lp7) and stray
inductances in the AC loop (Lp3 and Lp4) are the main cause of voltage spikes at
turn-off. Furthermore, the group of Lp4, Lp5 and Lp6 stray inductances located
between the OUT pin and the ground of the respective driver provides an
undesired contribution to the issue of below-ground voltage spikes on the IC gate
driver.
These spikes can be mitigated by good PCB layout based on:
• short tracks
− Lp5 may be reduced by placing the Rshunt resistor as close as
possible to the emitter of the low side IGBT
− Lp6 may be minimized by connecting the ground line (also called driver
ground) of the related gate driver directly to the shunt resistor
• paralleled tracks with current flowing in opposite directions - positive and
negative planes of the DC bus on top and bottom layers of the PCB and
overlapped as much as possible
• ground planes
• the use of shunt resistor Rshunt with a low intrinsic inductance
5. Lp7 represents the parasitic inductance located between the ground connections of
each gate driver (driver ground) and the ground connection of the application
controller (signal ground). This parasitic inductance introduces noise in the input
logic signals and the op-amp output analog signals. You can reduce this noise by
minimizing the distance between the signal ground and the driver ground (for each
gate driver in the system).
6. Connecting the signal ground to the three driver grounds through a star connection
improves the balance and symmetry of the three-phase driving topology.
7. It is also useful to ensure some distance between the lines switching with high
voltage transitions, and the signal lines sensitive to electrical noise. Specifically,
the tracks of each OUT phase carrying significant currents and high voltages
should be separated from the logic lines and analog sensing circuits of op-amps
and comparators.
36/51 DocID027840 Rev 1

AN4694 Practice case studies
6 Practice case studies
The main aspects in EMC-oriented PCB design are as summarized below.
6.1 Ground
• separate signal ground tracks from power ground tracks and connect with at a single
star connection directly on the shunt resistors
• wide ground traces reduce parasitic inductance
• fill unused board spaces with copper areas connected to the ground plane, especially
underneath all the high frequency IC (Figure 25: "Filled copper areas connected to
ground plane").
• when more than one power supply is required, separate the power and ground tracks
• when a multilayer PCB is used, implement a complete ground layer or place ground
traces in parallel with power traces to keep the supply clean
Figure 25: Filled copper areas connected to ground plane
DocID027840 Rev 1 37/51

Practice case studies AN4694
6.2 Power
• route parallel to ground on the same or adjacent layers to minimize loop area (Figure
26: "Routing supply and return traces")
Figure 26: Routing supply and return traces
• PCB planes or wide traces reduce parasitic inductance
• bypass capacitors (aluminum or tantalum) placed as close as possible to each IC and
IPM reduce the transient circuit demand on the power supply
• decoupling capacitors (with low ESR) placed as close as possible in parallel with the
bypass capacitor (Figure 27: "Example decoupling capacitor placement") reduce high
frequency switching noise on the power supply lines
• a 21 V Zener diode connected to each power supply pin prevents surge destruction
• a decoupling capacitor (with low ESR) in parallel with each bootstrap capacitor filters
high frequency disturbances
• a 21V Zener diode in parallel with each bootstrap capacitor prevents surge destruction
• a decoupling capacitor (with low ESR) in parallel with the electrolytic bulk capacitor
filters surge voltage; both capacitors should be placed as close as possible to the
power device (the decoupling capacitor has priority over the bulk capacitor)
• use low inductance shunt resistors for phase leg current sensing
• minimize the wiring length between the shunt resistor and power ground to avoid
malfunctions
• connect signal ground and power ground at only one point (near the terminal of the
shunt resistor) to avoid any malfunction due to power ground fluctuation
38/51 DocID027840 Rev 1

Figure 27: Example decoupling capacitor placement
6.3 Signal
• increase the distance between adjacent tracks and separate them to minimize
capacitance coupling interference
• place sensitive and high frequency away from high noise power tracks
• on double-layers boards, place signal and power tracks on the same side and ground
on the other
• do not use wire jumpers, minimize layer transitions for critical signal traces and keep
the same number of vias on each signal track where necessary
6.4 PCB
• group components according to their functionality (analog, digital, power, low-speed
and high-speed sections)
• place a filter at subsystem boundaries to promote signal flow between different
sections
• minimize the number of vias, especially in the high frequency signal tracks, as they
introduce parasitic impedance; distribute them around the PCB, avoiding
concentrations in small areas
• avoid right-angled track turns as these produce fields at the inner edge; 45° angled
tracks are preferable (Figure 28: "Example angled track")
• prefer star connections to stub connections, especially on critical signal tracks, as the
latter produces reflections
• keep a constant signal track width during the entire routing as variations change its
impedance and produce reflections
• unused pins cannot be unconnected and must be pulled-up or pulled-down
• respect current flow in layout design in EMI input filters
DocID027840 Rev 1 39/51

Figure 28: Example angled track
The following case studies reveal some examples of PCB layouts requiring improvement
and some enhanced design practices regarding EMC.
40/51 DocID027840 Rev 1

6.5 Case study 1
Figure 29: Case 1
1. ground tracks form a closed loop (white dashed line in Figure 29: "Case 1") which may
increase EMC problems by introducing noise into the ground (due to high voltage
switching tracks) and affect driver or application performance
2. the signal ground (SGND) of the IPM is connected away from the power ground
(PGND); all signal grounds must be connected in a star configuration to the power
ground
3. the shunt resistors are too far from the N-pins of the IPM and connected
asymmetrically (the net lengths are too dissimilar)
4. power ground tracks are too narrow; this may increase parasitic inductance
By implementing solutions such as rotating the IPM to improve the symmetry of the PCB,
the layout becomes the one shown in Figure 30: "Case 1 improved layout", where:
DocID027840 Rev 1 41/51

1. the ground path has been reshaped to remove any loops and increase the
width/length ratio of the tracks
2. the shunt resistor ground has been changed to a star point configuration for both
signal and power grounds
3. the shunt resistors have been relocated to guarantee shorter and symmetric
connections with the N pins of the IPM
Figure 30: Case 1 improved layout
42/51 DocID027840 Rev 1

6.6 Case study 2
Figure 31: Case 2
1. ground tracks form a loop (white dashed line in Figure 31: "Case 2") which may
increase EMC problems by introducing noise into the ground (due to high voltage
switching tracks) and affect driver or application performance
2. the signal ground (SGND) of the IPM is connected away from the power ground
(PGND); all signal grounds must be connected in a star configuration to the power
ground
3. the shunt resistor is too far from the N pins of the IPM
DocID027840 Rev 1 43/51

4. the power ground tracks are too narrow; this may increase parasitic inductance
The above layout can be improved by moving the bulk capacitor and shunt resistor closer
to each other as shown in Figure 32: "Case 2 improved layout", where:
1. the ground path has been reshaped to remove any loops and increase the
width/length ratio of the tracks
2. the shunt resistor ground has been changed to a star point configuration for both
signal and power grounds
3. the shunt resistor has been relocated to shorten connections with the IPM N pins
Figure 32: Case 2 improved layout
44/51 DocID027840 Rev 1

6.7 Case study 3
Figure 33: Case 3
1. the comparator ground for OCP (SGND) is too far from shunt resistor R14 (PGND)
and it crosses the SMPS power supply ground; finally, the comparator IC should be
closer to the shunt resistor and away from noisy tracks
2. the current sensing track should be connected directly to shunt resistor R14and the
filtering capacitor must be placed as close as possible to the comparator pin to reduce
the level of noise that could trigger false overcurrent protection
6.8 Case study 4
Figure 34: Case 4
DocID027840 Rev 1 45/51

1. separate the signal ground tracks from the power ground tracks and connect them at a
single point by using the shunt resistors in a star configuration; widen the power
ground track
2. jumpers on current sensing tracks should be avoided; the RC filter ground must be
connected to the IC comparator ground
3. the decoupling capacitor on the bus voltage should be connected between the P pin of
the IPM (as close as possible) and the power ground (on the shunt resistor)
6.9 Case study 5
Figure 35: Case 5
Figure 35: "Case 5" shows a PCB layout with decoupling capacitor C510 in parallel with the
bulk capacitor to absorb the charge from an ESD zap before it can accumulate on the IPM,
placed downstream of the device.
The effectiveness of the bypass capacitor can be improved by relocating it upstream of the
IPM (white lines in Figure 35: "Case 5") to detect the bus signal before it reaches the
device.
46/51 DocID027840 Rev 1

6.10 Case study 6
Figure 36: Case 6
Figure 36: "Case 6" shows a practical example of a layout using the discrete approach. It
represents the three-phase power stage section of the STEVAL-IHM021V1 demonstration
DocID027840 Rev 1 47/51

board, which includes three IC gate drivers (L6390), six IGBTs (or MOSFETs) in a DPAK
package and a bulk capacitor.
The fixed voltage tracks such as GND and HV lines can be used to shield the logic and
analog lines from the electrical noise produced by the switching lines (OUT1, OUT2 and
OUT3). Each half-bridge ground is connected in a star configuration and the three
RSENSE resistors are very close to each other and the power ground.
48/51 DocID027840 Rev 1

AN4694 References
7 References
[1] ST AN3353 – IEC 61000-4-2 standard testing
[2] ST AN1709 – EMC design guide for ST Microcontrollers
[3] ST AN2738 – L6390 half-bridge gate driver
[4] ST AN3338 – SLLIMM™
[5] ST AN4043 – SLLIMM™-nano
[6] Electromagnetic Compatibility (EMC) Part 4-2: Testing and Measurement Techniques—
Electrostatic Discharge Immunity Test (IEC 61000-4-2:2008 (Ed.2.0))
[7] Electromagnetic Compatibility (EMC) Part 4-4: Testing and Measurement Techniques—
Electrical Fast Transient/Burst Immunity Test (IEC 61000-4-4:2012 (Ed3.0))
[8] EN 55 014 European limits and methods of measurement of radio disturbance
characteristics of household appliances and power tools
DocID027840 Rev 1 49/51

Revision history AN4694
8 Revision history
Table 3: Document revision history
Date Revision Changes
05-Jun-2015 1 Initial release.
50/51 DocID027840 Rev 1