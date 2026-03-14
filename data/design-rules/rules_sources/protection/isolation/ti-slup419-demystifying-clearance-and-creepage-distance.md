---
source: "TI SLUP419 -- Demystifying Clearance and Creepage Distance"
url: "https://www.ti.com/document-viewer/lit/html/SLUP419"
format: "HTML"
method: "ti-html"
extracted: 2026-02-16
chars: 35295
---

Power Supply Design Seminar

# Demystifying Clearance and Creepage Distance for High-Voltage End Equipment

# Abstract

*Achieving the highest possible
power density while still maintaining safety and design guidelines requires
more careful high-voltage printed circuit board (PCB) spacing and integrated
circuit (IC) package selection. This topic summarizes the considerations and
provides a cheat sheet for popular end equipment, including
telecommunication, server and wireless infrastructures; motor drives, solar
inverters and charging piles; consumer AC/DC applications; and electric
vehicles and hybrid electric vehicles.*

# 1 Introduction

High-voltage PCB spacing and IC package
selection are increasingly important to achieve the highest possible power density while
still complying with safety and design guidelines. Challenges come from multiple angles,
however. As a designer, you must understand:

* Many technical terms, as well as
  their impact on creepage and clearance.
* The distinction between a normal
  operating transient voltage and a nonrecurring transient voltage.
* The impact of the equipment’s
  location relative to the primary-side energy source.
* Multiple industry standards
  addressing creepage, clearance and PCB spacing, where some standards are
  complimentary, some are redundant and some are conflicting.
* Different industry standards for
  different end-equipment types.
* Scenarios of safety isolation from
  the International Electrotechnical Commission (IEC), Underwriters Laboratories (UL)
  or Deutsche Institut für Normung (DIN) Verband der Elektrotechnik (VDE) to protect
  human safety vs. functional isolation to maintain proper operation.
* Other considerations such as use-case
  altitude, pollution degree, IC material group, PCB conformal coating, PCB cutouts
  and routine transient tests.

In this paper, we will introduce technical
terms with their physical meanings, and explain the relationships to and influences on
creepage and clearance. We will then provide guidelines and a flowchart with
step-by-step instructions to determine proper creepage and clearance with a structured
methodology.

# 2 Definitions

## 2.1 Creepage and Clearance

