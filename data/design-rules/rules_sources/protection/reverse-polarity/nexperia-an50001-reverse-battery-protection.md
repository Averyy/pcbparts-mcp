---
source: "Nexperia AN50001 -- Reverse Battery Protection"
url: "https://assets.nexperia.com/documents/application-note/AN50001.pdf"
format: "PDF 18pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 19036
---

# Reverse battery protection in automotive applications

This application note gives details of four methods of reverse battery protection (RBP) that can be used in 12 V automotive systems.

## 1. Introduction

This aim of this application note is to help the reader gain an insight into how to protect 12 V automotive systems from being exposed to a reversed biased battery condition e.g. during maintenance where the battery leads may be reconnected in the opposite polarity.

Four methods of reverse battery protection (RBP) are discussed:

- Recovery rectifier (PN diode)
- Schottky rectifier
- P-channel MOSFET
- N-channel MOSFET

The dominant losses in RBP applications are due to conduction. The ordering of the components in the above list is important as it gives an indication of the least capable to most capable methods. In other words for a particular current flow Recovery rectifiers exhibit the greatest loss and N-channel MOSFETs the least loss. Table 1 summarises the key factors of each method.

**Table 1. Reverse battery positive rail protection options**

| Method | Example Device | Key Characteristics |
|--------|---------------|-------------------|
| Recovery rectifier (PN diode) | PNE20030EP in CFP5 | Low power, e.g. ~1 A supply; Lower cost; Device rating: 200 V, 3 A; High conduction loss |
| Schottky rectifier | PMEG045T150EPD in CFP15 | Low power, e.g. ~3 A supply; Slightly higher cost; Device rating: 45 V, 15 A; High leakage current, especially at higher temperatures |
| P-channel MOSFET | BUK6Y14-40P in LFPAK56 | Medium-high power, e.g. ~5.7 A supply; Device specification: 14 mOhm, 40 V, 110 W; High-side, cost competitive vs N-channel with charge pump |
| N-channel MOSFET | BUK7J1R4-40H in LFPAK56E | High power, e.g. ~25 A supply; Device specification: 1.4 mOhm, 40 V, 395 W; High-side: charge pump / gate boost voltage required; Low-side: very cost effective solution |

## 2. Recovery rectifier (PN diode) steady state conduction loss

Using a Recovery rectifier as a blocking diode can be considered as the simplest and most cost-effective way to realize a reverse battery protection (RBP) circuit. Inserting a Recovery rectifier in series with the load ensures that current can flow only when the battery is correctly connected. There is no control input needed, resulting in a low complexity and low component count. The usage of a Recovery rectifier for RBP is however compromised by the high forward voltage drop of the PN junction. This is the reason why Recovery rectifiers are only used for low power applications (load currents below ~1 A).

**Fig. 1.** Recovery rectifier RBP -- rectifier in series between Vbat+ and load.

Inrush current through the rectifier must be considered e.g. when the battery is switched into circuit and the bulk capacitance begins to charge. The peak current and duration of the pulse must be checked to ensure it does not exceed specification.

The steady state conduction losses, Ploss, can be calculated by using the forward voltage drop VF of the diode given for a steady state temperature of the PN junction and the load current Iload:

Ploss = Iload x VF(T)    (1)

The forward voltage drop of a PN junction decreases by -1.9 mV/K as the device heats up, lowering the losses at higher junction temperatures. Nevertheless the maximum total power dissipation of the Recovery rectifier has to be respected as indicated in the data sheet of the particular diode.

