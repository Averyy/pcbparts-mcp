# JLCPCB MCP Test Reference Boards

Reference board BOMs for testing the MCP server. The LLM should determine appropriate searches based on the components listed.

---

## 1. Blues Notecarrier-A

**Purpose:** Development carrier board for battery-powered wireless IoT applications using the Blues Notecard. Features complete power management with USB, LiPo battery, and solar charging support, plus onboard cellular/WiFi and active GPS antennas.

**Repository:** https://github.com/blues/note-hardware/tree/master/Notecarrier-A

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| BQ24210DQCT | Li-Ion Battery Charger (800mA) | QFN |
| MAX17225ELT | Low-power Boost Converter | SOT23 |
| TPS62748YFPT | High-efficiency Buck Converter | DSBGA |
| SM6T6V8A | TVS Diode 600W 6.8V | SMB |
| PESD5V0L5UV | 5-channel ESD Protection | SOT-665 |
| BGA725L6E6327FTSA1 | GPS LNA | TSLP-6 |
| LQW18AN12NG80 | 12nH RF Inductor | 0603 |
| AO3420 | N-channel MOSFET | SOT-23 |
| XFL4020-222MEC | 2.2uH Shielded Inductor | 4020 |
| JST PH 4-pin | Battery/Solar Connectors | SMD |
| JST SH 4-pin | Qwiic I2C Connectors | SMD |
| USB Micro-B | Power/Data Connector | SMD |
| Nano-SIM Socket | External SIM Slot | SMD |
| 10uF/10V X5R | Output Capacitors | 0402 |
| 100nF/16V | Decoupling Capacitors | 0402 |

---

## 2. Blues Swan

**Purpose:** Low-cost STM32L4R5-based microcontroller dev board in Adafruit Feather form factor. Optimized for battery-powered IoT with 120MHz, 2MB Flash, 640KB RAM. Designed for edge inferencing and companion use with Blues Notecard.

**Repository:** https://github.com/blues/note-hardware/tree/master/Swan

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| STM32L4R5ZIY6 | ARM Cortex-M4 MCU 120MHz | WLCSP144 |
| TPS62748YFPT | DC/DC Step-down Converter | DSBGA |
| TPS63020DSJR | Buck-boost Converter | SON-14 |
| MCP73831-2ACI/MC | LiPo Battery Charger | SOT-23-5 |
| MAX17225ELT+T | Boost Converter | SOT23-6 |
| AP2139AK-3.3TRG1 | 3.3V LDO | SOT-23 |
| MAX40203ANS+ | Ideal Diode (x6) | SOT-23 |
| ABS06-107-32.768KHZ-T | 32.768kHz Crystal | 3215 |
| SM6T6V8A | TVS Diode | SMB |
| ESD5Z3.3T1G | ESD Protection (x2) | SOD-523 |
| 1285AS-H-2R2M | 2.2uH Inductor | 1210 |
| XFL4020-222MEC | 2.2uH Inductor | 4020 |
| USB Micro-B | Power/Data Connector | SMD |
| JST SH 4-pin | Qwiic Connector | SMD |
| JST PH 2-pin | Battery Connector | SMD |
| 100uF/6.3V Tantalum | Bulk Capacitors | Case A |

---

## 3. Olimex ESP32-POE

**Purpose:** IoT development board combining WiFi, Bluetooth, and 100Mb Ethernet with IEEE 802.3af Power-over-Ethernet support. Enables deployment of connected devices powered directly through Ethernet cable.

**Repository:** https://github.com/OLIMEX/ESP32-POE

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| ESP32-WROOM-32 | WiFi/BLE Module | Module |
| LAN8710A-EZC | 10/100 Ethernet PHY | QFN-32 |
| TPS2378DDAR | PoE PD Controller | HSOIC-8 |
| TX4138 | PoE Flyback Controller | ESOIC-8 |
| TPS62A02ADRLR | Sync Buck Converter | SOT-563 |
| CH340E | USB-UART Converter | MSOP-10 |
| BL4054B-42TPRN | LiPo Charger | SOT-23-5 |
| SN74LVC1G04DBVR | Single Inverter | SOT-23-5 |
| ESDS314DBVR | ESD Protection | SOT-23-5 |
| SMBJ6.0A | TVS Diode | SMB |
| BAT54C | Dual Schottky Diode | SOT-23 |
| RJ45 w/ Magnetics | Ethernet Jack | THT |
| USB Mini-B | Programming Connector | SMD |
| MicroSD Socket | Storage | Push-push |
| 470uF Electrolytic | PoE Bulk Capacitor | Radial |

---

## 4. Seeed XIAO ESP32-C3

**Purpose:** Thumb-sized (21x17.5mm) IoT development board based on ESP32-C3. Designed for IoT applications, wireless wearables, and embedded systems requiring WiFi/BLE in compact form factor.

