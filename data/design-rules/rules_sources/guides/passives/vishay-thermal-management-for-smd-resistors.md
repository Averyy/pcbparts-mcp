---
source: "Vishay -- Thermal Management for SMD Resistors"
url: "https://www.vishay.com/docs/30380/terminalderating.pdf"
format: "PDF 4pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 10388
---
Resistors White Paper

# Thermal Management for Surface-Mount Devices

By Bryan Yarborough

#### AMBIENT TEMPERATURE DERATING

The origins of the ambient derating curve go back decades to when the U.S. military specified the performance requirements of components used in the design of their equipment. The purpose was to provide a high level of confidence that the components' performance would ensure system and equipment reliability. Some of these standards, such as MIL-PRF-39009 or MIL-PRF-39017, specified the performance requirements in various environmental conditions, such as power derating for increased ambient temperatures. The ambient derating curve was used because the resistor products available during that time were through-hole axial leaded devices, which dissipated approximately 80 % to 90 % of the power / heat energy to the air through convection. The lead provided a very small dissipation pathway to the PCB for power wirewounds, while the body provided a much larger pathway through air with the larger surface area and / or increased air velocity.

The higher power resistors have larger bodies that improve heat transfer to air, whereas smaller body through-hole parts operating at a lower power have a greater proportion of the power conducted to the PCB. This is indicated by the different points of derating for the different resistor technologies, as illustrated by the graphs below.

Wirewound Derating Film Derating

As component technology changed from through-hole to surface-mount devices (SMD), the military performance standards did not keep up, so there are no references to terminal derating curves and perhaps only a few references to circuit board thermal design requirements. Industry design requirements push for smaller, more power-dense designs, which has led to the development of terminal derating to describe maximum component power capability.

## Thermal Management for Surface-Mount Devices

Through-hole devices dissipate approximately 80 % of their heat energy by convection to the air, whereas SMD devices can transfer as much as 90 % of their heat energy to the PCB with conduction. This means that through-hole devices tend to be limited by ambient temperature conditions rather than heat transferred from adjacent parts through the PCB. SMD devices, however, are less influenced by ambient conditions and are more influenced by terminal temperatures based on PCB design (copper thickness, copper heatsink, and proximity to other nearby power devices). During the early years of SMDs, the thermal design for resistors wasn't a significant concern because the power ratings and / or densities were low enough that standard PCB designs could dissipate the heat. Now, resistor power density has become substantially high, in some cases reaching 260 W/in2. These new designs have led to the introduction of new terms for defining power ratings in resistors.

### TERMINAL DERATING

Terminal derating is a method of defining the power rating of an SMD resistor in terms of thermal dissipation performance, instead of ambient temperature conditions. The terminal derating bases the 100 % power rating of the SMD resistor on not exceeding a maximum resistance element temperature or hotspot (refer to illustration below), using the heat transfer characteristics of the component to a maximum specified terminal temperature. In other words, it is the maximum power rating generating the highest element temperature at which the resistance change is less than or equal to the specified limit.

Terminal derating requires the end user to design the PCB to ensure that the terminal temperature is not exceeded. Terminal derating is a method of controlling the component's power rating instead of detailed information about its thermal performance as compared to thermal resistance (refer to next section).

## THERMAL RESISTANCE (R OR RTH; UNITS: °C/W)

The thermal resistance value is determined in a resistor by the difference between hotspot temperature and the terminal temperature divided by the applied power.

RTH = (hotspot - terminal temperature) / power

The value expressed for thermal resistance is the amount of temperature rise due to the amount of power applied and is typically expressed as °C/W.

Thermal resistance represents the resistance to heat flow from the hotspot of the element to the terminal. A lower value indicates that the heat energy will be transferred more freely and will offer better power performance.

