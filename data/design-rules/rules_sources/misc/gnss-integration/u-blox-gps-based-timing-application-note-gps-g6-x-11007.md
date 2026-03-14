---
source: "u-blox GPS-based Timing Application Note GPS.G6-X-11007"
url: "https://content.u-blox.com/sites/default/files/products/documents/Timing_AppNote_%28GPS.G6-X-11007%29.pdf"
format: "PDF 14pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 15454
---

GPS-based Timing
Considerations with
u-blox 6 GPS receivers
Application Note
Abstract
This document describes the time pulse feature for u-blox 6
modules and chipset designs. Special attention is paid to timing and
frequency applications using a u-blox 6 GPS receiver.
etarelecca
,etacinummoc
,etacol
www.u-blox.com

GPS-based Timing - Application Note
Document Information
Title GPS-based Timing
Considerations with
Subtitle
u-blox 6 GPS receivers
Document type Application Note
Document number GPS.G6-X-11007
Document status Preliminary
This document and the use of any information contained therein, is subject to the acceptance of the u-blox terms and conditions. They
can be downloaded from www.u-blox.com.
u-blox makes no warranties based on the accuracy or completeness of the contents of this document and reserves the right to make
changes to specifications and product descriptions at any time without notice.
u-blox reserves all rights to this document and the information contained herein. Reproduction, use or disclosure to third parties without
express permission is strictly prohibited. Copyright © 2011, u-blox AG.
GPS.G6-X-11007 Page 2 of 14

Contents
Contents .............................................................................................................................. 3
1 Introduction .................................................................................................................. 4
1.1 Time pulse ............................................................................................................................................ 4
1.2 Time mode ........................................................................................................................................... 4
1.2.1 Survey-in ....................................................................................................................................... 4
1.2.2 Single satellite navigation .............................................................................................................. 4
2 Measurement definitions ............................................................................................ 5
2.1 Accuracy of time pulse ......................................................................................................................... 5
2.2 Frequency accuracy............................................................................................................................... 7
2.3 Frequency stability ................................................................................................................................ 7
2.3.1 Allan deviation .............................................................................................................................. 7
2.3.2 Phase noise ................................................................................................................................... 8
3 Examples ..................................................................................................................... 10
3.1 Example 1 ........................................................................................................................................... 10
3.2 Example 2 ........................................................................................................................................... 10
4 Conclusions ................................................................................................................. 12
5 Related documents ..................................................................................................... 13
Revision history ................................................................................................................ 13
Contact .............................................................................................................................. 14
GPS.G6-X-11007 Preliminary Page 3 of 14

1 Introduction
GPS receivers can be used to provide highly accurate time information. For this reason the u-blox 6 Timing GPS
module includes a specific Time Mode, which assumes a known antenna position and calculates a time pulse
synchronized to either GPS or UTC (Coordinated Universal Time) [1]. This application note relates to the time
pulse feature of u-blox 6 modules and chipset designs.
1.1 Time pulse
The base of all timing and frequency applications is the one pulse per second (1PPS) time pulse, which is
synchronized to GPS time or UTC. For LEA-6T modules two time pulse outputs are available, which are
individually configurable from 1/60 Hz up to 10 MHz using the UBX-CFG-TP5 message [2].
A high frequency time pulse above 1 MHz requires 50 Ω conditions for transmission without
degradation due to effects of cable capacitance.
1.2 Time mode
The following modes are available with LEA-6T modules.
1.2.1 Survey-in
If the position is known, the receiver can provide an accurate time solution by tracking only one satellite. For an
unknown position, the receiver needs a minimum of four satellites to calculate a position fix and to solve for a
timing solution. This is known as survey-in and can be chosen using the UBX-CFG-TMODE2 message.
It is recommended to use survey-in only for non-moving platform applications. For optimal performance
a known fixed position of the antenna should be used.
1.2.2 Single satellite navigation
Single satellite navigation can be useful under poor GPS reception conditions. Time information can be heavily
degraded due to multipath effects. To avoid such degradation choose an antenna that primarily receives
satellites with high elevation angles. Using the UBX-CFG-NAV5 message, low elevation angle satellites can be
ignored. Furthermore the number of satellites can be reduced using the UBX-CFG-NAVX5 message.
When adjusting the time pulse the user should take the electrical delay into account, due to the cable length
connecting the antenna with the GPS receiver. In addition an arbitrary user delay can be considered to calibrate
the time pulse to a given reference time.
Note, that the time pulse is derived internally from a 48 MHz clock, which causes a jitter to the time pulse [3].
The UBX-TIM-TP message provides the quantization error in nanoseconds to the next pulse, which can be used
to compensate the timing solution.
For more information, consult the Receiver Description including Protocol Specification [4] and the
Firmware 7.01 fur u-blox 6 [5].
The quantization error is only valid if a 1 Hz time pulse is used.
GPS.G6-X-11007 Preliminary Page 4 of 14