**Repository:** https://github.com/Seeed-Studio/Seeed_Studio_XIAO_Series

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| ESP32-C3 | RISC-V WiFi/BLE MCU, 4MB Flash | QFN-32 |
| ETA4054 | Li-Ion Battery Charger (380mA) | SOT-23-5 |
| 3.3V LDO | Voltage Regulator (700mA max) | SOT-23 |
| USB Type-C | Power/Data Connector | 16-pin |
| Ceramic Antenna | 2.4GHz WiFi/BLE | Chip |
| U.FL Connector | External Antenna | SMD |
| Tactile Switch | Reset/Boot Buttons | SMD |
| Charge LED | Status Indicator | 0402 |
| 100nF Capacitors | Decoupling | 0402 |
| 10K Resistors | Pull-ups/Pull-downs | 0402 |

---

## 5. SparkFun BME280 Breakout

**Purpose:** Compact atmospheric sensor module measuring barometric pressure (30-110 kPa), relative humidity (0-100%), and temperature (-40 to 85C). For weather stations, altitude measurement, and HVAC monitoring.

**Repository:** https://github.com/sparkfun/SparkFun_BME280_Breakout_Board

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| BME280 | Environmental Sensor | LGA-8 (2.5x2.5mm) |
| 0.1uF 25V Capacitor | Decoupling (x2) | 0603 |
| 4.7K Resistor | I2C Pull-ups (x4) | 0603 |
| 4-pin Header | I2C Interface | PTH |
| 6-pin Header | SPI Interface | PTH Female |

---

## 6. SparkFun LSM6DSO Breakout

**Purpose:** 6-axis IMU combining 3-axis accelerometer and 3-axis gyroscope with 9kB FIFO buffer. For motion sensing including shock/tilt detection, pedometer, tap detection, and orientation sensing.

**Repository:** https://github.com/sparkfun/SparkFun_Qwiic_6DoF_LSM6DSO

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| LSM6DSO | 6-axis IMU (Accel + Gyro) | LGA-14 (2.5x3mm) |
| 4.7K Resistor | I2C Pull-ups (x2) | 0603 |
| 10K Resistor | CS Pull-up | 0603 |
| 100K Resistor | Pull-down | 0603 |
| 1K Resistor | LED Current Limit | 0603 |
| 30 ohm Ferrite Bead | Power Filter | 0603 |
| 0.1uF Capacitor | Decoupling (x2) | 0603 |
| JST SH 4-pin | Qwiic Connector (x2) | SMD |
| Red LED | Power Indicator | 0603 |

---

## 7. Adafruit ESP32-S3 Feather

**Purpose:** Dual-core 240 MHz WiFi/BLE development board with native USB support in the Feather form factor. For IoT, wearables, and smart home projects with Feather Wing ecosystem compatibility.

**Repository:** https://github.com/adafruit/Adafruit-ESP32-S3-Feather-PCB

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| ESP32-S3-MINI-1 | WiFi/BLE Module 8MB Flash | Module |
| MAX17048 | LiPo Fuel Gauge | DFN-8 |
| MCP73831 | LiPo Charger | SOT-23-5 |
| AP2112K | 3.3V 500mA LDO | SOT-23-5 |
| WS2812B | NeoPixel RGB LED | 5050 |
| USB Type-C | Power/Data Connector | 16-pin |
| JST SH 4-pin | STEMMA QT Connector | SMD |
| JST PH 2-pin | Battery Connector | SMD |
| Red LED | User LED | 0603 |
| Yellow LED | Charge Status | 0603 |
| 0402 Capacitors | Various values | 0402 |
| 0402 Resistors | Various values | 0402 |

---

## 8. Soldered BME680 Breakout

**Purpose:** Environmental sensing module with BME680 4-in-1 sensor measuring temperature, pressure, humidity, and air quality (IAQ index). For weather stations and indoor air quality monitoring with easyC/Qwiic connectivity.

**Repository:** https://github.com/SolderedElectronics/BME680-breakout-board-with-easyC-hardware-design

*Note: Hardware repository not yet publicly available. Components inferred from documentation.*

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| BME680 | 4-in-1 Environmental Sensor | LGA (3x3mm) |
| 3.3V LDO | Voltage Regulator | SOT-23 |
| 10K Resistor | I2C Pull-ups (x2) | 0603 |
| 100nF Capacitor | Decoupling | 0603 |
| JST SH 4-pin | easyC/Qwiic Connector (x2) | SMD |

---

## 9. Dangerous Prototypes Bus Pirate 5

**Purpose:** Universal serial interface debugging tool converting terminal commands into common bus protocols (1-Wire, I2C, SPI, UART, MIDI). Features live voltage/current measurement, programmable 1-5V power supply with current limiting, and color LCD.

