---
source: "TI SLVA680A -- ESD Protection Layout Guide"
url: "https://www.ti.com/lit/pdf/slva680"
format: "PDF 11pp"
method: "claude-extract"
extracted: 2026-02-16
chars: 17266
---

# ESD Protection Layout Guide

## Abstract

Successfully protecting a system against electrostatic discharge (ESD) is largely dependent on the printed circuit board (PCB) design. While selecting the proper transient voltage suppressor (TVS) founds the basis of an ESD protection strategy, its scope is not covered here. With the proper TVS selected, designing a PCB Layout that leverages the strategies outlined in this ESD Layout Guide will provide the PCB designer with an avenue towards successfully protecting a system against ESD.

## 1 Introduction

An ESD event rapidly forces current, I_ESD, into a system, usually through a user interface such as a cable connection, or a human input device like a key on a keyboard. Protecting a system against ESD using a TVS relies upon the TVS being able to shunt I_ESD to ground. Optimizing a PCB Layout for ESD suppression is largely dependant on designing the path to ground for I_ESD with as little impedance as possible. During an ESD event, the voltage presented to the protected integrated circuit (Protected IC), V_ESD, is a function of I_ESD and the impedance presented to it. Since the designer has no control over I_ESD, lowering the impedance to ground is the primary means available for minimizing V_ESD.

Lowering the impedance presents several challenges. Mainly, it cannot be of zero impedance, or the signal line being protected would be shorted to ground. In order for the circuit to have a realistic application, the protected line needs to be able to maintain some voltage, usually under a high impedance to ground. This is where the TVS becomes applicable.

A TVS is an array of diodes arranged to present a very high impedance to the voltages normally present in the circuit, but if voltages exceed the design, the TVS diodes will breakdown and shunt I_ESD to ground before it can damage the system being protected. The system designer is then challenged to lower the impedance for I_ESD from the ESD Source through the TVS to ground.

The impedance presented to I_ESD is a function of any impedance inherent with the TVS (in the diode array and the package of the TVS) and the PCB Layout between the ESD Source and the TVS ground. A TVS is generally designed to offer as low of an impedance to ground for I_ESD as its overall design constraints will allow. With the proper TVS selected, a critical phase of the design is to lower the impedance in the PCB Layout between the ESD Source and the TVS ground.

Another concern created by the rapidly changing I_ESD is its associated rapidly changing electromagnetic field (EM) causing interference (EMI) to couple onto other circuits of the PCB. This is especially true in the area between the ESD Source and the TVS. Once the TVS shunts I_ESD to ground, the trace between the TVS and the Protected IC should be relatively free of EMI. Therefore, unprotected circuits should not be adjacent to an ESD protected circuit's traces between the ESD Source and the TVS. In order to keep EMI emissions at a minimum, circuit traces between the ESD Source and the TVS should have corners which do not exceed 45 degrees or, ideally, which are curved with large radii.

In today's PCB Layout, board space is at a premium. ICs, including TVSs, are designed to be very compact. Also, the density of their placement on the PCB is continually increasing. Multiple layer PCB boards and routing lean heavily upon VIAs for maximizing the density to increase the system's feature set while decreasing the system's size. This PCB architecture, particularly related to layer switching and VIAs, plays an important role in shunting I_ESD to ground through the TVS. Large differences in V_ESD at the Protected IC can be induced by the manner in which the circuit is routed to the TVS using VIAs. Generally, placing a VIA between the ESD Source and the TVS is detrimental, but in some circumstances the designer is forced to do so. Even in these circumstances, if properly done, V_ESD can still be minimized at the Protected IC.

Grounding schemes are critical in protecting against ESD. Having a chassis ground for the TVS that is separated from the digital and/or analog ground by inductance provides very good protection against ESD related failures. Yet it presents great challenges when routing high speed circuits across multiple ground planes. For this reason, many designs use one common ground for the protected circuits. Ground planes are necessary for the TVS to have success in dissipating I_ESD without increasing V_ESD. Electrical connections to an earth grounded chassis, like a PCB grounded through-hole for a chassis screw, immediately adjacent to the TVS ground and the ESD Source's ground (for example, a connector shield) provide a sound methodology in keeping ground shifts at Protected ICs to a minimum. If a system cannot utilize a chassis earth ground, tightly coupled multiple layer ground planes can help keep ground shifts at Protected ICs to a minimum.

To summarize these parameters, successfully protecting a system against ESD includes:

- Controlling impedances around the TVS for dissipating ESD current, I_ESD
- Limiting the effects of EMI on unprotected circuits
- Properly using VIAs to maximize ESD dissipation by the TVS
- Designing a grounding scheme which has very low impedance for the TVS

## 2 PCB Layout Guidelines for Optimizing Dissipation of ESD

### 2.1 Optimizing Impedance for Dissipating ESD

