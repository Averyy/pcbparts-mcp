Source: https://www.ia.omron.com/data_pdf/guide/36/generalrelay_tg_e_10_2.pdf
Retrieved: 2026-11-09

[PDF: 26 pages.]

# **Technical Explanation for General-purpose Relays**

CSM_GeneralRelay_TG_E_10_2

#### **Introduction**


**What Is a Relay?**


Basically, a Relay is a device with contacts that opens and closes a switch as the result of an input signal (voltage or current)
applied to a coil.


**Signal applied to**
**an input coil.**


Input


**Electromagnetism**

**operates a motion.**


Motion is transferred.


**The output**
**contacts operate.**


**Other Names**

- Electromagnetic relay

- Auxiliary relay

- Miniature relay

- Power relay etc.


Electromagnetic section Switch

(coil) (contact structure)


To get an idea of what relays are, think of a children's athletic carnival. **The baton**
Little A holds on tightly to the baton and passes it to the big B. **is the signal.**
This is a relay.


Little A Big B


## **1**


**Technical Explanation for General-purpose Relays**


**Applications for Relays**


Relays are widely used in most machines and devices that use electricity.


Refrigerators

Washing machines, etc.


Molding equipment

Packing machinery

Industrial robots

Programmable controllers, etc.


Chemical plants

Shale gas plants

Control panels at power stations and transformer substations

Control panels for building management, etc.


Constant temperature tanks, etc.


Vending machines

Amusement machines, etc.


Measurement equipment, etc.


Copy machines, etc.


**Relay**
**Applications**


Home electrical appliances


Industrial machinery


Plants


Scientific equipment


Automatic vending machines


and entertainment equipment


Communications and

measurement equipment


OA devices


## **2**


**Technical Explanation for General-purpose Relays**


**Types of Relays**


There are mainly two types of relays: mechanical relays and solid state relays.
OMRON calls mechanical relays “General-purpose Relays.”


**Mechanical Relays**


**These relays transfer signals with mechanical motion.**

**Features**


Motion is transferred.


Input


Electromagnetic Switch
section section


Output


Mechanical relays have
contacts and use electromagnetic force to mechanically
open and close the contacts
to turn ON/OFF signals,
currents, or voltages.


**Rela** ~~**ys**~~


**Solid State Relays (SSRs)**


**These relays transfer signals with electronic circuits.**


A signal is transferred. (Motion is transferred.)
*Photocoupler or other device


Electromagnetic section Switch section
Input circuit Semiconductor switch
(e.g., thyristor)


**Features**

SSRs do not have the mechanical
moving parts that mechanical
relays with contacts do. Instead
they consist of semiconductors
and electronic parts.
SSRs turn ON/OFF signals,
currents, or voltages electronically
by the operation of these
electronic circuits.


- For details on SSRs, refer to the _Technical Explanation for Solid State Relays_ .


There are various types of mechanical relays (General- Hinged relays use the most common structure.
purpose Relays).


Control Relays Latching Relays
(Keep Relays)


I/O Relays


Ratchet Relays


Terminal Relays/
Relay Terminals


High-capacity Relays High-capacity Relays
for AC Loads for DC Loads


**Hinged Relays**
With hinged relays, the armature of the electromagnet rotates
around a fulcrum. This action directly or indirectoly opens and
closes a contact.


Armature

Release
spring


Coil


Moving
contact


Core


Coil Fixed Fixed
terminals NO contact NC contact


## **3**


**Technical Explanation for General-purpose Relays**


OMRON classified relays with contacts (General-purpose Relays) according to applications as shown in the following table.


**Type** **Points** **Typical Relays**


**Relays for control**
**panels**

 - Control Relays

 - I/O Relays

 - Latching Relays,
etc


**Built-in relays**

 - High -capacity
Relays, etc.


**Work-saving relays**

 - Terminal Relays

 - Relay Terminals,
etc.


**Relays for special**
**operations**

 - Ratchet Relays,
etc.


Relays with 1 to 4 poles are mainly
used for relay sequences or I/O
applications.


Built-in relays enable using a carry
current of up to 40 A and are used for
building into devices, e.g., to turn ON
load power supplies.


Work-saving relays are available in
relay units and are used mainly for I/O
applications for programmable
controllers when downsizing and
saving work are required.


Relays for special operations are
available as relays or relay units that
are specified for a specific
applications, such as alternative
operation and stepping operation of
pumps .


MM(K), MK(S), MY, LY, G2R(S), G2RV,
G7T, etc.


G7Z, G7J, G7X, etc.


G6D-F4B, G6B-4BND, etc.


G4Q, G9B, MYA, etc.


G5NB, G2RL, etc.


These specialized relays are mounted
**Relays for PCBs ***
on PCBs.


- Refer to the _OMRON Electronic Components Web_ (www.omron.com/ecb) for information on relays for PCBs.


## **4**


**Technical Explanation for General-purpose Relays**


**Structure and Operating Principle**


General-purpose Relays transfer signals through a mechanical action.
A hinged relay is shown below as an example.
Hinged relays switch contacts by the rotating movement of an armature around a fulcrum.


**Example: NO contacts (make contacts)**


**Illustration of Mechanical**
**Relay Structure**


Hinge
Armature

Release
spring


Attracted


ON


Attracted


ON


OFF


1. The input device (switch) is turned ON.


2. A current flows to the magnet (coil) to
magnetize the core.


3. Magnetism causes the armature to be
attracted to the core.


4. When the armature is attracted to the core,
the moving contact touches the fixed
contact and the lamp lights.
**Note:** At this time, the release spring is
stretched out.


5. The input device (switch) is turned OFF.


6. The current to the magnetic (coil) is
cut off, the force of attraction is lost, and
the force of the release spring returns
the armature to its original position.


7. When the armature returns to its original
position, the contacts separate and the
lamp turns OFF.


Coil


Moving
contact


Core


Coil Fixed Fixed
terminals NO contact NC contact


**Input terminals** **Output terminals**


The spring expands.


Spring contracts.


## **5**


**Technical Explanation for General-purpose Relays**


**Application Examples:** Latching Relays (Also Called Bistable Relays or Keep Relays)
Magnetic Latching Relays: Two-coil Latching Relays


**Relaxed State (after Reset)**

 - Battery Not Connected to Coil


Release
spring


Armature


Yoke


(b)


(a)


Coil A (set)


Coil B (reset)


Core


The diagram shows the relay in the relaxed state.
These relays are the same as the hinged relays described
previously except that the core, yoke, and armature are made
from semi-hard magnetic material and there are at least two
coils in the relay.


**Operating State (Set)**


(b)


(a)


Coil A (set)


Coil B (reset)


When current flows through coil A, the electromagnet (made
of semi-hard material) is magnetized and the armature is
attracted to the core.
As a result, the moving contact moves away from the normally
closed (NC) contact (turns OFF) and makes contact with the
normally open (NO) contact (turns ON).


(b)


(a)


Coil A (set)


Coil B (reset)


In the set state, the residual magnetic flux in the semi-hard
magnetic material (material that has properties similar to a
permanent magnet) will keep the armature attracted to the
core even if a current is no longer applied to coil A.


**Release State (Reset)** → **Relaxed State**


(b)


(a)


Coil A (set)


Coil B (reset)


If a current is applied to coil B, which is wound in the opposite
direction to coil A, the residual magnetic flux in the semi-hard
magnetic material will be reduced and the magnetic attraction
will weaken. The power of the release spring will become
stronger than the magnetic attraction, so the armature will
release and the relay will be in the relaxed state.
When the armature has released, there will be almost no
residual magnetic flux in the semi-hard magnetic material.


**Note:** In contrast to the hard magnetic material used in a permanent
magnet, semi-hard magnetic material requires less energy to
magnetize and de-magnetize.


## **6**


**Technical Explanation for General-purpose Relays**


**Product Lineup**


OMRON has a wide variety of General-purpose Relays so that you can select a relay that is suitable to the application.


**Types of Relays (Typical Examples)**


**Relays for**
**Control Circuits**
(For Relay Sequences)


Higher Load Capacity
**MK**


Circuit Operation
Confirmation

**MY(S)**


Greater Contact Reliability
(Minute Loads)

**MY4Z**


Greater Resistance to
Environments

**MYQ**


Even Higher Load Capacity

**MM**


Higher Load Capacity
**MK-S**