**Repository:** https://github.com/DangerousPrototypes/BusPirate5-hardware

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| RP2040 | Dual-core ARM Cortex-M0+ MCU | QFN-56 |
| W25Q128JVSIQ | 128Mbit SPI Flash | SOIC-8 |
| MT29F1G01ABAFDWB | 1Gbit NAND Flash | UPDFN-8 |
| AiP74LVC1T45 | Bidirectional Level Shifter (x8) | SOT-363 |
| AIP74HCT245 | 8-bit Bus Transceiver | TSSOP-20 |
| AIP74HC595 | Shift Register (x2) | TSSOP-16 |
| CD4067 | 16-ch Analog Mux | TSSOP-24 |
| AP2127 | Adjustable LDO (0.8-5V) | SOT-23-5 |
| ME6211A33 | 3.3V Fixed LDO | SOT-89 |
| LMV321 | Rail-to-rail Op-amp (x3) | SOT-23-5 |
| LMV324 | Quad Op-amp (x2) | TSSOP-14 |
| LMV331 | Comparator (x3) | SOT-23-5 |
| SI2301 | P-ch MOSFET (x10) | SOT-523 |
| MMBT7002K | N-ch MOSFET | SOT-23 |
| SK6812 | Addressable RGB LED (x18) | Various |
| 12MHz Crystal | MCU Oscillator | 3225 |
| USB Type-C | Power/Data Connector | SMD |
| 0.2R Current Sense | Shunt Resistor | 2512 |
| TFT LCD 240x320 | Color Display | Module |

---

## 10. ANAVI Macro Pad 8

**Purpose:** Open-source 8-key programmable mechanical keyboard with RGB backlighting running QMK firmware. For custom macros, shortcuts, and automation via USB.

**Repository:** https://github.com/AnaviTechnology/anavi-macro-pad-8

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| ATmega32U4-AU | 8-bit AVR MCU with USB | TQFP-44 |
| USB Micro-B | Power/Data Connector | SMD |
| 16MHz Crystal | MCU Oscillator | 3225 |
| 1N5819 | Schottky Diode | SMA |
| Cherry MX Compatible | Mechanical Switches (x8) | THT |
| 3mm LED | Backlight LEDs (x8) | THT |
| NPN Transistor | LED Driver | SOT-23 |
| 22R Resistor | USB Data Lines (x2) | 0603 |
| 10K Resistor | Reset Pull-up | 0603 |
| 68R Resistor | LED Current Limit (x8) | 0603 |
| 4.7K Resistor | I2C Pull-ups (x2) | 0603 |
| 22pF Capacitor | Crystal Load (x2) | 0603 |
| 1uF Capacitor | UCAP Decoupling | 0603 |
| 100nF Capacitor | Decoupling | 0603 |
| 4-pin Header | I2C/OLED Connector | PTH |
| 6-pin Header | ISP Programming | PTH |

---

## 11. Blues Cygnet

**Purpose:** Low-cost STM32L433CC-based microcontroller board in the Adafruit Feather form factor, designed for battery-powered IoT applications. Features integrated LiPo charging, USB-C connectivity, and a versatile power management system with buck-boost regulation for maximum efficiency.

**Repository:** https://github.com/blues/note-hardware/tree/master/Cygnet

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| STM32L433CCU6 | ARM Cortex-M4 MCU, 80MHz, 256KB Flash | UFQFPN-48 |
| TPS63020DSJT | Buck-Boost Switching Regulator, 3.3V 4A | VSON-14 |
| ISL9122AIINZ-T | I2C-Controlled Buck-Boost Regulator | WLCSP-12 |
| MCP73831-2ACI/MC | LiPo Battery Charge Management IC | DFN-8 |
| AP2139AK-3.3TRG1 | Ultra-Low Quiescent Current LDO | SOT-23-5 |
| LM66200DRLR | Ideal Diode with Reverse Polarity Protection | SOT-563-6 |
| 12402012E212A | USB Type-C Connector, 24-Pin | SMD |
| SM6T6V8A | TVS Diode, 6.8V, 600W | SMB |
| ESD5Z3.3T1G | ESD Protection Diode, 3.3V | SOD-523 |
| SML-P12U2TT86R | Red LED Indicator | 0402 |
| FTSH-107-01-L-DV-K | SWD/JTAG Debug Header, 14-Pin | 1.27mm pitch |
| BM04B-SRSS-TB | Qwiic/STEMMA QT I2C Connector | JST-SH 4-Pin |

---

## 12. Blues Notecarrier-F

**Purpose:** Feather-compatible carrier board designed for rapid IoT prototyping with the Blues Notecard cellular modem. Provides complete power management (USB, LiPo, and solar charging), level shifting for I2C communication, and multiple GPIO breakouts for sensors and peripherals.

