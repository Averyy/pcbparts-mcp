---
source: "ADI -- Basic Guidelines for Layout Design of Mixed-Signal PCBs"
url: "https://www.analog.com/en/resources/analog-dialogue/articles/what-are-the-basic-guidelines-for-layout-design-of-mixed-signal-pcbs.html"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 16189
---
### Abstract

This article will detail what to consider when designing the layout of mixed-signal PCBs. It will cover component placement, board layering, and ground plane considerations. The guidelines discussed in this article provide a practical approach to the layout design of mixed-signal boards and should assist engineers of all backgrounds.

### Introduction

A mixed-signal PCB design requires basic understanding of analog and digital circuitry to minimize, if not prevent, signal interference. Modern systems consist of components that are operational with both digital and analog domains, and these must be carefully designed to ensure signal integrity all throughout the system.

PCB layout as an important part of the mixed-signal development process can be intimidating and component placement is just the beginning. There are also other factors that must be considered including board layers and how to properly manage these to minimize interferences caused by parasitic capacitors that can be unintentionally created between the interplane layers of the PCB.

Grounding is also an integral process in the PCB layout design of a mixed-signal system. While grounding is a frequently debated topic in the industry, constructing a standardized approach may not always be the simplest task for any engineer. For instance, a single issue of quality grounding can affect the entire layout of a high performance mixed-signal PCB design. And for this reason, this area should not be overlooked.

### Component Placement

Similar to building a house, it is essential to create a floor plan of the system before placing the circuit components. This step will set the overall integrity of the system design and should help avoid noisy signal interference.
In developing a floor plan, it is advisable to follow the signal path of the schematic, especially for high speed circuits. The location of a component is also a critical aspect of the design. The designer should be able to identify the important functional block, signals, and the connection between the blocks in order to identify the best fit location of each component in the system. Connectors, for instance, are better placed on the edges of the board, while auxiliary components such as decoupling capacitors and crystals must be placed as close as possible to the mixed-signal device.

### Analog and Digital Blocks Partition

To help minimize the common return path for analog and digital signals, analog and digital block separation may be considered such that analog signals will not mix with digital signals.

Figure 1. Partition of analog and digital circuits.

Figure 1 shows a good example of analog and digital circuit separation. Some considerations when separating analog and digital sections are:

* Sensitive analog components such as amplifiers and voltage references are recommended to be placed within the analog plane. Similarly, the noisy digital components such as logic controls and timing blocks must be placed on the other side/digital plane.
* If a system contains one mixed-signal analog-to-digital converter (ADC) or a digital-to-analog converter (DAC) with low digital currents, this can be treated similar to analog components that are included in the analog plane.
* For designs with more than one ADC and DAC with high current, it is recommended to split the analog and digital supplies. That is, AVCC must be tied to the analog section while DVDD should be connected to the digital section.
* Microprocessors and microcontrollers may take up space and will generate heat. These components must be placed in the center of the board for better thermal dissipation, and, at the same time, close to their related circuit blocks.

### Power Supply Block

The power supply is an important part of the circuit and should be handled accordingly. As a rule of thumb, the power supply block must be isolated from the rest of the circuitry and at the same time remain close to the components being powered.

Complex systems with devices that have multiple supply pins can use separate power supply blocks dedicated for the analog and digital sections to avoid noisy digital interference.

On the other hand, power supply routing should be short, direct, and use wide traces to reduce inductance and avoid current limitation.

### Decoupling Techniques

Power supply rejection ratio (PSRR) is one of the important parameters a designer must consider in achieving target system performance. PSRR is the measure of the sensitivity of a device with respect to power supply variations, which will eventually dictate the performance of a given device.

To maintain an optimum PSRR, it is necessary to keep the high frequency energy from entering the device. This can be done by properly decoupling the power supply of the device to the low impedance ground plane with a combination of electrolytic and ceramic capacitors.

The whole concept of correct decoupling is to develop a low noise environment in which the circuit can operate. The basic rule is to make it easy for the current to return by providing the shortest path.

Designers must always check the high frequency filtering recommendation of each device. More so, this checklist will serve as a guide by providing general decoupling techniques and their correct implementation:

