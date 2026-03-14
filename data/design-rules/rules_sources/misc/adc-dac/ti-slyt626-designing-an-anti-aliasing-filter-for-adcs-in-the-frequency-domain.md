---
source: "TI SLYT626 -- Designing an Anti-Aliasing Filter for ADCs in the Frequency Domain"
url: "https://www.ti.com/lit/an/slyt626/slyt626.pdf"
format: "PDF 5pp"
method: "pdfplumber"
extracted: 2026-03-02
chars: 17642
---

Analog Applications Journal Industrial
Designing an anti-aliasing filter for ADCs in
the frequency domain
By Bonnie C. Baker
Senior Applications Engineer
Introduction
Data acquisition (DAQ) systems are found across numer-
ous applications where there is an interest to digitize a
real-world signal. These applications can range from
measuring temperatures to sensing light. When developing
a DAQ system, it is usually necessary to place an anti-
aliasing filter before the analog-to-digital converter (ADC)
to rid the analog system of higher-frequency noise and
signals. Figure 1 shows the general circuit diagram for this
type of application.
Figure 1. Basic topology of a DAQ circuit For the following evaluation, the example system uses
the following throughout:
• Input signal bandwidth of 1 kHz (f )
SIGNAL
• Low-pass filter corner frequency of 10 kHz (f )
Op Amp ADC C
• SAR-ADC sampling frequency of 100 kHz (f ) S
LPF
or AAF • Dual operational amplifier, single-supply OPA2314
V
S
Determine maximum signal frequency (f ,
f ) and acceptable gain error
LSB
The first action is to determine the bandwidth of the input
signal (f ). Next, determine the magnitude of the
The DAQ system starts with a signal, such as a wave- SIGNAL
acceptable gain error from the LPF or AAF[1]. This gain
form from a sensor, V . Next is the low-pass filter (LPF)
error does not occur instantaneously at the frequency that
or anti-aliasing filter (AAF) and the operational amplifier
is chosen to be measured. Actually, at DC, this gain error
(op amp) configured as a buffer. At the output of the
is zero. The LPF gain error progressively gets larger with
buffer amplifier is a resistor/capacitor pair that drives the
frequency. An LSB error in dB equals
ADC’s input. The ADC is a successive-approximation-
20 × log [(2N – err)/2N],
converter ADC (SAR ADC).
where N is the number of converter bits and the whole
Typically, evaluations of this type of circuit consist of
number, err, is the allowable bit error. This error is found
the offset, gain, linearity, and noise. Another perspective
by examining the SPICE closed-loop gain curve.
in evaluation involves the placement of events in the
In this example, the signal bandwidth is 1 kHz and
frequency domain.
acceptable gain error is equal to one code, which is equiv-
There are six frequencies that impact the design of this
alent to 1 LSB. For a 12-bit ADC where err equals 1 and N
system:
equals 12, the gain error equals –2.12 mdB.
1. f – Input signal bandwidth
2. f – Filter frequency with a tolerated gain error
that has a desired number of least significant bits
(LSBs). It is preferable that f is equal to f
LSB SIGNAL
3. f – LPF corner frequency
C
4. f – Amplifier maximum full-scale output versus
PEAK
frequency
5. f – ADC sampling frequency
6. f – Amplifier gain bandwidth frequency
GBW
Figure 2 shows the general relationship between these
frequencies.
Texas Instruments 7 AAJ 2Q 2015
–
+
Figure 2. Basic relationship of f ,
f , f , and f
GBW PEAK C
Frequency (Hz)
f
SIGNAL f f f f
f C PEAK S GBW

