---
source: "TDK InvenSense -- Analog and Digital MEMS Microphone Design Considerations"
url: "https://invensense.tdk.com/wp-content/uploads/2015/02/Analog-and-Digital-MEMS-Microphone-Design-Considerations.pdf"
format: "PDF 7pp"
method: "pdfplumber"
extracted: 2026-03-02
chars: 11495
---

Analog and Digital MEMS Microphone Design
Considerations
By Jerad Lewis
Microphones are transducers that convert acoustic pressure waves to electrical signals. Sensors have become more integrated with
other components in the audio signal chain, and MEMS technology is enabling microphones to be smaller and available with either
analog or digital outputs. Analog and digital microphone output signals obviously have different factors to consider in a design. I will
examine the differences and design considerations to consider when integrating analog and digital MEMS microphones into a
system design.
INSIDE A MEMS MICROPHONE
The output of a MEMS microphone does not come directly from the MEMS transducer element. The transducer is essentially a
variable capacitor with an extremely high output impedance in the gigaohm range. Inside the microphone package, the transducer’s
signal is sent to a preamplifier, whose first function is an impedance converter to bring the output impedance down to something
more usable when the microphone is connected in an audio signal chain. The microphone’s output circuitry is also implemented in
this preamp. For an analog MEMS microphone, this circuit whose block diagram is shown in Figure 1 is basically an amplifier with a
specific output impedance. In a digital MEMS microphone, that amplifier is integrated with an analog-to-digital converter (ADC) to
provide a digital output in either a pulse density modulated (PDM) or I2S format. Figure 2 shows a block diagram of a PDM-output
MEMS microphone and Figure 3 shows a typical I2S-output digital microphone. The I2S microphone contains all of the digital circuitry
that a PDM microphone has, as well as a decimation filter and serial port.
OUTPUT
AMPLIFIER OUTPUT
MEMS
TRANSDUCER
POWER
VDD GND
Figure 1. Typical Analog MEMS Microphone Block Diagram
CLK
ADC
DATA
POWER
MANAGEMENT
DDV DNG
PDM
MODULATOR
CHANNEL
SELECT
TCELES
R/L
AMPLIFIER
InvenSense Inc.
InvenSense reserves the right to change the detail 1745 Technology Drive, San Jose, CA 95110 U.S.A Document Number: WP
specifications as may be required to permit improvements +1(408) 988–7339 Revision: 1.0
in the design of its products. www.invensense.com Release Date: 12/31/2013

Figure 2. Typical PDM MEMS Microphone Block Diagram
FILTER
ADC Serial Data Clock
I2S
SERIAL Serial Data Output
PORT Word Clock
POWER HARDWARE
MANAGEMENT CONTROL
Figure 3. Typical I2S MEMS Microphone Block Diagram
A MEMS microphone package is unique among semiconductor devices, in that there is a hole in the package for the acoustic energy
to reach the transducer element. Inside this package, the MEMS microphone transducer and the analog or digital ASIC are bonded
together and mounted on a common laminate. A lid is then bonded over the laminate to enclose the transducer and ASIC. This
laminate is basically a small PCB that’s used to route the signals from the ICs to the pins on the outside of the microphone package.
Figures 3 and 4 show the inside of analog and digital MEMS microphones, respectively. In these pictures you can see the transducer
on the left and ASIC (under the epoxy) on the right side, both mounted on the laminate. The digital microphone has additional bond
wires to connect the electrical signals from the ASIC to the laminate.
DDV DNG
Document Number: WP Page 2 of 7
Revision: 1.0.
12/31/13

Figure 4. Transducer and ASIC of an Analog MEMS Microphone
Figure 5. Transducer and ASIC of a Digital MEMS Microphone
Document Number: WP Page 3 of 7

ANALOG MICROPHONES
An analog MEMS microphone’s output impedance is typically a few hundred ohms. This is higher than the low output impedance
that an op amp typically has, so you need to be aware of the impedance of the stage of the signal chain immediately following the
microphone. A low-impedance stage following the microphone will attenuate the signal level. For example, some codecs have a
programmable gain amplifier (PGA) before the ADC. At high gain settings, the PGA’s input impedance may be only a couple of kilo
ohms. A PGA with a 2 kΩ input impedance following a MEMS microphone with a 200 Ω output impedance will attenuate the signal
level by almost 10%.
1.8-3.3 V
R 1 R 2
V REF
0 . 1 µ F
V DD Op Amp V OUT
1 µ F
Analog O U T P U T
Microphone
10k? L
G N D V REF
Figure 6. Analog Microphone Connection to Non-Inverting Op Amp Circuit
The output of an analog MEMS mic is usually biased at a dc voltage somewhere between ground and the supply voltage. This bias
voltage is chosen so that the peaks of the highest amplitude output signals won’t be clipped by either the supply or ground voltage
limits. The presence of this dc bias also means that the microphone will usually be ac-coupled to the following amplifier or converter
ICs. The series capacitor needs to be selected so that the high-pass filter circuit that’s formed with the codec or amplifier’s input
impedance doesn’t roll off the signal’s low frequencies above the microphone’s natural low-frequency roll-off. For a microphone
with a 100 Hz low-frequency −3 dB point and a codec or amplifier with a 10 kΩ input impedance (both common values), even a
relatively-small 1.0 μF capacitor puts the high-pass filter corner at 16 Hz, well out of the range where it will affect the microphone’s
response. Figure 6 shows an example of this sort of circuit, with an analog MEMS microphone connected to an op amp in a non-
inverting configuration.
Digital Microphones
Digital microphones move the analog-to-digital conversion function from the codec into the microphone, enabling an all-digital
audio capture path from the microphone to the processor. Digital MEMS microphones are often used in applications where analog
audio signals may be susceptible to interference. For example, in a tablet computer, the microphone placement may not be near to
the ADC, so the signals between these two points may be run across or near Wi-Fi, Bluetooth or cellular antennae. By making these
connections digital, they are less prone to picking up this RF interference and producing noise or distortion in the audio signals. This
improvement in pickup of unwanted system noise provides greater flexibility in microphone placement in the design.
Digital microphones are also useful in systems that would otherwise only need an analog audio interface to connect to an analog
microphone. In a system that only needs audio capture and not playback, like a surveillance camera, a digital-output microphone
eliminates the need for a separate codec or audio converter and the microphone can be connected directly to a digital processor.
Of course, good digital design practices must still be applied to a digital microphone’s clock and data signals. Small-value (20-100 Ω)
source termination resistors are often useful to ensure good digital signal integrity across traces that are often at least a few inches
long (Figure 7). For shorter trace lengths, or when running the digital microphone clocks at a lower rate, it is possible that the
microphone’s pins can be directly connected to the codec or DSP, without the need for any passive components.
Document Number: WP Page 4 of 7

