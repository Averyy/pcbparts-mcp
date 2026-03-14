---
source: "Altium -- Stripline vs Microstrip: Differences and Routing Guidelines"
url: "https://resources.altium.com/p/stripline-vs-microstrip-understanding-their-differences-and-their-pcb-routing-guidelines"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 8334
---
Traces in a PCB are given two possible names based on their location in a PCB stackup: striplines and microstrips. In a PCB, a stripline and microstrip are two different transmission line structures used in a PCB layout. Microstrips and striplines also come in the coplanar and differential varieties, and all of these have certain advantages when used for high-speed or high-frequency signals. If you're looking for a thorough comparison of microstrips and striplines in a PCB layout, I'll present the advantages of each routing style as it is used in high speed PCB layout and routing.

Before getting started, it's important to know that the main factor creating differences between microstrips and striplines is their location in the PCB stackup. For a stripline placed inside the PCB stackup, the trace is fully exposed to the dielectric material, and the dielectric's material properties will have greater influence over a signal propagating along a stripline. We'll discuss the basics of striplines and microstrips below, and hopefully you'll be able to see why certain differences arise in these two trace routing styles.

## Striplines and Microstrips - What Are They?

Striplines and microstrips are [types of PCB transmission lines](https://resources.altium.com/p/board-layer-stackup-considerations-for-high-speed-board-design) in a circuit board layout. These types of traces do not only have to carry high speed signals, they can carry any slow or DC signal, or a high frequency signals. The goal in designing a stripline or microstrip is to first determine if a target impedance is needed, then determine the trace width that ensures the trace impedance will hit the target value. The target impedance is normally [50 Ohms for single-ended traces](https://resources.altium.com/p/mysterious-50-ohm-impedance-where-it-came-and-why-we-use-it), but it could be different depending on the interface or signaling standard being used in your components.

The main difference between these types of traces is their location in the PCB: microstrips are on the surface layer, while striplines are on an inner layer between two reference planes. The placement of the reference planes is important as this is what makes a microstrip or stripline trace. In modern designs, it's best to use these configurations to route high speed signals as the reference planes inside the layer stack will isolate signals on different layers from each other. Unless everything is operating at low speed, it's best not to put two signal layers adjacent in the PCB layer stackup, and instead focus on designing the stackup to enable microstrips and striplines.

In terms of manufacturing, the processes involved are basically the same: coat with photoresist, expose, and etch. The resulting developed layer will be incorporated into the layer stackup just like any other layer in a PCB. The additional cost involved in stripline fabrication comes from the fact that striplines only exist in a multilayer PCB, so the additional cost comes from the assembly steps required in constructing the stackup and not from the etching process used to form the actual striplines.

### Examples of Stripline and Microstrip Routing Styles

The following are some examples of stripline and microstrip routing techniques, as well as some of their basic characteristics:

1. **Microstrip.** Transmission lines that are routed on the external layers are called microstrips. These are always routed above a large reference plane on the adjacent layer.
2. **Edge-Coupled Microstrip.** This refers to two microstrips routed in parallel, which is used for routing differential pairs. It is the same structure used in regular microstrips.
3. **Symmetric Stripline.** These traces are routed on internal layers between two reference planes. A symmetric stripline is located centrally between the two reference planes, also simply called just plain “stripline”.
4. **Asymmetric Stripline.** Although similar in structure to an symmetric stripline, the trace is not centrally located between the two reference planes.
5. **Edge-Coupled Stripline.** Just like edge-coupled microstrips, these traces are routed in parallel and are normally used as differential pairs. These traces can be symmetric or asymmetric.
6. **Broadside-Coupled Stripline.** This technique is also used for routing differential pairs on internal layers, but the pairs are stacked on top of each other instead of being routed side-by-side.
7. **Embedded Microstrip.** Embedded microstrips are not really used in modern PCBs except in some HDI PCBs. In this case, because two groups of traces may be placed on the top two layers, the traces may not carry high speed signals, instead being used for slow GPIOs. However, the impedance and loss model for this type of routing could be used to examine the effects of soldermask on a microstrip.

Each of these could be placed in a coplanar configuration, where ground is poured around the traces to set the impedance to a desired value as well as provide some shielding around the trace at certain RF frequencies. The image below shows the set the geometries used in these trace configurations.

The geometry of each type of trace will determine its impedance. The layer of the PCB that the transmission line is routed on and the dielectric constant of the PCB materials are also used to calculate the impedance of these types of traces. There are many impedance calculators with stripline and microstrip models that are available for making these calculations. To see how impedance is calculated and to get a quick estimate of trace impedance, you can use one of our calculator applications:

If you want to get more accurate calculations, and you want to account for more advanced challenges like copper roughness, you will need a more advanced calculator. The best ECAD software will include a field solver-based model that can perform these calculations for you as you build your stackup.

### Comparing Striplines and Microstrips

Since these trace arrangements are the standard way to route boards for modern electronics, what are the relative advantages of these types of PCB traces? The electromagnetic field around striplines and microstrips determines how a traveling signal interacts with the surrounding dielectric material, which will then determine the amount of loss and radiation from the structure. The table below compares these characteristics for striplines and microstrips.

|  |  |  |
| --- | --- | --- |
|  | Microstrips | Striplines |
| Propagation constant | Lower (usually about 3); waves move faster | Higher (equal to substrate’s Dk); waves move slower |
| Dielectric losses | Lower | Higher |
| Radiation losses | Higher | Lower |
| Trace width | Can be 2x stripline width for moderate layer-to-layer spacing | Can be thin for given layer-to-layer spacing |
| Shielding | Lower; depends on distance to ground plane | Higher; only susceptible to crosstalk from other striplines on same layer |

My hope is that this tutorial on stripline and microstrip will clear up some confusion as to how these routing styles are designed. The most important point to remember is that these traces don't have to only be used in a [high speed board](https://resources.altium.com/p/an-overview-of-the-high-speed-pcb-design-guidelines-youll-need-for-your-pcb-layout), you can take advantage of the shielding provided by reference planes in any type of signal.

When you’re looking for the best ECAD software package for calculating trace impedance for striplines and microstrips, use the [Layer Stack Manager](https://www.altium.com/documentation/altium-designer/pcb/defining-layer-stack) and PCB routing features in Altium Develop. The integrated design rules engine and the industry's best routing features ensure your traces will always be accurately sized and placed in your PCB layout. When you’ve finished your design, and you want to release files to your manufacturer, Altium Develop makes it easy to collaborate and share your projects.
