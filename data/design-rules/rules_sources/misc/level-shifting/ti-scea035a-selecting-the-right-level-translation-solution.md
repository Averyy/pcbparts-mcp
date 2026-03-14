---
source: "TI SCEA035A -- Selecting the Right Level-Translation Solution"
url: "https://www.ti.com/lit/pdf/scea035"
format: "PDF 23pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 13102
---
# Selecting the Right Level-Translation Solution

Texas Instruments SCEA035A (June 2004)

Author: Prasad Dhond, Standard Linear and Logic

## Abstract

Supply voltages continue to migrate to lower nodes to support low-power, high-performance applications. While some devices are capable of running at lower supply nodes, others might not. To have switching compatibility between these devices, the output of each driver must be compliant with the input of the receiver. There are several level-translation schemes to interface these devices. Depending on application needs, one approach might be more suitable than another. This application report gives an overview of the methods and products used to translate logic levels and lists the advantages and disadvantages of each level-translation solution.

## 1. Introduction

The need for voltage level translation is prevalent on most electronic systems today. For example, an ASIC operating with supply voltage VCCA must communicate with an I/O device operating at VCCB. A level-translation solution is needed between them.

Input-voltage thresholds and output-voltage levels of electronic devices vary, depending on the device technology and supply voltage. To interface two devices successfully:

1. The VOH of the driver must be greater than the VIH of the receiver.
2. The VOL of the driver must be less than the VIL of the receiver.
3. The output voltage from the driver must not exceed the I/O voltage tolerance of the receiver.

**Digital Switching Levels by Technology:**

| Technology | VIH | VIL | VOH | VOL |
|---|---|---|---|---|
| 5V CMOS | 0.7*VCC | 0.3*VCC | 4.44V | 0.5V |
| 5V TTL | 2.0V | 0.8V | 2.4V | 0.4V |
| 3.3V LVTTL | 2.0V | 0.8V | 2.4V | 0.4V |
| 2.5V CMOS | 0.65*VCC | 0.35*VCC | 2.0V | 0.7V |
| 1.8V CMOS | 0.65*VCC | 0.35*VCC | VCC-0.45V | 0.45V |
| 1.5V CMOS | 0.65*VCC | 0.35*VCC | VCC-0.45V | 0.45V |
| 1.2V CMOS | 0.65*VCC | 0.35*VCC | VCC-0.45V | 0.45V |

## 2. Dual-Supply Level Translators

### 2.1 Features

Dual-supply devices are designed for asynchronous communication between two buses or devices operating at different supply voltages. They use two supply voltages: VCCA to interface with the A side and VCCB to interface with the B side. For bidirectional level translators, data is transmitted from A to B or B to A depending on the logic level at the DIR input. On devices with an output enable (OE) control input, the A and B buses are effectively isolated when OE is inactive.

Dual-supply devices from TI are available in a variety of bit widths and cover nearly every supply-voltage node in use. They are flexible, easy to use, and can translate bidirectionally (up-translate and down-translate).

**Advantages of dual-supply devices:**
- Flexibility in translating to/from a variety of voltage nodes
- Active current drive capability
- Available in a variety of bit widths

### 2.2 Product Portfolio

**Key dual-supply device families:**

- **SN74LVC3245A / SN74LVC4245A**: 2.3-3.6V to 3-5.5V or 4.5-5.5V to 2.7-3.6V translation
- **SN74ALVC164245**: 2.3-3.6V to 3-5.5V translation, 16-bit
- **SN74AVCA164245 / SN74AVCB164245 / SN74AVCB324245**: 1.4-3.6V on both sides, supporting 1.5V/1.8V/2.5V/3.3V CMOS translations
- **SN74AVC1T45 through SN74AVC32T245**: 1.2-3.6V on both sides, 1- to 32-bit widths, supporting 1.2V through 3.3V CMOS
- **SN74LVC1T45 / SN74LVC2T25 / SN74LVC8T25 / SN74LVC16T25**: 1.65-5.5V on both sides, supporting 1.8V through 5V CMOS

TI naming convention for dual-supply translators: SN74 [family] [bit-width] T [function]. Example: SN74AVC8T245 = AVC family, 8-bit, translator, 245-type function. The "T" indicates a translator device. Control circuitry is powered by VCCA unless otherwise stated.

## 3. Open-Drain Devices

