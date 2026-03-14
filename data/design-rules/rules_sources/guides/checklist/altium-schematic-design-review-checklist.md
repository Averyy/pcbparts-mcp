---
source: "Altium -- Schematic Design Review Checklist"
url: "https://resources.altium.com/p/schematic-review-checklist"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 11828
---
One of the most common points of failure of a device, especially when prototyping occurs even before you start to layout your circuit board. Mistakes in your schematic design can easily make their way all the way into prototypes or production without a second thought once the layout starts. In many companies, design reviews are performed to approve a schematic design to proceed with the layout - whether the schematic engineer is the layout engineer or not. Often these schematic reviews still let many issues pass through which are not found until the prototype is tested, as all too many companies are too pressed for time to come up with a formal design review checklist relevant to their products.

In this article, I’m not going to extol the virtues of a good schematic design, as I’ve already done in my article about creating elegant, readable schematics. I’m also not going to go into great detail on the items on this schematic review checklist. If they are relevant to your product, you should probably already know what they mean - if not, you should probably look them up. There are many articles on this blog from myself and other industry experts which cover the reasons and importance of the items presented here and Altium review.

Instead, this article is a simple no frill schematic design review checklist. While I’ve attempted to make it as comprehensive as possible, there are still going to be many items that are relevant to specific projects that focus heavily on RF, high-speed, or very small signal processing which you will want to add. Likewise, there are likely many items that are not going to be applicable to a basic device. The goal is to provide you with 90% of the checklist that you need to improve your design review process. You should be able to take this list and customize it to your requirements in a fraction of the time of coming up with every item yourself, as I know you probably just don’t have enough hours in your schedule to come up with the perfect design checklist for your specific use case without some form of seed list.

