"""
@file test_assembler_interface.py

@brief Tests for the assembler interface of the Classic CHIP-8 ISA.
"""

import unittest

from assembler.operand import AssemblerOperand, AssemblerOperandType
from chip8.isa.classicisa import ClassicInstructionSetArchitecture
from chip8.isa.instructionid import InstructionId
from tests.helpers import create_machine


class ClassicInstructionSetArchitectureAssemblerTest(unittest.TestCase):
    """
    @brief Tests for Classic CHIP-8 assembler instruction construction.
    """
    def test_create_cls_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        instruction = isa.create_assembler_instruction( "CLS", ())
        self.assertEqual( instruction.id, InstructionId.CLS)
        self.assertIsNone( instruction.x)
        self.assertIsNone( instruction.y)
        self.assertIsNone( instruction.n)
        self.assertIsNone( instruction.nn)
        self.assertIsNone( instruction.nnn)

    def test_create_cls_is_case_insensitive(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        instruction = isa.create_assembler_instruction( "cls", ())
        self.assertEqual( instruction.id, InstructionId.CLS)

    def test_create_cls_rejects_operands(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.VALUE, value=0))
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "CLS", operands)

    def test_create_unknown_instruction_rejects_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "NOT_AN_INSTRUCTION", ())


    def test_create_ret_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)

        instruction = isa.create_assembler_instruction( "RET", ())

        self.assertEqual( instruction.id, InstructionId.RET)
        self.assertIsNone( instruction.x)
        self.assertIsNone( instruction.y)
        self.assertIsNone( instruction.n)
        self.assertIsNone( instruction.nn)
        self.assertIsNone( instruction.nnn)

    def test_create_ret_is_case_insensitive(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        instruction = isa.create_assembler_instruction( "ret", ())
        self.assertEqual( instruction.id, InstructionId.RET)

    def test_create_ret_rejects_operands(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.VALUE, value=0))
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "RET", operands)

    def test_create_ret_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        instruction = isa.create_assembler_instruction( "RET", ())
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0x00EE)

