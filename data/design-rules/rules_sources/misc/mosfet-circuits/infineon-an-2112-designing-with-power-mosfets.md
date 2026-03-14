---
source: "Infineon AN_2112 -- Designing with Power MOSFETs"
url: "https://www.infineon.com/assets/row/public/documents/24/42/infineon-designing-with-power-mosfets-applicationnotes-en.pdf"
format: "PDF 27pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 16495
---

# Designing with Power MOSFETs

How to avoid common issues and failure modes

Author: Peter B. Green, Infineon Technologies

## About This Document

In common with all power semiconductor devices, power MOSFETs have their own technical strengths, weaknesses and subtleties, which need to be properly understood if the designer is to avoid reliability issues. This application note discusses some of the most common dos and don'ts of using power MOSFETs. The objective is to help the system designer understand how to use these devices correctly and avoid common mistakes, thereby reducing design time.

Intended for power engineers and students designing with power MOSFETs, with basic familiarity with MOSFETs but limited experience of designing with them.

## 1. Introduction to Power MOSFETs

Power MOSFETs were first introduced in the 1970s, and became the most widely used power transistors in the world. They offer many advantages over older technologies such as bipolar power transistors in both linear and switching applications, including greatly improved switching, easy paralleling capability, the absence of the second breakdown effect, and a wider safe operating area (SOA). MOSFETs are voltage-driven transconductance devices.

The differently doped layers of silicon fall into two broad technology categories: **planar** and **trench**.

- Infineon **OptiMOS** devices are based on trench technology
- **CoolMOS** devices are based on superjunction, an enhancement of planar technology enabling lower on-resistance

The topics in this application note are applicable to all silicon power MOSFET technologies, but may not apply to other devices such as IGBTs, SiC FETs or GaN HEMTs. The focus is on N-channel enhancement mode devices.

Although power MOSFETs may initially appear to be simple three-terminal voltage-driven switches, this is misleading. A solid understanding of the basic characteristics and behavior is essential before embarking on any design project.

## 2. Handling and Testing Power MOSFETs

Being MOS devices with very high gate impedance, power MOSFETs can be damaged by static discharge during handling, testing or installation. ESD damage typically occurs when the gate-to-source voltage is high enough to arc across the gate dielectric, burning a microscopic hole in the gate oxide and causing the part to fail immediately or later during operation.

**Handling precautions:**
- Leave devices in anti-static shipping bags, conductive foam, or metal containers until needed
- Handle by the package, not by the leads
- Use electrically conductive floor mats and grounded anti-static mats at test stations
- Do not apply voltage until all terminals are solidly connected
- Use a 100 ohm series gate resistor on curve tracers to damp spurious oscillations
- Use grounded soldering irons

## 3. Reverse Blocking Characteristics

All power MOSFETs are rated for a maximum reverse voltage, VBR(DSS). If the drain-to-source voltage exceeds this threshold, high electric fields across reverse biased p-n junctions create electron-hole pairs through impact ionization, causing the **avalanche effect** -- uncontrolled current multiplication, high power dissipation, rapid temperature rise and potential device destruction.

Avalanche typically occurs due to **unclamped inductive switching (UIS)**, where the part is being used outside of its datasheet specification. The designer should make all reasonable attempts NOT to operate a MOSFET in avalanche.

The datasheet VBR(DSS) rating is the minimum value over process variations. VBR(DSS) increases slightly with temperature.

### 3.1 Avalanche Failure Mechanisms

#### 3.1.1 Latch-up

The avalanche event generates a drain current that will be greater where the electric field has greater intensity. This triggers the parasitic NPN bipolar junction transistor within the MOSFET. If the current through the base resistor produces sufficient voltage, the bipolar transistor turns on uncontrollably, potentially causing damage. Infineon has mitigated latch-up in many OptiMOS technologies, but this is not the case for all MOSFET technologies.

#### 3.1.2 Thermal Failure

Occurs when the junction temperature reaches Tj,destr (close to the intrinsic temperature of silicon, typically ~400 deg C for OptiMOS families). This is responsible for the majority of avalanche failures, even for technologies prone to latch-up.

### 3.2 Avalanche Testing

MOSFET avalanche withstand capability is tested by means of a single-pulse UIS test circuit. A pulse of defined duration is applied to the MOSFET gate to switch the device on so that the drain current rises linearly due to the series inductor. The MOSFET is then switched off, producing a voltage transient above VBR(DSS) so that the inductor energy is transferred into the MOSFET during avalanche.

### 3.3 Single and Repetitive Avalanche Conditions

**Single-pulse avalanche**: A defined maximum amount of avalanche energy (EAS) that the MOSFET can withstand. Should only occur once, particularly near the limits, because conditions correspond to junction temperatures above Tj,max which would impair operating lifetime.

**Repetitive avalanche**: Events occur continuously at the switching frequency. The safe energy per event is much lower than for single-pulse. Exceeding Tj,max during repetitive avalanche has a cumulative effect, risking reduced reliability over the device's lifetime. Even low-energy avalanche events generate hot carriers that accumulate along the trench oxide, slowly impairing reliability.

