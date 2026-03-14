---
source: "Victron Energy -- DC Wiring (Cable Thickness Guide)"
url: "https://www.victronenergy.com/media/pg/The_Wiring_Unlimited_book/en/dc-wiring.html"
format: "HTML"
method: "fetchaller"
extracted: 2026-02-16
chars: 30242
---

# 4. DC wiring

It is important to use the correct cable thickness in a system. This chapter explains why and contains other useful information on what to look out for when designing a system's DC wiring.

## 4.1. Cable selection

The correct cable can only be selected once you know the currents in a system. The below list shows an example of what cable size belongs to these currents, providing that the cable distance is less than 5 meters.

**The preferred upper inverter power limits per system voltage are:**
- **12V:** up to 3000VA.
- **24V:** up to 5000VA.
- **48V:** 5000VA and up.

In order to avoid very thick cables, the first thing you should consider is to increase the system voltage. A system with a large inverter will cause large DC currents. If the DC system voltage is increased, the DC current will drop, and the cables can be thinner.

If you want to increase the system voltage, but there are DC loads or DC charge sources that only can deal with 12V, you could consider using DC-DC converters rather than choosing a low voltage for the entire system.

As explained already, it is very important to always use the right cable thickness. You can find the correct cable thickness in the product manual. Using a too-thin cable has a direct negative effect on system performance. Generally, cable core thickness is indicated in mm². This indicates the surface area of the cable core. But other annotations are used as well, like AWG (American Wire gauge).

To find out the core diameter of a stranded core cable, look at the cable insulation. There will be markings on the cable that indicate cable core thickness.

Be aware that some cables can have very thick insulation and they may appear thicker than they are. Find out the actual core diameter by looking at the cable marking or at its specifications, or alternatively do a physical check. Strip a bit of cable insulation away and look at the copper core of the cable and estimate the core diameter. In a solid cable, you can calculate the surface area if you measure the diameter of the cable core, but in a stranded cable this method is not that precise. (Please note that we do not recommend using solid core cables).

If you cannot find a thick enough cable, double up. Use two cables per connection, rather than one very thick one. But if you do, always make sure that the combined surface area of both cables is equal to the recommended surface area. For example, 2 x 35mm² cables equal one 70mm² cable. Larger Victron inverter/chargers are equipped with two positive and two negative battery connections, especially for this purpose.

**When selecting cables avoid these mistakes:**
- Don't use cables with coarse strands.
- Don't use non-flexible cables.
- Don't use AC cables.
- For marine or moist situations use "marine cables". These are cables with tin-coated copper strands.

**Calculating cable thickness can be difficult. There are ways to help you with selecting the correct cable thickness:**
- Look in the product manual.
- The Victron toolkit app.
- The rule of thumb.
- Recommended battery cables table.

**The Victron toolkit app:**
The Victron app helps you calculate cable size and voltage drop. You can enter the following parameters:
- Voltage.
- Cable length.
- Current.
- Cable cross-section.

Once the parameters have been entered, the app will calculate the voltage drop over both cables. You should aim for a voltage drop below 2.5%.

### Recommended battery cables table

The table below shows the maximum current for a number of standard cables where the voltage drop is 0.259 Volt. This table uses the total cable length, this is the length of the positive cable plus the length of the negative cable. Note that the losses over the contacts are not included.