2 Measurement definitions
2.1 Accuracy of time pulse
Configuration of the time pulse depends on the application. A low time pulse frequency e.g. 1 Hz is best for
exact timing measurements. The accuracy of the time pulse can be measured in terms of a difference to a
reference time. The reference time should be as accurate as possible and is normally generated by a GPS
receiver, which is synchronized to a rubidium clock. A typical measurement setup is shown in Figure 1.
Figure 1: Measurement setup at u-blox AG
The timing error consists of three parts:
• A constant error caused by delay from the antenna cable and from the receiver.
• A short-time error from pulse to pulse related to generation and quantization of the time pulse.
• The position uncertainty caused by multipath effects or caused by different transit times to the ionosphere.
The first error term can be removed by assuming a certain cable delay in the configuration table. The second
error term relating to the quantization error can be compensated by using the UBX-TIM-TP message. The last
error term related to the multipath effect can be minimized by using an antenna with suitable antenna pattern
[6] in conjunction with single satellite navigation.
Figure 2 and Figure 3 shows the accuracy of the u-blox time pulse with and without compensation. The
integration time was 1 s and the samples were averaged over 6 h. Please note that the average value is -2.35 ns,
which could be set to zero by adding a user delay of the same but positive value. The sampling deviation of
6.7 ns denotes the accuracy of time pulse.
GPS.G6-X-11007 Preliminary Page 5 of 14

Figure 2: Accuracy of time pulse without compensation
Figure 3: Accuracy of time pulse with compensation
Note that the accuracy can also be specified in terms of an RMS value, which can also be calculated using the
mentioned statistic. The LEA-6T Data Sheet [2] provides an RMS value of 30 ns without compensation and 15 ns
GPS.G6-X-11007 Preliminary Page 6 of 14

with compensation. This is because imperfect satellite constellations can degrade the timing solution and result
in somewhat less accuracy. Using UBX-NAV-DOP message indicates the quality of your solution. A time dilution
of precision less than 3 means high precision and a factor greater than 10 indicates low precision.
2.2 Frequency accuracy
A faster time pulse e.g. 8 kHz or more is used for accurate frequency measurements. Frequency accuracy is
calculated in two steps. First the difference to a reference frequency is measured as shown in Figure 4. Than the
average value of 4.965e-7 Hz is divided by its reference frequency, which is in this example 8 kHz. This results in
a frequency accuracy of 6.2e-11 or 0.062 ppb.
Figure 4: Frequency difference of an 8kHz time pulse
2.3 Frequency stability
Frequency stability depends on the observation time and is measured in terms of Allan deviation or phase noise.
u-blox time pulse shows excellent long-term stability and reasonable short-term stability, but it is not designed
for improved phase noise performance for reasons that will be discussed in the next sections.
2.3.1 Allan deviation
Allan deviation is typically measured for observation or integration intervals from 1 s to some 1000 s or even
more. It is a time domain fractional frequency measure which was initially used to characterize oscillators
suffering from aging and ambient effects. In this instance the Allan deviation, which is the square root of the
Allan variance, provides better results than the standard deviation calculated from a set of data. A typical curve is
shown in Figure 5. An observation interval around 1 s refers to short-term stability and above some seconds
refers to long-term-stability. Because of the fractional frequency usage Allan deviation is dimensionless and
plotted versus the observation interval.
GPS.G6-X-11007 Preliminary Page 7 of 14

Figure 5: Allan deviation of an 8kHz time pulse
2.3.2 Phase noise
Short-term stability with uncertainties lower than 0.1 s is measured in terms of phase noise. In practice, the noise
power in a single sideband over a bandwidth of 1 Hz with respect to the frequency offset from the carrier is
measured to characterize phase noise. If related to the total signal power, phase noise is given in dBc/Hz. Figure
6 shows the phase noise performance of the baseband PLL, which is used to generate the time pulse.
Figure 6: Phase noise of the baseband PLL
GPS.G6-X-11007 Preliminary Page 8 of 14

