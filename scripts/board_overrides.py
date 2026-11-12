"""Board-specific overrides for known source-data errors.

Component value/description fixes, metadata overrides (key_ics, description),
tag replacements, and net pin corrections.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Component overrides: (slug, ref) → {field: new_value}; None drops an attribute.
# ---------------------------------------------------------------------------

BOARD_OVERRIDES: dict[tuple[str, str], dict[str, str | None]] = {
    # The new MPN1 alias exposes stale 100nF / 1.5kohm primary identities.
    # MPN2 + Vendor2 + Seeed Description agree with BOTH placed value and
    # footprint (including C12's 0603), so select that documented source option.
    ("beagleconnect-freedom", "C2"): {'mpn': 'CC0402KRX7R9BB102', 'manufacturer': 'YAGEO', 'description': 'SMD CAP Ceramic 1nF-50V-10%-X7R;0402'},
    ("beagleconnect-freedom", "C6"): {'mpn': 'CC0402MRX5R5BB106', 'manufacturer': 'YAGEO', 'description': 'SMD CAP Ceramic 10uF-6.3V-20%-X5R;0402'},
    ("beagleconnect-freedom", "C10"): {'mpn': 'CC0402MRX5R5BB106', 'manufacturer': 'YAGEO', 'description': 'SMD CAP Ceramic 10uF-6.3V-20%-X5R;0402'},
    ("beagleconnect-freedom", "C11"): {'mpn': 'CC0402MRX5R5BB106', 'manufacturer': 'YAGEO', 'description': 'SMD CAP Ceramic 10uF-6.3V-20%-X5R;0402'},
    ("beagleconnect-freedom", "C12"): {'mpn': 'CC0603KRX5R6BB106', 'manufacturer': 'YAGEO', 'description': 'SMD CAP Ceramic 10uF-10V-10%-X5R;0603'},
    ("beagleconnect-freedom", "C17"): {'mpn': 'CC0402KRX5R6BB105', 'manufacturer': 'YAGEO', 'description': 'SMD CAP Ceramic 1uF-10V-10%-X5R;0402'},
    ("beagleconnect-freedom", "L1"): {'mpn': 'BLM15PD121SN1D', 'manufacturer': 'Murata', 'description': 'SMD Ferrite Bead 120R-1.3A;0402'},
    ("beagleconnect-freedom", "L3"): {'mpn': 'BLM15PD121SN1D', 'manufacturer': 'Murata', 'description': 'SMD Ferrite Bead 120R-1.3A;0402'},
    # Both source options say 2.2pF, against L5's placed 2.0pF. Keep the value
    # and its agreeing primary description, remove unsupported ordering codes.
    ("beagleconnect-freedom", "L5"): {"mpn": None, "prod_id": None},
    # OD501 C25 is placed 10nF; CL05B104KO5NNNC / C1525 identify 100nF.
    ("moco-od501-foc-controller", "C25"): {"mpn": None, "lcsc": None},

    # Wio LR1121 3_03 Power IN & MCU GPIOs: copied library identities disagree
    # with the placed values (6.8pF, 1nF, 100k, 200R, and 3.3nH respectively).
    # Preserve the designer's values; internal PN also identifies the wrong part.
    **{("seeed-wio-lr1121", ref): {"mpn": None, "prod_id": None, "description": None}
       for ref in ("C1", "C2", "C24", "C27", "C41", "C43", "C34",
                   "R2", "R3", "R4", "R8", "R9", "L13")},
    # L1's LQW15AN47NJ00D agrees with 47nH and L0402; its copied 3.3nH/0201
    # description and internal PN belong to L13's library part. L13's PCB also
    # has an L0201 footprint and an empty value, with no cached BOM to resolve it.
    ("seeed-wio-lr1121", "L1"): {"description": None, "prod_id": None},
    # 4_04 PIN OUT: an RF shield is described as an unrelated DIP PoE module.
    ("seeed-wio-lr1121", "SH1"): {"description": None},
    # EEZ consolidated r5B13a.sch: the placed full part numbers disagree with
    # the Panasonic FK technology (even its copied instance attributes). Preserve
    # the placed identity and decoded capacitance; drop unsupported FK ratings.
    # The BOM.ods/.pdf blobs are absent from the offline cache.
    ("eez-h24005", "C3"): {"mpn": "50SVPF18M", "voltage": None, "tolerance": None},
    ("eez-h24005", "C86"): {"mpn": "50SVPF18M", "voltage": None, "tolerance": None},
    ("eez-h24005", "C96"): {"mpn": "50SVPF18M", "voltage": None, "tolerance": None},
    ("eez-h24005", "C13"): {"mpn": "EEEFK1H470P", "voltage": None, "tolerance": None},
    ("eez-h24005", "C89"): {"mpn": "UWT1H220MCL", "voltage": None, "tolerance": None},
    ("eez-h24005", "C94"): {"mpn": "UWT1H220MCL", "voltage": None, "tolerance": None},
    # Value MOC3062 contradicts technology 33 / instance MPN MOC3033S-M.
    # The inherited description cites the MOC3043 datasheet, not the placed part.
    ("eez-h24005", "OK2"): {"mpn": None, "manufacturer": None, "description": None},
    # hackeeg-shield.sch IC5 says 24AA256UID, not technology LC256's 24LC256-I/SN.
    # Keep the source identity without inventing a package/ordering suffix.
    ("hackeeg-ads1299-shield", "IC5"): {"mpn": "24AA256UID"},
    # RX_20x20/v2.0 rx_1280.sch: placed value and deviceset both say 330R;
    # technology VALUE=1K / MPN=RC0805JR-071KL belongs to a different resistor.
    # No v2 BOM is cached; do not borrow the v1/other receivers' ordering codes.
    ("expresslrs-rx-20x20-v2", "R3"): {"mpn": None},
    ("expresslrs-rx-20x20-v2", "R4"): {"mpn": None},
    ("expresslrs-rx-20x20-v2", "R5"): {"mpn": None},
    # SimpleFMCWRadar README.md explicitly calls HMC476 a "MMIC gain block"
    # and HMC431 a "VCO". It supplies no HMC474 or MCP1700 description:
    # remove the reused ERA-2SM+, HMC385 (2.25-2.5GHz), and MCP1703 (16V) text.
    ("simplefmcwradar-gainblock", "IC1"): {"description": "HMC476 MMIC gain block"},
    ("simplefmcwradar-rf-board", "IC3"): {"description": "HMC476 MMIC gain block"},
    ("simplefmcwradar-rf-board", "IC2"): {"description": "HMC431 VCO"},
    ("simplefmcwradar-rf-board", "IC5"): {"description": None},
    ("simplefmcwradar-rf-board", "IC6"): {"description": None},
    # Retain the schematic's complete placed regulator identity after normalization.
    ("simplefmcwradar-rf-board", "IC1"): {
        "value": "MCP1700T-3302E", "mpn": "MCP1700T-3302E", "description": None,
    },
    # LibreSolar_BMS48V.sch and its cached CSV repeat copied instance identities:
    # 0805YC475 (4.7uF) on 1uF/2.2uF; 08055C104/0603B104 (100nF) on
    # 1uF/4.7nF; GRM188R71H104 (100nF) on C47/C48 (placed 4.3pF;
    # the older CSV even says 12.5pF). Keep the placed values, drop their MPNs
    # and manufacturer claims rather than inventing replacement ordering codes.
    **{("bms-15s80-sc", ref): {"mpn": None, "manufacturer": None} for ref in (
        "C1", "C2", "C3", "C10", "C13", "C15", "C17", "C47", "C48", "C50",
    )},
    # MCMR06X1001FTL is shared with the 1k resistors, RC0603FR-0710KL
    # with R17 (10k), ERJ3EKF1002V with R53-R69 (10k), and
    # CR0805-FX-1001ELF encodes 1k, not R68's placed 56k.
    **{("bms-15s80-sc", ref): {"mpn": None, "manufacturer": None} for ref in (
        "R6", "R7", "R11", "R12", "R13", "R15", "R68", "R70", "R71", "R72",
        "R73", "R74", "R77", "R78", "R79", "R80",
    )},
    # D5/D27/D28/D30 are placed 3.3V, not the library's 5.6V BZX384-C5V6.
    **{("bms-15s80-sc", ref): {"mpn": None, "manufacturer": None, "prod_id": None}
       for ref in ("D5", "D27", "D28", "D30")},
    # The named placed semiconductors also disagree with copied instance MPNs.
    ("bms-15s80-sc", "D1"): {"mpn": "NUP2105L", "manufacturer": None},
    ("bms-15s80-sc", "Q4"): {"mpn": "BSS123", "manufacturer": None},
    # Espressif DevKits (PADS layout + BOM): parts on the layout but not in the BOM are the schematic's
    # "(NC)" footprints; their values come from the schematic
    ("espressif-esp32-s3-devkitc-1", "C13"): {"value": "100nF", "description": "Not fitted ((NC) on Espressif's schematic): 0.1uF on GPIO0"},
    ("espressif-esp32-s3-devkitc-1", "C14"): {"value": "100nF", "description": "Not fitted ((NC) on Espressif's schematic): 0.1uF on CHIP_PU"},
    ("espressif-esp32-s3-devkitc-1", "C15"): {"value": "10uF", "description": "Not fitted ((NC) on Espressif's schematic)"},
    ("espressif-esp32-s3-devkitc-1", "R14"): {"value": "10kohm", "description": "Not fitted ((NC) on Espressif's schematic)"},
    ("espressif-esp32-s3-devkitm-1", "C13"): {"value": "100nF", "description": "Not fitted ((NC) on Espressif's schematic): 0.1uF on GPIO0"},
    ("espressif-esp32-s3-devkitm-1", "C14"): {"value": "100nF", "description": "Not fitted ((NC) on Espressif's schematic): 0.1uF on CHIP_PU"},
    ("espressif-esp32-s3-devkitm-1", "C15"): {"value": "10uF", "description": "Not fitted ((NC) on Espressif's schematic)"},
    ("espressif-esp32-s3-devkitm-1", "R14"): {"value": "10kohm", "description": "Not fitted ((NC) on Espressif's schematic)"},
    ("espressif-esp32-s3-devkitm-1", "R6"): {"value": "10kohm", "description": "Not fitted ((NC) on Espressif's schematic)"},
    ("espressif-esp32-devkitc-v4", "C15"): {"value": "100nF", "description": "Not fitted ((NC) on Espressif's schematic): 0.1uF on IO0"},
    ("espressif-esp32-devkitc-v4", "R23"): {"value": "10kohm", "description": "Not fitted ((NC) on Espressif's schematic)"},
    ("espressif-esp32-devkitc-v4", "U3"): {"value": "ESP32-WROVER", "description": "Not fitted ((NC) on Espressif's schematic): alternative ESP32-WROVER footprint under the WROOM module"},
    # The module is D2 on this board; its BOM value is the old "ESP-WROOM-32" name
    ("espressif-esp32-devkitc-v4", "D2"): {"value": "ESP32-WROOM-32D", "mpn": "ESP32-WROOM-32D"},
    ("espressif-esp32-devkitc-v4", "J1"): {"value": "Micro USB", "description": "Micro USB Type B receptacle, 5 pins, through-hole legs"},
    # Adafruit RFM LoRa breakout: shared schematic defaults to RFM69HCW,
    # but the board is sold/documented as RFM95W LoRa
    ("adafruit-rfm95w-lora-breakout", "U1"): {
        "value": "RFM95W",
        "description": "SX1276 LoRa Radio Transceiver",
    },
    # Adafruit ESP32-S3 Feather: Eagle library has S2 MPN on S3 package
    ("adafruit-esp32-s3-feather", "U1"): {
        "mpn": "ESP32-S3-MINI-1",
    },
    # Adafruit QT Py ESP32-S3: same Eagle library, S2 MPN on the ESP32-S3 chip
    ("adafruit-qt-py-esp32-s3", "X2"): {
        "mpn": "ESP32-S3",
    },
    # HackRF One: crystals have value "2x2 header" from shared footprint
    ("hackrf-one", "X1"): {"value": "25MHz"},
    ("hackrf-one", "X2"): {"value": "12MHz"},
    # Adafruit ADS1115 ADC: U1 value/description missing
    ("adafruit-ads1115-adc", "U1"): {
        "value": "ADS1115IDGST",
        "description": "16-bit 4-channel I2C ADC",
        "mpn": None,  # the shared Eagle part's ADS1015IDGST names the 12-bit sibling
    },
    # Adafruit ESP32-C6 Feather: X2 is actually a fuel gauge
    ("adafruit-esp32-c6-feather", "X2"): {
        "value": "MAX17048",
        "description": "LiPo fuel gauge",
    },
    # Adafruit PowerBoost 1000C: U2 needs description
    ("adafruit-powerboost-1000c", "U2"): {
        "description": "USB/solar charger with LiPo power management",
    },
    # ExpressLRS RX: U1 needs description
    ("expresslrs-rx-20x20-v2", "U1"): {
        "description": "2.4GHz LoRa transceiver",
    },
    # iCEBreaker v1.0a: Value=600 and Key=ferrite-0402-600 specify impedance;
    # the source does not specify a test frequency.
    # U6's placed value is the reused ICE5LP4K-SG48 symbol; the fitted FPGA is an iCE40UP5K, so that
    # string is no part number for it
    ("icebreaker", "U6"): {"mpn": None},
    ("icebreaker", "L1"): {"value": "600ohm"},
    ("icebreaker", "L2"): {"value": "600ohm"},
    # SparkFun LSM6DSO: placed Value and technology VALUE both say 30Ω.
    ("sparkfun-lsm6dso", "L1"): {"value": "30ohm"},
    # Blues Notecarrier-A: L1 is 2.2uH
    ("blues-notecarrier-a", "L1"): {"value": "2.2uH"},
    # SparkFun UM980: Value=30Ohm, library=30Ohm_0603_1.8A, Frequency=100MHz.
    ("sparkfun-um980-triband", "L2"): {"value": "30R@100MHz"},
    # SparkFun GPS RTK2: FB1 value "120N" is nanohenries, not nanoohms
    ("sparkfun-gps-rtk2", "FB1"): {"value": "ferrite bead"},
    # Soldered GNSS L86: Q1 is a generic NPN transistor
    ("soldered-gnss-l86-m33", "Q1"): {"value": "NPN transistor"},
    # Darth Vadar FMCW radar: empty IC values
    ("darth-vadar-2-4-ghz-fmcw-radar", "IC1"): {
        "value": "PD2425J5050S2HF", "description": "Wilkinson power divider",
    },
    ("darth-vadar-2-4-ghz-fmcw-radar", "IC2"): {
        "value": "BGS12PN10", "description": "SPDT RF switch",
    },
    ("darth-vadar-2-4-ghz-fmcw-radar", "IC3"): {
        "value": "BGS12PN10", "description": "SPDT RF switch",
    },
    ("darth-vadar-2-4-ghz-fmcw-radar", "U1"): {
        "value": "MAX2750", "description": "2.4GHz ISM-band VCO",
    },
    # SparkFun LSM6DSO: value has zero instead of letter O
    ("sparkfun-lsm6dso", "U1"): {"value": "LSM6DSO"},
    # SparkFun IoT BLDC Motor: ESP32 module name has stutter
    ("sparkfun-iot-bldc-motor", "U3"): {"value": "ESP32-WROOM-32D"},
    # SparkFun Audio Codec WM8960: U4 description has typo
    ("sparkfun-audio-codec-wm8960", "U4"): {
        "description": "Cirrus Logic WM8960 stereo codec with Class D amplifier",
    },
    # NFC Copy Cat: U1 full ordering code
    ("nfc-copy-cat", "U1"): {"value": "AP2112K-3.3"},
    # OpenSiPM TIA: U1 has MPN as footprint, fix value
    ("opensipm-tia-v3", "U1"): {"value": "OPA847"},
    # The source Value fields are MPNs; retain them alongside decoded capacitance.
    ("soldered-mppt-cn3791", "C3"): {"mpn": "VKMD1451H221MV"},
    ("soldered-mppt-cn3791", "C7"): {"mpn": "VKMD1451H221MV"},
    # Power.kicad_sch gives the bead's part number, not its impedance.
    ("internal-usb-hub", "FB1"): {"mpn": "7427934"},
    ("internal-usb-hub", "FB2"): {"mpn": "7427934"},
    ("internal-usb-hub", "FB3"): {"mpn": "7427934"},
}


# ---------------------------------------------------------------------------
# Board metadata overrides: slug → {key_ics: [...], description: "..."}
# ---------------------------------------------------------------------------

BOARD_META_OVERRIDES: dict[str, dict] = {
    "dangerous-prototypes-buspirate-5-rev10a": {
        "key_ics": ["RP2040", "AiP74LVC1T45GC363.TR", "AIP74HC595TA", "SK6812", "LMV321"],
        "description": "RP2040 bus tool: eight level shifters, TFT LCD, SK6812 LEDs, shift-register I/O, programmable PSU and current sense",
    },
    # Espressif's DevKits: the USB-UART bridge and LDO are what agents compare against
    "espressif-esp32-s3-devkitc-1": {"key_ics": ["ESP32-S3-WROOM-1", "CP2102N", "SGM2212"]},
    "espressif-esp32-s3-devkitm-1": {"key_ics": ["ESP32-S3-MINI-1", "CP2102N", "SGM2212"]},
    "espressif-esp32-devkitc-v4": {"key_ics": ["ESP32-WROOM-32D", "CP2102N", "AMS1117"]},
    # Guitar pedals: discrete stages, so the transistors and JFETs are the parts to compare
    "guitarml-classic-boost": {"key_ics": ["2N5088"]},
    "guitarml-ts-rat-combo": {"key_ics": ["TL072", "LM301", "2N5458", "2SC1815"]},
    "1590a-boost-effect": {"key_ics": ["MMBF5103", "DMMT5551"]},
    "1590a-buffered-base": {"key_ics": ["LT3462A", "AP2202", "DMC3071LVT"]},
    "1590a-compressor-effect": {"key_ics": ["LS844", "MMBF5103", "NMB2227A"]},
    "1590a-daisy-seed-base": {"key_ics": ["Daisy Seed", "LS844", "PMV250"]},
    "1590a-fuzz-effect": {"key_ics": ["MMBFJ201", "BAT41Z"]},
    "1590a-octaver-effect": {"key_ics": ["MMBF5103", "DMMT5551"]},
    "adafruit-esp32-s3-feather": {
        "key_ics": ["ESP32-S3-MINI-1", "LC709203F", "MCP73831"],
    },
    "adafruit-powerboost-1000c": {
        "key_ics": ["MCP73871", "TPS61090"],
    },
    "eez-h24005": {
        "key_ics": ["DAC8552", "ADS1120"],
        "description": "DAC8552 setpoint, ADS1120 sense, bench power supply module",
    },
    "adsbee-rf-board": {
        "key_ics": ["BGA2818"],
    },
    "glasgow-interface-explorer": {
        "key_ics": ["CY7C68013A", "ICE40HX8K"],
        "description": "iCE40HX8K FPGA, USB 2.0 FX2LP (CY7C68013A) debug tool",
    },
    "blues-notecarrier-f": {
        "key_ics": ["BQ24210", "TPS63020", "MAX17225", "TPS62748", "TXS0102"],
    },
    "antmicro-cm4-baseboard": {
        "key_ics": ["FT4233H", "PN7160", "MCP23017", "TPS2372", "DS1338"],
    },
    "expresslrs-rx-20x20-v2": {
        "key_ics": ["SX1280", "ESP8285"],
    },
    "t41-qsd2-receiver": {
        "key_ics": ["AD8226", "GALI-39+", "SN74CBT3253"],
    },
    "gshps-gnss-tracker": {
        "key_ics": ["RP2040", "PA1616S", "W25Q128JVS"],
    },
    "antmicro-usb-c-pd-adapter": {
        "key_ics": ["STUSB4500", "SIC477", "AP62301"],
    },
    "usb-armory-mk-ii": {
        "key_ics": ["PF1510", "MCIMX6Y2DVM09AB"],
        "description": "USB armory Mk II LAN: i.MX6ULL SoC, DDR3 SDRAM",
    },
    "sparkfun-um980-triband": {
        "key_ics": ["UM980", "CH340C"],
    },
    "darth-vadar-2-4-ghz-fmcw-radar": {
        "key_ics": ["MAX2750", "MDB-73H+", "GVA-60+", "BGA622"],
    },
    "blueesc": {
        "key_ics": ["ATMEGA168", "ACS711"],
    },
    "twisted-fields-driver-module": {
        "key_ics": ["INA240A1D", "EG3113"],
    },
    "px4-optical-flow": {
        "key_ics": ["STM32F407", "MT9V034", "L3GD20"],
    },
    "bioamp-exg-pill": {
        "key_ics": ["TL074"],
    },
    "adafruit-2-4-tft-featherwing-v2": {
        "key_ics": ["ILI9341", "TSC2007"],
    },
    "blues-notecarrier-b": {
        "key_ics": ["MCP73831", "MAX17225", "TPS62748"],
    },
    "prntrboardv2": {
        "key_ics": ["STM32F407VETx"],
    },
    "sparkfun-iot-bldc-motor": {
        "key_ics": ["ESP32-WROOM-32D", "TMC6300"],
    },
    "sparkfun-lsm6dso": {
        "key_ics": ["LSM6DSO"],
    },
    # Metadata the YAML carried before the current description/key-IC extraction (unchanged
    # registry text, values shipped in 0.8.24). Kept here so re-parsing a board reproduces them
    # instead of replacing curated part numbers with extraction noise ("DShot", "PM2.5").
    "6-ghz-fmcw-radar": {"key_ics": ["MCP4017", "HMC431", "HMC219", "SKY65404"]},
    "absmach-s0": {"key_ics": ["ESP32-C6-MINI-1/U", "SIM7080G", "TXB0108RGY", "RC-S2LP-868", "AMS1117-3.3"]},
    "adumx165-usb-isolator": {"description": "Isolated USB 2.0 High-Speed 480 Mbps (ADUM3165, 3.75kV)"},
    "anavi-thermometer": {"description": "ESP8266, headers for external DHT22/DS18B20 sensors", "key_ics": ["ESP8266"]},
    "aqeye-air-quality-sensor": {"key_ics": ["SGP40"]},
    "asac-fc-rev-b": {"key_ics": ["RP2040", "BMI270"]},
    "atmosfc": {"key_ics": ["STM32G473", "MAX7456", "ICM-42688-P"]},
    "beagleconnect-freedom": {"description": "CC1352P dual-band wireless MCU, MSP430F5503"},
    "bgeigiescint": {"key_ics": ["ESP32-C3_SUPERMINI_TH", "XC6209F332MR-G", "LT3014BHVES5#TRMPBF", "TLV7031DBVR", "TLR341G"]},
    "chameleonmini-revg": {"description": "NFC emulator: contactless smartcard emulation (ISO 14443A/B, ISO 15693)"},
    "corevus-g-v0-6": {"description": "High-performance 3D printer mainboard: STM32F407ZETx, TMC2160/TMC2209 stepper drivers"},
    "dcdc-llc-500w-isolated": {"key_ics": ["RP-1515S", "LM2904BIDDFR", "UCC21520DW", "UCC25600", "ZXRE330ASA-7"]},
    "duet3-6hc-v1-02": {"description": "Professional-grade mainboard: ATSAME70Q20B (Cortex-M7, 300MHz)"},
    "eez-dib-mio168": {"description": "Isolated mixed I/O module (SI8641BB isolator, SN6505B transformer driver)"},
    "ennoid-bms": {"description": "High-voltage modular BMS (48-400V, 500A): STM32F303", "key_ics": ["STM32F303", "LM5165"]},
    "esp32-uwb-dw3000": {"key_ics": ["ESP32-WROVER"]},
    "esphome-indoor-multi-sensor": {"description": "Comprehensive multi-sensor: ESP32-S3-WROOM-2, headers for external radar modules (HLK-LD2410B, HLK-LD2410S, HLK-LD2420, HLK-LD2450, DFRobot SEN0609), BMP581, SHT45, SCD41, SGP41, I2S speaker+mic", "key_ics": ["ESP32-S3-WROOM-2", "BMP581", "SCD41", "SHT45", "SGP41", "ADS1115"]},
    "hadesfcs": {"key_ics": ["STM32H753", "STM32F405", "INA219", "BMI088", "MPRLS0025", "PCA9685"]},
    "healthypi-5": {"key_ics": ["ESP32-C3", "RP2040", "MAX30001", "MAX30205", "MAX17048", "MCP73831", "AFE4400"]},
    "hv-flyback-converter": {"key_ics": ["LT3957AEUHE#PBF"]},
    "irrigation-controller": {"description": "4-zone solenoid valve irrigation controller, STDN-3A24-ADJ 5V buck module"},
    "isousbrs422": {"description": "Galvanic isolation: FT230X USB-UART + ADM2682E isolated RS-422/485, integrated isolated DC-DC power", "key_ics": ["FT230X", "SN74LVC2T45", "ADM2682E"]},
    "led-matrix-input-module": {"description": "Framework Laptop 16 LED matrix module, 297-LED array driven by IS31FL3741A (39×9 PWM, I2C), RP2040 controller"},
    "moco-oi401-foc-controller": {"key_ics": ["STM32G431CBUx", "RT9013-33", "DRV8316CR", "LM4040A50", "AS5047x"]},
    "moco-rd501-foc-controller": {"key_ics": ["STM32G431CBT6", "DRV8301"]},
    "odri-micro-driver-v2": {"description": "Dual BLDC motor driver (51x50mm, 13g)"},
    "olimex-esp32-evb": {"key_ics": ["ESP32-WROOM-32E", "LAN8710A", "SIT1050T", "VS1838B", "CH340X"]},
    "olimex-esp32-s2-devkit-lipo": {"key_ics": ["ESP32-S2", "BL4054B"]},
    "olimex-lora-stm32wl": {"description": "STM32L052K8U3 MCU, magnetometer (IIS2MDCTR), BME280/AHT20 sensors", "key_ics": ["STM32L052K8U3", "IIS2MDCTR"]},
    "olimex-mipi-hdmi": {"key_ics": ["ME2188C50M5G", "LT8912B", "RCLAMP0524P"]},
    "opensipm-bias-control": {"key_ics": ["ATSAMD21E18A-AF", "LT8361EMSE/LT8362EMSE", "MCP47FEB22A2-E_ST", "MIC5317-3.3", "RT9072B"]},
    "px4-fmuv2-pixhawk": {"description": "STM32F427 + STM32F103 I/O co-proc, triple-redundant IMU (MPU6000, LSM303D, L3GD20H), MS5611 baro, industry-standard autopilot"},
    "rpi-cm4-io-board": {"description": "CM4 reference design: dual HDMI 2.0, PCIe Gen 2 x1, Gigabit Ethernet + PoE", "source": "rpi-cm4io", "org": "raspberrypi", "key_ics": ["TPD4EUSB30", "EMC2301", "RT9742"]},
    "rpi-cm5-io-board-rev2": {"description": "CM5 reference design: dual HDMI 2.1, M.2 PCIe Gen 3 x4, USB 3.0, USB-C PD input", "source": "rpi-cm5io", "org": "raspberrypi", "key_ics": ["TPD4EUSB30", "RT9742"]},
    "s3xy-bms-tesla-retrofit": {"key_ics": ["RP2354B", "INA228"]},
    "soldered-bq27441-fuel-gauge": {"description": "Coulomb-counting fuel gauge (BQ27441DRZR)"},
    "weather-station": {"description": "LoRaWAN weather station: humidity (HIH6020), temperature (TMP36), light (BH1750)"},
    # ZIP boards: identity as published since they were added, consistent with the other Seeed
    # and Raspberry Pi boards (the registry's org text alone gives "seeed" and "raspberry-pi").
    "seeed-xiao-esp32-s3-sense": {"source": "seeed-xiao-esp32s3", "org": "Seeed-Studio", "org_display": "Seeed Studio"},
    # Boards whose registry text names no IC the extractor recognizes: without these the parts-list
    # fallback lists LDOs and diodes (CH32V203 Pro Micro) or nothing (ANAVI, ZED-F9R).
    "anavi-fume-extractor": {"key_ics": ["ESP8266"]},
    "anavi-light-controller": {"key_ics": ["ESP8266"]},
    "ch32v203-pro-micro": {"key_ics": ["CH32V203C8T6"]},
    "sparkfun-gps-rtk-dead-reckoning-zed-f9r": {"key_ics": ["ZED-F9R"]},
    # Its key coverage names the support parts too (MCP6004, AP7361C, MCP2562); the FOC chip and MCU are key
    "heev-motor-controller-2018": {"key_ics": ["TMC4671", "STM32F303"]},
}


# ---------------------------------------------------------------------------
# Tag overrides: slug → [tags] (REPLACEMENT, not additive)
# ---------------------------------------------------------------------------

TAG_OVERRIDES: dict[str, list[str]] = {
    # 2SP0115T2A IGBT gate-drive interfaces for a 650V VESC traction inverter, not a drone ESC.
    "axiom-motor-controller": ["inverter", "motor-control"],
    # TMC4671 FOC logic board: the IRFP3306 phase bridge is a separate design (MotorControllerPowerBoardRev2)
    # reached through J111 "Trinamic-Bridge"; this board has no gate drivers or FETs, so no inverter tag.
    "heev-motor-controller-2018": ["can-bus", "motor-control", "power-supply", "signal-conditioning"],
    # POWER_REF uses a ferrite bead and common ground, not a galvanic isolation barrier.
    "daq-4ch-16-bit-100ksps": ["adc-dac"],
    # Automotive-qualified ISO7741 parts on a general lab power-electronics control board.
    "lea-control-board": ["isolation", "power-supply"],
    # HD3SS3220 handles Type-C CC/orientation and current advertisement, not USB PD.
    "mte-usb-hub": ["usb"],
    # The reference IO boards expose USB ports even though coverage doesn't call them hubs.
    "rpi-cm4-io-board": ["ethernet", "rtc", "usb", "video"],
    "rpi-cm5-io-board-rev2": ["ethernet", "usb", "usb-pd", "video"],
    # KP254 pressure sensor U4 is present but not named in Key Coverage.
    "weather-station": ["lora", "pressure-sensor", "sensors"],
    # A guitar "boost" is a gain stage, not a boost converter
    "guitarml-classic-boost": ["audio"],
    "1590a-boost-effect": ["audio"],
    "darth-vadar-2-4-ghz-fmcw-radar": ["rf-sdr", "radar-fmcw"],
    "adf4158-10-ghz-fmcw-lo": ["rf-sdr", "radar-fmcw"],
    "simplefmcwradar-rf-board": ["rf-sdr", "radar-fmcw"],
    # Its VCO is an RF radar oscillator, not a Eurorack synth voice.
    "6-ghz-fmcw-radar": ["radar-fmcw", "rf-sdr", "signal-conditioning"],
    "simplefmcwradar-gainblock": ["rf-sdr"],
    "silentstepstick-tmc2209": ["stepper-driver", "motor-control"],
    "ehm-energy-harvester": ["energy-harvesting", "adc-dac"],
    "eez-h24005": ["power-supply", "adc-dac"],
    "adsbee-rf-board": ["rf-sdr"],
    "soldered-tca9548a-i2c-mux": ["i2c-mux"],
    "usb-armory-mk-ii": ["security", "embedded"],
    "rp2040-radar-presence": ["radar-presence", "microcontroller"],
    "blueesc": ["motor-control", "underwater"],
    "bioamp-exg-pill": ["biomedical", "analog"],
    "opensipm-tia-v3": ["photonics", "analog"],
    # Iridium satellite tracker: its "global coverage beyond cellular" isn't a cellular modem
    "artemis-global-tracker": ["gps-gnss"],
}


# ---------------------------------------------------------------------------
# Net pin fixes: (slug, bad_pin) → correct_pin
# ---------------------------------------------------------------------------

NET_PIN_FIXES: dict[tuple[str, str], str] = {
    # Eagle names the two ground pins AGND@2 and (misspelled) ANGD@1
    ("adafruit-max31865-rtd", "U1.ANGD@1"): "U1.AGND@1",
}


# Unlabelled importer fields have different meanings in different boards (even
# different symbols). Rename only schemas verified in the cached source survey;
# an explicit, named property still wins. "*" applies to all refs in that board.
BOARD_PROPERTY_ALIASES = {
    'crazyflie': {'*': {'Field4': 'Manufacturer', 'Field5': 'PART_OR_SPECS'}},
    's3xy-bms-tesla-retrofit': {'*': {'Field5': 'Description', 'Field6': 'Rating'}},
    'ubertooth-one': {'*': {'Field1': 'Manufacturer', 'Field2': 'MPN', 'Field3': 'Description'}},
    'anavi-miracle-controller': {'L1': {'Field4': 'Description', 'Field7': 'Manufacturer', 'Field8': 'MPN'}},
    'corevus-g-v0-6': {'*': {'Field4': 'LCSC'}},
    'esp32-f9p-io-board': {'*': {'Field4': 'Manufacturer'}},
    'pipad-cm4-logic-board': {'*': {'Field4': 'Supplier', 'Field5': 'Supplier Part', 'Field6': 'MPN', 'Field7': 'Manufacturer'}},
    'covg-daq-v2': {'*': {'Field4': 'PROD_ID'}},
    'ldo-leviathan-v1-3': {'*': {'Field4': 'LCSC', 'Field5': 'MPN'}},
    'nfc-copy-cat': {'*': {'Campo4': 'Manufacturer', 'Campo8': 'Description'}},
    'mystat-potentiostat': {'J2': {'Field4': 'Description', 'Field8': 'MPN', 'Field12': 'DigiKey', 'Field14': 'Manufacturer'}},
    'cheap-focer-2': {'U6': {'Field4': 'Manufacturer', 'Field8': 'MPN'}},
    'prusa-buddy-board-mini': {'U2': {'Pole6': 'MPN', 'Pole8': 'Manufacturer'}},
    'hadesfcs': {
        'U1': {'Field4': 'Description', 'Field5': 'Manufacturer', 'Field8': 'MPN'},
        'BAT1': {'Field5': 'MPN', 'Field7': 'Manufacturer'},
        'U5': {'Field6': 'Manufacturer', 'Field7': 'Description'},
        'U7': {'Field5': 'Description', 'Field7': 'Manufacturer'},
        'U10': {'Field5': 'Description', 'Field7': 'MPN'},
        'ANT1': {'Field4': 'Manufacturer', 'Field5': 'Description', 'Field6': 'MPN'},
    },
    **{slug: {'*': {'Field4': 'Supplier', 'Field5': 'Supplier Part',
                    'Field6': 'MPN', 'Field7': 'Manufacturer', 'Field8': 'PROD_ID'}}
       for slug in ('rpi-cm4-io-board', 'rpi-cm5-io-board-rev2', 'cm5-minima-rev2')},
}


# Run 7: placed values versus copied ordering identities and passive ratings.
# Evidence: cached schematic/PCB properties and maker coding schemes; no inferred
# substitutions. Source-supported options remain untouched.
BOARD_OVERRIDES.update({
    # 0104-usb-hub: Cached 0104-USB-HUB_BOM.csv labels PartNumber as the JLC supplier code and
    # Comment as the actual identity; schematic and PCB agree. Move C-number to lcsc and retain the
    # documented placed MPN.
    **{('0104-usb-hub', ref): {'lcsc': 'C136167', 'mpn': 'LESD5Z5.0CT1G'} for ref in (
        'D1', 'D10', 'D11', 'D12', 'D13', 'D14', 'D15', 'D2', 'D3', 'D7', 'D8', 'D9',
    )},
    # 0104-usb-hub: Cached 0104-USB-HUB_BOM.csv labels PartNumber as the JLC supplier code and
    # Comment as the actual identity; schematic and PCB agree. Move C-number to lcsc and retain the
    # documented placed MPN.
    ('0104-usb-hub', 'U1'): {'lcsc': 'C192893', 'mpn': 'SL2.1A'},
    # aqeye-air-quality-sensor: Schematic and PCB both give LM66100DCKR, SC-70-6; same-symbol
    # datasheet is lm66100.pdf and Description specifies the single-channel part. Replace copied
    # LM66200DRLR.
    ('aqeye-air-quality-sensor', 'U3'): {'mpn': 'LM66100DCKR'},
    # atmosfc: Keep the placed schematic value; the cached source has a conflicting ordering
    # identity and no documented substitution resolving it. Drop linked ordering fields.
    **{('atmosfc', ref): {'manufacturer': None, 'mpn': None} for ref in (
        'R11', 'R12', 'R17', 'R2', 'R20', 'R21', 'R27', 'R28', 'R29', 'R3', 'R30', 'R31', 'R32',
        'R33', 'R34', 'R35', 'R36', 'R37', 'R38', 'R8', 'R9',
    )},
    # axiom-motor-controller: Keep the placed schematic value; the cached source has a conflicting
    # ordering identity and no documented substitution resolving it. Drop linked ordering fields.
    **{('axiom-motor-controller', ref): {'digikey': None, 'manufacturer': None, 'mpn': None} for ref in (
        'C44', 'R50', 'R51', 'R55', 'R57',
    )},
    # beagleconnect-freedom: Keep the placed value; drop the copied description that specifies
    # another value. Both MPN1/MPN2 identify other values. PCB has an older value on some refs;
    # retain the current schematic value.
    **{('beagleconnect-freedom', ref): {'description': None, 'manufacturer': None, 'mpn': None, 'prod_id': None} for ref in (
        'C3', 'C4',
    )},
    # beagleconnect-freedom: MPN1/MPN2 CC0201CRNPO9BNR50 and Seeed Description agree with 0.5pF;
    # replace stale primary 1pF description with that same-symbol description.
    ('beagleconnect-freedom', 'C31'): {'description': 'SMD CAP Ceramic;0.5pF-50V-0.25pF-NPO;0201'},
    # beagleconnect-freedom: Keep the placed value; drop the copied description that specifies
    # another value. Both MPN1/MPN2 identify other values. PCB has an older value on some refs;
    # retain the current schematic value. Source Value and PCB both say 0R: this is a zero-ohm link
    # on a capacitor reference, not 0F.
    ('beagleconnect-freedom', 'C34'): {'description': None, 'manufacturer': None, 'mpn': None, 'prod_id': None, 'value': '0ohm'},
    # beagleconnect-freedom: Same-symbol MPN2 and PCB match the placed PMEG6020ER,115. Both copied
    # descriptions/vendor2 ST describe other parts; retain existing Nexperia manufacturer, drop
    # copied description/internal PN.
    ('beagleconnect-freedom', 'D9'): {'description': None, 'mpn': 'PMEG6020ER,115', 'prod_id': None},
    # beagleconnect-freedom: Keep the placed value; drop the copied description that specifies
    # another value. Both MPN1/MPN2 identify other values. PCB has an older value on some refs;
    # retain the current schematic value.
    **{('beagleconnect-freedom', ref): {'description': None, 'mpn': None, 'prod_id': None} for ref in (
        'R10', 'R15',
    )},
    # beagleconnect-freedom: Same-symbol MPN2/Vendor2/Seeed Description agree with placed 1.2k and
    # 0402; select the documented option.
    ('beagleconnect-freedom', 'R31'): {'description': 'SMD RES 1.2K-1%-1/16W;0402', 'manufacturer': 'YAGEO', 'mpn': 'RC0402FR-071K2L'},
    # beagleconnect-freedom: Keep the placed schematic value; the cached source has a conflicting
    # ordering identity and no documented substitution resolving it. Drop linked ordering fields.
    # Both MPN1/MPN2 identify other values. PCB has an older value on some refs; retain the current
    # schematic value.
    **{('beagleconnect-freedom', ref): {'description': None, 'manufacturer': None, 'mpn': None, 'prod_id': None} for ref in (
        'R56', 'R57', 'R60', 'R61',
    )},
    # beagleconnect-freedom: Same-symbol MPN2 and Link1 both explicitly give TPS62821DLCR; footprint
    # and primary 1A buck description match. Replace resistor MPN1.
    ('beagleconnect-freedom', 'U3'): {'mpn': 'TPS62821DLCR'},
    # beagleconnect-freedom: Same-symbol MPN2/Vendor2/Seeed Description and PCB agree with placed
    # 16Mbit GD25Q16CEIGR; replace the 8Mbit Macronix ordering fields.
    ('beagleconnect-freedom', 'U6'): {'description': 'SMD IC NOR Flash;16Mbit-SPI;USON-8;2*3mm', 'manufacturer': 'Gigadevice', 'mpn': 'GD25Q16CEIGR'},
    # bgeigiescint: Keep the placed schematic value; the cached source has a conflicting ordering
    # identity and no documented substitution resolving it. Drop linked ordering fields.
    ('bgeigiescint', 'R14'): {'lcsc': None, 'manufacturer': None, 'mpn': None},
    # bms-15s80-sc: Keep the placed schematic value; the cached source has a conflicting ordering
    # identity and no documented substitution resolving it. Drop linked ordering fields.
    ('bms-15s80-sc', 'U6'): {'manufacturer': None, 'mpn': None},
    # catsniffer: Keep the placed schematic value; the cached source has a conflicting ordering
    # identity and no documented substitution resolving it. Drop linked ordering fields.
    ('catsniffer', 'U1'): {'mouser': None, 'mpn': None},
    # chrono-vfd-driver: Keep the placed schematic value; the cached source has a conflicting
    # ordering identity and no documented substitution resolving it. Drop linked ordering fields.
    **{('chrono-vfd-driver', ref): {'digikey': None, 'manufacturer': None, 'mpn': None} for ref in (
        'C5', 'C6', 'R1', 'R14',
    )},
    # cm5-minima-rev2: Keep the placed schematic value; the cached source has a conflicting ordering
    # identity and no documented substitution resolving it. Drop linked ordering fields.
    ('cm5-minima-rev2', 'R707'): {'manufacturer': None, 'mpn': None, 'prod_id': None},
    # covg-daq-v2: Keep the placed schematic value; the cached source has a conflicting ordering
    # identity and no documented substitution resolving it. Drop linked ordering fields.
    ('covg-daq-v2', 'R284'): {'mpn': None},
    # dcdc-llc-500w-isolated: Same-symbol placed Value=2uF and matching MKP1848520704K2 footprint
    # identify the lost micro prefix in Description; correct 2F to 2uF.
    ('dcdc-llc-500w-isolated', 'C1'): {'description': '2uF Film Capacitor 700V Polypropylene (PP), Metallized Radial'},
    # duet3-6hc-v1-02: The maker MPN coding scheme resolves the rating for the same nominal value;
    # preserve the placed value and use the decoded rating.
    **{('duet3-6hc-v1-02', ref): {'voltage': '6.3V'} for ref in (
        'C169', 'C184', 'C200', 'C51', 'C55', 'C63', 'C65',
    )},
    # duet3-6hc-v1-02: The maker MPN coding scheme resolves the rating for the same nominal value;
    # preserve the placed value and use the decoded rating.
    **{('duet3-6hc-v1-02', ref): {'voltage': '16V'} for ref in (
        'C191', 'C194',
    )},
    # ennoid-bms: The maker MPN coding scheme resolves the rating for the same nominal value;
    # preserve the placed value and use the decoded rating.
    ('ennoid-bms', 'C91'): {'voltage': '50V'},
    # ennoid-bms: Keep the placed schematic value; the cached source has a conflicting ordering
    # identity and no documented substitution resolving it. Drop linked ordering fields.
    **{('ennoid-bms', ref): {'mpn': None} for ref in (
        'D14', 'D15', 'D17', 'D18', 'R166', 'R167', 'R42', 'R46', 'R50',
    )},
    # faultycat: Keep the placed schematic value; the cached source has a conflicting ordering
    # identity and no documented substitution resolving it. Drop linked ordering fields.
    **{('faultycat', ref): {'lcsc': None, 'mpn': None} for ref in (
        'D1', 'D10', 'D2', 'D3', 'D4', 'U1',
    )},
    # greatfet-azalea: Keep the placed schematic value; the cached source has a conflicting ordering
    # identity and no documented substitution resolving it. Drop linked ordering fields.
    ('greatfet-azalea', 'U2'): {'manufacturer': None, 'mpn': None},
    # hackrf-one: Keep the placed value; drop the copied description that specifies another value.
    **{('hackrf-one', ref): {'description': None, 'manufacturer': None, 'mpn': None} for ref in (
        'R25', 'R26',
    )},
    # hubbish: Keep the placed schematic value; the cached source has a conflicting ordering
    # identity and no documented substitution resolving it. Drop linked ordering fields.
    **{('hubbish', ref): {'lcsc': None, 'mpn': None} for ref in (
        'U10', 'U11', 'U12', 'U13', 'U14', 'U15', 'U16', 'U17', 'U2', 'U4', 'U5', 'U6', 'U7',
        'U8', 'U9',
    )},
    # ldo-leviathan-v1-3: Keep the placed schematic value; the cached source has a conflicting
    # ordering identity and no documented substitution resolving it. Drop linked ordering fields.
    **{('ldo-leviathan-v1-3', ref): {'lcsc': None, 'mpn': None} for ref in (
        'R22', 'R23', 'R26', 'R27',
    )},
    # libresolar-mppt-2420-lc: Keep the placed schematic value; the cached source has a conflicting
    # ordering identity and no documented substitution resolving it. Drop linked ordering fields.
    ('libresolar-mppt-2420-lc', 'U6'): {'manufacturer': None, 'mpn': None},
    # lora-gateway-cubesat-payload: Keep the placed schematic value; the cached source has a
    # conflicting ordering identity and no documented substitution resolving it. Drop linked
    # ordering fields.
    **{('lora-gateway-cubesat-payload', ref): {'mpn': None} for ref in (
        'R401', 'R402', 'R403', 'R407', 'R408', 'R409',
    )},
    # moco-od501-foc-controller: Keep the placed schematic value; the cached source has a
    # conflicting ordering identity and no documented substitution resolving it. Drop linked
    # ordering fields.
    **{('moco-od501-foc-controller', ref): {'lcsc': None, 'mpn': None} for ref in (
        'R4', 'R5', 'R6',
    )},
    # moco-oi401-foc-controller: The maker MPN coding scheme resolves the rating for the same
    # nominal value; preserve the placed value and use the decoded rating.
    **{('moco-oi401-foc-controller', ref): {'voltage': '50V'} for ref in (
        'C14', 'C15', 'C18',
    )},
    # moco-oi401-foc-controller: The maker MPN coding scheme resolves the rating for the same
    # nominal value; preserve the placed value and use the decoded rating.
    ('moco-oi401-foc-controller', 'C19'): {'voltage': '25V'},
    # moco-oi401-foc-controller: Keep the placed schematic value; the cached source has a
    # conflicting ordering identity and no documented substitution resolving it. Drop linked
    # ordering fields.
    **{('moco-oi401-foc-controller', ref): {'lcsc': None, 'mpn': None} for ref in (
        'R1', 'R3',
    )},
    # openmd-gan-motor-driver: Keep the placed schematic value; the cached source has a conflicting
    # ordering identity and no documented substitution resolving it. Drop linked ordering fields.
    ('openmd-gan-motor-driver', 'L1'): {'mpn': None},
    # openmd-gan-motor-driver: Keep the placed schematic value; the cached source has a conflicting
    # ordering identity and no documented substitution resolving it. Drop linked ordering fields.
    # The copied description/rating is not independently established for the placed device.
    ('openmd-gan-motor-driver', 'Q3'): {'description': None, 'mpn': None},
    # openmd-gan-motor-driver: Keep the placed schematic value; the cached source has a conflicting
    # ordering identity and no documented substitution resolving it. Drop linked ordering fields.
    # The copied description/rating is not independently established for the placed device.
    ('openmd-gan-motor-driver', 'U2'): {'mpn': None, 'voltage': None},
    # opensipm-bias-control: Keep the placed schematic value; the cached source has a conflicting
    # ordering identity and no documented substitution resolving it. Drop linked ordering fields.
    # The 4A/60V description belongs to LT8364, not either placed LT8361/LT8362 option.
    ('opensipm-bias-control', 'IC1'): {'description': None, 'manufacturer': None, 'mouser': None, 'mpn': None},
    # prusa-buddy-board-mini: Keep the placed schematic value; the cached source has a conflicting
    # ordering identity and no documented substitution resolving it. Drop linked ordering fields.
    ('prusa-buddy-board-mini', 'U2'): {'manufacturer': None, 'mpn': None},
    # rpi-cm4-io-board: Keep the placed schematic value; the cached source has a conflicting
    # ordering identity and no documented substitution resolving it. Drop linked ordering fields.
    **{('rpi-cm4-io-board', ref): {'manufacturer': None, 'mpn': None, 'prod_id': None} for ref in (
        'U1', 'U2', 'U4',
    )},
    # rpi-cm5-io-board-rev2: Keep the placed schematic value; the cached source has a conflicting
    # ordering identity and no documented substitution resolving it. Drop linked ordering fields.
    **{('rpi-cm5-io-board-rev2', ref): {'manufacturer': None, 'mpn': None, 'prod_id': None} for ref in (
        'U1', 'U2',
    )},
    # s3xy-bms-tesla-retrofit: Keep the placed value; drop the copied description that specifies
    # another value.
    ('s3xy-bms-tesla-retrofit', 'C42'): {'description': None},
    # seeed-recamera-s4-gc2053: The maker MPN coding scheme resolves the rating for the same nominal
    # value; preserve the placed value and use the decoded rating.
    **{('seeed-recamera-s4-gc2053', ref): {'tolerance': '5%'} for ref in (
        'R11', 'R6',
    )},
    # twisted-fields-rp2040-base: Keep the placed schematic value; the cached source has a
    # conflicting ordering identity and no documented substitution resolving it. Drop linked
    # ordering fields.
    **{('twisted-fields-rp2040-base', ref): {'digikey': None, 'lcsc': None, 'mpn': None} for ref in (
        'U23', 'U25', 'U6',
    )},
    # uberamp1-8-channel-dsp-amp: The maker MPN coding scheme resolves the rating for the same
    # nominal value; preserve the placed value and use the decoded rating.
    **{('uberamp1-8-channel-dsp-amp', ref): {'voltage': '50V'} for ref in (
        'C111', 'C112',
    )},
    # uberamp1-8-channel-dsp-amp: The maker MPN coding scheme resolves the rating for the same
    # nominal value; preserve the placed value and use the decoded rating.
    **{('uberamp1-8-channel-dsp-amp', ref): {'voltage': '63V'} for ref in (
        'C127', 'C128', 'C132', 'C162', 'C23', 'C24', 'C25', 'C26',
    )},
    # uberamp1-8-channel-dsp-amp: The maker MPN coding scheme resolves the rating for the same
    # nominal value; preserve the placed value and use the decoded rating.
    **{('uberamp1-8-channel-dsp-amp', ref): {'voltage': '200V'} for ref in (
        'C31', 'C32', 'C33', 'C34',
    )},
    # uberamp1-8-channel-dsp-amp: Keep the placed schematic value; the cached source has a
    # conflicting ordering identity and no documented substitution resolving it. Drop linked
    # ordering fields.
    **{('uberamp1-8-channel-dsp-amp', ref): {'mpn': None} for ref in (
        'R165', 'R166', 'R167', 'R168', 'R53', 'R55', 'R58', 'R59', 'U13', 'U16', 'U20', 'U26',
    )},
    # ulx3s: Keep the placed schematic value; the cached source has a conflicting ordering identity
    # and no documented substitution resolving it. Drop linked ordering fields.
    ('ulx3s', 'C56'): {'digikey': None, 'lcsc': None, 'mouser': None, 'mpn': None},
    # usb-armory-mk-ii: The maker MPN coding scheme resolves the rating for the same nominal value;
    # preserve the placed value and use the decoded rating.
    ('usb-armory-mk-ii', 'C6'): {'description': None, 'tolerance': '20%', 'voltage': '10V'},
    # usb-armory-mk-ii: The maker MPN coding scheme resolves the rating for the same nominal value;
    # preserve the placed value and use the decoded rating.
    **{('usb-armory-mk-ii', ref): {'tolerance': '5%'} for ref in (
        'R1', 'R10', 'R11', 'R12', 'R13', 'R14', 'R15', 'R16', 'R17', 'R18', 'R2', 'R22', 'R26',
        'R27', 'R28', 'R29', 'R3', 'R31', 'R32', 'R33', 'R4', 'R47', 'R48', 'R50', 'R57', 'R6',
        'R7', 'R8', 'R9',
    )},
    # yardstick-one: the Value field is stale. Upstream commit 25badce93e (2022-08-11, "YS1
    # Hardware: Update value of new decoupling caps") changed these caps' Part Number from
    # CL05C101JB5NNNC (100 pF) to CL05C470JB5NNNC and the Description to 47 pF without updating
    # Value; C33-C35 from the same change already read 47pF.
    **{('yardstick-one', ref): {
        'value': '47pF', 'mpn': 'CL05C470JB5NNNC', 'manufacturer': 'Samsung Electro-Mechanics',
        'description': 'CAP CER 47PF 50V C0G/NP0 0402',
    } for ref in ('C27', 'C28', 'C32')},
    # prntrboardv2: Preserve placed 100nF/50V and the independently supplied LCSC code; drop
    # malformed concatenated MPN.
    ('prntrboardv2', 'C24'): {'mpn': None},
})

# Run 7: description ratings independently checked against the same-value MPN.
BOARD_OVERRIDES.update({
    # beagleconnect-freedom: retain nominal value/MPN, drop copied voltage/tolerance/dielectric text.
    **{('beagleconnect-freedom', ref): {"description": None} for ref in ('C28', 'C36', 'C46', 'C55')},
    # blues-notecarrier-f: retain nominal value/MPN, drop copied voltage/tolerance/dielectric text.
    **{('blues-notecarrier-f', ref): {"description": None} for ref in ('C1', 'C16', 'C17', 'C2', 'C20', 'C21', 'C22', 'C23', 'C24', 'C27', 'C29')},
    # rpi-cm4-io-board: retain nominal value/MPN, drop copied voltage/tolerance/dielectric text.
    **{('rpi-cm4-io-board', ref): {"description": None} for ref in ('C60', 'C64')},
    # seeed-wio-lr1121: retain nominal value/MPN, drop copied voltage/tolerance/dielectric text.
    **{('seeed-wio-lr1121', ref): {"description": None} for ref in ('C25', 'C26')},
})

# Run 9: final-audit source review. Full evidence and queue decisions are in
# .codex-dobby/scratch/run9/; all inputs are cached sources/components.db.
BOARD_OVERRIDES.update({
    # tigard: tigard.sch F4 P/N=93LC56BT-I/OT and F5 LCSC=C190271; components.db C190271
    # independently identifies Microchip 93LC56BT-I/OT. F1 Value is stale.
    ('tigard', 'U4'): {'value': '93LC56BT-I/OT'},
    # lea-control-board: Debugger.kicad_sch Description=Ferrite Bead, 0603, 600Ohm, 300mA and
    # manf#=FCB-0603-601A agree with library Ferrite_0603_600R_300mA; replace package-only Value.
    **{('lea-control-board', ref): {'value': '600ohm'} for ref in (
        'L201', 'L202',
    )},
    # powerfeather-powerups: bq25622e.kicad_sch placed Value, library and Description all specify
    # BQ25622E; MPN=595-BQ25622RYKR names BQ25622 without E. No corroborating source option:
    # preserve placed identity, drop conflicting ordering code.
    ('powerfeather-powerups', 'U6'): {'mpn': None},
    # eurorack-pmod: vref.kicad_sch mfg# and dig# both specify LM4040BIM3-3.0/NOPB; lcsc#=C139380
    # independently confirms it in components.db. Replace inherited LM4040DBZ-3 VREF label.
    ('eurorack-pmod', 'U8'): {'value': 'LM4040BIM3-3.0/NOPB'},
    # rpi-cm4-io-board: Cached schematic Footprint=CM4IO:TRJG0926HENL and ordering
    # Field6=TRJG0926HENL independently agree. MagJack-A70-112-331N126 is the stale library/Value
    # identity, not a generic Ethernet connector label.
    ('rpi-cm4-io-board', 'U3'): {'value': 'TRJG0926HENL'},
    # rpi-cm5-io-board-rev2: Cached schematic Footprint=CM4IO:TRJG0926HENL and ordering
    # Field6=TRJG0926HENL independently agree. MagJack-A70-112-331N126 is the stale library/Value
    # identity, not a generic Ethernet connector label.
    ('rpi-cm5-io-board-rev2', 'U3'): {'value': 'TRJG0926HENL'},
    # esp32-uwb-dw3000: Eagle deviceset AP2112 text on placed ME6217C33M5G is a different regulator
    # identity.
    ('esp32-uwb-dw3000', 'U2'): {'description': None},
    # eez-h24005: Eagle VARISTOR deviceset names EPCOS B72220S0251K101 and 250VAC; placed
    # ERZE14A431/ERZE11A431 are Panasonic identities.
    **{('eez-h24005', ref): {'description': None} for ref in (
        'VAR1', 'VAR2', 'VAR3', 'VAR4',
    )},
    # eez-h24005: P6SMB68A library DO-214AA text is copied onto SMAJ51A and an unfitted option; do
    # not publish a competing package claim.
    **{('eez-h24005', ref): {'description': None} for ref in (
        'ZD1', 'ZD15',
    )},
    # eez-h24005: PSMAXX library text specifies P4SMA, not the placed SMAJ18A ordering family.
    **{('eez-h24005', ref): {'description': None} for ref in (
        'ZD11', 'ZD12', 'ZD14', 'ZD6', 'ZD8', 'ZD9',
    )},
    # healthypi-5: Eagle deviceset description lists multiple switch packages (6x6mm, KMR2
    # 4.6x2.8mm, EVQ 4.5x4.5mm); flattening/truncation makes the menu look like one part
    # specification.
    **{('healthypi-5', ref): {'description': None} for ref in (
        'SW1', 'SW2', 'SW4', 'SW5',
    )},
    # adafruit-esp32-s3-feather: Eagle deviceset description lists multiple switch packages (6x6mm,
    # KMR2 4.6x2.8mm, EVQ 4.5x4.5mm); flattening/truncation makes the menu look like one part
    # specification.
    **{('adafruit-esp32-s3-feather', ref): {'description': None} for ref in (
        'SW1', 'SW2',
    )},
    # adafruit-qt-py-esp32-s3: Eagle deviceset description lists multiple switch packages (6x6mm,
    # KMR2 4.6x2.8mm, EVQ 4.5x4.5mm); flattening/truncation makes the menu look like one part
    # specification.
    **{('adafruit-qt-py-esp32-s3', ref): {'description': None} for ref in (
        'Q1', 'Q2',
    )},
    # protocentral-openox: Eagle deviceset description lists multiple switch packages (6x6mm, KMR2
    # 4.6x2.8mm, EVQ 4.5x4.5mm); flattening/truncation makes the menu look like one part
    # specification.
    ('protocentral-openox', 'SW2'): {'description': None},
    # internal-usb-hub: Placed TMP61 is a PTC family (components.db TMP6131ELPGMQ1); inherited
    # Thermistor_NTC description claims the opposite coefficient.
    ('internal-usb-hub', 'TH1'): {'description': None},
    # hackeeg-ads1299-shield: Placed TPS72325 is a negative 200mA regulator (components.db
    # TPS72325DBVR); copied TPS732XX description claims NMOS 250mA.
    ('hackeeg-ads1299-shield', 'IC2'): {'description': None},
    # pipad-cm4-logic-board: Placed 15-position connector and SFW15R footprint conflict with copied
    # 22-position FH12 ordering fields; preserve placed value and drop copied identity.
    ('pipad-cm4-logic-board', 'J4'): {'description': None, 'manufacturer': None, 'mouser': None, 'mpn': None},
    # sparkfun-thing-plus-esp32-s3: RT9080 source VMax=5.5V and components.db RT9080 agree;
    # inherited description says 6V maximum.
    **{('sparkfun-thing-plus-esp32-s3', ref): {'description': None} for ref in (
        'U1', 'U6',
    )},
    # cm5-minima-rev2: Placed Value and P/N identify SN74LVC1G14 (inverting Schmitt trigger);
    # inherited 74LVC1G07 text claims non-inverting open-drain buffer.
    ('cm5-minima-rev2', 'U602'): {'description': None},
    # canitcam-ov5640: Placed XC6206P182MR/P282MR and SOT-23 footprint conflict with inherited
    # LT1085-3.6 text (3A, 3.6V, TO-220/263).
    **{('canitcam-ov5640', ref): {'description': None} for ref in (
        'U2', 'U3',
    )},
    # particle-tracker-eval: Eagle LP5910/TLV70433 devicesets carry a description explicitly sourced
    # from tps54531 (5A switching converter), not the placed LDOs.
    **{('particle-tracker-eval', ref): {'description': None} for ref in (
        'U5', 'U6',
    )},
    # px4-optical-flow: Placed RB751V40T1G uses SOD-323; MSS1P4-M3/89A uses MicroSMP (source
    # footprint/partno and components.db agree). Eagle deviceset text specifies DO214AC/SS14, a
    # different package.
    ('px4-optical-flow', 'D1'): {'description': None},
    # px4-fmuv2-pixhawk: Placed RB751V40T1G uses SOD-323; MSS1P4-M3/89A uses MicroSMP (source
    # footprint/partno and components.db agree). Eagle deviceset text specifies DO214AC/SS14, a
    # different package.
    **{('px4-fmuv2-pixhawk', ref): {'description': None} for ref in (
        'D602', 'D904',
    )},
    # beagleconnect-freedom: RF.kicad_sch MPN2, Vendor2 and Seeed Description all agree with placed
    # 6.8uH; primary 742792097 and Description name a 1.5kohm ferrite. Select the documented source
    # option.
    ('beagleconnect-freedom', 'L4'): {'description': 'SMD FIXED Inductor 6.8UH-20%-550MA;0805', 'manufacturer': 'TDK', 'mpn': 'MLZ2012N6R8LT000'},
    # hadesfcs: NAVCPeripherals.sch places u-blox MAX-8Q; copied library/Field7 identify MAX-7Q-0, a
    # different GPS generation. Preserve placed value and drop conflicting ordering code.
    ('hadesfcs', 'U10'): {'mpn': None},
    # opensipm-tia-v3: tiav3.kicad_sch places 1500nH; MLF1005GR56JTD25 encodes R56=0.56uH and even
    # specifies 1005 rather than placed 1608 footprint. No corroboration for changing the placed
    # value.
    ('opensipm-tia-v3', 'L2'): {'mpn': None},
    # powerfeather-powerups: powerups.kicad_sch places a zero-ohm link; copied
    # MPN=504-MFSA0603R0100FSM explicitly encodes 0.0100ohm and is shared with the placed 10mohm
    # R12. Preserve zero, drop copied ordering identity.
    ('powerfeather-powerups', 'R13'): {'mpn': None},
    # seeed-recamera-b4-can: B4_v0.2 schematic places 0R; copied MPZ2012S101AT000 and Description
    # specify a 100ohm ferrite. No second independent source resolving zero-ohm link versus bead;
    # preserve placed value and drop copied ordering fields.
    **{('seeed-recamera-b4-can', ref): {'description': None, 'manufacturer': None, 'mpn': None, 'prod_id': None} for ref in (
        'FB2', 'FB3', 'FB4', 'FB5',
    )},
    # openmd-gan-motor-driver: Cached source places 10uF; exact components.db FS32X475K101EGG
    # specifies 4.7e-06 SI capacitance_f. Keep placed value; remove conflicting MPN.
    **{('openmd-gan-motor-driver', ref): {'mpn': None} for ref in (
        'C1', 'C100', 'C101', 'C102', 'C103', 'C104', 'C105', 'C106', 'C107', 'C108', 'C12',
        'C15', 'C18', 'C19', 'C2', 'C21', 'C23', 'C24', 'C26', 'C27', 'C3', 'C6', 'C7', 'C78',
        'C79', 'C8', 'C80', 'C81', 'C82', 'C86', 'C87', 'C88', 'C89', 'C9', 'C91', 'C93', 'C94',
        'C98', 'C99',
    )},
    # openmd-gan-motor-driver: Cached source places 72kohm; exact components.db FRC0603J1R0 TS
    # specifies 1.0 SI resistance_ohms. Keep placed value; remove conflicting MPN.
    ('openmd-gan-motor-driver', 'R10'): {'mpn': None},
    # openmd-gan-motor-driver: Cached source places 27kohm; exact components.db FRC0603J1R0 TS
    # specifies 1.0 SI resistance_ohms. Keep placed value; remove conflicting MPN.
    ('openmd-gan-motor-driver', 'R15'): {'mpn': None},
    # openmd-gan-motor-driver: Cached source places 240kohm; exact components.db RTT03304JTP
    # specifies 300000.0 SI resistance_ohms. Keep placed value; remove conflicting MPN.
    **{('openmd-gan-motor-driver', ref): {'mpn': None} for ref in (
        'R16', 'R18', 'R20', 'R32',
    )},
    # openmd-gan-motor-driver: Cached source places 240kohm; exact components.db FRC0603J1R0 TS
    # specifies 1.0 SI resistance_ohms. Keep placed value; remove conflicting MPN.
    ('openmd-gan-motor-driver', 'R5'): {'mpn': None},
    # epdiy-v7: Cached source places 52.3kohm; LCSC C23196 identifies 0603WAF5102T5E (51000.0 SI
    # resistance_ohms) in components.db. No independent corroboration to replace placed value;
    # remove conflicting LCSC code.
    ('epdiy-v7', 'R20'): {'lcsc': None},
    # epdiy-v7: Cached source places 47.5kohm; LCSC C25819 identifies 0603WAF4702T5E (47000.0 SI
    # resistance_ohms) in components.db. No independent corroboration to replace placed value;
    # remove conflicting LCSC code.
    ('epdiy-v7', 'R24'): {'lcsc': None},
    # internal-usb-hub: Cached source places 22uF; LCSC C141660 identifies GRM21BR60J107ME15L
    # (9.999999999999999e-05 SI capacitance_f) in components.db. No independent corroboration to
    # replace placed value; remove conflicting LCSC code.
    **{('internal-usb-hub', ref): {'lcsc': None} for ref in (
        'C114', 'C117', 'C38',
    )},
    # internal-usb-hub: Cached source places 220nF; LCSC C114401 identifies CC0402JRX7R9BB221
    # (2.2e-10 SI capacitance_f) in components.db. No independent corroboration to replace placed
    # value; remove conflicting LCSC code.
    **{('internal-usb-hub', ref): {'lcsc': None} for ref in (
        'C41', 'C43', 'C46',
    )},
    # internal-usb-hub: Cached source places 1.5kohm; LCSC C327253 identifies RC0402FR-071R5L (1.5
    # SI resistance_ohms) in components.db. No independent corroboration to replace placed value;
    # remove conflicting LCSC code.
    **{('internal-usb-hub', ref): {'lcsc': None} for ref in (
        'R19', 'R64', 'R65', 'R85',
    )},
    # internal-usb-hub: Cached source places 290kohm; LCSC C5126158 identifies FRC0402F2873TS
    # (287000.0 SI resistance_ohms) in components.db. No independent corroboration to replace placed
    # value; remove conflicting LCSC code.
    ('internal-usb-hub', 'R76'): {'lcsc': None},
    # ulx3s: power.sch placed 100pF agrees with LCSC C14665 (catalog CC0603JRNPO9BN101, 100pF) and
    # Mouser 581-06035A101JAT4A; primary CS0603KRX7R9BB471 is 470pF. Select the independently
    # confirmed 100pF ordering identity; drop unverified supplier codes.
    ('ulx3s', 'C2'): {'digikey': None, 'mpn': 'CC0603JRNPO9BN101', 'newark': None},
    # corevus-g-v0-6: Cached source places 1uF; LCSC C1525 identifies CL05B104KO5NNNC
    # (1.0000000000000001e-07 SI capacitance_f) in components.db. No independent corroboration to
    # replace placed value; remove conflicting LCSC code.
    **{('corevus-g-v0-6', ref): {'lcsc': None} for ref in (
        'C28', 'C29',
    )},
    # ldo-leviathan-v1-3: Cached source places 10ohm; LCSC C226359 identifies AC0402FR-0722RL (22.0
    # SI resistance_ohms) in components.db. No independent corroboration to replace placed value;
    # remove conflicting LCSC code.
    **{('ldo-leviathan-v1-3', ref): {'lcsc': None} for ref in (
        'R35', 'R36', 'R40', 'R41',
    )},
    # twisted-fields-rp2040-base: Cached source places 47uF; LCSC C59461 identifies CL10A226MQ8NRNC
    # (2.2e-05 SI capacitance_f) in components.db. No independent corroboration to replace placed
    # value; remove conflicting LCSC code.
    ('twisted-fields-rp2040-base', 'C95'): {'lcsc': None},
    # twisted-fields-rp2040-base: Cached source places 47kohm; LCSC C328360 identifies
    # AECR0603F470KK9 (470000.0 SI resistance_ohms) in components.db. No independent corroboration
    # to replace placed value; remove conflicting LCSC code.
    **{('twisted-fields-rp2040-base', ref): {'lcsc': None} for ref in (
        'R20', 'R21',
    )},
    # 0104-usb-hub: Cached source supplier convention identifies C13585 as an LCSC/JLC ordering
    # code, not an MPN; move/retain it in lcsc. Exact catalog lookup: [('C13585', 'CL31A106KBHNNNE',
    # '10uF 50V X5R ±10% 1206 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS')]. Preserve placed
    # value.
    ('0104-usb-hub', 'C1'): {'lcsc': 'C13585', 'mpn': None},
    # 0104-usb-hub: Cached source supplier convention identifies C15525 as an LCSC/JLC ordering
    # code, not an MPN; move/retain it in lcsc. Exact catalog lookup: [('C15525', 'CL05A106MQ5NUNC',
    # '10uF 6.3V X5R ±20% 0402 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS')]. Preserve placed
    # value.
    **{('0104-usb-hub', ref): {'lcsc': 'C15525', 'mpn': None} for ref in (
        'C2', 'C3',
    )},
    # 0104-usb-hub: Cached source supplier convention identifies C15008 as an LCSC/JLC ordering
    # code, not an MPN; move/retain it in lcsc. Exact catalog lookup: [('C15008', 'CL31A107MQHNNNE',
    # '100uF 6.3V X5R ±20% 1206 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS')]. Preserve
    # placed value.
    **{('0104-usb-hub', ref): {'lcsc': 'C15008', 'mpn': None} for ref in (
        'C4', 'C5', 'C6',
    )},
    # 0104-usb-hub: Cached source supplier convention identifies C72041 as an LCSC/JLC ordering
    # code, not an MPN; move/retain it in lcsc. Exact catalog lookup: not in the offline stock
    # catalog. Preserve placed value.
    **{('0104-usb-hub', ref): {'lcsc': 'C72041', 'mpn': None} for ref in (
        'D4', 'D5', 'D6',
    )},
    # 0104-usb-hub: Cached source supplier convention identifies C883133 as an LCSC/JLC ordering
    # code, not an MPN; move/retain it in lcsc. Exact catalog lookup: [('C883133',
    # 'BSMD1206-150-16V', '-40℃~+85℃ 1.5A 1.6mm 1.9mm 130mΩ 16V 1W 25mΩ 3.6mm 300ms 3A 40A 1206
    # Resettable Fuses ROHS')]. Preserve placed value.
    **{('0104-usb-hub', ref): {'lcsc': 'C883133', 'mpn': None} for ref in (
        'F1', 'F2', 'F3',
    )},
    # 0104-usb-hub: Cached source supplier convention identifies C165948 as an LCSC/JLC ordering
    # code, not an MPN; move/retain it in lcsc. Exact catalog lookup: [('C165948', 'TYPE-C-31-M-12',
    # '-30℃~+80℃ 1 10,000 cycles 16P 20V 5A 7.35mm Female Surface Mount, Right Angle Type-C SMD USB
    # Connectors ROHS')]. Preserve placed value.
    ('0104-usb-hub', 'J1'): {'lcsc': 'C165948', 'mpn': None},
    # 0104-usb-hub: Cached source supplier convention identifies C386739 as an LCSC/JLC ordering
    # code, not an MPN; move/retain it in lcsc. Exact catalog lookup: [('C386739',
    # 'U-USBAN04P-F005', '0℃~+50℃ 1 1.5A 14mm 30V 4P Female Type-A USB 2.0 Vertical, Flag 插件 USB
    # Connectors ROHS')]. Preserve placed value.
    **{('0104-usb-hub', ref): {'lcsc': 'C386739', 'mpn': None} for ref in (
        'J2', 'J3', 'J4',
    )},
    # 0104-usb-hub: Cached source supplier convention identifies C25905 as an LCSC/JLC ordering
    # code, not an MPN; move/retain it in lcsc. Exact catalog lookup: [('C25905', '0402WGF5101TCE',
    # '-55℃~+155℃ 5.1kΩ 50V 62.5mW Thick Film Resistor ±1% ±100ppm/℃ 0402 Chip Resistor - Surface
    # Mount ROHS')]. Preserve placed value.
    **{('0104-usb-hub', ref): {'lcsc': 'C25905', 'mpn': None} for ref in (
        'R1', 'R2',
    )},
    # 0104-usb-hub: Cached source supplier convention identifies C4109 as an LCSC/JLC ordering code,
    # not an MPN; move/retain it in lcsc. Exact catalog lookup: [('C4109', '0402WGF2001TCE',
    # '-55℃~+155℃ 2kΩ 50V 62.5mW Thick Film Resistor ±1% ±100ppm/℃ 0402 Chip Resistor - Surface
    # Mount ROHS')]. Preserve placed value.
    **{('0104-usb-hub', ref): {'lcsc': 'C4109', 'mpn': None} for ref in (
        'R3', 'R4', 'R5',
    )},
    # 0104-usb-hub: Cached source supplier convention identifies C194405 as an LCSC/JLC ordering
    # code, not an MPN; move/retain it in lcsc. Exact catalog lookup: [('C194405', 'PB22E09071',
    # '-10℃~+60℃ 100mA 30V 3N Latching PC Pin Rectangular Button Through Hole White 插件 Pushbutton
    # Switches ROHS')]. Preserve placed value.
    **{('0104-usb-hub', ref): {'lcsc': 'C194405', 'mpn': None} for ref in (
        'SW1', 'SW2', 'SW3',
    )},
    # 0104-usb-hub: Cached source supplier convention identifies C9002 as an LCSC/JLC ordering code,
    # not an MPN; move/retain it in lcsc. Exact catalog lookup: [('C9002', 'X322512MSB4SI',
    # '-40℃~+85℃ 12MHz 20pF 80Ω Crystal Oscillator ±10ppm ±20ppm SMD3225-4P Crystals ROHS')].
    # Preserve placed value.
    ('0104-usb-hub', 'Y1'): {'lcsc': 'C9002', 'mpn': None},
    # s3xy-bms-tesla-retrofit: Cached source supplier convention identifies C46550429 as an LCSC/JLC
    # ordering code, not an MPN; move/retain it in lcsc. Exact catalog lookup: [('C46550429',
    # 'PA35V680M10x15', '-55℃~+105℃ 10mm 16mm 16mΩ@100kHz 2000hrs@105℃ 35V 4.1A@100kHz 5mm 680uF
    # Polarized Polymer ±20% Plugin,D10xL15mm Polymer Aluminum Capacitors ROHS')]. Preserve placed
    # value.
    **{('s3xy-bms-tesla-retrofit', ref): {'mpn': None} for ref in (
        'C112', 'C34', 'C69',
    )},
    # radar-speed-sign-hb100-amplifier: Cached source supplier convention identifies C49661 as an
    # LCSC/JLC ordering code, not an MPN; move/retain it in lcsc. Exact catalog lookup: [('C49661',
    # '2.54-1*2PFemale', '-40℃~+105℃ 1 1x2P 2.54mm 2P 3.3mm 3A Brass Square Hole Through Hole Top
    # 插件,P=2.54mm Female Headers ROHS')]. Preserve placed value.
    **{('radar-speed-sign-hb100-amplifier', ref): {'mpn': None} for ref in (
        'J1', 'J2', 'J3', 'J4',
    )},
    # cynthion: Cached source supplier convention identifies C42411 as an LCSC/JLC ordering code,
    # not an MPN; move/retain it in lcsc. Exact catalog lookup: [('C42411', '912-121A1027D10200',
    # '-55℃~+85℃ 1 1.5A 10.6mm 1500 Cycles 30V 4P Black Female Right Angle Type-A USB 2.0 插件 USB
    # Connectors ROHS')]. Preserve placed value.
    ('cynthion', 'J3'): {'lcsc': 'C42411', 'mpn': None},
    # orangecrab: J3's primary source is GCT USB4105-GF-A (Mfg/PN); its alternate (Mfg_1/PN_1) is
    # Jing Extension with LCSC code C167321 (918-418K2023S40001, a 16P Type-C receptacle). Keep the
    # primary part and record the alternate's ordering code in lcsc. Preserve placed value.
    ('orangecrab', 'J3'): {'lcsc': 'C167321'},
    # ldo-leviathan-v1-3: Cached source supplier convention identifies C83054 as an LCSC/JLC
    # ordering code, not an MPN; move/retain it in lcsc. Exact catalog lookup: [('C83054',
    # '0603B104K250CT', '100nF 25V X7R ±10% 0603 Multilayer Ceramic Capacitors MLCC - SMD/SMT
    # ROHS')]. Preserve placed value.
    **{('ldo-leviathan-v1-3', ref): {'mpn': None} for ref in (
        'C103', 'C134', 'C140', 'C146', 'C147', 'C148', 'C150', 'C151', 'C152', 'C154', 'C156',
        'C158', 'C159', 'C160', 'C161', 'C162', 'C163', 'C87', 'C98', 'C99',
    )},
    # bus-pirate-6-rev2b: Placed source literal CBW201209U300T uses the bounded maker-family value
    # code; decode to 30ohm and retain original ordering identity. See decoder tests and source
    # record.
    ('bus-pirate-6-rev2b', 'L201'): {'mpn': 'CBW201209U300T'},
    # eez-h24005: Placed source literal EECS5R5H105 uses the bounded maker-family value code; decode
    # to 1F and retain original ordering identity. See decoder tests and source record.
    ('eez-h24005', 'C112'): {'mpn': 'EECS5R5H105'},
    # soldered-capacitive-soil: Placed source literal tc33x-2-103e uses the bounded maker-family
    # value code; decode to 10kohm and retain original ordering identity. See decoder tests and
    # source record.
    ('soldered-capacitive-soil', 'R8'): {'mpn': 'tc33x-2-103e'},
    # seeed-wio-terminal: Placed source literal CBC3225T100MR uses the bounded maker-family value
    # code; decode to 10uH and retain original ordering identity. See decoder tests and source
    # record.
    ('seeed-wio-terminal', 'L6'): {'mpn': 'CBC3225T100MR'},
    # soldered-drv8825-stepper: Placed source literal 12101C335K4T2A uses the bounded maker-family
    # value code; decode to 3.3uF and retain original ordering identity. See decoder tests and
    # source record.
    ('soldered-drv8825-stepper', 'C1'): {'mpn': '12101C335K4T2A'},
    # soldered-drv8825-stepper: Placed source literal 08051C103KAT2A uses the bounded maker-family
    # value code; decode to 10nF and retain original ordering identity. See decoder tests and source
    # record.
    ('soldered-drv8825-stepper', 'C5'): {'mpn': '08051C103KAT2A'},
    # soldered-drv8825-stepper: Placed source literal tc33x-2-104e uses the bounded maker-family
    # value code; decode to 100kohm and retain original ordering identity. See decoder tests and
    # source record.
    ('soldered-drv8825-stepper', 'R4'): {'mpn': 'tc33x-2-104e'},
    # particle-tracker-eval: Placed source literal GZ1608D300TF uses the bounded maker-family value
    # code; decode to 30ohm and retain original ordering identity. See decoder tests and source
    # record.
    ('particle-tracker-eval', 'L10'): {'mpn': 'GZ1608D300TF'},
    # 4-channel-rf-front-end: Placed source literal CSR1206-0R002F1 uses the bounded maker-family
    # value code; decode to 2mohm and retain original ordering identity. See decoder tests and
    # source record.
    ('4-channel-rf-front-end', 'R5'): {'mpn': 'CSR1206-0R002F1'},
})
