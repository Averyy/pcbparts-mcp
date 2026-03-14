---
source: "Infineon AN_2203 -- Gate Drive for Power MOSFETs"
url: "https://www.infineon.com/dgdl/Infineon-Gate_drive_for_power_MOSFETs_in_switchtin_applications-ApplicationNotes-v01_00-EN.pdf?fileId=8ac78c8c80027ecd0180467c871b3622"
format: "PDF 36pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 17510
---

# Gate Drive for Power MOSFETs in Switching Applications

A guide to device characteristics and gate drive techniques

Authors: Peter B. Green, Liz Zheng, Infineon Technologies

## About This Document

This application note provides a brief introduction to silicon power MOSFETs and explains their differences with bipolar power transistors and insulated-gate bipolar transistors (IGBTs). This is followed by a description of a basic MOSFET structure with emphasis on the gate to illustrate how the physical structure of the device determines the gate drive requirements. The subject matter deals with the switching operation of MOSFETs with a focus on the gate drive. Several different gate drive circuits and techniques are discussed, including discrete solutions and different types of gate driver ICs.

Intended for power engineers and students designing with power MOSFETs in switching power converters, with basic familiarity with MOSFETs but without in-depth knowledge and experience.

## 1. Introduction

### 1.1 MOSFET and IGBT Gate Drive vs. Bipolar Transistor Base Drive

Bipolar junction transistors (BJTs) use both majority and minority (electron and hole) charge carriers during conduction. They are current driven. To switch on a BJT, a current must be applied between the base and emitter terminals to produce a flow of current in the collector. A significant amount of base current is necessary to switch and conduct current in power applications.

Another disadvantage of power BJTs is the **second breakdown effect**, in which a transistor with a large junction area becomes subject to current concentration in a single area of the base-emitter junction. A localized hotspot is produced, which draws even higher current due to the device's negative coefficient of resistance, leading to thermal runaway and failure.

In contrast, MOSFETs and IGBTs are **voltage-controlled transconductance devices**. A voltage must be applied between the gate and source terminals to produce a flow of current in the drain. The gate is isolated electrically from the source by a layer of silicon dioxide, so ideally no current flows into the gate when a DC voltage is applied to it; in practice there is an extremely small current in the order of nanoamperes.

A key difference between MOSFETs and IGBTs is that IGBTs enter a low collector-emitter voltage saturation mode when fully switched on, unlike MOSFETs, which enter a drain-source resistive state in the "triode, linear or ohmic region". (Note: Linear region is different from linear mode. Operating in linear mode means in the saturation region not the ohmic region.)

### MOSFET Parasitic Components

When a voltage is applied between the gate and source terminals, an electric field is set up within the MOSFET channel region. This field "inverts" the channel, enabling current to flow from drain to source in enhancement mode (normally off) devices.

There are several parasitic capacitances associated with the power MOSFET:

- **CGS**: Capacitance due to the overlap of the source and the channel regions by the polysilicon gate, independent of applied voltage
- **CGD**: Two parts -- capacitance associated with the overlap of the polysilicon gate and the silicon underneath in the JFET region, plus capacitance associated with the depletion region immediately under the gate. A nonlinear function of voltage.
- **CDS**: Capacitance associated with the body-drift diode, varies inversely with the square root of the drain-source bias

Gate charge rather than capacitance is a more useful parameter from the circuit design point of view. Gate charge is defined as the charge that must be supplied to the gate, either to change the gate voltage by a given amount or to achieve full switching.

The positive temperature coefficient RDS(on) of approximately 0.7 to 1 percent per degree C makes MOSFETs suitable for parallel operation. Unlike bipolar power transistors, parallel connected MOSFETs tend to share the current evenly among themselves.

## 2. Gate Voltage Limits

The insulating silicon dioxide layer between the gate and the source regions can be punctured by exceeding its dielectric strength. Care should be taken to remain within both the positive and negative gate-to-source maximum VGS ratings quoted in the datasheet. It is also very important to observe ESD safe handling procedures.