Devices with open-drain outputs have an N-channel transistor between the output and GND. They can be used in level-translation applications where the output voltage is determined by the pullup supply VCCB. VCCB can be greater (up-translation) or lower (down-translation) than the input high-level voltage.

When the output N-channel transistor is on, there is constant current flow from VCCB to GND through the pullup resistor and transistor, contributing to higher system power consumption. Using a higher-value pullup resistor minimizes current flow but slows the rise time due to higher RC time constant.

**Advantages of open-drain devices:**
- Can be used to up-translate and down-translate to/from a variety of voltage nodes
- Can be used in a wired-OR interface

### 3.1 Application Example: SN74LVC2G07

Using one buffer of the SN74LVC2G07 to translate up from 1.8V to 5V and the other to translate down from 3.3V to 1.8V (VCC = 1.8V):

Minimum pullup resistor value is restricted by the maximum current-sinking capability (IOL max) of the open-drain device; maximum value is limited by maximum allowable rise time:

    RPU(min) = (VPU - VOL) / IOL(max)

For the 1.8V to 5V translation (VPU1 = 5V +/- 0.5V, 5% resistors):

    RPU1(min) = (5.5V - 0.45V) / (4 mA * 0.95) = 1.33 kOhm -> use 1.5 kOhm

For the 3.3V to 1.8V translation (VPU2 = 1.8V +/- 0.15V):

    RPU2(min) = (1.8V - 0.45V) / (4 mA * 0.95) = 395 Ohm -> use 430 Ohm

As the pullup resistor value increases, the rise time of the output signal increases.

### 3.2 Do Not Use Pullup Resistors at Outputs of CMOS Drivers

System designers should NOT use a pullup resistor at the output of a device with CMOS (push-pull) outputs. When the output is high, the upper P-channel transistor is on, creating a backflow of current from the high supply to the low supply through the resistor and P-channel transistor. This current flow into the low supply could cause undesirable effects.

## 4. FET Switches

Bus switches from TI CB3T, CBT, CBTD, and TVC families can be used in level-translation applications. FET switches are ideal where active current drive is not required or where very fast propagation delays are desired.

**Advantages of FET switches:**
- Fast propagation delays
- TVC devices (or CBT configured as TVC) can be used for bidirectional level translation without direction control

### CB3T Devices

CB3T devices can be used for down-translation from 5V to 3.3V (VCC = 3.3V), from 5V or 3.3V to 2.5V (VCC = 2.5V). When channeling a signal from the 5V bus to the 3V bus, the CB3T clamps the output to VCC (3V). When channeling from the 3V bus to the 5V bus, the output is clamped to about 2.8V, which is a valid VIH level for a 5V TTL device.

Drawbacks:
1. The 2.8V VOH poses a reduced high-level noise margin on the 5V side (2.8V - 2.0V = 800 mV)
2. The 5V receiver exhibits excess power consumption (delta-ICC current) because the high output is not driven to the VCC rail

Note: 2.8V VOH is with VCC = 3V, TA = 25 deg C, IO = 1 uA. This would NOT be a valid VIH level for a 5V CMOS receiver; therefore CB3T devices cannot be used to up-translate from 3V to 5V CMOS (without a pullup resistor).

### 4.1 CBT and CBTD Devices

CBT and CBTD families can interface 5V systems with 3.3V systems. They can only be used to down-translate when interfacing 5V CMOS with 3.3V. They can be used for bidirectional translation when interfacing 5V TTL with 3.3V.

For the SN74CBT1G384, an external diode must be connected between the 5V supply and VCC pin, dropping the gate voltage to 4.3V. An additional VGS drop of 1V results in 3.3V on the output pin. Additional diodes can limit output to even lower voltages. The propagation delay from input to output is very minimal.

CBT devices can also be configured like TVC devices for flexible bidirectional translation without direction control (see TI application report SCDA006).

### 4.2 Translation Voltage Clamp (TVC) Devices

TVC devices are used for bidirectional level translation without a direction control signal. Each TVC device consists of an array of N-channel pass transistors with their gates tied together internally.

One FET is connected as a reference transistor, and the others are used as pass transistors. The most positive voltage on the low-voltage side of each pass transistor is limited to a voltage set by the reference transistor. The transistors are fabricated symmetrically, and I/O signals are bidirectional through each FET.

The drain of the reference transistor must be connected to VDDREF through a resistor, and VREF must be <= (VBIAS - 1) to bias the reference transistor into conduction. The gate of the reference transistor is tied to its drain to saturate the transistor.