Since the time pulse is derived from a 48 MHz clock it suffers from an additional jitter due to quantization or
granularity of the clock. Thus phase noise performance of the time pulse is further degraded compared to Figure
6.
Be aware, that the time pulse is not designed for improved phase noise specification. If necessary the
customer must add an external circuit e.g. a phase lock loop.
Figure 7 shows an example of how to improve phase noise performance. A phase lock loop is added to the time
pulse output to synchronize the time pulse to an external oscillator. If additional holdover performance is
required an oven-controlled oscillator should be used instead of a temperature-controlled oscillator.
Figure 7: External circuitry to improve phase noise performance
GPS.G6-X-11007 Preliminary Page 9 of 14

3 Examples
3.1 Example 1
The first example shows a 1 MHz time pulse when the receiver is locked to GPS time. Without a lock to GPS time
the time pulse output can be configured anyhow and is set to 0 V in this example. Figure 9 shows the
configuration GUI on u-center and a plot of the time pulse. The edges of each pulse are aligned to GPS time.
Figure 9: Configuration and screenshot of example 1
3.2 Example 2
The second example shows an 8 MHz time pulse when the receiver is locked to GPS time. Figure 10 shows the
configuration GUI and a plot of the time pulse. Note that there is almost no jitter on the clock edges, because
48 MHz divided by 8 MHz results in an integer ratio. For this reason a 10 MHz time pulse is less stable than an
8 MHz time pulse. A comparison of an 8 MHz and 10 MHz time pulse is shown in Figure 11 and Figure 12.
GPS.G6-X-11007 Preliminary Page 10 of 14

Figure 10: Configuration and screenshot of example 2
Figure 11: 8MHz time pulse without jitter Figure 12: 10MHz time pulse with jitter
GPS.G6-X-11007 Preliminary Page 11 of 14

4 Conclusions
The LEA-6T module provides two time pulse outputs which can be individually configured. In conjunction with
the Time Mode these outputs provide excellent long-term accuracy and stability for many timing and frequency
applications. However, short-term stability is limited because of jitter due to quantization or granularity of the
time pulse. For improved phase noise and holdover requirements an additional phase lock loop should be
considered.
GPS.G6-X-11007 Preliminary Page 12 of 14

5 Related documents
[1] GPS Essentials of Satellite Navigation, Docu. No GPS-X-02007
[2] LEA-6 Data Sheet, Docu. No GPS.G6-HW-09004
[3] UBX-G6010, UBX-G6000/UBX-G0010 Data Sheet, Docu No GPS.G6-X-09004
[4] u-blox 6 Receiver Description including Protocol Specification, Docu. No GPS.G6-SW-10018
[5] Release Notes Firmware 7.01 for u-blox 6, Docu. No GPS.G6-SW-10024
[6] GPS Antennas Application Note, Docu. No GPS-CS-06000
For regular updates to u-blox documentation and to receive product change notifications please register
on our homepage (www.u-blox.com).
Revision history
Revision Date Name Status / Comments
03/03/2011 ffel Initial release
GPS.G6-X-11007 Preliminary Page 13 of 14

Contact
For complete contact information visit us at www.u-blox.com
u-blox Offices
North, Central and South America Headquarters Asia, Australia, Pacific
Europe, Middle East, Africa
u-blox America, Inc. u-blox Singapore Pte. Ltd.
Phone: +1 (703) 483 3180 u-blox AG Phone: +65 6734 3811
E-mail: info_us@u-blox.com Phone: +41 44 722 74 44 E-mail: info_ap@u-blox.com
E-mail: info@u-blox.com Support: support_ap@u-blox.com
Regional Office West Coast:
Support: support@u-blox.com
Phone: +1 (703) 483 3184 Regional Office China:
E-mail: info_us@u-blox.com Phone: +86 10 68 133 545
E-mail: info_cn@u-blox.com
Technical Support: Support: support_cn@u-blox.com
Phone: +1 (703) 483 3185
E-mail: support_us@u-blox.com Regional Office Japan:
Phone: +81 3 4360 5343
E-mail: info_jp@u-blox.com
Support: support_jp@u-blox.com
Regional Office Korea:
Phone: +82 2 542 0861
E-mail: info_kr@u-blox.com
Support: support_kr@u-blox.com
Regional Office Taiwan:
Phone: +886 2 2657 1090
E-mail: info_tw@u-blox.com
Support: support_tw@u-blox.com
GPS.G6-X-11007 Preliminary Page 14 of 14