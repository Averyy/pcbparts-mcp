#!/usr/bin/env python3
"""Build sensor.db from scraped JSON data files.

Merges all sensor sources into a single SQLite database with FTS5 search.
Re-runnable — always rebuilds from scratch. Never modifies source JSON files.

Usage:
    python scripts/build_sensor_db.py [--data-dir data/] [--output data/sensor.db] [--quiet]
"""

import argparse
import json
import re
import sqlite3
import sys
from datetime import date

from pathlib import Path

# Source load order: first source to create an entry owns scalar fields.
# Later sources only enrich multi-value fields (measures, protocols, etc).
SOURCE_ORDER = [
    # Tier 1: Platform sources
    "arduino", "esphome", "circuitpython", "micropython", "tasmota", "zephyr",
    # Tier 2: Manufacturer sources
    "winsen", "maxbotix", "hilink", "benewake", "atlas_scientific", "bestmodules",
    # Tier 3: Breakout board sources
    "sparkfun", "dfrobot",
]

TIER3_SOURCES = {"sparkfun", "dfrobot"}

# IDs to skip entirely — these are Arduino library names, generic component wrappers,
# or product names that don't correspond to actual sensor ICs/modules.
SKIP_IDS = {
    # Not sensors, each checked against the maker's or project's documentation (2026-11-09).
    # ESPHome platform and software components: "number" had 13 measures from its device-class list
    "number", "dewpoint", "motion",
    # ESPHome integrations for appliances, controllers and other people's sensors
    "duco", "ecocomfort2", "emontx", "haierwaterheater", "mk2pvrouter", "renogyinverterble", "systabus", "vevordtx",
    # Other chips: USB PD controller, stepper driver, I/O expanders, analog mux, RF transceiver,
    # battery charge controller (TI BQ25820; its ADC reports its own voltages and currents)
    "fusb302b", "tmc2209", "waveshareioch32v003", "pca9536", "cd74hc4067", "cc1101", "bq25820",
    # Software with no device of its own, and Winsen ion generators
    "pid5sensors", "ximu3", "rk182xexamples", "zi100zi101", "zi121",
    # An Arduino category that merges MH-Z, Cozir, T67XX, S8, SCD4x, STC3x and PAS CO2 libraries
    "co2",
    # MCU/platform targets in a driver name are not the measured peripheral.
    "rp2040", "rp2350", "esp32", "esp8266", "arduino", "raspberrypi",
    # Sensors inside an SoC, not parts (Zephyr bflb,tsen: the Bouffalo Lab GPADC's own input;
    # silabs,emu-temp: Series 2 die temperature; raspberrypi,bcm283x-vc-thermal: SoC temperature)
    "tsen", "emu", "bcm283xvcthermal",
    # Arduino library names (not IC identifiers)
    "pressuresensor", "i2cencoder", "i2ccolor", "pm2", "10dof",
    "uvindex240370sensor", "24ghzradar",
    # ESPHome generic component wrappers (no specific IC)
    "gasmcv2", "soundlevel", "ultrasonic", "zioultrasonic",
    # Not sensors: utility/converter libraries, projects
    "kelvin2rgb",  # Color temperature to RGB converter (no hardware)
    "esp32solar2",  # Solar regulator project (not a sensor)
    "9dof",  # Generic "9DOF" with no specific IC
    "comp6dofn0m1",  # Generic compass tilt compensation library
    "razorimu9dof",  # SparkFun Razor IMU board (not an IC)
    "ezopmp",  # Atlas Scientific peristaltic pump (not a sensor)
    # Generic analog/protocol wrappers (no specific IC)
    "esp32thermistor",  # ESP32 NTC thermistor reading library (no IC)
    "aci10kantemp",  # Generic 10K RTD analog temperature reading
    "dalybms",  # Daly BMS battery management system (not a sensor)
    "i2s",  # I2S audio interface (protocol, not a sensor IC)
    "imu9dof",  # Generic "IMU 9DOF" library with no specific IC
    # Duplicate library wrappers (sensors already in DB under canonical ID)
    "nhcsr04",  # Duplicate HC-SR04 library wrapper
    "sr04",  # Generic HC-SR04 library wrapper
    "sr04t",  # Generic JSN-SR04T library wrapper
    "pjsnsr04t",  # Tasmota JSN-SR04T wrapper
    "sl001deepanshu",  # Generic ultrasonic distance sensor library
    "sonari2c",  # Generic sonar I2C library
    "mpbmp3xxfull",  # MicroPython BMP3XX library wrapper (duplicate of bmp3xx)
    # Protocol wrappers
    "p1meter",  # P1 electricity meter reader (smart meter protocol)
    "rs485",  # RS485 wind sensor protocol wrapper
    "rtd10k",  # Generic 10K RTD analog reading
    # Not sensors
    "sungtil2",  # SUN GTIL2 grid-tie inverter limiter (not a sensor)
    "sb041",  # senseBox SB041 solar charger (not a sensor)
    # Breakout boards that wrap ICs already in DB
    "gy33",  # GY-33 module (wraps TCS3472, already in DB)
    "gy512",  # GY-512 module (wraps MPU6050, already in DB)
    "gy521",  # GY-521 module (wraps MPU6050, already in DB)
    # Misc hobby/proprietary projects
    "dnmsi2c",  # DNMS custom/hobby sound sensor project
    "somo1elv",  # ELV Somo1 proprietary soil sensor
    "tfa433receiver",  # TFA 433MHz temperature receiver (generic RF)
    # Unknown/undocumented
    "hc8",  # Unknown/undocumented sensor
    "glr01",  # Unknown/undocumented sensor
    "wts01",  # Unknown/undocumented sensor
    # Best Modules non-sensor products
    "bm22o2221",  # Digital servo motor (not a sensor)
    "developmenttools",  # Development tools listing page (not a sensor)
}

# Manufacturer name normalization (acquisitions/rebrandings)
MANUFACTURER_ALIASES = {
    "maxim": "Analog Devices",
    "maxim integrated": "Analog Devices",
    "invensense": "TDK",
    "memsic": "MEMSIC",
}

# IC prefix -> manufacturer mapping for post-merge enrichment.
# Applied ONLY when manufacturer is NULL. Longest prefix matched first.
# Sources: datasheets, manufacturer websites, acquisition history.
IC_PREFIX_MANUFACTURERS: dict[str, str | None] = {
    "bno08xrvc": None,  # Multi-device firmware/library wrapper; no verified chip manufacturer.
    "mq2b": "Winsen",  # https://www.winsen-sensor.com/d/files/manual/mq-2b.pdf
    "pygp2y": "Sharp",  # https://global.sharp/products/device/lineup/selection/opto/dust/index.html
    # Split-device identity audit (2026-11-09); details: data/sensors/ic_alias_evidence.json
    "scd40": "Sensirion",  # https://sensirion.com/media/documents/48C4B7FB/64C134E7/Sensirion_SCD4x_Datasheet.pdf
    "scd41": "Sensirion",  # https://sensirion.com/media/documents/48C4B7FB/64C134E7/Sensirion_SCD4x_Datasheet.pdf
    "mhz19b": "Winsen",  # https://www.winsen-sensor.com/d/files/manual/mh-z19b.pdf
    "mhz19c": "Winsen",  # https://www.winsen-sensor.com/d/files/manual/mh-z19c.pdf
    "mhz19d": "Winsen",  # https://www.winsen-sensor.com/d/files/manual/mh-z19d.pdf
    "mhz19e": "Winsen",  # https://www.winsen-sensor.com/d/files/manual/mh-z19e.pdf
    "mhz1911a": "Winsen",  # https://www.winsen-sensor.com/d/files/manual/mh-z1911a.pdf
    "mhz14a": "Winsen",  # https://www.winsen-sensor.com/d/files/manual/mh-z14a.pdf
    "mhz14b": "Winsen",  # https://www.winsen-sensor.com/d/files/manual/mh-z14b.pdf
    "zh06ii": "Winsen",  # https://www.winsen-sensor.com/d/files/manual/zh06-ii.pdf
    "zh06iii": "Winsen",  # https://www.winsen-sensor.com/d/files/manual/zh06-iii.pdf
    "zh06iv": "Winsen",  # https://www.winsen-sensor.com/d/files/manual/zh06-iv.pdf
    "ld2410b": "Hi-Link",  # https://www.hlktech.net/index.php?id=65
    "ld2410c": "Hi-Link",  # https://www.hlktech.net/index.php?id=65
    "tfminiplus": "Benewake",  # https://en.benewake.com/TFminiPlus/index.html
    "fabo206uvsi1132": "Silicon Labs",  # https://www.silabs.com/documents/public/data-sheets/Si1132.pdf
    # Analog Devices (includes former Maxim Integrated, Linear Technology)
    "ad8": "Analog Devices",       # AD8232, AD8494/8495
    "ade": "Analog Devices",       # ADE7880, ADE7953 energy metering
    "adis": "Analog Devices",      # ADIS16470 IMU
    "ads1": "Texas Instruments",   # ADS1115, ADS1118, ADS1220, ADS1258, ADS1292R, ADS1293
    "adt": "Analog Devices",       # ADT7410
    "adxl": "Analog Devices",      # ADXL313, ADXL335, ADXL343, ADXL375
    "afe4": "Texas Instruments",   # AFE4490, AFE4950 (TI analog front ends)
    "ltc": "Analog Devices",       # LTC2959 (former Linear Technology)
    "max1": "Analog Devices",      # MAX17043, MAX17055 (former Maxim)
    "max3": "Analog Devices",      # MAX30001, MAX30003, MAX30102, MAX31820, MAX31850, MAX31855
    "max44": "Analog Devices",     # MAX44007
    "max471": "Analog Devices",    # MAX471
    "max6": "Analog Devices",      # MAX6626
    "max86": "Analog Devices",     # MAX86150
    "max96": "Analog Devices",     # MAX9611
    "ds18": "Analog Devices",      # DS18B20, DS18x20 (former Dallas/Maxim)
    "ds1621": "Analog Devices",    # DS1621 (former Dallas/Maxim)
    "ds1821": "Analog Devices",    # DS1821 (former Dallas/Maxim)
    "ds7505": "Analog Devices",    # DS7505 (former Maxim)

    # ams-OSRAM (includes former AMS, TAOS, CMOSIS)
    "as5": "ams-OSRAM",            # AS5047P, AS5200L, AS5600L (position sensors)
    "as7": "ams-OSRAM",            # AS7262, AS7263, AS7265X, AS7331, AS7341, AS7343
    "as3935": "ams-OSRAM",         # AS3935 lightning detector (now ScioSense spun off some, but AS3935 is still ams)
    "tcs3": "ams-OSRAM",           # TCS3430, TCS3472, TCS34725 (former TAOS)
    "tcs230": "ams-OSRAM",         # TCS230 (former TAOS)
    "tmd": "ams-OSRAM",            # TMD3725
    "tmf8": "ams-OSRAM",           # TMF8801, TMF8820, TMF8821
    "tsl2": "ams-OSRAM",           # TSL235R, TSL2550 (former TAOS)
    "apds99": "Broadcom",          # APDS9900, APDS9999 (Broadcom/Avago, NOT ams — apds9960 is Broadcom too)

    # Aosong
    "aht": "Aosong",               # AHT10, AHT1X, AHT2X, AHTX0
    "am23": "Aosong",              # AM2315, AM2315C, AM2320, AM2321
    "dht": "Aosong",               # DHT11, DHT12, DHT21, DHT22

    # Bosch Sensortec
    # Holtek Semiconductor (BM*S series sensor modules, sold via Best Modules Corp)
    "bm22s": "Holtek",             # BM22Sxxxx sensor modules
    "bm25s": "Holtek",             # BM25Sxxxx
    "bm32s": "Holtek",             # BM32Sxxxx
    "bm42s": "Holtek",             # BM42Sxxxx
    "bm62s": "Holtek",             # BM62Sxxxx
    "bm92s": "Holtek",             # BM92Sxxxx
    "bma": "Bosch",                # BMA220, BMA423
    "bme": "Bosch",                # BME280, BME680, BME690, BME34M101, etc.
    "bmh": "Holtek",               # BMH06203, BMH08002, etc. (Best Modules Corp / Holtek)
    "bmi": "Bosch",                # BMI270
    "bmk": "Holtek",               # BMK52T016, etc. (Best Modules Corp / Holtek)
    "bml": "Holtek",               # BML36M001 (Best Modules Corp / Holtek)
    "bmm": "Bosch",                # BMM150
    "bmp": "Bosch",                # BMP280, BMP585, BMP58X, BMP5XX
    "bms": "Holtek",               # BMS26M833, BMS33M332, etc. (Best Modules Corp / Holtek)
    "bmv": "Bosch",                # BMV080, BMV23M001
    "bmx": "Bosch",                # BMX055, BMX160
    "bno": "Bosch",                # BNO055, BNO080, BNO08X

    # Cubic Sensor and Instrument
    "cm1106": "Cubic",             # CM1106 CO2 sensor

    # Espressif (skip esp32/esp8266 — those are MCUs, not sensors)

    # FocalTech
    "ft5336": "FocalTech",         # FT5336 touch controller
    "ft6": "FocalTech",            # FT6X06 touch controller

    # Hynitron (now Chipsea)
    "cst8": "Hynitron",            # CST816D, CST8XX touch controllers

    # Infineon
    "tli4971": "Infineon",         # TLI4971 current sensor
    "tlv493d": "Infineon",         # TLV493D magnetic sensor

    # Kionix (now ROHM)
    "kx023": "ROHM",               # KX023 (Kionix, acquired by ROHM)
    "kx132": "ROHM",               # KX132 (Kionix)
    "kx134": "ROHM",               # KX134 (Kionix)
    "kxtj3": "ROHM",              # KXTJ3 (Kionix)

    # Lite-On
    "ltr3": "Lite-On",             # LTR308, LTR329, LTR381RGB, LTR390
    "ltr5": "Lite-On",             # LTR501, LTR507
    "ltralsps": "Lite-On",         # LTR ALS/PS generic

    # Measurement Specialties / TE Connectivity
    "hp03s": "TE Connectivity",    # HP03S
    "hp303b": "TE Connectivity",   # HP303B (also branded as DPS310 by Infineon, but HP303B is TE)
    "htu21": "TE Connectivity",    # HTU21D
    "htu31": "TE Connectivity",    # HTU31D
    "ms4525": "TE Connectivity",   # MS4525DO
    "ms5611": "TE Connectivity",   # MS5611
    "ms5803": "TE Connectivity",   # MS5803
    "ms580314": "TE Connectivity", # MS5803-14BA

    # Melexis
    "mlx90": "Melexis",            # MLX90377, MLX90392, MLX90393, MLX90614, MLX90615, etc.

    # Microchip (includes former Atmel)
    "at42qt": "Microchip",         # AT42QT1010, AT42QT1011 (former Atmel touch)
    "mcp9": "Microchip",           # MCP9802
    "mpl115": "NXP",               # MPL115A1, MPL115A2 (NXP/Freescale pressure)
    "mpl3115": "NXP",              # MPL3115A2 (NXP/Freescale pressure)
    "mpr121": "NXP",               # MPR121 (NXP touch controller)
    "mprls": "Honeywell",          # MPRLS (Honeywell MicroPressure)
    "cap1188": "Microchip",        # CAP1188
    "cap1203": "Microchip",        # CAP1203

    # MEMSIC
    "mmc56": "MEMSIC",             # MMC5603, MMC5603NJ
    "mmc5983": "MEMSIC",           # MMC5983, MMC5983MA
    "mmc34": "MEMSIC",             # MMC34160PJ

    # NXP (includes former Freescale)
    "fxas": "NXP",                 # FXAS21002C (former Freescale gyro)
    "mma7": "NXP",                 # MMA7455, MMA7660 (former Freescale accel)
    "mma8": "NXP",                 # MMA8451, MMA8452Q, MMA8453Q, MMA8652
    "pca9536": "NXP",              # PCA9536 I/O expander
    "pct2075": "NXP",              # PCT2075 temperature
    "mpx": "NXP",                  # MPX5700, MPXA6115A, MPXHZ6116A (pressure)

    # ON Semiconductor
    "ncs36000": "ON Semiconductor", # NCS36000

    # Panasonic
    "amg8833": "Panasonic",        # AMG8833 thermal camera
    "ekmb": "Panasonic",           # EKMB1107112 PIR
    "ekmc": "Panasonic",           # EKMC4607112K PIR

    # Plantower
    "pms": "Plantower",            # PMS3003, PMS5003, PMSA003I, PMSX003

    # PixArt
    "pmw33": "PixArt",             # PMW3360 optical mouse
    "pmw39": "PixArt",             # PMW3901 optical flow
    "paa5160": "PixArt",           # PAA5160E1

    # QST Corporation
    "qmc": "QST",                  # QMC5883, QMC5883L, QMC5883P
    "qmi": "QST",                  # QMI8658, QMI8658C
    "qmp": "QST",                  # QMP6988

    # Renesas (includes former Intersil, IDT)
    "isl28": "Renesas",            # ISL28022 (former Intersil)
    "isl29": "Renesas",            # ISL29034, ISL29125 (former Intersil)

    # ROHM
    "bh17": "ROHM",                # BH1730FVC, BH1749NUC, BH1750
    "bh19": "ROHM",                # BH1900NUX

    # ScioSense (spun off from ams)
    "ens": "ScioSense",            # ENS161

    # Sensirion
    "sfa": "Sensirion",            # SFA30, SFA40
    "sgp": "Sensirion",            # SGP4X
    "sht": "Sensirion",            # SHT11, SHT1X, SHT20, SHT25, SHT3X
    "sps30": "Sensirion",          # SPS30
    "stc31": "Sensirion",          # STC31
    "sen5": "Sensirion",           # SEN54, SEN55, SEN5X (Sensirion Environmental Node)
    "sen6": "Sensirion",           # SEN6X

    # Sharp
    "gp2y": "Sharp",               # GP2Y0A21YK, GP2Y0A41SK0F, GP2Y0E03

    # Silicon Labs
    "si7": "Silicon Labs",         # SI7005, SI7013, SI7021, SI705X, SI70XX
    "si114": "Silicon Labs",       # SI1142, SI1145, SI114X

    # STMicroelectronics
    "asm330": "STMicroelectronics",  # ASM330LHH
    "h3lis": "STMicroelectronics",   # H3LIS200DL, H3LIS331DL
    "hts221": "STMicroelectronics",  # HTS221
    "iis2": "STMicroelectronics",    # IIS2DULPX
    "imp34": "STMicroelectronics",   # IMP34DT05 MEMS microphone
    "ism330": "STMicroelectronics",  # ISM330IS
    "l3g": "STMicroelectronics",     # L3G, L3GD20
    "lis2": "STMicroelectronics",    # LIS2HH12
    "lis331": "STMicroelectronics",  # LIS331
    "lps2": "STMicroelectronics",    # LPS22, LPS28, LPS2X
    "lps35": "STMicroelectronics",   # LPS35HW
    "lsm": "STMicroelectronics",     # LSM303, LSM6DS3TR, LSM6DSM, LSM9DS1TR
    "mp23": "STMicroelectronics",    # MP23DB01HP MEMS microphone
    "stmpe": "STMicroelectronics",   # STMPE610 touch controller
    "vl53": "STMicroelectronics",    # VL53L4CD
    "vl6180": "STMicroelectronics",  # VL6180

    # TDK (includes former InvenSense, Chirp)
    "icg20": "TDK",                # ICG20660, ICG20660L
    "icm2": "TDK",                 # ICM20689, ICM20948, ICM20X
    "icm4": "TDK",                 # ICM42670P, ICM42670S, ICM45608, ICM45689
    "icp10": "TDK",                # ICP10111, ICP10125
    "ics406": "TDK",               # ICS40619 MEMS microphone
    "itg3200": "TDK",              # ITG3200 (former InvenSense)
    "mpu": "TDK",                  # MPU6000, MPU6886, MPU9X50

    # Texas Instruments
    "cd74hc": "Texas Instruments",  # CD74HC4067 mux
    "drv": "Texas Instruments",     # DRV series
    "hdc": "Texas Instruments",     # HDC1008, HDC3022
    "ina": "Texas Instruments",     # INA169, INA219, INA228, INA23X, INA260, INA2XX, INA780X
    "lm335": "Texas Instruments",   # LM335A
    "lm73": "Texas Instruments",    # LM73
    "lm75": "Texas Instruments",    # LM75, LM75A, LM75B (originally National Semi)
    "lmp91": "Texas Instruments",   # LMP91000
    "lmt01": "Texas Instruments",   # LMT01
    "opt": "Texas Instruments",     # OPT series
    "tmp": "Texas Instruments",     # TMP006 (TMP36 is Analog Devices — has separate longer prefix)

    # Vishay
    "vcnl": "Vishay",              # VCNL36687, VCNL4020
    "veml": "Vishay",              # VEML3235, VEML3328, VEML6030, VEML6070, VEML6075
    "temt6000": "Vishay",          # TEMT6000

    # Avia Semiconductor
    "hx71": "Avia Semiconductor",  # HX710, HX710A, HX710B, HX711

    # Allegro MicroSystems
    "acs7": "Allegro",             # ACS712, ACS723, ACS772

    # Honeywell
    "hsc": "Honeywell",            # HSCDTD008A
    "hpma": "Honeywell",           # HPMA115XX particle sensor

    # E+E Elektronik
    "ee895": "E+E Elektronik",     # EE895 CO2 sensor

    # Sensirion (HS3003 is actually Renesas)
    "hs3003": "Renesas",           # HS3003 humidity sensor (Renesas, was IDT)

    # Nuvoton
    "nau7802": "Nuvoton",          # NAU7802 ADC

    # Cypress / Infineon
    "cy8cmbr": "Infineon",         # CY8CMBR3xxx CapSense (former Cypress, now Infineon)

    # Omron
    "d6f": "Omron",                # D6F-PH flow sensor

    # Sensata / Amphenol
    "npi19": "Amphenol",           # NPI-19 pressure

    # Atmel / Microchip energy metering
    "atm90e": "Microchip",         # ATM90E26, ATM90E32 (former Atmel)

    # Hiletgo / generic module ICs
    "hcsr04": "Generic",           # HC-SR04 ultrasonic (multiple manufacturers)

    # TE Connectivity (additional)
    "msp300": "TE Connectivity",   # MSP300 pressure transducer

    # Würth Elektronik
    "wsen": "Würth Elektronik",    # WSEN series

    # Cubic
    "cb": "Cubic",                 # CB-HCHO-V4

    # DFRobot product SKUs (these are breakout boards, skip — manufacturer is the IC)
    # sen0xxx → DFRobot SKU numbers, skip

    # SM300D2: a Shenzhen-made module sold under its own code; no maker datasheet names a company
    # (2026-11-09), and nothing ties it to Amphenol
    "sm300d2": "Generic",
    "adc128d818": "Texas Instruments",  # ADC128D818 system monitor (formerly National)
    "cs1237": "Chipsea",           # CS1237/CS1238 load-cell ADCs

    # Microchip (MGC3130)
    "mgc3130": "Microchip",        # MGC3130 GestIC

    # Murata
    "sngcja5": "Panasonic",        # SN-GCJA5 is Panasonic
    "sca": "Murata",               # SCA series

    # Semtech
    "sx8634": "Semtech",           # SX8634 touch controller

    # Sensata/BEI
    "am4096": "RLS",               # AM4096 is RLS (Renishaw)

    # Rohm
    "ml8511": "ROHM",              # ML8511 UV sensor is ROHM (formerly Lapis)

    # Analog Devices (TMP36)
    "tmp36": "Analog Devices",     # TMP36 is Analog Devices, not TI

    # Microchip (TC74)
    "tc74": "Microchip",           # TC74 temperature sensor

    # CSE energy metering (Chipsea/HiSilicon)
    "cse77": "HiSilicon",          # CSE7761, CSE7766

    # BL energy metering (Shanghai Belling)
    "bl09": "Shanghai Belling",    # BL0906, BL0939, BL0940, BL0942

    # HLW energy metering (HiLance / HLW)
    "hlw80": "HiSilicon",          # HLW8012, HLW8032

    # Cirque
    "iqs5": "Azoteq",              # IQS5xx (Azoteq touch)

    # MEMSIC (MSA)
    "msa3": "MEMSIC",              # MSA301, MSA3XX accelerometers

    # Winbond (W25 series is flash, not sensors)

    # AP3216 — Lite-On
    "ap3216": "Lite-On",           # AP3216 ambient light + proximity

    # MC3479 — MEMSIC
    "mc3479": "MEMSIC",            # MC3479 accelerometer

    # NST1001 — Novosense
    "nst1001": "Novosense",        # NST1001 temperature

    # RM3100 etc — PNI
    "pni": "PNI",                  # PNI magnetometers

    # Asahi Kasei
    "ak97": "Asahi Kasei",         # AK9750, AK9753

    # PCT2075 — NXP (already above)

    # S5851A — ABLIC
    "s5851": "ABLIC",              # S5851A temperature

    # CHT — Sensirion (no, CHT8305/8310/832X is Gxht / Nanjing Gaohua)
    "cht8": "Gxht",                # CHT8305, CHT8310, CHT832X

    # LC709203F — ON Semiconductor
    "lc709203": "ON Semiconductor", # LC709203F battery gauge

    # EMC2101 — Microchip
    "emc2101": "Microchip",        # EMC2101 fan controller

    # CS5460A, CS5464, CS5490 — Cirrus Logic
    "cs54": "Cirrus Logic",        # CS5460A, CS5464 energy metering
    "cs549": "Cirrus Logic",       # CS5490

    # MT6701 — MagnTek
    "mt6701": "MagnTek",           # MT6701 magnetic encoder

    # SPA06 — Goertek
    "spa06": "Goertek",            # SPA06 barometric pressure

    # SPL06, SPL07 — Goertek
    "spl06": "Goertek",            # SPL06 barometric pressure
    "spl07": "Goertek",            # SPL07

    # MICS — SGX Sensortech (now Amphenol)
    "mics": "SGX Sensortech",      # MICS4514, MICS6814

    # IPS7100 — Piera Systems
    "ips7100": "Piera Systems",    # IPS7100 particle sensor

    # Honeywell (additional)
    "ah1815": "Diodes Incorporated",         # AH1815 Hall effect

    # TSC2007 — Texas Instruments
    "tsc2007": "Texas Instruments", # TSC2007 touch controller

    # TSD305 — TE Connectivity
    "tsd305": "TE Connectivity",   # TSD305 thermopile

    # PAJ7620 — PixArt
    "paj7620": "PixArt",           # PAJ7620U2 gesture

    # HMC6343, HMC6352 — Honeywell
    "hmc63": "Honeywell",          # HMC6343
    "hmc6352": "Honeywell",        # HMC6352

    # GDK101 — FTLAB
    "gdk101": "FTLAB",             # GDK101 gamma radiation

    # FS3000 — Renesas
    "fs3000": "Renesas",           # FS3000 air velocity (was IDT, now Renesas)

    # HTE501, TEE501 — TE Connectivity (no, these are IST AG / Innovative Sensor Technology)
    "hte501": "IST AG",            # HTE501 humidity+temp
    "tee501": "IST AG",            # TEE501 temperature

    # HYT271 — IST AG
    "hyt271": "IST AG",            # HYT271 humidity

    # ACS energy metering (already Allegro above)

    # AGS — ASAIR (now Aosong subsidiary)
    "ags": "ASAIR",                # AGS01DB, AGS02MA

    # Acconeer
    "a111": "Acconeer",            # A111 radar sensor
    "xm125": "Acconeer",           # XM125 radar module

    # PAV3000 - not a well-known IC, skip

    # RCWL — generic radar modules (RCWL-0516 etc.)

    # LD2420 — Hi-Link (already in manufacturer sources)

    # RFD77402 — Simblee/RF Digital (now Sparkfun-associated, but IC is by ams)
    "rfd77402": "ams-OSRAM",       # RFD77402 ToF (uses ams TMF8701 die)

    # ZMOD4450 — Renesas
    "zmod": "Renesas",             # ZMOD4450 gas sensor (was IDT)

    # Winsen (PM2005 etc.) — should be picked up by source, but just in case
    "pm2005": "Winsen",            # PM2005 particle sensor

    # SDS011, SDS021 — Nova Fitness
    "sds0": "Nova Fitness",        # SDS011, SDS021

    # Sensirion — SEN21231 is actually SparkFun's product number for the Useful Sensors Person Sensor
    # Skip sen0xxx and sen1xxxx — those are DFRobot/SparkFun product numbers

    # Senseair — already a known brand
    "senseair": "Senseair",        # Senseair CO2 sensors (K30, K70 etc.)

    # T6615, T6703, T6713 — Amphenol (formerly Telaire/GE)
    "t66": "Amphenol",             # T6615
    "t67": "Amphenol",             # T6703
    "t6713": "Amphenol",           # T6713

    # MTP40 — Winsen
    "mtp40": "Winsen",             # MTP40, MTP40F CO2 sensor

    # ACD10, ACD3100 — Aosong
    "acd": "Aosong",               # ACD10, ACD3100 CO2 sensors

    # XGZP — CFSensor
    "xgzp": "CFSensor",            # XGZP6897D, XGZP68XX pressure

    # PM1006 — Cubic
    "pm1006": "Cubic",             # PM1006, PM1006K

    # HM3301 — Seeed Studio sensor module (IC is Honeywell HPMA-style)
    # Actually HM3301 is by Seeed / Sensirion-type — skip, unclear IC origin

    # LWLP5000 — TE Connectivity (All Sensors, acquired by TE)
    "lwlp": "TE Connectivity",     # LWLP5000

    # u-blox GNSS
    "ublox": "u-blox",             # u-blox GNSS receivers

    # Unicore Communications
    "um980": "Unicore",            # UM980 GNSS

    # LG290P — Quectel
    "lg290p": "Quectel",           # LG290P GNSS

    # PPD71 — Shinyei
    "ppd71": "Shinyei",            # PPD71 particle sensor (Shinyei PPD42-equivalent)

    # PZEM — Peacefair
    "pzem": "Peacefair",           # PZEM004T energy meter

    # Hydreon — Hydreon Corporation (rain sensors)
    "hydreon": "Hydreon",          # Hydreon RG-XX rain sensors
    "hrg15": "Hydreon",            # HRG15 rain gauge
    "rg15": "Hydreon",             # RG15 rain gauge

    # K30, K70 — Senseair
    "k30": "Senseair",             # K30 CO2
    "k70": "Senseair",             # K70 CO2

    # TCRT5000 — Vishay
    "tcrt5000": "Vishay",          # TCRT5000 reflective optical

    # US1881 — Melexis
    "us1881": "Melexis",           # US1881 Hall-effect latch (actually by various, but Melexis is primary)

    # TTP223, TTP229 — Tontek Design (Tongtech)
    "ttp2": "Tontek",              # TTP223, TTP229

    # Goodix
    "gt9": "Goodix",               # GT9XX touch
    "gsl1680": "Silead",           # GSL1680 touch (Silead/Goodix ecosystem)

    # MMR902 — Murata
    "mmr902": "Murata",            # MMR902

    # Microchip (additional)
    "mcp": "Microchip",            # Generic MCP prefix

    # CT1780 — Sensylink Microelectronics (Shanghai)
    "ct1780": "Sensylink",             # CT1780 thermocouple amplifier IC

    # MPM10 — Memsfrontier (Shenzhen)
    "mpm10": "Memsfrontier",           # MPM10 laser particle sensor

    # INA — already TI above; tiina226 is a MicroPython library name prefix, not an IC prefix
    # pybina219, pympu6050, mpybh1750fvi, mpybme280 — library prefixes, not IC prefixes

    # DTS6012M — Amphenol
    "dts6012": "Amphenol",         # DTS6012M

    # TSL prefix — already ams-OSRAM above

    # LP5562 etc. — TI LED drivers
    # LIS prefix — STMicro, already covered

    # TAD2144 — TI (actually Infineon TDA2144 / TLE series?) — skip, unclear

    # TS4231, TS8000 — Triad Semiconductor (now owned by Qualcomm/Valve)
    "ts4231": "Triad Semiconductor",  # TS4231 IR light-to-digital
    "ts8000": "Triad Semiconductor",  # TS8000 IR light-to-digital

    # XPT2046 — Shenzhen Xptek
    "xpt2046": "Shenzhen Xptek",   # XPT2046 touch controller

    # GP20U7 — Adafruit breakout of a MediaTek GPS — skip, breakout product number

    # B-LUX-V30B — ROHM (BH series?) — actually it's by Beilijie/BeiLi, a Chinese company

    # TT21100 — Parade Technologies (formerly Cypress)
    "tt21100": "Parade Technologies",  # TT21100 touch controller

    # MSM261 — TDK/InvenSense MEMS microphone
    "msm261": "TDK",               # MSM261 MEMS microphone

    # AMT25 — CUI Devices (AMT encoder series)
    "amt25": "CUI Devices",        # AMT25 rotary encoder

    # SD3031 — WHWAVE (Shenzhen Whwave)
    "sd3031": "WHWAVE",            # SD3031 RTC

    # TL555Q — Texas Instruments
    "tl555q": "Texas Instruments",  # TL555Q timer (CMOS 555)

    # ADSTDS75LM75 — combo library for DS75/LM75 (both are Analog Devices/TI family)
    "adstds75": "Analog Devices",  # ADSTDS75LM75 library

    # 7Semi — 7Semi boards use Bosch BNO08X / CO2 sensors
    "7semi": "Bosch",              # 7Semi uses Bosch ICs

    # MTS4X — Sensirion (STS4x variant naming)
    "mts4": "Sensirion",           # MTS4X (Sensirion STS4x)

    # TAS501, TAS606 — ASAIR (Aosong subsidiary)
    "tas5": "ASAIR",               # TAS501
    "tas6": "ASAIR",               # TAS606

    # GR1030 — Shenzhen Grow
    "gr1030": "Grow",              # GR10_30 gesture

    # SCT013 — YHDC (Yueqing Huida)
    "sct013": "YHDC",              # SCT013 current transformer

    # ZMPT101B — ZMPT (Qingxian Zeming Langxi Electronic)
    "zmpt": "ZMPT",                # ZMPT101B voltage transformer

    # RC-WL series — Shenzhen RCWL
    "rcwl": "RCWL",                # RCWL-0516, RCWL9610, RCWL9620

    # RD03 — Ai-Thinker
    "rd03": "Ai-Thinker",          # RD03 radar module

    # MR24HPC1, MR60BHA2 — Seeed Studio (24GHz mmWave modules)
    "mr24": "Seeed Studio",        # MR24HPC1 mmWave
    "mr60": "Seeed Studio",        # MR60BHA2 mmWave

    # PM25 — Plantower (PM2.5 series)
    "pm25": "Plantower",           # PM25

    # LD2420 — Hi-Link
    "ld2420": "Hi-Link",           # LD2420 radar

    # DFRobot sensor SKU numbers — these are product IDs, not IC prefixes; skip
    # SEN0xxx, SEN1xxxx, TEL0xxx, DFR0xxx — all DFRobot product numbers

    # Honeywell (ABP, HIH series pressure/humidity)
    "honeywellabp": "Honeywell",    # Honeywell ABP pressure
    "honeywellhih": "Honeywell",    # Honeywell HIH humidity

    # Hi-Link radar modules (hlk prefix)
    "hlkld": "Hi-Link",            # HLK-LD2410, LD2410B, LD2410S
    "hlkfm": "Hi-Link",            # HLK-FM22X

    # MaxBotix (hrxl)
    "hrxlmaxsonar": "MaxBotix",    # HRXL MaxSonar WR

    # DFRobot URM series ultrasonic (these are DFRobot-branded but use known ICs)
    "urm07": "DFRobot",            # URM07 ultrasonic
    "urm09": "DFRobot",            # URM09 ultrasonic
    "urm13": "DFRobot",            # URM13 ultrasonic

    # DYP-ME007 — DYP (Dyp Corporation)
    "dypme007": "DYP",              # DYPME007 ultrasonic

    # FocalTech (uFT6336U)
    "uft6336": "FocalTech",         # uFT6336U touch

    # JSN-SR04T — generic ultrasonic module
    "jsnsr04t": "Generic",          # JSN-SR04T ultrasonic

    # ISYS4001 — InnoSenT
    "isys4001": "InnoSenT",        # iSYS-4001 radar

    # TFLI2C — Benewake (TFLuna I2C)
    "tfli2c": "Benewake",          # TFLi2c (TF-Luna I2C variant)

    # MG811 — Winsen (CO2 sensor)
    "mg811": "Winsen",              # MG811 CO2 sensor

    # T5403 — EPCOS (now TDK)
    "t5403": "TDK",                 # T5403 barometric (EPCOS, now TDK)

    # Xiaomi BLE thermometers
    "xiaomi": "Xiaomi",             # Xiaomi LYWSD02MMC, XMWSDJ04MMC

    # RP2040 — Raspberry Pi Foundation (MCU, not sensor, but in the DB)
    "rp2040": "Raspberry Pi",       # RP2040 MCU

    # ME007 — generic Chinese ultrasonic (unclear manufacturer)

    # Barometric HP20x — HopeRF HP203B
    "barometerhp20x": "HopeRF",    # HP20x barometric

    # WF100DPZ — Würth Elektronik
    "wf100dpz": "Würth Elektronik", # WF100DPZ differential pressure

    # HP303B is actually Infineon DPS310 packaged by various — fix the comment but keep TE
    # (HP303B is branded by GOERTEK, but often conflated with DPS310)

    # --- Added for manufacturer coverage improvement ---

    # DFRobot product SKU numbers (SEN0xxx, TEL0xxx, DFR0xxx, EC10, C400x, 64x8DTOF)
    "sen0": "DFRobot",              # SEN0153, SEN0161, SEN0285, SEN0321, SEN0322, SEN0343,
                                     # SEN0390, SEN0395, SEN0496, SEN0560, SEN0575, SEN0590
    "tel0": "DFRobot",              # TEL0157, TEL0171 GNSS modules
    "dfr0": "DFRobot",              # DFR0300 conductivity sensor
    "ec10": "DFRobot",              # EC10 conductivity sensor (DFR0300 variant)
    "c4001": "DFRobot",             # C4001 mmWave radar module (SEN0609/SEN0610)
    "c4002": "DFRobot",             # C4002 mmWave radar module (SEN0691)
    "64x8dtof": "DFRobot",          # 64x8 dToF laser ranging (SEN0682)
    "a02yyuw": "DFRobot",           # A02YYUW ultrasonic distance sensor
    "pav3000": "DFRobot",           # PAV3000 air velocity sensor
    "lidar07": "DFRobot",           # LIDAR07 laser ranging (SEN0413)
    "son1303": "DFRobot",           # SON1303 heart rate sensor (SEN0203)
    "wt61pc": "WIT-motion",         # WT61PC 6-axis IMU (SEN0386)

    # La Crosse Technology / Technoline wind sensors
    "tx20": "La Crosse Technology",  # TX20 anemometer
    "tx23": "La Crosse Technology",  # TX23 anemometer
    "ws2300": "La Crosse Technology", # WS2300-15 anemometer (Technoline)
    "tx07k": "La Crosse Technology",  # TX07K temperature sensor

    # SparkFun product numbers
    "sen10724": "SparkFun",          # SEN-10724 breakout board
    "sen21231": "SparkFun",          # SEN-21231 (Useful Sensors Person Sensor)
    "at407": "SparkFun",             # AT-407 breakout

    # RAKWireless modules
    "rak1": "RAKWireless",           # RAK12010, RAK12019, RAK12021, RAK12023, RAK12025,
                                      # RAK12039, RAK14002

    # IoT-devices (Ukrainian company)
    "ggreg20": "IoT-devices",       # GGreg20_V3 ionizing radiation detector

    # Seeed Studio
    "hm3301": "Seeed Studio",       # HM330X dust/particulate sensor

    # Benewake (additional)
    "lc02": "Benewake",             # TF-LC02 laser distance sensor

    # Garmin
    "lidarlightv3hp": "Garmin",     # LIDAR Lite v3HP

    # Melopero / u-blox SAM-M8Q GPS
    "meloperosamm8q": "u-blox",     # Melopero SAM-M8Q GNSS (u-blox IC)

    # TE Connectivity (additional)
    "tem3200": "TE Connectivity",   # TEM3200 pressure sensor

    # Keller (Swiss pressure sensors)
    "pd10lx": "Keller",             # PD-10LX pressure/temperature sensor

    # Invensense / TDK (additional)
    "tad2144": "TDK",               # TAD2144 TMR angle sensor

    # Ainstein
    "usd1": "Ainstein",             # US-D1 RADAR altimeter

    # uFire
    "ufire": "uFire",               # UFIRE_EC, UFIRE_ISE electrochemical sensors

    # Truebner
    "smt100": "Truebner",           # SMT100 soil moisture/temperature

    # Tinovi
    "pmwcs3": "Tinovi",             # PMWCS3 soil moisture sensor

    # ZyAura
    "zyaura": "ZyAura",             # ZyAura CO2/temperature monitor

    # TOF10120 — generic Chinese ToF sensor (multiple manufacturers)
    "tof10120": "Generic",          # TOF10120 laser ranging (no single mfr)

    # M5Stack
    "kmeteriso": "M5Stack",         # K-Meter ISO thermocouple module

    # Hamamatsu
    "s9706": "Hamamatsu",           # S9706 color sensor

    # FGSensors
    "fg3": "FGSensors",             # FG-3+ magnetometer

    # x-io Technologies
    "ximu3": "x-io Technologies",   # xIMU3 IMU

    # NEWOPTO
    "xycals21c": "NEWOPTO",         # XYC_ALS21C ambient light sensor

    # LCJ Capteurs (French anemometer company)
    "cv7": "LCJ Capteurs",          # CV7-OEM ultrasonic anemometer

    # Velleman
    "wpi430": "Velleman",           # WPI430/VMA430 GPS module

    # IoTy LiDAR sensors (spinning LiDAR modules, various manufacturers)
    "iotycoind4": "Generic",        # COIN-D4 360° LiDAR (Guoke Optical Core / CSPC Tech)
    "iotydelta2d": "Generic",       # Delta-2D 360° LiDAR (3iRobotix)
    "iotylds02rr": "Generic",       # LDS02RR 360° LiDAR (Xiaomi/Roborock OEM)

    # IM19 — Yostlabs / YEI Technology tilt sensor
    "im19": "Yostlabs",             # IM19 tilt sensor

    # B-LUX-V30B — Beilijie light sensor
    "bluxv30b": "Beilijie",         # B-LUX-V30B ambient light sensor

    # DCT532 — Analog Microelectronics (now part of Silicon Microstructures)
    "dct532": "Analog Microelectronics", # DCT532 industrial pressure sensor

    # GM1602 — Winsen CO sensor
    "gm1602": "Winsen",             # GM1602 CO sensor

    # GP20U7 — Adafruit breakout (MediaTek GPS — label as generic)
    "gp20u7": "Generic",            # GP20U7 GPS module (MediaTek chipset)

    # SC03 — Winsen electrochemical
    "sc03": "Winsen",               # SC03 C2H5OH electrochemical ethanol sensor

    # SP3S — Winsen (SP3S-AQ2 gas sensor)
    "sp3s": "Winsen",               # SP3S-AQ2 gas sensor

    # L58Touch — LILYGO (wraps FocalTech IC, but label as product)
    "l58touch": "Generic",          # L58 touch (LILYGO T-Watch, wraps FocalTech)

    # SEN0321 is DFRobot (ozone sensor) — already covered by sen0 prefix
    # SEN0390 is DFRobot (ambient light) — already covered by sen0 prefix

    # Generic/popular modules restored from SKIP_IDS
    "cc1101": "Texas Instruments",     # CC1101 RF transceiver IC
    "pt100": "Generic",               # PT100 RTD element (standard, many manufacturers)
    "fc28": "Generic",                # FC-28 soil moisture module
    "fc37": "Generic",                # FC-37 rain sensor module
    "ky040": "Generic",               # KY-040 rotary encoder module
    "yfs201waterflow": "Generic",     # YF-S201 water flow sensor
    "us100": "Generic",               # US-100 ultrasonic module
    "me007": "Generic",               # ME007 ultrasonic sensor
    "tal220": "Generic",              # TAL220 load cell
    "tal220b": "Generic",             # TAL220B load cell
    "tal221": "Generic",              # TAL221 load cell
    "gl5528": "Generic",              # GL5528 LDR photoresistor
    "ctclamp": "Generic",             # CT clamp current transformer
    "fingerprintgrow": "Generic",     # Grow fingerprint module (R503, R307, etc.)
    "sr04m": "Generic",               # AJ-SR-04M waterproof ultrasonic
    "ms01": "Sonoff",                 # Sonoff MS01 moisture sensor
    "tct40": "Generic",               # TCT40 ultrasonic transducer pair
    "gy26": "Generic",                # GY-26 compass module
    "fsr16x16bnl": "Generic",         # FSR 16x16 force sensing resistor array
    "hscdtd": "Alps Alpine",
    "amc1302": "Texas Instruments",
    "apc1": "ScioSense",
    "aranet": "SAF Tehnika",
    "bq76972": "Texas Instruments",
    "cw2017": "CellWise",
    "ds1603l": "DYP",
    "fsr40": "Interlink Electronics",
    "hwt901b": "WIT Motion",
    "it7259": "ITE Tech",
    "lc26g": "Quectel",
    "max78630": "Analog Devices",
    "mht7042a": "Winsen",
    "mt6826s": "MagnTek",
    "pasco2v01": "Infineon",
    "s3km1110": "Iclegend",
    "sciosenseens17x": "ScioSense",
    "spd1200": "ERDI",
    "st1vafe3bx": "STMicroelectronics",
    "tfmini": "Benewake",
    "xdb401": "XIDIBEI",
    "amg88": "Panasonic",
    "icm536": "TDK",
}

