"""Alternative component finding with spec-aware compatibility checking.

This module provides intelligent alternative finding that:
1. Matches parts by primary spec value (not just subcategory)
2. Verifies compatibility using same_or_better rules
3. Scores and ranks alternatives by usefulness
4. Returns verified alternatives for supported categories, similar_parts for unsupported
"""

import re
from typing import Any, Callable

# Import shared parsers from the unified parsers module
from pcbparts_mcp.parsers import (
    RESISTANCE_MATCH_TOLERANCE,
    parse_voltage,
    parse_esp32_module_memory,
    parse_isolation_voltage,
    parse_tolerance,
    parse_ppm,
    parse_forward_voltage,
    parse_power,
    parse_current,
    parse_resistance,
    parse_capacitance,
    parse_inductance,
    parse_frequency,
    parse_decibels,
    parse_impedance_at_freq,
    parse_length_mm,
    impedance_at_freq_match,
)


# =============================================================================
# SPEC PARSERS MAPPING
# =============================================================================
# Map spec names to their parser functions. "special" means use custom logic.

SPEC_PARSERS: dict[str, Callable[[str], float | None] | str | None] = {
    # Voltages
    "Voltage Rating": parse_voltage,
    "Voltage - DC Reverse(Vr)": parse_voltage,
    "Drain to Source Voltage": parse_voltage,
    "Collector - Emitter Voltage VCEO": parse_voltage,
    "Reverse Stand-Off Voltage (Vrwm)": parse_voltage,
    "Clamping Voltage": parse_voltage,
    "Isolation Voltage(Vrms)": parse_isolation_voltage,
    "Voltage - Max": parse_voltage,
    "Output Voltage": parse_voltage,
    "Voltage Dropout": parse_voltage,
    "Zener Voltage(Nom)": parse_voltage,
    "Voltage Rating (DC)": parse_voltage,
    "Voltage Rating (Max)": parse_voltage,
    "Reverse Voltage": parse_voltage,
    "Voltage(AC)": parse_voltage,
    "Voltage Rating (AC)": parse_voltage,
    "Voltage Rating - DC": parse_voltage,
    "Coil Voltage": parse_voltage,
    "Switching Voltage(Max)": parse_voltage,
    "Load Voltage": parse_voltage,
    "Varistor Voltage": parse_voltage,
    "Peak off - state voltage(Vdrm)": parse_voltage,
    "Trigger Voltage": parse_voltage,
    "Rated Voltage (Max)": parse_voltage,
    "Collector-Emitter Breakdown Voltage (Vces)": parse_voltage,
    "Vce Saturation(VCE(sat))": parse_voltage,
    "Voltage - Forward(Vf@If)": parse_forward_voltage,
    "Voltage - DC Spark Over (Nom)": parse_voltage,
    "Voltage - Supply": parse_voltage,  # For buzzers, etc.
    "Voltage - Supply(VCCA)": parse_voltage,  # Level shifters: each side's range
    "Voltage - Supply(VCCB)": parse_voltage,
    "Gate Threshold Voltage (Vgs(th))": parse_voltage,  # MOSFETs: "4V", "4V@250uA"
    "Gate Threshold Voltage": parse_voltage,  # Alternate name
    # Tolerances (percentage-based)
    "Tolerance": parse_tolerance,
    "Frequency Stability": parse_ppm,  # ±20ppm format
    # Power
    "Power(Watts)": parse_power,
    "Pd - Power Dissipation": parse_power,
    "Peak Pulse Power Dissipation (Ppp)": parse_power,
    "Rated Power": parse_power,
    # Currents
    "Quiescent Current": parse_current,
    "Quiescent Current(Iq)": parse_current,
    "standby current": parse_current,
    "Supply Current (Iq)": parse_current,
    "Current - Continuous Drain(Id)": parse_current,
    "Current - Collector(Ic)": parse_current,
    "Current - Rectified": parse_current,
    "Current Rating": parse_current,
    "Current - Saturation(Isat)": parse_current,
    "Current - Saturation (Isat)": parse_current,  # Variant with space
    "Output Current": parse_current,
    "Hold Current": parse_current,
    "Trip Current": parse_current,
    "Contact Current": parse_current,
    "Contact Rating": parse_current,
    "Switching Current(Max)": parse_current,
    "Load Current": parse_current,
    "Current - Average Rectified": parse_current,
    "Drain Current (Idss)": parse_current,
    "Output Current(Max)": parse_current,
    "Impulse Discharge Current": parse_current,
    "Peak Pulse Current-Ipp (10/1000us)": parse_current,
    "Current Rating (Max)": parse_current,
    "Average Rectified Current": parse_current,
    "Output Current(It(rms))": parse_current,
    "Peak Current": parse_current,
    "Maximum Continuous Current": parse_current,  # Power distribution (high-side) switches
    # Resistance
    "DC Resistance(DCR)": parse_resistance,
    "RDS(on)": parse_resistance,
    "Resistance": parse_resistance,
    "Resistance @ 25℃": parse_resistance,
    "Resistance Value (Ohms)": parse_resistance,  # digital potentiometers
    "Cell Resistance @ Illuminance": parse_resistance,
    # Capacitance
    "Capacitance": parse_capacitance,
    "Load Capacitance": parse_capacitance,
    # Inductance
    "Inductance": parse_inductance,
    # Frequency
    "Frequency": parse_frequency,
    # Physical dimensions (aluminum electrolytics, discrete caps, etc.)
    "Height - Seated (Max)": parse_length_mm,
    "Height": parse_length_mm,
    "Diameter": parse_length_mm,
    "Length": parse_length_mm,
    "Width": parse_length_mm,
    # Special handling
    "Impedance @ Frequency": "special",  # Uses impedance_at_freq_match()
    # String-match specs (no parser - use exact match)
    "Temperature Coefficient": None,
    "Illumination Color": None,
    "type": None,
    "Type": None,
    "Output Type": None,
    "Peak Wavelength": None,
    "Wavelength": None,
    "FET Type": None,
    "Number": None,  # Transistors: "1 N-channel", "2 NPN" (read by the polarity check)
    "B Constant (25℃/100℃)": None,
    "Number of Contacts": None,
    "Reference Series": None,
    "The Chip Type": None,
    "Number of Positions": None,
    "Number of Pins": None,
    "Number of Positions or Pins": None,
    "Number of Rows": None,
    "Pitch": None,
    "Connector Type": None,
    "Gender": None,
    "Pins Structure": None,
    "Circuit": None,
    "Contact Form": None,
    "Mounting Type": None,
    "Self Lock / No Lock": None,
    "Positions": None,
    "Number of Poles Per Deck": None,
    "Rated Functioning Temperature": None,
    "Number of Resistors": None,
    "Number of Capacitors": None,
    "Number of Lines": None,
    "Number of Forward Channels": None,
    "Number of Reverse Channels": None,
    "Number of Poles": None,
    "Number of Turns": None,
    "Number of Coils": None,
    "Impedance": None,
    "Driver Circuitry": None,
    "Ratings": None,
    "Data Rate": None,
    "Data Rate(Max)": None,
    "Color": None,
    "Number of Segments": None,
    "Direction": None,
    "Encoder Type": None,
    "Energy": None,
    "Sound Pressure Level(SPL)": parse_decibels,
    # Battery Management
    "Type of Battery": None,
    "Number of Cells": None,
    "Charge Current - Max": parse_current,
    # Level Shifters
    "Channel Type": None,
    # TVS/ESD
    "Polarity": None,
    "Number of Channels": None,
    # Diodes: "1 Independent" = "Standalone"; "1 Pair Common Cathode"; normalized by _compare_values
    "Diode Configuration": None,
    # Coax connectors: "SMA", "IPEX"; "Inner hole" (jack) vs "Inner pin" (plug)
    "RF Series": None,
    "Interface": None,
    # Wireless modules: the chip ("ESP32-S3R8")
    "Utilized IC / Part": None,
    # Motor Drivers
    "Number of H-bridges": None,
    # Audio Amplifiers
    "Class": None,  # Class D, Class AB, etc.
    # Wireless Modules
    "Output Power": parse_power,
    "Output Power(Max)": parse_power,
}


