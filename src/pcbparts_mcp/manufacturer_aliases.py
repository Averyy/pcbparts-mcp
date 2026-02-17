"""Manufacturer aliases for JLCPCB component search.

Maps abbreviations and alternate names to the exact manufacturer names
used by the JLCPCB API. Keys are lowercase for case-insensitive lookup.

NOTE: Only include TRUE aliases here (abbreviations, alternate names).
Do NOT include entries where key == value.lower() (e.g., "molex": "MOLEX").
The client handles case-insensitive matching for exact names automatically
using KNOWN_MANUFACTURERS.
"""

# Top manufacturers on JLCPCB by part count (for case-insensitive matching)
# This enables "molex" -> "MOLEX", "kemet" -> "KEMET" without explicit aliases
KNOWN_MANUFACTURERS: set[str] = {
    # Passives (resistors, capacitors, inductors)
    "YAGEO", "Samsung Electro-Mechanics", "Murata Electronics", "TDK Corporation",
    "Panasonic", "Wurth Elektronik", "Bourns", "Littelfuse", "KEMET",
    "UNI-ROYAL(Uniroyal Elec)", "FH (Guangdong Fenghua Advanced Tech)",
    "FOJAN", "CCTC", "HRE", "HKR(Hong Kong Resistors)", "RALEC", "Sunlord",
    # Semiconductors
    "Texas Instruments", "STMicroelectronics", "NXP Semicon", "Microchip Tech",
    "Analog Devices", "Analog Devices Inc./Maxim Integrated", "onsemi",
    "Infineon Technologies", "Infineon/Cypress Semicon", "Renesas Electronics",
    "ROHM Semicon", "Vishay Intertech", "Diodes Incorporated", "Nexperia",
    "Broadcom Limited", "Torex Semicon", "TOSHIBA",
    # Chinese semiconductors
    "SGMICRO", "XLSEMI", "GOFORD", "3PEAK", "INJOINIC", "TECH PUBLIC",
    "UMW(Youtai Semiconductor Co., Ltd.)", "Wuxi NCE Power Semiconductor",
    "Wuxi Chipown Micro-electronics", "MICRONE(Nanjing Micro One Elec)",
    "Advanced Monolithic Systems", "HXY MOSFET", "Leiditech",
    # Transistors / MOSFETs
    "Alpha & Omega Semicon", "Guangdong Hottech", "TWGMC", "Shikues", "LRC",
    "hongjiacheng", "JSMSEMI", "MSKSEMI", "GOODWORK", "FOSAN", "YONGYUTAI",
    "MDD(Microdiode Semiconductor)", "Slkor(SLKORMICRO Elec.)",
    # MCUs
    "GigaDevice Semicon Beijing", "WCH(Jiangsu Qin Heng)", "ARTERY", "Geehy",
    "PUYA", "Nuvoton Tech", "PADAUK Tech", "FMD(Fremont Micro Devices)",
    "HK", "CW", "STC Micro", "Holtek Semicon", "Espressif Systems",
    "Nordic Semicon", "Silicon Labs", "Raspberry Pi",
    # LEDs / Optoelectronics
    "Everlight Elec", "OSRAM Opto Semicon", "Lite-On", "Sharp Microelectronics",
    "Worldsemi", "Foshan NationStar Optoelectronics", "XINGLIGHT", "Kingbright",
    "CREE LED", "TUOZHAN", "Yongyu Photoelectric", "Hubei KENTO Elec",
    # Connectors
    "JST", "MOLEX", "CJT(Changjiang Connectors)", "Korean Hroparts Elec",
    "HANRUN(Zhongshan HanRun Elec)", "SHOU HAN", "Amphenol ICC",
    "TE Connectivity", "XKB Connection", "Shenzhen Kinghelm Elec",
    "Ningbo Kangnex Elec", "BOOMELE(Boom Precision Elec)",
    # Crystals / Oscillators
    "YXC Crystal Oscillators", "Seiko", "TAITIEN Elec", "Hosonic Elec",
    # Memory
    "Winbond Elec", "Micron Tech", "ISSI(Integrated Silicon Solution)",
    "MXIC(Macronix)", "RAMXEED/FUJITSU",
    # Power / Motor drivers
    "Allegro MicroSystems, LLC", "Richtek Tech", "MaxLinear",
    # Relays
    "Omron Electronics", "HF(Xiamen Hongfa Electroacoustic)",
    "Ningbo Songle Relay", "Zhejiang HKE",
    # Sensors
    "Sensirion", "TDK InvenSense",
    # Battery Management
    "ShangHai Consonance Elec",
    # Circuit Protection / ESD
    "RUILON(Shenzhen Ruilongyuan Elec)", "Seaward Elec", "BORN", "Brightking",
    "DOWO", "Shandong Jingdao Microelectronics", "TECHFUSE",
    "Jinrui Electronic Materials Co.",
    # Other Chinese manufacturers
    "SXN(Shun Xiang Nuo Elec)", "Jiangsu Changjing Electronics Technology Co., Ltd.",
    "UTC(Unisonic Tech)", "BL(Shanghai Belling)", "OB(On-Bright Elec)",
    "HCTL", "Shanghai Prisemi Elec", "JRC", "ST(Semtech)", "Pulse Elec",
    "FUXINSEMI", "KUU", "LUTE", "Walter Elec", "Xucheng Elec",
}

