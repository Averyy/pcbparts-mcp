---
source: "TI SLVAF84 -- Delay and Dead Time in Integrated MOSFET Drivers"
url: "https://www.ti.com/document-viewer/lit/html/SLVAF84"
format: "HTML"
method: "ti-html"
extracted: 2026-02-16
chars: 12994
---

# 1 Introduction

For integrated MOSFET drivers, data sheets define propagation delay as the time it takes for changing input logic edges INHx and INLx (whichever changes first if MCU dead time is added) to change the half-bridge output voltage (OUTx) as [Figure 1-1](#GUID-1536E919-AD5D-41C9-964F-96D9D85DFFEB) shows. It includes an input deglitch delay, an analog driver, and a comparator delay resulting in a propagation delay time (tpd). The analog drivers insert automatic internal dead time (tdead) to avoid cross conduction of MOSFETs and shoot-through currents.

Figure 1-1 Propagation Delay Timing in Integrated MOSFET Drivers

However, propagation delay and dead time can change based on many factors:

* Direction of current into or out of the phase
* Additional dead time from the MCU PWM inputs
* Delay Compensation to minimize duty cycle distortion

This application note investigates how each factor affects driver delay and dead time in integrated MOSFET drivers.

# 2 Direction of Current Into or Out of the Phase

When commutating with sinusoidal control, all three half-bridges are switching using synchronous PWM inputs with varying duty cycles and 120 degrees out of phase from each other. This results in smooth sinusoidal phase current ([Figure 2-1](#GUID-A0475690-1D00-4922-A801-B23CBCABC929)), which means that the current direction of each phase is going into or out of the motor output pins (OUTx) of each phase. Depending on the direction of the current, the propagation delay can vary depending on whether the high- and low-side inputs (INHx and INLx) of the phase are rising or falling and the direction of current at that instant in time.

Figure 2-1 Sinusoidal Current Control Waveforms

This application report describes four scenarios of synchronous inputs switching, direction of current from OUTx, and how they can affect propagation delay and dead time using the DRV8316 integrated MOSFET BLDC motor driver. An assumption is made that there is no additional MCU dead time and INHx and INLx are synchronous PWM inputs. Furthermore, a fixed output slew rate of 200 V/µs is assumed and the propagation delay and dead time to the values mentioned in the data sheet in [Figure 2-2](#GUID-932E94D5-3D37-45FA-B795-9A8474C74DD8) is compared.

Figure 2-2 DRV8316 Dead Time and Propagation Delay Specifications for 200 V/μs Slew Rate

## 2.1 INHx Rising, INLx Falling, Current is Going Out of the Phase

When current is going out of the
phase, propagation delay and driver dead time is determined by whether INHx is
rising or falling.

In [Figure 2-3](#GUID-65F56A05-8CF3-46AF-B15E-D1B3574FF686), when INLx goes low (green), current is momentarily pulled through the body diode
(purple) of the low-side (LS) FET to continue sourcing current out of OUTx (red).
The duration the body diode of the LS FET conducts is the dead time. When the body
diode stops conducting (dead time is over), the high-side (HS) FET begins to conduct
(blue).

Figure 2-3 Current Switching With INHx
Rising, INLx Falling, and Current Out of OUTx

Note how the current direction
is opposite internally between the body diode of the LS FET and the conduction path
of the HS FET. To reduce a large change of current, the device waits until the LS
body diode fully conducts and then turns on the HS FET, which lengthens propagation
delay to the typical or maximum value as specified in the data sheet.

The example
waveform in [Figure 2-4](#GUID-8BB64F30-7822-4DC6-B3CD-A0EE74CCCA9F) shows INHx
rising and INLx falling and current is going out of the phase (positive current in
green) for the DRV8316 with a slew rate of 200 V/µs and sinusoidal commutation. The
dead time and propagation delay typical values in the DRV8316 data sheet
specifications are 500 ns and 700 ns, respectively, with maximums included as well.
Note how internal dead time is included into the propagation delay.

Figure 2-4 Waveforms of Dead Time and
Propagation Delay When INHx is Rising, INLx is Falling, and Current Flows Out of
OUTx

## 2.2 INHx Falling, INLx Rising, Current is Going Out of the Phase

In [Figure 2-5](#GUID-92EF4A8D-0655-4752-B836-CBA921245AFD), when INHx goes low (green), current is again momentarily pulled through the body
diode (purple) of the LS FET to continue sourcing current out of OUTx (red). After a
short body diode conduction period, the LS FET begins to conduct (blue).

Figure 2-5 Current Switching With INHx
Falling, INLx Rising, and Current Out of OUTx

Note how the current direction is the
same internally between the body diode of the LS FET and the conduction path of the
LS FET. The device can turn on the LS FET instead of allowing the body diode to
fully conduct because the current direction is the same. This results in a shortened
propagation delay and dead time.

The example waveform in [Figure 2-6](#GUID-E76909CB-453A-4BB1-A9AB-DB8221295B52) shows INHx falling and INLx rising and current is going out of the phase
(positive current in green) for the DRV8316 with a slew rate of 200 V/µs and
sinusoidal commutation. The dead time and propagation delay minimum values in the
DRV8316 data sheet specifications are not specified because of this condition due to
the internal VGS handshaking feature of the device to avoid any shoot-through
conditions.

Figure 2-6 Waveforms of Dead Time and
Propagation Delay When INHx is Falling, INLx is Rising, and Current Flows Out of
OUTx

## 2.3 INHx Rising, INLx Falling, Current is Going Into the Phase

When current is going into the phase, propagation delay and driver dead time is determined by whether INLx is rising or falling.

In [Figure 2-7](#GUID-E8A9987B-291E-4682-9AC6-E295A06FD429), when INLx goes low (green), current is momentarily pulled through the body diode (purple) of the HS FET to continue sinking current into OUTx (red). After a short body diode conduction period, the HS FET begins to conduct (blue).

Figure 2-7 Current Switching With INHx Rising, INLx Falling, and Current Into OUTx

Note how the current direction is the same internally between the body diode of the HS FET and the conduction path of the HS FET. The device can turn on the HS FET instead of allowing the body diode to fully conduct because the current direction is the same. This results in a shortened propagation delay and dead time.

The example waveform in [Figure 2-8](#GUID-58A5FDE3-91E4-435F-8D2F-029F7930ABBE) shows INHx rising and INLx falling and current is going into the phase (positive current in green) for the DRV8316 with a slew rate of 200 V/µs and sinusoidal commutation. The dead time and propagation delay minimum values in the DRV8316 data sheet specifications are not specified because of this condition, where propagation and dead times can be much shorter than specified due to the internal VGS handshaking feature of the device to avoid any shoot-through conditions.

Figure 2-8 Waveforms of Dead Time and Propagation Delay When INHx is Rising, INLx is Falling, and Current Flows Into OUTx

## 2.4 INHx Falling, INLx Rising, Current is Going Into the Phase

In [Figure 2-9](#GUID-E467AE9E-C39A-42D5-ADFB-51C00687D3F6), when INHx goes low (green), current is momentarily pulled through the body diode (purple) of the HS FET to continue sinking current into OUTx (red). The duration the body diode of the HS FET conducts is the dead time. When the body diode stops conducting (dead time is over), the LS FET begins to conduct (blue).

Figure 2-9 Current Switching With INHx Falling, INLx Rising, and Current Into OUTx

Note how the current direction is opposite internally between the body diode of the HS FET and the conduction path of the LS FET. To reduce a large change of current, the device waits until the HS body diode fully conducts and then turns on the LS FET, which lengthens propagation delay to the typical or maximum value as specified in the data sheet.

The example waveform in [Figure 2-10](#GUID-25E6A494-F6B9-48EA-B2D9-D0E3228311E0) shows INHx falling and INLx rising and current is going out of the phase (positive current in green) for the DRV8316 with a slew rate of 200 V/µs and sinusoidal commutation. The dead time and propagation delay typical values in the DRV8316 data sheet specifications are 500 ns and 700 ns, respectively, with maximums included as well. Note how internal dead time is included into the propagation delay.

Figure 2-10 Waveforms of Dead Time and Propagation Delay When INHx is Falling, INLx is Rising, and Current Flows Into OUTx

[Table 4-1](GUID-EEDA9506-C6A4-4A30-8067-512AAF5D6559.html#GUID-197B6E83-3D82-47CE-8FB1-D4738ACDB9DF) summarizes all of the findings from this section for sinusoidal current, synchronous input PWMs in reference to a generalized typical propagation delay time and dead time for a slew rate setting.

# 3 Additional Dead Time From the MCU PWM Inputs

Many gate drivers and integrated FET drivers in the DRV8x family integrate automatic dead time insertion to prevention cross-conduction and shoot-through of the half-bridge driver ([Figure 3-1](#GUID-9C5F34A9-8E9B-4E76-A6D6-D94CD60D456A)). This is accomplished via handshaking between the gate-to-source voltage of the high-side and low-side gate drivers, which is internal in integrated MOSFET drivers. Dead time is dependent on the slew rate setting of the device, and it is specified with typical and maximum values.

Figure 3-1 Definition of Dead Time in Integrated MOSFET Drivers

Some designers prefer to additionally include dead time from the PWM outputs of the microcontroller as an extra precaution for shoot-through protection. This creates a condition where internal logic prioritizes the MCU dead time or driver dead time based on their durations.

Typically, if the MCU dead time is less than the driver dead time, the driver will compensate and make the true output dead time the value specified by the DRV device. Conversely, if the MCU dead time is larger than the driver dead time, then the driver will adjust accordingly to the MCU dead time as shown in [Table 4-1](GUID-EEDA9506-C6A4-4A30-8067-512AAF5D6559.html#GUID-197B6E83-3D82-47CE-8FB1-D4738ACDB9DF).

# 4 Summary of Delay Times in Integrated MOSFET Drivers

Table 4-1 Summary of Delay Times in
Integrated MOSFET Drivers Depending on Inputs, Inserted MCU Dead Time, and
Output Current Direction

| OUTx Current Direction | INHx | INLx | Propagation Delay (tPD) | Dead Time (tdead) | Inserted MCU Dead Time (tdead(MCU)) | |
| --- | --- | --- | --- | --- | --- | --- |
| tdead(MCU) < tdead | tdead(MCU) > tdead |
| **Out of OUTx** | Rising | Falling | Typical | Typical | Output dead time = tdead | Output dead time = tdead(MCU) |
| Falling | Rising | Smaller than typical | Smaller than typical | Output dead time < tdead | Output dead time < tdead(MCU) |
| **Into OUTx** | Rising | Falling | Smaller than typical | Smaller than typical | Output dead time < tdead | Output dead time < tdead(MCU) |
| Falling | Rising | Typical | Typical | Output dead time = tdead | Output dead time = tdead(MCU) |

# 5 Delay Compensation to Minimize Duty Cycle Distortion

Differences in delays in dead time and propagation delay can cause mismatches in output timings of PWMs, which can lead to duty cycle distortion. To accommodate differences in propagation delay between the conditions mentioned previously in this application note, some devices in the DRV831x and MCx831x families integrate a Delay Compensation feature.

Figure 5-1 Delay Compensation With Current Flowing Out of the Phase

Figure 5-2 Delay Compensation With Current Flowing Into the Phase

Delay Compensation is used to match delay times for currents going into and out of phase by adding variable delay time (tvar) to match a preset target delay time. This delay time is configurable in SPI devices, and it is recommended in the data sheets to choose a target delay time that is equal to the propagation delay time plus driver dead time (tpd + tdead).

In the following example, observe that the DRV8316 again uses a fixed slew rate of 200 V/μs and synchronous PWM inputs. Compare the propagation delays of [Figure 5-3](#GUID-82C1E43C-19FB-4BB1-94D6-06DB5FEC4E70) without and with Delay Compensation.

Figure 5-3 Comparison of DRV8316 Output Waveforms With and Without 1.5 μs of Delay Compensation

In the top two waveforms in [Figure 5-3](#GUID-82C1E43C-19FB-4BB1-94D6-06DB5FEC4E70), Delay Compensation is disabled and results in a mismatch of propagation delays and dead time due to the direction of the current at the OUTx pin, causing output duty cycle distortion.

In the bottom waveform in [Figure 5-3](#GUID-82C1E43C-19FB-4BB1-94D6-06DB5FEC4E70), Delay Compensation is enabled and the delay target time is set to DLY\_TARGET = 1.5 μs, resulting in matching propagation delays and a reduction of output duty-cycle distortion.