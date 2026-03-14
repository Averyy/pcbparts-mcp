---
source: "Eurocircuits -- Tombstoning: PCB Assembly Guidelines"
url: "https://www.eurocircuits.com/technical-guidelines/pcb-assembly-guidelines/tombstoning/"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 7169
---
#### What is Tombstoning?

Tombstoning (also known as Manhattan effect or crocodile effect) usually affects surface mount passive components such as resistors, capacitor and inductors. It is where one end of the component lifts from a pad of the PCB during the soldering process.

The final angle of the component will vary from a few degrees up to 90 degrees, however, regardless of the angle the result is that one of the component terminals is NOT soldered to the PCB pad and an open circuit is created.

#### What Causes a Component to Tombstone?

To understand what causes components to Tombstone we must first understand the part of the soldering process known as Wetting.

Wetting is where the Solderpaste becomes fluid or molten and is able to attach itself to the component terminal and to the pad on the PCB. The ideal situation is when all the terminals of a component complete the Wetting process at the same time creating a solid physical and electrical inter-metallic bond.

It is important as when the Solderpaste becomes fluid it applies a pulling force to each of the component terminals, known as the Meniscus Pull, something like a Tug-of-War on the component.

This pulling force has the benefit of helping self-centre the component between its pads if the Wetting process is completed at the same time.

On passive component a significant difference in the completion time of the Wetting process may result in many defects one of which is Tombstoning other include bill-boarding, misalignment, shorting etc. Basically, the pad that completes the Wetting process first will win the Tug-of-War and may pull the component vertically resulting in Tombstoning.

What it really comes down to is the difference in thermal mass between pads of the same component. This will define how quickly the Solderpaste is heated and becomes fluid then, how quickly the heat dissipates and the solder becomes solid.

Whilst there are assembly process issues that may result in Tombstoning we should accept that these are under control by the assembler.

Therefore, in this section we will focus only on the PCB Layout related issues and how to avoid them.

#### PCB Layouts that Cause Tombstoning

Tombstoning is related mainly to Passive Components with 2 terminals and the goal should be to ensure that the Wetting process for each of the terminals of a component is completed at the same time.

Below are the main reasons that influence the heat dissipation from a component pad and thus the Wetting process.

* Track Size to the Pad
* PTH Close to the Pad
* Pads Connected to Large Copper Areas
* Via in Pad

#### Track to the Pad Issues

Avoid multiple tracks to one pad and only one track to the other pad different track widths to pads of the same component, also avoid different track widths to pads of the same component.

Common Layout

Two possible solutions are shown above.

The aim is to make the track width to each pad of the component the same width. An important point to consider is that this unified track width must be run at least 0.25mm from the pad edge before the width changes to help keep the Wetting process in sync.

#### PTH Close to the Pad

Any PTH (Plated Through Hole) including Via Holes that are too close to a pad will dissipate the heat quicker during the Wetting process. There should be a minimum of 0.25mm from the edge of the component pad to the edge of the actual hole.

In addition, if the PTH is too close to the component pad to ensure a reliable Soldermask Dam then the solder will flow into the hole (known as Wicking or Solder Escape).

In both cases this may result in Tombstoning.

The graphic on the left shows a layout where the PTH is too close to the component pad, the one on the right, shows the PTH with the minimum distance of 0.25mm from the pad edge to hole edge.

The graphic above shows the Via Hole in the component pad, there are 2 possible solutions.

The first is to use Via Filling, this will help reduce the copper area of the pad however, the Via Hole itself will still dissipate heat and the Wetting process may still not be unified.

The second and more reliable solution is to move the Via Hole at least 0.25mm from the edge of the component pad to the edge of the Via Hole.

#### Pads Connected to Large Copper Areas

Large copper areas act as Heatsinks and therefore connecting a component pad to one as in the graphics above would most likely result in Tombstoning.

To solve this issue ensure a track of a similar size is connected to both pads (as in the graphic above). In addition, there should be at least 0.25mm of track before it connects to the copper area, in fact the longer the better.

If high power is involved then use a similar solution as above (Track to the Pad Issues),

#### Via in Pad

As miniaturisation of electronics continues so does the available real-estate on PCB to place components and run tracks etc.

One solution is to place Via Holes in component pads, however, the Solder will Wick/Escape down the hole resulting in an uneven Wetting Process.

Even if both component pads have Via Holes in them there is still a high chance of one completing the Wetting process before the other depending upon what the Via Hole is connected to and Tombstoning may still occur.

Also with Via Holes in pads there is the issue of having sufficient Solderpaste to fill the Via Hole and still attach to the Component terminals during the Reflow process.

The graphics show Via Holes in component pads, as the Via Holes are unfilled the Solder Paste will Wick/Escape into the holes and may result in Tombstoning or unsoldered an component terminal.

Via Filling is one solution and will help reduce the risk of Tombstoning.

However, moving the Via Holes at least 0.25mm from the component pad edge to the edge of the Via Hole is a more reliable solution.

#### Shape and Position of Pads

If the size of the pad is too big, it could cause shifted or rotated components or Tombstoning.

If the position of the pads differs too much from what is needed for this specific component, then the result of the soldering process will be most likely bad.

The best solution is to use IPC standard Pad shapes and sizes to avoid issues like this, compare the Pads of your CAD system to those recommended in the IPC standard. This you can also check by using our PCBA Visualizer as this is a standard check shown in the Assembly Checker.

#### Legend under a component

Even legend under smaller components could cause tombstoning. Together the copper-, soldermask- and legend layer could create a higher point than the height of the copper pads. See the R2 resistor on the picture bellow.

There is a track between the pads of the component and over it is solder mask and legend on top of that. The result can be a lift-off for the component.

This is critical in case of small components e.g. 0603. Please avoid to put legend under these components.
