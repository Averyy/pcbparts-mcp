---
source: "Altium -- Fly-by Topology for DDR3 and DDR4 Memory: Routing Guidelines"
url: "https://resources.altium.com/p/fly-topology-routing-ddr3-and-ddr4-memory"
format: "HTML"
method: "readability"
extracted: 2026-03-02
chars: 8155
---

*Banner image credit: [Nine Dot Connects](https://www.ninedotconnects.com/ddr-design-services)*

Take a look at your RAM chips the next time you're upgrading your desktop or laptop. If you need to, get the chip under a magnifying glass. Any traces you might see on the surface layer are just the beginning of a complicated web of traces between the edge connector and the RAM chips. Although the routing can get quite complicated, you can see a relatively simple topology when you take a 30,000 foot view of the PCB layout.

This relatively simple layout topology is known as fly-by topology. The layout scheme in fly-by topology is preferrable over a double-T topology for multiple signal integrity reasons. Fly-by topology incurs less simultaneous switching noise, and DDR protocols can still handle the skew incurred in fly-by routing by supporting write leveling. It also works well with high-frequency applications, and reduces the number and length of via stubs.

Since fly-by topology offers the best signal integrity for DDR3 and DDR4 memory, we should learn more about how it affects your DDR routing guidelines. Take a look at our DDR3 and DDR4 fly-by topology routing guidelines to learn more.

## DDR Layout Guidelines: Double-T vs. Fly-by Topology

Fly-by topology has a daisy chain structure that contains either very short stubs or no stubs whatsoever. Because of that structure, fly-by topology has fewer branches and point-to-point connections. When working with DDR3 and DDR4 routing, the fly-by topology begins with the controller, starts with Chip 0, and routes through Chip N—or the upper data bit. Routing occurs in order by byte lane numbers, and data byte lanes are routed on the same layer. Routing can be simplified by swapping data bits within a byte lane if needed. Fly-by topology is shown below.

*Fly-by topology for DDR layout and routing*

An alternative topology for DDR layout and routing is the double-T topology. In this topology, the differential clock, command, and address fanout from the memory controller all branch into a T-section, which can support 2 chips. Each branch could split again to support 2 chips each, for a total of 4 chips. In general, 2^N chips can be connected with a double-T topology (N = number of branches). Each section is then routed to a single RAM chip. The strobe and data lines are routed directly from the memory controller to each RAM chip. This is shown in the diagram below.

*Double-T topology for DDR layout and routing*

T-topologies were common in DDR2 routing, but each branch created accumulated impedance differences at DDR2 frequencies. Therefore, fly-by topology is preferable in DDR3 and later generations as each device only sees a single branch on the CLK/command/ADDR lines. In particular, fly-by topology is preferable for single-die RAM devices, while either topology could be used in multi-die devices. Although you have some some freedom to pick between these different topologies, DDR3 and DDR4 are easier to route with fly-by topology, and you'll see some signal integrity benefits.

## Fly-by Topology in DDR Layout and Routing Guidelines

In using fly-by topology, there are some basic DDR guidelines to follow as you route tracks that can help ensure signal integrity. The first is your layer stack arrangement and chip orientation. If the board design has sufficient space, the ADDR/command/control/CLK lines should be routed on the same layer, but you can save space by routing on different layers if needed. The ADDR/Command/Control/CLK routing progresses from the lowest data bit chip to the highest data bit chip. There should be no less than 200 mils of space between memory chips. Finally, place 100 Ω differential termination at the last SDRAM device in chain.

As you begin to place components, it’s important to set aside space for fan-out, termination resistors, and termination power supplies. Additionally, your routing plan must avoid routing through via voids on the plane. The vias should spread out and allow for two or more traces to be routed between the vias. Spreading the fanout increases the number of routing channels.

*The DQS lines in this SODIMM module are routed on the same layer.*

Note that fly-by topology intentionally adds some skew between each lane. This reduces [simultaneous switching noise](https://resources.altium.com/p/it-simultaneous-switching-noise-or-crosstalk) when one chip switches. In effect, nearby chips will be unaffected as there is some delay between switching events in different chips. In addition to this signal integrity advantage, there are other points to consider when routing DDR3 and DDR4 devices.

## Signal Integrity in Fly-by Routing for DDR3 and DDR4

If you're routing on the inner layers, striplines or dual striplines can be used for differential pairs. Surface traces should be routed as impedance-controlled microstrips. All lines need impedance control to suppress reflections along interconnects and at the receiver. Traces are recommended to have 50–60 Ω single-ended impedance (100–120 Ω differential impedance) for most interfaces. Note that the JEDEC spec for DDR3 specifies two drive strengths at 34 and 40 Ω for single-ended I/Os. DDR4 allows for an additional impedance option up to 48 Ω. However, modern devices use on-die termination to match to the appropriate characteristic impedance values, which may be programmable on the driving processor. Be sure to check the input and output impedances for your components and apply termination where necessary.

One approach to achieving greater signal sensitivity and constraints involves bundling the data byte lanes. This will simplify your routing process, but be careful of trace-to-trace spacing within lanes to prevent excessive crosstalk within a lane. Bundled signals should be carefully length matched according to the guidelines specified in your device datasheets, although be careful as these generally assume a Dk value of 4 for the substrate material. If you're routing on an alternative PCB substrate material, you'll need to adjust the length matching value to compensate for an allowed time delay ([or phase delay on differential pairs](https://resources.altium.com/p/delay-tuning-for-high-speed-signals-what-you-need-to-know)).

For trace spacing, many DDR guidelines will specify different values, but these can be easily taken out of context. Be careful with selecting the spacing between traces and pairs from application notes as these often assume a specific layer stack. The exact spacing between each end of differential pairs should be chosen to maintain required differential impedance. Wider traces can accommodate denser routing as they will have lower inductance, which is the dominant source of crosstalk at practical DDR frequencies. It's best to [run crosstalk simulations](https://resources.altium.com/p/evolution-simulation-technology-and-crosstalk) to examine your limits on spacing between single-ended and differential traces.

## Using Altium for Fly-by Route Design

Given the complexity of larger numbers of routes, you should use the schematic as the foundation for your design. With the schematic in hand, you can locate key components and nets. With this technique, you can use cross-selection and cross-probing from schematic components and nets to highlight the same item on the PCB. These features, combined with your design rule setting, will help you identify differential pairs that need length matching, will help you maintain target impedance, and required spacing during routing.

Take a look at these other articles to learn more about DDR3/DDR4 routing and layout guidelines:

High-speed PCB designs are complex and require planning for component placement and impedance control. Altium Develop gives you a complete set of rules-driven interactive routing tools for implementing fly-by topology in your DDR3 and DDR4 layout. Overall, you should build routes that result in a direct path and an interconnect solution for each side of the bus. The CAD features in Altium PCB Editor make it easy to create your DDR3 or DDR4 layout to ensure signal integrity and ease of routing.