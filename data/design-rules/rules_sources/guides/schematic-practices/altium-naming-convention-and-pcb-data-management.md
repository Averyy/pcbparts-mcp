---
source: "Altium -- Naming Convention and PCB Data Management"
url: "https://resources.altium.com/p/naming-convention-and-pcb-data-management"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 7311
---

## Introduction

There is a poem by John Godfrey Saxe that was from a Hindu fable about the six blind men of Indostan who went to see the Elephant. The first went up and felt the side of the Elephant and concluded that he was touching a wall. The second went up and felt a tusk, exclaimed: “This is not a wall at all; it is a spear.” The third blind man, feeling the huge trunk, decided that it was a snake. The fourth man felt the elephant’s leg and said, “It is obvious this is a tree”. The fifth man touched the massive ears and decided it was a fan he was feeling. Finally, the last blind man, feeling the tail of the elephant, proudly proclaimed, “You are all wrong; this is very clearly a rope”.

The moral of this poem is that it’s your perception of things and how you name them that are most important for clarity and understanding. An additional point is that without a broader picture of things, you most likely will be mistaken. It is no different when working with information in a data management system. When PCB Designers are not following a set standard, the results are long searches when seeking out information, and additionally, the increased possibility of duplicate components or models.

## Schematic Symbols Naming Standard

Schematic symbols tend to denote general categories. Meaning you use a single symbol with many components. An excellent example of this is any of the discrete symbols for Capacitor, Resistor or Inductor. The naming convention is also very general—such as General Resistor or General Capacitor.

On the more complex components, it gets a little trickier. You need to pull up the datasheet and study the Product Identification System. Here is an example taken directly from the datasheet for the AT24C01C/02 IC EEPROM 1K I2C 1MHZ 8SOIC.

You see that there is the base Part number AT24C01C. The [other parameters](https://resources.altium.com/p/whats-in-a-name-component-development-part-2) of the component are Package Option, Device Grade, Operating Voltage, and Shipping Carrier Option.

*Figure 1. Vendor specific product identification systems are responsible for the naming standards of most modern day components. The name includes information about the device type and parameters.*

*Figure 2. Most components are available in multiple packages. The package option part of the product identification system describes which package the product belongs to*

What you want to look at is the package types and specifically the Pin Configurations. With that, you can see that with six different Packages, only the SOT23 uses a 5-pin device. So, we are looking at two possible Schematic Symbols.

The first symbol being the eight-pin parts.

*Figure 3. You should design the schematic symbol for the components you use depending on the packaging option you choose. Here’s one for the the 8-lead SOIC of the AT24C01C-SS.*

Using a rather simple naming convention scheme of <Base Number>-<Package Option>.
For example, would be **AT24C01C-SS\_X\_MA\_P\_C**.

The name for the final component (SOT23) would be the following symbol with its name of AT24C01C-ST. Between these two rather simple schematic symbols, they would support a total of 24 different components. The great thing about this is if they search on just base number of AT24C01C, then both schematic symbols come up showing all six used component package types.

*Figure 4. In comparison, you would design the schematic symbol for the 5-lead SOT23 version with only five pins.*

## Footprints Naming Standard

For the footprint, we are going to reference the [IPC standard](https://resources.altium.com/p/working-ipc-compliant-footprint-models) IPC-7351, which is the Generic Requirements for Surface Mount Design and Land Pattern Standard.

It is rather easy to understand. Each component has an assigned family which has a 3-4 letter identifier. Moreover, the specific dimensions of the component are used to identify it. It is all done with characters used as component body identifiers, which are:

P= Pitch for components with more than two leads
W= Maximum Lead Width (or Component Lead Diameter)
L= Body Length for horizontal mounting
D= Body Diameter for round component body
T= Body Thickness for rectangular component body
H= Height for vertically mounted components
Q= Pin Quantity for components with more than two leads
R= Number of Rows for connectors
A, B & C= the fabrication complexity level as defined in the IPC-2221 and IPC-2222

For example, let us use our SOT23 that we looked at for our AT24C01C. IPC uses the syntax of SOT23-+ Pitch P + Lead Span Nominal X Height – Pin Qty+Density.

Component family designator is the SOT23

Referring to the datasheet once again we see all the needed information.

*Figure 5. Dimensions for the 5-Lead SOT23 package as shown in the datasheet.*

Plugging in the component dimensions gives us the following:

*Figure 6. Packaging factors that affect component nomenclature.*

Which gives us the name of SOT23-95P280X110-5N

*Figure 7. The full table of package dimensions available in the datasheet uses metric system values.*

The information used in the name are metric measurements, and you drop any leading zeros and the decimal points. So, the 0.95 becomes 95, 2.80 becomes the 280, and 1.10 becomes the 110.

There is a lot more information in the IPC-7351 standard to consider. It is one of those standards I keep handy at all times.

## A Word About Density

According to IPC, there are three variations of the land patterns for each component.

Density Level A: Maximum Land/Lead to Hole Relationship
Density Level B: Nominal Land/Lead to Hole Relationship
Density Level C: Least Land/Lead to Hole Relationship

The primary use of density is to accommodate a level of manufacturing producibility. With Level-A (Maximum) being the most Designed for Manufacturing (DFM) friendly vs. Level-C (Least) which would be the densest and challenging to manufacture.

*Figure 8. The three density levels illustrated.*

## Conclusion

Going back to our fable at the beginning of this blog, the deduction that each of the six blind men of Indostan determined would have been entirely different if they collaborated and looked at their findings as a whole. As the bigger picture, they would have known that it was an elephant they were feeling.

An individual PCB Designer cannot be a lone wolf running things the way they want, but rather as a team to develop a standard which everyone can follow.

Putting this all together for our example component. The name for the component would be the full part number that you are after. Let us use an AT24C01C-STUM-T the EEPROM Memory IC 1Kb (128 x 8) I²C 1MHz 550ns SOT-23-5. That completely identifies the specific component I need.

*Figure 8. Final component, symbol, and footprint naming.*

Would you like to find out more about how Altium can help you with your next PCB design? [Talk to an expert at Altium](https://www.altium.com/contact-us) and learn more about making [design decisions](https://www.altium.com/enterprise) with ease and confidence.