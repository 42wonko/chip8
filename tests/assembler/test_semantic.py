"""
@file test_semantic.py

@brief Tests for assembler semantic expression evaluation.
"""

import unittest

from assembler.ast import (
    AssemblyNode,
    BinaryExpression,
    BinaryOperator,
    DirectiveNode,
    IdentifierExpression,
    IndirectExpression,
    InstructionNode,
    LabelNode,
    LiteralExpression,
    SourceLine,
)
from assembler.operand import AssemblerOperandType
from assembler.semantic import (
    ExpressionEvaluationError,
    ExpressionEvaluator,
    InstructionResolver,
    OperandResolver,
    SemanticAnalysisError,
    SymbolCollector,
    SymbolReferenceCollector,
)
from assembler.symbol import SymbolTable
from assembler.token import SourceLocation
from chip8.isa.classicisa import ClassicInstructionSetArchitecture
from chip8.isa.instructionid import InstructionId
from emulator.constants import PROGRAM_START

#from tests.helpers import create_machine


class SymbolReferenceCollectorTest(unittest.TestCase):
    """
    @brief Tests for SymbolReferenceCollector.
    """

    def setUp(self) -> None:
        self.location = SourceLocation( line=1, column=1)


    def test_collects_instruction_symbol_reference(self) -> None:
        symbols = SymbolTable()
        symbols.define( "START", 0x300, SourceLocation( line=1, column=1))
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=InstructionNode(
                        mnemonic="JP",
                        operands=(
                            IdentifierExpression(
                                name="START",
                                location=SourceLocation( line=4, column=4)
                            ),
                        ),
                        location=self.location
                    )
                ),
            )
        )
        SymbolReferenceCollector(symbols).collect(assembly)
        self.assertEqual( symbols.references("START"), ( SourceLocation( line=4, column=4),))

    def test_collects_symbol_references_from_directives(self) -> None:
        """
        @brief Verify that directive expressions contribute symbol references.
        """
        symbols = SymbolTable()
        symbols.define(
            "BASE",
            0x300,
            SourceLocation(line=1, column=1),
        )
        symbols.define(
            "VALUE",
            0x42,
            SourceLocation(line=2, column=1),
        )
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=LabelNode( name="OFFSET", location=SourceLocation(line=3, column=1),),
                    statement=DirectiveNode(
                        name="EQU",
                        operands=( IdentifierExpression( name="BASE", location=SourceLocation(line=3, column=10),),
                        ),
                        location=SourceLocation(line=3, column=8),
                    ),
                ),
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="ORG",
                        operands=(
                            IdentifierExpression( name="BASE", location=SourceLocation(line=4, column=5),),
                        ),
                        location=SourceLocation(line=4, column=1),
                    ),
                ),
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="DB",
                        operands=(
                            IdentifierExpression( name="VALUE", location=SourceLocation(line=5, column=4),),
                        ),
                        location=SourceLocation(line=5, column=1),
                    ),
                ),
            )
        )
        SymbolReferenceCollector(symbols).collect(assembly)
        self.assertEqual( symbols.references("BASE"), ( SourceLocation(line=3, column=10), SourceLocation(line=4, column=5),),)
        self.assertEqual( symbols.references("VALUE"), (SourceLocation(line=5, column=4),),)


    def test_target_directive_does_not_create_symbol_reference(self) -> None:
        """
        @brief Verify that TARGET is metadata and has no symbol references.
        """
        symbols = SymbolTable()
        symbols.define( "COSMAC", 0x200, SourceLocation(line=1, column=1),)
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="TARGET",
                        operands=(
                            IdentifierExpression( name="COSMAC", location=SourceLocation(line=1, column=8),),
                        ),
                        location=SourceLocation(line=1, column=1),
                    ),
                ),
            )
        )
        SymbolReferenceCollector(symbols).collect(assembly)
        self.assertEqual(symbols.references("COSMAC"), ())


    def test_collects_symbol_references_from_binary_expression(self) -> None:
        """
        @brief Verify that all symbols in a binary expression are referenced.
        """
        symbols = SymbolTable()
        symbols.define(
            "BASE",
            0x300,
            SourceLocation(line=1, column=1)
        )
        symbols.define(
            "OFFSET",
            0x20,
            SourceLocation(line=2, column=1)
        )
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="ORG",
                        operands=(
                            BinaryExpression(
                                operator=BinaryOperator.ADD,
                                left=IdentifierExpression( name="BASE", location=SourceLocation(line=4, column=5)),
                                right=IdentifierExpression( name="OFFSET", location=SourceLocation(line=4, column=12)),
                                location=SourceLocation(line=4, column=9)
                            ),
                        ),
                        location=SourceLocation(line=4, column=1)
                    )
                ),
            )
        )
        SymbolReferenceCollector(symbols).collect(assembly)
        self.assertEqual( symbols.references("BASE"), (SourceLocation(line=4, column=5),))
        self.assertEqual( symbols.references("OFFSET"), (SourceLocation(line=4, column=12),))