| Cable diameter (mm) | Cable cross-section (mm²) | Max current (A) for total cable length up to 5m | Max current (A) for total cable length up to 10m | Max current (A) for total cable length up to 15m | Max current (A) for total cable length up to 20m |
| --- | --- | --- | --- | --- | --- |
| 0.98 | 0.75 | 2.3 | 1.1 | 0.8 | 0.6 |
| 1.38 | 1.5 | 4.5 | 2.3 | 1.5 | 1.1 |
| 1.78 | 2.5 | 7.5 | 3.8 | 2.5 | 1.9 |
| 2.26 | 4 | 12 | 6 | 4 | 3 |
| 2.76 | 6 | 18 | 9 | 6 | 5 |
| 3.57 | 10 | 30 | 15 | 10 | 8 |
| 4.51 | 16 | 48 | 24 | 16 | 12 |
| 5.64 | 25 | 75 | 38 | 25 | 19 |
| 6.68 | 35 | 105 | 53 | 35 | 26 |
| 7.98 | 50 | 150 | 75 | 50 | 38 |
| 9.44 | 70 | 210 | 105 | 70 | 53 |
| 11.00 | 95 | 285 | 143 | 95 | 71 |
| 12.36 | 120 | 360 | 180 | 120 | 90 |

**Rule of thumb:**
For a quick and general calculation for cables up to 5 meters use this formula: Cable cross-section (mm²) = Current (A) / 3.

For example: if the current is 200A, then the cable needs to be: 200/3 = 66mm².

### AWG to Metric conversion chart

| AWG | Diameter (in) | Diameter (mm) | Surface area (mm²) | Resistance (ohm/m) |
| --- | --- | --- | --- | --- |
| 4/0 = 0000 | 0.460 | 11.7 | 107 | 0.000161 |
| 3/0 = 000 | 0.410 | 10.4 | 85.0 | 0.000203 |
| 2/0 = 00 | 0.365 | 9.26 | 67.4 | 0.000256 |
| 1/0 = 0 | 0.325 | 8.25 | 53.5 | 0.000323 |
| 1 | 0.289 | 7.35 | 42.4 | 0.000407 |
| 2 | 0.258 | 6.54 | 33.6 | 0.000513 |
| 3 | 0.229 | 5.83 | 26.7 | 0.000647 |
| 4 | 0.204 | 5.19 | 21.1 | 0.000815 |
| 5 | 0.182 | 4.62 | 16.8 | 0.00103 |
| 6 | 0.162 | 4.11 | 13.3 | 0.00130 |
| 7 | 0.144 | 3.66 | 10.5 | 0.00163 |
| 8 | 0.128 | 3.26 | 8.36 | 0.00206 |
| 9 | 0.114 | 2.91 | 6.63 | 0.00260 |
| 10 | 0.102 | 2.59 | 5.26 | 0.00328 |

## 4.2. Busbars

Busbars are like cables, only they are rigid metal bars. They are made of copper or tinned copper. They are used in large systems where large currents flow. They provide a common positive and a common negative point between the batteries and multiple inverters. Busbars are also used in smaller systems, especially when there is a lot of DC equipment. A busbar in this case provides a nice location to connect all the various DC cables to.

To calculate busbar thickness, simply use the recommended cable surface area and apply that to the busbar cross-section area.

For example:
- A busbar of 10mm x 5mm.
- The surface area cross-section is 5 x 10 = 50mm².
- This should be suitable for 150A for distances up to 5 meters.

When wiring the system, please make sure that the cross-section of the connection between the batteries and the DC distribution point equals the sum of the required cross-sections of the connections between the distribution point and the DC equipment.

**CAUTION:** Busbars are not insulated. To prevent short circuits or electric shock use insulated tools and do not wear metallic jewellery. When using busbars, it is in most cases necessary to shield the busbar, especially if the busbar is out in the open. This is to prevent people from touching the busbar, or to prevent a short circuit if a metal object should accidentally fall across the positive and negative busbars. An easy way to do this is to mount a Perspex sheet in front or over the busbar.

Busbars can be easily made by yourself, you simply need a copper or brass bar in which you drill holes so that electrical cables can be connected to the bar. For marine applications use tinned copper or brass.

