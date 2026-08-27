"""
@file options.py

@brief Configuration options for the assembler.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AssemblyOptions:
    """
    @brief Options controlling assembler output.

    @details
    Binary ROM generation is enabled by default. Listing and
    cross-reference generation are optional.
    """

    generate_listing: bool = False
    generate_cross_reference: bool = False

