---
source: "Wurth ANE009 -- Production Guide USB 3.1 Type C (Connector Footprint)"
url: "https://www.we-online.com/components/media/o563289v410%20ANE009a_EN.pdf"
format: "PDF 17pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 15196
---

# Production Guide: USB 3.1 Type C

## 1. Introduction

USB-C now offers different connector variants ranging from USB 2.0 in Type-C housing to Type-C for a 10 GBit data rate. The housing variants have also become more diverse. From the horizontal hybrid type to vertical variants and the mid-mount type, which is placed in a PCB cutout. All these types have their special characteristics, which in many cases may already have to be taken into account in the layout to ensure problem-free manufacturing is possible afterwards. We would like to shed light on these points and identify ways of dealing with the challenges. The PCB itself and its manufacture cannot be left out of the equation either, as it has certain limitations that should be taken into account in order to achieve the best possible result. Once all this has been done, it is a matter of controlling the manufacturing process in its various steps from stencil printing to the soldering oven and optimizing the parameters, so that the slender type-C connectors can also be processed in a way suitable for series production.

## 2. Process Parameters for the USB-C Connectors

The USB-C product portfolio from Wurth Elektronik eiSos includes the plug, receptacle connectors, fastening elements (spacers) as well as USB-C cable without eMarker labeling. The aim of this Production Guide is to show the relevant process parameters and to depict the ideal production process by means of practical recommendations. The respective connectors have different requirements for the production materials as well as for the production process itself.

To illustrate this, let's start with the parameter table. It provides an overview of the product portfolio and the relevant process parameters. In the following sections, each product family is examined in more detail. Here, dimensioned stencil drawings are displayed and the production process is described step by step.

At the end of the document in the appendix you will find the basis for calculation and formulas for the THR (through-hole reflow) process.

### Product Family Overview

| Parameter | Plug Horizontal SMT 0.8mm | Plug Horizontal 0.8mm THR/SMT | Receptacle Horizontal THR/SMT | Receptacle Horizontal Mid-Mount | Receptacle Vertical SMT 1.0mm |
|---|---|---|---|---|---|
| Article no. | 632712000011 | 632712000112 | 632723100011, 632723300011 | 632723130112 | 632722110112 |
| Pins | 22 | 24 | 24 | 24 | 24 |
| PCB thickness | 0.8 mm | 0.8 mm | 1.00 / 1.60 mm | 1.60 mm | - |
| Mounting | SMT | SMT | SMT / THR | SMT / THR | SMT |
| Stencil thickness | 100 um | 100 um | 100 um | 100 um | 100 um |
| Electropolished | yes | yes | yes | yes | yes |
| Nano-coated | no | no | yes | yes | no |
| Grain size solder paste | 4 | 4 | 5 | 5 | 4 |
| Print speed | 40 mm/s | 40 mm/s | 20 mm/s | 20 mm/s | 40 mm/s |
| Squeegee force | 50 N | 50 N | 70 N | 70 N | 50 N |
| Squeegee angle | 60-67 deg | 60-67 deg | 45 deg | 45 deg | 60-67 deg |
| Squeegee type | Metal | Metal | Plastic | Plastic | Metal |
| Print cycles | 1 | 1 | 2 | 2 | 1 |
| Additional solder depot | no | no | yes | yes | yes |
| Assembly speed | Standard | Standard | Reduced to minimum | Reduced to minimum | Standard |
| Automatic assembly | Partially automated | Partially automated | yes | yes | yes |
| Solder profile | IPC / JEDEC J-STD-020E | IPC / JEDEC J-STD-020E | IPC / JEDEC J-STD-020E | IPC / JEDEC J-STD-020E | IPC / JEDEC J-STD-020E |
| Flow direction | - | - | Connector face or pins first | Connector face or pins first | - |
| Inspection | AOI | AOI | AOI / XRAY | AOI / XRAY | AOI |

## 3. Processing the USB-C Plug

The USB-C plug connector is not a classic connector assembled onto the PCB, but this component is shifted to the edge of the PCB. As a result, its component pads are located both on the underside and on the topside of the PCB. This poses a major challenge for effective and cost-effective process design. In order to achieve this, some adaptations are required in the stencil design as well as the production of a solder deposit on the underside of the PCB.

### 3.1 Stencil Recommendation

**Underside of the PCB:**
- Reduce the stencil opening by 4% circumferentially relative to the pad (as an oblong opening)
- Create a solder depot on the underside of the PCB with this first process step

**Topside of the PCB:**
- Reduce the stencil opening in the pad area to a width of 0.20 mm (pad width 0.30 mm)
- Place the stencil opening to the back by 1/3 of the pad length relative to the start of the pad (overprinting on the solder resist is intended and is important for the soldering process)
- The reduction in width and the shift of the stencil opening prevents excessive extrusion of paste during the assembly process. The risk of short-circuiting is thus significantly reduced.