**Victron busbar overview:**
- Busbars rated at 150, 250 and 600A, with a variety of connection options and with and without covers.
- Fuse holder 6-way for MEGA fuses with a 250A busbar.
- Modular MEGA fuse holders: 5 position busbar 500A rating, 6 position busbar 1500A.
- The Lynx distribution system consists of separate modules that can be connected to each other to form a continuous busbar for 12, 24 or 48V systems:
  1. Lynx Smart BMS - A BMS for Smart lithium batteries, with a battery monitor and Bluetooth. Uses VE.Can communication. Rated at 500A.
  2. Lynx distributor - to connect up to four DC loads or batteries and their fuses. Rated at 1000A.
  3. Lynx shunt - A battery monitor and main fuse holder. Uses VE.Can communication. Rated at 1000A.
  4. Lynx Power in - to connect batteries. Rated at 1000A.

## 4.3. Cable connections

There are several ways to connect cables to batteries, products, and other items in an electric system.

### Bolts, nuts, screws and eye lug terminals

The common sizes for bolts or screws are metric, like M5, M6, M8, and M10. Bolts for electrical applications are typically made of tinned brass. To prevent damage, always apply the manufacturer's specified torque when tightening. Over-tightening can cause the bolt or nut to fail.

Cable eye lugs connect cables to bolts and must match the cable's thickness. Use a special crimping tool to secure the lug to the cable. If the lug is uninsulated, ensure insulation is added afterwards.

When connecting a cable eye to a bolt, arrange the components in this order: washer, spring ring, and then the nut. Ensure the lug is flush with the mounting surface. Avoid placing anything, such as washers or fuses, between the lug and the surface, as this can reduce the connection's current carrying capacity.

Use insulated tools when tightening the nut. An accidental battery short circuit can be very dangerous, and the currents can melt your uninsulated spanner, or the spark can cause a battery explosion.

### Screw connectors

Screw connector terminals come in a variety of types, shapes and sizes, suitable for thick or thin wires. For an indication of the minimum or maximum wire size, always refer to the product manual.

**The basic screw connector terminal types:**
1. Rising cage clamp terminal - The screw operates a cage mechanism that rises to clamp down on the wire, providing a secure and even connection.
2. Pressure plate or clamp terminal - A screw tightens a metal plate or clamp, which compresses the wire against the terminal.
3. Standard screw terminal - Uses a simple screw that tightens directly onto the wire, compressing it against a metal plate.

**Wire insertion:** Before inserting the cable, strip enough insulation to expose the bare wire. If required, use a ferrule to secure the wire strands. Ensure that no insulation enters the connector cavity, as this can increase resistance, leading to overheating and potentially melting the connector. Additionally, ensure no bare wire is visible outside the connector, as this poses a risk of electrocution or short circuits.

The screws inside electrical connectors are typically made of tinned brass. When tightening, always apply the specified torque.

**Wire types and termination:** Generally speaking, do not use cables with a solid core, rigid or thick strands or where the strands are soldered together (unless the screw terminal is designed for this). This can result in poor electrical contact, leading to overheating or loosening of the connection. Ferrules are recommended to help align and secure the strands.

### Ferrules

Ferrules (also called wire-end ferrules or bootlace ferrules) are small sleeves that slide over stripped cable ends, holding the strands together for secure connections.

**Ferrule uses:**
- Prevention of splaying when inserted into a screw or push connector.
- Prevention of wire strand separation during installation.
- Stiffening strands, making inserting them into push-style terminals easier.
- Tidy appearance: They help create a neat and organised wiring system.

Ferrules come in various sizes and types. They must be crimped onto the wire using a dedicated crimping tool.

**Ferrule types:**
- Uninsulated ferrules, bare.
- Insulated ferrules with a plastic collar. The collar provides personal protection and ensures the ferrule is not inserted too deeply.
- Dual wire ferrules for two wires with a plastic collar. Used when two wires must be inserted into a single connector.

**Ferrule usage with screw terminals:**
- Standard screw terminal: Ferrules are required.
- Pressure plate terminal: Optional, but recommended if the wire is much smaller than the screw terminal cage.
- Rising cage clamp terminal: Not required, but most manufacturers permit ferrules.

