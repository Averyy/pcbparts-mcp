Source: https://www.ti.com/lit/pdf/scea094
Retrieved: 2026-11-09

[PDF: 2 pages.]

[www.ti.com](http://www.ti.com)

## _Product Overview_
# **_Debounce a Switch_**


Many physical switches can bounce for hundreds of microseconds after being pressed, while most logic devices
respond in just a few nanoseconds. This can result in false triggers and erroneous output. By adding an
appropriate debounce circuit between a button and a CMOS input, these bounces can be eliminated.


CMOS

Device


See more about this use case in the _Logic Minute_ video _[Debounce a Switch](https://training.ti.com/debounce-switch)_ .

**Design Considerations**


 - Select a time constant based on the bouncing characteristics of your switch

 - Select a resistor based on power consumption, input voltage, or capacitor size limitations

  - Power consumption is calculated with the pullup voltage and resistor value: P = V [2] ÷ R

  - Input voltage is determined by voltage drop across the resistor caused by leakage into the device input.
This is calculated with Ohm's Law: V = I × R

  - Capacitor values can be limited due to package size


**Time Constants for Common Resistor and Capacitor Values**


**Capacitor (μF)**


**Time Constant (ms)** **[(1)]**


**R = 10 kΩ** **R = 100 kΩ** **R = 1 MΩ**


1 **10** 100 1000


0.1 1 **10** 100


0.01 0.1 1 **10**


(1) Time constant should be approximately half of the desired debounce time. This is commonly
selected as 10 ms to give maximum debounce time while preventing humans from noticing the
delay.


 - [[FAQ] How does a slow or floating input affect a CMOS device?](https://e2e.ti.com/support/logic/f/151/t/737694)

 - Need additional assistance? Ask our engineers a question on the _[TI E2E™ logic support forum](https://e2e.ti.com/support/logic/f/151)_

**Recommended Parts**

**Automotive**
**Part Number** **Qualified** **VCC Range** **Type** **Features**

[SN74LVC1G17-Q1](https://www.ti.com/product/SN74LVC1G17-Q1) ✓ Schmitt-trigger inputs

1.65 V–5.5 V Single Buffer
[SN74LVC1G17](https://www.ti.com/product/SN74LVC1G17) Over-voltage tolerant inputs to 5.5 V


[SN74AUP1G17](https://www.ti.com/product/SN74AUP1G17) 0.8 V–3.6 V Single Buffer


Schmitt-trigger inputs
Over-voltage tolerant inputs to 3.6 V
Ultra low power


For more devices, browse through the _[online parametric tool](https://www.ti.com/logic-circuit/buffer-driver/non-inverting-buffer-driver/products.html#p776=Schmitt-Trigger)_ where you can sort by desired voltage, channel
numbers, and other features.


SCEA094 – OCTOBER 2020
_[Submit Document Feedback](https://www.ti.com/feedbackform/techdocfeedback?litnum=SCEA094&partnum=SN74LVC1G17,)_


_Debounce a Switch_ 1


Copyright © 2020 Texas Instruments Incorporated


**IMPORTANT NOTICE AND DISCLAIMER**

TI PROVIDES TECHNICAL AND RELIABILITY DATA (INCLUDING DATA SHEETS), DESIGN RESOURCES (INCLUDING REFERENCE
DESIGNS), APPLICATION OR OTHER DESIGN ADVICE, WEB TOOLS, SAFETY INFORMATION, AND OTHER RESOURCES “AS IS”
AND WITH ALL FAULTS, AND DISCLAIMS ALL WARRANTIES, EXPRESS AND IMPLIED, INCLUDING WITHOUT LIMITATION ANY
IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE OR NON-INFRINGEMENT OF THIRD
PARTY INTELLECTUAL PROPERTY RIGHTS.


These resources are intended for skilled developers designing with TI products. You are solely responsible for (1) selecting the appropriate
TI products for your application, (2) designing, validating and testing your application, and (3) ensuring your application meets applicable
standards, and any other safety, security, regulatory or other requirements.


These resources are subject to change without notice. TI grants you permission to use these resources only for development of an
application that uses the TI products described in the resource. Other reproduction and display of these resources is prohibited. No license
is granted to any other TI intellectual property right or to any third party intellectual property right. TI disclaims responsibility for, and you
will fully indemnify TI and its representatives against, any claims, damages, costs, losses, and liabilities arising out of your use of these
resources.


[TI’s products are provided subject to TI’s Terms of Sale or other applicable terms available either on ti.com or provided in conjunction with](https://www.ti.com/legal/termsofsale.html)
such TI products. TI’s provision of these resources does not expand or otherwise alter TI’s applicable warranties or warranty disclaimers for
TI products.


TI objects to and rejects any additional or different terms you may have proposed. IMPORTANT NOTICE


Mailing Address: Texas Instruments, Post Office Box 655303, Dallas, Texas 75265
Copyright © 2022, Texas Instruments Incorporated