# Name overrides for sensors where the scraped name is bad (too long, includes
# description text, library-specific prefixes, etc.). Applied post-merge.
NAME_OVERRIDES: dict[str, str] = {
    "rfd77402": "RFD77402",               # was "RFD77402 DISTANCE SENSOR - VCSEL TIME OF FLIGHT"
    "ina219": "INA219",                   # was "GyverINA" (Arduino lib name)
    "hmc5883l": "HMC5883L",              # was "HMC5883 Unified"
    "ak9750": "AK9750",                  # was "AK9750 HUMAN PRESENCE"
    "ak9753": "AK9753",                  # AK975X is the library, not this model
    "lidarlightv3hp": "LidarLite v3HP",   # was "LidarLight_v3HP_micropython"
    "mq2": "MQ-2",                       # was "Smoke Sensor - MQ-2"
    "ina237": "INA237",                   # was "INA237 AND INA238"
    "fg3": "FG-3",                       # was "FGSensors FG-3+"
    "ads1292r": "ADS1292R",              # was "ADS1292R ECG AND RESPIRATION"
    "afe4490": "AFE4490",                # was "AFE4490 PPG AND SPO2"
    "iqs5xx": "IQS5XX",                 # was "IQS5XX B000 TRACKPAD"
    "lg290p": "LG290P",                 # was "LG290P QUADBAND RTK GNSS"
    "ltr329": "LTR329",                 # was "LTR329 AND LTR303"
    "max30003": "MAX30003",             # was "MAX30003 ECG AFE"
    "max86150": "MAX86150",             # was "MAX86150 PPG AND ECG IC"
    "um980": "UM980",                   # was "UM980 TRIBAND RTK GNSS"
    "wpi430": "VMA430",                 # was "WPI430 VMA430 GPS"
    "paj7620u2": "PAJ7620U2",           # was "Gesture PAJ7620"
}

# Measures a source's wording adds that the sensor doesn't take. The Arduino library calls the
# BM25S2621 soil probe's moisture reading "soil humidity"; it doesn't measure air humidity.
# DFRobot's BMM150 library (SEN0419) is listed under sound; the BMM150 is a magnetometer.
MEASURE_REMOVALS: dict[str, set[str]] = {
    "bm25s2621": {"humidity"},
    "bmm150": {"sound"},
    "ccs811": {"co2", "humidity", "temperature"},  # estimated CO2; humidity/temp are compensation inputs
    # Calculated eCO2. ESPHome tags its compensation inputs; SparkFun's pressure, humidity and temperature
    # come from the BME280 on its ENS160/BME280 combo board, merged under this IC.
    "ens160": {"co2", "humidity", "pressure", "temperature"},
    "sgp30": {"co2"},  # CO2eq, calculated from ethanol and H2 signals
    # Makers' own terms for a calculated value: "CO2 equivalent" predictions, "does not directly measure CO2"
    "iaqcore": {"co2"},
    "bme680bsec": {"co2"},
    "bme68xbsec2": {"co2"},
    "apc1": {"co2"},
    # "the CO2 value and CH2O value output by the module are the equivalent values of TVOC"
    # (SM300D2 parameter table; ESPHome lists 4.8-5.2V)
    "sm300d2": {"co2"},
    "scd4x": {"gas"},  # a CO2 sensor, not a multi-gas breakout
    # Words in Arduino library text, scraped before the matcher learned them (scrapers/common.py):
    # "low noise" ADCs read as sound, "Iowa Scaled Engineering" as a weighing scale, "PGA/FSR"
    # (full-scale range) as a force-sensing resistor
    "ad7193": {"sound"}, "ad7194": {"sound"}, "ads122c04": {"sound"},
    "mcp3427": {"weight"}, "i2cirsense": {"weight"}, "tla2021": {"force"},
    # MAX32664 hubs read an optical front end and an accelerometer; they measure nothing themselves
    "max32664c": {"acceleration"},
}

# Measures a sensor takes that no source tags. ESPHome lists the PMWCS3 under temperature only;
# Tinovi's probe reads volumetric water content, conductivity (EC, E25) and soil temperature.
# The CY8CMBR3102 is the CapSense touch controller on SparkFun's capacitive soil moisture sensor
# (its library's only product); SparkFun notes it also works as a touch or proximity sensor.
MEASURE_ADDITIONS: dict[str, set[str]] = {
    "sen55": {"particulate"},  # Sensirion SEN5x datasheet v2 p.4; source omits this output.
    "ccs811": {"eco2", "voc"},
    "ens160": {"eco2", "voc"},
    "ens161": {"eco2"},
    "sciosenseens16x": {"eco2", "voc"},
    "sgp30": {"eco2", "voc"},
    "iaqcore": {"eco2", "voc"},
    "bme680bsec": {"eco2", "voc"},
    "bme68xbsec2": {"eco2", "voc"},
    "apc1": {"eco2", "voc"},
    "sm300d2": {"eco2", "voc"},
    # General-purpose ADCs measure a voltage; what a library connects to them is the library's
    "ad7194": {"voltage"}, "ads122c04": {"voltage"}, "mcp3427": {"voltage"}, "tla2021": {"voltage"},
    "adc128d818": {"voltage"}, "ads1258": {"voltage"},
    "max32664c": {"biometric"},
    "pmwcs3": {"soil_moisture", "conductivity"},
    "cy8cmbr3102": {"touch"},
}


def type_implied_measures(sensor_type: str | None, measures: set[str]) -> set[str]:
    """Measures a sensing technology implies for the part's own readings.

    A thermopile reporting a temperature reads it from the target's infrared radiation, so it is a
    non-contact (ir_temperature) sensor, as MLX90614 and the Grid-EYE arrays are tagged: TI's
    TMP006/TMP007 "measure the temperature of an object without having to be in direct contact".
    Thermopile air-velocity sensors (FS3000) report no temperature and get nothing.
    """
    if sensor_type == "thermopile" and "temperature" in measures:
        return {"ir_temperature"}
    return set()

