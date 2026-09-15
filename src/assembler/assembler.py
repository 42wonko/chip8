"""
@file assembler.py

@brief Assembler entry point.
"""

from __future__ import annotations

from typing import cast

from assembler.ast import AssemblyNode
from assembler.codegen import CodeGenerator, InstructionEncoder
from assembler.lexer import Lexer
from assembler.listing import ListingGenerator
from assembler.options import AssemblyOptions
from assembler.parser import Parser
from assembler.result import AssemblyResult
from assembler.semantic import (
    InstructionResolver,
    SemanticAnalysisError,
    SymbolCollector,
    SymbolReferenceCollector,
)
from assembler.symbol import SymbolTable
from assembler.target import Target

#from assembler.target_selector import TargetSelector
from chip8.isa.isa import InstructionSetArchitecture
from controller.diagnostics import AssemblerDiagnosticsReporter


class Assembler:
    """
    @brief Entry point for the assembler.
    """

    def __init__( self, diagnostics: AssemblerDiagnosticsReporter, isa: InstructionSetArchitecture) -> None:
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
            self._diagnostics.info("Started assembly.")
#            TargetSelector().select(source, target)
            self._diagnostics.info("Parsing source.")
            assembly = self._parse(source)
            if not assembly.lines:
                self._diagnostics.error("Assembly source is empty.")
                return AssemblyResult(success=False)
            symbols = SymbolTable()
            SymbolCollector(symbols, self._isa).collect(assembly)
            reference_collector = SymbolReferenceCollector(symbols)
            reference_collector.collect(assembly)
            resolver = InstructionResolver(symbols, self._isa)
            generator = CodeGenerator(symbols, resolver,cast(InstructionEncoder, self._isa), reference_collector)
            self._diagnostics.info("Generating binary image.")
            binary_image = generator.generate(assembly)
            listing = None
            if options.generate_listing:
                self._diagnostics.info("Generating listing.")
                if options.generate_cross_reference:
                    self._diagnostics.info("Creating cross-reference.")
                listing = ListingGenerator().generate(
                    source,
                    generator.records,
                    symbols,
                    reference_collector.references(),
                    options.generate_cross_reference
                )
            self._diagnostics.info("Assembly complete.")
            return AssemblyResult( success=True, binary_image=binary_image, listing=listing)
        except SemanticAnalysisError as error:
            self._diagnostics.error(str(error), error.location)
            return AssemblyResult(success=False)
        except (ValueError, TypeError) as error:
            self._diagnostics.error(str(error))
            return AssemblyResult(success=False)


    @staticmethod
    def _parse(source: str) -> AssemblyNode:
        """
        @brief Lex and parse assembler source.
        """
        tokens = Lexer(source).tokenize()
        return Parser(tokens).parse()


