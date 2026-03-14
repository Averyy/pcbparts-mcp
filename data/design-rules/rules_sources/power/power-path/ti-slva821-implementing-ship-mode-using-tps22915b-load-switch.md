---
source: "TI SLVA821 -- Implementing Ship Mode Using TPS22915B Load Switch"
url: "https://www.ti.com/lit/an/slva821/slva821.pdf"
format: "PDF 7pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 10035
---

Application Report

Implementing Ship Mode Using the TPS22915B Load
Switch
Alek Kaknevicius........................................................................................... Drivers and Load Switches
ABSTRACT
As the presence of global manufacturing and distribution increases, many original equipment
manufacturers are looking for creative ways to extend battery life during shipping and shelf life at big-box
warehouses. Keeping the battery sufficiently charged during shipment enables a consistent out-of-box
experience for the end user. A solution that has gained popularity is the use of a ship mode feature that
keeps devices in a low-power state during shipment and while on the shelf. This application note shows
how to use a load switch and a few external components to create a small, cost-effective solution.
Contents
1 Ship Mode Circuit Overview................................................................................................ 2
2 Choosing the Power Switch ................................................................................................ 2
3 Ship Mode Implementation Using the TPS22915B ..................................................................... 2
3.1 Exiting Ship Mode .................................................................................................. 3
3.2 Registering Button Presses ....................................................................................... 3
3.3 Entering Ship Mode ................................................................................................ 4
3.4 Ship Mode Current Consumption................................................................................. 4
4 Waveforms.................................................................................................................... 4
5 Conclusion.................................................................................................................... 6
6 References ................................................................................................................... 6

1 Ship Mode Circuit Overview
The ship mode circuit prolongs battery life during shipment of electronics and provides customers with a
consistent out-of-box experience. To do so, the battery must be electronically disconnected from the rest
of the system to minimize power drain while the product is idle. Once the product is turned on for the first
time, the battery is connected to the rest of the system and stays connected until the system puts itself
back into ship mode. The circuit which is used to connect and disconnect the battery is the ship mode
circuit. Figure 1 shows the behavior of the ship mode circuit when in ship mode (left) and when out of ship
mode (right).
Figure 1. Ship Mode Circuit Behavior: Ship Mode (Left), Out of Ship Mode (Right)
2 Choosing the Power Switch
The main component of this solution, the power switch, is used to disconnect the battery from the rest of
the system. As a power switch, load switches have many advantages when compared to a discrete
solution using field effect transistors (FETs). Load switches offer a controlled turn on, limiting the
damaging effects of inrush current. Many load switches offer a Quick Output Discharge (QOD) feature that
dissipates any residual energy on the output after the switch is disabled. Some load switches even offer
reverse current protection to protect upstream circuitry in case the supply potential dips. They also have
low leakage current when disabled and draw minimal power when enabled, improving battery life in
portable applications. Load switches are cost- and size-optimized to replace discrete solutions where
channel density and space is critical.
For this design, the TPS22915B load switch was chosen because it has a low shutdown current of 500 nA
(typical) to prolong battery life during shipment. The TPS22915B can operate with battery voltages from
1.05 V to 5.5 V, allowing common single-cell battery types to be used with this circuit. The 0.76-mm ×
0.76-mm CSP package utilizes a small footprint, reducing the total solution size.
3 Ship Mode Implementation Using the TPS22915B
For this design, the system requirements for the ship mode circuit included:
• The load switch is put in between the battery and system. When the circuit is put into ship mode, the
battery and system are disconnected due to the load switch being disabled.
• When the button on the product is pressed, the product exits ship mode and the system turns on. The
load switch is enabled, connecting the battery and system. When the button is depressed, the load
switch stays on so that the battery stays connected.
• If the button is pressed after the system has exited ship mode, it provides a signal which can be read
by the rest of the system. This is an advantage for applications with only one button since it can use
that button to both exit ship mode and control the system afterwards.