# Dimension spec fields that can fall back to the package string when the spec value is null.
DIMENSION_SPEC_FIELDS: frozenset[str] = frozenset({
    "Height - Seated (Max)", "Height", "Diameter",
})

# Specs that use exact string matching (case-insensitive)
STRING_MATCH_SPECS = {
    "Temperature Coefficient",
    "Illumination Color",
    "type",
    "Type",
    "Output Type",
    "Peak Wavelength",
    "Wavelength",
    "FET Type",
    "Number",
    "B Constant (25℃/100℃)",
    # Connectors
    "Number of Contacts",
    "Reference Series",
    "The Chip Type",
    "Number of Positions",
    "Number of Pins",
    "Number of Positions or Pins",
    "Number of Rows",
    "Pitch",
    "Connector Type",
    "Gender",
    "Pins Structure",
    # Switches
    "Circuit",
    "Contact Form",
    "Mounting Type",
    "Self Lock / No Lock",
    "Positions",
    "Number of Poles Per Deck",
    # Fuses
    "Rated Functioning Temperature",
    # Arrays/Networks
    "Number of Resistors",
    "Number of Capacitors",
    "Number of Lines",
    "Number of Forward Channels",
    "Number of Reverse Channels",
    "Number of Poles",
    "Number of Turns",
    "Number of Coils",
    # Audio/RF
    "Impedance",
    "Driver Circuitry",
    # Capacitors
    "Ratings",  # X1, X2, Y1, Y2 safety class
    # Data rates (string format varies too much)
    "Data Rate",
    "Data Rate(Max)",
    # Opto/misc
    "Color",
    "Number of Segments",
    "Direction",
    "Encoder Type",
    # Battery Management
    "Type of Battery",
    "Number of Cells",
    # Level Shifters
    "Channel Type",
    # TVS/ESD
    "Polarity",
    "Number of Channels",
    "Diode Configuration",
    "RF Series",
    "Interface",
    "Utilized IC / Part",
    # Motor Drivers
    "Number of H-bridges",
    # Audio Amplifiers
    "Class",
}


# =============================================================================
# COMPATIBILITY RULES
# =============================================================================
# Defines what makes a part a valid alternative for each supported subcategory.
# - primary: The main spec to search by
# - must_match: Specs that must be exactly equal
# - same_or_better: Specs where candidate must be >= or <= original
# - polarity: Transistor specs that give N/P (or NPN/PNP) and how many: the candidate must state its
#   polarity and match the original's (see _polarity)