Even Greater Contact
Reliability (Minute Loads)

**MY4Z-CBG**


Resistance to
Corrosive Gases

**MY4H**


Mechanically Higher Load Even Higher

Holding Circuit Held Relays Capacity Load Capacity
### **MY MY2K G7K MKK MMK**


Higher Load
Capacity


Holding Circuit
**MY2K**


Mechanically
Held Relays


**G7K**


**MKK**


**MMK**


High-capacity
DC Load Switching

**MK-S(X)**


Slim Relays
**G2R-**         - **-S**


Note: Mainly Two-pole Relays are used in control circuits.


Large Number of Poles
**MMX**


Even Higher
Capacity

**G7J**


Even Higher
Capacity

**MK-S(X)**


Even Higher
Reliability

**G7T**


Even Slimmer
Design

**G2RV**


Even Higher
Capacity

**G7Z**


Types of Terminal Relays
Terminal Relays I/O Relay Terminals
(4 Points) (8 or 16 Points)

**G6B-4BND/4CB** **G7TC-I**  - **Series**
**G6D-F4B** **G7TC-O**  - **Series**


**Relays for**
**I/O Applications**

### G2R- � -S


High AC
Capacity

**LY**


High DC
Capacity

**MMX**


Minute Loads
**G2RV-** - **-AP**


Slim Design
**G7T**


Note: Mainly One-pole Relays are used for I/O applications.


## **7**


**Technical Explanation for General-purpose Relays**


**Types of Square Sockets (Typical Examples)** *Round Sockets are also available.


**Sockets for Front Mounting**

**Main Models (Examples)**

**Terminal Types**


**P2RF**


**PYF** **P7SA**


**Phillips**
**screws**


**Slotted**
**screws**


**Push-in**


**Clamps**


**Sockets for Back Mounting**


**Terminal Types**


**Soldered terminals**


**PCB terminals**


**Wire-wrap**
**terminals**


**G2RV-SL700(SL701)** **G3RV-SL700**


**G2RV-SL500(SL501)** **G3RV-SL500**


**P2RF-** - **-S** **PYF-** - **-S**


**Main Models (Examples)**


**P2R** **PY**


**PT**


**P7SA-** - **P**


**P2R-** - **P**


**PY-02**


**PY** - **QN** **PT** - **QN**


## **8**


#### **Explanation of Terms**

**General Relay Terms**


**Relay**
A device designed to cause a sudden, predicted change in a
single or multiple electrical output circuits when certain
conditions are satisfied by the electrical input circuit that
controls the relay device.
**Note:** Relays can be classified into electromechanical relays that are
used for mechanical operations and static relays that are not.
Based on the operating principles, further classification
includes electromagnetic relays, thermal relays, piezo-electric
relays (electrostrictive relays), and contactless relays. The IEC
classifies relays into all-or-nothing relays, which set and reset
based on whether the input quantity is within the operating
region or is effectively zero, and measuring relays, which are
set when the characteristic quantity with a specified precision
reaches the operating value.


**DC Relays**
Relays designed to operate with a DC input.


**AC Relays**
Relays designed to operate with an AC input.


**Polarized Relays**
DC relays that change status depending on the polarity of the
control input current.
**Note:** There are single-side stable relays, double-sided stable relays,
and centrally stable relays.
Relays that are not affected by the polarity of the control input
current are called nonpolarized relays (neutral relays).


**Contact Section**


**Contact Configuration**
The contact configuration is called to the contact mechanism.
Types of contacts include NC contacts (break contacts), NO
contacts (make contacts), and transfer contacts.


**Number of Contact Poles**
The number of contact poles is referred to the number of
contact circuits.


**Contact Symbols**
The following symbols are used according to the contact
mechanism.


**NO**
**contacts**


**NC**
**contacts**


**Transfer**
**contacts**


**MBB**
**contacts**


**Catalog contact**
**symbols**


**JIS contact**
**symbols**


**Note:** Except for special cases, JIS contact symbols are used in the
_Technical Explanation for General-purpose Relays and Safety_
_Precautions for All Relays_ .


**Static Relays**
Static relays are designed to get a response not from a
mechanical operation but rather from an electrical,
electromagnetic, or optical action.
Note: Solid-state relays (SSRs) fall into this category.


**Flexure Type**
Flexure is a type of drive method for the contact spring. With
flexure-type relays, the contacting force is obtained from a
stud, card, or other pushing force.


**Technical Explanation for General-purpose Relays**


**Sealed Relays**
Relays that are completely encased in a container and sealed.
**Note:** Generally, sealed relays are sealed in a metal and metal or
metal and glass container by welding or similar method.
Enclosed relays are sometimes called sealed relays even
though they are simply closed without using welding or similar
sealing methods.


**Hinged Relays**
Hinged relays are classified by the structure of the
electromagnet. Hinged relays directly or indirectly switch
contacts by the rotating movement of an armature around a
fulcrum.
**Note:** Hinged relays with armatures that move at right angles to the
core axis direction are called side armature type hinged. Those
with armatures that move in the direction of the axis are called
end-on armature type hinged relays.


**Plunger Relays**
Plunger relays are classified by the structure of the
electromagnet. The armature in a plunger relay is at the
center of the coil and it moves along the coil axis.


**Lift-off Type**
Lift-off is a type of drive method for the contact spring. After
contact, the card or stud separates from the contact spring
and the contacting force is derived from the residual bend in
the moving spring.
**Note:** The pressure of a coil spring is also sometimes used.


**Intersecting Contacts**
Contacts that have intersecting bars.


Example of Single Cross Bars


**Twin Contacts**
Opposing contact springs act as a pair and a contact is
attached to the tip of each spring, which increases the contact
reliability.


Example of Twin Cross Bars

**Moving Contact**
A moving contact is directly driven a drive mechanism or by
part of it. The contact that is not directly driven is called the
fixed contact.


**Stationary Contact**
A stationary contact is designed for continuous contact.
**Note:** Terminals, connectors, etc., fall into this group.
The term “stationary contact” is sometimes used to indicate a
fixed contact, the opposite of a moving contact.


## **9**


**Make Contacts (NO Contacts)**
The contacts in relays or switches that are normally open and
close upon operation are called NO contacts. They are also
called front contacts.


**Break Contacts (NC Contacts)**
The contacts in relays or switches that are normally closed
and open upon operation are called NC contacts.
They are also called back contacts.


**BBM (Break Before Make) Contacts**
**(Non-shorting Contacts)**
BBM contacts are part of the group of contacts that have a
specified operating sequence. BBM contacts are a set of
contacts in which the contacts that should open at operation
open before closing the contacts that need to close.
They are also called transfer contacts.


b


a


**MBB (Make Before Break) Contacts**
**(Shorting Contacts)**
MBB contacts are part of the group of contacts that have a
specified operating sequence. MBB contacts are a set of
contacts in which the contacts that should close at operation
close before opening the contacts that need to open.
These are also called continuous contacts.


a


b


b


a


Overlap

**Contact Springs**
Springs for adding contacting force to the contact's contacting
section.


**Opening Force**
The force that operates on a contact to open it.


**Opening Speed**
The operating speed when a closed contact opens.


**Contact Gap**
The gap between a set of contacts when they are open.
**Note:** This is the shortest distance between two conductors that
make up the contacts.


**Clearance**
The shortest distance between two isolated bare live parts
that must be isolated from each other.


**Technical Explanation for General-purpose Relays**


**Creeping Distance**
The shortest distance along the surface of an insulating
material placed between two bare live parts that must be
insulated from each other.


**Double-Throw**
A set of contacts that have two contact positions, each of
which closes a different circuit. Contact sets consisting of only
one contacting position for closing the circuit are called singlethrow contacts.


**Wiping Action**
The sliding action performed after two opposing contacts
make contact. This wiping action helps to reduce the impact
of film or dust that collects on the surface of contacts.


**Rated Load**
A standard value for stipulating contact performance,
expressed as a combination of contact voltage and contact
current.


**Rated Carry Current**
The current that can be supplied continuously to a contact
without exceeding the maximum temperature when the
contact is not switching (according to JIS C4530).


**Maximum Switching Capacity**
The maximum load capacity that can be switched. Design
circuits to ensure that this value is not exceeded during
operation. The maximum switching capacity is expressed as
VA for AC relays and W for DC relays.