# Description overrides for sensors where no source provides a useful description.
# Applied post-merge ONLY when the sensor still has no description (or a very short one).
# Keep descriptions concise, search-friendly, and under 200 chars.
# Format: {sensor_id: "description"}
DESCRIPTION_OVERRIDES: dict[str, str] = {
    # Maker datasheets: https://www.st.com/resource/en/datasheet/lsm6dsox.pdf
    "lsm6dsox": "ST LSM6DSOX 6-axis MEMS accelerometer and gyroscope with machine learning core and embedded temperature sensor",
    # https://www.renesas.com/en/document/dst/fs3000-datasheet
    "fs3000": "FS3000 thermopile air-velocity sensor family; FS3000-1005 and FS3000-1015 have different measurement ranges",
    # https://sensirion.com/media/documents/48C4B7FB/64C134E7/Sensirion_SCD4x_Datasheet.pdf
    "scd41": "Sensirion SCD41 photoacoustic CO2 sensor with integrated temperature and humidity sensing",
    # ── Multi-platform sensors (platform_count >= 2) ─────────────────────────
    "ads1115010v": "ADS1115 16-bit ADC configured for 0-10V analog input measurement",
    "mics4514": "Dual-element gas sensor for CO and NO2 detection with separate reducing and oxidizing channels",
    "icg20660l": "6-axis IMU with 3-axis accelerometer and 3-axis gyroscope, I2C/SPI interface",
    "tmf8x01": "Time-of-flight distance sensor with multi-zone ranging and histogram output",
    "urm09": "Ultrasonic distance sensor module with I2C and analog output, 2cm-500cm range",

    # ── Energy metering ICs (ESPHome-only) ───────────────────────────────────
    "ade7880": "Polyphase energy metering IC for 3-phase power measurement with harmonic analysis",
    "atm90e32": "3-phase energy metering IC with voltage, current, and power measurement",
    "bl0906": "6-channel single-phase energy metering IC for multi-load power monitoring",
    "bl0939": "Single-phase energy metering IC with dual-channel current measurement",
    "cs5460a": "Single-phase bidirectional energy metering IC with active/reactive power measurement",
    "cse7761": "Dual-channel energy metering IC with voltage, current, and power measurement",
    "cse7766": "Single-channel energy metering IC with voltage, current, and power measurement",
    "ctclamp": "Current transformer clamp sensor for non-invasive AC current measurement",
    "sungtil2": "Grid-tie inverter limiter for solar energy monitoring and power export control",

    # ── Temperature & humidity sensors ───────────────────────────────────────
    "aht10": "Digital temperature and humidity sensor with I2C interface, low power consumption",
    "bh1900nux": "Digital temperature sensor with I2C interface and high accuracy",
    "hte501": "Digital temperature and humidity sensor module with calibrated output",
    "hyt271": "Capacitive humidity and temperature sensor with I2C interface, high accuracy",
    "lm75b": "Digital temperature sensor with I2C interface and thermal watchdog",
    "tee501": "High-accuracy digital temperature sensor element with I2C interface",
    "tem3200": "MEMS thermal flow sensor for gas flow measurement",
    "wts01": "Waterproof temperature sensor with digital output",
    "xiaomilywsd02mmc": "Xiaomi LYWSD02MMC BLE temperature and humidity sensor with E-ink display",
    "xiaomixmwsdj04mmc": "Xiaomi XMWSDJ04MMC BLE temperature and humidity sensor",

    # ── Pressure sensors ─────────────────────────────────────────────────────
    "lps22": "MEMS barometric pressure sensor with I2C/SPI interface, high resolution",
    "qmp6988": "Barometric pressure sensor with I2C interface, low power consumption",
    "honeywellabp": "Honeywell ABP series amplified basic pressure sensor with I2C/SPI output",
    "honeywellabp2": "Honeywell ABP2 series amplified pressure sensor with I2C/SPI, improved accuracy",
    "honeywellhih": "Honeywell HIH series relative humidity and temperature sensor with I2C output",
    "npi19": "Ceramic piezoresistive pressure sensor with analog output for industrial applications",
    "xgzp68xx": "Piezoresistive pressure sensor with I2C interface for differential/gauge measurement",

    # ── Light sensors ────────────────────────────────────────────────────────
    "ltr501": "Ambient light and proximity sensor with I2C interface, ALS and PS in one package",
    "ltralsps": "Lite-On ambient light and proximity sensor with I2C digital output",
    "veml3235": "Ambient light sensor with I2C interface, high sensitivity and wide dynamic range",

    # ── Gas & air quality sensors ────────────────────────────────────────────
    "bme680bsec": "BME680 environmental sensor with Bosch BSEC library for IAQ index calculation",
    "bme68xbsec2": "BME68x environmental sensor with Bosch BSEC2 library for gas detection and IAQ",
    "cm1106": "NDIR CO2 sensor module with UART/PWM output, single-beam infrared",
    "pm1006": "Laser-scattering particulate matter sensor for PM2.5 detection",
    "pm2005": "Laser-scattering particulate matter sensor with PM1.0/PM2.5/PM10 output",
    "pmsx003": "Plantower laser-scattering particulate matter sensor for PM1.0/PM2.5/PM10",
    "sen0321": "Electrochemical ozone sensor module with I2C output for O3 concentration",
    "senseair": "Senseair NDIR CO2 sensor module for indoor air quality monitoring",
    "sfa30": "Sensirion formaldehyde sensor with temperature and humidity compensation",
    "sgp4x": "Sensirion multi-gas sensor for VOC and NOx index with I2C interface",
    "sm300d2": "7-in-1 air quality module (UART and RS485): TVOC, eCO2 and eCH2O calculated from TVOC, laser PM2.5/PM10, temperature, humidity",
    "t6615": "NDIR CO2 sensor module with UART output for HVAC and indoor air quality",
    "zyaura": "CO2, temperature, and humidity sensor module with USB output for monitoring",

    # ── Distance & ranging sensors ───────────────────────────────────────────
    "hrxlmaxsonarwr": "MaxBotix HRXL MaxSonar WR ultrasonic rangefinder, weather-resistant, RS232/analog",
    "jsnsr04t": "Waterproof ultrasonic distance sensor module with UART trigger, 25cm-450cm range",
    "tof10120": "Time-of-flight laser distance sensor with UART/I2C, 10-180cm range",
    "rd03d": "24GHz radar distance sensor module for presence detection and ranging",

    # ── Current & voltage measurement ────────────────────────────────────────
    "ads1118": "16-bit delta-sigma ADC with internal temperature sensor and SPI interface",
    "ina2xx": "Texas Instruments INA2xx series high/low-side current and power monitor with I2C",
    "max9611": "High-side current-sense amplifier with 12-bit ADC and I2C interface",
    "dalybms": "DALY BMS battery management system with UART interface for cell monitoring",
    "lc709203f": "Smart LiPo battery fuel gauge IC with I2C interface and coulomb counting",

    # ── Motion & presence sensors ────────────────────────────────────────────
    "mr24hpc1": "24GHz mmWave radar module for human presence and motion detection",
    "msa3xx": "MEMSIC 3-axis accelerometer with I2C interface, low power consumption",
    "hlkfm22x": "Hi-Link 24GHz radar module for presence detection and ranging",
    "glr01": "Gesture and light recognition sensor module",
    "sen21231": "Person detection sensor with machine learning for face counting and tracking",

    # ── Analog multiplexer / ADC ─────────────────────────────────────────────
    "cd74hc4067": "16-channel analog multiplexer/demultiplexer for sensor input expansion",

    # ── Soil & water sensors ─────────────────────────────────────────────────
    "pmwcs3": "Capacitive soil moisture sensor with I2C interface, temperature-compensated",
    "smt100": "Soil moisture and temperature sensor with SDI-12/RS485 interface",
    "ufireec": "Electrical conductivity sensor interface for water quality monitoring",
    "ufireise": "Ion-selective electrode interface for pH and ORP water quality measurement",

    # ── Biometric sensors ────────────────────────────────────────────────────
    "fingerprintgrow": "Optical fingerprint sensor module with UART interface for identification",
    "kmeteriso": "Isolated K-type thermocouple temperature measurement module with I2C",

    # ── Miscellaneous sensors ────────────────────────────────────────────────
    "hc8": "HC-8 series sensor module for environmental monitoring",
    "hydreonrgxx": "Hydreon optical rain sensor for rainfall detection and intensity measurement",

    # ── Thermal imaging ──────────────────────────────────────────────────────
    "mlx90621": "16x4 pixel far-infrared thermal sensor array for contactless temperature measurement",

    # ── DFRobot product sensors ──────────────────────────────────────────────
    "sen0161": "Analog pH sensor module for water quality measurement",

    # ── SparkFun / breakout-only sensors (platform_count = 0) ────────────────
    "at407": "Tilt sensor switch for angle and orientation detection",
    "at42qt1010": "Single-key capacitive touch sensor IC with auto-calibration",
    "at42qt1011": "Single-key capacitive touch sensor IC with proximity detection mode",
    "gp2y0a41sk0f": "Sharp infrared proximity sensor, 4-30cm range, analog output",
    "max31820": "1-Wire ambient temperature sensor, DS18B20-compatible, -55C to +125C",
    "mpl115a1": "MEMS absolute barometric pressure sensor with SPI interface",
    "tal220": "Straight bar load cell for weight measurement, strain gauge type",
    "tas501": "S-type load cell for weight measurement, high capacity",
    "tas606": "Disc-shaped load cell for weight measurement, compact form factor",
    "ags01db": "TVOC gas sensor with I2C interface for indoor air quality detection",

    # ── Sensors with descriptions cleaned to bare IC names or too short ──────
    "gsl1680": "Capacitive multi-touch screen controller with I2C interface",
    "hp03s": "Barometric pressure and temperature sensor module with calibrated output",
    "ads111x": "16-bit delta-sigma ADC with programmable gain amplifier and I2C interface",
    "urm07": "Ultrasonic distance sensor module with RS485 interface, long range",
    "sen0153": "Ultrasonic distance sensor module for liquid level measurement",
    "sen0575": "Optical rain sensor module for rainfall detection",
}


def fix_names(merged: dict[str, dict], quiet: bool = False) -> int:
    """Apply NAME_OVERRIDES to fix bad sensor names. Always overrides."""
    fixed = 0
    for sid, name in NAME_OVERRIDES.items():
        if sid in merged:
            merged[sid]["name"] = name
            fixed += 1
    if not quiet:
        print(f"  Applied {fixed} name overrides")
    return fixed


def enrich_descriptions(merged: dict[str, dict], quiet: bool = False) -> int:
    """Fill in descriptions from DESCRIPTION_OVERRIDES where currently empty or poor.

    Applied post-merge. Replaces description when:
    - Missing or empty, OR
    - Existing description is very short (< 20 chars) and the override is longer
      (short descriptions like "A range sensor" carry little search value)

    Never overrides meaningful existing descriptions (>= 20 chars).

    Returns the number of sensors enriched.
    """
    enriched = 0
    for sid, sensor in merged.items():
        if sid not in DESCRIPTION_OVERRIDES:
            continue
        current = (sensor.get("description") or "").strip()
        override = DESCRIPTION_OVERRIDES[sid]
        # Correct known component/family contamination; otherwise fill only missing or short prose.
        if sid in {"lsm6dsox", "fs3000", "scd41"} or not current or (len(current) < 20 and len(override) > len(current)):
            sensor["description"] = override
            enriched += 1

    if not quiet:
        # Report remaining gaps
        still_missing = sum(
            1 for s in merged.values()
            if not (s.get("description") or "").strip()
        )
        total = len(merged)
        covered = total - still_missing
        pct = (covered / total * 100) if total else 0
        print(f"  Applied {enriched} description overrides")
        print(f"  Description coverage: {covered}/{total} ({pct:.1f}%)")

    return enriched


def enrich_manufacturers(merged: dict[str, dict], quiet: bool = False) -> int:
    """Fill in manufacturer from IC prefix lookup where currently NULL.

    Only sets manufacturer when it's missing — never overrides existing data.
    Matches longest prefix first to avoid false positives.

    Returns the number of sensors enriched.
    """
    # Sort prefixes longest-first for greedy matching
    sorted_prefixes = sorted(IC_PREFIX_MANUFACTURERS.keys(), key=len, reverse=True)

    enriched = 0
    for sid, sensor in merged.items():
        if sensor["manufacturer"] is not None:
            continue

        for prefix in sorted_prefixes:
            if sid.startswith(prefix):
                manufacturer = IC_PREFIX_MANUFACTURERS[prefix]
                sensor["manufacturer"] = manufacturer
                enriched += 1
                break

    if not quiet:
        print(f"  Enriched {enriched} sensors via IC prefix lookup")

    return enriched


# ---------------------------------------------------------------------------
# Type enrichment: infer sensing technology from measures and descriptions
# ---------------------------------------------------------------------------

# Stage 1: Measure-pattern inference
# Maps frozenset of measures that MUST be present -> inferred type.
# Checked via superset: if sensor measures >= key, type is assigned.
MEASURE_TYPE_INFERENCE = {
    # Ultrasonic distance sensors
    frozenset({"distance", "ultrasonic"}): "ultrasonic",
    frozenset({"flow", "ultrasonic"}): "ultrasonic",
    # Time-of-flight / LiDAR distance sensors
    frozenset({"distance", "lidar"}): "tof",
    frozenset({"distance", "tof"}): "tof",
    # Thermopile IR temperature sensors
    frozenset({"ir_temperature"}): "thermopile",
    # PIR motion sensors
    frozenset({"motion", "pir"}): "pir",
    # Radar motion/presence sensors
    frozenset({"motion", "radar"}): "radar",
    frozenset({"proximity", "radar"}): "radar",
    frozenset({"distance", "radar"}): "radar",
    # Touch sensors
    frozenset({"touch"}): "capacitive",
    # ORP / pH / conductivity / dissolved_oxygen — electrochemical probes
    frozenset({"orp"}): "electrochemical",
    frozenset({"ph"}): "electrochemical",
    frozenset({"conductivity"}): "electrochemical",
    frozenset({"dissolved_oxygen"}): "electrochemical",
}

# Stage 2: Description keyword inference (case-insensitive).
# Only applied when type is still NULL after stage 1.
# Order matters for priority: first match wins.
TYPE_KEYWORDS = [
    ("tof", ["time-of-flight", "time of flight", " tof "]),
    ("ultrasonic", ["ultrasonic"]),
    ("ndir", ["ndir", "non-dispersive infrared", "non dispersive infrared"]),
    ("radar", ["radar", "mmwave", "millimeter-wave", "millimeter wave", "24ghz", "60ghz", "77ghz"]),
    ("thermopile", ["thermopile"]),
    ("thermocouple", ["thermocouple"]),
    ("pir", ["passive infrared", "pyroelectric infrared", " pir "]),
    ("lidar", ["lidar"]),
    ("mems", ["mems microphone", "mems accelerometer", "mems gyroscope", "mems inertial", "mems imu"]),
    ("capacitive", ["capacitive touch", "capacitive humidity", "capacitive soil",
                     "capacitive sensor", "capacitive keypad"]),
    ("resistive", ["resistive touch"]),
    ("hall_effect", ["hall effect", "hall-effect", "hall sensor"]),
    ("piezoelectric", ["piezoelectric"]),
    ("strain_gauge", ["load cell", "strain gauge", "strain gage"]),
    ("electrochemical", ["electrochemical"]),
    ("catalytic", ["catalytic"]),
    ("semiconductor", ["semiconductor sensor", "metal oxide semiconductor", "metal oxide gas",
                        "bandgap temperature", "silicon bandgap"]),
    ("rtd", ["pt100", "pt1000", " rtd "]),
    ("ntc", [" ntc ", "negative temperature coefficient"]),
    ("photoacoustic", ["photoacoustic"]),
    ("shunt", ["current shunt", "shunt-based", "shunt based"]),
    ("adc", ["analog-to-digital", "analog to digital", " adc "]),
]

