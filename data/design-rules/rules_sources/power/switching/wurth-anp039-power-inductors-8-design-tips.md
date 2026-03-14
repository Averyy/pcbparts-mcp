---
source: "Wurth ANP039 -- Power Inductors 8 Design Tips"
url: "https://www.we-online.com/components/media/o109038v410%20AppNotes_ANP039_PowerInductors8DesignTipps_EN.pdf"
format: "PDF 6pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 9206
---

Power Inductors
8 Design Tips
www.we-online.com

A practical guide for the selection of
power inductors for DC/DC converters
Switching frequency Inductor current ratings
The switching frequency of typical converter ICs on the market is in the range 100 kHz to The current load for power inductors can be calculated very accurately in terms of DC
2 MHz. First generation regulators operated in the range 30 kHz to 55 kHz. This leads to the current load and ripple current load (core losses) using the manufacturers’ simulation
following recommendations: software. The following approach can be chosen as a rough calculation:
Step-down regulator:
DESIGN TIP 1:
Nominal current of the inductor: I = I
N out
Maximum coil current: I = 1.5 x I
max N
Suitable core materials
Switching frequency < 100 kHz: Iron powder, ferrite, Superflux, WE-PERM
Step-up regulator:
Switching frequency 100-1000 kHz: Ferrite, Superflux, WE-PERM
Nominal current of the inductor: I = (U / U) I
N out in out
Switching frequency > 1000 kHz: Ferrite, WE-PERM
Maximum coil current: I = 2 x I
max N
DESIGN TIP 3:
Inductance value
Please observe the definitions for the data sheet specifications. The nominal
current for power inductors is usually linked to the specified self-heating with
If there is no application note or software available, inductance can be calculated using the DC current – here self-heating of +40°C is common at the nominal current.
following rule-of-thumb formula: According to semiconductor manufacturers‘ recommendations, the saturation
current is the point at which the inductance value has fallen by 10 %. Unfortu-
(U - U ) • (U + U)
in max out out D nately, this is not a standard value for power inductor data sheet specifications
Step-down regulator: L =
(U + U) • 0.3 • I • f and often leads to misinterpretation among users.
in max D out
(U + U - U ) • U2
out D in min in
Step-up regulator: L =
2 • 0.2 • I • (U + U )2 • f
out out D
DC resistance
with the ripple current factors 0.2 to 0.4 (selected as 0.2 and 0.3 in this example). I is the
out
operating current of the circuit to be supplied, U the output voltage and U the input vol- Once the required values for inductance L and inductor currents are calculated, you select
out in
tage, f is the switching frequency of the regulator IC. Standard values for inductance L can a power inductor with the minimum possible DC resistance. Here the demands are often
be selected on the basis of the calculated value. If, for example, the value 37.36 μH is ob- counteractive:
tained as the result – you would select the standard values 33 μH, 39 μH and possibly also
47 μH for testing. Small size, high energy storage density and low DC resistance.
Using suitable winding methods and new series, such as the Würth Elektronik WE-HCI and
DESIGN TIP 2:
WE-PDF flat-wire inductors, this ideal case is very close to realisation. The data sheet de-
finition must also be observed here:
Inductance value
Is the DC resistance specified as a typical value or as the max. value required for calcula-
 higher inductance – smaller ripple current
ting the circuit under worst case conditions?
 lower inductance – higher ripple current
The ripple current is essential in determining the core losses. Besides the
switching frequency, it is therefore an important parameter for minimising the DESIGN TIP 4:
power loss of the power inductor.
DC resistance with the same size
 higher inductance – higher DC resistance
 lower inductance – lower DC resistance
 same inductance for a shielded inductor – lower DC resistance
The DC resistance is essential in determining the wire heating losses; this is
another important parameter for minimising the power loss of the power inductor.
02 www.we-online.com

Type and EMC Output L-C filter
Magnetic shielded power inductors like WE-PD, WE-TPC, WE-DD or WE-HCI are recom- An L-C filter at the DC converter output is recommended if a low noise output voltage is
mended for EMC-critical applications. The shielding prevents uncontrolled magnetic cou- required. The components can be selected as follows [1]:
pling of the windings with neighbouring conductor tracks or components.
from DC converter
DESIGN TIP 5:
Use a magnetically shielded power inductor if at all possible. Do not route any
conductor tracks under the component and do not place any circuit boards di-
rectly above the component, as this could give rise to coupling via the air gap
remaining. Output L-C filter
Unshielded power inductors like WE-PD2 can be used for uncritical applications or for low
power circuits. Many packaging series can even be changed from shielded to unshielded DESIGN TIP 7:
versions while maintaining solder pad compatibility.
 Select cut-off frequency at 1/10 of the switching regulator frequency
 Select output capacitor (e.g. 22 µF)
