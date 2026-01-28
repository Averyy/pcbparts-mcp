#!/usr/bin/env python3
"""
Build SQLite database from scraped JLCPCB component data.

Reads gzipped JSONL files from data/categories/ and creates a searchable
SQLite database with FTS5 full-text search.

Usage:
    python scripts/build_database.py [--data-dir PATH] [--output PATH]

The database is built on deploy/startup and used for parametric searches.
"""

import argparse
import gzip
import json
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

# Add parent directory to path for imports when running as script
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from jlcpcb_mcp.parsers import (
    parse_capacitance,
    parse_capacitance_pf,
    parse_current,
    parse_decibels,
    parse_freq_range,
    parse_frequency,
    parse_inductance,
    parse_integer,
    parse_length_mm,
    parse_luminosity,
    parse_memory_size,
    parse_percentage,
    parse_power,
    parse_ppm,
    parse_resistance,
    parse_temp_range,
    parse_tolerance,
    parse_vgs_range,
    parse_vin_range,
    parse_voltage,
    parse_wavelength,
)


# Attribute name -> (column_name, parser_function) mapping
# Multiple attribute names can map to the same column
ATTRIBUTE_TO_COLUMN: dict[str, tuple[str, Any]] = {
    # Passives - Resistance
    "Resistance": ("resistance_ohms", parse_resistance),

    # Passives - Capacitance
    "Capacitance": ("capacitance_f", parse_capacitance),

    # Passives - Inductance
    "Inductance": ("inductance_h", parse_inductance),
    "DC Resistance(DCR)": ("dcr_ohms", parse_resistance),
    "Current - Saturation(Isat)": ("isat_a", parse_current),
    "Current - Saturation (Isat)": ("isat_a", parse_current),
    "Saturation Current": ("isat_a", parse_current),

    # Voltage
    "Voltage Rating": ("voltage_max_v", parse_voltage),
    "Voltage - Supply": ("voltage_max_v", parse_voltage),
    "Voltage-Supply(Max)": ("voltage_max_v", parse_voltage),

    # Current
    "Current Rating": ("current_max_a", parse_current),

    # Tolerance
    "Tolerance": ("tolerance_pct", parse_tolerance),

    # Power
    "Power(Watts)": ("power_w", parse_power),
    "Pd - Power Dissipation": ("power_w", parse_power),

    # MOSFETs
    "Drain to Source Voltage": ("vds_max_v", parse_voltage),
    "Gate Threshold Voltage (Vgs(th))": ("_vgs_th_range", parse_vgs_range),
    "Gate Threshold Voltage": ("_vgs_th_range", parse_vgs_range),
    "Current - Continuous Drain(Id)": ("id_max_a", parse_current),
    "RDS(on)": ("rds_on_ohms", parse_resistance),
    "Total Gate Charge(Qg)": ("qg_nc", parse_capacitance),  # Stored in Coulombs

    # Diodes
    "Voltage - Forward(Vf@If)": ("vf_v", parse_voltage),
    "Voltage - DC Reverse(Vr)": ("vr_max_v", parse_voltage),
    "Current - Rectified": ("if_max_a", parse_current),

    # Voltage Regulators
    "Output Voltage": ("vout_v", parse_voltage),
    "Output Current": ("iout_max_a", parse_current),
    "Voltage Dropout": ("vdropout_v", parse_voltage),
    "Input Voltage": ("_vin_range", parse_vin_range),
    "Quiescent Current(Iq)": ("iq_ua", parse_current),
    "Quiescent Current": ("iq_ua", parse_current),

    # Frequency
    "Frequency": ("_freq_range", parse_freq_range),
    "Frequency Range": ("_freq_range", parse_freq_range),

    # ADC/DAC
    "Resolution(Bits)": ("resolution_bits", parse_integer),
    "Number of Bits": ("resolution_bits", parse_integer),
    "Sampling Rate": ("sample_rate_hz", parse_frequency),

    # Crystals
    "Load Capacitance": ("load_capacitance_pf", parse_capacitance),
    "Frequency Stability": ("freq_tolerance_ppm", parse_ppm),

    # Connectors
    "Number of Pins": ("num_pins", parse_integer),
    "Pitch": ("pitch_mm", parse_length_mm),
    "Number of Rows": ("num_rows", parse_integer),

    # Op-Amps
    "Gain Bandwidth Product": ("gbw_hz", parse_frequency),
    "Slew Rate": ("slew_rate_vus", parse_voltage),  # V/µs
    "Input Offset Voltage": ("vos_uv", parse_voltage),
    "Common Mode Rejection Ratio(CMRR)": ("cmrr_db", parse_decibels),

    # Capacitors (electrolytic)
    "Ripple Current": ("ripple_current_a", parse_current),
    "Equivalent Series Resistance(ESR)": ("esr_ohms", parse_resistance),
    "Lifetime": ("lifetime_hours", parse_integer),

    # RF
    "Noise Figure": ("noise_figure_db", parse_decibels),
    "Gain": ("gain_db", parse_decibels),

    # MCU / Microcontrollers
    "Flash": ("flash_size_bytes", parse_memory_size),
    "Program Memory Size": ("flash_size_bytes", parse_memory_size),
    "Program Storage Size": ("flash_size_bytes", parse_memory_size),
    "SRAM": ("ram_size_bytes", parse_memory_size),
    "RAM Size": ("ram_size_bytes", parse_memory_size),
    "Speed": ("clock_speed_hz", parse_frequency),
    "Max Frequency": ("clock_speed_hz", parse_frequency),
    "Operating Frequency": ("clock_speed_hz", parse_frequency),
    "CPU Maximum Speed": ("clock_speed_hz", parse_frequency),

    # Memory ICs
    "Capacity": ("memory_capacity_bits", parse_memory_size),
    "Memory Size": ("memory_capacity_bits", parse_memory_size),

    # Battery Chargers
    "Charging Current": ("charge_current_a", parse_current),
    "Fast Charge Current": ("charge_current_a", parse_current),
    "Charge Current": ("charge_current_a", parse_current),
    "Charge Current - Max": ("charge_current_a", parse_current),

    # TVS / ESD Protection
    "Clamping Voltage@Ipp": ("clamping_voltage_v", parse_voltage),
    "Clamping Voltage": ("clamping_voltage_v", parse_voltage),
    "Reverse Stand-off Voltage(Vrwm)": ("standoff_voltage_v", parse_voltage),
    "Reverse Stand-Off Voltage (Vrwm)": ("standoff_voltage_v", parse_voltage),
    "Breakdown Voltage": ("standoff_voltage_v", parse_voltage),
    "Peak Pulse Power(Ppk)": ("surge_power_w", parse_power),
    "Peak Pulse Power (Ppk)": ("surge_power_w", parse_power),
    "Peak Pulse Power Dissipation (Ppp)": ("surge_power_w", parse_power),

    # Temperature Range
    "Operating Temperature": ("_temp_range", parse_temp_range),
    "Operating Temperature Range": ("_temp_range", parse_temp_range),

    # LEDs
    "Dominant Wavelength": ("wavelength_nm", parse_wavelength),
    "Wavelength - Dominant": ("wavelength_nm", parse_wavelength),
    "Luminous Intensity": ("luminous_intensity_mcd", parse_luminosity),
    "Luminous Intensity (mcd)": ("luminous_intensity_mcd", parse_luminosity),
    "Forward Current(If)": ("forward_current_ma", parse_current),
    "Forward Current (If)": ("forward_current_ma", parse_current),
    "If - Forward Current": ("forward_current_ma", parse_current),

    # MOSFET additional
    "Input Capacitance(Ciss)": ("ciss_pf", parse_capacitance_pf),
    "Input Capacitance (Ciss)": ("ciss_pf", parse_capacitance_pf),
    "Ciss": ("ciss_pf", parse_capacitance_pf),

    # Power / Efficiency
    "Efficiency": ("efficiency_pct", parse_percentage),
}