# Stage 3: Well-known IC → type mappings for popular sensors where
# measure-pattern and keyword inference can't determine the technology.
IC_TYPE_OVERRIDES: dict[str, str | None] = {
    # Split-device identity audit (2026-11-09); details: data/sensors/ic_alias_evidence.json
    "lsm6dsl": "mems",  # https://www.st.com/resource/en/datasheet/lsm6dsl.pdf
    "lsm6dso": "mems",  # https://www.st.com/resource/en/datasheet/lsm6dso.pdf
    "lsm6dsr": "mems",  # https://www.st.com/resource/en/datasheet/lsm6dsr.pdf
    "lsm6dsv16x": "mems",  # https://www.st.com/resource/en/datasheet/lsm6dsv16x.pdf
    "lsm6dsv16bx": "mems",  # https://www.st.com/resource/en/datasheet/lsm6dsv16bx.pdf
    "ism330dhcx": "mems",  # https://www.st.com/resource/en/datasheet/ism330dhcx.pdf
    "lsm6ds3": "mems",  # https://community.st.com/ysqtg83639/attachments/ysqtg83639/stm32-mcu-products-forum/89677/2/%5BATT%5D11987.pdf
    "lsm9ds0": "mems",  # https://www.st.com/resource/en/datasheet/lsm9ds0.pdf
    "mpu6500": "mems",  # https://www.invensense.tdk.com/en-us/products/inertial-sensors/mpu-6500
    "bmi323": "mems",  # https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmi323-ds000.pdf
    "max30100": "optical",  # https://www.analog.com/media/en/technical-documentation/data-sheets/max30100.pdf
    "max30105": "optical",  # https://www.analog.com/media/en/technical-documentation/data-sheets/max30105.pdf
    "ds18s20": "semiconductor",  # https://www.analog.com/media/en/technical-documentation/data-sheets/DS18S20.pdf
    "sht30": "capacitive",  # https://sensirion.com/media/documents/213E6A3B/63A5A569/Datasheet_SHT3x_DIS.pdf
    "sht31": "capacitive",  # https://sensirion.com/media/documents/213E6A3B/63A5A569/Datasheet_SHT3x_DIS.pdf
    "sht31d": "capacitive",  # https://sensirion.com/media/documents/213E6A3B/63A5A569/Datasheet_SHT3x_DIS.pdf
    "sht35": "capacitive",  # https://sensirion.com/media/documents/213E6A3B/63A5A569/Datasheet_SHT3x_DIS.pdf
    "sht40": "capacitive",  # https://sensirion.com/media/documents/33FD6951/6A7C10A0/HT_DS_Datasheet_SHT4x_V7.3.pdf
    "sht45": "capacitive",  # https://sensirion.com/media/documents/33FD6951/6A7C10A0/HT_DS_Datasheet_SHT4x_V7.3.pdf
    "sht21": "capacitive",  # https://sensirion.com/media/documents/120BBE4C/63500094/Sensirion_Datasheet_Humidity_Sensor_SHT21.pdf
    "sht25": "capacitive",  # https://sensirion.com/media/documents/66189A49/6350F979/Sensirion_Datasheet_Humidity_Sensor_SHT25.pdf
    "bme680": "semiconductor",  # https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme680-ds001.pdf
    "bme688": "semiconductor",  # https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme688-ds000.pdf
    "bmp388": "mems",  # https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp388-ds001.pdf
    "bmp390": "mems",  # https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp390-ds002.pdf
    "bmp085": "mems",  # https://cdn.sparkfun.com/assets/6/f/3/9/4/BST-BMP085-DS000-05.pdf
    "scd40": "photoacoustic",  # https://sensirion.com/media/documents/48C4B7FB/64C134E7/Sensirion_SCD4x_Datasheet.pdf
    "scd41": "photoacoustic",  # https://sensirion.com/media/documents/48C4B7FB/64C134E7/Sensirion_SCD4x_Datasheet.pdf
    "hdc1000": "capacitive",  # https://www.ti.com/lit/ds/symlink/hdc1000.pdf
    "hdc1010": "capacitive",  # https://www.ti.com/lit/ds/symlink/hdc1010.pdf
    "opt3001": "photodiode",  # https://www.ti.com/lit/ds/symlink/opt3001.pdf
    "opt3002": "photodiode",  # https://www.ti.com/lit/ds/symlink/opt3002.pdf
    "mhz19b": "ndir",  # https://www.winsen-sensor.com/d/files/manual/mh-z19b.pdf
    "mhz19c": "ndir",  # https://www.winsen-sensor.com/d/files/manual/mh-z19c.pdf
    "mhz19d": "ndir",  # https://www.winsen-sensor.com/d/files/manual/mh-z19d.pdf
    "mhz19e": "ndir",  # https://www.winsen-sensor.com/d/files/manual/mh-z19e.pdf
    "mhz1911a": "ndir",  # https://www.winsen-sensor.com/d/files/manual/mh-z1911a.pdf
    "mhz14a": "ndir",  # https://www.winsen-sensor.com/d/files/manual/mh-z14a.pdf
    "mhz14b": "ndir",  # https://www.winsen-sensor.com/d/files/manual/mh-z14b.pdf
    "zh06ii": "laser",  # https://www.winsen-sensor.com/d/files/manual/zh06-ii.pdf
    "zh06iii": "laser",  # https://www.winsen-sensor.com/d/files/manual/zh06-iii.pdf
    "zh06iv": "laser",  # https://www.winsen-sensor.com/d/files/manual/zh06-iv.pdf
    "ld2410b": "radar",  # https://www.hlktech.net/index.php?id=65
    "ld2410c": "radar",  # https://www.hlktech.net/index.php?id=65
    "tmf8820": "tof",  # https://look.ams-osram.com/m/52236c476132a095/original/TMF882X-DS000693.pdf
    "tmf8821": "tof",  # https://look.ams-osram.com/m/52236c476132a095/original/TMF882X-DS000693.pdf
    "as7262": "photodiode",  # https://look.ams-osram.com/m/663487deeb7089a7/original/AS7262-DS000486.pdf
    "as7263": "photodiode",  # https://look.ams-osram.com/m/2f885f8e1b074032/original/AS7263-DS000476.pdf
    "fs30001005": "thermopile",  # https://www.renesas.com/en/document/dst/fs3000-datasheet
    "fs30001015": "thermopile",  # https://www.renesas.com/en/document/dst/fs3000-datasheet
    "ms580314ba": "mems",  # https://www.te.com/en/product-MS580314BA01-50.html
    "tfminiplus": "tof",  # https://en.benewake.com/TFminiPlus/index.html
    "sen54": None,  # https://sensirion.com/media/documents/6791EFA0/62A1F68F/Sensirion_Datasheet_Environmental_Node_SEN5x.pdf
    "sen55": None,  # https://sensirion.com/media/documents/6791EFA0/62A1F68F/Sensirion_Datasheet_Environmental_Node_SEN5x.pdf
    "amg8833": "thermopile",  # https://industrial.panasonic.com/ww/products/pt/grid-eye/models/AMG8833
    "fabo206uvsi1132": "photodiode",  # https://www.silabs.com/documents/public/data-sheets/Si1132.pdf
    "am2301": "capacitive",  # Identity audit: technology unverified; do not infer a sibling's type.
    "htu21d": "capacitive",  # Identity audit: technology unverified; do not infer a sibling's type.
    "bno08xrvc": None,  # Identity audit: technology unverified; do not infer a sibling's type.
    "max3010x": None,  # Identity audit: technology unverified; do not infer a sibling's type.
    "mq3": None,  # Identity audit: technology unverified; do not infer a sibling's type.
    "mq7": None,  # Identity audit: technology unverified; do not infer a sibling's type.
    "tfmini": None,  # Identity audit: technology unverified; do not infer a sibling's type.
    "amg88": None,  # Identity audit: technology unverified; do not infer a sibling's type.
    "as7262x": None,  # Identity audit: technology unverified; do not infer a sibling's type.
    "kx134": "mems",  # Identity audit: technology unverified; do not infer a sibling's type.
    "mq2lpg": None,  # Identity audit: technology unverified; do not infer a sibling's type.
    "mq2b": "semiconductor",  # Identity audit: technology unverified; do not infer a sibling's type.
    "sen0032": None,  # Identity audit: technology unverified; do not infer a sibling's type.
    "sen0140": None,  # Identity audit: technology unverified; do not infer a sibling's type.
    "sen0430": None,  # Identity audit: technology unverified; do not infer a sibling's type.
    "sen0610": None,  # Identity audit: technology unverified; do not infer a sibling's type.
    "sen0456": None,  # Identity audit: technology unverified; do not infer a sibling's type.
    "microfiresht3x": None,  # Identity audit: technology unverified; do not infer a sibling's type.
    "myld2410": None,  # Identity audit: technology unverified; do not infer a sibling's type.
    "pygp2y": "photodiode",  # Identity audit: technology unverified; do not infer a sibling's type.
    "si1142": None,  # Identity audit: technology unverified; do not infer a sibling's type.
    # ── MOX (metal oxide semiconductor) gas sensors ───────────────────
    "ccs811": "semiconductor",
    "ens160": "semiconductor",
    "ens161": "semiconductor",
    "sgp30": "semiconductor",
    "sgp40": "semiconductor",
    "sgp41": "semiconductor",
    "bme68x": "semiconductor",
    "ags02ma": "semiconductor",
    "ags10": "semiconductor",
    "mics4514": "semiconductor",
    "mics6814": "semiconductor",
    "ags01db": "semiconductor",
    "ags2616": "semiconductor",
    "ags3870": "semiconductor",
    "ags3871": "semiconductor",
    "iaqcore": "semiconductor",
    "sciosenseens16x": "semiconductor",
    "bme680bsec": "semiconductor",
    "bme68xbsec2": "semiconductor",
    "sgp4x": "semiconductor",
    "lmp91000": "semiconductor",
    "sen0321": "semiconductor",
    "sen0560": "semiconductor",
    "sp3s": "semiconductor",
    "mg811": "semiconductor",
    "mhz9041a": "semiconductor",
    "mp4": "semiconductor",
    "mp7": "semiconductor",
    "mpn5": "semiconductor",
    "zh101": "semiconductor",
    "zh401": "semiconductor",
    "zi100zi101": "semiconductor",
    "zl940v3c": "semiconductor",
    "zmod4450": "semiconductor",
    "zph07": "semiconductor",
    "zs03": "semiconductor",
    "zs0301": "semiconductor",
    "zs05": "semiconductor",
    "zwc102": "semiconductor",
    "zwhc101": "semiconductor",
    "cbhchov4": "semiconductor",
    "gm1602": "semiconductor",
    "sm300d2": "semiconductor",
    "sen6x": "semiconductor",
    "bm22s3021": "semiconductor",
    "bm22s3421": "semiconductor",
    "bm25s3421": "semiconductor",
    # ── Semiconductor temperature sensors (bandgap / CMOS) ────────────
    "mcp9808": "semiconductor",
    "stts22h": "semiconductor",
    "tmp117": "semiconductor",
    "adt7410": "semiconductor",
    "as6212": "semiconductor",
    "as6221": "semiconductor",
    "ds18b20": "semiconductor",
    "lm75": "semiconductor",
    "pct2075": "semiconductor",
    "tc74": "semiconductor",
    "tmp102": "semiconductor",
    "tmp1075": "semiconductor",
    "sts3x": "semiconductor",
    "sts4x": "semiconductor",
    "mts4x": "semiconductor",
    "si7055": "semiconductor",
    "stts751": "semiconductor",
    "emc2101": "semiconductor",
    "ds18x20": "semiconductor",
    "lm75a": "semiconductor",
    "mcp9700": "semiconductor",
    "ds1624": "semiconductor",
    "lm75b": "semiconductor",
    "adt7310": "semiconductor",
    "adt7420": "semiconductor",
    "adstds75lm75": "semiconductor",
    "adltc2990": "semiconductor",
    "mcp9701": "semiconductor",
    "mcp970x": "semiconductor",
    "mcp9800": "semiconductor",
    "mcp9802": "semiconductor",
    "ds1621": "semiconductor",
    "ds1821": "semiconductor",
    "ds7505": "semiconductor",
    "ds3231": "semiconductor",
    "max30205": "semiconductor",
    "max30210": "semiconductor",
    "max31820": "semiconductor",
    "max31875": "semiconductor",
    "max6605mxk": "semiconductor",
    "max6605mxkv": "semiconductor",
    "max6607ixk": "semiconductor",
    "max6613mxk": "semiconductor",
    "max6626": "semiconductor",
    "lm335a": "semiconductor",
    "lm35": "semiconductor",
    "lm35c": "semiconductor",
    "lm35d": "semiconductor",
    "lm45b": "semiconductor",
    "lm50b": "semiconductor",
    "lm50c": "semiconductor",
    "lm73": "semiconductor",
    "lm95234": "semiconductor",
    "lmt01": "semiconductor",
    "tmp108": "semiconductor",
    "tmp112": "semiconductor",
    "tmp114": "semiconductor",
    "tmp116": "semiconductor",
    "tmp11x": "semiconductor",
    "tmp126": "semiconductor",
    "tmp36": "semiconductor",
    "tmp435": "semiconductor",
    "tmp61": "semiconductor",
    "tmp9a00": "semiconductor",
    "si7051": "semiconductor",
    "si705x": "semiconductor",
    "si7060": "semiconductor",
    "nst1001": "semiconductor",
    "s5851a": "semiconductor",
    "f75303": "semiconductor",
    "nct75": "semiconductor",
    "bh1900nux": "semiconductor",
    "bd1020hfv": "semiconductor",
    "stlm20dd9f": "semiconductor",
    "stlm20w87f": "semiconductor",
    "tc1046": "semiconductor",
    "tc1047": "semiconductor",
    "tcn75a": "semiconductor",
    "tee501": "semiconductor",
    "tsicxx6": "semiconductor",
    "tsys01": "semiconductor",
    "p3t1755": "semiconductor",
    "tem3200": "semiconductor",
    "jc424": "semiconductor",
    "kmeteriso": "semiconductor",
    "rv3032": "semiconductor",
    "sb041": "semiconductor",
    "wts01": "semiconductor",
    "tx07k": "semiconductor",
    "ad22100a": "semiconductor",
    "ad22100k": "semiconductor",
    "ad22100s": "semiconductor",
    "ad22103k": "semiconductor",
    "bq27220": "semiconductor",
    "ct1780": "semiconductor",
    "max17043": "semiconductor",
    "max17055": "semiconductor",
    "lc709203f": "semiconductor",
    "tad2144": "semiconductor",
    "yds13": "semiconductor",
    "wsentids": "semiconductor",
    "pmwcs3": "semiconductor",
    "ad8232": "semiconductor",
    "gdk101": "semiconductor",
    "ggreg20v3": "semiconductor",
    # ── Thermopile sensors ────────────────────────────────────────────
    "tmp007": "thermopile",
    "i2cirsense": "thermopile",
    # ── Capacitive humidity+temperature sensors ───────────────────────
    "sht3x": "capacitive",
    "sht4x": "capacitive",
    "hdc1080": "capacitive",
    "hdc302x": "capacitive",
    "hts221": "capacitive",
    "htu21df": "capacitive",
    "si7021": "capacitive",
    "aht20": "capacitive",
    "am2320": "capacitive",
    "ens210": "capacitive",
    "hs300x": "capacitive",
    "dht12": "capacitive",
    "sht20": "capacitive",
    "dht": "capacitive",
    "dht11": "capacitive",
    "dht20": "capacitive",
    "dht21": "capacitive",
    "dht22": "capacitive",
    "hdc2010": "capacitive",
    "htu31d": "capacitive",
    "shtc3": "capacitive",
    "ahtx0": "capacitive",
    "am2301b": "capacitive",
    "am2315c": "capacitive",
    "hdc2080": "capacitive",
    "sht85": "capacitive",
    "shtcx": "capacitive",
    "th02": "capacitive",
    "aht10": "capacitive",
    "aht1x": "capacitive",
    "aht2x": "capacitive",
    "am2315": "capacitive",
    "am2321": "capacitive",
    "hdc1008": "capacitive",
    "hdc10xx": "capacitive",
    "hdc2021": "capacitive",
    "hdc2022": "capacitive",
    "hdc3020": "capacitive",
    "hdc3022": "capacitive",
    "hs3003": "capacitive",
    "hs400x": "capacitive",
    "hte501": "capacitive",
    "htu21": "capacitive",
    "hyt271": "capacitive",
    "sht3xd": "capacitive",
    "sht11": "capacitive",
    "sht1x": "capacitive",
    "si7005": "capacitive",
    "si7006": "capacitive",
    "si7013": "capacitive",
    "si70xx": "capacitive",
    "cht8305": "capacitive",
    "cht8310": "capacitive",
    "cht832x": "capacitive",
    "hih61xx": "capacitive",
    "honeywellhih": "capacitive",
    "sciosenseens21x": "capacitive",
    "ms8607": "capacitive",
    "wsenhids": "capacitive",
    "msz202": "capacitive",
    "msz302": "capacitive",
    "somo1elv": "capacitive",
    "xiaomilywsd02mmc": "capacitive",
    "xiaomixmwsdj04mmc": "capacitive",
    "tfa433receiver": "capacitive",
    "sfa30": "capacitive",
    "sfa40": "capacitive",
    # ── MEMS accelerometers / gyroscopes / IMUs ───────────────────────
    "mpu6050": "mems",
    "mpu9250": "mems",
    "mpu6886": "mems",
    "bmi160": "mems",
    "bmi270": "mems",
    "bno055": "mems",
    "bno08x": "mems",
    "lsm6dsox": "mems",
    "lsm9ds1": "mems",
    "lis3dh": "mems",
    "lis2dh12": "mems",
    "lis2mdl": "mems",
    "lis3mdl": "mems",
    "adxl345": "mems",
    "adxl343": "mems",
    "icm20948": "mems",
    "icm42688": "mems",
    "ism330dlc": "mems",
    "kx132": "mems",
    "mma8451": "mems",
    "fxos8700": "mems",
    "lis2dw12": "mems",
    "msa301": "mems",
    "adxl362": "mems",
    "adxl372": "mems",
    "bma400": "mems",
    "bmx160": "mems",
    "icg20660l": "mems",
    "icm42605": "mems",
    "icm45605": "mems",
    "icm45686": "mems",
    "iis2dlpc": "mems",
    "iis2mdc": "mems",
    "ism6hg256x": "mems",
    "itg3200": "mems",
    "lis2du12": "mems",
    "lis2duxs12": "mems",
    "lis2hh12": "mems",
    "lis331": "mems",
    "lsm303": "mems",
    "lsm303agr": "mems",
    "lsm6ds0": "mems",
    "lsm6dso16is": "mems",
    "mma8452q": "mems",
    "adis16470": "mems",
    "adxl313": "mems",
    "adxl335": "mems",
    "adxl34x": "mems",
    "adxl355": "mems",
    "adxl366": "mems",
    "adxl367": "mems",
    "adxl375": "mems",
    "adxl37x": "mems",
    "asm330lhh": "mems",
    "bma220": "mems",
    "bma280": "mems",
    "bma423": "mems",
    "bma4xx": "mems",
    "bmc150": "mems",
    "bmg160": "mems",
    "bmi085": "mems",
    "bmi088": "mems",
    "bmi08x": "mems",
    "bmi270bmm150": "mems",
    "bms56m206a": "mems",
    "bmx055": "mems",
    "bno080": "mems",
    "fxas210002c": "mems",
    "fxas21002": "mems",
    "fxas21002c": "mems",
    "fxls8974": "mems",
    "h3lis200dl": "mems",
    "h3lis331dl": "mems",
    "hg4930": "mems",
    "icg20660": "mems",
    "icm20689": "mems",
    "icm20x": "mems",
    "icm42670p": "mems",
    "icm42670s": "mems",
    "icm42686": "mems",
    "icm45605s": "mems",
    "icm45608": "mems",
    "icm45686s": "mems",
    "icm45688p": "mems",
    "icm45689": "mems",
    "iis2dh": "mems",
    "iis2dulpx": "mems",
    "iis2iclx": "mems",
    "iis328dq": "mems",
    "iis3dhhc": "mems",
    "iis3dwb": "mems",
    "ism330is": "mems",
    "kx023": "mems",
    "kxtj3": "mems",
    "l3g": "mems",
    "l3gd20": "mems",
    "l3gd20u": "mems",
    "lis2de12": "mems",
    "lis2dh": "mems",
    "lis2ds12": "mems",
    "lis2dux12": "mems",
    "lsm303accel": "mems",
    "lsm303c": "mems",
    "lsm303dlh": "mems",
    "lsm303dlhc": "mems",
    "lsm6": "mems",
    "lsm6ds3tr": "mems",
    "lsm6dsm": "mems",
    "lsm6dso32": "mems",
    "lsm6dsv320x": "mems",
    "lsm6dsv32x": "mems",
    "lsm6dsv80x": "mems",
    "lsm9ds0mfd": "mems",
    "lsm9ds1tr": "mems",
    "mc3419": "mems",
    "mc3479": "mems",
    "mma7455": "mems",
    "mma7660": "mems",
    "mma8453q": "mems",
    "mma8652": "mems",
    "mma8653": "mems",
    "mpu6000": "mems",
    "mpu9x50": "mems",
    "msa3xx": "mems",
    "qmi8658": "mems",
    "qmi8658c": "mems",
    "sca100t": "mems",
    "scl3300": "mems",
    "scl3400": "mems",
    "wsenisds": "mems",
    "wsenitds": "mems",
    "wt61pc": "mems",
    "ximu3": "mems",
    "gy512": "mems",
    "gy521": "mems",
    "imu9dof": "mems",
    "sen10724": "mems",
    "rak12034": "mems",
    "7semibno08x": "mems",
    "im19": "mems",
    "at407": "mems",
    # ── MEMS barometric pressure sensors ──────────────────────────────
    "bme280": "mems",
    "bmp280": "mems",
    "bmp180": "mems",
    "bmp3xx": "mems",
    "bmp581": "mems",
    "dps310": "mems",
    "lps22hb": "mems",
    "lps22hh": "mems",
    "ms5611": "mems",
    "ms5637": "mems",
    "ms5803": "mems",
    "mpl3115a2": "mems",
    "icp10111": "mems",
    "spl06001": "mems",
    "mpl115a2": "mems",
    "bmp58x": "mems",
    "ilps22qs": "mems",
    "lps22df": "mems",
    "lps25hb": "mems",
    "lps28dfw": "mems",
    "lps35hw": "mems",
    "ms5837": "mems",
    "spa06003": "mems",
    "spa06": "mems",
    "spl06": "mems",
    "spl07": "mems",
    "qmp6988": "mems",
    "hp303b": "mems",
    "hp03s": "mems",
    "hp206c": "mems",
    "barometerhp20x": "mems",
    "bmp384": "mems",
    "bmp580": "mems",
    "bmp585": "mems",
    "bmp5xx": "mems",
    "bme690": "mems",
    "icp10100": "mems",
    "icp10125": "mems",
    "icp101xx": "mems",
    "icp20100": "mems",
    "icp201xx": "mems",
    "lps22": "mems",
    "lps25h": "mems",
    "lps28": "mems",
    "lps2x": "mems",
    "mpbmp3xxfull": "mems",
    "ms4525do": "mems",
    "ms5607": "mems",
    "ms5xxx": "mems",
    "sdp3x": "mems",
    "sdp31": "mems",
    "t5403barometric": "mems",
    "wsenpads": "mems",
    "wsenpdms": "mems",
    "wsenpdus": "mems",
    "xgzp6897d": "mems",
    "xgzp68xx": "mems",
    "ens220": "mems",
    "dct532": "mems",
    "2smpb": "mems",
    "7semico2th": "mems",
    "zpa4756": "mems",
    "mmr902": "mems",
    "d6fph": "mems",
    "omrond6fph": "mems",
    "sm9000": "mems",
    "sen0343": "mems",
    "wf100dpz": "mems",
    "lwlp5000": "mems",
    "honeywellabp": "mems",
    "honeywellabp2": "mems",
    "mprls": "mems",
    "i2casdx": "mems",
    "ams5812": "mems",
    "ams5915": "mems",
    "mpx5700": "mems",
    "mpx5999d": "mems",
    "mpxa4250a": "mems",
    "mpxa6115a": "mems",
    "mpxh6115a": "mems",
    "mpxh6400a": "mems",
    "mpxhz6116a": "mems",
    "mpxhz6250a": "mems",
    "mpl115a1": "mems",
    "pd10lx": "mems",
    "wpah31": "mems",
    "wpak63": "mems",
    "wpak63j": "mems",
    "wpak64": "mems",
    "wpak65": "mems",
    "wpak66": "mems",
    "wpak67": "mems",
    "wpak68": "mems",
    "wpak69": "mems",
    "wpak70": "mems",
    "wpas12": "mems",
    "wpbh01": "mems",
    "wpch01": "mems",
    "wpch04": "mems",
    "wpck03": "mems",
    "wpck05": "mems",
    "wpck07": "mems",
    "wpck08": "mems",
    "wpck62": "mems",
    "wpck81": "mems",
    "wpck89": "mems",
    "msp300": "mems",
    "npi19": "mems",
    # ── MEMS microphones / sound / flow / tilt ────────────────────────
    "inmp441": "mems",
    "imp34dt05": "mems",
    "ics40619": "mems",
    "mp23db01hp": "mems",
    "msm261": "mems",
    "icu10201": "mems",
    "i2s": "mems",
    "dnmsi2c": "mems",
    "ch101": "mems",
    "sfm3200": "mems",
    "pav3000": "mems",
    "bm62s2301": "mems",
    # ── RTD interfaces / probes ───────────────────────────────────────
    "max31865": "rtd",
    "pt100": "rtd",
    "pt1000probe": "rtd",
    "rtdoem": "rtd",
    "surveyorrtd": "rtd",
    # ── Thermocouple interfaces ───────────────────────────────────────
    "max31850": "thermocouple",
    # ── Photoacoustic CO2 ─────────────────────────────────────────────
    "scd4x": "photoacoustic",
    # ── Magnetometers and rotary encoders (Hall, AMR/TMR, fluxgate, capacitive) ─
    "as5600": "hall_effect",
    "mlx90393": "hall_effect",
    "bmm150": "hall_effect",
    "qmc5883l": "magnetoresistive",
    "hmc5883l": "magnetoresistive",
    "bmm350": "magnetoresistive",
    "mmc5603": "magnetoresistive",
    "mmc56x3": "magnetoresistive",
    "mmc5983": "magnetoresistive",
    "mmc5983ma": "magnetoresistive",
    "mmc5603nj": "magnetoresistive",
    "mmc34160pj": "magnetoresistive",
    "qmc5883": "magnetoresistive",
    "qmc5583l": "hall_effect",
    "qmc5883p": "magnetoresistive",
    "rm3100": "magneto_inductive",
    "ak8975": "hall_effect",
    "akm09918c": "hall_effect",
    "hmc6343": "magnetoresistive",
    "hmc6352": "magnetoresistive",
    "ist8310": "magnetoresistive",
    "tlv493d": "hall_effect",
    "mlx90377": "hall_effect",
    "mlx90392": "hall_effect",
    "mlx90394": "hall_effect",
    "mlx90395": "hall_effect",
    "as5040": "hall_effect",
    "as5047p": "hall_effect",
    "as5048": "hall_effect",
    "as5200l": "hall_effect",
    "as5600l": "hall_effect",
    "am4096": "hall_effect",
    "mt6701": "hall_effect",
    "gy26": "magnetoresistive",
    "fg3": "fluxgate",
    "hscdtd008a": None,  # Alps names no technology; it is not stated to be Hall
    "lsm303dlhmag": "hall_effect",
    "lsm9ds1mag": "hall_effect",
    "bm32s2031": "optical",
    "bms36t001": "hall_effect",
    "ad2s1210": "adc",
    "amt25": "capacitive",
    "ky040": "mechanical",
    # ── Shunt / current / power monitor ICs ───────────────────────────
    "ina219": "shunt",
    "ina226": "shunt",
    "ina228": "shunt",
    "ina3221": "shunt",
    "ina260": "shunt",
    "ina237": "shunt",
    "ina219b": "shunt",
    "ina230": "shunt",
    "ina232": "shunt",
    "ina236": "shunt",
    "ina23x": "shunt",
    "ina2xx": "shunt",
    "ina780x": "shunt",
    "ina169": "shunt",
    "isl28022": "shunt",
    "ltc2959": "shunt",
    "max471": "shunt",
    "max9611": "shunt",
    "acs37800": "hall_effect",
    "tli4970": "hall_effect",
    "tli4971": "hall_effect",
    "sct013": "transformer",
    "ctclamp": "transformer",
    "zmpt101b": "transformer",
    "pzem004t": "shunt",
    "p1meter": "shunt",
    "atm90e26": "shunt",
    "atm90e32": "shunt",
    "atm90e32as": "shunt",
    "ade7880": "shunt",
    "ade7953": "shunt",
    "ade7978": "shunt",
    "bl0940": "shunt",
    "bl0942": "shunt",
    "bl0906": "shunt",
    "bl0939": "shunt",
    "hlw8012": "shunt",
    "hlw8032": "shunt",
    "cse7761": "shunt",
    "cse7766": "shunt",
    "cs5460a": "shunt",
    "cs5464": "shunt",
    "cs5490": "shunt",
    "stpm34": "shunt",
    "mcp39f521": "shunt",
    "dalybms": "shunt",
    "sungtil2": "shunt",
    # ── ADC (analog-to-digital converters) ────────────────────────────
    "ads1115": "adc",
    "ads1115010v": "adc",
    "ads1015": "adc",
    "ads1118": "adc",
    "ads111x": "adc",
    "ads1220": "adc",
    "ads1258": "adc",
    "ads1292r": "adc",
    "ads1293": "adc",
    "ad7193": "adc",
    "ad7194": "adc",
    "ad7797": "adc",
    "cd74hc4067": "adc",
    "mcp3427": "adc",
    # ── Strain gauge / load cell ADCs ─────────────────────────────────
    "hx710a": "adc",
    "hx710b": "adc",
    "tal220": "strain_gauge",
    "bmh12m105": "strain_gauge",
    "tas501": "strain_gauge",
    "tas606": "strain_gauge",
    # ── Photodiode light / color / UV / spectral sensors ──────────────
    "bh1750": "photodiode",
    "tsl2561": "photodiode",
    "tsl2591": "photodiode",
    "veml7700": "photodiode",
    "veml6075": "photodiode",
    "max44009": "photodiode",
    "opt300x": "photodiode",
    "tcs34725": "photodiode",
    "apds9960": "photodiode",
    "as7341": "photodiode",
    "bh1730": "photodiode",
    "ltr390": "photodiode",
    "vcnl4040": "photodiode",
    "as726x": "photodiode",
    "ltr390uv": "photodiode",
    "si1145": "photodiode",
    "tcs3430": "photodiode",
    "vcnl4010": "photodiode",
    "veml6070": "photodiode",
    "apds9306": "photodiode",
    "isl29125": "photodiode",
    "ltr308": "photodiode",
    "ltr329": "photodiode",
    "ltr553": "photodiode",
    "max44007": "photodiode",
    "opt4048": "photodiode",
    "vcnl4200": "photodiode",
    "veml6040": "photodiode",
    "veml6046": "photodiode",
    "si114x": "photodiode",
    "tcs3200": "photodiode",
    "as7265x": "photodiode",
    "as7331": "photodiode",
    "as7341l": "photodiode",
    "as7343": "photodiode",
    "alspt19": "photodiode",
    "ap3216": "photodiode",
    "apds9253": "photodiode",
    "apds9900": "photodiode",
    "apds9950": "photodiode",
    "apds9999": "photodiode",
    "bh1730fvc": "photodiode",
    "bh1749nuc": "photodiode",
    "bluxv30b": "photodiode",
    "gl5528": "photodiode",
    "isl29034": "photodiode",
    "isl29035": "photodiode",
    "ltr308als": "photodiode",
    "ltr329als": "photodiode",
    "ltr329ltr303": "photodiode",
    "ltr381rgb": "photodiode",
    "ltr501": "photodiode",
    "ltr507": "photodiode",
    "ltralsps": "photodiode",
    "ltrf216a": "photodiode",
    "ml8511": "photodiode",
    "opt3004": "photodiode",
    "s11059": "photodiode",
    "s9706": "photodiode",
    "tcs230": "photodiode",
    "tcs3210": "photodiode",
    "tcs3400": "photodiode",
    "tcs3472": "photodiode",
    "temt6000": "photodiode",
    "tmd2620": "photodiode",
    "tmd3725": "photodiode",
    "tsl235r": "photodiode",
    "tsl2540": "photodiode",
    "tsl2550": "photodiode",
    "ts4231": "photodiode",
    "vcnl3040": "photodiode",
    "vcnl36687": "photodiode",
    "vcnl36825t": "photodiode",
    "vcnl4020": "photodiode",
    "veml3235": "photodiode",
    "veml3328": "photodiode",
    "veml6030": "photodiode",
    "veml6031": "photodiode",
    "vncl4020c": "photodiode",
    "xycals21c": "photodiode",
    "gy33": "photodiode",
    "pca9536": "photodiode",
    "rak12010": "photodiode",
    "rak12019": "photodiode",
    "rak12021": "photodiode",
    "sen0390": "photodiode",
    "bm62s6021": "photodiode",
    "bm92s2021": "photodiode",
    # ── Biometric / PPG / ECG (photodiode-based) ──────────────────────
    "max30101": "photodiode",
    "max30102": "photodiode",
    "max30001": "adc",  # biopotential (ECG) and bioimpedance AFEs, like the ADS1292R
    "max30003": "adc",
    "max86150": "photodiode",
    # Sensor hubs: a microcontroller that reads an optical front end (MAX30101, MAX86141) and an
    # accelerometer, with no sensing element of its own (MAX32664 datasheet Rev 4, p.1)
    "max32664": None, "max32664c": None,
    "bh1790": "photodiode",
    "afe4490": "photodiode",
    "afe44xx": "photodiode",
    "afe4950": "photodiode",
    "bmh08101": "photodiode",
    "son1303": "photodiode",
    # ── Optical distance / gesture / flow (photodiode array) ──────────
    "gp2y0a21yk": "photodiode",
    "gp2y0e03": "photodiode",
    "gp2y0a41sk0f": "photodiode",
    "tcrt5000": "photodiode",
    "paj7620": "photodiode",
    "paj7620u2": "photodiode",
    "gr1030": "photodiode",
    "bm32s3021": "photodiode",
    "pmw3360": "photodiode",
    "pmw3901": "photodiode",
    "paa3905": "photodiode",
    "paa5160e1": "photodiode",
    "pat9136": "photodiode",
    "sen21231": "photodiode",
    # ── Capacitive touch / proximity sensors ──────────────────────────
    "mgc3130": "capacitive",
    "iqs5xx": "capacitive",
    "sx9500": "capacitive",
    "fdc1004": "capacitive",
    "at42qt1010": "capacitive",
    "at42qt1011": "capacitive",
    "gsl1680": "capacitive",
    "l58touch": "capacitive",
    "rak14002": "capacitive",
    "sen0285": "capacitive",
    "ncs36000": "capacitive",
    "fingerprintgrow": "optical",
    # ── Resistive touch controllers ───────────────────────────────────
    "xpt2046": "resistive",
    "xpt2046touchpad": "resistive",
    # ── Capacitive soil / moisture / rain ─────────────────────────────
    "fc28": "capacitive",
    "smt100": "capacitive",
    "rak12023": "capacitive",
    "tl555q": "capacitive",
    "ms01": "capacitive",
    "fc37": "resistive",
    "hrg15": "capacitive",
    "rg15": "capacitive",
    "hydreonrgxx": "capacitive",
    "sen0575": "capacitive",
    # ── ToF (time-of-flight) distance sensors ─────────────────────────
    "tmf8x01": "tof",
    "tof10120": "tof",
    "lc02": "tof",
    "glr01": "tof",
    # ── Ultrasonic distance / wind sensors ────────────────────────────
    "a01nyub": "ultrasonic",
    "urm07": "ultrasonic",
    "urm09": "ultrasonic",
    "urm13": "ultrasonic",
    "jsnsr04t": "ultrasonic",
    "sen0153": "ultrasonic",
    "hrxlmaxsonarwr": "ultrasonic",
    "tx20": "ultrasonic",
    "tx23": "ultrasonic",
    "cv7": "ultrasonic",
    "ws2300": "ultrasonic",
    "rs485": "ultrasonic",
    # ── Radar sensors ─────────────────────────────────────────────────
    "c4001": "radar",
    "mr24hpc1": "radar",
    "mr60bha2": "radar",
    "ld2420": "radar",
    "hlkfm22x": "radar",
    "rd03d": "radar",
    # ── RF / Lightning / GNSS ─────────────────────────────────────────
    "as3935": "rf",
    "cc1101": "rf",
    "ubloxgnssv3": "rf",
    "um980": "rf",
    "lg290p": "rf",
    "gp20u7": "rf",
    "meloperosamm8q": "rf",
    "tel0157": "rf",
    "tel0171": "rf",
    "wpi430": "rf",
    "sd3031": "rf",
    # ── Flow sensors (Hall-effect) ────────────────────────────────────
    "yfs201waterflow": "hall_effect",
    "f1012": "hall_effect",
    "f1032": "hall_effect",
    "flowmeter": "hall_effect",
    # ── Water quality / electrochemical probes ────────────────────────
    "dfr0300": "electrochemical",
    "ec10": "electrochemical",
    "ufireec": "electrochemical",
    "ufireise": "electrochemical",
    "sen0161": "electrochemical",
    "sen0322": "electrochemical",
    # ── Resistive force sensors ───────────────────────────────────────
    "fsr16x16bnl": "resistive",
    # ── MEMS gyro modules ────────────────────────────────────────────
    "rak12025": "mems",
    # ── Atlas Scientific / water quality modules ──────────────────────
    "ezoflo": "hall_effect",         # EZO-FLO flow meter (Hall)
    "ezohum": "capacitive",          # EZO-HUM humidity (capacitive)
    "ezoo2": "electrochemical",      # EZO-O2 dissolved oxygen
    "ezoprs": "mems",                # EZO-PRS pressure (MEMS)
    "ezorgb": "photodiode",          # EZO-RGB color sensor
    # ── Winsen water quality probes ───────────────────────────────────
    "mworp101": "electrochemical",
    "mwtds101": "electrochemical",
    "mwtds110": "electrochemical",
    "zwc101": "electrochemical",
    "zworp101": "electrochemical",
    "zwph102": "electrochemical",
    "zwph103": "electrochemical",
    "zwtds102": "electrochemical",
    "zwtds103": "electrochemical",
    "zwts101": "electrochemical",
    "zwtur101": "photodiode",        # Turbidity (optical/photodiode)
    "zwtur102": "photodiode",
    "zwtur103": "photodiode",
    # --- Best Modules Corp (Holtek) sensor modules ---
    "bm22s2021": "photodiode",       # Smoke detector (photoelectric)
    "bm22s2301": "photodiode",       # Ultra-compact smoke detector
    "bma26m202": "photodiode",       # Smoke detector module
    "bm25s2021": "resistive",        # Temp/humidity (resistive humidity sensor)
    "bm25s2621": "capacitive",       # Soil moisture (capacitive)
    "bm25s4021": "electrochemical",  # TDS water quality
    "bm25s4421": "electrochemical",  # pH sensor module
    "bm32s2021": "photodiode",       # Infrared proximity (datasheet: reflected IR)
    "bm42p782n1": "strain_gauge",    # Weighing scale module
    "bm42s3021": "thermocouple",     # Thermocouple module
    "bm62s2201": "mems",             # Air pressure sensor (MEMS)
    "bm62s3202": "mems",             # Water level sensor (pressure-based)
    "bme21m621": "mems",             # Air pressure sensor (MEMS)
    "bme33m251": "resistive",        # Temp/humidity
    "bme33m251a": "resistive",       # Temp/humidity
    "bme58m332": "ndir",             # CO2 detector (NDIR)
    "bme63m001": "electrochemical",  # TDS water quality
    "bme82m131": "photodiode",       # VEML7700 light sensor
    "bme82m131a": "photodiode",      # VEML7700 light sensor
    "bmh05102": "shunt",             # Body fat / heart rate (bioimpedance)
    "bmh05104": "shunt",             # Body composition (bioimpedance)
    "bmh08002": "photodiode",        # Oximeter (optical PPG)
    "bmh83m002": "photodiode",       # Oximeter (optical PPG)
    "bmh12m205": "strain_gauge",     # Weighing kit (load cell)
    "bmh23m001": "adc",              # 24-bit ADC module
    "bmh23m002": "adc",              # 24-bit ADC module
    "bms26m833": "thermopile",       # AMG8833 IR array
    "bms56m605": "mems",             # MPU-6050 IMU
    "bms81m001": "mems",             # MPU-6050 shake detection
    "bmv23m001": "mems",             # Sound detector (MEMS mic)
    "gtm5210f32": "optical",         # Fingerprint sensor
    "gtm5210f52": "optical",         # Fingerprint sensor
    "bme26m301": "mems",             # Air velocity sensor
    "bm25s4221": "photodiode",       # Turbidity (optical, like the ZW-TUR probes)
    "bme34k262a": "capacitive",      # Soil moisture kit built on the BM25S2621-1
    "bmh83m101a": "photodiode",      # Pulse oximetry (transmissive PPG)
    "bms33m332": "photodiode",       # STK3337 ambient light + IR proximity
    "stc31": "thermal_conduction",
    "stcc4": "thermal_conduction",
    "stmpe610": "resistive",
    "tsc2007": "resistive",
    "cs1237": "adc",
    "hx710": "adc",
    "hx711": "adc",
    "nau7802": "adc",
    "pasco2": "photoacoustic",
    "pasco2v01auma3": "photoacoustic",
}


