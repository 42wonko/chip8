"""
@file assembler.py

@brief Assembler entry point.
"""

from __future__ import annotations

from assembler.ast import AssemblyNode
from assembler.codegen import CodeGenerator
from assembler.lexer import Lexer
from assembler.listing import ListingGenerator
from assembler.options import AssemblyOptions
from assembler.parser import Parser
from assembler.result import AssemblyResult
from assembler.semantic import (
    InstructionResolver,
    SymbolCollector,
    SymbolReferenceCollector,
)
from assembler.symbol import SymbolTable
from assembler.target import Target
from assembler.target_selector import TargetSelector
from chip8.isa.isa import InstructionSetArchitecture
from controller.diagnostics import DiagnosticReporter


class Assembler:
    """
    @brief Entry point for the assembler.
    """

    def __init__( self, diagnostics: DiagnosticReporter, isa: InstructionSetArchitecture) -> None:
        """
        @brief Construct an assembler.

        @param diagnostics
            Diagnostic reporter configured for the assembler subsystem.

        @param isa
            Instruction-set architecture supplied by the controller.
        """
        self._diagnostics = diagnostics
        self._isa = isa


    def assemble( self, source: str, target: Target | None, options: AssemblyOptions | None = None) -> AssemblyResult:
        """
        @brief Assemble source code.

        @param source
            Assembly source text.

        @param target
            Target architecture selected externally, or None.

        @param options
            Assembly output options.

        @return
            Assembly result.
        """
        if options is None:
            options = AssemblyOptions()
        try:
            assembly = self._parse(source)
            if not assembly.lines:
                self._diagnostics.error("Assembly source is empty.")
                return AssemblyResult(success=False)
            TargetSelector().select(source, target)
            symbols = SymbolTable()
            SymbolCollector(symbols).collect(assembly)
            SymbolReferenceCollector(symbols).collect(assembly)
            resolver = InstructionResolver( symbols, self._isa)
            generator = CodeGenerator( symbols, resolver, self._isa)
            binary_image = generator.generate(assembly)
            listing = None
            if options.generate_listing:
                listing = ListingGenerator().generate( source, generator.records)
            return AssemblyResult( success=True, binary_image=binary_image, listing=listing)
        except (ValueError, TypeError) as error:
            self._diagnostics.error(str(error))
            return AssemblyResult( success=False)


    @staticmethod
    def _parse(source: str) -> AssemblyNode:
        """
        @brief Lex and parse assembler source.
        """
        tokens = Lexer(source).tokenize()
        return Parser(tokens).parse()
