"""
@file test_codegen.py

@brief Tests for assembler binary code generation.
"""

import unittest

from assembler.ast import AssemblyNode, DirectiveNode, LiteralExpression, SourceLine
from assembler.codegen import CodeGenerator
from assembler.symbol import SymbolTable
from assembler.token import SourceLocation


class FakeInstructionResolver:
    """
    @brief Minimal instruction resolver for DB tests.
    """

    def resolve(self, instruction):
        raise NotImplementedError


class FakeInstructionEncoder:
    """
    @brief Minimal instruction encoder for DB tests.
    """
    def encode(self, instruction):
        raise NotImplementedError


class CodeGeneratorTest(unittest.TestCase):
    """
    @brief Tests for CodeGenerator.
    """
    def setUp(self) -> None:
        self.location = SourceLocation(line=1, column=1)
        self.symbols = SymbolTable()
        self.generator = CodeGenerator( self.symbols, FakeInstructionResolver(), FakeInstructionEncoder())


    def test_db_emits_byte(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine( label=None, statement=DirectiveNode( name="DB", operands=( LiteralExpression( value=0x42, location=self.location),), location=self.location)),
            )
        )
        self.assertEqual( self.generator.generate(assembly), b"\x42")


    def test_db_emits_multiple_bytes(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="DB",
                        operands=(
                            LiteralExpression( value=0x12, location=self.location),
                            LiteralExpression( value=0x34, location=self.location),
                            LiteralExpression( value=0x56, location=self.location),
                        ),
                        location=self.location
                    )
                ),
            )
        )
        self.assertEqual( self.generator.generate(assembly), b"\x12\x34\x56")


    def test_db_emits_string(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode( name="DB", operands=( LiteralExpression( value="Hello", location=self.location),), location=self.location)
                ),
            )
        )
        self.assertEqual( self.generator.generate(assembly), b"Hello")


    def test_org_defines_image_base(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="ORG",
                        operands=( LiteralExpression( value=0x300, location=self.location),),
                        location=self.location
                    )
                ),
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="DB",
                        operands=( LiteralExpression( value=0x42, location=self.location),),
                        location=self.location
                    )
                ),
            )
        )
        self.assertEqual( self.generator.generate(assembly), b"\x42")


    def test_org_fills_gap_with_zeroes(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="ORG",
                        operands=( LiteralExpression( value=0x300, location=self.location),),
                        location=self.location
                    )
                ),
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="DB",
                        operands=( LiteralExpression( value=0x01, location=self.location),),
                        location=self.location
                    )
                ),
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="ORG",
                        operands=( LiteralExpression( value=0x305, location=self.location),),
                        location=self.location
                    )
                ),
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="DB",
                        operands=( LiteralExpression( value=0x02, location=self.location),),
                        location=self.location
                    )
                ),
            )
        )
        self.assertEqual( self.generator.generate(assembly), b"\x01\x00\x00\x00\x00\x02")


    def test_no_org_starts_at_program_start(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="DB",
                        operands=( LiteralExpression( value=0x42, location=self.location),),
                        location=self.location
                    )
                ),
            )
        )
        self.assertEqual( self.generator.generate(assembly), b"\x42")


    def test_equ_does_not_emit_bytes(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="EQU",
                        operands=( LiteralExpression( value=0x42, location=self.location),),
                        location=self.location
                    )
                ),
            )
        )
        self.assertEqual( self.generator.generate(assembly), b"")


    def test_target_does_not_emit_bytes(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="TARGET",
                        operands=( LiteralExpression( value="COSMAC", location=self.location),),
                        location=self.location
                    )
                ),
            )
        )
        self.assertEqual( self.generator.generate(assembly), b"")