In the option examples above the PNE20030EP Recovery rectifier is identified as being well suited to this type of application. Using close to the example current in a simulation gives an indication of the expected forward voltage drop, junction and PCB temperatures, with the ambient temperature (on the product's case) of 105 degC.

**Fig. 2.** Recovery rectifier RBP simulation schematic.

See graphs of the simulation data results in Fig. 3, Fig. 4 and Fig. 5.

**Fig. 3.** Recovery rectifier simulation results - junction and mounting base temperatures. Tj = 167.2 degC, Tmb = 115.7 degC at steady state.

**Fig. 4.** Recovery rectifier simulation results - D1 anode-to-cathode voltage. VAK = 0.63 V at steady state.

**Fig. 5.** Recovery rectifier simulation results - load current. IL = 0.961 A at steady state.

## 3. Schottky rectifier steady state conduction loss

In order to overcome the high conduction losses of a Recovery rectifier, designers could use a Schottky rectifier for RBP. A Schottky device as blocking diode comes with the same advantages as a Recovery rectifier (least complexity). Thanks to its lower forward voltage drop it can be used for higher load currents up to approximately 3 A. However a Schottky rectifier comes with a higher leakage current due to its metal-semiconductor interface. The leakage current of a Schottky rectifier becomes significantly larger at higher junction temperatures, resulting in unwanted effects such as thermal runaway.

**Fig. 6.** Schottky rectifier RBP -- rectifier in series between Vbat+ and load.

Similarly to the Recovery rectifier, inrush current through the diode must be considered e.g. when the battery is switched into circuit and the bulk capacitance begins to charge. The peak current and duration of the pulse must be checked to ensure it does not exceed specifications.

Like in the case of the Recovery rectifier the conduction losses can be calculated by multiplying the temperature-dependent voltage drop with the load current.

Also for Schottky rectifiers the junction temperature must not exceed the specified maximum junction temperature which is 175 degC for automotive types.

In the option examples above the Schottky rectifier PMEG045T150EPD is identified as being well suited to this type of application. Using close to the example current in simulation gives an indication of the expected forward voltage drop, power dissipation, junction and PCB temperatures for an ambient temperature of 105 degC on the product's case.

**Fig. 7.** Schottky rectifier RBP simulation schematic.

See graphs of the simulation data results in Fig. 8, Fig. 9 and Fig. 10.

**Fig. 8.** Schottky rectifier simulation results - junction and mounting base temperatures. Tj = 147.7 degC, Tmb = 116.3 degC at steady state.

**Fig. 9.** Schottky rectifier simulation results - D1 anode-to-cathode voltage. VAK = 0.251 V at steady state.

**Fig. 10.** Schottky rectifier simulation results - load current. IL = 2.51 A at steady state.

## 4. P-channel MOSFET solution steady state conduction loss

In RBP applications the MOSFET can be considered as operating in two modes: "DIODE" mode and "MOSFET" mode.

During manufacture a parasitic PN junction diode is created within each MOSFET cell, the anti-parallel "diode" on the die actually comprises many parallel diodes distributed uniformly across the whole active die area.

**Fig. 11.** P-channel MOSFET RBP -- MOSFET in series between Vbat+ and load, source connected to battery positive.

When the MOSFET is not enhanced i.e. the gate terminal does not have a sufficiently negative voltage below its source to exceed its minimum threshold to turn-on then, with the battery connected correctly, it behaves as a forward biased DIODE. The power loss in the device is the product of the forward diode voltage and current flowing through it. The forward diode voltage decreases with increase in temperature by -1.9 mV/K. Therefore as the die heats the power dissipation reduces for a given current.

Once the gate-source threshold is reached the MOSFET becomes enhanced and switches from "DIODE" to "MOSFET" mode. Current then flows in the drain-source channel. The power loss is then the product of the on-state resistance RDSon and square of the current flowing in the channel.

To aid illustration a mix of data sheet calculation and simulation is used, the graphical results obtained from simulation are shown in Fig. 12 below:

**Fig. 12.** P-channel MOSFET RBP simulation schematic.

The P-channel simulation is initially set up with a slightly higher load current to the Schottky rectifier simulation.

To observe the device behaving as a diode look at the first portion of the junction temperature plot where the junction rises significantly above case temperature. Later observe the difference in power dissipation when the MOSFET is enhanced and switches from "DIODE" to "MOSFET" mode. If we consider a battery voltage of 13.5 V and VSD = 0.7 V typical at 25 degC, (values taken from the BUK6Y14-40P data sheet), driving a load resistance of 2.35 Ohm. The expected power dissipation would be somewhere around 0.7 V x (13.5 V / 2.35 Ohm) = 0.7 V x 5.75 A = ~4.02 W. It will be shown that the effects of temperature soon modify this expected result. This is true because products within vehicles soon rise above this notional outside air ambient of 25 degC and the impact on component behaviour must be considered.

**Table 2. BUK6Y14-40P source-drain voltage characteristics**

| Symbol | Parameter | Conditions | Min | Typ | Max | Unit |
|--------|-----------|-----------|-----|-----|-----|------|
| VSD | source-drain voltage | IS = -64.4 A; VGS = 0 V; Tj = 25 degC | - | -0.7 | -1.2 | V |

Temperatures above 125 degC are not uncommon dependent on product location within the vehicle and the ambient air temperature. However the focus here is on a product operating with a case temperature representing it being mounted on or near the engine jacket where the coolant temperature is expected to be around 105 degC.

Therefore what we see in the simulation is rather more accurate in that it accounts for the impedance presented by the diode and the drop in diode forward voltage as the die temperature rises. The load current is seen reduced to ~5.5 A and diode dissipation to ~3.07 W.

The mounting base temperature is that of the component's location on the PCB. In other words there will be some mounting base offset temperature expected dependent on how good the thermal linkage is between the component's mounting base (Tmb) and local pedestals connecting the component to the product's external case (local ambient) temperature of 105 degC.

The steady state condition considers the PCB thermal resistance Rth value dominant rather than the transient Zth value. Simulation uses a Rth(PCB) of 30 K/W and reduced thermal capacitance to allow this dominance. If the device were left in DIODE mode the simulation shows the notional temperature on the PCB would be very close to the maximum junction temperature specification of 175 degC and damage to the PCB surface may result even though a high temperature material may have been chosen for the application.

To illustrate the effect of DIODE mode self-heating the simulation delays enhancement to MOSFET mode for ~35 s, see Fig. 13. In this time for a dissipation of 3.07 W, simulation shows Tmb has risen to 168.13 degC and Tj to 172.2 degC.

**Fig. 13.** P-channel MOSFET RBP simulation results; Tj and Tmb. In DIODE mode (0-35 s): Tj = 172.2 degC, Tmb = 168.13 degC. After MOSFET enhancement (by 531 s): Tj = 126.47 degC, Tmb = 125.51 degC.

We can make a calculation based on using the data sheet Rth(j-mb) maximum value of 1.4 K/W, see Table 3. For a power dissipation of 3.07 W we should expect the junction temperature to rise by 3.07 W x 1.4 K/W = 4.29 degC above Tmb. This calculation yields a junction temperature of 172.42 degC which correlates reasonably well with the simulation.

**Table 3. BUK6Y14-40P thermal characteristics**

| Symbol | Parameter | Conditions | Min | Typ | Max | Unit |
|--------|-----------|-----------|-----|-----|-----|------|
| Rth(j-mb) | thermal resistance from junction to mounting base | - | - | 1.1 | 1.4 | K/W |

When the device has sufficient gate bias applied to enhance (turn-on) the MOSFET element the device behaves as having a resistance in parallel with the diode. Table 4 gives the typical and maximum values of the on-state resistance with a junction temperature of 25 degC.

**Table 4. BUK6Y14-40P drain-source on-state resistance characteristics**

| Symbol | Parameter | Conditions | Min | Typ | Max | Unit |
|--------|-----------|-----------|-----|-----|-----|------|
| RDSon | drain-source on-state resistance | VGS = -10 V; ID = -10.8 A; Tj = 25 degC | - | 11 | 14 | mOhm |

Looking at the simulation results shown in Fig. 13, by 531 seconds after enhancement MOSFET power dissipation and Tmb have dropped significantly to near steady state values of 683.77 mW and 125.51 degC respectively. The load current has increased slightly to ~5.69 A indicating a reduction in line impedance presented by the MOSFET to the battery.

If we make a power loss calculation based on 5.69 A load current and RDSon, the formula changes from DIODE power = V x I to MOSFET power = I^2 x R where I is drain current and R is RDSon, by substitution (5.694^2) x 14 mOhm = 453.9 mW. So why is there such a discrepancy with the 683.78 mW shown in the simulation? The above calculation was made using RDSon maximum @ 25 degC neglecting to factor in temperature.

RDSon has a positive temperature coefficient, see Fig. 14. The simulation models how RDSon changes from that 14 mOhm maximum value at 25 degC to a 1.51 typical multiplier @ 125 degC. Using 1.51 x 14 mOhm = 21.14 mOhm we can expect a power dissipation of (5.694^2) x 21.14 mOhm = 685.39 mW which correlates well with simulation.

Now if the power dissipation is multiplied by Rth(j-mb) we see a junction temperature of 685.39 mW x 1.4 K/W = 0.956 degC above the mounting base temperature; 125.51 degC + 0.956 degC = 126.4695 degC which correlates very well with the junction temperature result of 126.4705 degC seen in simulation.

**Fig. 14.** BUK6Y14-40P normalized drain-source on-state resistance as a function of junction temperature; typical values. Normalization factor a = 1.51 @ 125 degC.

The BUK6Y14-40P data sheet specifies the maximum permitted drain current at 25 degC and 100 degC, see Table 5.

**Table 5. BUK6Y14-40P limiting values**

In accordance with the Absolute Maximum Rating System (IEC 60134).

| Symbol | Parameter | Conditions | Min | Max | Unit |
|--------|-----------|-----------|-----|-----|------|
| ID | drain current | VGS = -10 V; Tmb = 25 degC | - | -64 | A |
| | | VGS = -10 V; Tmb = 100 degC | - | -46 | A |

The maximum drain current derating for temperature is given by the equation below, where maximum junction temperature Tj = 175 degC:

ID(Tmb) = ID(25 degC) x sqrt[(Tj - Tmb) / (Tj - 25 degC)]    (2)

Hence the maximum permissible drain current = sqrt[(175 - 125.51) / (175 - 25)] = 0.57 of full rated value @ 25 degC. This gives a value of 64 A x 0.57 = 36.8 A, so we have excellent margin.

If the threshold voltage falls to -1 V the device is guaranteed to be off, see Fig. 15 and the DIODE will be the only conduction path.

**Fig. 15.** BUK6Y14-40P sub-threshold drain current as a function of gate-source voltage. VDS = -5 V; Tj = 25 degC. Shows min, typ, max curves from VGS = 0 V to -4 V.

Hence losses when the device is in DIODE mode are large compared to when the device is operating in MOSFET mode making the MOSFET ideally suited to larger current, high temperature RBP applications.

## 5. N-channel MOSFET solution steady state conduction loss

The majority of the description of P-channel behaviour also applies to N-channel devices. The major difference being that to enhance an N-channel device into MOSFET mode its gate must be biased positively with respect to its source.

**Fig. 16.** N-channel MOSFET RBP -- MOSFET in series on high-side with charge pump providing gate boost voltage above Vbat+.

Importantly the N-channel MOSFET is capable of conducting larger currents as the RDSon value for a particular die size is much lower than that of a P-channel device. The significantly lower power dissipation in MOSFET mode means that the N-channel device is much better suited for applications demanding larger currents.

The N-channel simulation uses as an example 24.5 A rather than 5.69 A of the P-channel simulation. This is based on an ambient temperature of 105 degC and a near stable Tj of 140 degC. The power dissipated in the MOSFET is around 1.165 W at 140 degC. The circuit board material used is assumed to be suitable for such high temperatures ("normal" FR4 is capable to around 105 degC only, this is the ambient temperature here).

Referring to the simulation it can be seen that the source is at the battery positive voltage. Therefore to bias the gate above battery positive voltage a charge pump is normally required. To prevent the MOSFET being in linear mode where its RDSon would cause the device to dissipate more power than desirable, gate switching must be delayed until a satisfactory threshold voltage can be achieved.

In the simulation, there is a 30 second delay before the MOSFET switches on. During this time, the full load current is passing through the MOSFET body diode and the junction temperature reaches a peak of 175 degC, see Fig. 18. The power dissipated in the device is around 15 W. This demonstrates that by switching on the MOSFET, a significant power saving can be achieved.

**Fig. 17.** N-channel MOSFET RBP simulation schematic.

**Fig. 18.** N-channel MOSFET RBP simulation results; Tj. Peak Tj = 175.11 degC during body diode conduction (0-30 s), settling to ~140 degC after MOSFET enhancement.

## 6. Summary

The four key methods of reverse battery protection have been discussed.

Guidance has been provided to clarify the best approach to meet demands of the application while achieving optimal cost and performance.

Nexperia offers products which are very well suited for RBP applications.

Choose from very cost-effective Recovery rectifiers or Schottky rectifiers as solutions for lower power applications. Choose from P-channel and N-channel MOSFETs as the load current increases. Nexperia offers a range of thermally and electrically efficient device packages to support each area of application. To assist in that selection process electro-thermal simulation results are included in this application note and those simulations are available for the reader to explore via the Nexperia website interactive application note pages.

## 7. References

- [PNE20030EP data sheet](https://assets.nexperia.com/documents/data-sheet/PNE20030EP.pdf)
- [PMEG045T150EPD data sheet](https://assets.nexperia.com/documents/data-sheet/PMEG045T150EPD.pdf)
- [BUK6Y14-40P data sheet](https://assets.nexperia.com/documents/data-sheet/BUK6Y14-40P.pdf)
- [BUK7J1R4-40H data sheet](https://assets.nexperia.com/documents/data-sheet/BUK7J1R4-40H.pdf)
- [Nexperia interactive application notes](https://www.nexperia.com/applications/interactive-app-notes/)

## 8. Revision history

| Revision | Date | Description |
|----------|------|-------------|
| 1.0 | 2021-01-12 | Initial version |