PDM MIC 1 CODEC
CLK CLOCKOUTPUT
DATA DATAINPUT
PCM MIC 2
CLK
DATA
Figure 7. PDM Microphone Connection to Codec with Source Termination
PDM is the most common digital microphone interface; this format allows two microphones to share a common clock and data line.
The microphones are each configured to generate their output on a different edge of the clock signal. This keeps the outputs of the
two microphones in sync with each other, so the designer can be sure that the data from each of the two channels is captured
simultaneously. At worst, the data captured from the two microphones will be separated in time by a half period of the clock signal.
The frequency of this clock is typically about 3 MHz, which would lead to an intrachannel time difference of just 16 μs – well below
the threshold that a listener will notice. This same synchronization can be extended to systems with more than two PDM
microphones by simply ensuring that the microphones are all connected to the same clock source and the data signals are all being
filtered and processed together. With analog microphones, this synchronization is left up to the ADC.
I2S has been a common digital interface for audio converters and processors for years, but it’s just recently being integrated into the
devices at the edges of the signal chain, such as a microphone. An I2S microphone has the same system design benefits as a PDM
microphone, but instead of outputting a high-sample rate PDM output, its digital data is output at a decimated baseband audio
sample rate. With a PDM microphone, this decimation happens in the codec or DSP, but with an I2S microphone this processing is
done directly in the microphone, which in some systems can eliminate the need for an ADC or codec entirely. An I2S microphone can
connect directly to a DSP or microcontroller for processing with this standard interface (Figure 8). Like with PDM microphones, two
I2S mics can be connected to a common data line, although the I2S format uses two clock signals, a word clock and a bit clock,
instead of the one for PDM.
Document Number: WP Page 5 of 7

VDD
Serial Data Clock
Word Clock
Serial Data Output
LEFT RIGHT
MICROPHONE MICROPHONE
GND
Figure 8. Stereo I2S microphone connection to a DSP
WHEN SIZE MATTERS
Generally, analog MEMS microphones are available in smaller packages than digital microphones. This is because an analog
microphone package needs fewer pins (typically three, vs. five or more for a digital microphone) and the analog preamp has less
circuitry than a digital preamp. This makes the analog preamp smaller than a digital preamp manufactured in the same fab
geometry. Consequently, in the most space-constrained designs, such as in many small mobile devices, analog microphones are
preferred in part because of their small size. An analog microphone can be in a package with dimensions 2.5 × 3.35 × 0.88 mm or
smaller, while PDM microphones often come in a 3 × 4 × 1 mm package, an increase of 62% in package volume. Figure 9 shows a
comparison of three bottom-port microphone packages. The smallest is the ADMP504, an analog microphone in the 2.5 × 3.35 ×
0.88 mm, the middle-sized microphone is the ADMP521, a PDM microphone in the 3 × 4 × 1 mm package, and the microphone in the
largest package is the ADMP441, an I2S microphone in a 3.76 × 4.72 × 1.0 mm package. This last microphone is in this larger package
to support its nine pins. Despite its larger size, a microphone like this is comparable in functionality to an analog microphone and an
ADC together, so the savings in PCB area if a converter is otherwise not needed outweighs the slightly larger microphone footprint.
Figure 9. Comparison of Microphone Package Sizes
kcolC
ataD
laireS
kcolC
droW
DSP
tupnI
ataD
laireS
Serial Data Clock
Word Clock
Serial Data Output
GND
Document Number: WP Page 6 of 7

Analog and digital MEMS microphones both have advantages in different applications. Considering the system’s size and component
placement constraints, electrical connections, and potential sources of noise and interference will lead to a well-informed decision
on which type of microphone is best for your design.
Author
Jerad Lewis is a MEMS microphone applications engineer at InvenSense, Inc. He has a BSEE from Penn State University, where he is
currently pursuing a M.Eng. in Acoustics.
Document Number: WP Page 7 of 7