class ExpressionEvaluatorTest(unittest.TestCase):
    """
    @brief Tests for ExpressionEvaluator.
    """

    def setUp(self) -> None:
        self.location = SourceLocation( line=1, column=1,)
        self.symbols = SymbolTable()
        self.evaluator = ExpressionEvaluator(self.symbols)


    def test_evaluate_literal(self) -> None:
        expression = LiteralExpression( value=42, location=self.location,)
        self.assertEqual( self.evaluator.evaluate(expression), 42,)


    def test_evaluate_negative_literal(self) -> None:
        expression = LiteralExpression( value=-5, location=self.location,)
        self.assertEqual( self.evaluator.evaluate(expression), -5,)


    def test_evaluate_identifier(self) -> None:
        self.symbols.define( name="START", value=0x200, location=self.location,)
        expression = IdentifierExpression( name="START", location=self.location,)
        self.assertEqual( self.evaluator.evaluate(expression), 0x200,)


    def test_evaluate_undefined_identifier_reports_location(self) -> None:
        location = SourceLocation(line=3, column=7)
        expression = IdentifierExpression(name="MISSING", location=location)
        with self.assertRaises(ExpressionEvaluationError) as context:
            self.evaluator.evaluate(expression)
        self.assertEqual(context.exception.location, location)


    def test_evaluate_addition(self) -> None:
        expression = BinaryExpression(
            operator=BinaryOperator.ADD,
            left=LiteralExpression( value=10, location=self.location,),
            right=LiteralExpression( value=5, location=self.location,),
            location=self.location
        )
        self.assertEqual( self.evaluator.evaluate(expression), 15,)


    def test_evaluate_subtraction(self) -> None:
        expression = BinaryExpression(
            operator=BinaryOperator.SUBTRACT,
            left=LiteralExpression( value=10, location=self.location,),
            right=LiteralExpression( value=5, location=self.location,),
            location=self.location
        )
        self.assertEqual( self.evaluator.evaluate(expression), 5,)


    def test_evaluate_expression_using_symbol(self) -> None:
        self.symbols.define( name="START", value=0x200, location=self.location,)
        expression = BinaryExpression(
            operator=BinaryOperator.ADD,
            left=IdentifierExpression( name="START", location=self.location,),
            right=LiteralExpression( value=3, location=self.location,),
            location=self.location
        )
        self.assertEqual( self.evaluator.evaluate(expression), 0x203,)


    def test_evaluate_nested_expression(self) -> None:
        expression = BinaryExpression(
            operator=BinaryOperator.ADD,
            left=BinaryExpression(
                operator=BinaryOperator.ADD,
                left=LiteralExpression( value=10, location=self.location,),
                right=LiteralExpression( value=5, location=self.location,),
                location=self.location,
            ),
            right=LiteralExpression( value=2, location=self.location,),
            location=self.location
        )
        self.assertEqual( self.evaluator.evaluate(expression), 17,)