def extract_numeric_columns(attributes: list) -> dict[str, Any]:
    """Extract numeric values from attributes list.

    Args:
        attributes: List of [name, value] pairs

    Returns:
        Dict of column_name -> parsed_value
    """
    result: dict[str, Any] = {}

    for attr in attributes:
        try:
            # Handle malformed attributes gracefully
            if not isinstance(attr, (list, tuple)) or len(attr) != 2:
                continue
            attr_name, attr_value = attr

            if attr_name not in ATTRIBUTE_TO_COLUMN:
                continue

            col_name, parser = ATTRIBUTE_TO_COLUMN[attr_name]

            # Handle special range columns
            if col_name == "_vgs_th_range":
                min_val, max_val = parser(attr_value)
                if min_val is not None:
                    result["vgs_th_min_v"] = min_val
                if max_val is not None:
                    result["vgs_th_max_v"] = max_val
            elif col_name == "_freq_range":
                min_val, max_val = parser(attr_value)
                if min_val is not None:
                    result["freq_min_hz"] = min_val
                if max_val is not None:
                    result["freq_max_hz"] = max_val
            elif col_name == "_vin_range":
                min_val, max_val = parser(attr_value)
                if min_val is not None:
                    result["vin_min_v"] = min_val
                if max_val is not None:
                    result["vin_max_v"] = max_val
            elif col_name == "_temp_range":
                min_val, max_val = parser(attr_value)
                if min_val is not None:
                    result["temp_min_c"] = min_val
                if max_val is not None:
                    result["temp_max_c"] = max_val
            else:
                # Regular column
                parsed = parser(attr_value)
                if parsed is not None:
                    result[col_name] = parsed
        except (ValueError, TypeError, AttributeError):
            # Skip malformed or unparseable attributes
            continue

    return result


