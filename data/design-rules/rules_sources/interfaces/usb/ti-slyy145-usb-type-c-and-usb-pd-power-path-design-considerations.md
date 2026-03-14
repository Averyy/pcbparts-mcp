---
source: "TI SLYY145 -- USB Type-C and USB PD Power Path Design Considerations"
url: "https://www.ti.com/lit/slyy145"
format: "PDF 8pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 12540
---

# USB Type-C and USB Power Delivery Power Path Design Considerations

## Introduction

With a USB Type-C connector, users can charge their laptop and connect to a monitor, dock, storage device or headphones, all through the same connector. Through the introduction of USB Power Delivery (PD), many functions that were once separate are now merged onto the same connector. The USB PD specification allows for up to 5 A of current as either a source or sink device.

For some applications, 5 A of current might not be sufficient, thus requiring customization. Texas Instruments (TI) enables the configuration of USB PD controllers in a power duo mode, in which two USB Type-C power paths operate in parallel to allow as much as 10 A of current capability at the same voltages as a standard USB PD power source: 5 V, 9 V, 15 V and 20 V. This custom behavior requires special consideration in both the design of the power supply and configuration of the PD controller.

## Hardware Design

When designing a system to source high current, you need to take into account specific design considerations for both thermal performance and efficiency. Most laptops on the market charge at 20 V, and the AC/DC converters in standard laptop chargers have a DC output voltage of 19.5 V to 20 V. 19.5 V is within the allotted 5% error for a 20 V USB PD contract as defined in the USB PD specification.

This allows for a design using a buck-only power architecture if the buck controller supports a 100% duty cycle on the external field-effect transistor (FET). Alternatively, adding a bypass path in parallel with the buck converter passes the input voltage directly to the output of the buck converter -- without passing through the inductor. This method may offer superior thermal performance, but requires the addition of two extra FETs.

## DC/DC Buck Design

For this specific design example, the LM3489 hysteretic p-channel FET (PFET) controller from TI is used. This IC allows a 100% duty cycle on the external PFET to directly pass through the external 19.5 V from the AC/DC converter. Most USB PD controllers on the market have general-purpose input/output (GPIO) events to control the external regulator output voltage. The PD controller can adjust the output voltage of the LM3489 DC/DC buck converter by adjusting the feedback network of the buck.

Figure 1. DC/DC adjustable feedback network.

The architecture shown in Figure 1 can be used to output all four of the standard USB PD voltages (5 V, 9 V, 15 V and 20 V). Select R1 and R2 so that the default output voltage is 5 V. When the USB PD controller negotiates a higher source voltage, it will toggle GPIO signals to turn on the n-channel FETs (NFETs) in the feedback network to adjust the output voltage. When Q1 is enabled, the feedback network adjusts so that R2 and R3 are in parallel with R1 at the top of the divider, resulting in a 9 V output.

When Q2 is enabled, the feedback network adjusts so that R2 and R4 are in parallel with R1 at the top of the divider. R4 is selected so that the parallel resistance of R2 and R4 with R1 at the top of the divider results in a 15 V output. Finally, when Q1 and Q2 are enabled, R2, R3 and R4 are all in parallel with R1 at the top of the divider. Choose the resistor values so that this results in a 20 V output.

To design a system that can output more than 5 A, a bypass path can directly pass the AC/DC output voltage to the VBUS FET in the system. Using a PFET bypass path controlled through GPIOs is a simple way to implement this. Using a relatively large PFET with low RDS(on) for this application will minimize losses through the external bypass path.

This power architecture enables the LM3489 to generate all of the standard USB PD voltages depending on what is connected. Once the Alternate Mode is negotiated for high-power mode, the USB PD controller can toggle a GPIO to enable the external bypass path to directly pass the AC/DC output voltage to the VBUS FET. This enables the USB PD source system to remain compliant while also minimizing losses in high-power mode.

Figure 2 highlights the power architecture -- including a bypass path consisting of back-to-back PFETs. When the path is disabled, the body diode of the PFET on the VOUT side will prevent the AC/DC supply voltage from leaking through to the output of the LM3489. Negotiating and entering Alternate Mode enables the external PFET path. Use this same GPIO signal to simultaneously disable the LM3489 DC/DC by toggling the enable pin so that the DC/DC is not back-fed with 20 V when the external PFET path is enabled.

Figure 2. GPIO-controlled buck DC/DC with bypass FET.

## USB PD Controller Design

The USB PD controller is critical in enabling the features discussed earlier; it must be able to control GPIOs and handle large currents with minimal loss through its VBUS FET. In this specific example, the TPS65987D is used. To control the LM3489 DC/DC from the previous section, the TPS65987D uses two GPIOs in a truth table (Table 1) to generate the output voltages.

| Output voltage | GPIO0 | GPIO1 |
|----------------|-------|-------|
| 5 V | 0 | 0 |
| 9 V | 1 | 0 |
| 15 V | 0 | 1 |
| 20 V | 1 | 1 |

Table 1. GPIO control truth table.

Alternatively, if the input voltage of the system is less than 20 V, you could use an I2C-controlled buck-boost like the bq25703A instead of the LM3489. Although you typically need a microcontroller (MCU) to control the buck-boost controller, with the TPS65987D's integrated I2C master, the MCU is not necessary.