**Failure Rate**
The percentage of failures per unit time (or number of
operations) during continuous relay switching under
individually specified test types and loads.
The failure rate will depend on the switching frequency, the
environmental conditions, and the expected reliability level.
Failure rates must always be checked on equipment under
real operating conditions.
In this catalog, the failure rate is given as the P level
(reference value). This expresses the failure level at a
reliability level of 60% ( λ 60) (JIS C5003).


**Failure rate**
**Level**
**(/operation)**


L 5×10 [-6]

M 1×10 [-6]

N 0.5×10 [-6]

P 0.1×10 [-6]

Q 0.05×10 [-6]


Example:
λ 60 = 0.1×10 [-6] /operation means that
1 failure can be expected in 10,000,000
operations at a reliability level of 60%.


## **10**


**Contact Resistance**
The contact resistance is a combination of the inherent
resistance of the conductors that make up the armature,
terminals, contacts, and other parts, the boundary resistance
where the two contacts meet, and the concentrated
resistance.
The contact resistances given in this catalog are the initial
specified values. The size of the values does not indicate
performance during actual operation.
The contact resistance is measured using the voltage drop
method (four-terminal method) shown in the following
diagram by applying the measurement currents stipulated in
the following table.


V
Contact resistance ~~=~~ ( Ω )
I

(The contact resistance for DC relays is the average of
measured values for both for forward and reverse polarity.)


**Test Currents (JIS C5442)**


**Rated current or switched current (A)** **Test current (mA)**


Less than 0.01 1


0.01 or higher but less than 0.1 10


0.1 or higher but less than 1 100


1 or higher 1,000


**Technical Explanation for General-purpose Relays**


**Chattering**
The problem where an ON contact repeatedly switches due to
an external cause. The time that chattering continues is called
the chattering time.


External cause


ON


OFF


ON


OFF


Current



Voltage



ON


OFF


Contact waveform


Time


The following diagram shows the relationship between
bounce and the response of each part when a coil turns ON.


Bounce


Operating Release
time time


Q


R Time


NC
contact


NO
contact


Coil
current


Coil
voltage


A


V


R


:Ammeter

:Voltmeter

:Variable resistor


**V**


Relay


V


Terminal


Terminal


Note 1: Q is the point when the
armature attaches to the core.
Note 2: R is the back voltage.


NC contact waveform


NO contact waveform


R


**A**


Power supply


(DC or AC)


**Maximum Contact Voltage**
The maximum value of the contact voltage that can be
switched. Never exceed this value during operation.


**Maximum Contact Current**
The maximum value of the contact current that can be
switched. Never exceed this value during operation.


**Bounce**
Undesirable intermittent switching that occurs between
contacts when they are turned ON or OFF.
The time that this intermittent switching continues is called the
bounce time. The operating time and release time does not
include the bounce time.


**Measurement Circuit**


Coil current


X


**Gluing**
Contacting surfaces cannot be opened easily, even though
they are not fused together or mechanically caught.
**Note:** Gluing occurs easily for contact surfaces of a low hardness that
are clean.


**Welding**
Contacting surface and surrounds fuse together and are
difficult to open.


Melted and stuck together.


**Locking**
Deformation due to contact wear and transfer causes
opposing contacting surfaces to become mechanically caught
and difficult to open.


NO contacts


NC contacts


ON


OFF


Operating time


ON


OFF


Bounce time Release time for relays
with NO contacts only


Release time


Bounce time


## **11**


**Transfer**
Contacting surfaces and the surrounds are affected by
electrical discharge or Joule heat and part of the material from
one contact transfers to the other opposing contact.


Moving armature


Transfer


Fixed armature

**Note:** Transfer caused by discharge was previously called large transfer
and transfer from other causes was called small transfer.


**Anode Arc**
An arc that transfers contact material from the anode side to
the contact surface on the cathode side.
Note: It is said that the direction of the transfer is affected by
the contact materials, the balance of heat in a circuit, etc.


**Cathode Arc**
An arc that transfers contact material from the cathode side to
the contact surface on the anode side.


**Coherer Effect**
The problem where the contact resistance drops dramatically
for contacts that make contact through a contact film because
the contact voltage has exceeded a certain value causing that
film to be electrically damaged.


**Black Powder**
Carbon generated by the electrical switching operation of contacts
that attaches to the surface of contacts and causes activation.


**Brown Powder**
A brown or black-brown organic compound in powder form that is
created by the reactions of organic gases on contact surfaces.


Powder


Contact


Terminal


Contacting point

**Note:** Brown powder is generated by the rubbing action of contacts
when certain organic gases are present in the operating
environment, mainly during switching of platinum contacts, and
can cause contact damage.


**Coil Section**


**Coil Symbols**
The following diagrams are used to indicate the coil drive
types.


**Double-winding latching**
**Single stable coils**
**coils**


**Single-winding**
**Polarized** **Non-** **4-terminal** **3-terminal** **latching coils**

**polarized**

**coils** **coils** **coils**


**Non-**
**polarized**
**coils**


**4-terminal**
**coils**


**3-terminal**
**coils**


**Rated Voltage**
The standard voltage applied to the operating coil when a relay is
used under normal conditions (according to JIS C4530).


**Technical Explanation for General-purpose Relays**


**Insulation Breakdown**
Sudden loss of insulation due to the voltage applied to two
electrodes either side of an insulating material.


**Compound Contacts**
Contacts made from two or more layers of different materials.


**Joined Contacts**
Contacts made of two different metals pasted together.


**Diffusion Alloy Contacts**
Contacts made using diffusion processing.


**Multi-layer Contacts**
Contacts with a multi-layer construction, using plating, joining,
or other method.


AuAg

Ag
CuNi


Example


**Plated Contacts**
Contacts with plating on the contacting surfaces.


**Sintered Contacts**
Contacts created using powder metallurgy.
**Note:** There are various types of these contacts, such as metal
sintered contacts and compound sintered contacts.


**Inrush Current**
A current larger than normal that flows instantaneously or
transiently when a contact is closed.


Inrush Current


Rated current


ON Time


**Rated Current**
The standard current that flows to the coil to enable use a
relay under normal conditions (JIS C4530).
The value is given at a coil temperature of 23°C.
The tolerance, unless otherwise specified in the model
specifications, is +15% and −20%.


**Coil Resistance**
The coil resistance is the resistance between the coil
terminals when the coil temperature is 23°C.
The tolerance is ±15% unless otherwise specified in the
model specifications.
(The coil resistance for AC specifications and the coil
inductance are the reference values.)


## **12**


**Rated Power Consumption**
The power consumed by the coil when the rated voltage is
applied to the coil (rated voltage × rated current).
The rated power consumption for AC specifications is the
value at a f60-Hz frequency.


**Must-operate Voltage**
The minimum voltage required to operate a relay (JIS C5442).
The value is given at a coil temperature of 23°C.


**Must-release Voltage**
The maximum voltage at which the relay will release when the
voltage drops dramatically or gradually (JIS C5442).
The value is given at a coil temperature of 23°C.


**Example: MY4 DC Relay**
The distributions of the must-operate voltage and the mustrelease voltage are shown in the following graph.
As shown in the graph, the relay operates at voltages less
than 80% of the rated voltage and releases at voltages greater
than 10% of the rated voltage.
Therefore, in this catalog, the operating and must-release
voltages are taken to be 80% max. and 10% min. respectively
of the rated voltage.


**Technical Explanation for General-purpose Relays**


**Hot Start**
The status power is supplied to contacts and the power that
has been supplied to the coil is turned OFF then ON. The
must-operate voltage at that time is given.
(The coil voltage, contact current, and ambient temperature
are set as conditions.)


**Minimum Pulse Width**
For a latching relay, the minimum pulse width of the rated
voltage applied to the coil to set and reset the contacts.
The value is the rated voltage applied to the coil at an ambient
temperature of 23°C.


**Coil Inductance**
For a DC relay, the value found from the time constant when
a rectangular wave is applied.
For an AC relay, the value is given at the rated frequency.
The values are different for operation and release.


**Core**
A magnetic body inserted in the coil to effectively operate the
magnetomotive force in an electromagnet.
**Note:** The term core is used mainly for fixed magnetic objects. Those
that move inside the coil are called moving cores. Sometimes
pole pieces are attached to effectively utilize the magnetic
attraction.


