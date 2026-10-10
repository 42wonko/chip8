"""
@file test_parser.py

@brief Unit tests for the assembler parser.
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
)
from assembler.classicparser import ClassicParser
from assembler.lexer import Lexer
from assembler.parser import Parser, ParserError
from chip8.isa.classicisa import ClassicInstructionSetArchitecture


class PermissiveParser(Parser):
    """Test parser that accepts any instruction mnemonic."""

    def _is_instruction_mnemonic(self, mnemonic: str) -> bool:
        return True

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
        parser = PermissiveParser()
        parser.set_tokens(tokens)
        return parser.parse()

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
        assembly = self._parse("DATA: DB 'A'")
        statement = assembly.lines[0].statement
        self.assertIsInstance( statement, DirectiveNode)
        operand = statement.operands[0]
        self.assertIsInstance( operand, LiteralExpression)
        self.assertEqual( operand.value, ord("A"))

    def test_string_operand(self) -> None:
        assembly = self._parse('DATA: DB "Hello"')
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
        parser = PermissiveParser()
        parser.set_tokens(tokens)
        assembly = parser.parse()
        statement = assembly.lines[0].statement
        self.assertIsInstance(statement, DirectiveNode)
        self.assertEqual(statement.name, "ORG")
        self.assertEqual(len(statement.operands), 1)
        operand = statement.operands[0]
        self.assertIsInstance(operand, LiteralExpression)
        self.assertEqual(operand.value, 0x300)

    def test_label_on_org_is_syntax_error(self) -> None:
        with self.assertRaises(ParserError) as context:
            self._parse("start: ORG 0x200")
        self.assertEqual(context.exception.location.line, 1)
        self.assertEqual(context.exception.location.column, 1)
        self.assertEqual( str(context.exception), "A label cannot be used with the ORG directive.")

    def test_parse_org_expression(self) -> None:
        tokens = Lexer("ORG 0x200 + 0x20").tokenize()
        parser = PermissiveParser()
        parser.set_tokens(tokens)
        assembly = parser.parse()
        statement = assembly.lines[0].statement
        self.assertIsInstance(statement, DirectiveNode)
        self.assertEqual(statement.name, "ORG")
        self.assertEqual(len(statement.operands), 1)
        operand = statement.operands[0]
        self.assertIsInstance(operand, BinaryExpression)
        self.assertEqual(operand.operator, BinaryOperator.ADD)

    def test_indirect_operand(self) -> None:
        assembly = self._parse("LD V2, [I]")
        statement = assembly.lines[0].statement
        self.assertIsInstance( statement, InstructionNode)
        self.assertEqual( len(statement.operands), 2)
        operand = statement.operands[1]
        self.assertIsInstance( operand, IndirectExpression)
        self.assertIsInstance( operand.expression, IdentifierExpression)
        self.assertEqual( operand.expression.name, "I")

    def test_missing_closing_bracket(self) -> None:
        with self.assertRaises(ParserError):
            self._parse("LD V2, [I")

    def test_index_register_is_not_indirect(self) -> None:
        assembly = self._parse("LD I, 0x300")
        statement = assembly.lines[0].statement
        self.assertIsInstance( statement, InstructionNode)
        operand = statement.operands[0]
        self.assertIsInstance( operand, IdentifierExpression)
        self.assertEqual( operand.name, "I")

    def test_set_tokens_resets_parser_state(self) -> None:
        parser = PermissiveParser()

        parser.set_tokens(Lexer("CLS").tokenize())
        first = parser.parse()
        self.assertEqual(first.lines[0].statement.mnemonic, "CLS")

        parser.set_tokens(Lexer("RET").tokenize())
        second = parser.parse()
        self.assertEqual(second.lines[0].statement.mnemonic, "RET")


class TestClassicParser(unittest.TestCase):
    """
    @brief Tests for the Classic CHIP-8 assembler parser.
    """

    def setUp(self) -> None:
        self._isa = ClassicInstructionSetArchitecture()
        self._parser = ClassicParser(self._isa)


    def _parse(self, source: str) -> AssemblyNode:
        tokens = Lexer(source).tokenize()
        self._parser.set_tokens(tokens)
        return self._parser.parse()


    def test_accepts_classic_instruction(self) -> None:
        assembly = self._parse("CLS")
        self.assertEqual(len(assembly.lines), 1)
        self.assertIsInstance(assembly.lines[0].statement, InstructionNode)
        self.assertEqual(assembly.lines[0].statement.mnemonic, "CLS")


    def test_accepts_classic_instruction_case_insensitively(self) -> None:
        assembly = self._parse("cls")
        statement = assembly.lines[0].statement
        self.assertIsInstance(statement, InstructionNode)
        self.assertEqual(statement.mnemonic, "cls")


    def test_rejects_unsupported_instruction(self) -> None:
        with self.assertRaises(ParserError):
            self._parse("PLANE 1")


    def test_classic_parser_inherits_common_parser(self) -> None:
        self._parser.set_tokens(Lexer("CLS").tokenize())
        assembly = self._parser.parse()
        statement = assembly.lines[0].statement
        self.assertIsInstance(statement, InstructionNode)
        self.assertEqual(statement.mnemonic, "CLS")

    def test_set_tokens_resets_parser_state(self) -> None:
        """
        @brief Verify that a parser can parse independent token streams
        sequentially.
        """
        parser = PermissiveParser()

        first_tokens = Lexer("CLS\n").tokenize()
        parser.set_tokens(first_tokens)
        first = parser.parse()

        second_tokens = Lexer("RET\n").tokenize()
        parser.set_tokens(second_tokens)
        second = parser.parse()

        self.assertEqual(first.lines[0].statement.mnemonic, "CLS")
        self.assertEqual(second.lines[0].statement.mnemonic, "RET")

    def test_classic_parser_accepts_classic_instruction(self) -> None:
        isa = ClassicInstructionSetArchitecture()
        parser = ClassicParser(isa)
        parser.set_tokens(Lexer("CLS\n").tokenize())
        assembly = parser.parse()
        self.assertEqual(len(assembly.lines), 1)

    def test_classic_parser_rejects_unsupported_instruction(self) -> None:
        isa = ClassicInstructionSetArchitecture()
        parser = ClassicParser(isa)
        parser.set_tokens(Lexer("NOT_A_CHIP8_INSTRUCTION\n").tokenize())
        with self.assertRaises(ParserError):
            parser.parse()

    def test_classic_parser_accepts_lowercase_instruction(self) -> None:
        isa = ClassicInstructionSetArchitecture()
        parser = ClassicParser(isa)
        parser.set_tokens(Lexer("cls\n").tokenize())
        assembly = parser.parse()
        self.assertEqual(len(assembly.lines), 1)

    def test_base_parser_cannot_be_instantiated(self) -> None:
        with self.assertRaises(TypeError):
            Parser()

    def test_parser_does_not_validate_operand_signatures(self) -> None:
        """
        @brief Verify that operand signature validation belongs to
        semantic analysis rather than parsing.
        """
        assembly = self._parse("RND V1, V2")
        self.assertEqual(len(assembly.lines), 1)
        statement = assembly.lines[0].statement
        self.assertIsInstance(statement, InstructionNode)
        self.assertEqual(statement.mnemonic, "RND")
        self.assertEqual(len(statement.operands), 2)