Figure 1: Stencil recommendation of the USB-C Plug for the topside of the PCB

### 3.2 Assembly Process

1. If possible: Carry out solder paste printing on the underside of the PCB. With this process step, a solder deposit can be created (according to stencil recommendation for the underside of PCB in section 3.1).
2. Reflow soldering of the underside of the PCB.
3. Solder paste printing of the topside of the PCB using the stencil recommendation shown in Figure 1.
4. Assembly of the USB-C plug (whether automatic or manual assembly is possible depends on the production equipment).
5. During the reflow soldering process, it is important that the USB-C enters the reflow oven with the connector face or pin row first. This prevents the USB-C from bending. This bending can occur if the solder paste of the pin row does not melt simultaneously.
6. AOI (automatic optical inspection)

Figure 2: IPC-compliant soldered component connections on the topside of the PCB

Figure 3: IPC-compliant soldered component connections on the underside of the PCB

## 4. Processing the USB-C Receptacle Hybrid

In USB-C hybrid variants, the 24 contacts are made up of twelve SMT and twelve THR contacts. In addition, there are four more housing pins in THR design. The mix of SMT and THR contacts confers significant mechanical advantages. The most decisive factors here are significantly higher retention forces on the PCB compared to a fully SMT design and minimization of soldering problems as a result of insufficient coplanarity of the consecutive rows of pins. The pin mix and the very compact design of the USB-C hybrid type means it is a challenge to get enough solder paste around the THR pad as well as into its hole.

### 4.1 Solder Paste Print Parameters

- Use solder paste with a grain size of 5.
- Implementation of a second printing process (i.e. a second printing cycle immediately follows the first without lifting the stencil from the PCB). This favors greater penetration of the solder paste into the depth of the hole.
- Reduce printing speed to 20 mm/s (typically 40 mm/s).
- Increase squeegee force to 70 N (typically 50 N).
- Do not use a standard squeegee with an angle between 60-67 deg, but a squeegee with a 45 deg angle. This is necessary to transport the maximum amount of solder paste into the depth of the hole. If possible, a plastic squeegee is also recommended here (this has the property of preloading the stencil a little more).

### 4.2 Stencil Recommendations

Figure 4: USB-C hybrid shown as Altium element incl. stencil recommendation for the underside of the PCB

Figure 5: Dimensioned stencil openings of the underside of the PCB

Figure 6: USB-C hybrid shown as Altium element incl. stencil recommendation for the topside of the PCB

Figure 7: Dimensioned stencil openings of the topside of the PCB

### 4.3 Assembly Process

1. If possible: Provide for solder paste printing on the underside of the PCB. Please use the stencil recommendation shown in Figs. 4 and 5. This process step can be used to create a solder deposit on the underside of the PCB. However, it must be ensured that no solder paste enters the hole. This would make it difficult or even impossible to assemble the USB-C later in the process.
2. Reflow soldering of the underside of the PCB.
3. Solder paste printing of the topside of the PCB using the stencil recommendation shown in Figs. 6 and 7. It is recommended to carry out a print check for prototypes, initial series and production starts. The solder paste print is optically inspected and measured. The filling level of the paste after the printing process is particularly important for the USB-C soldering process. This should ideally correspond to approx. 75% of the hole depth.
4. Carry out the assembly of the USB-C using a pick and place machine. The component 632723100011 can be used up to a PCB thickness of 1.3 mm. Please reduce the settling speed here too. The slower this is selected, the less likely it is to push or punch the paste out of the hole. This inevitably leads to a deterioration of the soldering result.
5. During the reflow soldering process, it is recommended that the USB-C enters the reflow oven with the connector face or pin row first (see Figure 8). This prevents the USB-C from bending. This bending can occur if the solder paste of the pin row does not melt simultaneously.
6. Perform AOI for the visible pins. The hidden pins can be checked and the filling level determined by X-ray.

Figure 8: Recommended flow direction of the USB-C hybrid during reflow soldering

## 5. Layout Tips for the USB-C Mid-Mount

To facilitate the routing of the differential pairs B2/B3 and B10/B11, it is possible to increase the distance to the milled edge in deviation from the layout recommendation. Assuming a milling cutter with a diameter of 0.50 mm and a resulting radius of 0.25 mm, which is common in PCB production, the distance from the center of the lowest row of pins to the center of the milling contour can be changed as follows:

According to the data sheet, a distance of 0.80 mm is specified for this. This results in a distance of 0.55 mm from the center of the row of pins to the milled edge. Thus, the width available for routing is only 225 um. The area between the pad rest-ring and the milling contour can be increased by 200 um by increasing the distance from the center of the lowest pin row to the center of the milling contour to 1.00 mm. The 425 um now available is sufficient for routing the differential pairs (125 um per track).

Contrary to the data sheet, the oblong holes B1 and B12 can also be designed as drilled holes similar to B2 to B11. This simplifies the PCB manufacturing process.

Figure 9: Comparison of the two footprint variants of the USB-C mid-mount (original vs. optimized)

Figure 10: Dimensioned original footprint

Figure 11: Dimensioned optimized footprint

**Caution:** The displacement of the milling contour must be discussed with the assembler (EMS). As the milling contour is now moved closer to the component, higher positioning accuracy is required of the pick-and-place machines. Assembly/placement accuracy of +/- 50 um is recommended here.

Figure 12: 3D representation of the shifted milled edge (left: original / right: optimized)

## 6. Processing the USB-C Receptacle Vertical

With the USB-C receptacle vertical, the component connections are implemented with two SMT pin rows aligned parallel to each other. This greatly simplifies stencil design as well as the soldering process. The four shield lances on the housing are nevertheless implemented as THR pins for mechanical stabilization.

When designing the stencil, make sure to select a 100 um thick stencil and to design the stencil openings as oblongs, in contrast to the pads. These should also be 4% smaller than the original pads all round. Excessive overprinting around the shield lances is not necessary, since the relatively large hole opening allows sufficient solder paste to be pressed into the hole.

Figure 13: Stencil recommendation for the USB-C vertical

## 7. Use of the SMD Spacer for Cable Fixation

Wurth Elektronik offers SMD spacers in addition to the existing USB-C connectors and cables. These allow screwable USB-C cables to be integrated into the system. There are two types of locking: cables that are fixed with a central screw and cables that are fixed with two screws along the edge.

Solder bridges may occur when locking the cable with the two lateral screws, due to the very small distance between the USB-C shield lances and the SMD spacer. However, these do not adversely affect the system functionality (same potential) and do not necessarily have to be corrected / reworked.

### 7.1 Locking Types

- **Centric one-screw locking:** M2 screw (0.4-6 g), M2 SMT block for 1.6 mm PCB (art no.: 7466302) or 1.0 mm PCB
- **Lateral two-screw locking:** 2x M2 screws (0.4-6 g), 15.00 +/- 0.10 mm spacing, 1.20 mm offset, M2 SMT Block (art no.: 7466302)

### 7.2 Types of Installation

**Integration of the PCB into a housing:**
- The spacers must be positioned at the edge of the PCB (solder pads of the spacer are located 0.40 mm behind the edge of the PCB and therefore do not interfere with PCB manufacture or the assembly and soldering process).
- The USB-C connector is placed up to the front edge of the housing and thus beyond the edge of the PCB.

**Assembly without housing:**
- The spacers must be positioned at the edge of the PCB.
- Caution: For centric one-screw fixation, the USB-C connector must be placed at the PCB edge, contrary to the layout recommendation. Otherwise, the cable connector may bend when tightening the screw. As a result, mechanical and electrical damage can occur to the component as well as to the entire device.
- This mechanical torsion cannot occur with the two-screw system. This allows the USB-C connector to be placed both at the edge of the PCB and beyond.

## Appendix: Basis of Calculation of the THR Process

### Volume Calculation of the PCB (Drilled Hole)

- Vpcb = pi * (Dh^2 / 4) * Tb
  - Tb: PCB thickness
  - Dh: Hole diameter = pin diameter + 0.3 mm for round pins (0.25 mm for rectangular pins)
  - Dsp: Solder pad diameter = Dh + 0.6 to 0.8 mm

### Volume Calculation for the Pin

- Vpin = pi * pin_radius^2 * PCB_thickness
  - For round pins: pin_radius = Wp / 2
  - For rectangular pins: pin_radius = sqrt(A * B / pi)

### Volume Calculation for the Fillet (Pappus-Guldin Formula)

- Vfillet = 0.215 * C^2 * (0.2334 * C + pin_radius) * 2 * pi
  - C = (solder_pad_diameter - pin_diameter) / 2

### Solder Paste Volume and Stencil Opening

- Vpaste = (2 * Vfillet + Vpcb - Vpin) * 2
  - The total volume is taken x2, as standard solder pastes have a metallic content of 50%.
- Stencil opening (mm^2) = Vpaste / Ts (stencil thickness)
  - Caution: How deep the paste is pressed into the hole depends on the diameter and height of the stencil. This is also influenced by the printing parameters: print cycles, force, speed and the squeegee angle.

### Quality Requirements According to IPC-A-610

- Ideal case: 100% filling level
- Minimum: 75% filling level