Without ferrules, stranded cables may splay or get pinched by the screw, leading to incomplete contact or damage to the strands.

**Ferrule crimping:** Always use a dedicated crimping tool to compress the ferrule securely around the wire strands, ensuring a durable, secure and gas-tight connection. Simply tightening a ferrule onto a wire without crimping leads to poor connections.

**Ferrule orientation:** Ensure the wire size and ferrule fit into the connector cage. The crimping shape should match the cage shape. When inserting the ferrule, align it correctly with the terminal cage orientation.

### Push connectors

Push connectors are spring-loaded clamping connectors. Some are snap-in, and some are lever-operated and latch to prevent the wire from being pulled out again.

How to use:
- Strip away a sufficient length of cable insulation.
- Push down the orange part with a flat screwdriver.
- Insert the stripped wire.
- Avoid cable insulation entering the connector (can lead to overheating).
- Avoid exposing uninsulated cables outside the connector (short circuit/electrocution risk).
- Release the orange part.
- The cable is now locked in place. Give it a small tug to check if securely fastened.

### Spade terminals

A spade crimp terminal must be crimped to the cable with a special crimping tool. These connectors include ones with and without insulation and some with special features, like piggyback connectors.

### MC connectors

These connectors are exclusively used to connect solar panels to other solar panels and/or to solar chargers. The most common is the MC4. The letters "MC" stand for MultiContact. The digits 1 to 4 indicate the contact pin cross-section in mm².

Some specifics:
- They are waterproof (IP67) and can be used outdoors.
- Male or female connectors.
- Rated for 20A, 600V (newer versions 1500V).
- A special crimping tool is needed.
- They can be bought as pre-assembled cables.
- MC4 Y-pieces (or Y cables) are used to connect solar panels in parallel.

### Anderson plugs

Spring-loaded connectors made of tin- or nickel-plated copper to resist corrosion. They come in various sizes to accommodate different wire gauges and current requirements. Often used in automotive or mobile applications where rapid connection and disconnections are common.

Ensure the current rating matches the current when your system is under full load. They will add to the cable resistance if they are located between the battery and the inverter. In this case, limit or avoid their use.

### Battery clamps

These are only meant for temporary connections. They often do not have a high enough current rating and should never be permanently used in an electrical system.

## 4.4. Crimp terminals

Some special notes on insulated crimp terminals. These types are readily available and easy to use.

They come in 3 colours:
- Red - for wire between 0.5 and 1.5mm².
- Blue - for wires between 1.5 and 2.5mm².
- Yellow - for wires between 2.5 and 6mm².

**Crimp terminal types (from left to right):**
- Female spade terminal, uninsulated.
- Female spade terminal, insulated.
- Male spade terminal.
- Fork terminal.
- Female bullet terminal - not recommended; often make bad contact.
- Male bullet terminal - not recommended; often make bad contact.
- Pin terminal.
- Butt splice terminal - not recommended; often make bad contact. A better alternative is the WAGO Compact Splicing Connector 221-482 rated for cables up to 4mm².
- Blade terminal.

Use a professional ratcheting crimping tool. The ratcheting action ensures correct pressure. The tool has 3 crimping areas indicated with red, blue and yellow dots corresponding with the crimp terminal colour.

Before crimping, ensure the wire insulation is not pushed too deep into the crimp terminal. The crimp terminal has two different crimp sections, one for the wire core and one for the wire insulation.

After crimping, test the crimp by giving the wire a small tug.

## 4.5. Cable runs

When running and connecting cables between all the components in a system, there are a number of practical things to watch out for.

**Use the correct cable thickness and if need be, double up:** When wiring a system the required cable thickness might be not available or hard to obtain. Also, very thick cables are hard to manoeuvre or unable to make tight bends. In those cases, it is okay to use two cables instead of a single cable. A lot of inverters and inverter/chargers have double positive and double negative terminals for that exact purpose.