COMPATIBILITY_RULES: dict[str, dict[str, Any]] = {
    # ============== RESISTORS ==============
    "Chip Resistor - Surface Mount": {
        "primary": "Resistance",
        "same_or_better": {
            "Tolerance": "lower",  # ±1% can replace ±5%
            "Power(Watts)": "higher",  # 1/4W can replace 1/10W
        },
    },
    "Through Hole Resistors": {
        "primary": "Resistance",
        "same_or_better": {
            "Tolerance": "lower",
            "Power(Watts)": "higher",
        },
    },
    "Current Sense Resistors / Shunt Resistors": {
        "primary": "Resistance",
        "same_or_better": {
            "Tolerance": "lower",
            "Power(Watts)": "higher",
        },
    },
    "Resistor Networks, Arrays": {
        "primary": "Resistance",
        "must_match": ["Number of Resistors"],
        "same_or_better": {
            "Tolerance": "lower",
            "Power(Watts)": "higher",
        },
    },
    "Potentiometers, Variable Resistors": {
        "primary": "Resistance",
        "must_match": ["Number of Turns"],
        "same_or_better": {
            "Power(Watts)": "higher",
            "Tolerance": "lower",
        },
    },
    # ============== CAPACITORS ==============
    "Multilayer Ceramic Capacitors MLCC - SMD/SMT": {
        "primary": "Capacitance",
        "must_match": ["Temperature Coefficient"],  # X7R != X5R
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        },
    },
    "Multilayer Ceramic Capacitors MLCC - Leaded": {
        "primary": "Capacitance",
        "must_match": ["Temperature Coefficient"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        },
    },
    "Through Hole Ceramic Capacitors": {
        "primary": "Capacitance",
        "must_match": ["Temperature Coefficient"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        },
    },
    "Aluminum Electrolytic Capacitors - SMD": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
        },
    },
    "Aluminum Electrolytic Capacitors - Leaded": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
        },
    },
    "Aluminum Electrolytic Capacitors (Can - Screw Terminals)": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
        },
    },
    "Tantalum Capacitors": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        },
    },
    "Film Capacitors": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        },
    },
    "Polypropylene Film Capacitors (CBB)": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        },
    },
    "Polymer Aluminum Capacitors": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
        },
    },
    "Hybrid Aluminum Electrolytic Capacitors": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
        },
    },
    "Horn-Type Electrolytic Capacitors": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
        },
    },
    "Niobium Oxide Capacitors": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        },
    },
    "Mica and PTFE Capacitors": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        },
    },
    "Safety Capacitors": {
        "primary": "Capacitance",
        "must_match": ["Ratings"],  # X1, X2, Y1, Y2 class
        "same_or_better": {
            "Voltage(AC)": "higher",
            "Tolerance": "lower",
        },
    },
    "Capacitor Networks, Arrays": {
        "primary": "Capacitance",
        "must_match": ["Number of Capacitors"],
        "same_or_better": {
            "Voltage Rating": "higher",
        },
    },
    # ============== INDUCTORS ==============
    "Inductors (SMD)": {
        "primary": "Inductance",
        "same_or_better": {
            "Current Rating": "higher",
            "Current - Saturation (Isat)": "higher",
            "DC Resistance(DCR)": "lower",
        },
    },
    "Power Inductors": {
        "primary": "Inductance",
        "same_or_better": {
            "Current Rating": "higher",
            "Current - Saturation(Isat)": "higher",
            "DC Resistance(DCR)": "lower",
        },
    },
    "Color Ring Inductors / Through Hole Inductors": {
        "primary": "Inductance",
        "same_or_better": {
            "Current Rating": "higher",
            "DC Resistance(DCR)": "lower",
        },
    },
    "Wireless Charging Coils": {
        "primary": "Inductance",
        "must_match": ["Number of Coils"],
        "same_or_better": {
            "DC Resistance(DCR)": "lower",
        },
    },
    # ============== FERRITE BEADS ==============
    "Ferrite Beads": {
        "primary": "Impedance @ Frequency",
        "same_or_better": {
            "Current Rating": "higher",
            "DC Resistance(DCR)": "lower",
        },
    },
    "Common Mode Filters": {
        "primary": "Impedance @ Frequency",
        "must_match": ["Number of Lines"],
        "same_or_better": {
            "Current Rating": "higher",
            "Voltage Rating - DC": "higher",
        },
    },
    # ============== MOSFETs ==============
    "MOSFETs": {
        "primary": "Drain to Source Voltage",
        "polarity": ["Type", "Number"],  # N-channel can't replace P-channel; single can't replace dual
        "same_or_better": {
            "Drain to Source Voltage": "higher",
            "Current - Continuous Drain(Id)": "higher",
            "RDS(on)": "lower",
            "Gate Threshold Voltage (Vgs(th))": "lower",  # a 4V part won't switch on from a 3.3V GPIO
        },
    },
    "Silicon Carbide Field Effect Transistor (MOSFET)": {
        "primary": "Drain to Source Voltage",
        "polarity": ["Type", "Number"],
        "same_or_better": {
            "Drain to Source Voltage": "higher",
            "Current - Continuous Drain(Id)": "higher",
            "RDS(on)": "lower",
        },
    },
    # ============== JFETs ==============
    "JFETs": {
        "primary": "FET Type",
        "must_match": ["FET Type"],
        "polarity": ["FET Type", "Number"],
        "same_or_better": {
            "Drain Current (Idss)": "higher",
            "RDS(on)": "lower",
        },
    },
    # ============== BJTs ==============
    "Bipolar (BJT)": {
        "primary": "type",
        "must_match": ["type"],
        "polarity": ["type", "Number"],
        "same_or_better": {
            "Collector - Emitter Voltage VCEO": "higher",
            "Current - Collector(Ic)": "higher",
        },
    },
    "Darlington Transistors": {
        "primary": "Type",
        "must_match": ["Type"],
        "polarity": ["Type", "Number"],
        "same_or_better": {
            "Collector - Emitter Voltage VCEO": "higher",
            "Current - Collector(Ic)": "higher",
        },
    },
    "Digital Transistors": {
        "primary": "type",
        "must_match": ["type"],
        "polarity": ["type", "Number"],
        "same_or_better": {
            "Collector - Emitter Voltage VCEO": "higher",
        },
    },
    "Phototransistors": {
        "primary": "Peak Wavelength",
        "must_match": ["Peak Wavelength"],
        "same_or_better": {
            "Collector - Emitter Voltage VCEO": "higher",
            "Current - Collector(Ic)": "higher",
        },
    },
    # ============== IGBTs ==============
    "IGBT Transistors / Modules": {
        "primary": "Collector-Emitter Breakdown Voltage (Vces)",
        "same_or_better": {
            "Collector-Emitter Breakdown Voltage (Vces)": "higher",
            "Current - Collector(Ic)": "higher",
            "Vce Saturation(VCE(sat))": "lower",
        },
    },
    # ============== DIODES ==============
    "Schottky Diodes": {
        "primary": "Voltage - DC Reverse(Vr)",
        "must_match": ["Diode Configuration"],  # single, series pair, common cathode/anode
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
            "Voltage - Forward(Vf@If)": "lower",
        },
    },
    "Switching Diodes": {
        "primary": "Voltage - DC Reverse(Vr)",
        "must_match": ["Diode Configuration"],  # single, series pair, common cathode/anode
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
        },
    },
    "Zener Diodes": {
        "primary": "Zener Voltage(Nom)",
        "must_match": ["Zener Voltage(Nom)", "Diode Configuration"],
        "same_or_better": {
            "Pd - Power Dissipation": "higher",
        },
    },
    "Diodes - General Purpose": {
        "primary": "Voltage - DC Reverse(Vr)",
        "must_match": ["Diode Configuration"],  # single, series pair, common cathode/anode
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
        },
    },
    "Diodes - Rectifiers - Fast Recovery": {
        "primary": "Voltage - DC Reverse(Vr)",
        "must_match": ["Diode Configuration"],  # single, series pair, common cathode/anode
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Average Rectified": "higher",
        },
    },
    "Fast Recovery / High Efficiency Diodes": {
        "primary": "Voltage - DC Reverse(Vr)",
        "must_match": ["Diode Configuration"],  # single, series pair, common cathode/anode
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
        },
    },
    "Bridge Rectifiers": {
        "primary": "Voltage - DC Reverse(Vr)",
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
            "Voltage - Forward(Vf@If)": "lower",
        },
    },
    "Super Barrier Rectifiers (SBR)": {
        "primary": "Voltage - DC Reverse(Vr)",
        "must_match": ["Diode Configuration"],  # single, series pair, common cathode/anode
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
            "Voltage - Forward(Vf@If)": "lower",
        },
    },
    "Avalanche Diodes": {
        "primary": "Voltage - DC Reverse(Vr)",
        "must_match": ["Diode Configuration"],  # single, series pair, common cathode/anode
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
        },
    },
    "High Effic Rectifier": {
        "primary": "Reverse Voltage",
        "same_or_better": {
            "Reverse Voltage": "higher",
            "Average Rectified Current": "higher",
        },
    },
    "SiC Diodes": {
        "primary": "Voltage - DC Reverse(Vr)",
        "must_match": ["Diode Configuration"],  # single, series pair, common cathode/anode
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
        },
    },
    # ============== ESD/TVS PROTECTION ==============
    "ESD and Surge Protection (TVS/ESD)": {
        "primary": "Reverse Stand-Off Voltage (Vrwm)",
        # A unidirectional part can't replace a bidirectional one; TVS (surge) vs ESD; channel count
        "must_match": ["Polarity", "Type", "Number of Channels"],
        "same_or_better": {
            "Clamping Voltage": "lower",
            "Peak Pulse Power Dissipation (Ppp)": "higher",
        },
    },
    "Varistors": {
        "primary": "Varistor Voltage",
        "must_match": ["Varistor Voltage"],
        "same_or_better": {
            "Clamping Voltage": "lower",
            "Energy": "higher",
        },
    },
    "Gas Discharge Tube Arresters (GDT)": {
        "primary": "Voltage - DC Spark Over (Nom)",
        "must_match": ["Number of Poles"],
        "same_or_better": {
            "Impulse Discharge Current": "higher",
        },
    },
    "Semiconductor Discharge Tubes (TSS)": {
        "primary": "Peak off - state voltage(Vdrm)",
        "same_or_better": {
            "Peak Pulse Current-Ipp (10/1000us)": "higher",
        },
    },
    "LED Protection": {
        "primary": "Trigger Voltage",
        "must_match": ["Trigger Voltage"],
        "same_or_better": {
            "Hold Current": "higher",
        },
    },
    # ============== FUSES ==============
    "Resettable Fuses": {
        "primary": "Hold Current",
        "must_match": ["Hold Current", "Trip Current"],
        "same_or_better": {
            "Voltage - Max": "higher",
        },
    },
    "Automotive Fuses": {
        "primary": "Current Rating",
        "must_match": ["Current Rating", "Type"],
        "same_or_better": {
            "Voltage Rating (DC)": "higher",
        },
    },
    "Thermal Fuses (TCO)": {
        "primary": "Rated Functioning Temperature",
        "must_match": ["Rated Functioning Temperature"],
        "same_or_better": {
            "Current Rating": "higher",
            "Voltage Rating": "higher",
        },
    },
    "Disposable fuses": {
        "primary": "Current Rating",
        "must_match": ["Current Rating", "Type"],
        "same_or_better": {
            "Voltage Rating (AC)": "higher",
            "Voltage Rating (DC)": "higher",
        },
    },
    # ============== THERMISTORS ==============
    "NTC Thermistors": {
        "primary": "Resistance @ 25℃",
        "must_match": ["Resistance @ 25℃", "B Constant (25℃/100℃)"],
    },
    "PTC Thermistors": {
        "primary": "Resistance @ 25℃",
        "must_match": ["Resistance @ 25℃"],
    },
    # ============== LEDs ==============
    "LED Indication - Discrete": {
        "primary": "Illumination Color",
        "must_match": ["Illumination Color"],
    },
    "Infrared LED Emitters": {
        "primary": "Wavelength",
        "must_match": ["Wavelength"],
    },
    "Ultraviolet LEDs (UVLED)": {
        "primary": "Peak Wavelength",
        "must_match": ["Peak Wavelength"],
    },
    # ============== OPTOCOUPLERS ==============
    "Transistor, Photovoltaic Output Optoisolators": {
        "primary": "Isolation Voltage(Vrms)",
        "same_or_better": {
            "Isolation Voltage(Vrms)": "higher",
        },
    },
    "Logic Output Optoisolators": {
        "primary": "Isolation Voltage(Vrms)",
        "same_or_better": {
            "Isolation Voltage(Vrms)": "higher",
            "Data Rate": "higher",
        },
    },
    "Triac, SCR Output Optoisolators": {
        "primary": "Load Voltage",
        "same_or_better": {
            "Load Voltage": "higher",
            "Output Current(It(rms))": "higher",
            "Isolation Voltage(Vrms)": "higher",
        },
    },
    "Gate Drive Optocoupler": {
        "primary": "Isolation Voltage(Vrms)",
        "same_or_better": {
            "Isolation Voltage(Vrms)": "higher",
            "Output Current(Max)": "higher",
        },
    },
    "Photointerrupters - Slot Type - Transistor Output": {
        "primary": "Peak Wavelength",
        "must_match": ["Peak Wavelength"],
        "same_or_better": {
            "Load Voltage": "higher",
            "Output Current": "higher",
        },
    },
    "Reflective Optical Interrupters": {
        "primary": "Output Type",
        "must_match": ["Output Type"],
        "same_or_better": {
            "Current - Collector(Ic)": "higher",
        },
    },
    "Photoresistors": {
        "primary": "Cell Resistance @ Illuminance",
        "same_or_better": {
            "Voltage - Max": "higher",
        },
    },
    # ============== TIMING ==============
    "Crystals": {
        "primary": "Frequency",
        "must_match": ["Frequency", "Load Capacitance"],
        "same_or_better": {
            "Frequency Stability": "lower",
        },
    },
    "Crystal Oscillators": {
        "primary": "Frequency",
        "must_match": ["Frequency", "Output Type"],
        "same_or_better": {
            "Frequency Stability": "lower",
        },
    },
    "Ceramic Resonators": {
        "primary": "Frequency",
        "must_match": ["Frequency"],
    },
    "SAW Resonators": {
        "primary": "Frequency",
        "must_match": ["Frequency"],
    },
    "Temperature Compensated Crystal Oscillators (TCXO)": {
        "primary": "Frequency",
        "must_match": ["Frequency", "Output Type"],
        "same_or_better": {
            "Frequency Stability": "lower",
        },
    },
    "Voltage-Controlled Crystal Oscillators (VCXOs)": {
        "primary": "Frequency",
        "must_match": ["Frequency", "Output Type"],
        "same_or_better": {
            "Frequency Stability": "lower",
        },
    },
    "Oven Controlled Crystal Oscillators (OCXOs)": {
        "primary": "Frequency",
        "must_match": ["Frequency", "Output Type"],
        "same_or_better": {
            "Frequency Stability": "lower",
        },
    },
    # ============== VOLTAGE REGULATORS ==============
    "Voltage Regulators - Linear, Low Drop Out (LDO) Regulators": {
        "primary": "Output Voltage",
        "must_match": ["Output Voltage", "Output Type"],
        "ranges": {"Output Voltage": False, "Voltage - Supply": True},
        "same_or_better": {
            "Output Current": "higher",
            "Voltage Dropout": "lower",
        },
    },
    "DC-DC Converters": {
        "primary": "Output Voltage",
        "must_match": ["Topology", "Output Voltage", "Output Type"],  # Buck, Boost, Buck-Boost must match
        "ranges": {"Output Voltage": False, "Voltage - Supply": True},
        "same_or_better": {
            "Output Current": "higher",
        },
    },
    "Voltage Reference": {
        "primary": "Output Voltage",
        "must_match": ["Output Voltage"],
        "same_or_better": {
            "Tolerance": "lower",
            "Temperature Coefficient": "lower",
        },
    },
    # ============== DIGITAL ISOLATORS ==============
    "Digital Isolators": {
        "primary": "Number of Forward Channels",
        "must_match": ["Number of Forward Channels", "Number of Reverse Channels"],
        "same_or_better": {
            "Isolation Voltage(Vrms)": "higher",
            "Data Rate(Max)": "higher",
        },
    },
    # ============== SWITCHES ==============
    "Tactile Switches": {
        "primary": "Mounting Type",
        "must_match": ["Mounting Type"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Contact Current": "higher",
        },
    },
    "DIP Switches": {
        "primary": "Number of Positions",
        "must_match": ["Number of Positions", "Type"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Current Rating": "higher",
        },
    },
    "Slide Switches": {
        "primary": "Circuit",
        "must_match": ["Circuit", "Mounting Type"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Current Rating": "higher",
        },
    },
    "Toggle Switches": {
        "primary": "Circuit",
        "must_match": ["Circuit"],
        "same_or_better": {
            "Voltage Rating (DC)": "higher",
            "Current Rating": "higher",
        },
    },
    "Rocker Switches": {
        "primary": "Circuit",
        "must_match": ["Circuit"],
        "same_or_better": {
            "Voltage Rating (DC)": "higher",
            "Current Rating": "higher",
        },
    },
    "Pushbutton Switches": {
        "primary": "Self Lock / No Lock",
        "must_match": ["Self Lock / No Lock"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Contact Current": "higher",
        },
    },
    "Rotary Switches": {
        "primary": "Positions",
        "must_match": ["Positions", "Number of Poles Per Deck"],
        "same_or_better": {
            "Voltage Rating (DC)": "higher",
            "Current Rating": "higher",
        },
    },
    # ============== RELAYS ==============
    "Power Relays": {
        "primary": "Coil Voltage",
        "must_match": ["Coil Voltage", "Contact Form"],
        "same_or_better": {
            "Contact Rating": "higher",
            "Switching Voltage(Max)": "higher",
        },
    },
    "Signal Relays": {
        "primary": "Coil Voltage",
        "must_match": ["Coil Voltage", "Contact Form"],
        "same_or_better": {
            "Contact Rating": "higher",
            "Switching Current(Max)": "higher",
        },
    },
    "Automotive Relays": {
        "primary": "Coil Voltage",
        "must_match": ["Coil Voltage", "Contact Form"],
        "same_or_better": {
            "Contact Rating": "higher",
            "Switching Voltage(Max)": "higher",
        },
    },
    "Reed Relays": {
        "primary": "Coil Voltage",
        "must_match": ["Coil Voltage", "Contact Form"],
        "same_or_better": {
            "Switching Voltage(Max)": "higher",
            "Switching Current(Max)": "higher",
        },
    },
    "Solid State Relays (MOS Output)": {
        "primary": "Load Voltage",
        "same_or_better": {
            "Load Voltage": "higher",
            "Load Current": "higher",
            "RDS(on)": "lower",
        },
    },
    "Solid State Relays (Triac Output)": {
        "primary": "Load Voltage",
        "must_match": ["Contact Form"],
        "same_or_better": {
            "Load Voltage": "higher",
            "Load Current": "higher",
        },
    },
    # ============== CONNECTORS ==============
    "Pin Headers": {
        "primary": "Pitch",
        "must_match": ["Pitch", "Number of Pins", "Number of Rows", "Mounting Type"],
        "same_or_better": {
            "Current Rating": "higher",
        },
    },
    "Female Headers": {
        "primary": "Pitch",
        "must_match": ["Pitch", "Number of Positions", "Number of Rows", "Mounting Type"],
        "same_or_better": {
            "Current Rating": "higher",
        },
    },
    "Screw Terminal Blocks": {
        "primary": "Number of Positions or Pins",
        "must_match": ["Number of Positions or Pins", "Mounting Type"],
        "same_or_better": {
            "Voltage Rating (Max)": "higher",
            "Current Rating": "higher",
        },
    },
    "Barrier Terminal Blocks": {
        "primary": "Number of Positions or Pins",
        "must_match": ["Pitch", "Number of Positions or Pins", "Mounting Type"],
        "same_or_better": {
            "Voltage Rating (Max)": "higher",
            "Current Rating": "higher",
        },
    },
    "Pluggable System Terminal Block": {
        "primary": "Number of Positions or Pins",
        "must_match": ["Pitch", "Number of Positions or Pins", "Mounting Type"],
        "same_or_better": {
            "Voltage Rating (Max)": "higher",
            "Current Rating": "higher",
        },
    },
    "USB Connectors": {
        "primary": "Connector Type",
        "must_match": ["Connector Type", "Gender", "Number of Contacts", "Mounting Type"],
    },
    "HDMI Connectors": {
        "primary": "Connector Type",
        "must_match": ["Connector Type", "Gender", "Mounting Type"],
    },
    "DisplayPort (DP) Connector": {
        "primary": "Connector Type",
        "must_match": ["Connector Type", "Mounting Type"],
    },
    "Audio Connectors": {
        "primary": "Connector Type",
        "must_match": ["Connector Type", "Mounting Type"],
        "same_or_better": {
            "Voltage Rating (Max)": "higher",
            "Current Rating": "higher",
        },
    },
    "Coaxial Connectors (RF)": {
        "primary": "Connector Type",
        "must_match": ["Connector Type", "Impedance", "RF Series", "Interface", "Mounting Type"],  # SMA vs IPEX; jack vs plug
    },
    "IDC Connectors": {
        "primary": "Number of Positions or Pins",
        "must_match": ["Number of Positions or Pins", "Pitch", "Mounting Type"],
        "same_or_better": {
            "Current Rating": "higher",
        },
    },
    "Wire To Board Connector": {
        "primary": "Pitch",
        "must_match": ["Pitch", "Pins Structure", "Reference Series", "Mounting Type"],
        "same_or_better": {
            "Current Rating": "higher",
            "Voltage Rating": "higher",
        },
    },
    "Circular Connectors & Cable Connectors": {
        "primary": "Number of Pins",
        "must_match": ["Number of Pins", "Gender", "Mounting Type"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Current Rating": "higher",
        },
    },
    "XLR (Cannon) Connectors": {
        "primary": "Number of Pins",
        "must_match": ["Number of Pins", "Gender", "Mounting Type"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Current Rating": "higher",
        },
    },
    "DIN41612 Connectors": {
        "primary": "Number of Pins",
        "must_match": ["Pitch", "Number of Pins", "Number of Rows", "Mounting Type"],
        "same_or_better": {
            "Current Rating": "higher",
        },
    },
    "Shunts, Jumpers": {
        "primary": "Pitch",
        "must_match": ["Pitch", "Number of Positions or Pins", "Mounting Type"],
        "same_or_better": {
            "Current Rating": "higher",
        },
    },
    # ============== AUDIO ==============
    "Speakers": {
        "primary": "Impedance",
        "must_match": ["Impedance"],
        "same_or_better": {
            "Rated Power": "higher",
        },
    },
    "Buzzers": {
        "primary": "Voltage - Supply",
        "must_match": ["Driver Circuitry"],
        "same_or_better": {
            "Sound Pressure Level(SPL)": "higher",
        },
    },
    "Microphones": {
        "primary": "Direction",
        "must_match": ["Direction"],
    },
    "MEMS Microphones": {
        "primary": "Output Type",
        "must_match": ["Output Type"],
    },
    # ============== MISC ==============
    "Vibration Motors": {
        "primary": "Voltage Rating",
        "same_or_better": {
            "Voltage Rating": "higher",
            "Current Rating": "higher",
        },
    },
    "Rotary Encoders": {
        "primary": "Encoder Type",
        "must_match": ["Encoder Type"],
        "same_or_better": {
            "Rated Voltage (Max)": "higher",
            "Current Rating (Max)": "higher",
        },
    },
    # ============== BATTERY MANAGEMENT ==============
    "Battery Management": {
        "primary": "Type of Battery",
        "must_match": ["Type of Battery", "Number of Cells", "The Chip Type"],
        "same_or_better": {
            "Charge Current - Max": "higher",
        },
    },
    # ============== LEVEL SHIFTERS ==============
    "Translators, Level Shifters": {
        "primary": "Channel Type",
        "must_match": ["Channel Type"],  # Bidirectional vs Unidirectional
    },
    # ============== WIRELESS MODULES ==============
    "WiFi Modules": {
        "primary": "Voltage - Supply",
        "must_match": ["Voltage - Supply", "Utilized IC / Part"],  # an ESP32-C3 module can't replace an ESP32-S3 one
        "same_or_better": {
            "Output Power": "higher",
        },
    },
    "Bluetooth Modules": {
        "primary": "Voltage - Supply",
        "must_match": ["Voltage - Supply", "Utilized IC / Part"],
        "same_or_better": {
            "Output Power(Max)": "higher",
        },
    },
    "LoRa Modules": {
        "primary": "Frequency",
        "must_match": ["Frequency", "Voltage - Supply"],
        "same_or_better": {
            "Output Power": "higher",
        },
    },
    # ============== MOTOR DRIVERS ==============
    # Note: Many Motor Driver ICs have sparse specs in JLCPCB data.
    # These rules apply when specs are available.
    "Motor Driver ICs": {
        "primary": "Output Current",
        "same_or_better": {
            "Output Current": "higher",
            "Voltage - Supply": "higher",
        },
    },
    "Brushed DC Motor Drivers": {
        "primary": "Output Current",
        "must_match": ["Number of H-bridges"],  # Critical: 2-bridge can't replace 1-bridge
        "same_or_better": {
            "Output Current": "higher",
            "Peak Current": "higher",
            "RDS(on)": "lower",
        },
    },
    # ============== AUDIO ==============
    "Audio Amplifiers": {
        "primary": "Class",  # Class D, Class AB, etc.
        "must_match": ["Class"],
        "same_or_better": {
            "Output Power": "higher",
        },
    },
}