When down-translating from B to A side, the voltage on A is clamped at VREF. When up-translating from A to B, as the voltage on A approaches VREF, the pass transistor switches off and the B side is pulled up through the pullup resistor.

**Possible TVC voltage-translation combinations include:**

- 5V CMOS to/from: 3.3V, 2.5V, 1.8V, 1.5V, 1.2V, 0.8V CMOS
- 3.3V to/from: 2.5V, 1.8V, 1.5V, 1.2V, 0.8V CMOS
- 2.5V to/from: 1.8V, 1.5V, 1.2V, 0.8V CMOS
- 1.8V to/from: 1.5V, 1.2V, 0.8V CMOS
- And all intermediate combinations

## 5. Overvoltage-Tolerant Devices

Devices with overvoltage-tolerant inputs can tolerate input voltages greater than the device supply voltage. This is made possible by eliminating the input clamp diode to VCC and using thicker gate oxides. These devices perform down-translation.

**How to identify overvoltage-tolerant inputs:**
- Look at the VI parameter: max VI is independent of VCC and specified as a definite number (e.g., 5.5V)
- Look at the IIK parameter under absolute maximum ratings: only a minus sign (e.g., -20 mA instead of +/-20 mA), indicating only a GND clamp diode is present

Devices from the AUC, LVC, LV-A, and AHC families have overvoltage-tolerant inputs. For transceiver functions, I/Os are overvoltage-tolerant only if the device has the IOFF feature. Note: AHC family does NOT have the IOFF feature.

**Caution:** When using overvoltage-tolerant devices for level translation with slow input edges, the duty cycle of the output signal might be affected. The device switches at VCC threshold levels, so a 0-5V input signal with slow edges through a 3.3V device could result in a shifted output duty cycle (e.g., 50% input to 60% output). Therefore, overvoltage-tolerant devices might not be ideal where output duty cycle is critical (e.g., clock applications).

**Advantages:**
- Only one supply voltage needed
- Broad portfolio of AHC, AUC, AVC, LV-A, and LVC devices

## 6. Devices with TTL-Compatible Inputs

Devices from the HCT, AHCT, ACT, ABT, and FCT families accept TTL-level input signals and output 5V CMOS signals. Because 5V TTL and 3V LVTTL/LVCMOS switching thresholds are equal, these devices can translate from 3.3V to 5V.

However, because the input high signals are not driven to the 5V rail, the input stages draw extra static current called delta-ICC current. For example, the SN74HCT541 draws approximately 290 uA per input with a static 3.3V input signal.

**Advantages:**
- Only one supply voltage needed
- Broad portfolio of HCT, AHCT, ACT, ABT, and FCT devices

## 7. Summary of Translation Solutions

**Dual-supply devices:** Best choice for most applications. Bidirectional translation between a variety of voltage nodes. Low power, fast propagation delays, active current drive.

**Open-drain devices:** Flexible up-translate or down-translate with external pullup resistor. Not power efficient.

**Overvoltage-tolerant devices:** Good option for down-translation. Potential duty cycle shift with slow input edges.

**CB3T devices:** Ideal for 5V-to-2.5V, 5V-to-3.3V, and 3.3V-to-2.5V down-translation. Sub-1ns propagation delays, very low power. No drive current -- use dual-supply translator if buffering is needed.

**CBT/CBTD devices:** 5V to 3.3V down-translation (CBT with external diode or CBTD). Fast propagation, low power. No current drive.

**TVC devices:** Bidirectional level translation without direction control. Requires external pullup resistors. A CBT device can also be configured as a TVC device.

**Devices with TTL-compatible inputs:** HCT/AHCT/ACT/ABT/FCT families for 3.3V to 5V up-translation. Causes excess system power consumption (delta-ICC).

## 8. Conclusion

There are several ways to achieve logic-level translation, and each approach has its own merits and demerits. Dual-supply level translators are usually the best option for most applications. TI offers a broad portfolio of dual-supply level translators. In situations where these are not optimal, other solutions should be considered: open-drain devices for up/down translation where power is not a concern; bus switches and overvoltage-tolerant devices for down-translation; devices with TTL-compatible inputs for 3.3V to 5V up-translation if increased power is acceptable.

## References

1. Thomas V. McCaughey, Stephen M. Nolan, and John D. Pietrzak, "Flexible Voltage-Level Translation With CBT Family Devices," TI literature number SCDA006.