**Repository:** https://github.com/blues/note-hardware/tree/master/Notecarrier-F

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| BQ24210DQCR | Solar/USB LiPo Battery Charger IC | WSON-10 |
| TPS62748YFPR | Ultra-Low Power Buck Converter | DSBGA-8 |
| MAX17225ELT+T | Boost Converter, 1.8-5V 1A | TDFN-6 |
| TXS0102DCUR | 2-Channel Bidirectional I2C Level Shifter | VFSOP-8 |
| DGQ2788AEN-T1-GE4 | Quad SPDT Analog Switch | UFQFN-16 |
| B360A-13-F | Schottky Diode, 60V 3A | SMA |
| SM6T6V8A | TVS Diode, 6.8V 600W | SMB |
| ESDLC5V0M5-TP | 5-Channel USB ESD Protection | SOT-563-6 |
| 10118193-0001LF | Micro-USB Type-B Connector | SMD |
| CJS-1200TA | SPDT Slide Switch | SMD |
| SM04B-SRSS-TB | Qwiic I2C Connector | JST-SH 4-Pin |
| PPTC161LFBN-RC | 16-Pin Female Header (Feather) | 2.54mm PTH |

---

## 13. Olimex ESP32-GATEWAY

**Purpose:** IoT development platform providing triple connectivity: WiFi, Bluetooth Low Energy, and wired Ethernet. Designed for gateway applications where reliable network bridging between wireless sensors and wired infrastructure is needed, with additional microSD storage for data logging.

**Repository:** https://github.com/OLIMEX/ESP32-GATEWAY

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| ESP32-WROOM-32E-N4 | ESP32 WiFi/BLE module with 4MB flash | Module |
| LAN8710A-EZC-ABC | Ethernet PHY transceiver (10/100 Mbps) | QFN-32 |
| TPS62A02ADRLR | 2A Synchronous Step-down DC-DC | SOT-563-6 |
| CH340X | USB to UART bridge controller | MSOP-10 |
| RJLD-060TC1 | RJ45 Ethernet connector with magnetics | THT |
| WPM2015-3/TR | P-channel MOSFET for power switching | SOT-23 |
| 1N5819S4 | Schottky barrier diode (40V, 1A) | SOD-123 |
| SMBJ6.0A | TVS diode for transient protection | SMB |
| GG0402052R542P | ESD protection TVS diode array | 0402 |
| 1N5822/SS34 | Schottky rectifier (3A, 40V) | SMA |
| USB-C Connector | USB Type-C for power and programming | SMD |
| MicroSD Socket | MicroSD card connector | SMD |

---

## 14. Olimex Neo6502pc

**Purpose:** Modern retro computer using a genuine WDC 65C02 processor paired with an RP2040 co-processor. Provides HDMI video output, USB keyboard/mouse/gamepad support, and USB flash drive storage - bridging authentic 6502 computing with contemporary I/O capabilities.

**Repository:** https://github.com/OLIMEX/Neo6502pc

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| W65C02S6TQTG-14 | WDC 65C02 8-bit microprocessor (14MHz) | TQFP-44 |
| RP2040 | Dual-core ARM Cortex-M0+ MCU | QFN-56 |
| CH334S | 4-port USB 2.0 hub controller | SSOP-28 |
| CH217K | USB hub current limiting switch | SOT-23-6 |
| ZD25Q16BTIGT | 16Mbit SPI NOR flash memory | SOIC-8 |
| 74LVC245APW | 8-bit bus transceiver (level shifter) | TSSOP-20 |
| HDMI-SWM-19 | HDMI Type-A female connector | SMD |
| USB-C 16P | USB Type-C programming connector | SMD |
| USB-A Connector | USB Type-A host ports (x4) | THT |
| 12MHz Crystal | Clock oscillator for RP2040 | 3225 |
| FSMD035-1206 | Resettable PTC fuse (350mA) | 1206 |
| SS-12D10L5 | SPDT slide switch for hub reset | THT |

---

## 15. Seeed Wio Terminal

**Purpose:** Complete development platform featuring an ATSAMD51 microcontroller, WiFi/Bluetooth connectivity via RTL8720DN module, a 2.4" LCD display, buttons, and multiple expansion ports. Designed for IoT prototyping running Arduino, MicroPython, or ArduPy.

**Repository:** https://github.com/Seeed-Studio/OSHW-WioTerminal

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| ATSAMD51P19A-CTUT | ARM Cortex-M4F MCU (120MHz, 512KB Flash) | TQFP-128 |
| RTL8720DN-VA1-CG | WiFi/Bluetooth Dual-band Module | LGA Module |
| W25Q32JVSSIQ | 32Mbit SPI NOR Flash Memory | SOP-8 |
| MP2161GJ | 2A DC-DC Buck Converter | TSOT-23-8 |
| AP2112K-3.3TRG1 | 600mA 3.3V LDO Regulator | SOT-23-5 |
| LMV358IDGKR | Dual Op-Amp (for audio) | VSSOP-8 |
| LIS3DHTR | 3-axis Accelerometer | LGA-16 |
| FA-128 40MHz | Crystal Oscillator | 2-pin SMD |
| UBF31-0171 | USB Type-C Receptacle | SMD |
| DPX165950DT-8148A1 | WiFi Antenna Diplexer | SMD |
| SP3012-06UTG | 6-Channel ESD Protection Array | USON-10 |
| B5819WS | Schottky Barrier Diode | SOD-323 |
| 1206L300SLTHYR | 3A Resettable PTC Fuse | 1206 |
| MLZ2012M2R2HT000 | 2.2uH Power Inductor | 0805 |

