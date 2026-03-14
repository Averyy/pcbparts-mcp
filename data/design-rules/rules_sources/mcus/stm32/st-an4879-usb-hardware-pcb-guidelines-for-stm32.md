---
source: "ST AN4879 -- USB Hardware/PCB Guidelines for STM32"
url: "https://www.st.com/resource/en/application_note/an4879-introduction-to-usb-hardware-and-pcb-guidelines-using-stm32-mcus-stmicroelectronics.pdf"
format: "PDF 31pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 9192
---
# Introduction to USB hardware and PCB guidelines using STM32 MCUs

## Introduction

STM32 microcontrollers include a group of products embedding a USB (universal serial bus) peripheral. Full-speed and high-speed operations are provided through embedded and/or external PHYs (physical layers).

This application note gives an overview of the USB peripherals implemented on STM32 MCUs and provides hardware guidelines for PCB design to ensure electrical compliance with USB standards.

## 1 General information

**References:**
- System Level ESD-expanded, JEDEC, September 2013
- Improve System ESD Protection While Lowering On-Chip ESD Protection, www.mobiledevdesign.com, February 2009
- USB 2.0 specification, revision 2.0, April 2000 (www.usb.org)
- On The Go and Embedded Host Supplement to the USB revision 2.0 specification, revision 2.0, July 2012 (www.usb.org)
- High Speed USB Platform Design Guidelines (www.usb.org)

## 2 USB on STM32 products

Each device with USB support embeds at least one of the following interfaces:

| Category | Description | Integrated PHY |
|---|---|---|
| A (USB) | Universal serial bus full-speed device interface | USB2.0 FS |
| B (OTG_FS) | USB on-the-go full-speed | USB2.0 FS |
| C (OTG_HS) | USB on-the-go high-speed (requires external ULPI PHY) | -- |
| D (OTG_HS/OTG) | USB on-the-go high-speed with embedded HS PHY | USB2.0 HS |
| E (USB) | Universal serial bus full-speed host/device interface | USB2.0 FS |

### 2.2 Supported USB speeds

**OTG_FS:**
| Mode | FS (12 Mbit/s) | LS (1.5 Mbit/s) |
|---|---|---|
| Host | Yes | Yes |
| Device | Yes | No |

**OTG_HS:**
| Mode | HS (480 Mbit/s) | FS (12 Mbit/s) | LS (1.5 Mbit/s) |
|---|---|---|---|
| Host | Yes | Yes | Yes |
| Device | Yes | Yes | No |

### 2.3 Protection against ESD and EMI

System must comply with JESD22-A114D (HBM, up to 2 kV) and IEC 61000-4-2 standards.

STM32 MCUs are HBM tolerant up to 2 kV discharge. IEC 61000-4-2 compliance requires dedicated ESD protection components placed as close as possible to the receptacle.

| Interface | Low price protection | Low area protection |
|---|---|---|
| USB FS | USBLC6-2SC6 (+ ESDA7P60-1U1M for VBUS) | USBLC6-2P6 (+ ESDA7P60-1U1M for VBUS) |
| USB FS OTG | USBLC6-4SC6 | DSILC6-4P6 |
| USB HS | ECMF02-2AMX6 (+ ESDA7P60-1U1M for 5V VBUS) | |
| USB HS OTG | ECMF02 | ECMF02-2AMX6 (+ ESDA7P60-1U1M for 5V VBUS + ESDALC6V1-1U2 for ID) |

### 2.4 Clock

The FS USB device/OTG requires a precise 48 MHz clock, generated from:
- Internal main PLL (requires HSE crystal oscillator), or
- Internal 48 MHz oscillator, synchronized via:
  - USB data stream SOF signalization (crystal-less, device mode only)
  - Internal 48 MHz oscillator trimmed on LSE (not accurate enough for USB host)
  - MSI and LSE (STM32L47x/L48x only)

For HS operation: OTG PHY connected via 12-signal ULPI port, clocked using 60 MHz output from HS PHY.

For STM32F7x3xx: USB HS PHY includes two PLLs:
- PLL1: HSE input (12, 12.5, 16, 24, or 25 MHz), outputs 60 MHz
- PLL2: outputs 480 MHz for high-speed

> AHB frequency must be > 14.2 MHz for USB OTG_FS and > 30 MHz for USB OTG_HS.

### 2.5 Power

USB transceiver operating voltage: 3.0 to 3.6 V, from VDD or dedicated VDDUSB.

Key points:
- USB FS transceiver functionality ensured down to 2.7 V. Electrical characteristics degraded between 2.7-3.0 V.
- VDDUSB pin must be connected to two external decoupling capacitors (100 nF ceramic + 1 uF tantalum or ceramic)
- When VDDUSB is connected to a separate power supply, it must be the last applied and first removed
- On STM32F7x3xx: VDD12OTGHS pin needs external 2.2 uF capacitor
- On STM32H7x3: VDD50USB can supply VDD33USB via internal USB regulator

### 2.6 VBUS sensing detection

A USB device must use VBUS sensing detection. Two cases:
- **Bus-powered:** VBUS sensing not mandatory (USB always connected when powered)
- **Self-powered:** VBUS sensing is mandatory

