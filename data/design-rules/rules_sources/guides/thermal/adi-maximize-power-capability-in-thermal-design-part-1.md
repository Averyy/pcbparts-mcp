---
source: "ADI -- Maximize Power Capability in Thermal Design Part 1"
url: "https://www.analog.com/en/resources/analog-dialogue/articles/maximize-power-capability-in-thermal-design-part-1.html"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 12410
---

## Abstract

With the increasing power density of electronic circuits and the presence of severe working environments such as high ambient temperatures, thermal performance has become a growing concern for monolithic
power products. This article delves into the general thermal concepts of power IC applications and provides quantified thermal analysis of various factors that influence the overall thermal performance.

## Introduction

Monolithic power IC data sheets typically specify two current limits: the maximum continuous limit and the peak transient limit. The peak transient current is constrained by the integrated power FETs, whereas the continuous current limit is influenced by thermal performance. The continuous current limit provided in the data sheet is derived from typical voltage conversion, room temperature, and standard demo board conditions. Implementing effective thermal design is crucial to ensure the IC can reliably handle the required current in specific operational environments.

This article is divided into two parts: Part 1 covers general thermal concepts and chip-level thermal considerations, while Part 2 addresses system-level (chip-on-board) factors impacting thermal
performance in power IC applications. The goal is to concisely summarize critical considerations for effective thermal design in power devices.

## Thermal Concepts and Parameters

For clarity, Table 1 provides analogies between steady-state electrical and thermal parameters.

Table 1. Parameters Conversion

|  |  |
| --- | --- |
| Electrical Domain | Thermal Domain |
| Voltage, V in (V) | Temperature, T in (K) or (°C) |
| Current, I in (A) | Power dissipation, P in (W) |
| Resistance, R in (Ω) | Thermal resistance, θ in (K/W) or (°C/W) |
| ΔVAB = VA – VB = I × RAB | ΔTAB = TA – TB = P × θAB |

From a steady-state perspective, current flows in the electrical domain from higher potential to lower potential, favoring paths with lower resistance. Similarly, in the thermal domain, thermal energy dissipates from areas of higher temperature to those of lower temperature, with greater energy dissipation occurring through paths characterized by lower thermal resistance.

In power IC applications, where the junction (die) is typically considered the heat source, the thermal equation in Table 1 can be adjusted as follows:

where:

* TJ is the IC junction temperature.
* TA is the ambient temperature.
* PLOSS is the IC power loss.
* θJA is the junction-to-ambient thermal resistance.

From Equation 1, either reducing IC power loss or thermal resistance could help to reduce ΔTJA and improve thermal performance.

## Thermal Dissipation Modes

There are three thermal dissipation modes:

1. **Thermal conduction:** Dissipation through direct contact.
2. **Thermal convection:** Dissipation carried by surrounding fluid in motion.
3. **Thermal radiation:** Dissipation in the form of electromagnetic waves.

As illustrated in Figure 1, in IC applications, thermal conduction typically refers to dissipation within the IC package and through the PCB copper. Thermal convection generally occurs between the IC or PCB surface and the surrounding air. Thermal radiation is ubiquitous as it does not require a medium.

Figure 1. Thermal dissipation in IC applications.

To calculate thermal resistance for different modes:

Thermal conduction:

where L is the material length or thermal conduction distance (m), k is the material thermal conductivity [W/(m × K)], and A is the material cross-section area (m2).

For thermal convection:

where h is the heat transfer coefficient [W/(K × m2)] and Acool is the cooling area (m2).

For thermal radiation:

where ε is the material thermal emissivity, σ is the Stefan-Boltzmann constant, Asurf is the surface area (m2), Tsurf is the surface temperature (K), and Ta is the ambient temperature (K).

From Equation 4, it is evident that thermal resistance in the radiation mode is highly dependent on temperature. As the temperature increases, θradi decreases, making it challenging to target a reduction in θradi in practical scenarios. Consequently, the following sections will focus on thermal resistance in conduction and convection modes.

## Simplified Thermal Model

As illustrated in Figure 2, a simplified thermal model is introduced to evaluate system-level (chip-on-board) thermal performance.

Figure 2. Simplified thermal model.

This model decomposes θJA into four distinct parameters:

* θJT (θJCtop): IC junction-to-case top thermal resistance.
* θJB: IC junction-to-board thermal resistance.
* θTA: IC case top-to-ambient thermal resistance.
* θBA: Board-to-ambient thermal resistance.

The relationship between these parameters is given by:

## Difference Between θ and ψ

Some data sheets list both θ and ψ values as thermal parameters, where θ refers to actual thermal resistance and ψ indicates the thermal characteristic value. For example, consider θJT and ψJT:

The primary difference is that Equation 6 assumes thermal energy dissipates solely through the IC case top, whereas Equation 7 assumes thermal dissipation occurs through all potential paths. Therefore, in real-world applications with natural cooling, it is more accurate to use ψJT instead of θJT to calculate the junction temperature:

It should be noted that ψJT is not a thermal resistance and has no physical meaning; it merely represents the numerical relationship between TJ and Tcasetop from a system perspective. Additionally, ψJT cannot be used to build a thermal model. A similar distinction applies to θJB and ψJB.

## IC Package Influence

Thermal dissipation within the power IC occurs primarily through conduction, as described by Equation 2. Table 2 provides the thermal conductivity values for materials utilized in IC packaging2,
which can be employed to assess thermal dissipation pathways in various packages. It is important to note that these values are also influenced by temperature.

Table 2. Thermal Conductivity of Different Materials in ICs

