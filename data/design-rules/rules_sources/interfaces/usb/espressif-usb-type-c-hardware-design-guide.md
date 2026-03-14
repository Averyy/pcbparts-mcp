---
source: "Espressif -- USB Type-C Hardware Design Guide"
url: "https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_overview/usb_typec_hardware_guide.html"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 8620
---
# **USB Type-C Hardware Design Guide**

## USB Type-C Overview

Since its official release in 2014, USB Type-C has rapidly gained widespread adoption in various electronic devices due to its compact size, reversible connector design, and support for high-power transmission capabilities. Compared to traditional USB Type-A interfaces, USB-C not only offers greater convenience in use but also better suits the design requirements of modern portable devices, demonstrating strong compatibility and practicality in mobile devices, laptops, and even certain high-power applications.

USB Type-A and USB Type-C connectors

USB Type-C Connector Pins

USB Type-C Connector Pin Functions

| Function | Pins | Description |
| --- | --- | --- |
| USB 3.x | A2, A3, B2, B3, A10, A11, B10, B11 | USB 3.x data transfer |
| USB 2.0 | A6/B6 (D+), A7/B7 (D−) | USB 2.0 data transfer |
| Config | CC1, CC2 | Configuration interface, plug detection, power delivery protocol info transfer, Vconn function |
| Sideband Use | SBU1, SBU2 | Low speed signals are allocated exclusively for use in alternate modes. |
| Power | VBUS, GND | Power supply |

In addition, USB Type-C connectors are available in various pin configurations to suit different application scenarios, such as 24-pin, 16-pin, 12-pin, and 6-pin versions. The 6-pin configuration includes only power pins and does not support data transmission; the 12-pin and 16-pin configurations add USB 2.0 data support on top of power delivery; the 24-pin configuration provides full-featured Type-C functionality. Users can select the appropriate pin configuration based on their specific application needs to achieve a balance between performance and cost.

## USB Type-C Role Identification and Power Detection

Compared to previous USB specifications, USB Type-C defines a broader range of roles:

* **Power roles:** A USB-C port can act as a **Source** (power provider), a **Sink** (power consumer), or a **Dual-Role Power (DRP)** port.
* **Data roles:** A USB-C port can operate as a **Downstream-Facing Port (DFP)**, an **Upstream-Facing Port (UFP)**, or a **Dual-Role Data (DRD)** port.

The identification and configuration of these roles are accomplished through the CC lines within the Type-C connector.

Type-C CC Pull-up and Pull-down Model

* As a Source, the USB-C port asserts one pull-up resistor (Rp) on each CC pin.
* As a Sink, the USB-C port asserts a pull-down resistor (Rd) on each CC pin.
* When a Source-side USB-C port is connected to a Sink-side USB-C port, the Source detects the Sink’s Rd on CC and interprets this as a valid attachment, confirming the partner is a Sink. If both sides are Sources or both are Sinks, no valid connection (attachment) is established, and neither side will operate normally.

Note

For dual-role ports, the CC line will continuously alternate between pull-up and pull-down states.

The pull-down resistor Rd is typically 5.1 KΩ, while the pull-up resistor Rp determines the current-carrying capability. Without USB Power Delivery (PD), USB Type-C supports up to 5V and a maximum current of 3A:

USB Type-C Power Capabilities

| Power Profile | Rp (5V drive) | Rp (3.3V drive) |
| --- | --- | --- |
| Default Power | 56 KΩ ±20% | 36 KΩ ±20% |
| 1.5A @ 5V | 22 KΩ ±20% | 12 KΩ ±20% |
| 3A @ 5V | 10 KΩ ±20% | 4.7 KΩ ±20% |

Note

If your application requires power negotiation above 15W, support for alternate functions such as DisplayPort, or if the power and data roles do not match, a USB PD controller is required.

## Introduction to USB PD

