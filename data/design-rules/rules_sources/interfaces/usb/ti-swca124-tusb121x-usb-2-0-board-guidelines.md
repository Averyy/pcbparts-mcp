---
source: "TI SWCA124 -- TUSB121x USB 2.0 Board Guidelines"
url: "https://www.ti.com/lit/pdf/swca124"
format: "PDF 4pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 6509
---

# TUSB121x USB 2.0 Board Guidelines

## Abstract

The document describes the TUSB121x USB 2.0 board guidelines.

## 1. TUSB121x USB 2.0 Product Family Board Layout Recommendations

### USB General Considerations

| Item | Recommendation |
|------|---------------|
| 1.00 | USB design requires symmetrical termination and symmetrical component placement along the DP and DM paths |
| 1.01 | Place the USB host controller and major components on the unrouted board first. |
| 1.02 | Place the USB host controller as close as possible to the transceiver device, that is, ULPI interface traces as short as possible |
| 1.03 | Route high-speed clock and high-speed USB. Route differential pairs first. Since these signals are critical and long length traces are to be avoided, it is therefore recommended to route DP/DM before routing less critical signals on the board. A similar recommendation is true for CLK and ULPI signals which should be routed with equalized trace length. |
| 1.04 | Maintain maximum possible distance between high-speed clocks/periodic signals to high speed USB differential pairs and any connector leaving the PCB (such as I/O connectors, control, and signal headers or power connectors). |
| 1.05 | Place the USB receptacle at the board edge |
| 1.06 | Maximum TI-recommended external capacitance on DP (or DM) lines is 4 pF. This capacitance is the sum of all external discrete components; the total capacitance on DP (or DM) lines including trace capacitance can be larger than 4 pF. All discrete components should be placed as close as possible to the USB receptacle. |
| 1.07 | Place the low-capacitance ESD protections as close as possible to the USB receptacle, with no other external devices in between. |
| 1.08 | Common mode chokes degrade signal quality, thus they should only be used if EMI performance enhancement is absolutely necessary. |
| 1.09 | Place the common mode choke (if required to improve EMI performance) as close as possible to the USB receptacle (but after the ESD device(s)). |

### USB Interface (DP, DM)

| Item | Recommendation |
|------|---------------|
| 2.00 | Separate signal traces into similar categories and route similar signal traces together, that is, DP/DM and ULPI. |
| 2.01 | Route the USB receptacle ground pin to the analog ground plane of the device with multiple via connections. |
| 2.02 | Route the DP/DM trace pair together. |
| 2.03 | For HS-capable devices, route the DP/DM signals from the device to the USB receptacle with an optimum trace length of 5 cm. Maximum trace length 1-way delay of 0.5 ns (7.5 cm for 67 ps/cm in FR-3). |
| 2.04 | Match the DP/DM trace lengths. Maximum mismatch allowable is 150 mils (~0.4 cm). |
| 2.05 | Route the DP/DM signals with 90 ohm differential impedance, and 22.5~30 ohm common-mode impedance (objective is to have Zodd ~= Z0 = Zdiff/2 = 45 ohm). |
| 2.06 | Use an impedance calculator to determine the trace width and spacing required for the specific board stackup being used. |
| 2.07 | Keep the maximum possible distance between DP and DM signals from the other platform clocks, power sources and digital/analog signals |
| 2.08 | Do not route DP/DM signals over or under crystals, oscillators, clock synthesizers, magnetic devices, or ICs that use clocks. |
| 2.09 | Avoid changing the routing layer for DP/DM traces. If unavoidable, use multiple vias. |
| 2.10 | Minimize bends and corners on DP/DM traces. |
| 2.11 | When it becomes necessary to turn 90 deg, use two 45 deg turns or an arc instead of making a single 90 deg turn. This reduces reflections on the signal by minimizing impedance discontinuities. |
| 2.12 | Avoid creating stubs on the DP/DM traces as stubs cause signal reflections and affect global signal quality. |
| 2.13 | If stubs are unavoidable, they must be less than 200 mils (~0.5 cm). |
| 2.14 | Route DP/DM signals over continuous VCC or GND planes, without interruption, avoiding crossing anti-etch (plane splits), which increase both inductance and radiation levels by introducing a greater loop area. |
| 2.15 | Route DP/DM signals with at least 25 mils (~0.65 mm) away from any plane splits. |
| 2.16 | Follow the 20*h thumb rule by keeping traces at least 20*(height above the plane) away from the edge of the plane (VCC or GND, depending on the plane the trace is over). |
| 2.17 | Changing signal layers is preferable to crossing plane splits if a choice must be made. |
| 2.18 | If crossing a plane split is completely unavoidable, proper placement of stitching capacitors can minimize the adverse effects on EMI and signal quality performance caused by crossing the split. |
| 2.19 | Avoid anti-etch on the ground plane. |

### ULPI Interface (ULPIDATA<7:0>, ULPICLK, ULPINXT, ULPIDIR, ULPISTP)

| Item | Recommendation |
|------|---------------|
| 3.00 | Route ULPI 12-pin bus as a 50 ohm single-ended adapted bus. |
| 3.01 | Route ULPI 12-pin bus with minimum trace lengths and a strict maximum of 90 mm, to ensure timing. (Timing budget 600 ps maximum 1-way delay assuming 66 ps/cm.) |
| 3.02 | Route ULPI 12-pin bus equalizing path lengths as much as possible to have equal delays. |
| 3.03 | Route ULPI 12-pin bus as clock signals and set a minimum spacing of 3 times the trace width (S < 3W). |
| 3.04 | If the 3W minimum spacing is not respected, the minimum spacing for clock signals based on EMI testing experience is 50 mils (1.27 mm). |
| 3.05 | Route ULPI 12-pin bus with a dedicated ground plane. |
| 3.06 | Place and route the ULPI monitoring buffers as close as possible from the device ULPI bus (on test boards). |

### USB Clock (USBCLKIN, CLK_IN1, CLK_IN0)

| Item | Recommendation |
|------|---------------|
| 4.00 | Route the USB clock with the minimum possible trace length. |
| 4.01 | Keep the maximum possible distance between the USB clock and the other platform clocks, power sources, and digital and analog signals. |
| 4.02 | Route the USBCLKIN, CLK_IN1 and CLK_IN0 inputs as 50 ohm single-ended signals. |

### USB Power Supply (VBUS, REG3V3, REG1V5, VBAT)

| Item | Recommendation |
|------|---------------|
| 5.00 | VBUS must be a power plane from the device VBUS ball to the USB receptacle, or if a power plane is not possible, VBUS must be as large as possible. |
| 5.01 | Power signals must be wide to accommodate current level. |
