---
source: "TI SLMA002H -- PowerPAD Thermally Enhanced Package"
url: "https://www.ti.com/lit/pdf/slma002"
format: "PDF 31pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 31314
---
# PowerPAD™ Thermally Enhanced Package

Steven Kummerl

#### **ABSTRACT**

The PowerPAD™ thermally enhanced package provides greater design flexibility and increased thermal efficiency in a standard size device package. The PowerPAD package's improved performance permits higher clock speeds, more compact systems and more aggressive design criteria. PowerPAD™ packages are available in several standard surface mount configurations. They can be mounted using standard printed-circuit board (PCB) assembly techniques, and can be removed and replaced using standard repair procedures. To make optimum use of the thermal efficiencies designed into the PowerPAD™ package, the PCB must be designed with this technology in mind. In order to leverage the full thermal performance benefits offered from the PowerPad™ package, the exposed pad must be soldered to the board. This document focuses on the specifics of integrating a PowerPAD™ package into the PCB design.


#### **1 Introduction**

The PowerPAD™ concept is implemented in a standard epoxy-resin package material. The integrated circuit die is attached to the leadframe die pad using a thermally conductive epoxy. The package is molded so that the leadframe die pad is exposed at a surface of the package. This provides an extremely low thermal resistance (θJP) path between the device junction and the exterior of the case. Because the external surface of the leadframe die pad is on the PCB side of the package, it can be attached to the board using standard reflow soldering techniques. This allows efficient attachment to the board, and permits board structures to be used as heat sinks for the IC. Using vias, the leadframe die pad can be attached to an internal copper plane or special heat sink structure designed into the PCB. Check the respective product data sheet to verify which signal, power, or ground plane the device should be soldered to. For the first time, the PCB designer can implement power packaging without the constraints of extra hardware, special assembly instructions, thermal grease or additional heat sinks.

**Figure 1. Cross Section of PowerPAD™ Package Mounted to PCB and Resulting Heat Transfer**

