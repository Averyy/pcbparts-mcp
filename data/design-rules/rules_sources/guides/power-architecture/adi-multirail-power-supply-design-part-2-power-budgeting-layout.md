---
source: "ADI -- Multirail Power Supply Design Part 2: Power Budgeting + Layout"
url: "https://www.analog.com/en/resources/analog-dialogue/articles/multirail-power-supply-design-for-successful-application-boards-part2.html"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 12956
---
### Introduction: An Engineer’s Challenges in Evolving Times

Power supply design can be broken down into three main stages: (a) design strategy and IC choice, (b) schematic design, simulation, and testing, and (c) placement and routing. Investing time into the (a) design and (b) simulation stages can prove the efficacy of your design concept, but the real test requires putting it all together and testing it on the benchtop. In this article, we’re going to skip to step (c), as there are a significant number of resources that cover Analog Devices’ simulation and design power tools, all free to download, such as LTpowerPlanner®, LTpowerCad®, LTspice®, and LTpowerPlay®. [Part 1](/en/resources/analog-dialogue/articles/multirail-power-supply-design-for-successful-application-boards-part1.html) of this series covered (a) strategy.

This article is the second of a 2-part series that addresses issues sometimes overlooked when designing multirail power supplies. Part 1 focused on the strategy and topology, while this article focuses of the specifics of power budgeting and board layout. As many application boards require a number of power rails, this 2-part series examines a multisupply board solution. The goal is to achieve a quality initial design with good component placement and routing to highlight some power budget and routing tips and tricks.

In power supply design, careful layout and routing are crucial to producing robust designs with plenty of headroom with regard to size, accuracy, efficiency, and avoiding problems in production. Years of benchtop experience can help, so lean on the knowledge of layout engineers with respect to final completion of board manufacture.

### The Efficacy of Careful Design

A design may look solid on paper (that is, from a schematic point of view) and may even simulate without issue, but the real test is after layout, PCB manufacturing, and prototype stress test by loading the circuits. This section highlights some tips and tricks to avoid pitfalls by using real design examples. A few important concepts can be helpful in avoiding design flaws and other pitfalls that may result in redesign and/or PCB respins. Figure 1 shows how costs can quickly escalate if the design goes far into production without careful testing and headroom analysis.

Figure 1. Costs can quickly escalate when problems show up on a production board.

### Power Budgeting

Watch out for systems that operate as expected under normal conditions, but not so in full speed mode or when erratic data starts appearing (when noise and interference have been ruled out).

Avoid current limit scenarios when tapping off cascading stages. Figure 2 shows a typical cascaded application: (a) shows a design consisting of the [ADP5304](/en/products/adp5304.html) buck regulator (PSU1) producing a 3.3 V supply with a max current of 500 mA. For efficiency, designers should tap off the 3.3 V rail rather than the incoming 5 V supply. The 3.3 V output is further tapped off to supply PSU2 (LT1965)—this LDO regulator is used to further regulate down to 2.5 V, with a maximum output current of 1.1 A as required by on-board 2.5 V circuitry and ICs.

This is a system with some classic hidden problems. The system works fine under normal conditions. But issues arise when the system has initialized and begins running full throttle—for example, when the microprocessor and/or the ADC start sampling at high speed. Since no regulator can produce more power at its output than it has at the input, in Figure 2a the max power (P = V × I) at VOUT1 is 3.3 V × 0.5 A = 1.65 W to supply the combined circuits VOUT1 and VOUT2. This assumes 100% efficiency, so there is less available power due to losses in the supply. The assumed max available powerfor the 2.5 V supply rail is 2.75 W. If the circuits attempt to demand this much power, they will not be satisfied, resulting in erratic behavior when the PSU1 starts to current limit. The current may start limiting due to PSU1 or, worse, some regulators shut down completely due to overcurrent.

If Figure 2a is implemented after successful troubleshooting, it may require a higher power regulator replacement. Best case is a pin-compatible higher current replacement; worst case is a complete PCB redesign and respin. Potential project delay timelines (see Figure 1) can be avoided by keeping the power budget in mind prior to the design concept stage.

With this in mind, before choosing a regulator or regulators, create a realistic power budget. Include all of your required power rails: 2.5 V, 3.3 V, 5 V, etc. Include all pull-up resistors, discrete devices, and ICs that consume power for each rail. Use these values and work backward to estimate your power supply requirements as shown in Figure 2b. Use a power tree system design tool, such as LTpowerPlanner (Figure 3), to easily create a power tree supporting the required power budget.

Figure 2. Avoid current limit design flaws in the power tree.

Figure 3. LTpowerPlanner power tree.

### Layout, Tracking, and Routing

Correct layout, tracking, and routing avoid current capacity limitations caused by burning out of tracks due to the wrong track width, wrong vias, insufficient number of pins (connectors), the wrong contact size, etc. The following section includes some worthy reminders with a few PCB design tips.

#### Connectors and Pin Headers

Extending the example shown in Figure 2 to a total current of 17 A, designers must account for the current handling contact capability at the pin (or pins), as shown in Figure 4. Generally, current carrying capacity by pins or contacts depends on several factors, such as the physical pin size (the contact area), metal composition, etc. A typical through-hole male header pin with a diameter of 1.1 mm1 is around 3 A. If 17 A is required, make sure your design has enough pins to handle the total current carrying capacity. This is easily achieved by multiplying the current carrying capability per conductor (or contact), with some safety margin, to exceed the total current consumption by the PCB circuitry. In this example, to achieve 17 A requires six pins (with 1 A headroom). A total of 12 pins are required for both VCC and GND. To reduce the number of contacts, consider power jacks or larger contacts.

