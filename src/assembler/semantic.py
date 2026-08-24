"""
@file semantic.py

@brief Semantic analysis and expression evaluation for the assembler.
"""

from __future__ import annotations

from typing import Protocol

from assembler.ast import (
    AssemblyNode,
    BinaryExpression,
    BinaryOperator,
    DirectiveNode,
    Expression,
    IdentifierExpression,
    InstructionNode,
    LiteralExpression,
    SourceLine,
)
from assembler.instruction import AssemblerInstruction
from assembler.operand import AssemblerOperand, AssemblerOperandType
from assembler.symbol import SymbolTable
from emulator.constants import INSTRUCTION_SIZE, PROGRAM_START


class SymbolCollector:
    """
    @brief Collects symbols defined by an assembly AST.
    """

    def __init__(self, symbols: SymbolTable) -> None:
        """
        @brief Construct a symbol collector.

        @param symbols
            Symbol table to populate.
        """
        self._symbols = symbols


    def collect(self, assembly: AssemblyNode) -> None:
        """
        @brief Collect symbols from an assembly AST.

        @param assembly
            Parsed assembly source.
        """
        address = PROGRAM_START
        evaluator = ExpressionEvaluator(self._symbols)

        for source_line in assembly.lines:
            statement = source_line.statement

            if isinstance(statement, DirectiveNode):
                name = statement.name.upper()
                if name == "EQU":
                    self._define_equ(source_line, evaluator)
                    continue
                if name == "ORG":
                    address = self._resolve_org(statement, evaluator)
                    continue
                if source_line.label is not None:
                    self._symbols.define( source_line.label.name, address, source_line.label.location)
                if name == "DB":
                    address += self._resolve_db_size(statement, evaluator)
                    continue
                if name == "TARGET":
                    continue
                raise ValueError( f"Unsupported directive '{statement.name}'.")
            if source_line.label is not None:
                self._symbols.define( source_line.label.name, address, source_line.label.location)
            if statement is None:
                continue
            if isinstance(statement, InstructionNode):
                address += INSTRUCTION_SIZE
                continue
            raise ValueError( f"Unsupported statement type: {type(statement).__name__}")

    ###########################################################################
    # private helper functions
    ###########################################################################
    def _resolve_org( self, directive: DirectiveNode, evaluator: ExpressionEvaluator) -> int:
        """
        @brief Resolve an ORG directive.

        @param directive
            ORG directive.

        @param evaluator
            Expression evaluator used to resolve the address.

        @return
            New assembly address.
        """
        if len(directive.operands) != 1:
            raise ValueError("ORG requires exactly one operand.")
        try:
            address = evaluator.evaluate(directive.operands[0])
        except ValueError as error:
            raise ValueError( "ORG operand must be an evaluatable integer expression.") from error
        if not 0 <= address <= 0xFFFF:
            raise ValueError( "ORG address must be in the range 0x0000 to 0xFFFF.")
        return address

    def _define_equ( self, source_line: SourceLine, evaluator: ExpressionEvaluator) -> None:
        """
        @brief Define a symbol using an EQU directive.
        """
        statement = source_line.statement
        if not isinstance(statement, DirectiveNode):
            raise ValueError("EQU requires a directive statement.")
        if source_line.label is None:
            raise ValueError("EQU requires a label.")
        if len(statement.operands) != 1:
            raise ValueError("EQU requires exactly one operand.")
        value = evaluator.evaluate(statement.operands[0])
        self._symbols.define( source_line.label.name, value, source_line.label.location)


    def _resolve_db_size( self, directive: DirectiveNode, evaluator: ExpressionEvaluator) -> int:
        """
        @brief Validate a DB directive and return its emitted byte count.
        """
        if len(directive.operands) == 0:
            raise ValueError("DB requires at least one operand.")
        size = 0
        for operand in directive.operands:
            if isinstance(operand, LiteralExpression):
                if isinstance(operand.value, str):
                    for character in operand.value:
                        if ord(character) > 0xFF:
                            raise ValueError( "DB string contains a character outside the byte range.")
                    size += len(operand.value)
                    continue
            value = evaluator.evaluate(operand)
            if not 0 <= value <= 0xFF:
                raise ValueError( f"DB value {value} is outside the range 0x00 to 0xFF.")
            size += 1
        return size


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
            if not isinstance(expression.value, int):
                raise ExpressionEvaluationError( "String literals cannot be evaluated as integers.")
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



