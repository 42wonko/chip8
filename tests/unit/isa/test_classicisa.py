"""
@file test_classicisa.py

@brief Unit tests for the Classic CHIP-8 Instruction Set Architecture.
"""

import unittest

from chip8.isa.classicisa import ClassicInstructionSetArchitecture
from chip8.isa.instructionid import InstructionId
from emulator.constants import FONT_CHARACTER_SIZE, FONT_START
from tests.helpers import create_machine


class TestClassicInstructionSetArchitecture(unittest.TestCase):

    def setUp(self) -> None:
        self.isa = ClassicInstructionSetArchitecture(create_machine())

    ###########################################################################
    # decoder tests
    ###########################################################################
    def test_decode_instruction_ids(self) -> None:
        test_cases = [
            (0x0000, InstructionId.SYS),
            (0x0123, InstructionId.SYS),
            (0x00E0, InstructionId.CLS),
            (0x00EE, InstructionId.RET),
            (0x1234, InstructionId.JP),
            (0x2345, InstructionId.CALL),
            (0x3123, InstructionId.SE_BYTE),
            (0x4123, InstructionId.SNE_BYTE),
            (0x5120, InstructionId.SE_REGISTER),
            (0x6123, InstructionId.LD_BYTE),
            (0x7123, InstructionId.ADD_BYTE),
            (0x8120, InstructionId.LD_REGISTER),
            (0x8121, InstructionId.OR),
            (0x8122, InstructionId.AND),
            (0x8123, InstructionId.XOR),
            (0x8124, InstructionId.ADD_REGISTER),
            (0x8125, InstructionId.SUB),
            (0x8126, InstructionId.SHR),
            (0x8127, InstructionId.SUBN),
            (0x812E, InstructionId.SHL),
            (0x9120, InstructionId.SNE_REGISTER),
            (0xA123, InstructionId.LD_I),
            (0xB123, InstructionId.JP_V0),
            (0xC123, InstructionId.RND),
            (0xD12C, InstructionId.DRW),
            (0xE19E, InstructionId.SKP),
            (0xE1A1, InstructionId.SKNP),
            (0xF107, InstructionId.LD_VX_DT),
            (0xF10A, InstructionId.LD_VX_K),
            (0xF115, InstructionId.LD_DT_VX),
            (0xF118, InstructionId.LD_ST_VX),
            (0xF11E, InstructionId.ADD_I_VX),
            (0xF129, InstructionId.LD_F_VX),
            (0xF133, InstructionId.LD_B_VX),
            (0xF155, InstructionId.LD_I_VX),
            (0xF165, InstructionId.LD_VX_I),
        ]
        for opcode, expected_id in test_cases:
            with self.subTest(opcode=f"{opcode:04X}"):
                instruction = self.isa.decode(0x200, opcode)
                self.assertIs(instruction.id, expected_id)

    def test_decode_unknown_instructions(self) -> None:
        test_cases = [
            0x5121,
            0x8128,
            0x8129,
            0x812A,
            0x812B,
            0x812C,
            0x812D,
            0x812F,
            0x9121,
            0xE100,
            0xF100,
        ]
        for opcode in test_cases:
            with self.subTest(opcode=f"{opcode:04X}"):
                instruction = self.isa.decode(0x200, opcode)
                self.assertIs(instruction.id, InstructionId.UNKNOWN)

    def test_decode_operands(self) -> None:
        instruction = self.isa.decode(0x234, 0xDABC)
        self.assertEqual(instruction.address, 0x234)
        self.assertEqual(instruction.opcode, 0xDABC)
        self.assertIs(instruction.id, InstructionId.DRW)
        self.assertEqual(instruction.x, 0xA)
        self.assertEqual(instruction.y, 0xB)
        self.assertEqual(instruction.n, 0xC)
        self.assertEqual(instruction.nn, 0xBC)
        self.assertEqual(instruction.nnn, 0xABC)

    def test_decode_masks_address(self) -> None:
        instruction = self.isa.decode(0x1234, 0x6123)
        self.assertEqual(instruction.address, 0x234)

    def test_decode_masks_opcode(self) -> None:
        instruction = self.isa.decode(0x200, 0x16123)
        self.assertEqual(instruction.opcode, 0x6123)
        self.assertIs(instruction.id, InstructionId.LD_BYTE)


    ###########################################################################
    # dispatcher tests
    ###########################################################################
    def test_format_dispatch(self) -> None:
        instruction = self.isa.decode(0x200, 0x1234)
        self.assertEqual(self.isa.format(instruction), "JP 234")

    def test_execute_dispatch(self) -> None:
        instruction = self.isa.decode(0x200, 0xE0FF)
        with self.assertRaises(ValueError):
            self.isa.execute(instruction)

    def test_execute_unknown_instruction(self) -> None:
        instruction = self.isa.decode(0x200, 0x5121)
        with self.assertRaises(ValueError):
            self.isa.execute(instruction)

    def test_format_unknown_instruction(self) -> None:
        instruction = self.isa.decode(0x200, 0x5121)
        with self.assertRaises(ValueError):
            self.isa.format(instruction)

    def test_execute_cls(self) -> None:
        instruction = self.isa.decode(0x200, 0x00E0)
        result = self.isa.execute(instruction)
        self.assertTrue(result.display_changed)


    def test_ret(self) -> None:
        self.isa._machine.stack.push(0x456)
        instruction = self.isa.decode(0x200, 0x00EE)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.sp , 0)
        self.assertEqual(self.isa._machine.registers.pc , 0x456)

    def test_jp(self) -> None:
        instruction = self.isa.decode(0x200, 0x1234)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x234)

    def test_call(self) -> None:
        instruction = self.isa.decode(0x200, 0x2345)
        self.assertEqual(self.isa._machine.registers.pc, 0x200)
        self.assertEqual(self.isa._machine.registers.sp, 0)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x345)
        self.assertEqual(self.isa._machine.registers.sp, 1)

    def test_call_ret(self) -> None:
        self.isa._machine.registers.pc = 0x202  # small hack because the test harness behaves slightly different then the original machine
        call = self.isa.decode(0x200, 0x2456)
        self.isa.execute(call)
        self.assertEqual(self.isa._machine.registers.pc, 0x456)
        self.assertEqual(self.isa._machine.registers.sp, 1)
        ret = self.isa.decode(0x456, 0x00EE)
        self.isa.execute(ret)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.sp, 0)

    def test_se_byte(self) -> None:
        self.isa._machine.registers.pc = 0x202  # small hack because the test harness behaves slightly different then the original machine
        self.isa._machine.registers.write_register(1, 0x42)
        instruction = self.isa.decode(0x200, 0x3142)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x204)
        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(1, 0x43)
        instruction = self.isa.decode(0x200, 0x3142)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)

    def test_sne_byte(self) -> None:
        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(1, 0x42)
        instruction = self.isa.decode(0x200, 0x4142)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(1, 0x43)
        instruction = self.isa.decode(0x200, 0x4142)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x204)

    def test_se_register(self) -> None:
        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(1, 0x42)
        self.isa._machine.registers.write_register(2, 0x42)
        instruction = self.isa.decode(0x200, 0x5120)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x204)
        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(1, 0x43)
        self.isa._machine.registers.write_register(2, 0x42)
        instruction = self.isa.decode(0x200, 0x5120)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)

    def test_ld_byte(self) -> None:
        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(1, 0x42)
        self.assertEqual(self.isa._machine.registers.read_register(1), 0x42)
        instruction = self.isa.decode(0x200, 0x61BD)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.read_register(1), 0xBD)

    def test_add_byte(self) -> None:
        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(5, 0xFE)
        self.assertEqual(self.isa._machine.registers.read_register(5), 0xFE)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x7505)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.read_register(5), 0x03)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)

    def test_ld_register(self) -> None:
        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(3, 0x55)
        self.isa._machine.registers.write_register(7, 0xAA)
        self.assertEqual(self.isa._machine.registers.read_register(3), 0x55)
        self.assertEqual(self.isa._machine.registers.read_register(7), 0xAA)
        instruction = self.isa.decode(0x200, 0x8370)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.read_register(3), 0xAA)
        self.assertEqual(self.isa._machine.registers.read_register(7), 0xAA)

    def test_or(self) -> None:
        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(3, 0x55)
        self.isa._machine.registers.write_register(7, 0xAA)
        self.assertEqual(self.isa._machine.registers.read_register(3), 0x55)
        self.assertEqual(self.isa._machine.registers.read_register(7), 0xAA)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x8371)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.read_register(3), 0xFF)
        self.assertEqual(self.isa._machine.registers.read_register(7), 0xAA)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)

    def test_and(self) -> None:
        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(3, 0x55)
        self.isa._machine.registers.write_register(7, 0xAA)
        self.assertEqual(self.isa._machine.registers.read_register(3), 0x55)
        self.assertEqual(self.isa._machine.registers.read_register(7), 0xAA)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x8372)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.read_register(3), 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(7), 0xAA)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)


    def test_xor(self) -> None:
        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(3, 0x55)
        self.isa._machine.registers.write_register(7, 0xAA)
        self.assertEqual(self.isa._machine.registers.read_register(3), 0x55)
        self.assertEqual(self.isa._machine.registers.read_register(7), 0xAA)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x8373)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.read_register(3), 0xFF)
        self.assertEqual(self.isa._machine.registers.read_register(7), 0xAA)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)

    def test_add_register(self) -> None:
        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(3, 0x10)
        self.isa._machine.registers.write_register(7, 0x20)
        self.isa._machine.registers.write_register(15, 0x01)
        self.assertEqual(self.isa._machine.registers.read_register(3), 0x10)
        self.assertEqual(self.isa._machine.registers.read_register(7), 0x20)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x01)
        instruction = self.isa.decode(0x200, 0x8374)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.read_register(3), 0x30)
        self.assertEqual(self.isa._machine.registers.read_register(7), 0x20)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)

        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(3, 0xFF)
        self.isa._machine.registers.write_register(7, 0x01)
        self.isa._machine.registers.write_register(15, 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(3), 0xFF)
        self.assertEqual(self.isa._machine.registers.read_register(7), 0x01)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x8374)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.read_register(3), 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(7), 0x01)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x01)

        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(3, 0xFE)
        self.isa._machine.registers.write_register(7, 0x03)
        self.isa._machine.registers.write_register(15, 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(3), 0xFE)
        self.assertEqual(self.isa._machine.registers.read_register(7), 0x03)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x8374)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.read_register(3), 0x01)
        self.assertEqual(self.isa._machine.registers.read_register(7), 0x03)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x01)

    def test_sub_register(self) -> None:
        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(3, 0x50)
        self.isa._machine.registers.write_register(7, 0x20)
        self.isa._machine.registers.write_register(15, 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(3), 0x50)
        self.assertEqual(self.isa._machine.registers.read_register(7), 0x20)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x8375)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.read_register(3), 0x30)
        self.assertEqual(self.isa._machine.registers.read_register(7), 0x20)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x01)

        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(3, 0x20)
        self.isa._machine.registers.write_register(7, 0x50)
        self.isa._machine.registers.write_register(15, 0x01)
        self.assertEqual(self.isa._machine.registers.read_register(3), 0x20)
        self.assertEqual(self.isa._machine.registers.read_register(7), 0x50)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x01)
        instruction = self.isa.decode(0x200, 0x8375)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.read_register(3), 0xD0)
        self.assertEqual(self.isa._machine.registers.read_register(7), 0x50)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)

        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(3, 0x50)
        self.isa._machine.registers.write_register(7, 0x50)
        self.isa._machine.registers.write_register(15, 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(3), 0x50)
        self.assertEqual(self.isa._machine.registers.read_register(7), 0x50)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x8375)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.read_register(3), 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(7), 0x50)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x01)

    def test_shr(self) -> None:
        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(1, 0x02)
        self.isa._machine.registers.write_register(2, 0x55)
        self.isa._machine.registers.write_register(15, 0x01)
        self.assertEqual(self.isa._machine.registers.read_register(1), 0x02)
        self.assertEqual(self.isa._machine.registers.read_register(2), 0x55)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x01)
        instruction = self.isa.decode(0x200, 0x8126)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.read_register(1), 0x01)
        self.assertEqual(self.isa._machine.registers.read_register(2), 0x55)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)

        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(1, 0x03)
        self.isa._machine.registers.write_register(2, 0x55)
        self.isa._machine.registers.write_register(15, 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(1), 0x03)
        self.assertEqual(self.isa._machine.registers.read_register(2), 0x55)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x8126)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.read_register(1), 0x01)
        self.assertEqual(self.isa._machine.registers.read_register(2), 0x55)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x01)

        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(1, 0x80)
        self.isa._machine.registers.write_register(2, 0x55)
        self.isa._machine.registers.write_register(15, 0x01)
        self.assertEqual(self.isa._machine.registers.read_register(1), 0x80)
        self.assertEqual(self.isa._machine.registers.read_register(2), 0x55)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x01)
        instruction = self.isa.decode(0x200, 0x8126)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.read_register(1), 0x40)
        self.assertEqual(self.isa._machine.registers.read_register(2), 0x55)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)

    def test_subn(self) -> None:
        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(1, 0x20)
        self.isa._machine.registers.write_register(2, 0x50)
        self.isa._machine.registers.write_register(15, 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(1), 0x20)
        self.assertEqual(self.isa._machine.registers.read_register(2), 0x50)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x8127)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.read_register(1), 0x30)
        self.assertEqual(self.isa._machine.registers.read_register(2), 0x50)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x01)

        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(1, 0x50)
        self.isa._machine.registers.write_register(2, 0x20)
        self.isa._machine.registers.write_register(15, 0x01)
        self.assertEqual(self.isa._machine.registers.read_register(1), 0x50)
        self.assertEqual(self.isa._machine.registers.read_register(2), 0x20)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x01)
        instruction = self.isa.decode(0x200, 0x8127)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.read_register(1), 0xD0)
        self.assertEqual(self.isa._machine.registers.read_register(2), 0x20)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)

        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(1, 0x55)
        self.isa._machine.registers.write_register(2, 0x55)
        self.isa._machine.registers.write_register(15, 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(1), 0x55)
        self.assertEqual(self.isa._machine.registers.read_register(2), 0x55)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x8127)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.read_register(1), 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(2), 0x55)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x01)

    def test_shl(self) -> None:
        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(1, 0x40)
        self.isa._machine.registers.write_register(2, 0x55)
        self.isa._machine.registers.write_register(15, 0x01)
        self.assertEqual(self.isa._machine.registers.read_register(1), 0x40)
        self.assertEqual(self.isa._machine.registers.read_register(2), 0x55)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x01)
        instruction = self.isa.decode(0x200, 0x812E)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.read_register(1), 0x80)
        self.assertEqual(self.isa._machine.registers.read_register(2), 0x55)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)

        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(1, 0x80)
        self.isa._machine.registers.write_register(2, 0x55)
        self.isa._machine.registers.write_register(15, 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(1), 0x80)
        self.assertEqual(self.isa._machine.registers.read_register(2), 0x55)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x812E)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.read_register(1), 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(2), 0x55)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x01)

        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(1, 0xC1)
        self.isa._machine.registers.write_register(2, 0x55)
        self.isa._machine.registers.write_register(15, 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(1), 0xC1)
        self.assertEqual(self.isa._machine.registers.read_register(2), 0x55)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x812E)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.read_register(1), 0x82)
        self.assertEqual(self.isa._machine.registers.read_register(2), 0x55)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x01)

    def test_sne_register(self) -> None:
        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(1, 0x42)
        self.isa._machine.registers.write_register(2, 0x43)
        instruction = self.isa.decode(0x200, 0x9120)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x204)

        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(1, 0x42)
        self.isa._machine.registers.write_register(2, 0x42)
        instruction = self.isa.decode(0x200, 0x9120)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)

    def test_ld_i(self) -> None:
        self.isa._machine.registers.pc = 0x202
        self.assertEqual(self.isa._machine.registers.i, 0x000)
        self.isa._machine.registers.write_register(1, 0x00)
        self.isa._machine.registers.write_register(2, 0x00)
        self.isa._machine.registers.write_register(3, 0x00)
        self.isa._machine.registers.write_register(4, 0x00)
        self.isa._machine.registers.write_register(5, 0x00)
        self.isa._machine.registers.write_register(6, 0x00)
        self.isa._machine.registers.write_register(7, 0x00)
        self.isa._machine.registers.write_register(8, 0x00)
        self.isa._machine.registers.write_register(9, 0x00)
        self.isa._machine.registers.write_register(10, 0x00)
        self.isa._machine.registers.write_register(11, 0x00)
        self.isa._machine.registers.write_register(12, 0x00)
        self.isa._machine.registers.write_register(13, 0x00)
        self.isa._machine.registers.write_register(14, 0x00)
        self.isa._machine.registers.write_register(15, 0x00)
        instruction = self.isa.decode(0x200, 0xA456)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers.i, 0x456)
        self.assertEqual(self.isa._machine.registers.read_register(1), 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(2), 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(3), 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(4), 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(5), 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(6), 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(7), 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(8), 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(9), 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(10), 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(11), 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(12), 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(13), 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(14), 0x00)
        self.assertEqual(self.isa._machine.registers.read_register(15), 0x00)

    def test_jp_v0(self) -> None :
        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(0, 0x10)
        self.isa._machine.registers.write_register(1, 0x43)
        instruction = self.isa.decode(0x200, 0xB456)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x466)

        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers.write_register(0, 0x00)
        self.isa._machine.registers.write_register(1, 0x43)
        instruction = self.isa.decode(0x200, 0xB456)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x456)

    def test_execute_rnd_vx_nn_zero_mask(self) -> None:
        self.isa._machine.registers[0x3] = 0xAB
        instruction = self.isa.decode(0x200, 0xC300)
        result = self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers[0x3], 0x00)
        self.assertEqual(self.isa._machine.registers.pc, 0x200)
        self.assertEqual(result.display_changed, False)

    def test_execute_rnd_vx_nn_full_mask(self) -> None:
        self.isa._machine.registers[0x3] = 0x00
        instruction = self.isa.decode(0x200, 0xC3FF)
        result = self.isa.execute(instruction)
        self.assertGreaterEqual(self.isa._machine.registers[0x3], 0x00)
        self.assertLessEqual(self.isa._machine.registers[0x3], 0xFF)
        self.assertEqual(self.isa._machine.registers.pc, 0x200)
        self.assertEqual(result.display_changed, False)

    def test_execute_rnd_vx_nn_masks_random_value(self) -> None:
        instruction = self.isa.decode(0x200, 0xC30F)
        for _ in range(100):
            self.isa._machine.registers[0x3] = 0x00
            self.isa.execute(instruction)
            self.assertLessEqual(self.isa._machine.registers[0x3], 0x0F)

    def test_execute_drw_vx_vy_n(self) -> None:
        self.isa._machine.registers.i = 0x300
        self.isa._machine.registers[0x3] = 2
        self.isa._machine.registers[0x4] = 3
        self.isa._machine.memory.write_byte(0x300, 0xA0)
        instruction = self.isa.decode(0x200, 0xD341)
        result = self.isa.execute(instruction)
        self.assertTrue(result.display_changed)
        self.assertEqual(self.isa._machine.registers[0xF], 0)
        self.assertTrue(self.isa._machine.framebuffer.get_pixel(2, 3))
        self.assertTrue(self.isa._machine.framebuffer.get_pixel(4, 3))
        self.assertFalse(self.isa._machine.framebuffer.get_pixel(3, 3))

    def test_execute_drw_multiple_rows(self) -> None:
        self.isa._machine.registers.i = 0x350
        self.isa._machine.registers[0x3] = 1
        self.isa._machine.registers[0x4] = 2
        self.isa._machine.memory.write_byte(0x350, 0x80)
        self.isa._machine.memory.write_byte(0x351, 0x40)
        self.isa._machine.memory.write_byte(0x352, 0x20)
        instruction = self.isa.decode(0x200, 0xD343)
        result = self.isa.execute(instruction)
        self.assertTrue(result.display_changed)
        self.assertEqual(self.isa._machine.registers[0xF], 0)
        self.assertTrue(self.isa._machine.framebuffer.get_pixel(1, 2))
        self.assertTrue(self.isa._machine.framebuffer.get_pixel(2, 3))
        self.assertTrue(self.isa._machine.framebuffer.get_pixel(3, 4))

    def test_execute_drw_collision(self) -> None:
        self.isa._machine.registers.i = 0x300
        self.isa._machine.registers[0x3] = 2
        self.isa._machine.registers[0x4] = 3
        self.isa._machine.memory.write_byte(0x300, 0xA0)
        instruction = self.isa.decode(0x200, 0xD341)
        first_result = self.isa.execute(instruction)
        self.assertTrue(first_result.display_changed)
        self.assertEqual(self.isa._machine.registers[0xF], 0)
        self.assertTrue(self.isa._machine.framebuffer.get_pixel(2, 3))
        self.assertTrue(self.isa._machine.framebuffer.get_pixel(4, 3))
        second_result = self.isa.execute(instruction)
        self.assertTrue(second_result.display_changed)
        self.assertEqual(self.isa._machine.registers[0xF], 1)
        self.assertFalse(self.isa._machine.framebuffer.get_pixel(2, 3))
        self.assertFalse(self.isa._machine.framebuffer.get_pixel(4, 3))

    def test_execute_drw_no_collision(self) -> None:
        self.isa._machine.registers[0xF] = 1
        self.isa._machine.registers.i = 0x300
        self.isa._machine.registers[0x3] = 0
        self.isa._machine.registers[0x4] = 0
        self.isa._machine.memory.write_byte(0x300, 0x80)
        instruction = self.isa.decode(0x200, 0xD341)
        result = self.isa.execute(instruction)
        self.assertTrue(result.display_changed)
        self.assertEqual(self.isa._machine.registers[0xF], 0)

    def test_execute_skp_vx_key_pressed(self) -> None:
        self.isa._machine.registers.pc = 0x200
        self.isa._machine.registers[0x3] = 0xA
        self.isa._machine.keyboard.press(0xA)
        instruction = self.isa.decode(0x200, 0xE39E)
        result = self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertFalse(result.display_changed)

    def test_execute_skp_vx_key_not_pressed(self) -> None:
        self.isa._machine.registers.pc = 0x200
        self.isa._machine.registers[0x3] = 0xA
        instruction = self.isa.decode(0x200, 0xE39E)
        result = self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x200)
        self.assertFalse(result.display_changed)

    def test_execute_skp_vx_uses_vx(self) -> None:
        self.isa._machine.registers.pc = 0x200
        self.isa._machine.registers[0x3] = 0xA
        self.isa._machine.registers[0x4] = 0xB
        self.isa._machine.keyboard.press(0xB)
        instruction = self.isa.decode(0x200, 0xE39E)
        result = self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x200)
        self.assertFalse(result.display_changed)

    def test_execute_sknp_vx_key_pressed(self) -> None:
        self.isa._machine.registers.pc = 0x200
        self.isa._machine.registers[0x3] = 0xA
        self.isa._machine.keyboard.press(0xA)
        instruction = self.isa.decode(0x200, 0xE3A1)
        result = self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x200)
        self.assertFalse(result.display_changed)

    def test_execute_sknp_vx_key_not_pressed(self) -> None:
        self.isa._machine.registers.pc = 0x200
        self.isa._machine.registers[0x3] = 0xA
        instruction = self.isa.decode(0x200, 0xE3A1)
        result = self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertFalse(result.display_changed)

    def test_execute_sknp_vx_uses_vx(self) -> None:
        self.isa._machine.registers.pc = 0x200
        self.isa._machine.registers[0x3] = 0xA
        self.isa._machine.registers[0x4] = 0xB
        self.isa._machine.keyboard.press(0xB)
        instruction = self.isa.decode(0x200, 0xE3A1)
        result = self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertFalse(result.display_changed)

    def test_execute_ld_vx_dt(self) -> None:
        self.isa._machine.timers.delay_timer = 0x7B
        self.isa._machine.registers[0x3] = 0x00
        self.isa._machine.registers.pc = 0x200
        instruction = self.isa.decode(0x200, 0xF307)
        result = self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers[0x3], 0x7B)
        self.assertEqual(self.isa._machine.timers.delay_timer, 0x7B)
        self.assertEqual(self.isa._machine.registers.pc, 0x200)
        self.assertFalse(result.display_changed)

    def test_execute_ld_vx_dt_preserves_vf(self) -> None:
        self.isa._machine.timers.delay_timer = 0x42
        self.isa._machine.registers[0xF] = 0xAB
        instruction = self.isa.decode(0x200, 0xF507)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers[0x5], 0x42)
        self.assertEqual(self.isa._machine.registers[0xF], 0xAB)

    def test_execute_ld_vx_k_no_key_pressed(self) -> None:
        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers[0x3] = 0xAB
        instruction = self.isa.decode(0x200, 0xF30A)
        result = self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x200)
        self.assertEqual(self.isa._machine.registers[0x3], 0xAB)
        self.assertFalse(result.display_changed)

    def test_execute_ld_vx_k_key_pressed(self) -> None:
        self.isa._machine.registers.pc = 0x202
        self.isa._machine.registers[0x3] = 0xAB
        self.isa._machine.keyboard.press(0x7)
        instruction = self.isa.decode(0x200, 0xF30A)
        result = self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers[0x3], 0x07)
        self.assertFalse(result.display_changed)

    def test_execute_ld_vx_k_uses_first_pressed_key(self) -> None:
        self.isa._machine.registers.pc = 0x202
        self.isa._machine.keyboard.press(0xA)
        self.isa._machine.keyboard.press(0x3)
        instruction = self.isa.decode(0x200, 0xF50A)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.pc, 0x202)
        self.assertEqual(self.isa._machine.registers[0x5], 0x03)

    def test_execute_ld_dt_vx(self) -> None:
        self.isa._machine.registers.pc = 0x200
        self.isa._machine.registers[0x3] = 0x7B
        self.isa._machine.timers.delay_timer = 0x00
        instruction = self.isa.decode(0x200, 0xF315)
        result = self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.timers.delay_timer, 0x7B)
        self.assertEqual(self.isa._machine.registers[0x3], 0x7B)
        self.assertEqual(self.isa._machine.registers.pc, 0x200)
        self.assertFalse(result.display_changed)

    def test_execute_ld_dt_vx_zero(self) -> None:
        self.isa._machine.registers[0x3] = 0x00
        self.isa._machine.timers.delay_timer = 0xFF
        instruction = self.isa.decode(0x200, 0xF315)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.timers.delay_timer, 0x00)
        self.assertEqual(self.isa._machine.registers[0x3], 0x00)

    def test_execute_ld_dt_vx_maximum(self) -> None:
        self.isa._machine.registers[0x3] = 0xFF
        self.isa._machine.timers.delay_timer = 0x00
        instruction = self.isa.decode(0x200, 0xF315)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.timers.delay_timer, 0xFF)
        self.assertEqual(self.isa._machine.registers[0x3], 0xFF)

    def test_execute_ld_dt_vx_preserves_vf(self) -> None:
        self.isa._machine.registers[0xF] = 0xAB
        self.isa._machine.registers[0x3] = 0x42
        instruction = self.isa.decode(0x200, 0xF315)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers[0xF], 0xAB)
        self.assertEqual(self.isa._machine.timers.delay_timer, 0x42)

    def test_execute_ld_st_vx(self) -> None:
        self.isa._machine.registers.pc = 0x200
        self.isa._machine.registers[0x3] = 0x7B
        self.isa._machine.timers.delay_timer = 0x00
        instruction = self.isa.decode(0x200, 0xF318)
        result = self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.timers.sound_timer, 0x7B)
        self.assertEqual(self.isa._machine.registers[0x3], 0x7B)
        self.assertEqual(self.isa._machine.registers.pc, 0x200)
        self.assertFalse(result.display_changed)

    def test_execute_ld_st_vx_zero(self) -> None:
        self.isa._machine.registers[0x3] = 0x00
        self.isa._machine.timers.delay_timer = 0xFF
        instruction = self.isa.decode(0x200, 0xF318)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.timers.sound_timer, 0x00)
        self.assertEqual(self.isa._machine.registers[0x3], 0x00)

    def test_execute_ld_st_vx_maximum(self) -> None:
        self.isa._machine.registers[0x3] = 0xFF
        self.isa._machine.timers.delay_timer = 0x00
        instruction = self.isa.decode(0x200, 0xF318)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.timers.sound_timer, 0xFF)
        self.assertEqual(self.isa._machine.registers[0x3], 0xFF)

    def test_execute_ld_st_vx_preserves_vf(self) -> None:
        self.isa._machine.registers[0xF] = 0xAB
        self.isa._machine.registers[0x3] = 0x42
        instruction = self.isa.decode(0x200, 0xF318)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers[0xF], 0xAB)
        self.assertEqual(self.isa._machine.timers.sound_timer, 0x42)

    def test_execute_add_i_vx(self) -> None:
        self.isa._machine.registers.pc = 0x200
        self.isa._machine.registers.i = 0x300
        self.isa._machine.registers[0x3] = 0x42
        self.isa._machine.registers[0xF] = 0xAB
        instruction = self.isa.decode(0x200, 0xF31E)
        result = self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.i, 0x342)
        self.assertEqual(self.isa._machine.registers[0x3], 0x42)
        self.assertEqual(self.isa._machine.registers[0xF], 0xAB)
        self.assertEqual(self.isa._machine.registers.pc, 0x200)
        self.assertFalse(result.display_changed)

    def test_execute_add_i_vx_zero(self) -> None:
        self.isa._machine.registers.i = 0x300
        self.isa._machine.registers[0x3] = 0x00
        instruction = self.isa.decode(0x200, 0xF31E)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.i, 0x300)

    def test_execute_add_i_vx_maximum_value(self) -> None:
        self.isa._machine.registers.i = 0x300
        self.isa._machine.registers[0x3] = 0xFF
        instruction = self.isa.decode(0x200, 0xF31E)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.i, 0x3FF)

    def test_execute_add_i_vx_crosses_address_range(self) -> None:
        self.isa._machine.registers.i = 0xFFF
        self.isa._machine.registers[0x3] = 0x01
        instruction = self.isa.decode(0x200, 0xF31E)
        self.isa.execute(instruction)
        self.assertEqual(self.isa._machine.registers.i, 0x000)

    def test_execute_ld_f_vx(self) -> None:
        self.isa._machine.registers[0x3] = 0x0A

        instruction = self.isa.decode(0x200, 0xF329)
        result = self.isa.execute(instruction)

        self.assertEqual(self.isa._machine.registers.i, FONT_START + 0x0A * FONT_CHARACTER_SIZE)
        self.assertFalse(result.display_changed)

    def test_execute_ld_f_vx_uses_low_nibble(self) -> None:
        self.isa._machine.registers[0x3] = 0xFA

        instruction = self.isa.decode(0x200, 0xF329)
        self.isa.execute(instruction)

        self.assertEqual(self.isa._machine.registers.i, FONT_START + 0x0A * FONT_CHARACTER_SIZE)

    def test_execute_ld_b_vx(self) -> None:
        self.isa._machine.registers.i = 0x300
        self.isa._machine.registers[0x3] = 234

        instruction = self.isa.decode(0x200, 0xF333)
        result = self.isa.execute(instruction)

        self.assertEqual(self.isa._machine.memory.read_byte(0x300), 2)
        self.assertEqual(self.isa._machine.memory.read_byte(0x301), 3)
        self.assertEqual(self.isa._machine.memory.read_byte(0x302), 4)
        self.assertEqual(result.memory_range, (0x300, 0x302))

    def test_execute_ld_b_vx_zero(self) -> None:
        self.isa._machine.registers.i = 0x300
        self.isa._machine.registers[0x3] = 0

        instruction = self.isa.decode(0x200, 0xF333)
        self.isa.execute(instruction)

        self.assertEqual(self.isa._machine.memory.read_byte(0x300), 0)
        self.assertEqual(self.isa._machine.memory.read_byte(0x301), 0)
        self.assertEqual(self.isa._machine.memory.read_byte(0x302), 0)

    def test_execute_ld_b_vx_maximum(self) -> None:
        self.isa._machine.registers.i = 0x300
        self.isa._machine.registers[0x3] = 255

        instruction = self.isa.decode(0x200, 0xF333)
        self.isa.execute(instruction)

        self.assertEqual(self.isa._machine.memory.read_byte(0x300), 2)
        self.assertEqual(self.isa._machine.memory.read_byte(0x301), 5)
        self.assertEqual(self.isa._machine.memory.read_byte(0x302), 5)

    def test_execute_ld_i_vx(self) -> None:
        self.isa._machine.registers.i = 0x300
        self.isa._machine.registers[0] = 0x10
        self.isa._machine.registers[1] = 0x20
        self.isa._machine.registers[2] = 0x30
        self.isa._machine.registers[3] = 0x40

        instruction = self.isa.decode(0x200, 0xF355)
        result = self.isa.execute(instruction)

        self.assertEqual(self.isa._machine.memory.read_byte(0x300), 0x10)
        self.assertEqual(self.isa._machine.memory.read_byte(0x301), 0x20)
        self.assertEqual(self.isa._machine.memory.read_byte(0x302), 0x30)
        self.assertEqual(self.isa._machine.memory.read_byte(0x303), 0x40)
        self.assertEqual(result.memory_range, (0x300, 0x303))

    def test_execute_ld_i_vx_preserves_i(self) -> None:
        self.isa._machine.registers.i = 0x350
        self.isa._machine.registers[0x2] = 0xAA

        instruction = self.isa.decode(0x200, 0xF255)
        self.isa.execute(instruction)

        self.assertEqual(self.isa._machine.registers.i, 0x350)

    def test_execute_ld_vx_i(self) -> None:
        self.isa._machine.registers.i = 0x300
        self.isa._machine.memory.write_byte(0x300, 0x10)
        self.isa._machine.memory.write_byte(0x301, 0x20)
        self.isa._machine.memory.write_byte(0x302, 0x30)
        self.isa._machine.memory.write_byte(0x303, 0x40)

        instruction = self.isa.decode(0x200, 0xF365)
        result = self.isa.execute(instruction)

        self.assertEqual(self.isa._machine.registers[0], 0x10)
        self.assertEqual(self.isa._machine.registers[1], 0x20)
        self.assertEqual(self.isa._machine.registers[2], 0x30)
        self.assertEqual(self.isa._machine.registers[3], 0x40)
        self.assertEqual(self.isa._machine.registers.i, 0x300)
        self.assertFalse(result.display_changed)

    def test_execute_ld_vx_i_does_not_modify_registers_above_vx(self) -> None:
        self.isa._machine.registers.i = 0x300
        self.isa._machine.memory.write_byte(0x300, 0x12)
        self.isa._machine.memory.write_byte(0x301, 0x34)

        self.isa._machine.registers[0x2] = 0xAA
        self.isa._machine.registers[0x3] = 0xBB

        instruction = self.isa.decode(0x200, 0xF165)
        self.isa.execute(instruction)

        self.assertEqual(self.isa._machine.registers[0], 0x12)
        self.assertEqual(self.isa._machine.registers[1], 0x34)
        self.assertEqual(self.isa._machine.registers[2], 0xAA)
        self.assertEqual(self.isa._machine.registers[3], 0xBB)


if __name__ == "__main__":
    unittest.main(verbosity=2)


