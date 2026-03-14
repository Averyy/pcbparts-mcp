---
source: "TI SLVA652A -- Basics of Load Switches"
url: "https://www.ti.com/lit/an/slva652a/slva652a.pdf"
format: "PDF 14pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 18110
---

# Basics of Load Switches

Benjamin Mak, Texas Instruments -- Drivers and Load Switches

## Abstract

Integrated load switches are electronic switches that can be used to turn on and turn off power supply rails in systems, similar to a relay or a discrete FET. Load switches offer many other benefits to the system some including protection features that are often difficult to implement with discrete components. There are many different applications where load switches are implemented including, but not limited to:

- Power Distribution
- Power Sequencing and Power State Transition
- Reduced Leakage Current in Standby Mode
- Inrush Current Control
- Controlled Power Down

This application note will provide the fundamental basics of what load switches are, when they should be used, and how they can be implemented in a system.

## 1. What Are Load Switches?

Integrated load switches are integrated electronic switches used to turn on and turn off power rails. Basic load switches consist of four pins: input voltage, output voltage, enable and ground. When the device is enabled via the ON pin, the pass FET turns on, thereby allowing current to flow from the input pin to the output pin, and power is passed to the downstream circuitry.

### 1.1 General Load Switch Block Diagram

An understanding of what the architecture of a load switch looks like will be helpful in determining the specifications of a load switch. A basic load switch is made up of five basic blocks. Additional blocks can be included to add functionality to the load switch.

Key blocks:

1. **Pass FET** -- the main component of the load switch, which determines the maximum input voltage and maximum load current the load switch can handle. The on-resistance of the load switch is a characteristic of the pass FET and will be used in calculating the power dissipated by the load switch. The pass FET can be either an N-channel or P-channel FET, which will determine the architecture of the load switch.

2. **Gate Driver** -- charges and discharges the gate of the FET in a controlled manner, thereby controlling the rise time of the device.

3. **Control Logic** -- driven by an external logic signal. It controls the turn-on and turn-off of the pass FET and other blocks, such as quick output discharge, the charge pump, and blocks with protection features. This external logic signal is commonly connected directly to an external microcontroller.

4. **Charge Pump** -- not included in all load switches. This is used in load switches with an N-channel FET, since a positive differential voltage between the gate and the source (VOUT) is needed in order to turn on the FET properly.

5. **Quick Output Discharge** -- an on-chip resistor from VOUT to GND that is turned on when the device is disabled via the ON pin. This will discharge the output node, preventing the output from floating. For the devices with quick output discharge, this feature is only present when VIN and VBIAS are within the operating range.

6. **Additional features** include, but are not limited to, thermal shutdown, current limiting, and reverse current protection.

### 1.2 Datasheet Parameters

Below is a list of common datasheet parameters and definitions for load switches:

- **Input voltage range (VIN)** -- the range of input voltages that the load switch can support.
- **Bias voltage range (VBIAS)** -- the range of bias voltages that the load switch can support. This may be required to power the internal blocks of the load switch, depending on the architecture.
- **Maximum continuous current (IMAX)** -- the maximum continuous DC current the load switch can support. System thermal performance plays a key role in determining the maximum continuous DC current in a system.
- **ON-state resistance (RON)** -- the resistance measured from the VIN pin to the VOUT pin, which takes into consideration the resistance of the packaging and the internal pass FET.
- **Quiescent Current (IQ)** -- the required amount of current to power the internal blocks of the device, measured as the current flowing into the VIN pin without any load on VOUT.
- **Shutdown Current (ISD)** -- the amount of current flowing into VIN when the device is disabled.
- **ON pin input leakage current (ION)** -- the amount of current flowing into the ON pin when the ON pin has a high voltage applied to it.
- **Pull-down resistance (RPD)** -- the value of the pull-down resistor from VOUT to GND when the device is disabled.

## 2. Why Do You Need Load Switches

### 2.1 Power Distribution

Many systems have limited control of sub-systems power distribution. Load switches can be used to turn on and off sub-systems of the same input voltage instead of using multiple DC/DC converters or LDOs. By using a load switch, power can be distributed across different loads with control for each individual load.

### 2.2 Power Sequencing and Power State Transition

In some systems, especially those with a processor, there is a strict power-up sequence that must be followed. By using a GPIO or I2C interface, load switches are a simple solution to implement power sequencing to meet the power-up requirements. Load switches can provide independent control of each power path to provide simplified point-of-load control for power sequencing.

### 2.3 Reduced Leakage Current

In many designs, there are sub-systems that are only used during certain modes of operation. Load switches can be used to limit the amount of leakage current and power consumption by turning off power to these sub-systems.

In some applications, the circuitry such as DC/DC converters, LDOs, and modules can be disabled and put into standby mode. However, the leakage current of these modules can be relatively high, even in the shutdown state. By placing a load switch before the load, the leakage can be reduced to significantly lower levels.

### 2.4 Inrush Current Control

When turning on a sub-system without any slew rate control, the input rail may sag because of the inrush current that can happen from quickly charging a load capacitor. This can be problematic as this rail may be supplying power to other sub-systems. Load switches solve this issue by controlling the rise time of the output voltage, thereby eliminating the sag on the input voltage. The inrush current is proportional to the load capacitance.

