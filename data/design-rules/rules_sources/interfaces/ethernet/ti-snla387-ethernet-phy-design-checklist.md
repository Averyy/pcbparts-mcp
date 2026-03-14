---
source: "TI SNLA387 -- Ethernet PHY Design Checklist"
url: "https://www.ti.com/document-viewer/lit/html/SNLA387"
format: "HTML"
method: "ti-html"
extracted: 2026-02-16
chars: 8641
---

# 1 Introduction

The design recommendations in this document apply
to all Ethernet PHY PCB designs, including designs using Texas Instrument Ethernet PHYs.
Following these guidelines is important because it helps reduce emissions, minimize
noise, ensure proper component behavior, minimize leakage and improve signal quality, to
name a few. This document is designed to work as a supplemental checklist to the device
and component data sheets.

# 2 PHY Design Checklist

The following is a list of areas that
should be reviewed on the PHY design. Each topic suggests which considerations to
take about the listed topic. Please check through all of the following listed topics
prior to submitting a request for additional engineer review. Comments, questions
and additional review will be able to be answered more quickly when using this list
as a guide.

**⃞ DRC Error Check**

Verify that the DRC rules are
accurate, and run a DRC error check. No errors should be present. Any DRC errors
should be corrected before continuing.

**⃞ Decoupling Capacitors**

Decoupling capacitors should be placed
as close to the PHY as possible. It is usually recommended that the smallest
capacitors are the closest to the PHY, but please check with the device data sheet
to verify this recommendation aligns with device-specific recommendations. For some
pins on some devices, the data sheet might recommend to place the larger capacitors
closer to the PHY.

**⃞ Clock Source**

The oscillator should be placed close
to the PHY. The further the an oscillator is from a PHY, the higher likelihood of
seeing PLL noise or out of spec behavior. A crystal should never be driving more
than one device. Please reference the following app note for more details on crystal
placement and design guides: <https://www.ti.com/lit/an/snla290/snla290.pdf>

**⃞ RBIAS Resistor**

The RBIAS Resistor should also be
placed close to the PHY.

**⃞ MDI Traces**

The total length of each MDI trace
should be less than 2 inches, or 2000 mils. The traces should be length-matched
within 20 mils for 1G transmissions and within 50 mils for 100M or 10M
transmissions. The number of vias and stubs on the MDI traces should be kept to a
minimum.

The typical impedance should be a 100
Ohm differential with a +/- 10% control. An impedance mismatch will decrease
throughput, sometimes significant enough to cause communication failure. The
mismatches cause signal reflections that prevent maximum power from being
transferred beyond the point of reflection. The impedance on the MDI traces may need
to be adjusted to match the impedance of the cable. Verify the cable impedance using
the cable's data sheet.

If *w* equals the width of the
MDI trace, ground planes on the same layer should be distanced at least 3\*w from the
MDI trace. The preferred distance is 5\*w from the MDI trace. Designing this distance
between the MDI trace and the ground plane prevents unwanted capacitive
impedance.

Figure 2-1 MDI Trace and Ground Plane
Spacing Example

Continuous ground is recommended on
the layer under the MDI traces. The ground plane should be cut, or void, only under
the components on the trace. Some of these components include transformer/magnetics,
chokes, AC coupling capacitors and ESD diodes. For automotive applications, an
*all-layer* void is recommended, but a *two-layer* void is the minimum
requirement. The *two-layer* void would include the layer the component is on
and the layer below. For standard applications, a *two-layer* void is
recommended. The distance between the edge of the component and the edge of the void
should be about 20 mils for most applications. Some applications can have a shorter
distance, while other may require a larger distance. Please use the design's EMC
requirements to determine the best distance.

**⃞ MII Traces**

The total length of each MII trace
should be less than 6 inches, or 6000 mils. The traces should be length-matched
within 20 mils for 1G transmissions and length-matched within 50 mils for 100M or
10M transmissions. RX traces must be length-matched to the other RX traces, and TX
traces must be length-matched to the other TX traces. The number of vias and stubs
on the MII traces should be kept to a minimum.

