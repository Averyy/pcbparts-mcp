---
source: "pcbchecklist.com (Henrik Hansen) -- Most exhaustive"
url: "https://pcbchecklist.com/"
format: "HTML + GitHub"
method: "readability"
extracted: 2026-02-09
chars: 26857
---

# Electronics and electrical design checklist

Compiled and edited by Henrik Enggaard Hansen. [Feedback and suggestions at Github.](https://github.com/henrikh/pcb-checklist)

Other tools: [Debugging worksheet](/debugging_worksheet.html)

1. ## Process

   1. Is there a method of tracking versions/revisions?
      1. For system
      2. For schematics
      3. For PCBs
      4. For software
   2. Is source version control used? (Git, SVN etc.)
   3. Is offsite backup used?
   4. Are design decisions documented?
      1. Within or separate from the schematics/drawings/code?
2. ## System

   1. What should have ESD protection? #ESD
   2. Are amplifier circuits stable?
   3. Is there a simulation/simulator of the system or subsystems?
   4. Has the design or subsystems of it been simulated?
   5. What kind of interfaces and connections are necessary?
      1. For humans?
      2. For computers / control software?
      3. For power?
      4. For other subsystems?
   6. Are there status LEDs
      1. Power
      2. Programmable
   7. Subsystems
      1. Are multiple boards needed?
      2. How are subsystems connected?
      3. Is there a breakout board for subsystem connectors?
      4. Have harnesses/wiring/connectors been identified?
         1. Have pin-outs been defined and specified?
         2. What is the max current draw?
      5. Should any subsystems be default off? #power
   8. Communication
      1. Which busses/protocols will be used?
         1. Between subsystems?
         2. Between chips/modules?
      2. Has addresses been allocated?
   9. Watchdog and reset
      1. Can the watchdog be bypassed? #testing
      2. Can it be overruled? #testing
      3. Can it be emulated? #testing
      4. What interval is necessary? #safety
      5. Is the worst case behavior documented?
      6. Should reset be pulled to default on or off?
   10. System characteristics
       1. Is there a power budget?
       2. Estimated power dissipation of each subsystem?
       3. Estimated current draw of each subsystem?
       4. Estimated expected operating temperature?
   11. Power
       1. How is power provided?
       2. Is power-up well-defined?

          Some subsystems might need to be unpowered before other subsystems are powered, e.g.

          LED

          drivers unpowered until the software has booted.

          Certain components such as complex microprocessors,

          FPGAs

          and other complex

          ICs

          need special power sequencing to operate correctly; consult datasheets for details.
       3. Is power-down well-defined?
       4. Should any subsystems be isolated?
       5. Which voltage levels are needed?
       6. Which current draws are needed?
       7. Is there a shared power supply?
          1. Can it deliver sufficient power for all connected subsystems?
       8. Is the ground connection made first in hot-plugging connectors?
       9. Is a separate earth necessary?
       10. Will under or over voltage protection be needed?
   12. Clocks and oscillators
       1. Frequency linewidth/jitter are within tolerances across all environments?

          Clocks and oscillators are not perfect. Their frequency jitter can vary with temperature and other environmental factors.
       2. Driving ICs support crystals if crystals are used?
       3. Input rules for clocks are followed?
   13. Testing
       1. Test points on PCB for critical circuits?
       2. Test pads for flying probe/bed-of-nails/pogos setups?
       3. Has a test procedure been written?
       4. Are special connectors needed for testing?
       5. Are special peripheral circuitry needed for testing?
          1. Breakout boards for connectors?
       6. Is special equipment needed for testing?
       7. Should there be in-circuit testing?
          1. Voltage monitoring?
          2. Current monitoring?
          3. Temperature monitoring?
          4. Peripheral device behavior
          5. Board revision or version

             The board revision or version can be made software readable using either GPIO or shift register pins tied to ground or supply. An ADC can also be used to read a voltage divider. This can also be used for board specific functionality.

             [5 Tips for Versioning Embedded Systems - Design News](https://www.designnews.com/electronics-test/5-tips-versioning-embedded-systems/93647737161546)
       8. Is there event/data logging?
          1. Voltage monitoring?
          2. Current monitoring?
          3. Temperature monitoring?
          4. Connections/disconnects?
          5. Peripheral device states?
          6. Battery health?
   14. Maintainability
       1. Is disassembly easy?
       2. Is reassembly easy?
   15. Safety
       1. Fuses
          1. Appropriately sized?
          2. Fast enough for the load?
          3. Replaceable when board is assembled
          4. Replaceable when devices is assembled
          5. Storage for spare fuse?
       2. Can connections be mated in an unsafe way?
       3. Do connectors for different purposes share the same type of plug/socket?
       4. Is signal and power avoided in same connector?

          Wide Band Laboratory Fire, Fermi National Accelerator Laboratory, 1987.

          A misjoined connector resulted in several amps being drawn through cables rated for only 1 A. A fire started from this. Source:

          [Wide Band Laboratory Fire](http://www.tvsfpe.org/_images/zamirowski_&_tess_-_wide_band_fire.pdf)
   16. EMC
       1. Requirements
          1. What noise frequencies are emitted? (e.g. clock and SMPS frequencies)
          2. What noise frequencies is the circuit sensitive to?
          3. What noise will be generated by connected devices? (e.g. mains adaptors)
          4. What countries will the product be sold in? What standards cover these countries?
          5. What is the end use for the product? Does this have any specific EMC requirements ?

             Industrial or automotive use has different test requirements and permissable emission levels than consumer goods. For industrial, the levels are usually higher. See

             [Conformance UK's guide](https://www.conformance.co.uk/adirectives/doku.php?id=emc#tests)
       2. Prevention
          1. Do switching supplies have (or have an option for) RC snubbers?

             While not always needed for stability, an

             RC

             snubber can dampen ringing oscillations, which result in high frequency noise that may exceed

             EMC

             limits.
          2. Is differential signalling used for digital signals where possible?

             Differential signals are not only more immune to noise, but emit less as well. For high speed, long signal lines (e.g. remote displays in automotive), the difference can be considerable.
          3. Is differential signalling used for analog signals?
          4. Are shielded connectors needed?
          5. Is a shielded case needed? How will this be bonded to ground?
          6. Are switched-mode power supplies synchronized?
   17. Failure mode analysis
       1. Loss of ground pins on connector
       2. Effect of lost connection
          1. Between subsystems
          2. To computer
       3. System behavior when battery is fully discharged?
       4. Effects of voltage transients and high voltages on FETs
       5. Expected failure modes of failed semiconductors
          1. Expected effects of failed semiconductors
       6. Are component ratings derated by expected operating temperature/voltage/current?
       7. Environmental tolerance
          1. Vibration
          2. Heating
          3. Radiation
          4. Humidity
          5. Magnetism
3. ## Components

   1. Are the necessary components in stock?
      1. With a margin for defects/failures/loss?
      2. With a margin for spill from Pick-and-Place machine?
   2. Are voltage ratings of components sufficient? #schematic #electrical
   3. Are any components expected for obsoletion?
   4. Are there multiple sources?
   5. Are there alternate manufacturers?
   6. Are suitable alternatives identified?
   7. Have errata sheets been checked? #schematic #components
   8. Is reset active-high or active-low?
   9. Do any pins need biasing / pull-up / pull-down / strap?
      1. During initialization?
      2. For addresses?
   10. Are some functions only available in certain modes?
   11. Are the inputs and outputs organized in banks?
4. ## Floorplan

   1. Are mechanical constraints defined?
      1. Mounting
      2. Board size/shape
      3. Connector placement
      4. Human interface placement
   2. Can components be oriented in roughly the same way / consistency in layout?
   3. Are components easily accessible?

      Large components or high density boards might make it difficult to inspect components during testing or after failure. Apart from visual blocking it can also manifest as physically blocking from accessing with probes.

      1. For inspection?
      2. For replacement?
   4. Are interactive components placed in a logical manner? (Consistent orientation of buttons? Consistent rotation of potentiometers?)
   5. Are temperature sensitive components placed away from hot components?
   6. Should there be a ground ring?

      *Ground rings*

      serve both a signal integrity and a practical purpose. For

      EMC

      it is necessary to avoid traces along edges of the

      PCB

      . Adding a ground ring is an easy way of ensuring this constraint is held. It also provides somewhat better

      EMI

      prevention. Source:

      [Why are vias placed this way on a PCB? - Stack Exchange](https://electronics.stackexchange.com/a/36845/2795)
5. ## Schematic

   1. Set up
      1. Has DRC been set up and configured?
      2. Has a grid size been picked
      3. Has paper sizes been selected for sheets?
   2. Symbols
      1. Are explicit and informative
      2. Do they resemble electrical circuit symbols?
      3. Mark internal pull-up/-down
      4. Mark internal termination
      5. Reflect the functionality or logical structure of the component

         In contrast to placing pins as the physically appear on the device. Schematics should reflect functionality; board layout should reflect physical reality. Physical pin layout has its merit in making debugging easier -- however, so does having a clearer schematic.
      6. Pins are assigned the correct type (passive, power, in, out etc.)
      7. Are active-high and active-low marked consistently?
      8. Are power (and ground) pins consistently placed and marked?
      9. Do pin positions adhere to the selected grid size
   3. Functionality
      1. Are all pins on all ICs handled?
         1. Unused OPAMPs: output to negative input and positive input to ground.
         2. Unused comparators: All pins to common.
         3. Beak-out of extra pins from ICs or subsystems?
      2. Are mating connectors on different boards matched in pin-out?
      3. Have necessary inputs been ESD protected? #ESD

         A typical solution would be current limiting resistors, clamping diodes.
      4. Multipart components are identified and utilized
   4. Electrical
      1. Are reset pins pulled to high/low?
      2. Is reset filtered?
      3. Are polarized components protected/ensured against from reverse voltage?
      4. Pull-up on all open-collector?
      5. Are resistors operating within their specified voltage range?
      6. Is a low-impedance source driving tantalum capacitors?

         It can result in premature failure. Switch-on current should also be limited. References:
      7. Is there sufficient bulk capacitance?
   5. Testing
      1. Are there ground connection points? (for probes etc.)
      2. Have necessary test points been added?
      3. Have configurable strap-in pins been biased?
      4. Have configurable strap-in pins been connected with jumpers or similar?
   6. Busses
      1. I2C
         1. Pull-up on SDA an SCL
      2. JTAG
         1. Have datasheets been consulted for necessary pull-up/-down?

            Typically

            TMS

            and

            TDI

            are pull-up and

            TCK

            is pull-down, but it changes between manufacturers and devices. Some devices have internal pull-up/-down, yet external resistors are recommended to keep start-up well-defined.
      3. SWD
         1. Have datasheets been consulted for necessary pull-up/-down?

            Typically

            TMS

            and

            TDI

            are pull-up and

            TCK

            is pull-down, but it changes between manufacturers and devices. Some devices have internal pull-up/-down, yet external resistors are recommended to keep start-up well-defined.
   7. Signal integrity
      1. Is there sufficient decoupling?
      2. Is there filtering between analog and digital commons?
      3. Are optocouplers filtered?
      4. Impedance on inputs from outside of board?
      5. Are ferrite beads on input/output power lines?
      6. Are ferrite beads on sensitive signal lines?

         This includes signal lines that are not sensitive themselves, but connect to sensitive components.
         E.g. U-Blox recommend ferrite beads on

         GPS

         module

         UART

         connections to avoid

         RF

         noise travelling "along" and into the module, see

          [U-Blox M8 Hardware Integration Manual](https://www.u-blox.com/sites/default/files/NEO-M8_HardwareIntegrationManual_%28UBX-13003557%29.pdf)
      7. Do all ferrite beads have sufficient margin in DC current rating?
      8. Is there an estimate of what frequencies the ferrite beads are required to filter?
      9. Do high-speed single-ended digital signals have series resistors?
      10. Is there a footprint for a common mode filter on high-speed differential signals going offboard?

          For high-speed differential buses like

          USB

          3.0, DisplayPort, and

          HDMI

          , a common-mode filter will stop common-mode noise generated in the transceiver from traveling into the signal line where it may radiate from the cable. Notice that the filter might degrade the differential signal slightly.

          Using a footprint allows one to be quickly fitted in case

          EMC

          testing fails.
      11. Do op-amps have input filters for EMI?
   8. Documentation and notes
      1. Unpopulated parts are clearly marked
      2. Are destinations noted if they go to other sheets
      3. Are connections marked with expected current draw?
      4. Has special PCB or layout requirements been noted? #schematic #pcb
         1. Impedance?
         2. Ground planes?
         3. Routing?
         4. Keep-out?
         5. References to datasheet's recommendations
      5. Notes explaining purpose, functionality, origin, references and caculations for circuits
   9. Drafting
      1. No overlap between text, notes references, wires, symbols etc.
      2. Is all text horizontal?

         Within reason and if there is space for it.
      3. Do all components have reference and value?
         1. Are values in a uniform format
         2. Are references using standard designators?
         3. Are references placed unambiguously?
         4. Decimal points avoided?
      4. Are all junctions dotted?
      5. Are no-connects marked?
      6. No 4-way connections
      7. No upwards pointing ground symbols?
      8. Are component references ordered by schematic layout?
      9. Are the appropriate power nets connected? (Vcc, Vss, Vdd)
      10. Net names on top of lines
      11. Are unused nets left unlabeled?
      12. All connections/markings have a purpose

          Connections going from and to nowhere lead to confusion.
   10. Sheets
       1. Sheets are consistently sized
       2. Readable when printed
       3. Logical layout should go left-right, top-bottom.
       4. Header/block
          1. Name of author
          2. Name of reviewer
          3. List of revisions and changes
          4. Date
          5. Revision
          6. Company / organization
          7. Sheet/drawing number
   11. Final
       1. Has DRC passed?
6. ## Printed circuit board

   1. Manufacturing
      1. Are gold fingers needed?
      2. How is the PCB panelized?
         1. Do layers align on panelized files?
      3. What stack-up is needed?
      4. Which finish is necessary?
      5. What thickness of finish?
      6. Is there a bill of materials?
      7. Ability for blind or buried vias?
      8. Are solder paste openings the proper size?
      9. Are manufacturing tolerances honored?
         1. Solder mask
         2. Silk screen
         3. Traces
         4. Holes
      10. Are all manufacturing requirements noted on the layout file?
          1. Finish, holes, thickness, solder mask
      11. Panelization
          1. Panelized PCB fits test rig
      12. Assembly
          1. Is there enough space for the minimum bending radius of the wire harnessing?
          2. Are fiducials needed for assembly?
          3. Is there a recommended/necessary order for mounting components on the board?
          4. Will mounting certain components make it impossible to mount others?
          5. Is there an assembly order for subsystems?
          6. Is there a testing order for subsystems?
   2. Footprints
      1. Is pin 1 marked in a consistent manner?
      2. Is component polarity marked in a consistent manner?
         1. For electrically polarized components like capacitors?
         2. For keyed components like connectors?
      3. Are high-density chips marked with pin numbers?
      4. Are there tick-marks for every 5/10 pin on high pin count?
      5. Are there square pins on components? Are the holes big enough?
      6. Have the footprint dimensions been cross-checked with recommended footprint for the specific component?
      7. Are the footprints from the datasheet defined as top view or bottom view?
      8. Are edge-connectors/fingers interleaved/zig-zag?

         Edge pins on

         SODIMM

         are interleaved in placement when comparing the two sides of the inserted board. References:
      9. Are there the necessary thermal pads?
         1. Are they exposed?
         2. Are they connected to the right net?

            The net is not necessarily ground.
      10. Are certain pins only accessible on the thermal pad/unexposed pads and is the assembly procedure for this noted?

          Sometimes the only ground connection is the thermal pad. This requires soldering the thermal pad and it is thus a assembly requirement to ensure it is soldered.
   3. Placement
      1. Are jumpers accessible?
      2. Are debug connectors accessible?
      3. Filter resistors closer to the source?
      4. Termination resistors closer to the target?
   4. Clearance
      1. Are all keep-out areas honored?
      2. Around mounting holes?
      3. For IC extraction tools?
      4. For programming tools?
      5. For assembly tools (wrenches, screwdrivers etc.)
      6. For probes?
      7. Trace-to-trace clearance based upon voltage rating?
   5. Mechanical
      1. Is there spacing for an assembly run marking?
      2. Is there clearance for connectors?
      3. Are there mounting holes?
      4. Should mounting holes be electrically isolated?
      5. Should grounded mounting holes have via stitching?
      6. Are hole diameters compensating for plating?
      7. Is the outline of the board defined?
      8. Is the mechanical enclosure defined?
      9. Is there enough space for the mating connectors? #clearance #connectors
      10. Is there enough vertical space for components?
      11. Is there a drill legend?
      12. Are internal corners rounded? Can they be milled?
   6. Electrical
      1. What stack-up is needed?
      2. Polarized components are oriented correctly
      3. All traces are routed?
      4. Are decoupling capacitors placed close to power pins of ICs?
      5. Are analog and digital commons joined at only one point?
      6. Does ERC pass?
      7. Are isolation barriers large enough? #mechanical #power #safety
      8. Are the appropriate power nets connected? (Vcc, Vss, Vdd)
   7. Signal integrity
      1. Are digital signals routed over separate (digital) ground planes?
      2. Do high-speed signals avoid gaps in ground planes?
      3. Are stubs minimized for high-speed signals?
      4. Are differential pair spacing based upon impedance matching?
      5. Are transmission lines terminated with an appropriate impedance?
      6. Are crystal connections short?
      7. Is there a guard ring around the crystal?
      8. Are there filters on A/D pins?
      9. Drivers / receivers placed close to connectors?
      10. EMI / RFI close to entry / exit of shielded areas?
      11. Are traces avoided under sensitive components?
      12. Are traces avoided under noisy components?
      13. Are vias avoided under metal-film resistors?
      14. Is via fencing of sensitive RF transission lines done with the proper via spacing? (< 1/20 lambda)
      15. Is there an option for a shielding can over sensitive circuitry e.g. RF?
      16. Are bypass capacitors close to power pins?
      17. Is low inductance mounting used for decoupling?
   8. Copper pour
      1. Ground / power pins are connected and checked?
      2. No pour between adjacent pins on ICs?

         These can be mistaken for shorts during inspection. A keep-out zone between pins can fix this without adjusting the pour clearances.
      3. Has all layers been checked?
      4. Are there thermal reliefs at appropriate places?
      5. Do they introduce ground loops?
   9. Traces
      1. Are trace-pad connections sufficiently obtuse (angle 90 deg or more)?
      2. Are the trace widths sufficient for the current draw and max heating?
      3. No connections between adjacent pins on ICs?

         These can be mistaken for shorts during inspection.
      4. Are vias for internal power traces big enough?
      5. Is there enough space for heatsinks? #mechanical #thermal
      6. Has mitered bends or soft curves (r > 3 trace width) been implemented for impedance sensitive traces?
   10. Thermal
       1. Are temperature sensitive components placed away from hot components?
       2. Are there thermal vias in thermal pads?
   11. Testing
       1. Are there ground connection points close to analog test points?
       2. Are there test points for nets which are difficult to probe due to layout?

          Some nets might be inaccessible because of other components, casing and so on. In this case they should be made more accessible.
   12. Silk screen
       1. Notes and documentation
          1. Is there a revision number?
          2. Is there a date?
          3. Is there blank space for a serial/assembly number?
          4. Are connector pin-outs labeled?
          5. Fuse size and type marked on PCB
          6. Are functional groups marked?
          7. Are high-density chips marked with pin numbers?
          8. Is functionality labeled?
             1. Test points
             2. LEDs
             3. Buttons
             4. Connectors/terminals
             5. Mounting holes
             6. Jumpers
       2. Drafting
          1. No silk screen on pads
          2. All text is readable from at most two directions
          3. Will the silk screen be legible?
          4. Are component references order by PCB layout?
          5. Is there a coordinate system?
   13. Final
       1. Does ERC pass?
       2. Are there any superfluous vias?
       3. Does LVS pass?

          *Layout Versus Schematic*

          is a check to confirm that the board layout actually implements the schematic. That is: Are the traces actually connecting the proper components? Resources:

          [Wikipedia](https://en.wikipedia.org/wiki/Layout_Versus_Schematic)

          .
   14. Header/block
       1. Name of author
       2. Name of reviewer
       3. List of revisions and changes
       4. Date
       5. Revision
       6. Company / organization
       7. Sheet/drawing number
7. ## Ordering

   1. Do production files match design files?
      1. Missing or wrong geometry?

         Complex geometry can sometimes cause errors during export. Pads and artwork can also be assigned to the wrong layers.
      2. Right number of layers?
   2. Has the correct/latest files been uploaded?

      Yes, this does happen.
8. ## Board inspection

   1. Solder mask alignment
   2. Solder mask curing
9. ## Wired harnessing

   1. Wire gauge compatible with termination
   2. Cable ties and lacing cord is noted
   3. Length and color is noted
   4. Avoid signal and power in same connector
   5. Avoid current flow to remote sources through earth
   6. Is there a breakout board for the connector?
   7. Wire termination is noted
      1. Heat shrink tubing
      2. Solder
      3. Crimp force
10. ## Software

    1. Is automated software testing used? #software #procedure
    2. Is there a style guide?
    3. Are loops checked for termination conditions?
    4. Is power up and power down handled correctly?
    5. Are unused interrupts handled? (Either restart or damage control)
    6. Is there a difference between warm and cold reset?
       1. How does the devices behave if only the software is reset?
    7. Memories
       1. Are setup, hold and access times correct for external memories?
       2. Is memory integrity checked?
       3. Is memory integrity guaranteed?
       4. Is unused program memory/ROM spaces filled with traps or restart instructions?
    8. Bounds checks
       1. Is user/sensor input bounds checked?
       2. Are outputs bounds checked?
       3. Are calculations bounds checked?
       4. Are buffer overflows handled?
    9. Data structures and formats
       1. Do they include a version number or identifier?
       2. Are the bounds of variable size formats well-defined?
    10. Software characteristics
        1. CPU utilization
        2. Memory utilization
        3. Interrupt response time
        4. Interrupt execution time
    11. Versioning
        1. How is software versioned?
        2. Is version defined in a header?

           By defining the version in a header it is easy to update and consistently written.
11. ## Documentation

    1. Usage instructions
    2. Assembly instructions
    3. Troubleshooting instructions
    4. Component list
    5. Schematic diagrams
    6. PCB explanation
    7. Design decisions

## Neat resources

## Other checklists