### 2.5 Controlled Power Down

When a DC/DC converter or LDO without quick output discharge turns off, the load voltage is left floating and power down timing is dictated by the load. This can cause unwanted activity as modules downstream are not powered down to a defined state.

Using a load switch with quick output discharge can mitigate these problems. The load will be powered down quickly in a controlled manner and will be reset to a known good state for the next power up. This will eliminate any floating voltages at the input of the load and ensure that the load remains in a defined power state at all times.

### 2.6 Protection Features

Certain applications may require fault protection features to be integrated into the load switch. Some load switches include integrated features such as:

- **Reverse current protection** -- stops current from flowing from the VOUT pin to the VIN pin. In the absence of this feature, current may flow from the VOUT pin to the VIN pin if the voltage on VOUT is greater than VIN by a diode drop. There are many different methods of implementing reverse current protection. In some situations (e.g., TPS22916), the device monitors the voltage levels at the VIN pin and VOUT pin; when this differential voltage exceeds a certain threshold, the switch is disabled and the body diode is disengaged. Some devices (e.g., TPS22963C) only have reverse current protection when the device is disabled.

- **ON pin hysteresis** -- allows for more robust GPIO enable. With a voltage difference between a logic level high and logic level low on the ON pin, the control circuitry will operate as intended when there is noise on the GPIO line.

- **Current limiting** -- limits the amount of current the load switch will output, ensuring that there is not an excessive amount of current being pulled by external circuitry. In the current limited mode, the load switch works as a constant current until the switch current falls below the current limit.

- **Undervoltage lock-out (UVLO)** -- turns off the device if the VIN voltage drops below a threshold value, ensuring that the downstream circuitry is not damaged by being supplied by a voltage lower than intended.

- **Overtemperature protection** -- disables the switch if the temperature of the device exceeds a threshold temperature.

### 2.7 Lower BOM Count and PCB Area

Using an integrated load switch can lower the BOM count of a system. When a load switch is created discretely, there are many resistors, capacitors and transistors required to implement a gate driver, control logic, output discharge and protection features. With an integrated load switch, this is all accomplished with only a single device.

## 3. Part Selection and Design Considerations

### 3.1 NMOS vs PMOS

In an NMOS device, the pass FET is turned on by bringing the gate voltage above the source. Usually, the source voltage is at the same potential as the VIN terminal. In order to create this voltage differential between the gate and the source, a charge pump is required. Using a charge pump will increase the quiescent current of the device.

In a PMOS device, the pass FET is turned on by bringing the gate voltage below the source voltage. The architecture of a PMOS device does not require a charge pump, resulting in a lower quiescent current when compared to an NMOS device.

One major difference between a PMOS based architecture and NMOS based architecture is that PMOS based load switches do not perform well at lower voltages, while NMOS devices are good for lower VIN applications.

### 3.2 ON-State Resistance (RON)

ON-state resistance (RON) is a particularly important specification, as this determines the voltage drop across the load switch and power dissipation of the load switch. The larger the RON, the larger the voltage drop across the load switch will be and the higher the power dissipation.

### 3.3 Voltage (VIN) and Current (IMAX) Rating

One of the key considerations in selecting a load switch is the voltage and current required for the application. The load switch must be able to support the DC voltage and current that is expected during steady state operation, as well as the transient voltages and peak currents. Some load switches require a bias voltage to turn on the device and bias the internal circuitry, independent from the input voltage.

### 3.4 Shutdown Current (ISD) and Quiescent Current (IQ)

Quiescent current is the current that the load switch consumes when the load switch is ON. If the load currents are large enough, the power consumed due to quiescent current is negligible. Shutdown current determines the amount of power the load switch consumes when it is disabled via the ON pin.

### 3.5 Rise Time (tR)

Rise time varies from device to device. The rise time may need to be shorter or longer depending on the application. Inrush current is inversely proportional to rise time.

### 3.6 Quick Output Discharge (QOD)

Some load switches have an internal resistor that will pull the output to ground when the switch is turned off, preventing it from floating. For the quick output discharge feature to function, the voltage on the input voltage pins need within the operating range.

Load switches can offer the quick output discharge feature in either of these categories:
- **Fixed quick output discharge** -- devices with a fixed, internal resistor
- **Adjustable quick output discharge** -- devices such as TPS22918 have a dedicated pin that allows adjusting the discharge rate externally
- **No quick output discharge** at all

However, there are applications where quick output discharge would not be beneficial:
- If the output of the load switch was connected to a battery, quick output discharge would cause the battery to drain when the load switch is disabled.
- If two load switches are being used as a 2-input, 1-output multiplexer (where the outputs are tied together), the load switches cannot have quick output discharge.

### 3.7 Package Size

Integrated load switches come in all different shapes and sizes. In space constrained systems, it may be necessary to choose a smaller package size.

### 3.8 Input and Output Capacitance

