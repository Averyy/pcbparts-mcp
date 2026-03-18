"""Board-specific overrides for known source-data errors.

Component value/description fixes, metadata overrides (key_ics, description),
tag replacements, and net pin corrections.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Component overrides: (slug, ref) → {field: new_value}
# ---------------------------------------------------------------------------

BOARD_OVERRIDES: dict[tuple[str, str], dict[str, str]] = {
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
    # HackRF One: crystals have value "2x2 header" from shared footprint
    ("hackrf-one", "X1"): {"value": "25MHz"},
    ("hackrf-one", "X2"): {"value": "12MHz"},
    # Adafruit ADS1115 ADC: U1 value/description missing
    ("adafruit-ads1115-adc", "U1"): {
        "value": "ADS1115IDGST",
        "description": "16-bit 4-channel I2C ADC",
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
    # iCEBreaker: L1/L2 are ferrite beads
    ("icebreaker", "L1"): {"value": "ferrite bead"},
    ("icebreaker", "L2"): {"value": "ferrite bead"},
    # SparkFun LSM6DSO: L1 is ferrite bead
    ("sparkfun-lsm6dso", "L1"): {"value": "ferrite bead"},
    # Blues Notecarrier-A: L1 is 2.2uH
    ("blues-notecarrier-a", "L1"): {"value": "2.2uH"},
    # SparkFun UM980: L2 has crazy value (30H!), it's a ferrite bead
    ("sparkfun-um980-triband", "L2"): {"value": "ferrite bead"},
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
}


# ---------------------------------------------------------------------------
# Board metadata overrides: slug → {key_ics: [...], description: "..."}
# ---------------------------------------------------------------------------

BOARD_META_OVERRIDES: dict[str, dict] = {
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
        "key_ics": ["SE4150L", "MAX2112"],
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
        "key_ics": ["PF1510", "MCIMX6Z0DVM09AB"],
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
        "key_ics": ["ATMEGA2560", "FT232RL"],
    },
    "sparkfun-iot-bldc-motor": {
        "key_ics": ["ESP32-WROOM-32D", "TMC6300"],
    },
    "sparkfun-lsm6dso": {
        "key_ics": ["LSM6DSO"],
    },
}


# ---------------------------------------------------------------------------
# Tag overrides: slug → [tags] (REPLACEMENT, not additive)
# ---------------------------------------------------------------------------

TAG_OVERRIDES: dict[str, list[str]] = {
    "darth-vadar-2-4-ghz-fmcw-radar": ["rf-sdr", "radar-fmcw"],
    "adf4158-10-ghz-fmcw-lo": ["rf-sdr", "radar-fmcw"],
    "simplefmcwradar-rf-board": ["rf-sdr", "radar-fmcw"],
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
}


# ---------------------------------------------------------------------------
# Net pin fixes: (slug, bad_pin) → correct_pin
# ---------------------------------------------------------------------------

NET_PIN_FIXES: dict[tuple[str, str], str] = {
    ("adafruit-max31865-rtd", "U1.ANGD"): "U1.AGND",
}
