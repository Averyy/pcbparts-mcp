---
source: "ADI -- PCBs Layout Guidelines for RF & Mixed-Signal"
url: "https://www.analog.com/en/resources/technical-articles/pcbs-layout-guidelines-for-rf--mixedsignal.html"
format: "HTML"
method: "readability"
extracted: 2026-02-16
chars: 14797
---

# PCBs Layout Guidelines for RF & Mixed-Signal

## Abstract

This application note provides guidelines and suggestions for RF printed-circuit board (PCB) design and layout, including some discussion of mixed-signal applications. The material provides "best practices" guidance, and should be used in conjunction with all other design and manufacturing guidelines that may apply to particular components, PCB manufacturers, and material sets as applicable.

This application note applies to all Analog Device wireless products.

## Introduction

This application note provides guidelines and suggestions for RF printed-circuit board (PCB) design and layout, including some discussion of mixed-signal applications, such as digital, analog, and RF components on the same PCB. The material is arranged by topic areas and provides "best practices" guidance. It should be used in conjunction with all other design and manufacturing guidelines that may apply to particular components, PCB manufacturers, and material sets as applicable.

## RF Transmission Lines

Many of Analog Devices' RF components require controlled impedance transmission lines that will transport RF power to (or from) IC pins on the PCB. These transmission lines can be implemented on a exterior layer (top or bottom), or buried in an internal layer. Guidelines for these transmission lines include discussions relating to the microstrip, suspended stripline, coplanar waveguide (grounded), and characteristic impedance. It also describes transmission line bends and corner compensation, and layer changes for transmission lines.

#### Microstrip

This type of transmission line consists of fixed-width metal routing (the conductor), along with a solid unbroken ground plane located directly underneath (on the adjacent layer). For example, a microstrip on Layer 1 (top metal) requires a solid ground plane on Layer 2 (Figure 1). The width of the routing, the thickness of the dielectric layer, and the type of dielectric determine the characteristic impedance (typically 50Ω or 75Ω).

Figure 1. Microstrip example (isometric view).

#### Suspended Stripline

This line consists of a fixed-width routing on an inner layer, with solid ground planes above and below the center conductor. The conductor can be located midway between the ground planes (Figure 2), or it can be offset (Figure 3). This is the appropriate method for RF routing on inner layers.

Figure 2. Suspended stripline (end view).

Figure 3. Offset suspended stripline. A variant of the stripline, for PCBs with unequal layer thicknesses (end view).

#### Coplanar Waveguide (Grounded)

A coplanar waveguide provides for better isolation between nearby RF lines, as well as other signal lines (end view). This medium consists of a center conductor with ground planes on either side and below (Figure 4).

Figure 4. A coplanar waveguide provides for better isolation between nearby RF lines and other signal lines.

Via "fences" are recommended on both sides of a coplanar waveguide, as shown in Figure 5. This top view provides an example of a row of ground vias on each top metal gound plane on either side of the center conductor. Return currents induced on the top layer are shorted to the underlying ground layer.

Figure 5. Via fences are recommended on both sides of a coplanar waveguide.

#### Characteristic Impedance

There are several calculators available to properly set the signal conductor line width to achieve the target impedance. However, caution should be used when entering the dielectric constant of the layers. The outer laminated layers of typical PCBs often contain less glass content than the core of the board, and consequently the dielectric constant is lower. For example, FR4 core is generally given as εR = 4.2, whereas the outer laminate (prepreg) layers are typically εR = 3.8. Examples given below for reference only, metal thickness assumed for 1oz copper (1.4 mils, 0.036mm).

Table 1. Examples of Characteristic Impedance

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| Microstrip | Prepreg (3.8) | 6 (0.152) | 11.5 (0.292) | N/A | 50.3 |
| 10 (0.254) | 20 (0.508) | 50.0 |
| Diff. Pair | Prepreg (3.8) | 6 (0.152) | 25 (0.635) | 6 (0.152) | 50.6 |
| Stripline | FR4 (4.5) | 12 (0.305) | 3.7 (0.094) | N/A | 50.0 |
| Offset Stripline | Prepreg (3.9) | 6 (0.152) upper, | 4.8 (0.122) | N/A | 50.1 |
| 10 (0.254) lower |
| Coplanar WG | Prepreg (3.8) | 6 (0.152) | 14 (0.35) | 20 (0.50) | 49.7 |

