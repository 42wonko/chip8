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

    ###################################################
    # test for creatig CLS assembler instruction
    ###################################################
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

    ###################################################
    # test for creatig unknown assembler instruction
    ###################################################
    def test_create_unknown_instruction_rejects_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "NOT_AN_INSTRUCTION", ())


    ###################################################
    # test for creation assembler instruction for RET
    ###################################################
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

    ###################################################
    # test for creation assembler instruction for SYS
    ###################################################
    def test_create_sys_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x234),)
        instruction = isa.create_assembler_instruction( "SYS", operands)
        self.assertEqual( instruction.id, InstructionId.SYS)
        self.assertEqual( instruction.nnn, 0x234)

    def test_create_sys_is_case_insensitive(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x234),)
        instruction = isa.create_assembler_instruction( "sys", operands)
        self.assertEqual( instruction.id, InstructionId.SYS)
        self.assertEqual( instruction.nnn, 0x234)

    def test_create_sys_rejects_missing_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "SYS", ())

    def test_create_sys_rejects_too_many_operands(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.ADDRESS,
            value=0x234), AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x235)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "SYS", operands)

    def test_create_sys_rejects_value_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x234),)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "SYS", operands)

    def test_create_sys_rejects_register_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.REGISTER, value=0),)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "SYS", operands)

    def test_create_sys_rejects_address_above_12_bits(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x1000),)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "SYS", operands)

    def test_create_sys_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x234),)
        instruction = isa.create_assembler_instruction( "SYS", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0x0234)

    ###################################################
    # test for creation assembler instruction for JP
    ###################################################
    def test_create_jp_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x234),)
        instruction = isa.create_assembler_instruction( "JP", operands)
        self.assertEqual( instruction.id, InstructionId.JP)
        self.assertEqual( instruction.nnn, 0x234)

    def test_create_jp_is_case_insensitive(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x234),)
        instruction = isa.create_assembler_instruction( "jp", operands)
        self.assertEqual( instruction.id, InstructionId.JP)
        self.assertEqual( instruction.nnn, 0x234)

    def test_create_jp_rejects_missing_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "JP", ())

    def test_create_jp_rejects_too_many_operands(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x234),
            AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x235)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "JP", operands)

    def test_create_jp_rejects_value_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x234),)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "JP", operands)

    def test_create_jp_rejects_register_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.REGISTER, value=0),)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "JP", operands)

    def test_create_jp_rejects_address_above_12_bits(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x1000),)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "JP", operands)

    def test_create_jp_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x234),)
        instruction = isa.create_assembler_instruction( "JP", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0x1234)

    ###################################################
    # test for creation assembler instruction for CALL
    ###################################################
    def test_create_call_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x234),)
        instruction = isa.create_assembler_instruction( "CALL", operands)
        self.assertEqual( instruction.id, InstructionId.CALL)
        self.assertEqual( instruction.nnn, 0x234)

    def test_create_call_is_case_insensitive(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x234),)
        instruction = isa.create_assembler_instruction( "call", operands)
        self.assertEqual( instruction.id, InstructionId.CALL)
        self.assertEqual( instruction.nnn, 0x234)

    def test_create_call_rejects_missing_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "CALL", ())

    def test_create_call_rejects_too_many_operands(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x234),
            AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x235)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "CALL", operands)

    def test_create_call_rejects_value_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x234),)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "CALL", operands)

    def test_create_call_rejects_register_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.REGISTER, value=0),)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "CALL", operands)

    def test_create_call_rejects_address_above_12_bits(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x1000),)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "CALL", operands)

    def test_create_call_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x234),)
        instruction = isa.create_assembler_instruction( "CALL", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0x2234)
