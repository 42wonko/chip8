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
    # test for creation assembler instruction for JP
    ###################################################
    def test_create_jp_v0_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x234)
        )
        instruction = isa.create_assembler_instruction( "JP", operands)
        self.assertEqual( instruction.id, InstructionId.JP_V0)
        self.assertEqual( instruction.nnn, 0x234)

    def test_create_jp_v0_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x234)
        )
        instruction = isa.create_assembler_instruction( "JP", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0xB234)

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

    ###################################################
    # test for creation assembler instruction for LD Vx, <byte>
    ###################################################
    def test_create_ld_vx_nn_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x42)
        )
        instruction = isa.create_assembler_instruction( "LD", operands)
        self.assertEqual( instruction.id, InstructionId.LD_BYTE)
        self.assertEqual( instruction.x, 3)
        self.assertEqual( instruction.nn, 0x42)

    def test_create_ld_vx_nn_is_case_insensitive(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x42)
        )
        instruction = isa.create_assembler_instruction( "ld", operands)
        self.assertEqual( instruction.id, InstructionId.LD_BYTE)

    def test_create_ld_vx_nn_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x42)
        )
        instruction = isa.create_assembler_instruction( "LD", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0x6342)

    def test_create_ld_vx_nn_rejects_missing_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    def test_create_ld_vx_nn_rejects_too_many_operands(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x42),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x43)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    def test_create_ld_vx_nn_rejects_non_register_first_operand( self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x42)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    def test_create_ld_vx_nn_rejects_non_value_second_operand( self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x42)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    def test_create_ld_vx_nn_rejects_value_above_8_bits(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x100)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    def test_create_ld_vx_nn_rejects_register_above_vf(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=0x10),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x42)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    ###################################################
    # test for creation assembler instruction for LD Vx, Vy
    ###################################################
    def test_create_ld_vx_vy_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=7)
        )
        instruction = isa.create_assembler_instruction( "LD", operands)
        self.assertEqual( instruction.id, InstructionId.LD_REGISTER)
        self.assertEqual( instruction.x, 3)
        self.assertEqual( instruction.y, 7)

    def test_create_ld_vx_vy_is_case_insensitive(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=7)
        )
        instruction = isa.create_assembler_instruction( "ld", operands)
        self.assertEqual( instruction.id, InstructionId.LD_REGISTER)

    def test_create_ld_vx_vy_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=7)
        )
        instruction = isa.create_assembler_instruction( "LD", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0x8370)

    def test_create_ld_vx_vy_rejects_non_register_first_operand( self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=7)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    def test_create_ld_vx_vy_rejects_non_register_second_operand( self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=7)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    def test_create_ld_vx_vy_rejects_first_register_above_vf( self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=0x10),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=7)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    def test_create_ld_vx_vy_rejects_second_register_above_vf( self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=0x10)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    ###################################################
    # test for creation assembler instruction for LD I, <add>
    ###################################################
    def test_create_ld_i_nnn_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.INDEX_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x234)
        )
        instruction = isa.create_assembler_instruction( "LD", operands)
        self.assertEqual( instruction.id, InstructionId.LD_I)
        self.assertEqual( instruction.nnn, 0x234)

    def test_create_ld_i_nnn_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.INDEX_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x234)
        )
        instruction = isa.create_assembler_instruction( "LD", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0xA234)

    def test_create_ld_i_nnn_is_case_insensitive(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.INDEX_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x234)
        )
        instruction = isa.create_assembler_instruction( "ld", operands)
        self.assertEqual( instruction.id, InstructionId.LD_I)

    def test_create_ld_i_nnn_rejects_general_register(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x234)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    def test_create_ld_i_nnn_rejects_value(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.INDEX_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x234)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    def test_create_ld_i_nnn_rejects_address_above_12_bits(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.INDEX_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x1000)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    ###################################################
    # test for creation assembler instruction for LD Vx, DT
    ###################################################
    def test_create_ld_vx_dt_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.DELAY_REGISTER, value=0)
        )
        instruction = isa.create_assembler_instruction( "LD", operands)
        self.assertEqual( instruction.id, InstructionId.LD_VX_DT)
        self.assertEqual( instruction.x, 3)

    def test_create_ld_vx_dt_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.DELAY_REGISTER, value=0)
        )
        instruction = isa.create_assembler_instruction( "LD", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0xF307)

    def test_create_ld_vx_dt_is_case_insensitive(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.DELAY_REGISTER, value=0)
        )
        instruction = isa.create_assembler_instruction( "ld", operands)
        self.assertEqual( instruction.id, InstructionId.LD_VX_DT)

    def test_create_ld_vx_dt_rejects_sound_register_source(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.SOUND_REGISTER, value=0)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    def test_create_ld_vx_dt_rejects_register_above_vf(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=0x10),
            AssemblerOperand( type=AssemblerOperandType.DELAY_REGISTER, value=0)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    ###################################################
    # test for creation assembler instruction for LD Vx, K
    ###################################################
    def test_create_ld_vx_k_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.KEY, value=0)
        )
        instruction = isa.create_assembler_instruction( "LD", operands)
        self.assertEqual( instruction.id, InstructionId.LD_VX_K)
        self.assertEqual( instruction.x, 3)

    def test_create_ld_vx_k_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.KEY, value=0)
        )
        instruction = isa.create_assembler_instruction( "LD", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0xF30A)

    def test_create_ld_vx_k_is_case_insensitive(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.KEY, value=0)
        )
        instruction = isa.create_assembler_instruction( "ld", operands)
        self.assertEqual( instruction.id, InstructionId.LD_VX_K)

    def test_create_ld_vx_k_rejects_sound_register(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.SOUND_REGISTER, value=0)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    def test_create_ld_vx_k_rejects_register_above_vf(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=0x10),
            AssemblerOperand( type=AssemblerOperandType.KEY, value=0)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    def test_create_ld_vx_k_rejects_wrong_operand_combination( self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=3),
            AssemblerOperand( type=AssemblerOperandType.KEY, value=0)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    ###################################################
    # test for creation assembler instruction for LD DT, Vx
    ###################################################
    def test_create_ld_dt_vx_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.DELAY_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3)
        )
        instruction = isa.create_assembler_instruction( "LD", operands)
        self.assertEqual( instruction.id, InstructionId.LD_DT_VX)
        self.assertEqual( instruction.x, 3)

    def test_create_ld_dt_vx_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.DELAY_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3)
        )
        instruction = isa.create_assembler_instruction( "LD", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0xF315)

    def test_create_ld_dt_vx_is_case_insensitive(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.DELAY_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3)
        )
        instruction = isa.create_assembler_instruction( "ld", operands)
        self.assertEqual( instruction.id, InstructionId.LD_DT_VX)

    def test_create_ld_dt_vx_rejects_value_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.DELAY_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=3)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    def test_create_ld_dt_vx_rejects_register_above_vf(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.DELAY_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=0x10)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    ###################################################
    # test for creation assembler instruction for LD ST, Vx
    ###################################################
    def test_create_ld_st_vx_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.SOUND_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3)
        )
        instruction = isa.create_assembler_instruction( "LD", operands)
        self.assertEqual( instruction.id, InstructionId.LD_ST_VX)
        self.assertEqual( instruction.x, 3)

    def test_create_ld_st_vx_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.SOUND_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3)
        )
        instruction = isa.create_assembler_instruction( "LD", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0xF318)

    def test_create_ld_st_vx_is_case_insensitive(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.SOUND_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3)
        )
        instruction = isa.create_assembler_instruction( "ld", operands)
        self.assertEqual( instruction.id, InstructionId.LD_ST_VX)

    def test_create_ld_st_vx_rejects_register_above_vf(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.SOUND_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=0x10)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    def test_create_ld_st_vx_rejects_value_destination(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    ###################################################
    # test for creation assembler instruction for LD B, Vx
    ###################################################
    def test_create_ld_b_vx_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.BCD_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3)
        )
        instruction = isa.create_assembler_instruction( "LD", operands)
        self.assertEqual( instruction.id, InstructionId.LD_B_VX)
        self.assertEqual( instruction.x, 3)

    def test_create_ld_b_vx_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.BCD_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3)
        )
        instruction = isa.create_assembler_instruction( "LD", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0xF333)

    def test_create_ld_b_vx_is_case_insensitive(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.BCD_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3)
        )
        instruction = isa.create_assembler_instruction( "ld", operands)
        self.assertEqual( instruction.id, InstructionId.LD_B_VX)

    def test_create_ld_b_vx_rejects_register_above_vf(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.BCD_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=0x10)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    def test_create_ld_b_vx_rejects_value_source(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.BCD_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=3)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    ###################################################
    # test for creation assembler instruction for LD F, Vx
    ###################################################
    def test_create_ld_f_vx_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.FONT_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3)
        )
        instruction = isa.create_assembler_instruction( "LD", operands)
        self.assertEqual( instruction.id, InstructionId.LD_F_VX)
        self.assertEqual( instruction.x, 3)

    def test_create_ld_f_vx_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.FONT_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3)
        )
        instruction = isa.create_assembler_instruction( "LD", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0xF329)

    def test_create_ld_f_vx_is_case_insensitive(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.FONT_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3)
        )
        instruction = isa.create_assembler_instruction( "ld", operands)
        self.assertEqual( instruction.id, InstructionId.LD_F_VX)

    def test_create_ld_f_vx_rejects_register_above_vf(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.FONT_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=0x10)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    def test_create_ld_f_vx_rejects_value_source(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.FONT_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=3)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "LD", operands)

    def test_create_ld_i_vx_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)

        operands = (
            AssemblerOperand(
                type=AssemblerOperandType.INDEX_REGISTER,
                value=0
            ),
            AssemblerOperand(
                type=AssemblerOperandType.REGISTER,
                value=3
            )
        )

        instruction = isa.create_assembler_instruction(
            "LD",
            operands
        )

        self.assertEqual(
            instruction.id,
            InstructionId.LD_I_VX
        )
        self.assertEqual(
            instruction.x,
            3
        )

    def test_create_ld_i_vx_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)

        operands = (
            AssemblerOperand(
                type=AssemblerOperandType.INDEX_REGISTER,
                value=0
            ),
            AssemblerOperand(
                type=AssemblerOperandType.REGISTER,
                value=3
            )
        )

        instruction = isa.create_assembler_instruction(
            "LD",
            operands
        )

        opcode = isa.encode(instruction)

        self.assertEqual(
            opcode,
            0xF355
        )

    def test_create_ld_i_vx_is_case_insensitive(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)

        operands = (
            AssemblerOperand(
                type=AssemblerOperandType.INDEX_REGISTER,
                value=0
            ),
            AssemblerOperand(
                type=AssemblerOperandType.REGISTER,
                value=3
            )
        )

        instruction = isa.create_assembler_instruction(
            "ld",
            operands
        )

        self.assertEqual(
            instruction.id,
            InstructionId.LD_I_VX
        )

    def test_create_ld_i_vx_rejects_register_above_vf(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)

        operands = (
            AssemblerOperand(
                type=AssemblerOperandType.INDEX_REGISTER,
                value=0
            ),
            AssemblerOperand(
                type=AssemblerOperandType.REGISTER,
                value=0x10
            )
        )

        with self.assertRaises(ValueError):
            isa.create_assembler_instruction(
                "LD",
                operands
            )

    def test_create_ld_vx_i_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)

        operands = (
            AssemblerOperand(
                type=AssemblerOperandType.REGISTER,
                value=3
            ),
            AssemblerOperand(
                type=AssemblerOperandType.INDEX_REGISTER,
                value=0
            )
        )

        instruction = isa.create_assembler_instruction(
            "LD",
            operands
        )

        self.assertEqual(
            instruction.id,
            InstructionId.LD_VX_I
        )
        self.assertEqual(
            instruction.x,
            3
        )

    def test_create_ld_vx_i_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)

        operands = (
            AssemblerOperand(
                type=AssemblerOperandType.REGISTER,
                value=3
            ),
            AssemblerOperand(
                type=AssemblerOperandType.INDEX_REGISTER,
                value=0
            )
        )

        instruction = isa.create_assembler_instruction(
            "LD",
            operands
        )

        opcode = isa.encode(instruction)

        self.assertEqual(
            opcode,
            0xF365
        )

    def test_create_ld_vx_i_is_case_insensitive(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)

        operands = (
            AssemblerOperand(
                type=AssemblerOperandType.REGISTER,
                value=3
            ),
            AssemblerOperand(
                type=AssemblerOperandType.INDEX_REGISTER,
                value=0
            )
        )

        instruction = isa.create_assembler_instruction(
            "ld",
            operands
        )

        self.assertEqual(
            instruction.id,
            InstructionId.LD_VX_I
        )

    def test_create_ld_vx_i_rejects_register_above_vf(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)

        operands = (
            AssemblerOperand(
                type=AssemblerOperandType.REGISTER,
                value=0x10
            ),
            AssemblerOperand(
                type=AssemblerOperandType.INDEX_REGISTER,
                value=0
            )
        )

        with self.assertRaises(ValueError):
            isa.create_assembler_instruction(
                "LD",
                operands
            )



    ###################################################
    # test for creation assembler instruction for ADD
    ###################################################
    def test_create_add_i_vx_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.INDEX_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3)
        )
        instruction = isa.create_assembler_instruction( "ADD", operands)
        self.assertEqual( instruction.id, InstructionId.ADD_I_VX)
        self.assertEqual( instruction.x, 3)

    def test_create_add_i_vx_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.INDEX_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3)
        )
        instruction = isa.create_assembler_instruction( "ADD", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0xF31E)

    def test_create_add_i_vx_is_case_insensitive(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.INDEX_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3)
        )
        instruction = isa.create_assembler_instruction( "add", operands)
        self.assertEqual( instruction.id, InstructionId.ADD_I_VX)

    def test_create_add_i_vx_rejects_register_above_vf(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.INDEX_REGISTER, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=0x10)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "ADD", operands)

    def test_create_add_i_vx_rejects_value_as_first_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "ADD", operands)

    def test_create_add_vx_value_remains_add_byte(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=5)
        )
        instruction = isa.create_assembler_instruction( "ADD", operands)
        self.assertEqual( instruction.id, InstructionId.ADD_BYTE)
        self.assertEqual( instruction.x, 3)
        self.assertEqual( instruction.nn, 5)


    ###################################################
    # test for creation assembler instruction for SKp Vx
    ###################################################
    def test_create_skp_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),)
        instruction = isa.create_assembler_instruction( "SKP", operands)
        self.assertEqual( instruction.id, InstructionId.SKP)
        self.assertEqual( instruction.x, 3)

    def test_create_skp_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),)
        instruction = isa.create_assembler_instruction( "SKP", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0xE39E)

    def test_create_skp_is_case_insensitive(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),)
        instruction = isa.create_assembler_instruction( "skp", operands)
        self.assertEqual( instruction.id, InstructionId.SKP)

    def test_create_skp_rejects_register_above_vf(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.REGISTER, value=0x10),)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "SKP", operands)

    def test_create_skp_rejects_value_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.VALUE, value=3),)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "SKP", operands)

    def test_create_skp_rejects_missing_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "SKP", ())

    ###################################################
    # test for creation assembler instruction for SKp Vx
    ###################################################
    def test_create_sknp_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),)
        instruction = isa.create_assembler_instruction( "SKNP", operands)
        self.assertEqual( instruction.id, InstructionId.SKNP)
        self.assertEqual( instruction.x, 3)

    def test_create_sknp_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),)
        instruction = isa.create_assembler_instruction( "SKNP", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0xE3A1)

    def test_create_sknp_is_case_insensitive(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),)
        instruction = isa.create_assembler_instruction( "sknp", operands)
        self.assertEqual( instruction.id, InstructionId.SKNP)

    def test_create_sknp_rejects_register_above_vf(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.REGISTER, value=0x10),)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "SKNP", operands)

    def test_create_sknp_rejects_value_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.VALUE, value=3),)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "SKNP", operands)

    ###################################################
    # test for creation assembler instruction for SKp Vx
    ###################################################
    def test_create_se_vx_byte_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=5)
        )
        instruction = isa.create_assembler_instruction( "SE", operands)
        self.assertEqual( instruction.id, InstructionId.SE_BYTE)
        self.assertEqual( instruction.x, 3)
        self.assertEqual( instruction.nn, 5)

    def test_create_se_vx_byte_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=5)
        )
        instruction = isa.create_assembler_instruction( "SE", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0x3305)

    def test_create_se_vx_vy_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=5)
        )
        instruction = isa.create_assembler_instruction( "SE", operands)
        self.assertEqual( instruction.id, InstructionId.SE_REGISTER)
        self.assertEqual( instruction.x, 3)
        self.assertEqual( instruction.y, 5)

    def test_create_se_vx_vy_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=5)
        )
        instruction = isa.create_assembler_instruction( "SE", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0x5350)

    def test_create_se_rejects_address_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x234)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "SE", operands)

    def test_create_se_rejects_register_above_vf(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=0x10),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=5)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "SE", operands)

    ###################################################
    # test for creation assembler instruction for SKp Vx
    ###################################################
    def test_create_sne_vx_byte_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=5)
        )
        instruction = isa.create_assembler_instruction( "SNE", operands)
        self.assertEqual( instruction.id, InstructionId.SNE_BYTE)
        self.assertEqual( instruction.x, 3)
        self.assertEqual( instruction.nn, 5)

    def test_create_sne_vx_byte_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=5)
        )
        instruction = isa.create_assembler_instruction( "SNE", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0x4305)

    def test_create_sne_vx_vy_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=5)
        )
        instruction = isa.create_assembler_instruction( "SNE", operands)
        self.assertEqual( instruction.id, InstructionId.SNE_REGISTER)
        self.assertEqual( instruction.x, 3)
        self.assertEqual( instruction.y, 5)

    def test_create_sne_vx_vy_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=5)
        )
        instruction = isa.create_assembler_instruction( "SNE", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0x9350)

    ###################################################
    # test for creation assembler instruction for OR Vx, Vy
    ###################################################
    def test_create_or_vx_vy_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=5)
        )
        instruction = isa.create_assembler_instruction( "OR", operands)
        self.assertEqual( instruction.id, InstructionId.OR)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0x8351)

    def test_create_or_rejects_value_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=5)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "OR", operands)

    ###################################################
    # test for creation assembler instruction for AND Vx, Vy
    ###################################################
    def test_create_and_vx_vy_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=5)
        )
        instruction = isa.create_assembler_instruction( "AND", operands)
        self.assertEqual( instruction.id, InstructionId.AND)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0x8352)

    def test_create_and_rejects_value_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=5)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "AND", operands)

    ###################################################
    # test for creation assembler instruction for XOR Vx, Vy
    ###################################################
    def test_create_xor_vx_vy_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=5)
        )
        instruction = isa.create_assembler_instruction( "XOR", operands)
        self.assertEqual( instruction.id, InstructionId.XOR)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0x8353)

    def test_create_xor_rejects_value_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=5)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "XOR", operands)

    ###################################################
    # test for creation assembler instruction for ADD Vx, Vy
    ###################################################
    def test_create_add_vx_vy_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=5)
        )
        instruction = isa.create_assembler_instruction( "ADD", operands)
        self.assertEqual( instruction.id, InstructionId.ADD_REGISTER)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0x8354)


    ###################################################
    # test for creation assembler instruction for SUB Vx, Vy
    ###################################################
    def test_create_sub_vx_vy_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=5)
        )
        instruction = isa.create_assembler_instruction( "SUB", operands)
        self.assertEqual( instruction.id, InstructionId.SUB)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0x8355)

    def test_create_sub_rejects_value_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=5)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "SUB", operands)


    ###################################################
    # test for creation assembler instruction for SHR Vx, Vy
    ###################################################
    def test_create_shr_vx_vy_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=5)
        )
        instruction = isa.create_assembler_instruction( "SHR", operands)
        self.assertEqual( instruction.id, InstructionId.SHR)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0x8356)

    def test_create_shr_rejects_value_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=5)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "SHR", operands)

    ###################################################
    # test for creation assembler instruction for SUBN Vx, Vy
    ###################################################
    def test_create_subn_vx_vy_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=5)
        )
        instruction = isa.create_assembler_instruction( "SUBN", operands)
        self.assertEqual( instruction.id, InstructionId.SUBN)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0x8357)

    def test_create_subn_rejects_value_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=5)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "SUBN", operands)

    ###################################################
    # test for creation assembler instruction for SHL Vx, Vy
    ###################################################
    def test_create_shl_vx_vy_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=5)
        )
        instruction = isa.create_assembler_instruction( "SHL", operands)
        self.assertEqual( instruction.id, InstructionId.SHL)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0x835E)

    def test_create_shl_rejects_value_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=5)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "SHL", operands)

    ###################################################
    # test for creation assembler instruction for RND Vx, nn
    ###################################################
    def test_create_rnd_vx_byte_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x5A)
        )
        instruction = isa.create_assembler_instruction( "RND", operands)
        self.assertEqual( instruction.id, InstructionId.RND)
        self.assertEqual(instruction.x, 3)
        self.assertEqual(instruction.nn, 0x5A)

    def test_create_rnd_is_case_insensitive(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x5A)
        )
        instruction = isa.create_assembler_instruction( "rnd", operands)
        self.assertEqual( instruction.id, InstructionId.RND)

    def test_create_rnd_vx_byte_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x5A)
        )
        instruction = isa.create_assembler_instruction( "RND", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0xC35A)

    def test_create_rnd_accepts_zero_byte(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x00)
        )
        instruction = isa.create_assembler_instruction( "RND", operands)
        self.assertEqual(instruction.id, InstructionId.RND)
        self.assertEqual(instruction.nn, 0x00)

    def test_create_rnd_accepts_maximum_byte(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0xFF)
        )
        instruction = isa.create_assembler_instruction( "RND", operands)
        self.assertEqual(instruction.id, InstructionId.RND)
        self.assertEqual(instruction.nn, 0xFF)

    def test_create_rnd_rejects_missing_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "RND", operands)

    def test_create_rnd_rejects_extra_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x5A),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x01)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "RND", operands)

    def test_create_rnd_rejects_non_register_destination(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x5A)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "RND", operands)

    def test_create_rnd_rejects_register_as_second_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=5)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "RND", operands)

    def test_create_rnd_rejects_address_as_second_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x123)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "RND", operands)

    def test_create_rnd_rejects_register_above_vf(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=0x10),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x5A)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "RND", operands)

    def test_create_rnd_rejects_value_above_byte(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x100)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "RND", operands)

    ###################################################
    # test for creation assembler instruction for DRW Vx, Vy, n
    ###################################################
    def test_create_drw_vx_vy_nibble_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=5),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=7)
        )
        instruction = isa.create_assembler_instruction( "DRW", operands)
        self.assertEqual( instruction.id, InstructionId.DRW)
        self.assertEqual(instruction.x, 3)
        self.assertEqual(instruction.y, 5)
        self.assertEqual(instruction.n, 7)

    def test_create_drw_vx_vy_nibble_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=5),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=7)
        )
        instruction = isa.create_assembler_instruction( "DRW", operands)
        opcode = isa.encode(instruction)
        self.assertEqual( opcode, 0xD357)

    def test_create_drw_is_case_insensitive(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=5),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=7)
        )
        instruction = isa.create_assembler_instruction( "drw", operands)
        self.assertEqual( instruction.id, InstructionId.DRW)

    def test_create_drw_accepts_zero_height(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=5),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0)
        )
        instruction = isa.create_assembler_instruction( "DRW", operands)
        self.assertEqual(instruction.n, 0)

    def test_create_drw_accepts_maximum_height(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=5),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0xF)
        )
        instruction = isa.create_assembler_instruction( "DRW", operands)
        self.assertEqual(instruction.n, 0xF)

    def test_create_drw_rejects_height_above_nibble(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=5),
            AssemblerOperand( type=AssemblerOperandType.VALUE, value=0x10)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "DRW", operands)

    def test_create_drw_rejects_register_as_height(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = (
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=5),
            AssemblerOperand( type=AssemblerOperandType.REGISTER, value=7)
        )
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction( "DRW", operands)


    ###################################################
    # misselaneous test for SKP and SKPN
    ###################################################
    def test_create_skp_vx_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),)
        instruction = isa.create_assembler_instruction( "SKP", operands)
        self.assertEqual(instruction.id, InstructionId.SKP)
        self.assertEqual(instruction.x, 3)

    def test_create_skp_vx_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),)
        instruction = isa.create_assembler_instruction( "SKP", operands)
        opcode = isa.encode(instruction)
        self.assertEqual(opcode, 0xE39E)

    def test_create_skp_rejects_non_register_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.VALUE, value=3),)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction("SKP", operands)

    def test_create_sknp_vx_instruction(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),)
        instruction = isa.create_assembler_instruction( "SKNP", operands)
        self.assertEqual(instruction.id, InstructionId.SKNP)
        self.assertEqual(instruction.x, 3)

    def test_create_sknp_vx_instruction_can_be_encoded(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3),)
        instruction = isa.create_assembler_instruction( "SKNP", operands)
        opcode = isa.encode(instruction)
        self.assertEqual(opcode, 0xE3A1)

    def test_create_sknp_rejects_non_register_operand(self) -> None:
        machine = create_machine()
        isa = ClassicInstructionSetArchitecture(machine)
        operands = ( AssemblerOperand( type=AssemblerOperandType.VALUE, value=3),)
        with self.assertRaises(ValueError):
            isa.create_assembler_instruction("SKNP", operands)