# =============================================================================
# PIN COUNT NORMALIZATION (for connectors)
# =============================================================================
# Specs that represent pin/position counts needing normalization
PIN_COUNT_SPECS = {
    "Number of Contacts",
    "Number of Pins",
    "Number of Positions",
    "Number of Positions or Pins",
    "Pin Structure",
    "Pins Structure",
}


def _lower(value: str) -> str:
    return " ".join(value.lower().split())


def _same_as(synonyms: dict[str, str]) -> Callable[[str], str]:
    """Normalizer that maps synonyms (lowercase) to one name and lowercases everything else."""
    return lambda value: synonyms.get(_lower(value), _lower(value))


def _chip_names(value: str) -> str:
    """A module's chips: "ESP32-DOWD-V3、ESP32-DOWDR2-V3" (letter O, as some listings have it) =
    "ESP32-D0WD-V3、ESP32-D0WDR2-V3"; "ESP8266 Chip" = "ESP8266"."""
    names = {re.sub(r"\s+chip$", "", name).replace("o", "0") for name in _lower(value).split("、") if name.strip()}
    names = {re.sub(r"^(esp32-[schp]\d+)r\d+$", r"\1", name) for name in names}
    return "、".join(sorted(names))


# String specs whose values have synonyms, compared after normalizing
_MATCH_NORMALIZERS: dict[str, Callable[[str], str]] = {
    "Diode Configuration": _same_as({"standalone": "1 independent", "independent": "1 independent"}),
    "Temperature Coefficient": _same_as({"np0": "c0g", "npo": "c0g", "cog": "c0g"}),  # one dielectric
    "Interface": _same_as({"inner bore": "inner hole", "male pin": "inner pin"}),  # coax jack vs plug
    "Utilized IC / Part": _chip_names,
}

