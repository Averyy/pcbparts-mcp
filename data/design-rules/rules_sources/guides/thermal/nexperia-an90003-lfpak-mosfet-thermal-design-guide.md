---
source: "Nexperia AN90003 -- LFPAK MOSFET Thermal Design Guide"
url: "https://assets.nexperia.com/documents/application-note/AN90003.pdf"
format: "PDF 53pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 65195
---
### **Document information**

| Information | Content                                                                                        |
|-------------|------------------------------------------------------------------------------------------------|
| Keywords    | Thermal design, LFPAK56D, LFPAK33, LFPAK56, LFPAK88                                            |
| Abstract    | Thermal design guide: estimate of MOSFET power dissipation capability depending on PCB design. |

#
# **1. Introduction**

This application note is a guide to assist design engineers in understanding the power dissipation limits of the LFPAK family of packages. The maximum power that a MOSFET can dissipate is considered as a function of the Printed Circuit Board (PCB) design, using some common configurations. The application notes comprises of three main sections. The first section gives some background on MOSFET power loss and the thermal environment. The next two sections address separately the low power LFPAKs (LFPAK56D and LFPAK33) and the high power LFPAKs (LFPAK56 and LFPAK88).

# **2. MOSFET power dissipation and the design environment**

During normal operation, MOSFETs can exhibit three kinds of power losses:

- Switching losses due to voltage and current being non-zero during the transition between the ON and OFF states.
- Conduction losses when the device is fully on due to its on-state resistance RDSon.
- Avalanche losses if the device breakdown voltage is exceeded and an avalanche event occurs.