**Shading Coil**
A short-circuited coil for partially delaying the change in
magnetic flux by using the current generated by mutual
inductance between the magnetic pole of a DC electromagnet
that has been partially encased and an excitation coil.
Shading coils reduce the vibration of the moving parts.


Shading coil


Core








10 20 40 60 80


Percentage of rated voltage (%)


Sample: MY4 DC
Number of samples: 32


Must-operate
voltage
Must-release
Voltage


**Example: G2R-1 DC Relay**
The distributions of the must-operate voltage and the mustrelease voltage are shown in the following graph.
As shown in the graph, the relay operates at voltages less
than 70% of the rated voltage and releases at voltages greater
than 15% of the rated voltage.
Therefore, in this catalog, the operating and must-release
voltages are taken to be 70% max. and 15% min. respectively
of the rated voltage.










Sample: G2R-1 DC12 Must-release Voltage
Number of samples: 32

~~Must-operate~~
voltage


10 15 20 25 30 35 40 45 50 55 60 65 70 75 80


Percentage of rated voltage (%)


## **13**


**Electrical Characteristics**


**Operating Time**
The time between the moment the rated voltage is applied to
the coil and when the contacts operate.
For relays with more than one contact, the operating time is
the time until the slowest contact operates, unless otherwise
defined (JIS C5442).
The operating time is given for a coil temperature of 23°C and
does not include bounce time.


ON

Coil

OFF


ON

NO contact


OFF


ON

NC contacts

OFF


Release time
for relays with
Operating time NO contacts only


Release time


**Set Time (Latching Relays Only)**
The time from the moment when the rated voltage is applied
to the set coil until the contacts operate.
For relays with more than one contact, the set time is the time
until the slowest contact operates, unless otherwise defined
(JIS C5442).
The set time is given for a coil temperature of 23°C and does
not include bounce time.


Set
coil


Reset
coil


Singlewinding
latching


NO contact


Set time


NC contacts


Reset
time

Min. set Min. reset
pulse width pulse width

**Release Time**
The time from the moment the rated voltage is removed from
the coil until the contacts release.
For relays with more than one contact, the release time is the
time until the slowest contact releases, unless otherwise
defined (JIS C5442).
For relays with only NO contacts, the release time is the time
until the slowest NO contact opens.
The release time is given for a coil temperature of 23°C and
does not include bounce time.


**Reset Time (Latching Relays Only)**
The time from when the rated voltage is applied to the reset
coil until the contacts release.
For relays with NO contacts only, the reset time is the time
until the slowest NO contact opens.
For relays with more than one contact, the reset time is the time
until the slowest contact releases, unless otherwise specified.
The reset time is given for a coil temperature of 23°C and
does not include bounce time.


**Bounce**
Intermittent switching between contacts due to shock and vibration
caused by the impact between the moving parts of relays
(armatures) colliding with the core or other contacts (JIS C5442).


**Technical Explanation for General-purpose Relays**


**Operating Bounce Time**
The bounce time for NO contacts when the coil rated voltage
is applied at a coil temperature of 23°C.


**Release Bounce Time**
The bounce time for NC contacts when the coil rated voltage
is removed at a coil temperature of 23°C.


**Switching Frequency**
Number of relay operations per unit time.


**Insulation Resistance**
The resistance of the isolated sections between contacts and
coils, conducting terminals and uncharged metallic parts (e.g.,
core frame and core), or between contacts.
This value is given for the relay and does not include lands on PCBs.
(1) Between coils and contacts:
Between coil terminals and all contact terminals
(2) Between contacts with different polarity:
Between contact terminals of different polarity
(3) Between contacts with the same polarity:
Between contact terminals with the same polarity
(4) Between set coils and reset coils:
Between set coil terminals and reset coil terminals


**Dielectric Strength**
The maximum value before insulation damage occurs when
voltage is applied for one minute to an isolated metallic part
(especially charged metal part).
The voltage is applied at the same location as the insulation
resistance.
The leakage current (the current used to detect insulation
damage) is normally 1 mA.
Sometimes, however, a leakage current of 3 mA or 10 mA is used.


**Impulse Withstand Voltage**
The maximum abnormal voltage that the relay can withstand
when the voltage surges momentarily due to lightning,
switching an inductive load, etc.
The surge waveform, unless otherwise specified, is the
standard impulse voltage waveform according to JIS C5442,
i.e., 1.2 × 50 μ s.


0
0 1.2 Time(µs) 50


FCC Part 68 specifies 10 × 160 μ s ± 1,500 V.


**Vibration**
The vibration resistance of a relay is divided into two
categories: Destruction, which quantifies the characteristic
changes of, or damage to, the relay due to considerably large
vibrations which may develop during the transportation or
mounting of the relay, and malfunction durability, which
quantifies the malfunction of the relay due to vibrations while
it is in operation.
α =0.002f [2] A×9.8 α : Acceleration of vibration (m/s [2] )
f : Frequency (Hz)
A : Double amplitude (mm)


90




Peak value


## **14**


**Shock**
The shock resistance of a relay is divided into two categories:
Destruction, which quantifies the characteristic change of, or
damage to, the relay due to considerably large shocks which
may develop during the transportation or mounting of the
relay, and malfunction durability, which quantifies the
malfunction of the relay while it is in operation.


**Mechanical Durability**
The durability of contacts when no load is applied and the
contact is switched at a specified switching frequency.


**Electrical Durability**
The durability of contacts when a rated load is applied and the
contact is switched at a specified switching frequency.


**Problems and Status**


**Flashover**
The problem where discharge between opposing conductors
causes a short-circuit.
This often occurs with contacts used with medium and large
currents.


**Sticking**
Welding, locking, or gluing make it difficult to open contacts.


**Contact Wear**
The wear of contacts due to mechanical causes, such as wear
during repeated operation.


**Contact Erosion**
The expending of contacts due to electrical, thermal,
chemical, and other causes during repeated operation.


**Activation**
The problem where contact surfaces become dirty and
discharge occurs more easily.
**Note:** If precious metal contacts switching in an environment with
certain types of organic gases present, the organic gas that
attaches to the surface of the contacts will break down as a
result of the discharge and create black powder (e.g., carbon),
which makes discharge more likely to occur.


**Operating Forms**


**Technical Explanation for General-purpose Relays**


**Thermoelectromotive Force**
If different metals are attached at both ends and the temperatures
where the metals are connected are held at different
temperatures, current will flow in one direction in the circuit.
The electromotive force that causes this current is called
thermoelectromotive force.
Thermoelectromotive force occurs between the different
metals in terminals, armatures, and contacts in relays.
This thermoelectromotive force is the reason the actual
temperature and the measured temperature are different
when relays are used to switch thermocouples.


**Contact Film**
Metal oxide, sulfide, and other films that are generated on or
attach to contact surfaces and cause boundary resistance.


**Fringing Effect**
The magnetic characteristics caused by the shape around
directly opposing magnetic surfaces.


**Humming**
Noise due to mechanical vibration caused by AC poles or a
rectifier wave drive with insufficient smoothing.


**Soak**
Removing the difference due to the effect of the magnetic
history by applying a saturation current to the operating coil
during measurement of the must-operate and must-release
voltage (or current) or during testing.
**Note:** The current that is used is called the soak current.


**Single-stable (Standard) Relays**
Relays where the contacts switch
based on the non-excitation and
excitation of the coil and otherwise have
no special functions based on operating
elements.


**Double-winding Latching Relays**
Relays with a set coil and reset coil
and a latching configuration to hold
the set status or reset status.