One critical item that can be cut down at this point of your design process, which a single checklist item I don’t think really covers sufficiently is a bill of material (BOM) line count reduction. In production, every [BOM line](https://resources.altium.com/p/ad18-activebom-webinar-slides) can have substantial costs for feeders, full roll of components, space in a pick and place machine, programming costs, etc. Often you can reduce the BOM count by rounding values up or down without impacting your circuit’s functionality, or by placing components in series or parallel.

## Style

* Does each schematic sheet have the correct template applied?
* Is the title block filled out on each sheet?
* Can the sheet sizes be printed on your office’s printer?
  + Sheets should not exceed Tabloid/A3 size.
* Are all schematic sheets the same size?
* Do nets have netlabels to ease readability and PCB layout?
* Are nets consistently labeled?
* Are power ports consistently labeled?
* If there are multiple sheets:
  + Is there a top sheet?
  + Does the top sheet show connections between each sub-sheet?
  + Do you need a table of contents?
* Does the schematic design compile and pass design rules without errors?
* Has each warning from compiling the schematic design been checked to see if it is actually critical?
* Is there a change list or revision list if this is not the first design review for the schematic?
* Are all components aligned to the grid, and are all the net wires correctly connected to each pin?
* Can groups of offsheet connections be grouped into a bus, or harness to improve the legibility of the top sheet?
* Are multi-channel blocks implemented as multi-channel sheets?
* Are differential pairs correctly identified with \_P and \_N signals?
* Do differential pairs have a differential pair label?
* Are there net classes applied to each net that needs it?
  + High voltage
  + High current
  + RF/Impedance matched
  + Differential pairs
* Do all components have the correct designators? (i.e.: You annotated the schematic)

## Usability/Testing

* Is there a LED for each power rail? At least for the input?
* Are there test points for each power rail?
* Are there test points for critical signals/signals of interest?

## Production

* Can any component values be safely merged to reduce BOM line items?
* Is only one part number specified for each passive component value with a specific size?
* Check that each symbol has a manufacturer and part number assigned.
* Are all components active production, and not end-of-life/discontinued/not recommended for new designs at the time of the schematic review?
* Does each component have sufficient stock in the supply chain?

## Connectors

* Check that I/O pins have a pull-up or down to define their default state when disconnected.
* Ensure there is a decoupling capacitor for each power pin on the connector.
* Do electrically noisy pins need to be treated as pseudo-differential pairs?
* Do long cables need to be isolated for EMC?

## Components

* Check all symbol pinouts against the datasheet, even if you have used the IC before or trust the symbol source.
* Tantalum Capacitors' voltage rating is at least 20% higher than the maximum expected voltage.
* Have you checked the current passing through each resistor for power dissipation?
  + Is it safely within the rating of the components?
  + Will the temperature of the resistor be too high, even if it’s within the ratings?
* Is each resistor’s voltage rating sufficient for the maximum voltage applied (mostly relevant to 0402 and smaller sizes)?
* Have all the current limiting resistors been correctly calculated for each LED's forward voltage?
* Have all the current limiting resistors been correctly calculated for each optoisolator forward voltage?
* Do reset/enable pins need an external pull-up or pull-down resistors?
* Are any potentially floating pins pulled up or down with external resistors?
  + Pins drove with diodes
  + Pins drove with transistors or MOSFETs
  + Comparator outputs
* Are any pins with a state that is critical at power up externally pulled up or down?
  + Gate/base pins on MOSFETs and transistors
  + External connectors
  + Safety devices
  + Thermal management devices
* Do any programmable devices have a programming header/pad accessible?
  + For prototypes, can you read/write flash/EEPROMs externally with a connector?
* Is each operational amplifier and comparator connected with the correct polarity?
* Are any unused devices in array components (e.g.: quad operational amplifiers) correctly terminated or tied to a rail?
* Check for the correct polarity of each diode or LED.

## Power

* Every power pin of every IC should have a decoupling capacitor.
* Has each switched mode voltage regulator been simulated to ensure it is stable across all load conditions?
* Has each switched mode voltage regulator been simulated to ensure it can supply the required current?
* Has each switched mode voltage regulator been simulated to ensure it can provide the required voltage under all load conditions?
* Do multiple voltage rails need sequencing?
* Do you need a reset supervisor IC on any devices if a regulator has a soft start?
* Has the power distribution network been analyzed for a total load? Can the regulators supply this load?
* Should any subsystems have isolated supplies?
* Should any subsystems have separately regulated supplies?
* Does each voltage regulator’s output meet the precision requirements for the subsystems connected to it?
* Is the total capacitance connected to each regulator within its ability to supply?
* Is there sufficient input capacitance on each regulator to prevent reverse supply under changing loads?
* Are any input voltages to regulators able to drop below the regulator’s minimum operating voltage?
* Are any input voltages to regulators able to exceed the regulator's maximum voltage?
* Is there a linear regulator between any devices that need extremely clean power (e.g.: operational amplifiers with high gain) and a switched mode regulator source?

## Signal

* Are there filters on every Analog to Digital converter pin?
* Have amplifier circuits been simulated to ensure they are stable?
* Have all voltage dividers been re-calculated to ensure the output voltage is correct?
* Is there capacitance and/or a Zener diode on the output of each operational amplifier?
* Are all signals feeding into logic devices within the maximum voltage rating?

## EMI/EMC/Protection

* Does every externally accessible connection/exposed piece of metal have adequate ESD protection? Keep in mind that ESD spark gaps for what is exposed.
  + Connector pins
  + Connector housings
  + Metal shields on buttons
  + Pins of buttons
  + Displays
  + Potentiometers/dials
  + Card socket pins
  + Metal card housings
* Does the input power require a fuse to protect upstream devices?
* Is the input power protected against reverse polarity?
* Is there overvoltage protection on the power input?
* Is there overcurrent protection on the power input?
* Are there current limiting resistors on nets from external devices to sensitive devices (e.g.: microcontroller pins)
* Do all optoisolators have parallel resistors/capacitors with their diode for noise immunity?
* Is there input under-voltage protection?
* Is there short circuit protection on each voltage rail that has an external connection/output?
* Does every switching regulator have a sufficient input filter to prevent conducted EMI from escaping on its input?
* Are MOSFETs protected against voltage transients with external diodes?

The items on this list are diverse, and some are quite broad topics as a single item to check. Design review checklists should not be seen as merely an administrative process that needs to be completed to satisfy management. If this is your attitude to the design review process, you’re missing out on a valuable chance to improve your product, and for your team to share their experience and skills with each other. Schematics and PCB design reviews are a chance to have a final discussion of the implementation of the product. It’s much easier to add an extra button, capacitor, or additional functionality before your [PCB layout](https://resources.altium.com/p/how-create-pcb-layout-schematic-altium-designer) begins and you find you need to cram in dozen more components.

Use the items on your schematic review checklist as a basis for discussion around that topic, rather than merely confirming the box is checked. These discussions can lead to fantastic opportunities to improve your product’s functionality, usability, and reliability, or even reduce cost as you find that some features are probably not actually necessary for the end design. Taking on this discussion early on, a revisit of the product's requirements specification can save dozens of engineering hours later. Your schematic design review is also an excellent time to confirm that your product design meets all the required specifications that were issued at the start of the design process. Finding that you are missing a critical specification or have misinterpreted some aspect of the requirements at this stage of development makes rectification of the deficiency easy compared to once you have a failing PCB in your hands.

The design tools in [Altium Designer](https://www.altium.com/altium-designer)® contain everything you need to keep up with new technology. Talk to us today and find out how we can enhance your next PCB Design.