def enrich_types(merged: dict[str, dict], quiet: bool = False) -> int:
    """Infer sensor type from measures and description keywords.

    Three-stage approach:
    1. IC-specific type lookup: direct mapping for well-known sensors.
    2. Measure-pattern matching: high-confidence inference from measure combinations.
    3. Description keyword matching: scan description for technology terms.

    Only fills type where it's currently NULL — never overrides existing data.
    Returns the number of sensors enriched.
    """
    enriched = 0
    stage1_count = 0
    stage2_count = 0
    stage3_count = 0

    for sid, sensor in merged.items():
        if sensor["type"] is not None:
            continue

        # --- Stage 1: IC-specific type lookup ---
        if sid in IC_TYPE_OVERRIDES:
            sensor["type"] = IC_TYPE_OVERRIDES[sid]
            enriched += 1
            stage1_count += 1
            continue

        measures = sensor["measures"]

        # --- Stage 2: Measure-pattern inference ---

        # Check explicit measure-pattern combinations
        inferred = None
        for pattern, sensor_type in MEASURE_TYPE_INFERENCE.items():
            if measures >= pattern:  # measures is a superset of pattern
                inferred = sensor_type
                break

        if inferred:
            sensor["type"] = inferred
            enriched += 1
            stage2_count += 1
            continue

        # --- Stage 3: Description keyword inference ---
        desc = (sensor.get("description") or "").lower()
        if not desc:
            continue

        # Pad description with spaces for word-boundary-ish matching on " tof "
        padded = f" {desc} "
        for sensor_type, keywords in TYPE_KEYWORDS:
            if any(kw in padded for kw in keywords):
                sensor["type"] = sensor_type
                enriched += 1
                stage3_count += 1
                break

    if not quiet:
        print(f"  Enriched {enriched} sensors ({stage1_count} IC lookup, {stage2_count} measures, {stage3_count} descriptions)")

    return enriched


# ---------------------------------------------------------------------------
# Voltage enrichment: static lookup for well-known sensor ICs
# ---------------------------------------------------------------------------

# Legacy fallbacks not yet superseded by a per-field review in curated.json.
# Format: "min-max" or a single nominal value in volts. These remaining entries
# include unresolved/unverified records; their presence is not verification.
# Applied as post-merge enrichment — never overwrites existing voltage data.
VOLTAGE_TABLE: dict[str, str] = {
    # Split-device identity audit (2026-11-09); details: data/sensors/ic_alias_evidence.json
    "fabo206uvsi1132": "1.71-3.6",  # https://www.silabs.com/documents/public/data-sheets/Si1132.pdf
    # --- Temperature / Humidity / Pressure ---
    "lm75": "2.7-5.5",          # TI/NXP LM75 datasheet

    # --- Temperature probes (thermocouple/RTD/1-wire) ---

    # --- Light ---

    # --- Gas / Air Quality ---

    # --- IMU / Motion ---

    # --- Magnetometer ---

    # --- Distance / Proximity ---

    # --- Load cell ---

    # --- Touch ---

    # --- Lightning ---

    # --- Encoder ---
    "as5600": "3.0-3.6",        # ams AS5600 datasheet

    # --- Gesture ---

    # --- Power monitoring ---

    # --- Infrared temperature ---
    "mlx90614": "2.6-3.6",      # Melexis MLX90614 datasheet

    # --- Radar ---

    # --- Particulate ---

    # --- Additional well-known sensors ---
    "amg88xx": "3.0-3.6",       # Panasonic AMG88xx datasheet (alias)

    # --- More temperature ---

    # --- More humidity ---

    # --- More pressure ---

    # --- More light ---

    # --- More gas ---

    # --- More IMU / accel ---

    # --- More magnetometer ---
    "mmc56x3": "1.62-3.6",      # MEMSIC MMC56x3 datasheet
    "mmc5983": "1.62-3.6",      # MEMSIC MMC5983MA datasheet

    # --- More distance ---
    "gp2y0a21yk": "4.5-5.5",    # Sharp GP2Y0A21YK datasheet

    # --- More particulate ---

    # --- Power monitoring ---

    # --- Gesture ---

    # --- Touch ---

    # --- Misc ---

    # --- Batch 2: DHT / Aosong ---
    "acd3100": "4.5-5.5",
    # --- TMP / TI temp ---
    "lm335": "0.5-40.0",
    # --- ADS / TI ADCs ---
    # --- MCP / Microchip temp ---
    # --- AS / ams-OSRAM ---
    "as5040": "3.0-5.5", "as5047p": "3.0-3.6", "as5048": "3.0-3.6",
    "as5200l": "3.0-3.6", "as5600l": "3.0-3.6",
    # --- HDC / TI humidity ---
    # --- HTU / TE humidity ---
    # --- NXP ---
    # --- ADXL / Analog Devices accel ---
    # --- Analog Devices misc ---
    "adstds75lm75": "2.7-5.5",
    # --- INA / TI power ---
    "ina2xx": "2.7-5.5",
    # --- Bosch ---
    "bma4xx": "1.2-3.6",
    "bme680bsec": "1.71-3.6",
    "bme68xbsec2": "1.71-3.6",
    # --- STMicroelectronics ---
    "lsm6dsv": "1.71-3.6",
    # --- TDK / InvenSense ---
    "icm42670s": "1.71-3.6",
    "ics40619": "1.5-3.6",
    # --- Silicon Labs ---
    # --- Sensirion ---
    "co2": "4.5-5.5",
    # --- ROHM ---
    # --- Lite-On ---
    "ap3216": "2.4-3.6",
    # --- Vishay ---
    # --- Broadcom ---
    # --- Melexis ---
    # --- Allegro ---
    "acs37800": "3.0-5.5",
    # --- Infineon ---
    # --- Renesas ---
    "isl29034": "2.25-3.63",
    # --- Microchip ---
    "atm90e32": "2.8-3.6",
    # --- MEMSIC ---
    # --- ScioSense ---
    # --- QST ---
    # --- Goertek ---
    "spa06": "1.7-3.6",
    # --- Panasonic ---
    # --- MaxBotix LV-MaxSonar-EZ: 2.5-5.5V ---
    "mb1060": "2.5-5.5", "mb1061": "2.5-5.5",
    "mb1710": "2.5-5.5", "mb1711": "2.5-5.5", "mb1712": "2.5-5.5",
    # --- MaxBotix XL-MaxSonar: 3.0-5.5V ---
    # --- MaxBotix I2CXL: 3.0-5.5V ---
    "mb1403": "3.0-5.5", "mb1413": "3.0-5.5", "mb1414": "3.0-5.5",
    "mb1423": "3.0-5.5", "mb1424": "3.0-5.5", "mb1433": "3.0-5.5",
    "mb1434": "3.0-5.5", "mb1443": "3.0-5.5", "mb1444": "3.0-5.5",
    # --- MaxBotix XL-WR: 3.0-5.5V ---
    # --- MaxBotix HRXL-WR: 2.7-5.5V ---
    "mb8450": "3.0-5.5",
    # --- Hi-Link radar ---
    "hlkld2410": "5.0-5.0", "hlkld2410b": "5.0-5.0",
    "hlkld2410s": "3.0-3.6",
    "ld2412": "5.0-5.0",
    "ld2452": "5.0-5.0",
    "ld6001a": "3.0-3.6", "ld6001c": "3.0-3.6",
    "ld8001": "3.0-3.6",
    "ld101": "5.0-5.0", "ld101l": "5.0-5.0",
    "ld101v": "5.0-5.0",
    "hlkfm22x": "5.0-5.0",
    # --- Benewake LiDAR ---
    "tfli2c": "3.7-5.2",
    # --- Atlas Scientific ---
    # --- Amphenol ---
    # --- Shanghai Belling ---
    # --- HiSilicon ---
    "cse7761": "3.0-3.6",
    # --- Cirrus Logic ---
    # --- Asahi Kasei ---
    # --- TE Connectivity ---
    "ms4525do": "3.3-5.5",
    # --- Honeywell ---
    "honeywellabp": "3.0-3.6",
    # --- Plantower ---
    # --- Gas ---
    # --- Avia ---
    # --- DFRobot/Ultrasonic ---
    # --- TI misc ---
    "cd74hc4067": "2.0-6.0",
    "opt4001": "1.6-3.6",
    # --- Touch ---
    "cst8xx": "2.6-3.6", "tt21100": "1.7-3.6",
    # --- Gxht ---
    # --- HopeRF ---
    # --- Würth ---
    "wsenpdus": "1.7-3.6",
    # --- Omron ---
    # --- Acconeer ---
    # --- Misc ---
    "pms7003t": "4.5-5.5",
    "c4001": "3.0-3.6",  "hm3301": "5.0-5.0",
    "hrg15": "5.0-24.0",
    "pzem004t": "5.0-5.0",
    "ags3870": "3.0-5.5",
    "xgzp68xx": "3.0-5.5",
    "mtp40": "3.6-5.5",
    "dypme007": "3.0-5.5",
    "tx20": "3.0-3.6",

    # --- Additional voltage entries (from datasheet research) ---

    # TI AFE / capacitance-to-digital
    "afe44xx": "2.0-3.6",

    # TI INA current/power monitors

    # TI HDC humidity/temperature

    # TI temperature sensors
    "tmp11x": "1.9-5.5",

    # TI optical / magnetic

    # TI misc

    # ST IIS industrial MEMS

    # ST LIS accelerometers

    # ST LSM IMUs

    # ST LSM303 combos
    "lsm303accel": "2.16-3.6",
    "lsm303dlhmag": "2.16-3.6",

    # ST L3G gyroscopes / LPS pressure
    "l3g": "2.4-3.6", "l3gd20u": "2.4-3.6",

    # TDK ICM/ICG IMUs
    "icm45605s": "1.71-3.6", "icm45686s": "1.71-3.6", "icm45688p": "1.71-3.6",

    # TDK ICP pressure
    "icp20100": "1.62-1.98", "icp201xx": "1.62-1.98",

    # NXP
    "fxas210002c": "2.1-3.6",

    # MEMSIC / Melexis

    # Microchip

    # onsemi / iSentek / Silicon Labs

    # Semtech / ams-OSRAM optical

    # Vishay

    # Sensirion

    # TE Connectivity / MEAS pressure
    "ms5xxx": "1.5-3.6",

    # ScioSense

    # ROHM / Renesas / Honeywell / PixArt
    "pmw3360": "3.3-3.6",

    # ams ToF / TE humidity / misc
    "ams5812": "3.0-5.5", "ams5915": "3.0-5.5",

    # Broadcom ToF

    # --- Generic modules ---
    "jsnsr04t": "3.0-5.5",         # JSN-SR04T waterproof ultrasonic
    "sr04m": "3.0-5.5",            # SR04M waterproof ultrasonic variant
    "tof10120": "3.0-5.0",         # TOF10120 laser rangefinder
    "me007": "3.0-5.5",            # ME007 ultrasonic rangefinder
    "us100": "2.4-5.5",            # US-100 ultrasonic (has both 3.3V and 5V mode)
    "fc28": "3.3-5.0",             # FC-28 soil moisture module
    "fc37": "3.3-5.0",             # FC-37 rain sensor module
    "ky040": "3.3-5.0",            # KY-040 rotary encoder module
    "yfs201waterflow": "5.0-24.0",  # YF-S201 water flow sensor
    "fingerprintgrow": "3.3-6.0",  # R307/R503 fingerprint modules
    "cc1101": "1.8-3.6",           # TI CC1101 RF transceiver
    "l58touch": "3.3-3.3",         # L58 touch sensor

    # --- MaxBotix ultrasonic ---

    # --- Benewake LiDAR/ToF ---
    "hornrt": "5.0-5.0",           # Benewake Horn-RT

    # --- Senseair CO2 ---
    "senseair": "4.5-5.25",        # Senseair S8

    # --- Melexis ---

    # --- Murata ---

    # --- NXP pressure ---
    "pca9536": "2.3-5.5",          # NXP PCA9536 I/O expander

    # --- STMicroelectronics ---

    # --- Sensirion ---

    # --- Panasonic ---
    "sngcja5": "5.0-5.0",          # Panasonic SN-GCJA5 PM sensor

    # --- DFRobot modules ---

    # --- Plantower ---
    "pm25": "5.0-5.0",             # Plantower PMSx003

    # --- Other well-known ---
    "zyaura": "4.5-5.5",           # ZyAura CO2 sensor module
    "qmc5583l": "2.16-3.6",        # QMC5883L compass

    # --- Holtek/Best Modules (common 3-5V modules) ---
    "bm22s3021": "3.0-5.0",
    "bm62s6021": "3.0-5.0",
    "bm92s2021": "3.0-5.0",

    # --- ScioSense ---

    # --- TE Connectivity ---

    # --- TDK ---

    # --- Honeywell ---
    "i2casdx": "4.75-5.25",        # ASDX pressure sensor

    # --- Microchip ---
    "jc424": "2.0-3.6",            # MCP9844 renamed

    # --- Vishay ---
    "vncl4020c": "2.5-3.6",        # VCNL4020C proximity/ambient light
    # (TCRT5000 already added above in generic)

    # --- Bosch ---
    "7semibno08x": "2.4-3.6",      # BNO08x 9-DoF IMU

    # --- RAKWireless modules ---
    "rak12023": "3.0-3.6",  "rak12039": "5.0-5.0",

    # --- Xiaomi BLE sensors ---
    "xiaomixmwsdj04mmc": "3.0-3.0",

    # --- Atlas Scientific probes (circuit boards) ---

    # --- Garmin ---

    # --- Winsen active sensors ---
    "ze29ac2h5oh": "3.7-9.0",      # Winsen ZE29A electrochemical module (common spec)
    "gm1602": "5.0-5.0",           # Winsen GM1602 semiconductor gas module

    # --- Other remaining well-known ---
    "sm300d2": "4.8-5.2",          # 5 ± 0.2V (SM300D2 parameter table; ESPHome docs)
}


def _enrich_voltages(merged: dict[str, dict], quiet: bool = False) -> int:
    """Fill in voltage from static lookup where currently NULL.

    Only sets voltage when it's missing — never overrides scraped data.

    Returns the number of sensors enriched.
    """
    enriched = 0
    for sid, sensor in merged.items():
        if sensor["voltage"] is not None:
            continue
        voltage = VOLTAGE_TABLE.get(sid)
        if voltage:
            sensor["voltage"] = voltage
            enriched += 1

    if not quiet:
        print(f"  Enriched {enriched} sensors via voltage lookup table")

    return enriched


# ---------------------------------------------------------------------------
# Protocol enrichment — maps well-known sensor IDs to their communication
# protocols. Applied as post-merge enrichment: ONLY adds protocols where none
# exist from any source JSON.
# ---------------------------------------------------------------------------

