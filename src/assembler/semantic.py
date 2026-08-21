"""
@file semantic.py

@brief Semantic analysis and expression evaluation for the assembler.
"""

from __future__ import annotations
#from enum import Enum
from assembler.operand import AssemblerOperand, AssemblerOperandType
from assembler.ast import BinaryExpression, BinaryOperator, Expression, IdentifierExpression, LiteralExpression
from assembler.symbol import SymbolTable


class ExpressionEvaluationError(ValueError):
    """
    @brief Raised when an assembler expression cannot be evaluated.
    """


class ExpressionEvaluator:
    """
    @brief Evaluates assembler AST expressions.
    """

    def __init__(self, symbols: SymbolTable) -> None:
        """
        @brief Construct an expression evaluator.

        @param symbols
            Symbol table used to resolve identifiers.
        """
        self._symbols = symbols


    def evaluate(self, expression: Expression) -> int:
        """
        @brief Evaluate an expression to an integer value.

        @param expression
            Expression to evaluate.

        @return
            Evaluated integer value.

        @exception ExpressionEvaluationError
            If the expression type is unsupported.
        """
        if isinstance(expression, LiteralExpression):
            return expression.value
        if isinstance(expression, IdentifierExpression):
            return self._symbols.lookup(expression.name).value
        if isinstance(expression, BinaryExpression):
            return self._evaluate_binary(expression)
        raise ExpressionEvaluationError( f"Unsupported expression type: {type(expression).__name__}")


    def _evaluate_binary(self, expression: BinaryExpression) -> int:
        """
        @brief Evaluate a binary expression.
        """
        left = self.evaluate(expression.left)
        right = self.evaluate(expression.right)
        if expression.operator == BinaryOperator.ADD:
            return left + right
        if expression.operator == BinaryOperator.SUBTRACT:
            return left - right
        raise ExpressionEvaluationError( f"Unsupported binary operator: {expression.operator}")


    #######################################################################
    # private helper functions
    #######################################################################
 