When double cables are used it could be that each cable needs to be individually fused. Check local regulations. Another local requirement can be that each individual conductor must be able to carry the full load.

**Keep cables as short as possible:** Try to keep the distance between high current cables, like battery and inverter or inverter/charger as close as possible. But do watch out, not to locate electronic equipment directly above lead acid batteries, even if sealed.

**Be aware that cables generate heat:** Due to the cable resistance, the cables generate heat when current is passing through them. The higher the voltage drop over the cable, the more heat is generated. For example, if the voltage drop is 2.5%, this means that if 1000W of power travels through the cable, 25W of heat is dissipated.

If cables are enclosed, for example by cable conduit, the heat might not be able to dissipate. Use a cable conduit that is open at the top. Alternatively use thicker cables.

A suggestion might be to run a system at full load and check the cables with a thermal camera. This is also a good way to detect loose cable connections or badly crimped terminals.

**Keep slack in the cables:** Tight cables together with vehicle vibration is not a good thing. The crimp terminals and battery poles are under too much stress and will come loose over time.

**Use strain reliefs:** Thick cables are heavy, do not let the full weight of a thick cable fully hang off a connection. This is especially important if the installation is exposed to vibration.

## 4.6. Fuses and circuit breakers

A fuse is an electrical safety device that protects wires in a circuit from excessively high currents, which can cause overheating or fire. The fuse is placed in the supply cable to an electrical device. As soon as current flows through the fuse that is higher than its current rating, for a certain amount of time, the fuse will blow.

**The fuse protects wires and equipment against:**
- Overcurrent - when more current runs in a wire than it is rated for.
- Short circuit - when one conductor accidentally comes in contact with another conductor.

### Fuse mechanisms

**Wire fuse (one time only):** Contains a wire or strip of metal that melts as soon as an unacceptable high current passes through. Once blown, it must be replaced.

**Re-settable fuses (circuit breakers):** Automatic fuses that interrupt current flow when high current is detected. Sometimes they reconnect after the high current event has passed, or they need to be manually reset. Two mechanisms:
- Thermal circuit breaker: Contains a bi-metal strip that heats up and bends when overcurrent flows, breaking the current path.
- Magnetic breaker: Contains an electromagnet sensitive to large current that creates a magnetic force to break the current path.

### Location of DC fuses

Each consumer that connects to a battery needs to be fused. The fuse is placed in the positive cable. Each individual consumer needs an individual fuse. A DC circuit usually contains a main battery fuse, after which it branches off to the individual consumers.

### Fuse ratings and selection

When selecting a fuse there are 4 selection criteria:
- Current rating
- Voltage rating
- Speed
- Type

**Current rating:** If there is only one consumer, the fuse will need to match the current rating of that consumer or the current rating of the cable, whichever is lower. If multiple consumers, the fuse will need to match the current rating of the cabling.

**Voltage rating:** The fuse voltage rating needs to be equal to or bigger than the expected maximum voltage. The fuse needs to be specifically rated for DC and/or AC. Most DC fuses are suitable for 12 and 24V, but they are not necessarily suitable for 48V and higher. Note that circuit breakers might be unidirectional, so for DC, it matters which way they are wired.

**Speed:** The time it takes for the fuse to open when a fault current occurs.
- Slow blow fuses: Used in DC applications with high start-up currents (motors, capacitors, inverters).
- Fast blow fuses: Used in AC applications with sensitive consumers.

Fuse element speed range:
- FF: Very Fast Acting (Flink Flink)
- F: Fast Acting (Flink)
- M: Medium Acting (Mitteltrage)
- T: Slow Acting (Trage)
- TT: Very Slow Acting (Trage Trage)

### Overview of fuse types