#### Transmission Line Bends and Corner Compensation

When transmission lines are required to bend (change direction) due to routing constraints, use a bend radius that is at least 3 times the center conductor width. In other words:

Bend Radius ≥ 3 × (Line Width).

This will minimize any characteristics impedance changes moving through the bend.

In cases where a gradually curved bend is not possible, the transmission line can undergo a right-angle bend (noncurved). See Figure 6. However, this must be compensated to reduce the impedance discontinuity caused by the local increase in effective line width going through the bend. A standard compensation method is the angled miter, as illustrated below. The optimum microstrip right-angle miter is given by the formula of Douville and James:

Where M is the fraction (%) of the miter compared to the unmitered bend. This formula is independent of the dielectric constant, and is subject to the constraint that w/h ≥ 0.25.

Similar methods can be employed for other transmission lines. If there is any uncertainty as to the correct compensation, the bend should be modeled using an electromagnetic simulator if the design requires high-performance transmission lines.

Figure 6. When a curved bend is not possible, the transmission line can undergo a right-angle bend.

#### Layer Changes for Transmission Lines

When layout constraints required that a transmission line move to a different layer, it is recommended that at least two via holes be used for each transition to minimize the via inductance loading. A pair of vias will effectively cut the transition inductance by 50%, and the largest diameter via should be utilized that is compatible with the transmission line width. For example, on a 15-mil microstrip line, a via diameter (finished plated diameter) of 15 mils to 18 mils would be used. If space does not permit the use of larger vias, then three transition vias of smaller diameter should be used.

## Signal Line Isolation

Care must be taken to prevent unintended coupling between signal lines. Some examples of potential coupling and preventative measures:

* **RF Transmission Lines**: Lines should be kept as far apart as possible, and should not be routed in close proximity for extended distances. Coupling between parallel microstrip lines will increase with decreasing separation and increasing parallel routing distance. Lines that cross on separate layers should have a ground plane keeping them apart. Signal lines that will carry high power levels should be kept away from all other lines whenever possible. The grounded coplanar waveguide provides for excellent isolation between lines. It is impractical to achieve isolation better than approximately -45dB between RF lines on small PCBs.
* **High-Speed Digital Signal Lines**: These lines should be routed separately on a different layer than the RF signal lines, to prevent coupling. Digital noise (from clocks, PLLs, etc.) can couple onto RF signal lines, and these can be modulated onto RF carriers. Alternatively, in some cases digital noise can be up/down-converted.
* **VCC/Power Lines**: These should be routed on a dedicated layer. Adequate decoupling/bypass capacitors should be provided at the main VCC distribution node, as well as at VCC branches. The choice of the bypass capacitances must be made based on the overall frequency response of the RF IC, and the expected frequency distribution nature of any digital noise from clocks and PLLs. These lines should also be separated from any RF lines that will transmit large amounts of RF power.

## Ground Planes

The recommended practice is to use a solid (continuous) ground plane on Layer 2, assuming Layer 1 is used for the RF components and transmission lines. For striplines and offset striplines, ground planes above and below the center conductor are required. These planes must not be shared or assigned to signal or power nets, but must be uniquely allocated to ground. Partial ground planes on a layer, sometimes required by design constraints, must underlie all RF components and transmission lines. Ground planes must not be broken under transmission line routing.

Ground vias between layers should be added liberally throughout the RF portion of the PCB. This helps prevent accrual of parasitic ground inductance due to ground-current return paths. The vias also help to prevent cross-coupling from RF and other signal lines across the PCB.

## Special Consideration on Bias and Ground Layers

The layers assigned to system bias (DC supply) and ground must be considered in terms of the return current for the components. The general guidance is to not have signals routed on layers between the bias layer and the ground layer.

Figure 7. Incorrect layer assignment: there are signal layers between the bias layer and ground-current return path on ground layer. Bias line noise can be coupled to the signal layers.

Figure 8. Better layer assignment: there are no signal layers between the bias and ground return layers.

## Power (Bias) Routing and Supply Decoupling

