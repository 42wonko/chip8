"""
@file assembler.py

@brief Assembler entry point.
"""

from __future__ import annotations

from assembler.options import AssemblyOptions
from assembler.result import AssemblyResult
from assembler.target import Target
from controller.diagnostics import DiagnosticReporter


class Assembler:
    """
    @brief Entry point for the assembler.

    @details
    The assembler provides the public interface to the assembly
    pipeline. Parsing, semantic analysis and code generation are
    introduced in later development phases.
    """

    def __init__(self, diagnostics: DiagnosticReporter) -> None:
        """
        @brief Construct an assembler.

        @param diagnostics
            Diagnostic reporter configured for the assembler subsystem.
        """
        self._diagnostics = diagnostics


    def assemble( self, source: str, target: Target, options: AssemblyOptions | None = None,) -> AssemblyResult:
        """
        @brief Assemble source code.

        @param source
            Assembly source text.

        @param target
            Target architecture.

        @param options
            Assembly output options. Default options are used when None.

        @return
            Assembly result.
        """
        del source
        del target
        if options is None:
            options = AssemblyOptions()
        del options
        self._diagnostics.info( "Assembler implementation is not yet available.")
        return AssemblyResult( success=False,)