---

## 16. ANAVI Light Controller

**Purpose:** ESP8266-based WiFi controller for 12V RGB LED strips. Provides 3-channel PWM output via power MOSFETs to control non-addressable (analog) LED strips, with optional I2C sensor connectivity for ambient light sensing or environmental monitoring.

**Repository:** https://github.com/AnaviTechnology/anavi-light-controller

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| ESP-12E | ESP8266 WiFi Module (4MB Flash) | Castellated Module |
| IRF8721PBF-1 | 30V N-Channel Power MOSFET (14A) | SO-8 |
| LD1117S33TR | 3.3V 800mA LDO Regulator | SOT-223 |
| 1N4148 | Fast Switching Diode | DO-35 |
| 68R Resistor | LED Current Limiting | 0603 |
| 4.7K Resistor | I2C Pull-ups (x2) | 0603 |
| 220R Resistor | MOSFET Gate Resistors (x3) | 0603 |
| 2K Resistor | ESP8266 Pull-up | 0603 |
| 100nF Capacitor | Ceramic Bypass | 0603 |
| 10uF Capacitor | Electrolytic Filter | 0805 |
| DC Barrel Jack | 12V Power Input | THT |
| Screw Terminal 4-pos | RGB LED Strip Output | Phoenix MKDS1.5 |
| Pin Header 1x04 | I2C Sensor Connectors (x3) | 2.54mm PTH |
| SW_PUSH_6mm | Momentary Reset Button | THT |

---

## 17. SparkFun OpenLog Artemis

**Purpose:** Versatile open-source data logger with automatic sensor detection for 50+ Qwiic sensors. Features a built-in 9-axis IMU (ICM-20948), RTC timestamping, and microSD storage. Designed for extended battery operation with sleep currents around 500uA.

**Repository:** https://github.com/sparkfun/OpenLog_Artemis

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| Artemis Module | Apollo3 ARM Cortex-M4F MCU (BLE, 1MB Flash) | Module |
| ICM-20948 | 9-DoF IMU (Accel/Gyro/Mag) | QFN-24 |
| MCP73831 | LiPo Battery Charger (500mA) | SOT-23-5 |
| AP2112K-3.3 | 3.3V LDO Regulator (600mA) | SOT-23-5 |
| SP6214-1.8V | 1.8V LDO for IMU (100mA) | SOT-23 |
| CH340E | USB-to-Serial Converter | MSOP-10 |
| USB Type-C | Power/Data Connector | SMD |
| JST SH 4-pin | Qwiic Connector | SMD |
| JST PH 2-pin | LiPo Battery Connector | SMD |
| Micro-SD Socket | Data Storage (SDIO) | Push-push |
| ML414H | Rechargeable RTC Backup Battery | SMD |
| 32.768kHz Crystal | RTC Oscillator | 3215 |
| RE1C00UNTL | N-ch MOSFET Level Shifter (x5) | SOT-323 |
| Schottky Diode | Power Path Protection (x3) | SOD-323 |

---

## 18. Adafruit Feather M0 WiFi

**Purpose:** WiFi-enabled ARM Cortex-M0+ development board in the Feather form factor. Combines an ATSAMD21 microcontroller with the ATWINC1500 WiFi module for IoT applications. Features LiPo battery charging, 3.3V regulation, and native USB support.

**Repository:** https://github.com/adafruit/Adafruit-Feather-M0-WiFi-WINC1500-PCB

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| ATSAMD21G18 | ARM Cortex-M0+ MCU (48MHz, 256KB Flash) | QFN-48 |
| ATWINC1500-MR210PA | WiFi Module (802.11 b/g/n) | Module |
| AP2112K-3.3 | 3.3V LDO Regulator (600mA) | SOT-23-5 |
| MCP73831T-2ACI/OT | LiPo Battery Charger (500mA) | SOT-23-5 |
| MBR120 | Schottky Diode (Power Path) | SOD-123 |
| 32.768kHz Crystal | RTC Oscillator | 3215 |
| Micro-USB | Power/Data Connector | SMD |
| JST PH 2-pin | LiPo Battery Connector | SMD |
| 1x16 Header | Feather Wing Interface | PTH |
| 1x12 Header | Feather Wing Interface | PTH |
| Red LED | User/Status Indicator | 0805 |
| Orange LED | Charge Status | 0805 |
| Tactile Switch | Reset Button | KMR2 SMD |

---

## 19. Soldered Inkplate 10

