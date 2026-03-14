---
source: "RPi -- Pico 2 Datasheet (RP2350 reference impl.)"
url: "https://datasheets.raspberrypi.com/pico/pico-2-datasheet.pdf"
format: "PDF 27pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 22360
---

# Raspberry Pi Pico 2 Datasheet

An RP2350-based microcontroller board

## Chapter 1. About Raspberry Pi Pico 2

Raspberry Pi Pico 2 is a microcontroller board based on the Raspberry Pi RP2350 microcontroller chip.

*[Figure 1. Both sides of the Raspberry Pi Pico 2 board.]*

Raspberry Pi Pico 2 has been designed to be a low cost yet flexible development platform for RP2350, with the following key features:

- RP2350A microcontroller with 4 MB flash
- Micro-USB B port for power and data (and for reprogramming the flash)
- 40 pin 21x51 'DIP' style 1mm thick PCB with 0.1" through-hole pins also with edge castellations
  - Exposes 26 multi-function 3.3 V General Purpose I/O (GPIO), 3 can be used for ADC
  - Can be surface mounted as a module
- 3-pin ARM Serial Wire Debug (SWD) port
- Simple yet highly flexible power supply architecture
  - Various options for easily powering the unit from micro-USB, external supplies or batteries
- High quality, low cost, high availability
- Comprehensive SDK, software examples and documentation

For full details of the RP2350A microcontroller, see the RP2350 Datasheet. The headline features are:

- Dual Cortex-M33 or Hazard3 processors at up to 150MHz
  - On-chip PLL allows variable core frequency
- 520 kB multi-bank high performance SRAM
- External Quad-SPI flash with eXecute In Place (XIP) and 16 kB on-chip cache
- High performance full-crossbar bus fabric
- On-board USB1.1 (device or host)
- 30 multi-function GPIO pins (4 can be used for ADC)
  - 1.8-3.3 V IO Voltage (NOTE Pico 2 IO voltage is fixed at 3.3 V)
- 12-bit 500ksps Analogue to Digital Converter (ADC)
- Various digital peripherals
  - 2x UART, 2x I2C, 2x SPI, 24x PWM channels
  - 2x Timer with 4 alarms, 1x AON Timer
- 3x Programmable IO (PIO) blocks, 12 state machines total
  - Flexible, user-programmable high-speed IO
  - Can emulate interfaces such as SD Card and VGA

Pico 2 provides minimal (yet flexible) external circuitry to support the RP2350 chip: flash (Winbond W25Q32RV), crystal (Abracon ABM8-272-T3), power supplies and decoupling, and USB connector. The majority of the RP2350 microcontroller pins are brought to the user IO pins on the left and right edge of the board. Four RP2350 IO are used for internal functions - driving an LED, on-board Switched Mode Power Supply (SMPS) power control and sensing the system voltages.

Pico 2 has been designed to use either soldered 0.1" pin-headers (it is one 0.1" pitch wider than a standard 40-pin DIP package) or can be used as a surface mountable 'module', as the user IO pins are also castellated. There are SMT pads underneath the USB connector and BOOTSEL button, which allow these signals to be accessed if used as a reflow-soldered SMT module.

*[Figure 2. The pinout of the Raspberry Pi Pico 2 board]*

Pico 2 uses an on-board buck-boost SMPS which is able to generate the required 3.3 V (to power RP2350 and external circuitry) from a wide range of input voltages (1.8 to 5.5 V). This allows significant flexibility in powering the unit from various sources such as a single Lithium-ion cell, or 3x AA cells in series. Battery chargers can also be very easily integrated with the Pico 2 powerchain.

Reprogramming the Pico 2 flash can be done using USB (simply drag and drop a file onto the Pico 2 which appears as a mass storage device), or the standard Serial Wire Debug (SWD) port can reset the system and load and run code without any button presses. The SWD port can also be used to interactively debug code running on the RP2350.

### 1.1. Raspberry Pi Pico 2 design files

The source design files, including the schematic and PCB layout, are made available openly, with no limitations.

| Resource | Description |
|---|---|
| Schematic | The full schematic is reproduced in Appendix B. The schematic is also distributed alongside the layout files. |
| STEP 3D | A STEP 3D model of Raspberry Pi Pico 2, for 3D visualisation and fit check. |
| Fritzing | A Fritzing part for use in e.g. breadboard layouts. |

## Chapter 2. Differences from Raspberry Pi Pico

Pico 2 improves in the following ways from the original Raspberry Pi Pico board:

