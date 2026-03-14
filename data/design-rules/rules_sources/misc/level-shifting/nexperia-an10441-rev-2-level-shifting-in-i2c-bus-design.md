---
source: "Nexperia AN10441 Rev.2 -- Level Shifting in I2C-Bus Design"
url: "https://assets.nexperia.com/documents/application-note/AN10441.pdf"
format: "PDF 5pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 4874
---
# Level Shifting Techniques in I2C-Bus Design

## 1. Introduction

Present technology processes for integrated circuits with clearances of 0.5 um and less limit the maximum supply voltage and consequently the logic levels for the digital I/O signals. To interface these lower voltage circuits with existing 5 V devices, a level shifter is needed. For bidirectional bus systems like the I2C-bus, such a level shifter must also be bidirectional, without the need of a direction control signal. The simplest way to solve this problem is by connecting a discrete MOSFET to each bus line.

## 2. Bidirectional Level Shifter for Fast-mode and Standard-mode I2C-Bus Systems

In spite of its surprising simplicity, such a solution not only fulfils the requirement of bidirectional level shifting without a direction control signal, it also:

- Isolates a powered-down bus section from the rest of the bus system
- Protects the 'lower voltage' side against high voltage spikes from the 'higher-voltage' side.

The bidirectional level shifter can be used for both Standard-mode (up to 100 kbit/s) or in Fast-mode (up to 400 kbit/s) I2C-bus systems. It is not intended for Hs-mode systems, which may have a bridge with a level shifting possibility.

### 2.1. Connecting Devices with Different Logic Levels

Different voltage devices could be connected to the same bus by using pull-up resistors to the supply voltage line. Although this is the simplest solution, the lower voltage devices must be 5 V tolerant, which can make them more expensive to manufacture. By using a bidirectional level shifter, however, it is possible to interconnect two sections of an I2C-bus system, with each section having a different supply voltage and different logic levels.

The left 'low-voltage' section has pull-up resistors and devices connected to a 3.3 V supply voltage; the right 'high-voltage' section has pull-up resistors and devices connected to a 5 V supply voltage. The devices of each section have I/Os with supply voltage related logic input levels and an open-drain output configuration.

The level shifter for each bus line is identical and consists of one discrete N-channel enhancement MOSFET; TR1 for the serial data line SDA and TR2 for the serial clock line SCL. The gates (g) have to be connected to the lowest supply voltage VDD1, the sources (s) to the bus lines of the 'lower-voltage' section, and the drains (d) to the bus lines of the 'higher-voltage' section. Many MOSFETs have the substrate internally connected with its source, if this is not the case, an external connection should be made. Each MOSFET has an integral diode (n-p junction) between the drain and substrate.

### 2.1.1. Operation of the Level Shifter

The following three states should be considered during the operation of the level shifter:

1. **No device is pulling down the bus line.** The bus line of the 'lower-voltage' section is pulled up by its pull-up resistors Rp to 3.3 V. The gate and the source of the MOSFET are both at 3.3 V, so its VGS is below the threshold voltage and the MOSFET is not conducting. This allows the bus line at the 'higher-voltage' section to be pulled up by its pull-up resistor Rp to 5 V. So the bus lines of both sections are HIGH, but at a different voltage level.

2. **A 3.3 V device pulls down the bus line to a LOW level.** The source of the MOSFET also becomes LOW, while the gate stays at 3.3 V. VGS rises above the threshold and the MOSFET starts to conduct. The bus line of the 'higher-voltage' section is then also pulled down to a LOW level by the 3.3 V device via the conducting MOSFET. So the bus lines of both sections go LOW to the same voltage level.

3. **A 5 V device pulls down the bus line to a LOW level.** The drain-substrate diode of the MOSFET pulls the 'lower-voltage' section down until VGS passes the threshold and the MOSFET starts to conduct. The bus line of the 'lower-voltage' section is then further pulled down to a LOW level by the 5 V device via the conducting MOSFET. So the bus lines of both sections go LOW to the same voltage level.

The three states show that the logic levels are transferred in both directions of the bus system, independent of the driving section. State 1 performs the level shift function. States 2 and 3 perform a 'wired-AND' function between the bus lines of both sections as required by the I2C-bus specification.

Supply voltages other than 3.3 V for VDD1 and 5 V for VDD2 can also be applied, e.g., 2 V for VDD1 and 10 V for VDD2 is feasible. In normal operation VDD2 must be equal to or higher than VDD1 (VDD2 is allowed to fall below VDD1 during switching power on/off).
