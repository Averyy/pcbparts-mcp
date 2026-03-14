---
source: "Sierra Circuits -- How to Draw and Design a PCB Schematic"
url: "https://www.protoexpress.com/blog/how-to-draw-design-pcb-schematic/"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 18857
---
A PCB schematic is a logical and visual representation of an electrical circuit. It is the first step of electronic product design. You must follow standard schematic guidelines such as precision net labeling, and symbol standardization to have a well-structured and error-free design.

Today, designers use numerous [EDA tools](https://www.protoexpress.com/blog/10-best-pcb-layout-design-tools-recommended-by-pcb-designers/) for schematics generation, such as Altium Designer, Allegro, Pads, Kicad, Tinycad, Express PCB, and Zuken.

 **Highlights****:**

* Adhere to net labeling, off-page connections, and signal flow representation guidelines to minimize visual complexity.
* Use auto-grouping to organize redundant design blocks in your layout.
* Employ DRC, netlist verification, and a comprehensive BOM to improve design accuracy.

## What is the importance of a schematic diagram?

Schematic is one of the important aspects of electronic circuit design. A good schematic helps you conceptualize a well-structured circuit diagram clearly depicting the electrical connections between various electronic components and overall circuit functionality.

It should also be noted that a technically correct but crowded schematic is still a bad one, as it might confuse you. Schematics can be an extremely valuable troubleshooting tool during [circuit board repair](https://www.protoexpress.com/blog/how-to-troubleshoot-and-repair-your-pcb/) as it traces out the connections in the circuit.

## Guidelines to draw a PCB schematic diagram

To achieve a successful design, follow these standard schematic guidelines.

### 1. Select a suitable page size
Most of the design tools offer different page sizes. Generally, the tools would select the page size as A4. However, it should be noted that various other page sizes are also available. You should select the size based on the size of their circuit design.

### 2. Name the pages in alphabetical order
The logical blocks of the schematic should be separated by pages. The pages can be named using the letters A, B, C, and so on. By doing this, we can place the pages in alphabetical order. An example of such a naming convention is shown below.

* A\_Block Diagram
* B\_Power supply
* C\_ MCU interface
* D\_Memory interface
* E\_ Revision history

Block diagrams and revision history are often ignored by most designers to save time. However, they can be very helpful for other designers trying to understand the schematic. Product-based organizations mandate all such protocols and regulations.

### 3. Implement a grid system for establishing reference points
Though it is not a direct requirement, the tool must have some references. Hence, the grid system is followed. Having grids helps you reference the parts properly and make their connection. Circuit components and connections must always be on the grid; this helps in probing the nets during analysis.

### 4. Include a title block in the footer of the page
The page title block is present in the footer of the schematic page. It is a good practice to fill in all the required details such as page size, update date, revision, document number, name/function of the circuit, and company disclaimer. An example of the title block is shown below.

A page title block in the schematic

### 5. Add important notes/comments on separate pages
You need to write the necessary comments concerning the circuitry. The notes can be written on either independent documents or schematic pages. Generally, notes are provided on a separate page for complex designs. Examples of notes could be jumper status, [PCB layout](https://www.protoexpress.com/blog/how-design-pcb-layout/) constraints/guidelines, etc. A schematic with notes can be seen below.

Schematic with notes and comments

### 6. Include a revision history on the first or last page
The revision history contains the changes that were made to the design. This document provides information such as the date and description of the changes made, the name of the author and the reviewer, and review comments, if any. Revision history is generally placed on the first or last page of the schematic. An example of schematic revision history is shown below.

Example of revision history of a schematic

### 7. Incorporate a table of contents into the schematic document
The table of contents lists the topics present in the schematic document. This page helps you easily locate a specific module in a complex and large design. This can be skipped if the design is small and simple. An example of a ToC is given below.

Table of contents of a schematic document

### 8. Utilize a block diagram to illustrate design modules and the signal flow
The block diagram represents the different modules in the design and signal flow. This greatly helps the reviewer to understand the design for review purposes. Block diagrams may not be required for simpler designs but are primarily used in more intricate projects. An example of a schematic block diagram can be seen below.

Block diagram of a schematic

Implement [**auto-grouping of repetitive PCB design blocks**](https://www.protoexpress.com/blog/auto-grouping-repetitive-pcb-design-blocks/) if you have redundant blocks in your layout.

### 9. Illustrate the signal flow path using a hierarchical schematic design
If the design is complex and contains many modules, a hierarchical design is preferred. The hierarchical schematic clearly displays the signal flow from one module to another, as shown below. A detailed view of each module can be accessed by clicking on the respective module in the hierarchical schematic.

Hierarchical schematic design

### 10. Employ standard component reference designators
The table below shows the names of the generally used electronic components and their corresponding reference designators used in any schematic. The designators are assigned as per the IEEE standard. It is recommended to name the components with its standard reference designators. Also, always use capital letters to designate the schematic symbols.

| Component | Reference designator | Component | Reference designator | Component | Reference designator |
| --- | --- | --- | --- | --- | --- |
| Resistor | R | Plug /Connector | P/CON | Power supply | PS |
| Capacitor | C | Jumper | Jp | Crystal | X or Y |
| Diode/LED | D | Cable/wire | W | Oscillator | OSC |
| Zener diode | Z | Test Point | Tp | Heatsink | H |
| Resistor Network | Rn | Relay | K | Fiducial | Fd |
| Inductor/Bead | L | Fuse | F | Buzzer/Loud speaker | LS |
| IC (Integrated Circuit) | U/IC | Switch | SW | Battery | BT |

### 11. Generate component symbols using the standard library
The schematic diagram consists of different types of components, such as active components, passive components, and connectors. Active components include transistors, diodes, logic gates, processor IC, FPGA, Op-amps, and so on.

Components like capacitors, inductors, and transformers are referred to as passive devices. Creating new symbols is not advisable unless the symbol for that component is not present in the standard library.

For more on symbol generation, see [how to create a schematic and symbol library in KiCad](https://www.protoexpress.com/blog/how-to-create-a-schematic-and-symbol-library-kicad/).

#### Resistors

Resistors can be represented in two different ways, as shown below. You should take care to keep up the consistency in the symbols used.

Resistor symbols used in schematic design

The unit of the resistance is ohms and is represented by the symbol ‘Ω.’ Sometimes, the symbol ‘Ω’ can be replaced with the letter ‘E’. You should ensure that consistent unit representation is followed throughout the entire design. All required data about the components should be entered in the design tool. This makes it easier to create a [BOM](https://www.protoexpress.com/blog/what-is-bill-of-materials-pcb-design/) at the end of the design.

#### Polarized and non-polarized capacitors
Capacitors have two terminals, one positive and one negative. Care should be taken to mark the polarity of these terminals. An error in the polarity of the capacitor terminal might lead to exploding. The figure below shows the capacitor symbols from IEEE standards.

Polarized and nonpolarized capacitors

You should also ensure that the pin numbers assigned to the symbols match the footprint layout.

#### Transistors
A transistor is a three-terminal semiconductor device. The terminals are the base, collector, and emitter. You should always refer to the component datasheet while mapping the pins in the footprint layout to the schematic symbol.

Transistor symbol with pin numbers

When the symbols are created, it is important to enter a description of the component. This is very useful for future reference or when the part is obsolete and needs to be replaced. Having these details on the BOM improves readability. The two images below show filled description fields of a transistor symbol.

Symbol description of transistor

Symbol description of a component (Image credit: Altium)

#### Op-amp
It is very important to create the op-amp symbol per the IEEE standards. Many designers often draw the op-amp as per their convenience, which tends to lose readability. This may happen due to a lack of understanding and experience of CAD schematic tools.

Op-amp symbol

When you create a symbol, it is recommended to have all the input pins on the left and all the output pins on the right. Similarly, power and ground pins can be placed at the top and bottom, respectively. In the image shown, the input pins are 2 and 3, the output pin is 4, and the power and ground pins are 7 and 4, respectively.

You should be careful while flipping or changing the orientation of the symbol. When we do so, there is a good chance that positive and negative terminals will switch their positions.

Failure to adjust the wiring after flipping symbols can lead to misalignments between the schematic and physical connections, potentially causing incorrect functionality or circuit failure. Hence, care should be taken to cross-check each symbol with the manufacturer’s datasheet.

#### Heterogeneous schematic symbol

Complex devices such as FPGA, memory, and microprocessors are called heterogeneous components. These components have different types of pins in large numbers, such as data lines, inputs/outputs, address lines, control lines, and power lines.

To retain clarity and readability, you should create multiple components of a single package, such as UxA, UxB, UxC, and UxD.

Some pins on components may have multiple functions, and this flexibility is usually denoted on the symbol, accompanied by specific details provided outside the symbol. For instance, pin AA5 below is assigned various functions, such as GPIO.6, CLKOK, PWM, or T3.

Additionally, external notes at the connection point specify the current function of the pin; for instance, the label “GPIO6” outside the symbol indicates its present function.

 An example of such a heterogeneous schematic symbol of a component is given below.

Heterogeneous schematic symbol of a component

#### Power and ground symbols

The symbols of power and ground pins are shown below.

Power and ground symbols

It is always a good idea to represent voltages with a ‘+’ sign since there could be negative voltages present on the board. You should follow a standard and consistent convention to represent the voltage levels and their sections inside the silicon.

For example, +3.3V\_IO, +3.3V\_DG, +3.3V\_AN +1.8V\_Core, +1.2V\_LVCore, +2.5\_Vref etc.

Similarly, different types of grounds could be present on the board. The symbols are shown below.

Different types of ground symbols

### 12. Reduce unnecessary net connections to enhance clarity
Whenever you have two wires that form a junction and share an electrical connection, that intersection needs to have a junction dot. This is a standard practice in every schematic design.

However, most schematic design software applications exclude the junction dot when a wire connects directly to a pin or terminal on a component.

Net connection in a schematic design

#### Net labeling conventions
The objective of a schematic is to make your circuitry easier to understand for you as a designer. Unnecessary net connections should be minimized. This is commonly observed when drawing the symbol of an integrated circuit (IC) on a schematic.

Rather than drawing dozens of nets all over the place, you can assign a net name for a specific pin, which is associated with a pin on another device. These pins will have the same name. Pins with the same name are assumed to be connected.

This improves the readability of a schematic. This approach is especially beneficial when the net is linked to three or more locations. The below image shows a series of named nets.

Net labeling convention

#### Net labeling guidelines
When nets are connected on the same page directly to another IC, net naming is not required.

You can follow these simple rules while naming the nets:

* Signal names should always be written in uppercase and should be placed just above the net.
* Avoid long names. Preferably, the names can have a maximum of 4 letters.
* Describe active low or high signals using the upper bar. A pin with an upper bar is considered to be an active low pin.
* Open nets/connections should be removed.

#### Off-page connection
To improve readability, designers usually name the nets in the schematic. This works fine when the signal is to be connected on the same page. If there is a requirement to connect the net to a pin that is present on a different page, an off-page connector symbol should be used.

#### Signal flow representation
On a schematic page, the signal flows from the left to right side of the page. Any power and ground connections are shown on the top or bottom side of the page, respectively. You are advised to keep this in mind and to keep components accordingly.

### 13. Maintain readability when depicting the component placement
[Component placement](https://www.protoexpress.com/blog/component-placement-guidelines-pcb-design-assembly/) in a schematic is one of the important tasks. This is because the layout engineer is going to keep the components accordingly. The parallel connection of the capacitors is shown on the left. As we can see, the readability of the schematic is not up to the mark.

Parallel connection of capacitors in a schematic

To improve the readability, the connection can be made as shown below.

Preferred parallel connection of capacitors in a schematic

Also, read [How to Place Components in KiCad](https://www.protoexpress.com/blog/component-placement-guidelines-pcb-design-assembly/).

### 14. Place components connected to the crystal in close proximity
Crystal placement in the schematic is always made, as shown below. The components connected to the crystal are always placed near it as the signals could be of high frequency.

Typically, when the design requires placing two components in close proximity, they should be illustrated accordingly (e.g., shunt and series terminations).

Crystal placement in a schematic

For more information on high-speed schematic design tips, see [how to create a schematic for high-speed designs in KiCad](https://www.protoexpress.com/blog/how-to-create-schematic-high-speed-design-kicad/).

### 15. Run a DRC to assess the integrity of the design
[Design Rule Check (DRC)](https://www.protoexpress.com/blog/drc-pcb-manufacturing/) is an intelligent feature offered by CAD software to check both the logical and physical integrity of a design. Checks are made against all enabled design rules and can be made online as you design.

### 16. Manually verify the nets to eliminate potential design errors
The netlist is generated when the schematic design is complete and ready to be imported into the layout. The most common file extension for netlist is the .net. Manually verifying the nets is recommended to avoid design errors.

 For more, read [schematic and netlist checks to ensure error-free design](https://www.protoexpress.com/blog/schematic-and-netlist-checks-ensure-error-free-designs/).

### 17. Generate complete BOM by importing components from the library
Currently, CAD tools provide a key feature called BOM creation.  A complete and sufficient BOM can be generated only if you have provided all the inputs in the tools while creating or importing components from the library.

The inputs to the BOM could be MPN (Manufacturing Part Number), package, vendor name, vendor part number, and so on. It is recommended to provide all the required information during the symbol creation.

Elevate your PCB designs with our expert schematic design services and transform your concepts into a circuit board with unmatched reliability and the best signal integrity.

## Checklist for a flawless PCB schematic
The schematic checklist is the most often ignored point in schematic creation. This is more related to the organization’s process, which is based on past design experiences. Having a checklist avoids errors in the schematic and makes the design robust. Below is the checklist.

1. Verify pin numbering and labels for each component and align them according to the datasheet.
2. Conduct a polarity check for all polarized components in the schematic.
3. Check for overlapping labels and pin numbers to ensure legibility.
4. Validate the alignment of the base, collector, and emitter pins of transistors with the datasheet, schematic symbol, and footprint package.
5. Confirm the accuracy of component values, reference designators, and physical locations.
6. Ensure the presence of schematic symbol descriptions, such as MPN, vendor name, and vendor part number.
7. Check for the presence and accuracy of off-page connectors.
8. Verify inter-sheet references for seamless connectivity.
9. Conduct checks on [decoupling capacitors](https://www.protoexpress.com/blog/decoupling-capacitor-use/) for all ICs, ensuring proper ground pin separation based on signal type (analog, digital, signal, ground).
10. Perform bill of materials checks, including package types, quantity, and part numbers.

Schematic is the backbone of any circuit board design. A good schematic should ensure a seamless transition from a good concept to a layout. From net labeling to component symbol creation, you need to adhere to the set of standard guidelines to ensure an error-free PCB schematic.

Need assistance in creating schematics for your design? Post your queries on SierraConnect; our design experts will help you!