- double the on-board flash (2 MB to 4 MB)
- an upgrade from RP2040 to RP2350, which includes the following improvements:
  - higher core clock speed (133MHz to 150MHz)
  - double the on-chip SRAM (264 kB to 520 kB)
  - more powerful Arm cores (Dual-core cortex M0+ to Dual Cortex-M33)
  - RISC-V cores (none to Hazard3)
  - new security features, including Arm TrustZone for Cortex-M, signed boot, 8 kB of antifuse OTP for key storage, SHA-256 acceleration, a hardware TRNG, and fast glitch detectors
  - upgraded interfacing capabilities, increasing from 2 PIO blocks (8 state machines total), to 3 PIO blocks (12 state machines total)

## Chapter 3. Mechanical specification

The Raspberry Pi Pico 2 is a single sided 51x21mm 1mm thick PCB with a micro-USB port overhanging the top edge and dual castellated/through-hole pins around the remaining edges. Pico 2 is designed to be usable as a surface mount module as well as being in Dual Inline Package (DIP) type format, with the 40 main user pins on a 2.54mm (0.1") pitch grid with 1mm holes and hence compatible with veroboard and breadboard. Pico 2 also has 4x 2.1mm (+/- 0.05mm) drilled mounting holes to provide for mechanical fixing, see Figure 3.

*[Figure 3. The dimensions of the Raspberry Pi Pico 2 board.]*

### 3.1. Raspberry Pi Pico 2 pinout

The Pico 2 pinout has been designed to directly bring out as much of the RP2350 GPIO and internal circuitry function as possible, while also providing a suitable number of ground pins to reduce EMI (Electro Magnetic Interference) and signal crosstalk. This is important in general but especially for RP2350 which is built on a modern 40nm silicon process and hence the digital IO edge rates are very fast.

*[Figure 4. The pin numbering of the Raspberry Pi Pico 2 board.]*

A few RP2350 GPIO pins are used for internal board functions, these are:

| GPIO | Direction | Function |
|---|---|---|
| GPIO29 | IP | Used in ADC mode (ADC3) to measure VSYS/3 |
| GPIO25 | OP | Connected to user LED |
| GPIO24 | IP | VBUS sense - high if VBUS is present, else low |
| GPIO23 | OP | Controls the on-board SMPS Power Save pin |

Apart from GPIO and ground pins, there are 7 other pins on the main 40-pin interface:

| Pin | Name |
|---|---|
| PIN40 | VBUS |
| PIN39 | VSYS |
| PIN37 | 3V3_EN |
| PIN36 | 3V3 |
| PIN35 | ADC_VREF |
| PIN33 | AGND |
| PIN30 | RUN |

**VBUS** is the micro-USB input voltage, connected to micro-USB port pin 1. This is nominally 5V (or 0V if the USB is not connected or not powered).

**VSYS** is the main system input voltage, which can vary in the allowed range 1.8V to 5.5V, and is used by the on-board SMPS to generate the 3.3V for the RP2350 and its GPIO.

**3V3_EN** connects to the on-board SMPS enable pin, and is pulled high (to VSYS) via a 100k resistor. To disable the 3.3V (which also de-powers the RP2350), short this pin low.

**3V3** is the main 3.3V supply to RP2350 and its I/O, generated by the on-board SMPS. This pin can be used to power external circuitry (maximum output current will depend on RP2350 load and VSYS voltage, it is recommended to keep the load on this pin less than 300mA).

**ADC_VREF** is the ADC power supply (and reference) voltage, and is generated on Pico 2 by filtering the 3.3V supply. This pin can be used with an external reference if better ADC performance is required.

**AGND** is the ground reference for GPIO26-29, there is a separate analog ground plane running under these signals and terminating at this pin. If the ADC is not used or ADC performance is not critical, this pin can be connected to digital ground.

**RUN** is the RP2350 enable pin, and has an internal (on-chip) pull-up resistor to 3.3V of about ~50k. To reset RP2350, short this pin low.

Finally, there are also 7 Test Points (TP1-TP7) which can be accessed if required:

| Test Point | Function |
|---|---|
| TP1 | Ground (close coupled ground for differential USB signals) |
| TP2 | USB DM |
| TP3 | USB DP |
| TP4 | GPIO23/SMPS PS pin (do not use) |
| TP5 | GPIO25/LED (not recommended to be used) |
| TP6 | BOOTSEL |
| TP7 | 1V1 (do not use) |

TP1, TP2 and TP3 can be used to access the USB signals instead of using the micro-USB port. TP6 can be used to drive the system into mass-storage USB programming mode (by shorting it low at power-up). Note that TP4 and TP7 are not intended to be used externally, and TP5 is not really recommended to be used as it will only swing from 0V to the LED forward voltage (and hence can only really be used as an output with special care).

### 3.2. Surface-mount footprint

*[Figure 5. The SMT footprint of the Raspberry Pi Pico 2 board.]*

The footprint shows the test point locations and pad sizes as well as the 4 USB connector shell ground pads (A,B,C,D). The USB connector on Pico 2 is a through-hole part, which provides it with mechanical strength. The USB socket pins do not protrude all the way through the board, however solder does pool at these pads during manufacture and can stop the module sitting completely flat. Hence we provide pads on the SMT module footprint to allow this solder to reflow in a controlled manner when Pico 2 goes through reflow again.

For test points that are not used, it is acceptable to void any copper under these (with suitable clearance) on the carrier board.

Through trials with customers, we have determined that the paste stencil must be bigger than the footprint. Over-pasting the pads ensures the best possible results when soldering. We recommend paste zones 163% larger than the footprint.

*[Figure 6. The paste stencil of the Raspberry Pi Pico 2 board.]*

### 3.3. Recommended operating conditions

| Parameter | Value |
|---|---|
| Operating Temp Max | 85C (including self-heating) |
| Operating Temp Min | -20C |
| VBUS | 5V +/- 10% |
| VSYS Min | 1.8V |
| VSYS Max | 5.5V |

Note that VBUS and VSYS current will depend on use-case. Recommended maximum ambient temperature of operation is 70C.

## Chapter 4. Electrical specification

### 4.1. Power consumption

The power consumption tables show the typical VBUS (5V) current consumption during RP2350's low power states, and also various software use cases. These numbers are not guaranteed maximum values; they are an indication of the current consumption a user can typically expect the device to draw when used in these scenarios.

#### 4.1.1. Low Power States

All externally accessible GPIOs, SWD and SWCLK are unconnected. The RP2350's USB PHY has been powered down, and the DP and DM pull-downs enabled prior to entering the low power state. The USB cable remains connected to a host computer.

**Table 1. Low Power States Power Consumption**

| Low Power State | VBUS current (uA) | Power (mW) |
|---|---|---|
| P1.0 | 233 | 1.16 |
| P1.1 | 192 | 0.96 |
| P1.2 | 194 | 0.97 |
| P1.3 | 153 | 0.77 |
| P1.4 | 226 | 1.13 |
| P1.5 | 187 | 0.93 |
| P1.6 | 188 | 0.94 |
| P1.7 | 148 | 0.74 |
| RUN low | 388 | 1.9 |

#### 4.1.2. Typical Use Cases

All externally accessible GPIOs are unconnected, with the exception of GPIOs 0 and 1, which are connected to a Raspberry Pi Debug Probe. SWD and SWCLK are unconnected, and the USB cable remains connected to a host computer in all cases.

**Table 2. Typical Use Case Power Consumption**

| Use Case | VBUS current (uA) | Power (mW) |
|---|---|---|
| USB Boot mode - idle | 5470 | 27.4 |
| USB Boot mode - peak during boot | 14260 | 71.3 |
| USB Boot mode - UF2 write | 6613 | 33.1 |
| Hello_serial | 12427 | 62.1 |
| Hello_usb | 12740 | 63.7 |
| Hello_adc | 12503 | 62.5 |
| CoreMark single core benchmark | 9380 | 46.9 |

## Chapter 5. Applications information

### 5.1. Programming the flash

The on-board 4 MB QSPI flash can be (re)programmed either using the Serial Wire Debug port or by the special USB Mass Storage Device mode.

The simplest way to reprogram the Pico 2's flash is to use the USB mode. To do this, depower the board, then hold the BOOTSEL button down during board power-up (e.g. hold BOOTSEL down while connecting the USB). The Pico 2 will then appear as a USB Mass Storage Device. Dragging a special .uf2 file onto the disk will write this file to the flash and restart the Pico 2.

The USB boot code is stored in ROM on RP2350, so can not be accidentally overwritten.

### 5.2. General purpose I/O

The Raspberry Pi Pico 2's GPIO is powered from the on-board 3.3V rail and is therefore fixed at 3.3V.

The Pico 2 exposes 26 of the 30 possible RP2350 GPIO pins by routing them straight out to Pico 2 header pins. GPIO0 to GPIO22 are digital only and GPIO 26-28 are able to be used either as digital GPIO or as ADC inputs (software selectable).

One thing to note is that the ADC capable GPIO26-29 have an internal reverse diode to the VDDIO (3V3) rail and so the input voltage must not exceed VDDIO plus about 300mV. Also, if the RP2350 is unpowered, applying a voltage to these GPIO pins will 'leak' through the diode into the VDDIO rail. Normal digital GPIO pins 0-25 (and also the debug pins) do not have this restriction and therefore voltage can safely be applied to these pins when RP2350 is unpowered.

### 5.3. Using the ADC

The RP2350 ADC does not have an on-board reference and therefore uses its own power supply as a reference. On Pico 2 the ADC_AVDD pin (the ADC supply) is generated from the SMPS 3.3V by using an R-C filter (201 ohm into 2.2uF). This is a simple solution but does have the following drawbacks:

1. We are relying on the 3.3V SMPS output accuracy, which isn't great.
2. We can only do so much filtering and therefore ADC_AVDD will be somewhat noisy.
3. The ADC draws current (about 150uA if the temperature sense diode is disabled, but it varies from chip to chip) and therefore there will be an inherent offset of about 150uA*200 = ~30mV. There is a small difference in current draw when the ADC is sampling (about +20uA) so that offset will also vary with sampling as well as operating temperature.

Changing the resistance between the ADC_VREF and 3V3 pin can reduce the offset at the expense of more noise - which may be OK especially if the use case can support averaging over multiple samples.

Driving high the SMPS mode pin (GPIO23), to force the power supply into PWM mode, can greatly reduce the inherent ripple of the SMPS at light load, and therefore the ripple on the ADC supply. This does reduce the power efficiency of the board at light load, so the low-power PFM mode can be re-enabled between infrequent ADC measurements by driving GPIO23 low once more.

The ADC offset can be reduced by tying a second channel of the ADC to ground, and using this zero-measurement as an approximation to the offset.

For much improved ADC performance, an external 3.0V shunt reference, such as LM4040, can be connected from the ADC_VREF pin to ground. Note that if doing this the ADC range is limited to 0-3.0V signals (rather than 0-3.3V), and the shunt reference will draw continuous current through the 200 ohm filter resistor (3.3V-3.0V)/200 = ~1.5mA.

Note that the 1 ohm resistor on Pico 2 (R9) is designed to (maybe) help with shunt references that would otherwise become unstable when directly connected to 2.2uF. It also makes sure there is a little filtering even in the case that 3.3V and ADC_VREF are shorted together (which is a valid thing to do if you don't care about noise and want to reduce the inherent offset).

Finally, R7 can be relatively easily removed if a user wants to isolate ADC_VREF and do their own thing with the ADC voltage, for example powering it from an entirely separate voltage (e.g. 2.5V). Note that the ADC on RP2350 has only been qualified at 3.0/3.3V but should work down to about 2V.

### 5.4. Powerchain

Raspberry Pi Pico 2 has been designed with a simple yet flexible power supply architecture and can easily be powered from other sources such as batteries or external supplies. Integrating the Pico 2 with external charging circuits is also straightforward.

*[Figure 7. The powerchain of the Raspberry Pi Pico 2 board.]*

VBUS is the 5V input from the micro-USB port, which is fed through a Schottky diode to generate VSYS. The VBUS to VSYS diode (D1) adds flexibility by allowing power ORing of different supplies into VSYS.

VSYS is the main system 'input voltage' and feeds the RT6150 buck-boost SMPS, which generates a fixed 3.3V output for the RP2350 device and its IO (and can be used to power external circuitry). VSYS is R-C filtered and divided by 3 (by R5, R6, R16 and C3 in the Pico 2 schematic) and can be monitored on ADC channel 3. This can be used for example as a crude battery voltage monitor.

The buck-boost SMPS, as its name implies, can seamlessly switch from buck to boost mode, and therefore can maintain an output voltage of 3.3V from a wide range of input voltages, ~1.8V to 5.5V, which allows a lot of flexibility in the choice of power source.

GPIO24 monitors the existence of VBUS, while R10 and R1 act to pull VBUS down to make sure it is 0V if VBUS is not present.

GPIO23 controls the RT6150 PS (Power Save) pin. When PS is low (the default on Pico 2) the regulator is in Pulse Frequency Modulation mode, which, at light loads, saves considerable power by only turning on the switching MOSFETs occasionally to keep the output capacitor topped up. Setting PS high forces the regulator into Pulse Width Modulation (PWM) mode. PWM mode forces the SMPS to switch continuously, which reduces the output ripple considerably at light loads (which can be good for some use cases) but at the expense of much worse efficiency. Note that under heavy load the switcher will be in PWM mode irrespective of the PS pin state.

The SMPS EN pin is pulled up to VSYS by a 100k resistor and made available on Pico 2 pin 37. Shorting this pin to ground will disable the switcher and put it into a low power state.

> **NOTE:** The RP2350 has an on-chip switching regulator that powers the digital core at 1.1V (nominal) from the 3.3V supply, which is not shown in Figure 7.

### 5.5. Powering Pico 2

The simplest way to power Pico 2 is to plug in the micro-USB, which will power VSYS (and therefore the system) from the 5V USB VBUS voltage, via D1 (so VSYS becomes VBUS minus the Schottky diode drop).

If the USB port is the only power source, VSYS and VBUS can be safely shorted together to eliminate the Schottky diode drop (which improves efficiency and reduces ripple on VSYS).

If the USB port is not going to be used, it is safe to power Pico 2 by connecting VSYS to your preferred power source (in the range ~1.8V to 5.5V).

> **IMPORTANT:** If you are using Raspberry Pi Pico 2 in USB Host mode (e.g. using one of the TinyUSB host examples) then you must power Pico 2 by providing 5V to the VBUS pin.

The simplest way to safely add a second power source to Pico 2 is to feed it into VSYS via another Schottky diode (see Figure 8). This will 'OR' the two voltages, allowing the higher of either the external voltage or VBUS to power VSYS, with the diodes preventing either supply from back-powering the other. For example a single Lithium-Ion cell (cell voltage ~3.0V to 4.2V) will work well, as will 3xAA series cells (~3.0V to ~4.8V) and any other fixed supply in the range ~2.3V to 5.5V.

*[Figure 8. Raspberry Pi Pico 2 power ORing using diodes.]*

An improved way to power from a second source is using a P-channel MOSFET (P-FET) to replace the Schottky diode as shown in Figure 9. Here, the gate of the FET is controlled by VBUS, and will disconnect the secondary source when VBUS is present. The P-FET should be chosen to have low on resistance.

An example of a suitable P-MOSFET for most situations is Diodes DMG2305UX which has a maximum Vt of 0.9V and Ron of 100m ohm (at 2.5V Vgs).

*[Figure 9. Raspberry Pi Pico 2 power ORing using P channel MOSFET.]*

> **CAUTION:** If using Lithium-Ion cells they must have, or be provided with, adequate protection against over-discharge, over-charge, charging outside allowed temperature range, and overcurrent. Bare, unprotected cells are dangerous and can catch fire or explode if over-discharged, over-charged or charged / discharged outside their allowed temperature and/or current range.

### 5.6. Using a battery charger

Pico 2 can also be used with a battery charger. Figure 10 shows an example of using a 'Power Path' type charger (where the charger seamlessly manages swapping between powering from battery or powering from the input source and charging the battery, as needed).

*[Figure 10. Using Raspberry Pi Pico 2 with a charger.]*

In the example we feed VBUS to the input of the charger, and we feed VSYS with the output via the previously mentioned P-FET arrangement. Depending on your use case you may also want to add a Schottky diode across the P-FET as described in the previous section.

### 5.7. USB

RP2350 has an integrated USB1.1 PHY and controller which can be used in both Device and Host mode. Pico 2 adds the two required 27 ohm external resistors and brings this interface to a standard micro-USB port.

The USB port can be used to access the USB bootloader (BOOTSEL mode) stored in the RP2350 boot ROM. It can also be used by user code, to access an external USB device or host.

### 5.8. Debugging

Raspberry Pi Pico 2 brings the RP2350 Serial Wire Debug (SWD) interface to a 3 pin debug header on the lower edge of the board.

> **NOTE:** The RP2350 chip has internal pull up resistors on the SWDIO and SWCLK pins, both nominally 60k.

## Appendix A: Availability

Raspberry Pi guarantee availability of the Raspberry Pi Pico 2 product until at least January 2040.

**Table 3. Part Numbers**

| Model | Order Code | EAN | Minimal Order Quantity | RRP |
|---|---|---|---|---|
| Raspberry Pi Pico 2 | SC1631 | 5056561803951 | 1+ pcs / Bulk | US$5.00 |
| Raspberry Pi Pico 2 with Headers | SC1632 | 5056561803968 | 1+ pcs / Bulk | US$6.00 |

## Appendix B: Pico 2 schematic

*[Figure 11. The Raspberry Pi Pico 2 board schematic.]*

## Appendix C: Pico 2 component locations

*[Figure 12. The Raspberry Pi Pico 2 board component locations.]*
