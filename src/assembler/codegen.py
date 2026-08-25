"""
@file codegen.py

@brief Binary code generation for the assembler.
"""

from __future__ import annotations

from typing import Protocol

from assembler.ast import (
    AssemblyNode,
    DirectiveNode,
    InstructionNode,
    LiteralExpression,
)
from assembler.instruction import AssemblerInstruction
from assembler.semantic import ExpressionEvaluator, InstructionResolver
from assembler.symbol import SymbolTable
from emulator.constants import INSTRUCTION_SIZE, PROGRAM_START


class InstructionEncoder(Protocol):
    """
    @brief Interface required to encode assembler instructions.
    """

    def encode(self, instruction: AssemblerInstruction) -> int:
        """
        @brief Encode an assembler instruction.

        @param instruction
            Instruction to encode.

        @return
            Encoded opcode.
        """


class CodeGenerator:
    """
    @brief Generates a binary ROM image from an assembly AST.
    """

    def __init__( self, symbols: SymbolTable, instruction_resolver: InstructionResolver, encoder: InstructionEncoder) -> None:
        """
        @brief Construct a code generator.
        """
        self._instruction_resolver = instruction_resolver
        self._encoder = encoder
        self._evaluator = ExpressionEvaluator(symbols)


    def generate(self, assembly: AssemblyNode) -> bytes:
        """
        @brief Generate a binary ROM image.

        The image starts at the first ORG address, or PROGRAM_START when
        no ORG directive occurs. Gaps are filled with zero bytes.
        """
        address = PROGRAM_START
        base_address = PROGRAM_START
        first_org_seen = False
        image: dict[int, int] = {}

        for source_line in assembly.lines:
            statement = source_line.statement

            if statement is None:
                continue

            if isinstance(statement, InstructionNode):
                instruction = self._instruction_resolver.resolve(statement)
                opcode = self._encoder.encode(instruction)

                self._write_word(image, address, opcode)
                address += INSTRUCTION_SIZE
                continue

            if isinstance(statement, DirectiveNode):
                name = statement.name.upper()

                if name == "TARGET":
                    continue

                if name == "EQU":
                    continue

                if name == "ORG":
                    address = self._evaluator.evaluate( statement.operands[0])
                    if not first_org_seen:
                        base_address = address
                        first_org_seen = True
                    continue

                if name == "DB":
                    address = self._emit_db( statement, address, image)
                    continue

                raise ValueError( f"Unsupported directive '{statement.name}'.")

            raise ValueError( f"Unsupported statement type: {type(statement).__name__}")

        return self._create_image(image, base_address)


    def _emit_db( self, directive: DirectiveNode, address: int, image: dict[int, int]) -> int:
        """
        @brief Emit a DB directive.

        Validation has already been performed by semantic analysis.
        """
        for operand in directive.operands:
            if isinstance(operand, LiteralExpression):
                if isinstance(operand.value, str):
                    for character in operand.value:
                        image[address] = ord(character)
                        address += 1
                    continue

            image[address] = self._evaluator.evaluate(operand)
            address += 1

        return address


    @staticmethod
    def _write_word( image: dict[int, int], address: int, opcode: int) -> None:
        """
        @brief Write a 16-bit CHIP-8 opcode in big-endian order.
        """
        image[address] = (opcode >> 8) & 0xFF
        image[address + 1] = opcode & 0xFF


    @staticmethod
    def _create_image( image: dict[int, int], base_address: int) -> bytes:
        """
        @brief Convert absolute addresses into a contiguous ROM image.
        """
        if not image:
            return b""

        highest_address = max(image)
        result = bytearray(highest_address - base_address + 1)

        for address, value in image.items():
            result[address - base_address] = value

        return bytes(result)
