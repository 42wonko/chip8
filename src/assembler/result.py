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

    Diagnostics are included in the result so that structured assembly
    errors, including their source locations, are available to the caller.
    This is separate from AssemblerDiagnostics, which is used to report
    assembly progress and diagnostics to the assembler dialog.

    Source locations in the result are also intended to support future
    source navigation by the controller.

    Output products are optional because listing and cross-reference
    generation can be disabled through AssemblyOptions.
    """

    success: bool
    diagnostics: tuple[Diagnostic, ...] = ()
    binary_image: bytes | None = None
    listing: str | None = None
#    cross_reference: str | None = None