The single ended impedance should be
50 Ohms +/- 10%. The implications of an impedance mismatch are listed in the
previous topic.

Using the same definition of "w" from
the previous topic, ground keep out should be 3\*w at minimum around the MII traces.
The preferred distance is 5\*w.

**⃞ Signal Routing**

Crosstalk must be avoided. No signals
should cross unless properly separated by a ground layer. Additionally, different
differential pairs must have at least 30 mils of separation between the pairs.

As mentioned in the previous topics,
traces should be length matched. To match the trace lengths, different routing
techniques can be used. It is recommended to apply those techniques on the same end
of the length-matched pair. The figure below shows the difference between mismatched
length-matching and matched length-matching.

Figure 2-2 Length Matching

Depending on the characteristic
impedance throughout varying sections of the board, a mistmatched length-matching
could create additional timing or signal quality issues.

When placing signal vias, it is
recommended to place ground, or return, vias close by in order to provide a short
path to ground. [Figure 2-3](GUID-69D2F7FD-5907-444F-99C5-309715E2443C.html#FIG_NFG_BMW_FPB) shows an example.

Figure 2-3 Nearby Ground Vias for Short
Return Path

**⃞ Magnetic Isolation**

No metal should be under the magnetics
on any layer. If metal is needed under the magnetics, it must be separated by a
ground plane at the least. Metal under the RJ45 connector with integrated magnetic
is allowed. [Figure 2-4](GUID-69D2F7FD-5907-444F-99C5-309715E2443C.html#FIG_Y4K_VMW_FPB) shows a layout example with no metal below the magnetics.

Figure 2-4 Magnetics Metal
Keep-out

**⃞ ESD Device Selection and
Layout**

If ESD diodes are used in the design,
please make sure that their acting voltage range is sufficient enough to accommodate
the proper voltages needed for signal transmission. Refer to the PHY data sheet to
confirm the voltage specifications. The following app note covers the fundamentals
and general guidelines for ESD device layout: <https://www.ti.com/lit/an/slvaex9/slvaex9.pdf>. This next following app note covers Ethernet-specific ESD
guidelines and considerations: <https://www.ti.com/lit/an/slvae50/slvae50.pdf>.

It should be noted that the two app notes mentioned above have a different
recommendation for placement location for the protection device. The
Ethernet-specific app note recommends that the protection device be placed on the
PHY side of the magnetics, rather than the connector side. The reason for this
contradiction is that Ethernet has a risk for high common mode voltage swings on the
connector side. Placing the protection device on the PHY side of the magnetics
ensures that the protection device doesn’t fail during high, non-ESD voltages.

**⃞ Power Planes**

Use power planes where possible to
avoid voltage drops from supply to pin. If stitching power planes across layers, use
multiple vias to avoid voltage drops.

**⃞ Ground Planes**

Place Ground Planes where possible and
use stitching vias throughout the board to create short return paths. [Figure 2-5](GUID-69D2F7FD-5907-444F-99C5-309715E2443C.html#FIG_FRD_PNW_FPB) shows an example of ground via distribution.

Figure 2-5 Ground Plane Vias

**⃞ Earth Ground
Isolation**

Earth ground should be isolated from
the rest of the board by at least 20 mil keep out on all layers. [Figure 2-6](GUID-69D2F7FD-5907-444F-99C5-309715E2443C.html#FIG_OCS_VNW_FPB) shows an example of this.

Figure 2-6 Ground and Earth Ground Keep
Out

The recommended exception to the keep out is as follows: earth ground and normal
ground should be connected with a capacitor and a high value resistor. A resistor of
1 MΩ or more is recommended.

# 3 Summary

The checklist described is a list of
suggestions that will help a PHY operate the closest to ideal behavior. Following these
suggestions can help prevent unwanted issues. PCB design issues that are not listed in
this document can still occur, and all designs should be checked using the component
data sheets. PCB designs should also be reviewed by more than one engineer before
fabrication.