In load switch applications, input capacitors should be placed to limit the amount of voltage drop on the input supply caused by the transient inrush currents into the discharged load capacitors. A 1 uF capacitor between VIN and GND placed near the VIN terminal (CIN) is highly recommended. Higher values of capacitance will reduce the voltage drop during high-current applications.

The total output capacitance (CL) between VOUT and GND may cause the voltage on VOUT to exceed the voltage on VIN when the supply is removed, which may result in current flow from VOUT to VIN through the body diode in the pass FET for devices without reverse current protection. It is recommended, but not required, to maintain a 10 to 1 ratio between the input capacitor and the load capacitance to prevent this.

## 4. Basic Calculations

### 4.1 Voltage Drop

To determine an appropriate device for an application, it is necessary to understand how much voltage drop across the load switch is acceptable:

    RON,max = dVmax / ILOAD

Where:
- dVmax = maximum voltage drop from VIN to VOUT
- ILOAD = load current
- RON,max = maximum on-resistance of the device for a given VIN

### 4.2 Inrush Current

To determine how much inrush current will be caused by the CL capacitor:

    IINRUSH = CL * (dVOUT / dt)

Where:
- IINRUSH = amount of inrush current caused by CL
- CL = total capacitance on VOUT
- dVOUT = change in voltage of VOUT when the device is enabled
- dt = the time it takes for VOUT voltage to change by dVOUT

It is important to ensure that the rise time of the load switch is chosen such that the device does not exceed the maximum specifications -- specifically IPLS -- upon startup as indicated in the datasheet. Some devices have a separate CT pin, which allows the rise time to be programmed with an external capacitor from the CT pin to GND.

### 4.3 Power Dissipation

The input voltage and load current is necessary to calculate the power dissipated in the load switch:

    PD = VIN * IQ + ILOAD^2 * RON

Where:
- VIN = input voltage
- IQ = quiescent current of the load switch
- ILOAD = load current of the load switch
- RON = ON-resistance of the load switch

For large load currents, it is possible to ignore the IQ of the device, since the product of VIN and IQ may be negligible when compared to the losses due to RON.

### 4.4 Thermal Considerations

The maximum IC junction temperature should be restricted to the maximum junction temperature as indicated on the absolute maximum table under normal operating conditions:

    PD(max) = (TJ(max) - TA) / theta_JA

Where:
- PD(max) = maximum allowable power dissipation
- TJ(max) = maximum allowable junction temperature
- TA = ambient temperature of the device
- theta_JA = junction to air thermal impedance (highly dependent upon board layout)

## 5. Design Examples

### 5.1 RON and Inrush Current Calculations

Example system specifications:

| Design Parameter | Example Value |
|-----------------|---------------|
| VIN | 5.0 V |
| ILOAD | 500 mA |
| Max IINRUSH | 1 A |
| dVMAX | 0.3 V |
| CL | 20 uF |
| PD | 150 mW |

**RON calculation:**

    RON,max = 0.3 V / 0.5 A = 600 mOhm

**Power-driven RON:**

    RON,max = dVmax^2 / PD = (0.3V)^2 / 150 mW = 600 mOhm

**Minimum rise time:**

    dt = (dVOUT * CL) / IINRUSH = (5 V * 20 uF) / 1 A = 100 us

### 5.2 Standby Power Savings

Some modules (LCD displays, power amplifiers, GPS modules, processors) can have several mA or more of leakage current in standby mode. Using a load switch can reduce this current to uA range.

Example: a 5 V rail with a downstream module that has 1 mA leakage current:
- Without load switch: 5 V x 1 mA = 5 mW
- With load switch: 5 V x 1 uA = 5 uW
- Power savings factor of 1000x

### 5.3 Power Sequencing without Processor Intervention

Load switches can be arranged such that there is power-up sequencing without any processor intervention. When the uC GPIO turns on the first load switch, it provides power to load 1. Once the voltage rail of load 1 has exceeded the VIH level of the second load switch, the second load switch will turn on. This can be expanded to allow for one GPIO line to sequence many load switches.

### 5.4 2-to-1 Power Mux

Two active-low load switches with reverse current protection can be configured to multiplex two supplies to one load. Active-low load switches are devices that turn on when the ON pin is pulled low. This configuration gives priority to Power Supply 1: whenever Power Supply 1 has a voltage applied, the load switch on the bottom gets disabled due to the resistor divider, while the load switch connected to Power Supply 1 is kept on with reverse current protection preventing current from flowing from VOUT to VIN.

## 6. Conclusion

Integrated load switches are an effective solution for achieving power sequencing, power distribution, controlled rise time, lower standby power, lower BOM count, and smaller PCB area.

## 7. References

1. Integrated Load Switches versus Discrete MOSFETs (SLVA716)
2. Managing Inrush Current (SLVUA74)
3. Load Switch Thermal Considerations (SLVUA74)
4. Quiescent Current vs Shutdown Current for Load Switch Power Consumption (SLVA757)
5. Reverse Current Protection in Load Switches (SLVA730)
6. Fundamentals of On-Resistance in Load Switches (SLVA771)
7. Timing of Load Switches (SLVA883)
8. Power Multiplexing Using Load Switches and eFuses (SLVA811)
