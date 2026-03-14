---
source: "onsemi AN-5086 -- USB Type-C CC Pin Design Considerations"
url: "https://www.onsemi.com/pub/Collateral/AN-5086-D.PDF"
format: "PDF 5pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 14720
---

ON Semiconductor
Is Now
To learn more about onsemi™, please visit our website at
www.onsemi.com
onsemi and and other names, marks, and brands are registered and/or common law trademarks of Semiconductor Components Industries, LLC dba “onsemi” or its affiliates and/or
subsidiaries in the United States and/or other countries. onsemi owns the rights to a number of patents, trademarks, copyrights, trade secrets, and other intellectual property. A listing of onsemi
product/patent coverage may be accessed at www.onsemi.com/site/pdf/Patent-Marking.pdf. onsemi reserves the right to make changes at any time to any products or information herein, without
notice. The information herein is provided “as-is” and onsemi makes no warranty, representation or guarantee regarding the accuracy of the information, product features, availability, functionality,
or suitability of its products for any particular purpose, nor does onsemi assume any liability arising out of the application or use of any product or circuit, and specifically disclaims any and all
liability, including without limitation special, consequential or incidental damages. Buyer is responsible for its products and applications using onsemi products, including compliance with all laws,
regulations and safety requirements or standards, regardless of any support or applications information provided by onsemi. “Typical” parameters which may be provided in onsemi data sheets and/
or specifications can and do vary in different applications and actual performance may vary over time. All operating parameters, including “Typicals” must be validated for each customer application
by customer’s technical experts. onsemi does not convey any license under any of its intellectual property rights nor the rights of others. onsemi products are not designed, intended, or authorized
for use as a critical component in life support systems or any FDA Class 3 medical devices or medical devices with a same or similar classification in a foreign jurisdiction or any devices intended for
implantation in the human body. Should Buyer purchase or use onsemi products for any such unintended or unauthorized application, Buyer shall indemnify and hold onsemi and its officers, employees,
subsidiaries, affiliates, and distributors harmless against all claims, costs, damages, and expenses, and reasonable attorney fees arising out of, directly or indirectly, any claim of personal injury or death
associated with such unintended or unauthorized use, even if such claim alleges that onsemi was negligent regarding the design or manufacture of the part. onsemi is an Equal Opportunity/Affirmative
Action Employer. This literature is subject to all applicable copyright laws and is not for resale in any manner. Other names and brands may be claimed as the property of others.

AN-5086/D
USB Type-C,
CC Pin Design
Considerations
High voltage design considerations for
Type−C connector pins in systems www.onsemi.com
supporting non-USB standard charging
APPLICATION NOTE
protocol and/or fault cases
SUMMARY individual IC, is the best way to achieve overall system
When designing hardware systems with Type−C robustness.
connectors, a designer also has to consider all legacy, Below are few important specifications to ensure the right
TVS is selected based on the Type−C specification, and the
standard, and non-standard specifications that exist in the
Type−C controller ESD protection.
USB connector eco system. With the introduction of the
Type−C connector and the Configuration channel (CC Pin)
Reverse Standoff Voltage
new challenges occur trying to ensure overall system
This specification is important spec to look at when
robustness. This note addresses some of the concerns with
selecting a TVS, due to the types of signals that will utilize
the CC pin in a robust system environment.
the CC pin during normal operation, as well as absolute
maximum spec. of the CC controller IC. Selecting the right
DESIGN CONSIDERATIONS – SYSTEM ESD value ensures the TVS is actually effective in protecting the
AND SURGE system. Reverse Standoff Voltage, V is a common
RWM,
IEC61000−4−2 (henceforth called just “IEC”) is the specification in a TVS product data sheet. For the CC pin, we
industry’s standard for system level ESD testing. IEC testing should pick a 5 V maximum for the V RWM , due to normal
is a system level test, while other ESD specifications like operation of the CC pin, there should never be a case where
Charged Device Model (CDM) and Human Body Model the CC pin should exceed 5 V, and also the reverse standoff
(HBM) target the manufacturing process and human voltage should be lower than the absolute maximum voltage
handling. Most IC’s have integrated Electro-Static on the CC controller IC.
Discharge (ESD) protection intended to protect the device
Diode Capacitance
during manufacturing while external protection in the form
In Power Delivery specification, section 5.8.6, BMC
of a TVS is added for the IEC system level testing. It is very
receiver capacitance requirements are shown below in
important to understand that, implementing TVS protection
Table1.
at the system level and having it work together with the
Table 1. BCM RECEIVER NORMATIVE REQUIREMENTS
Name Description Min Nom Max Unit Comment
cReceiver CC Receiver 200 − 600 pF The DFP or UFP system shall have capacitance within this
Capacitance range when not transmitting on the line
The cReceiver requirement of the CC receiver Breakdown Voltage
capacitance is 200 pF to 600 pF, this has a direct impact on Breakdown voltage is the voltage threshold where the
PD communication. Any device in the CC path, such as TVS diode becomes more conductive to ground and allows
aTVS diode, needs to ensure that capacitance of the device higher amount of current flow from cathode to anode.
does not exceed this specification but can also be used to Figure1 shows a typical TVS I−V cure, and as we can see
meet the minimum capacitance requirements. By choosing after the V BR, the current shot up very quickly as the TVS
the appropriate TVS that works well in the system, you can became very conductive. The voltage increases until it hits
avoid placing additional capacitance on the CC line by the clamping voltage where the TVS effectively becomes
utilizing just the diode capacitance. aresistor that shorts to ground. With a large amount of
© Semiconductor Components Industries, LLC, 2016 1 Publication Order Number:
September, 2017 − Rev. 2 AN−5086/D