class SymbolCollectorTest(unittest.TestCase):
    """
    @brief Tests for SymbolCollector.
    """

    def setUp(self) -> None:
        self.location = SourceLocation(line=1, column=1)
        self.isa = ClassicInstructionSetArchitecture()


    def test_target_requires_exactly_one_architecture_name(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode( name="TARGET", operands=(), location=self.location)
                ),
            )
        )
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        with self.assertRaises(ValueError) as context:
            collector.collect(assembly)
        self.assertEqual( str(context.exception), "TARGET requires exactly one architecture name.")


    def test_target_requires_identifier_architecture_name(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="TARGET",
                        operands=(LiteralExpression(value=1, location=self.location),),
                        location=self.location
                    )
                ),
            )
        )
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        with self.assertRaises(ValueError) as context:
            collector.collect(assembly)
        self.assertEqual( str(context.exception), "TARGET requires an architecture name.")


    def test_collects_label_at_program_start(self) -> None:
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        assembly = AssemblyNode(
            lines=(
                SourceLine( label=LabelNode( name="START", location=self.location), statement=None),
            )
        )
        collector.collect(assembly)
        self.assertEqual( symbols.lookup("START").value, 0x200)


    def test_instruction_advances_address(self) -> None:
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        assembly = AssemblyNode(
            lines=(
                SourceLine( label=None, statement=InstructionNode( mnemonic="CLS", operands=(), location=self.location)),
                SourceLine( label=LabelNode( name="NEXT", location=self.location), statement=None),
            )
        )
        collector.collect(assembly)
        self.assertEqual( symbols.lookup("NEXT").value, 0x202)


    def test_label_on_instruction_uses_instruction_address(self) -> None:
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        assembly = AssemblyNode(
            lines=(
                SourceLine( label=LabelNode( name="START", location=self.location), statement=InstructionNode( mnemonic="CLS", operands=(), location=self.location)),
                SourceLine( label=LabelNode( name="NEXT", location=self.location), statement=InstructionNode( mnemonic="RET", operands=(), location=self.location)),
            )
        )
        collector.collect(assembly)
        self.assertEqual( symbols.lookup("START").value, 0x200)
        self.assertEqual( symbols.lookup("NEXT").value, 0x202)


    def test_label_only_line_does_not_advance_address(self) -> None:
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        assembly = AssemblyNode(
            lines=(
                SourceLine( label=LabelNode( name="START", location=self.location), statement=None),
                SourceLine( label=LabelNode( name="NEXT", location=self.location), statement=None),
            )
        )
        collector.collect(assembly)
        self.assertEqual( symbols.lookup("START").value, 0x200)
        self.assertEqual( symbols.lookup("NEXT").value, 0x200)