| Fuse type | Current | Voltage | Speed |
| --- | --- | --- | --- |
| Glass or ceramic fuses | Up to ~60A | Up to 250V AC or DC | Fast or slow |
| Blade fuses (automotive) | Up to 120A | 32V DC | Slow |
| Midi fuses | 23–200A | 32V DC | Slow |
| Cooper Bussmann MRBF fuses | 30–300A | 58V DC | Marine rated |
| CNN fuses | 10–800A | 48V DC, 125V AC | Fast |
| Mega fuses | 40–500A | 32V DC | Slow |
| ANL fuses | 35–750A | 32V DC | Fast |
| NH fuses | Up to 1000A | 500-690V AC, 440-550V DC | Multiple speeds |
| Circuit breakers (CB or MCB) | Various | Various AC or DC | Various |

## 4.7. DC isolation switches

A battery isolation switch can be used to isolate the battery (or battery bank) from the rest of the electrical circuit. This is useful for maintenance or when the system is not being used.

When selecting an isolator switch always make sure it is rated to the currents expected under full load.

If battery isolation is needed, it is recommended to only isolate the positive battery cable.

It might not even be necessary to add an isolator switch. Removing the main fuse will also break the circuit.

Always use quality isolator switches. A low-quality switch will have more resistance, increasing voltage drop and causing system issues.

Isolator switches are rated for a certain voltage and a continuous current (make sure it is DC current) and are often also rated for a 5-minute current and a few seconds peak current.

Some isolator switches are not designed to break current (especially DC current) and some battery switches cannot switch under load. Refer to the technical specifications.

**Types of isolator switches:**
- Battery isolator switch for mobile systems (usually 12 and 24V).
- DIN mounted circuit breakers, for land-based systems (usually 48V and up).
- NH fuse holder switch for high current land-based systems (usually 48V and up).

**Systems with multiple inverters or inverter/chargers:** Each unit must be fused individually, using the same type of fuse. Avoid using a single large circuit breaker for the entire system. A short circuit in an individual unit will rarely have low enough resistance to trip the large fuse.

It is preferred to maintain a continuous negative DC connection and only switch/fuse the positive DC connection of each unit. A loose connection in the DC negative path is difficult to troubleshoot in multi-unit systems.

## 4.8. Shunt

A shunt is added to a system to measure current flow, used for monitoring and battery state-of-charge calculations.

A shunt is a resistive element used to measure current. When current flows through the shunt, a small voltage drop proportional to the current is created. By measuring this voltage drop, the amount and direction of the current can be determined.

A shunt has a current and a voltage rating, for example, 500A, 50mV. This indicates that a 500A current passing through the shunt will cause a 50mV (0.05V) voltage drop.

The shunt must be rated for the maximum DC current that will flow in the system's combined consumers. Example: A 3000VA inverter with peak power of 6000W at 12V will draw 500A.

For safety reasons, the shunt is typically placed in the negative cable. It should be the last component before the battery bank or battery bank busbar. All DC consumers and supplies must be connected after the shunt.

Misplacing the shunt can cause issues, especially in large systems where there is a long path between the battery and inverter/chargers.

## 4.9. Parallel and/or 3-phase system DC wiring

When connecting multiple inverter/chargers together, they all need to be connected to the same battery bank. For correct operation, it is essential that each unit receives exactly the same voltages.

**The DC path from the battery bank to each individual unit, or from the busbar to each individual unit needs to be exactly the same** — same cable type, cross-section and cable length for each unit.

Different voltages mean different currents. The unit with a lower voltage will have a higher current running through its power electronics and will go into overload before the other units do. The unit with bad wiring will determine the performance of the whole system.

To achieve a balanced system:
- Use the same cable type, cross-section and cable length for each unit.
- Ensure all cable lugs are identical.
- All connections tightened with the same torque values.
- Consider using busbar power posts between battery bank and inverter/chargers.
- When using fuses, use one fuse per unit and make sure all fuses are exactly the same.

