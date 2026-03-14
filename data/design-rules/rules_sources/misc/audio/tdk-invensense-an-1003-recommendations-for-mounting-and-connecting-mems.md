---
source: "TDK InvenSense -- AN-1003: Recommendations for Mounting and Connecting MEMS Microphones"
url: "https://invensense.tdk.com/wp-content/uploads/2015/02/Recommendations-for-Mounting-and-Connecting-InvenSense-MEMS-Microphones.pdf"
format: "PDF 11pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 17655
---

Application Note
AN-1003
Recommendations for Mounting and
Connecting InvenSense MEMS Microphones
INTRODUCTION
The InvenSense bottom-ported MEMS microphones are high-performance acoustic transducers featuring an extended wideband
frequency response. Although the response of the microphone exhibits very little variation over its operating range, placement of the
microphone inside a device case may introduce changes to this response. This application note provides mounting recommendations for
minimizing the influence of packaging on the microphone performance in the final product. Electrical connections, codec interfaces,
and performance aspects are described, as well.
This application note discusses the following:
• Mechanical design considerations: printed circuit board (PCB) mounting, use of gaskets and spacers, and avoiding resonances
• Electrical connections: analog connections, digital data format, and codec interfaces
• Application-enabling performance aspects
MECHANICAL DESIGN CONSIDERATIONS
The InvenSense bottom-ported MEMS microphones are designed to be reflow soldered directly onto a PCB. A hole in the PCB is
required to admit the sound into the microphone package. In addition, the PCB with the microphone is placed in a housing that also
must have an opening connecting the microphone to the outside environment.
The PCB, together with the housing, forms elements of an acoustic circuit that can affect the frequency response of the microphone.
This application note provides recommendations to help ensure the best audio performance from the microphone.
SOUND PATH DESIGN
The microphone requires a path for the sound into the package through the bottom port. Due to the small size of the microphone
packages and their related features, the exact geometry of the sound path does not significantly influence the response of the
microphone. Because all dimensional references in acoustics are related to the wavelength of sound, the following formula for
converting frequency to wavelength is useful:
λ = c/f
where:
λ is the wavelength, m.
c is the speed of sound, approximately 340 m/sec.
f is the frequency, Hz.
For example, at 10 kHz, the wavelength is 34 mm (see Figure 1).
InvenSense Inc.
InvenSense reserves the right to change the detail 1745 Technology Drive, San Jose, CA 95110 U.S.A Document Number: AN-1003-00
specifications as may be required to permit improvements +1(408) 988–7339 Revision: 1.0
in the design of its products. www.invensense.com Release Date: 12/31/2013

