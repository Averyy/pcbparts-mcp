---
source: "TI SCEA064A -- Level Translation for SPI, UART, JTAG"
url: "https://www.ti.com/lit/pdf/scea064"
format: "PDF 9pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 8726
---
# Voltage Level Translation for SPI, UART, and JTAG Interfaces With Focus On 2N7001T

Karan Kotadia, Shreyas Rao

## Abstract

This application report discusses the SPI, UART, and JTAG interface standards. Voltage level translation using the 2N7001T and AXC family of translators along with the usage examples in video doorbell and wireless speaker end equipments are discussed.

## 1 Introduction

The 2N7001T is a single bit unidirectional level shifter device. This voltage signal converter uses two separate configurable power supply rails to translate an unidirectional signal up or down. The device helps system designers implement unidirectional level shifting solutions while reducing component count and board space compared to discrete level shifting implementations.

| Parameter | 2N7001T |
|---|---|
| Voltage Support | 1.65 V - 3.6 V |
| Data Rate | 100 Mbps |
| Drive Strength | 12 mA |
| Icc (AXC1T at 125C) | 14 uA |
| ESD Ratings | 2 kV HBM, 1 kV CDM |
| Operating Temperature | -40C to 125C |
| Power Sequencing | Not Required |
| Ioff Partial Power Down | Supported |
| Packages | SC-70 (DCK) and X2SON (DPW) |

Signal level shifting is necessary to enable communication between two devices which are operating at different voltage levels. A common level shifting example would be the communication of a processor I/O at 1.8 V and a peripheral device I/O that operates at 3.3 V. The 2N7001T is able to provide a great solution to level shifting due to the buffered architecture of the device.

This device can be utilized for common communication interface standards such as Serial Peripheral Interface (SPI), Universal asynchronous receive transmit (UART), Joint Test Access Group (JTAG), or the General purpose Input output (GPIO) pins such as enable or restart.

## 2 Common Interfaces and 2N7001T Implementation

### 2.1 General Purpose Input Output (GPIO)

Communication between any two devices occur when a signal is sent from the output of one device to the input of the interfacing device; the core device and the peripheral devices, however, might be operating at different voltage levels, which is why a level shifter is needed in between them to facilitate the communication. If the required signals are not shifted to the voltage at which the core device is operating, then the reliability of communication is impacted. The 2N7001T provides a good solution for voltage translating common control I/O signals such as enable or restart. Clock buffering, power good, error flag, reset, memory error, processor overheat, LED, and display driving are other common signal types that often need level shifting.

## 3 Serial Peripheral Interface (SPI)

SPI provides synchronous communication between a processor and a peripheral device. The SPI interface has a total of four signal lines:

| Signal | Description | Direction |
|---|---|---|
| CLK | Clock Signal | Controller to Peripheral |
| CIPO | Controller Input/Peripheral Output | Peripheral to Controller |
| COPI | Controller Output/Peripheral Input | Controller to Peripheral |
| CS | Peripheral Select | Controller to Peripheral |

The first is the clock (CLK), which only the controller can control. The controller can transmit one bit of data or receive one bit of data from the peripheral on each pulse of the CLK. Since SPI is full duplex, it requires one line for transmission (COPI) and one line for receiving data (CIPO), meaning it can receive and transmit at the same time. Finally, there is a line for peripheral select (CS) which activates the peripheral.

Communication occurs when the peripheral select line is held low to initiate communication, and then one bit of data is transmitted or received on each clock pulse. This communication is only possible if the peripheral device and the processor are operating at the same voltage levels. Since this is usually not the case, the 2N7001T can be used to provide a unidirectional level shift for the CIPO line. The three other lines that are operating in the opposite direction can be level shifted using the SN74AXC4T245, which is a 4-bit direction controlled level shifter. The 2N7001T can easily operate with data rates of up to 100 Mbps, which is usually within the recommended communication speeds for SPI interface. Alternatively, the SN74AXC4T774 or TXB0104 devices can work as a single chip solution.

### 3.1 Application -- SPI

SPI has the ability to support high data rates and full duplex data communication while having a simple hardware interface and complete protocol flexibility for the bits transferred. Due to these advantages, SPI is implemented in many application use cases. Video Doorbell is one example of the use of SPI protocol. It is the preferred communication method for sensors, control devices, camera lenses, memory, LCD, and SD cards.

Another notable use case involves the control devices in the two way audio communication block. The SPI communication protocol is commonly used in ADC, DAC, CODEC, and DSP processors. Another critical advantage of using SPI instead of I2C for these devices is that SPI allows for a faster data rate. This results in a higher sample rate, which produces better sound quality.

## 4 Universal Asynchronous Receive Transmit (UART)

UART is an asynchronous, moderate speeds, full duplex communication interface with either two or four channels; TX (transmit), RX (receive), or RX, RTS, CTS, and TX.

Communication occurs with a start bit being sent, the data line being pulled from high to low in the middle of a bit period. The start bit is followed by 8 bits of information and a stop bit, the data line going from a logic low to a logic high in the middle of a bit period. Certain communication protocols sometimes have a parity bit which confirms that the correct information was transferred. UART does not depend on a clock line because the receiver and transmitter will have internal clocks that can be set to a selected baud rate or bits per second (usually from 300 bps to 115 kbps) for transmission.

For the UART interfaces to operate appropriately between two devices that are at different voltages, for example 1.8 V to 3.3 V, two of the 2N7001T unidirectional level shifters can be used at each of the signal lines. Since the device can up translate or down translate, it can be used for the receive and transmit lines.

### 4.1 Application -- UART

A common use case for UART interfaces is as a communication link between devices. An example is the communication between the circuits of a wireless speaker. The 2N7001T provides a simple solution for voltage level shifting between the processor and MCU.

## 5 Joint Test Access Group (JTAG)

The Joint Test Access Group developed a hardware interface to allow for the debugging, programming, and testing of embedded devices. JTAG, similar to SPI, operates using a set of five JTAG interface signals:

| Signal | Description | Direction |
|---|---|---|
| TCK | Test Clock Signal | Controller to Debugger |
| TDI | Test Data In | Controller to Debugger |
| TDO | Test Data Out | Debugger to Controller |
| TMS | Test Mode Select | Controller to Debugger |
| TRST (Optional) | Test Reset | Controller to Debugger |

The test clock is used to provide a steady timing signal at which the test data will arrive. The test mode select allows the user to select what section or circuit is going to be tested. TDI is the pin that is used to perform the test and the results are returned through the TDO pin. The optional test reset pin allows the ability to reset JTAG to a known good state.

Usually, there are multiple devices on a board that need to be tested via the JTAG interface. Using JTAG, these devices can be daisy chained to each other with the TDO pin, which extends out of the last device in the chain. If this last device in the daisy chain is on a different voltage level, the 2N7001T can be used for a voltage translation. The signal flow of TDO is opposite to the direction of the other pins allowing for the use of the 2N7001T in combination with SN74AXC4T245, for the remaining three channels.

## 6 Additional Resources

- *2N7001T Evaluation Module* user's guide (SCEU013)
- *Common Risks of Discrete FET Voltage Translation and Advantages of TI's Integrated 2N7001T Level Shifter* (SCEA062)
- *Glitch Free Power Sequencing With AXC Level Translators* (SCEA058)
- *Optimizing Video Doorbell Designs with Common Logic Use Cases* (SCLA018)
- *SN74AXC4T245 Four-bit Bus Transceiver with Configurable Voltage Translation and Tri-State Outputs* (SCES877)
