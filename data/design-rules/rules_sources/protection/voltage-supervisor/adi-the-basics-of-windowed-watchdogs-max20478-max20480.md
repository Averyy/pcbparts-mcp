---
source: "ADI -- The Basics of Windowed Watchdogs (MAX20478/MAX20480)"
url: "https://www.analog.com/en/resources/technical-articles/the-basics-of-windowed-watchdogs.html"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 13179
---

# The Basics of Windowed Watchdogs

## Abstract

A watchdog is an important part of a comprehensive system and must be well understood to take full advantage of its functions. Most watchdogs are windowed, which require more precise timing than non-windowed watchdogs but allow for greater capability. Windowed watchdogs can be used by designers to implement features such as power-on extended open windows, latch features, and programmable hold times.

## Introduction

This application note describes the operation of windowed watchdogs featured in the [MAX20478](/en/products/max20478.html)and [MAX20480](/en/products/max20480.html) family of products. These watchdogs feature programmable extended windows, programmable RESETx hold times, single or consecutive watchdog fault assertions, and RESETx latch capability. This application note provides a more comprehensive understanding of watchdogs and their capabilities.

## Basics of Watchdog Operation

A watchdog is a feature that is used in systems to ensure that system-on-chip (SoC) devices or microcontrollers (MCUs) are operating properly. This could mean detecting an SoC that is caught in an infinite loop, is taking too long to perform a task, or even shut down completely. The use of a watchdog in a system requires the SoC to periodically send a signal to the watchdog in a step called servicing/refreshing. Once the SoC has serviced the watchdog, the watchdog has then confirmed proper operation of the SoC and then starts a new cycle in which it waits for another service command from the SoC. If the SoC does not service the watchdog for a duration set by the watchdog, a fault will assert. This operation describes a non-windowed watchdog which will not be addressed in this application note. A windowed watchdog operates in a very similar fashion but features a service cycle that is split into CLOSED and OPEN durations called windows. This requires more precise timing for valid services since a service is only valid at certain times in the windowed cycle.

The duration of these windows is defined by the IC watchdog clock. The watchdog clock is derived from the IC system clock and typically starts at 1/32nd of the system clock which is normally 1.28MHz. Some parts have a programmable WDIV field that allows for this clock to be divided more to allow for longer window times. In the following examples, the watchdog period is 200µs and the equations used are specific to the MAX20478 (Figure 1).

Figure 1. Examples of combinations of CLOSED and OPEN window lengths according to MAX20478 watchdog equations.

A watchdog service during an OPEN window of a watchdog cycle is considered a valid service. After a valid service, the OPEN window will immediately transition to a CLOSED window regardless of the time left in the OPEN window. Figure 2 shows an example of a valid watchdog cycle.

Figure 2. Valid watchdog refresh during an OPEN window. A new CLOSED and OPEN immediately follows.

A watchdog service from the SoC in a CLOSED window of a watchdog cycle will be interpreted by the watchdog as a fault. If no service occurs by the time both the CLOSED and OPEN windows have elapsed, the watchdog asserts a fault. To understand how CLOSED windows operate in windowed watchdogs, extended windows must first be explored.

## Extended Windows

In most systems, SoCs and MCUs require additional time to power on or to perform other more important tasks than servicing the watchdog. As a result, it's possible a system will fail a normal windowed watchdog frame with a CLOSED and OPEN window. To address this, ADI products feature extended windows. These windows occur at first power-on and after every RESETx assertion and operate as an OPEN window where a service at any time during the window duration is considered valid.

During normal operation, with a valid watchdog service in the OPEN window, the watchdog will immediately start a new cycle after a valid refresh. This means a new CLOSED window followed by an OPEN window. In a watchdog with extended windows, if any fault occurs, the watchdog will immediately stop whatever window it is currently in and start a new extended window after the RESETx hold time has elapsed. This extended window does not have a CLOSED duration and will accept any watchdog service as valid for the duration of the window. If the watchdog is serviced in this window, the extended window is immediately stopped, and a normal CLOSE/OPEN cycle follows. If the watchdog is not serviced in the extended window, RESETx will assert for the hold time and another extended window will follow. This repeats until the watchdog is serviced.

Figures 3 and 4 show two potential timing situations for invalid refreshes.

Figure 3. RESETx will immediately assert if WD is refreshed during the CLO window. An EXT window will start after the RESETx de-assertion. Extended windows continue to repeat until the watchdog is serviced.

Figure 4. RESETx will immediately assert after the end of the OPN window if the watchdog is not refreshed. A new EXT window will start after RESETx de-asserts. An EXT window will continue to repeat until the watchdog is refreshed.

## Variable RESETx Hold Times

It is common for systems to enter an interrupt procedure after a failure to service a watchdog. These interrupt routines may take several milliseconds to complete before the SoC or MCU can refresh the watchdog again. This could cause the watchdog to assert RESETx again and possibly enter the interrupt routine repeatedly. This issue can be addressed by changing the duration of the RESETx hold time to allow the SoC or MCU to finish the interrupt routine. The variable RESETx hold time feature will hold the RESETx pin of the IC low for a set duration after a fault. If a fault occurs, the watchdog will immediately stop the window it was in and assert the RESETx pin of the IC for the set duration determined by the hold time. Once RESETx de-asserts, the watchdog resumes normal operation and the SoC or MCU can service the watchdog. In Figures 3 and 4, the RESETx hold time length has been omitted to simplify diagrams. Figures 5 and 6 describe two different RESETx hold times.