# Numeric columns to add to schema (order matters for SQL)
NUMERIC_COLUMNS = [
    # Passives
    "resistance_ohms REAL",
    "capacitance_f REAL",
    "inductance_h REAL",
    "dcr_ohms REAL",
    "isat_a REAL",
    "voltage_max_v REAL",
    "current_max_a REAL",
    "tolerance_pct REAL",
    "power_w REAL",
    # MOSFETs
    "vds_max_v REAL",
    "vgs_th_min_v REAL",
    "vgs_th_max_v REAL",
    "id_max_a REAL",
    "rds_on_ohms REAL",
    "qg_nc REAL",
    # Diodes
    "vf_v REAL",
    "vr_max_v REAL",
    "if_max_a REAL",
    # Regulators
    "vout_v REAL",
    "iout_max_a REAL",
    "vdropout_v REAL",
    "vin_min_v REAL",
    "vin_max_v REAL",
    "iq_ua REAL",
    # Frequency
    "freq_min_hz REAL",
    "freq_max_hz REAL",
    # ADC/DAC
    "resolution_bits INTEGER",
    "sample_rate_hz REAL",
    # Crystals
    "load_capacitance_pf REAL",
    "freq_tolerance_ppm REAL",
    # Connectors
    "num_pins INTEGER",
    "pitch_mm REAL",
    "num_rows INTEGER",
    # Op-Amps
    "gbw_hz REAL",
    "slew_rate_vus REAL",
    "vos_uv REAL",
    "cmrr_db REAL",
    # Capacitors
    "ripple_current_a REAL",
    "esr_ohms REAL",
    "lifetime_hours REAL",
    # RF
    "noise_figure_db REAL",
    "gain_db REAL",
    # MCU / Microcontrollers
    "flash_size_bytes REAL",
    "ram_size_bytes REAL",
    "clock_speed_hz REAL",
    # Memory ICs
    "memory_capacity_bits REAL",
    # Battery Chargers
    "charge_current_a REAL",
    # TVS / ESD Protection
    "clamping_voltage_v REAL",
    "standoff_voltage_v REAL",
    "surge_power_w REAL",
    # Temperature Range
    "temp_min_c REAL",
    "temp_max_c REAL",
    # LEDs
    "wavelength_nm REAL",
    "luminous_intensity_mcd REAL",
    "forward_current_ma REAL",
    # MOSFET additional
    "ciss_pf REAL",
    # Power / Efficiency
    "efficiency_pct REAL",
]

# Column names only (for INSERT)
NUMERIC_COLUMN_NAMES = [col.split()[0] for col in NUMERIC_COLUMNS]