# Compared after normalizing ("8P" = "1x8P", "NP0" = "C0G"), so an exact string match in SQL would
# miss equal values
NORMALIZED_MATCH_SPECS = frozenset({*PIN_COUNT_SPECS, *_MATCH_NORMALIZERS})


def _normalize_pin_count(value: str) -> str:
    """Normalize pin count values for comparison.

    Examples:
        '1x8P' -> '8'
        '8P' -> '8'
        '8' -> '8'
        '2x10P' -> '20' (2 rows x 10 = 20 total pins)
    """
    value = value.strip()

    # Handle "NxMP" format (rows x pins per row) -> total
    match = re.match(r"(\d+)\s*x\s*(\d+)\s*[Pp]?$", value)
    if match:
        rows = int(match.group(1))
        pins_per_row = int(match.group(2))
        return str(rows * pins_per_row)

    # Handle "1xNP" format -> just N (single row)
    match = re.match(r"1\s*x\s*(\d+)\s*[Pp]?$", value)
    if match:
        return match.group(1)

    # Handle "NP" format -> N
    match = re.match(r"(\d+)\s*[Pp]$", value)
    if match:
        return match.group(1)

    # Handle plain number
    match = re.match(r"(\d+)$", value)
    if match:
        return match.group(1)

    return value


# =============================================================================
# COMPATIBILITY CHECKING FUNCTIONS
# =============================================================================


# A value that says nothing: empty, "-", or "-、-" in multi-value fields
_PLACEHOLDER_PATTERN = re.compile(r"[\s\-、,/]*")


def is_stated(value: str | None) -> bool:
    """True if a spec value says something (not missing, empty or "-")."""
    return value is not None and not _PLACEHOLDER_PATTERN.fullmatch(value)


