"""Smart parser package for natural language component searches.

This package provides intelligent parsing of queries like:
- "TP4056 lithium battery charger" -> searches for TP4056 model
- "100V mosfet" -> subcategory=MOSFETs, Vds>=100V
- "10uH inductor 2A" -> subcategory=Inductors, L=10uH, Current Rating>=2A
- "schottky diode SOD-123 1A" -> subcategory=Schottky, package=SOD-123, If>=1A
- "n-channel mosfet low Vgs" -> subcategory=MOSFETs, Type=N-Channel, Vgs(th)<2.5V

Key features:
1. Token classification (model numbers, values, packages, types, descriptors)
2. Category-aware attribute mapping (voltage->Vds for MOSFETs, ->Vr for diodes)
3. Semantic descriptor interpretation ("low Vgs", "logic level", "bidirectional")
4. Smart FTS fallback (only search model numbers when structured filters exist)
"""

from .parser import ParsedQuery, parse_smart_query
from .packages import PACKAGE_PATTERNS, extract_package
from .values import ExtractedValue, extract_values
from .models import MODEL_PATTERNS, extract_model_number
from .types import extract_component_type, extract_mounting_type
from .semantic import SemanticFilter, SEMANTIC_DESCRIPTORS, extract_semantic_descriptors, NOISE_WORDS, remove_noise_words
from .mapping import CATEGORY_ATTRIBUTE_MAP, map_value_to_spec, infer_subcategory_from_values

__all__ = [
    # Main API
    "parse_smart_query",
    "ParsedQuery",
    # Data classes
    "ExtractedValue",
    "SemanticFilter",
    # Pattern constants
    "PACKAGE_PATTERNS",
    "MODEL_PATTERNS",
    "SEMANTIC_DESCRIPTORS",
    "CATEGORY_ATTRIBUTE_MAP",
    "NOISE_WORDS",
    # Extraction functions
    "extract_package",
    "extract_values",
    "extract_model_number",
    "extract_component_type",
    "extract_mounting_type",
    "extract_semantic_descriptors",
    "remove_noise_words",
    "map_value_to_spec",
    "infer_subcategory_from_values",
]
