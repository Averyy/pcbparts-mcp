"""Sensor scraper registry."""

from .arduino import scrape_arduino
from .atlas_scientific import scrape_atlas_scientific
from .benewake import scrape_benewake
from .bestmodules import scrape_bestmodules
from .circuitpython import scrape_circuitpython
from .dfrobot import scrape_dfrobot
from .esphome import scrape_esphome
from .hilink import scrape_hilink
from .maxbotix import scrape_maxbotix
from .micropython import scrape_micropython
from .sparkfun import scrape_sparkfun
from .tasmota import scrape_tasmota
from .winsen import scrape_winsen
from .zephyr import scrape_zephyr

# Registry: key -> (display_name, scrape_function)
# Each function takes (output_dir: Path) -> None
SCRAPERS = {
    "arduino": ("Arduino Library Index", scrape_arduino),
    "esphome": ("ESPHome Components", scrape_esphome),
    "circuitpython": ("CircuitPython Drivers", scrape_circuitpython),
    "micropython": ("MicroPython Libraries", scrape_micropython),
    "tasmota": ("Tasmota Peripherals", scrape_tasmota),
    "zephyr": ("Zephyr RTOS Sensors", scrape_zephyr),
    "maxbotix": ("Maxbotix Sensors", scrape_maxbotix),
    "benewake": ("Benewake LiDAR", scrape_benewake),
    "hilink": ("Hi-Link Radar", scrape_hilink),
    "atlas_scientific": ("Atlas Scientific", scrape_atlas_scientific),
    "winsen": ("Winsen Sensors", scrape_winsen),
    "bestmodules": ("Best Modules Corp (Holtek)", scrape_bestmodules),
    "sparkfun": ("SparkFun Sensors", scrape_sparkfun),
    "dfrobot": ("DFRobot Sensors", scrape_dfrobot),
}