**Purpose:** All-in-one e-paper display board with integrated ESP32-WROVER, real-time clock, and battery management. The 9.7" e-ink display is sourced from recycled Kindle screens and provides low-power operation ideal for digital signage and dashboards.

**Repository:** https://github.com/SolderedElectronics/Soldered-Inkplate-10-hardware-design

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| ESP32-WROVER | WiFi/BLE MCU with PSRAM | Module |
| TPS65186RGZR | E-Ink Display Power Supply | VQFN-49 |
| TPS7A2633DRVR | 3.3V LDO Regulator | SOT-553 |
| TPS3840PL27DBVR | Voltage Supervisor | SOT-23-5 |
| CH340C | USB-UART Converter | SOP-16 |
| MCP73831T | LiPo Battery Charger | SOT-23-5 |
| PCF85063A | Real-Time Clock | SO-8 |
| PCAL6416AHF | 16-bit I/O Expander (x2) | TQFN-24 |
| SN74LVC1G34DBV | Single Buffer Gate | SOT-23-5 |
| SSM3J358R | P-Channel MOSFET | SOT-23 |
| LQH44PN4R7MP0L | 4.7uH Power Inductor | 4x4mm |
| 7LC32768F12UC | 32.768kHz Crystal | 3215 |
| U262-161N-4BVC11 | USB Type-C Connector | SMD |
| JST 2-pin | Battery Connector | SMD |

---

## 20. Unexpected Maker ReflowMaster

**Purpose:** Open-source toaster oven reflow controller for SMT soldering. Converts a standard toaster oven into a programmable reflow station with temperature profiling via thermocouple sensor, 2.4" color TFT display, and tactile button interface for profile selection.

**Repository:** https://github.com/UnexpectedMaker/ReflowMaster

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| ATSAMD21G18A | ARM Cortex-M0+ MCU 48MHz | TQFP-48 |
| MAX31855 | Thermocouple-to-Digital Converter | SOIC-8 |
| AP2112K | 3.3V 600mA LDO | SOT-23-5 |
| MMBT2222AL | NPN Transistor 600mA/40V | SOT-23 |
| MBR120 | Schottky Diode 20V | SOD-123 |
| USB-B-MICRO-SMD | USB Micro-B Connector | SMD |
| EVQQ2 (KMR2) | SMT Tactile Switch | SMD |
| ABM3B-32.768KHZ | Crystal Oscillator | 3215 |
| 1206 LED | Status LEDs (Green/Red/Yellow) | 1206 |
| 1x14 Header | TFT Display Connector | PTH |
| 1x02 Header | Power/Control Headers (x5) | PTH |
| 10K Resistor | Pull-up/Pull-down (x4) | 0805 |
| 10uF Capacitor | Bulk Decoupling | 0805 |
| 100nF Capacitor | Decoupling | 0805 |

---

## 21. OLIMEX LoRa868/LoRa915 Module

**Purpose:** Compact, open-source LoRa transceiver module based on the Semtech SX1276 for long-range, low-power wireless communication. Operates on 868 MHz (EU) or 915 MHz (US) ISM bands with up to +14 dBm output power and U.FL connector for external antenna.

**Repository:** https://github.com/OLIMEX/LoRa-868-915

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| SX1276 | Semtech LoRa transceiver IC (137-1020 MHz) | QFN-28 |
| 32.000MHz Crystal | 10ppm crystal oscillator for SX1276 | SMD |
| U.FL Connector | Miniature coaxial RF connector | SMD |
| 15pF Capacitor | Crystal load capacitors (x2) | 0402 |
| 100nF Capacitor | Bypass/decoupling capacitors (x5) | 0402 |
| 22uF Capacitor | Bulk decoupling capacitor | 0603 |
| 10nF Capacitor | RF matching/filter capacitor | 0402 |
| 47pF Capacitor | RF matching capacitor | 0402 |
| 33pF Capacitor | RF matching capacitor | 0402 |
| 33nH Inductor | RF matching inductor | 0402 |
| 6.8nH Inductor | RF matching inductor | 0402 |
| 10nH Inductor | RF matching inductor | 0402 |
| 8-pin Header | SPI interface connector | 2.54mm PTH |

---

## 22. OLIMEX ESP32-C6-EVB

**Purpose:** Evaluation board featuring the ESP32-C6-WROOM-1-N4 module with WiFi 6 (802.11ax), Bluetooth 5 LE, and IEEE 802.15.4 radio for Zigbee and Thread/Matter connectivity. Includes 4 relay outputs, 4 optoisolated inputs, USB-C, and UEXT connector for peripheral expansion.