Example: [WSLF2512](http://www.vishay.com/doc?30193)

Page 2 under Dimensional Data - Thermal Resistance: refer to 0.5 m of 6.7 °C/W

In this example, a 0.5 m WSLF2512 will have a resistance element hotspot temperature 6.7 °C higher than the terminal temperature for 1 W of applied power, regardless of board thermal characteristics. Both the terminal temperature and the resistive element hotspot will be elevated above the product design limits if the board thermal capacity is not able to spread the heat energy or if neighboring power products elevate the board temperature. The thermal resistance remains constant at 6.7 °C/W because it is a characteristic of the part based on how heat energy transfers through the part due to the construction and materials.

By providing the thermal resistance value for the resistor, the end user is better able to relate heat dissipation in terms that are familiar from the power semiconductor industry, with thermal resistance of the junction to ambient or R(JA). The designer can directly relate the thermal management practices used for semiconductors, such as heavy copper, larger pad area, multiple vias, filled vias, ground planes, etc. The same PCB board design techniques that assure a semiconductor maintains safe thermal limits will ensure that the maximum power density can be achieved for Power Metal Strip® resistors. The following graphics illustrate the influences of PCB design on heat flow. For example, the use of thicker copper carries more heat than a thin layer, and thermal vias can transfer the heat to other thick copper layers or heatsinks.

## MEASURING THERMAL RESISTANCE

Thermal resistance values are determined by applying varying power and measuring the surface temperature of the resistor at the hottest spot and the terminal temperature using a thermal imaging camera, which does not sink heat like a thermocouple. The test board is mounted horizontally in 25 °C air with free convection (no forced air).

Designers using thermal simulation tools have used this power vs. temperature data to develop thermal models for their system designs. These tools generally do not require the highly detailed 3D models and material lists that are initially expected. They typically adapt a metal analog that has a comparable thickness and the heat transfer properties that are characterized by these data points using the thermal resistance value. It provides the essential information to create a thermal model and understand how the part transfers heat.

Thermal resistance can vary significantly for current sense resistors such as the [WSL,](http://www.vishay.com/doc?30100) [WSL-18,](http://www.vishay.com/doc?31057) [WSLP,](http://www.vishay.com/doc?30122) and [WSLP-18](http://www.vishay.com/doc?30298) families, where the construction depends on the resistance value. This is different from thick film resistors or commercial foil resistors that can have a single thermal resistance for all resistance values of the same case size, which is due to the resistance element being in direct contact with a dissipating mass that is consistent for all resistance values. The ceramic substrate provides a uniform and fixed thermal pathway for heat to dissipate from the resistance element to the PCB.

In Power Metal Strip resistors, the thermal resistance can differ because of different alloys, resistance element thicknesses, and laser trimming to achieve the resistance value. These differences affect the heat dissipation characteristics to the terminals, and therefore each value and size has a different thermal resistance value (consult the factory for details). In many cases, a higher thermal resistance can mean that the solder joint will remain cooler (however the device will be limited to lower power levels) as compared to other resistor technologies.

- 1. Resistive element
- 2. Copper terminal with solderable finish
- 3. Terminal to element weld
- 4. High temperature encapsulant

Power Metal Strip resistors such as the [WSLF2512,](http://www.vishay.com/doc?30193) [WSHP2818,](http://www.vishay.com/doc?30347) [WSK1216,](http://www.vishay.com/doc?30189) [WSLP-18](http://www.vishay.com/doc?30298), and [side-terminated WSL](http://www.vishay.com/doc?30183) offer features that reduce thermal resistance compared to standard parts to provide very high power densities, which can reduce power supply size and weight. One of the construction features is the side-terminated [WSL1020](http://www.vishay.com/doc?30183), which when compared to the standard 2010 reduces the path length from the hotpot to the terminal, as well as increasing the cross-sectional area contacting the PCB, thus decreasing the thermal resistance. A second feature that optimizes thermal performance is the large resistor elements of the [WSLF2512](http://www.vishay.com/doc?30193), [WSLP3921, WSLP 5931.](http://www.vishay.com/doc?30176) The [WSHP2818](http://www.vishay.com/doc?30347) uses several design features to achieve optimal thermal performance, including large copper terminals and a resistance element with a short thermal path to the copper terminals. The low thermal resistance ensures the power capability is maximized. It also ensures that TCR will have the smallest effect possible for the applied power, also called PCR or power coefficient of resistance.

#### Additional resources for Power Metal Strip resistors:

- Power Metal Strip overview: www.vishay.com/doc?49581
- Automotive Grade: www.vishay.com/doc?49924
- WSLP infographic: www.vishay.com/doc?48134
- Did You Know? Pulse Capability: www.vishay.com/doc?48158
- Power Metal Strip products datasheets: www.vishay.com/resistors-fixed/power-metal-strip/
