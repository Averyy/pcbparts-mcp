---
source: "Embedded Hardware Design -- USB 2.0 PCB Layout Guidelines"
url: "https://embeddedhardwaredesign.com/usb2-0-pcb-layout-guidelines/"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 14097
---
When implementing a USB interface on a PCB to connect a microcontroller, microprocessor, or USB PHY to a peripheral device, maintaining signal integrity becomes crucial. At USB 2.0 High-Speed rates (up to 480 Mbps), factors such as signal reflections, insertion loss, crosstalk, and noise significantly impact performance.

> *To ensure reliable operation, [USB 2.0](https://embeddedhardwaredesign.com/usb-2-0-architecture-explained/) PCB layout guidelines must be carefully followed to address these concerns and achieve proper signal integrity, EMI/EMC compliance, and optimal performance. In this blog, we will explore the key considerations and best practices to keep in mind while routing USB 2.0 signals.*

# USB2.0 Parameters

# USB2.0 Placement Guidelines

Below is the [standard USB 2.0](https://embeddedhardwaredesign.com/usb-2-0-standard-explained/) circuit. Let’s review and understand how each of these USB components should be placed on the PCB for optimal performance.

Source: https://www.ti.com/

## Ferrite Bead & RC Filtering

* To prevent EMI from coupling onto the USB VBUS line—which can act as a large antenna—a ferrite bead can be inserted in series with the VBUS pin (pin 1 of the USB connector). This ferrite should have impedance in the range of 47 Ω to 1000 Ω at 100 MHz, and similarly maintain resistive characteristics up to approximately 1 GHz.
* Place a 0.01 μF capacitor between each VBUS line and chassis ground, positioned close to the USB connector pin.
* As shown above, place a 0.01 μF capacitor (as a placeholder) and a resistor placeholder between the ground line and the chassis ground, positioned close to the USB connector pins. The placeholder components should use a 1206 package or larger. The RC values can be adjusted and optimized during EMI/EMC testing to achieve better performance

## ESD Protection Placement Guidelines

To effectively suppress electrostatic discharge (ESD), the protection circuitry should be placed as close as possible to the USB connector. This minimizes the risk of high-voltage, high-frequency ESD pulses propagating into the PCB and affecting sensitive components.

Most equipment must comply with IEC 61000-4-2 standards, which define ESD testing requirements. To meet CE compliance—required for marketing products within the European Union—devices must successfully pass:

* Contact discharge up to 8 kV
* Air discharge up to 15 kV

During IEC ESD testing, only pins or interfaces accessible from the outside of the product need to meet these criteria. Ensuring proper ESD protection near the USB connector is key to passing compliance tests and maintaining product reliability.

## Other Placement Guidelines

* The USB 2.0 PHY/MCU/MPU should be placed directly above a solid, continuous ground plane to ensure proper signal referencing and reduce EMI.
* If USB PHY is used, place the crystal and its load capacitors as close as possible to the USB PHY clock input/output pins (XI and XO) to minimize trace length and preserve signal integrity.
* Avoid placing power sources or large capacitors near the crystal, as their noise can modulate the clock signal, potentially leading to issues like dropped USB packets.
* Include a placeholder for a resistor in parallel with the crystal to support oscillator startup stability, if needed.
* Switching power regulators can generate significant noise, which may couple into sensitive parts of the circuit. To minimize interference, these regulators should be placed **away from critical components** such as the **DP/DM signal lines**, the **external clock crystal or oscillator**, and the **USB PHY**

## Recommended USB2.0 Layer Stack-up

Due to the high frequencies involved in USB signaling, it is recommended to use a **printed circuit board with at least four layers**. A typical stack-up includes **two signal layers**, separated by **continuous ground and power planes**, as illustrated in the figure.

Ideally, USB signal traces should be routed on a **single signal layer (preferably SIGNAL1)**. This layer should be positioned **adjacent to an unbroken ground plane** to ensure consistent impedance and minimize noise. **Avoid routing signals across splits** in the ground or power planes, as this can degrade signal integrity. Additionally, **minimizing the use of signal vias** is important to reduce EMI, as each via introduces inductance, especially at high frequencies.

# USB2.0 Routing Guidelines

The USB data lines, D– and D+, should be routed as a differential pair with matched impedance. The trace impedance on PCB must align with the USB cable’s nominal differential impedance of 90 ohms. Failure to maintain proper impedance matching can lead to signal reflections and degrade the eye diagram, as illustrated in the figure below.

USB 2.0 Eye Diagram

The DP/DM signal amplitude is relatively low (400 mV ±10%), making it susceptible to differential noise picked up by the twisted pair. When DP/DM traces lack proper shielding, they can act like antennas, capturing noise from nearby components and the surrounding environment. To reduce these effects, consider the following layout guidelines:

## Recommended Routing Rules of Thumb

**Differential Pair Routing (DP/DM)**

* **Impedance Control**:
  + Target **90 Ω ±15% differential impedance**.
  + Single-ended impedance of **45 Ω ±10%** per trace.
* **Trace Geometry**:
  + Keep DP and DM traces **parallel and tightly coupled**.
  + Use **controlled impedance stackup** (consult your PCB fab).
* **Length Matching**:
  + Route DP and DM as short as reasonably possible
  + Match DP and DM traces **within 2 mils (0.002″)**.
  + Total trace length should be **<4 inches (100 mm)** to preserve eye diagram quality.
* **Avoid Stubs**:
  + Route test points in **fly-by** fashion—no branches/stubs.
* **Trace Width and Spacing**:
  + Determine based on PCB material and layer stackup to maintain 90 Ω differential impedance.
  + Use online impedance calculators or consult your manufacturer.

## Grounding and Reference Planes

* Maintain a **continuous ground reference** under DP/DM signals.
* Avoid splits or gaps in the reference plane beneath USB signals.
* Use **a solid ground plane** directly under the USB differential pairs from source to destination to prevent EMI and maintain impedance.

## Via Usage

* **Minimize vias** on DP/DM lines to reduce impedance discontinuity and signal loss.
* If vias are necessary, **match them** on both lines and keep them close together.

## Test Points

* If test points are needed, **route through** them—not as stubs.
* Use small SMT pads directly in the signal path (if required).

## Few USB2.0 Specific Guidelines Explained

**Differential Skew & D+ & D- Length Matching**

As per High Speed USB2.0 100 ps skew limit in the High Speed standard, we can now calculate the allowed length mismatch between the two sides of the differential pair (the D+ and D- signals). Taking the approximate 6 ns/inch propagation delay estimate for surface-layer routing, and multiplying by the skew limit, we get a 0.6 inch (600 mil) trace length difference.

This is very large! We have a lot of freedom to allow for some trace length matching. However, there is an important point here: this includes the entire length of the interconnect (your board + cable + receiving board). Therefore, just to be safe, do your best to limit skew as much as possible by [routing the pairs together](https://resources.altium.com/p/high-speed-pcb-differential-pair-routing-to-preserve-signal-integrity) and enforcing a bit of length matching where possible.

This is quite easy because USB controller chips will generally place the D+ and D- signals on the same edge of the chip. Subtracting the transmitter output driver skew and allow to allow skew guard band, the differential length should be matched within 50 mil, whereas 20 mil provide best result.

When serpentine is used to match the length, the matching should be made as close as possible to the point where the mismatch occurred as shown in below picture.

Length matching near location of the mismatch

Some of the eye diagrams illustrate the impact of different USB signal trace lengths—2 inches, 5 inches, and 10 inches. It is clearly evident that shorter USB trace lengths result in a much cleaner and more open eye diagram, indicating better signal integrity.

Shorter USB2.0 traces length Vs Longer trace length

Several of the eye diagrams demonstrate the effects of short USB 2.0 signal traces with both matched and mismatched differential pair lengths. It is clearly evident why maintaining length matching in differential pairs is critical for preserving signal integrity.

USB2.0 matched differentials pair Vs mismatched pair 1.5 Inches

USB2.0 matched differentials pair Vs mismatched pair 7 Inches

**Avoid Stub on USB2.0 trace**

Stubs should be avoided, as they can cause signal reflections. However, this is rarely an issue in USB designs since the data traces are typically point-to-point. If a test point is required, the signal should be routed through it in a fly-by configuration, rather than using a Long Branch trace to connect the test point as show in below pictures.

**USB2.0 Traces Layer Switching**

When routing USB 2.0 signals between different PCB layers, it’s important to ensure a continuous return path for the signals. Although differential pairs primarily reference each other, they still rely on a nearby reference plane for proper return current. Therefore, stitching vias should be placed adjacent to the signal vias to maintain return path continuity, as illustrated in the figure below. This becomes especially critical in multilayer PCB designs.

Switching layers on PCB

**Routing Over Split Plan**

If crossing a split in the reference plane is unavoidable, it’s essential to provide a **continuous return path for high-frequency currents**. This can be achieved by placing a **decoupling capacitor (e.g., 100 nF in a 0603 or smaller package, stitching capacitors)** between the two planes, positioned **close to each high-speed signal trace**.

A **power plane** can also serve as a valid reference for high-speed signals, provided there is an effective return current path. Additionally, when a trace **transitions between reference planes**, it should **cross at a 90-degree angle** to minimize coupling and maintain signal integrity.

**Differential Pair to Pair/ Other High Speed Signal spacing**

To reduce crosstalk, **minimize the length of high-speed clock and other periodic signal traces** that run parallel to USB 2.0 high-speed differential pairs. Maintain a **minimum spacing (D) of at least four times the dielectric height (h)** between the USB pair and nearby traces.

If adjacent signals have **significantly higher voltage swings or faster edge rates** than the USB signals, increase the spacing to **at least 30 mils** to prevent unwanted coupling.

## Layout Guidelines for USB Connector

A standard USB connector provides good ESD protection. However, following guidelines should be observed to ensure good ESD protection.

* There should be an easily accessible shield plate next to the connector for air-discharge mode purpose.
* Tie the outer shield of the connector to GND. When a cable is inserted into the connector, the shield of the cable should first make contact with the outer shield.
* If the connector includes power and GND, the lead of power and GND need to be longer than the leads of signal.

# USB 2.0 PCB Layout Guidelines – Summary

### **Overview**

When integrating USB 2.0 (High-Speed) interfaces into a PCB, maintaining **signal integrity**, **EMI/EMC compliance**, and **robust ESD protection** is essential. USB 2.0 operates at up to **480 Mbps**, making trace impedance, length matching, and routing discipline critical.

### **Component Placement Guidelines**

* **Ferrite Bead** on VBUS to block EMI (47–1000 Ω @100 MHz).
* **01 µF capacitor** close to USB connector between VBUS and chassis ground.
* **RC Filter (placeholders)** between GND and chassis ground; use ≥1206 package.
* **ESD Protection** must be placed as close as possible to USB connector.
* **Crystal Oscillator**: Place close to PHY pins (XI/XO), avoid noisy power sources nearby.
* **Switching Regulators**: Keep away from USB signal traces and PHY.

### **PCB Layer Stack-up**

* Recommended: **4-layer PCB**
  + SIGNAL1 (top layer) for USB routing
  + Ground Plane (below SIGNAL1) for return path and impedance control
* Avoid routing across plane splits.
* **Minimize signal vias** to reduce EMI and preserve impedance.

### **Routing Guidelines**

#### Differential Pair (DP/DM) Routing

* **Impedance Control**:
  + 90 Ω ±15% differential (45 Ω ±10% per trace)
* **Trace Geometry**:
  + Keep DP/DM parallel, tightly coupled, on same layer
* **Length Matching**:
  + Match within **20 mils**, max **50 mils**
  + Max trace length: **< 4 inches**
* **Avoid Stubs**:
  + Route test points in **fly-by configuration**, not as branches
* **Via Usage**:
  + Avoid when possible; if needed, match via placement between DP and DM

### **Grounding & Return Path**

* **Continuous solid ground plane** under differential pair.
* **Stitching vias** near signal vias during **layer transitions** to maintain return path.
* If **crossing split planes**, use **decoupling capacitors** (e.g., 100 nF) as stitching caps.

### **Crosstalk & Signal Spacing**

* Maintain **spacing ≥ 4 × dielectric height (h)** between USB pair and other high-speed traces.
* Increase spacing to **≥ 30 mils** if adjacent signals have fast edges or large swings.

### **USB Connector Layout**

* Ensure **shield pin** is tied to **chassis ground**.
* Allow early contact of shield before signal lines during cable insertion.
* Include an accessible **shield plate** for **air discharge protection**.