def _compare_values(orig_val: str, cand_val: str, spec: str) -> bool | None:
    """Check if two spec values match (for must_match rules). None if they can't be compared
    (a numeric spec whose value doesn't parse)."""
    # Special handler for complex formats
    if spec == "Impedance @ Frequency":
        return impedance_at_freq_match(orig_val, cand_val)

    # Pin count specs: normalize before comparing (handles "8P" vs "1x8P" vs "8")
    if spec in PIN_COUNT_SPECS:
        return _normalize_pin_count(orig_val) == _normalize_pin_count(cand_val)

    normalize = _MATCH_NORMALIZERS.get(spec)
    if normalize:
        return normalize(orig_val) == normalize(cand_val)

    # String-based specs: exact match (case-insensitive)
    if spec in STRING_MATCH_SPECS:
        return orig_val.strip().lower() == cand_val.strip().lower()

    # Numeric specs: parse and compare with tolerance
    parser = SPEC_PARSERS.get(spec)
    if parser and parser != "special" and callable(parser):
        orig_parsed = parser(orig_val)
        cand_parsed = parser(cand_val)
        if orig_parsed is None or cand_parsed is None:
            return None
        # 2% tolerance for matching (handles rounding differences in display); resistors closer
        if orig_parsed == 0:
            return cand_parsed == 0
        share = RESISTANCE_MATCH_TOLERANCE if parser is parse_resistance else 0.02
        return abs(orig_parsed - cand_parsed) / abs(orig_parsed) < share

    # Fallback: string match
    return orig_val.strip().lower() == cand_val.strip().lower()


def _values_match(orig_val: str, cand_val: str, spec: str) -> bool:
    """Check if two spec values match (for must_match rules). Values that can't be compared pass."""
    return _compare_values(orig_val, cand_val, spec) is not False


def _spec_ok(orig_val: str, cand_val: str, spec: str, direction: str) -> bool:
    """Check if candidate spec meets same_or_better requirement."""
    parser = SPEC_PARSERS.get(spec)
    if not parser or parser == "special" or not callable(parser):
        return True  # Can't parse, allow through

    orig_parsed = parser(orig_val)
    cand_parsed = parser(cand_val)

    if orig_parsed is None or cand_parsed is None:
        return True  # Can't parse, allow through

    if direction == "higher":
        return cand_parsed >= orig_parsed * 0.98  # 2% tolerance
    elif direction == "lower":
        return cand_parsed <= orig_parsed * 1.02  # 2% tolerance
    else:
        return True


# value@condition specs where lower is better and the value rises as the condition gets harder:
# spec -> (value parser, condition parser, which way the condition gets harder)
_CONDITIONAL_SPECS: dict[str, tuple[Callable[[str], float | None], Callable[[str], float | None], str]] = {
    "Voltage Dropout": (parse_voltage, parse_current, "higher"),  # "240mV@(50mA)": rises with load
    "Voltage - Forward(Vf@If)": (parse_voltage, parse_current, "higher"),  # "550mV@3A"
    "RDS(on)": (parse_resistance, parse_voltage, "lower"),  # "12mΩ@10V、15mΩ@4.5V": rises as Vgs falls
}


def _conditional_pairs(value: str, spec: str) -> list[tuple[float, float | None]]:
    """(value, condition) pairs: "47mΩ@10V、60mΩ@4.5V" -> [(0.047, 10.0), (0.06, 4.5)]."""
    value_parser, condition_parser, _ = _CONDITIONAL_SPECS[spec]
    pairs = []
    for item in value.split("、"):
        number, _, condition = item.partition("@")
        parsed = value_parser(number)
        if parsed is not None:
            pairs.append((parsed, condition_parser(condition) if condition else None))
    return pairs


def _conditional_ok(orig_val: str, cand_val: str, spec: str) -> bool | None:
    """same_or_better ("lower") for a value@condition spec. Compares at a condition both list; otherwise
    the first values, as other specs do, except that a lower value at an easier condition (Vf at a lower
    current, RDS(on) at a higher Vgs) proves nothing: None. None also when either doesn't parse."""
    orig, cand = _conditional_pairs(orig_val, spec), _conditional_pairs(cand_val, spec)
    if not orig or not cand:
        return None
    for orig_value, orig_cond in orig:
        for cand_value, cand_cond in cand:
            if orig_cond is not None and cand_cond is not None and abs(cand_cond - orig_cond) <= abs(orig_cond) * 0.02:
                return cand_value <= orig_value * 1.02
    (orig_value, orig_cond), (cand_value, cand_cond) = orig[0], cand[0]
    if cand_value > orig_value * 1.02:
        return False
    if orig_cond is not None and cand_cond is not None:
        easier = cand_cond < orig_cond if _CONDITIONAL_SPECS[spec][2] == "higher" else cand_cond > orig_cond
        if easier:
            return None
    return True


# "2 N-Channel", "1 NPN (Pre-Biased)", "3 n-channels": a count per polarity
_POLARITY_COUNT_PATTERN = re.compile(r"(\d+)\s*(N-?channels?|P-?channels?|NPN|PNP)\b", re.IGNORECASE)
# "N-Channel + P-Channel", "NPN+PNP", "NPN、PNP": polarity only
_POLARITY_PATTERN = re.compile(r"\b(N-?channel|P-?channel|NPN|PNP)\b", re.IGNORECASE)


def _polarity(specs: dict[str, str], names: list[str]) -> tuple[frozenset[str], dict[str, int] | None] | None:
    """A transistor's polarity from the specs that state it, as (letters, counts per letter):
    "1 N-channel" -> ({"N"}, {"N": 1}), "2 NPN" -> ({"N"}, {"N": 2}),
    "N-Channel + P-Channel" -> ({"N", "P"}, None). None if no spec states it or two disagree.
    """
    letters: frozenset[str] | None = None
    counts: dict[str, int] | None = None
    for name in names:
        value = specs.get(name)
        if not value or not is_stated(value):
            continue
        found_counts: dict[str, int] = {}
        for number, kind in _POLARITY_COUNT_PATTERN.findall(value):
            found_counts[kind[0].upper()] = found_counts.get(kind[0].upper(), 0) + int(number)
        found = frozenset(found_counts) or frozenset(m[0].upper() for m in _POLARITY_PATTERN.findall(value))
        if not found:
            continue  # e.g. MOSFET Type "ESD"
        if letters is not None and found != letters:
            return None
        letters = found
        if found_counts:
            if counts is not None and found_counts != counts:
                return None
            counts = found_counts
    return (letters, counts) if letters is not None else None


def _voltage_ranges(value: str | None) -> list[tuple[float, float]] | None:
    """Parse every interval; a partly understood range cannot establish coverage."""
    if not is_stated(value):
        return None
    ranges = []
    for interval in value.split("、"):
        endpoints = re.split(r"[~～–]", interval)
        if len(endpoints) not in (1, 2):
            return None
        parsed = []
        for endpoint in endpoints:
            if not re.fullmatch(r"\s*[+-]?\d+(?:\.\d+)?\s*[mk]?V?\s*", endpoint, re.IGNORECASE):
                return None
            number = parse_voltage(endpoint)
            if number is None:
                return None
            parsed.append(-number if endpoint.strip().startswith("-") else number)
        ranges.append((min(parsed), max(parsed)))
    return ranges


def voltage_range_covers(original: str | None, candidate: str | None, maximum_only: bool = False) -> bool | None:
    """Candidate covers every original interval; narrower operating ranges cannot pass.

    A scalar supply rating states only a maximum; it cannot prove the minimum of a range.
    """
    orig, cand = _voltage_ranges(original), _voltage_ranges(candidate)
    if orig is None or cand is None:
        return None
    for low, high in orig:
        if maximum_only and low == high:
            if not any(c_high >= high and (c_low == c_high or c_low <= high) for c_low, c_high in cand):
                return False
        elif maximum_only and all(c_low == c_high for c_low, c_high in cand):
            return None
        elif not any(c_low <= low and c_high >= high
                     for c_low, c_high in cand):
            return False
    return True


def _esp32_family(value: str | None) -> str | None:
    """Recognize ESP32 families in module ordering codes and stated chip variants."""
    match = re.match(r"^ESP32(?:-([SCHP]\d+)[A-Z0-9]*)?(?:[-\s]|$)", value or "", re.IGNORECASE)
    return ("ESP32" + (f"-{match[1].upper()}" if match[1] else "")) if match else None