**Terminal Arrangement/**
**Internal Connections**
**(Bottom View)**


**Terminal Arrangement/**
**Internal Connections**
**(Bottom View)**


S: Set coil
R: Reset coil


**Terminal Arrangement/**
**Internal Connections**
**(Bottom View)**


S: Set coil
R: Reset coil


**Single-winding Latching Relays**
Relays with one coil and a latching
configuration that can switch to and
hold a set or reset status according to
the polarity of the applied voltage.


**Stepping Relays**
Relays that turn multiple contacts ON and OFF in order each
time an input pulse is received.


**Ratchet Relays**
Relays that perform a type of stepping operation, where the
contacts alternate between ON and OFF for each input pulse.


## **15**


**Dimensions and Shapes**


**Dimensions**
For general-purpose relays, the maximum dimensions are
listed as guides for design.
Limited to relays characterized by their small size. The
maximum dimensions and the average dimensions (indicated
in parentheses and marked with an asterisk *) are both
indicated as guides for design.


-                        

             

 0.4


- Indicates the average dimensions.


**PCB Relays**


**High-frequency Isolation**
Indicates the degree of high-frequency signal leakage
between open contact terminals and unconnected terminals.


**Insertion Loss**
The loss of a high-frequency signal between closed contact
terminals.


**Return Loss**
The quantity of high-frequency signal reflection that occurs in
a transmission path.


**V.S.W.R.**
The voltage standing-wave ratio that occurs in a transmission
path.
**Note:** Formula for converting return loss to V.S.W.R.


**Technical Explanation for General-purpose Relays**


**Marking**
The markings on the relay itself include the model, the voltage
specifications, etc., as well as the internal connections. Some
small relays do not have internal connections shown on the
relay itself.


**Maximum High-frequency Carry Power**
The maximum high-frequency signal power that can pass
between closed contact terminals.


**Maximum High-frequency Switching Power**
The maximum high-frequency signal power that a contact can
switch. The electrical durability will be shorter than for the
rated load.


**Crosstalk Characteristic**
The degree of high-frequency signal leakage between contact
circuits.


**TV Rating (UL/CSA)**
The TV rating is one of the common ratings used to evaluate
the inrush current resistance characteristics in the UL and
CSA standards. It indicates the load switching level for a relay,
including the inrush current.
A tungsten lamp is used as the load in the switching test
(durability test) and a switching durability of 25,000 times total
is required.


 - _X_
20


- _X_
20


1+10
V.S.W.R.=


1-10 20
_x_ : Return loss


**Example Method for Measuring High-frequency**
**Characteristics**


Network analyzer


Storage normalizer


B A R RF


Transmission test set


OUT IN OUT


**Inrush**
**TV rating**
**current**


**Steady-state**
**Example models**
**current**


TV-3 51 A 3 A G2R-1A

TV-5 78 A 5 A G5RL-1A(-E)-LN

G4W-1112P-US-TV8
TV-8 117 A 8 A G5RL-U1A-E
G5RL-K1A-E

TV-10 141 A 10 A G7L

TV-15 191 A 15 A G4A


8 11 3 14
(14) (8)


High-frequency relay


50 Ω
termination


Contacts that are not related to the measurement are
terminated at 50 Ω .


## **16**


**Direction Marks**
The marks used mostly on PCB relays to show the coil
direction.
This makes it easier to determine the relay coil direction when
designing patterns for PCBs and installing PCBs.


Direction mark


**Terminal arrangement/**
**PCB mounting dimensions**
**internal connections**


**Symbol**


**Technical Explanation for General-purpose Relays**


**Terminal Arrangement/Internal Connections**
**1.Top View**
Limited to relays with terminal arrangements that can be seen
from the top, as shown in the diagram. The internal
connections are drawn showing a top view of the relay.


**2.Bottom View**
Limited to relays with terminals that cannot be seen from the
top, as shown in the diagram. The internal connections are
drawn showing a bottom view of the relay.


**3.Bottom View Rotation Direction**
The terminal arrangements for PCB relays are shown with the
relay is rotated in the direction of the arrow when the coil is on
the left (direction mark on the left).


Rotating axis


Direction
mark


Direction
mark


**Usage**
**example**


(BOTTOM VIEW)


(BOTTOM VIEW)


**Note:** The external dimensions, PCB mounting dimensions, and
terminal arrangement/internal connections all have the
direction mark on the left.
JIS contact symbols are not used, in order to match the case
markings.


## **17**


#### **Further Information**

**FAQs**


**What is the value in parentheses for models**
**with the coil voltage listed as “100/(110) VAC”?**


“100/(110) VAC” indicates that the coil has three
ratings.
Three Ratings
100 VAC 50 Hz
100 VAC 60 Hz
110 VAC 60 Hz
If the specification is listed as “100/110 VAC,” the coil
has four ratings, i.e., it also has the following rating:
110 VAC 50 Hz.
For example, the MY and LY Relays have four ratings.


**Technical Explanation for General-purpose Relays**


**What are twin-contact relay models suitable for**
**switching minute loads?**


The highly reliable crossbar twin contact or twin
contact relays are recommended for switching minute
loads.
**Series Suitable for Minute Loads**
Crossbar twin contacts:
G7T Series and MY4Z-CBG Series
Twin contacts: MY4Z Series and MKZP Series


**How should the contact reliability be viewed in**
**minute load ranges?**


**Do the operating and release times include**
**bounce time?**


No, they do not.
Operating time:
The time from when power is supplied to the coil
until the NO contact (make contact) turns ON.
Release time:
The time from when the coil turns OFF and the NO
contact (make contact) turns OFF (or, for transfer
contacts, until the NC contact is reached).


Coil


NO contact


NC contacts


The contact resistance of contacts sometimes
becomes a problem when switching minute loads.
Sometimes contacts recover during the next operation
even if there is random high contact resistance.
The contact resistance may also be increased by the

The time from when power is supplied to the coil generation of film on the contacts.
until the NO contact (make contact) turns ON. Whether or not the contact resistance will cause a

problem in the circuit must be a factor used to

The time from when the coil turns OFF and the NO determine if the contact resistance value constitutes a
contact (make contact) turns OFF (or, for transfer failure or not. For this reason, only the initial value is
contacts, until the NC contact is reached). specified as reference for contact resistance failure for

a relay. Failure rates are expressed as P levels

ON

(reference values) with the minimum applicable load

OFF

used as a guide. Some relay contacts are suitable for

ON

OFF minute loads and some are not.


ON


OFF


ON


Operating time


ON


OFF


Bounce Release time for relays
time with NO contacts only


Release time


Bounce time


**Is the switching capacity doubled if two relays**
**contacts are connected in parallel?**


No, it is not.
The two contacts are not always going to turn ON/
OFF at the same time (there may be a slight delay) so
one contact will bear the full load momentarily.


Relay


Load


## **18**


**Technical Explanation for General-purpose Relays**


**Influence of External Conditions, Environment, and Atmosphere on Relays**


**Coils**


**Relationship with Power**
(1) For a DC relay, the relationship is as follows:

Applied voltage
Coil current=
Coil resistance

(2) For an AC relay, the coil impedance must be taken into
account because it is affected by the coil inductance.
The coil impedance varies with the frequency. If the
characteristic at 60 Hz is 100%, using the same relay at
50 Hz will produce the characteristics shown in the
following table.
These values will depend on the type of relay. Check the
values before using a relay.


**Rated current, power consumption, and**
Approx. 117%
**temperature rise**


**Must-operate current** Approx. 100%


**Must-operate voltage and must-release voltage** Approx. 85%


(3) Be careful of the following points: DC relays, such as
keep relays and relays with built-in operation indicators or
surge-absorbing diodes, have polarity.
If the relay is connected incorrectly, elements may be
destroyed or malfunction.
Applying a DC voltage to an AC relay will cause the coil
to heat. This may lead to burning.
Applying an AC voltage to a DC relay will cause the
armature to vibrate and the relay will not operate properly.


**Relationship with Temperature**
Temperature changes affect the resistance of the copper
wires used for coils by approximately 0.4% per °C.
This directly affects the relay characteristics because the coil
current, which generates the attractive force of an
electromagnet, to change.
The effect of temperature on the operating characteristics
(such as the must-operate voltage and must-release voltage)
of an AC relay is smaller because the ratio of DC resistance
of the coil to the coil impedance is small.


Changes in coil resistance also affect the coil temperature for
DC relays. This is because a change in coil current causes the
amount of power that is consumed to change. The value of
temperature rise changes according to the rate of change in
the coil current due to changes in the temperature.
A typical example is shown in the following figure.


**Electrolytic Corrosion**
If the relay coil is not a
operating state, exposure to
high temperatures or high
humidity when there is a
potential difference between
the coil and other metals,
such as the core, may cause
the copper wire coil winding to
corrode. The corrosion is
caused by ionized current
passing between the metals
when the insulation between
them is insufficient.


This can be made analogous
to the process of creating
metal plating. The effect is
accelerated when acid or
base is involved.


Not a lot of attention has been
paid to this effect in the past;
however, recently good
quality plastics have been
developed for spooling, and
insulation materials, such as
polyurethane, polyester,
polyamide, and fluorine resin,
have also been developed for
the winding. These modern
plastics reduce the effect of
electrolytic corrosion.


To prevent electrolytic
corrosion, avoid storage in
locations with high
temperature or high humidity.
Thought must be given to the
circuit layout, such as
positioning the switch so that
the winding is not subject to a
constant positive voltage, or
create a positive ground.
Good and bad examples are
shown on the right.


The temperature inside the box increases because of heat
generated by the relays and other devices.
The ambient temperature that must be used is the
temperature inside the box near the relay.


Box


Ta (near the relays)


Relay Relay Relay


＋


－









Exposed relay


Relay enclosed in case
~~(plug-in type)~~


-10 0 10 20 30 40 50 60


Ambient temperature (°C)


 - This is the percentage of coil temperature rise caused by a 20°C
increase in ambient temperature.
Change in coil temperature caused by change in ambient temperature.

**Definition of Ambient Temperature**


## **19**


**Operating Time**
**Relationship between Shape of Relay and operating Time**
The operating time of the relay is determined by the coil time
constant, delay time due to the moment of inertia, and the contact
switching time. These values differ with the shape of the relay. For
example, relays with a large gap between the core and the armature
or relays that have electromagnets made from materials with a large
magnetic resistance, have small inductance values, and the time
constant is small. However, this weakens the attractive force, hence
more time is required to attract the armature. This phenomenon often
occurs in DC operation. The magnetic attraction is weakened
because it is inversely proportional to the square of the distance
between the core and the armature. For high-speed relays, the gap
is made smaller and material with high magnetic permeability is used
to reduce the amount of coil winding.

In AC operation, a current larger than the rated current is drawn when power
is supplied. The shape of the relay is not as relevant as it is for DC operation.

The moment of inertia has an indirect driving force that prevents
large loads on the armatures when they begin to move.

Movement of the armature practically dictates the contact switching
time. For this reason, the load and the attractive force must be balanced
so that the armature movement is as small as possible, and it moves
smoothly through all stages of the movement. Contact bounce is
affected by factors such as the moving speed of the armature, quality
of the moving parts, and springiness of the contact springs.

Generally, the shape of the contact spring, the contact segment, or the
structure of the stopper is designed to dampen the shock from the movement.


**Relationship between Voltage/Current Applied to Coils**
**and Operating Time**
The relay operating time is affected by the voltage/current
applied to the coils.

As shown in the following figure, when a voltage slightly higher
than the must-operate voltage is applied, the time taken for the
coil current to reach the must-operate current, the time taken for
the moving parts to overcome inertia and start moving, and the
time taken for the attractive force to overcome the weight of the
load and switch the contacts all become longer, therefore the
operating time is considerably longer.

When a voltage much higher than the must-operate voltage is
applied, all the times become shorter, and therefore the
operating time becomes shorter.

The relationship between the voltage applied to the coil and
operating time is as explained above, however, the voltage
applied to the coil also affects other characteristics. This is
why a rated coil voltage is specified.


**Relationship between Applied Coil Voltage/Current and Operating Time**


**Technical Explanation for General-purpose Relays**


**Relationship between Coil Temperature and Operating Time**
When the relay temperature changes, the springiness of the
relay contact spring, the amount of friction, and the coil
resistance change. Of these, the coil resistance has the
largest impact on the operating time. As explained in the
section on the principles of operation, the movement of the
electromagnet is related to the current. The current of DC
electromagnets can be expressed by the following equation.


0 20 40 60 80 100
Coill temperature (°C)

**Operating Environment**

**Silver Migration**
Silver migration occurs when certain humidity and oxidationreduction conditions exist and an DC voltage is applied to
silver electrodes for an extended period of time.
This phenomenon causes the insulation to deteriorate and
occasionally causes short-circuit problems.


Silver Migration


E
i = 1 - e
R


t

τ


i : Coil current
R : Coil resistance
E : Voltage applied to coil
τ : L/R coil time constant
t : Time elapsed from when voltage was applied to coil
At this point, if the coil temperature rises and the coil
resistance increases by 0.4% per °C as stated before. This
increases R (the DC coil resistance) of the coil time constant
(L/R), therefore reducing the waiting time of the contacts and
shortening the operating time. On the other hand, if the coil
resistance increases, the coil current decreases. This extends
the operating time of the DC relay.
The figure shows the change in operating time according to
coil temperature for voltage and current operation.

Large relays that have an operating time of a few 10 ms do not
change a lot even if the temperature changes. Small relays
that have an operating time of less than 10 ms tend to change
more when the temperature changes.


**Relationship between Coil Temperature and Operating Time**










Voltage operation


Current operation


DC voltage


Silver-plated terminal


Insulation with high
absorbency (e.g., phenol resin)


Ag



Must-operate Rated voltage Voltage (current)
voltage (current) (current) applied to coil


## **20**


Enlarged Photograph of Silver Migration


It is not well known what causes silver migration or what
conditions accelerate silver migration. However, the following
points can be made.


**Technical Explanation for General-purpose Relays**


**High-humidity Relays**
When shipping relays through tropical zones, regardless
whether it is just the relays or the relays are built in to other
devices, they will be exposed to high temperatures and high
humidity.
To protect the metallic materials from this kind of environment,
high-humidity relays with special external specifications have
been developed.


**Contact Deterioration Due to the Environment**
Even if relays are not used and just stored, the degradation of
the contacts may progress.
This is due to the influences of sulfur and chlorine contained
in the atmosphere, as shown in the following table.
If a relay is to be stored for such a long period as years, it is
recommended to perform a conductivity test when the Relay
is actually used, or to use Relays with gold-plated or gold-clad
contacts.


**Detected**
**Area**
**elements**


Chemical
Ag and S
plant


Steel mill Ag and S


**Results of observation of contact surfaces**
**(Ag contacts left for 12 months)**


Almost uniform and dense corrosive
substances were observed on the entire
surface of the contacts. As a result of analysis,
Ag [2] S was detected.


Irregular projections and recesses were
observed and pillars of crystals were
dispersed. As a result of analysis, Ag [2] S was
detected .


**Conditions that Cause Silver**
**Migration**


Usage of silver


Applying DC voltage for an
extended period of time


Insulation with high absorbency of
humidity


Usage in high-temperature or highhumidity environments


**Conditions that Accelerate Silver**
**Migration**


- Applied voltage is high and insulation
is thin (high potential gradient).

- High water absorption rate of
insulation material

- Oxidation-reduction gases such as
(SO2, H2S, NH3)


General-purpose relays made by OMRON do not use silverplated terminals and silver migration will not occur in them.


**Cat Whiskers**
When a plated part is stored for an extended period of time,
needlelike crystals form on the surface. These crystals are
called cat whiskers because of their shape. Depending on the
length of the crystals, they may cause short-circuit problems.

The reason why cat whiskers are formed is not completely
understood. However, it is said that they will form easily when
brass or zinc is used as the base material and tin or zinc is
used for the plating material.


Example of Whisker Formation


General-purpose relays made by OMRON have hot dip
plating or special zinc plating to guard against the formation of
whiskers. When designing parts, print boards, or patterns,
keep in mind about the use of zinc and brass, and allocate
enough space for the insulation.


Circular crystals were sporadically observed.
Highway Ag, S, and CL Ag [2] S was extremely thin at the white portions,
approx. 20 Å.


**Chemical Plant**


**×5,000**


**Steel Mill**


**×5,000**


**Highway**


**×5,000**


## **21**


**Contacts**
**Inherent Characteristics of Contacts**
The desirable features of contacts, purely from a usage point
of view, are that they have stable characteristics (such as
contact resistance) and that they have a long life. To meet
these conditions, contact follow and contact pressure are
important aspects.

The contact pressure is normally 5 to 50 g for general-use
silver and platinum, and 3 to 10 g for precious metals such as
gold, silver, and palladium. The pressure is smaller for
precious metals because the switching capacity is smaller and
they are relatively robust against environmental influences.

Contact follow requires the contacts to be touching even if the
contacts are somewhat worn out. It is closely related to the contact
pressure. The product of the two is the workload of the contacts.
For a certain workload, the contact pressure can be increased or
the contact follow can be increased to change the contactability.

For example, when the contact pressure is large and the contact
follow is small, initially characteristics will appear stable, but as
the contact begins to wear out, the contact pressure will rapidly
drop and eventually the contacts will not touch at all.

On the other hand, if the contact pressure is small and the contact
follow is large, the contact resistance may increase, or it may be
difficult to break down the film. Therefore, good relays must have
a reasonable balance between contact follow and contact
pressure. Contact resistance can be thought of as the
concentrated resistance and boundary resistance.

At first glance, the contacts look like they are touching the
whole surface. However, depending on the shape and the
roughness of the surface of the contacts, they actually touch
only on a single or multiple points. Current flow is concentrated
at these contact points and the generated resistance is the
concentrated resistance.

The contact resistance is related to the contact stiffness, contact pressure,
and the inherent resistance of contact material. A model of the contacting
parts is shown below. Contact is made over an extremely small area, and
current is concentrated in this extremely small area.

A measurement example of the relationship between contact
pressure and contact resistance is also shown below.


Current Distribution at Connection Point


Contacting surface
Current flux


Contact Pressure and Contact Resistance


**Technical Explanation for General-purpose Relays**


If contacts are exposed to the air, the formation of oxidation
and sulphurization films is unavoidable. The resistance
caused by these films is called the boundary resistance (film
resistance).

Generally, the concentrated resistance makes up a large
proportion of the contact resistance before the contacts are
used. However, as the contacts are used, arcing and
mechanical friction begin to wear them out, and the proportion
of the boundary resistance increases.
The proportion depends on the switching frequency.
Contact surfaces subject to higher switching frequencies are
relatively clean and the boundary resistance is low. Contacts
with low switching frequencies generate films with fairly high
boundary resistance.

The contact resistance of a relay is listed in catalogs but it is
only a provision of the initial value determined using a
standard testing method. The actual contact resistance must
be suitable for the application device. Normally it is
determined by the tolerance to load impedance. Except for
special cases, such as the transmission of sound currents
where distortion and attenuation becomes problems, the
contact resistance has a tolerance of 1% to 5% of the load
impedance.


**Load Conditions and Contacts**
Most of the problems that occur to a relay are caused by the
contactability of the contacts. Load conditions also influence
the types of problems that occur.
Load conditions can be grouped into micro-energy level (dry
circuit), mid-energy level, and high-energy level conditions.

The micro-energy level in a strict sense is a load condition of
a mechanical contact circuit, where the status of the contacts
is not affected by heat or discharge. In reality, however, the
status of the contacts does not change even when a
reasonable voltage is applied, so this load condition is
included in the definition.

The voltage level at which the status of the contacts remains
unaffected is called the softening voltage. It is 0.09 V for silver,
0.08 V for gold, 0.25 V for platinum, and 0.6 V for tungsten.

The mid-energy level is a load condition where a there is a
mild discharge effect. It is from the softening voltage to where
arc discharge begins. Flashover begins at 12 V for silver, 15 V for
gold, 17.5 V for platinum, 15 V for tungsten, and 11 V for 10%
palladium silver alloy.

The high-energy level describes voltages that exceed the arc
discharge voltage.




Sample 4


0 10 20 Contact pressure (g)


## **22**


**Problems Specific to Contacts**

Particular problems can occur depending on how contacts are
used. The following describes some of them.
(1) Abnormal Corrosion from Load Switching
This problem occurs when arcing due to load switching bonds
nitrogen and oxygen in the atmosphere together to form
HNO3, which corrodes metallic materials. (This is called nitric
acid corrosion.)

Example of Nitric Acid Corrosion


The following countermeasures may be effective.
1. Reduce the amount of arcing that occurs during load
switching by creating an arc reduction circuit.
2. Reduce the switching frequency to eliminate continual
arcing.
3. Reduce the humidity in the atmosphere.
(2) Coherer Effect
If there is a film on the surface of a contact and the contacts
are touching, the film electrically breaks down and the contact
resistance drops rapidly when the contact voltage exceeds a
certain value.
(3) Thermoelectromotive Force
Relay contacts are made from a combination of metals (such
as silver and copper alloy), depending on their function.
The temperature varies between the junctions depending on
the distance from the heat-emitting body (such as the coil) and
depending on the path of heat conduction. As a result,
thermoelectromotive force from a few to a few tens of μ V is
created between the contact terminals. Care must be taken
especially when handling micro signals.
A latching relay (keep relay) can be used to shorten the time
required for current to pass through the coil, thus limiting the
amount of heat generated by the coil and reducing the
thermoelectromotive force. A relay with small
thermoelectromotive force can also be used. (These relay
have a specially designed contact conduction section.)


**Contactability under Load Conditions**
The effect on the contacts is completely different between the
micro-energy level and high-energy level load conditions. The
micro-energy level has little contact wear, but the existence of
contact faults becomes a problem. Contact wear, welding, and
transfer become problems in the high-energy level load condition.
At the micro-energy level, the cleanliness of the contacts is
the most important aspect. If any non-conductive material or
film is stuck to the contacts, it will cause contact failure.
Non-conductive materials may be dust, such as sand and
fibers, but micro-load relays have relatively small contact
wipes and pressure so any particles stuck to the contact
surfaces will cause contact faults. This is a problem for all


**Technical Explanation for General-purpose Relays**


relays regardless of the contact material, which makes it
difficult to select and use the right relay. Formation of a nonconductive film may be caused by the type of material the
relay is made from, or the surrounding environment. The film
depends on the moisture in the air, oily or oxidized
substances, organic gases emitted from other relays or
structures, exhaust gas from vehicles, smoke from factories,
flux from soldering, and fingerprints of the assembly worker.
Therefore, strategies are required for the structure of the
relay, the material of the contacts, and ambient conditions.

Generic silver contacts oxidize and sulphurize easily.
Oxidized films do not affect the contacts a lot, but
sulphurization films have a large effect. For this reason,
precious metals that do not sulphurize easily are used.
Normally, palladium, gold, or platinum-gold is combined with
silver to form silver alloys to use for the contacts.
Contacts made from platinum alloys generate insulating powder
(brown powder) due to the unsaturated organic gas that is
emitted from benzene, gasoline, and similar substances. Gold
does not form any films and the contactability remains stable, but
it is soft, so it bends under low pressure. It cannot be used by
itself, so palladium may be used to create a double-layer contact
where the top layer is a gold film.
In conditions where discharge occurs even with only microloads, the contacts may oxidize or combustible gases in the
atmosphere may burn and create a carbonized film.
Carbonized films are not perfect insulators, so the resistance
may reach a few ten to a few hundred ohms.

At the high-energy level, flashover continuously generates a lot of
energy. This may cause the contacts to melt when they are
switching, or the contacts to wear out from scattering of metallic
vapor. They may also suffer from problems such as transfer of
metallic powder from one contact to the other, or welding where
the contacts melt and bond together when power is supplied.
DC voltages and DC currents do not have points that cross at
zero like there is for an AC voltage and current. So even for
fairly small loads, arcing may continue for a long time.
Under these load conditions, adherence of metallic powder
and carbonizing of the insulator may deteriorate the
insulation. For this reason, certain types of insulation
materials and shapes are chosen. The type of damage that
occurs to the contacts depends on the type of load.
Loads such as transformers, motors, and lamps cause large
inrush currents and can cause welding of the contacts.
Lamps, motors, transformers, and solenoids cause currents
of a few times to multiples of ten times the current.
Inductive loads, such as motors, transformers, and solenoids,
cause large reverse currents when power is turned OFF. The
voltages reach 4 to 20 times the normal voltage. This may
wear out the contacts or damage the load.


Waveform of Induction Motor Starting Current


Waveform of AC Solenoid Starting Current


Waveform of Lamp Starting Current


## **23**


#### **Troubleshooting**

**Failure Examples**


Measurements:


**Technical Explanation for General-purpose Relays**


Problem Possible cause of failure


Humming and vibration
(AC only)


Coil power supply ripple factor
is high.


Counter-electromotive voltage
absorbing diode short-circuited.


Coil disconnection


NC contact welding


Contact sticking (contact gluing)


Failure to operate due to
adhered material or burrs.


Foreign matter attached to
contact surfaces.


Silicone attached to contact
surfaces.


No contact follow


Contact sulphurization,
chlorination, or corrosion


Contact carbonization


Entry of foreign matter


Contact welding


~~L~~ ocking due to contact transfer


Failure to release due to
adhered material or burrs.


Burnout


CR element short circuit or
burning


Coil resistance
is zero.


Coil resistance
is infinite.


Coil resistance
is normal.


Contact resistance
is infinite.


Contact resistance
is large.


**Abnormal**
**noise**
**during**
**operation**


**No**
~~**operating**~~
**noise**


**Operating**
**noise**
**heard but**
~~**no**~~
**contact**
**continuity**


**Always on.**
~~**(Relay does**~~
**not release.)**


**Burnout**


Measure
coil
resistance.


Measure
contact
resistance.


**Relay**
**problems**


Contact resistance


Must-release voltage


Must-operate voltage


**Note:** You may perform troubleshooting, but do not open the case.


## **24**


**Technical Explanation for General-purpose Relays**


**Failures and Assessing Causes**


Various problems can occur with relays in devices that use relays.
An analysis, such as s fault tree analysis (FTA), is useful for assessing the cause of the problem.
The following table lists relay failure modes and suggests possible causes.


**Problems Visible from Outside the Relay**


**Failure** **Item to check** **Possible cause**


- The breaker or fuse may have been activated.
1. Is the input voltage reaching the relay?               - The wiring may be incorrect or there may be a leakage.

- The screw terminals have not been tightened sufficiently.


2. Is a relay with specifications suitable for the input

- Use 200 VAC relays for 100 VAC voltage lines.
voltage being used?


- The supply power has insufficient capacity.
3. Is there voltage drop in the input voltage?

- The wiring covers a long distance.


Relay does not operate.


The relay does not
release.


The relay malfunctions.
The indicator lights
incorrectly.


Burnout


- The coil is disconnected.
4. Is the relay damaged?

- There is mechanical damage from being dropped or exposed to shock.


1. Is there burnout from the coil?


2. Is there burning from the contact?


5. Is there an error in the output circuit?


- Output side power supply

- Load failure

- Incorrect wiring

- Faulty connection


- Contact error
6. Is there a faulty contact? - Contact deterioration due to end of service life

- Mechanical damage


- Leakage current in the protective circuit (surge absorber)
1. Is the applied voltage completely cut off? - Voltage applied by bypass circuit

- Semiconductor control circuit with residual voltage


2. Relay error


- Contact weld

- Insulation deterioration

- Mechanical damage

- Inductive voltage (long-distance wiring)


1. Is incorrect voltage being applied to the relay input - Inductive voltage (long-distance wiring)
terminals?  - Bypass circuit from inductive voltage (A latching relay not holding.)


2. Is excessive vibration or shock being applied? - Unsuitable operating conditions


- Incorrect coil specifications selected.

- Applied voltage exceeds rating.

- Imperfect operation of electromagnet with AC specifications (insufficient
armature connection)


- Current exceeds rating for contacts.

- Allowable inrush current exceeded.

- Short-circuit current

- Imperfect external connection (heat generated by imperfect contact with
socket)


**Problems Visible from Inside the Relay**


**Failure** **Item to check** **Possible cause**


- A rush current, e.g., from a lamp load
1. Was there a large current flow?

- Load short-circuited current


- External vibration or shock

- AC relay humming

- Contact chattering from imperfect operation caused by voltage drop (Voltage
drop sometimes occurs instantaneously when the motor is operated.)


Contact welding


Faulty contacts


Humming


Abnormal deterioration
of contacts


2. Has there been abnormal vibration in the contacting
section?


3. Is switching occurring too frequently?
――
4. Has the relay reached the end of its service life?


1. Is there foreign matter on the contact surfaces? - Silicone, carbon, or other foreign matter


2. Is the contact surface corroded? - Contact sulphurization from SO2 and H2S


3. Is there a mechanical cause? - Terminal displacement, contact displacement, or contact follow


4. Have the contacts deteriorated? - End of relay service life


- Incorrect relay coil specifications
1. Is the applied voltage sufficient? - Applied voltage ripple

- Slow rise in input voltage


2. Has the correct relay type been chosen? - DC specifications used for AC lines


3. Is the electromagnet operating correctly? - Foreign matter between the moving armature and core


1. Has the correct relay been selected? - Incorrect selection of voltage, current, or inrush current ratings


2. Has enough consideration been given to the connected

- Inrush current from a motor load, solenoid load, lamp load, etc.
load?


## **25**


**Approach to Maintenance**


There are two main types of maintenance: corrective maintenance,
i.e., inspections and replacements that take place after a failure has
occurred, and preventative maintenance, i.e., inspections and
maintenance that is undertaken before failure occurs.

One of the important issues with preventative maintenance is when
to perform inspections and replacements, how to know when that is
required, and how to determine the timing.

The factors that must be considered when determining maintenance
schedules for relays is the target device and its level of importance
and the required reliability level, when looking at maintenance from
the device or system perspective. There are also different types of
failure for the different characteristics and items based on the type of
relay.

Relay failure types can be broadly classified into failures from wear,
typified by worn out contacts, and deterioration failures, such as layer
shorts in coil windings.


**Technical Explanation for General-purpose Relays**


In general, once the conditions of use for the relay being used have
been determined, it is possible to predict maintenance requirements
because types of wear, such as contact wear, and the timing of
wearrelated failures is aligned to the number of operations. On the
other hand, deterioration failures, such as layer shorts in coil
windings, are greatly affected by the inherent reliability of the relay
being used. The maintenance requirements are affected by use
reliability, e.g., operating conditions and on-site environment. This
means that the failures are often different for each case, which
makes it difficult to determine a maintenance schedule beforehand.

In actual operation, wear and deterioration progress at the same time
and it is important to know which type of failure is going to occur first
when determining maintenance schedules.

The following items are useful for reference when determining
maintenance timing.


**Maintenance Timing**


**Determined**
**by No. of**
**operations**


**Determined**
**Remarks**
**by time**


Contact wear


Wear


Deterioration


Contact wear 
there is no applicable electrical durability curve, the maintenance If the number of
timing can be determined from test values from the device. switching operation

The maintenance timing can be determined from number of per unit time can be
operations in the mechanical durability of the relay. If the ❍ determined, the
mechanical durability listed in the performance specifications is a number of

Wear in operating value determined under standard test conditions and the actual - operations can be
mechanisms replaced by the time.


Insulation
Deterioration of Coils
and Coil Windings


Contacting Stability of
Contacts

Deterioration of
performance of
metallic material

Deterioration of
performance of resin
material


❍


The maintenance timing can be determined from the electrical
durability curve drawn from load voltage, current, and load type. If
there is no applicable electrical durability curve, the maintenance
timing can be determined from test values from the device.

The maintenance timing can be determined from number of
operations in the mechanical durability of the relay. If the
mechanical durability listed in the performance specifications is a
value determined under standard test conditions and the actual
operating conditions differ from these standard test conditions, the
maintenance timing should be determined based on test values
from actual operating conditions.

The life of a coil can be predicted if the temperature in the conditions
that the coil is operated under is known. A total of 40,000 hours at
120°C is used as a reference point for most polyurethane copper
wire coils.


Inherent reliability is changed dramatically by operating conditions
and the environment.
Maintenance timing can be determined by understanding the
operating conditions and environment and performing sampling.


- ❍ 


- ❍


It is important to
understand toxic gas
concentrations that
adversely affect the
on-site environment
and contact material.


**Maintenance Guidelines**


**Mechanical Durability** **Electrical Durability**
The external appearance and change in performance are The external appearance and change in performance are
monitored with a rated voltage (or rated frequency for AC monitored with a rated load connected to the contact and the
operation) applied to a coil when the contact is under no load rated voltage (or rated frequency for AC operation) applied to
and is switched at the rated frequency. the coil.

Whether or not the electrical durability has been reached
depends on the type of usage.
Guide to Determining the Durability


**Evaluated item** Specified value

**External appearance** No looseness, deformation, or damage

**Insulation resistance** 1 M Ω min. if not specified

**Dielectric strength** 75% min. of initial specified value

**Coil resistance** 95% of initial specified lower limit to 105% of initial specified upper limit

**Must-operate voltage** 1.2 times max. of initial specified value

**Must-release voltage** 0.5 times max. of initial specified value

**Operating time** 1.2 times max. of initial specified value

**Release time** 2 times max. of initial specified value

Contact rated current or switching current (A) Measured current (A) Resistance after contact resistance test ( Ω )

Less than 0.01 0.001 100


**Contact resistance**


0.01 min. to less than 0.1 0.01 20

0.1 min. to less than 1 0.1 5

1 min. 1 2


Based on the NECA C5442. (NECA: Nippon Electric Control Equipment Industries Association)


## **26**