IC_PROTOCOLS: dict[str, list[str]] = {
    "am2301": ["gpio"],  # https://www.aosong.com/userfiles/files/media/AM2301%E8%A7%84%E6%A0%BC%E4%B9%A6-%E8%8B%B1%E6%96%87%E7%89%88%EF%BC%8820210407%EF%BC%89.pdf
    "htu21d": ["i2c"],  # https://my.avnet.com/wcm/connect/c76abfe6-a20b-4fe8-bfdf-db3dc9842ebd/TE-Connectivity-HTU21D-EN-Datasheet.pdf?CACHE=NONE&CVID=pFu5s5u&ContentCache=NONE&MOD=AJPERES
    "kx134": ["i2c", "spi"],  # https://fscdn.rohm.com/kionix/en/datasheet/kx134-1211-e.pdf
    "pygp2y": ["analog"],  # https://global.sharp/products/device/lineup/selection/opto/dust/index.html
    # Split-device identity audit (2026-11-09); details: data/sensors/ic_alias_evidence.json
    "lsm6dsl": ["i2c", "spi"],  # https://www.st.com/resource/en/datasheet/lsm6dsl.pdf
    "lsm6dso": ["i2c", "spi", "i3c"],  # https://www.st.com/resource/en/datasheet/lsm6dso.pdf
    "lsm6dsr": ["i2c", "spi", "i3c"],  # https://www.st.com/resource/en/datasheet/lsm6dsr.pdf
    "lsm6dsv16x": ["i2c", "spi", "i3c"],  # https://www.st.com/resource/en/datasheet/lsm6dsv16x.pdf
    "lsm6dsv16bx": ["i2c", "spi", "i3c"],  # https://www.st.com/resource/en/datasheet/lsm6dsv16bx.pdf
    "ism330dhcx": ["i2c", "spi"],  # https://www.st.com/resource/en/datasheet/ism330dhcx.pdf
    "lsm6ds3": ["i2c", "spi"],  # https://community.st.com/ysqtg83639/attachments/ysqtg83639/stm32-mcu-products-forum/89677/2/%5BATT%5D11987.pdf
    "lsm9ds0": ["i2c", "spi"],  # https://www.st.com/resource/en/datasheet/lsm9ds0.pdf
    "mpu6500": ["i2c", "spi"],  # https://www.invensense.tdk.com/en-us/products/inertial-sensors/mpu-6500
    "bmi323": ["i2c", "spi", "i3c"],  # https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmi323-ds000.pdf
    "max30100": ["i2c"],  # https://www.analog.com/media/en/technical-documentation/data-sheets/max30100.pdf
    "max30105": ["i2c"],  # https://www.analog.com/media/en/technical-documentation/data-sheets/max30105.pdf
    "ds18s20": ["one_wire"],  # https://www.analog.com/media/en/technical-documentation/data-sheets/DS18S20.pdf
    "sht30": ["i2c"],  # https://sensirion.com/media/documents/213E6A3B/63A5A569/Datasheet_SHT3x_DIS.pdf
    "sht31": ["i2c"],  # https://sensirion.com/media/documents/213E6A3B/63A5A569/Datasheet_SHT3x_DIS.pdf
    "sht31d": ["i2c"],  # https://sensirion.com/media/documents/213E6A3B/63A5A569/Datasheet_SHT3x_DIS.pdf
    "sht35": ["i2c"],  # https://sensirion.com/media/documents/213E6A3B/63A5A569/Datasheet_SHT3x_DIS.pdf
    "sht40": ["i2c"],  # https://sensirion.com/media/documents/33FD6951/6A7C10A0/HT_DS_Datasheet_SHT4x_V7.3.pdf
    "sht45": ["i2c"],  # https://sensirion.com/media/documents/33FD6951/6A7C10A0/HT_DS_Datasheet_SHT4x_V7.3.pdf
    "sht21": ["i2c"],  # https://sensirion.com/media/documents/120BBE4C/63500094/Sensirion_Datasheet_Humidity_Sensor_SHT21.pdf
    "bme680": ["i2c", "spi"],  # https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme680-ds001.pdf
    "bme688": ["i2c", "spi"],  # https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme688-ds000.pdf
    "bmp388": ["i2c", "spi"],  # https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp388-ds001.pdf
    "bmp390": ["i2c", "spi"],  # https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp390-ds002.pdf
    "bmp085": ["i2c"],  # https://cdn.sparkfun.com/assets/6/f/3/9/4/BST-BMP085-DS000-05.pdf
    "scd40": ["i2c"],  # https://sensirion.com/media/documents/48C4B7FB/64C134E7/Sensirion_SCD4x_Datasheet.pdf
    "scd41": ["i2c"],  # https://sensirion.com/media/documents/48C4B7FB/64C134E7/Sensirion_SCD4x_Datasheet.pdf
    "hdc1000": ["i2c"],  # https://www.ti.com/lit/ds/symlink/hdc1000.pdf
    "hdc1010": ["i2c"],  # https://www.ti.com/lit/ds/symlink/hdc1010.pdf
    "opt3001": ["i2c"],  # https://www.ti.com/lit/ds/symlink/opt3001.pdf
    "opt3002": ["i2c"],  # https://www.ti.com/lit/ds/symlink/opt3002.pdf
    "mhz19b": ["uart", "pwm"],  # https://www.winsen-sensor.com/d/files/manual/mh-z19b.pdf
    "mhz19c": ["uart", "pwm"],  # https://www.winsen-sensor.com/d/files/manual/mh-z19c.pdf
    "mhz19d": ["uart", "pwm"],  # https://www.winsen-sensor.com/d/files/manual/mh-z19d.pdf
    "mhz19e": ["uart", "pwm"],  # https://www.winsen-sensor.com/d/files/manual/mh-z19e.pdf
    "mhz1911a": ["uart", "pwm"],  # https://www.winsen-sensor.com/d/files/manual/mh-z1911a.pdf
    "mhz14a": ["uart", "pwm"],  # https://www.winsen-sensor.com/d/files/manual/mh-z14a.pdf
    "mhz14b": ["uart", "pwm"],  # https://www.winsen-sensor.com/d/files/manual/mh-z14b.pdf
    "zh06ii": ["uart", "pwm"],  # https://www.winsen-sensor.com/d/files/manual/zh06-ii.pdf
    "zh06iii": ["uart", "pwm"],  # https://www.winsen-sensor.com/d/files/manual/zh06-iii.pdf
    "zh06iv": ["uart", "pwm"],  # https://www.winsen-sensor.com/d/files/manual/zh06-iv.pdf
    "ld2410b": ["gpio", "uart"],  # https://www.hlktech.net/index.php?id=65
    "ld2410c": ["gpio", "uart"],  # https://www.hlktech.net/index.php?id=65
    "tmf8820": ["i2c"],  # https://look.ams-osram.com/m/52236c476132a095/original/TMF882X-DS000693.pdf
    "tmf8821": ["i2c"],  # https://look.ams-osram.com/m/52236c476132a095/original/TMF882X-DS000693.pdf
    "as7262": ["i2c", "uart"],  # https://look.ams-osram.com/m/663487deeb7089a7/original/AS7262-DS000486.pdf
    "as7263": ["i2c", "uart"],  # https://look.ams-osram.com/m/2f885f8e1b074032/original/AS7263-DS000476.pdf
    "fs30001005": ["i2c"],  # https://www.renesas.com/en/document/dst/fs3000-datasheet
    "fs30001015": ["i2c"],  # https://www.renesas.com/en/document/dst/fs3000-datasheet
    "ms580314ba": ["i2c", "spi"],  # https://www.te.com/en/product-MS580314BA01-50.html
    "tfminiplus": ["i2c", "uart"],  # https://en.benewake.com/TFminiPlus/index.html
    "amg8833": ["i2c"],  # https://industrial.panasonic.com/ww/products/pt/grid-eye/models/AMG8833
    "fabo206uvsi1132": ["i2c"],  # https://www.silabs.com/documents/public/data-sheets/Si1132.pdf
    # ===== Temperature / Humidity / Pressure =====
    "bme280": ["i2c", "spi"],
    "bme68x": ["i2c", "spi"],
    "bme68xbsec2": ["i2c", "spi"],
    "bme690": ["i2c", "spi"],
    "bme82m131": ["i2c"],
    "bmp180": ["i2c"],
    "bmp280": ["i2c", "spi"],
    "bmp3xx": ["i2c", "spi"],
    "bmp580": ["i2c", "spi"],
    "bmp585": ["i2c", "spi"],
    "bmp58x": ["i2c", "spi"],
    "bmp5xx": ["i2c", "spi"],
    "sht3x": ["i2c"],
    "sht4x": ["i2c"],
    "sht20": ["i2c"],
    "sht25": ["i2c"],
    "sht85": ["i2c"],
    "sht11": ["i2c"],
    "shtcx": ["i2c"],
    "aht20": ["i2c"],
    "ahtx0": ["i2c"],
    "htu21df": ["i2c"],
    "si7021": ["i2c"],
    "si7005": ["i2c"],
    "si7013": ["i2c"],
    "si7051": ["i2c"],
    "si705x": ["i2c"],
    "si70xx": ["i2c"],
    "hdc1080": ["i2c"],
    "hdc1008": ["i2c"],
    "hdc10xx": ["i2c"],
    "hdc3020": ["i2c"],
    "hdc3022": ["i2c"],
    "tmp117": ["i2c"],
    "tmp116": ["i2c"],
    "tmp126": ["spi"],
    "mcp9808": ["i2c"],
    "mcp9800": ["i2c"],
    "mcp9802": ["i2c"],
    "mcp9601": ["i2c"],
    "mcp9700": ["analog"],
    "mcp9701": ["analog"],
    "mcp970x": ["analog"],
    "lps22hb": ["i2c", "spi"],
    "lps25h": ["i2c", "spi"],
    "lps28": ["i2c", "spi"],
    "lps2x": ["i2c", "spi"],
    "lps35hw": ["i2c", "spi"],
    "dps310": ["i2c", "spi"],
    "tmp006": ["i2c"],
    "tmp36": ["analog"],
    "tmp61": ["analog"],
    "tmp9a00": ["i2c"],
    "lm35": ["analog"],
    "lm35c": ["analog"],
    "lm35d": ["analog"],
    "lm45b": ["analog"],
    "lm50b": ["analog"],
    "lm50c": ["analog"],
    "lm73": ["i2c"],
    "lm75a": ["i2c"],
    "lm335a": ["analog"],
    "ds3231": ["i2c"],
    "ds1821": ["one_wire"],
    "ds7505": ["i2c"],
    "pct2075": ["i2c"],
    "adt7410": ["i2c"],
    "am2315": ["i2c"],
    "cht8305": ["i2c"],
    "cht8310": ["i2c"],
    "cht832x": ["i2c"],
    "hs3003": ["i2c"],
    "hih61xx": ["i2c"],
    "tsys01": ["i2c"],
    "stlm20dd9f": ["analog"],
    "stlm20w87f": ["analog"],
    "s5851a": ["i2c"],
    "nst1001": ["one_wire"],
    "bd1020hfv": ["analog"],
    "max30205": ["i2c"],
    "max6605mxk": ["analog"],
    "max6605mxkv": ["analog"],
    "max6607ixk": ["analog"],
    "max6613mxk": ["analog"],
    "max6626": ["spi"],
    "tsicxx6": ["one_wire"],
    "tc1046": ["analog"],
    "tc1047": ["analog"],
    "ad22100a": ["analog"],
    "ad22100k": ["analog"],
    "ad22100s": ["analog"],
    "ad22103k": ["analog"],
    "barometerhp20x": ["i2c"],
    "ms5611": ["i2c", "spi"],
    "ms5803": ["i2c", "spi"],
    "ms5637": ["i2c"],
    "ms5xxx": ["i2c", "spi"],
    "mpl115a1": ["spi"],
    "mpl115a2": ["i2c"],
    "mpx5700": ["analog"],
    "mpx5999d": ["analog"],
    "mpxa4250a": ["analog"],
    "mpxa6115a": ["analog"],
    "mpxh6115a": ["analog"],
    "mpxh6400a": ["analog"],
    "mpxhz6116a": ["analog"],
    "mpxhz6250a": ["analog"],
    "xgzp6897d": ["i2c"],
    "lwlp5000": ["i2c"],
    "ams5812": ["i2c"],
    "ams5915": ["i2c"],
    "hp03s": ["i2c"],
    "spa06": ["i2c", "spi"],
    "spa06003": ["i2c", "spi"],
    "spl06": ["i2c", "spi"],
    "spl07": ["i2c", "spi"],
    "icp10100": ["i2c"],
    "icp10111": ["i2c"],
    "icp20100": ["i2c"],
    "d6fph": ["i2c"],
    "sdp31": ["i2c"],
    "sfm3200": ["i2c"],
    "t5403barometric": ["i2c"],

    # ===== IMU / Motion / Accelerometer =====
    # InvenSense PS-MPU-6000A-00 section 9.1: only MPU-6000 supports SPI.
    # https://cdn.sparkfun.com/datasheets/Components/General%20IC/PS-MPU-6000A.pdf
    "mpu6050": ["i2c"],
    "mpu6000": ["i2c", "spi"],
    "mpu9x50": ["i2c", "spi"],
    "bmi160": ["i2c", "spi"],
    "bmi270": ["i2c", "spi"],
    "bmi270bmm150": ["i2c", "spi"],
    "bmi085": ["i2c", "spi"],
    "bmi088": ["i2c", "spi"],
    "lsm6dsox": ["i2c", "spi"],
    "lsm6ds3tr": ["i2c", "spi"],
    "lsm6dsm": ["i2c", "spi"],
    "lsm6": ["i2c", "spi"],
    "lsm9ds1tr": ["i2c", "spi"],
    "lsm303": ["i2c"],
    "lsm303accel": ["i2c"],
    "lsm303c": ["i2c", "spi"],
    "lsm303dlh": ["i2c"],
    "lsm303dlhmag": ["i2c"],
    "lis3dh": ["i2c", "spi"],
    "lis2hh12": ["i2c", "spi"],
    "lis331": ["i2c", "spi"],
    "h3lis200dl": ["i2c", "spi"],
    "adxl345": ["i2c", "spi"],
    "adxl335": ["analog"],
    "adxl343": ["i2c", "spi"],
    "adxl34x": ["i2c", "spi"],
    "adxl355": ["i2c", "spi"],
    "adxl375": ["i2c", "spi"],
    "adxl37x": ["i2c", "spi"],
    "bno055": ["i2c", "uart"],
    "bno080": ["i2c", "spi", "uart"],
    "bno08x": ["i2c", "spi", "uart"],
    "7semibno08x": ["i2c", "spi", "uart"],
    "mma8451": ["i2c"],
    "mma8452q": ["i2c"],
    "mma8453q": ["i2c"],
    "mma8652": ["i2c"],
    "mma8653": ["i2c"],
    "mma7455": ["i2c", "spi"],
    "mma7660": ["i2c"],
    "msa301": ["i2c"],
    "mc3479": ["i2c", "spi"],
    "icg20660": ["i2c", "spi"],
    "icg20660l": ["i2c", "spi"],
    "icm20689": ["i2c", "spi"],
    "icm20x": ["i2c", "spi"],
    "icm42670p": ["i2c", "spi"],
    "icm42670s": ["i2c", "spi"],
    "icm45608": ["i2c", "spi"],
    "icm45689": ["i2c", "spi"],
    "ism330is": ["i2c", "spi"],
    "iis2dulpx": ["i2c", "spi"],
    "asm330lhh": ["i2c", "spi"],
    "bmx055": ["i2c", "spi"],
    "bmx160": ["i2c", "spi"],
    "bma220": ["i2c", "spi"],
    "bma423": ["i2c"],
    "itg3200": ["i2c"],
    "l3g": ["i2c", "spi"],
    "l3gd20": ["i2c", "spi"],
    "l3gd20u": ["i2c", "spi"],
    "fxas210002c": ["i2c", "spi"],
    "fxas21002c": ["i2c", "spi"],
    "adis16470": ["spi"],
    "hscdtd008a": ["i2c"],
    "scl3300": ["spi"],
    "scl3400": ["spi"],
    "kx023": ["i2c", "spi"],
    "kxtj3": ["i2c"],
    "qmi8658": ["i2c", "spi"],
    "qmi8658c": ["i2c", "spi"],
    "gy521": ["i2c"],
    "gy512": ["i2c"],
    "comp6dofn0m1": ["i2c"],
    "9dof": ["i2c"],
    "imu9dof": ["i2c"],
    "hg4930": ["spi"],

    # ===== Light / UV =====
    "bh1750": ["i2c"],
    "bh1730fvc": ["i2c"],
    "bh1749nuc": ["i2c"],
    "veml7700": ["i2c"],
    "veml6040": ["i2c"],
    "veml3328": ["i2c"],
    "tsl2591": ["i2c"],
    "tsl235r": ["analog"],
    "tsl2550": ["i2c"],
    "apds9960": ["i2c"],
    "apds9900": ["i2c"],
    "apds9950": ["i2c"],
    "apds9999": ["i2c"],
    "opt300x": ["i2c"],
    "opt3101": ["i2c"],
    "isl29034": ["i2c"],
    "isl29125": ["i2c"],
    "ltr390uv": ["i2c"],
    "ltr308": ["i2c"],
    "ltr308als": ["i2c"],
    "ltr329als": ["i2c"],
    "ltr329ltr303": ["i2c"],
    "ltr381rgb": ["i2c"],
    "ltr507": ["i2c"],
    "tcs3200": ["gpio"],
    "tcs3210": ["gpio"],
    "tcs230": ["gpio"],
    "tcs3430": ["i2c"],
    "tcs3472": ["i2c"],
    "si1142": ["i2c"],
    "si1145": ["i2c"],
    "ap3216": ["i2c"],
    "bluxv30b": ["i2c"],
    "vcnl4010": ["i2c"],
    "vcnl4020": ["i2c"],
    "vcnl3040": ["i2c"],
    "vcnl36687": ["i2c"],
    "vcnl4200": ["i2c"],
    "vncl4020c": ["i2c"],
    "max44007": ["i2c"],
    "ml8511": ["analog"],
    "alspt19": ["analog"],
    "temt6000": ["analog"],
    "as7262x": ["i2c"],
    "as726x": ["i2c"],
    "as7341l": ["i2c"],
    "tmd3725": ["i2c"],
    "s9706": ["spi"],

    # ===== Gas / CO2 / Air Quality =====
    "ccs811": ["i2c"],
    "sgp30": ["i2c"],
    "sgp40": ["i2c"],
    "ens160": ["i2c", "spi"],
    "ens190": ["i2c"],
    "ens220": ["i2c", "spi"],
    "scd4x": ["i2c"],
    "scd30": ["i2c", "uart"],
    "mhz19": ["uart"],
    "sds011": ["uart"],
    "sds021": ["uart"],
    "sps30": ["i2c", "uart"],
    "ags01db": ["i2c"],
    "ags02ma": ["i2c"],
    "ags2616": ["uart"],
    "ags3870": ["i2c"],
    "ags3871": ["i2c"],
    "sen54": ["i2c"],
    "sen55": ["i2c"],
    "sfa40": ["i2c"],
    "hpma115": ["uart"],
    "ips7100": ["i2c", "uart"],
    "sngcja5": ["i2c", "uart"],
    "cbhchov4": ["uart"],
    "co2": ["uart"],
    "7semico2th": ["i2c"],
    "acd10": ["i2c"],
    "acd3100": ["i2c"],
    "mics6814": ["i2c", "analog"],
    "ppd71": ["analog"],
    "gp2y1010au0f": ["analog"],
    "pm1006k": ["uart"],
    "zmod4450": ["i2c"],
    "mg811": ["analog"],

    # ===== Distance / Proximity =====
    "vl53l0x": ["i2c"],
    "vl53l1x": ["i2c"],
    "vl6180x": ["i2c"],
    "vl6180": ["i2c"],
    "ds18b20": ["one_wire"],
    "ds18x20": ["one_wire"],
    "max31820": ["one_wire"],
    "max31850": ["one_wire", "spi"],
    "gp2y0a21yk": ["analog"],
    "gp2y0e03": ["i2c"],
    "gp2y0a41sk0f": ["analog"],
    "nhcsr04": ["gpio"],
    "sr04": ["gpio"],
    "sr04t": ["uart"],
    "rfd77402": ["i2c"],
    "lidar07": ["i2c", "uart"],
    "tmf8x01": ["i2c"],
    "tmf8801": ["i2c"],
    "tmf882x": ["i2c"],
    "lidarlightv3hp": ["i2c"],
    "ch101": ["i2c"],
    "sonari2c": ["i2c"],
    "urm07": ["uart"],
    "urm09": ["i2c", "uart"],
    "urm13": ["i2c", "uart"],
    "rcwl9610": ["i2c"],
    "rcwl9620": ["i2c"],
    "c4001": ["i2c", "uart"],
    "c4002": ["i2c", "uart"],
    "64x8dtof": ["i2c"],
    "64xdtof": ["i2c"],
    "tfli2c": ["i2c"],

    # ===== Current / Voltage / Power =====
    "ina219": ["i2c"],
    "ina219b": ["i2c"],
    "ina226": ["i2c"],
    "ina228": ["i2c"],
    "ina23x": ["i2c"],
    "ina169": ["analog"],
    "ina780x": ["i2c"],
    "ads1115": ["i2c"],
    "ads1015": ["i2c"],
    "ads1115010v": ["i2c"],
    "ads1220": ["spi"],
    "ads1258": ["spi"],
    "ads1292r": ["spi"],
    "ads1293": ["spi"],
    "acs712": ["analog"],
    "acs723": ["analog"],
    "acs772": ["analog"],
    "max471": ["analog"],
    "ctclamp": ["analog"],
    "hlw8012": ["gpio"],
    "atm90e32as": ["spi"],
    "cs5464": ["spi"],
    "cs5490": ["spi"],
    "pzem004t": ["uart"],
    "ad7193": ["spi"],
    "ad7194": ["spi"],
    "ad7797": ["spi"],
    "ltc2959": ["spi"],
    "mcp3427": ["i2c"],
    "mcp39f521": ["i2c", "uart"],
    "stpm34": ["spi", "uart"],

    # ===== Weight / Force =====
    "hx711": ["gpio"],
    "hx710": ["gpio"],
    "hx710a": ["gpio"],
    "hx710b": ["gpio"],

    # ===== Magnetic / Compass =====
    "qmc5883l": ["i2c"],
    "qmc5883": ["i2c"],
    "qmc5583l": ["i2c"],
    "qmc5883p": ["i2c"],
    "bmm150": ["i2c", "spi"],
    "hmc6352": ["i2c"],
    "mmc5603nj": ["i2c"],
    "mmc34160pj": ["i2c"],
    "mlx90377": ["spi"],
    "mlx90392": ["i2c"],
    "mlx90395": ["i2c", "spi"],
    "gy33": ["uart"],
    "as5040": ["spi"],
    "as5047p": ["spi"],
    "as5200l": ["i2c"],
    "as5600l": ["i2c"],
    "am4096": ["spi"],
    "amt25": ["spi"],
    "mt6701": ["i2c", "spi"],
    "esp8266hmc5883l": ["i2c"],

    # ===== Thermocouple / IR Temperature =====
    "max31855": ["spi"],
    "max31865": ["spi"],
    "mlx90614": ["i2c"],
    "mlx90615": ["i2c"],
    "mlx90621": ["i2c"],
    "mlx90632": ["i2c"],
    "mlx90641": ["i2c"],
    "mlx90642": ["i2c"],
    "amg88xx": ["i2c"],
    "ad8494": ["analog"],
    "tsd305": ["i2c"],
    "pt1000probe": ["spi"],

    # ===== Touch =====
    "mpr121": ["i2c"],
    "cap1188": ["i2c", "spi"],
    "at42qt1010": ["gpio"],
    "at42qt1011": ["gpio"],
    "tsc2007": ["i2c"],
    "stmpe610": ["i2c", "spi"],
    "ft5336": ["i2c"],
    "ft6x06": ["i2c"],
    "cst816d": ["i2c"],
    "cst8xx": ["i2c"],
    "sx8634": ["i2c"],
    "gsl1680": ["i2c"],
    "tt21100": ["i2c"],
    "xpt2046": ["spi"],
    "xpt2046touchpad": ["spi"],
    "cy8cmbr3102": ["i2c"],
    "iqs5xx": ["i2c"],
    "ttp223": ["gpio"],
    "ttp229bsf": ["i2c"],
    "fdc1004": ["i2c"],
    "l58touch": ["i2c"],
    "uft6336u": ["i2c"],

    # ===== Gesture =====
    "paj7620u2": ["i2c"],
    "mgc3130": ["i2c"],

    # ===== Radar / Presence =====
    "bgt60tr13c": ["spi"],
    "rcwl0516": ["gpio"],
    "a111": ["spi"],
    "rd03": ["uart"],
    "isys4001": ["uart"],

    # ===== Heart Rate / Biometric =====
    "max30102": ["i2c"],
    "max32664": ["i2c"],
    "max30001": ["spi"],
    "max30003": ["spi"],
    "max86150": ["i2c"],
    "afe4490": ["spi"],
    "afe44xx": ["spi"],
    "afe4950": ["spi"],

    # ===== Microphone =====
    "imp34dt05": ["i2s"],
    "ics40619": ["analog"],
    "mp23db01hp": ["i2s"],
    "msm261": ["i2s"],
    "i2s": ["i2s"],

    # ===== GNSS / GPS =====
    "gp20u7": ["uart"],
    "ubloxgnssv3": ["uart", "i2c"],
    "um980": ["uart"],
    "lg290p": ["uart"],

    # ===== Miscellaneous =====
    "as3935": ["i2c", "spi"],
    "rg15": ["uart"],
    "cd74hc4067": ["gpio"],
    "dht": ["gpio"],
    "us1881": ["gpio"],
    "ah1815": ["gpio"],
    "tli4970": ["spi"],
    "tli4971": ["analog"],
    "tlv493d": ["i2c"],
    "ak9750": ["i2c"],
    "tcrt5000": ["analog"],
    "sct013": ["analog"],
    "zmpt101b": ["analog"],
    "lmp91000": ["i2c"],
    "bq27220": ["i2c"],
    "max17055": ["i2c"],
    "tl555q": ["analog"],
    "gr1030": ["i2c"],
    "pca9536": ["i2c"],
    "pav3000": ["i2c"],
    "wt61pc": ["i2c"],
    "rv3032": ["i2c"],
    "mmr902": ["i2c"],
    "ncs36000": ["analog"],
    "pmw3360": ["spi"],
    "pmw3901": ["spi"],
    "p1meter": ["uart"],
    "p760": ["i2c"],
    "ms4525do": ["i2c"],
    "sen0153": ["uart"],
    "sen0285": ["i2c"],
    "sen0322": ["i2c"],
    "sen0343": ["i2c"],
    "sen0395": ["uart"],
    "sen0496": ["i2c"],
    "sen0560": ["i2c"],
    "sen0575": ["i2c"],
    "sen0590": ["uart"],
    "sen10724": ["analog"],
    "ad8232": ["analog"],
    "cv7": ["uart"],
    "aci10kantemp": ["analog"],
    "esp32thermistor": ["analog"],
    "rtd10k": ["analog"],
    "tfa433receiver": ["gpio"],
    "mprls": ["i2c", "spi"],
    "dnmsi2c": ["i2c"],
    "sb041": ["i2c"],
    "dfr0300": ["analog"],
    "pd10lx": ["analog"],
    "mpbmp3xxfull": ["i2c", "spi"],
    "mpm10": ["i2c"],
    # Finished BLE thermometers: ESPHome reads their advertisements (AUTO_LOAD xiaomi_ble);
    # nothing on them can be wired to an I2C bus.
    "xiaomilywsd02mmc": ["ble"],
    "xiaomixmwsdj04mmc": ["ble"],
    "sca100t": ["spi"],
    "wf100dpz": ["i2c"],
    "tel0157": ["uart"],
    "tel0171": ["i2c"],
    "sen0161": ["analog"],
    "zyaura": ["uart"],

    # ===== Bosch BM-series shuttle boards =====
    "bm22s2021": ["uart"],
    "bm22s3021": ["uart"],
    "bm22s3031": ["uart"],
    "bm22s3221": ["uart"],
    "bm22s3421": ["uart"],
    "bm22s4221": ["uart"],
    "bm25s2021": ["i2c", "one_wire"],
    "bm25s3221": ["uart"],
    "bm25s3321": ["uart"],
    "bm25s3421": ["uart"],
    "bm25s4021": ["uart"],
    "bm32s2031": ["uart"],
    "bm32s3021": ["uart"],
    "bm42s3021": ["i2c"],
    "bm42s5321": ["i2c", "uart"],
    "bm62s2201": ["i2c", "uart"],
    "bm62s2301": ["i2c"],
    "bm62s6021": ["uart"],
    "bm92s2021": ["uart"],
    "bmh06203": ["i2c"],
    "bmh08002": ["uart"],
    "bmh08101": ["uart"],
    "bmh12m105": ["i2c", "uart"],
    "bmh12m205": ["uart"],
    "bmk52t016": ["i2c"],
    "bmk54t004": ["i2c"],
    "bmk56t004": ["i2c"],
    "bml36m001": ["i2c"],
    "bms26m833": ["i2c"],
    "bms33m332": ["i2c"],
    "bms36t001": ["uart"],
    "bms56m206a": ["i2c"],
    "bms56m605": ["i2c"],
    "bms81m001": ["i2c"],
    "bmv23m001": ["i2c"],

    # ===== RAKwireless =====
    "rak12010": ["i2c"],
    "rak12019": ["i2c"],
    "rak12021": ["i2c"],
    "rak12023": ["analog"],
    "rak12025": ["i2c"],
    "rak12034": ["spi"],
    "rak12039": ["uart"],
    "rak14002": ["i2c"],

    # ===== Winsen sensors with known protocols =====
    # ZE-series electrochemical modules with UART output
    "ze03": ["uart"],
    "ze07ch2o": ["uart"],
    "ze07co": ["uart"],
    "ze07h2": ["uart"],
    "ze08kch2o": ["uart"],
    "ze11": ["uart"],
    "ze12a": ["uart"],
    "ze14o3": ["uart"],
    "ze15co": ["uart"],
    "ze16bco": ["uart"],
    "ze16co": ["uart"],
    "ze18co": ["uart"],
    "ze21cs": ["uart"],
    "ze21h2": ["uart"],
    "ze25ao3": ["uart"],
    "ze25o3": ["uart"],
    "ze27o3": ["uart"],
    "ze29ac2h5oh": ["uart"],
    "ze30c2h5oh": ["uart"],
    "ze31c2h5oh": ["uart"],
    "ze40btvoc": ["uart"],
    "ze40tvoc": ["uart"],
    "ze510ch2o": ["uart"],
    "ze610h2": ["uart"],
    "ze630h2": ["uart"],
    "zeh100": ["uart"],
    # ZW-series water quality modules
    "zwc101": ["uart"],
    "zwc102": ["uart"],
    "zwhc101": ["uart"],
    "zwo101": ["uart"],
    "zwo103": ["uart"],
    "zworp101": ["uart"],
    "zwph101": ["uart"],
    "zwph102": ["uart"],
    "zwph103": ["uart"],
    "zwrcl101": ["uart"],
    "zwtds102": ["uart"],
    "zwtds103": ["uart"],
    "zwts101": ["uart"],
    "zwtur101": ["uart"],
    "zwtur102": ["uart"],
    "zwtur103": ["uart"],
    # MW-series water quality modules
    "mwo101": ["uart"],
    "mwo201": ["uart"],
    "mworp101": ["uart"],
    "mwph101": ["uart"],
    "mwrcl101": ["uart"],
    "mwtds101": ["uart"],
    "mwtds110": ["uart"],
    # Winsen WAV/WAP/WP-series all-in-one modules
    "wai01": ["uart"],
    "wap01": ["uart"],
    "wav01": ["uart"],
    "wav03": ["uart"],
    "wav04": ["uart"],
    "wav05": ["uart"],
    "wpah01": ["uart"],
    "wpah31": ["uart"],
    "wpak63": ["uart"],
    "wpak63j": ["uart"],
    "wpak64": ["uart"],
    "wpak65": ["uart"],
    "wpak66": ["uart"],
    "wpak67": ["uart"],
    "wpak68": ["uart"],
    "wpak69": ["uart"],
    "wpak70": ["uart"],
    "wpas01": ["uart"],
    "wpas02": ["uart"],
    "wpas12": ["uart"],
    "wpbh01": ["uart"],
    "wpch01": ["uart"],
    "wpch04": ["uart"],
    "wpck03": ["uart"],
    "wpck05": ["uart"],
    "wpck07": ["uart"],
    "wpck08": ["uart"],
    "wpck62": ["uart"],
    "wpck81": ["uart"],
    "wpck89": ["uart"],
    "wpi430": ["uart"],
    "wvi01": ["uart"],
    "wvv01": ["uart"],
    # Winsen misc
    "wsm8000a": ["analog"],
    "wsp2110": ["analog"],
    "wsuscgl": ["analog"],
    "yds13": ["uart"],
    "zc01": ["analog"],
    "zc02": ["analog"],
    "zc41": ["analog"],
    "zc601": ["uart"],
    "zc61": ["analog"],
    "zce04b": ["uart"],
    "zh101": ["uart"],
    "zh401": ["uart"],
    "zi100zi101": ["uart"],
    "zl940v3c": ["uart"],
    "zs03": ["uart"],
    "zs0301": ["uart"],
    "zs05": ["uart"],
    "mtp40": ["uart"],
    "mtp40f": ["uart"],
    "mts4x": ["uart"],
    "zph07": ["uart"],
    # Winsen ME2/ME3/ME4 raw electrochemical cells (analog output)
    "me2c2h5oh1313": ["analog"],
    "me2c2h5oh16": ["analog"],
    "me2ch2o16": ["analog"],
    "me2ch2o1615": ["analog"],
    "me2co": ["analog"],
    "me2co14x14": ["analog"],
    "me2co14x5": ["analog"],
    "me2co14x50c": ["analog"],
    "me2o220": ["analog"],
    "me2o3": ["analog"],
    "me2o316x15": ["analog"],
    "me3c2h3cl": ["analog"],
    "me3c2h4": ["analog"],
    "me3c2h6s": ["analog"],
    "me3c2h6s2": ["analog"],
    "me3c3h9n": ["analog"],
    "me3c6h6": ["analog"],
    "me3c7h8": ["analog"],
    "me3c8h8": ["analog"],
    "me3ch2chcl": ["analog"],
    "me3ch2o": ["analog"],
    "me3ch4s": ["analog"],
    "me3cl2": ["analog"],
    "me3co": ["analog"],
    "me3cs2": ["analog"],
    "me3eto": ["analog"],
    "me3h2": ["analog"],
    "me3h2s": ["analog"],
    "me3hcl": ["analog"],
    "me3hcn": ["analog"],
    "me3hf": ["analog"],
    "me3nh3": ["analog"],
    "me3no2": ["analog"],
    "me3o3": ["analog"],
    "me3ph3": ["analog"],
    "me3so2": ["analog"],
    "me4cl2": ["analog"],
    "me4co": ["analog"],
    "me4coe4": ["analog"],
    "me4eto": ["analog"],
    "me4h2": ["analog"],
    "me4h2s": ["analog"],
    "me4nh3": ["analog"],
    "me4no2": ["analog"],
    "me4so2": ["analog"],
    "medo2la": ["analog"],
    "medo2lb": ["analog"],
    "mesco": ["analog"],
    "meu2co": ["analog"],
    "meu2o2": ["analog"],
    "meuco": ["analog"],
    "meuh2s": ["analog"],
    "meuo2": ["analog"],
    "mevgh01": ["analog"],
    "uenh3": ["analog"],
    "sc03c2h5oh": ["analog"],

    # ===== MQ-series (Winsen semiconductor gas sensors, analog output) =====
    "mq131": ["analog"],
    "mq135": ["analog"],
    "mq136": ["analog"],
    "mq137": ["analog"],
    "mq138": ["analog"],
    "mq2": ["analog"],
    "mq2b": ["analog"],
    "mq2lpg": ["analog"],
    "mq303b": ["analog"],
    "mq316": ["analog"],
    "mq3b": ["analog"],
    "mq4": ["analog"],
    "mq4b": ["analog"],
    "mq5": ["analog"],
    "mq5b": ["analog"],
    "mq6": ["analog"],
    "mq7b": ["analog"],
    "mq8": ["analog"],
    "mq9b": ["analog"],

    # ===== Sensors restored from SKIP_IDS =====
    "cc1101": ["spi"],            # TI CC1101 RF transceiver — SPI interface
    "tal220": ["analog"],         # Load cell — analog strain gauge
    "tal220b": ["analog"],
    "tal221": ["analog"],
    "fsr16x16bnl": ["analog"],    # Force sensing resistor — analog
    "gl5528": ["analog"],         # LDR photoresistor — analog
    "fc28": ["analog"],           # Soil moisture — analog
    "fc37": ["analog"],           # Rain sensor — analog
    "ky040": ["gpio"],            # Rotary encoder — GPIO
    "sr04m": ["gpio"],            # AJ-SR-04M ultrasonic — GPIO trigger/echo
    "tct40": ["gpio"],            # TCT40 ultrasonic transducer — GPIO
    "me007": ["uart"],            # ME007 ultrasonic — UART
    "us100": ["uart", "gpio"],    # US-100 ultrasonic — UART or GPIO
    "fingerprintgrow": ["uart"],  # Grow fingerprint module — UART
    "ms01": ["uart"],             # Sonoff MS01 moisture sensor
    "gy26": ["uart", "i2c"],      # GY-26 compass module
    "pt100": ["analog"],          # PT100 RTD — analog resistance
    "yfs201waterflow": ["gpio"],  # YF-S201 flow — Hall pulse output

    # ===== Other missing protocols =====
    "tas501": ["analog"],         # ASAIR load cell amplifier
    "tas606": ["analog"],
    "usd1": ["uart"],             # Ainstein USD1 radar — UART
    "dts6012m": ["uart"],         # Amphenol ToF — UART
    "dct532": ["i2c"],            # Analog Microelectronics pressure — I2C
    "lc02": ["uart"],             # Benewake LC02 ToF — UART
    "pm1": ["uart"],              # Bosch PM1 particle — UART
    "ec10": ["analog"],           # DFRobot EC10 electrochemical
    "son1303": ["i2c"],           # DFRobot SON1303 light
    "fg3": ["analog"],            # FGSensors Hall-effect
    "i2casdx": ["i2c"],           # Honeywell ASDX pressure — I2C
    "tx07k": ["gpio"],            # La Crosse TX07K — RF/GPIO
    "zpa4756": ["i2c", "spi"],    # Murata ZPA4756 pressure — I2C/SPI
    "xycals21c": ["i2c"],         # NEWOPTO ALS21C light — I2C
    "omrond6fph": ["i2c"],        # Omron D6F-PH flow — I2C
    "pm25": ["uart"],             # Plantower PM25 — UART
    "sciosenseas60xx": ["i2c"],   # ScioSense AS60XX ultrasonic — I2C
    "sciosenseens16x": ["i2c"],   # ScioSense ENS16x gas — I2C
    "sciosenseens21x": ["i2c"],   # ScioSense ENS21x humidity — I2C
    "ufm01": ["i2c"],             # ScioSense UFM01 ultrasonic — I2C
    "ufm02": ["i2c"],             # ScioSense UFM02 ultrasonic — I2C
    "ct1780": ["one_wire"],       # Sensylink CT1780 thermocouple — 1-Wire
    "at407": ["i2c"],             # SparkFun AT407 pressure — I2C
    "icu10201": ["i2c"],          # TDK ICUX0201 ultrasonic — I2C
    "tad2144": ["i2c"],           # TDK TAD2144 — I2C
    "msp300": ["analog"],         # TE MSP300 pressure — analog
    "sm9000": ["i2c"],            # TE SM9000 flow — I2C
    "ts4231": ["gpio"],           # Triad photodiode — GPIO
    "ts8000": ["gpio"],           # Triad ultrasonic — GPIO
    "sd3031": ["i2c"],            # WHWAVE SD3031 RTC — I2C
    "im19": ["uart"],             # Yostlabs IM19 tilt — UART
    "i2cirsense": ["i2c"],        # ams-OSRAM IR thermopile — I2C
    "meloperosamm8q": ["i2c", "uart"],  # u-blox SAM-M8Q GNSS — I2C/UART
    "ximu3": ["uart", "usb"],     # x-io XIMU3 — UART/USB

    # ===== IoTy LiDAR modules =====
    "iotycoind4": ["uart"],       # COIN-D4 spinning LiDAR — UART
    "iotydelta2d": ["uart"],      # Delta-2D spinning LiDAR — UART
    "iotylds02rr": ["uart"],      # LDS02RR spinning LiDAR — UART

    # ===== Winsen flow/Hall sensors =====
    "f1012": ["gpio"],            # Winsen F1012 flow — Hall pulse
    "f1032": ["gpio"],            # Winsen F1032 flow — Hall pulse
    "ea134": ["analog"],          # Winsen EA-134 vibration — analog
    "gm1602": ["analog"],         # Winsen GM1602 CO — analog
    "msz202": ["uart"],           # Winsen MS-Z202 humidity — UART
    "msz302": ["uart"],           # Winsen MS-Z302 humidity — UART
    "sp3s": ["analog"],           # Winsen SP3S gas — analog
    # --- Best Modules Corp (Holtek) sensor modules ---
    "bme82m131a": ["i2c"],          # BME82M131A VEML7700 light — I2C
    "bmh05102": ["uart"],           # BMH05102 body fat scale: page lists none, datasheet V1.0.1 "UART interface"
    # HT7M21xx PIR modules: "Optional communication interfaces: I2C or I/O" (datasheet V1.50)
    "ht7m2126": ["gpio", "i2c"],
    "ht7m2127": ["gpio", "i2c"],
    "ht7m2136": ["gpio", "i2c"],
    "ht7m2156": ["gpio", "i2c"],
    "ht7m2176": ["gpio", "i2c"],
    "adc128d818": ["i2c"],
    "ads122c04": ["i2c"],
    "afs01": ["i2c"],
    "bma580": ["i2c", "i3c", "spi"],
    "d6fw04a1": ["analog"],
    "ina229": ["spi"],
    "it7259": ["i2c"],
    "mt6826s": ["gpio", "pwm", "spi"],
    "sciosenseens17x": ["i2c", "spi"],
    "spd1200": ["uart"],
    "tla2021": ["i2c"],
    "tsw10": ["analog"],
    "ze40b": ["uart"],
    "acs37800": ["i2c", "spi"],
    "mb7040": ["i2c"],
    "mb7137": ["i2c"],
    "mb8000": ["i2c", "uart"],
    "mb1000": ["analog", "pwm", "uart"],
    "mb1001": ["gpio", "uart"],
    "mb1002": ["gpio", "uart"],
    "mb1003": ["analog", "pwm", "uart"],
    "mb1004": ["gpio", "uart"],
    "mb1005": ["gpio", "uart"],
    "mb1006": ["gpio", "uart"],
    "mb1007": ["gpio", "uart"],
    "mb1008": ["gpio", "uart"],
    "mb1009": ["gpio", "uart"],
    "mb1010": ["analog", "pwm", "uart"],
    "mb1013": ["analog", "pwm", "uart"],
    "mb1014": ["gpio", "uart"],
    "mb1020": ["analog", "pwm", "uart"],
    "mb1023": ["analog", "pwm", "uart"],
    "mb1024": ["gpio", "uart"],
    "mb1030": ["analog", "pwm", "uart"],
    "mb1033": ["analog", "pwm", "uart"],
    "mb1034": ["gpio", "uart"],
    "mb1040": ["analog", "pwm", "uart"],
    "mb1043": ["analog", "pwm", "uart"],
    "mb1044": ["gpio", "uart"],
    "mb1200": ["analog", "pwm", "uart"],
    "mb1202": ["i2c"],
    "mb1210": ["analog", "pwm", "uart"],
    "mb1212": ["i2c"],
    "mb1220": ["analog", "pwm", "uart"],
    "mb1222": ["i2c"],
    "mb1230": ["analog", "pwm", "uart"],
    "mb1232": ["i2c"],
    "mb1240": ["analog", "pwm", "uart"],
    "mb1242": ["i2c"],
    "mb1260": ["analog", "pwm", "uart"],
    "mb1261": ["analog", "pwm", "uart"],
    "mb1300": ["analog", "uart"],
    "mb1310": ["analog", "uart"],
    "mb1320": ["analog", "uart"],
    "mb1330": ["analog", "uart"],
    "mb1340": ["analog", "uart"],
    "mb1360": ["analog", "uart"],
    "mb1361": ["analog", "uart"],
    "mb1403": ["usb"],
    "mb1413": ["usb"],
    "mb1414": ["usb"],
    "mb1423": ["usb"],
    "mb1424": ["usb"],
    "mb1433": ["usb"],
    "mb1434": ["usb"],
    "mb1443": ["usb"],
    "mb1444": ["usb"],
    "mb1603": ["analog", "pwm", "uart"],
    "mb1604": ["analog", "pwm", "uart"],
    "mb1613": ["analog", "pwm", "uart"],
    "mb1614": ["analog", "pwm", "uart"],
    "mb1623": ["analog", "pwm", "uart"],
    "mb1624": ["analog", "pwm", "uart"],
    "mb1633": ["analog", "pwm", "uart"],
    "mb1634": ["analog", "pwm", "uart"],
    "mb1643": ["analog", "pwm", "uart"],
    "mb1644": ["analog", "pwm", "uart"],
    "mb1710": ["usb"],
    "mb1711": ["usb"],
    "mb1712": ["i2c"],
    "mb2530": ["analog", "pwm", "uart"],
    "mb2532": ["analog", "uart"],
    "mb7051": ["analog", "pwm", "uart"],
    "mb7052": ["analog", "pwm", "uart"],
    "mb7053": ["analog", "pwm", "uart"],
    "mb7060": ["analog", "pwm", "uart"],
    "mb7062": ["analog", "pwm", "uart"],
    "mb7066": ["analog", "pwm", "uart"],
    "mb7070": ["analog", "uart"],
    "mb7076": ["analog", "uart"],
    "mb7092": ["analog", "uart"],
    "mb7138": ["analog", "pwm", "uart"],
    "mb7139": ["analog", "pwm", "uart"],
    "mb7150": ["analog", "uart"],
    "mb7155": ["analog", "uart"],
    "mb7354": ["analog", "pwm", "uart"],
    "mb7360": ["analog", "pwm", "uart"],
    "mb7363": ["analog", "pwm", "uart"],
    "mb7364": ["analog", "pwm", "uart"],
    "mb7366": ["analog", "pwm", "uart"],
    "mb7368": ["analog", "pwm", "uart"],
    "mb7369": ["analog", "pwm", "uart"],
    "mb7374": ["analog", "pwm", "uart"],
    "mb7375": ["analog", "pwm", "uart"],
    "mb7380": ["analog", "pwm", "uart"],
    "mb7383": ["analog", "pwm", "uart"],
    "mb7384": ["analog", "pwm", "uart"],
    "mb7386": ["analog", "pwm", "uart"],
    "mb7388": ["analog", "pwm", "uart"],
    "mb7389": ["analog", "pwm", "uart"],
    "mb7395": ["analog", "pwm", "uart"],
    "mb7534": ["analog", "pwm", "uart"],
    "mb7544": ["analog", "pwm", "uart"],
    "mb7554": ["analog", "pwm", "uart"],
    "mb7560": ["analog", "pwm", "uart"],
    "mb7563": ["analog", "pwm", "uart"],
    "mb7564": ["analog", "pwm", "uart"],
    "mb7566": ["analog", "pwm", "uart"],
    "mb7568": ["analog", "pwm", "uart"],
    "mb7569": ["analog", "pwm", "uart"],
    "mb7574": ["analog", "pwm", "uart"],
    "mb7580": ["analog", "pwm", "uart"],
    "mb7583": ["analog", "pwm", "uart"],
    "mb7584": ["analog", "pwm", "uart"],
    "mb7586": ["analog", "pwm", "uart"],
    "mb7588": ["analog", "pwm", "uart"],
    "mb7589": ["analog", "pwm", "uart"],
    "mb7850": ["analog", "uart"],
    "mb7851": ["analog", "uart"],
    "mb7853": ["analog", "uart"],
    "mb7854": ["analog", "uart"],
    "mb8460": ["uart"],
    "mb8480": ["uart"],
    "mb7072": ["analog", "uart"],
    "mb7334": ["analog", "pwm", "uart"],
    "mb7344": ["analog", "pwm", "uart"],
    "mb8450": ["usb"],
}