# True aliases only - abbreviations and alternate names
# Case normalization for exact names is handled via KNOWN_MANUFACTURERS

MANUFACTURER_ALIASES: dict[str, str] = {
    # Major semiconductor companies
    "ti": "Texas Instruments",
    "texas": "Texas Instruments",
    "stm": "STMicroelectronics",
    "st": "STMicroelectronics",
    "stmicro": "STMicroelectronics",
    "nxp": "NXP Semicon",
    "nxp semiconductor": "NXP Semicon",
    "microchip": "Microchip Tech",
    "microchip technology": "Microchip Tech",
    "adi": "Analog Devices",
    "analog": "Analog Devices",
    "maxim": "Analog Devices Inc./Maxim Integrated",
    "maxim integrated": "Analog Devices Inc./Maxim Integrated",
    "on": "onsemi",
    "on semi": "onsemi",
    "on semiconductor": "onsemi",
    "infineon": "Infineon Technologies",
    "cypress": "Infineon/Cypress Semicon",
    "renesas": "Renesas Electronics",
    "rohm": "ROHM Semicon",
    "rohm semiconductor": "ROHM Semicon",
    "vishay": "Vishay Intertech",
    "vishay intertechnology": "Vishay Intertech",
    "diodes": "Diodes Incorporated",
    "diodes inc": "Diodes Incorporated",
    "broadcom": "Broadcom Limited",
    "torex": "Torex Semicon",
    # Chinese manufacturers (popular on JLCPCB)
    "fh": "FH (Guangdong Fenghua Advanced Tech)",
    "fenghua": "FH (Guangdong Fenghua Advanced Tech)",
    "guangdong fenghua advanced tech": "FH (Guangdong Fenghua Advanced Tech)",
    "sxn": "SXN(Shun Xiang Nuo Elec)",
    "shun xiang nuo elec": "SXN(Shun Xiang Nuo Elec)",
    "changjing": "Jiangsu Changjing Electronics Technology Co., Ltd.",
    "jscj": "Jiangsu Changjing Electronics Technology Co., Ltd.",
    "uniroyal": "UNI-ROYAL(Uniroyal Elec)",
    "uni-royal": "UNI-ROYAL(Uniroyal Elec)",
    "uniroyal elec": "UNI-ROYAL(Uniroyal Elec)",
    "mdd": "MDD(Microdiode Semiconductor)",
    "microdiode": "MDD(Microdiode Semiconductor)",
    "microdiode semiconductor": "MDD(Microdiode Semiconductor)",
    "boomele": "BOOMELE(Boom Precision Elec)",
    "boom precision elec": "BOOMELE(Boom Precision Elec)",
    "stc": "STC Micro",
    "kento": "Hubei KENTO Elec",
    "hxy": "HXY MOSFET",
    "slkor": "Slkor(SLKORMICRO Elec.)",
    "slkormicro": "Slkor(SLKORMICRO Elec.)",
    "slkormicro elec.": "Slkor(SLKORMICRO Elec.)",
    "utc": "UTC(Unisonic Tech)",
    "unisonic tech": "UTC(Unisonic Tech)",
    "holtek": "Holtek Semicon",
    # Chinese power/analog IC makers
    "umw": "UMW(Youtai Semiconductor Co., Ltd.)",
    "youtai": "UMW(Youtai Semiconductor Co., Ltd.)",
    "youtai semiconductor": "UMW(Youtai Semiconductor Co., Ltd.)",
    "youtai semiconductor co., ltd.": "UMW(Youtai Semiconductor Co., Ltd.)",
    "sg micro": "SGMICRO",
    "xl semiconductor": "XLSEMI",
    "nce": "Wuxi NCE Power Semiconductor",
    "nce power": "Wuxi NCE Power Semiconductor",
    "goford semiconductor": "GOFORD",
    "chipown": "Wuxi Chipown Micro-electronics",
    "threepeak": "3PEAK",
    "microne": "MICRONE(Nanjing Micro One Elec)",
    "micro one": "MICRONE(Nanjing Micro One Elec)",
    "nanjing micro one elec": "MICRONE(Nanjing Micro One Elec)",
    "ams": "Advanced Monolithic Systems",
    # Chinese transistor/MOSFET makers
    "aos": "Alpha & Omega Semicon",
    "alpha omega": "Alpha & Omega Semicon",
    "aosemi": "Alpha & Omega Semicon",
    "hottech": "Guangdong Hottech",
    "hjc": "hongjiacheng",
    "jsm": "JSMSEMI",
    "msk": "MSKSEMI",
    # Chinese MCU makers
    "gd": "GigaDevice Semicon Beijing",
    "gigadevice": "GigaDevice Semicon Beijing",
    "wch": "WCH(Jiangsu Qin Heng)",
    "qinheng": "WCH(Jiangsu Qin Heng)",
    "jiangsu qin heng": "WCH(Jiangsu Qin Heng)",
    "ch32": "WCH(Jiangsu Qin Heng)",
    "at32": "ARTERY",
    "apm": "Geehy",
    "apm32": "Geehy",
    "py32": "PUYA",
    "nuvoton": "Nuvoton Tech",
    "padauk": "PADAUK Tech",
    "fmd": "FMD(Fremont Micro Devices)",
    "fremont": "FMD(Fremont Micro Devices)",
    "fremont micro devices": "FMD(Fremont Micro Devices)",
    "hk32": "HK",
    "cw32": "CW",
    # Chinese passive/capacitor makers
    "hkr": "HKR(Hong Kong Resistors)",
    "hong kong resistors": "HKR(Hong Kong Resistors)",
    # Optoelectronics / LEDs
    "everlight": "Everlight Elec",
    "osram": "OSRAM Opto Semicon",
    "liteon": "Lite-On",
    "sharp": "Sharp Microelectronics",
    "ws": "Worldsemi",
    "ws2812": "Worldsemi",
    "nationstar": "Foshan NationStar Optoelectronics",
    "cree": "CREE LED",
    "yongyu": "Yongyu Photoelectric",
    # Connectors
    "kangnex": "Ningbo Kangnex Elec",
    "cjt": "CJT(Changjiang Connectors)",
    "changjiang": "CJT(Changjiang Connectors)",
    "changjiang connectors": "CJT(Changjiang Connectors)",
    "hroparts": "Korean Hroparts Elec",
    "korean hroparts": "Korean Hroparts Elec",
    "hanrun": "HANRUN(Zhongshan HanRun Elec)",
    "zhongshan hanrun elec": "HANRUN(Zhongshan HanRun Elec)",
    "shouhan": "SHOU HAN",
    "amphenol": "Amphenol ICC",
    "te": "TE Connectivity",
    "xkb": "XKB Connection",
    "kinghelm": "Shenzhen Kinghelm Elec",
    # Passives
    "samsung": "Samsung Electro-Mechanics",
    "murata": "Murata Electronics",
    "tdk": "TDK Corporation",
    "wurth": "Wurth Elektronik",
    "würth": "Wurth Elektronik",
    # Crystals / Oscillators
    "yxc": "YXC Crystal Oscillators",
    "yangxing": "YXC Crystal Oscillators",
    "seiko epson": "Seiko",
    "taitien": "TAITIEN Elec",
    "hosonic": "Hosonic Elec",
    # MCU/SoC
    "espressif": "Espressif Systems",
    "nordic": "Nordic Semicon",
    "nordic semiconductor": "Nordic Semicon",
    "silabs": "Silicon Labs",
    "rpi": "Raspberry Pi",
    # Memory
    "winbond": "Winbond Elec",
    "micron": "Micron Tech",
    "micron technology": "Micron Tech",
    "issi": "ISSI(Integrated Silicon Solution)",
    "integrated silicon solution": "ISSI(Integrated Silicon Solution)",
    "macronix": "MXIC(Macronix)",
    "mxic": "MXIC(Macronix)",
    "ramxeed": "RAMXEED/FUJITSU",
    "fujitsu": "RAMXEED/FUJITSU",
    # Motor drivers / Power
    "allegro": "Allegro MicroSystems, LLC",
    "allegro microsystems": "Allegro MicroSystems, LLC",
    "richtek": "Richtek Tech",
    # Relays
    "omron": "Omron Electronics",
    "hongfa": "HF(Xiamen Hongfa Electroacoustic)",
    "hf": "HF(Xiamen Hongfa Electroacoustic)",
    "xiamen hongfa electroacoustic": "HF(Xiamen Hongfa Electroacoustic)",
    "songle": "Ningbo Songle Relay",
    "hke": "Zhejiang HKE",
    # Sensors
    "invensense": "TDK InvenSense",
    # Chinese IC makers
    "belling": "BL(Shanghai Belling)",
    "shanghai belling": "BL(Shanghai Belling)",
    "bl": "BL(Shanghai Belling)",
    "on-bright": "OB(On-Bright Elec)",
    "onbright": "OB(On-Bright Elec)",
    "ob": "OB(On-Bright Elec)",
    "on-bright elec": "OB(On-Bright Elec)",
    "prisemi": "Shanghai Prisemi Elec",
    # Battery Management
    "consonance": "ShangHai Consonance Elec",
    "shanghai consonance": "ShangHai Consonance Elec",
    # Circuit Protection / ESD
    "ruilon": "RUILON(Shenzhen Ruilongyuan Elec)",
    "ruilongyuan": "RUILON(Shenzhen Ruilongyuan Elec)",
    "shenzhen ruilongyuan elec": "RUILON(Shenzhen Ruilongyuan Elec)",
    "seaward": "Seaward Elec",
    # Other
    "semtech": "ST(Semtech)",
    "pulse": "Pulse Elec",
}
