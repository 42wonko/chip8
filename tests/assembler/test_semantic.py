"""
@file test_semantic.py

@brief Tests for assembler semantic expression evaluation.
"""

import unittest

from assembler.ast import (
    BinaryExpression,
    BinaryOperator,
    IdentifierExpression,
    LiteralExpression,
)
from assembler.semantic import ExpressionEvaluator
from assembler.symbol import SymbolTable
from assembler.token import SourceLocation


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


    def test_evaluate_undefined_identifier(self) -> None:
        expression = IdentifierExpression( name="MISSING", location=self.location,)
        with self.assertRaises(ValueError):
            self.evaluator.evaluate(expression)


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