#### Tracks

Use available online PCB tools to assist in determining current capabilities in layout. One ounce of copper PCB with a track width of 1.27 mm results in approximately 3 A of current carrying capacity, and 3 mm of track width results in approximately 5 A of current carrying capacity. Allowing some headroom, a 20 A track requires a width of 19 mm (approximately 20 mm) (please note that increases in temperature have not been factored into this example). From Figure 4, a 20 mm track width is not feasible due to space constraints used for PSU and system circuitry. To resolve this, one easy solution is to make use of multiple PCB layers. Reduce the track width—for example, to 3 mm—and replicate these tracks to all available layers in the PCB to ensure that the total combined tracks (in all layers) meet at least 20 A of current capability.

Figure 4. Physical contacts and current handling capability.

#### Vias and Stitching

Figure 5 shows an example of vias in stitching the power planes of a PCB from a regulator. If a 1 A via is chosen and your power requirement is 2 A, the track width must be capable of carrying 2 A and the via stitching must be able to handle it too. The example in Figure 5 requires at least two vias (preferably three if the space is available) to stitch the current to the power plane. This is often overlooked when just a single via is used for stitching. When this is done, the via acts like a fuse, which will blow and disconnect power to the adjacent plane. Underdesigned vias can be hard to troubleshoot, as a blown via might not be noticeable or could be difficult to see if it’s been obstructed by components.

Figure 5. Via stitching.

Please note the following parameters for vias and PCB tracks: the track width, via hole size, and electrical parameters depend on several factors such as the PCB plating, routing layer, temperature of operation, etc., that influence the final current carrying capability. The previous PCB design tips have not factored in these dependencies, but designers should be aware of these when determining layout parameters. Many PCB track/via calculators are available online. It is highly advisable for designers to consult their PCB manufacturer or the layout engineers after the schematic design with these details in mind.

### Avoid Overheating

A number of factors can result in thermal issues, such as enclosures, airflow, etc., but this section focuses on the exposed paddle. Regulators with exposed paddles, such as the [LTC3533](/en/products/ltc3533.html), [ADP5304](/en/products/adp5304.html), [ADP2386](/en/products/adp2386.html), [ADP5054](/en/products/adp5054.html), etc., have a lower thermal resistance if connected correctly to the board. In general, if a regulator IC has power MOSFETs designed into the die (that is, it is monolithic), the IC typically has exposed pads for thermal dissipation. If the converter IC operates using external power MOSFETs (it is a controller IC), then the controlling IC generally does not require an exposed pad, since the main sources of heat (the power MOSFETs) are outside the IC.

Usually, these exposed pads must be soldered onto the PCB ground plane to be effective. There are exceptions depending on the IC, as some regulators specify that they can be connected to an isolated solder PCB area to act as a heat sink for thermal relief. If unsure, please refer to the data sheet for the part in question.

When you do connect the exposed pad to the PCB plane or to an isolated area, (a) make sure to stitch these vias (many of them are in an array form) to the ground plane for thermal relief (heat transfer). With respect to multilayer PCB ground planes, it is recommended that the required ground planes (on all layers) under the paddle be stitched together with vias. For more information, see the “[Thermal Design Basics](/media/en/training-seminars/tutorials/mt-093.pdf)” tutorial MT-093,2 AN136: “[PCB Layout Considerations for Nonisolated Switching Power Supplies](/media/en/technical-documentation/application-notes/an136f.pdf),”3 and AN139: “[Power Supply Layout and EMI](/media/en/technical-documentation/application-notes/an139f.pdf).”4

Note that the discussion about exposed pads is with respect to regulators. Usage of exposed pads for other ICs can require very different treatment. For further discussion about the use of exposed pads, visit the [EngineerZone](https://ez.analog.com/amplifiers/operational-amplifiers/f/q-a/17470/ad8045-exposed-paddle-connection)®.5

### Conclusion and Summary

Designing power supplies with sufficiently low noise, without impacting your systems circuitry with track or via burnout, is a challenge in terms of cost, efficiency, performance, and PCB area. This article highlighted some areas that a designer may overlook, such as architecting the power tree to support all downstream loads using a power budget analysis.

Schematics and simulation are just the first step in design, to be followed by careful component placement and routing techniques. Vias, tracks, and current carrying capability must be compliant and assessed. System circuitry will misbehave, and troubleshooting can be difficult to isolate if switching noise is present either at the interface or has been fed through to the IC’s power pins.

## References

1 [61302221121 header pin](https://www.digikey.ie/product-detail/en/w%C3%83%C2%BCrth-elektronik/61302221121/732-5302-ND/4846866). Würth Elektronik.

2 MT-093 Tutorial: “[Thermal Design Basics](/media/en/training-seminars/tutorials/mt-093.pdf).” Analog Devices, Inc., 2009.

3 Application Note 136: “[PCB Layout Considerations for Nonisolated Switching Power Supplies](/media/en/technical-documentation/application-notes/an136f.pdf).” Linear Technology, June 2012.

4 Application Note 139: “[Power Supply Layout and EMI](/media/en/technical-documentation/application-notes/an139f.pdf).” Linear Technology, October 2012.

5 [AD8045 Exposed Paddle Connection](https://ez.analog.com/amplifiers/operational-amplifiers/f/q-a/17470/ad8045-exposed-paddle-connection). EngineerZone, January 2011.

[LTM4700](/en/products/ltm4700.html). Analog Devices, Inc., October 2018.

[Power Management Tools](/en/resources/design-tools-and-calculators/power-management-tools.html). Analog Devices, Inc.