#    def test_duplicate_label_is_rejected(self) -> None:
#        symbols = SymbolTable()
#        collector = SymbolCollector(symbols, self.isa)
#        assembly = AssemblyNode(
#            lines=(
#                SourceLine( label=LabelNode( name="START", location=self.location), statement=None),
#                SourceLine( label=LabelNode( name="START", location=self.location), statement=None),
#            )
#        )
#        with self.assertRaises(ValueError):
#            collector.collect(assembly)

    def test_duplicate_label_reports_second_definition_location(self) -> None:
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        first_location = SourceLocation(line=1, column=1)
        second_location = SourceLocation(line=2, column=1)
        assembly = AssemblyNode(
            lines=(
                SourceLine(label=LabelNode(name="START", location=first_location), statement=None),
                SourceLine(label=LabelNode(name="START", location=second_location), statement=None),
            )
        )
        with self.assertRaises(SemanticAnalysisError) as context:
            collector.collect(assembly)
        self.assertEqual(str(context.exception), "Symbol 'START' is already defined.")
        self.assertEqual(context.exception.location, second_location)
        self.assertEqual(symbols.lookup("START").location, first_location)

    def test_duplicate_equ_reports_second_definition_location(self) -> None:
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        first_location = SourceLocation(line=1, column=1)
        second_location = SourceLocation(line=2, column=1)
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=LabelNode(name="VALUE", location=first_location),
                    statement=DirectiveNode(
                        name="EQU",
                        operands=(LiteralExpression(value=1, location=first_location),),
                        location=first_location
                    )
                ),
                SourceLine(
                    label=LabelNode(name="VALUE", location=second_location),
                    statement=DirectiveNode(
                        name="EQU",
                        operands=(LiteralExpression(value=2, location=second_location),),
                        location=second_location
                    )
                ),
            )
        )
        with self.assertRaises(SemanticAnalysisError) as context:
            collector.collect(assembly)
        self.assertEqual(str(context.exception), "Symbol 'VALUE' is already defined.")
        self.assertEqual(context.exception.location, second_location)
        self.assertEqual(symbols.lookup("VALUE").value, 1)

    def test_label_then_equ_duplicate_reports_second_definition_location(self) -> None:
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        first_location = SourceLocation(line=1, column=1)
        second_location = SourceLocation(line=2, column=1)
        assembly = AssemblyNode(
            lines=(
                SourceLine(label=LabelNode(name="VALUE", location=first_location), statement=None),
                SourceLine(
                    label=LabelNode(name="VALUE", location=second_location),
                    statement=DirectiveNode(
                        name="EQU",
                        operands=(LiteralExpression(value=42, location=second_location),),
                        location=second_location
                    )
                ),
            )
        )
        with self.assertRaises(SemanticAnalysisError) as context:
            collector.collect(assembly)
        self.assertEqual(context.exception.location, second_location)
        self.assertEqual(symbols.lookup("VALUE").value, PROGRAM_START)

    def test_equ_then_label_duplicate_reports_second_definition_location(self) -> None:
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        first_location = SourceLocation(line=1, column=1)
        second_location = SourceLocation(line=2, column=1)
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=LabelNode(name="VALUE", location=first_location),
                    statement=DirectiveNode(
                        name="EQU",
                        operands=(LiteralExpression(value=42, location=first_location),),
                        location=first_location
                    )
                ),
                SourceLine(label=LabelNode(name="VALUE", location=second_location), statement=None),
            )
        )
        with self.assertRaises(SemanticAnalysisError) as context:
            collector.collect(assembly)
        self.assertEqual(context.exception.location, second_location)
        self.assertEqual(symbols.lookup("VALUE").value, 42)

    def test_duplicate_symbol_is_case_insensitive(self) -> None:
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        first_location = SourceLocation(line=1, column=1)
        second_location = SourceLocation(line=2, column=1)
        assembly = AssemblyNode(
            lines=(
                SourceLine(label=LabelNode(name="start", location=first_location), statement=None),
                SourceLine(label=LabelNode(name="START", location=second_location), statement=None),
            )
        )
        with self.assertRaises(SemanticAnalysisError) as context:
            collector.collect(assembly)
        self.assertEqual(context.exception.location, second_location)
        self.assertEqual(symbols.lookup("START").name, "start")


    def test_org_changes_address(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine( label=None, statement=DirectiveNode( name="ORG", operands=( LiteralExpression( value=0x300, location=self.location),), location=self.location)),
                SourceLine( label=LabelNode( name="START", location=self.location), statement=None)
            )
        )
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        collector.collect(assembly)
        self.assertEqual(symbols.lookup("START").value, 0x300)


    def test_org_applies_after_instruction(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine( label=LabelNode( name="START", location=self.location), statement=InstructionNode( mnemonic="CLS", operands=(), location=self.location)),
                SourceLine( label=None, statement=DirectiveNode( name="ORG", operands=( LiteralExpression( value=0x400, location=self.location),), location=self.location)),
                SourceLine( label=LabelNode( name="NEXT", location=self.location), statement=None)
            )
        )
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        collector.collect(assembly)
        self.assertEqual( symbols.lookup("START").value, PROGRAM_START)
        self.assertEqual( symbols.lookup("NEXT").value, 0x400)


    def test_org_accepts_expression(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine( label=None, statement=DirectiveNode( name="ORG", operands=( BinaryExpression( operator=BinaryOperator.ADD, left=LiteralExpression( value=0x300, location=self.location), right=LiteralExpression( value=0x20, location=self.location), location=self.location),), location=self.location)),
                SourceLine( label=LabelNode( name="START", location=self.location), statement=None)
            )
        )
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        collector.collect(assembly)
        self.assertEqual( symbols.lookup("START").value, 0x320)


    def test_org_rejects_missing_operand(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine( label=None, statement=DirectiveNode( name="ORG", operands=(), location=self.location)),
            )
        )
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        with self.assertRaises(ValueError):
            collector.collect(assembly)


    def test_org_rejects_multiple_operands(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine( label=None, statement=DirectiveNode( name="ORG", operands=( LiteralExpression( value=0x300, location=self.location), LiteralExpression( value=0x400, location=self.location)), location=self.location)),
            )
        )
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        with self.assertRaises(ValueError):
            collector.collect(assembly)


    def test_org_rejects_address_above_ffff(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine( label=None, statement=DirectiveNode( name="ORG", operands=( LiteralExpression( value=0x10000, location=self.location),), location=self.location)),
            )
        )
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        with self.assertRaises(ValueError):
            collector.collect(assembly)


    def test_org_rejects_negative_address(self) -> None:
        assembly = AssemblyNode( lines=( SourceLine( label=None, statement=DirectiveNode( name="ORG", operands=( LiteralExpression( value=-1, location=self.location),), location=self.location)),))
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        with self.assertRaises(ValueError):
            collector.collect(assembly)


    def test_equ_defines_symbol(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=LabelNode( name="VALUE", location=self.location), statement=DirectiveNode( name="EQU",
                        operands=( LiteralExpression( value=42, location=self.location),), location=self.location
                    )
                ),
            )
        )
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        collector.collect(assembly)
        self.assertEqual(symbols.lookup("VALUE").value, 42)


    def test_equ_does_not_advance_address(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=LabelNode( name="VALUE", location=self.location),
                    statement=DirectiveNode( name="EQU", operands=( LiteralExpression( value=42, location=self.location),), location=self.location)
                ),
                SourceLine( label=LabelNode( name="START", location=self.location), statement=None)
            )
        )
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        collector.collect(assembly)
        self.assertEqual(symbols.lookup("VALUE").value, 42)
        self.assertEqual(symbols.lookup("START").value, PROGRAM_START)


    def test_equ_accepts_expression(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=LabelNode(
                        name="VALUE",
                        location=self.location
                    ),
                    statement=DirectiveNode(
                        name="EQU",
                        operands=(
                            BinaryExpression( operator=BinaryOperator.ADD, left=LiteralExpression( value=40, location=self.location), right=LiteralExpression( value=2, location=self.location), location=self.location),
                        ),
                        location=self.location
                    )
                ),
            )
        )
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        collector.collect(assembly)
        self.assertEqual(symbols.lookup("VALUE").value, 42)


    def test_equ_can_reference_previous_symbol(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=LabelNode( name="BASE", location=self.location),
                    statement=DirectiveNode( name="EQU", operands=( LiteralExpression( value=0x200, location=self.location),), location=self.location)
                ),
                SourceLine(
                    label=LabelNode( name="NEXT", location=self.location),
                    statement=DirectiveNode(
                        name="EQU",
                        operands=(
                            BinaryExpression( operator=BinaryOperator.ADD, left=IdentifierExpression( name="BASE", location=self.location), right=LiteralExpression( value=3, location=self.location), location=self.location),
                        ),
                        location=self.location
                    )
                ),
            )
        )
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        collector.collect(assembly)
        self.assertEqual(symbols.lookup("BASE").value, 0x200)
        self.assertEqual(symbols.lookup("NEXT").value, 0x203)


    def test_equ_requires_label(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode( name="EQU", operands=( LiteralExpression( value=42, location=self.location),), location=self.location)
                ),
            )
        )
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        with self.assertRaises(ValueError):
            collector.collect(assembly)


    def test_equ_requires_one_operand(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=LabelNode( name="VALUE", location=self.location),
                    statement=DirectiveNode( name="EQU", operands=(), location=self.location)
                ),
            )
        )
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        with self.assertRaises(ValueError):
            collector.collect(assembly)


    def test_equ_rejects_multiple_operands(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=LabelNode( name="VALUE", location=self.location),
                    statement=DirectiveNode(
                        name="EQU",
                        operands=( LiteralExpression( value=1, location=self.location), LiteralExpression( value=2, location=self.location)),
                        location=self.location
                    )
                ),
            )
        )
        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)
        with self.assertRaises(ValueError):
            collector.collect(assembly)


    def test_db_advances_address_by_one(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="DB",
                        operands=(
                            LiteralExpression(
                                value=0x42,
                                location=self.location
                            ),
                        ),
                        location=self.location
                    )
                ),
                SourceLine(
                    label=LabelNode(
                        name="NEXT",
                        location=self.location
                    ),
                    statement=None
                )
            )
        )

        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)

        collector.collect(assembly)

        self.assertEqual(
            symbols.lookup("NEXT").value,
            PROGRAM_START + 1
        )

    def test_db_advances_address_for_multiple_bytes(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="DB",
                        operands=(
                            LiteralExpression(value=1, location=self.location),
                            LiteralExpression(value=2, location=self.location),
                            LiteralExpression(value=3, location=self.location)
                        ),
                        location=self.location
                    )
                ),
                SourceLine(
                    label=LabelNode(
                        name="NEXT",
                        location=self.location
                    ),
                    statement=None
                )
            )
        )

        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)

        collector.collect(assembly)

        self.assertEqual(
            symbols.lookup("NEXT").value,
            PROGRAM_START + 3
        )

    def test_db_label_uses_first_byte_address(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=LabelNode(
                        name="DATA",
                        location=self.location
                    ),
                    statement=DirectiveNode(
                        name="DB",
                        operands=(
                            LiteralExpression(value=1, location=self.location),
                            LiteralExpression(value=2, location=self.location),
                            LiteralExpression(value=3, location=self.location)
                        ),
                        location=self.location
                    )
                ),
            )
        )

        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)

        collector.collect(assembly)

        self.assertEqual(
            symbols.lookup("DATA").value,
            PROGRAM_START
        )

    def test_db_string_advances_address_by_string_length(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="DB",
                        operands=(
                            LiteralExpression(
                                value="ABC",
                                location=self.location
                            ),
                        ),
                        location=self.location
                    )
                ),
                SourceLine(
                    label=LabelNode(
                        name="NEXT",
                        location=self.location
                    ),
                    statement=None
                )
            )
        )

        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)

        collector.collect(assembly)

        self.assertEqual(
            symbols.lookup("NEXT").value,
            PROGRAM_START + 3
        )

    def test_db_rejects_missing_operand(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="DB",
                        operands=(),
                        location=self.location
                    )
                ),
            )
        )

        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)

        with self.assertRaises(ValueError):
            collector.collect(assembly)

    def test_db_rejects_negative_value(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="DB",
                        operands=(
                            LiteralExpression(
                                value=-1,
                                location=self.location
                            ),
                        ),
                        location=self.location
                    )
                ),
            )
        )

        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)

        with self.assertRaises(ValueError):
            collector.collect(assembly)

    def test_db_rejects_value_above_ff(self) -> None:
        assembly = AssemblyNode(
            lines=(
                SourceLine(
                    label=None,
                    statement=DirectiveNode(
                        name="DB",
                        operands=(
                            LiteralExpression(
                                value=0x100,
                                location=self.location
                            ),
                        ),
                        location=self.location
                    )
                ),
            )
        )

        symbols = SymbolTable()
        collector = SymbolCollector(symbols, self.isa)

        with self.assertRaises(ValueError):
            collector.collect(assembly)


    def test_rejects_assembler_operands_as_labels(self) -> None:
        for name in ("I", "DT", "ST", "K", "F", "B", "V0", "VF", "i", "dt", "v0"):
            with self.subTest(name=name):
                symbols = SymbolTable()
                collector = SymbolCollector(symbols, self.isa)
                assembly = AssemblyNode(
                    lines=(
                        SourceLine(
                            label=LabelNode(name=name, location=self.location),
                            statement=None
                        ),
                    )
                )
                with self.assertRaises(ValueError):
                    collector.collect(assembly)


    def test_rejects_assembler_operands_as_equ_symbols(self) -> None:
        for name in ("I", "DT", "ST", "K", "F", "B", "V0", "VF", "i", "dt", "v0"):
            with self.subTest(name=name):
                symbols = SymbolTable()
                collector = SymbolCollector(symbols, self.isa)
                assembly = AssemblyNode(
                    lines=(
                        SourceLine(
                            label=LabelNode(name=name, location=self.location),
                            statement=DirectiveNode(
                                name="EQU",
                                operands=(
                                    LiteralExpression(
                                        value=42,
                                        location=self.location
                                    ),
                                ),
                                location=self.location
                            )
                        ),
                    )
                )
                with self.assertRaises(ValueError):
                    collector.collect(assembly)