Creepage is the shortest distance
along the surface of a solid insulation material between two conductive parts, as
shown in [Figure 1](#FIG_EBW_K3B_MZB). This distance is dimensioned for a pollution degree, material group and working
voltage, which is the highest root-mean-square (RMS) voltage to which the insulating
material may be subjected. It is defined to ensure that no flashover or breakdown of
insulation will occur. Besides working voltage, the factors that most affect
creepage are pollution, humidity and condensation.

Clearance is the shortest distance in
air between two conductive parts, as shown in [Figure 2](#FIG_T4Z_L3B_MZB). This distance is dimensioned in order to prevent air ionization or arcing during
any required transient overvoltage. The factors that matter the most for clearance
are air pressure (altitude) and pollution. There is a multiplication factor for
altitudes greater than 2,000 m, which we will cover in [Methodology to Determine Creepage,
Clearance and High-Voltage PCB Spacing Requirements](GUID-8A5B41AA-CD97-49C7-8219-E21382BB359A.html#GUID-8A5B41AA-CD97-49C7-8219-E21382BB359A).

Figure 1 Creepage.

Figure 2 Clearance.

Creepage handles long-term
steady-state working voltages, while clearance handles short-term transients that
are a few milliseconds or less. There is no physical relationship between the two,
but the creepage distance cannot be less than the clearance distance. It is
important to maximize both creepage and clearance whenever possible while
considering the trade-offs of size and cost.

It is also important to note that in
some cases where the corner pins are close to the edge of the package, the shortest
creepage distance can be across the side instead of the top or bottom, as
illustrated in [Figure 3](#FIG_KRJ_P3B_MZB).

Figure 3 Example where the shortest
creepage distance is across the side rather than the top.

It is also possible for creepage and
clearance to be the same. In [Figure 4](#FIG_GVY_R3B_MZB), for example, depopulating the middle pins of the UCC21551-Q1 dual-channel
isolated gate driver increases the creepage and clearance.

Figure 4 Functional isolation example
where creepage and clearance are the same.

## 2.2 Material Group and Comparative Tracking Index

The comparative tracking index (CTI)
categorizes insulating materials based on the voltage at which electrical breakdown
occurs. The CTI rating is determined by a test that applies a voltage to a material
on which there are 50 drops of water, contaminated with 0.1% ammonium chloride. The
CTI rating is the maximum voltage that the material can withstand during this test
where there is less than 0.5 A of tracking current flowing [[1](GUID-5676A8B2-9274-422A-B7B2-E7E9C4825B07.html#GUID-5F794665-53F6-4232-BF6C-51A89BEC2C1E)]. [Table 1](#TABLE_HRJ_PJB_MZB) shows the categories of insulating materials based on the CTI. These material
groups can help you determine the required creepage distance for a given insulation
requirement, as discussed in [Methodology to Determine Creepage,
Clearance and High-Voltage PCB Spacing Requirements](GUID-8A5B41AA-CD97-49C7-8219-E21382BB359A.html#GUID-8A5B41AA-CD97-49C7-8219-E21382BB359A).

Table 1 Material groups based on the
CTI.

| Material group | CTI range (VRMS) |
| --- | --- |
| I | 600 ≤ CTI |
| II | 400 ≤ CTI < 600 |
| IIIa | 175 ≤ CTI < 400 |
| IIIb | 100 ≤ CTI < 175 Or if not specified |

Most FR4 materials used in PCB
fabrication are rated for material group IIIa. All Texas Instruments isolation
products are material group I in order to help reduce the package size and PCB
footprint required.

## 2.3 Pollution Degree

The next important parameter for determining required creepage and clearance
distances is the pollution degree. Pollution degree environments are classified into
four categories [[2](GUID-5676A8B2-9274-422A-B7B2-E7E9C4825B07.html#GUID-791FDC2D-F7F6-447F-A56A-B00947A9EC4D)]:

* Pollution degree 1: There is no pollution, or only dry, nonconductive pollution.
  These systems are sealed to exclude dust and moisture, or the PCB uses conformal
  coating so that components will not be subject to humidity- or
  temperature-related condensation.
* Pollution degree 2: The environment can temporarily become conductive from
  occasional condensation. Common examples of environments classified by pollution
  degree 2 are labs, offices and enclosures for servers, telecommunications
  equipment and wireless infrastructures.
* Pollution degree 3: The environment is subject to conductive pollution, or
  nonconductive pollution that can become conductive from expected condensation.
  Common examples are industrial applications, farming equipment and unheated
  factory rooms.
* Pollution degree 4: Continuous conductivity occurs from conductive dust, rain or
  other wet conditions. This is common for outdoor applications.

## 2.4 Transient Overvoltage Category

Another factor used in determining the
required clearance is the transient overvoltage category, which categorizes
equipment based on where it is connected relative to the mains voltage. This voltage
level is not categorized by math, but rather by a probabilistic implication based on
the equipment’s location.

[Figure 5](#FIG_JRF_HKB_MZB) is a
diagram of a residential building with examples of locations labeled for different
transient overvoltage categories. The four categories are [[3](GUID-5676A8B2-9274-422A-B7B2-E7E9C4825B07.html#GUID-83687E14-A95F-431D-A6E4-8EF0311FC034)]:

* Category I: This lowest category
  is for circuits connected in a way that takes measures to limit overvoltage
  transients. Examples include equipment such as 24-VAC thermostats and
  sprinkler systems connected to the mains through a step-down transformer.
* Category II: This category is for
  equipment supplied from a fixed installation. Examples include equipment plugged
  into an outlet that is 10 m away from category III.
* Category III: This is for
  equipment with a fixed installation subject to special requirements. Examples
  include equipment permanently connected such as switches within a fuse panel,
  air conditioners or industrial machinery hardwired to the AC mains.
* Category IV: This is for
  equipment used at the origin of installation, which means connected directly to
  the mains voltage. Examples include electricity meters, distribution panels and
  utility transformers.

Figure 5 Example transient overvoltage
categories.

## 2.5 Standards Pertaining to Creepage, Clearance and PCB Spacing

There are numerous standards relating
to creepage and clearance. Some of these are complementary, some are contradictory,
and many are redundant. There is no one standard where you can just use an equation
or lookup table to figure out the required creepage and clearance.

In this section, we will introduce the
various standards, and explain when and how to use them in [Methodology to Determine Creepage,
Clearance and High-Voltage PCB Spacing Requirements](GUID-8A5B41AA-CD97-49C7-8219-E21382BB359A.html#GUID-8A5B41AA-CD97-49C7-8219-E21382BB359A). But first, let’s separate the standards into two categories: those relating to
user safety in an insulation system, and those relating to PCBs.

The foundational standard for user
safety in an insulation system is IEC 60664-1, which applies to systems up to 1.5
kVDC or 1 kVAC. IEC 60664-1 covers creepage, clearance and
electric strength testing. There are several other standards specific to certain end
equipment that build on IEC 60664-1 but add more specific guidelines. These include
IEC 62368-1 and IEC 60950-1 for telecommunications, servers, audio and video, and
cloud computing [[4](GUID-5676A8B2-9274-422A-B7B2-E7E9C4825B07.html#GUID-4A48CA62-3CD7-4A42-AA65-76E59A1F495D)], [[5](GUID-5676A8B2-9274-422A-B7B2-E7E9C4825B07.html#GUID-B065072C-D736-4671-AED1-4EBE90A6319C)]; IEC 61800-5 for motor drivers [[6](GUID-5676A8B2-9274-422A-B7B2-E7E9C4825B07.html#GUID-B3405905-944E-4492-9C89-4D1D56A83FA4)]; and IEC 62109-1 for solar [[7](GUID-5676A8B2-9274-422A-B7B2-E7E9C4825B07.html#GUID-14062350-9086-48BD-8366-E1E6F33F860E)].

The standards for PCB spacing address
proper or functional operation only and do not address user safety. The primary
standard is Institute for Printed Circuits (IPC)-2221B, which is a general standard
that covers generic requirements [[8](GUID-5676A8B2-9274-422A-B7B2-E7E9C4825B07.html#GUID-B3BE507E-B730-4ACB-9BA1-C90B50C6CF46)]. Another common standard addressing PCB spacing is IPC-9592B, which builds on
IPC-2221B but adds specific guidelines for the computer and telecommunications
industries [[9](GUID-5676A8B2-9274-422A-B7B2-E7E9C4825B07.html#GUID-027B3595-7D8E-433C-8118-05E756898236)]. IPC-9592B is a little stricter than IPC-2221B. Furthermore, IEC 62368-1 also
provides guidelines for both coated and uncoated PCBs for telecommunications,
servers, audio and video, and cloud computing.

## 2.6 Insulation Standards

There are various insulation standards
for isolators that verify an insulation barrier’s ability to withstand electrical,
mechanical and thermal stresses as well as environmental influences. These include
DIN VDE V 0884-11 for the European Union, UL 1577 for the United States and China
Quality Certification (CQC) GB4943.1 for China [[10](GUID-5676A8B2-9274-422A-B7B2-E7E9C4825B07.html#GUID-73EDB169-D98D-440B-8A56-48CDD422D73D)-[12](GUID-5676A8B2-9274-422A-B7B2-E7E9C4825B07.html#GUID-ADE82D98-2175-4BE7-BCB1-5C5734D3BC4D)]. The parameters addressed in these certification standards describe the
insulation barrier, and do not directly relate to creepage and clearance. What does
matter for creepage and clearance are the isolation grades, such as basic,
reinforced and functional.

## 2.7 Isolation Grades and Guidelines

There are five types of isolation
grades [[13](GUID-5676A8B2-9274-422A-B7B2-E7E9C4825B07.html#GUID-44DBD8A4-A299-4835-985E-F6B358CA593D)]:

* Functional isolation is just for
  proper circuit operation in the presence of things such as ground bounce, high
  operating voltages and transients between secondary circuits (not the primary
  mains). Functional isolation is not related to user safety.
* Basic isolation is a single level
  of isolation that protects users against electric shock under both normal and
  abnormal operating conditions.
* Supplementary isolation is an
  additional layer of isolation protection to address single-fault conditions. If
  the first layer of isolation fails, a supplementary one will protect users
  against electric shock.
* Double isolation is a combination
  of basic and supplementary isolation.
* Reinforced isolation provides the
  same ratings and protection as double isolation, but is implemented in a single
  layer of insulation material.

The two types of isolation that are
most common in practice and addressed by the isolation standards introduced in [Insulation Standards](GUID-12D989CF-D980-4629-B4F7-E2833F277749.html#GUID-12D989CF-D980-4629-B4F7-E2833F277749) are basic and reinforced. Any required creepage and clearance distances depend on
whether the design requires basic or reinforced isolation.

IEC 60664-1, IEC 62368-1 and IEC
60950-1 all provide guidelines to help determine whether an application requires
basic or reinforced isolation. In these guidelines, the terms “ordinary person” and
“user” are used interchangeably. The standards also use different terminology to
classify different voltage levels, but it is possible to simplify the terminology
into three energy-source classes depending on their voltage:

* Energy source class 1 (ES1)
  consists of circuits with a voltage up to 60 V. These circuits are safe to touch
  and no isolation is needed from users. IEC 60950-1 defines this voltage class as
  safety extra low voltage (SELV). This class includes circuits in
  telecommunications network voltage class one (TNV-1), as defined by IEC
  60950-1.
* ES2 includes circuits with
  voltages between 60 V and 120 V. These require basic isolation between the
  circuit and user. These include circuits in the TNV-2 and TNV-3 classes, as
  defined by IEC 60950-1.
* ES3 includes circuits with
  voltages above 120 V. These voltages are considered hazardous and require
  reinforced isolation between the circuit and user.

Figure 2H in IEC 60950-1 offers a very
comprehensive guide to determine the required isolation levels between different
circuits. The figure shows when functional, basic or reinforced isolation is
required between primary circuits; earthed/unearthed SELV; earthed/unearthed TNV-1,
2 or 3; and earthed/unearthed hazardous voltages. Connecting a circuit to earth
ground will often reduce the isolation level required. [Table 2](#TABLE_DZT_KMB_MZB) is a simplified summary of Figure 2H in IEC 60950-1, along with common
examples.

Table 2 Examples of isolation grades
required for common applications.

| Isolation grade | Parts being separated | | Example |
| --- | --- | --- | --- |
| Functional | SELV | SELV | <60-V brick module |
| Reinforced circuit |
| Basic | Primary, ES2, TNV-2, TNV-3, hazardous | Earthed SELV | * >60-V   DC/DC. * AC/DC   rectifiers with 12-V or 48-V output. * 400-V onboard   charger. |
| Primary | Unearthed hazardous |
| Reinforced | Primary, hazardous | Unearthed SELV | AC/DC rectifiers with 12-V or 48-V output |
| ES2, TNV-2, TNV-3 | >60-V DC/DC |

# 3 Methodology to Determine Creepage, Clearance and High-Voltage PCB Spacing Requirements

## 3.1 Flowchart

We have introduced several
definitions, classifications, ratings, standards and complex guidelines. Now, in
order to simplify and expedite the development process, we put it all together into
a single flowchart (see [Figure 6](#FIG_YXC_5NB_MZB)) with step-by-step instructions to determine the proper creepage and clearance
for an application.

Figure 6 Flowchart for determining the
required creepage and clearance for an application.

The flowchart has two main paths: one
for insulated systems for user safety and one for PCB spacing. The path for user
safety has two subpaths: one for determining creepage and one for clearance.

Let’s explain how to use this
flowchart to determine creepage for user safety, clearance for user safety, and
high-voltage spacing for PCBs.

## 3.2 Determining Creepage in Insulated Systems for User Safety

For creepage, you need to know the
working voltage of the application, the material group of the insulating material,
and the pollution degree of the environment. The next step is to determine whether
you need basic or reinforced isolation using Figure 2H in IEC 60950-1. If you need
basic isolation, use the creepage distance value determined by the next step. If you
need reinforced isolation, double the distance determined in the next step.

Based on your end equipment, look up
the required creepage distance; for general-purpose end equipment, use Table F.4 in
IEC 60664-1. For audio, video, and information and telecommunications equipment, use
Table 17 in IEC 62368-1. For motor drives, use Table 10 in IEC 61800-5-1. For solar
applications, use Table 14 in IEC 62109-1.

Based on your end equipment, look up
the required creepage distance:

* For general-purpose end
  equipment, use Table F.4 in IEC 60664-1.
* For audio, video, and information
  and telecommunications equipment, use Table 17 in IEC 62368-1.
* For motor drives, use Table 10 in
  IEC 61800-5-1.
* For solar applications, use Table
  14 in IEC 62109-1.

[Table 3](#TABLE_HPP_24B_MZB) is a small subset of Table F.4 in IEC 60664-1, simplified to show common working
voltages and pollution degrees. You can see that for pollution degree 1, there is no
pollution, so the material group does not matter. For pollution degree 2 and
material group I, an application with a 400-V working voltage would require 2 mm of
creepage for basic isolation, or (doubled) 4 mm of creepage for reinforced
isolation. For pollution degree 2 and material group III, an application with a
400-V working voltage would require 4 mm of creepage for basic isolation, or
(doubled) 8 mm of creepage for reinforced isolation.

Table 3 Subset of IEC 60664-1 Table
F.4, showing common working voltages, pollution degrees and material
groups.

| VRMS | Creepage distances to avoid failure caused by tracking (mm) | | | |
| --- | --- | --- | --- | --- |
| Pollution degree 1 | Pollution degree 2 | | |
| All material groups | Material group | | |
| I | II | III |
| 63 | 0.2 | 0.63 | 0.9 | 1.25 |
| 400 | 1.0 | 2.0 | 2.8 | 4.0 |
| 800 | 2.4 | 4.0 | 5.6 | 8.0 |
| 1,000 | 3.2 | 5.0 | 7.1 | 10.0 |

## 3.3 Determining Clearance in Insulated Systems for User Safety

For clearance, you need to know the
required transient voltage for the application, which is a function of the mains
nominal voltage and the transient overvoltage category. You also need to know the
pollution degree of the environment and the intended operating altitude (meters
above sea level).

Using the mains nominal voltage and
transient overvoltage category, see Table F.1 in IEC 60664-1 to determine the
required impulse voltage rating. If you require basic isolation, then this is the
voltage you need to use to determine clearance. If your application is for audio,
video, or information and telecommunications equipment, you need to use IEC 62368-1,
which gives the clearances for both basic and reinforced isolation in those types of
end equipment. For any other end-equipment type, you will be using a table that only
gives values for basic isolation. Therefore, for reinforced isolation, you need to
use the impulse voltage that is one step up from your application in Table F.1 in
IEC 60664-1. Section 5.1.6 in IEC 60664-1 describes this process in more detail.

[Table 4](#TABLE_AHH_TPB_MZB) is a small subset of Table F.1 in IEC 60664-1, simplified to show common working
voltages. Use this table to determine the required impulse voltage rating. For
example, a 230-V line-to-neutral application installed in transient overvoltage
category II would require 2,500 V of impulse voltage for basic isolation, or 4,000 V
for reinforced isolation if using any standard other than IEC 62368-1.

Table 4 Subset of IEC 60664-1 Table
F.1, showing common working voltages.

| Voltage line to neutral (VRMS) | Mains transient/rated impulse voltage (VPEAK) | | | |
| --- | --- | --- | --- | --- |
| Overvoltage category | | | |
| I | II | III | IV |
| ≤50 | 330 | 500 | 800 | 1,500 |
| ≤150 (for example, 120 V in the U.S.) | 800 | 1,500 | 2,500 | 4,000 |
| ≤300 (for example, 230 V in the European Union, China) | 1,500 | 2,500 | 4,000 | 6,000 |
| ≤600 (for example, industrial motors, ship power) | 2,500 | 4,000 | 6,000 | 8,000 |

For some systems, you may not be
subjected to AC mains transients. For these cases, you can calculate the required
impulse voltage rating by adding 1,200 V to the nominal line-to-neutral voltage, as
described in Section 5.3.3.2.3 in IEC 60664-1.

Now that you know the required impulse
voltage, you will look up the required clearance for applications up to 2,000 m
above sea level from the appropriate table based on your end-equipment type. For
general-purpose end equipment, use Table F.2 in IEC 60664-1. For audio, video, and
information and telecommunications equipment, use Table 10 in IEC 62368-1. For motor
drives, use Table 9 in IEC 61800-5. For solar applications, use Table 13 in IEC
62109-1.

[Table 5](#TABLE_RP3_QRB_MZB) is a small subset of Table F.2 in IEC 60664-1, simplified to show common impulse
voltage ratings. For comparison, we’ve included the values from IEC 62368-1 Table 10
in parentheses. You can see how for audio, video, information and telecommunications
applications, the requirements are a little stricter.

Table 5 Subset of IEC 60664-1 Table
F.2 showing common impulse voltages and pollution degrees. The numbers in
parentheses are clearance values from Table 10 in IEC 62368-1.

| Required impulse withstand voltage (kV) | Minimum clearances (mm) | | |
| --- | --- | --- | --- |
| Pollution degree | | |
| 1 | 2 | 3 |
| 0.5 | 0.04 | 0.2 | 0.8 |
| 1.5 | 0.5 (0.76) | | 0.8 |
| 2.5 | 1.5 (1.8) | | |
| 4.0 | 3.0 (3.8) | | |
| 6.0 | 5.5 (7.9) | | |

Finally, if the operating altitude is
greater than 2,000 m, use Table A.2 in IEC 60664-1 to determine the appropriate
multiplication factor for clearances.

## 3.4 Determining High-Voltage PCB Spacing

For PCB high-voltage spacing, you will
need to look up the required spacing based on end equipment. Additionally, there are
other exceptions that you may need to consider. These exceptions can include PCB
conformal coating in scenarios where it is not possible to meet required clearance
distances, routine transient high-potential tests during production to ensure
dielectric withstand strength against high voltages, or any other internal rules
that may apply.

Table F.4 in
IEC 60664-1 (the same table used to determine creepage) and Table 6-1 in IPC-2221B
give general PCB guidelines. The first two columns in Table F.4 in IEC 60664-1 cover
“printed wiring material,” or PCB traces. These values are very close to the values
in Table 6-1 of IPC-2221B for conductors on external PCB layers that do not use
conformal coating. IPC-2221B includes the clearance requirements for internal PCB
layers, external PCB layers with and without conformal coating, and clearances for
external component assemblies. IPC-9592B gives specific guidelines for computer and
telecommunications end equipment. Those clearance guidelines are a little more
conservative than the more general IPC-2221B. They state that if any conductors
cannot meet the required clearances, then you must use conformal coating.

[Figure 7](#FIG_GLY_XSB_MZB) shows the required clearance versus peak voltage for different standards: IEC
60664-1, IPC-2221B for uncoated external layers, IPC-2221B for coated external
layers, IPC-2221B for inner layers and IPC-9592B. You can see how inner PCB layers
require much less spacing than external layers, and external layers with conformal
coating require less spacing than external layers without conformal coating. For
example, if an application has 400-V peak voltages, an inner PCB layer only requires
0.25 mm of clearance according to IPC-2221B. For external layers that are not
conformal coated, the clearances range from 2 mm to 2.6 mm depending on the
standard. For the generic standards, IEC 60664-1 requires 2 mm and IPC-2221B
requires 2.5 mm. In this case, we advise you to go with the more conservative 2.5
mm. For a computer or telecommunications application, the clearance would need to be
2.6 mm per IPC-9592B. If it is not possible to meet these clearances, you would need
to use conformal coating. With conformal coating, external layers would only require
0.8 mm of clearance.

Figure 7 PCB high-voltage clearance
requirements as given by different standards.

## 3.5 Example Using the Flowchart: Telecommunications AC/DC Front End

We went through the flowchart and
described how to use the relevant tables from several standards. Now, let’s go
through an example of a telecommunications AC/DC front end, as shown in [Figure 8](#FIG_XHD_BTB_MZB). This application has a universal 85- to 265-VAC input and a 40- to
60-VDC output, which is floating relative to earth ground.

Figure 8 Example of an AC/DC front end
for telecommunications equipment.

The first step is to determine the
required creepage, which requires knowledge of the working voltage, pollution degree
and material group. The highest working voltage inside this converter is 400 V, as
that is the DC link voltage. The pollution degree will be 2 because this power
supply will be inside an enclosure for telecommunications equipment.

It is important to look up the
creepage required for all three material groups, as this creepage will be specific
to the individual components used in the system. For example, an isolated gate
driver from Texas Instruments may have material group I insulation, but an
optocoupler from another vendor may have material group II insulation, and PCB FR4
material may have material group IIIa. The goal is to design the power supply for
operation up to 5,000 m above sea level.

The next step
is to determine whether you need reinforced or basic isolation. The input is primary
mains, and the output is unearthed SELV according to IEC 60950-1. From primary mains
to unearthed SELV, Figure 2H in IEC 60950-1 states that reinforced isolation is
required. Note that connections from output ground to earth ground only require
basic isolation, which would have resulted in smaller creepage and clearance
requirements. This power supply’s output is not grounded to earth ground, though, so
the reinforced isolation rules apply. Table 17 in IEC 62368-1 lists the required
creepage, and you will double it, since this application requires reinforced
isolation. Table 17 specifies that for material group I, you need 4 mm; for material
group II, you need 5.6 mm; and for material group III, you need 8 mm of creepage.
This includes the doubling factor for reinforced isolation.

It's now time to determine the
required clearance. You know that the pollution degree is 2 and the altitude you
need to design for is 5,000 m, so the next step is to determine the required mains
transient impulse voltage. The mains nominal line-to-neutral voltage is up to 265 V,
and the transient overvoltage category is II, since this power converter will be
plugged into an outlet. From Table F.1 in IEC 60664-1, you can see that the rated
impulse voltage is 2.5 kV for overvoltage category II. If you used the generic IEC
60664-1 Table F.2 clearance rules, you would need to use the next highest value, 4
kV, since this application is for reinforced isolation. However, since this is for a
telecommunications application, you will use Table 10 in IEC 62368-1, which gives
the values for both basic and reinforced isolation. From the table, you will find
that for a 2.5-kV rated impulse voltage, you need 3.6 mm of clearance for reinforced
isolation. This is more conservative than the 3 mm of clearance that you would have
gotten from using 4 kV in IEC 60664-1 Table F.2.

Now, you need to apply the altitude
correction factor from Table A.2 in IEC 60664-1. For 5,000 m, the correction factor
is 1.48. The required clearance for the application is 5.33 mm (3.6 mm × 1.48).

[Table 6](#TABLE_CTB_ZTB_MZB) summarizes the creepage and clearance distances, the parameters required to
determine them, and references to the relevant tables from the standards.

Table 6 Summary of creepage and
clearance requirements for an example AC/DC front end for
telecommunications.

| Parameter | Value | | | Source |
| --- | --- | --- | --- | --- |
| Mains nominal voltage | 235 VAC | | | Application specifics |
| Maximum working voltage | 400 VDC | | |
| Altitude | 5,000 m | | |
| Transient overvoltage category | II | | |
| Pollution degree | 2 | | |
| Insulation grade | Reinforced | | | IEC 60950-1 Figure 2H |
| Material group | I | II | III | Component data sheet |
| Creepage | 4 mm (2 mm × 2) | 5.6 mm (2.8 mm × 2) | 8 mm (4 mm × 2) | IEC 62368-1 Table 17 |
| Rated impulse voltage | 2.5 kV | | | IEC 60664-1 Table F.1 |
| Altitude correction factor | 1.48 | | | IEC 60664-1 Table A.2 |
| Clearance | 5.33 mm (3.6 mm × 1.48) | | | IEC 62368-1 Table 10 |

# 4 Exceptions When You Cannot Meet the Required Creepage and Clearance

We’ve discussed how PCBs can be
conformal coated when it is not possible to meet a clearance requirement.
Additionally, you can use PCB cutouts when it is not possible to meet creepage, and
perform routine transient tests when it is not possible to meet creepage, clearance,
or both, and only functional isolation is required.

Sometimes, it may not be possible to
meet the required creepage distance on a PCB. This is especially true for cases
where an IC insulation is material group I, but the PCB is material group IIIa. For
instance, the AC/DC front end for the telecommunications example required 4 mm of
creepage for material group I and 8 mm for material group IIIa. There may be a case
where a 4-mm creepage package keeps you from using 8 mm of spacing on the PCB. In
this case, it is possible to cut a groove in the PCB to increase the creepage. Doing
so will have no effect on clearance, but you can increase the creepage, as it is a
measure of the shortest distance along the surface of the insulating material.
Section 6.2 of IEC 60664-1 gives guidelines for increasing the creepage. If the slot
has a width = X, then there are minimum values = X based on the pollution degree.
[Figure 9](#FIG_FSM_KZB_MZB) is a cross-section of a PCB with a cutout, while [Table 7](#TABLE_ZT3_NZB_MZB) shows the minimum width the slot needs to be, based on pollution degree.

Figure 9 Cross-sectional area of a PCB
with a slot cutout to increase the creepage of the PCB.

Table 7 The minimum value of the width
of a slot cut into a PCB to increase creepage.

| Pollution degree | Minimum dimension |
| --- | --- |
| 1 | 0.25 mm |
| 2 | 1.0 mm |
| 3 | 1.5 mm |

If you only require functional
isolation, you can use a routine transient (high-potential) test in production when
it is not possible to meet the required creepage and clearance distances. This test
applies a high voltage between two conductors that are intentionally isolated, and
measures the resulting leakage current. If the leakage current exceeds a certain
threshold, the device fails. The voltage applied during a high-potential test is
generally twice the working voltage plus 1,000 V.

For example, an application with a
maximum working voltage of 265 VAC would be tested at 2 × 265 + 1,000 =
1,530 V. For this reason, 1.5 kV is a common test voltage. Several standards give
guidelines for high-potential testing when it is not possible to meet creepage and
clearance: Sections 5.2.2.1 and 5.1.3.3 in IEC 60664-1; Section 5.3.4 in IEC
60950-1; and Section B.4.4 in IEC 62368-1.

# 5 Conclusions

There are many standards addressing creepage and clearance distances, and many technical
terms that designers need to understand in order to use them. The flowchart and
methodology presented in this paper should help you better understand creepage,
clearance and high-voltage spacing, and help expedite the development process. With this
knowledge, you can increase power density while still maintaining safety design
guidelines.

# 6 References

1. [Method for
   the Determination of the Proof and the Comparative Tracking Indices of Solid
   Insulating Materials.](https://webstore.iec.ch/publication/32739) IEC 60112. IEC: Geneva, Switzerland, Oct. 27,
   2020.
2. [Insulation
   Coordination for Equipment Within Low-Voltage Supply Systems – Part 1:
   Principles, Requirements and Tests.](https://webstore.iec.ch/publication/59671) IEC 60664-1. IEC: Geneva,
   Switzerland, May 26, 2020.
3. Electrical Installations for
   Buildings. IEC 60364. IEC: Geneva, Switzerland.
4. [Audio/Video, Information and Communication Technology Equipment – Part 1:
   Safety Requirements.](https://webstore.iec.ch/publication/69308) IEC 62368-1. IEC: Geneva, Switzerland, May 26,
   2023.
5. [Information
   Technology Equipment – Safety – Part 1: General Requirements.](https://webstore.iec.ch/publication/4024) IEC
   60950-1. IEC: Geneva, Switzerland, May 28, 2013.
6. [Adjustable
   Speed Electrical Power Drive Systems – Part 5-1: Safety Requirements –
   Electrical, Thermal and Energy.](https://webstore.iec.ch/publication/62103) IEC 61800-5. IEC: Geneva,
   Switzerland, Aug. 31, 2022.
7. [Safety of
   Power Converters for Use in Photovoltaic Power Systems – Part 1: General
   Requirements.](https://webstore.iec.ch/publication/6470) IEC 62109-1. IEC: Geneva, Switzerland, April 28,
   2010.
8. [Generic
   Standard on Printed Board Design.](https://www.ipc.org/TOC/IPC-2221B.pdf) IPC-2221B. IPC: Bannockburn,
   Illinois, November 2012.
9. [Requirements for Power Conversion Devices for the Computer and
   Telecommunications Industries.](https://shop.ipc.org/ipc-9592/ipc-9592-standard-only) IPC-9592, Revision B. IPC:
   Bannockburn, Illinois, Jan. 14, 2013.
10. Semiconductor Devices – Part 11: Magnetic and Capacitive Coupler for Basic and
    Reinforced Isolation. DIN VDE V 0884-11. VDE: Frankfurt, Germany, January
    2017.
11. [Optical Isolators,](https://www.shopulstandards.com/ProductDetail.aspx?UniqueKey=27729) UL 1577. UL: Northbrook,
    Illinois, April 25, 2014.
12. Audio/Video, Information and
    Communication Technology Equipment – Part 1: Safety Requirements. CQC GB4943.1.
    People’s Republic of China Certification and Accreditation Administration:
    Beijing, China, Aug. 1, 2022.
13. “[Isolation Glossary.](https://www.ti.com/lit/an/slla353a/slla353a.pdf?ts=1690838404153&ref_url=https%253A%252F%252Fwww.google.com%252F)” Texas Instruments literature
    No. SLLA353A, September 2017.