By default, the USB Type-C interface supports up to 5V and 3A (i.e., 15W), which is suitable for powering common low-power devices. To meet the needs of higher-power devices, the USB Power Delivery (PD) specification was introduced. The latest USB PD 3.2 version significantly increases power delivery capability, allowing up to 240W over a single USB Type-C cable, greatly expanding the application range of USB-C. Note that for voltages of 20V and power above 60W, the current is limited by cable specifications.

Evolution of USB PD Versions

### USB PD Power Negotiation Process

USB PD operates by using the CC line of the USB Type-C interface as a data channel to negotiate voltage, current, and power direction. Once a power source and sink are connected via USB Type-C, USB PD messages are transmitted over the CC line using a 300kbps ±10% bi-phase mark code (BMC) signal. The negotiation process includes the following steps:

* The power source sends a Source\_Capabilities message containing its available power profiles (e.g., 5V/3A, 9V/3A, etc.).
* The sink receives the Source\_Capabilities message, selects the desired power profile, and sends a Request message.
* The source receives the Request message, checks if it can supply the requested power, and if so, sends an Accept message. The source then sends a PS\_Rdy message to indicate that the requested power is being supplied. If the request cannot be met, a Reject message is sent.

USB PD Communication

The current ESP32 series chips are unable to parse the USB PD protocol, so an external PD controller is required to implement specific voltage requests.

## USB Type-C Data Transmission

USB Type-C is compatible with multiple USB specifications, including USB 1.0, 1.1, 2.0, 3.2 Gen 1, 3.2 Gen 2, 3.2 Gen 2×2, USB4 20 Gbps, and USB4 40 Gbps. Given that current ESP32-series chips support up to USB 2.0 High-Speed, this document focuses on USB 2.0 and earlier specifications.

USB Type-C provides two sets of D+/D− pins **A6/A7** and **B6/B7**. To guarantee proper differential signaling regardless of plug orientation, **A6 is tied to B6** as **D+**, and **A7 is tied to B7** as **D−**. This differential pair carries the USB data, ensuring the link operates correctly in either insertion direction.

D+/D− pins on USB Type-C

For the **SuperSpeed differential pairs (TX/RX)**, since current ESP32 devices do **not** support USB 3.x data rates, these pins should be left **unconnected (NC)**. No routing or terminations are required.

## USB Type-C Hardware Reference Designs

Based on the requested voltage, the USB Type-C hardware design can be divided into two schemes: with or without an external PD controller. For the hardware solution with an external PD controller, this section will focus solely on the Device hardware design.

### Device Hardware Design with PD Controller

Since the USB-PD protocol is relatively complex, the device side can use a PD controller chip to simplify the design, quickly complete voltage negotiation and output the required voltage:

IP2721 PD Controller

The IP2721 can automatically detect device connection status through the CC pin and use hardware PD protocol to parse power source capability information, thereby automatically requesting matching voltage output. Users can also select other models of PD controllers according to actual requirements to implement voltage request functionality.

### Hardware Design for Device, Host, and DRP without PD Controller

#### USB Type-C Device Design

USB Type-C Device Design

In the device design, CC1 and CC2 need to be pulled down with 5.1 KΩ resistors.

Important

When a device needs more than the USB default current (500 mA for USB 2.0; 900 mA after USB 3.x enumeration), it is necessary to read the source’s advertised current level on the Type-C CC line (using CC logic and a Type-C port controller) and set the device’s input current limit no higher than that level; otherwise, the source may be overloaded.

#### USB Type-C Host and DRP Design

USB Type-C Host and DRP Design

The Host and DRP design use the TI TUSB320LA Type-C CC logic and port controller, which configures the TUSB320 to switch between DFP, UFP, and DRP roles through the I2C interface. Users can also select other models of CC logic and port controllers according to actual requirements.

Important

In mass-produced products, USB ports must also account for conditions such as **overcurrent and overtemperature**. This ensures that in abnormal situations, current output can be limited to protect the power supply system. You can opt for USB port power switch chips with adjustable current limit thresholds, such as the [CH217](https://www.wch-ic.com/downloads/CH217DS1_PDF.html), to simplify the Host VBUS design.

## USB Type-C Reference Documents