AN−5086/D
current passing though the TVS, it will eventually burn up
and destroy the diode in this clamped state.
Figure 1. TVS I−V Curve
In order to make sure proper function of the Type−C CC mobile phones have implemented higher than standard
line communication, and overall system are protected in USB2.0 charging protocol to allow for shorter and faster
ESD/Surge event, the correct breakdown voltage must be charging. Due to the limitation of the USB cable it is not
considered. In Type−C design, the CC pin break down ideal to push more than 2.4 A of current. In order to be able
voltage should be above 5 V to ensure normal operation, and to charge at higher wattage, non-Type−C connector based
below 7 V to ensure that the TVS can help direct extra designs have gone above 5 V on V to reduce charging
BUS
charge to ground when fault occurs. time of the device. Due to backward compatibility support
of Type−C, the Type−C specification allows legacy adapters
DESIGN CONSIDERATION – NONE USB like a Type−A to Type−C Cable. The Type−A to Type−C and
STANDARD CHARGING PROTOCOL Type−C to USB−(cid:2)B cable integrate an internal pull up
resistor (R ) in the cable. Below is a functional model in the
Standard USB2.0 spec. of 500 mA charging current is p
specification 4.5.3.2.4.
clearly not enough for the majority of the devices in the
market today, power/process intensive devices such as
Figure 2. Legacy Host Port to DRP Functional Model
2

In this case when the non-standard USB charging protocol the voltage down. We will discuss how to select the correct
increases the V voltage level, the CC pin will also be Zener in the next section. If the proper Zener diode is
pulled up due to R . When following the Type−C selected, it can also protect against Illegal Type−A to
p
specification, the R value should be 56 k(cid:3), which means Type−C cables with incorrect R .
p p
there will be two cases of higher than normal voltage present
Case 3 – Rapid Insert and Removal of Cable
on the CC line.
Some non-standard USB legacy chargers achieve faster
Case 1 – R d is Enabled charging time by increasing the V BUS voltage. In certain
We can simply calculate the voltage that will show up on cases, when a user unplugs the device from the charger/host
the CC line with Equation1. adapter and cable, while the system is charging at higher
V (cid:2)V (cid:3)0.0835 (eq. 1) than 5 V, there will be a short time period for the charger to
CC BUS
recognize disconnect event and disable the V supply.
Assume R d = 5.1k(cid:3), R p = 56 k(cid:3) During this time, if the R p is still connected to V BUS, and
since it is no longer connected to the device, the residual
In Table2 we can find the typical V voltage of
BUS charge will bring the CC pin to the same voltage as V and
non-standard charging protocol and its corresponding CC BUS
slowly discharge over time. If the user decides to quickly
voltage.
plug the charger back in, there will be a higher than normal
voltage on the CC pin that we would need to consider.
Table 2. V BUS TO CC VOLTAGE WHEN R d ENABLED However, in this case the time duration is very short, and the
VBUS VCC charge remaining on the CC pin is not very large.
Incorporating a protection device like a Zener diode or TVS
9 V 0.75 V
diode in the system can prevent damages to the system.
12 V 1.00 V
15 V 1.25 V DESIGN CONSIDERATION – ILLEGAL TYPE−A
20 V 1.67 V TO TYPE−C CABLE
The support of existing standard A connectors/host
adapters was achieved with a Type−A to Type−C cable
Table2 shows that voltage on CC line is still relatively
shown in Figure3. Although, the Type−C Specification is
low, so there is no high voltage concern for this case.
public, there are still a lot of bad cables with illegal R
p
Case 2 – R is Disabled resistors made and being sold on the market today.
d
With R disabled, the CC line will be pulled high to V Application note AN−6012 explains in detail the bad/illegal
d BUS
voltage, so in this case high voltage will show up on the CC cable and how to utilize the Zener diode to protect against it,
line, thus protection is needed. However, since the current is as well as how to pick the right Zener diode to use.
limited by the 56 k(cid:3) we can uses the Zener diode to clamp
Figure 3. Example of Type−A to Type−C Cable
3