**Important**: Tj,max can be as low as 150 deg C for parts in QFN 5x6 (SuperSO8) or S3O8 packages (a package limitation, not silicon). The same die in TO-220 or D2PAK may be rated at 175 deg C.

Infineon does not insert repetitive avalanche ratings within OptiMOS "Industrial and Standard Grades" datasheets.

### 3.4 How to Avoid Avalanche

1. **Select the right VBR(DSS) rating**: The maximum steady-state voltage under worst-case conditions should have a safety margin of at least 20%. In motor drive inverters, it is not unusual to select a MOSFET with VBR(DSS) of twice the DC bus voltage.
2. **Do not over-specify**: A part with a higher rating than needed gives higher RDS(on) and probably costs more.
3. **Slow down the MOSFET switch-off** by adjusting the gate drive network.
4. **Add RC snubbers** between drain and source (creates additional switching losses).

Gate drive circuits can be configured to control switch-on and switch-off speeds independently:

- **Equal timing (basic)**: Single resistor Rg
- **Faster switch-off**: Diode in parallel with Rg_off allows stronger pull-down during off
- **Faster switch-on**: Diode reversed for faster on

## 4. MOSFET Current Ratings and Heatsinking

The continuous drain current rating ID(MAX) that appears on a MOSFET datasheet **does not represent the current at which the device can be operated in a practical system**. Such ratings are based on ideal test conditions not achievable in a practical design. Different manufacturers use different criteria, and it is therefore **a mistake to rely on these ratings to compare different devices**.

A more realistic approach: compare **RDS(on) at 25 deg C** as a common basis, then consider junction-case thermal resistance **RthJC** to determine true current-handling capability.

Most SMD packages are bottom or back-side cooled: heat passes through the drain tab to the PCB, which needs thermal vias underneath the drain pad. There are also top-side cooled packages (e.g., TOLT package).

The heatsink must be sized to maintain a safe junction temperature. The junction-to-ambient thermal resistance is calculated by adding all series thermal resistances (PCB, thermal insulation material/TIM, heatsink).

## 5. Gate-to-source Voltage Transients

Excessive voltage transients can punch through the thin gate-source oxide layer and result in permanent damage. During switch-on or switch-off, a high dVDS/dt is produced which, combined with parasitic inductances in gate, source and drain leads, and the MOSFET CGD (Miller capacitance), produces transient voltages between gate and source.

**Mitigation:**
- The ratio of CGS/CGD (or equivalently QGD/QGS) must be as high as possible to minimize drain-to-source voltage coupling
- Optimize PCB layout to reduce parasitic inductance
- Small gate-source capacitors can help reduce spikes (but slow down switching)
- Charge ratios: QGD/QGS of 0.5 to 0.8 and QGD/QGS(TH) less than 1.0 is recommended for hard switching applications

## 6. Safe Operating Area (SOA)

Modern power MOSFETs have focused on fast switching with ultralow RDS(on), reducing die area. The power-handling capabilities for a specific RDS(on) have therefore generally decreased, especially in linear operation mode. When designing with power MOSFETs, it is **essential to pay close attention to the SOA diagram** and ensure that the device will never be operated outside the defined limit-lines.

### 6.1 RDS(on) Limit

Dictated by Ohm's law for a specific VDS at VGS = 10 V and Tj = 150 deg C. At lower temperatures, a higher drain current is possible.

### 6.2 Maximum Operating Current Limit

Defines the maximum current-handling capability of the **package** (bond wires, clip dimensions). Does not change with temperature.

### 6.3 Power Limit

Calculated from the maximum power the device is permitted to dissipate that produces a stable junction temperature Tj of 150 deg C at TC = 25 deg C, considering junction-to-case thermal impedance ZthJC.

For short pulses, ZthJC depends on pulse length and duty cycle. An increased pulse duration shifts the maximum thermal limit-line downward.

### 6.4 Thermal Stability Limit

Also known as the **Spirito effect**: thermal instability where power loss rises more rapidly than power dissipation with respect to temperature, so thermal equilibrium cannot be achieved. Current crowding in hotter cells causes thermal runaway.

Thermal instability occurs when:

    dP_generated/dT > dP_dissipated/dT     ... [1]

This occurs when VGS is below the **zero-temperature coefficient (ZTC) point**. Modern power MOSFETs exhibit ever-increasing transconductances and therefore ZTC points at higher VGS. To avoid failures, ensure the SOA thermal stability limit will not be violated.

### 6.5 Breakdown Voltage

Represents the device VBR(DSS) rating.

## 7. Induced Turn-on and Shoot-through

Induced turn-on occurs when MOSFETs are used in fast-switching applications where high dVDS/dt transitions appear at the drain while the device is in the off-state. Typical in hard-switching half-bridge configurations.