* While electrolytic capacitors act as charge reservoirs to transient currents to minimize low frequency noise on power supplies, low inductance ceramic capacitors on the other hand reduce high frequency noise. Also, ferrite beads are optional but will add extra high frequency noise isolation and decoupling.
* Decoupling capacitors must be placed as close as possible to the power supply pins of the device. These capacitors should connect to a large area of low impedance ground plane through a via or short trace to minimize additional series inductance.
* The smaller capacitor, typically 0.01 μF to 0.1 μF, should be placed as close as physically possible to the power pins of the device. When the device has several outputs switching at the same time, this placement prevents instabilities. The electrolytic capacitor, typically 10 μF to 100 μF, should be placed no more than one inch away from the power pin of the device.
* For easier implementation, decoupling capacitors can be linked through a T-type connection to the ground plane using vias near the GND pin of the component rather than creating a trace. See the sample in Figure 2.

Figure 2. A decoupling technique for power supply pins.

### Board Layers

Once component placement and the floor plan have been set, we can go through the other dimension of the board design, which is commonly referred to as board layers. It is highly recommended that board layers should be considered first before doing the PCB routing as this will determine the allowable return current paths of the system design.

A board layer is the vertical arrangement of the copper layers in the board. These layers should manage the currents and signal throughout the board.

Figure 3. A sample 4-layer PCB.

A visual representation of the board layers is shown in Figure 3. Table 1 details a typical 4-layer PCB setup:

#### Table 1. Typical 4-Layer PCB

|  |  |
| --- | --- |
| 1 | Digital/analog signal (top layer) |
| 2 | Ground |
| 3 | Power plane |
| 4 | Aux signal (bottom layer) |

In general, high performance data collecting systems should have four or more layers. The top layer is often used for digital/analog signals, while the bottom layer is used for auxiliary signals. The second layer (ground layer) serves as a reference plane for impedance-controlled signals and used for reducing IR drops and shielding the digital signals in the top layer. Finally, the power plane is on the third layer.

Power and ground planes must be adjacent to each other as they provide additional interplane capacitance, which helps with the high frequency decoupling of the power supply.

For the ground layer, advice has changed over the years for the mixed-signal design. Over the years, splitting the ground plane between analog and digital has made sense but for modern mixed-signal devices, a new approach is recommended. Proper floor planning and separating signals should prevent any issues with noisy signals.

### Ground Plane: To Split or Not to Split?

Grounding is an essential process in the layout design of a mixed-signal PCB. A typical 4-layer PCB must have at least one layer dedicated to the ground plane to ensure a low impedance path for return signals. All integrated circuit ground pins should be routed and connected correctly to the low impedance ground plane to minimize the series inductance and resistance.

It has become a standard grounding approach for mixed-signal systems to separate analog and digital ground. However, mixed-signal devices with low digital current can be best managed with a single ground. Moving forward, a designer must consider which grounding practice suits best depending on the mixed-signal current requirement. There are two grounding practices a designer must consider.

### Single Ground Plane

For mixed-signal systems with a single ADC or DAC with low digital current, a solid single ground plane would be the best approach. To understand the importance of a single ground layer, we need to recall return current. Return current is the current that flows while returning to ground and traces between devices to complete a loop. To prevent mixed-signal interference, each return path must be tracked throughout the PCB layout.

Figure 4. Return current for system with a solid ground plane.

The simple circuit in Figure 4 shows the advantage of a single solid ground plane over a split ground plane. The signal current has an equal but opposite flow of return current. This return current flows in the ground plane back to the source and it will follow the path of least impedance.

For low frequency signals, the return current will take the path of least resistance, usually a straight line between the ground reference points of the devices. However, for higher frequency signals, a certain portion of the return current will try to follow the signal path back. This is because the impedance is lower following this path since it minimizes the size of the loop formed between the outgoing and returning current.

### Analog and Digital Ground Separation

For complex systems where a solid ground scheme can be challenging to achieve, a split ground may be more appropriate. A split ground plane is another popular approach where the ground plane is split in two: analog and digital ground planes. This is applicable for more complex systems with multiple mixed-signal devices consuming high digital current. Figure 5 shows an example of a system with a split ground plane.

Figure 5. Return current for systems with a split ground plane.

For systems with a split ground plane, the simplest solution to achieve a cohesive ground is to remove the break in the ground planes and allow the return current to take a more direct route through a star ground junction. The star ground is the junction where the analog and digital ground planes are joined together on a mixed-signal layout design.