**Repository:** https://github.com/OLIMEX/ESP32-C6-EVB

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| ESP32-C6-WROOM-1-N4 | ESP32-C6 WiFi 6/BLE/Zigbee/Thread module | Module |
| TX4138 | DC-DC buck converter controller | ESOIC-8 |
| SY8089AAAC | 2A synchronous step-down regulator | SOT-23-5 |
| PC817CS | Optocoupler for isolated inputs (x4) | SMD |
| LMUN2235LT1G | NPN digital transistor with bias resistors | SOT-23 |
| WPM2015-3/TR | P-Channel MOSFET | SOT-23 |
| RAS-0515 | 5V SPDT relay (x4) | THT |
| SMAJ58A | TVS diode for transient protection | SMA |
| 1N4148W | Fast switching diode (x8) | SOD-123 |
| SS310 | 3A Schottky rectifier diode | SMA |
| NRS3015T2R2MNGH | 2.2uH power inductor 1.5A | 3015 |
| PD3316MT330 | 33uH power inductor 2A | DBS135 |
| USB-C-16P-F | USB Type-C receptacle | SMD |
| DG306-5.0-3P | 3-position 5mm terminal block (x4) | THT |

---

## 23. SparkFun Big Easy Driver

**Purpose:** High-power stepper motor driver board designed to drive bi-polar stepper motors at up to 2A per phase. Uses the Allegro A4988 microstepping driver IC with adjustable current control via trimmer potentiometer, ideal for CNC machines, 3D printers, and robotics.

**Repository:** https://github.com/sparkfun/Big_Easy_Driver

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| A4988 | Microstepping bipolar stepper motor driver | QFN-28 |
| LM317L | Adjustable voltage regulator | SOT-89 |
| B340A-13-F | 40V 3A Schottky barrier rectifier | SMA |
| 47uF Electrolytic | Motor power filtering capacitor, 50V | Radial |
| 0.11 ohm Resistor | Current sense resistor, 1/2W 1% (x2) | 2010 |
| 10K Trimmer | Potentiometer for current adjustment | 3mm |
| 20K Resistor | Pull-up/pull-down resistors (x11) | 0603 |
| 8.2K Resistor | Voltage divider resistor | 0603 |
| 1K Resistor | LED current limiting (x3) | 0603 |
| 0.1uF Capacitor | Decoupling capacitors, 100V (x7) | 0603 |
| 0.22uF Capacitor | Ceramic capacitor, 50V | 0603 |
| 1.0uF Capacitor | Ceramic capacitor, 16V | 0603 |
| Yellow LED | Power indicator | 0603 |
| 4-pin Header | Motor output connector | 2.54mm PTH |

---

## 24. Soldered GNSS GPS L86-M33 Breakout

**Purpose:** Compact GNSS receiver breakout featuring the Quectel L86-M33 module with built-in antenna. Supports GPS, GLONASS, and Galileo constellations with EASY and AlwaysLocate technologies for fast positioning. Includes CR1220 battery holder for backup and IPX connector for external antenna.

**Repository:** https://github.com/SolderedElectronics/GNSS-GPS-L86-M33-breakout-hardware-design

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| L86-M33 | Quectel GNSS receiver (GPS/GLONASS/Galileo) | Module |
| SE5218 | 3.3V LDO voltage regulator | SOT-23-5 |
| NMOS-DUAL | Dual N-channel MOSFET for level shifting | SOT-363 |
| NPN Transistor | General purpose NPN | SOT-23 |
| M4 Schottky Diode | Schottky diode (x2) | M4 |
| CR1220 Holder | Coin cell battery holder for backup | THT |
| IPX Connector | Antenna connector for external antenna | SMD |
| 10uF Capacitor | Bulk decoupling | 1206 |
| 2.2uF Capacitor | Decoupling (x2) | 0603 |
| 100nF Capacitor | Bypass capacitor | 0603 |
| 10K Resistor | Pull-up/pull-down (x5) | 0603 |
| 2.2K Resistor | I2C pull-ups (x2) | 0402 |
| Blue LED | Status indicator | 0402 |
| 8-pin Header | Breakout header | 2.54mm PTH |

---

## 25. Adafruit MAX98357 I2S Amp Breakout

**Purpose:** Compact mono Class D digital audio amplifier accepting I2S digital audio input, decoding to analog, and amplifying directly to a speaker. Delivers 3.2W into 4-ohm speaker from 5V supply, combining DAC and amplifier in one package for Raspberry Pi and embedded audio projects.

**Repository:** https://github.com/adafruit/Adafruit-MAX98357-I2S-Amp-Breakout

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| MAX98357A | I2S Class D Mono Amplifier with DAC | QFN-16 |
| 0.1uF Capacitor | Decoupling capacitor | 0805 |
| 10uF Capacitor | Bulk decoupling | 0805 |
| 220pF Capacitor | EMI filter capacitors (x2) | 0805 |
| 1M Resistor | Gain setting resistor | 0805 |
| Ferrite Bead | EMI suppression (x2) | 0805 |
| 2-pos Terminal Block | Speaker output | 5.08mm pitch |
| 1x7 Pin Header | I2S signals + power | 2.54mm PTH |

---

## 26. Soldered INA219 Current Sensor Breakout