|  |  |  |
| --- | --- | --- |
| Material | Typical Usage | Thermal Conductivity (W/m × K) |
| Copper (25°C to 125°C) | Lead frame, copper pillar | 401 to 393 |
| Gold | Wire bond | 314 |
| Silicon (25°C to 125°C) | Die | 148 to 100 |
| SnPb | Solder | 50 |
| Silver Epoxy | Die attach | 2.09 |
| Epoxy Mold Compound | IC package mold | 0.72 |

## Bonding-Wire Package with Bottom Exposed Thermal Pad (ADI MSE)

Figure 3 illustrates the standard structure of the ADI MSE package, which comprises wire bonds and an exposed bottom pad. In conjunction with the data presented in Table 2, Table 3 is introduced to evaluate various thermal dissipation paths. The path exhibiting the lowest thermal resistance is identified as the die-die attach-bottom exposed pad configuration.

Figure 3. Typical structure of MSE package.

Table 3. Thermal Dissipation Paths in MSE

|  |  |  |  |
| --- | --- | --- | --- |
| Thermal Path | Distance L | Cross Section A | Thermal Conductivity k |
| Wire Bond | Long | Small | Very high |
| Die Attach | Very short | Large | Low |
| Exposed Pad | Short | Large | Very high |
| Epoxy Mold | Long | Large | Very low |

## Wafer Level Chip-Scale Package (WLCSP)

Figure 4 illustrates the standard structure of a WLCSP. Correspondingly, Table 4 provides detailed information on WLCSP, highlighting that the optimal thermal dissipation path, characterized by the lowest thermal resistance, is achieved through the die-Cu redistribution layer (RDL)-solder ball configuration.

Figure 4. Typical structure of WLCSP.

Table 4. Thermal Dissipation Paths in WLCSP

|  |  |  |  |
| --- | --- | --- | --- |
| Thermal Path | Distance L | Cross Section A | Thermal Conductivity k |
| Cu RDL | Short | Small | Very high |
| Solder Ball | Long | Large | High |
| Die Passivation | Very short | Large | Low |
| Dielectric | Very short | Large | Very low |

## Flip-Chip with Bottom Exposed Thermal Pad (ADI LQFN)

Figure 5 illustrates the standard structure of the ADI LQFN package. In conjunction with Table 5, it demonstrates that the dissipation path with the lowest thermal resistance is established
through the die-copper pillar-solder and the bottom exposed pad.

Figure 5. Typical structure of LQFN package.

Table 5. Thermal Dissipation Paths in LQFN

|  |  |  |  |
| --- | --- | --- | --- |
| Thermal Path | Distance L | Cross Section A | Thermal Conductivity k |
| Cu pillar | Short | Large | Very high |
| Solder | Very short | Large | High |
| Exposed pad | Short | Large | Very high |
| Epoxy mold | Very long | Large | Very low |

## θ and ψ Numerical Difference Based on Package Feature

As previously discussed, the thermal resistance, θ, is calculated under the assumption that heat dissipates in a specific direction, whereas the ψ value is determined based on natural cooling conditions. In encapsulated packages, the top epoxy mold compound exhibits relatively low thermal conductivity and a longer path for heat dissipation. Consequently, minimal thermal energy dissipates through the top, resulting in the Tcasetop being close to TJ. According to Equations 6 and 7, ψJT is significantly smaller than θJT. Conversely, since most of the thermal energy dissipates through the IC case bottom and the PCB, the ψJB value is typically close to θJB.1

## Exposed Die Package

Unlike encapsulated packages with an epoxy layer on top, the exposed die package has a thicker die. Figure 6 illustrates the typical structure of an LQFN package with an exposed die.

Figure 6. Typical structure of exposed die LQFN package.

The additional silicon on top reduces the thermal resistance (θJT) from the heat source to the case top, thereby enhancing thermal dissipation through the top of the package. However, under
natural cooling conditions, the exposed die package does not significantly enhance thermal performance due to other system-level factors affecting overall thermal resistance. Further details on the thermal benefits of the exposed die package will be provided in Part 2.

## Thermal Parameters on Data Sheet

The power IC data sheet typically lists multiple thermal parameters for reference, as illustrated in Figure 7. Due to the encapsulated IC package characteristics, θJCBOT is smaller than θJT (θJCTOP), and ψJT is significantly smaller than θJT (θJCTOP). Calculating TJ using θJT under natural cooling conditions can lead to substantial errors. It is also important to note that θJCBOT differs from θJB, as θJB represents the thermal resistance between the junction and the board, rather than the IC case bottom.3

Figure 7. Thermal parameters on data sheet.

Both JEDEC and demo board θJA values are presented in the example. The JEDEC board is constructed according to JEDEC standard 51-7 for measuring thermal parameters.4 Typically,
JEDEC boards do not have an optimized layout for thermal dissipation, resulting in a higher θJA compared to demo boards. Generally, the θJA on a JEDEC board reflects the thermal performance of the IC package itself, while the θJA on a demo board indicates the optimized system design value.

## Conclusion

Thermal conduction is the primary mode of heat dissipation within a power IC package. Depending on the thermal properties of the materials inside the package, some internal paths may exhibit lower thermal resistance. However, the actual dissipation paths are also influenced by system-level factors such as assembly, PCB design, air cooling, and the use of heatsinks. More details about these system-level factors will be provided in Part 2.

## References

1 “JESD51-12: Guidelines for Reporting and Using Electronic Package Thermal Information.” JEDEC Solid State Technology Association, May 2005.

2 “Thermal Analysis of Semiconductor Systems.” NXP.

3 “JESD51-8: Integrated Circuit Thermal Test Method Environment Conditions – Junction-to-Board.” JEDEC Solid State Technology Association, October 1999.

4 “JESD51-7: High Effective Thermal Conductivity Test Board for Leaded Surface Mount Packages.” JEDEC Solid State Technology Association, February 1999.