In common systems, the star ground can be associated with a simple narrow continued junction in between analog and digital ground planes. For more complex designs, the star ground is commonly implemented with a jumper shunt to a ground header. No high current carrying a header and jumper shunt is required as there will be no flow of current in the star ground, but rather its main purpose is to make sure that both grounds have the same reference levels.

Designers must always check grounding recommendations found in each device’s data sheet to ensure grounding specifications will be met and avoid ground related issues. On another note, for mixed-signal devices that have AGND and DGND pins, these can be tied to their respective ground planes since the star ground will also connect both grounds at one point. In this way, all noisy digital currents will flow through the digital power supply down to the digital ground plane and back to the digital supply all the while being isolated from the sensitive analog circuitry. Isolation of the AGND and DGND planes must be implemented on all layers of a multilayer PCB.

### Other Common Grounding Practices

Here is a procedure/checklist that one can follow to ensure an appropriate grounding scheme has been implemented in a mixed-signal analog/digital system:

* Wide copper traces should make up the connections at the star point.
* Check the ground plane for narrow traces, as these connections are undesired.
* It is useful to provide pads and vias so that the analog and digital ground planes can be connected, if necessary.

### Conclusion

The PCB layout for mixed-signal applications can be challenging. Creating a component floor plan is just the starting point. Properly managing board layers and preparing an adequate grounding scheme are also part of the key points a system designer must consider when trying to achieve optimum performance in a mixed-signal system layout. Preparing a component floor plan will help set the overall integrity of the system design. Proper board layer organization will help manage the currents and signal throughout the board. Finally, choosing the most beneficial grounding scheme will improve the system’s performance and prevent any issues with noisy signals and return current.

## References

Walt Kester. [*The Data Conversion Handbook*](/en/resources/technical-books/data-conversion-handbook.html). Analog Devices, Inc., 2005.

John Ardizzoni. “[A Practical Guide to High-Speed Printed-Circuit-Board Layout](/en/resources/analog-dialogue/articles/high-speed-printed-circuit-board-layout.html).” *Analog Dialogue*, Vol. 39, No. 9, September 2005.

Ralph Morrison. *Grounding and Shielding Techniques*. John Wiley & Sons, Inc., 1998.

Thomas O’Shea. “[AN-1349 Application Note: PCB Implementation Guidelines to Minimize Radiated Emissions on the ADM2582E/ADM2587E RS-485/RS-422 Transceivers](/media/en/technical-documentation/application-notes/an-1349.pdf).” Analog Devices, Inc., August 2018.

“[MT-101 Tutorial Decoupling Techniques](/media/en/training-seminars/tutorials/mt-101.pdf).” Analog Devices, Inc., 2009.

*[Linear Circuit Design Handbook](/en/resources/technical-books/linear-circuit-design-handbook.html)*. Analog Devices, Inc., 2008.

Paul Brokaw. “[AN-342 Application Note, Analog Signal-Handling for High Speed and Accuracy](/media/en/technical-documentation/application-notes/2904748046167431066an-342.pdf).” Analog Devices, Inc.

Walt Kester, James Bryant, and Mike Byrne. “[MT-031 Tutorial Grounding Data Converters and Solving the Mystery of ‘AGND’ and ‘DGND’](/media/en/training-seminars/tutorials/mt-031.pdf).” Analog Devices, Inc., 2009.

Paul Brokaw and Jeff Barrow. “[AN-345 Application Note: Grounding for Low- and High-Frequency Circuits, Know Your Ground and Signal Paths for Effective Designs, Current Flow Seeks Path of Least Impedance–Not Just Resistance](/media/en/technical-documentation/application-notes/6001142869552014948960492698455131755584673020828an_345.pdf).” Analog Devices, Inc.

Doug Grant and Scott Wurce. “[AN-348 Application Note: Avoiding Passive Component Pitfalls, The Wrong Passive Component Can Derail Even the Best Op Amp or Data Converter Here Are Some Basic Traps to Watch For](/media/en/technical-documentation/application-notes/500824934643930414583807523874018494695982855668424783486554001060an348.pdf).” Analog Devices, Inc.

## Acknowledgements

The material presented in this article was compiled from many contributors, including Eric Carty, Genesis Garcia, Giovanni Aguirri, Brendan Somers, Stuart Servis, Leandro Peje, Mar Christian Lacida, and Yoworex Tiu.