def _module_chip(part: dict[str, Any]) -> str | None:
    """Use a stated chip, or infer the ESP32 family from the module's ordering code."""
    chip = part.get("specs", {}).get("Utilized IC / Part")
    if is_stated(chip):
        return chip
    return _esp32_family(part.get("model"))


def prefer_same_package(subcategory: str) -> bool:
    """Package is the footprint for passives and crystals; keep other packages visible."""
    primary = COMPATIBILITY_RULES.get(subcategory, {}).get("primary")
    return primary in {
        "Resistance", "Resistance @ 25℃", "Cell Resistance @ Illuminance",
        "Capacitance", "Inductance", "Impedance @ Frequency",
    } or "crystal" in subcategory.lower()


def is_compatible_alternative(
    original: dict[str, Any], candidate: dict[str, Any], subcategory: str
) -> tuple[bool, dict[str, Any]]:
    """Check if candidate is a compatible alternative for original.

    Returns (is_compatible, verification_info). Known mismatches fail. Missing required matches
    stay eligible only for the caller's unverified list; other unchecked specs lower confidence.
    """
    rules = COMPATIBILITY_RULES.get(subcategory)
    if not rules:
        return True, {"specs_verified": [], "specs_unparseable": []}

    orig_specs = original.get("specs", {})
    cand_specs = candidate.get("specs", {})

    specs_verified: list[str] = []
    specs_unparseable: list[str] = []
    unverified_requirements: list[str] = []
    unchecked_requirements: list[str] = []

    def result(is_compat: bool) -> tuple[bool, dict[str, Any]]:
        return is_compat, {
            "specs_verified": specs_verified, "specs_unparseable": specs_unparseable,
            "unverified_requirements": unverified_requirements,
            "unchecked_requirements": list(dict.fromkeys([*specs_unparseable, *unchecked_requirements])),
        }

    # A required match needs both values. Reference series applies only when the original states it.
    for spec in dict.fromkeys([rules["primary"], *rules.get("must_match", [])]):
        orig_val = orig_specs.get(spec)
        cand_val = cand_specs.get(spec)
        if spec == "Utilized IC / Part":
            inferred = not (is_stated(orig_val) and is_stated(cand_val))
            orig_val, cand_val = _module_chip(original), _module_chip(candidate)
            orig_family, cand_family = _esp32_family(orig_val), _esp32_family(cand_val)
            if inferred and orig_family and cand_family:
                if orig_family != cand_family:
                    return result(False)
                specs_unparseable.append(spec)
                unverified_requirements.append(spec)
                continue  # A family match cannot verify the exact chip.
        if spec == "Reference Series" and not is_stated(orig_val):
            continue
        if spec in rules.get("ranges", {}):
            continue  # Compare both endpoints below, rather than the first number.
        if is_stated(orig_val) and is_stated(cand_val):
            matched = _compare_values(orig_val, cand_val, spec)
            if matched is False:
                return result(False)
            (specs_verified if matched else specs_unparseable).append(spec)
            if matched is None:
                unverified_requirements.append(spec)
        else:
            specs_unparseable.append(spec)
            unverified_requirements.append(spec)

    for spec, maximum_only in rules.get("ranges", {}).items():
        orig_val, cand_val = orig_specs.get(spec), cand_specs.get(spec)
        covers = voltage_range_covers(orig_val, cand_val, maximum_only)
        if covers is False:
            return result(False)
        (specs_verified if covers else specs_unparseable).append(spec)
        if covers is None:
            unverified_requirements.append(spec)
        if maximum_only and (not is_stated(orig_val) or not any(mark in orig_val for mark in ("~", "～", "–"))):
            unchecked_requirements.append("minimum input voltage")
    if rules.get("ranges"):
        unchecked_requirements.extend(["pinout", "external circuit requirements"])

    if "Utilized IC / Part" in rules.get("must_match", []):
        orig_memory = parse_esp32_module_memory(original.get("model"))
        cand_memory = parse_esp32_module_memory(candidate.get("model"))
        for spec, required, available in zip(("Module Flash", "Module PSRAM"), orig_memory, cand_memory):
            if required is None:
                continue
            if available is None:
                specs_unparseable.append(spec)
                unverified_requirements.append(spec)
            elif available < required:
                return result(False)
            else:
                specs_verified.append(spec)

    # N/P (or NPN/PNP) and how many: a candidate that doesn't say can't be used
    polarity_specs = rules.get("polarity")
    if polarity_specs:
        orig_polarity = _polarity(orig_specs, polarity_specs)
        if orig_polarity is None:
            specs_unparseable.append("polarity")
            unverified_requirements.append("polarity")
        else:
            cand_polarity = _polarity(cand_specs, polarity_specs)
            if cand_polarity is None or cand_polarity[0] != orig_polarity[0]:
                return result(False)
            if orig_polarity[1] is not None and cand_polarity[1] is not None and cand_polarity[1] != orig_polarity[1]:
                return result(False)
            specs_verified.append("polarity")

    # Check same_or_better specs
    for spec, direction in rules.get("same_or_better", {}).items():
        orig_val = orig_specs.get(spec)
        cand_val = cand_specs.get(spec)
        parser = SPEC_PARSERS.get(spec)
        if spec in _CONDITIONAL_SPECS and direction == "lower" and orig_val and cand_val:
            better = _conditional_ok(orig_val, cand_val, spec)
            if better is False:
                return result(False)
            outcome = specs_verified if better else specs_unparseable
        elif (
            orig_val and cand_val and callable(parser)
            and parser(orig_val) is not None and parser(cand_val) is not None
        ):
            if not _spec_ok(orig_val, cand_val, spec, direction):
                return result(False)
            outcome = specs_verified
        elif orig_val or cand_val:
            outcome = specs_unparseable  # One side missing, no parser, or couldn't parse
        else:
            continue
        if spec not in specs_verified and spec not in specs_unparseable:  # primary is often also here
            outcome.append(spec)

    return result(True)


def verify_primary_spec_match(
    original: dict[str, Any], candidate: dict[str, Any], primary_attr: str
) -> bool:
    """Verify candidate has same primary spec value as original. Passes when that can't be checked
    (is_compatible_alternative lists it as unparseable)."""
    orig_value = original.get("specs", {}).get(primary_attr)
    cand_value = candidate.get("specs", {}).get(primary_attr)

    if not is_stated(orig_value) or not is_stated(cand_value):
        return True  # Can't verify, allow through

    return _values_match(orig_value, cand_value, primary_attr)


# =============================================================================
# SCORING AND RANKING
# =============================================================================


def score_alternative(
    part: dict[str, Any],
    original: dict[str, Any],
    min_price_in_results: float | None,
) -> tuple[int, dict[str, int]]:
    """Score an alternative part for ranking.

    Returns (total_score, breakdown_dict) tuple.
    Higher score = better alternative.
    """
    score = 0
    breakdown: dict[str, int] = {}

    # Library type (biggest factor - $3 savings)
    if part.get("library_type") in ("basic", "preferred"):
        score += 1000
        breakdown["library_type"] = 1000
    else:
        breakdown["library_type"] = 0

    # Availability (user controls floor via min_stock param)
    stock = part.get("stock", 0)
    if stock >= 10000:
        avail_score = 70  # Excellent availability
    elif stock >= 1000:
        avail_score = 50  # Good availability
    elif stock >= 100:
        avail_score = 30  # Acceptable
    else:
        avail_score = -10  # Minor penalty for <100
    score += avail_score
    breakdown["availability"] = avail_score

    # EasyEDA footprint bonus (easier for users)
    if part.get("has_easyeda_footprint"):
        score += 20
        breakdown["easyeda"] = 20
    else:
        breakdown["easyeda"] = 0

    # Same manufacturer bonus (consistency)
    if part.get("manufacturer") == original.get("manufacturer"):
        score += 10
        breakdown["same_manufacturer"] = 10
    else:
        breakdown["same_manufacturer"] = 0

    # Price (minor factor, tiebreaker only)
    part_price = part.get("price")
    if part_price and part_price > 0 and min_price_in_results and min_price_in_results > 0:
        price_ratio = min_price_in_results / part_price
        price_score = min(10, int(10 * price_ratio))  # 0-10 points, capped
        score += price_score
        breakdown["price"] = price_score
    else:
        breakdown["price"] = 0

    return score, breakdown