10
1
0.1
0.01
125 250 500 1000 2000 4000 8000 16,000
FREQUENCY (Hz)
Figure 1. Wavelength of Sound vs. Frequency
PCB THICKNESS AND THE USE OF FLEXIBLE PCB
The performance of an InvenSense MEMS microphone is not affected by PCB thickness. The microphone can be mounted on a flexible
PCB using the guidelines listed in the microphone data sheet available at www.invensense.com and in the AN-1068 Application Note.
The flexible PCB with the microphone can be attached directly to the device housing with an adhesive layer. This mounting method
offers a reliable seal around the sound port, while providing the shortest acoustic path for good sound quality.
PCB SOUND HOLE SIZE
The response of an InvenSense MEMS microphone is not affected by the PCB hole size, as long as the hole is not smaller than 0.25
mm (0.010 inch) in diameter. A 0.5 mm to 1 mm (0.020 inch to 0.040 inch) diameter for the hole is typical. Take care to align the
hole in the microphone package with the hole in the PCB. The exact degree of the alignment does not affect the microphone
performance, as long as the holes are not partially or completely blocked.
AVOIDING RESONANCES
One acoustical structure that can influence sound quality, even when its dimensions are much smaller than the wavelength, is a
Helmholtz resonator. This resonator consists of a wide section forming an inner cavity and a narrow hole, or vent, to the outside. A
Helmholtz resonator may be formed when, for example, a wide gasket is used between the microphone PCB and the device case (see
Figure 2).
Figure 2. Helmholtz Resonator Example
This structure may result in a high-frequency response peak and should be avoided unless the product designer deliberately seeks such
a peak. To avoid this resonance, the gasket should be as small as possible, or the board should be placed directly against the device
case. When a longer acoustic path is required by industrial design constraints, the effective path diameter should be close in size or smaller
than the device case opening (the vent, as shown in Figure 3). Multiple small holes can be used in place of a single vent in the device
case.
)m(
HTGNELEVAW
VENT
DEVICE CASE
CAVITY GASKET
MEMS MICROPHONE HELMHOLTZ
RESONATOR
Page 2 of 11
Document Number: AN-1003-00
Revision: 1.0.
Rev Date: 12/31/13

VENT
DEVICE CASE
GASKET
MEMS MICROPHONE
Figure 3. Recommended Gasket Design Example
A good seal between the device case and the gasket and between the PCB and the gasket is important. The influence of the stiffness of
the gasket material on the overall microphone performance is negligible. Examples of gasket material include rubber, silicone,
neoprene, or closed-cell foam.
To calculate the Helmholtz resonance frequency, the following formula can be used:
c×D
f =
b
4 π×V×(L+ π×D/2)
f is the resonance frequency, Hz.
b
c is the speed of sound, approximately 340 m/sec.
D is the vent diameter, mm.
V is the cavity volume, mm3.
L is the vent length, mm.
The calculated resonance frequency can differ from the actual measurement results due to nonrigid gasket walls, leakages, and
other imperfections. Use the previous formula for an estimate of where in the frequency domain the resonance is likely to be located
rather than to establish an exact value.
Page 3 of 11

ELECTRICAL CONNECTIONS—DIGITAL MEMS MICROPHONES WITH PDM OUTPUT
CODECS SUPPORTING PDM DATA FORMAT
InvenSense has multiple MEMS microphones with a pulse-density modulated (PDM) output that connect directly to codecs or ADCs
with a dedicated PDM input. For the PDM format, a codec or processor typically provides the clock to the microphone, and up to two
microphone data output signals can be connected on the same signal line that is connected to the input of the codec. See Figure 4
for an example connection and refer to the data sheets for more details on the PDM microphone interface.
1.8V TO 3.3V
0.1µF
VDD CODEC
PDM CLK CLOCK OUTPUT
MICROPHONE
L/R SELECT DATA DATA INPUT
GND
1.8V TO 3.3V
VDD
PDM CLK
L/R SELECT DATA
Figure 4. Codec Interface Block Diagram
with Two PDM Microphones
CONNECTING TWO MICROPHONES TO A SINGLE DATA LINE
As shown in Figure 4, two microphones can be connected to a single DATA wire for stereo operation. This is possible because the DATA
output is in high impedance mode during half of every clock cycle. The L/R SELECT pin controls assignment of the microphone to the
left or right output channel (see
Table 1).
TABLE 1. L/R SELECT PIN ASSIGNMENT
L/R SELECT Connected To Selected Mode
Logical low (GND) Right microphone (DATA1)
Logical high (V ) Left microphone (DATA2)
DD
The DATA1 output bit is valid when the clock is low. The DATA2 output bit is valid when the clock is high. This means that the right
channel (DATA1) bit must be read on the low-to-high clock transition, and the left channel (DATA2) bit must be read on the high-to-low
clock transition. See Figure 5 for a suggested two-microphone connection schematic. Depending on the distance between the two
microphones and the length of the V trace, a separate 0.1 µF V bypass capacitor may be required per microphone.
DD DD
Page 4 of 11

DATA2 DATA
LEFT
L/R SELECT
CLK CLK
VDD VDD
GND GND
DATA1
RIGHT
MICROPHONE L/R SELECT
CLK
Figure 5. Two PDM Microphones Connected to a Single DATA Wire
WIRE LENGTH RECOMMENDATIONS
For out-of-product evaluations, a PDM microphone can be connected to a codec directly with wire lengths of up to 6 inches (15 cm).
When longer wires are required, a 20 to 100 Ω (depending on the trace’s characteristic impedance) source termination resistor is
recommended on the clock output of the codec to minimize overshoot or ringing of the clock signal. In some cases, a clock buffer
may be necessary to avoid performance degradation with excessively long wires. A schematic for a simple clock buffer is suggested in
Figure 6. This design uses a 74LVC2T45 bidirectional level translator as a buffer for the clock and data signals between the
microphone and codec.
1 8
2 7
A1 B1
3 6
A2 B2
4
Figure 6. PDM Microphone Buffer Schematic Suggestion
DNG
VDD VDD
C1 C2
0.10µF 0.10µF
U1 4
U2 CODEC
2 5
LR_SELECT DATA DATA INPUT
PDM MEMS MIC CLOCK OUTPUT
1 5
CLK GND DIR
3
74LVC2T45 DUAL
LEVEL SHIFTER/BUFFER
ACCV BCCV
Page 5 of 11

ELECTRICAL CONNECTIONS—ANALOG MEMS MICROPHONES
CONNNECTING ANALOG MEMS MICROPHONES TO A CODEC OR AN OP AMP GAIN STAGE
An InvenSense MEMS microphone with analog outputs can be connected to a dedicated codec microphone input (see Figure 7) or to
a high input impedance gain stage (see Figure 8). A 0.1 µF ceramic capacitor, placed close to the power supply pin of the
microphone, is used for testing and is recommended to adequately decouple the microphone from noise on the power supply. A DC-
blocking capacitor is required at the output of the microphone.
MICBIAS
CODEC
VDD OR
Analog 2.2µF ADC
Microphone MINIMUM
OUTPUT INPUT
Figure 7. InvenSense MEMS Microphone Connected to
a Codec or ADC Input
GAIN = (R1 + R2)/R1
R1 R2
VREF
Analog Amp VOUT
1µF
Microphone MINIMUM
OUTPUT
GND 10kΩ
VREF
Figure 8. InvenSense MEMS Microphone Connected to
an Op Amp Preamp Stage
CONNNECTING ANALOG OUTPUT MEMS MICROPHONES TO A DIFFERENTIAL INPUT
Routing low level, single-ended signals across circuit boards in the presence of electromagnetic interference may inject audible noise
into the signal chain. The use of balanced signal paths, a simple solution that is often overlooked, may result in significant reduction in
the noise pickup even when the microphone itself has a single-ended output.
The critical property of a balanced line is that both conductors have equal impedance with respect to ground1. This condition can be
replicated by using a reference conductor terminated into appropriate impedance. For example, many InvenSense MEMS
microphones have an output impedance of 200 Ω. A balanced signal path is created by adding a 200 Ω resistor at the ground
reference point of the microphone and routing a reference trace in parallel with the signal (see Figure 9). While not creating perfect
balanced-line conditions due to resistor value tolerances and other factors, this low cost circuit has been shown to reduce RFI noise in
real-life applications.
Page 6 of 11

MICBIAS
CODEC
VDD OR
MEMS 2.2µF ADC
MICROPHONE MINIMUM
OUTPUT LINN
GND LINP
R1 CM
200Ω
Figure 9. Connecting a Single-Ended Analog Output MEMS Microphone to a Differential Input
Note 1: Bill Whitlock, Balanced Lines in Audio Systems: Fact, Fiction, and Transformers, presented at the 97th Convention of the Audio Engineering Society, San
Francisco, CA, 1994 November 10–13; revised 1995 March 9.
Page 7 of 11

PERFORMANCE
LOW VIBRATION SENSITIVITY
The InvenSense MEMS microphones exhibit low vibration sensitivity due to very low surface density (mass per unit area) of the
membrane. The surface density of a membrane is a product of the membrane’s material density and thickness. The equivalent
sound pressure that is generated by axial vibration is then
p = ρ × t × a
a
p is the equivalent sound pressure, Pa.
a
ρ is the membrane material density, kg/m3.
t is the membrane thickness, m.
a is the vibration acceleration, m/sec2.
Due to a much lower surface density of a MEMS microphone membrane, the vibration signal generated by the MEMS micro-phone is
significantly lower than that of a typical electret condenser microphone (ECM). Table 2 provides examples of axial vibration sensitivity of
several types of microphones for reference. These calculated equivalent sound pressure levels are in excellent agreement with
experimental data where available.
TABLE 2. VIBRATION SENSITIVITY OF VARIOUS CONDENSER MICROPHONES AND AXIAL ACCELERATION
Microphone, Membrane Material, SPL at SPL at
Thickness 1 m/sec2, dB 1 g, dB
Bruel & Kjaer ½” mic, metal, 4 µm 65 85
A Typical ECM, Mylar 10 µm 57 77
InvenSense MEMS, p-Si, 0.9 µm 40 60
The low mechanical vibration sensitivity of the MEMS microphones enables better performance in many applications. One particular
application where low vibration sensitivity becomes critical is a microphone in a speakerphone with echo cancelling. A vibration
signal picked up by a microphone can significantly impair the performance of an acoustic echo cancellation algorithm. This reduction in
parasitic pickup applies to mechanical vibration only. When the vibration produces sound at the microphone location, the microphone
pickup of that sound is determined by its acoustic sensitivity.
FREQUENCY MAGNITUDE AND PHASE RESPONSE REPEATIBILITY
The InvenSense MEMS microphones have a frequency response with low variability from part to part due to high repeatability of the
semiconductor manufacturing process. This response consistency makes multi-microphone applications, such as beamforming, possible
without additional testing and matching of microphones. Figure 10 illustrates an example of overlaid magnitude responses of 40
randomly selected ADMP421 microphones. Due to the minimum phase nature of these tiny MEMS microphones, their phase
responses are directly related to the magnitude responses and, therefore, are tightly matched, as well (see Figure 11). Note that the
responses are normalized at 1 kHz.
Page 8 of 11

Figure 10. Magnitude Frequency Responses of Multiple ADMP421 Microphones
Figure 11. Phase Frequency Responses of Multiple ADMP421 Microphones
)Bd(
0
–3
–6
–9
–12
100 1k 10k
180
135
90
45
–45
–90
–135
–180
100 1k 10k
seergeD
Page 9 of 11

STABLE SENSITIVITY VS. TEMPERATURE
The sensitivity of the InvenSense MEMS microphones varies very little over temperature, a fraction of a decibel at most (see Figure
12). This improves performance of multi-microphone designs, especially in situations where temperature variations between
microphones result from internal heat sources such as power supplies.
5
4
2
1
–1
–2
–3
–4
–5
–40 –30 0 25 60 85
Figure 12. ADMP421 Sensitivity vs. Temperature (Typical)
)Bd(
TEMPERATURE (°C)
Page 10 of 11

Compliance Declaration Disclaimer:
InvenSense believes this compliance information to be correct but cannot guarantee accuracy or completeness. Conformity
documents for the above component constitutes are on file. InvenSense subcontracts manufacturing and the information contained
herein is based on data received from vendors and suppliers, which has not been validated by InvenSense.
Environmental Declaration Disclaimer:
InvenSense believes this environmental information to be correct but cannot guarantee accuracy or completeness. Conformity
documents for the above component constitutes are on file. InvenSense subcontracts manufacturing and the information contained
herein is based on data received from vendors and suppliers, which has not been validated by InvenSense.
This information furnished by InvenSense is believed to be accurate and reliable. However, no responsibility is assumed by
InvenSense for its use, or for any infringements of patents or other rights of third parties that may result from its use. Specifications
are subject to change without notice. InvenSense reserves the right to make changes to this product, including its circuits and
software, in order to improve its design and/or performance, without prior notice. InvenSense makes no warranties, neither
expressed nor implied, regarding the information and specifications contained in this document. InvenSense assumes no
responsibility for any claims or damages arising from information contained in this document, or from the use of products and
services detailed therein. This includes, but is not limited to, claims or damages based on the infringement of patents, copyrights,
mask work and/or other intellectual property rights.
Certain intellectual property owned by InvenSense and described in this document is patent protected. No license is granted by
implication or otherwise under any patent or patent rights of InvenSense. This publication supersedes and replaces all information
previously supplied. Trademarks that are registered trademarks are the property of their respective companies. InvenSense sensors
should not be used or sold in the development, storage, production or utilization of any conventional or mass-destructive weapons
or for any other weapons or life threatening applications, as well as in any other life critical applications such as medical equipment,
transportation, aerospace and nuclear instruments, undersea equipment, power plant equipment, disaster prevention and crime
prevention equipment.
©2013 InvenSense, Inc. All rights reserved. InvenSense, MotionTracking, MotionProcessing, MotionProcessor, MotionFusion,
MotionApps, DMP, and the InvenSense logo are trademarks of InvenSense, Inc. Other company and product names may be
trademarks of the respective companies with which they are associated.
©2013 InvenSense, Inc. All rights reserved.
Page 11 of 11