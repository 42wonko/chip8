"""
@file ast.py

@brief Abstract syntax tree definitions for the assembler.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from assembler.token import SourceLocation


class ExpressionType(Enum):
    """
    @brief Types of expressions in the assembler AST.
    """

    LITERAL = "LITERAL"
    IDENTIFIER = "IDENTIFIER"
    BINARY = "BINARY"


@dataclass(frozen=True, slots=True)
class Expression:
    """
    @brief Base class for assembler expressions.
    """

    type: ExpressionType
    location: SourceLocation


@dataclass(frozen=True, slots=True)
class LiteralExpression(Expression):
    """
    @brief Literal value expression.

    @details
    Numeric and character literals are represented by integer values.
    String literals are represented by string values.

    No ISA-specific range validation is performed here.
    """

    value: int | str

    def __init__(
        self,
        value: int | str,
        location: SourceLocation
    ) -> None:
        object.__setattr__(
            self,
            "type",
            ExpressionType.LITERAL
        )
        object.__setattr__(
            self,
            "location",
            location
        )
        object.__setattr__(
            self,
            "value",
            value
        )


@dataclass(frozen=True, slots=True)
class IdentifierExpression(Expression):
    """
    @brief Identifier or register reference expression.
    """

    name: str

    def __init__(
        self,
        name: str,
        location: SourceLocation
    ) -> None:
        object.__setattr__(
            self,
            "type",
            ExpressionType.IDENTIFIER
        )
        object.__setattr__(
            self,
            "location",
            location
        )
        object.__setattr__(
            self,
            "name",
            name
        )


class BinaryOperator(Enum):
    """
    @brief Operators supported by binary expressions.
    """

    ADD = "+"
    SUBTRACT = "-"


@dataclass(frozen=True, slots=True)
class BinaryExpression(Expression):
    """
    @brief Binary arithmetic expression.
    """

    operator: BinaryOperator
    left: Expression
    right: Expression

    def __init__(
        self,
        operator: BinaryOperator,
        left: Expression,
        right: Expression,
        location: SourceLocation
    ) -> None:
        object.__setattr__(
            self,
            "type",
            ExpressionType.BINARY
        )
        object.__setattr__(
            self,
            "location",
            location
        )
        object.__setattr__(
            self,
            "operator",
            operator
        )
        object.__setattr__(
            self,
            "left",
            left
        )
        object.__setattr__(
            self,
            "right",
            right
        )


@dataclass(frozen=True, slots=True)
class InstructionNode:
    """
    @brief Instruction in the assembler source.
    """

    mnemonic: str
    operands: tuple[Expression, ...]
    location: SourceLocation


@dataclass(frozen=True, slots=True)
class LabelNode:
    """
    @brief Label declaration in the assembler source.
    """

    name: str
    location: SourceLocation


@dataclass(frozen=True, slots=True)
class DirectiveNode:
    """
    @brief Assembler directive.
    """

    name: str
    operands: tuple[Expression, ...]
    location: SourceLocation


@dataclass(frozen=True, slots=True)
class SourceLine:
    """
    @brief One parsed source line.
    """

    label: LabelNode | None
    statement: InstructionNode | DirectiveNode | None


@dataclass(frozen=True, slots=True)
class AssemblyNode:
    """
    @brief Root node of the assembler AST.
    """

    lines: tuple[SourceLine, ...]