Because the exact thermal performance of any PCB is dependent on the details of the circuit design and component installation, exact performance figures cannot be given here. However, representative performance is very important in making design decisions. The data shown in [Table](#page-2-2) 1 is typical of the performance that can be expected from the PowerPAD™ package.

| Table 1. Typical Power-Handling $β$ Capabilities of | PowerPAD™ Packages(1)                                     |
|-----------------------------------------------------|-----------------------------------------------------------|
| PowerPAD™ Packages(1)                               | Descriptive text for the data cell (not visible in image) |

| PACKAGE<br>TYPE | PIN COUNT | STANDARD<br>PACKAGE | PowerPAD™<br>PACKAGE |
|-----------------|-----------|---------------------|----------------------|
| SSOP            | 20        | 0.75                | 3.25                 |
| TSSOP           | 24        | 0.55                | 2.32                 |

<sup>(1)</sup> Assumes +150°C junction temperature (T<sup>J</sup> ) and +80°C ambient temperature. Values are calculated from θJA figures shown in [Appendix](#page-16-0) A.

For example, the user can expect 3.25 W of power-handling capability for the PowerPAD™ version of the 20-pin SSOP package. The standard version of this package can handle only 0.75 W. Details for all package styles and sizes are given in Appendix A.

The standard package used in this example is a fully encapsulated device, whereas the PowerPAD™ package has an exposed die mounting pad which is soldered directly to the PCB. The PowerPAD™ package is not designed to be used without the exposed pad being soldered to the PCB.

#### **2 Installation and Use**

#### *2.1 PCB Attachment*

Proper thermal management of the PowerPAD™ package requires PCB preparation. This preparation is not difficult, nor does it use any extraordinary PCB design techniques, however it is necessary for proper heat removal. The PowerPAD™ package with exposed pad down is designed to be soldered to the PCB. Texas Instruments does not recommend the use of a PowerPAD™ package without soldering it to the PCB due to the risk of lower thermal performance and mechanical integrity.

Pad-Up PowerPAD™ packages should have appropriately designed heat sinks attached. Because of the variation and flexible nature of this type of heat sink, additional details should come from the specific manufacturer of the heat sink.

**Figure 2. Bottom and Top View of the 20-Pin TSSOP PowerPAD™ Package**

**PowerPAD™ Package**

All of the thermally enhanced packages incorporate features that provide a very low thermal resistance path for heat removal from the integrated circuit - either to and through a printed-circuit board (in the case of zero airflow environments), or to an external heatsink. The TI PowerPAD™ implementation does this by creating a leadframe where the bottom of the die pad is exposed, as opposed to the case where a heat slug is embedded in the package body. (See [Figure](#page-2-1) 2 and [Figure](#page-2-1) 3).

## *2.2 PCB Design Considerations*

The printed-circuit board used with PowerPAD™ packages must have features included in the design to create an efficient thermal path to remove the heat from the package. As a minimum, there must be an area of solderable copper underneath the PowerPAD™ package. This area is called the thermal land. As detailed below, the thermal land varies in size depending on the PowerPAD™ package being used, the PCB construction and the amount of heat that needs to be removed. In addition, this thermal land may or may not contain thermal vias depending on PCB construction. The requirements for thermal lands and thermal vias are detailed below.

#### *2.3 Thermal Lands*

A thermal land is required on the surface of the PCB directly underneath the body of the PowerPAD™ package. During normal surface mount reflow solder operations, the leadframe on the underside of the package is soldered to this thermal land creating a very efficient thermal path. Normally, the PCB thermal land has a number of thermal vias within it that provide a thermal path to internal copper planes (or to the opposite side of the PCB) that provide for more efficient heat removal. The size of the thermal land should be as large as needed to dissipate the required heat.

For simple, double-sided PCBs, where there are no internal layers, the surface layers must be used to remove heat. Shown in [Figure](#page-3-0) 4 is an example of a thermal land for a 24-pin package. Details of the package, the thermal land and the required solder mask are shown. Refer to the device-specific data sheet for detailed dimensions of the exposed pad on the package. If the PCB copper area is not sufficient to remove the heat, the designer can also consider external means of heat conduction, such as attaching the copper planes to a convenient chassis member or other hardware connection.

**Figure 4. Package and PCB Land Configuration for a Single Layer PCB**

In the PWP-24 example shown in [Figure](#page-3-0) 4, the copper area is maximized on the surface of the board with a soldermask defined pad designed onto the copper area. The PCB's solder mask defined pad should be designed to the maximum exposed pad size shown in the respective device's product data sheet.

**NOTE:** Refer to the device-specific data sheet for the exact pad dimensions for the used device.

For multilayer PCBs, the designer can take advantage of internal copper layers (such as the ground plane) for heat removal. Check the respective device's product data sheet to verify which signal, power, or ground plane the device should be soldered to. The external thermal land on the surface layer is still required, however the thermal vias can conduct heat out through the internal power or ground plane. Shown in [Figure](#page-4-0) 5 is an example of a thermal land used for multilayer PCB construction. In this case, the primary method of heat removal is down through the thermal vias to an internal copper plane.

**Figure 5. Package and PCB Land Configuration for a Multi-Layer PCB**

**NOTE:** The dimensions of the 24-pin PWP package shown in [Figure](#page-4-0) 5 is for reference only. Refer to the device-specific data sheet for exact package dimensions for your device.

The details of a 64-pin TQFP PowerPAD™ package are shown in [Figure](#page-5-0) 6 . The recommended PCB thermal land for this package is shown in [Figure](#page-6-0) 7. The maximum copper land size for TQFP packages is the package body size minus 2.0 mm. A solder mask defined pad is then placed onto the copper land sized to the maximum exposed pad size listed in the respective product data sheet.

Note that the PowerPAD™ package land patterns are device specific with the exposed pad size shown in the product data sheet. This land is normally attached to the PCB for heat removal, but can be configured to take the heat to an external heat sink. This is preferred when airflow is available.

# *Definitions and Modeling*

#### *A.1 Thermal Resistance Definition*

**Thermal Resistance** is defined as the temperature drop from the packaged chip to it's primary heat sink per watt of power dissipated in the package. The primary heat sink may be the ambient air, the PWB itself, or a heat sink that is mounted on the package. Thermal resistance is denoted by the symbol θJx (or Theta-Jx) where 'x' denotes the external reference point where the temperature is measured

- θJA is junction-to-ambient air thermal resistance
- θJC is junction-to-case thermal resistance
- θJP is junction-to-pad thermal resistance
- θJB is junction-to-board thermal resistance

**Thermal Parameter** is different from a thermal resistance in that the referenced external temperature is not the ultimate heat sink for the package. A thermal parameter can be used to estimate junction temperatures for a device in its end-use environment. A thermal parameter is denoted by the symbol ψJx (or Psi-Jx) where 'x' denotes the referenced point where the temperature is measured. The thermal parameters are measured during the ψJA test only. Currently defined thermal parameters include the following:

- ψJT is the junction-to-package top center thermal parameter. A thermocouple is attached to the top center of the package in order to measure the surface temperature
- ψJB is the junction-to-board thermal parameter. A thermocouple is attached to a trace on the board at the middle of the long side of the package to measure the PWB temperature.

#### Common Uses

- θJA rough comparison
- θJB, θJC, θJAP system model
- ψJB, ψJT probing on board

**Figure 16. Thermal Resistance Diagram**

#### where

- T<sup>A</sup> is the ambient temperature
- T<sup>J</sup> is the device junction temperature
- T<sup>C</sup> is the case temperature
- T<sup>B</sup> is the board temperature at lead
- T<sup>P</sup> is the exposed pad temperature

## *A.2 General Information*

Thermal modeling is used to estimate the performance and capability of device packages. From a thermal model, design changes can be made and thermally tested before any time is spent on manufacturing. It can also be determined what components have the most influence on the heat dissipation of a package. Models can give an approximation of the performance of a package under many different conditions. In this case, a thermal analysis was performed in order to approximate the improved performance of a PowerPAD™ thermally enhanced package to that of a standard package.

#### *A.3 Modeling Considerations*

Only a few differences exist between the thermal models of the standard packages and models for the PowerPAD™ package. The geometry of both packages was essentially the same, except for the location of the lead frame bond pad. The pad for the thermally enhanced PowerPAD™ package is deep downset, so its location is further away from the lead fingers than a standard package lead frame pad. Both models used the maximum pad and die size possible for the package, as well as using a lead frame that had a gap of one lead frame thickness between the pad and the lead fingers. The lead frame thickness was:

- TQFP/LQFP: 0.127 mm, or 5 mils
- TSSOP/TVSOP/SSOP: 0.147 mm, or 5.8 mils

In addition, the board design for the standard package is different from that of the PowerPAD™ package. One of the most influential components on the performance of a package is board design. In order to take advantage of the PowerPAD™ package's heat dissipating abilities, a board must be used that acts similarly to a heat sink and allows for the use of the exposed (and solderable) deep downset pad. This is Texas Instruments' recommended board for the PowerPAD™ device (see [Figure](#page-17-0) 17). A summary of the board geometry is included below.

#### *A.4 Texas Instruments Example Jedec Board Design for PowerPAD™ Packages*

- 0.062" thick
- 3" x 3" (for packages <27 mm long)
- 4" x 4" (for packages >27 mm long)
- 2 oz. copper traces located on the top of the board (0.071 mm thick)
- Copper areas located on the top and bottom of the PCB for soldering
- Power and ground planes, 1 oz. copper (0.036 mm thick)
- Thermal vias, 0.3 mm diameter, 1.5 mm pitch
- Thermal isolation of power plane

- A power plane with specified dimensions of 0.5246 − 0.5606 mm.
- A board base and bottom pad ranging from 0.0 to 0.071 mm in thickness.
- A ground plane defined between 1.0142 − 1.0502 mm.
- A component trace with dimensions of 1.5038 − 1.5748 mm.

Additional features mentioned include a thermal via and thermal isolation, which is noted to apply only to the power plane and has a size of 0.18 mm (square). The text also refers to a package solder pad with a bottom trace at 1.5748 mm.

**Figure 17. Texas Instruments Example Jedec Board Design (Side View)**

The standard packages were placed on a board that is commonly used in the industry today, following the JEDEC standard. It does not contain any of the thermal features that are found on the Texas Instruments recommended board. It only has component traces on the top of the board. A summary of the standard is located below:

#### *A.5 JEDEC Low Effective Thermal Conductivity Board (Low-K)*

- 0.062" thick
- 3" x 3" (for packages <27 mm long)
- 4" x 4" (for packages >27 mm long)
- 1 oz. copper traces located on the top of the board (0.036 mm thick)

These boards were used to estimate the thermal resistance for both PowerPAD™ and the standard packages under many different conditions. The PowerPAD™ package was modeled on the JEDEC low-k board for comparison purposes only. It is recommended that it be used on the Texas Instruments heat dissipating board design. It allows for the exposed pad to be directly soldered to the board, which creates an extremely low thermal resistance path for the heat to escape.

A general modeling template was used for each PowerPAD™ package, with variables dependent on the package size and type. The package dimensions and an example of the template used to model the packages are shown in [Figure](#page-17-0) 17 and [Table](#page-19-0) 4. While only 1/4 of the package was modeled (in order to simplify the model and to lessen the calculation time), the dimensions shown are those for a full model.

**Figure 18. Thermal Pad and Lead Attachment to PCB Using the PowerPAD™ Package**

#### **Table 4. PowerPAD™ Package Template Description**

| Component<br>Description | Size (mm)   |
|--------------------------|-------------|
| PCB Thickness            | 1.5748      |
| PCB Length               | 76.2(1)     |
| PCB Width                | 76.2(1)     |
| Chip Thickness           | 0.381       |
| Chip Length              | (2)         |
| Chip Width               | (2)         |
| Die Attach Thickness     | 0.0127      |
| Lead Frame Downset       | (3)         |
| Tie Strap Width          | (3)         |
| PCB to Package Bottom    | 0.09        |
| Shoulder Lead Width      | (3) (4) (5) |
| Shoulder Lead Space      | (3) (5)     |
| Shoulder to PCB Dist.    | (6)         |
| Package Thickness        | (3)         |
| Package Length           | (3)         |
| Package Width            | (3)         |
| Pad Thickness            | 0.147 (7)   |
| Pad Length               | (3)         |
| Pad Width                | (3)         |
| PCB Trace Length         | 25.4        |
| PCB Trace Thickness      | 0.071       |
| PCB Backplane Thickness  | 0.0 (8)     |
| PCB Trace Width          | 0.254       |
| Foot Width               | (4)         |
| Foot Length on PCB       | (3)         |

<sup>(1)</sup> 99.6 mm for packages > 27 mm maximum length

<sup>(2)</sup> Chip size is 10 mils smaller than the largest pad size (5 mils from each side)

<sup>(3)</sup> Dependent on package size and type

<sup>(4)</sup> Foot width was set equal to shoulder lead width for model efficiency

<sup>(5)</sup> Lead pitch is equal to the shoulder lead width plus the shoulder lead space (pitch = G + H)

<sup>(6)</sup> The shoulder to board distance is equal to the downset plus the board to package bottom distance (J = D + E)

<sup>(7)</sup> The pad thickness for TQFP/LQFP is equal to 0.127 mm

<sup>(8)</sup> The recommended board requires the addition of two internal copper planes, solder pads, and thermal vias

In addition to following a template for the dimensions of the package, a simplified lead frame was used. A description of the lead frame geometry is seen in Figure 19.

Figure 19. General Leadframe Drawing Configuration

**NOTE:** The leadframe downset bend area = 20 mils (leadframe thickness). For SSOP, TSSOP, and TVSOP packages, add the bend area to the width of the pad. For TQFP and LQFP, add the bend area to both the width and length of the pad.

#### A.6 Boundary Considerations

The junction-to-ambient  $(\theta_{JA})$ , junction-to-pad  $(\theta_{JP})$ , and junction-to-top of package  $(\psi_{JT})$  thermal resistances were calculated using a Texas Instruments finite difference program. This program uses assumptions in order to simplify the calculation time, but is still accurate to within 10% of the actual measured number. Of course, the model conditions must be approximately the same as the test conditions for this to be true. Below is a summary of the analysis boundary conditions.

Junction-to-ambient ( $\theta_{JA}$ )

- □ Software calculated convection coefficients
- No radiation inputs
- □ +25°C ambient temperature

Junction-to-top of package ( $\psi_{IT}$ )

- ☐ (Highest Device Temp. Highest Package Surface Temp.)/Power
- $\Box$  Extracted graphically from  $\theta_{JA}$  solution

Junction-to-pad (θ<sub>JP</sub>)

□ For the PowerPAD<sup>™</sup> package, the board was removed and the bottom of the pad set to a fixed temperature of +25°C. (See Figure 20).

Figure 20. PowerPAD™ θ<sub>JP</sub> Measurement

For the standard package, the board was removed and the top of the package was set to 25°C. (See Figure 21).

Figure 21. Standard Package  $\theta_{\text{JC}}$  Measurement

## *A.7 Results*

The purpose of the thermal modeling analysis was to estimate the increase in performance that could be achieved by using the PowerPAD™ package over a standard package. For this package comparison, several conditions were examined.

- 1. PowerPAD™ package soldered to the TI-recommended board.
- 2. A standard package configuration on a Low-K board
- 3. A standard package on the TI recommended board

The first two cases show a comparison of PowerPAD™ packages on the recommended board to standard packages on a board commonly used in the industry. From these results, it was shown that the PowerPAD™ package, as soldered to the TI recommended board, performed 73% cooler than a standard package on a low-k board.

For the final case, a separate analysis was performed in order to show the difference in thermal resistance when the standard and the thermally enhanced packages are used on the same board. The results showed that the PowerPAD™ package, as soldered, performed an average of 44% cooler than the standard package (See [Figure](#page-22-0) 22).

**Figure 22. Comparison of θJA for Various Packages**

#### *A.8 Conclusions*

The deep downset pad of a PowerPAD™ package allows for an extensive increase in package performance. Standard packages are limited by using only the leads to transport a majority of the heat away. The addition of a heat sink improves standard package performance, but greatly increases the cost of a package. The PowerPAD™ package improves performance, but maintains a low cost. The results of the thermal analysis showed that the PowerPAD™ package directly to a board designed to dissipate heat, thermal performance increased approximately 44% over the standard packages used on the same board.

# *Rework Process for Heat Sink TQFP and TSSOP PowerPAD™ Packages - from Air-Vac Engineering*

#### *B.1 Introduction*

The addition of bottom side heat sink attachment has enhanced the thermal performance of standard surface mounted devices. This has presented new process requirements to effectively remove, redress, and replace (rework) these devices due to the hidden and massive heat sink, coplanarity issues, and balance of heat to the leads and heat sink. The following is based on rework of the TQFP100 and TSSOP20/24 pin devices.

**Figure 23. DRS22C Reworking Station**

#### *B.2 Equipment*

The equipment used was the Air-Vac Engineering DRS22C hot gas reflow module. The key requirements for the heat sink applications include: stable PCB platform with sufficient bottom side preheat, alignment capabilities, very accurate heat control, and proper nozzle design.

PCB support is critical to reduce assembly sagging and to provide a stable, flat condition throughout the process. The robust convection-based area heater provides sufficient and accurate bottom side heat to reduce thermal gradient, minimize local PCB warpage, and compensate for the heat sink thermal characteristics. The unique pop-up feature allows visible access to the PCB with multiple easy position board supports.

**Figure 24. Reworking Nozzles of Various Sizes Figure 25. Reworking Nozzles of Various Sizes**

During removal, alignment, and replacement, the device is held and positioned by a combination hot gas/hot bar nozzle. Built-in nozzle tooling positions the device correctly to the heat flow. A vacuum cup holds the component in place. Hot gas is applied to the top of the device while hot gas/hot bar heating is applied to the component leads. The hot bar feature also insures bonding of the fine pitch leads.

**Figure 26. Nozzle Configuration**

#### *B.3 Profile*

The gas temperature, flow, and operator step-by-step instructions are controlled by an established profile. This allows complete process repeatability and control with minimal operator involvement. Very accurate, low gas flow is required to insure proper temperature control of the package and to achieve good solder joint quality.

#### *B.4 Removal*

The assembly is preheated to 75°C. While the assembly continued to preheat to 100°C, the nozzle is preheated. After the preheat cycle, the nozzle is lowered and the device is heated until reflow occurs. Machine settings: TSSOP 20/24 - 220°C at 0.39 scfm gas flow for 50 seconds (preheat) above board level, 220°C at 0.39 scfm for 10 seconds. TQFP 100 - 240°C at 0.10 scfm for 60 seconds (preheat) above board level, 250°C at 0.65 scfm for 15 seconds. The built in vacuum automatically comes on at the end of the cycle and the nozzle is raised. The time to reach reflow was approximately 15 seconds. The component is released automatically allowing the part to fall into an appropriate holder.

#### *B.5 Site Redress*

After component removal the site must be cleaned of residual solder. This may be done by vacuum desoldering or wick. The site is cleaned with alcohol and lint-free swab. It is critical that the heat sink area be flat to allow proper placement on the leads on new device. Stenciling solder paste is the preferred method to apply new solder. Solder dispensing or reflowing the solder bumps on the pads for the leads may also be an alternative, but reflow (solid mass) of solder to the heat sink is not.

**Figure 27. Air-Vac Vision System**

#### *B.6 Alignment*

A replacement device is inserted into the gas nozzle and held by vacuum. The device is raised to allow the optical system to be used. The optical system used for alignment consists of a beam-splitting prism combined with an inspection quality stereo microscope or camera/video system. the leads of the device are superimposed over the corresponding land pattern on the board. This four sided viewing allows quick and accurate operator alignment.

## *B.7 Replacement*

Once aligned, the x/y table is locked and the optical system retracts away from the work area. The preheat cycle is activated. The device is then lowered to the board. An automatic multi-step process provides a controlled reflow cycle with repeatable results. Machine settings for TSSOP 20/24: 160°C at 0.39 scfm gas flow for 40 seconds (preheat), 220°C at 0.39 scfm for 60 seconds above board level, 220°C at 0.39 scfm for 10 seconds. For TQFP 100: 100°C at 0.78 scfm for 40 seconds (preheat), 240°C at 0.10 scfm for 90 seconds above board level, 250°C at 0.65 scfm for 15 seconds (2 stages).

#### *B.8 Conclusion*

Rework of heat sink devices, TQFP and TSSOP, can be successful with attention to the additional issues they present. With respect to proper thermal profiling of the heat sink, die, and lead temperatures, the correct gas nozzle and profile can be developed to meet the requirements of the device and assembly. Existing equipment and nozzle design by Air-Vac can provide the tools and process knowledge to meet the heat sink TQFP and TSSOP rework application.

# *PowerPAD™ Process Rework Application Note from Metcal*

#### *C.1 Introduction*

The following report references six of Texas Instruments' fine pitch, surface mount prototype packages (TSOP20, TSOP56, TSOP24, TQFP100, and TQFP64). The shapes and sizes are not new to the circuit board industry. Normally, you could use Metcal conduction tools to simply remove and replace these components. However, these packages are unique because all packages include a 'dye lead' on the underside of the package. This dye lead cannot be accessed by contact soldering. Therefore, convection rework methods are necessary for component placement.

**NOTE:** Conduction tools can be used for removal. But convection rework techniques are required for placement, and recommended for removal.

#### *C.2 Removal*

Conduction (optional): All packages can be removed with Metcal conduction tips. Use the following tips.

| Component | Metcal Tip Cartridge | OK Nozzle |
|-----------|----------------------|-----------|
| TSOP20    | SMTC-006             | N-S16     |
| TSOP56    | SMTC-166             | N-TSW32   |
| TSOP24    | SMTC-006             | N-S16     |
| TQFP100   | SMTC-0118            | N-P68     |
| TQFP64    | SMTC-112             | N-P20     |

**Table 5. Metcal Conduction Tips**

The dye lead, which is not in contact with the Metcal tip, easily reflows as heat passes through the package.

#### *C.3 Conduction Procedure*

- 1. Tin the tip, contact all perimeter leads simultaneously, and wait 3-5 seconds for the leads to reflow
- 2. Lift the package off the board (surface tension holds it in the tip cartridge). Dislodge the component from the tip by wiping the tip cartridge on a damp sponge.

#### *C.4 Convection Procedure*

- 1. Flux the leads. Preferably, use a liquid RMA/rosin flux. Pre-heat the board at 100°C. Use a convection or IR preheater, like the SMW-2201 from OK Industries. The settings 2-4 generally heats a heavy board to 100°C in 60 seconds.
- 2. Remove the component with the OK Industries FCR hot air system. Use a nozzle that matches the size and shape of the component (see above). With the preheat still on, heat the top of the board for 30-45 seconds on a setting of 3-4 (depending on board thickness and amount of copper in board).

Since convection is *necessary* for placement, convection is recommended for removal.

#### *C.5 Placement Procedure*

1. Pads can be tinned by putting solder paste on the pads and reflowing with hot air. Simply apply a fine bead of solder paste (pink nozzle, 24AWG) to the rows of pads. Be sure to apply very little paste. Excessive paste causes bridging, especially with fine pitch components.

2. Once the pads are tinned, apply gel flux (or liquid flux) to the pads. RMA flux is preferable. Be sure to apply gel flux to the dye pad as well. It is important that your pads not be OVER tinned. If too much solder has formed on the dye pad, the component sits above the perimeter leads, causing co-planarity problems. The gel flux is tacky and helps with manual placement. The joints require very little solder, so stenciling is not necessary. The pads are so thin that a minimal amount of solder is needed to form a good joint. Use a hot air nozzle for the FCR system. Pre-heat the board and (setting 3 to 5). Use low air flow (5 to 10 liters/minute) and topside heat (setting 3-4) for about 30 to 45 seconds.

**NOTE:** The quality of the dye lead's solder joint cannot be visually inspected. An X-ray machine, cross sectioning, or electrical testing is required. The vias on the test board are not solder masked very well which causes some bridging and solder wicking.

Specific board and component temperatures varies from board to board and from nozzle to nozzle. Larger nozzles require a higher setting because the heat must travel farther away from the heat source. There is a slight convection cooling effect from pushing hot air through long flutes, and depending on how wide the nozzle is. However, as a rule, keep the board temperature at 100°C (as thermocoupled from the TOP). You can regulate the board temperature by setting the temperature knob on the bottom side pre-heater. Apply a HIGHER topside heat from the FCR heating head. As a rule, use a maximum of 200°C to 210°C for a short peak period (10 seconds). Look for the flux to burn off. For board profiling purposes, you can visually inspect the condition of the solder joints during the removal process. Note the time allotted for reflow and set the system to Auto Remove or Auto Place at the same time designation for good repeatability. Be sure not to overheat the joints. Excessive heat can cause board delamination and discoloration. Alignment self-corrects once all the solder has reflowed. Tap board lightly. Remove any solder bridges with solder braid. Also, limit the board's heating cycles to a minimum. Excessive heat shock may warp the board or cause cracking in the solder joints.