DESIGN TIP 6:
 Calculate inductance
Advantage of magnetically shielded inductors of the same type: 1
L =
 higher A value, therefore lower DC resistances for the same inductance =
L (2 • π • f)2 • C
lower wire losses.
Disadvantage of magnetically shielded inductors of the same type:
 sslliigghhttllyy iinnccrreeaasseedd ccoorree lloosssseess dduuee ttoo aa llaarrggeerr ccoorree vvoolluummee.. GGiivveenn ccoorrrreecctt
ddiimmeennssiioonniinngg tthhee ccoorree lloosssseess rreemmaaiinn llooww..
03

Summary
DESIGN TIP 8:
The power inductor selection steps described are based on the design tips given in this
Ripple measurements article and are linked to the data sheet specifications. Not only the relevant design soft-
To properly measure ripple on either input or output of a switching regulator, a ware from the semiconductor manufacturer serves to reduce development times. With
proper ring in Tipp measurement is required. Standard oscilloscope probes the software Component Selector you get a tool which identifies very quick the right in-
come with a grounding clip, or a long wire with an alligator clip. Unfortunately, ductance for a buck or a boost converter. As a matter of course power inductors from
for high frequency measurements, this ground clip can pick-up high frequency Würth Elektronik are also listed in the leading semiconductor manufacturers‘ software
noise and erroneously inject it into the measured output ripple. solutions and hence they are immediately available for inclusion in the simulations. Cor-
respondingly assembled design kits help optimise prototypes. Magnetically shielded pow-
The standard evaluation board accommodates a home made version by provid- er inductors should be deployed for EMC-critical applications.
ing probe points for both the input and output supplies and their respective
grounds. This requires the removing of the oscilloscope probe sheath and
ground clip from a standard oscilloscope probe and wrapping a non-shielded
bus wire around the oscilloscope probe. If there does not happen to be any non
shielded bus wire immediately available, the leads from axial resistors will
work. By maintaining the shortest possible ground lengths on the oscilloscope
probe, true ripple measurements can be obtained.
References:
[1] Schramm, C.; DC-Wandler: Ausgangsspannung „säubern“
[DC converters: “clean up” output voltage]; ELEKTRONIK, Issue 23/2001. pg. 88ff
[2] Gerfer, A.; Rall, B.; Zenkner, H.: Trilogy of Magnetics, 4th extended edition
2009, Swiridoff Verlag, ISBN 978-3-89929-157-5
[3] Würth Elektronik, Component Selector, download at:
www.we-online.com/component-selector
[4] Linear Technology Switcher CAD III /LTspice IV, download at:
www.linear.com/ltspice
[5] Texas Instruments, Switcher Pro, download at:
www.ti.com/switcherpro
[6] Exar, Power Lab, download at:
www.exar.com/powerlab
[7] National Semiconductor, WEBENCH, download at:
wwwwww..nnaattiioonnaall..ccoomm//wweebbeenncchh
Probe connection
04

Switching regulators are becoming increasingly important thanks to their high efficiencies. The trend
is towards regulators with output voltages lower than 1 V, load currents up to 60 A and switching frequencies
up to 8 MHz. At the same time, users demand the smallest possible types.
Switching regulator design is supported by specialised software, for example from Würth Elektronik
(Component Selector), Texas Instruments (Switcher Pro for TPS60xxx, TPS40xxx and TPS54xxx), Exar
(Power Lab), National Semiconductor (WEBENCH) or Linear Technology (Switcher CAD/LTspice IV).
The relevant SMD power inductor design kits from Würth Elektronik offer quick access to a range of
components for the construction of in-house prototypes or for optimisation. But what has to be taken into
account when using power inductors?
05 www.we-online.com

YLF
.'5.3120
NEZNIRPRAKCENEID
Electronic & Electromechanical
Components
EMC Components
Power Magnetics
Power Modules
Signal & Communications
LEDs
Connectors
Switches
Assembly Technique
Power Elements
www.we-online.com · eiSos-hotline@we-online.com