Even when the applied gate voltage is maintained below the maximum rating, stray inductance in the gate connection coupled with the gate capacitance can generate ringing voltages. Overvoltages can also be coupled to the gate through CGD due to transients at the drain. **A gate drive circuit with low impedance is essential.**

Zener diodes rated at a voltage of no more than 80 percent of VGS(MAX) are sometimes connected between gate and source to clamp the voltage. However, these are not necessary when using modern gate driver ICs, and they can contribute to oscillations in some cases. Zener diodes are recommended when using pulse transformer gate drive circuits if the pulse transformer has significant leakage inductance.

### 2.1 Standard-level MOSFETs

VGS maximum positive and negative voltage limits are typically +20 V and -20 V. The VGS threshold VGS(TH) is typically between 2 and 4 V. The device RDS(on) rating is typically given for a VGS of 10 V. Standard levels are typically driven with 10 to 15 V gate pulses.

### 2.2 Logic-level MOSFETs

The key difference is that VGS(TH) is much lower, typically between 1.2 and 2.2 V. The maximum VGS ratings are still +20 and -20 V. Such devices can be driven with logic-level gate drive voltage, typically 5 V.

Logic-level devices have **higher gate charge** than standard-level parts of similar VBR(DSS) and RDS(on). Low gate threshold makes logic-level devices susceptible to induced turn-on caused by dVDS/dt in half-bridge configurations, which creates shoot-through currents and increased switching losses. **Standard-level devices are preferred for high-frequency switching applications.**

## 3. Gate Input Characteristics

### 3.1 Steady-state Behavior

Under steady-state conditions, a fixed DC voltage VGS is applied between gate and source. If VDS is below the pinch-off voltage (VDS < VGS - VTH), the device operates in the ohmic (triode or linear) region. If VDS exceeds the pinch-off voltage, it operates in the saturation region (i.e., in linear mode).

### 3.2 Dynamic/Switching Behavior

In most power circuits MOSFETs operate in switch mode. Each switch-on and switch-off event occurs during a defined period of time, in which the device state changes from blocking to conducting and vice-versa. The time required for these switching operations depends on the device gate charge characteristics and the gate drive sink and source current capability. PCB layout optimization is necessary to achieve correct switching behavior.

#### Switch-on Sequence (Hard Switching, Inductive Load)

- **Before t0**: Gate-to-source voltage is zero, drain current is zero, DUT supports full circuit voltage VDD
- **t0**: Switch opened, current flows to the gate, CGS starts to charge
- **t1**: VGS reaches threshold voltage VGS(TH), drain current starts to flow
- **t1 to t2**: CGS continues to charge, drain current rises proportionally. Freewheeling rectifier stays in conduction clamping drain to VDD
- **t2**: Drain current reaches ID, freewheeling diode ceases to conduct, drain potential begins to fall
- **t2 to t3**: Miller plateau -- VGS remains virtually flat while VDS falls. Gate current diverted to drain via CGD through the Miller effect (CGD * dVDS/dt)
- **t3**: Drain voltage falls to ID x RDS(on), DUT enters ohmic region
- **t4**: VGS rises to its maximum drive voltage VG

#### Parasitic Effects During Switching

In practical circuits, stray inductances are present in the source (LS) and drain (LD) current paths from MOSFET package leads, bond wires, and PCB traces:

- **Common source inductance (LS)**: Develops an induced voltage as source current increases, counteracting the applied VDRIVE and slowing the rate of rise of VGS. Creates negative feedback effect.
- **Drain inductance (LD)**: Causes reduction in drain-source voltage during switching, reflected across CGD drawing discharge current through it, increasing effective capacitive load.
- **Freewheeling diode reverse recovery**: The diode has a finite reverse recovery time trr.

#### Switch-off Sequence

At t0 VGS starts to fall until at t1 VDS starts to rise, reaching a Miller plateau level. Once VDS has transitioned to the bus voltage, VGS and ID start to fall until VGS falls below VTH where the MOSFET is fully switched off. The overshoot of VDS is caused by the reverse recovery of the MOSFET body diode acting on LD.

**Key principle**: MOS-gated transistors should be driven from low-impedance (voltage) sources, not only to reduce switching losses, but to avoid dv/dt-induced turn-on and reduce the susceptibility to noise.