**Purpose:** INA219-based breakout enabling bidirectional current, voltage, and power measurement via I2C. Features 0.1 ohm shunt resistor for measurement up to ±3.2A and voltages up to 26V. Includes configurable I2C address jumpers and easyC (Qwiic-compatible) connectors.

**Repository:** https://github.com/SolderedElectronics/Voltage---current-sensor-INA219-breakout-hardware-design

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| INA219 | High-Side Current/Power Monitor IC | SOT23-8 |
| 0.1 ohm Resistor | Precision shunt resistor (1%) | 1210 |
| 10K Resistor | I2C pull-up resistors | 0603 |
| 100nF Capacitor | Decoupling capacitor | 0603 |
| easyC Connector | Qwiic/STEMMA QT compatible (x2) | SMD |
| 2-pin Screw Terminal | Power input/sense | 5.0mm pitch |
| 4-pin Header | I2C breakout | 2.54mm PTH |
| SMD Jumper | I2C address select | 3-pad SMD |

---

## 27. SparkFun Dual TB6612FNG Motor Driver

**Purpose:** Dual H-bridge DC motor driver based on the Toshiba TB6612FNG. Controls up to two DC motors at 1.2A continuous (3.2A peak) with PWM speed control up to 100kHz. Supports four modes per motor: clockwise, counter-clockwise, short-brake, and stop.

**Repository:** https://github.com/sparkfun/Motor_Driver-Dual_TB6612FNG

### Key Components

| Part Number | Description | Package |
|-------------|-------------|---------|
| TB6612FNG | Dual H-Bridge Motor Driver IC | SSOP-24 |
| 0.1uF Capacitor | Ceramic decoupling (x2) | 0402 |
| 10uF Capacitor | Tantalum bypass capacitor | EIA3528 |
| 1x8 Header | Motor/Power connector | 2.54mm PTH |
| 1x8 Header | Control signal connector | 2.54mm PTH |

---

## Component Type Coverage Summary

| Category | Components Covered |
|----------|-------------------|
| **MCUs** | RP2040, STM32L4R5/L433, ATmega32U4, ATSAMD21/51, ESP32-C3/C6/S3/WROOM/WROVER, ESP8266, W65C02, Apollo3 (Artemis) |
| **Power ICs** | BQ24210, TPS62748/62A02/63020/65186/7A26, MAX17225, MCP73831, AP2112/2127/2139, ISL9122A, LM66200, MP2161, LD1117, SP6214, SY8089, TX4138, LM317, SE5218 |
| **Motor Drivers** | A4988 (stepper), TB6612FNG (DC H-bridge) |
| **Audio** | MAX98357A (I2S Class D amplifier) |
| **Current Sensors** | INA219 (I2C power monitor) |
| **GPS/GNSS** | Quectel L86-M33 |
| **Sensors** | BME280, BME680, LSM6DSO, ICM-20948, LIS3DH |
| **Thermocouple** | MAX31855 |
| **Protection** | TVS (SM6T6V8A, SMBJ6.0A, SMAJ58A), ESD (PESD5V0L5UV, ESD5Z3.3, SP3012, ESDLC5V0M5), PTC fuses |
| **Level Shifters** | 74LVC1T45, 74LVC245, 74HCT245, TXS0102 |
| **Logic ICs** | 74HC595, CD4067, PCAL6416A (I/O Expander), SN74LVC1G34 |
| **USB Controllers** | CH340C/E/X, CH334S (Hub), CH217K |
| **RTC** | PCF85063A |
| **Analog Switches** | DGQ2788A |
| **Op-Amps** | LMV321, LMV324, LMV331, LMV358 |
| **MOSFETs** | SI2301 (P-ch), AO3420/IRF8721 (N-ch), MMBT7002K, SSM3J358R, WPM2015 |
| **Transistors** | MMBT2222A (NPN), LMUN2235 (digital) |
| **Optocouplers** | PC817 |
| **Relays** | RAS-0515 (5V SPDT) |
| **Connectors** | USB-C, USB Micro-B, USB-A, HDMI, JST SH/PH, RJ45, u.FL, IPX, DC Barrel Jack, Screw Terminals |
| **LEDs** | WS2812B/SK6812 (addressable), standard 0402/0603/0805/1206/3mm |
| **Passives** | 0201/0402/0603/0805/1206/1210/2010 R/C, inductors, ferrites, trimmers, shunt resistors |
| **Memory** | W25Q32/128 (SPI Flash), MT29F1G01 (NAND), ZD25Q16 |
| **Battery Holders** | CR1220 (coin cell backup) |
| **Ethernet** | LAN8710A PHY, PoE controllers |
| **LoRa** | SX1276 transceiver |
| **Zigbee/Thread** | ESP32-C6 (IEEE 802.15.4) |
| **RF** | GPS LNA, GNSS modules, ceramic antennas, WiFi diplexers, u.FL/IPX connectors, RF matching networks |
| **E-Ink** | TPS65186 display driver |
