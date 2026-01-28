"""Search package for parametric component queries.

This package provides the search engine and related utilities for
querying components with parametric filtering.
"""

from .engine import SearchEngine
from .spec_filter import SpecFilter, SPEC_TO_COLUMN, ATTRIBUTE_ALIASES, get_attribute_names, escape_like
from .resolvers import (
    expand_query_synonyms,
    expand_package,
    resolve_manufacturer,
    PACKAGE_FAMILIES,
    IMPERIAL_CHIP_SIZES,
    SMD_PACKAGE_FAMILIES,
)
from .result import row_to_dict

__all__ = [
    "SearchEngine",
    "SpecFilter",
    "SPEC_TO_COLUMN",
    "ATTRIBUTE_ALIASES",
    "get_attribute_names",
    "escape_like",
    "expand_query_synonyms",
    "expand_package",
    "resolve_manufacturer",
    "PACKAGE_FAMILIES",
    "IMPERIAL_CHIP_SIZES",
    "SMD_PACKAGE_FAMILIES",
    "row_to_dict",
]