Using a TINA-TI™ SPICE model to analyze a fourth-
Figure 3. Gain error at 1.04 kHz equals –2 mdB
order, 10-kHz low-pass Butterworth filter, the closed-loop
of a fourth-order, 10-kHz Butterworth LPF
gain response is shown in Figures 3 and 4. In both figures,
the location of the “b” cursor identifies the point where
gain error is –2 mdB (f = 1.04 kHz).
1-LSB
In Figure 3, the measurement window shows that the
marker at “b” is at 1.04 kHz. The window also shows the
–2 mdB[2] difference between frequency markers “a” and
“b” on the y-axis.
Figure 4 zooms in on the y-axis of the Butterworth
filter’s action before the filter passes through its corner
frequency (f ). The first observation of this response is
that the gain curve has a slight up-shoot before it begins
to slope downwards. This upward peak reaches a magni-
tude of approximately +38 mdB. This is a fundamental
characteristic of a fourth-order, Butterworth low-pass
filter.
If a higher gain error is acceptable, Table 1 shows the
change in f , versus the LSB value.
Table 1. LSB error versus f
LSB error (LSB) LSB error (dB) f
LSB Figure 4. Closed-loop gain response of a
1 –0.002 1.04 kHz fourth-order, 10-kHz Butterworth filter
2 –0.004 1.47 kHz
3 –0.006 1.82 kHz
4 –0.008 2.11 kHz
Filter corner frequency (f )
Note that the corner frequency (f ) of the low-pass filter
at the frequency where the attenuation of closed-loop
frequency response is –3 dB. If a fourth-order LPF is
chosen, f is approximately ten times higher than f .
C 1LSB
SPICE simulations with the WEBENCH® Filter Designer
allows this value to be determined quickly. When design-
ing a single-supply filter in the filter designer, select the
multiple-feedback (MFB) topology, which exercises the
amplifiers with a static DC common-mode voltage that is at
mid-supply. Figure 5 shows a circuit diagram of this fourth-
order, 10-kHz Butterworth LPF.
Figure 5. Fourth-order, Butterworth LPF with f = 10 kHz
V+1 Vcm1 R2_S1 R2_S2
11.3 kOhm 5.62 kOhm
125.0 mW 125.0 mW
V V+ = 5.0 V V V c = m 2.5 V C 91 1 0 _ .0 S p 1 F C 91 1 0. _ 0 S p 2 F
R1_S1
11.3 kOhm R3 _S1 V+_S1 R3_S2 V+_S2
125.0 mW 7.68 kOhm 2.87 kOhm
125.0 mW R1_S2 125.0 mW
5.62 kOhm
125.0 mW
Vcm_S1 A1_S1 Vcm_S2 A1_S2
OPA2314AIDR OPA2314AIDR
Vsignal
C2_S1 C2_S2
2.2 nF 12.0 nF
Texas Instruments 8 AAJ 2Q 2015