According to the USB PD specification, a device that will ever advertise RD on its configuration channel (CC) line must isolate the output capacitance from the DC/DC controller from VBUS. In this case, the system will need to have a VBUS FET to meet this specification. The TPS65987D has two high-voltage, back-to-back integrated FETs that will meet this requirement. The internal FETs in the TPS65987D have an RDS(on) of about 25 mohm at a 25 deg C ambient temperature. For high-current applications this resistance may be too high. With 5 A of current going through one of the internal FETs, approximately 750 mW of power will be dissipated in the FET. Through the use of power duo mode, the TPS65987D is able to close both of its internal power paths simultaneously in parallel. This effectively halves the RDS(on) of the power path and also halves the power dissipation inside the FETs.

Figure 3. GPIO-controlled DC/DC buck with bypass FET into the USB PD controller.

Having both FETs on at the same time not only allows twice as much current to pass through the USB PD controller; it also allows for a significant loss reduction through the VBUS FET. There are many applications that have a very strict power budget. Having a high RDS(on) VBUS FET prevents USB Type-C from being adopted in some spaces. TI solves this by offering an incredibly low RDS(on) integrated power path solution, enabling the adoption of USB Type-C in areas where it could never be considered before.

## VBUS Power-Path Protection

When designing a system with high power levels, it is crucial to protect the user and system from any harmful events that can happen on the power path. The most difficult event to protect against is a VBUS short to ground. In this instance, the current on VBUS will spike rapidly; it is up to the power path to open the FET immediately before it is damaged by these high current levels. If the FET does not open quickly enough, the spiked current can damage the FET and the rest of the system.

Many USB PD controllers on the market do not integrate the power paths. With these types of USB PD controllers, it is up to the hardware designer to implement protections using discrete components. Implementing an overcurrent protection scheme discretely can be tedious; it usually involves using a sense resistor with a current-sense amplifier. The output of the current-sense amplifier is then fed into a comparator that will trigger a fault GPIO on the USB PD controller, or activate circuitry to disable the gate of the VBUS FET. This is not the best solution, as it's not possible to adjust the overcurrent trip point once the comparator is set. In the event of a VBUS short to ground, it will take longer for a discrete solution to detect the short and open the FET than it would for the integrated power path to detect it.

Like overcurrent protection, implementing reverse-current protection protects a system from noncompliant USB PD devices or adapters. Using a USB PD controller without an integrated power path requires a discrete implementation of reverse current protection, which is another design consideration that you need to take into account when selecting a USB PD controller. Having a USB PD controller that integrates the power path and protection will save design time, as all of the protections are already implemented.

Figure 4 highlights what should happen during a VBUS short to ground with a properly protected power path. As the current on VBUS rises rapidly to approximately 35 A, the USB PD controller detects this high current and immediately opens the FET. VBUS short-to-ground protection must be implemented through a hardware comparator as a firmware implementation would not be able to react fast enough to protect the power path and system. Quick turnoff of the power path protects the system and FET in the event of a hard short.

Figure 4. VBUS short to ground with VBUS = 20 V.

## Power Sink Design

Implementing a device that will sink power over a USB Type-C connector is simpler than the source device. The sink device does not need to implement any overcurrent protection, as it relies on the power source for protection. Many USB PD controllers on the market support "dead battery" operation. Because the only source of power in the system is VBUS, dead battery mode allows you to design a system that is entirely powered from VBUS and does not require any external source of power. Dead battery mode is also useful when you have a device with a fully discharged battery. Dead battery operation allows for the entire system to boot up successfully and begin charging the battery or powering the system without any dependency on external power.

Figure 5. Parallel FET to VBUS in a USB PD controller.

## Power Duo Mode

Power duo mode is configurable using TI's configuration tool. In order to support high currents, you must ensure that both the sink and source devices are configured in power duo mode, and that cabling between the devices is rated to handle the desired current. This generally requires captive cabling or cables with e-markers. Cables without e-markers would be inadequate for more than 3 A of current and should not be used for high-current modes. The USB PD specification states that cables and connectors must support a 200% operating current condition so that a 5 A cable and connector can support 10 A for a period of time.

When the source-side device enters power duo mode, it will simultaneously close both power paths in parallel and generate a GPIO event, which will then configure the power supply to supply the appropriate current. Conversely, when the sink-side device enters power duo mode, it also generates a GPIO event, signaling to the sink system that it may begin drawing high current. It is important that the sink device does not start drawing high current until both devices have been configured in power duo mode.

## Conclusion

USB Type-C and USB PD have enabled end equipment to accomplish more features over the same connector. With a combination of high-speed data and up to 5 A of current in a single cable, USB Type-C offers a comprehensive connectivity solution for many different types of end equipment. However, 5 A of current is not sufficient for all designs wanting to move to USB Type-C. For these specific applications, power duo mode can enable system designers to achieve lower RDS(on).

TI's TPS65987D offers an incredibly low RDS(on) solution using power duo mode for high-current charging. USB PD controllers with integrated power paths can reduce design cycle time by simplifying system power design. With integrated power path protection, you can focus your design efforts on other aspects of your system and not be concerned with your power paths becoming damaged.
