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


