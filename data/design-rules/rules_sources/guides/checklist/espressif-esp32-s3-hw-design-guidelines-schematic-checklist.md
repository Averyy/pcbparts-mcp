---
source: "Espressif ESP32-S3 HW Design Guidelines -- Schematic Checklist"
url: "https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html"
format: "HTML"
method: "readability"
extracted: 2026-02-16
chars: 30656
---

# Schematic Checklist

## Overview

The integrated circuitry of ESP32-S3 requires only 20 electrical components (resistors, capacitors, and inductors) and a crystal, as well as an SPI flash. The high integration of ESP32-S3 allows for simple peripheral circuit design. This chapter details the schematic design of ESP32-S3.

The following figure shows a reference schematic design of ESP32-S3. It can be used as the basis of your schematic design.

ESP32-S3 Reference Schematic

Note that Figure [ESP32-S3 Reference Schematic](#fig-chip-core-schematic) shows the connection for 3.3 V, quad, off-package SPI flash/PSRAM.

* In cases where 1.8 V or 3.3 V, octal, in-package or off-package SPI flash/PSRAM is used, GPIO33 ~ GPIO37 are occupied and cannot be used for other functions.
* If an in-package SPI flash/PSRAM is used and VDD\_SPI is configured to 1.8 V or 3.3 V via the VDD\_SPI\_FORCE eFuse, the GPIO45 strapping pin no longer affects the VDD\_SPI voltage. In these cases, the presence of R1 is optional. For all other cases, refer to [ESP32-S3 Chip Series Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf#cd-pins-strap-vdd-spi) > Section *VDD\_SPI Voltage Control* > Table *VDD\_SPI Voltage Control* to determine whether R1 should be populated or not.
* The connection for 1.8 V, octal, off-package flash/PSRAM is as shown in Figure [ESP32-S3 Schematic for Off-Package 1.8 V Octal Flash/PSRAM](#fig-esp32-s3-core-sch-external-1v8-spi8).
* When only in-package flash/PSRAM is used, there is no need to populate the resistor on the SPI traces or to care the SPI traces.

ESP32-S3 Schematic for Off-Package 1.8 V Octal Flash/PSRAM

Any basic ESP32-S3 circuit design may be broken down into the following major building blocks:

The rest of this chapter details the specifics of circuit design for each of these sections.

## Power Supply

The general recommendations for power supply design are:

* When using a single power supply, the recommended power supply voltage is 3.3 V and the output current is no less than 500 mA.
* It is suggested to add an ESD protection diode and at least 10 μF capacitor at the power entrance.

The power scheme is shown in Figure [ESP32-S3 Power Scheme](#fig-chip-power-scheme).

ESP32-S3 Power Scheme

More information about power supply pins can be found in [ESP32-S3 Series Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf#cd-pwr-supply) > Section *Power Supply*.

### Digital Power Supply

ESP32-S3 has pin46 VDD3P3\_CPU as the digital power supply pin, and pin 20 VDD3P3\_RTC as the RTC and partial digital power supply pin, with an operating voltage range of 3.0 V ~ 3.6 V. It is recommended to add a 0.1 μF capacitor close to the digital power supply pins in the circuit.

Pin VDD\_SPI serves as the power supply for the external device at either 1.8 V or 3.3 V (default). It is recommended to add extra 0.1 μF and 1 μF decoupling capacitors close to VDD\_SPI. Please do not add excessively large capacitors.

* When VDD\_SPI operates at 1.8 V, it is powered by ESP32-S3’s internal LDO. The typical current this LDO can offer is 40 mA.
* When VDD\_SPI operates at 3.3 V, it is driven directly by VDD3P3\_RTC through a 14 Ω resistor, therefore, there will be some voltage drop from VDD3P3\_RTC.

Attention

* When using VDDVDD\_SPI\_SPI as the power supply pin for in-package or off-package 3.3 V flash/PSRAM, please ensure that VDD3P3\_RTC remains above 3.0 V to meet the operating voltage requirements of the flash/PSRAM, considering the voltage drop mentioned earlier.
* Note that VDD3P3\_RTC cannot supply power alone; all power supplies must be powered on at the same time.

Depending on the value of EFUSE\_VDD\_SPI\_FORCE, the VDD\_SPI voltage can be controlled in two ways, as Table [VDD\_SPI Voltage Control](#tab-vdd-spi-voltage-control) shows.

VDD\_SPI Voltage Control

| EFUSE\_VDD\_SPI\_FORCE | GPIO45 | EFUSE\_VDD\_SPI\_TIEH | Voltage | VDD\_SPI Power Source |
| --- | --- | --- | --- | --- |
| 0 | 0 | Ignored | 3.3 V | VDD3P3\_RTC via RSPI (default) |
| 0 | 1 | Ignored | 1.8 V | Flash Voltage Regulator |
| 1 | Ignored | 0 | 1.8 V | Flash Voltage Regulator |
| 1 | Ignored | 1 | 3.3 V | VDD3P3\_RTC via RSPI |

VDD\_SPI can also be driven by an external power supply.

It is recommended to use the VDD\_SPI output to supply power to external or internal flash/PSRAM.

### Analog Power Supply

ESP32-S3’s VDD3P3 pins (pin2 and pin3) and VDDA pins (pin55 and pin56) are the analog power supply pins, working at 3.0 V ~ 3.6 V.

For VDD3P3, when ESP32-S3 is transmitting signals, there may be a sudden increase in the current draw, causing power rail collapse. Therefore, it is highly recommended to add a 10 μF capacitor to the power rail, which can work in conjunction with the 1 μF capacitor(s) or other capacitors.

It is suggested to add an extra 10 μF capacitor at the power entrance. If the power entrance is close to VDD3P3, then two 10 μF capacitors can be merged into one.

Add an LC circuit to the VDD3P3 power rail to suppress high-frequency harmonics. The inductor’s rated current is preferably 500 mA and above.

For the remaining capacitor circuits, please refer to [ESP32-S3 Reference Schematic](#fig-chip-core-schematic).

## Chip Power-up and Reset Timing

ESP32-S3’s CHIP\_PU pin can enable the chip when it is high and reset the chip when it is low.

When ESP32-S3 uses a 3.3 V system power supply, the power rails need some time to stabilize before CHIP\_PU is pulled up and the chip is enabled. Therefore, CHIP\_PU needs to be asserted high after the 3.3 V rails have been brought up.

To reset the chip, keep the reset voltage VIL\_nRST in the range of (–0.3 ~ 0.25 × VDD3P3\_RTC) V. To avoid reboots caused by external interferences, make the CHIP\_PU trace as short as possible.

Figure [ESP32-S3 Power-up and Reset Timing](#fig-chip-timing) shows the power-up and reset timing of ESP32-S3.

ESP32-S3 Power-up and Reset Timing

Table [Description of Timing Parameters for Power-up and Reset](#tab-chip-timing) provides the specific timing requirements.

Description of Timing Parameters for Power-up and Reset

| Parameter | Description | Minimum (µs) |
| --- | --- | --- |
| tSTBL | Time reserved for the power rails to stabilize before the CHIP\_PU pin is pulled high to activate the chip | 50 |
| tRST | Time reserved for CHIP\_PU to stay below VIL\_nRST to reset the chip | 50 |

Attention

* CHIP\_PU must not be left floating.
* To ensure the correct power-up and reset timing, it is advised to add an RC delay circuit at the CHIP\_PU pin. The recommended setting for the RC delay circuit is usually R = 10 kΩ and C = 1 μF. However, specific parameters should be adjusted based on the characteristics of the actual power supply and the power-up and reset timing of the chip.
* If the user application has one of the following scenarios:

  > + Slow power rise or fall, such as during battery charging.
  > + Frequent power on/off operations.
  > + Unstable power supply, such as in photovoltaic power generation.

  Then, the RC circuit itself may not meet the timing requirements, resulting in the chip being unable to boot correctly. In this case, additional designs need to be added, such as:

  > + Adding an external reset chip or a watchdog chip, typically with a threshold of around 3.0 V.
  > + Implementing reset functionality through a button or the main controller.

## Flash and PSRAM

ESP32-S3 requires in-package or off-package flash to store application firmware and data. In-package PSRAM or off-package PSRAM is optional.

### In-Package Flash and PSRAM

The tables list the pin-to-pin mapping between the chip and in-package flash/PSRAM. Please note that the following chip pins can connect at most one flash and one PSRAM. That is to say, when there is only flash in the package, the pin occupied by flash can only connect PSRAM and cannot be used for other functions; when there is only PSRAM, the pin occupied by PSRAM can only connect flash; when there are both flash and PSRAM, the pin occupied cannot connect any more flash or PSRAM.

Pin-to-Pin Mapping Between Chip and In-Package Quad SPI Flash

| ESP32-S3FN8/ESP32-S3FH4R2 | In-Package Flash (Quad SPI) |
| --- | --- |
| SPICLK | CLK |
| SPICS0 | CS# |
| SPID | DI |
| SPIQ | DO |
| SPIWP | WP# |
| SPIHD | HOLD# |

Pin-to-Pin Mapping Between Chip and In-Package Quad SPI PSRAM

| ESP32-S3R2/ESP32-S3FH4R2 | In-Package PSRAM (2 MB, Quad SPI) |
| --- | --- |
| SPICLK | CLK |
| SPICS1 | CE# |
| SPID | SI/SIO0 |
| SPIQ | SO/SIO1 |
| SPIWP | SIO2 |
| SPIHD | SIO3 |

Pin-to-Pin Mapping Between Chip and In-Package Octal SPI PSRAM

| ESP32-S3R8/ESP32-S3R8V | In-Package PSRAM (8 MB, Octal SPI) |
| --- | --- |
| SPICLK | CLK |
| SPICS1 | CE# |
| SPID | DQ0 |
| SPIQ | DQ1 |
| SPIWP | DQ2 |
| SPIHD | DQ3 |
| GPIO33 | DQ4 |
| GPIO34 | DQ5 |
| GPIO35 | DQ6 |
| GPIO36 | DQ7 |
| GPIO37 | DQS/DM |

### Off-Package Flash and PSRAM

To reduce the risk of software compatibility issues, it is recommended to use flash and PSRAM models officially validated by Espressif. For detailed model selection, consult the sales or technical support team. If VDD\_SPI is used to supply power, make sure to select the appropriate off-package flash and RAM according to the power voltage on VDD\_SPI (1.8 V/3.3 V). It is recommended to add zero-ohm resistor footprints in series on the SPI communication lines. These footprints provide flexibility for future adjustments, such as tuning drive strength, mitigating RF interference, correcting signal timing, and reducing noise, if needed.

## Clock Source

ESP32-S3 supports two external clock sources:

### External Crystal Clock Source (Compulsory)

The ESP32-S3 firmware only supports 40 MHz crystal.

The circuit for the crystal is shown in Figure [ESP32-S3 Schematic for External Crystal](#fig-external-crystal-schematic). Note that the accuracy of the selected crystal should be within ±10 ppm.

ESP32-S3 Schematic for External Crystal

Please add a series component on the XTAL\_P clock trace. Initially, it is suggested to use an inductor of 24 nH to reduce the impact of high-frequency crystal harmonics on RF performance, and the value should be adjusted after an overall test.

The initial values of external capacitors C1 and C4 can be determined according to the formula:

\[C\_L = \frac{C1 \times C4} {C1+C4} + C\_{stray}\]

where the value of CL (load capacitance) can be found in the crystal’s datasheet, and the value of Cstray refers to the PCB’s stray capacitance. The values of C1 and C4 need to be further adjusted after an overall test as below:

1. Select TX tone mode using the [Certification and Test Tool](https://www.espressif.com/en/support/download/other-tools?keys=).
2. Observe the 2.4 GHz signal with a radio communication analyzer or a spectrum analyzer and demodulate it to obtain the actual frequency offset.
3. Adjust the frequency offset to be within ±10 ppm (recommended) by adjusting the external load capacitance.

> * When the center frequency offset is positive, it means that the equivalent load capacitance is small, and the external load capacitance needs to be increased.
> * When the center frequency offset is negative, it means the equivalent load capacitance is large, and the external load capacitance needs to be reduced.
> * External load capacitance at the two sides are usually equal, but in special cases, they may have slightly different values.

Note

* Defects in the manufacturing of crystal (for example, large frequency deviation of more than ±10 ppm, unstable performance within the operating temperature range, etc) may lead to the malfunction of ESP32-S3, resulting in a decrease of the RF performance.
* It is recommended that the amplitude of the crystal is greater than 500 mV.
* When Wi-Fi or Bluetooth connection fails, after ruling out software problems, you may follow the steps mentioned above to ensure that the frequency offset meets the requirements by adjusting capacitors at the two sides of the crystal.

### RTC Clock Source (Optional)

ESP32-S3 supports an external 32.768 kHz crystal to act as the RTC clock. The external RTC clock source enhances timing accuracy and consequently decreases average power consumption, without impacting functionality.

Figure [ESP32-S3 Schematic for 32.768 kHz Crystal](#fig-32khz-crystal-schematic) shows the schematic for the external 32.768 kHz crystal.

ESP32-S3 Schematic for 32.768 kHz Crystal

Please note the requirements for the 32.768 kHz crystal:

The parallel resistor R is used for biasing the crystal circuit (5 MΩ < R ≤ 10 MΩ).

In general, you do not need to populate the resistor.

If the RTC clock source is not required, then the pins for the 32.768 kHz crystal can be used as GPIOs.

## RF

### RF Circuit

ESP32-S3’s RF circuit is mainly composed of three parts, the RF traces on the PCB board, the chip matching circuit, the antenna and the antenna matching circuit. Each part should meet the following requirements:

* For the RF traces on the PCB board, 50 Ω impedance control is required.
* For the chip matching circuit, it must be placed close to the chip. A CLC structure is preferred.
* For the antenna and the antenna matching circuit, to ensure radiation performance, the antenna’s characteristic impedance must be around 50 Ω. Adding a CLC matching circuit near the antenna is recommended to adjust the antenna. However, if the available space is limited and the antenna impedance point can be guaranteed to be 50 Ω by simulation, then there is no need to add a matching circuit near the antenna.

ESP32-S3 Schematic for RF Matching

### RF Tuning

The RF matching parameters vary with the board, so the ones used in Espressif modules could not be applied directly. Follow the instructions below to do RF tuning.

Figure [ESP32-S3 RF Tuning Diagram](#fig-rf-tuning) shows the general process of RF tuning.

ESP32-S3 RF Tuning Diagram

In the matching circuit, define the port near the chip as Port 1 and the port near the antenna as Port 2. S11 describes the ratio of the signal power reflected back from Port 1 to the input signal power, the transmission performance is best if the matching impedance is conjugate to the chip impedance. S21 is used to describe the transmission loss of signal from Port 1 to Port 2. If S11 is close to the chip conjugate point 35+j0 and S21 is less than -35 dB at 4.8 GHz and 7.2 GHz, the matching circuit can satisfy transmission requirements.

Connect the two ends of the matching circuit to the network analyzer, and test its signal reflection parameter S11 and transmission parameter S21. Adjust the values of the components in the circuit until S11 and S21 meet the requirements. If your PCB design of the chip strictly follows the PCB design stated in Chapter [PCB Layout Design](pcb-layout-design.html#pcb-layout-design), you can refer to the value ranges in Table [Recommended Value Ranges for Components](#tab-recommended-value-ranges-components) to debug the matching circuit.

Recommended Value Ranges for Components

| Reference Designator | Recommended Value Range | Serial No. |
| --- | --- | --- |
| C11 | 1.2 ~ 1.8 pF | GRM0335C1H1RXBA01D |
| L2 | 2.4 ~ 3.0 nH | LQP03TN2NXB02D |
| C12 | 1.8 ~ 1.2 pF | GRM0335C1H1RXBA01D |

Please use 0201 packages for RF matching components and add a stub to the first capacitor in the matching circuit at the chip end.

Note

If RF function is not required, it is recommended not to initialize the RF stack in firmware. In this case, the RF pin can be left floating. However, if RF function is enabled, make sure an antenna is connected. Operation without an antenna may result in unstable behavior or potential damage to the RF circuit.

## UART

ESP32-S3 includes 3 UART interfaces, UART0, UART1, and UART2. U0TXD and U0RXD are GPIO43 and GPIO44 by default. Other UART signals can be mapped to any available GPIOs by software configurations.

Usually, UART0 is used as the serial port for download and log printing. For instructions on download over UART0, please refer to Section [Download Guidelines](download-guidelines.html#download-guidelines). It is recommended to connect a 499 Ω series resistor to the U0TXD line to suppress harmonics.

If possible, use other UART interfaces as serial ports for communication. For these interfaces, it is suggested to add a series resistor to the TX line to suppress harmonics.

## SPI

When using the SPI function, to improve EMC performance, add a series resistor (or ferrite bead) and a capacitor to ground on the SPI\_CLK trace. If space allows, it is recommended to also add a series resistor and capacitor to ground on other SPI traces. Ensure that the RC/LC components are placed close to the pins of the chip or module.

## Strapping Pins

At each startup or reset, a chip requires some initial configuration parameters, such as in which boot mode to load the chip, etc. These parameters are passed over via the strapping pins. After reset, the strapping pins work as normal function pins.

GPIO0, GPIO3, GPIO45, and GPIO46 are strapping pins.

All the information about strapping pins is covered in [ESP32-S3 Series Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf) > Chapter *Boot Configurations*.

For strapping pin information related to VDD\_SPI, please refer to Section [Digital Power Supply](#digital-power-supply).

In this section, we will mainly cover the strapping pins related to boot mode.

After chip reset is released, the combination of GPIO0 and GPIO46 controls the boot mode. See Table [Boot Mode Control](#tab-chip-boot-mode-control).

Boot Mode Control

| Boot Mode | GPIO0 | GPIO46 |
| --- | --- | --- |
| Default Config | 1 (Pull-up) | 0 (Pull-down) |
| SPI Boot (default) | 1 | Any value |
| Joint Download Boot 1 | 0 | 0 |

1 Joint Download Boot mode supports the following download methods:

> * USB Download Boot:
> * UART Download Boot

2 In addition to SPI Boot and Joint Download Boot modes, ESP32-S3 also supports SPI Download Boot mode. For details, please see [ESP32-S3 Technical Reference Manual](https://www.espressif.com/sites/default/files/documentation/esp32-s3_technical_reference_manual_en.pdf) > Chapter *Chip Boot Control*.

Signals applied to the strapping pins should have specific *setup time* and *hold time*. For more information, see Figure [Setup and Hold Times for Strapping Pins](#fig-shared-strap-pin-timing) and Table [Description of Timing Parameters for Strapping Pins](#tab-strap-pin-timing).

Setup and Hold Times for Strapping Pins

Description of Timing Parameters for Strapping Pins

| Parameter | Description | Minimum (ms) |
| --- | --- | --- |
| tSU | Time reserved for the power rails to stabilize before the chip enable pin (CHIP\_PU) is pulled high to activate the chip. | 0 |
| tH | Time reserved for the chip to read the strapping pin values after CHIP\_PU is already high and before these pins start operating as regular IO pins. | 3 |

Attention

* It is recommended to place a pull-up resistor at the GPIO0 pin.
* Do not add high-value capacitors at GPIO0, or the chip may enter download mode.

## GPIO

The pins of ESP32-S3 can be configured via IO MUX or GPIO matrix. IO MUX provides the default pin configurations (see [ESP32-S3 Series Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf#cd-append-consolid-pin-overview) > Appendix *ESP32-S3 Consolidated Pin Overview*), whereas the GPIO matrix is used to route signals from peripherals to GPIO pins. For more information about IO MUX and GPIO matrix, please refer to [ESP32-S3 Technical Reference Manual](https://www.espressif.com/sites/default/files/documentation/esp32-s3_technical_reference_manual_en.pdf) > Chapter *IO MUX and GPIO Matrix*.

Some peripheral signals have already been routed to certain GPIO pins, while some can be routed to any available GPIO pins. For details, please refer to [ESP32-S3 Series Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf) > Section *Peripherals*.

When using GPIOs, please:

* Pay attention to the states of strapping pins during power-up.
* Pay attention to the default configurations of the GPIOs after reset. The default configurations can be found in the table below. It is recommended to add a pull-up or pull-down resistor to pins in the high-impedance state or enable the pull-up and pull-down during software initialization to avoid extra power consumption.
* Avoid using the pins already occupied by flash/PSRAM.
* Some pins will have glitches during power-up. Refer to Table [Power-Up Glitches on Pins](#tab-glitches-on-pins) for details.
* When USB-OTG Download Boot mode is enabled, some pins will have level output. Refer to Table [IO Pad Status After Chip Initialization in the USB-OTG Download Boot Mode](#io-pad-status-after-chip-initialization-in-the-usb-otg-download-boot-mode) for details.
* SPICLK\_N, SPICLK\_P, and GPIO33 ~ GPIO37 work in the same power domain, so if octal 1.8 V flash/PSRAM is used, then SPICLK\_P and SPICLK\_N also work in the 1.8 V power domain.
* Only GPIOs in the VDD3P3\_RTC power domain can be controlled in Deep-sleep mode.

IO Pin Default Configuration

| No. | Name | Power | At Reset | After Reset |
| --- | --- | --- | --- | --- |
| 1 | LNA\_IN |  |  |  |
| 2 | VDD3P3 |  |  |  |
| 3 | VDD3P3 |  |  |  |
| 4 | CHIP\_PU | VDD3P3\_RTC |  |  |
| 5 | GPIO0 | VDD3P3\_RTC | IE, WPU | IE, WPU |
| 6 | GPIO1 | VDD3P3\_RTC | IE | IE |
| 7 | GPIO2 | VDD3P3\_RTC | IE | IE |
| 8 | GPIO3 | VDD3P3\_RTC | IE | IE |
| 9 | GPIO4 | VDD3P3\_RTC |  |  |
| 10 | GPIO5 | VDD3P3\_RTC |  |  |
| 11 | GPIO6 | VDD3P3\_RTC |  |  |
| 12 | GPIO7 | VDD3P3\_RTC |  |  |
| 13 | GPIO8 | VDD3P3\_RTC |  |  |
| 14 | GPIO9 | VDD3P3\_RTC |  | IE |
| 15 | GPIO10 | VDD3P3\_RTC |  | IE |
| 16 | GPIO11 | VDD3P3\_RTC |  | IE |
| 17 | GPIO12 | VDD3P3\_RTC |  | IE |
| 18 | GPIO13 | VDD3P3\_RTC |  | IE |
| 19 | GPIO14 | VDD3P3\_RTC |  | IE |
| 20 | VDD3P3\_RTC |  |  |  |
| 21 | XTAL\_32K\_P | VDD3P3\_RTC |  |  |
| 22 | XTAL\_32K\_N | VDD3P3\_RTC |  |  |
| 23 | GPIO17 | VDD3P3\_RTC |  | IE |
| 24 | GPIO18 | VDD3P3\_RTC |  | IE |
| 25 | GPIO19 | VDD3P3\_RTC |  |  |
| 26 | GPIO20 | VDD3P3\_RTC | USB\_PU | USB\_PU |
| 27 | GPIO21 | VDD3P3\_RTC |  |  |
| 28 | SPICS1 | VDD\_SPI | IE, WPU | IE, WPU |
| 29 | VDD\_SPI |  |  |  |
| 30 | SPIHD | VDD\_SPI | IE, WPU | IE, WPU |
| 31 | SPIWP | VDD\_SPI | IE, WPU | IE, WPU |
| 32 | SPICS0 | VDD\_SPI | IE, WPU | IE, WPU |
| 33 | SPICLK | VDD\_SPI | IE, WPU | IE, WPU |
| 34 | SPIQ | VDD\_SPI | IE, WPU | IE, WPU |
| 35 | SPID | VDD\_SPI | IE, WPU | IE, WPU |
| 36 | SPICLK\_N | VDD\_SPI / VDD3P3\_CPU | IE | IE |
| 37 | SPICLK\_P | VDD\_SPI / VDD3P3\_CPU | IE | IE |
| 38 | GPIO33 | VDD\_SPI / VDD3P3\_CPU |  | IE |
| 39 | GPIO34 | VDD\_SPI / VDD3P3\_CPU |  | IE |
| 40 | GPIO35 | VDD\_SPI / VDD3P3\_CPU |  | IE |
| 41 | GPIO36 | VDD\_SPI / VDD3P3\_CPU |  | IE |
| 42 | GPIO37 | VDD\_SPI / VDD3P3\_CPU |  | IE |
| 43 | GPIO38 | VDD3P3\_CPU |  | IE |
| 44 | MTCK | VDD3P3\_CPU |  | IE |
| 45 | MTDO | VDD3P3\_CPU |  | IE |
| 46 | VDD3P3\_CPU |  |  |  |
| 47 | MTDI | VDD3P3\_CPU |  | IE |
| 48 | MTMS | VDD3P3\_CPU |  | IE |
| 49 | U0TXD | VDD3P3\_CPU | IE, WPU | IE, WPU |
| 50 | U0RXD | VDD3P3\_CPU | IE, WPU | IE, WPU |
| 51 | GPIO45 | VDD3P3\_CPU | IE, WPD | IE, WPD |
| 52 | GPIO46 | VDD3P3\_CPU | IE, WPD | IE, WPD |
| 53 | XTAL\_N |  |  |  |
| 54 | XTAL\_P |  |  |  |
| 55 | VDDA |  |  |  |
| 56 | VDDA |  |  |  |
| 57 | GND |  |  |  |

* IE – input enabled
* WPU – internal weak pull-up resistor enabled
* WPD – internal weak pull-down resistor enabled
* USB\_PU – USB pull-up resistor enabled

  > + By default, the USB function is enabled for USB pins (i.e., GPIO19 and GPIO20), and the pin pull-up is decided by the USB pull-up resistor. The USB pull-up resistor is controlled by USB\_SERIAL\_JTAG\_DP/DM\_PULLUP and the pull-up value is controlled by USB\_SERIAL\_JTAG\_PULLUP\_VALUE. For details, see [ESP32-S3 Technical Reference Manual](https://www.espressif.com/sites/default/files/documentation/esp32-s3_technical_reference_manual_en.pdf) > Chapter *USB Serial/JTAG Controller*.
  > + When the USB function is disabled, USB pins are used as regular GPIOs and the pin’s internal weak pull-up and pull-down resistors are disabled by default (configurable by IO\_MUX\_FUN\_WPU/WPD)

Power-Up Glitches on Pins

| Pin | Glitch | Typical Time (µs) |
| --- | --- | --- |
| GPIO1 | Low-level glitch | 60 |
| GPIO2 | Low-level glitch | 60 |
| GPIO3 | Low-level glitch | 60 |
| GPIO4 | Low-level glitch | 60 |
| GPIO5 | Low-level glitch | 60 |
| GPIO6 | Low-level glitch | 60 |
| GPIO7 | Low-level glitch | 60 |
| GPIO8 | Low-level glitch | 60 |
| GPIO9 | Low-level glitch | 60 |
| GPIO10 | Low-level glitch | 60 |
| GPIO11 | Low-level glitch | 60 |
| GPIO12 | Low-level glitch | 60 |
| GPIO13 | Low-level glitch | 60 |
| GPIO14 | Low-level glitch | 60 |
| XTAL\_32K\_P | Low-level glitch | 60 |
| XTAL\_32K\_N | Low-level glitch | 60 |
| GPIO17 | Low-level glitch | 60 |
| GPIO18 | Low-level/High-level glitch | 60 |
| GPIO19 | Low-level glitch/High-level glitch | 60 |
| GPIO20 | Pull-down glitch/High-level glitch | 60 |

## ADC

Table below shows the correspondence between ADC channels and GPIOs.

ADC Functions

| GPIO Pin Name | ADC Function |
| --- | --- |
| GPIO1 | ADC1\_CH0 |
| GPIO2 | ADC1\_CH1 |
| GPIO3 | ADC1\_CH2 |
| GPIO4 | ADC1\_CH3 |
| GPIO5 | ADC1\_CH4 |
| GPIO6 | ADC1\_CH5 |
| GPIO7 | ADC1\_CH6 |
| GPIO8 | ADC1\_CH7 |
| GPIO9 | ADC1\_CH8 |
| GPIO10 | ADC1\_CH9 |
| GPIO11 | ADC2\_CH0 |
| GPIO12 | ADC2\_CH1 |
| GPIO13 | ADC2\_CH2 |
| GPIO14 | ADC2\_CH3 |
| GPIO15 | ADC2\_CH4 |
| GPIO16 | ADC2\_CH5 |
| GPIO17 | ADC2\_CH6 |
| GPIO18 | ADC2\_CH7 |
| GPIO19 | ADC2\_CH8 |
| GPIO20 | ADC2\_CH9 |

Please add a 0.1 μF filter capacitor between ESP pins and ground when using the ADC function to improve accuracy.

ADC1 is recommended for use.

The calibrated ADC results after hardware calibration and [software calibration](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/adc_calibration.html) are shown in the list below. For higher accuracy, you may implement your own calibration methods.

* When ATTEN=0 and the effective measurement range is 0 ~ 850 mV, the total error is ±5 mV.
* When ATTEN=1 and the effective measurement range is 0 ~ 1100 mV, the total error is ±6 mV.
* When ATTEN=2 and the effective measurement range is 0 ~ 1600 mV, the total error is ±10 mV.
* When ATTEN=3 and the effective measurement range is 0 ~ 2900 mV, the total error is ±50 mV.

## SDIO

ESP32-S3 only has one SD/MMC Host controller, which cannot be used as a slave device.

The SDIO interface can be configured to any free GPIO by software. Please add pull-up resistors to the SDIO GPIO pins, and it is recommended to reserve a series resistor on each trace.

## USB

ESP32-S3 has a full-speed USB On-The-Go (OTG) peripheral with integrated transceivers. The USB peripheral is compliant with the USB 2.0 specification.

ESP32-S3 integrates a USB Serial/JTAG controller that supports USB 2.0 full-speed device.

GPIO19 and GPIO20 can be used as D- and D + of USB respectively. It is recommended to populate 22/33 ohm series resistors between the mentioned pins and the USB connector. Also, reserve a footprint for a capacitor to ground on each trace. Note that both components should be placed close to the chip.

The USB RC circuit is shown in Figure [ESP32-S3 USB RC Schematic](#fig-usb-rc-schematic).

ESP32-S3 USB RC Schematic

Note that upon power-up, the USB\_D+ signal will fluctuate between high and low states. The high-level signal is relatively strong and requires a robust pull-down resistor to drive it low. Therefore, if you need a stable initial state, adding an external pull-up resistor is recommended to ensure a consistent high-level output voltage at startup.

ESP32-S3 also supports download functions and log message printing via USB. For details please refer to Section [Download Guidelines](download-guidelines.html#download-guidelines).

When USB-OTG Download Boot mode is enabled, the chip initializes the IO pad connected to the external PHY in ROM when starts up. The status of each IO pad after initialization is as follows.

IO Pad Status After Chip Initialization in the USB-OTG Download Boot Mode

| IO Pad | Input/Output Mode | Level Status |
| --- | --- | --- |
| VP (MTMS) | INPUT | – |
| VM (MTDI) | INPUT | – |
| RCV (GPIO21) | INPUT | – |
| OEN (MTDO) | OUTPUT | HIGH |
| VPO (MTCK) | OUTPUT | LOW |
| VMO(GPIO38) | OUTPUT | LOW |

If the USB-OTG Download Boot mode is not needed, it is suggested to disable the USB-OTG Download Boot mode by setting the eFuse bit EFUSE\_DIS\_USB\_OTG\_DOWNLOAD\_MODE to avoid IO pad state change.

## Touch Sensor

ESP32-S3 has 14 capacitive-sensing GPIOs, which detect variations induced by touching or approaching the GPIOs with a finger or other objects. The low-noise nature of the design and the high sensitivity of the circuit allow relatively small pads to be used. Arrays of pads can also be used, so that a larger area or more points can be detected.

The touch sensing performance is further enhanced by the waterproof design and digital filtering feature.

Attention

ESP32-S3 touch sensor has not passed the Conducted Susceptibility (CS) test for now, and thus has limited application scenarios.

Table below shows the correspondence between touch sensor channels and GPIOs.

Touch Sensor Functions

| GPIO Pin Name | Touch Sensor Function |
| --- | --- |
| GPIO1 | TOUCH1 |
| GPIO2 | TOUCH2 |
| GPIO3 | TOUCH3 |
| GPIO4 | TOUCH4 |
| GPIO5 | TOUCH5 |
| GPIO6 | TOUCH6 |
| GPIO7 | TOUCH7 |
| GPIO8 | TOUCH8 |
| GPIO9 | TOUCH9 |
| GPIO10 | TOUCH10 |
| GPIO11 | TOUCH11 |
| GPIO12 | TOUCH12 |
| GPIO13 | TOUCH13 |
| GPIO14 | TOUCH14 |

Note that only GPIO14 (TOUCH14) can drive the shield electrode.

When using the touch function, it is recommended to populate a series resistor at the chip side to reduce the coupling noise and interference on the line, and to strengthen the ESD protection. The recommended resistance is from 470 Ω to 2 kΩ, preferably 510 Ω. The specific value depends on the actual test results of the product.