RELATED RESOURCES
•
FUSB301 − Autonomous USB Type−C Controller with Super Speed Switch Control
• FUSB301A − Autonomous USB Type−C Control with Configurable I2C Address
FUSB302 − Programmable USB Type−C Controller w/PD
AN−6102 – USB Type−C, CC Pin Protection Application Note
AN−6105 – USB Type–C Design Considerations
ON Semiconductor and are trademarks of Semiconductor Components Industries, LLC dba ON Semiconductor or its subsidiaries in the United States and/or other countries.
ON Semiconductor owns the rights to a number of patents, trademarks, copyrights, trade secrets, and other intellectual property. A listing of ON Semiconductor’s product/patent coverage
may be accessed at www.onsemi.com/site/pdf/Patent−Marking.pdf. ON Semiconductor reserves the right to make changes without further notice to any products herein.
ON Semiconductor makes no warranty, representation or guarantee regarding the suitability of its products for any particular purpose, nor does ON Semiconductor assume any liability
arising out of the application or use of any product or circuit, and specifically disclaims any and all liability, including without limitation special, consequential or incidental damages. Buyer
is responsible for its products and applications using ON Semiconductor products, including compliance with all laws, regulations and safety requirements or standards, regardless of
any support or applications information provided by ON Semiconductor. “Typical” parameters which may be provided in ON Semiconductor data sheets and/or specifications can and
do vary in different applications and actual performance may vary over time. All operating parameters, including “Typicals” must be validated for each customer application by customer’s
technical experts. ON Semiconductor does not convey any license under its patent rights nor the rights of others. ON Semiconductor products are not designed, intended, or authorized
for use as a critical component in life support systems or any FDA Class 3 medical devices or medical devices with a same or similar classification in a foreign jurisdiction or any devices
intended for implantation in the human body. Should Buyer purchase or use ON Semiconductor products for any such unintended or unauthorized application, Buyer shall indemnify and
hold ON Semiconductor and its officers, employees, subsidiaries, affiliates, and distributors harmless against all claims, costs, damages, and expenses, and reasonable attorney fees
arising out of, directly or indirectly, any claim of personal injury or death associated with such unintended or unauthorized use, even if such claim alleges that ON Semiconductor was
negligent regarding the design or manufacture of the part. ON Semiconductor is an Equal Opportunity/Affirmative Action Employer. This literature is subject to all applicable copyright
laws and is not for resale in any manner.
PUBLICATION ORDERING INFORMATION
LITERATURE FULFILLMENT: N. American Technical Support: 800−282−9855 Toll Free ON Semiconductor Website: www.onsemi.com
Literature Distribution Center for ON Semiconductor USA/Canada
19521 E. 32nd Pkwy, Aurora, Colorado 80011 USA Europe, Middle East and Africa Technical Support: Order Literature: http://www.onsemi.com/orderlit
Phone: 303−675−2175 or 800−344−3860 Toll Free USA/Canada Phone: 421 33 790 2910
Fax: 303−675−2176 or 800−344−3867 Toll Free USA/Canada Japan Customer Focus Center For additional information, please contact your local
Email: orderlit@onsemi.com Phone: 81−3−5817−1050 Sales Representative
◊ www.onsemi.com AN−5086/D
4