## 4. Gate Drive Voltage and Current

### 4.1 Overview

Power MOSFETs have a defined gate charge QG, which must be supplied with sufficient current to raise VGS from zero to the required gate drive voltage (typically 10 V for a standard-level device):

    QG = integral(i(t) dt) from 0 to tON     ... [1]

Gate drive circuits supply a voltage through a resistance (external RGD + internal RG + driver output impedance RSRC):

    iG(t) = (VDRIVE - VGS(t)) / (RGD + RG + RSRC)     ... [2]

### 4.2 Gate Charge Measurements

Total gate charge QG is a key parameter for gate driver design. Example: For an IRF130 (100 V MOSFET), QG is 16 nC switching 80 V at 10 A. If 1 A is supplied to the gate, the switching time is 16 ns.

The relationship between bus voltage and Miller plateau length is not proportional because CGD varies in a non-linear function of voltage, decreasing as voltage increases.

Average gate drive power:

    PDRIVE = QG * VG * fsw     ... [3]

Example: 100 kHz switcher, QG = 27 nC, VG = 14 V: PDRIVE = 27 nC x 14 V x 100 kHz = 38 mW.

### 4.3 Gate Drive Circuit Design

Three basic gate drive circuits:

**Circuit A (Basic)**: A single resistor RG limits gate drive current and controls switching time. A pull-down resistor RGS (typically 10 kOhm) between gate and source is highly recommended so the MOSFET gate will be discharged if the gate becomes disconnected from the driver circuit.

**Circuit B (Switch OFF faster than switch ON)**: A diode blocks current through Rg_off during switch-on, but during switch-off the diode conducts through both Rg_off and Rg_on, enabling faster switch-off and stronger pull-down. Important in hard-switching half-bridge or full-bridge configurations to prevent C.dv/dt-induced turn-on.

**Circuit C (Switch ON faster than switch OFF)**: The diode is reversed so it conducts only during switch-on.

## 5. Ground-Referenced Gate Driver Circuit

### 5.1 Discrete Gate Drive Circuits

**BJT emitter follower**: Requires four small-signal BJT devices and three resistors. A level-shift stage converts a 3.3 V pulse to a 12 V pulse. Can provide gate drive output voltage above 11.4 V during on-time, pull-down below 0.6 V during off-time, and +/- 0.5 A sink and source currents.

**MOSFET gate drive circuit**: Requires fewer components -- three small-signal MOSFETs and two resistors. The output can swing from 0 to 12 V.

### 5.2 Gate Driver ICs

A single device in a SOT-23 package (e.g., IRS44273L) can replace discrete circuits and includes Schmitt trigger inputs and undervoltage lockout (UVLO), capable of sinking and sourcing up to 1.5 A.

More sophisticated gate driver ICs (e.g., 1ED44175N01B) provide additional features such as a current sense (CS) comparator and an enable/fault indicator pin for fast system protection.

Single-low-side and dual-low-side gate driver ICs are available with options for output current, logic configurations, packages and protection features such as UVLO, integrated overcurrent protection (OCP) and truly differential inputs (TDIs).

### 5.3 Truly Differential Inputs

The 1EDN7550/1EDN8550 gate driver ICs have TDIs. Their control signal inputs are largely independent from the ground potential. Only the voltage difference between its inputs determines the switching state of the gate driver output, which prevents false triggering of power MOSFETs due to parasitic inductances in the PCB layout.

## 6. Floating/High-side Gate Drive Circuits

In many topologies (buck regulators, half-bridge, full-bridge converters, multilevel converters), power MOSFET sources are not connected to circuit 0 V bus. A gate drive circuit is needed where the input signal can be referenced to 0 V but the output gate drive signal can be referenced to the MOSFET source terminal.

### 6.1 Pulse Transformer Gate Drive Circuits

A pulse transformer provides isolation for the high-side gate drive. A DC blocking capacitor is required to balance the transformer flux (volt-seconds) so that it will not saturate.

**Limitation**: Cannot be used with high duty-cycle pulses. As duty cycle increases, the positive voltage falls and the negative voltage rises to keep the volt-second product equal.