def build_database(data_dir: Path, db_path: Path, verbose: bool = True) -> dict:
    """
    Build SQLite database from compressed JSON files.

    Returns stats dict with counts and timing.
    """
    start_time = time.time()

    if verbose:
        print(f"Building database from {data_dir}")
        print(f"Output: {db_path}")

    # Remove existing database
    if db_path.exists():
        db_path.unlink()

    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    # Build CREATE TABLE with numeric columns
    numeric_cols_sql = ",\n            ".join(NUMERIC_COLUMNS)
    conn.execute(f"""
        CREATE TABLE components (
            lcsc TEXT PRIMARY KEY,
            mpn TEXT,
            manufacturer TEXT,
            package TEXT,
            stock INTEGER,
            library_type TEXT CHECK(library_type IN ('b', 'p', 'e')),
            subcategory_id INTEGER,
            price REAL,
            description TEXT,
            attributes TEXT,
            {numeric_cols_sql}
        )
    """)

    # Create subcategories table
    conn.execute("""
        CREATE TABLE subcategories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            category_name TEXT NOT NULL
        )
    """)

    # Create categories table (derived from subcategories)
    conn.execute("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT NOT NULL
        )
    """)

    # Load subcategories
    subcategories_file = data_dir / "subcategories.json"
    if subcategories_file.exists():
        with open(subcategories_file) as f:
            subcats = json.load(f)

        # Track unique categories
        categories_seen = {}

        for subcat_id, info in subcats.items():
            conn.execute(
                "INSERT INTO subcategories VALUES (?, ?, ?, ?)",
                (int(subcat_id), info["name"], info["category_id"], info["category_name"])
            )

            # Track category
            cat_id = info["category_id"]
            if cat_id not in categories_seen:
                categories_seen[cat_id] = info["category_name"]

        if verbose:
            print(f"Loaded {len(subcats)} subcategories")

    # Load manifest for category slugs
    manifest_file = data_dir / "manifest.json"
    if manifest_file.exists():
        with open(manifest_file) as f:
            manifest = json.load(f)

        for slug, cat_info in manifest.get("categories", {}).items():
            conn.execute(
                "INSERT OR REPLACE INTO categories VALUES (?, ?, ?)",
                (cat_info["id"], cat_info["name"], slug)
            )

    # Load all category files
    categories_dir = data_dir / "categories"
    total_parts = 0
    category_counts = {}
    BATCH_SIZE = 1000  # Insert in batches for better performance

    for gz_file in sorted(categories_dir.glob("*.jsonl.gz")):
        cat_slug = gz_file.stem.replace(".jsonl", "")
        count = 0
        batch = []

        # Build column names for INSERT
        base_cols = ["lcsc", "mpn", "manufacturer", "package", "stock", "library_type",
                     "subcategory_id", "price", "description", "attributes"]
        all_cols = base_cols + NUMERIC_COLUMN_NAMES
        placeholders = ", ".join(["?"] * len(all_cols))
        insert_sql = f"INSERT INTO components ({', '.join(all_cols)}) VALUES ({placeholders})"

        with gzip.open(gz_file, "rt") as f:
            for line in f:
                if not line.strip():
                    continue

                part = json.loads(line)
                attrs = part.get("a", [])

                # Extract numeric values from attributes
                numeric_values = extract_numeric_columns(attrs)

                # Build row tuple
                row = [
                    part["l"],
                    part.get("m"),
                    part.get("f"),
                    part.get("p"),
                    part.get("s"),
                    part.get("t"),
                    part.get("c"),
                    part.get("$"),
                    part.get("d"),
                    json.dumps(attrs),
                ]
                # Add numeric column values (None if not parsed)
                for col_name in NUMERIC_COLUMN_NAMES:
                    row.append(numeric_values.get(col_name))

                batch.append(tuple(row))
                count += 1

                # Insert batch when full
                if len(batch) >= BATCH_SIZE:
                    conn.executemany(insert_sql, batch)
                    batch = []

        # Insert remaining parts
        if batch:
            conn.executemany(insert_sql, batch)

        category_counts[cat_slug] = count
        total_parts += count

        if verbose and count > 0:
            print(f"  {cat_slug}: {count:,} parts")

    if verbose:
        print(f"Total parts loaded: {total_parts:,}")
        print("Creating indexes...")

    # Create indexes for common queries
    conn.execute("CREATE INDEX idx_subcategory ON components(subcategory_id)")
    conn.execute("CREATE INDEX idx_stock ON components(stock)")
    conn.execute("CREATE INDEX idx_library_type ON components(library_type)")
    conn.execute("CREATE INDEX idx_package ON components(package)")
    conn.execute("CREATE INDEX idx_manufacturer ON components(manufacturer)")
    conn.execute("CREATE INDEX idx_price ON components(price)")

    # Composite indexes for common filter combinations
    conn.execute("CREATE INDEX idx_subcat_stock ON components(subcategory_id, stock)")
    conn.execute("CREATE INDEX idx_subcat_libtype ON components(subcategory_id, library_type)")

    # Indexes for numeric columns (partial indexes for non-NULL values)
    if verbose:
        print("Creating numeric column indexes...")
    conn.execute("CREATE INDEX idx_resistance ON components(resistance_ohms) WHERE resistance_ohms IS NOT NULL")
    conn.execute("CREATE INDEX idx_capacitance ON components(capacitance_f) WHERE capacitance_f IS NOT NULL")
    conn.execute("CREATE INDEX idx_inductance ON components(inductance_h) WHERE inductance_h IS NOT NULL")
    conn.execute("CREATE INDEX idx_voltage_max ON components(voltage_max_v) WHERE voltage_max_v IS NOT NULL")
    conn.execute("CREATE INDEX idx_current_max ON components(current_max_a) WHERE current_max_a IS NOT NULL")
    conn.execute("CREATE INDEX idx_vds ON components(vds_max_v) WHERE vds_max_v IS NOT NULL")
    conn.execute("CREATE INDEX idx_rds_on ON components(rds_on_ohms) WHERE rds_on_ohms IS NOT NULL")
    conn.execute("CREATE INDEX idx_freq_max ON components(freq_max_hz) WHERE freq_max_hz IS NOT NULL")
    conn.execute("CREATE INDEX idx_resolution ON components(resolution_bits) WHERE resolution_bits IS NOT NULL")
    conn.execute("CREATE INDEX idx_num_pins ON components(num_pins) WHERE num_pins IS NOT NULL")
    conn.execute("CREATE INDEX idx_vout ON components(vout_v) WHERE vout_v IS NOT NULL")
    conn.execute("CREATE INDEX idx_iq ON components(iq_ua) WHERE iq_ua IS NOT NULL")
    # MCU indexes
    conn.execute("CREATE INDEX idx_flash ON components(flash_size_bytes) WHERE flash_size_bytes IS NOT NULL")
    conn.execute("CREATE INDEX idx_ram ON components(ram_size_bytes) WHERE ram_size_bytes IS NOT NULL")
    conn.execute("CREATE INDEX idx_clock ON components(clock_speed_hz) WHERE clock_speed_hz IS NOT NULL")
    # Memory IC index
    conn.execute("CREATE INDEX idx_memory ON components(memory_capacity_bits) WHERE memory_capacity_bits IS NOT NULL")
    # TVS/ESD indexes
    conn.execute("CREATE INDEX idx_clamping ON components(clamping_voltage_v) WHERE clamping_voltage_v IS NOT NULL")
    conn.execute("CREATE INDEX idx_standoff ON components(standoff_voltage_v) WHERE standoff_voltage_v IS NOT NULL")
    # Battery charger index
    conn.execute("CREATE INDEX idx_charge_current ON components(charge_current_a) WHERE charge_current_a IS NOT NULL")
    # Temperature range indexes
    conn.execute("CREATE INDEX idx_temp_min ON components(temp_min_c) WHERE temp_min_c IS NOT NULL")
    conn.execute("CREATE INDEX idx_temp_max ON components(temp_max_c) WHERE temp_max_c IS NOT NULL")

    if verbose:
        print("Creating FTS5 full-text search index...")

    # Create FTS5 index for text search
    # Store content directly for reliable searching
    conn.execute("""
        CREATE VIRTUAL TABLE components_fts USING fts5(
            lcsc,
            mpn,
            manufacturer,
            description
        )
    """)

    # Populate FTS index directly from components table
    conn.execute("""
        INSERT INTO components_fts(lcsc, mpn, manufacturer, description)
        SELECT lcsc, mpn, manufacturer, description FROM components
    """)

    if verbose:
        print("Optimizing database...")

    # Commit all changes first
    conn.commit()

    # Analyze for query optimization
    conn.execute("ANALYZE")

    # Vacuum to reclaim space and optimize (must be outside transaction)
    conn.execute("VACUUM")

    # Get final stats
    cursor = conn.execute("SELECT COUNT(*) FROM components")
    final_count = cursor.fetchone()[0]

    cursor = conn.execute("SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()")
    db_size = cursor.fetchone()[0]

    conn.close()

    elapsed = time.time() - start_time

    stats = {
        "total_parts": final_count,
        "categories": len(category_counts),
        "category_counts": category_counts,
        "db_size_bytes": db_size,
        "db_size_mb": round(db_size / (1024 * 1024), 2),
        "build_time_seconds": round(elapsed, 2),
    }

    if verbose:
        print()
        print("=" * 50)
        print("DATABASE BUILD COMPLETE")
        print("=" * 50)
        print(f"Parts: {final_count:,}")
        print(f"Categories: {len(category_counts)}")
        print(f"Database size: {stats['db_size_mb']} MB")
        print(f"Build time: {elapsed:.1f} seconds")
        print(f"Output: {db_path}")

    return stats


def main():
    parser = argparse.ArgumentParser(description="Build component database")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Data directory with scraped files (default: data/)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("data/components.db"),
        help="Output database path (default: data/components.db)",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress output",
    )
    args = parser.parse_args()

    if not args.data_dir.exists():
        print(f"Error: Data directory not found: {args.data_dir}")
        return 1

    categories_dir = args.data_dir / "categories"
    if not categories_dir.exists():
        print(f"Error: Categories directory not found: {categories_dir}")
        return 1

    build_database(args.data_dir, args.output, verbose=not args.quiet)
    return 0


if __name__ == "__main__":
    exit(main())