Outside of controlled RLC values, PCBs have inherent parasitics which contribute to overall board performance. Usually these parasitics are detrimental to the functionality of the design. An important parasitic to consider when designing a circuit to dissipate ESD is inductance. Because V_ESD = V_br_TVS + R_DYN(TVS) * I_ESD + L * (dI_ESD/dt), and the term dI_ESD/dt is very large, the forced current in an ESD event will cause large voltages to drop across any inductance. For example, in an 8 kV ESD event as specified by IEC 61000-4-2, the dI_ESD/dt = (30 A) / (0.8 x 10^-9 s) = 4 x 10^10 A/s. So even with 0.25 nH of inductance an additional 10 V is presented to the system.

Note:
- V_br_TVS is the voltage required for the TVS to enter its breakdown region and begin shunting I_ESD to ground.
- R_DYN(TVS) refers to the resistance through the TVS diode array while operating in the breakdown region of the IV curve.

In Figure 2-1, four parasitic inductors are shown: L1 and L2 is the inductance in the circuit between the ESD Source (typically a connector) and the TVS, L3 is the inductance between the TVS and ground, and L4 is the inductance between the TVS and the Protected IC. Not considering VIAs, the inductors L1 and L4 are generally dependant upon design constraints such as impedance controlled signal lines. However, I_ESD can still be "steered" towards the TVS by making L4 much larger than L1. This is accomplished by placing the TVS as near to the ESD Source as the PCB design rules allow while placing the Protected IC far away from the TVS, for example near the middle of the PCB. This effectively creates L4 >> L1, helping shunt the I_ESD to the TVS. Placing the TVS adjacent to the connector also mitigates EMI from radiating into the system. The inductor shown at L2 should not be present in a well designed system. This represents a stub between the TVS and the line being protected. This design practice should be avoided. The Protected Line should run directly from the ESD Source to the protection Pin of the TVS, ideally with no VIAs in the path. The inductor at L3 represents the inductance between the TVS and ground. This value should be reduced as much as possible, and perhaps represents the most predominant parasitic influencing V_ESD. The voltage presented to the node "Protected Line" will be V_ESD = V_br_TVS + I_ESD * R_DYN(TVS) + (L2 + L3) * (dI_ESD/dt). Thus the PCB designer needs to minimize L3 and eliminate L2. Minimizing L3 is covered in Section 2.4. Minimizing L1 is covered in Section 2.2 and Section 2.3.

Summary:
- Minimize any inductance between the ESD Source and the path to ground through the TVS
- Place the TVS as near to the connector as design rules allow
- Place the Protected IC much further from the TVS than the TVS is to the connector
- Do not use stubs between the TVS and the Protected Line, route directly from the ESD Source to the TVS
- Minimizing inductance between the TVS and ground is critical

### 2.2 Limiting EMI from ESD

Fast transients like ESD with high di/dt can cause EMI without proper steps for suppression. For ESD, the primary source of radiation will be in the circuit between the ESD Source and the TVS. For this reason, the PCB designer should consider this region a Keep-Out area for unprotected PCB traces which could damage the system by either having direct contact with an IC, or by carrying the EMI further into the system where it could radiate more EMI. Even with no inductance at L1 (as shown in Figure 2-1) the rapidly changing electric field during ESD can couple onto nearby circuits, resulting in undesired voltages on unintended circuits. Having any induction at L1 amplifies the EMI.

Figure 2-2 shows an unprotected line running adjacent to a protected line between the ESD Source and the TVS. This practice should be avoided. During an ESD event there will be a large dI_ESD/dt between the ESD Source and the TVS. The traces on this path will radiate EMI and any nearby traces could have a current induced in them by the EMI. If these traces have no TVS protecting them, the induced current in the unprotected line can cause system damage.

If there are any VIAs on the protected line between the ESD Source and the TVS, these same principles apply to any layer the VIA crosses -- no unprotected lines should be run adjacent to the VIA.

Another aspect of PCB Layout to consider is the style of the corners between the ESD Source and the TVS. Corners tend to radiate EMI during I_ESD. The best method of routing from the ESD Source to the TVS is using straight paths which are as short as possible. Beyond lowering the impedance in the path to ground for I_ESD, shortening the length of this path also reduces the EMI being radiated inside the system. If corners are necessary, they should be curved with the largest radii possible, with 45 degree corners being the maximum angle if the PCB technology does not allow curved traces.

In Figure 2-3, note that for a 90 degree corner, the corner is a strong source of EMI. The electric field at the corner is at least 7 kV. This will lead to an electric arc (ionization) for any radius less than about 2.6 mm (in air). The EMI for the 45 degree and curve are much less pronounced.

Summary:
- Do not route unprotected circuits in the area between the ESD Source and the TVS.
- Place the TVS as near to the connector as design rules allow.
- Route with straight traces between the ESD Source and the TVS if possible.
- If corners must be used, curves are preferred and a maximum of 45 degrees is acceptable.

### 2.3 Routing with VIAs

