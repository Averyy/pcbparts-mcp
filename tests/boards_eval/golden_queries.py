"""Golden query definitions for board search quality evaluation.

Each GoldenQuery captures:
- Search parameters (what to search for)
- Ground truth (what results are expected)
- Metadata (category, description, holdout flag)
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GoldenQuery:
    """A single annotated search query with expected results."""

    id: str  # e.g. "comp-mcp73831"
    category: str  # component-exact, text-functional, etc.
    description: str  # Why this query matters

    # Search params (passed to db.search())
    query: str | None = None
    component: str | None = None
    tag: str | list[str] | None = None
    org: str | None = None
    layers: int | None = None
    limit: int = 10

    # Ground truth
    must_include: list[str] = field(default_factory=list)  # Slugs that MUST appear
    must_exclude: list[str] = field(default_factory=list)  # Slugs that MUST NOT appear
    expected_first: str | None = None  # Expected top result slug (for MRR)
    expected_total_range: tuple[int, int] | None = None  # (min, max) inclusive

    holdout: bool = False  # Reserve for overfitting detection


# ---------------------------------------------------------------------------
# Golden query set
# ---------------------------------------------------------------------------

GOLDEN_QUERIES: list[GoldenQuery] = [
    # ===== COMPONENT-EXACT (exact IC name match) =====
    GoldenQuery(
        id="comp-mcp73831",
        category="component-exact",
        description="Exact battery charger IC — common, should find all boards using it",
        component="MCP73831",
        must_include=["adafruit-esp32-s3-feather", "blues-notecarrier-b",
                       "esp32-c3-devkit-rust-1"],
        expected_total_range=(15, 25),
    ),
    GoldenQuery(
        id="comp-tmc2209",
        category="component-exact",
        description="Exact stepper driver IC",
        component="TMC2209",
        must_include=["silentstepstick-tmc2209", "prusa-buddy-board-mini",
                       "ldo-leviathan-v1-3", "corevus-g-v0-6"],
        expected_total_range=(3, 8),
    ),
    GoldenQuery(
        id="comp-max17048",
        category="component-exact",
        description="Exact fuel gauge IC",
        component="MAX17048",
        must_include=["micromod-asset-tracker", "healthypi-5"],
        expected_total_range=(3, 8),
    ),
    GoldenQuery(
        id="comp-acs712",
        category="component-exact",
        description="Exact current sensor IC",
        component="ACS712",
        must_include=["sparkfun-acs712-current-sensor"],
        expected_first="sparkfun-acs712-current-sensor",
        expected_total_range=(1, 5),
    ),
    GoldenQuery(
        id="comp-sx1276",
        category="component-exact",
        description="Exact LoRa transceiver IC",
        component="SX1276",
        must_include=["olimex-lora-868-915"],
        expected_total_range=(1, 5),
    ),
    GoldenQuery(
        id="comp-bq24295",
        category="component-exact",
        description="Exact battery charger IC — specific part",
        component="BQ24295",
        must_include=["soldered-bq24295-charger"],
        expected_first="soldered-bq24295-charger",
        expected_total_range=(1, 5),
    ),
    GoldenQuery(
        id="comp-wm8960",
        category="component-exact",
        description="Exact audio codec IC",
        component="WM8960",
        must_include=["sparkfun-audio-codec-wm8960"],
        expected_first="sparkfun-audio-codec-wm8960",
        expected_total_range=(1, 3),
    ),

    # ===== COMPONENT-PARTIAL (substring IC match) =====
    GoldenQuery(
        id="comp-stm32",
        category="component-partial",
        description="Broad MCU family — should match many STM32 variants",
        component="STM32",
        must_include=["px4-fmuv2-pixhawk", "prusa-buddy-board-mini",
                       "axiom-motor-controller", "stmbl"],
        expected_total_range=(25, 45),
    ),
    GoldenQuery(
        id="comp-rp2040",
        category="component-partial",
        description="Popular MCU — many boards use it",
        component="RP2040",
        limit=20,
        must_include=["corne-v4", "picocnc-v1-55", "adafruit-rp2040-can-bus",
                       "adafruit-rp2040-thinkink"],
        expected_total_range=(15, 25),
    ),
    GoldenQuery(
        id="comp-esp32-s3",
        category="component-partial",
        description="ESP32-S3 variant — subset of ESP32 family",
        component="ESP32-S3",
        must_include=["adafruit-esp32-s3-feather", "epdiy-v7",
                       "esphome-indoor-multi-sensor"],
        expected_total_range=(3, 10),
    ),
    GoldenQuery(
        id="comp-nrf52840",
        category="component-partial",
        description="Nordic BLE SoC",
        component="nRF52840",
        must_include=["particle-xenon", "feather-nrf52840-sense",
                       "particle-tracker-eval"],
        expected_total_range=(2, 8),
    ),
    GoldenQuery(
        id="comp-ecp5",
        category="component-partial",
        description="Lattice ECP5 FPGA family",
        component="ECP5",
        must_include=["orangecrab", "ulx3s"],
        expected_total_range=(2, 6),
    ),

    # ===== TEXT-IC (FTS search for IC names) =====
    GoldenQuery(
        id="text-rp2040",
        category="text-ic",
        description="FTS search for IC name — should find boards mentioning RP2040",
        query="RP2040",
        must_include=["adafruit-rp2040-can-bus", "adafruit-rp2040-thinkink",
                       "adafruit-rp2040-usb-host"],
        expected_total_range=(15, 30),
    ),
    GoldenQuery(
        id="text-esp32",
        category="text-ic",
        description="FTS search for ESP32 — broad MCU family",
        query="ESP32",
        must_include=["adafruit-esp32-c6-feather", "adafruit-esp32-s3-feather"],
        expected_total_range=(15, 40),
    ),
    GoldenQuery(
        id="text-stm32f405",
        category="text-ic",
        description="Specific STM32 variant in text search",
        query="STM32F405",
        must_include=["axiom-motor-controller", "vesc-4-12"],
        expected_total_range=(3, 10),
    ),

    # ===== TEXT-FUNCTIONAL (conceptual/descriptive queries) =====
    GoldenQuery(
        id="text-motor-driver",
        category="text-functional",
        description="Functional query — should find motor driver boards, not inverters",
        query="motor driver",
        must_include=["sparkfun-motor-driver-tb6612fng", "openmd-gan-motor-driver",
                       "odri-micro-driver-v2"],
        must_exclude=["tpa3116-stereo-sub-amp"],
        expected_first="sparkfun-motor-driver-tb6612fng",
        expected_total_range=(15, 30),
    ),
    GoldenQuery(
        id="text-battery-charger",
        category="text-functional",
        description="Functional query — battery charging circuits",
        query="battery charger",
        must_include=["soldered-bq24295-charger", "adafruit-powerboost-1000c",
                       "solarmeshtasticnode"],
        expected_first="soldered-bq24295-charger",
        expected_total_range=(8, 20),
    ),
    GoldenQuery(
        id="text-power-supply",
        category="text-functional",
        description="Broad functional query — power-supply tagged boards should rank high",
        query="power supply",
        must_include=["adafruit-powerboost-1000c", "eez-h24005", "smps-19v-3a"],
        # espresence is a presence sensor that mentions "power supply" peripherally
        must_exclude=["espresence"],
        expected_total_range=(30, 60),
    ),
    GoldenQuery(
        id="text-current-sensor",
        category="text-functional",
        description="Functional query — current sensing boards",
        query="current sensor",
        must_include=["sparkfun-acs712-current-sensor", "s3xy-bms-tesla-retrofit"],
        expected_first="sparkfun-acs712-current-sensor",
        expected_total_range=(5, 15),
    ),
    GoldenQuery(
        id="text-flight-controller",
        category="text-functional",
        description="Functional query — drone flight controllers",
        query="flight controller",
        must_include=["tinyfish", "hadesfcs", "asac-fc-rev-b", "atmosfc"],
        must_exclude=["sparkfun-acs712-current-sensor"],
        expected_total_range=(2, 10),
    ),
    GoldenQuery(
        id="text-audio-amplifier",
        category="text-functional",
        description="Functional query — audio amplification boards",
        query="audio amplifier",
        must_include=["adafruit-max98357-i2s-amp", "tpa3116-stereo-sub-amp",
                       "tpa3255-pbtl-class-d-amp"],
        must_exclude=["silentstepstick-tmc2209"],
        expected_total_range=(5, 15),
    ),
    GoldenQuery(
        id="text-led-driver",
        category="text-functional",
        description="Functional query — LED driver circuits, led-driver tagged boards rank high",
        query="led driver",
        must_include=["adafruit-tps61169-cc-boost-led-driver", "cc-led-driver-lm3424",
                       "sparkfun-femtobuck"],
        expected_first="adafruit-tps61169-cc-boost-led-driver",
        expected_total_range=(10, 25),
    ),
    GoldenQuery(
        id="text-thermocouple",
        category="text-functional",
        description="Specific sensor type — thermocouple interfaces",
        query="thermocouple",
        must_include=["adafruit-max31856-thermocouple",
                       "unexpected-maker-reflowmaster"],
        expected_first="adafruit-max31856-thermocouple",
        expected_total_range=(2, 6),
    ),
    GoldenQuery(
        id="text-can-bus",
        category="text-functional",
        description="CAN bus text search — dedicated CAN boards should rank first",
        query="CAN bus",
        must_include=["adafruit-rp2040-can-bus", "candlelight-usb-can"],
        expected_first="adafruit-rp2040-can-bus",
        expected_total_range=(12, 25),
    ),
    GoldenQuery(
        id="text-stepper",
        category="text-functional",
        description="Stepper motor/driver search",
        query="stepper driver",
        must_include=["silentstepstick-tmc2209", "soldered-drv8825-stepper"],
        expected_total_range=(3, 15),
    ),

    # ===== TEXT-ALIAS (queries that need alias expansion) =====
    GoldenQuery(
        id="text-bluetooth",
        category="text-alias",
        description="Alias: bluetooth → BLE",
        query="bluetooth",
        must_include=["particle-xenon", "feather-nrf52840-sense"],
        expected_total_range=(3, 12),
    ),
    GoldenQuery(
        id="text-eink",
        category="text-alias",
        description="Alias: eink → e-ink, synonym group with e-paper/EPD",
        query="eink",
        must_include=["epdiy-v7", "soldered-inkplate-10"],
        expected_total_range=(2, 8),
    ),
    GoldenQuery(
        id="text-epaper",
        category="text-alias",
        description="Alias: epaper → e-paper (synonym group with e-ink)",
        query="epaper",
        must_include=["epdiy-v7"],
        expected_total_range=(2, 8),
    ),
    GoldenQuery(
        id="text-neopixel",
        category="text-alias",
        description="Alias: neopixel → WS2812",
        query="neopixel",
        expected_total_range=(1, 10),
    ),
    GoldenQuery(
        id="text-lipo",
        category="text-alias",
        description="Alias: lipo → battery",
        query="lipo",
        expected_total_range=(5, 40),
    ),
    GoldenQuery(
        id="text-brushless",
        category="text-alias",
        description="Alias: brushless → BLDC",
        query="brushless",
        must_include=["sparkfun-iot-bldc-motor"],
        expected_total_range=(1, 15),
    ),

    # ===== TAG-FILTER (exact tag matching) =====
    GoldenQuery(
        id="tag-motor-control",
        category="tag-filter",
        description="Tag filter — motor control boards",
        tag="motor-control",
        must_include=["prusa-buddy-board-mini", "ldo-leviathan-v1-3",
                       "silentstepstick-tmc2209", "vesc-4-12"],
        limit=25,
        expected_total_range=(25, 35),
    ),
    GoldenQuery(
        id="tag-sensors",
        category="tag-filter",
        description="Tag filter — sensor boards",
        tag="sensors",
        limit=20,
        must_include=["esphome-indoor-multi-sensor", "px4-fmuv2-pixhawk",
                       "healthypi-5"],
        expected_total_range=(40, 55),
    ),
    GoldenQuery(
        id="tag-drone-uav",
        category="tag-filter",
        description="Tag filter — drone/UAV boards",
        tag="drone-uav",
        limit=15,
        must_include=["px4-fmuv2-pixhawk", "crazyflie", "tinyfish", "hadesfcs"],
        expected_total_range=(10, 18),
    ),
    GoldenQuery(
        id="tag-lora",
        category="tag-filter",
        description="Tag filter — LoRa boards",
        tag="lora",
        must_include=["olimex-lora-868-915", "adafruit-rfm95w-lora-breakout"],
        limit=15,
        expected_total_range=(8, 15),
    ),
    GoldenQuery(
        id="tag-fpga",
        category="tag-filter",
        description="Tag filter — FPGA boards",
        tag="fpga",
        must_include=["orangecrab", "ulx3s", "icebreaker"],
        expected_total_range=(7, 14),
    ),
    GoldenQuery(
        id="tag-battery-charging",
        category="tag-filter",
        description="Tag filter — battery charging boards",
        tag="battery-charging",
        must_include=["adafruit-powerboost-1000c", "soldered-bq24295-charger"],
        limit=20,
        expected_total_range=(14, 22),
    ),

    # ===== ORG-FILTER (organization matching) =====
    GoldenQuery(
        id="org-adafruit",
        category="org-filter",
        description="Org filter — Adafruit boards",
        org="adafruit",
        must_include=["adafruit-rp2040-can-bus", "adafruit-esp32-s3-feather"],
        expected_total_range=(24, 32),
    ),
    GoldenQuery(
        id="org-sparkfun",
        category="org-filter",
        description="Org filter — SparkFun boards",
        org="sparkfun",
        limit=15,
        must_include=["sparkfun-gps-rtk2", "sparkfun-openlog-artemis"],
        expected_total_range=(24, 32),
    ),
    GoldenQuery(
        id="org-olimex",
        category="org-filter",
        description="Org filter — Olimex boards (case-insensitive)",
        org="Olimex",
        limit=15,
        must_include=["olimex-lora-868-915"],
        expected_total_range=(12, 18),
    ),

    # ===== COMBINED (multiple filters) =====
    GoldenQuery(
        id="combined-wifi-sensors",
        category="combined",
        description="Combined: query=wifi + tag=sensors",
        query="wifi",
        tag="sensors",
        must_include=["seeed-wio-terminal"],
        expected_total_range=(1, 8),
    ),
    GoldenQuery(
        id="combined-adafruit-2layer",
        category="combined",
        description="Combined: org=adafruit + layers=2 (all Adafruit boards are 2-layer)",
        org="adafruit",
        layers=2,
        expected_total_range=(24, 32),
    ),
    GoldenQuery(
        id="combined-motor-stm32",
        category="combined",
        description="Combined: tag=motor-control + component=STM32",
        tag="motor-control",
        component="STM32",
        must_include=["prusa-buddy-board-mini", "heev-motor-controller-2018"],
        expected_total_range=(3, 15),
    ),
    GoldenQuery(
        id="combined-battery-esp32",
        category="combined",
        description="Combined: query=battery + component=ESP32",
        query="battery",
        component="ESP32",
        expected_total_range=(1, 10),
    ),
    GoldenQuery(
        id="combined-drone-sensors",
        category="combined",
        description="Combined: tag=drone-uav + tag=sensors (AND logic)",
        tag=["drone-uav", "sensors"],
        must_include=["px4-fmuv2-pixhawk", "hadesfcs"],
        expected_total_range=(3, 10),
    ),

    # ===== LAYERS FILTER =====
    GoldenQuery(
        id="layers-4",
        category="layers-filter",
        description="4-layer boards — many complex designs",
        layers=4,
        expected_total_range=(80, 100),
    ),

    # ===== NEGATIVE / EDGE CASES =====
    GoldenQuery(
        id="neg-nonexistent-ic",
        category="negative",
        description="Nonexistent IC — should return 0 results",
        component="ZZZZNOTREAL42",
        expected_total_range=(0, 0),
    ),
    GoldenQuery(
        id="neg-nonexistent-tag",
        category="negative",
        description="Nonexistent tag — should return 0 results",
        tag="does-not-exist-xyz",
        expected_total_range=(0, 0),
    ),
    GoldenQuery(
        id="neg-empty-query",
        category="negative",
        description="All-stopword query — should degrade gracefully",
        query="the and or",
        expected_total_range=(0, 285),
    ),
    GoldenQuery(
        id="edge-short-query",
        category="negative",
        description="Very short query (2 chars) — should still work",
        query="IO",
        expected_total_range=(0, 50),
    ),

    # ===== USER SCENARIOS (what a person building a board would actually search) =====
    GoldenQuery(
        id="scenario-battery-esp32-iot",
        category="user-scenario",
        description="Building battery-powered ESP32 IoT sensor — LiPo charging + ESP32",
        component="ESP32",
        tag="battery-charging",
        must_include=["adafruit-esp32-s3-feather", "olimex-esp32-s2-devkit-lipo",
                       "esp32-c3-devkit-rust-1"],
        expected_total_range=(3, 12),
    ),
    GoldenQuery(
        id="scenario-solar-harvesting",
        category="user-scenario",
        description="Solar-powered outdoor node — MPPT charging for small solar panels",
        query="solar",
        tag="energy-harvesting",
        must_include=["solarmeshtasticnode", "soldered-mppt-cn3791",
                       "libresolar-mppt-2420-lc"],
        expected_total_range=(3, 10),
    ),
    GoldenQuery(
        id="scenario-usb-c-pd-sink",
        category="user-scenario",
        description="Adding USB-C PD sink to project — PD controller reference designs",
        tag="usb-pd",
        must_include=["antmicro-usb-c-pd-adapter", "anavi-fixed-power-delivery"],
        limit=15,
        expected_total_range=(7, 14),
    ),
    GoldenQuery(
        id="scenario-bldc-foc-motor",
        category="user-scenario",
        description="BLDC motor controller with FOC — gate driver and current sense",
        query="FOC",
        tag="motor-control",
        must_include=["moteus-c1"],
        expected_total_range=(1, 10),
    ),
    GoldenQuery(
        id="scenario-env-sensor-node",
        category="user-scenario",
        description="Indoor air quality monitor — multiple I2C environmental sensors",
        component="SHT",
        tag="sensors",
        must_include=["esphome-indoor-multi-sensor"],
        expected_total_range=(1, 8),
    ),
    GoldenQuery(
        id="scenario-lora-gateway",
        category="user-scenario",
        description="LoRa gateway for mesh network — RF frontend reference",
        tag="lora",
        must_include=["olimex-lora-868-915", "adafruit-rfm95w-lora-breakout",
                       "solarmeshtasticnode"],
        limit=15,
        expected_total_range=(9, 15),
    ),
    GoldenQuery(
        id="scenario-can-bus-robot",
        category="user-scenario",
        description="Adding CAN bus to robot controller — transceiver and termination",
        tag=["can-bus", "motor-control"],
        must_include=["moteus-c1", "vesc-4-12"],
        limit=15,
        expected_total_range=(3, 15),
    ),
    GoldenQuery(
        id="scenario-gps-tracker",
        category="user-scenario",
        description="GPS asset tracker — GNSS receiver and antenna reference designs",
        tag="gps-gnss",
        must_include=["sparkfun-gps-rtk2", "artemis-global-tracker"],
        limit=15,
        expected_total_range=(10, 16),
    ),
    GoldenQuery(
        id="scenario-led-driver-lighting",
        category="user-scenario",
        description="Constant-current LED driver for lighting — boost/buck LED driver",
        tag="led-driver",
        must_include=["adafruit-tps61169-cc-boost-led-driver", "sparkfun-femtobuck",
                       "cc-led-driver-lm3424"],
        limit=15,
        expected_total_range=(12, 18),
    ),
    GoldenQuery(
        id="scenario-eink-display",
        category="user-scenario",
        description="E-paper display — EPD driver and bias voltage generation",
        query="e-ink",
        must_include=["epdiy-v7", "soldered-inkplate-10"],
        expected_total_range=(2, 8),
    ),
    GoldenQuery(
        id="scenario-fpga-ecp5-dev",
        category="user-scenario",
        description="FPGA dev board with ECP5 — DDR and power sequencing",
        component="ECP5",
        tag="fpga",
        must_include=["orangecrab", "ulx3s"],
        expected_total_range=(2, 6),
    ),
    GoldenQuery(
        id="scenario-3d-printer-controller",
        category="user-scenario",
        description="3D printer mainboard — TMC stepper drivers and heater MOSFETs",
        component="TMC",
        tag="3d-printer",
        must_include=["prusa-buddy-board-mini", "ldo-leviathan-v1-3",
                       "corevus-g-v0-6"],
        expected_total_range=(3, 10),
    ),
    GoldenQuery(
        id="scenario-buck-converter-psu",
        category="user-scenario",
        description="Buck converter for sensor board — real OSHW reference designs",
        query="buck",
        tag="power-supply",
        must_include=["sparkfun-femtobuck"],
        expected_total_range=(3, 15),
    ),
    GoldenQuery(
        id="scenario-rs485-industrial",
        category="user-scenario",
        description="Industrial sensor node — isolated RS-485 for Modbus",
        tag=["rs485", "isolation"],
        must_include=["halpi2-rs-485", "piaa-industrial-i-o"],
        expected_total_range=(2, 8),
    ),
    GoldenQuery(
        id="scenario-lora-weather-station",
        category="user-scenario",
        description="Outdoor LoRa weather station with environmental sensors",
        tag=["lora", "sensors"],
        must_include=["weather-station"],
        expected_total_range=(1, 5),
    ),
    GoldenQuery(
        id="scenario-bluetooth-speaker",
        category="user-scenario",
        description="Portable Bluetooth speaker — I2S DAC + Class D amplifier",
        query="speaker",
        tag="audio",
        must_include=["tpa3116-stereo-sub-amp", "esp32-bluetooth-speaker"],
        expected_total_range=(1, 12),
    ),

    # --- Hobbyist / maker scenarios ---
    GoldenQuery(
        id="scenario-smart-relay-esp32",
        category="user-scenario",
        description="Smart home relay board with ESP32 WiFi control",
        query="relay",
        component="ESP32",
        must_include=["esp32-4-channel-relays"],
        expected_first="esp32-4-channel-relays",
        expected_total_range=(1, 6),
    ),
    GoldenQuery(
        id="scenario-keyboard-pcb",
        category="user-scenario",
        description="Split ergonomic keyboard PCB — key matrix and USB",
        tag="keyboard",
        must_include=["corne-v4", "ferris-0-2"],
        must_exclude=["vesc-4-12"],
        expected_total_range=(3, 8),
    ),
    GoldenQuery(
        id="scenario-eurorack-synth",
        category="user-scenario",
        description="Eurorack synthesizer module — audio DAC and op-amp circuits",
        tag="eurorack",
        must_include=["mutable-plaits"],
        must_exclude=["prusa-buddy-board-mini"],
        expected_total_range=(3, 6),
    ),
    GoldenQuery(
        id="scenario-nfc-reader",
        category="user-scenario",
        description="NFC reader/writer for access control project",
        tag="nfc-rfid",
        must_include=["adafruit-st25dv16-nfc-eeprom", "nfc-copy-cat"],
        expected_total_range=(3, 8),
    ),
    GoldenQuery(
        id="scenario-reflow-oven",
        category="user-scenario",
        description="DIY reflow oven controller with thermocouple",
        query="reflow",
        must_include=["unexpected-maker-reflowmaster"],
        expected_first="unexpected-maker-reflowmaster",
        expected_total_range=(1, 4),
    ),

    # --- Professional / industrial scenarios ---
    GoldenQuery(
        id="scenario-drone-fc-stm32",
        category="user-scenario",
        description="Drone flight controller with STM32 — IMU and motor outputs",
        tag="drone-uav",
        component="STM32",
        must_include=["px4-fmuv2-pixhawk", "hadesfcs"],
        expected_total_range=(5, 15),
    ),
    GoldenQuery(
        id="scenario-bms-pack",
        category="user-scenario",
        description="Battery management system for lithium pack — cell balancing",
        tag="battery-management",
        must_include=["s3xy-bms-tesla-retrofit", "ennoid-bms",
                       "bms-15s80-sc"],
        expected_total_range=(5, 12),
    ),
    GoldenQuery(
        id="scenario-radar-presence",
        category="user-scenario",
        description="Radar-based presence detection sensor module",
        query="radar",
        must_include=["rp2040-radar-presence", "6-ghz-fmcw-radar"],
        expected_first="rp2040-radar-presence",
        expected_total_range=(5, 15),
    ),
    GoldenQuery(
        id="scenario-isolated-dcdc",
        category="user-scenario",
        description="Isolated DC-DC converter for industrial power supply",
        tag=["isolation", "power-supply"],
        must_include=["dcdc-llc-500w-isolated"],
        limit=15,
        expected_total_range=(5, 15),
    ),
    GoldenQuery(
        id="scenario-ethernet-gateway",
        category="user-scenario",
        description="Ethernet-connected IoT gateway board",
        tag="ethernet",
        must_include=["antmicro-cm4-baseboard"],
        limit=15,
        expected_total_range=(10, 18),
    ),
    GoldenQuery(
        id="scenario-ecg-biomedical",
        category="user-scenario",
        description="ECG frontend for biomedical heart monitoring",
        query="ECG",
        must_include=["card-io-ecg-frontend", "hackeeg-ads1299-shield"],
        expected_first="card-io-ecg-frontend",
        expected_total_range=(3, 10),
    ),
    GoldenQuery(
        id="scenario-current-sense-motor",
        category="user-scenario",
        description="Motor controller with inline current sensing",
        tag=["current-sensing", "motor-control"],
        must_include=["sparkfun-iot-bldc-motor"],
        expected_total_range=(1, 6),
    ),

    # --- Specific IC lookup scenarios ---
    GoldenQuery(
        id="scenario-w25q-flash",
        category="user-scenario",
        description="Adding W25Q SPI flash to a board — see how others wire it",
        component="W25Q",
        must_include=["hackrf-one", "prusa-buddy-board-mini"],
        limit=15,
        expected_total_range=(15, 30),
    ),
    GoldenQuery(
        id="scenario-ch340-usb-serial",
        category="user-scenario",
        description="CH340 USB-to-serial for programming interface",
        component="CH340",
        must_include=["olimex-esp32-gateway", "artemis-global-tracker"],
        limit=15,
        expected_total_range=(10, 22),
    ),
    GoldenQuery(
        id="scenario-battery-fuel-gauge",
        category="user-scenario",
        description="Battery fuel gauge for remaining capacity indication",
        query="fuel gauge",
        must_include=["soldered-bq27441-fuel-gauge"],
        expected_first="soldered-bq27441-fuel-gauge",
        expected_total_range=(2, 8),
    ),

    # --- Functional design queries ---
    GoldenQuery(
        id="scenario-boost-converter",
        category="user-scenario",
        description="Boost converter for powering 5V from single LiPo cell",
        query="boost",
        tag="power-supply",
        must_include=["adafruit-powerboost-1000c"],
        expected_total_range=(8, 20),
    ),
    GoldenQuery(
        id="scenario-i2s-audio",
        category="user-scenario",
        description="I2S audio output — DAC and amplifier wiring",
        query="I2S",
        tag="audio",
        must_include=["adafruit-max98357-i2s-amp"],
        expected_first="adafruit-max98357-i2s-amp",
        expected_total_range=(2, 8),
    ),
    GoldenQuery(
        id="scenario-zigbee-coordinator",
        category="user-scenario",
        description="Zigbee/Thread coordinator for smart home mesh",
        tag="zigbee-thread",
        must_include=["olimex-esp32-c6-evb", "catsniffer"],
        expected_total_range=(3, 8),
    ),
    GoldenQuery(
        id="scenario-sub-ghz-radio",
        category="user-scenario",
        description="Sub-GHz radio for long-range low-power IoT link",
        tag="sub-ghz",
        must_include=["catsniffer", "yardstick-one"],
        expected_total_range=(3, 8),
    ),
    GoldenQuery(
        id="scenario-data-logger",
        category="user-scenario",
        description="Data logger with SD card storage and GPS",
        tag="data-logging",
        must_include=["sparkfun-openlog-artemis"],
        expected_total_range=(2, 6),
    ),

    # --- Display / UI scenarios ---
    GoldenQuery(
        id="scenario-oled-display",
        category="user-scenario",
        description="Adding an OLED display to a project — SSD1306 I2C wiring",
        query="OLED",
        must_include=["adafruit-ssd1306-128x32-oled"],
        expected_first="adafruit-ssd1306-128x32-oled",
        expected_total_range=(10, 22),
    ),
    GoldenQuery(
        id="scenario-lvds-panel",
        category="user-scenario",
        description="LVDS panel interface for embedded display — DSI to LVDS",
        query="LVDS",
        must_include=["cm4-dsi-to-lvds-adapter"],
        expected_total_range=(1, 6),
    ),

    # --- Level shifting / interface ---
    GoldenQuery(
        id="scenario-level-shifter",
        category="user-scenario",
        description="3.3V to 5V level shifting for mixed-voltage design",
        tag="level-shifting",
        limit=15,
        expected_total_range=(12, 18),
    ),
    GoldenQuery(
        id="scenario-rs232-serial",
        category="user-scenario",
        description="RS-232 serial interface for legacy equipment",
        tag="rs232",
        must_include=["sparkfun-max3232-rs-232"],
        expected_total_range=(2, 6),
    ),

    # --- Power stage / inverter ---
    GoldenQuery(
        id="scenario-gate-driver-inverter",
        category="user-scenario",
        description="Half-bridge gate driver for motor inverter or power stage",
        query="gate driver",
        tag="inverter",
        must_include=["openinverter-gate-driver", "moteus-c1"],
        expected_first="openinverter-gate-driver",
        expected_total_range=(5, 15),
    ),
    GoldenQuery(
        id="scenario-vesc-esc",
        category="user-scenario",
        description="Open-source ESC — VESC motor controller reference designs",
        query="VESC",
        must_include=["vesc-4-12", "cheap-focer-2"],
        expected_first="vesc-4-12",
        expected_total_range=(2, 8),
    ),

    # --- USB ---
    GoldenQuery(
        id="scenario-usb-hub",
        category="user-scenario",
        description="USB hub controller for multi-port device",
        query="USB hub",
        must_include=["mte-usb-hub"],
        expected_first="mte-usb-hub",
        expected_total_range=(5, 15),
    ),

    # --- ADC / measurement ---
    GoldenQuery(
        id="scenario-adc-sensor-measurement",
        category="user-scenario",
        description="ADC for precision sensor measurement — voltage/current/temp",
        tag=["adc-dac", "sensors"],
        must_include=["crazyflie"],
        expected_total_range=(3, 10),
    ),
    GoldenQuery(
        id="scenario-energy-meter",
        category="user-scenario",
        description="CT clamp energy meter for home power monitoring",
        query="energy meter",
        must_include=["circuitsetup-6-channel-energy-meter", "emontx-v4"],
        expected_first="circuitsetup-6-channel-energy-meter",
        expected_total_range=(1, 5),
    ),

    # --- Relay / switching ---
    GoldenQuery(
        id="scenario-relay-switching",
        category="user-scenario",
        description="Relay driver board for switching AC loads — home automation",
        tag="relay",
        must_include=["esp32-4-channel-relays"],
        expected_total_range=(5, 10),
    ),

    # --- Robotics ---
    GoldenQuery(
        id="scenario-robotics-platform",
        category="user-scenario",
        description="Robotics motor controller platform — CAN + motor drivers",
        tag=["robotics", "motor-control"],
        must_include=["twisted-fields-rp2040-base", "moteus-c1"],
        expected_total_range=(2, 8),
    ),

    # --- WiFi ---
    GoldenQuery(
        id="scenario-wifi-esp32-gateway",
        category="user-scenario",
        description="ESP32 WiFi-connected gateway or IoT controller",
        component="ESP32",
        tag="wifi",
        must_include=["olimex-esp32-c6-evb"],
        expected_total_range=(1, 8),
    ),

    # ===== HOLDOUT QUERIES (never inspect during tuning) =====
    GoldenQuery(
        id="holdout-comp-ads1115",
        category="component-exact",
        description="Holdout: ADC IC",
        component="ADS1115",
        must_include=["adafruit-ads1115-adc", "esphome-indoor-multi-sensor"],
        holdout=True,
        expected_total_range=(2, 8),
    ),
    GoldenQuery(
        id="holdout-text-gps",
        category="text-functional",
        description="Holdout: GPS boards",
        query="GPS",
        must_include=["sparkfun-gps-rtk2", "adafruit-ultimate-gps"],
        holdout=True,
        expected_total_range=(8, 18),
    ),
    GoldenQuery(
        id="holdout-text-relay",
        category="text-functional",
        description="Holdout: relay boards",
        query="relay",
        must_include=["sparkfun-qwiic-relay", "esp32-4-channel-relays"],
        holdout=True,
        expected_total_range=(4, 12),
    ),
    GoldenQuery(
        id="holdout-text-lora",
        category="text-alias",
        description="Holdout: LoRa search (FTS)",
        query="lora",
        must_include=["olimex-lora-868-915", "adafruit-rfm95w-lora-breakout"],
        holdout=True,
        expected_total_range=(8, 18),
    ),
    GoldenQuery(
        id="holdout-tag-can-bus",
        category="tag-filter",
        description="Holdout: CAN bus tag",
        tag="can-bus",
        limit=20,
        must_include=["adafruit-rp2040-can-bus", "candlelight-usb-can"],
        holdout=True,
        expected_total_range=(12, 20),
    ),
    GoldenQuery(
        id="holdout-text-usb-pd",
        category="text-functional",
        description="Holdout: USB PD search",
        query="usb pd",
        must_include=["antmicro-usb-c-pd-adapter"],
        holdout=True,
        expected_total_range=(5, 15),
    ),
    GoldenQuery(
        id="holdout-text-fpga",
        category="text-ic",
        description="Holdout: FPGA text search",
        query="FPGA",
        must_include=["orangecrab", "icebreaker"],
        holdout=True,
        expected_total_range=(6, 14),
    ),
    GoldenQuery(
        id="holdout-org-soldered",
        category="org-filter",
        description="Holdout: Soldered Electronics org",
        org="Soldered Electronics",
        holdout=True,
        expected_total_range=(12, 20),
    ),
    GoldenQuery(
        id="holdout-scenario-stepper-cnc",
        category="user-scenario",
        description="Holdout: Stepper motor driver for CNC",
        query="stepper",
        tag="motor-control",
        must_include=["silentstepstick-tmc2209", "soldered-drv8825-stepper"],
        holdout=True,
        expected_total_range=(3, 20),
    ),
    GoldenQuery(
        id="holdout-scenario-gnss-rtk",
        category="user-scenario",
        description="Holdout: GNSS RTK rover — ZED-F9P integration",
        component="ZED-F9P",
        must_include=["sparkfun-gps-rtk2"],
        expected_first="sparkfun-gps-rtk2",
        holdout=True,
        expected_total_range=(1, 5),
    ),
    GoldenQuery(
        id="holdout-scenario-video-board",
        category="user-scenario",
        description="Holdout: Video processing/streaming board",
        tag="video",
        must_include=["antmicro-cm4-baseboard"],
        holdout=True,
        limit=15,
        expected_total_range=(8, 16),
    ),
    GoldenQuery(
        id="holdout-scenario-sdr-radio",
        category="user-scenario",
        description="Holdout: SDR ham radio transceiver",
        tag=["ham-radio", "rf-sdr"],
        must_include=["t41-sdr-main-board"],
        holdout=True,
        expected_total_range=(1, 5),
    ),
    GoldenQuery(
        id="holdout-scenario-atsamd21",
        category="user-scenario",
        description="Holdout: ATSAMD21 microcontroller board",
        component="ATSAMD21",
        must_include=["unexpected-maker-reflowmaster"],
        holdout=True,
        expected_total_range=(2, 8),
    ),
    GoldenQuery(
        id="holdout-scenario-signal-cond",
        category="user-scenario",
        description="Holdout: Signal conditioning / analog frontend",
        tag="signal-conditioning",
        holdout=True,
        limit=15,
        expected_total_range=(10, 18),
    ),
    GoldenQuery(
        id="holdout-scenario-esd-usb",
        category="user-scenario",
        description="Holdout: ESD protection on USB port",
        tag=["esd-protection", "usb"],
        must_include=["adafruit-rp2040-usb-host"],
        holdout=True,
        expected_total_range=(1, 4),
    ),
]


# ---------------------------------------------------------------------------
# Golden board_get queries — focus response correctness
# ---------------------------------------------------------------------------


@dataclass
class GoldenBoardGet:
    """A single annotated board_get query with expected focus results."""

    id: str
    description: str

    # board_get params
    slug: str
    focus: str

    # Assertions
    focus_found: bool = True  # Should focus match succeed?
    ic_value_contains: str | None = None  # Substring in matched IC value
    pins_present: list[str] = field(default_factory=list)  # Pin names that must exist
    has_decoupling: bool | None = None  # _decoupling section present?
    has_consensus: bool | None = None  # Consensus auto-included?
    min_consensus_boards: int | None = None  # Minimum board count in consensus
    no_junk_values: bool = True  # No bare R/C/L in pin component values


GOLDEN_BOARD_GETS: list[GoldenBoardGet] = [
    GoldenBoardGet(
        id="get-feather-mcp73831",
        description="MCP73831 battery charger on Feather — well-known IC with wide consensus",
        slug="adafruit-esp32-s3-feather",
        focus="MCP73831",
        ic_value_contains="MCP73831",
        pins_present=["PROG", "STAT"],
        has_consensus=True,
        min_consensus_boards=10,
    ),
    GoldenBoardGet(
        id="get-feather-esp32",
        description="Partial 'ESP32' match should resolve to ESP32-S3-MINI-1 with fallback consensus",
        slug="adafruit-esp32-s3-feather",
        focus="ESP32",
        ic_value_contains="ESP32-S3",
        has_decoupling=True,
        has_consensus=True,
        min_consensus_boards=10,
    ),
    GoldenBoardGet(
        id="get-prusa-tmc2209",
        description="TMC2209 stepper driver on Prusa Mini — decoupling + multi-board consensus",
        slug="prusa-buddy-board-mini",
        focus="TMC2209",
        ic_value_contains="TMC2209",
        has_decoupling=True,
        has_consensus=True,
        min_consensus_boards=2,
    ),
    GoldenBoardGet(
        id="get-ads1115",
        description="ADS1115 ADC — I2C address pin, SPI pins, decoupling",
        slug="adafruit-ads1115-adc",
        focus="ADS1115",
        ic_value_contains="ADS1115",
        pins_present=["ADDR", "SCL", "SDA"],
        has_decoupling=True,
    ),
    GoldenBoardGet(
        id="get-acs712",
        description="ACS712 current sensor — FILT pin has cap, VOUT has resistor",
        slug="sparkfun-acs712-current-sensor",
        focus="ACS712",
        ic_value_contains="ACS712",
        pins_present=["FILT", "VOUT"],
        has_decoupling=True,
    ),
    GoldenBoardGet(
        id="get-max31856",
        description="MAX31856 thermocouple — SPI + thermocouple input pins",
        slug="adafruit-max31856-thermocouple",
        focus="MAX31856",
        ic_value_contains="MAX31856",
        pins_present=["T+", "T-"],
        has_decoupling=True,
        has_consensus=False,
    ),
    GoldenBoardGet(
        id="get-vesc-stm32",
        description="Partial 'STM32' match on VESC board — should find STM32F40X",
        slug="vesc-4-12",
        focus="STM32",
        ic_value_contains="STM32F4",
        has_decoupling=True,
    ),
    GoldenBoardGet(
        id="get-rp2040-can",
        description="MCP25625 CAN controller on RP2040 CAN bus board — NOT MCP2515",
        slug="adafruit-rp2040-can-bus",
        focus="MCP25625",
        ic_value_contains="MCP25625",
        has_decoupling=True,
        has_consensus=True,
        min_consensus_boards=2,
    ),
    GoldenBoardGet(
        id="get-rp2040-can-bad",
        description="MCP2515 is NOT on this board — should fail with available_ics",
        slug="adafruit-rp2040-can-bus",
        focus="MCP2515",
        focus_found=False,
    ),
    GoldenBoardGet(
        id="get-feather-nonexistent",
        description="Nonexistent IC — should fail gracefully with available_ics list",
        slug="adafruit-esp32-s3-feather",
        focus="ZZZZNOTREAL",
        focus_found=False,
    ),
]