The shape of the power can change depending on the nature of the load. A generalized model of the total power dissipated by a MOSFET is the sum of these three losses, see [Equation \(1\)](#page-1-0).

$$P_{tot} = P_{sw} + P_{cond} + P_{av} \tag{1}$$

In addition to electrical requirements another challenge is often the harsh environment that a device needs to operate in, particularly in terms of temperature. For instance, in automotive and industrial applications it's not uncommon to encounter high ambient temperature requirements, (from 85 °C up to 125 °C), this limits the amount of power that a MOSFET can safely handle.

Semiconductor devices are not the only parts to consider when dealing with high temperatures. For instance, the PCB material FR4 has a maximum operating temperature of around 130 °C, depending on manufacturer and chemistry, this is much lower than the limit specified for the junction of a silicon die (175 °C).

Modern applications continue to push the limits of power MOSFETs, while searching for better and better performances. As a consequence thermals have become one of the most important aspects of systems design. One way to address thermal issues is to carefully choose a device with the appropriate performances and provide a good enough path through which heat can flow freely, avoiding any impact on the device reliability.

### 2.1. Heat propagation phenomena

Heat propagates because of a temperature difference between the junction and the outside/ ambient. Propagation occurs from junction and the outside/ambient through different material, from solids (silicon, copper, FR4, aluminum) to fluids (surrounding air or even air pockets trapped in the solder joints on the PCB). Heat finds a path whether it's defined by an engineer or not. This means that if the path is not designed correctly then heat might get trapped and raise the temperature of one or multiple mediums.

The physical phenomena by which heat can propagate are: conduction, convection and radiation.

# 2.1.1. Conduction

Conduction is the propagation of heat in a solid medium due to a temperature difference within it, and it is caused by the random movement of atoms and molecules. The rate of heat flow Q is directly proportional to the cross-section area A, temperature difference and thermal conductivity k. It is inversely proportional to the length x of the heat path, see Equation (2).

$$Q = k \cdot A \cdot \frac{T_1 - T_2}{x} \tag{2}$$

Thermal conductivity, measured as W/(mK), is a physical property of a material and defines its ability to conduct heat. The higher its value the higher the rate of heat transfer, therefore the better thermal conductor. From <a href="Equation 2">Equation 2</a> it can be derived that rate of heat flow is measured in W. Therefore, heat is measured in Joule (Ws).

Table 1 lists some materials with their thermal conductivity values. Air is a very bad conductor of heat, thus a good thermal insulator. It's thermal conductivity is 2,000 times lower than that of steel. Notice how thermal glue has a very low thermal conductivity of less than 2, (generic brand). Thermal glue is not a good thermal conductor, however its main function is to create a good fit between two surfaces that otherwise would form trapped pockets of air, which is 100 times a better insulator than the glue itself.


**Table 1. Typical thermal conductivity values**

| Material         | k (W/mK) |
|------------------|----------|
| Air (not moving) | 0.024    |
| Brick            | 0.6      |
| Glass            | 0.8      |
| Thermal glue     | 1.78     |
| Steel            | 50.2     |
| Brass            | 109      |
| Silicon          | 130      |
| Aluminium        | 205      |
| Copper           | 385      |
| Silver           | 406      |
| Diamond          | 1000     |

### **2.1.2. Convection**

Convection is the transfer of heat from a solid body to a fluid due to its movement with respect to the surface of the body, and it is promoted by a difference in temperature between the two mediums. The fluid may be a gas (air) or a liquid.

Here the rate of heat flow depends only on surface *A*, temperature difference and convection coefficient *h*, see [Equation \(3\).](#page-3-1)

$$Q = h \cdot A \cdot (T_s - T_{amb}) \tag{3}$$

The convection coefficient is not a physical property of the fluid (like the conduction coefficient) but an abstract quantity verified by experimentation. It depends on fluid density, velocity, viscosity, turbulence and on the solid medium surface geometry.

The convection coefficient is measured in W/(m 2 K). [Table](#page-3-2) 2 lists some values measured in different scenarios of free/natural and forced cooling.

**Table 2. Thermal convection coefficient values**

| Flow type    | h (W/m²K)       |                |  |
|--------------|-----------------|----------------|--|
|              | Free air        | Forced cooling |  |
| Gases        | 2 - 20          | 25 - 300       |  |
| Air          | 10              | 100            |  |
| Liquids      | 50 - 1,000      | 100 - 40,000   |  |
| Phase change | 2,500 - 100,000 |                |  |

As can be seen during a phase change the convection coefficient rises dramatically up to 100,000. This is due to the fact that during a phase change all the energy involved, and transferred to the fluid, is used to rearrange molecules structure and does not result in a temperature change.

#### 2.1.3. Radiation

Radiation is the propagation of heat via infrared radiation.

The main benefit of radiation is that as the ambient temperature increases, and the component temperature with it, the heat transfer by radiation increases as well. As you can see in <u>Equation</u> (4), it depends on the fourth power of temperature. The radiation is bigger but not by a lot and the overall effect is that radiation does not help a body get cooler.

$$Q = \boldsymbol{\varepsilon} \cdot \boldsymbol{\sigma} \cdot \boldsymbol{A} \cdot (T_1^4 - T_2^4) \tag{4}$$

The amount of radiation is determined by the surface emissivity. Emissivity of a material is measured between 0 and 1. A perfect emitter is called a black body because it emits 100% of the energy it absorbs, and is assigned an emissivity value of 1. <u>Table 3</u> below gives emissivity values for different materials.

Table 3. Typical emissivity values

| Emissivity coefficient (ε)                   |  |
|----------------------------------------------|--|
| 0.05                                         |  |
| 0.25                                         |  |
| 0.95                                         |  |
| 0.01                                         |  |
| 0.65                                         |  |
| 0.88                                         |  |
| 0.98                                         |  |
| 0.05<br>0.25<br>0.95<br>0.01<br>0.65<br>0.88 |  |

A new piece of polished aluminum has emissivity of 0.05, (not good), its emissivity increases as it oxides by 5 times. Every object emits thermal radiation, the amount of radiation that a particular object emits as a function of wavelength looks as a bell shaped curve. Energy is emitted at all frequencies but the major part of the emission occurs at a certain wavelength range which depends on the source temperature. The higher the temperature the higher the frequency (lower the wavelength), that is why we see materials change color as they heat up.

At the receiving side, for most of the surfaces, the same graph looks quite flat but to a very small range of wavelengths at which the object absorbs all the impinging radiation. These surfaces are called selective surfaces, because they absorb only certain wavelengths.

# **2.2. Thermal – Electrical analogy**

When considering thermal propagation, classical methods of analysis may be used. These are based on the thermal equations and thermal networks. These describe the paths through which heat propagates through mediums or from one medium to another.

Any thermal network can be modelled by means of an electrical circuit. An analogy for every thermal parameter can be found in the electrical domain. The respective analogues of electric potential and current are temperature difference and rate of heat flow. Based on these it may be observed that the thermal resistance is the ratio of temperature and rate of heat flow similarly to how the voltage and current ratio defines the electrical resistance using Ohm's law. The main analogies may be seen in [Table](#page-5-0) 4 below. Based on these, thermal networks can be solved using many of the electrical theory laws such as Ohm's and Kirchhoff's laws. Also circuits can be simplified by means of series and parallel resistor equivalences.

**Table 4. Thermal and electrical analogous parameters**

| Temperature T (°C)              | Voltage V (V)             |
|---------------------------------|---------------------------|
| Rate of heat flow Q (W)         | Current I (A)             |
| Thermal resistance Rth (K/W)    | Resistance R (Ω)          |
| Thermal capacitance Cth [W·s/K] | Capacitance C (A·s/V = F) |

An example of a thermal circuit modelled in the electrical domain using a SPICE software may be seen in [Fig. 5.](#page-5-1) [Fig. 6](#page-5-2) shows the response of this example circuit as a temperature plot, where the transient and steady state thermal behaviour may be seen.

#### 2.2.1. Thermal resistance

Thermal resistance is a measure of the inertia of a material or medium towards heat flow, just like the electrical resistance is to the movement of electrons. It is therefore a physical property of the specific component. It is calculated as the ratio of the temperature difference between two points and the rate of heat flow, therefore as K/W. The thermal and electrical models may be seen in the pictures below.

Every phenomenon governing how heat flows, namely conduction, convection and radiation, has its own thermal resistance. Each one of them depends inversely on a coefficient and surface or cross section area of the material from where heat is generated or simply passing through. In conduction the resistance depends directly to the length of the medium.

### 2.2.2. Thermal capacitance

Thermal capacitance, sometimes known also as thermal mass, is a property of a material which represents how much heat (thermal energy) it can store in time, similar to its electrical counterpart with electrical energy. Thermal capacitance provides also a quantity of the inertia against temperature fluctuations, the higher the value the harder it will be to drive the stored energy in or out.

Thermal capacitance is typically referred to using the symbol  $C_{th}$ , and it's measured as J/K. For a body of uniform composition, it can be approximated as the product of mass (m) of the body and specific heat capacity ( $C_p$ ), which is the heat capacity of a sample of the substance divided by the mass of the sample.

## **2.2.3. Transient and steady state thermal behavior**

• Thermal transients describe temperatures which are changing, even at the end of the analysis window. An example may be observed below in the yellow part of the junction temperature plot.

• Steady state thermals describe the stable region where temperatures show minimal to no change at all. These temperature remain unchanged with the passing of time and thus represent the final values a system might show under constant conditions.

# **2.3. MOSFET steady state thermal characteristics**

This section focuses on two important MOSFET thermal aspects. The junction to mounting base thermal resistance as well as the junction to ambient thermal resistance. The aim in this chapter is to overview the two thermal paths and to show the thermal network which describes these paths.

## **2.3.1. Thermal resistance junction to mounting base - Rth(j-mb)**

There is some confusion to why Nexperia does not state thermal resistance junction to case, Rth(jc), in its data sheets unlike its competitors. In JESD51-1, the definition of Rth(j-c) is the thermal resistance produced when heat is transferred through the shortest path from the junction to the heat sunk surface of the case. This would be through to the mounting base of the device due to its high thermal conductivity and surface area. Hence, it is the reason why Nexperia states Rth(j-mb) as opposed to Rth(j-c) for standard power packages.

The thermal resistance from the MOSFET junction to its mounting base is one of the most important specifications in a data sheet. This is because it is the most dominant heat path for standard power packages, due to the large copper alloy mounting base. This is illustrated by the large red arrow representing heat flow in [Fig. 10.](#page-7-0)

**Fig. 10. Dominant thermal path from the die junction to the mounting base and ambient for a standard power package**

Rth(j-mb) describes the ease for heat to propagate in a one-dimensional path from the junction to the external surface of the mounting base. This is calculated by taking the temperature difference between junction and mounting base and dividing by the power dissipated between those two

physical points. In doing so, it assumes that there are no other heat flow paths apart from those two locations mentioned. In [Fig.](#page-8-0) 11, the thermal resistance is represented with a simple resistor network from the junction to the mounting base.

In reality, the MOSFET and heat flow paths are 3-dimensional. Thus, one has to be aware that Rth(j-mb) and the network seen in [Fig.](#page-8-0) 11, is actually an extensive 3-D parallel resistor network. In addition, the parameter describes the thermal characteristics under steady-state conditions. Therefore, the average power dissipation through the MOSFET should be used in order to obtain the temperature values at various locations in the device.

The thermal resistance from junction to top-case for standard power packages is a confusing parameter to many people. It can be referred to by Rth(j-tc), Rth(j-top) or Rth(j-ctop). For the sake of consistency, it will be referred to by Rth(j-tc) for the remainder of this document. Nexperia receives a number of these requests, as some would like to use the value to estimate the junction temperature of a MOSFET. However, using the Rth(j-tc) value is unnecessary and below are some of the reasons explaining why it is not stated on the data sheets of bottom-cooled MOSFETs.

It has already been established that the path at which heat flows from the junction to the ambient is through a parallel resistor network. As stated previously, the heat flow from the junction to the mounting base is the dominant path due to the high thermal conductivity and large surface area of the mounting base. The surface of the top-case and the rest of the encapsulant for that matter, is made from plastic. This material has a lower thermal conductivity and therefore a higher thermal resistance compared to other materials in the device such as copper alloy and solder. Therefore, heat takes longer to propagate through to the ambient via the encapsulant per unit time compared to the large metallic mounting base. As such, it is considered to be a minor heat flow path shown by the small blue arrows in [Fig. 12](#page-8-1).

Since the heat flow path through the top-case to the ambient is highly resistive, the power dissipated through it can be assumed to be negligible. Thus Rth(j-tc) is not stated on the data sheets for standard, bottom-cooled power packages.

Due to the slow propagation of heat through the top-case, it is found to be similar but slightly lower in temperature compared to the junction at steady-state conditions. This has been verified through various thermal simulations using CFD as illustrated in [Table](#page-9-0) 5.

**Table 5. Percentage difference between junction temperature and top-case temperature using various mounting base copper areas**

| Mounting base area | Power input (W) |       |      |
|--------------------|-----------------|-------|------|
|                    | 0.1 W           | 0.5 W | 1 W  |
| 10 mm x 10 mm      | 1.7%            | 2.9%  | 3.7% |
| 20 mm x 20 mm      | 1.5%            | 2.8%  | 3.6% |
| 30 mm x 30 mm      | 1.0%            | 2.7%  | 3.7% |

From this data, it can be seen that the percentage difference in between junction temperature and top-case temperature increases slightly as power input to the device increases. In addition, there is negligible percentage difference between junction temperature and top-case temperature when varying the copper area that the device is mounted upon. This proves that the mounting base is the dominant path for heat to exit the device.

If one is able to use a thermocouple or a thermal camera to record the top-case temperature, the junction temperature can be estimated with reasonable confidence as within 10 °C above the topcase temperature. When using a thermocouple, slight differences in temperature readings may come as a result of different wire lengths used. Also the method of attachment to the device can cause variations due to the slight heatsinking effect of the thermocouple. Therefore, the use of a thermal camera would be the most preferred method to record the top-case temperature of a bottom-cooled MOSFET.

## **2.3.2. Thermal resistance junction to ambient - Rth(j-a)**

The thermal heat path between the MOSFET junction and the ambient encompasses paths within the MOSFET itself as well as additional ones when a MOSFET is mounted onto a PCB. Hence, heat may spread from the junction towards the mounting base and the case. Afterwards, when the extremities of the MOSFET are reached, the heat will flow into the surroundings via the PCB or directly from the case. These heat paths are depicted in [Fig. 13](#page-9-1).

[Fig. 13](#page-9-1) a) shows the heat moving from the junction to the mounting base and to the case top and afterwards to the ambient. [Fig. 13](#page-9-1) b) shows the heat moving from the mounting base to the PCB and through it in order to reach the ambient.

A simplified thermal circuit may be seen in [Fig. 14.](#page-10-0) It is important to notice that the two thermal paths from the component to the ambient are in parallel, thus improving both may be redundant.

A more cost effective method of reducing the thermal resistance between the MOSFET to the surroundings may be to focus on one of the thermal paths and improve it in the best way possible.

[Fig. 15](#page-10-1) shows a thermal circuit which encompasses the MOSFET the PCB and the environment, it may be observed that the three heat spreading methods are shown by individual thermal resistors. In this particular case, the heat spreads:

- Through *conduction* from the junction towards the outside of the MOSFET, represented by the mounting base and the case.
- From the case to the ambient the heat propagates through *convection* and *radiation*.
- From the mounting base to the PCB and into it, *conduction* is again the main way of propagation.
- From the PCB into the environment *convection* and *conduction* are the main methods through which heat propagates to the ambient, radiation is usually negligible.

The thermal circuit seen in [Fig. 15](#page-10-1) is also represented in [Fig. 1](#page-2-1). Finally, the two thermal resistor networks highlighted in green are also represented in [Fig. 14](#page-10-0).

### **2.3.3. PCB thermal limitation and the 1 Watt rule**

As previously described, the junction to ambient thermal path contains the board or PCB. This is often made from FR4 material, which from a thermal and electrical perspective is an insulator. Moreover, planes, pours and traces of copper are also present as these provide the circuit interconnections. Altogether we can consider them as forming the board and giving it a certain thermal characteristic called the board thermal resistance. It was found that this value is

approximately **50-60** *K/W*, depending on the amount of copper, insulation layer thickness and other factors. Since this is specific to the materials and dimensions of a board, this limit is imposed.

Moreover, the ambient temperature in which a board operates, the thermal limitations of a system, the FR4 temperature limit of 120 °C to 140 °C, as well as the temperature ranges within which a board needs to function in, gives rise to a power limitation. These same dependencies can be noted from the following equations:

Thermal resistivity
$$\left[\frac{mK}{W}\right] = \frac{1}{Thermal\ conductivity \left[\frac{W}{mK}\right]}$$
 (5)

Thermal resistance
$$\left[\frac{K}{W}\right] = Thermal resitivity \left[\frac{mK}{W}\right] \times \frac{Thickness [m]}{Area [m^2]}$$
 (6)

Thermal resistance
$$\left[\frac{K}{W}\right] = \frac{Temperature \ difference \ [K]}{Power \ [W]}$$
 (7)

PCB thickness, area and thermal resistivity determine the PCB thermal resistance, given in K/W. Hence, given a specific ambient temperature and a maximum FR4 temperature, or the system maximum operation temperature, a  $\Delta T$  is obtained.

Example: calculate the power dissipation of a MOSFET mounted on an FR4 PCB within an automotive environment where the ambient temperature is 80 °C.

- The FR4 PCB material has a thermal resistance R<sub>th(FR4 PCB)</sub> = 50 K/W
- The FR4 PCB material maximum temperature (T<sub>FR4(max)</sub>) = 130 °C
- The ambient temperature T<sub>amb</sub> = 80 °C

$$\Delta T = T_{FR4(max)} - T_{(amb)} = 130 \, ^{\circ}C - 80 \, ^{\circ}C = 50 \, ^{\circ}C$$
 (8)

$$P = \frac{\Delta T}{R_{th(FR4\ PCB)}} = \frac{50\ K}{50\ K/W} = 1\ W \tag{9}$$

Given the above ambient temperature and FR4 PCB characteristics, approximately 1 watt of power may be dissipated in a MOSFET within this automotive environment.

### 2.3.4. Thermal nomenclature

Terminology surrounding thermal characterization of power MOSFETs has been revised multiple times over the years. Regardless of these efforts, standards organizations and semiconductor manufacturers may still use different names when referring to the same thermal parameter, or to slightly different variations of it. The terms often used to indicate one or the other type of thermal resistance are: R and  $\theta$ . In the case of junction to ambient, the  $R_{th(i-amb)} = R_{\theta(i-amb)} = \theta_{(i-amb)}$ .


# **3. LFPAK56D and LFPAK33**

## **3.1. Simple configuration with a single layer**

In this section, we will present the maximum power dissipation results for a simple PCB configuration using a single layer with varying copper area.

Results for the LFPAK56D and LFPAK33 packages are given, for the LFPAK56D with only one or with both MOSFETs conducting.

### **3.1.1. LFPAK56D**

#### Set-up:

- 1 layer on the top
- MOSFET power dissipation is 0.1 W, 0.5 W and 1 W applied to each MOSFET
- Maximum junction temperature of 175 °C
- PCB material is standard FR4, 1.6 mm thickness, dimension 100 x 100 mm
- Maximum PCB operating temperature of 120 °C
- Copper thickness is 2 oz./ft<sup>2</sup> (70 μm)
- The PCB is suspended in free air at ambient temperature of 20 °C
- The simulation is carried out for conduction, convection and radiation heat transfer
- There is no forced air cooling applied, i.e. only natural convection is modeled

The simplest possible PCB stack-up is that of a single top copper layer, see [Fig. 16.](#page-12-0)

In this analysis, we will examine the variation in device junction temperature (T<sup>j</sup> ) as a function of the top copper area.

The graph in [Fig. 17](#page-13-0) captures two important factors:

- T<sup>j</sup> depends greatly on length "x" and thus copper area, the bigger the area the better the thermal performance
- However, the ability of the top copper to provide heatsinking for the MOSFET shows a "law of diminishing returns". In other words, we cannot keep on adding more copper area in the hope of

# **3.1.3. LFPAK33**

### Set-up:

- 1 layer on the top
- MOSFET power dissipation is 0.1 W, 0.5 W and 1 W applied in the MOSFET
- Maximum junction temperature of 175 °C
- PCB material is standard FR4, 1.6 mm thickness, dimension 100 x 100 mm
- Maximum PCB operating temperature of 120 °C
- Copper thickness is 2 oz./ft<sup>2</sup> (70 μm)
- The PCB is suspended in free air at ambient temperature of 20 °C
- The simulation is carried out for conduction, convection and radiation heat transfer
- There is no forced air cooling applied i.e. only natural convection is modeled

The simplest possible PCB stack-up is that of a single top copper layer. In this analysis, we will examine the variation in device junction temperature (T<sup>j</sup> ) as a function of top copper area.

The graph in [Fig. 23](#page-17-0) captures two important factors:

- T<sup>j</sup> depends greatly on length "x" and thus copper area, the bigger the area the better the thermal performance
- However, the ability of the top copper to provide heatsinking for the MOSFET shows a "law of diminishing returns". In other words, we cannot keep on adding more copper area in the hope of continuing to reduce T<sup>j</sup> . As can be seen from [Fig. 23](#page-17-0) below, T<sup>j</sup> will plateau at around 40 °C (for 0.5 W per MOSFET) no matter how much copper area we provide.

Care must be taken for T<sup>j</sup> above 120 °C as PCB temperature directly under the transistor would be close to the MOSFET T<sup>j</sup> .

An alternative to the previous approach is to look at the maximum power allowed before reaching Tj(max) = 175 °C (MOSFET absolute max). Maximum power allowed is shown for different ambient temperature and copper length. In this example the PCB temperature was not considered so care must be taken for the resulting heat on the PCB.

In the graph below, [Fig. 24,](#page-18-0) the maximum power for the conditions given is as follows:

Tamb = 20 °C: Max power is 3.7 W in the MOSFET Tamb = 80 °C: Max power is 2.4 W in the MOSFET

**Fig. 24. Maximum permissible power dissipation as a function of copper side length x for LFPAK33**

# **3.2. Usual configuration: 4 layers + vias**

In this section, we will present the maximum power dissipation results for a PCB configuration using 4 layers + vias for dissipation on the bottom layer, with varying copper area.

Results for the LFPAK56D and LFPAK33 packages are given, for the LFPAK56D with only one or with both MOSFETs conducting.

### **3.2.1. LFPAK56D**

- 4 layers + vias (vias number increases with the copper area with a maximum of 25 vias for each side)
- MOSFET power dissipation is 0.1 W, 0.5 W and 1 W applied to each MOSFET
- Maximum junction temperature of 175 °C
- PCB material is standard FR4, 1.6 mm thickness, dimension 100 x 100 mm
- Maximum PCB operating temperature of 120 °C
- Copper thickness on all layers (external and internal) is 2 oz./ft<sup>2</sup> (70 μm)
- The PCB is suspended in free air at ambient temperature of 20 °C
- The simulation is carried out for conduction, convection and radiation heat transfer
- There is no forced air cooling applied i.e. only natural convection is modeled

The common PCB stack-up is 4 layers with vias under MOSFETs to create a dissipation path to the heatsink.

In this analysis, we will examine the variation in device junction temperature (T<sup>j</sup> ) as a function of top copper area. In [Fig. 25](#page-19-0) below, we can see the vias configuration:

**Fig. 26. Sectional view: LFPAK56D**

**Table 6. Limitation of number of vias**

| X (mm)               | vias configuration |                                                                     |                                          |  |
|----------------------|--------------------|---------------------------------------------------------------------|------------------------------------------|--|
| minimal<br>footprint | 2+2 vias           | Vias pitch 2.5 mm<br>Vias side length 0.7 mm                        |                                          |  |
| 6                    | 9+9 vias           | Maximum number<br>of vias able to be inserted in the copper surface | Copper thickness 70 μm<br>No solder fill |  |
| 8                    | 12+12 vias         |                                                                     |                                          |  |
| 10                   | 20+20 vias         |                                                                     | 25 vias maximum                          |  |
| 15                   | 25+25 vias         |                                                                     |                                          |  |
| 20                   | 25+25 vias         |                                                                     |                                          |  |
| 25                   | 25+25 vias         |                                                                     |                                          |  |
| 30                   | 25+25 vias         |                                                                     |                                          |  |
| 35                   | 25+25 vias         |                                                                     |                                          |  |
| 40                   | 25+25 vias         |                                                                     |                                          |  |
| 50                   | 25+25 vias         |                                                                     |                                          |  |

The graph in [Fig. 27](#page-20-0) captures two important factors:

- T<sup>j</sup> depends greatly on length "x" and thus copper area, the bigger the area the better the thermal performance
- However, the ability of the top copper to provide heatsinking for the MOSFET shows a "law of diminishing returns". In other words, we cannot keep on adding more copper area in the hope of continuing to reduce T<sup>j</sup> . As can be seen from the graph in [Fig. 27](#page-20-0), T<sup>j</sup> will plateau at around 36 °C (for 0.5 W per MOSFET) no matter how much copper area we provide.

Care must be taken for Tj above 120 °C as the PCB temperature directly under the transistor would be close to the MOSFET T<sup>j</sup> .

An alternative to the previous approach is to look at the maximum power allowed before reaching Tj(max) = 175 °C (MOSFET absolute max). Maximum power allowed is shown for different ambient temperature and copper length. In this example the PCB temperature was not considered so care must be taken for the resulting heat on the PCB.

In the graph below, [Fig. 28](#page-21-0) the maximum power for the conditions given is as follows:

Tamb = 20 °C: Max power is 5.3 W per MOSFET ( 2 × 5.3 W permissible in this package)

Tamb = 80 °C: Max power is 3.55 W per MOSFET ( 2 × 3.55 W permissible in this package)

**Fig. 28. Maximum permissible power dissipation as a function of copper side length x for LFPAK56D**

## **3.2.2. LFPAK56D only one MOSFET active at a time**

In a typical half bridge application only one MOSFET conducts at a time. [Fig. 29](#page-22-0) below shows the results for 1 W applied to the left MOSFET (blue curve). We can see that 1 W dissipated in one MOSFET is not equivalent to 0.5 W dissipation in each of the two MOSFETs (yellow curve).

As can be seen temperature is higher in the case of one MOSFET conducting with 1 W than it is with two MOSFETs each dissipating 0.5 W.

(1) P = 2 x 0.5 W; this section shows a relatively lower junction temperature compared to others.

(2) P = 1 W on the left side; this section indicates an intermediate level of junction temperature for one side being at 1 W.

(3) P = 2 x 1W; this section demonstrates a higher junction temperature than (1) and (2).

(4) PCB limit: This section shows the maximum allowable junction temperature based on the PCB limitations.

The graph includes four points for each condition labeled (1), (2), (3), and (4), illustrating how the junction temperature varies with copper side length 'x'.

An alternative to the previous approach is to look at the maximum power allowed before reaching Tj(max) = 175 °C (MOSFET absolute max). Maximum power allowed is shown for different ambient temperature and copper length. In this example the PCB temperature was not considered so care must be taken for the resulting heat on the PCB.

In [Fig. 30](#page-22-1) the maximum power for the conditions given is as follows:

- Tamb = 20 °C: Max power is 6 W with only left MOSFET
- Tamb = 80 °C: Max power is 4 W with only left MOSFET

As previously mentioned, when only one MOSFET is active the second MOSFET does not make a significant contributution to the total dissipation capabilty – see [Fig. 21](#page-16-0).

### **3.2.3. LFPAK33**

- 4 layers + vias (vias number increases with the copper area with a maximum of 25 vias for each side)
- MOSFET power dissipation is 0.1 W, 0.5 W and 1 W applied in the MOSFET
- Maximum junction temperature of 175 °C
- PCB material is standard FR4, 1.6 mm thickness, dimension 100 x 100 mm
- Maximum PCB operating temperature of 120 °C
- Copper thickness on all layers (external and internal) is 2 oz./ft<sup>2</sup> (70 μm)
- The PCB is suspended in free air at ambient temperature of 20 °C
- The simulation is carried out for conduction, convection and radiation heat transfer
- There is no forced air cooling applied i.e. only natural convection is modeled

The common PCB stack-up is 4 layers with vias under the MOSFETs to create a dissipation path to the heatsink.

In this analysis, we will examine the variation in device junction temperature (T<sup>j</sup> ) as a function of top copper area.

In [Fig. 31](#page-23-0) below, we can see the vias configuration:

**Fig. 32. Sectional view: LFPAK33**

**Table 7. Vias configuration**

| X (mm)               | vias configuration | Pitch (mm)                             | Vias side length (mm)                    |
|----------------------|--------------------|----------------------------------------|------------------------------------------|
| minimal<br>footprint | 1 via              | Vias pitch 2.5<br>Vias side length 0.7 |                                          |
| 6                    | 6 vias             | inserted in the copper<br>surface      | Copper thickness 70 μm<br>No solder fill |
| 8                    | 9 vias             |                                        |                                          |
| 10                   | 20 vias            |                                        | 25 vias maximum                          |
| 15                   | 25 vias            |                                        |                                          |
| 20                   | 25 vias            |                                        |                                          |
| 25                   | 25 vias            |                                        |                                          |
| 30                   | 25 vias            |                                        |                                          |
| 35                   | 25 vias            |                                        |                                          |
| 40                   | 25 vias            |                                        |                                          |
| 50                   | 25 vias            |                                        |                                          |

The graph [Fig. 33](#page-25-0) captures two important factors:

- T<sup>j</sup> depends greatly on length "x" and thus copper area, the bigger the area the better the thermal performance
- However, the ability of the top copper to provide heatsinking for the MOSFET shows a "law of diminishing returns". In other words, we cannot keep on adding more copper area in the hope of continuing to reduce T<sup>j</sup> . As can be seen from [Fig. 33](#page-25-0) below T<sup>j</sup> will plateau at around 33 °C (for 0.5 W per MOSFET) no matter how much copper area we provide.

Care must be taken for T<sup>j</sup> above 120 °C as PCB temperature directly under the transistor would be close to the MOSFET T<sup>j</sup> .

An alternative to the previous approach is to look at the maximum power allowed before reaching Tj(max) = 175 °C (MOSFET absolute max). Maximum power allowed is shown for different ambient temperature and copper length. In this example the PCB temperature was not considered so care must be taken for the resulting heat on the PCB.

In the graph below the maximum power for the conditions given is as follows:

Tamb = 20 °C: Max power is 6.5 W in the MOSFET Tamb = 80 °C: Max power is 4.3 W in the MOSFET

**Fig. 34. Maximum permissible power dissipation as a function of copper side length x for LFPAK33**

# **3.3. Placement advice for improved dissipation**

In this section, we will present some results for two MOSFETs placed close to each other on a single layer PCB with varying copper area.

### **3.3.1. LFPAK56D**

Simulation of two MOSFETs placed next to each other is carried out and checked against results seen in [section 2.1.](#page-12-1) The aim is to understand the dissipation effect that the two LFPAK56D have on one another.

#### Set-up

- 1 layer on the top side
- MOSFET power dissipation is 0.5 W applied to each MOSFET
- Maximum junction temperature of 175 °C
- PCB material is standard FR4, 1.6 mm thickness, dimension 200 x 150 mm
- Maximum PCB operating temperature of 120 °C
- Copper thickness on all layers (external and internal) is 2 oz./ft<sup>2</sup> (70 μm)
- The PCB is suspended in free air at ambient temperature of 20 °C
- The simulation is carried out for conduction, convection and radiation heat transfer
- There is no forced air cooling applied i.e. only natural convection is modeled

The simplest possible PCB stack-up is that of a single top copper layer. In this analysis, we will examine the variation in device junction temperature (T<sup>j</sup> ) as a function of top copper area.

- 2 mm gap between right and left copper layers
- Simulation carried out for different length "x"
- 0.5 W applied on each internal MOSFET

**Fig. 35. Copper area configuration: LFPAK56D, single top copper layer**

The graph in [Fig. 36](#page-27-0) shows:

- The results (in green) are similar to the ones observed in [section 2.1](#page-12-1) (slightly higher +3 °C)
- This is due to the low conductivity of FR4, despite only 2 mm gap it showed no heat transfer from one copper area to the other

### **3.3.2. LFPAK33**

Simulation of two MOSFETs placed next to each other is carried out and checked against results seen in [section 2.3.](#page-16-1) The aim is to understand the dissipation effect that the two MOSFETs have on one another.

- 1 layer on the top
- MOSFET power dissipation is 0.5 W applied in the MOSFET
- Maximum junction temperature of 175 °C
- PCB material is standard FR4, 1.6 mm thickness, dimension 200 x 150 mm
- Maximum PCB operating temperature of 120 °C
- Copper thickness is 2 oz./ft<sup>2</sup> (70 μm)
- The PCB is suspended in free air at ambient temperature of 20 °C
- The simulation is carried out for conduction, convection and radiation heat transfer
- There is no forced air cooling applied i.e. only natural convection is modeled

The simplest possible PCB stack-up is that of a single top copper layer. In this analysis, we will examine the variation in device junction temperature (T<sup>j</sup> ) as a function of top copper area.

- 2 mm gap between right and left copper layers
- Simulation carried out for different length "x"
- 0.5 W applied on each MOSFET

- A length of 200 mm is marked on one side.
- On the opposite side, there's a length measurement of 150 mm next to FR4 material, indicating the substrate thickness or type.
- There is a 'Length x' label above both measurements, signifying that these lengths are along the same dimension axis.
- A small gap of 2 mm is noted between layers, and this spacing is kept constant throughout the configuration.

This figure is designated as Figure 37 in the document.

The graph in [Fig. 39](#page-29-0) shows:

- The results for x > 20 mm are similar to the ones observed in [section 2.3](#page-16-1) (slightly higher +3 °C)
- This is due to the low conductivity of FR4, despite only 2 mm gap it showed no heat transfer from one copper area to the other
- For x < 20 mm results show up to 20 °C higher compared to the results from [section 2.3.](#page-16-1)
- This is due to the MOSFETs being brought closer to each other as a result of reduced copper area – note that in this case the space between MOSFETs is half the space between MOSFETs in the case of LFPAK56D

In [Fig. 38](#page-29-1) you can see that for x = 10 mm, the distance between the LFPAK33 MOSFETs is approximatively 10 mm. Less than 20 mm apart, the MOSFETs are close enough to heat each other, hence we start to see a temperature difference.

**Fig. 38. Copper area configuration: 2 x LFPAK33, 2 x LFPAK56D; separation between MOSFETs**

**Fig. 39. Junction temperature as a function of copper side length x for 2 LFPAK33**


# **3.4. Comparison between two LFPAK56 and one LFPAK56D, then one LFPAK56D and two LFPAK33**

In this section we will present some comparative results for different package devices on a single layer board with varying copper area.

### **3.4.1. Two LFPAK56 to LFPAK56D**

In this section the results of two single LFPAK56 MOSFETs are compared to the results of one dual LFPAK56D MOSFET (see [Section 3.1.1](#page-12-1))

The aim is to highlight the benefit of using one LFPAK56D dual MOSFET instead of two single LFPAK56 MOSFETs.

### Set-up:

- 1 layer on the top
- MOSFET power dissipation is 0.5 W applied to each MOSFET
- Maximum junction temperature of 175 °C
- PCB material is standard FR4, 1.6 mm thickness, dimension 100 x 100 mm
- Maximum PCB operating temperature of 120 °C
- Copper thickness is 2 oz./ft<sup>2</sup> (70 μm)
- The PCB is suspended in free air at ambient temperature of 20 °C
- The simulation is carried out for conduction, convection and radiation heat transfer
- There is no forced air cooling applied, i.e. only natural convection is modeled

The simplest possible PCB stack-up is that of a single top copper layer. In this analysis, we will examine the variation in device junction temperature (T<sup>j</sup> ) as a function of top copper area.

- Same gap between copper layer was used for both single LFPAK56 and dual LFPAK56D
- Simulation carried out for different length "x".
- 0.5 W applied on each MOSFET

**Fig. 40. Copper area configuration: 1 x LFPAK56D, 2 x LFPAK56, single top copper layer**

The graph in [Fig. 41](#page-31-0) shows:

• Overall two single LFPAK56 show better heat dissipation than one dual LFPAK56D by up to approximately 10 °C. This is due to the larger surface area of the LFPAK56 drain tab giving improved heat spreading and thermal dissipation.

• Note that the 10 °C is the relative figure between the two packages, the most important factor is the operating junction temperature

• If there is enough margin before reaching 175 °C at the junction, then LFPAK56D offers an attractive option due to its space saving

### **3.4.2. LFPAK56D to two LFPAK33**

In this section the results of one dual LFPAK56D MOSFET are compared to the results of two single LFPAK33 MOSFETs (see [section 4.2](#page-27-1))

Aim is to highlight the benefit of using one LFPAK56D dual instead of two single LFPAK33.

- 1 layer on the top
- MOSFET power dissipation is 0.5 W applied to each MOSFET
- Maximum junction temperature of 175 °C
- PCB material is standard FR4, 1.6 mm thickness, dimension 100 x 100 mm
- Maximum PCB operating temperature of 120 °C
- Copper thickness is 2 oz./ft<sup>2</sup> (70 μm)
- The PCB is suspended in free air at ambient temperature of 20 °C
- The simulation is carried out for conduction, convection and radiation heat transfer
- There is no forced air cooling applied, i.e. only natural convection is modeled

The simplest possible PCB stack-up is that of a single top copper layer. In this analysis, we will examine the variation in device junction temperature (T<sup>j</sup> ) as a function of top copper area.

- Same gap between copper layer was used for both single LFPAK33 and dual LFPAK56D
- Simulation carried out for different length "x"
- 0.5 W applied on each MOSFET

**Fig. 42. Copper area configuration: 1 x LFPAK56D, 2 x LFPAK33, single top copper layer**

#### The graph in [Fig. 43](#page-32-0) shows:

- Overall two single LFPAK33 show better heat dissipation than a dual LFPAK56D by up to approximately 5 °C. This is due to the larger drain surface area of the LFPAK33 offering better thermal dissipation, (less improvement than with LFPAK56 as LFPAK33 is a smaller package).
- Note that the 5 °C is the relative figure between the two packages, the most important factor is the operating junction temperature.
- If there is enough margin before reaching 175 °C at the junction, then LFPAK56D offers an attractive option due to all the advantages that one component offers versus two in terms of PCB layout, placement, cost effectiveness, etc.

**Fig. 43. Junction temperature as a function of copper side length x for 1 LFPAK56D and 2 LFPAK33**

# 3.5. Impact of R<sub>th(j-mb)</sub> compared to R<sub>th(mb-a)</sub>

Dissipation losses from the MOSFET junction are not mainly limited by the thermal resistance  $R_{th(j-mb)}$  as this is very low. The high thermal path for heat dissipation is presented by the thermal resistance  $R_{th(mb-amb)}$  (mounting base to PCB to ambient).

Example: for the part number BUK7M15-60E (LFPAK33, 15 m $\Omega$ , 60 V) the maximum thermal resistance junction to mounting base is 2.43 K/W:

Table 8. Thermal resistance BUK7M15-60E

| Symbol         | Parameter                                                     | Conditions | Min | T_{th(j-mb)} | Max  | Unit |
|----------------|---------------------------------------------------------------|------------|-----|--------------|------|------|
| $R_{th(j-mb)}$ | thermal<br>resistance<br>from junction<br>to mounting<br>base | Fig. 5     | -   | 2.01         | 2.43 | K/W  |

Using thermal simulation (Flotherm) with the following conditions:

0.5 W of losses in the MOSFET, air ambient is 20 °C, 35  $\mu m$  copper, we can calculate some thermal resistance.

- R<sub>th(j-mb)</sub> is 0.8 K/W
  - This is a lower value than given in the data sheet due to the simulation using ideal conditions
- As can be seen in <u>Table 9</u> below, thermal resistance for other items have high value compared Rth j-mb
- The total thermal resistance, junction to ambient, is 59.4 K/W when using 65.4 °C as (ambient) reference point.

Table 9 lists temperatures for different points captured in the simulation and shown in Fig. 45.

Table 9. Breakdown of thermal resistance for a simple case

| Thermal resistance part                    | Temperature (°C) | Rth (K/W) |
|--------------------------------------------|------------------|-----------|
| Junction                                   | 95.1             | -         |
| Mounting base                              | 94.7             | 0.8       |
| PCB under MOSFET                           | 88.6             | 12.2      |
| PCB to the right of the MOSFET             | 86.6             | 4         |
| Ambient air 0.5 mm over the top of the PCB | 79.1             | 15        |

| Thermal resistance part                     | Temperature (°C) | Rth (K/W) |
|---------------------------------------------|------------------|-----------|
| Ambient air 1 mm over the<br>top of the PCB | 65.4             | 27.4      |

Due to the very low thermal resistance between junction and mounting base it is very important to take care of design surrounding the MOSFET, (i.e. thermal vias, copper area, heat sink, water cooling, air cooling), in order to reduce the total thermal resistance.


# **4. LFPAK56 and LFPAK88**

## **4.1. Simple configuration with a single layer**

In this section, we will present the maximum power dissipation results for a simple PCB configuration using a single layer with varying copper area.

Results are given for the LFPAK56 and LFPAK88 packages. Models used are based on 1 mΩ LFPAK56E and LFPAK88.

### **4.1.1. Set-up:**

- 1 copper layer on the top
- MOSFET power dissipation is 1 W, 1.5 W and 2 W
- Maximum junction temperature of 175 °C
- PCB material is standard FR4, 1.6 mm thickness, dimension 100 x 100 mm
- PCB operating temperature of 120 °C and T<sup>j</sup> of 175 °C are highlighted in graphs
- Copper thickness is 2 oz./ft<sup>2</sup> (70 μm)
- The PCB is suspended in free air at ambient temperature of 20 °C
- The simulation is carried out for conduction, convection and radiation heat transfer
- There is no forced air cooling applied, i.e. only natural convection is modeled

The simplest possible PCB stack-up is that of a single top copper layer, see [Fig. 46.](#page-35-0)

In this analysis, we will examine the variation in device junction temperature (T<sup>j</sup> ) as a function of the top copper area and calculate the maximum power that can be safely dissipated in the MOSFET to reach a T<sup>j</sup> of 175 °C.

**Fig. 46. Copper area configuration: LFPAK56, single top copper layer, the configuration is the same for LFPAK88**

### **4.1.2. Junction temperature as a function of copper area**

The graphs in [Fig. 47](#page-36-0) and [Fig. 48](#page-36-1) capture two important factors:

- T<sup>j</sup> depends greatly on length "x" and thus copper area, the bigger the area the better the thermal performance
- However, the ability of the top copper to provide heatsinking for the MOSFET shows a "law of diminishing returns". In other words, we cannot keep on adding more copper area in the hope of continuing to reduce T<sup>j</sup> . As can be seen from [Fig. 47](#page-36-0) below, for LFPAK56, 1 W profile, T<sup>j</sup> will plateau at around 55 °C.

**Note:** Standard FR4 PCBs operate at a maximum temperature of 120 °C, care must be taken for T<sup>j</sup> > 120 °C as the PCB area directly under the transistor will be close to the MOSFET junction temperature, (due to low Rth(j-mb)).

The graphs below also shows the absolute minimum copper area needed for T<sup>j</sup> ≤ 175 °C.

**Fig. 47. Junction temperature as a function of copper side length x for LFPAK56**

**Fig. 48. Junction temperature as a function of copper side length x for LFPAK88**

## **4.1.3. Maximum allowed power dissipation as a function of copper area**

The maximum allowed power dissipation is shown in [Fig. 49](#page-37-0) and [Fig. 50](#page-37-1) below, for different ambient temperature and copper side length. In this example the PCB temperature was not considered so care must be taken for the resulting heat on the PCB.

From graphs in [Fig. 49](#page-37-0) and [Fig. 50](#page-37-1) the maximum permissible power, (Tamb = 20 °C), is 5.05 W and 5.9 W for the LFPAK56 and LFPAK88 packages respectively:

**Table 10. Maximum power dissipation**

| Device  | Tamb = 20 °C | Tamb = 80 °C |
|---------|--------------|--------------|
| LFPAK56 | 5.05 W       | 3.2 W        |
| LFPAK88 | 5.9 W        | 3.8 W        |

**Fig. 49. Maximum permissible power dissipation as a function of copper side length "x" for LFPAK56**

**Fig. 50. Maximum permissible power dissipation as a function of copper side length "x" for LFPAK88**

## **4.2. Usual configuration: 4 layers + vias**

In this section, we will present the maximum power dissipation results for a PCB configuration using 4 layers + vias for dissipation on the bottom layer, with varying copper area.

Results are given for the LFPAK56 and LFPAK88 packages.

### **4.2.1. Set-up:**

- Four layers with vias (max number of vias is 25 and for small copper areas this number will decrease accordingly, see [Table](#page-39-0) 11)
- MOSFET power dissipation is 1 W, 1.5 W and 2 W
- Maximum junction temperature of 175 °C
- PCB material is standard FR4, 1.6 mm thickness, dimension 100 x 100 mm
- PCB operating temperature of 120 °C and T<sup>j</sup> of 175 °C are highlighted in graphs
- Copper thickness of all layers is 2 oz./ft<sup>2</sup> (70 μm)
- The PCB is suspended in free air at ambient temperature of 20 °C
- The simulation is carried out for conduction, convection and radiation heat transfer
- There is no forced air cooling applied, i.e. only natural convection is modeled

The common PCB stack-up is 4 layers with vias under the MOSFET to create a dissipation path to heatsink (no heat sink was used in simulation).

In this analysis, we will examine the variation in device junction temperature (T<sup>j</sup> ) as a function of copper area (same area size applied to all layers).

The configuration of the vias is shown below in [Fig. 51](#page-38-0) and [Fig. 52](#page-39-1):

**Fig. 51. Copper area configuration: LFPAK56, 4 layers with vias, the configuration is similar for LFPAK88**

Vias configuration: square vias used for ease of simulation.

**Fig. 52. Sectional view: LFPAK56**

**Table 11. Limitation of number of vias**

| X (mm) | Vias configuration | Comments                                       | Vias information                                                                                               |  |  |  |
|--------|--------------------|------------------------------------------------|----------------------------------------------------------------------------------------------------------------|--|--|--|
| 6      | 9 vias             | Maximum number of                              | Square vias: length 0.7 mm<br>Vias pitch:<br>2.5 mm (between vias in columns)<br>2.0 mm (between vias in rows) |  |  |  |
| 8      |                    | vias able to be inserted<br>in the copper area |                                                                                                                |  |  |  |
| 10     | 20 vias            |                                                | Copper thickness 70 μm<br>No solder fill                                                                       |  |  |  |
| 15     | 25 vias            | 25 vias maximum                                |                                                                                                                |  |  |  |
| 20     | 25 vias            |                                                | Copper thickness 70 μm<br>No solder fill                                                                       |  |  |  |
| 25     | 25 vias            |                                                |                                                                                                                |  |  |  |
| 30     | 25 vias            |                                                |                                                                                                                |  |  |  |
| 35     | 25 vias            |                                                |                                                                                                                |  |  |  |
| 40     | 25 vias            |                                                |                                                                                                                |  |  |  |
| 45     | 25 vias            |                                                |                                                                                                                |  |  |  |
| 50     | 25 vias            |                                                |                                                                                                                |  |  |  |
| 60     | 25 vias            |                                                |                                                                                                                |  |  |  |

### **4.2.2. Junction temperature as a function of copper area (4 layers and vias)**

The graphs in [Fig. 53](#page-40-0) and [Fig. 54](#page-40-1) below show the junction temperature as a function of drain copper area following the same trend as the single layer PCB configuration in that:

- T<sup>j</sup> depends greatly on copper area
- The ability of the top copper to provide heatsinking for the MOSFET shows a "law of diminishing returns".

**Fig. 53. Junction temperature as a function of copper side length x for LFPAK56**

**Fig. 54. Junction temperature as a function of copper side length x for LFPAK88**

## **4.2.3. Maximum allowed power dissipation as a function of copper area (4 layers and vias)**

From graphs in [Fig. 55](#page-41-0) and [Fig. 56](#page-41-1) the maximum power for a given package and conditions are as follows:

**Table 12. Maximum power dissipation**

| Device  |         | Tamb = 20 °C | Tamb = 80 °C |
|---------|---------|--------------|--------------|
| LFPAK56 | 9.6 W   | 6.3 W        |              |
| LFPAK88 | 10.65 W | 6.9 W        |              |

**Fig. 55. Maximum permissible power dissipation as a function of copper side length "x" for LFPAK56**

**Fig. 56. Maximum permissible power dissipation as a function of copper side length "x" for LFPAK88**


## **4.3. Simple configuration with a single split layer of copper**

In this section, we will present the maximum power dissipation results as per the previous section for a simple PCB configuration using a single layer and varying copper area, but with copper layer split in two part (one part placed under the drain tab of the MOSFET and the other under the source pins).

Results are given for the LFPAK88 package only.

### **4.3.1. Set-up:**

- 1 copper layer on the top split into two areas:
  - 3/5 of area under drain tab
  - 2/5 of area under source pins
- MOSFET power dissipation is 1 W, 1.5 W and 2 W
- Maximum junction temperature of 175 °C
- PCB material is standard FR4, 1.6 mm thickness, dimension 100 x 100 mm
- PCB operating temperature of 120 °C and T<sup>j</sup> of 175 °C are highlighted in graphs
- Copper thickness is 2 oz./ft<sup>2</sup> (70 μm)
- The PCB is suspended in free air at ambient temperature of 20 °C
- The simulation is carried out for conduction, convection and radiation heat transfer
- There is no forced air cooling applied, i.e. only natural convection is modeled

The simplest possible PCB stack-up is that of a single top copper layer, see [Fig. 57.](#page-42-0)

In this analysis, we will examine the variation in device junction temperature (T<sup>j</sup> ) as a function of the top copper area.

The graph in [Fig. 58](#page-43-0) captures what has been previously mentioned in terms of copper area and heat dissipation i.e. the bigger the area the better the thermal performance. More importantly in this configuration, it shows the importance in considering the source pins of an LFPAK MOSFET as a thermal path for efficiently dissipating heat.

The graph in [Fig. 58](#page-43-0) also shows that coper area of length "x" = 40 mm in split copper configuration provides a performance equivalent of that provided in the solid (non-split) copper area of length "x" = 60 mm.

Split copper configuration for length "x" = 40 mm is as follows:

- 24 mm x 40 mm copper area placed under the drain tab of the LFPAK MOSFET
- 16 mm x 40 mm copper area placed under the source pins of the LFPAK MOSFET

**Note:** Standard FR4 PCBs operate at maximum temperature of 120 °C, care must be taken for T<sup>j</sup> > 120 °C as PCB area directly under the transistor would be close to the MOSFET junction temperature (due to low Rth(j-mb)).

Results are for LFPAK88, but the principle applies to all Nexperia clip bond LFPAK devices. Tamb = 20 °C: Max power of ~6 W is achieved with an area of 40 mm x 40 mm single copper layer in split configuration, whist previously shown to require an area of 60 mm x 60 mm for single solid copper layer.

# 4.4. Impact of R<sub>th(j-mb)</sub> compared to R<sub>th(mb-amb)</sub>

The thermal resistance  $R_{th(j-mb)}$  of the MOSFET is very low and therefore dissipation losses are mainly limited by the high thermal resistive path presented by  $R_{th(mb-amb)}$  (mounting base to ambient).

Example: for the part number BUK7S1R0-40H (LFPAK88, 1 m $\Omega$ , 40 V) the maximum thermal resistance junction to mounting base is 0.4 K/W, see <u>Table 13</u>:

Table 13. Thermal resistance BUK7S1R0-40H

| Symbol    | Parameter          | Conditions                     | Min | Tour     | Max     | Unit |
|-----------|--------------------|--------------------------------|-----|----------|---------|------|
| Rth(j-mb) | thermal resistance | from junction to mounting base | -   | 0.35 K/W | 0.4 K/W |      |
|           | resistance         |                                |     |          |         |      |
|           | from junction      |                                |     |          |         |      |
|           | to mounting        |                                |     |          |         |      |
|           | base               |                                |     |          |         |      |

Using thermal simulation (Flotherm) with the following conditions:

- 1 W of losses in the MOSEFT
- · Ambient air temperature of 20 °C
- 70 µm copper

we can calculate the thermal resistance for different paths, example:

- 1 W of losses in the MOSFET
- Junction temperature = 52.2 °C
- Mounting base temperature = 52.0 °C
- $R_{\Theta} = \Delta T / P => R_{th(i-mb)} = 0.2 \text{ K/W}.$

This is lower than the measured value given in the data sheet due to simulation using ideal conditions.

As can be seen in Fig. 60 below, the thermal resistance between mounting base and ambient is of much higher value (~30 K/W) than  $R_{th(j-mb)}$ .

**Fig. 62. Thermal resistance LFPAK88: single split layer copper profile (40 x 40 mm: split into 24 x 40 mm and 16 x 40 mm)**

# **5. Conclusion**

All the LFPAK packages offer a very good junction to mounting base thermal performance, meaning that the mounting base can be near to the junction temperature, but this is often limited by the PCB high temperature capability.

It is very important for designs to reduce the thermal resistance between mounting base and the ambient environment as this will present the bottleneck in heat dissipation. All of Nexperia LFPAK packages use clip bond technology making their source pins a good thermal path in addition to the thermal path provided by the drain tab. To take full advantage of this feature, it is important for PCB layout designs to consider placing a good amount of copper under the source pins. The drain tab still presents the main thermal path for heat dissipation and should be the focus for any thermal design layout.

In all cases a configuration with 4 layers with vias substantially improves the heat dissipation.

This thermal guide establishes the necessary principles in thermal design approaches, combined with LFPAK packages features (i.e. low Rth(j-mb) and source clip bond) offer the designer good options in optimizing PCB thermal design.

Good thermal design practices should be applied to take advantage of the very good thermal performance LFPAK packages and Tj(max) must be kept < 175 °C for safe operation.