# =============================================================================
# RESPONSE BUILDING
# =============================================================================


def build_response(
    original: dict[str, Any],
    scored_alternatives: list[tuple[int, dict[str, Any], dict[str, int], dict[str, Any]]],
    subcategory: str,
    primary_attr: str | None,
    primary_value: str | None,
    limit: int,
    *,
    unverified_alternatives: list[tuple[int, dict[str, Any], dict[str, int], dict[str, Any]]] | None = None,
    library_type: str | None = None,
    extended_count: int = 0,
    board_quantity: int = 1,
    placements_per_board: int = 1,
) -> dict[str, Any]:
    """Build the find_alternatives response for a supported subcategory."""
    alternatives = scored_alternatives[:limit]
    unverified = (unverified_alternatives or [])[:limit]

    # Count basic/preferred alternatives
    no_fee_count = sum(
        1
        for _, p, _, _ in alternatives
        if p.get("library_type") in ("basic", "preferred")
    )

    # Unchecked ranges and replacement requirements must never imply a verified drop-in pinout.
    unchecked = list(dict.fromkeys(
        spec for _, _, _, info in alternatives
        for spec in info.get("unchecked_requirements", info["specs_unparseable"])
    ))
    all_specs_verified = bool(alternatives) and not unchecked
    confidence = "high" if all_specs_verified else "medium" if alternatives else "low"
    confidence_reason = (
        "All catalog rule checks passed; review datasheets for replacement suitability"
        if all_specs_verified else
        "Some requirements remain unchecked - verify manually" if alternatives else
        "No verified alternatives found; any unverified candidates require manual comparison"
    )

    # Build human-readable summary
    if not alternatives:
        if library_type == "no_fee":
            message = f"No basic/preferred part meets the checked specs; {extended_count} extended alternative(s) do in the evaluated candidates"
        else:
            message = (
                f"No compatible alternatives found matching {primary_value}"
                if is_stated(primary_value) else "No compatible alternatives found"
            )
    elif no_fee_count > 0 and original.get("library_type") in ("basic", "preferred"):
        message = f"Found {no_fee_count} basic/preferred alternative(s)"
    elif no_fee_count > 0:
        message = (
            f"Found {no_fee_count} basic/preferred alternative(s) that save $3 assembly fee"
        )
    else:
        message = f"Found {len(alternatives)} alternative(s), but all are extended library"

    # Calculate savings vs best alternative
    best_part = alternatives[0][1] if alternatives else None
    savings = None
    if best_part:
        original_fee = 3.0 if original.get("library_type") == "extended" else 0.0
        replacement_fee = 3.0 if best_part.get("library_type") == "extended" else 0.0
        assembly_savings = original_fee - replacement_fee
        orig_price = original.get("price")
        best_price = best_part.get("price")
        price_diff = round(orig_price - best_price, 8) if orig_price is not None and best_price is not None else None
        component_quantity = board_quantity * placements_per_board
        savings = {
            "assembly_fee": assembly_savings,
            "unit_price_diff": price_diff,
            "board_quantity": board_quantity,
            "placements_per_board": placements_per_board,
            "component_quantity": component_quantity,
            "order_total": round(assembly_savings + price_diff * component_quantity, 4) if price_diff is not None else None,
            "note": "Assembly fees are per unique part type per order, assuming the original type is removed and the replacement type is newly added. Unit prices use qty 1 tiers, not order quotes.",
        }

    # Comparison helper
    comparison = None
    if best_part:
        comparison = {
            "original": {
                "lcsc": original.get("lcsc"),
                "library_type": original.get("library_type"),
                "price": original.get("price"),
                "stock": original.get("stock"),
            },
            "recommended": {
                "lcsc": best_part.get("lcsc"),
                "library_type": best_part.get("library_type"),
                "price": best_part.get("price"),
                "stock": best_part.get("stock"),
            },
            "savings": savings,
        }

    # Build alternatives list with verification info, MOQ warnings, and package warnings
    original_pkg = original.get("package", "")
    alternatives_output = []
    unverified_output = []
    for score, part, breakdown, verify_info in [*alternatives, *unverified]:
        alt: dict[str, Any] = {
            **part,
            "score": score,
            "score_breakdown": breakdown,
            "specs_verified": verify_info["specs_verified"],
            "specs_unparseable": verify_info["specs_unparseable"],
            "unchecked_requirements": verify_info.get("unchecked_requirements", verify_info["specs_unparseable"]),
        }
        # Add MOQ warning if high
        moq = part.get("min_order", 1)
        if moq and moq > 100:
            alt["moq_warning"] = f"High MOQ: {moq} units minimum"
        # Add package warning if different from original
        part_pkg = part.get("package", "")
        if original_pkg and part_pkg and original_pkg != part_pkg:
            alt["package_warning"] = f"Different package: {part_pkg} vs original {original_pkg}"
        if verify_info.get("unverified_requirements"):
            alt["verification_status"] = "unverified - required specs could not be checked"
            alt["unverified_requirements"] = verify_info["unverified_requirements"]
            unverified_output.append(alt)
        else:
            alternatives_output.append(alt)

    return {
        "original": original,
        "alternatives": alternatives_output,
        "unverified_alternatives": unverified_output,
        "summary": {
            "found": len(alternatives),
            "unverified_count": len(unverified_output),
            "extended_count": extended_count,
            "basic_preferred_count": no_fee_count,
            "message": message,
            "is_supported_category": True,
            "price_note": "Prices shown are unit price at qty 1 tier",
        },
        "comparison": comparison,
        "confidence": {
            "level": confidence,
            "reason": confidence_reason,
            "unchecked_requirements": unchecked,
        },
        "search_criteria": {
            "primary_attribute": primary_attr,
            "matched_value": primary_value,
            "subcategory": subcategory,
            "compatibility_verified": bool(alternatives),
        },
    }


def build_unsupported_response(
    original: dict[str, Any],
    scored_parts: list[tuple[int, dict[str, Any], dict[str, int], dict[str, Any]]],
    subcategory: str,
    primary_attr: str | None,
    limit: int,
) -> dict[str, Any]:
    """Build response for unsupported subcategories - similar parts, not alternatives."""
    similar = scored_parts[:limit]

    # Use attribute names from original part for verification guidance
    specs_to_verify = list(original.get("specs", {}).keys())
    original_pkg = original.get("package", "")

    similar_parts_output = []
    for score, part, breakdown, _ in similar:
        item: dict[str, Any] = {
            **part,
            "score": score,
            "score_breakdown": breakdown,
        }
        moq = part.get("min_order", 1)
        if moq and moq > 100:
            item["moq_warning"] = f"High MOQ: {moq} units minimum"
        # Add package warning if different from original
        part_pkg = part.get("package", "")
        if original_pkg and part_pkg and original_pkg != part_pkg:
            item["package_warning"] = f"Different package: {part_pkg} vs original {original_pkg}"
        similar_parts_output.append(item)

    primary_value = None
    if primary_attr:
        primary_value = original.get("specs", {}).get(primary_attr)

    return {
        "original": original,
        "alternatives": [],  # Empty - we can't verify compatibility
        "similar_parts": similar_parts_output,
        "summary": {
            "found": 0,
            "similar_count": len(similar),
            "message": "No compatibility rules for this category. Showing similar parts for manual comparison.",
            "is_supported_category": False,
            "price_note": "Prices shown are unit price at qty 1 tier",
        },
        "manual_comparison": {
            "original_specs": original.get("specs", {}),
            "specs_to_verify": specs_to_verify[:5],
            "guidance": (
                f"Compare these specs manually: {', '.join(specs_to_verify[:5])}"
                if specs_to_verify
                else "Review datasheets for compatibility"
            ),
        },
        "search_criteria": {
            "primary_attribute": primary_attr,
            "matched_value": primary_value,
            "subcategory": subcategory,
            "compatibility_verified": False,
        },
    }
