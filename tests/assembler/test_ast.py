"""
@file test_ast.py

@brief Unit tests for assembler AST classes.
"""

import unittest

from assembler.ast import (
    AssemblyNode,
    BinaryExpression,
    BinaryOperator,
    DirectiveNode,
    ExpressionType,
    IdentifierExpression,
    InstructionNode,
    LabelNode,
    LiteralExpression,
    SourceLine,
)
from assembler.token import SourceLocation


class AstTest(unittest.TestCase):
    """
    @brief Tests for assembler AST classes.
    """

    def setUp(self) -> None:
        self.location = SourceLocation( line=1, column=1)

    def test_literal_expression(self) -> None:
        expression = LiteralExpression( value=42, location=self.location)
        self.assertEqual( expression.type, ExpressionType.LITERAL)
        self.assertEqual( expression.value, 42)
        self.assertEqual( expression.location, self.location)

    def test_identifier_expression(self) -> None:
        expression = IdentifierExpression( name="start", location=self.location)
        self.assertEqual( expression.type, ExpressionType.IDENTIFIER)
        self.assertEqual( expression.name, "start")
        self.assertEqual( expression.location, self.location)

    def test_binary_expression(self) -> None:
        left = IdentifierExpression( name="start", location=self.location)
        right = LiteralExpression( value=2, location=SourceLocation( line=1, column=9))
        expression = BinaryExpression( operator=BinaryOperator.ADD, left=left, right=right, location=self.location)
        self.assertEqual( expression.type, ExpressionType.BINARY)
        self.assertEqual( expression.operator, BinaryOperator.ADD)
        self.assertIs( expression.left, left)
        self.assertIs( expression.right, right)

    def test_subtraction_expression(self) -> None:
        left = LiteralExpression( value=10, location=self.location)
        right = LiteralExpression( value=3, location=SourceLocation( line=1, column=6))
        expression = BinaryExpression( operator=BinaryOperator.SUBTRACT, left=left, right=right, location=self.location)
        self.assertEqual( expression.operator, BinaryOperator.SUBTRACT)

    def test_instruction_uses_expressions(self) -> None:
        operand = LiteralExpression( value=42, location=SourceLocation( line=1, column=7))
        instruction = InstructionNode( mnemonic="LD", operands=(operand,), location=self.location)
        self.assertEqual( instruction.mnemonic, "LD")
        self.assertEqual( len(instruction.operands), 1)
        self.assertIs( instruction.operands[0], operand)

    def test_directive_uses_expressions(self) -> None:
        operand = IdentifierExpression( name="COSMAC", location=SourceLocation( line=1, column=8))
        directive = DirectiveNode( name="TARGET", operands=(operand,), location=self.location)
        self.assertEqual( directive.name, "TARGET")
        self.assertIs( directive.operands[0], operand)

    def test_label_node(self) -> None:
        label = LabelNode( name="start", location=self.location)
        self.assertEqual( label.name, "start")

    def test_source_line(self) -> None:
        line = SourceLine( label=None, statement=None)
        self.assertIsNone( line.label)
        self.assertIsNone( line.statement)

    def test_assembly_node(self) -> None:
        assembly = AssemblyNode( lines=())
        self.assertEqual( assembly.lines, ())

    def test_expression_is_immutable(self) -> None:
        expression = LiteralExpression( value=42, location=self.location)
        with self.assertRaises(AttributeError):
            expression.value = 43
