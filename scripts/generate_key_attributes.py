#!/usr/bin/env python3
"""Generate key_attributes.py from key-attributes-v3.md.

Usage:
    python scripts/generate_key_attributes.py

This parses the markdown file and generates the Python module with
the KEY_ATTRIBUTES dictionary mapping subcategory names to their
essential attributes for search results.
"""

import re
from pathlib import Path


def parse_markdown(content: str) -> dict[str, list[str]]:
    """Parse key-attributes-v3.md and extract subcategory -> attributes mapping."""
    data = {}

    # Find all subcategory entries: ### Name followed by **Key Count: N** | attrs
    pattern = r"### ([^\n]+)\n\*\*Key Count: (\d+)\*\* \| ([^\n]+)"
    matches = re.findall(pattern, content)

    for subcategory, count, attrs in matches:
        subcategory = subcategory.strip()
        count = int(count)

        if count == 0 or attrs.strip() == "(no attributes)":
            data[subcategory] = []
        else:
            # Split by comma and strip
            attr_list = [a.strip() for a in attrs.split(",")]
            data[subcategory] = attr_list

    return data


def generate_python(data: dict[str, list[str]]) -> str:
    """Generate Python module content."""
    lines = [
        '"""Key attributes mapping for each component subcategory.',
        "",
        "Maps subcategory names to the essential attributes that engineers need",
        "for component selection. Used to reduce token usage in search results.",
        '"""',
        "",
        "# Auto-generated from key-attributes-v3.md",
        "# Regenerate with: python scripts/generate_key_attributes.py",
        "",
        "KEY_ATTRIBUTES: dict[str, list[str]] = {",
    ]

    for subcategory, attrs in sorted(data.items()):
        if attrs:
            attrs_str = ", ".join(f'"{a}"' for a in attrs)
            lines.append(f'    "{subcategory}": [{attrs_str}],')
        else:
            lines.append(f'    "{subcategory}": [],')

    lines.append("}")
    lines.append("")

    return "\n".join(lines)


def main():
    # Find project root (parent of scripts/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Read markdown source
    md_path = project_root / "key-attributes-v3.md"
    if not md_path.exists():
        print(f"Error: {md_path} not found")
        return 1

    content = md_path.read_text()

    # Parse and generate
    data = parse_markdown(content)
    print(f"Parsed {len(data)} subcategories from {md_path.name}")

    python_content = generate_python(data)

    # Write output
    output_path = project_root / "src" / "jlcpcb_mcp" / "key_attributes.py"
    output_path.write_text(python_content)
    print(f"Generated {output_path}")

    return 0


if __name__ == "__main__":
    exit(main())
