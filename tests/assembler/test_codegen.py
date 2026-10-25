"""
@file test_codegen.py

@brief Tests for assembler binary code generation.
"""

import unittest
from unittest.mock import Mock


from assembler.ast import AssemblyNode, DirectiveNode, InstructionNode, LiteralExpression, SourceLine
from assembler.codegen import CodeGenerator
from assembler.semantic import SemanticAnalysisError
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
        self.generator = CodeGenerator( self.symbols, FakeInstructionResolver(), FakeInstructionEncoder(), 0xFFFF)

    def test_generate_collects_instruction_references(self) -> None:
        instruction = InstructionNode( mnemonic="CLS", operands=(), location=self.location)
        assembly = AssemblyNode( lines=( SourceLine(label=None, statement=instruction),))
        resolved_instruction = Mock()
        references = (Mock(),)
        resolver = Mock()
        resolver.resolve.return_value = resolved_instruction
        resolver.instruction_references.return_value = references
        encoder = Mock()
        encoder.instruction_size.return_value = 2
        encoder.encode.return_value = 0x00E0
        collector = Mock()
        generator = CodeGenerator( self.symbols, resolver, encoder, 0xFFFF, collector)
        result = generator.generate(assembly)
        self.assertEqual(result, b"\x00\xE0")
        resolver.instruction_references.assert_called_once_with( resolved_instruction)
        collector.add_instruction_references.assert_called_once_with(
            resolved_instruction,
            self.location,
            references
        )

    def test_instruction_generation_without_reference_collector(self) -> None:
        instruction = InstructionNode( mnemonic="CLS", operands=(), location=self.location)
        assembly = AssemblyNode( lines=( SourceLine(label=None, statement=instruction),))
        resolver = Mock()
        resolved_instruction = Mock()
        resolver.resolve.return_value = resolved_instruction
        encoder = Mock()
        encoder.instruction_size.return_value = 2
        encoder.encode.return_value = 0x00E0
        generator = CodeGenerator( self.symbols, resolver, encoder, 0xFFFF)
        result = generator.generate(assembly)
        self.assertEqual(result, b"\x00\xE0")
        resolver.resolve.assert_called_once_with(instruction)
        resolver.instruction_references.assert_not_called()

    def test_generate_rejects_unsupported_directive(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="UNKNOWN",
                        operands=(),
                        location=self.location
                    )
                ),
            )
        )
        with self.assertRaisesRegex( ValueError, "Unsupported directive 'UNKNOWN'."):
            self.generator.generate(assembly)

    def test_generate_rejects_unsupported_statement_type(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=object()
                ),
            )
        )
        with self.assertRaisesRegex( ValueError, "Unsupported statement type: object"):
            self.generator.generate(assembly)

    def test_db_string_exceeding_address_limit_raises_error(self) -> None:
        generator = CodeGenerator( self.symbols, FakeInstructionResolver(), FakeInstructionEncoder(), 0x200)
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="DB",
                        operands=(
                            LiteralExpression(
                                value="AB",
                                location=self.location
                            ),
                        ),
                        location=self.location
                    )
                ),
            )
        )
        with self.assertRaisesRegex( Exception, "DB data exceeds the assembler address space."):
            generator.generate(assembly)


    def test_resolver_value_error_is_converted_to_semantic_error(self) -> None:
        resolver = Mock()
        resolver.resolve.side_effect = ValueError("Invalid instruction")
        generator = CodeGenerator( self.symbols, resolver, FakeInstructionEncoder(), 0xFFFF)
        instruction = InstructionNode( mnemonic="INVALID", operands=(), location=self.location)
        assembly = AssemblyNode( lines=( SourceLine(label=None, statement=instruction),))
        with self.assertRaisesRegex( SemanticAnalysisError, "Invalid instruction"):
            generator.generate(assembly)

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


    def test_dw_emits_word_in_big_endian_order(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="DW",
                        operands=(LiteralExpression(value=0x1234, location=self.location),),
                        location=self.location,
                    ),
                ),
            )
        )
        self.assertEqual(self.generator.generate(assembly), b"\x12\x34")
        self.assertEqual(self.generator.records[0].address, 0x200)
        self.assertEqual(self.generator.records[0].data, b"\x12\x34")

    def test_dw_emits_multiple_words(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="DW",
                        operands=(
                            LiteralExpression(value=0x1234, location=self.location),
                            LiteralExpression(value=0xABCD, location=self.location),
                        ),
                        location=self.location,
                    ),
                ),
            )
        )
        self.assertEqual(self.generator.generate(assembly), b"\x12\x34\xAB\xCD")


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


    def test_multiple_org_directives_use_lowest_address_as_image_base(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="ORG",
                        operands=(
                            LiteralExpression(value=0x300, location=self.location),
                        ),
                        location=self.location
                    )
                ),
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="DB",
                        operands=(
                            LiteralExpression(value=0x01, location=self.location),
                        ),
                        location=self.location
                    )
                ),
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="ORG",
                        operands=(
                            LiteralExpression(value=0x200, location=self.location),
                        ),
                        location=self.location
                    )
                ),
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="DB",
                        operands=(
                            LiteralExpression(value=0x02, location=self.location),
                        ),
                        location=self.location
                    )
                ),
            )
        )

        result = self.generator.generate(assembly)

        self.assertEqual(result[0], 0x02)
        self.assertEqual(result[0x100], 0x01)
        self.assertEqual(len(result), 0x101)


    def test_multiple_org_directives_use_minimum_org_address(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="ORG",
                        operands=(
                            LiteralExpression(value=0x300, location=self.location),
                        ),
                        location=self.location
                    )
                ),
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="DB",
                        operands=(
                            LiteralExpression(value=0x03, location=self.location),
                        ),
                        location=self.location
                    )
                ),
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="ORG",
                        operands=(
                            LiteralExpression(value=0x280, location=self.location),
                        ),
                        location=self.location
                    )
                ),
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="DB",
                        operands=(
                            LiteralExpression(value=0x02, location=self.location),
                        ),
                        location=self.location
                    )
                ),
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="ORG",
                        operands=(
                            LiteralExpression(value=0x200, location=self.location),
                        ),
                        location=self.location
                    )
                ),
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="DB",
                        operands=(
                            LiteralExpression(value=0x01, location=self.location),
                        ),
                        location=self.location
                    )
                ),
            )
        )

        result = self.generator.generate(assembly)

        self.assertEqual(result[0], 0x01)
        self.assertEqual(result[0x80], 0x02)
        self.assertEqual(result[0x100], 0x03)
        self.assertEqual(len(result), 0x101)


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