Gate drive pulse transformers must have high inductance to avoid high magnetizing current, and windings must be well coupled to minimize leakage inductance.

### 6.2 Half-bridge Gate Driver ICs

IC drivers (e.g., IR2101) accept logic-level signals at LIN and HIN inputs. The low-side gate drive output swings from 0 V to VCC; the high-side gate drive output switches between VS and VB, where VS is connected to the half-bridge switch node.

A dead time is introduced between switch-off of one MOSFET and switch-on of the other to prevent overlap (shoot-through). The bootstrap capacitor is charged to VCC through the bootstrap diode when the low-side MOSFET is on, providing a floating high-side supply voltage.

**Limitation**: Cannot operate at very high duty cycles because a minimum pulse width at LO is necessary to replenish the bootstrap capacitor.

Available from 100 to 1200 V maximum voltage ratings.

### 6.3 Junction Isolation (JI) IC Technology

The high-voltage integrated circuit (HVIC) technology uses patented monolithic structures integrating bipolar, CMOS and lateral DMOS devices with breakdown voltages above 700 and 1400 V. In some cases, the IC includes an internal HV bootstrap diode.

### 6.4 Silicon-on-Insulator (SOI) IC Technology

Each transistor is isolated by buried silicon dioxide, eliminating parasitic bipolar transistors that cause latch-up. SOI drivers feature rugged integrated ultra-fast bootstrap diodes. EiceDRIVER products using SOI technology have best-in-industry operational robustness and require very low charge for level shifting, enabling higher-frequency operations.

### 6.5 Isolated Gate Driver ICs

For galvanic isolation between PWM signals and MOSFETs. The EiceDRIVER 2EDi family provides functional (2EDFx) or reinforced (2EDSx) isolation using coreless transformer (CT) technology.

Isolated gate drivers require floating power supplies connected from VDDx to GNDx referenced to each MOSFET source. In complex applications such as multilevel converters, many separate floating power supplies are needed, typically via low-power flyback or fly-buck power supplies with multiple isolated outputs.

### 6.6 Configurable Gate Driver ICs (MOTIX 6EDL7141)

An advanced three-phase half-bridge driver IC for BLDC motor driver inverters, with configurable gate drive sink and source currents.

Features:
- SPI interface for configuration via GUI
- Gate drive current: 10 mA to 1.5 A for both source and sink
- Slew rate control via programmable time segments (TDRIVE1 through TDRIVE4)
- Driving voltage options: 7 V, 10 V, 12 V, 15 V (selectable via SPI)
- Full duty-cycle range up to 100% via charge pumps
- UVLO protection on gate drive outputs

### 6.7 Configuration of the Gate Driver

The MOTIX 6EDL7141 gate driver allows precise control of switching:

**Switch-on sequence:**
1. **TDRIVE1**: Pre-charge current (IPRE_SRC) applied for time TDRIVE1. MOSFET gate should reach VGS(TH).
2. **TDRIVE2**: Main switching current (IHS_SRC / ILS_SRC) applied. This determines dID/dt and dVDS/dt by supplying current to charge QSW.
3. **Full current**: After TDRIVE2, full 1.5 A applied for fastest full turn-on.

**Switch-off sequence:**
1. **TDRIVE3**: Pre-discharge current (IPRE_SNK) applied
2. **TDRIVE4**: Main discharge current (IHS_SINK / ILS_SINK) applied

This eliminates resistor-diode gate driver networks and enables precise tailoring of the gate drive to allow optimization during switching and in the off-state.

**Integrated pull-down features:**
- **Weak pull-down**: Always connected between gate and source when the gate driver is off
- **Strong pull-down**: Activated if the external gate-to-source voltage increases during gate driver off periods

## References

1. AN-937, Gate drive characteristics and requirements for HEXFET power MOSFETs
2. AN-944, Use gate charge to design the gate drive circuit for power MOSFETs and IGBTs
3. TI SLUA618A, Fundamentals of MOSFET and IGBT gate driver circuits
4. AN_2112, Designing with power MOSFETs (How to avoid common issues and failure modes)