It is best to route traces on the PCB from the ESD Source to the TVS without switching layers by VIA. Figure 2-5 shows two examples. In Case 1, there is no VIA between the ESD Source and the TVS, so that I_ESD is forced to the TVS protection pin before the VIA in the path to the Protected IC. In this case the VIA represents L4 shown in Figure 2-1. In Case 2, I_ESD branches between the Protected IC and the VIA to the TVS protection pin. In this case the VIA represents L2 in Figure 2-1. This practice should be avoided. The inductance of the VIA is between the TVS and the path from the ESD Source to the Protected IC. This has two detrimental effects: Since current seeks the path to ground with the least impedance, the Protected IC may take the brunt of the current in I_ESD and any current that does pass through the VIA will increase the voltage presented to the Protected IC by L_VIA * (dI_ESD/dt).

There may be cases where the designer has no choice but to place the TVS on a different layer than the ESD Source. Figure 2-6 shows Case 3, a variation to Case 2. In Case 3, I_ESD is forced to the protection pin of the TVS before I_ESD has a path to the Protected IC. This is an acceptable compromise to Case 2.

These three cases represent examples when VIAs are used between the ESD Source and the Protected IC. It is best to avoid this practice, but if necessary Case 1 is the preferred method, Case 2 should be avoided, and Case 3 is acceptable if there is no alternative.

Summary:
- Avoid VIAs between the ESD Source and TVS if possible
- If a VIA is required between the ESD Source and the Protected IC, route directly from the ESD Source to the TVS before using the VIA

### 2.4 Optimizing Ground Schemes for ESD

Successfully eliminating all the parasitic inductance between the ESD Source and the TVS will not be effective without a very low impedance path to ground for the TVS. The TVS ground pin should connect to a same layer ground plane that is coupled with another ground plane on an immediately adjacent layer. These ground planes should be stitched together with VIAs, with one VIA immediately adjacent to the ground pin of the TVS.

Figure 2-7 shows the PCB Inductance around a single-channel TVS (as shown earlier in Figure 2-1). This section considers only the inductance at L3. Recall that, with L2 eliminated, the voltage presented to the Protected IC during an ESD event will be V_ESD = V_br_TVS + I_ESD * R_DYN(TVS) + L3 * (dI_ESD/dt) and for 8 kV, dI_ESD/dt = 4 x 10^10. Clearly, L3 must be lowered as much as possible.

To lower L3, the TVS ground pin would ideally connect directly to a coupled ground plane. Figure 2-8 shows the ground pad of a TVS connected to the top layer ground plane. There are four stitching VIAs connecting the top layer ground plane to an internal ground plane. These could connect more than one ground plane layer depending on the layer count and board design. A grounded chassis screw is located very near to the TVS ground pad as well. A grounding scheme resembling this yields a very low impedance to ground for L3.

Figure 2-8 is not relevant for some types of TVSs due to package types. Those with BGA packages which have the ground pin surrounded by other pins will need to VIA to an internal ground plane, preferably to multiple, coupled ground planes.

VIAs need to be constructed to offer as little impedance as possible. Due to the skin effect, maximizing the surface area of the GND VIA minimizes the impedance of the path to ground. For this reason make both the VIA pad diameter and the VIA drill diameter as large as possible, thus maximizing the surface area of the outside of the VIA surface and the inside of the VIA surface. The ground plane should not be broken in the vicinity of the GND VIA. If possible, attaching the GND VIA to a ground plane on multiple layers minimizes the impedance. The GND VIA should be filled with a non-conductive filler (like epoxy) as opposed to a conductive filler, in order to keep the surface area of the inside of the VIA created by the drill. The GND VIA should be plated over at the SMD pad. Clearances between the GND VIA and non-ground planes (for example, power planes) should be kept at a minimum. This increases capacitance which lowers impedance.

## 3 Conclusion

Designing ESD protection into a system can be successful with the proper techniques applied. Following these ESD layout guide outlines will ensure the TVS has optimum conditions for dissipating the ESD.

In summary:

- Control Impedances around the TVS for dissipating ESD current, I_ESD:
  - Minimize any inductance between the ESD Source and the path to ground through the TVS
  - Place the TVS as near to the connector as design rules allow
  - Place the Protected IC much further from the TVS than the TVS is to the connector
  - Do not use stubs between the TVS and the Protected Line, route directly from the ESD Source to the TVS
  - Minimizing inductance between the TVS and ground is critical
- Limit the effects of EMI on unprotected circuits:
  - Do not route unprotected circuits in the area between the ESD Source and the TVS
  - Place the TVS as near to the connector as design rules allow
  - Route with straight traces between the ESD Source and the TVS if possible
  - If corners must be used curves are preferred and a maximum of 45 degrees is acceptable
- Properly use VIAs to maximize ESD dissipation by the TVS:
  - Avoid VIAs between the ESD Source and the TVS if possible
  - If a VIA is required between the ESD Source and the Protected IC, route directly from the ESD Source to the TVS before using the VIA
- Use a grounding scheme that has very low impedance:
  - Connect the TVS Ground Pin directly to a same layer ground plane that has nearby VIAs stitching to an adjacent internal ground plane
  - Use multiple ground planes when possible
  - Use a chassis screw, connected to PCB ground, near to the TVS and ESD Source (for example, the connector ground shield)
  - Use VIAs of large diameter with a large drill, which lowers impedance