class OperandResolverTest(unittest.TestCase):
    """
    @brief Tests for OperandResolver.
    """

    def setUp(self) -> None:
        self.location = SourceLocation(line=1, column=1)
        self.symbols = SymbolTable()
        self.isa = ClassicInstructionSetArchitecture()
        self.resolver = OperandResolver(self.symbols, self.isa)


    def test_resolve_register(self) -> None:
        expression = IdentifierExpression( name="V3", location=self.location)
        operand = self.resolver.resolve( expression, AssemblerOperandType.REGISTER)
        self.assertEqual(operand.type, AssemblerOperandType.REGISTER)
        self.assertEqual(operand.value, 3)


    def test_resolve_index_register(self) -> None:
        expression = IdentifierExpression( name="I", location=self.location)
        operand = self.resolver.resolve( expression, AssemblerOperandType.INDEX_REGISTER)
        self.assertEqual( operand.type, AssemblerOperandType.INDEX_REGISTER)
        self.assertEqual(operand.value, 0)


    def test_resolve_delay_register(self) -> None:
        expression = IdentifierExpression( name="DT", location=self.location)
        operand = self.resolver.resolve( expression, AssemblerOperandType.DELAY_REGISTER)
        self.assertEqual( operand.type, AssemblerOperandType.DELAY_REGISTER)


    def test_resolve_sound_register(self) -> None:
        expression = IdentifierExpression( name="ST", location=self.location)
        operand = self.resolver.resolve( expression, AssemblerOperandType.SOUND_REGISTER)
        self.assertEqual( operand.type, AssemblerOperandType.SOUND_REGISTER)


    def test_resolve_key_register(self) -> None:
        expression = IdentifierExpression( name="K", location=self.location)
        operand = self.resolver.resolve( expression, AssemblerOperandType.KEY)
        self.assertEqual(operand.type, AssemblerOperandType.KEY)


    def test_resolve_font_register(self) -> None:
        expression = IdentifierExpression( name="F", location=self.location)
        operand = self.resolver.resolve( expression, AssemblerOperandType.FONT_REGISTER)
        self.assertEqual( operand.type, AssemblerOperandType.FONT_REGISTER)


    def test_resolve_bcd_register(self) -> None:
        expression = IdentifierExpression( name="B", location=self.location)
        operand = self.resolver.resolve( expression, AssemblerOperandType.BCD_REGISTER)
        self.assertEqual( operand.type, AssemblerOperandType.BCD_REGISTER)


    def test_resolve_literal_value(self) -> None:
        expression = LiteralExpression( value=42, location=self.location)
        operand = self.resolver.resolve( expression, AssemblerOperandType.VALUE)
        self.assertEqual(operand.type, AssemblerOperandType.VALUE)
        self.assertEqual(operand.value, 42)


    def test_resolve_literal_address(self) -> None:
        expression = LiteralExpression( value=0x234, location=self.location)
        operand = self.resolver.resolve( expression, AssemblerOperandType.ADDRESS)
        self.assertEqual( operand.type, AssemblerOperandType.ADDRESS)
        self.assertEqual(operand.value, 0x234)


    def test_resolve_symbol_as_value(self) -> None:
        self.symbols.define( name="START", value=0x200, location=self.location)
        expression = IdentifierExpression( name="START", location=self.location)
        operand = self.resolver.resolve( expression, AssemblerOperandType.VALUE)
        self.assertEqual(operand.type, AssemblerOperandType.VALUE)
        self.assertEqual(operand.value, 0x200)


    def test_resolve_symbol_expression_as_address(self) -> None:
        self.symbols.define( name="START", value=0x200, location=self.location)
        expression = BinaryExpression( operator=BinaryOperator.ADD, left=IdentifierExpression( name="START", location=self.location), right=LiteralExpression( value=3, location=self.location), location=self.location)
        operand = self.resolver.resolve( expression, AssemblerOperandType.ADDRESS)
        self.assertEqual( operand.type, AssemblerOperandType.ADDRESS)
        self.assertEqual(operand.value, 0x203)


    def test_resolve_register_as_value_is_rejected(self) -> None:
        expression = IdentifierExpression( name="V3", location=self.location)
        with self.assertRaises(ExpressionEvaluationError):
            self.resolver.resolve( expression, AssemblerOperandType.VALUE)


    def test_resolve_index_register_as_value_is_rejected(self) -> None:
        expression = IdentifierExpression( name="I", location=self.location)
        with self.assertRaises(ExpressionEvaluationError):
            self.resolver.resolve( expression, AssemblerOperandType.VALUE)


    def test_resolve_unknown_identifier_reports_location(self) -> None:
        location = SourceLocation(line=4, column=9)
        expression = IdentifierExpression(name="MISSING", location=location)
        with self.assertRaises(ExpressionEvaluationError) as context:
            self.resolver.resolve(expression, AssemblerOperandType.VALUE)
        self.assertEqual(context.exception.location, location)


    def test_resolve_string_literal_is_rejected(self) -> None:
        expression = LiteralExpression( value="HELLO", location=self.location)
        with self.assertRaises(ExpressionEvaluationError):
            self.resolver.resolve( expression, AssemblerOperandType.VALUE)


    def test_resolve_indirect_index(self) -> None:
        expression = IndirectExpression(
            expression=IdentifierExpression(
                name="I",
                location=self.location
            ),
            location=self.location
        )
        operand = self.resolver.resolve( expression, AssemblerOperandType.INDIRECT_INDEX)
        self.assertEqual( operand.type, AssemblerOperandType.INDIRECT_INDEX)
        self.assertEqual( operand.value, 0)


    def test_resolve_indirect_index_is_case_insensitive(self) -> None:
        expression = IndirectExpression(
            expression=IdentifierExpression(
                name="i",
                location=self.location
            ),
            location=self.location
        )
        operand = self.resolver.resolve( expression, AssemblerOperandType.INDIRECT_INDEX)
        self.assertEqual( operand.type, AssemblerOperandType.INDIRECT_INDEX)


    def test_resolve_indirect_literal_rejects_operand(self) -> None:
        expression = IndirectExpression(
            expression=LiteralExpression(
                value=0x300,
                location=self.location
            ),
            location=self.location
        )
        with self.assertRaises(ExpressionEvaluationError):
            self.resolver.resolve( expression, AssemblerOperandType.INDIRECT_INDEX)


    def test_resolve_indirect_register_rejects_operand(self) -> None:
        expression = IndirectExpression(
            expression=IdentifierExpression(
                name="V3",
                location=self.location
            ),
            location=self.location
        )
        with self.assertRaises(ExpressionEvaluationError):
            self.resolver.resolve( expression, AssemblerOperandType.INDIRECT_INDEX)


    def test_unknown_identifier_is_not_architectural_operand(self) -> None:
        expression = IdentifierExpression( name="XYZ", location=self.location)
        with self.assertRaises(ExpressionEvaluationError):
            self.resolver.resolve( expression, AssemblerOperandType.REGISTER)


