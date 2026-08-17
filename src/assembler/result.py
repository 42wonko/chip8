"""
@file result.py

@brief Result of an assembler operation.
"""

from __future__ import annotations

from dataclasses import dataclass

from controller.diagnostic import Diagnostic


@dataclass(slots=True)
class AssemblyResult:
    """
    @brief Result produced by the assembler.

    @details
    The result contains the status of the assembly operation, any
    diagnostics generated during assembly, and the requested output
    products.

    Output products are optional because listing and cross-reference
    generation can be disabled through AssemblyOptions.
    """

    success: bool
    diagnostics: tuple[Diagnostic, ...] = ()
    binary_image: bytes | None = None
    listing: str | None = None
    cross_reference: str | None = None