Figure 5. The duration of the RESETx hold time is programmable. ADI parts have several set durations that are programmed when the part is made. Refer to the ADI IC datasheet for exact RESETx hold times.

Figure 6. The duration of the RESETx hold time is set to 8ms in this diagram. Refer to ADI IC datasheet for exact RESETx hold times.

## Single/Consecutive WD Fault Counter

In some systems that implement a watchdog, RESETx assertions do not necessarily constitute a problem with the system. An errant RESETx assertion may appear in a system even if the system is operating correctly. To address this, ADI watchdogs feature watchdog fault counters which allow for RESETx assertions to occur on single or double watchdog faults.

If a single fault counter option is selected, only one watchdog fault (no service, service during CLO window, etc.) is required to assert RESETx. If the double fault option is chosen, the first watchdog fault will increment the watchdog fault counter and the second fault will then assert RESETx. To RESETx the fault counter after one watchdog fault, two consecutive valid services of the watchdog are required. This is described in Figures 7 to 10.

Figure 7. RESETx counter will increase to one if WD is refreshed during CLO window. No refresh after the end of the next OPN window will increase the counter to 2. This causes RESETx to assert, an EXT window will start after RESETx de-assertion, and the fault counter is RESETx to 0. RESETx asserts again after no refresh during EXT window or OPN window.

Figure 8. RESETx counter will increase to one if the watchdog is not refreshed during the 1st OPN window. Another normal CLO and OPEN will occur. If there is no refresh, RESETx counter will reach 2 and assert.

Figure 9. No refresh after the first OPN window increases the fault counter to 1. The next frame has a refresh, but the fault counter remains 1. The next OPN window does not receive a refresh, so the counter is increased to 2. Fault is asserted and the EXT window starts after RESETx de-assertion.

Figure 10.No refresh after the first OPN increases the fault counter to 1. The next frame has a refresh, but the counter remains 1. The third window also receives a refresh, so the counter is cleared to 0. The next two frames do not receive refresh, so the counter reaches 2 and the EXT window follows de-assertion.

## RESETx Latch Feature

Another feature of ADI watchdogs is the ability to latch RESETx assertions. If a system sees a fault condition for longer than the longest possible RESETx hold time, it may be beneficial to continue to hold RESETx until the fault condition is removed. For example, if the SoC cannot service the watchdog, normal RESETx hold times will mean that RESETx would be de-asserted for the duration of the extended window and then will assert for hold time duration. This will mean the RESETx signal will toggle between asserted and de-asserted. Using the RESETx latch feature, the RESETx signal in this example will stay asserted until the SoC regains the ability to service the watchdog. This feature is also useful as an enable/disable for other signals. As an example, the watchdog latch feature can be used to disable all CAN bus communication if a fault is detected. All communication on the CAN bus will be stopped while the SoC addresses the system fault.

If the watchdog has not been through first power-up, the SoC will only need one valid service to de-assert the latched RESETx signal. After power-up, the SoC needs two consecutive valid services to de-assert the latched RESETx signal, regardless of whether the consecutive fault counter feature is used or not. This is described in Figure 11.

Figure 11. The example above shows the watchdog RESETx signal will latch until the watchdog is serviced again. It shows a fault due to refreshing during a closed window, but it is true for any RESETx fault. The duration of the RESETx hold time is effectively the time that the SoC requires to properly service the watchdog. Normal CLO/OPN windows occur during RESETx latch.

## Challenge/Response Watchdog

Another feature of some ADI watchdogs is the ability to use a challenge/response to service the watchdog through I2C. In some systems, it is not enough to just require the SoC to send a pulse. It may be beneficial to require the SoC to perform a task or computation to ensure the SoC is fully operational. This is where a challenge/response watchdog can meet this requirement. In a challenge/response service, there is a key-value register in the IC that must be read by the SoC. After having read the register, the SoC must use this value to compute the appropriate response. This response is then sent back to the IC over I2C. Once the register has been updated with the correct response, the watchdog has been serviced. The watchdog operates the same way as in a windowed setup with the only change being that the key register is updated rather than the watchdog being refreshed with a rising edge. The IC contains a linear-feedback shift register with a polynomial of x8+x6+x5+x4+1. This will shift all bits upward towards the MSb and insert the calculated bit as the new LSb. The SoC must calculate the response in this manner and send it back to the register in the IC. This is described in Figure 12.

Figure 12. Timing for challenge/response watchdogs are very similar to windowed watchdogs. The key register is read by the SoC via I2C and only needs to occur once. Once the SoC has read the key register, the next value is calculated using the previous one. The response is calculated and then written back to the register in the IC. On the next clock edge, the answer is confirmed and a new CLO/OPN window is started immediately.

In Table 1, a feature list is shown with several ADI ICs that contain watchdogs. ADI has several design calculators available for those wanting to learn more. Please contact ADI for more technical literature as well as datasheets for any of the parts listed.

Table 1. Feature List

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| MAX20478 | ASIL-D | x | x | x |  |  |
| MAX20480 | ASIL-D | x | x |  | x | x |

## Conclusion

As windowed watchdogs become more commonly implemented, it is important to develop a basic understanding of their operation. This application note covered several features of windowed watchdogs for the reader to develop a general knowledge regarding the MAX20478 and MAX20480 product families. These features include programmable extended windows, programmable RESETx hold times, single or consecutive watchdog fault assertions, and RESETx latch capability. With these features, designers have more freedom to incorporate more complex designs into their projects.