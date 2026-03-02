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
}

# IC prefix -> manufacturer mapping for post-merge enrichment.
# Applied ONLY when manufacturer is NULL. Longest prefix matched first.
# Sources: datasheets, manufacturer websites, acquisition history.
IC_PREFIX_MANUFACTURERS: dict[str, str] = {
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

    # Amphenol
    "sm300d2": "Amphenol",         # SM300D2

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
    "ah1815": "Honeywell",         # AH1815 Hall effect

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
}

# Name overrides for sensors where the scraped name is bad (too long, includes
# description text, library-specific prefixes, etc.). Applied post-merge.
NAME_OVERRIDES: dict[str, str] = {
    "rfd77402": "RFD77402",               # was "RFD77402 DISTANCE SENSOR - VCSEL TIME OF FLIGHT"
    "ina219": "INA219",                   # was "GyverINA" (Arduino lib name)
    "hmc5883l": "HMC5883L",              # was "HMC5883 Unified"
    "ak9750": "AK9750",                  # was "AK9750 HUMAN PRESENCE"
    "ak9753": "AK975X",                  # was "AK975X Human Presence"
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

# Description overrides for sensors where no source provides a useful description.
# Applied post-merge ONLY when the sensor still has no description (or a very short one).
# Keep descriptions concise, search-friendly, and under 200 chars.
# Format: {sensor_id: "description"}
DESCRIPTION_OVERRIDES: dict[str, str] = {
    # ── Multi-platform sensors (platform_count >= 2) ─────────────────────────
    "ads1115010v": "ADS1115 16-bit ADC configured for 0-10V analog input measurement",
    "sfa40": "Sensirion formaldehyde and VOC sensor module with temperature and humidity output",
    "mics4514": "Dual-element gas sensor for CO and NO2 detection with separate reducing and oxidizing channels",
    "icg20660l": "6-axis IMU with 3-axis accelerometer and 3-axis gyroscope, I2C/SPI interface",
    "tmf8x01": "Time-of-flight distance sensor with multi-zone ranging and histogram output",
    "urm09": "Ultrasonic distance sensor module with I2C and analog output, 2cm-500cm range",

    # ── Energy metering ICs (ESPHome-only) ───────────────────────────────────
    "ade7880": "Polyphase energy metering IC for 3-phase power measurement with harmonic analysis",
    "ade7953": "Single-phase energy metering IC with power, voltage, and current measurement",
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
    "sm300d2": "Multi-parameter air quality sensor module with CO2, PM2.5, temperature, humidity",
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
    "ld2420": "Hi-Link 24GHz mmWave radar module for motion and presence detection",
    "mr24hpc1": "24GHz mmWave radar module for human presence and motion detection",
    "mr60bha2": "60GHz mmWave radar module for breathing and heartbeat detection",
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
        # Replace if empty OR if current is very short and override is better
        if not current or (len(current) < 20 and len(override) > len(current)):
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

# Single-measure shortcuts: if sensor has ONLY these measures (possibly
# combined with generic ones like temperature/humidity), infer type.
# For CO2: only apply NDIR when no gas/voc/particulate measures (those
# indicate a MOX or multi-sensor module that estimates eCO2).
_MOX_INDICATORS = {"voc", "gas", "particulate"}

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
    ("mems", ["mems microphone", "mems accelerometer", "mems gyroscope", "mems inertial"]),
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
    ("shunt", ["current shunt", "current monitor", "power monitor", "energy meter",
               "energy metering", "power metering"]),
    ("adc", ["analog-to-digital", "analog to digital", " adc "]),
]

# Stage 3: Well-known IC → type mappings for popular sensors where
# measure-pattern and keyword inference can't determine the technology.
IC_TYPE_OVERRIDES: dict[str, str] = {
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
    "mht5052b": "semiconductor",
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
    "bm22s2021": "semiconductor",
    "bm22s3021": "semiconductor",
    "bm22s3221": "semiconductor",
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
    "bm42s3021": "semiconductor",
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
    "bm25s2021": "capacitive",
    "bm25s2621": "capacitive",
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
    "bms56m605": "mems",
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
    "max32664c": "mems",
    "bms81m001": "mems",
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
    "bme34m101": "mems",
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
    "bm62s2201": "mems",
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
    "wpah01": "mems",
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
    "bmv23m001": "mems",
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
    # ── Hall-effect magnetometers / magnetic encoders ─────────────────
    "as5600": "hall_effect",
    "mlx90393": "hall_effect",
    "bmm150": "hall_effect",
    "qmc5883l": "hall_effect",
    "hmc5883l": "hall_effect",
    "bmm350": "hall_effect",
    "mmc5603": "hall_effect",
    "mmc56x3": "hall_effect",
    "mmc5983": "hall_effect",
    "mmc5983ma": "hall_effect",
    "mmc5603nj": "hall_effect",
    "mmc34160pj": "hall_effect",
    "qmc5883": "hall_effect",
    "qmc5583l": "hall_effect",
    "qmc5883p": "hall_effect",
    "rm3100": "hall_effect",
    "ak8975": "hall_effect",
    "akm09918c": "hall_effect",
    "hmc6343": "hall_effect",
    "hmc6352": "hall_effect",
    "ist8310": "hall_effect",
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
    "gy26": "hall_effect",
    "fg3": "hall_effect",
    "hscdtd008a": "hall_effect",
    "lsm303dlhmag": "hall_effect",
    "lsm9ds1mag": "hall_effect",
    "bm32s2031": "hall_effect",
    "bms33m332": "hall_effect",
    "bms36t001": "hall_effect",
    "ad2s1210": "hall_effect",
    "amt25": "hall_effect",
    "ky040": "hall_effect",
    "rp2040": "hall_effect",
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
    "acs37800": "shunt",
    "tli4970": "shunt",
    "tli4971": "shunt",
    "sct013": "shunt",
    "ctclamp": "shunt",
    "zmpt101b": "shunt",
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
    "hx710a": "strain_gauge",
    "hx710b": "strain_gauge",
    "tal220": "strain_gauge",
    "bmh12m105": "strain_gauge",
    "bmh12m205": "strain_gauge",
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
    "bme82m131": "photodiode",
    "bm62s6021": "photodiode",
    "bm92s2021": "photodiode",
    # ── Biometric / PPG / ECG (photodiode-based) ──────────────────────
    "max30101": "photodiode",
    "max30102": "photodiode",
    "max30001": "photodiode",
    "max30003": "photodiode",
    "max86150": "photodiode",
    "max32664": "photodiode",
    "bh1790": "photodiode",
    "afe4490": "photodiode",
    "afe44xx": "photodiode",
    "afe4950": "photodiode",
    "bmh08002": "photodiode",
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
    "bme63m001": "capacitive",
    "bm25s4021": "capacitive",
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
    "frn03h": "hall_effect",
    "frn03p": "hall_effect",
    "frn06": "hall_effect",
    "frn20": "hall_effect",
    "flowmeter": "hall_effect",
    # ── Water quality / electrochemical probes ────────────────────────
    "dfr0300": "electrochemical",
    "ec10": "electrochemical",
    "ufireec": "electrochemical",
    "ufireise": "electrochemical",
    "sen0161": "electrochemical",
    "sen0322": "electrochemical",
    "fcxmldx5": "electrochemical",
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
    "bm32s2021": "capacitive",       # Proximity sensing module
    "bm42p782n1": "strain_gauge",    # Weighing scale module
    "bm42s3021": "thermopile",       # Thermocouple temperature
    "bm62s2201": "mems",             # Air pressure sensor (MEMS)
    "bm62s3202": "mems",             # Water level sensor (pressure-based)
    "bm92d3021": "shunt",            # Motor obstruction detection (current sensing)
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
    "bmh23m001": "semiconductor",    # 24-bit ADC module
    "bmh23m002": "semiconductor",    # 24-bit ADC module
    "bms26m833": "thermopile",       # AMG8833 IR array
    "bms56m605": "mems",             # MPU-6050 IMU
    "bms81m001": "mems",             # MPU-6050 shake detection
    "bmv23m001": "mems",             # Sound detector (MEMS mic)
    "gtm5210f32": "optical",         # Fingerprint sensor
    "gtm5210f52": "optical",         # Fingerprint sensor
    "bme26m301": "mems",             # Air velocity sensor
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

        # CO2 sensors without MOX indicators -> NDIR
        if inferred is None and "co2" in measures and not (measures & _MOX_INDICATORS):
            inferred = "ndir"

        # Standalone particulate sensors -> laser (most PM sensors use laser scattering)
        if inferred is None and "particulate" in measures and "co2" not in measures:
            inferred = "laser"

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

# Format: "min-max" in volts (operating supply voltage from datasheet).
# Only includes values verified from manufacturer datasheets.
# Applied as post-merge enrichment — never overwrites existing voltage data.
VOLTAGE_TABLE: dict[str, str] = {
    # --- Temperature / Humidity / Pressure ---
    "bme280": "1.71-3.6",       # Bosch BME280 datasheet
    "bme68x": "1.71-3.6",       # Bosch BME680/688 datasheet
    "bmp280": "1.71-3.6",       # Bosch BMP280 datasheet
    "bmp180": "1.8-3.6",        # Bosch BMP180 datasheet
    "bmp3xx": "1.65-3.6",       # Bosch BMP384/388/390 datasheet
    "bmp581": "1.71-3.6",       # Bosch BMP581 datasheet
    "dps310": "1.7-3.6",        # Infineon DPS310 datasheet
    "ms5611": "1.8-3.6",        # TE MS5611 datasheet
    "ms8607": "1.5-3.6",        # TE MS8607 datasheet
    "mpl3115a2": "1.95-3.6",    # NXP MPL3115A2 datasheet
    "mpl115a2": "2.375-5.5",    # NXP MPL115A2 datasheet
    "sht3x": "2.15-5.5",        # Sensirion SHT30/31/35 datasheet
    "sht4x": "1.08-3.6",        # Sensirion SHT40/41/45 datasheet
    "hts221": "1.7-3.6",        # ST HTS221 datasheet
    "hdc1080": "2.7-5.5",       # TI HDC1080 datasheet
    "hdc2010": "1.62-3.6",      # TI HDC2010 datasheet
    "hdc302x": "1.62-3.6",      # TI HDC3020/3021/3022 datasheet
    "htu21df": "1.5-3.6",       # TE HTU21D datasheet
    "htu31d": "2.6-5.5",        # TE HTU31D datasheet
    "si7021": "1.9-3.6",        # Silicon Labs Si7021 datasheet
    "aht20": "2.0-5.5",         # ASAIR AHT20 datasheet
    "am2320": "3.1-5.5",        # ASAIR AM2320 datasheet
    "dht11": "3.0-5.5",         # ASAIR DHT11 datasheet
    "dht12": "2.7-5.5",         # ASAIR DHT12 datasheet
    "dht": "3.3-5.5",           # Generic DHT (DHT22/AM2302)
    "dht20": "2.0-5.5",         # ASAIR DHT20 datasheet
    "stts22h": "1.5-3.6",       # ST STTS22H datasheet
    "tmp117": "1.7-5.5",        # TI TMP117 datasheet
    "mcp9808": "2.7-5.5",       # Microchip MCP9808 datasheet
    "adt7410": "2.7-5.5",       # Analog Devices ADT7410 datasheet
    "as6212": "1.4-3.6",        # ams AS6212 datasheet
    "as6221": "1.6-3.6",        # ams AS6221 datasheet
    "lm75": "2.7-5.5",          # TI/NXP LM75 datasheet

    # --- Temperature probes (thermocouple/RTD/1-wire) ---
    "max31855": "3.0-3.6",      # Analog Devices MAX31855 datasheet
    "max31856": "3.0-3.6",      # Analog Devices MAX31856 datasheet
    "max6675": "3.0-5.5",       # Analog Devices MAX6675 datasheet
    "max31865": "3.0-3.6",      # Analog Devices MAX31865 datasheet
    "ds18b20": "3.0-5.5",       # Analog Devices DS18B20 datasheet
    "mcp9600": "2.7-5.5",       # Microchip MCP9600 datasheet

    # --- Light ---
    "bh1750": "2.4-3.6",        # ROHM BH1750 datasheet
    "tsl2561": "2.7-3.6",       # ams TSL2561 datasheet
    "tsl2591": "3.0-3.6",       # ams TSL2591 datasheet
    "veml7700": "2.5-3.6",      # Vishay VEML7700 datasheet
    "veml6075": "1.7-3.6",      # Vishay VEML6075 datasheet
    "max44009": "1.7-3.6",      # Analog Devices MAX44009 datasheet
    "opt300x": "1.6-3.6",       # TI OPT3001/3002 datasheet
    "ltr390": "1.7-3.6",        # Lite-On LTR-390UV datasheet
    "ltr390uv": "1.7-3.6",      # Lite-On LTR-390UV datasheet
    "apds9960": "2.4-3.6",      # Broadcom APDS-9960 datasheet
    "tcs34725": "2.7-3.6",      # ams TCS34725 datasheet
    "as7341": "1.7-3.6",        # ams AS7341 datasheet
    "as726x": "2.7-3.6",        # ams AS7262/7263 datasheet

    # --- Gas / Air Quality ---
    "scd4x": "2.4-5.5",         # Sensirion SCD40/41 datasheet
    "scd30": "3.3-5.5",         # Sensirion SCD30 datasheet
    "sgp30": "1.62-1.98",       # Sensirion SGP30 datasheet
    "sgp40": "1.62-1.98",       # Sensirion SGP40 datasheet
    "ccs811": "1.8-3.6",        # ams CCS811 datasheet
    "ens160": "1.71-3.6",       # ScioSense ENS160 datasheet
    "ags02ma": "3.0-5.5",       # ASAIR AGS02MA datasheet
    "sds011": "4.7-5.3",        # Nova SDS011 datasheet
    "mics4514": "4.9-5.1",      # SGX MICS-4514 datasheet

    # --- IMU / Motion ---
    "mpu6050": "2.375-3.46",    # TDK MPU-6050 datasheet
    "mpu9250": "2.4-3.6",       # TDK MPU-9250 datasheet
    "bmi160": "1.71-3.6",       # Bosch BMI160 datasheet
    "bmi270": "1.71-3.6",       # Bosch BMI270 datasheet
    "lsm6dsox": "1.71-3.6",     # ST LSM6DSOX datasheet
    "lsm9ds1": "1.9-3.6",       # ST LSM9DS1 datasheet
    "lis3dh": "1.71-3.6",       # ST LIS3DH datasheet
    "lis2dw12": "1.62-3.6",     # ST LIS2DW12 datasheet
    "adxl345": "2.0-3.6",       # Analog Devices ADXL345 datasheet
    "mma8451": "1.95-3.6",      # NXP MMA8451Q datasheet
    "msa301": "1.62-3.6",       # MEMSensing MSA301 datasheet
    "icm42688": "1.71-3.6",     # TDK ICM-42688-P datasheet
    "bno055": "2.4-3.6",        # Bosch BNO055 datasheet
    "fxos8700": "1.95-3.6",     # NXP FXOS8700CQ datasheet

    # --- Magnetometer ---
    "bmm150": "1.62-3.6",       # Bosch BMM150 datasheet
    "bmm350": "1.62-3.6",       # Bosch BMM350 datasheet
    "lis2mdl": "1.71-3.6",      # ST LIS2MDL datasheet
    "lis3mdl": "1.71-3.6",      # ST LIS3MDL datasheet
    "hmc5883l": "2.16-3.6",     # Honeywell HMC5883L datasheet
    "qmc5883l": "2.16-3.6",     # QST QMC5883L datasheet
    "mmc5603": "1.62-3.6",      # MEMSIC MMC5603NJ datasheet
    "mlx90393": "2.2-3.6",      # Melexis MLX90393 datasheet

    # --- Distance / Proximity ---
    "vl53l0x": "2.6-3.5",       # ST VL53L0X datasheet
    "vl53l1x": "2.6-3.5",       # ST VL53L1X datasheet
    "vl6180x": "2.6-3.0",       # ST VL6180X datasheet
    "hcsr04": "4.5-5.5",        # Generic HC-SR04 datasheet

    # --- Load cell ---
    "hx711": "2.6-5.5",         # Avia HX711 datasheet

    # --- Touch ---
    "mpr121": "1.71-3.6",       # NXP MPR121 datasheet

    # --- Lightning ---
    "as3935": "2.4-5.5",        # ams AS3935 datasheet

    # --- Encoder ---
    "as5600": "3.0-3.6",        # ams AS5600 datasheet

    # --- Gesture ---
    "mgc3130": "2.7-3.6",       # Microchip MGC3130 datasheet

    # --- Power monitoring ---
    "ina219": "3.0-5.5",        # TI INA219 datasheet
    "ina226": "2.7-5.5",        # TI INA226 datasheet
    "ina260": "2.7-5.5",        # TI INA260 datasheet
    "ina3221": "2.7-5.5",       # TI INA3221 datasheet
    "atm90e26": "2.8-3.6",      # Microchip ATM90E26 datasheet
    "ads1115": "2.0-5.5",       # TI ADS1115 datasheet

    # --- Infrared temperature ---
    "mlx90614": "2.6-3.6",      # Melexis MLX90614 datasheet

    # --- Radar ---
    "ld2410": "5.0-5.0",        # Hi-Link LD2410 (5V only)

    # --- Particulate ---
    "sps30": "4.5-5.5",         # Sensirion SPS30 datasheet
    "pms5003": "4.5-5.5",       # Plantower PMS5003 datasheet

    # --- Additional well-known sensors ---
    "sht1x": "2.4-5.5",         # Sensirion SHT10/11/15 datasheet
    "sht2x": "2.1-3.6",         # Sensirion SHT20/21/25 datasheet
    "sht20": "2.1-3.6",         # Sensirion SHT20 datasheet (alias)
    "sht21": "2.1-3.6",         # Sensirion SHT21 datasheet (alias)
    "sht85": "2.15-5.5",        # Sensirion SHT85 datasheet
    "shtc3": "1.62-3.6",        # Sensirion SHTC3 datasheet
    "shtcx": "1.62-3.6",        # Sensirion SHTC1/SHTC3 datasheet
    "sts3x": "2.15-5.5",        # Sensirion STS30/31/35 datasheet
    "lps22hb": "1.7-3.6",       # ST LPS22HB datasheet
    "lps22hh": "1.7-3.6",       # ST LPS22HH datasheet
    "lps22df": "1.7-3.6",       # ST LPS22DF datasheet
    "lps25hb": "1.7-3.6",       # ST LPS25HB datasheet
    "lps28dfw": "1.7-3.6",      # ST LPS28DFW datasheet
    "lps35hw": "1.7-3.6",       # ST LPS35HW datasheet
    "ilps22qs": "1.7-3.6",      # ST ILPS22QS datasheet
    "amg8833": "3.0-3.6",       # Panasonic AMG8833 datasheet
    "amg88xx": "3.0-3.6",       # Panasonic AMG88xx datasheet (alias)
    "veml6070": "2.7-5.5",      # Vishay VEML6070 datasheet
    "max30102": "1.7-2.0",      # Analog Devices MAX30102 datasheet
    "max30101": "1.7-2.0",      # Analog Devices MAX30101 datasheet
    "bmx160": "1.71-3.6",       # Bosch BMX160 datasheet

    # --- More temperature ---
    "pct2075": "2.7-5.5",       # NXP PCT2075 datasheet
    "tc74": "2.7-5.5",          # Microchip TC74 datasheet
    "tmp102": "1.4-3.6",        # TI TMP102 datasheet
    "tmp1075": "1.7-5.5",       # TI TMP1075 datasheet
    "tmp007": "2.5-5.5",        # TI TMP007 datasheet (discontinued)
    "tmp006": "2.2-5.5",        # TI TMP006 datasheet
    "lm75a": "2.7-5.5",         # NXP LM75A datasheet
    "ds18x20": "3.0-5.5",       # Analog Devices DS18x20 family
    "ds1624": "2.7-5.5",        # Analog Devices DS1624 datasheet
    "emc2101": "3.0-3.6",       # Microchip EMC2101 datasheet
    "stts751": "2.25-3.6",      # ST STTS751 datasheet
    "mlx90615": "2.6-3.6",      # Melexis MLX90615 datasheet
    "mlx90632": "2.6-3.6",      # Melexis MLX90632 datasheet
    "mlx90640": "3.0-3.6",      # Melexis MLX90640 datasheet
    "sths34pf80": "1.7-3.6",    # ST STHS34PF80 datasheet

    # --- More humidity ---
    "hdc2080": "1.62-3.6",      # TI HDC2080 datasheet
    "am2301b": "2.2-5.5",       # ASAIR AM2301B datasheet
    "am2315c": "2.2-5.5",       # ASAIR AM2315C datasheet
    "ahtx0": "2.0-5.5",         # ASAIR AHT10/AHT20 family
    "dht22": "3.3-5.5",         # ASAIR DHT22/AM2302 datasheet
    "hs300x": "1.8-3.6",        # Renesas HS300x datasheet
    "ens210": "1.71-3.6",       # ScioSense ENS210 datasheet

    # --- More pressure ---
    "bmp58x": "1.71-3.6",       # Bosch BMP58x family datasheet
    "ms5803": "1.8-3.6",        # TE MS5803 datasheet
    "ms5837": "1.5-3.6",        # TE MS5837 datasheet
    "icp10111": "1.65-3.6",     # TDK ICP-10111 datasheet
    "sdp3x": "1.7-3.6",         # Sensirion SDP3x datasheet

    # --- More light ---
    "tcs3430": "1.7-3.6",       # ams TCS3430 datasheet
    "tcs3200": "2.7-5.5",       # ams TCS3200 datasheet
    "si1145": "1.71-3.6",       # Silicon Labs SI1145 datasheet
    "apds9306": "1.7-3.6",      # Broadcom APDS-9306 datasheet
    "bh1730": "2.4-3.6",        # ROHM BH1730 datasheet
    "ltr308": "1.7-3.6",        # Lite-On LTR-308ALS datasheet
    "ltr329": "1.7-3.6",        # Lite-On LTR-329ALS datasheet
    "ltr553": "2.4-3.6",        # Lite-On LTR-553ALS datasheet
    "veml6040": "2.5-3.6",      # Vishay VEML6040 datasheet
    "opt4048": "1.6-3.6",       # TI OPT4048 datasheet
    "vcnl4010": "2.5-3.6",      # Vishay VCNL4010 datasheet
    "vcnl4040": "2.5-3.6",      # Vishay VCNL4040 datasheet
    "vcnl4200": "2.5-3.6",      # Vishay VCNL4200 datasheet
    "isl29125": "2.5-3.3",      # Renesas ISL29125 datasheet

    # --- More gas ---
    "sgp41": "1.7-3.6",         # Sensirion SGP41 datasheet
    "ags10": "3.0-5.5",         # ASAIR AGS10 datasheet
    "mics6814": "4.9-5.1",      # SGX MICS-6814 datasheet
    "sen5x": "4.5-5.5",         # Sensirion SEN5x datasheet
    "sen6x": "4.5-5.5",         # Sensirion SEN6x datasheet
    "sfa40": "3.15-3.45",       # Sensirion SFA40 datasheet
    "ee895": "3.0-5.5",         # E+E Elektronik EE895 datasheet

    # --- More IMU / accel ---
    "adxl343": "2.0-3.6",       # Analog Devices ADXL343 datasheet
    "adxl362": "1.6-3.5",       # Analog Devices ADXL362 datasheet
    "adxl372": "1.6-3.5",       # Analog Devices ADXL372 datasheet
    "bma400": "1.2-3.6",        # Bosch BMA400 datasheet
    "bno08x": "2.4-3.6",        # CEVA BNO08x datasheet
    "icm20948": "1.71-3.6",     # TDK ICM-20948 datasheet
    "icm42605": "1.71-3.6",     # TDK ICM-42605 datasheet
    "icm45605": "1.71-3.6",     # TDK ICM-45605 datasheet
    "icm45686": "1.71-3.6",     # TDK ICM-45686 datasheet
    "icg20660l": "1.71-3.45",   # TDK ICG-20660L datasheet
    "itg3200": "2.1-3.6",       # TDK ITG-3200 datasheet
    "mpu6886": "2.4-3.6",       # TDK MPU-6886 datasheet
    "mma8452q": "1.95-3.6",     # NXP MMA8452Q datasheet
    "kx132": "1.7-3.6",         # ROHM/Kionix KX132 datasheet
    "lis2dh12": "1.71-3.6",     # ST LIS2DH12 datasheet
    "lis2du12": "1.71-3.6",     # ST LIS2DU12 datasheet
    "lis2duxs12": "1.71-3.6",   # ST LIS2DUXS12 datasheet
    "lis2hh12": "1.71-3.6",     # ST LIS2HH12 datasheet
    "lis331": "2.16-3.6",       # ST LIS331DLH datasheet
    "lsm6ds0": "1.8-3.6",      # ST LSM6DS0 datasheet
    "lsm6dso16is": "1.71-3.6",  # ST LSM6DSO16IS datasheet
    "lsm303": "2.16-3.6",       # ST LSM303DLHC datasheet
    "lsm303agr": "1.71-3.6",    # ST LSM303AGR datasheet
    "ism330dlc": "1.71-3.6",    # ST ISM330DLC datasheet
    "iis2dlpc": "1.62-3.6",     # ST IIS2DLPC datasheet
    "iis2mdc": "1.71-3.6",      # ST IIS2MDC datasheet

    # --- More magnetometer ---
    "mmc56x3": "1.62-3.6",      # MEMSIC MMC56x3 datasheet
    "mmc5983": "1.62-3.6",      # MEMSIC MMC5983MA datasheet
    "qmc5883": "2.16-3.6",      # QST QMC5883 datasheet
    "rm3100": "1.8-3.6",        # PNI RM3100 datasheet

    # --- More distance ---
    "vl53l5cx": "2.6-3.5",      # ST VL53L5CX datasheet
    "vl6180": "2.6-3.0",        # ST VL6180 datasheet (alias)
    "tmf8x01": "2.7-5.5",       # ams TMF8801 datasheet
    "gp2y0a21yk": "4.5-5.5",    # Sharp GP2Y0A21YK datasheet

    # --- More particulate ---
    "pms7003": "4.5-5.5",       # Plantower PMS7003 datasheet
    "pmsa003i": "4.5-5.5",      # Plantower PMSA003I datasheet
    "gp2y1010au0f": "2.5-5.5",  # Sharp GP2Y1010AU0F datasheet

    # --- Power monitoring ---
    "ina237": "1.7-5.5",        # TI INA237/INA238 datasheet
    "nau7802": "2.7-5.5",       # Nuvoton NAU7802 datasheet
    "hlw8012": "3.0-5.5",       # HLW8012 datasheet
    "hlw8032": "3.0-5.5",       # HLW8032 datasheet
    "max17043": "2.5-4.5",      # Analog Devices MAX17043 datasheet
    "mcp39f521": "3.0-3.6",     # Microchip MCP39F521 datasheet

    # --- Gesture ---
    "paj7620": "2.7-3.6",       # PixArt PAJ7620U2 datasheet
    "paj7620u2": "2.7-3.6",     # PixArt PAJ7620U2 datasheet (alias)

    # --- Touch ---
    "cap1188": "2.5-5.5",       # Microchip CAP1188 datasheet

    # --- Misc ---
    "mcp9700": "2.3-5.5",       # Microchip MCP9700 datasheet
    "spa06003": "1.7-3.6",      # Goertek SPA06-003 datasheet

    # --- Batch 2: DHT / Aosong ---
    "dht21": "3.3-5.5", "aht10": "2.0-5.5", "aht1x": "2.0-5.5",
    "aht2x": "2.0-5.5", "am2315": "3.1-5.5", "am2321": "3.1-5.5",
    "acd10": "4.5-5.5", "acd3100": "4.5-5.5",
    # --- TMP / TI temp ---
    "tmp36": "2.7-5.5", "lm335": "0.5-40.0", "lm73": "2.7-5.5",
    "lmt01": "2.0-5.5",
    # --- ADS / TI ADCs ---
    "ads1015": "2.0-5.5", "ads111x": "2.0-5.5", "ads1115010v": "2.0-5.5",
    "ads1118": "2.0-5.5", "ads1220": "2.3-5.5", "ads1258": "4.75-5.25",
    "ads1292r": "2.7-5.25", "ads1293": "1.7-3.6",
    # --- MCP / Microchip temp ---
    "mcp9802": "2.7-5.5", "mcp9601": "2.7-5.5", "mcp9701": "2.3-5.5",
    # --- AS / ams-OSRAM ---
    "as5040": "3.0-5.5", "as5047p": "3.0-3.6", "as5048": "3.0-3.6",
    "as5200l": "3.0-3.6", "as5600l": "3.0-3.6", "as7265x": "2.7-3.6",
    "as7331": "1.7-2.0", "as7341l": "1.7-3.6", "as7343": "1.7-3.6",
    "iaqcore": "3.0-5.5",
    # --- HDC / TI humidity ---
    "hdc1008": "3.0-5.0", "hdc10xx": "3.0-5.0",
    # --- HTU / TE humidity ---
    "htu21d": "1.5-3.6",
    # --- NXP ---
    "fxas21002": "2.1-3.6", "fxas21002c": "2.1-3.6",
    "mma7660": "2.4-3.6", "mma7455": "2.4-3.6",
    "mma8453q": "1.95-3.6", "mma8652": "1.95-3.6",
    "mpl115a1": "2.375-5.5", "mpx5700": "4.75-5.25",
    "mpxa6115a": "4.75-5.25", "mpxhz6116a": "4.75-5.25",
    # --- ADXL / Analog Devices accel ---
    "adxl313": "1.6-3.5", "adxl335": "1.8-3.6", "adxl34x": "2.0-3.6",
    "adxl355": "2.25-3.6", "adxl366": "1.6-3.5", "adxl367": "1.1-3.6",
    "adxl375": "2.0-3.6", "adxl37x": "2.0-3.6",
    # --- Analog Devices misc ---
    "ad22100a": "4.0-6.5", "ad22100k": "4.0-6.5", "ad22100s": "4.0-6.5",
    "ad22103k": "3.1-3.5", "ad7193": "3.0-5.25", "ad7194": "3.0-5.25",
    "ad7797": "2.7-5.25", "ad8232": "2.0-3.5", "ad8494": "2.7-36.0",
    "ad2s1210": "4.75-5.25", "ade7880": "2.4-3.7", "ade7953": "2.4-3.7",
    "ade7978": "2.4-3.7", "adis16470": "3.0-3.6", "adltc2990": "2.9-5.5",
    "adstds75lm75": "2.7-5.5", "adt7310": "2.7-5.5", "adt7420": "2.7-5.5",
    "ds1621": "2.7-5.5", "ds1821": "3.0-5.5", "ds3231": "2.3-5.5",
    "ds7505": "1.7-3.7", "ltc2959": "2.7-80.0", "max17055": "2.7-4.5",
    "max30001": "1.7-3.6", "max30003": "1.7-3.6", "max30205": "2.7-3.6",
    "max30210": "1.7-3.6", "max31820": "3.0-3.6", "max31850": "3.0-3.6",
    "max31855k": "3.0-3.6", "max31875": "1.6-3.6",
    "max32664": "1.8-3.3", "max32664c": "1.8-3.3",
    "max44007": "1.7-3.6", "max471": "3.0-36.0",
    "max6605mxk": "3.0-5.5", "max6605mxkv": "3.0-5.5",
    "max6607ixk": "2.7-5.5", "max6613mxk": "2.4-5.5",
    "max6626": "3.0-5.5", "max86150": "1.7-2.0", "max9611": "2.7-5.5",
    # --- INA / TI power ---
    "ina169": "2.7-60.0", "ina228": "2.7-5.5", "ina23x": "1.7-5.5",
    "ina2xx": "2.7-5.5", "ina780x": "2.7-5.5",
    # --- Bosch ---
    "bma220": "2.0-3.6", "bma280": "1.62-3.6", "bma423": "1.2-3.6",
    "bma4xx": "1.2-3.6", "bmc150": "1.62-3.6", "bme34m101": "1.71-3.6",
    "bme63m001": "1.71-3.6", "bme680bsec": "1.71-3.6",
    "bme68xbsec2": "1.71-3.6", "bme690": "1.71-3.6",
    "bme82m131": "1.71-3.6", "bmg160": "2.4-3.6",
    "bmi085": "1.71-3.6", "bmi088": "1.71-3.6", "bmi08x": "1.71-3.6",
    "bmi270bmm150": "1.71-3.6", "bmx055": "2.4-3.6", "bno080": "2.4-3.6",
    "bmp384": "1.65-3.6", "bmp580": "1.71-3.6", "bmp585": "1.71-3.6",
    "bmp5xx": "1.71-3.6", "bmv080": "1.62-3.6",
    # --- STMicroelectronics ---
    "asm330lhh": "1.71-3.6", "h3lis200dl": "2.16-3.6",
    "h3lis331dl": "2.16-3.6", "ism330is": "1.71-3.6",
    "ism6hg256x": "1.71-3.6", "iis2dulpx": "1.62-3.6",
    "l3gd20": "2.4-3.6", "lps2x": "1.7-3.6", "lsm6ds3tr": "1.71-3.6",
    "lsm6dsm": "1.71-3.6", "lsm6dso": "1.71-3.6", "lsm6dsv": "1.71-3.6",
    "lsm9ds1tr": "1.9-3.6", "stmpe610": "1.8-3.3", "vl53l4cd": "2.6-3.5",
    "mp23db01hp": "1.64-3.6", "imp34dt05": "1.6-3.6",
    # --- TDK / InvenSense ---
    "icm20689": "1.71-3.45", "icm20x": "1.71-3.6",
    "icm42670p": "1.71-3.6", "icm42670s": "1.71-3.6",
    "icm45608": "1.71-3.6", "icm45689": "1.71-3.6",
    "icp10125": "1.65-3.6", "ics40619": "1.5-3.6",
    "mpu6000": "2.375-3.46", "mpu9x50": "2.4-3.6", "ch101": "1.8-3.6",
    # --- Silicon Labs ---
    "si7005": "1.9-3.6", "si7013": "1.9-3.6", "si7051": "1.9-3.6",
    "si7055": "1.9-3.6", "si705x": "1.9-3.6", "si70xx": "1.9-3.6",
    "si114x": "1.71-3.6",
    # --- Sensirion ---
    "sfa30": "3.15-3.45", "sgp4x": "1.62-1.98", "stc31": "1.08-3.6",
    "sts4x": "1.08-3.6", "sht11": "2.4-5.5", "sht25": "2.1-3.6",
    "co2": "4.5-5.5", "sdp31": "1.7-3.6",
    # --- ROHM ---
    "bh1730fvc": "2.4-3.6", "bh1749nuc": "2.3-3.6", "bh1790": "1.7-3.6",
    "bh1900nux": "2.5-3.6", "bd1020hfv": "2.7-5.5",
    "kx134": "1.7-3.6", "kxtj3": "1.7-3.6", "kx023": "1.7-3.6",
    # --- Lite-On ---
    "ltr308als": "1.7-3.6", "ltr329als": "1.7-3.6",
    "ltr329ltr303": "1.7-3.6", "ltr381rgb": "1.7-3.6",
    "ltr501": "2.4-3.6", "ltr507": "1.7-3.6", "ltralsps": "1.7-3.6",
    "ltrf216a": "1.7-3.6", "ap3216": "2.4-3.6",
    # --- Vishay ---
    "vcnl36687": "2.5-3.6", "vcnl4020": "2.5-3.6", "veml3235": "2.6-3.6",
    "veml3328": "2.5-3.6", "veml6030": "2.5-3.6", "veml6046": "2.5-3.6",
    "temt6000": "3.3-5.0", "alspt19": "2.5-5.5",
    # --- Broadcom ---
    "apds9253": "1.7-3.6", "apds9900": "2.4-3.6",
    "apds9950": "2.4-3.6", "apds9999": "1.7-3.6",
    # --- Melexis ---
    "mlx90377": "3.0-3.6", "mlx90392": "1.8-3.6", "mlx90395": "2.6-3.6",
    # --- Allegro ---
    "acs712": "4.5-5.5", "acs723": "4.5-5.5", "acs772": "4.5-5.5",
    "acs37800": "3.0-5.5", "als31300": "2.5-3.6",
    # --- Infineon ---
    "tlv493d": "2.7-3.5", "tli4970": "3.1-3.5", "tli4971": "3.1-3.5",
    "bgt60tr13c": "1.8-3.3",
    # --- Renesas ---
    "isl29034": "2.25-3.63", "hs3003": "2.3-5.5",
    "fs3000": "3.0-3.6", "isl28022": "2.7-5.5",
    # --- Microchip ---
    "cap1203": "2.5-5.5", "at42qt1010": "1.8-5.5", "at42qt1011": "1.8-5.5",
    "atm90e32": "2.8-3.6", "atm90e32as": "2.8-3.6",
    # --- MEMSIC ---
    "mc3479": "1.7-3.6", "mmc34160pj": "2.16-3.6", "mmc5603nj": "1.62-3.6",
    "mmc5983ma": "1.62-3.6", "msa3xx": "1.62-3.6",
    # --- ScioSense ---
    "ens161": "1.71-3.6",
    # --- QST ---
    "qmc5883p": "2.16-3.6", "qmi8658": "1.71-3.6",
    "qmi8658c": "1.71-3.6", "qmp6988": "1.71-3.6",
    # --- Goertek ---
    "spa06": "1.7-3.6", "spl06": "1.7-3.6", "spl07": "1.7-3.6",
    # --- Panasonic ---
    "gcja5": "4.5-5.5",
    # --- MaxBotix LV-MaxSonar-EZ: 2.5-5.5V ---
    "mb1000": "2.5-5.5", "mb1001": "2.5-5.5", "mb1002": "2.5-5.5",
    "mb1003": "2.5-5.5", "mb1004": "2.5-5.5", "mb1005": "2.5-5.5",
    "mb1006": "2.5-5.5", "mb1007": "2.5-5.5", "mb1008": "2.5-5.5",
    "mb1009": "2.5-5.5", "mb1010": "2.5-5.5", "mb1013": "2.5-5.5",
    "mb1014": "2.5-5.5", "mb1020": "2.5-5.5", "mb1023": "2.5-5.5",
    "mb1024": "2.5-5.5", "mb1030": "2.5-5.5", "mb1033": "2.5-5.5",
    "mb1034": "2.5-5.5", "mb1040": "2.5-5.5", "mb1043": "2.5-5.5",
    "mb1044": "2.5-5.5", "mb1060": "2.5-5.5", "mb1061": "2.5-5.5",
    "mb1710": "2.5-5.5", "mb1711": "2.5-5.5", "mb1712": "2.5-5.5",
    # --- MaxBotix XL-MaxSonar: 3.0-5.5V ---
    "mb1200": "3.0-5.5", "mb1202": "3.0-5.5", "mb1210": "3.0-5.5",
    "mb1212": "3.0-5.5", "mb1220": "3.0-5.5", "mb1222": "3.0-5.5",
    "mb1230": "3.0-5.5", "mb1232": "3.0-5.5", "mb1240": "3.0-5.5",
    "mb1242": "3.0-5.5", "mb1260": "3.0-5.5", "mb1261": "3.0-5.5",
    "mb1300": "3.0-5.5", "mb1310": "3.0-5.5", "mb1320": "3.0-5.5",
    "mb1330": "3.0-5.5", "mb1340": "3.0-5.5", "mb1360": "3.0-5.5",
    "mb1361": "3.0-5.5",
    # --- MaxBotix I2CXL: 3.0-5.5V ---
    "mb1403": "3.0-5.5", "mb1413": "3.0-5.5", "mb1414": "3.0-5.5",
    "mb1423": "3.0-5.5", "mb1424": "3.0-5.5", "mb1433": "3.0-5.5",
    "mb1434": "3.0-5.5", "mb1443": "3.0-5.5", "mb1444": "3.0-5.5",
    "mb1603": "3.0-5.5", "mb1604": "3.0-5.5", "mb1613": "3.0-5.5",
    "mb1614": "3.0-5.5", "mb1623": "3.0-5.5", "mb1624": "3.0-5.5",
    "mb1633": "3.0-5.5", "mb1634": "3.0-5.5", "mb1643": "3.0-5.5",
    "mb1644": "3.0-5.5", "mb2530": "3.0-5.5", "mb2532": "3.0-5.5",
    # --- MaxBotix XL-WR: 3.0-5.5V ---
    "mb7040": "3.0-5.5", "mb7051": "3.0-5.5", "mb7052": "3.0-5.5",
    "mb7053": "3.0-5.5", "mb7060": "3.0-5.5", "mb7062": "3.0-5.5",
    "mb7066": "3.0-5.5", "mb7070": "3.0-5.5", "mb7072": "3.0-5.5",
    "mb7076": "3.0-5.5", "mb7092": "3.0-5.5", "mb7137": "3.0-5.5",
    "mb7138": "3.0-5.5", "mb7139": "3.0-5.5", "mb7150": "3.0-5.5",
    "mb7155": "3.0-5.5",
    # --- MaxBotix HRXL-WR: 2.7-5.5V ---
    "mb7334": "2.7-5.5", "mb7344": "2.7-5.5", "mb7354": "2.7-5.5",
    "mb7360": "2.7-5.5", "mb7363": "2.7-5.5", "mb7364": "2.7-5.5",
    "mb7366": "2.7-5.5", "mb7368": "2.7-5.5", "mb7369": "2.7-5.5",
    "mb7380": "2.7-5.5", "mb7383": "2.7-5.5", "mb7384": "2.7-5.5",
    "mb7386": "2.7-5.5", "mb7388": "2.7-5.5", "mb7389": "2.7-5.5",
    "mb7560": "2.7-5.5", "mb7563": "2.7-5.5", "mb7564": "2.7-5.5",
    "mb7566": "2.7-5.5", "mb7568": "2.7-5.5", "mb7569": "2.7-5.5",
    "mb7580": "2.7-5.5", "mb7583": "2.7-5.5", "mb7584": "2.7-5.5",
    "mb7586": "2.7-5.5", "mb7588": "2.7-5.5", "mb7589": "2.7-5.5",
    "mb8000": "3.0-5.5", "mb8450": "3.0-5.5", "mb8460": "3.0-5.5",
    "mb8480": "3.0-5.5", "hrxlmaxsonarwr": "2.7-5.5",
    # --- Hi-Link radar ---
    "hlkld2410": "5.0-5.0", "hlkld2410b": "5.0-5.0",
    "hlkld2410s": "3.0-3.6", "ld2410b": "5.0-5.0",
    "ld2410c": "5.0-5.0", "ld2410d": "5.0-5.0", "ld2410s": "3.0-3.6",
    "ld2411": "5.0-5.0", "ld2411s": "5.0-5.0", "ld2412": "5.0-5.0",
    "ld2413": "5.0-5.0", "ld2415h": "5.0-5.0", "ld2420": "5.0-5.0",
    "ld2450": "5.0-5.0", "ld2451": "5.0-5.0", "ld2452": "5.0-5.0",
    "ld2460": "5.0-5.0", "ld2401": "5.0-5.0", "ld2402": "5.0-5.0",
    "ld6001": "3.0-3.6", "ld6001a": "3.0-3.6", "ld6001c": "3.0-3.6",
    "ld6002": "3.0-3.6", "ld6002c": "3.0-3.6", "ld6002h": "3.0-3.6",
    "ld6004": "3.0-3.6", "ld8001": "3.0-3.6", "ld8001b": "3.0-3.6",
    "ld8001h": "3.0-3.6", "ld012": "5.0-5.0", "ld020": "5.0-5.0",
    "ld021": "5.0-5.0", "ld101": "5.0-5.0", "ld101l": "5.0-5.0",
    "ld101v": "5.0-5.0", "ld1040": "5.0-5.0", "ld1040c": "5.0-5.0",
    "hlkfm22x": "5.0-5.0", "as201": "12.0-12.0", "as2019": "12.0-12.0",
    # --- Benewake LiDAR ---
    "tfluna": "3.7-5.2", "tfli2c": "3.7-5.2",
    "tfminis": "4.5-5.5", "tfminiplus": "4.5-5.5", "tfminii": "4.5-5.5",
    "tf02pro": "5.0-12.0", "tf02prow": "5.0-12.0", "tf02i": "5.0-12.0",
    "tf03": "5.0-24.0", "tf350": "5.0-24.0", "tfnova": "5.0-5.0",
    # --- Atlas Scientific ---
    "ezoph": "3.3-5.0", "ezoec": "3.3-5.0", "ezoorp": "3.3-5.0",
    "ezodo": "3.3-5.0", "ezortd": "3.3-5.0", "ezoco2": "3.3-5.0",
    "ezoflo": "3.3-5.0", "ezohum": "3.3-5.0", "ezoo2": "3.3-5.0",
    "ezoprs": "3.3-5.0", "ezorgb": "3.3-5.0", "phoem": "3.3-5.0",
    "dooem": "3.3-5.0", "ecoem": "3.3-5.0", "orpoem": "3.3-5.0",
    "rtdoem": "3.3-5.0",
    # --- Amphenol ---
    "t6615": "4.5-5.5", "t6703": "4.5-5.5", "t6713": "4.5-5.5",
    # --- Shanghai Belling ---
    "bl0906": "3.0-3.6", "bl0939": "3.0-3.6",
    "bl0940": "3.0-3.6", "bl0942": "3.0-3.6",
    # --- HiSilicon ---
    "cse7761": "3.0-3.6", "cse7766": "3.0-3.6",
    # --- Cirrus Logic ---
    "cs5460a": "3.0-3.6", "cs5464": "3.0-3.6", "cs5490": "3.0-3.6",
    # --- Asahi Kasei ---
    "ak8975": "2.4-3.6", "ak9750": "3.0-3.6",
    "ak9753": "3.0-3.6", "akm09918c": "1.65-3.6",
    # --- TE Connectivity ---
    "lwlp5000": "3.0-3.6", "ms4525do": "3.3-5.5",
    "ms580314ba": "1.8-3.6", "mprls": "3.0-3.6",
    "hte501": "2.0-5.5", "tee501": "2.0-5.5", "tsd305": "3.0-3.6",
    # --- Honeywell ---
    "hpma115": "5.0-5.0", "hpma115xx": "5.0-5.0",
    "hih61xx": "2.3-5.5", "honeywellabp": "3.0-3.6",
    "honeywellabp2": "1.8-3.6", "honeywellhih": "2.3-5.5",
    "hscdtd008a": "2.7-3.6",
    # --- Plantower ---
    "pms3003": "4.5-5.5", "pmsx003": "4.5-5.5",
    # --- Gas ---
    "cm1106": "4.5-5.5", "cbhchov4": "3.5-5.0",
    "pm1006": "4.5-5.5", "pm1006k": "4.5-5.5",
    "explorirm": "3.25-5.5", "envco2": "3.2-5.5",
    # --- Avia ---
    "hx710": "2.4-5.5", "hx710a": "2.4-5.5", "hx710b": "2.4-5.5",
    # --- DFRobot/Ultrasonic ---
    "a01nyub": "3.3-5.0", "urm07": "3.3-5.5", "urm09": "3.3-5.5",
    "urm13": "3.3-5.5", "us100": "2.4-5.5",
    # --- TI misc ---
    "bq27220": "2.4-4.5", "cd74hc4067": "2.0-6.0",
    "lmp91000": "2.7-5.25", "tsc2007": "1.5-3.6", "opt4001": "1.6-3.6",
    # --- Touch ---
    "ft5336": "2.6-3.3", "ft6x06": "2.6-3.3", "uft6336u": "2.6-3.3",
    "cst816d": "2.6-3.6", "cst8xx": "2.6-3.6", "tt21100": "1.7-3.6",
    "iqs5xx": "2.0-3.5", "cy8cmbr3102": "1.7-5.5",
    "sx8634": "2.4-3.6", "xpt2046": "2.7-5.25",
    # --- Gxht ---
    "cht8305": "1.35-5.5", "cht8310": "1.35-5.5", "cht832x": "1.35-5.5",
    # --- HopeRF ---
    "th02": "2.1-3.6", "barometerhp20x": "3.0-3.6", "hp206c": "3.0-3.6",
    # --- Würth ---
    "wsenpdus": "1.7-3.6", "wsentids": "1.7-3.6", "wsenpads": "1.7-3.6",
    "wsenhids": "1.7-3.6", "wsenitds": "1.7-3.6", "wsenisds": "1.7-3.6",
    # --- Omron ---
    "2smpb": "1.7-3.6", "d6fph": "3.0-3.6",
    # --- Acconeer ---
    "a111": "1.8-3.6", "xm125": "1.8-3.6",
    # --- Misc ---
    "s11059": "2.25-3.6", "gdk101": "3.3-5.0", "rfd77402": "2.7-3.3",
    "sds021": "4.7-5.3", "pms7003t": "4.5-5.5",
    "hmc6343": "2.7-3.6", "hmc6352": "2.7-3.6",
    "mt6701": "3.0-3.6", "s5851a": "2.4-5.5", "nst1001": "1.5-5.5",
    "f75303": "3.0-3.6", "lc709203f": "2.4-4.5",
    "ags01db": "3.0-5.5", "hyt271": "2.7-5.5", "ips7100": "5.0-5.0",
    "c4001": "3.0-3.6", "hm330x": "5.0-5.0", "hm3301": "5.0-5.0",
    "hrg15": "5.0-24.0", "hydreonrgxx": "5.0-24.0", "rg15": "5.0-24.0",
    "gp2y0a41sk0f": "4.5-5.5", "gp2y0e03": "2.7-5.3",
    "pzem004t": "5.0-5.0",
    "ags2616": "3.0-5.5", "ags3870": "3.0-5.5", "ags3871": "3.0-5.5",
    "rcwl0516": "4.0-28.0", "rcwl9610": "3.0-5.5", "rcwl9620": "3.0-5.5",
    "ncs36000": "3.0-5.5",
    "xgzp6897d": "3.0-5.5", "xgzp68xx": "3.0-5.5",
    "mr24hpc1": "5.0-5.0", "mr60bha2": "5.0-5.0",
    "mtp40": "3.6-5.5", "mg811": "5.0-6.0",
    "rd03": "5.0-5.0", "rd03d": "5.0-5.0",
    "a02yyuw": "3.0-5.5", "jsnsr04t": "3.0-5.5", "dypme007": "3.0-5.5",
    "ggreg20v3": "3.3-5.0", "gr1030": "3.0-3.6",
    "tx20": "3.0-3.6", "isys4001": "3.0-3.6",

    # --- Additional voltage entries (from datasheet research) ---

    # TI AFE / capacitance-to-digital
    "afe4490": "2.0-3.6", "afe44xx": "2.0-3.6", "afe4950": "1.7-3.6",
    "fdc1004": "3.0-3.6", "fdc2x1x": "2.7-3.6",

    # TI INA current/power monitors
    "ina219b": "3.0-5.5", "ina230": "2.7-5.5", "ina232": "1.7-5.5", "ina236": "1.7-5.5",

    # TI HDC humidity/temperature
    "hdc2021": "1.62-3.6", "hdc2022": "1.62-3.6", "hdc3020": "1.62-3.6", "hdc3022": "1.62-3.6",

    # TI temperature sensors
    "lm35": "4.0-30.0", "lm35c": "4.0-30.0", "lm35d": "4.0-30.0",
    "lm45b": "4.0-10.0", "lm50b": "4.5-10.0", "lm50c": "4.5-10.0",
    "lm95234": "3.0-5.5", "tmp108": "1.4-3.6", "tmp112": "1.4-3.6",
    "tmp114": "1.9-5.5", "tmp116": "1.9-5.5", "tmp11x": "1.9-5.5",
    "tmp126": "1.62-5.5", "tmp435": "2.7-5.5", "tmp61": "1.8-5.5",

    # TI optical / magnetic
    "opt3004": "1.6-3.6", "opt3101": "3.0-5.0",
    "tmag5170": "2.3-5.5", "tmag5273": "1.7-3.6",

    # TI misc
    "lm335a": "0.5-40.0", "lm75b": "2.8-5.5",

    # ST IIS industrial MEMS
    "iis2dh": "1.71-3.6", "iis2iclx": "1.71-3.6", "iis328dq": "2.16-3.6",
    "iis3dhhc": "1.71-3.6", "iis3dwb": "2.1-3.6",

    # ST LIS accelerometers
    "lis2de12": "1.71-3.6", "lis2dh": "1.71-3.6", "lis2ds12": "1.62-1.98",
    "lis2dux12": "1.71-3.6",

    # ST LSM IMUs
    "lsm6": "1.71-3.6", "lsm6dso32": "1.71-3.6", "lsm6dsv32x": "1.71-3.6",
    "lsm6dsv80x": "1.71-3.6",

    # ST LSM303 combos
    "lsm303accel": "2.16-3.6", "lsm303c": "1.71-3.6",
    "lsm303dlh": "2.16-3.6", "lsm303dlhc": "2.16-3.6",
    "lsm303dlhmag": "2.16-3.6",

    # ST L3G gyroscopes / LPS pressure
    "l3g": "2.4-3.6", "l3gd20u": "2.4-3.6",
    "lps22": "1.7-3.6", "lps25h": "1.7-3.6", "lps28": "1.7-3.6",

    # TDK ICM/ICG IMUs
    "icg20660": "1.71-3.45", "icm42686": "1.71-3.6",
    "icm45605s": "1.71-3.6", "icm45686s": "1.71-3.6", "icm45688p": "1.71-3.6",

    # TDK ICP pressure
    "icp10100": "1.7-1.89", "icp101xx": "1.7-1.89",
    "icp20100": "1.62-1.98", "icp201xx": "1.62-1.98",

    # NXP
    "fxas210002c": "2.1-3.6", "fxls8974": "1.71-3.6", "mma8653": "1.95-3.6",
    "p3t1755": "1.4-3.6",

    # MEMSIC / Melexis
    "mc3419": "1.7-3.6",
    "mlx90394": "1.7-3.6", "mlx90621": "2.6-3.3", "mlx90641": "3.0-3.6",

    # Microchip
    "mcp3427": "2.7-5.5", "mcp970x": "2.3-5.5", "mcp9800": "2.7-5.5",
    "tcn75a": "2.7-5.5",

    # onsemi / iSentek / Silicon Labs
    "nct75": "3.0-5.5", "ist8310": "1.71-3.6",
    "si7006": "1.9-3.6", "si7060": "1.71-5.5", "si7210": "1.71-5.5",

    # Semtech / ams-OSRAM optical
    "sx9500": "2.7-5.5",
    "tcs3210": "2.7-5.5", "tcs3400": "2.7-3.6", "tcs3472": "2.7-3.3",
    "tmd2620": "2.7-3.6", "tmd3725": "1.7-2.0",
    "tsl2540": "1.7-2.0", "tsl2550": "2.7-5.5",

    # Vishay
    "vcnl3040": "2.5-3.6", "vcnl36825t": "2.64-3.6", "veml6031": "2.5-3.6",

    # Sensirion
    "sht3xd": "2.15-5.5",

    # TE Connectivity / MEAS pressure
    "ms5607": "1.8-3.6", "ms5637": "1.5-3.6", "ms5xxx": "1.5-3.6",
    "hp03s": "2.2-3.6", "hp303b": "1.7-3.6", "tsys01": "2.7-3.6",

    # ScioSense
    "ens190": "4.5-5.5", "ens220": "1.62-1.98",

    # ROHM / Renesas / Honeywell / PixArt
    "ml8511": "2.7-3.6", "hs400x": "1.8-3.6", "isl29035": "2.25-3.63",
    "pmw3360": "3.3-3.6", "pmw3901": "1.8-2.1",

    # ams ToF / TE humidity / misc
    "tmf8801": "2.7-3.3", "tmf882x": "2.7-3.6",
    "htu21": "1.5-3.6",
    "ams5812": "3.0-5.5", "ams5915": "3.0-5.5",

    # Broadcom ToF
    "afbrs50": "5.0-5.0",

    # --- Generic modules ---
    "hcsr04": "5.0-5.0",           # HC-SR04 ultrasonic (5V)
    "jsnsr04t": "3.0-5.5",         # JSN-SR04T waterproof ultrasonic
    "sr04m": "3.0-5.5",            # SR04M waterproof ultrasonic variant
    "tof10120": "3.0-5.0",         # TOF10120 laser rangefinder
    "me007": "3.0-5.5",            # ME007 ultrasonic rangefinder
    "us100": "2.4-5.5",            # US-100 ultrasonic (has both 3.3V and 5V mode)
    "tct40": "5.0-5.0",            # TCT40 ultrasonic transducer driver
    "fc28": "3.3-5.0",             # FC-28 soil moisture module
    "fc37": "3.3-5.0",             # FC-37 rain sensor module
    "gl5528": "3.3-5.0",           # GL5528 LDR (voltage divider circuit)
    "ky040": "3.3-5.0",            # KY-040 rotary encoder module
    "gp20u7": "3.0-5.5",           # GP20U7 GPS module
    "gy26": "3.0-5.0",             # GY-26 compass module
    "yfs201waterflow": "5.0-24.0",  # YF-S201 water flow sensor
    "sct013": "3.3-3.3",           # SCT-013 CT clamp (analog output)
    "ctclamp": "3.3-5.0",          # CT clamp module
    "fingerprintgrow": "3.3-6.0",  # R307/R503 fingerprint modules
    "cc1101": "1.8-3.6",           # TI CC1101 RF transceiver
    "zmpt101b": "3.3-5.0",         # ZMPT101B voltage transformer module
    "ttp223": "2.0-5.5",           # TTP223 touch sensor
    "ttp229bsf": "2.4-5.5",        # TTP229 16-key touch pad
    "tcrt5000": "3.3-5.0",         # TCRT5000 reflective sensor module
    "pt100": "3.3-5.0",            # PT100 RTD amplifier module (MAX31865)
    "l58touch": "3.3-3.3",         # L58 touch sensor

    # --- MaxBotix ultrasonic ---
    "mb7374": "3.0-5.5", "mb7375": "3.0-5.5", "mb7395": "3.0-5.5",
    "mb7534": "3.0-5.5", "mb7544": "3.0-5.5", "mb7554": "3.0-5.5",
    "mb7574": "3.0-5.5", "mb7850": "3.0-5.5", "mb7851": "3.0-5.5",
    "mb7853": "3.0-5.5", "mb7854": "3.0-5.5",

    # --- Benewake LiDAR/ToF ---
    "lc02": "5.0-5.0",             # Benewake LC02 short-range
    "tfs20l": "5.0-5.0",           # Benewake TFS20-L
    "hornrt": "5.0-5.0",           # Benewake Horn-RT
    "hornx2pro": "9.0-28.0",       # Benewake Horn-X2-Pro (industrial)

    # --- Senseair CO2 ---
    "k30": "4.5-14.0",             # Senseair K30
    "k70": "4.5-5.25",             # Senseair K70
    "senseair": "4.5-5.25",        # Senseair S8

    # --- Melexis ---
    "mlx90642": "3.0-3.6",         # MLX90642 IR array
    "us1881": "3.5-24.0",          # US1881 hall-effect latch

    # --- Murata ---
    "sca100t": "5.0-5.0",          # SCA100T inclinometer
    "scl3300": "3.0-3.6",          # SCL3300 inclinometer
    "scl3400": "3.0-3.6",          # SCL3400 inclinometer
    "zpa4756": "1.65-3.6",         # ZPA4756 pressure sensor (Murata/SureSensor)

    # --- NXP pressure ---
    "mpx5999d": "4.75-5.25",       # NXP MPX5999D
    "mpxa4250a": "4.75-5.25",      # NXP MPXA4250A
    "mpxh6115a": "4.85-5.35",      # NXP MPXH6115A
    "mpxh6400a": "4.85-5.35",      # NXP MPXH6400A
    "mpxhz6250a": "4.85-5.35",     # NXP MPXHZ6250A
    "pca9536": "2.3-5.5",          # NXP PCA9536 I/O expander

    # --- STMicroelectronics ---
    "stlm20dd9f": "2.4-5.5",       # STLM20 analog temp sensor
    "stlm20w87f": "2.4-5.5",       # STLM20 analog temp sensor
    "stpm34": "3.0-3.6",           # STPM3x energy metering
    "lsm6dsv320x": "1.71-3.6",     # LSM6DSV32OX IMU

    # --- Sensirion ---
    "mts4x": "1.08-3.6",           # STS4x temperature sensor
    "sfm3200": "4.5-5.5",          # SFM3x00 flow sensor

    # --- Panasonic ---
    "ekmb1107112": "3.0-6.0",      # Panasonic PIR sensor
    "ekmc4607112k": "3.0-6.0",     # Panasonic PIR sensor
    "sngcja5": "5.0-5.0",          # Panasonic SN-GCJA5 PM sensor

    # --- DFRobot modules ---
    "sen0153": "3.3-5.0",          # DFRobot ultrasonic
    "sen0321": "3.3-5.5",          # DFRobot ozone sensor
    "sen0395": "5.0-12.0",         # DFRobot mmWave radar

    # --- Plantower ---
    "pm25": "5.0-5.0",             # Plantower PMSx003

    # --- Other well-known ---
    "ct1780": "1.62-3.6",          # Sensylink CT1780 temp sensor
    "zyaura": "4.5-5.5",           # ZyAura CO2 sensor module
    "k30": "4.5-14.0",             # Senseair K30
    "gsl1680": "2.8-3.3",          # Silead GSL1680 touch controller
    "rv3032": "1.3-5.5",           # Micro Crystal RV-3032 RTC
    "rp2040": "1.8-3.3",           # Raspberry Pi RP2040 (temp sensor built-in)
    "tcs230": "2.7-5.5",           # TCS230 color sensor
    "tsl235r": "2.7-5.5",          # TSL235R light-to-frequency
    "qmc5583l": "2.16-3.6",        # QMC5883L compass

    # --- Holtek/Best Modules (common 3-5V modules) ---
    "bm22s2021": "3.0-5.0", "bm22s3021": "3.0-5.0", "bm22s3031": "3.0-5.0",
    "bm22s3221": "3.0-5.0", "bm22s3421": "3.0-5.0", "bm22s4221": "3.0-5.0",
    "bm25s2021": "2.7-5.5", "bm25s2621": "2.7-5.5", "bm25s3221": "3.0-5.0",
    "bm25s3321": "3.0-5.0", "bm25s3421": "3.0-5.0", "bm25s4021": "3.0-5.0",
    "bm32s2031": "3.0-5.0", "bm32s3021": "3.0-5.0",
    "bm42s3021": "3.0-5.0", "bm42s5321": "3.0-5.0",
    "bm62s2201": "3.0-5.0", "bm62s2301": "3.0-5.0", "bm62s6021": "3.0-5.0",
    "bm92s2021": "3.0-5.0",

    # --- ScioSense ---
    "sciosenseas60xx": "1.8-3.6",   # AS6031/AS6040 ultrasonic flow
    "sciosenseens16x": "1.8-3.6",   # ENS160/161 MOx gas sensor
    "sciosenseens21x": "1.8-3.6",   # ENS210/211 temp/humidity

    # --- TE Connectivity ---
    "msp300": "4.75-5.25",         # MSP300 pressure transducer

    # --- TDK ---
    "icu10201": "1.8-3.6",         # ICU-10201 ultrasonic ToF

    # --- Honeywell ---
    "ah1815": "3.0-5.5",           # AH1815 hall-effect
    "i2casdx": "4.75-5.25",        # ASDX pressure sensor

    # --- Microchip ---
    "tc1046": "2.5-5.5",           # TC1046 analog temp sensor
    "tc1047": "2.7-4.4",           # TC1047 analog temp sensor
    "jc424": "2.0-3.6",            # MCP9844 renamed
    "xpt2046touchpad": "2.7-5.25",  # XPT2046 touch controller

    # --- Vishay ---
    "vncl4020c": "2.5-3.6",        # VCNL4020C proximity/ambient light
    # (TCRT5000 already added above in generic)

    # --- Bosch ---
    "bmv23m001": "1.71-3.6",       # BMV23M001 motion sensor
    "7semibno08x": "2.4-3.6",      # BNO08x 9-DoF IMU
    "7semico2th": "1.8-3.6",       # BME688 variant (Bosch 7semi)
    "rak12034": "1.71-3.6",        # RAK12034 uses BME680

    # --- RAKWireless modules ---
    "rak12010": "3.0-3.6", "rak12019": "3.0-3.6", "rak12021": "3.0-3.6",
    "rak12023": "3.0-3.6", "rak12025": "3.0-3.6", "rak12039": "5.0-5.0",
    "rak14002": "3.0-3.6",

    # --- Xiaomi BLE sensors ---
    "xiaomilywsd02mmc": "3.0-3.0",  # CR2032 battery
    "xiaomixmwsdj04mmc": "3.0-3.0",

    # --- Atlas Scientific probes (circuit boards) ---
    "doprobe": "3.3-5.0",          # EZO-DO circuit
    "ecprobe": "3.3-5.0",          # EZO-EC circuit
    "orpprobe": "3.3-5.0",         # EZO-ORP circuit
    "phprobe": "3.3-5.0",          # EZO-pH circuit
    "pt1000probe": "3.3-5.0",      # EZO-RTD circuit

    # --- Garmin ---
    "lidarlightv3hp": "4.75-5.25",  # Garmin LIDAR-Lite v3HP

    # --- Winsen active sensors ---
    "mhz1341b": "3.3-5.5",         # Winsen MH-Z1341B NDIR
    "mtp40f": "4.2-5.5",           # MemsFrontier MTP40-F NDIR CO2
    "sp3s": "5.0-5.0",             # Shinyei SP3S semiconductor gas
    "pm2005": "5.0-5.0",           # Cubic PM2005 laser particle
    "ze29ac2h5oh": "3.7-9.0",      # Winsen ZE29A electrochemical module (common spec)
    "gm1602": "5.0-5.0",           # Winsen GM1602 semiconductor gas module
    "mhz9041a": "5.0-5.0",         # Winsen MHZ9041A gas sensor module
    "zwc102": "5.0-5.0",           # Winsen ZW-C102 water quality module

    # --- Other remaining well-known ---
    "tl555q": "4.5-16.0",          # TI TL555Q CMOS timer
    "tmp9a00": "1.62-3.6",         # TI TMP9A sensor (via I3C)
    "ms01": "3.0-3.3",             # Sonoff MS01 soil moisture
    "ppd71": "5.0-5.0",            # Shinyei PPD71 particle sensor
    "sm300d2": "5.0-5.0",          # Amphenol SM300D2 multi-gas
    "bluxv30b": "2.7-5.5",         # B-Lux-V30B ambient light
    "kmeteriso": "5.0-5.0",        # M5Stack K-Meter thermocouple
    "mmr902": "3.0-3.6",           # Murata MMR902 radar
    "wsenpdms": "1.2-3.6",         # Würth WSEN-PDUS pressure
    "amt25": "4.75-5.25",          # CUI AMT25 encoder
    "am4096": "3.0-5.5",           # RLS AM4096 encoder
    "zmod4450": "1.7-3.6",         # Renesas ZMOD4450 gas sensor
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
    # ===== Temperature / Humidity / Pressure =====
    "bme280": ["i2c", "spi"],
    "bme34m101": ["i2c", "spi"],
    "bme63m001": ["i2c"],
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
    "mpu6050": ["i2c", "spi"],
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
    "gl5528": ["analog"],
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
    "us100": ["uart"],
    "nhcsr04": ["gpio"],
    "sr04": ["gpio"],
    "sr04m": ["gpio"],
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
    "gy26": ["i2c", "uart"],
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
    "pt100": ["spi"],
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
    "ky040": ["gpio"],
    "dht": ["gpio"],
    "us1881": ["gpio"],
    "ah1815": ["gpio"],
    "tli4970": ["spi"],
    "tli4971": ["spi"],
    "tlv493d": ["i2c"],
    "ak9750": ["i2c"],
    "tcrt5000": ["analog"],
    "fc28": ["analog"],
    "fc37": ["analog"],
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
    "rp2040": ["i2c", "spi"],
    "cv7": ["uart"],
    "aci10kantemp": ["analog"],
    "esp32thermistor": ["analog"],
    "rtd10k": ["analog"],
    "tfa433receiver": ["gpio"],
    "yfs201waterflow": ["gpio"],
    "mprls": ["i2c", "spi"],
    "dnmsi2c": ["i2c"],
    "sb041": ["i2c"],
    "dfr0300": ["analog"],
    "pd10lx": ["analog"],
    "mpbmp3xxfull": ["i2c", "spi"],
    "mpm10": ["i2c"],
    "xiaomilywsd02mmc": ["i2c"],
    "xiaomixmwsdj04mmc": ["i2c"],
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
    "bm25s2621": ["uart"],
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
    "rak12019": ["analog"],
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
    "frn03h": ["gpio"],           # Winsen FRn03H flow — Hall pulse
    "frn03p": ["gpio"],           # Winsen FRn03P flow — Hall pulse
    "ea134": ["analog"],          # Winsen EA-134 vibration — analog
    "gm1602": ["analog"],         # Winsen GM1602 CO — analog
    "msz202": ["uart"],           # Winsen MS-Z202 humidity — UART
    "msz302": ["uart"],           # Winsen MS-Z302 humidity — UART
    "sp3s": ["analog"],           # Winsen SP3S gas — analog
    # --- Best Modules Corp (Holtek) sensor modules ---
    "bce22s4421": ["gpio"],         # BCE-22S4421 microwave radar — digital output
    "bm42s3021": ["uart"],          # BM42S3021 thermocouple — UART
    "bme26m301": ["uart"],          # BME26M301 air velocity — UART
    "bme33m251": ["uart"],          # BME33M251 temp/humidity — UART
    "bme82m131": ["i2c"],           # BME82M131 VEML7700 light — I2C
    "bme82m131a": ["i2c"],          # BME82M131A VEML7700 light — I2C
    "bmh05102": ["uart"],           # BMH05102 body fat scale — UART
    "bml36m001": ["i2c"],           # BML36M001 VL53L1X ToF — I2C
    "ht7m2126": ["gpio"],           # HT7M2126 PIR module — digital output
    "ht7m2176": ["gpio"],           # HT7M2176 PIR module — digital output
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
    "thermopile": ["analog"],
    "thermal_conduction": ["analog"],
    "mems": ["i2c"],
    "pid": ["analog"],
}

# MaxBotix ultrasonic sensors all have analog + PWM + UART output
MAXBOTIX_PROTOCOLS = ["analog", "uart", "pwm"]

# Benewake ToF LiDAR sensors — default UART, some also support I2C
BENEWAKE_PROTOCOLS = ["uart", "i2c"]

# Hi-Link radar modules (LD-series) — all use UART
HILINK_RADAR_PROTOCOLS = ["uart"]
HILINK_IMU_PROTOCOLS = ["uart"]

# Atlas Scientific probes/modules — all support I2C and UART
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

        # 1. IC protocol lookup — always union (adds secondary interfaces like SPI)
        if sid in IC_PROTOCOLS:
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

        # 3. MaxBotix ultrasonic sensors (all have analog + UART + PWM)
        if not added and "maxbotix" in sensor["sources"]:
            sensor["protocols"].update(MAXBOTIX_PROTOCOLS)
            added = True

        # 4. Benewake ToF LiDAR (UART + I2C)
        if not added and "benewake" in sensor["sources"]:
            sensor["protocols"].update(BENEWAKE_PROTOCOLS)
            added = True

        # 5. Hi-Link modules
        if not added and "hilink" in sensor["sources"]:
            stype = (sensor.get("type") or "").lower()
            if stype == "radar":
                sensor["protocols"].update(HILINK_RADAR_PROTOCOLS)
                added = True
            elif stype == "imu":
                sensor["protocols"].update(HILINK_IMU_PROTOCOLS)
                added = True

        # 6. Atlas Scientific probes (all I2C + UART)
        if not added and "atlas_scientific" in sensor["sources"]:
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
    re.compile(r"DFRobot Standard library\S*\.?\s*", re.IGNORECASE),
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
    # Strip remaining bare brand names anywhere
    re.compile(rf"{_BRANDS}\s*", re.IGNORECASE),
    # Strip SKU references like "(SKU:SEN0206/SEN0263)"
    re.compile(r"\s*\(SKU[:\s][^)]*\)", re.IGNORECASE),
    # Strip trailing period if description is very short after cleaning
    re.compile(r"\.\s*$"),
]


def clean_name(name: str, sensor_id: str = "") -> str:
    """Strip brand names, 'Library', 'Breakout', etc. from sensor names.

    If the cleaned name doesn't contain any part of the sensor_id (indicating
    the library name is completely disconnected from the IC), falls back to
    uppercasing the sensor_id.
    """
    for pat in _NAME_CLEAN:
        name = pat.sub(" " if pat.pattern.startswith(r"\s{2") else "", name)
    # Collapse spaces, strip punctuation and leading underscores
    cleaned = re.sub(r"\s{2,}", " ", name).strip(" -,_")

    # If cleaned name is empty or doesn't relate to the IC at all,
    # fall back to uppercased sensor ID
    if sensor_id and cleaned:
        sid_alpha = re.sub(r"[^a-z0-9]", "", sensor_id.lower())
        name_alpha = re.sub(r"[^a-z0-9]", "", cleaned.lower())
        # If the name doesn't share a 3+ char substring with the ID, it's disconnected
        if len(sid_alpha) >= 3 and sid_alpha[:3] not in name_alpha and sid_alpha not in name_alpha:
            cleaned = sensor_id.upper()
        else:
            # Strip unknown prefixes/suffixes around the IC name
            # e.g., "ASTRON_CCS811" -> "CCS811", "BH1750_WE" -> "BH1750"
            # Use uppercase for comparison to handle mixed-case names
            sid_upper = sensor_id.upper()
            cleaned_upper = cleaned.upper()
            if sid_upper in cleaned_upper and cleaned_upper != sid_upper:
                idx = cleaned_upper.index(sid_upper)
                after = cleaned_upper[idx + len(sid_upper):].lstrip(" _-")
                if after and " " not in after:
                    after = ""
                cleaned = (sid_upper + (" " + after if after else "")).strip()

    # If the cleaned name is all lowercase and looks like a raw IC ID
    # (no spaces, just alphanumeric+underscore), uppercase it
    if cleaned and cleaned == cleaned.lower() and " " not in cleaned:
        cleaned = cleaned.upper()

    return cleaned or sensor_id.upper()


def clean_description(desc: str) -> str:
    """Strip brand names and boilerplate from descriptions.

    After pattern cleaning, also discards results that are just a bare IC name
    (e.g. "GSL1680") or a bare IC name + generic suffix like "-sensor".
    """
    for pat in _DESC_CLEAN:
        desc = pat.sub("", desc)
    desc = desc.strip(" -,_")
    # If cleaned result is just an IC-like identifier (alphanumeric, possibly
    # with hyphens/underscores), it carries no search value — discard it
    if desc and re.match(r'^[A-Za-z0-9][-A-Za-z0-9_]*$', desc) and len(desc) < 30:
        return ""
    return desc


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
    with open(alias_file) as f:
        return json.load(f)


def resolve_id(raw_id: str, aliases: dict[str, str]) -> str:
    """Resolve an IC ID through the alias table."""
    return aliases.get(raw_id, raw_id)


def load_source(data_dir: Path, source_name: str) -> list[dict]:
    """Load sensors from a single source JSON file."""
    path = data_dir / "sensors" / f"{source_name}.json"
    if not path.exists():
        print(f"  Warning: {path} not found, skipping", file=sys.stderr)
        return []
    with open(path) as f:
        data = json.load(f)
    return data.get("sensors", [])


def merge_sensors(data_dir: Path, aliases: dict[str, str], quiet: bool = False) -> dict[str, dict]:
    """Merge all sources into a single dict of sensor entries."""
    merged: dict[str, dict] = {}

    for source_name in SOURCE_ORDER:
        sensors = load_source(data_dir, source_name)
        is_tier3 = source_name in TIER3_SOURCES

        if not quiet:
            print(f"  {source_name}: {len(sensors)} sensors")

        for raw in sensors:
            raw_id = raw.get("id", "").strip().lower()
            if not raw_id:
                continue

            canonical_id = resolve_id(raw_id, aliases)
            if canonical_id in SKIP_IDS or raw_id in SKIP_IDS:
                continue

            existing = merged.get(canonical_id)

            # If the raw ID was an alias, the canonical ID's own entry
            # should override the name (e.g. dht22 overrides am2302's name)
            is_alias = raw_id != canonical_id

            if existing is None:
                # New entry
                merged[canonical_id] = {
                    "id": canonical_id,
                    "name": clean_name(raw.get("name", raw_id), canonical_id),
                    "manufacturer": normalize_manufacturer(raw.get("manufacturer")),
                    "type": raw.get("type"),
                    "voltage": raw.get("voltage"),
                    "datasheet_url": raw.get("datasheet_url"),
                    "description": clean_description(raw.get("description", "")),
                    "source_tier": "breakout_only" if is_tier3 else "primary",
                    "measures": set(raw.get("measures", [])),
                    "protocols": set(raw.get("protocol", [])),
                    "platforms": set(raw.get("platforms", [])),
                    "urls": list(raw.get("urls", [])),
                    "sources": [source_name],
                    "_from_alias": is_alias,
                }
            else:
                # Enrich existing entry
                # If this is the canonical ID entry and the existing was created
                # by an alias, upgrade name and popularity
                if not is_alias and existing.get("_from_alias"):
                    existing["name"] = clean_name(raw.get("name", existing["name"]), canonical_id)

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

                # Description: keep longest, max 200 chars
                new_desc = clean_description(raw.get("description") or "")
                if len(new_desc) > len(existing["description"] or ""):
                    existing["description"] = new_desc[:200]

                # Upgrade tier if enriched by non-tier3 source
                if not is_tier3 and existing["source_tier"] == "breakout_only":
                    existing["source_tier"] = "primary"

                # Track provenance
                if source_name not in existing["sources"]:
                    existing["sources"].append(source_name)

    return merged


def build_db(merged: dict[str, dict], output_path: Path, quiet: bool = False):
    """Create SQLite database from merged sensor data."""
    # Delete existing DB
    for suffix in ("", "-wal", "-shm"):
        p = Path(str(output_path) + suffix)
        if p.exists():
            p.unlink()

    conn = sqlite3.connect(str(output_path))
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
            (s["description"] or "")[:200] or None,
            s["source_tier"],
            json.dumps(s["sources"]),
        ))

        for m in sorted(s["measures"]):
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

    conn.commit()
    conn.execute("ANALYZE")
    conn.execute("VACUUM")
    conn.close()

    if not quiet:
        print_stats(output_path)


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