A common practice is to use a "star" configuration for the power-supply routes, if a component has several supply connections (Figure 9). A larger decoupling capacitor (tens of µFds) is mounted at the "root" of the star, and smaller capacitors at each of the star branches. The value of these latter capacitors depends on the operating frequency range of the RF IC, and their specific functionality (i.e., interstage vs. main supply decoupling). An example is shown below.

Figure 9. If a component has several supply connections, the power-supply routes can be arranged in a star configuration.

The "star" configuration avoids long ground return paths that would result if all the pins connected to the same bias net were connected in series. A long ground return path would cause a parasitic inductance that could lead to unintended feedback loops. The key consideration with supply decoupling is that the DC supply connections must be electrically defined as AC ground.

## Selection of Decoupling or Bypass Capacitors

Real capacitors have limited effective frequency ranges due to their self-resonant frequency (SRF). The SRF is available from the manufacturer, but sometimes must be characterized by direct measurement. Above the SRF, the capacitor is inductive, and therefore will not perform the decoupling or bypass function. When broadband decoupling is required, standard practice is to use several capacitors of increasing size (capacitance), all connected in parallel. The smaller value capacitors normally have higher SRFs (for example, a 0.2pF value in a 0402 SMT package with an SRF = 14GHz), while the larger values have lower SRFs (for example, a 2pF value in the same package with an SRF = 4GHz). A typical arrangement is depicted in Table 2.

Table 2. Useful Frequency Ranges of Capacitors

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| Ultra-High Range | 20pF | 0402 | 2.5GHz | 800MHz to 2.5GHz |
| Very High Range | 100pF | 0402 | 800MHz | 250MHz to 800MHz |
| High Range | 1000pF | 0402 | 250MHz | 50MHz to 250MHz |
| Midrange | 1µF | 0402 | 60MHz | 100kHz to 60MHz |
| Low Range | 10µF | 0603 | 600kHz | 10kHz to 600kHz |
| \*Low end of useful frequency range defined as less than 5Ω of capacitive reactance. | | | | |

## Bypass Capacitor Layout Considerations

Since the supply lines must be AC ground, it is important to minimize the parasitic inductance added to the AC ground return path. These parasitic inductances can be caused by layout or component orientation choices, such as the orientation of a decoupling capacitor's ground. There are two basic methods, shown in Figure 10 and Figure 11.

Figure 10. This configuration presents the smallest total footprint for the bypass capacitor and related vias.

In this configuration, the vias connecting the VCC pad on the top layer to the inner power plane (layer) potentially impede the AC ground current return, forcing a longer return path with resulting higher parasitic inductance. Any AC current flowing into the VCC pin passes through the bypass capacitor to its ground side before returning on the inner ground layer. This configuration presents the smallest total footprint for the bypass capacitor and related vias.

Figure 11. This configuration requires more PCB area.

In this alternate configuration, the AC ground return paths are not blocked by the power-plane vias. Generally this configuration requires somewhat more PCB area.

## Grounding of Shunt-Connected Components

For shunt-connected (grounded) components (such as power-supply decoupling capacitors), the recommended practice is to use at least two grounding vias for each component (Figure 12). This reduces the effect of via parasitic inductance. Via ground "islands" can be used for groups of shunt-connected components.

Figure 12. Using at least two grounding vias for each components reduces the effect of via parasitic inductance.

## IC Ground Plane ("Paddle")

Most ICs require a solid ground plane on the component layer (top or bottom of PCB) directly underneath the component. This ground plane will carry DC and RF return currents through the PCB to the assigned ground plane. The secondary function of this component "ground paddle" is to provide a thermal heatsink, so the paddle should include the maximum number of thru vias that are allowed by the PCB design rules. The example below shows a 5 × 5 array of via holes embedded in the central ground plane (on the component layer) directly under the RF IC (Figure 13). The maximum number of vias that can be accommodated by other layout considerations should be used. These vias are ideally thru-vias (i.e., penetrate all the way through the PCB), and must be plated. If possible, the vias should be filled with thermally conductive paste to enhance the heatsink (the paste is applied after via plating and prior to final board plating).

Figure 13. A 5 × 5 array of via holes embedded in the central ground plane directly under the RF IC.