Keeping all of these things in mind, the following circuit was assembled:
Figure 2. Ship Mode Circuit Using the TPS22915B Load Switch
For the PMOS, the CSD23382F4 transistor was chosen since it features a footprint of 0.6 mm × 1.00 mm
and helps minimize the total solution size. Using resistors and capacitors that are 0201 components, the
total solution size can be reduced to 1.89 mm2 when using two layers.
3.1 Exiting Ship Mode
Before the button is pressed, the solution is in ship mode, meaning that the system is not powered and the
TPS22915B load switch is turned off. When the button is pressed, the voltage from the battery is passed
through the PMOS to the ON pin of the TPS22915B. The voltage enables the TPS22915B, brings VOUT
high, turns off the PMOS, and powers the system. The ON pin is pulled up to VOUT, which keeps the load
switch enabled even after the button is released.
3.2 Registering Button Presses
After exiting ship mode, button presses can be registered by the rest of the system at the Button Press
node shown in Figure 2. When the button is pressed, the battery voltage is connected to the node and
when the button is released the node is left floating. A pulldown resistance can be added on the node to
make the button press a high signal and the button release a low signal.
The button press signal may need to be regulated to a lower voltage for use with a microcontroller GPIO.
This is the case if the battery voltage is higher than the GPIO voltage tolerance. Figure 3 shows two
potential solutions.
Figure 3. Regulating the Button Press Signal for a GPIO Input

The first solution pulls the GPIO to a regulated voltage in the system, whereas the second solution uses a
resistor divider to lower the button press voltage. TI recommends using a series resistance between the
signal and microcontroller to limit current into the GPIO pin before the microcontroller is powered.
3.3 Entering Ship Mode
If the application requires it, the system can be brought back into ship mode by pulling the ON pin node
low. This can be done using a microcontroller GPIO or by using a push button to connect the node to a
pulldown circuit. With the ON pin low, the TPS22915B is disabled and the battery is disconnected from
the rest of the system. The system exits ship mode if the button is pressed.
3.4 Ship Mode Current Consumption
When in ship mode, the battery is disconnected from the rest of the system. However, there is a small
amount of leakage current due to the ship mode circuit, which is dependent on the load switch used.
When disabled, the TPS22915B has 500 nA of leakage current flowing into the VIN pin. This is the only
drain on the battery when the system is in ship mode.
To estimate the battery life of a system with ship mode implemented, use the following equation:
Battery Life [days] = (Battery Capacity [mAh] / Leakage Current [mA]) × (1 day / 24 hours) × 85% Derating Factor (1)
The calculation for a 100-mAh battery follows:
Battery Life = (100 mAh / 0.0005 mA) × (1 day / 24 hours) × 85%
Battery Life = 7083.33 days
With the ship mode circuit, a fully charged 100-mAh battery will last 7083.33 days (19.4 years) before
dying. That means the system will be able to sit on a shelf for 1.94 years before only 10% of the battery
has drained.
4 Waveforms
Figure 4 shows a scope capture of the system entering ship mode.
Figure 4. Scope Capture: System Exiting Ship Mode
The button is pressed, and the Button Press node goes high. The voltage is passed through the PMOS
and is seen at the ON pin of the TPS22915B. With the ON pin high, the TPS22915B turns on and
provides a controlled, linear turn on for the rest of the system.

Once the system has exited ship mode, repeated button presses cause the Button Press node to go high
without disturbing the system power as illustrated in Figure 5.
Figure 5. Scope Capture of Button Press: System Out of Ship Mode
To put the circuit back into ship mode, the ON pin node can be pulled low by a microcontroller, as shown
in Figure 6.
Figure 6. Scope Capture: System Entering Ship Mode
With the ON pin pulled low, the TPS22915B shuts down and disables power to the rest of the system.
The system stays in ship mode until the button is pressed.

5 Conclusion
Using the design in this application note, a ship mode circuit with the following parameters can be created:
Parameter Value
Input Voltage Range 1.05 V to 5.5 V
Output Current 2 A
Current Consumption in Ship Mode 500 nA (typical)
Current Consumption out of Ship Mode 7.6 µA (typical)
Solution Size 1.89 mm2
For more information, refer to the TI design Load Switch Based Ship Mode Reference Design for
Wearables which tests this solution on a physical PCB.
6 References
1. Load Switch Based Ship Mode Reference Design for Wearables (TIDA-00556)
2. TPS2291xx, 5.5-V, 2-A, 37mΩ On-Resistance Load Switch (SLVSCO0)