class OperandResolver:
    """
    @brief Resolves assembler expressions into typed operands.
    """

    def __init__(self, symbols: SymbolTable) -> None:
        """
        @brief Construct an operand resolver.

        @param symbols
            Symbol table used to resolve identifiers.
        """
        self._evaluator = ExpressionEvaluator(symbols)
        self._symbols = symbols


    def resolve( self, expression: Expression, operand_type: AssemblerOperandType) -> AssemblerOperand:
        """
        @brief Resolve an expression into an assembler operand.

        @param expression
            Operand expression from the assembler AST.

        @param operand_type
            Required assembler operand type.

        @return
            Resolved assembler operand.

        @exception ExpressionEvaluationError
            If the expression cannot represent the requested operand.
        """
        if isinstance(expression, IdentifierExpression):
            return self._resolve_identifier(expression, operand_type)

        if isinstance(expression, BinaryExpression):
            value = self._evaluator.evaluate(expression)
            return self._resolve_value(value, operand_type)

        if isinstance(expression, LiteralExpression):
            if not isinstance(expression.value, int):
                raise ExpressionEvaluationError( "String literals cannot be used as instruction operands.")
            return self._resolve_value(expression.value, operand_type)

        raise ExpressionEvaluationError( f"Unsupported operand expression type: " f"{type(expression).__name__}")


    def _resolve_identifier( self, expression: IdentifierExpression, operand_type: AssemblerOperandType) -> AssemblerOperand:
        """
        @brief Resolve an identifier operand.
        """
        name = expression.name.upper()

        special_operands = {
            "I": AssemblerOperandType.INDEX_REGISTER,
            "DT": AssemblerOperandType.DELAY_REGISTER,
            "ST": AssemblerOperandType.SOUND_REGISTER,
            "K": AssemblerOperandType.KEY,
            "F": AssemblerOperandType.FONT_REGISTER,
            "B": AssemblerOperandType.BCD_REGISTER
        }

        if name in special_operands:
            actual_type = special_operands[name]
            if actual_type != operand_type:
                raise ExpressionEvaluationError( f"Operand '{expression.name}' has type " f"{actual_type.value}, expected {operand_type.value}.")
            return AssemblerOperand(type=actual_type, value=0)

        if name.startswith("V") and len(name) == 2:
            try:
                register = int(name[1], 16)
            except ValueError:
                register = -1
            if 0 <= register <= 0xF:
                if operand_type != AssemblerOperandType.REGISTER:
                    raise ExpressionEvaluationError( f"Register '{expression.name}' is not valid as {operand_type.value}.")
                return AssemblerOperand( type=AssemblerOperandType.REGISTER, value=register)
        if self._symbols.contains(name):
            value = self._evaluator.evaluate(expression)
            return self._resolve_value(value, operand_type)
        raise ExpressionEvaluationError( f"Unknown assembler operand '{expression.name}'.")


    def _resolve_value( self, value: int, operand_type: AssemblerOperandType) -> AssemblerOperand:
        """
        @brief Resolve an evaluated integer according to its required type.
        """
        if operand_type not in ( AssemblerOperandType.VALUE, AssemblerOperandType.ADDRESS):
            raise ExpressionEvaluationError( f"Integer value cannot be resolved as {operand_type.value}.")
        return AssemblerOperand( type=operand_type, value=value)

class AssemblerInstructionFactory(Protocol):
    """
    @brief Interface required by InstructionResolver to create instructions.
    """
    def create_assembler_instruction( self, mnemonic: str, operands: tuple[AssemblerOperand, ...]) -> AssemblerInstruction:
        """
        @brief Create an assembler instruction from resolved operands.
        """