class InstructionResolverTest(unittest.TestCase):
    """
    @brief Tests for InstructionResolver.
    """

    def setUp(self) -> None:
        self.location = SourceLocation(line=1, column=1)
        self.symbols = SymbolTable()
        self.isa = ClassicInstructionSetArchitecture()
        self.resolver = InstructionResolver(self.symbols, self.isa)


    def test_resolve_ld_vx_byte(self) -> None:
        instruction = InstructionNode(
            mnemonic="LD",
            operands=(
                IdentifierExpression(name="V3", location=self.location),
                LiteralExpression(value=0x42, location=self.location)
            ),
            location=self.location
        )
        result = self.resolver.resolve(instruction)
        self.assertEqual(result.id, InstructionId.LD_BYTE)
        self.assertEqual(result.x, 3)
        self.assertEqual(result.nn, 0x42)


    def test_resolve_ld_vx_dt(self) -> None:
        instruction = InstructionNode(
            mnemonic="LD",
            operands=(
                IdentifierExpression(name="V3", location=self.location),
                IdentifierExpression(name="DT", location=self.location)
            ),
            location=self.location
        )
        result = self.resolver.resolve(instruction)
        self.assertEqual(result.id, InstructionId.LD_VX_DT)
        self.assertEqual(result.x, 3)


    def test_resolve_ld_dt_vx(self) -> None:
        instruction = InstructionNode(
            mnemonic="LD",
            operands=(
                IdentifierExpression(name="DT", location=self.location),
                IdentifierExpression(name="V3", location=self.location)
            ),
            location=self.location
        )
        result = self.resolver.resolve(instruction)
        self.assertEqual(result.id, InstructionId.LD_DT_VX)
        self.assertEqual(result.x, 3)


    def test_resolve_add_vx_byte(self) -> None:
        instruction = InstructionNode(
            mnemonic="ADD",
            operands=( IdentifierExpression(name="V3", location=self.location), LiteralExpression(value=5, location=self.location)),
            location=self.location
        )
        result = self.resolver.resolve(instruction)
        self.assertEqual(result.id, InstructionId.ADD_BYTE)
        self.assertEqual(result.x, 3)
        self.assertEqual(result.nn, 5)


    def test_resolve_add_vx_vy(self) -> None:
        instruction = InstructionNode(
            mnemonic="ADD",
            operands=( IdentifierExpression(name="V3", location=self.location), IdentifierExpression(name="V5", location=self.location)),
            location=self.location
        )
        result = self.resolver.resolve(instruction)
        self.assertEqual(result.id, InstructionId.ADD_REGISTER)
        self.assertEqual(result.x, 3)
        self.assertEqual(result.y, 5)


    def test_resolve_add_i_vx(self) -> None:
        instruction = InstructionNode(
            mnemonic="ADD",
            operands=( IdentifierExpression(name="I", location=self.location), IdentifierExpression(name="V3", location=self.location)),
            location=self.location
        )
        result = self.resolver.resolve(instruction)
        self.assertEqual(result.id, InstructionId.ADD_I_VX)
        self.assertEqual(result.x, 3)


    def test_resolve_jp_address_symbol(self) -> None:
        self.symbols.define( name="LOOP", value=0x300, location=self.location)
        instruction = InstructionNode( mnemonic="JP", operands=( IdentifierExpression(name="LOOP", location=self.location),), location=self.location)
        result = self.resolver.resolve(instruction)
        self.assertEqual(result.id, InstructionId.JP)
        self.assertEqual(result.nnn, 0x300)