**To check if a system is correctly wired:**
- Load the system to maximum load.
- Current clamp the DC wires to each unit.
- Compare the current readings; each unit should have similar DC currents.
- Alternatively, measure voltage on the busbar vs. at each unit's battery terminals. All readings should be identical.

## 4.10. Large system busbars

Large installations with multiple DC consumers and sources all connect to a central busbar. It is important to alternately connect the inverter/chargers and the solar chargers to the busbars. This reduces current flowing through the busbars — the current from a solar charger can travel via a short path straight into the inverter or battery without traveling through the entire busbar.

When wiring:
- Make sure all inverter/chargers have the same cable length.
- Solar chargers need approximately the same cable length.
- Same for the batteries.
- Do not have all inverter/chargers on one side and solar chargers on the other side. Intermix them.
- If the system has only one battery bank, connect it in the middle of the busbars.
- If several parallel battery banks, distribute them evenly along the busbars.

## 4.11. Voltage sensing and compensation

Voltage sensing is a battery charger feature. It works by measuring the difference between the voltage in the unit and the voltage at the battery terminals. As soon as a difference is detected, the charge voltage will be increased to compensate for cable losses during charging.

This feature generally compensates for voltage losses up to 1V. If the losses are bigger than 1V, the battery cables are too thin and the charge current needs to be reduced.

Voltage sense can also compensate for voltage losses when diode splitters are used (0.3V voltage drop over the diode).

If the product has a voltage sense (V-sense) terminal, two wires can be connected from the V-sense terminal directly to the battery's positive and negative terminals. Use a cable with a cross-section of 0.75mm².

**Voltage sensing in an ESS with a DC solar charger:**

In an ESS system that only contains DC solar chargers (without grid-feed inverters), the charger of the inverter/charger is disabled. The solar charger charges the battery and excess solar power is fed back into the grid. The GX device sets the solar charger at a higher DC voltage than the inverter/charger's DC voltage.

When the battery is almost full, the battery voltage will be slightly higher than the inverter/charger's DC voltage. This is the "cue" for the inverter/charger to feed power into the grid. In a 48V system, this overvoltage is set at 0.4V, and in a 24V system, this is 0.2V.

Special care is needed for DC cabling, fuses and connections, as they can cause a voltage drop that reduces the "overvoltage" signal.

Example of an ESS system with a 100A solar charger, two 1-meter 35mm² cables and a 150A fuse:
- The resistance of the connections is 0.35mΩ.
- The resistance of a 150A fuse is 0.35mΩ.
- The resistance of a 2m cable is 1.08mΩ.
- The total resistance is 1.78mΩ.
- The voltage drop at 100A is 178mV.

The solution is to use a solar charger with automatic voltage drop compensation (voltage sensing). If the solar charger does not have voltage sensing, connect it directly to the inverter/charger.

## 4.12. Solar

Solar panels are not allowed to be directly connected to a battery. A solar charger needs to be placed between the solar panels and the batteries. The solar charger converts the higher solar panel voltage into a voltage suitable for battery charging.

**MC4 connectors:** The male connector connects to the positive cable from the solar panel and the female connector connects to the negative cable.

**Solar cable types:** A solar cable is designed for outdoor use. It is dust, age and UV resistant and has tinned copper wire strands.

**Solar arrays:** If you connect solar panels in series the voltage increases; in parallel the current increases.

**MC4 splitters:** Used to make parallel connections easy. Two types: 1 male/2 female and 1 female/2 male.

**Solar array total voltage:** When designing a solar array, make sure the array's open circuit voltage (Voc) does not exceed the voltage rating of the MPPT. If you look at the specs of a 12V solar panel, the Voc is around 22V. For a 75/15 MPPT solar charger (max 75V), you can connect up to 3 x 12V panels in series.

**Note on MPPT charge current at different battery voltages:** For a 75/15 MPPT solar charger, the current rating is 15A into the battery. With a 12V battery you will get less power than with a 24V battery.