When the low-side MOSFET switches off and the high-side switches on, the HB node transitions rapidly from zero volts to VBUS. This "C.dv/dt" causes a current pulse to couple through CGD to the gate, inducing a voltage spike. If this exceeds the MOSFET VTH, the device partially turns on, creating a high shoot-through current that can violate SOA limits and destroy one or both devices.

Note: The MOSFET may have significant internal gate resistance RG(INT), so the induced gate spike at the silicon may be larger than observed at the gate terminal.

### 7.1 How to Avoid Induced Turn-on

1. **Select MOSFETs with higher CGS/CGD ratio**: Lower QGD/QGS and QGD/QGS(TH). A QGD/QGS of 0.5 to 0.8 and QGD/QGS(TH) < 1.0 is recommended for hard switching.
2. **Slow down the switching transition**: Increase Rg_on on the high-side device (reduces dv/dt).
3. **Use "switch off faster than switch on" gate drive network**: Diode + resistor for strong pull-down.
4. **Add external gate-to-source capacitor**: Increases effective CGS/CGD ratio but slows switching.
5. **Use smart gate driver ICs** (e.g., MOTIX 6EDL7141) with programmable gate current.

## 8. Body Diode

The body diode is intrinsic to the MOSFET structure, formed by the p-n junction between p-body and n-epi layers. Power MOSFETs are three-terminal devices where the body and source are connected internally. The body diode exhibits minority carrier reverse recovery with a finite reverse recovery time (trr) and reverse recovery charge (Qrr).

### Reverse Recovery in Half-bridge Circuits

In a synchronous buck regulator operating in continuous conduction mode (CCM), when Q1 switches on, the body diode of Q2 must undergo reverse recovery. If Q1 switches on too rapidly, the peak reverse recovery current of Q2's body diode will rise too rapidly, potentially destroying the device.

**Mitigation:**
- Select devices with appropriate body diode ruggedness (e.g., Infineon CoolMOS CFD family with fast-recovery body diodes)
- Slow down the rate of change of current during commutation by slowing the gate driving pulse
- At frequencies up to ~20 kHz, this is a practical solution
- At higher frequencies, careful attention to voltages, currents, device selection and gate drive scheme is essential

## 9. Package and Board Layout Considerations

Different packages have different parasitic inductances. Leaded packages have higher inductances than SMD packages. Where high currents are switched in hard commutation, an SMD package with lowest possible inductance and a well laid-out PCB are required.

Stray inductance increases overvoltage transient amplitude:

    VDS = LS * (diD/dt)     ... [5]

where LS is determined by the current loop from the bus decoupling capacitor through the switching elements and back.

**PCB layout optimization:**
- Place MOSFETs as close to each other and the DC bus decoupling capacitor as possible
- Use two or more copper layers, placing the return current path directly underneath the current path
- Reserve one or more copper layers for a power ground plane
- Keep signal/digital grounds and power grounds separated ("ground bounce" prevention)
- Join power and signal grounds at one point, preferably the decoupling capacitor ground connection
- Use multiple thermal vias underneath the drain pad to transfer heat through to the bottom of the board
- Follow manufacturer's recommended device footprint and soldering guidelines

## 10. Paralleling of Power MOSFETs

### Steady-state Current Balancing

Achieved because RDS(on) has a positive temperature coefficient. If one device conducts more current, its die temperature rises, raising RDS(on) and diverting current to other parallel devices. Devices should be placed close together with similar copper trace lengths and widths.

### Dynamic Current Balancing

More challenging under switching conditions, and more so at higher frequencies. Mis-matches in the following parameters affect current sharing: VTH, gfs, CGS, CGD, Qrr, and RDS(on).

**PCB layout requirements:**
- Gate loop and current path inductances must be as similar as possible
- Circuit layout should be as symmetrical as possible
- Gates of parallel connected devices may be decoupled by small ferrite beads or individual series resistors to prevent parasitic oscillations
- **Each parallel MOSFET should have its own gate drive network** placed between the gate and the shared connection to the gate driver

## 11. Conclusion

Designing power conversion systems based on MOSFETs requires careful consideration of the trade-offs between switching speed and losses, turn-off transients that may cause avalanching, remaining within the different SOA limits, and the reverse recovery of the body diode.

Steps:
1. Choose the best-suited device and heatsinking arrangement
2. Optimize the gate drive to balance switch-off transients and body diode stress against switching losses
3. Optimize the PCB layout to minimize parasitic inductance in the high-current switching path

## References

1. AN-936A, The dos and don'ts of using MOS-gated transistors, Brian R. Pelly
2. AN-1084, Power MOSFET basics, Vrej Barkhordarian
3. AN-955, Protecting IGBTs and MOSFETs from ESD
4. AN-1005, Power MOSFET avalanche design guidelines
5. AN_201611, Some key facts about avalanche, Olivier Guillemant
6. AN_201709, A new approach to datasheet maximum drain current ID rating
7. AP99007, Linear mode operation and safe operating diagram of power MOSFETs
8. AN_201403, Hard commutation of power MOSFETs, Alan Huang
9. Paralleling of power MOSFETs for higher power output, James B. Forsythe
