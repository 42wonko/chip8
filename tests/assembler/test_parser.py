"""
@file test_parser.py

@brief Unit tests for the assembler parser.
"""

import unittest

from assembler.ast import (
    BinaryExpression,
    BinaryOperator,
    DirectiveNode,
    IdentifierExpression,
    InstructionNode,
    LabelNode,
    LiteralExpression,
)
from assembler.lexer import Lexer
from assembler.parser import Parser, ParserError


class ParserTest(unittest.TestCase):
    """
    @brief Tests for the assembler parser.
    """

    def _parse(self, source: str):
        """
        @brief Lex and parse assembler source.

        @param source
            Assembly source.

        @return
            Parsed assembly tree.
        """
        tokens = Lexer(source).tokenize()
        return Parser(tokens).parse()

    def test_empty_source(self) -> None:
        assembly = self._parse("")
        self.assertEqual( len(assembly.lines), 0)

    def test_instruction_without_operands(self) -> None:
        assembly = self._parse("CLS")
        statement = assembly.lines[0].statement
        self.assertIsInstance( statement, InstructionNode)
        self.assertEqual( statement.mnemonic, "CLS")
        self.assertEqual( statement.operands, ())

    def test_instruction_with_number_operand(self) -> None:
        assembly = self._parse("LD V0, 42")
        statement = assembly.lines[0].statement
        self.assertIsInstance( statement, InstructionNode)
        self.assertEqual( statement.mnemonic, "LD")
        self.assertEqual( len(statement.operands), 2)
        register = statement.operands[0]
        value = statement.operands[1]
        self.assertIsInstance( register, IdentifierExpression)
        self.assertEqual( register.name, "V0")
        self.assertIsInstance( value, LiteralExpression)
        self.assertEqual( value.value, 42)

    def test_hexadecimal_operand(self) -> None:
        assembly = self._parse("LD V0, 0x2A")
        statement = assembly.lines[0].statement
        self.assertIsInstance( statement, InstructionNode)
        operand = statement.operands[1]
        self.assertIsInstance( operand, LiteralExpression)
        self.assertEqual( operand.value, 42)

    def test_binary_operand(self) -> None:
        assembly = self._parse("LD V0, 0b101010")
        statement = assembly.lines[0].statement
        self.assertIsInstance( statement, InstructionNode)
        operand = statement.operands[1]
        self.assertIsInstance( operand, LiteralExpression)
        self.assertEqual( operand.value, 42)

    def test_character_operand(self) -> None:
        assembly = self._parse("DB 'A'")
        statement = assembly.lines[0].statement
        self.assertIsInstance( statement, DirectiveNode)
        operand = statement.operands[0]
        self.assertIsInstance( operand, LiteralExpression)
        self.assertEqual( operand.value, ord("A"))

    def test_string_operand(self) -> None:
        assembly = self._parse('DB "Hello"')
        statement = assembly.lines[0].statement
        self.assertIsInstance( statement, DirectiveNode)
        operand = statement.operands[0]
        self.assertIsInstance( operand, LiteralExpression)
        self.assertEqual( operand.value, "Hello")

    def test_identifier_operand(self) -> None:
        assembly = self._parse("JP start")
        statement = assembly.lines[0].statement
        self.assertIsInstance( statement, InstructionNode)
        operand = statement.operands[0]
        self.assertIsInstance( operand, IdentifierExpression)
        self.assertEqual( operand.name, "start")

    def test_addition_expression(self) -> None:
        assembly = self._parse("JP start + 2")
        statement = assembly.lines[0].statement
        self.assertIsInstance( statement, InstructionNode)
        expression = statement.operands[0]
        self.assertIsInstance( expression, BinaryExpression)
        self.assertEqual( expression.operator, BinaryOperator.ADD)
        self.assertIsInstance( expression.left, IdentifierExpression)
        self.assertEqual( expression.left.name, "start")
        self.assertIsInstance( expression.right, LiteralExpression)
        self.assertEqual( expression.right.value, 2)

    def test_subtraction_expression(self) -> None:
        assembly = self._parse("JP start - 2")
        statement = assembly.lines[0].statement
        self.assertIsInstance( statement, InstructionNode)
        expression = statement.operands[0]
        self.assertIsInstance( expression, BinaryExpression)
        self.assertEqual( expression.operator, BinaryOperator.SUBTRACT)

    def test_chained_expression(self) -> None:
        assembly = self._parse("JP start + 2 - 1")
        statement = assembly.lines[0].statement
        self.assertIsInstance( statement, InstructionNode)
        expression = statement.operands[0]
        self.assertIsInstance( expression, BinaryExpression)
        self.assertEqual( expression.operator, BinaryOperator.SUBTRACT)
        self.assertIsInstance( expression.left, BinaryExpression)
        self.assertEqual( expression.left.operator, BinaryOperator.ADD)

    def test_parenthesized_expression(self) -> None:
        assembly = self._parse("JP (start + 2)")
        statement = assembly.lines[0].statement
        self.assertIsInstance( statement, InstructionNode)
        expression = statement.operands[0]
        self.assertIsInstance( expression, BinaryExpression)
        self.assertEqual( expression.operator, BinaryOperator.ADD)

    def test_label(self) -> None:
        assembly = self._parse("start:")
        line = assembly.lines[0]
        self.assertIsInstance( line.label, LabelNode)
        self.assertEqual( line.label.name, "start")
        self.assertIsNone( line.statement)

    def test_label_with_instruction(self) -> None:
        assembly = self._parse("start: CLS")
        line = assembly.lines[0]
        self.assertIsInstance( line.label, LabelNode)
        self.assertEqual( line.label.name, "start")
        self.assertIsInstance( line.statement, InstructionNode)

    def test_directive(self) -> None:
        assembly = self._parse("TARGET COSMAC")
        statement = assembly.lines[0].statement
        self.assertIsInstance( statement, DirectiveNode)
        self.assertEqual( statement.name, "TARGET")
        self.assertEqual( len(statement.operands), 1)
        operand = statement.operands[0]
        self.assertIsInstance( operand, IdentifierExpression)
        self.assertEqual( operand.name, "COSMAC")

    def test_multiple_operands(self) -> None:
        assembly = self._parse("LD V0, V1, V2")
        statement = assembly.lines[0].statement
        self.assertIsInstance( statement, InstructionNode)
        self.assertEqual( len(statement.operands), 3)
        self.assertIsInstance( statement.operands[0], IdentifierExpression)
        self.assertIsInstance( statement.operands[1], IdentifierExpression)
        self.assertIsInstance( statement.operands[2], IdentifierExpression)

    def test_comment(self) -> None:
        assembly = self._parse("CLS ; comment")
        statement = assembly.lines[0].statement
        self.assertIsInstance( statement, InstructionNode)
        self.assertEqual( statement.mnemonic, "CLS")

    def test_empty_lines(self) -> None:
        assembly = self._parse("\n\nCLS\n\nRET\n")
        self.assertEqual( len(assembly.lines), 2)
        self.assertIsInstance( assembly.lines[0].statement, InstructionNode)
        self.assertIsInstance( assembly.lines[1].statement, InstructionNode)

    def test_missing_expression_after_comma(self) -> None:
        with self.assertRaises(ParserError):
            self._parse("LD V0,")

    def test_unexpected_token(self) -> None:
        with self.assertRaises(ParserError):
            self._parse("LD V0, :")

    def test_missing_closing_parenthesis(self) -> None:
        with self.assertRaises(ParserError):
            self._parse("JP (start + 2")

    def test_empty_parenthesized_expression(self) -> None:
        with self.assertRaises(ParserError):
            self._parse("JP ()")

    def test_trailing_tokens(self) -> None:
        with self.assertRaises(ParserError):
            self._parse("CLS V0 V1")

    def test_parse_org_directive(self) -> None:
        tokens = Lexer("ORG 0x300").tokenize()
        assembly = Parser(tokens).parse()
        statement = assembly.lines[0].statement
        self.assertIsInstance(statement, DirectiveNode)
        self.assertEqual(statement.name, "ORG")
        self.assertEqual(len(statement.operands), 1)
        operand = statement.operands[0]
        self.assertIsInstance(operand, LiteralExpression)
        self.assertEqual(operand.value, 0x300)

    def test_parse_org_expression(self) -> None:
        tokens = Lexer("ORG 0x200 + 0x20").tokenize()
        assembly = Parser(tokens).parse()
        statement = assembly.lines[0].statement
        self.assertIsInstance(statement, DirectiveNode)
        self.assertEqual(statement.name, "ORG")
        self.assertEqual(len(statement.operands), 1)
        operand = statement.operands[0]
        self.assertIsInstance(operand, BinaryExpression)
        self.assertEqual(operand.operator, BinaryOperator.ADD)