# Winsen sensor type -> protocol mapping.
# Applied to Winsen-sourced sensors that have a `type` but no protocol data,
# and were NOT already handled by IC_PROTOCOLS.
WINSEN_TYPE_PROTOCOLS: dict[str, list[str]] = {
    "ndir": ["uart"],
    "laser": ["uart"],
    "electrochemical": ["uart"],
    "semiconductor": ["analog"],
    "catalytic": ["analog"],
    "pir": ["analog"],
    "pyroelectric": ["analog"],
    "photoresistor": ["analog"],  # PbS/PbSe photoconductive flame cells (REF-X2212)
    "thermopile": ["analog"],
    "thermal_conduction": ["analog"],
    "mems": ["i2c"],
    "pid": ["analog"],
}

# Legacy MaxSonar output set; apply only to documented MaxSonar product families.
MAXBOTIX_PROTOCOLS = ["analog", "uart", "pwm"]

# Benewake interfaces come from the scraper (the product menu's Interface row per model). The
# former UART+I2C default for every Benewake part contradicted that row for CAN/RS-485-only
# (TF02-i, TFmini-i), RS-232-only (TFA170-L) and Ethernet (Horn) parts, so there is none.

# Hi-Link radar modules (LD-series) — all use UART
HILINK_RADAR_PROTOCOLS = ["uart"]
HILINK_IMU_PROTOCOLS = ["uart"]

# Atlas EZO/OEM digital circuits; probes and Surveyor meters have separate outputs.
ATLAS_SCIENTIFIC_PROTOCOLS = ["i2c", "uart"]


def enrich_protocols(merged: dict[str, dict], quiet: bool = False) -> int:
    """Fill in protocols from IC lookup table and manufacturer defaults.

    Only adds protocols where none exist from any source — never overrides
    existing protocol data.

    Returns the number of sensors enriched.
    """
    enriched = 0

    for sid, sensor in merged.items():
        had_protocols = bool(sensor["protocols"])
        added = False

        # 1. IC protocol lookup — union (adds secondary interfaces like SPI). Winsen product pages
        # state each part's outputs, so for a Winsen part the table only fills one whose page names
        # none: its blanket guesses ("WAV/WAP/WP-series all-in-one modules": UART) gave 4-20 mA
        # transmitters, millivolt pressure cores and CAN modules a UART.
        if sid in IC_PROTOCOLS and not ("winsen" in sensor.get("sources", ()) and had_protocols):
            new_protos = set(IC_PROTOCOLS[sid]) - sensor["protocols"]
            if new_protos:
                sensor["protocols"].update(IC_PROTOCOLS[sid])
                added = True

        # 2. Winsen type->protocol mapping (only when no protocol data at all)
        if not had_protocols and not added and "winsen" in sensor["sources"] and sensor.get("type"):
            stype = sensor["type"].lower()
            if stype in WINSEN_TYPE_PROTOCOLS:
                sensor["protocols"].update(WINSEN_TYPE_PROTOCOLS[stype])
                added = True

        # MaxBotix outputs are model-specific; supplied by the scraper or IC lookup.

        # 5. Hi-Link modules
        if not added and "hilink" in sensor["sources"]:
            stype = (sensor.get("type") or "").lower()
            if stype == "radar":
                sensor["protocols"].update(HILINK_RADAR_PROTOCOLS)
                added = True
            elif stype == "imu":
                sensor["protocols"].update(HILINK_IMU_PROTOCOLS)
                added = True

        # 6. Atlas digital circuits only; never infer a probe's bus from its reader.
        if not had_protocols and not added and "atlas_scientific" in sensor["sources"] and (
            (sid.startswith("ezo") and not sid.startswith("ezocomplete")) or sid.endswith("oem")
        ):
            sensor["protocols"].update(ATLAS_SCIENTIFIC_PROTOCOLS)
            added = True

        if added:
            enriched += 1

    if not quiet:
        print(f"  Enriched {enriched} sensors with protocol data")

    return enriched


SCHEMA_SQL = """
CREATE TABLE sensors (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    manufacturer TEXT,
    type TEXT,
    voltage TEXT,
    datasheet_url TEXT,
    platform_count INTEGER DEFAULT 0,
    description TEXT,
    source_tier TEXT DEFAULT 'primary',
    sources TEXT
);

CREATE TABLE sensor_measures (
    sensor_id TEXT NOT NULL REFERENCES sensors(id),
    measure TEXT NOT NULL,
    PRIMARY KEY (sensor_id, measure)
);

CREATE TABLE sensor_protocols (
    sensor_id TEXT NOT NULL REFERENCES sensors(id),
    protocol TEXT NOT NULL,
    PRIMARY KEY (sensor_id, protocol)
);

CREATE TABLE sensor_platforms (
    sensor_id TEXT NOT NULL REFERENCES sensors(id),
    platform TEXT NOT NULL,
    PRIMARY KEY (sensor_id, platform)
);

CREATE TABLE sensor_urls (
    sensor_id TEXT NOT NULL REFERENCES sensors(id),
    url TEXT NOT NULL,
    PRIMARY KEY (sensor_id, url)
);
"""

INDEX_SQL = """
CREATE INDEX idx_sensor_platform_count ON sensors(platform_count DESC);
CREATE INDEX idx_sensor_type ON sensors(type);
CREATE INDEX idx_sensor_measure ON sensor_measures(measure);
CREATE INDEX idx_sensor_protocol ON sensor_protocols(protocol);
CREATE INDEX idx_sensor_platform ON sensor_platforms(platform);
"""

FTS_SQL = """
CREATE VIRTUAL TABLE sensors_fts USING fts5(id, name, manufacturer, description);
INSERT INTO sensors_fts(id, name, manufacturer, description)
    SELECT id, name, COALESCE(manufacturer, ''), COALESCE(description, '') FROM sensors;
"""


# Brand/vendor names to strip from names and descriptions
_BRANDS = r"(?:SparkFun|DFRobot|Adafruit|ProtoCentral|BlueDot|Deneyap|7Semi|Seeed|Grove)"

# Name cleaning patterns (applied in order)
_NAME_CLEAN = [
    # Strip leading underscores (DFRobot library naming: _BME280, _AS6221)
    re.compile(r"^_+"),
    # Strip brand names
    re.compile(rf"{_BRANDS}\s*", re.IGNORECASE),
    # Strip "Arduino Library", "Library", "boards library" suffixes
    re.compile(r"\s+(?:Arduino\s+)?(?:[Ll]ibrary|boards\s+library)\s*$"),
    # Strip "-Library" suffix (e.g., "MAX31855-Library")
    re.compile(r"-Library$", re.IGNORECASE),
    # Strip "Breakout" / "Qwiic" / "(Qwiic)" product terms
    re.compile(r"\s*\(Qwiic\)", re.IGNORECASE),
    re.compile(r"\bQwiic\b\s*", re.IGNORECASE),
    re.compile(r"\bBreakout\b\s*-?\s*", re.IGNORECASE),
    # Strip noise suffixes: -driver, -sensor, _CurrentSensor, etc.
    re.compile(r"[-_](?:driver|(?:\w+)?[Ss]ensor|temp-sensor)\s*$", re.IGNORECASE),
    # Strip trailing " Sensor" (but keep text before it, e.g. "AK9750 Human Presence Sensor" -> "AK9750 Human Presence")
    re.compile(r"\s+Sensor\s*$", re.IGNORECASE),
    # Strip generic product terms
    re.compile(r"\bArduino\b\s*", re.IGNORECASE),
    # Strip "RAKwireless" brand
    re.compile(r"\bRAKwireless\b\s*", re.IGNORECASE),
    # Strip "Soldered" brand prefix
    re.compile(r"\bSoldered\b\s*", re.IGNORECASE),
    # Collapse multiple spaces / leading dashes
    re.compile(r"\s{2,}"),
    re.compile(r"^\s*-\s*"),
]

# Description cleaning patterns (applied in order)
_DESC_CLEAN = [
    # Strip "DFRobot Standard library(SKU:...)." lines first
    re.compile(r"DFRobot Standard library(?:\s+for\s+(?:the\s+)?|\S*\.?\s*)", re.IGNORECASE),
    # Strip "Easy to use <IC>." — these are empty-calorie descriptions
    re.compile(r"^Easy to use \w+\.?\s*$", re.IGNORECASE),
    # Strip "A library for/to/of/that ..." preamble — keep the useful part after it
    re.compile(
        r"^A library\s+"
        r"(?:for|to|of|that|written for \w+ that)\s+"
        r"(?:interface with|interfacing with|interacting with|communicate with|"
        r"control|read|support|"
        r"make(?:s)?\s+(?:it\s+)?easy(?:er)?\s+(?:to\s+)?us(?:e|ing))\s+"
        r"(?:the\s+)?",
        re.IGNORECASE,
    ),
    # Broader: "A library for/to/of ..." (simpler preambles without verb)
    re.compile(r"^A library\s+(?:for|to|of)\s+(?:the\s+)?", re.IGNORECASE),
    # Strip "Driver for (the) (manufacturer) ..." preamble — keep the IC part
    re.compile(
        r"^Driver for\s+(?:the\s+)?"
        r"(?:(?:ST|TI|NXP|Bosch|Sensirion|Honeywell|Vishay|Melexis|Infineon|"
        r"Microchip|Broadcom|Renesas|Allegro|Panasonic|Plantower|ROHM|Murata|"
        r"Omron|InvenSense|Iowa Scaled Engineering)(?:'s)?\s+)?",
        re.IGNORECASE,
    ),
    # Strip "The SparkFun" / "This SparkFun" etc. prefixes
    re.compile(rf"\b(?:The|This)\s+{_BRANDS}\s+", re.IGNORECASE),
    # Strip remaining bare brand names anywhere except inside a URL or host name: removing it
    # from "https://cdn-shop.adafruit.com/datasheets/tmp007.pdf" left "cdn-shop..com"
    re.compile(rf"(?<![\w./-]){_BRANDS}(?!\.\w)\s*", re.IGNORECASE),
    # Strip SKU references like "(SKU:SEN0206/SEN0263)"
    re.compile(r"\s*\(SKU[:\s][^)]*\)", re.IGNORECASE),
    # Strip trailing period if description is very short after cleaning
    re.compile(r"\.\s*$"),
]


def clean_name(name: str, sensor_id: str = "") -> str:
    """Use the complete model identity, preserving its source punctuation.

    A sibling or family sharing three letters is not evidence for a model's
    name. Only a complete token matching the ID can supply display spelling.
    Reviewed exceptions are applied later via curated.json.
    """
    for pat in _NAME_CLEAN:
        name = pat.sub(" " if pat.pattern.startswith(r"\s{2") else "", name)
    # Collapse spaces, strip punctuation and leading underscores
    cleaned = re.sub(r"\s{2,}", " ", name).strip(" -,_")

    if sensor_id:
        if re.sub(r"[^a-z0-9]", "", cleaned.lower()) != sensor_id:
            model = r"[\s_.-]*".join(re.escape(c) for c in sensor_id)
            match = re.search(r"(?<![a-z0-9])" + model + r"(?![a-z0-9])", cleaned, re.I)
            cleaned = match.group().upper() if match else sensor_id.upper()

    # If the cleaned name is all lowercase and looks like a raw IC ID
    # (no spaces, just alphanumeric+underscore), uppercase it
    if cleaned and cleaned == cleaned.lower() and " " not in cleaned:
        cleaned = cleaned.upper()

    return cleaned or sensor_id.upper()


_SOFTWARE_PREFIX = re.compile(
    r"^(?:An\s+)?(?:Arduino\s+library|MicroPython\s+(?:driver|module)|Library)"
    r"\s+for\s+(?:the\s+)?", re.IGNORECASE,
)
_SENSING = re.compile(
    r"\b(?:sensor|accelerometer|gyroscope|magnetometer|encoder|imu|adc|"
    r"transducers?|thermistors?|thermopile|spectrometer|altimeter|"
    r"(?:power|energy)\s+monitor|flow\s+(?:converter|sensing)|"
    r"particulate\s+(?:matter\s+)?(?:sensing|sensors)|"
    r"light\s+to\s+frequency\s+convertor|ambient\s+light\s+detection)\b|"
    r"\b(?:temperature|humidity|pressure)\b.*\bsensors\b", re.IGNORECASE,
)
_SOFTWARE = re.compile(
    # "Class for DHT11, DHT12, DHT21 and DHT22 Sensors" is a C++ class, not the part
    r"\b(?:librar\w*|drivers?|wrappers?|examples?|APIs?|functions|function\s+calls?|methods|classes|class\s+for|"
    r"implement\w*|code|firmware|sketch\w*|beginner[- ]friendly|register\s+access|"
    r"heading\s+helpers?|precision\s+control|optimized\s+for|support\s+for\s+Arduino|"
    r"for\s+(?:MicroPython|Arduino)|pure\s+Python|drive(?!-thru)|managing|"
    r"interfacing|communicating|controlling|interrupt[- ]based|dependenc(?:y|ies)|"
    # An application built around the part ("Current monitor using the INA219 and an SSD1306 OLED",
    # "Air Quality monitor using PMS5003 sensor and WiPy") is not the part's own description
    r"SSD1306|OLED|WiPy|monitor\s+using)\b|^reading\b|\ballows\s+reading\b", re.IGNORECASE,
)
_BOARD_PROSE = re.compile(
    r"\b(?:boards?|shields?|breakouts?|development\s+kit|platform\s+for|"
    r"Wemos|Trinket|Gemma|your|our|projects?|easy-to-use|professional-grade|"
    r"unprecedented|pocket-sized|micro-sized|sewable)\b", re.IGNORECASE,
)
_PREFIX_REMAINDER_PROSE = re.compile(
    r"\b(?:librar\w*|drivers?|Arduino|MicroPython|boards?|shields?|breakouts?|"
    r"examples?|protocol)\b", re.IGNORECASE,
)


def strip_software_prefix(description: str) -> str:
    """Remove only a preamble that leaves a sensing description, not more prose."""
    remainder = _SOFTWARE_PREFIX.sub("", description)
    if (remainder != description and _SENSING.search(remainder)
            and not _PREFIX_REMAINDER_PROSE.search(remainder)):
        return remainder
    return description


_BINDING_BOUNDARY = re.compile(
    r"\bWhen\s+setting\b|\bThis\s+(?:driver|binding)\b|"
    r"\bThis\s+sensor\s+requires\b(?=[^.!?]*\bpinctrl\b)|\bThe\s+<zephyr/dt-bindings/|"
    r"\bNOTES:\s*This\s+driver\b|\bDriver\s+based\s+on\b|"
    r"\bSPI\s+mode\s+is\s+currently\b|"
    r"\bAdditionally\s+use\b|&[\w]+\s*\{", re.IGNORECASE,
)


def trim_zephyr_description(description: str) -> str:
    """Cut at binding prose/code, preserving every preceding hardware sentence."""
    boundary = _BINDING_BOUNDARY.search(description)
    if not boundary:
        return description
    hardware = description[:boundary.start()].rstrip()
    # A reference link immediately before instructions is not a hardware sentence.
    hardware = re.sub(r"\s+See\s+(?:more info at:?\s+|datasheet at\s+)?https?://\S+\s*$",
                      "", hardware, flags=re.IGNORECASE)
    return hardware.rstrip()


