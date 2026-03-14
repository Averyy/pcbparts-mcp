---
source: "Altium -- Checklist for Systematically Testing PCB Prototypes"
url: "https://resources.altium.com/p/checklist-systematically-testing-pcb-prototypes"
format: "HTML"
method: "readability"
extracted: 2026-03-02
chars: 11629
---

The whole reason we build prototypes of a PCB is to test the functionality and reliability of the product. Functional testing often seems easy: simply plug in the product, let it power up, and check that it works as intended. Is it really that simple?

Of course, the answer is a solid “no,” it’s not that simple. Functional testing is part of [prototype testing](https://resources.altium.com/p/beginners-essentials-equipment-pcb-testing), but there is another aspect of prototype testing related to reliability. Simple throwaway consumer products generally don't need to be tested for reliability, they are usually examined for form and function, and then they can be quickly scaled to volume production. High-reliability products are another matter, and they require many rounds of reliability testing to ensure that they meet the target operating specifications.

The above points are true in Industries like automotive, aerospace, military, and some areas like medical equipment. If it has suddenly become your job to oversee a testing program to assess product reliability, I've compiled a list of tests here for you to consider for PCB prototype testing.

## Functional PCB Prototype Testing

Functional testing is just like it sounds: assess the functionality of the product in its intended operating environment. The corollary to this is assessing that it executes all its functions and programming correctly.

### Electrical Testing

This is probably the first test that will be performed on a prototype PCB: assess that the system performs its basic tasks of manipulating signals, receiving power and supplying power. This is the basic "check that it works" set of tests and typically involves:

* Checking the board with a [multimeter](https://resources.altium.com/p/how-test-short-circuit-pcb)
* Checking power input and output with a supply and load
* Checking data interfaces with other equipment or sensors
* Briefly monitoring important signals with an [oscilloscope](https://resources.altium.com/p/oscilloscope-basics-beginner-guide) or spectrum analyzer

I write briefly in the final point above because these tools are typically used for deeper investigation of the board. For example, if the board does not appear to exhibit the correct functions, data handling, or power, it may warrant further investigation of important points on the board with an oscilloscope.

Following these initial tests, assuming the functionality does not exhibit problems, had opt to move towards Emi pre-compliance testing or thermal testing. During electrical testing, thermal problems will soon become obvious while testing the board. These can be assessed further during reliability testing as discussed below.

### Application Testing

Once the prototype has passed through electrical testing and it is able to run code, it's time to perform a round of application testing. Testing of the application is intimately related to electrical testing because a mistake in the electrical design can cause an application to work incorrectly. The opposite is also true: a mistake in the code can cause the device to work incorrectly, even if the electrical design is correct.

Application testing can follow a process based on pass-fail result from an initial power-on and boot-up test:

1. Perform a simple “does it work” test
2. If there is a problem, monitor logic and sensors while running code
3. Monitor outputs from code on a PC or logic analyzer

Monitoring devices with an embedded application has been [discussed elsewhere on the blog](https://resources.altium.com/p/how-design-test-embedded-systems), and a good way to do this is to insert error handlers so that you know exactly where in the application logic a problem will arise. This helps you narrow down testing to specific components, pins, signals, and functions.

### Static Thermal Testing

As part of functional testing, the static or equilibrium temperature of the board in ambient room temperature should be examined. This is a simple touch test: does the board appear to operate in its intended temperature range? If not, are there any excessively hot components on the PCB? If there are hot spots, where do they arise and what is the exact temperature?

These tests are just a check of the design for thermal performance. A touch test is acceptable for most products. Designs with large processors and power electronics should not involve a touch test as the hottest components will be PMICs, switchers, and processors. Instead, higher power systems or systems where high temperatures are expected should be monitored with thermocouples and/or an infrared camera.

*Thermocouples like this one can be used with multimeters to get a quick measurement of equilibrium temperature during operation.*

Thermocouple measurements are very useful at this point because they can be used to target specific components in the design. This is all done before any long-term thermal testing to ensure reliability:, it is simply to ensure that the design does not run excessively hot and risk failure before going through much more rigorous testing. Thermocouples are cheap and are packaged with many multimeters, such as in the image shown above. This is a very quick and easy way to monitor multiple components and verify that they're not excessively hot, even when the device is running at high power.

## PCB Reliability Testing

Once a prototype has been thoroughly proven to be electrically functional, it also needs to be proven to be highly reliable. Any product that is intended for use in a standard commercial application or in a much higher reliability setting (like automotive) needs to pass a series of reliability tests. These comprise mechanical, electrical, and thermal stress tests that push the PCB assembly and its components to their limits.

Just to give a high level overview, these tests include:

* Long-term electrical tests at high or low temperatures
* Mechanical shock tests or vibration tests
* [ESD tests](https://resources.altium.com/p/overview-human-body-model-emc) or electrical over stress EOS tests
* Thermal cycling tests or shock tests

### Thermal Electrical Testing

Long-term testing of the board at elevated or very low temperatures assesses whether the board can operate as intended at the extremes of the expected operating temperature range. At these extreme temperatures, certain parts of the board might be prone to failure, the cooling mechanisms may become ineffective, or some components may stop working due to thermal protection mechanisms. Operation at very high temperatures needs to be monitored over extended time intervals.

Some of this thermal testing can be performed inside of an environmental chamber. Some Chambers have electrical feed throughs that allow cabling to be inserted so that the board can be powered and monitored. This would include thermocouple wiring which could be used to monitor specific components or circuits.

*Programmable thermal chamber*

Very large thermal chambers are quite expensive and only large companies would be able to afford these. Thermal chambers that go to high temperatures are less costly and simpler to operate than thermal chambers going to low temperatures. More often, we're much more worried about the high end of the operation range because electrical components generate heat. Low operating temperature can still be a concern however, such as electronics that will operate in cold climates.

One major part of developing a thermal testing plan is the need to evaluate the equilibrium temperature during the thermal test, as well as determine whether active cooling might be needed in the product. Thermal testing is a long-term test, you should set it and allow an automated system to monitor the temperature during the test:

1. Load the PCB and its electrical connections into the thermal chamber
2. Set the target test temperature in the thermal chamber
3. While monitoring the system, allow the system to reach an equilibrium operating temperature

These long-term tests are “set it and forget it,” they should be monitored with an automated system and there should be minimal human intervention. If a board fails at high temperature, it's worth bringing the device back to room temperature and trying to run it again, just to see if the device will continue to function at lower temperatures. This could indicate a latent failure that arises at high temperature, or an unintended thermal shut off that occurs in one of the components.

### Mechanical Shock Tests

A mechanical shock test can be quite simple, such as dropping the board from a prescribed height and checking to see whether it breaks. Shock tests are more elaborate when a specific force value is applied to the enclosure/PCB at various angles, and any damage is inspected visually or under a microscope. Following mechanical shock testing, the design can be electrically tested to verify it still functions.

Shock testing machines are used in design and destructive testing of circuits, components, hybrids, and complete assemblies. They can provide half-sine, sawtooth, and square-wave shock pulses from 3G to 30,000G for product validation.

*Older mechanical shock tester*

### Thermal Cycling or Thermal Shock

Sometimes, a component or PCB interconnect does not fail at excessively high temperature. In some cases, failure does not arise until thermal cycling or thermal shock occurs. Thermal cycling and thermal shock are very similar; thermal cycling involves changing the temperature between very high and very low values periodically. Meanwhile, thermal shock involves a very sudden change between two extreme temperatures. This is done by using a dual climate chamber that can transfer the product from one temperature extreme to the other in less than 30 seconds.

### ESD Testing , EOS Testing, or Isolation Testing

Many products have a [galvanic isolation requirement](https://resources.altium.com/p/isolated-vs-non-isolated-power-supplies-right-choice-without-fail) or specification that must be met. Similarly, they may have ESD specifications that must be met. Both can be tested electrically in ESD testing and galvanic isolation testing. A broader classification of this category of testing is electrical overstress testing, or EOS testing.

EOS results for many different factors. ESD or exposure to high voltage AC are two common factors that lead to failure, but there is also the possibility of being exposed to lower voltage rises over extended time intervals.

* Use an ESD gun to apply a specific ESD pulse to a device
* Apply static DC voltage above or below spec
* Apply slow surges with a large programmable power supply

*NX30 ESD simulator gun from [Avalon Test Equipment](https://avalontest.com/em-test-esd-nx30-esd-simulatorgun-30kv-2)*

## You Passed Reliability Testing, Now What?

After plenty of testing, your product just might be ready for the next step in heading to market: Emi testing and scaling production. Once you can prove your product will be compliant with EMC regulations for your industry, as well as broader government regulations, you will be able to scale the product into your target market. There are other certifications that might be needed, such as Underwriters Laboratories (UL) testing for some consumer devices. If you are not an expert in these areas, there are specialized labs that can provide testing services and recommend any required redesigns.

We have only scratched the surface of what’s possible with Altium Designer on Altium 365. [Start your free trial of Altium Designer + Altium 365 today](https://www.altium.com/).