PA9 is a five volt-tolerant pin dedicated to VBUS sensing. Must avoid 5 V VBUS on PA9 when MCU is not powered (violates absolute maximum ratings). Use voltage divider to keep voltage below 4 V.

#### 2.6.1 Simple resistor divider

- VDD 3.0-3.6 V range: 82 kohm (to GND), 33 kohm (to VBUS)
- VDD 1.65-2.0 V range: 68 kohm (to GND), 82 kohm (to VBUS)

Assessed with +/-1% tolerance, checked against VIL/VIH across STM32 families, guaranteeing switching when VBUS is between 0.8 and 3.67 V.

> Works well when GPIO maximum operating conditions >= VDD + 3.6 V

*[Figure 4. Simple resistor divider]*

*[Figure 5. Resistor divider supporting both 1.8 and 3.3V ranges]*

#### 2.6.2 MOSFET detector

When GPIO input tolerance is lower (< VDD + 3.6 V), use N-channel MOSFET (2N7002). Detection is inverted (low when VBUS present).

*[Figure 6. VBUS detection with MOSFET]*

## 3 Hardware guidelines for USB implementation

### 3.1 USB FS upstream port

USB FS impedance driver is always managed internally -- no external serial resistors needed on data lines.

Two use cases:
- **Self-powered:** Platform provides own power supply, acts as upstream port
- **Bus-powered:** Platform supplied only through VBUS

#### 3.1.1 USB FS upstream port in self-powered applications

- Only start USB PHY and controller on VBUS detection
- Implement resistor bridge for VBUS detection
- Use ESD protection as close as possible to USB connector
- USB_DP (D+) must be pulled up with 1.5 kohm resistor to 3.0-3.6 V (embedded on some STM32s)

*[Figure 7. USB FS upstream with embedded pull-up in self-powered applications]*

*[Figure 8. USB FS upstream without embedded pull-up in self-powered applications]*

> DP pull-up must be connected only when VBUS is plugged. A GPIO drives it after VBUS detection.

#### 3.1.2 USB FS upstream port in bus-powered applications

PHY and controller must always be active. Use external LDO (e.g., LDO39050PU33R) to lower input supply. Place ESD protection close to connector.

*[Figure 9. USB FS upstream with embedded pull-up in bus-powered applications]*

*[Figure 10. USB FS upstream without embedded pull-up in bus-powered applications]*

### 3.2 USB FS downstream port

VBUS overload must be indicated to user via switch with overcurrent protection (STMPS2151STR or equivalent). ESD protection close to connector.

*[Figure 11. USB FS downstream implementation]*

### 3.3 OTG applications through embedded PHY

OTG platforms must include:
- STM32 MCU supporting OTG
- Micro-AB connector (USB role identified through ID pin)
- VBUS generation when acting as downstream facing port
- VBUS current overflow monitoring

Requirements:
- OTG specification requires capacitor (max 4.7 uF) on VBUS
- ESD protection close to connector
- Power switch (e.g., STMPS2151STR) required
- Route VBUS far from DP/DM
- STM32 must always be supplied when connected as device to a host

*[Figure 12. OTG schematic implementation (dual-mode)]*

### 3.4 OTG_HS PHY connected through ULPI

Refer to High Speed USB Platform Design Guidelines (www.usb.org). For full-speed driver part of a high-speed driver, impedance is 45 ohm +/-10%.

Recommendations:
- Crystal oscillator required for ULPI CLK precision
- OTG specification requires capacitor (max 4.7 uF) on VBUS
- ESD protection close to connector

*[Figure 13. USB HS via ULPI interface]*

#### 3.4.1 Compatible external USB HS PHYs

Tested PHYs: ISP1705AET, USB3300-EZK, USB3320C-EZK on various STM32 evaluation boards.

### 3.5 USB applications through embedded OTG_HS PHY

For STM32F7x3 devices (internal HS USB PHY):
- External 2.2 uF capacitor on VDD12OTGHS pin
- OTG_HS_REXT pin connected to GND via external precision resistor (3 kohm +/-1%) for calibration

## 4 FAQs

**Minimum operating voltage for USB?** VDD/VDDUSB >= 2.7 V for functionality. 3.0 V minimum for USB specification compliance.

**USB below 3.0 V?** PLL generates 48 MHz correctly and transceivers are functional, but electrical signals are not USB 2.0 compliant (eye diagram test fails). USB is operational but cannot get certification.

**Pull-up resistor always needed on D+?** A full-speed device uses pull-up on D+ to identify itself. Embedded on some STM32s, otherwise must be added externally.

**VBUS sensing resistor bridge values?** Voltage must be < 4 V and > 0.7 x VDD. ~200 uA typical current consumption.

**External clock source (HSE bypass) for USB?** Yes, HSE ON with external crystal or HSE bypass mode required. HSI cannot be used.

**Two USB ports simultaneously?** Yes, feasible.

**Multiple devices on one USB host port?** No, hub operation not supported.

**USB FS for LS device?** No, only full-speed in device mode.

**Matching resistors embedded?** Yes, matching output impedance embedded in internal USB PHYs, compliant with USB specification. No external resistors needed.

**USB when VDD < 2.7 V?** Only if VDDUSB pin is available. MCU can be powered at minimum specified voltage while independent 3.3 V supply connects to VDDUSB.