def description_quality(description: str) -> int:
    """Hardware facts beat software prose; board marketing cannot displace a title.

    A removable library preamble still ranks below an independent hardware text.
    Keep that distinction when ranking raw input, before displaying cleaned text.
    """
    if not description:
        return -1
    remainder = strip_software_prefix(description)
    if _BOARD_PROSE.search(remainder):
        return 0
    if _SOFTWARE.search(remainder):
        return 0
    # Text naming a software platform is library copy ("Arduino Temp & Humidity Sensors for DHT11
    # and DHT22"); an independent hardware text wins a tie with it.
    if remainder != description or _PLATFORM_PROSE.search(remainder):
        return 1
    return 2


_PLATFORM_PROSE = re.compile(r"\b(?:Arduino|MicroPython|CircuitPython)\b", re.IGNORECASE)


def has_software_prose(description: str) -> bool:
    """Identify remaining prose for review, without inventing replacement facts."""
    return bool(_SOFTWARE.search(description) or re.search(
        r"\b(?:Arduino|MicroPython|Python|ESP8266|ESP32|beginner[- ]friendly)\b",
        description, re.IGNORECASE,
    ))


def clean_description(desc: str, *, strip_prefix: bool = True) -> str:
    """Strip brand names and boilerplate from descriptions.

    After pattern cleaning, also discards results that are just a bare IC name
    (e.g. "GSL1680") or a bare IC name + generic suffix like "-sensor".
    """
    for pat in _DESC_CLEAN:
        desc = pat.sub("", desc)
    desc = desc.strip(" -,_")
    if strip_prefix:
        desc = strip_software_prefix(desc)
    # If cleaned result is just an IC-like identifier (alphanumeric, possibly
    # with hyphens/underscores), it carries no search value — discard it
    if desc and re.match(r'^[A-Za-z0-9][-A-Za-z0-9_]*$', desc) and len(desc) < 30:
        return ""
    return desc


# Maker pages (mostly Winsen and Best Modules) use full-width punctuation, invisible
# spaces, list bullets and subscript digits. CO₂ and CH₄ also hide "CO2"/"CH4" from search.
_TEXT_TIDY = str.maketrans({
    "（": "(", "）": ")", "，": ", ", "、": ", ", "：": ": ", "～": "~",
    " ": " ", "​": "", "⬥": "-", "◆": "-",
    **{chr(0x2080 + d): str(d) for d in range(10)},
})


def tidy_text(text: str | None) -> str | None:
    """ASCII punctuation, plain digits and single spaces for stored descriptions."""
    if not text:
        return text
    return re.sub(r"\s{2,}", " ", text.translate(_TEXT_TIDY)).strip()


DESCRIPTION_LIMIT = 200
_CUT_MARK = re.compile(r"\s*(?:\.{2,}|…)\s*$")
_SENTENCE_END = re.compile(r"[.!?](?=\s|$)")


def fit_description(text: str | None, limit: int = DESCRIPTION_LIMIT) -> str | None:
    """Fit a description in the stored column, ending at a sentence rather than mid-word.

    Scrapers cut long text at 197 characters plus "...", and the column at 200, which stopped
    descriptions mid-word or mid-number ("The DHT11 ..", "0~500ppm: 0.1ppm - 500p.."). A cut
    text keeps its complete sentences when they hold at least 40% of the limit; otherwise it
    ends at the last whole word, marked "...". Text that fits and wasn't cut is unchanged: a
    short text ending in ".." is the source's own wording ("ammonia, alcohol.."), not a cut.
    """
    if not text:
        return None
    cut = _CUT_MARK.search(text) if len(text) >= limit - 15 else None
    if len(text) <= limit and not cut:
        return text
    body = (text[:cut.start()] if cut else text)[:limit - 3]
    ends = [m.end() for m in _SENTENCE_END.finditer(body)]
    if ends and ends[-1] >= limit * 0.4:
        return body[:ends[-1]]
    words = body.rsplit(" ", 1)[0] if " " in body else body
    return words.rstrip(" ,;:-") + "..."


def normalize_manufacturer(name: str | None) -> str | None:
    """Normalize manufacturer name via alias table."""
    if not name:
        return None
    key = name.strip().lower()
    return MANUFACTURER_ALIASES.get(key, name.strip())


def load_aliases(data_dir: Path) -> dict[str, str]:
    """Load IC alias mapping (alias_id -> canonical_id)."""
    alias_file = data_dir / "sensors" / "ic_aliases.json"
    if not alias_file.exists():
        return {}
    with open(alias_file, encoding="utf-8") as f:
        return json.load(f)


def apply_curated(merged: dict[str, dict], data_dir: Path) -> list[str]:
    """Validate and apply field-level corrections after every enrichment rule.

    IDs are canonical merged record IDs, not aliases. Validate the whole file
    before mutating records so undocumented edits abort the build. An ID with no
    record (a part that left every source after three missed scrapes, or whose
    pages are gone) is skipped with a warning and returned: failing would make the
    catalog build that gates the monthly scrape discard every source's data.
    tests/test_sensor_db.py requires every curated ID to exist, so typos still fail.
    """
    path = data_dir / "sensors" / "curated.json"
    if not path.exists():
        return []
    corrections = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(corrections, dict):
        raise ValueError(f"{path}: expected an object keyed by sensor ID")
    stale: list[str] = []
    scalar_fields = {"name", "description", "manufacturer", "type", "voltage", "datasheet_url"}
    nullable_fields = {"manufacturer", "type", "voltage", "datasheet_url"}
    for sid, fields in corrections.items():
        exclusion = fields.get("exclude") if isinstance(fields, dict) else None
        if sid not in merged and not (isinstance(exclusion, dict) and exclusion.get("value") is True):
            stale.append(sid)
        if not isinstance(fields, dict) or not fields:
            raise ValueError(f"{path}: {sid}: expected field corrections")
        for field, correction in fields.items():
            context = f"{path}: {sid}.{field}"
            if field not in scalar_fields | {"measures", "protocols", "exclude"}:
                raise ValueError(f"{context}: unsupported curated field")
            if not isinstance(correction, dict) or "value" not in correction:
                raise ValueError(f"{context}: missing value")
            evidence = correction.get("evidence")
            if not isinstance(evidence, dict) or not (
                (isinstance(evidence.get("url"), str) and re.match(r"https?://\S+$", evidence["url"]))
                or (isinstance(evidence.get("document"), str) and evidence["document"].strip()
                    and isinstance(evidence.get("page"), int) and evidence["page"] > 0)
                or (isinstance(evidence.get("source"), str) and evidence["source"].strip()
                    and isinstance(evidence.get("text"), str) and evidence["text"].strip())
            ):
                raise ValueError(f"{context}: missing evidence (URL, document/page, or scraper source/text)")
            reviewed = correction.get("review_date")
            try:
                if not isinstance(reviewed, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", reviewed):
                    raise ValueError
                date.fromisoformat(reviewed)
            except ValueError:
                raise ValueError(f"{context}: review_date must be YYYY-MM-DD") from None
            value = correction["value"]
            if field in scalar_fields:
                if not (isinstance(value, str) and value.strip()) and not (value is None and field in nullable_fields):
                    raise ValueError(f"{context}: expected a nonempty string" + (" or null" if field in nullable_fields else ""))
                if field == "description" and len(value) > 200:
                    raise ValueError(f"{context}: description exceeds DB limit of 200 characters")
            elif field in {"measures", "protocols"}:
                if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value):
                    raise ValueError(f"{context}: expected an exact list of nonempty strings")
            elif not isinstance(value, bool) or not isinstance(correction.get("reason"), str) or not correction["reason"].strip():
                raise ValueError(f"{context}: exclude requires a boolean value and a reason")

    for sid, fields in corrections.items():
        if sid not in merged:  # A persistent exclusion can outlive its scraped record.
            continue
        sensor = merged[sid]
        for field, correction in fields.items():
            if field != "exclude":
                value = correction["value"]
                sensor[field] = set(value) if field in {"measures", "protocols"} else value
        # Measures have legacy additions/removals at insertion time; bypass them
        # only when an exact curated set is present.
        sensor["_curated_measures"] = "measures" in fields
        if fields.get("exclude", {}).get("value"):
            del merged[sid]
    if stale:
        print(f"  WARNING: {len(stale)} curated IDs have no record and were skipped: {', '.join(sorted(stale))}",
              file=sys.stderr)
    return stale


def strip_identity_prefixes(raw: str, known_ids=()) -> str:
    """Prefer known identities after removing vendor/library wrappers.

    Lookup also accepts digit-first models (24GHzRadar) and short stems
    (A02YYUW). Unknown models retain the conservative shape-based rule.
    Kept identical in the standalone database builder for Docker builds.
    """
    normalize = lambda value: re.sub(r"[^a-z0-9]", "", value.lower())
    library_prefixes = (
        "adafruit", "sparkfun", "dfrobot", "micropython", "esp", "circuitpython",
        "grove", "seeed", "closedcube", "bluedot", "artronshop", "sensirion",
        "protocentral", "stm32duino", "reefwing", "pwfusion", "arduino",
        "smarteverything", "bolderflight_systems", "bolderflightsystems",
    )
    prefixes = ("7semi", "microfire", "ioty", "hlk", "omron", "my") + library_prefixes
    pending = [raw]
    seen = set()
    while pending:
        candidate = pending.pop(0)
        key = normalize(candidate)
        if candidate != raw and key in known_ids:
            return candidate
        if key in seen:
            continue
        seen.add(key)
        for prefix in prefixes:
            if candidate.lower().startswith(prefix):
                rest = candidate[len(prefix):].lstrip(" _. -")
                if rest:
                    pending.append(rest)
    # For new models, strip library prefixes only at a separator boundary.
    stripped = re.sub(
        r"^(?:" + "|".join(library_prefixes) + r")[\s_.-]+", "", raw, flags=re.I,
    )
    if stripped != raw:
        return strip_identity_prefixes(stripped, known_ids)
    return re.sub(
        r"^(?:(?:7semi|microfire|ioty|hlk|omron)[\s_.-]*|my[\s_.-]*(?=[a-z]{2,}\d))"
        r"(?=[a-z]+[\s_.-]*\d)", "", raw, flags=re.IGNORECASE,
    )


def resolve_id(raw_id: str, aliases: dict[str, str], known_ids=()) -> str:
    """Resolve an IC ID through the alias table."""
    if raw_id in aliases:
        return aliases[raw_id]
    if raw_id in aliases.values():  # Preserve explicitly chosen, published module IDs.
        return raw_id
    normalized = re.sub(r"[^a-z0-9]", "", strip_identity_prefixes(raw_id, known_ids).lower())
    return aliases.get(normalized, normalized)


def transfer_platform_support(merged: dict[str, dict], data_dir: Path) -> None:
    """Attach reviewed multi-device driver support without merging identities.

    Only platform tags, driver URLs and provenance transfer. Measurements,
    descriptions and electrical specs of a software wrapper never transfer.
    Target metadata is used only to introduce a previously missing real part.
    """
    path = data_dir / "sensors" / "support_transfers.json"
    if not path.exists():
        return
    for origin, entry in json.loads(path.read_text(encoding="utf-8")).items():
        if not entry.get("evidence", {}).get("url") or not entry.get("targets"):
            raise ValueError(f"{path}: {origin}: targets and evidence URL required")
        driver = merged.get(origin)
        if driver is None:
            continue
        for part in entry["targets"]:
            sid = part["id"]
            if sid not in merged:
                if "measures" not in part:  # Reference to a part absent from this scrape.
                    continue
                merged[sid] = {
                    "id": sid, "name": part["name"], "manufacturer": part.get("manufacturer"),
                    "description": part["description"], "measures": set(part["measures"]),
                    "protocols": set(part.get("protocols", [])), "platforms": set(),
                    "type": None, "voltage": None, "datasheet_url": None,
                    "source_tier": "primary", "urls": [], "sources": [],
                }
            target = merged[sid]
            target["platforms"].update(driver["platforms"])
            for field in ("urls", "sources"):
                target[field].extend(value for value in driver[field] if value not in target[field])


def load_source(data_dir: Path, source_name: str) -> list[dict]:
    """Load sensors from a single source JSON file."""
    path = data_dir / "sensors" / f"{source_name}.json"
    if not path.exists():
        print(f"  Warning: {path} not found, skipping", file=sys.stderr)
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("sensors", [])


def description_rank(source: str, description: str, *, library_title: bool = False) -> tuple[int, int, int]:
    """Prefer hardware facts, then source authority, then length.

    Length breaks ties within the same authority; it cannot promote an all-in-one
    board's feature list into its component IC's description.
    """
    if not description:
        return (-1, -1, 0)
    authority = (0 if source in TIER3_SOURCES else
                 2 if source in {"esphome", "circuitpython", "zephyr"} or source not in {"arduino", "micropython", "tasmota"}
                 else 1)
    quality = description_quality(description)
    # Generic library/breakout copy must not replace a useful IC title. Promote
    # it across source tiers only when it identifies a part or gives a numeric spec.
    if source in TIER3_SOURCES | {"arduino", "micropython"} and quality == 2 and not re.search(
        r"\b[A-Za-z]{2,}[- ]?\d|\d+(?:\.\d+)?\s*(?:nm|[kM]?Hz|[mµu]?A|[mµu]?V|bit)\b",
        description,
    ):
        quality = 1
    if library_title and quality == 2:
        quality = 1
    return quality, authority, len(description)


def merge_sensors(data_dir: Path, aliases: dict[str, str], quiet: bool = False) -> dict[str, dict]:
    """Merge all sources into a single dict of sensor entries."""
    merged: dict[str, dict] = {}

    sources = {source: load_source(data_dir, source) for source in SOURCE_ORDER}
    known_ids = set(aliases) | set(aliases.values()) | SKIP_IDS
    known_ids.update(re.sub(r"[^a-z0-9]", "", raw.get("id", "").lower())
                     for sensors in sources.values() for raw in sensors)
    curated_path = data_dir / "sensors" / "curated.json"
    if curated_path.exists():
        known_ids.update(json.loads(curated_path.read_text(encoding="utf-8")))

    for source_name, sensors in sources.items():
        is_tier3 = source_name in TIER3_SOURCES

        if not quiet:
            print(f"  {source_name}: {len(sensors)} sensors")

        for raw in sensors:
            raw_id = raw.get("id", "").strip().lower()
            if not raw_id:
                continue

            canonical_id = resolve_id(raw_id, aliases, known_ids)
            if canonical_id in SKIP_IDS or raw_id in SKIP_IDS:
                continue

            existing = merged.get(canonical_id)

            # If the raw ID was an alias, the canonical ID's own entry
            # should override the name (e.g. dht22 overrides am2302's name)
            is_alias = raw_id != canonical_id

            # Rank before prefix cleanup so an independent hardware description
            # beats a library title. Trim binding instructions before both steps.
            raw_desc = raw.get("description") or ""
            if source_name == "zephyr":
                raw_desc = trim_zephyr_description(raw_desc)
            new_desc = clean_description(raw_desc)
            rank = description_rank(
                source_name, clean_description(raw_desc, strip_prefix=False),
                library_title=raw.get("description_is_library_title", False),
            ) if new_desc else (-1, -1, 0)

            if existing is None:
                # New entry
                merged[canonical_id] = {
                    "id": canonical_id,
                    "name": clean_name(raw.get("name", raw_id), canonical_id),
                    "manufacturer": normalize_manufacturer(raw.get("manufacturer")),
                    "type": raw.get("type"),
                    "voltage": raw.get("voltage"),
                    "datasheet_url": raw.get("datasheet_url"),
                    "description": new_desc,
                    "source_tier": "breakout_only" if is_tier3 else "primary",
                    "measures": set(raw.get("measures", [])),
                    "protocols": set(raw.get("protocol", [])),
                    "platforms": set(raw.get("platforms", [])),
                    "urls": list(raw.get("urls", [])),
                    "sources": [source_name],
                    "_search_names": {raw.get("name", raw_id)},
                    "_from_alias": is_alias,
                    "_description_rank": rank,
                }
            else:
                # Enrich existing entry
                # If this is the canonical ID entry and the existing was created
                # by an alias, upgrade name and popularity
                if not is_alias and existing.get("_from_alias"):
                    existing["name"] = clean_name(raw.get("name", existing["name"]), canonical_id)
                    existing["_from_alias"] = False

                existing["_search_names"].add(raw.get("name", raw_id))

                # Multi-value: union
                existing["measures"].update(raw.get("measures", []))
                existing["protocols"].update(raw.get("protocol", []))
                existing["platforms"].update(raw.get("platforms", []))

                # URLs: append + dedup, max 10
                for url in raw.get("urls", []):
                    if url not in existing["urls"] and len(existing["urls"]) < 10:
                        existing["urls"].append(url)

                # Scalars: first non-null wins (don't override from tier 3)
                if not is_tier3:
                    if not existing["manufacturer"] and raw.get("manufacturer"):
                        existing["manufacturer"] = normalize_manufacturer(raw["manufacturer"])
                    if not existing["type"] and raw.get("type"):
                        existing["type"] = raw["type"]
                    if not existing["voltage"] and raw.get("voltage"):
                        existing["voltage"] = raw["voltage"]
                    if not existing["datasheet_url"] and raw.get("datasheet_url"):
                        existing["datasheet_url"] = raw["datasheet_url"]

                # Description: hardware quality first, authority and length break ties.
                if rank > existing["_description_rank"]:
                    existing["description"] = new_desc[:200]
                    existing["_description_rank"] = rank

                # Upgrade tier if enriched by non-tier3 source
                if not is_tier3 and existing["source_tier"] == "breakout_only":
                    existing["source_tier"] = "primary"

                # Track provenance
                if source_name not in existing["sources"]:
                    existing["sources"].append(source_name)

    return merged


# Deploy-path guard floor. build_sensor_db runs inside the Docker image build on EVERY deploy
# (triggered by either the sensor OR the daily components workflow), so a grossly-truncated
# committed sensor dataset can't silently ship even if the sensor workflow's CI gate is bypassed.
# Well below the normal ~1.5-2.4k; a single small source dying is caught by the loud CI gate instead.
MIN_SENSOR_COUNT = 1200


def build_db(merged: dict[str, dict], output_path: Path, quiet: bool = False):
    """Create SQLite database from merged sensor data.

    Builds into a temp file and atomically replaces output_path on success; on any
    failure (Ctrl-C included) the temp is removed and the old DB is left intact.
    """
    if len(merged) < MIN_SENSOR_COUNT:
        raise ValueError(
            f"Only {len(merged)} sensors merged (< floor {MIN_SENSOR_COUNT}) — refusing to build a "
            f"truncated sensor.db. Check data/sensors/*.json for a collapsed source."
        )

    # Build to a temp path and atomically replace on success — an interrupted build never
    # leaves a missing/corrupt sensor.db (mirrors build_history_db.py / build_boards_db.py).
    tmp_path = output_path.with_suffix(".db.tmp")
    for suffix in ("", "-wal", "-shm"):
        Path(str(tmp_path) + suffix).unlink(missing_ok=True)  # clear stale tmp from a prior crash

    try:
        _build_into_tmp(merged, output_path, tmp_path)
    except BaseException:
        # BaseException so Ctrl-C/SystemExit clean up too; the old DB stays intact.
        for suffix in ("", "-wal", "-shm"):
            Path(str(tmp_path) + suffix).unlink(missing_ok=True)
        raise

    if not quiet:
        print_stats(output_path)


def _build_into_tmp(merged: dict[str, dict], output_path: Path, tmp_path: Path):
    """Build the sensor DB into tmp_path, then atomically move it to output_path."""
    conn = sqlite3.connect(str(tmp_path))
    try:
        _fill_tmp_and_swap(conn, merged, output_path, tmp_path)
    finally:
        # Already closed on success. On failure it must close before build_db() deletes the
        # tmp: Windows can't delete an open file (WinError 32) and that error would mask the
        # real one.
        conn.close()


def _fill_tmp_and_swap(conn: sqlite3.Connection, merged: dict[str, dict], output_path: Path,
                       tmp_path: Path):
    """Load the merged sensors into the open tmp DB, then atomically move it to output_path."""
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    # Create tables (no indexes yet for faster inserts)
    conn.executescript(SCHEMA_SQL)

    # Insert sensors
    sensor_rows = []
    measure_rows = []
    protocol_rows = []
    platform_rows = []
    url_rows = []

    for sid, s in sorted(merged.items()):
        platforms = sorted(s["platforms"])
        sensor_rows.append((
            sid,
            s["name"],
            s["manufacturer"],
            s["type"],
            s["voltage"],
            s["datasheet_url"],
            len(platforms),  # platform_count
            fit_description(tidy_text(s["description"])),
            s["source_tier"],
            json.dumps(s["sources"]),
        ))

        measures = set(s["measures"])
        if not s.get("_curated_measures"):
            measures = (measures | MEASURE_ADDITIONS.get(sid, set())) - MEASURE_REMOVALS.get(sid, set())
            measures |= type_implied_measures(s["type"], measures)
        for m in sorted(measures):
            measure_rows.append((sid, m))
        for p in sorted(s["protocols"]):
            protocol_rows.append((sid, p))
        for pl in platforms:
            platform_rows.append((sid, pl))
        for url in s["urls"]:
            url_rows.append((sid, url))

    conn.executemany(
        "INSERT INTO sensors VALUES (?,?,?,?,?,?,?,?,?,?)",
        sensor_rows,
    )
    conn.executemany("INSERT INTO sensor_measures VALUES (?,?)", measure_rows)
    conn.executemany("INSERT INTO sensor_protocols VALUES (?,?)", protocol_rows)
    conn.executemany("INSERT INTO sensor_platforms VALUES (?,?)", platform_rows)
    conn.executemany("INSERT INTO sensor_urls VALUES (?,?)", url_rows)

    # Create indexes after bulk insert
    conn.executescript(INDEX_SQL)

    # Create and populate FTS5
    conn.executescript(FTS_SQL)
    # Search-only source/historical names; displayed sensors.name stays clean.
    conn.executemany(
        "UPDATE sensors_fts SET name = ? WHERE id = ?",
        [(" ".join(sorted({s["name"]} | s.get("_search_names", set()))), sid)
         for sid, s in sorted(merged.items())],
    )

    conn.commit()
    conn.execute("ANALYZE")
    conn.execute("VACUUM")
    conn.close()

    # Drop stale sidecars of the OLD db first, then atomically move the new build into place.
    for suffix in ("-wal", "-shm"):
        Path(str(output_path) + suffix).unlink(missing_ok=True)
    tmp_path.replace(output_path)


def print_stats(db_path: Path):
    """Print database statistics."""
    conn = sqlite3.connect(str(db_path))
    size_kb = db_path.stat().st_size / 1024

    sensor_count = conn.execute("SELECT COUNT(*) FROM sensors").fetchone()[0]
    measure_count = conn.execute("SELECT COUNT(DISTINCT measure) FROM sensor_measures").fetchone()[0]

    print(f"\n{'='*50}")
    print(f"Database: {db_path} ({size_kb:.0f} KB)")
    print(f"Sensors:  {sensor_count}")
    print(f"Measures: {measure_count} unique types")

    # Source tier breakdown
    print("\nSource tiers:")
    for tier, count in conn.execute(
        "SELECT source_tier, COUNT(*) FROM sensors GROUP BY source_tier ORDER BY 2 DESC"
    ):
        print(f"  {tier}: {count}")

    # Top measures
    print("\nTop measures:")
    for measure, count in conn.execute(
        "SELECT measure, COUNT(*) c FROM sensor_measures GROUP BY measure ORDER BY c DESC LIMIT 10"
    ):
        print(f"  {measure}: {count}")

    # Platform distribution
    print("\nPlatforms:")
    for platform, count in conn.execute(
        "SELECT platform, COUNT(*) FROM sensor_platforms GROUP BY platform ORDER BY 2 DESC"
    ):
        print(f"  {platform}: {count}")

    # Top sensors by platform count
    print("\nTop by platform support:")
    for sid, name, pc in conn.execute(
        "SELECT id, name, platform_count FROM sensors ORDER BY platform_count DESC LIMIT 5"
    ):
        print(f"  {name} (platforms={pc})")

    conn.close()
    print(f"{'='*50}")


def build(data_dir: Path, output: Path, verbose: bool = True) -> None:
    """Build sensor.db from scraped JSON data. Callable from connection.py.

    Args:
        data_dir: Directory containing sensors/ subdirectory with JSON files
        output: Output SQLite database path
        verbose: If True, print progress output
    """
    quiet = not verbose

    if not (data_dir / "sensors").is_dir():
        raise FileNotFoundError(f"Sensor data directory not found: {data_dir / 'sensors'}")

    if not quiet:
        print("Loading IC aliases...")
    aliases = load_aliases(data_dir)
    if not quiet:
        print(f"  {len(aliases)} aliases loaded")

    if not quiet:
        print("\nMerging sources...")
    merged = merge_sensors(data_dir, aliases, quiet=quiet)

    if not quiet:
        print("\nFixing bad sensor names...")
    for sensor in merged.values():
        sensor["_search_names"].add(sensor["name"])
    fix_names(merged, quiet=quiet)

    if not quiet:
        print("\nEnriching manufacturers via IC prefix lookup...")
    enrich_manufacturers(merged, quiet=quiet)

    if not quiet:
        print("\nEnriching descriptions via overrides...")
    enrich_descriptions(merged, quiet=quiet)

    if not quiet:
        print("\nEnriching types via measure patterns and description keywords...")
    enrich_types(merged, quiet=quiet)

    if not quiet:
        print("\nEnriching voltages via static lookup table...")
    _enrich_voltages(merged, quiet=quiet)

    if not quiet:
        print("\nEnriching protocols via IC lookup and manufacturer defaults...")
    enrich_protocols(merged, quiet=quiet)

    if not quiet:
        print("\nApplying curated field corrections...")
    transfer_platform_support(merged, data_dir)
    for sensor in merged.values():
        sensor.setdefault("_search_names", set()).add(sensor["name"])
    apply_curated(merged, data_dir)
    name_aliases = data_dir / "sensors" / "name_aliases.json"
    if name_aliases.exists():
        for sid, names in json.loads(name_aliases.read_text(encoding="utf-8")).items():
            if sid in merged:
                merged[sid]["_search_names"].update(names)

    if not quiet:
        print(f"\nBuilding database ({len(merged)} sensors)...")
    build_db(merged, output, quiet=quiet)

    if not quiet:
        print("\nDone.")


def main():
    parser = argparse.ArgumentParser(description="Build sensor.db from scraped JSON data")
    parser.add_argument("--data-dir", default="data/", help="Directory containing sensor JSON files")
    parser.add_argument("--output", default="data/sensor.db", help="Output SQLite database path")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    output_path = Path(args.output)

    if not (data_dir / "sensors").is_dir():
        print(f"Error: {data_dir / 'sensors'} not found", file=sys.stderr)
        sys.exit(1)

    build(data_dir, output_path, verbose=not args.quiet)


if __name__ == "__main__":
    main()
