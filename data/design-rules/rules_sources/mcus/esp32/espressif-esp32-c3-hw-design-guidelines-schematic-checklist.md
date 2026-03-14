---
source: "Espressif ESP32-C3 HW Design Guidelines -- Schematic Checklist"
url: "https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 22621
---
# Schematic Checklist

## Overview

The integrated circuitry of ESP32-C3 requires only 20 electrical components (resistors, capacitors, and inductors) and a crystal, as well as an SPI flash. The high integration of ESP32-C3 allows for simple peripheral circuit design. This chapter details the schematic design of ESP32-C3.

The following figure shows a reference schematic design of ESP32-C3. It can be used as the basis of your schematic design.

ESP32-C3 Reference Schematic

Any basic ESP32-C3 circuit design may be broken down into the following major building blocks:

The rest of this chapter details the specifics of circuit design for each of these sections.

## Power Supply

The general recommendations for power supply design are:

* When using a single power supply, the recommended power supply voltage is 3.3 V and the output current is no less than 500 mA.
* It is suggested to add an ESD protection diode and at least 10 μF capacitor at the power entrance.

The power scheme is shown in [ESP32-C3 Series Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf#cd-pwr-scheme) > Figure *ESP32-C3 Power Scheme*.

More information about power supply pins can be found in [ESP32-C3 Series Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf#cd-pwr-supply) > Section *Power Supply*.

### Digital Power Supply

ESP32-C3 has pin17 VDD3P3\_CPU as the digital power supply pin(s) working in a voltage range of 3.0 V ~ 3.6 V. It is recommended to add an extra 0.1 μF decoupling capacitor close to the pin(s).

Pin VDD\_SPI can serve as the power supply for the external device at 3.3 V (typical value), provided by VDD3P3\_CPU via RSPI. Therefore, there will be some voltage drop from VDD3P3\_CPU. When the VDD\_SPI outputs 3.3 V, it is recommended that users add a 1 μF capacitor close to VDD\_SPI.

VDD\_SPI can be connected to and powered by an external power supply.

When not serving as a power supply pin, VDD\_SPI can be used as a regular GPIO.

Attention

When using VDD\_SPI as the power supply pin for the in-package flash or external 3.3 V flash, the supply voltage should be 3.0 V or above, so as to meet the requirements of flash’s working voltage. In such cases, VDD\_SPI cannot be used as a regular GPIO.

### Analog Power Supply

ESP32-C3’s VDDA and VDD3P3 pins are the analog power supply pins, working at 3.0 V ~ 3.6 V.

For VDD3P3, when ESP32-C3 is transmitting signals, there may be a sudden increase in the current draw, causing power rail collapse. Therefore, it is highly recommended to add a 10 μF capacitor to the power rail, which can work in conjunction with the 0.1 μF capacitor(s) or other capacitors.

It is suggested to add an extra 10 μF capacitor at the power entrance. If the power entrance is close to VDD3P3, then two 10 μF capacitors can be merged into one.

Add an LC circuit to the VDD3P3 power rail to suppress high-frequency harmonics. The inductor’s rated current is preferably 500 mA and above.

For the remaining capacitor circuits, please refer to [ESP32-C3 Reference Schematic](#fig-chip-core-schematic).

### RTC Power Supply

ESP32-C3’s VDD3P3\_RTC pin is the RTC and analog power pin. It is recommended to place a 0.1 μF decoupling capacitor near this power pin in the circuit.

Note that this power supply cannot be used as a single backup power supply.

The schematic for the RTC power supply pin is shown in Figure [ESP32-C3 Schematic for RTC Power Supply Pin](#fig-chip-rtc-power).

ESP32-C3 Schematic for RTC Power Supply Pin

## Chip Power-up and Reset Timing

ESP32-C3’s CHIP\_EN pin can enable the chip when it is high and reset the chip when it is low.

When ESP32-C3 uses a 3.3 V system power supply, the power rails need some time to stabilize before CHIP\_EN is pulled up and the chip is enabled. Therefore, CHIP\_EN needs to be asserted high after the 3.3 V rails have been brought up.

To reset the chip, keep the reset voltage VIL\_nRST in the range of (–0.3 ~ 0.25 × VDD) V. To avoid reboots caused by external interferences, make the CHIP\_EN trace as short as possible.

Figure [ESP32-C3 Power-up and Reset Timing](#fig-chip-timing) shows the power-up and reset timing of ESP32-C3.

ESP32-C3 Power-up and Reset Timing

Table [Description of Timing Parameters for Power-up and Reset](#tab-chip-timing) provides the specific timing requirements.

Description of Timing Parameters for Power-up and Reset

| Parameter | Description | Minimum (µs) |
| --- | --- | --- |
| tSTBL | Time reserved for the power rails to stabilize before the CHIP\_EN pin is pulled high to activate the chip | 50 |
| tRST | Time reserved for CHIP\_EN to stay below VIL\_nRST to reset the chip | 50 |

Attention

* CHIP\_EN must not be left floating.
* To ensure the correct power-up and reset timing, it is advised to add an RC delay circuit at the CHIP\_EN pin. The recommended setting for the RC delay circuit is usually R = 10 kΩ and C = 1 μF. However, specific parameters should be adjusted based on the characteristics of the actual power supply and the power-up and reset timing of the chip.
* If the user application has one of the following scenarios:

  > + Slow power rise or fall, such as during battery charging.
  > + Frequent power on/off operations.
  > + Unstable power supply, such as in photovoltaic power generation.

  Then, the RC circuit itself may not meet the timing requirements, resulting in the chip being unable to boot correctly. In this case, additional designs need to be added, such as:

  > + Adding an external reset chip or a watchdog chip, typically with a threshold of around 3.0 V.
  > + Implementing reset functionality through a button or the main controller.

## Flash

ESP32-C3 can support up to 16 MB external flash, powered by VDD\_SPI. It is recommended to add zero-ohm resistor footprints in series on the SPI communication lines as shown in Figure [ESP32-C3 Schematic for External Flash](#fig-external-flash-schematic). These footprints provide flexibility for future adjustments, such as tuning drive strength, mitigating RF interference, correcting signal timing, and reducing noise, if needed.

For the ESP32-C3 variants with in-package SPI flash, the pins for flash communication cannot be used externally for other purposes.

ESP32-C3 Schematic for External Flash

## Clock Source

ESP32-C3 supports two external clock sources:

### External Crystal Clock Source (Compulsory)

The ESP32-C3 firmware only supports 40 MHz crystal.

The circuit for the crystal is shown in Figure [ESP32-C3 Schematic for External Crystal](#fig-external-crystal-schematic). Note that the accuracy of the selected crystal should be within ±10 ppm.

ESP32-C3 Schematic for External Crystal

Please add a series component on the XTAL\_P clock trace. Initially, it is suggested to use an inductor of 24 nH to reduce the impact of high-frequency crystal harmonics on RF performance, and the value should be adjusted after an overall test.

The initial values of external capacitors C1 and C2 can be determined according to the formula:

\[C\_L = \frac{C1 \times C2} {C1+C2} + C\_{stray}\]

where the value of CL (load capacitance) can be found in the crystal’s datasheet, and the value of Cstray refers to the PCB’s stray capacitance. The values of C1 and C2 need to be further adjusted after an overall test as below:

1. Select TX tone mode using the [Certification and Test Tool](https://www.espressif.com/en/support/download/other-tools?keys=).
2. Observe the 2.4 GHz signal with a radio communication analyzer or a spectrum analyzer and demodulate it to obtain the actual frequency offset.
3. Adjust the frequency offset to be within ±10 ppm (recommended) by adjusting the external load capacitance.

> * When the center frequency offset is positive, it means that the equivalent load capacitance is small, and the external load capacitance needs to be increased.
> * When the center frequency offset is negative, it means the equivalent load capacitance is large, and the external load capacitance needs to be reduced.
> * External load capacitance at the two sides are usually equal, but in special cases, they may have slightly different values.

Note

* Defects in the manufacturing of crystal (for example, large frequency deviation of more than ±10 ppm, unstable performance within the operating temperature range, etc) may lead to the malfunction of ESP32-C3, resulting in a decrease of the RF performance.
* It is recommended that the amplitude of the crystal is greater than 500 mV.
* When Wi-Fi or Bluetooth connection fails, after ruling out software problems, you may follow the steps mentioned above to ensure that the frequency offset meets the requirements by adjusting capacitors at the two sides of the crystal.

### RTC Clock Source (Optional)

ESP32-C3 supports an external 32.768 kHz crystal to act as the RTC clock. The external RTC clock source enhances timing accuracy and consequently decreases average power consumption, without impacting functionality.

Figure [ESP32-C3 Schematic for 32.768 kHz Crystal](#fig-32khz-crystal-schematic) shows the schematic for the external 32.768 kHz crystal.

ESP32-C3 Schematic for 32.768 kHz Crystal

Please note the requirements for the 32.768 kHz crystal:

The parallel resistor R is used for biasing the crystal circuit (5 MΩ < R ≤ 10 MΩ).

In general, you do not need to populate the resistor.

If the RTC clock source is not required, then the pins for the 32.768 kHz crystal can be used as GPIOs.

## RF

### RF Circuit

ESP32-C3’s RF circuit is mainly composed of three parts, the RF traces on the PCB board, the chip matching circuit, the antenna and the antenna matching circuit. Each part should meet the following requirements:

* For the RF traces on the PCB board, 50 Ω impedance control is required.
* For the chip matching circuit, it must be placed close to the chip. A CLC structure is preferred.

  > + The CLC structure is mainly used to adjust the impedance point and suppress harmonics, and a set of LC can be added if space permits.
  > + The RF matching circuit is shown in Figure [ESP32-C3 Schematic for RF Matching](#fig-rf-matching-schematic).
* For the antenna and the antenna matching circuit, to ensure radiation performance, the antenna’s characteristic impedance must be around 50 Ω. Adding a CLC matching circuit near the antenna is recommended to adjust the antenna. However, if the available space is limited and the antenna impedance point can be guaranteed to be 50 Ω by simulation, then there is no need to add a matching circuit near the antenna.

ESP32-C3 Schematic for RF Matching

### RF Tuning

The RF matching parameters vary with the board, so the ones used in Espressif modules could not be applied directly. Follow the instructions below to do RF tuning.

Figure [ESP32-C3 RF Tuning Diagram](#fig-rf-tuning) shows the general process of RF tuning.

ESP32-C3 RF Tuning Diagram

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

Usually, UART0 is used as the serial port for download and log printing. For instructions on download over UART0, please refer to Section [Download Guidelines](download-guidelines.html#download-guidelines). It is recommended to connect a 499 Ω series resistor to the U0TXD line to suppress harmonics.

If possible, use other UART interfaces as serial ports for communication. For these interfaces, it is suggested to add a series resistor to the TX line to suppress harmonics.

When using the AT firmware, please note that the UART GPIO is already configured (refer to [Hardware Connection](https://docs.espressif.com/projects/esp-at/en/latest/esp32c3/Get_Started/Hardware_connection.html)). It is recommended to use the default configuration.

## SPI

When using the SPI function, to improve EMC performance, add a series resistor (or ferrite bead) and a capacitor to ground on the SPI\_CLK trace. If space allows, it is recommended to also add a series resistor and capacitor to ground on other SPI traces. Ensure that the RC/LC components are placed close to the pins of the chip or module.

## Strapping Pins

At each startup or reset, a chip requires some initial configuration parameters, such as in which boot mode to load the chip, etc. These parameters are passed over via the strapping pins. After reset, the strapping pins work as normal function pins.

GPIO2, GPIO8, and GPIO9 are strapping pins.

All the information about strapping pins is covered in [ESP32-C3 Series Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf) > Chapter *Boot Configurations*.

In this section, we will mainly cover the strapping pins related to boot mode.

After chip reset is released, the combination of GPIO2, GPIO8, and GPIO9 controls the boot mode. See Table [Boot Mode Control](#tab-chip-boot-mode-control).

Boot Mode Control

| Boot Mode | GPIO2 | GPIO8 | GPIO9 |
| --- | --- | --- | --- |
| Default Config | – (Floating) | – (Floating) | 1 (Pull-up) |
| SPI Boot (default) | 1 | Any value | 1 |
| Joint Download Boot | 1 | 1 | 0 |

Signals applied to the strapping pins should have specific *setup time* and *hold time*. For more information, see Figure [Setup and Hold Times for Strapping Pins](#fig-shared-strap-pin-timing) and Table [Description of Timing Parameters for Strapping Pins](#tab-strap-pin-timing).

Setup and Hold Times for Strapping Pins

Description of Timing Parameters for Strapping Pins

| Parameter | Description | Minimum (ms) |
| --- | --- | --- |
| tSU | Time reserved for the power rails to stabilize before the chip enable pin (CHIP\_EN) is pulled high to activate the chip. | 0 |
| tH | Time reserved for the chip to read the strapping pin values after CHIP\_EN is already high and before these pins start operating as regular IO pins. | 3 |

Attention

* It is recommended to place a pull-up resistor at the GPIO9 pin.
* Do not add high-value capacitors at GPIO9, or the chip may enter download mode.

## GPIO

The pins of ESP32-C3 can be configured via IO MUX or GPIO matrix. IO MUX provides the default pin configurations (see [ESP32-C3 Series Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf#cd-append-consolid-pin-overview) > Appendix *ESP32-C3 Consolidated Pin Overview*), whereas the GPIO matrix is used to route signals from peripherals to GPIO pins. For more information about IO MUX and GPIO matrix, please refer to [ESP32-C3 Technical Reference Manual](https://www.espressif.com/sites/default/files/documentation/esp32-c3_technical_reference_manual_en.pdf) > Chapter *IO MUX and GPIO Matrix*.

Some peripheral signals have already been routed to certain GPIO pins, while some can be routed to any available GPIO pins. For details, please refer to [ESP32-C3 Series Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf) > Section *Peripherals*.

When using GPIOs, please:

* Pay attention to the states of strapping pins during power-up.
* Pay attention to the default configurations of the GPIOs after reset. The default configurations can be found in the table below. It is recommended to add a pull-up or pull-down resistor to pins in the high-impedance state or enable the pull-up and pull-down during software initialization to avoid extra power consumption.
* Avoid using the pins already occupied by flash.
* Some pins will have glitches during power-up. Refer to Table [Power-Up Glitches on Pins](#tab-glitches-on-pins) for details.

IO MUX Pin Functions

| Name | No. | Function 0 | Function 1 | Function 2 | Reset | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| XTAL\_32K\_P | 4 | GPIO0 | GPIO0 | — | 0 | R |
| XTAL\_32K\_N | 5 | GPIO1 | GPIO1 | — | 0 | R |
| GPIO2 | 6 | GPIO2 | GPIO2 | FSPIQ | 1 | R |
| GPIO3 | 8 | GPIO3 | GPIO3 | — | 1 | R |
| MTMS | 9 | MTMS | GPIO4 | FSPIHD | 1 | R |
| MTDI | 10 | MTDI | GPIO5 | FSPIWP | 1 | R |
| MTCK | 12 | MTCK | GPIO6 | FSPICLK | 1\* | G |
| MTDO | 13 | MTDO | GPIO7 | FSPID | 1 | G |
| GPIO8 | 14 | GPIO8 | GPIO8 | — | 1 | — |
| GPIO9 | 15 | GPIO9 | GPIO9 | — | 3 | — |
| GPIO10 | 16 | GPIO10 | GPIO10 | FSPICS0 | 1 | G |
| VDD\_SPI | 18 | GPIO11 | GPIO11 | — | 0 | — |
| SPIHD | 19 | SPIHD | GPIO12 | — | 3 | — |
| SPIWP | 20 | SPIWP | GPIO13 | — | 3 | — |
| SPICS0 | 21 | SPICS0 | GPIO14 | — | 3 | — |
| SPICLK | 22 | SPICLK | GPIO15 | — | 3 | — |
| SPID | 23 | SPID | GPIO16 | — | 3 | — |
| SPIQ | 24 | SPIQ | GPIO17 | — | 3 | — |
| GPIO18 | 25 | GPIO18 | GPIO18 | — | 0 | USB, G |
| GPIO19 | 26 | GPIO19 | GPIO19 | — | 0\* | USB |
| U0RXD | 27 | U0RXD | GPIO20 | — | 3 | G |
| U0TXD | 28 | U0TXD | GPIO21 | — | 4 | — |

**Reset**

The default configuration of each pin after reset:

* 0 – input disabled, in high impedance state (IE = 0)
* 1 – input enabled, in high impedance state (IE = 1)
* 2 – input enabled, pull-down resistor enabled (IE = 1, WPD = 1)
* 3 – input enabled, pull-up resistor enabled (IE = 1, WPU = 1)
* 4 – output enabled, pull-up resistor enabled (OE = 1, WPU = 1)
* 0\* – input disabled, pull-up resistor enabled (IE = 0, WPU = 0, USB\_WPU = 1). See details in Notes
* 1\* – When the value of eFuse bit EFUSE\_DIS\_PAD\_JTAG is

  > + 0, input enabled, pull-up resistor enabled (IE = 1, WPU = 1)
  > + 1, input enabled, in high impedance state (IE = 1)

**Notes**

* R – These pins have analog functions.
* USB – GPIO18 and GPIO19 are USB pins.

  > + By default, the USB function is enabled for USB pins (i.e., GPIO18 and GPIO19), and the pin pull-up is decided by the USB pull-up resistor. The USB pull-up resistor is controlled by USB\_SERIAL\_JTAG\_DP/DM\_PULLUP and the pull-up value is controlled by USB\_SERIAL\_JTAG\_PULLUP\_VALUE. For details, see [ESP32-C3 Technical Reference Manual](https://www.espressif.com/sites/default/files/documentation/esp32-c3_technical_reference_manual_en.pdf) > Chapter *USB Serial/JTAG Controller*.
  > + When the USB function is disabled, USB pins are used as regular GPIOs and the pin’s internal weak pull-up and pull-down resistors are disabled by default (configurable by IO\_MUX\_FUN\_WPU/WPD).
* G – These pins have glitches during power-up. See details in Table [Power-Up Glitches on Pins](#tab-glitches-on-pins).

Power-Up Glitches on Pins

| Pin | Glitch | Typical Time (ns) |
| --- | --- | --- |
| MTCK | Low-level glitch | 5 |
| MTDO | Low-level glitch | 5 |
| GPIO10 | Low-level glitch | 5 |
| U0RXD | Low-level glitch | 5 |
| GPIO18 | High-level glitch | 50,000 |

## ADC

Please add a 0.1 μF filter capacitor between ESP pins and ground when using the ADC function to improve accuracy.

It is recommend to use ADC1, given that ADC2 is not factory-calibrated, and ADC2 of some chip revisions is not operable. For details, please refer to [ESP32-C3 Series SoC Errata](https://www.espressif.com/sites/default/files/documentation/esp32-c3_errata_en.pdf).

The calibrated ADC results after hardware calibration and [software calibration](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/api-reference/peripherals/adc_calibration.html) are shown in the list below. For higher accuracy, you may implement your own calibration methods.

* When ATTEN=0 and the effective measurement range is 0 ~ 750 mV, the total error is ±10 mV.
* When ATTEN=1 and the effective measurement range is 0 ~ 1050 mV, the total error is ±10 mV.
* When ATTEN=2 and the effective measurement range is 0 ~ 1300 mV, the total error is ±10 mV.
* When ATTEN=3 and the effective measurement range is 0 ~ 2500 mV, the total error is ±35 mV.

## USB

ESP32-C3 integrates a USB Serial/JTAG controller that supports USB 2.0 full-speed device.

GPIO18 and GPIO19 can be used as D- and D + of USB respectively. It is recommended to populate 22/33 ohm series resistors between the mentioned pins and the USB connector. Also, reserve a footprint for a capacitor to ground on each trace. Note that both components should be placed close to the chip.

Note that upon power-up, the USB\_D+ signal will fluctuate between high and low states. The high-level signal is relatively strong and requires a robust pull-down resistor to drive it low. Therefore, if you need a stable initial state, adding an external pull-up resistor is recommended to ensure a consistent high-level output voltage at startup.

ESP32-C3 also supports download functions and log message printing via USB. For details please refer to Section [Download Guidelines](download-guidelines.html#download-guidelines).