class InstructionResolver:
    """
    @brief Resolves parsed instructions into assembler instructions.
    """

    def __init__( self, symbols: SymbolTable, isa: AssemblerInstructionFactory) -> None:
        """
        @brief Construct an instruction resolver.

        @param symbols
            Symbol table used to resolve operands.

        @param isa
            Instruction-set architecture used to create the instruction.
        """
        self._operand_resolver = OperandResolver(symbols)
        self._isa = isa

    def resolve(self, instruction: InstructionNode) -> AssemblerInstruction:
        """
        @brief Resolve an instruction AST node.

        @param instruction
            Parsed instruction.

        @return
            Assembler instruction.

        @exception ExpressionEvaluationError
            If the instruction cannot be resolved.
        """
        signatures = self._get_signatures( instruction.mnemonic, len(instruction.operands))

        if not signatures:
            raise ExpressionEvaluationError( f"Unsupported instruction '{instruction.mnemonic}'.")
        last_error: ExpressionEvaluationError | None = None
        for signature in signatures:
            try:
                operands = self._resolve_operands( instruction.operands, signature)
            except ExpressionEvaluationError as error:
                last_error = error
                continue
            try:
                return self._isa.create_assembler_instruction( instruction.mnemonic, operands)
            except ValueError as error:
                last_error = ExpressionEvaluationError(str(error))
        if last_error is not None:
            raise last_error
        raise ExpressionEvaluationError( f"Invalid operands for instruction '{instruction.mnemonic}'.")

    def _resolve_operands( self, expressions: tuple[Expression, ...], operand_types: tuple[AssemblerOperandType, ...]) -> tuple[AssemblerOperand, ...]:
        """
        @brief Resolve expressions according to one operand signature.
        """
        if len(expressions) != len(operand_types):
            raise ExpressionEvaluationError("Operand count does not match signature.")
        return tuple(
            self._operand_resolver.resolve(expression, operand_type)
            for expression, operand_type in zip(expressions, operand_types)
        )

    def _get_signatures( self, mnemonic: str, operand_count: int) -> tuple[tuple[AssemblerOperandType, ...], ...]:
        """
        @brief Return legal operand signatures for a mnemonic.
        """
        name = mnemonic.upper()
        if name in ("CLS", "RET"):
            return ((),) if operand_count == 0 else ()
        if name == "SYS":
            return self._signatures( operand_count, (AssemblerOperandType.ADDRESS,))
        if name == "JP":
            if operand_count == 1:
                return ( (AssemblerOperandType.ADDRESS,),)
            if operand_count == 2:
                return ( ( AssemblerOperandType.REGISTER, AssemblerOperandType.ADDRESS),)
            return ()
        if name == "CALL":
            return self._signatures( operand_count, (AssemblerOperandType.ADDRESS,))
        if name in ("SE", "SNE"):
            return self._signatures(
                operand_count,
                (AssemblerOperandType.REGISTER, AssemblerOperandType.VALUE),
                (AssemblerOperandType.REGISTER, AssemblerOperandType.REGISTER)
            )
        if name == "LD":
            return self._signatures(
                operand_count,
                (AssemblerOperandType.REGISTER, AssemblerOperandType.REGISTER),
                (AssemblerOperandType.REGISTER, AssemblerOperandType.VALUE),
                (AssemblerOperandType.INDEX_REGISTER, AssemblerOperandType.ADDRESS),
                (AssemblerOperandType.REGISTER, AssemblerOperandType.DELAY_REGISTER),
                (AssemblerOperandType.REGISTER, AssemblerOperandType.KEY),
                (AssemblerOperandType.DELAY_REGISTER, AssemblerOperandType.REGISTER),
                (AssemblerOperandType.SOUND_REGISTER, AssemblerOperandType.REGISTER),
                (AssemblerOperandType.REGISTER, AssemblerOperandType.BCD_REGISTER),
                (AssemblerOperandType.REGISTER, AssemblerOperandType.FONT_REGISTER),
                (AssemblerOperandType.REGISTER, AssemblerOperandType.INDEX_REGISTER)
            )
        if name == "ADD":
            return self._signatures(
                operand_count,
                (AssemblerOperandType.REGISTER, AssemblerOperandType.VALUE),
                (AssemblerOperandType.REGISTER, AssemblerOperandType.REGISTER),
                (AssemblerOperandType.INDEX_REGISTER, AssemblerOperandType.REGISTER)
            )
        if name in ("OR", "AND", "XOR", "SUB", "SHR", "SUBN", "SHL"):
            return self._signatures(
                operand_count,
                (AssemblerOperandType.REGISTER, AssemblerOperandType.REGISTER)
            )
        if name in ("SKP", "SKNP"):
            return self._signatures( operand_count, (AssemblerOperandType.REGISTER,))
        return ()

    @staticmethod
    def _signatures( operand_count: int, *signatures: tuple[AssemblerOperandType, ...]) -> tuple[tuple[AssemblerOperandType, ...], ...]:
        """
        @brief Filter operand signatures by operand count.
        """
        return tuple( signature for signature in signatures if len(signature) == operand_count)