Define the amplifier’s gain bandwidth the mismatches between the amplifier rise and fall times
frequency (f ) and the responsivity of the amplifier at the peaks and
valleys of the sinusoidal input voltage swing.
The low-pass filter’s Q factor, gain (G), and corner
frequency (f ) determine the amplifier’s minimum allow- SAR-ADC sampling frequency
able gain bandwidth (f ). When finding the Q factor,
GBW The challenge now is to identify the sampling frequency of
first identify the type of filter approximation (Butterworth,
the SAR ADC. Given a 1-kHz maximum input signal, it is
Bessel, Chebyshev, etc.) and the filter order[2]. As previ-
imperative that the SAR ADC samples the signal more
ously specified, the corner frequency is 10 kHz. In this
than one cycle per second. Actually, over ten times is pref-
example, the filter approximation is Butterworth and the
erable. This implies that a 10-kHz sampling ADC will work.
gain is 1 V/V. Finally, this is a fourth-order filter. The
Additionally, it is important to eliminate signal-path
determination of the gain bandwidth of the amplifier is:
noise when possible. If the SAR ADC is converting at
f = 100 × Q × G × f (1) higher frequencies above the corner frequency of the filter,
GBW C
that portion of the noise will not be aliased back into the
In this system, f must be equal to or greater than
system. Consequently, a 100-kHz sampling SAR ADC
1.31 MHz (as verified by WEBENCH Filter Designer). The
meets the requirements.
gain bandwidth of the OPA2314 dual amplifier is 2.7 MHz.
If the sampling frequency is 100 kHz, the Nyquist
Amplifier’s maximum full-scale output frequency is 50 kHz. At 50 kHz, the frequency response of
In most applications, it is imperative that the amplifier is the low-pass filter is down by approximately 50 dB. This
capable of delivering its full-scale output. This may or may level of attenuation limits the impact on noise going
not be true. One check is to get a rough estimate from the through the system.
amplifier’s slew-rate specification.
Conclusion
A conservative definition of the maximum output
The development of a DAQ system in the frequency
voltage per frequency for an amplifier is equal to approxi-
domain can present interesting challenges. A system
mately f
PEAK
= SR/(V
PP
× p), where SR is the amplifier’s
consisting of a filter and a SAR ADC is usually evaluated
datasheet slew rate and V is the peak-to-peak specified
with the performance specifications of the DC- and
output swing. Note that the amplifier’s rise and fall times
AC-amplifier and the converter. This article, however,
may not be exactly equal. So the slew-rate specification of
evaluated the system’s signal path from a frequency
the datasheet is an estimate.
perspective.
The datasheet slew rate of the OPA2314 amplifier is
The important frequency specifications are the signal
1.5 V/µs and in the 5.5-V system, V equals 5.46 V. While
bandwidth, filter corner frequency, amplifier bandwidth,
the amplifier is in the linear region, the rail-to-rail output
and converter sampling speed. Even though the signal
with a 5.5-V power supply is equal to 5.46 V. Figure 6
bandwidth is small, 1 kHz, the required AAF corner
shows the tested behavior of the OPA2314 with an output
frequency should be 10 times higher than the signal band-
range that goes beyond the linear region of the amplifier.
width in an effort to reduce high-frequency gain errors.
The calculated maximum output voltage of the OPA2314
Additionally, the converter’s sampling frequency is higher
occurs at approximately 87.5 kHz. However, in Figure 6,
than expected in an effort to reduce complications caused
the maximum value with bench data is shown to be
by noise aliasing.
approximately 70 kHz. This discrepancy exists because of
References
Figure 6. OPA2314 maximum output voltage 1. Bonnie Baker, “Analog filters and specifications swim-
ming: Mapping to your ADC,” On Board with Bonnie, TI
Blog, Nov 5, 2014.
6
R L = 10 kΩ 2. Bonnie Baker, “Analog Filters and Specification
5 V IN = 5.5 V C L = 10 pF Swimming: Selecting the right bandwidth for your filter,”
On Board with Bonnie, TI blog, Nov 8, 2013.
)P 4
V P V IN = 3.3 V Related Web sites
g e
(
3 TINA-TI™ WEBENCH® tool:
a
olt
2
IN
= 1.8 V www.ti.com/tina-ti
Product information:
1 www.ti.com/OPA2314
Subscribe to the AAJ:
0
10 k 100 k 1 M 10 M www.ti.com/subscribe-aaj
Frequency (Hz)
Texas Instruments 9 AAJ 2Q 2015

Analog Applications Journal
TI Worldwide Technical Support
Internet
TI Semiconductor Product Information Center
Home Page
support.ti.com
TI E2E™ Community Home Page
e2e.ti.com
Product Information Centers
Americas Phone +1(512) 434-1560 Asia
Phone Toll-Free Number
Brazil Phone 0800-891-2616
Note: Toll-free numbers may not support
Mexico Phone 0800-670-7544 mobile and IP phones.
Australia 1-800-999-084
Fax +1(972) 927-6377 China 800-820-8682
Internet/Email support.ti.com/sc/pic/americas.htm Hong Kong 800-96-5941
India 000-800-100-8888
Europe, Middle East, and Africa
Indonesia 001-803-8861-1006
Phone
Korea 080-551-2804
European Free Call 00800-ASK-TEXAS
Malaysia 1-800-80-3973
(00800 275 83927)
New Zealand 0800-446-934
International +49 (0) 8161 80 2121
Philippines 1-800-765-7404
Russian Support +7 (4) 95 98 10 701
Singapore 800-886-1028
Taiwan 0800-006800
Note: The European Free Call (Toll Free) number is not active in
Thailand 001-800-886-0010
all countries. If you have technical difficulty calling the free call
number, please use the international number above. International +86-21-23073444
Fax +86-21-23073686
Fax +(49) (0) 8161 80 2045 Email tiasia@ti.com or ti-china@ti.com
Internet www.ti.com/asktexas Internet support.ti.com/sc/pic/asia.htm
Direct Email asktexas@ti.com
Important Notice: The products and services of Texas Instruments
Incorporated and its subsidiaries described herein are sold subject to TI’s
Japan
standard terms and conditions of sale. Customers are advised to obtain the
most current and complete information about TI products and services
Fax International +81-3-3344-5317
before placing orders. TI assumes no liability for applications assistance,
Domestic 0120-81-0036 customer’s applications or product designs, software performance, or
infringement of patents. The publication of information regarding any other
Internet/Email International support.ti.com/sc/pic/japan.htm company’s products or services does not constitute TI’s approval, warranty
or endorsement thereof.
Domestic www.tij.co.jp/pic
A021014
© 2015 Texas Instruments Incorporated. All rights reserved. E2E and TINA-TI are trademarks and WEBENCH is a registered trademark of Texas
Instruments. All other trademarks are the property of their respective owners.
SLYT626

IMPORTANT NOTICE
Texas Instruments Incorporated and its subsidiaries (TI) reserve the right to make corrections, enhancements, improvements and other
changes to its semiconductor products and services per JESD46, latest issue, and to discontinue any product or service per JESD48, latest
issue. Buyers should obtain the latest relevant information before placing orders and should verify that such information is current and
complete. All semiconductor products (also referred to herein as “components”) are sold subject to TI’s terms and conditions of sale
supplied at the time of order acknowledgment.
TI warrants performance of its components to the specifications applicable at the time of sale, in accordance with the warranty in TI’s terms
and conditions of sale of semiconductor products. Testing and other quality control techniques are used to the extent TI deems necessary
to support this warranty. Except where mandated by applicable law, testing of all parameters of each component is not necessarily
performed.
TI assumes no liability for applications assistance or the design of Buyers’ products. Buyers are responsible for their products and
applications using TI components. To minimize the risks associated with Buyers’ products and applications, Buyers should provide
adequate design and operating safeguards.
TI does not warrant or represent that any license, either express or implied, is granted under any patent right, copyright, mask work right, or
other intellectual property right relating to any combination, machine, or process in which TI components or services are used. Information
published by TI regarding third-party products or services does not constitute a license to use such products or services or a warranty or
endorsement thereof. Use of such information may require a license from a third party under the patents or other intellectual property of the
third party, or a license from TI under the patents or other intellectual property of TI.
Reproduction of significant portions of TI information in TI data books or data sheets is permissible only if reproduction is without alteration
and is accompanied by all associated warranties, conditions, limitations, and notices. TI is not responsible or liable for such altered
documentation. Information of third parties may be subject to additional restrictions.
Resale of TI components or services with statements different from or beyond the parameters stated by TI for that component or service
voids all express and any implied warranties for the associated TI component or service and is an unfair and deceptive business practice.
TI is not responsible or liable for any such statements.
Buyer acknowledges and agrees that it is solely responsible for compliance with all legal, regulatory and safety-related requirements
concerning its products, and any use of TI components in its applications, notwithstanding any applications-related information or support
that may be provided by TI. Buyer represents and agrees that it has all the necessary expertise to create and implement safeguards which
anticipate dangerous consequences of failures, monitor failures and their consequences, lessen the likelihood of failures that might cause
harm and take appropriate remedial actions. Buyer will fully indemnify TI and its representatives against any damages arising out of the use
of any TI components in safety-critical applications.
In some cases, TI components may be promoted specifically to facilitate safety-related applications. With such components, TI’s goal is to
help enable customers to design and create their own end-product solutions that meet applicable functional safety standards and
requirements. Nonetheless, such components are subject to these terms.
No TI components are authorized for use in FDA Class III (or similar life-critical medical equipment) unless authorized officers of the parties
have executed a special agreement specifically governing such use.
Only those TI components which TI has specifically designated as military grade or “enhanced plastic” are designed and intended for use in
military/aerospace applications or environments. Buyer acknowledges and agrees that any military or aerospace use of TI components
which have not been so designated is solely at the Buyer's risk, and that Buyer is solely responsible for compliance with all legal and
regulatory requirements in connection with such use.
TI has specifically designated certain components as meeting ISO/TS16949 requirements, mainly for automotive use. In any case of use of
non-designated products, TI will not be responsible for any failure to meet ISO/TS16949.
Products Applications
Audio www.ti.com/audio Automotive and Transportation www.ti.com/automotive
Amplifiers amplifier.ti.com Communications and Telecom www.ti.com/communications
Data Converters dataconverter.ti.com Computers and Peripherals www.ti.com/computers
DLP® Products www.dlp.com Consumer Electronics www.ti.com/consumer-apps
DSP dsp.ti.com Energy and Lighting www.ti.com/energy
Clocks and Timers www.ti.com/clocks Industrial www.ti.com/industrial
Interface interface.ti.com Medical www.ti.com/medical
Logic logic.ti.com Security www.ti.com/security
Power Mgmt power.ti.com Space, Avionics and Defense www.ti.com/space-avionics-defense
Microcontrollers microcontroller.ti.com Video and Imaging www.ti.com/video
RFID www.ti-rfid.com
OMAP Applications Processors www.ti.com/omap TI E2E Community e2e.ti.com
Wireless Connectivity www.ti.com/wirelessconnectivity
Mailing Address: Texas Instruments, Post Office Box 655303, Dallas, Texas 75265