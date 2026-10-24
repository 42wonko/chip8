"""
@file test_classicisa.py

@brief Unit tests for the Classic CHIP-8 Instruction Set Architecture.
"""

from typing import cast
import unittest

from assembler.instruction import AssemblerInstruction
from assembler.operand import AssemblerOperand, AssemblerOperandType
from chip8.isa.classicisa import ClassicInstructionSetArchitecture
from chip8.isa.instructionid import InstructionId
from chip8.isa.reference import ReferenceAccess
from chip8.isa.instruction import Instruction

#from src.assembler import instruction instruction

from emulator.constants import FONT_CHARACTER_SIZE, FONT_START, INSTRUCTION_SIZE
from tests.helpers import create_machine


class TestClassicInstructionSetArchitecture(unittest.TestCase):

    def setUp(self) -> None:
        self.machine    = create_machine()
        self.isa        = ClassicInstructionSetArchitecture()

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

    def test_isa_does_not_own_machine(self) -> None:
        self.assertFalse(hasattr(self.isa, "_machine"))

    ###########################################################################
    # dispatcher tests
    ###########################################################################
    def test_format_dispatch(self) -> None:
        instruction = self.isa.decode(0x200, 0x1234)
        self.assertEqual(self.isa.format(instruction), "JP 234")

    def test_execute_dispatch(self) -> None:
        instruction = self.isa.decode(0x200, 0xE0FF)
        with self.assertRaises(ValueError):
            self.isa.execute(self.machine, instruction)

    def test_execute_unknown_instruction(self) -> None:
        instruction = self.isa.decode(0x200, 0x5121)
        with self.assertRaises(ValueError):
            self.isa.execute(self.machine, instruction)

    def test_format_unknown_instruction(self) -> None:
        instruction = self.isa.decode(0x200, 0x5121)
        with self.assertRaises(ValueError):
            self.isa.format(instruction)

    def test_execute_cls(self) -> None:
        instruction = self.isa.decode(0x200, 0x00E0)
        result = self.isa.execute(self.machine, instruction)
        self.assertTrue(result.display_changed)


    def test_ret(self) -> None:
        self.machine.stack.push(0x456)
        instruction = self.isa.decode(0x200, 0x00EE)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.sp , 0)
        self.assertEqual(self.machine.registers.pc , 0x456)

    def test_jp(self) -> None:
        instruction = self.isa.decode(0x200, 0x1234)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x234)

    def test_call(self) -> None:
        instruction = self.isa.decode(0x200, 0x2345)
        self.assertEqual(self.machine.registers.pc, 0x200)
        self.assertEqual(self.machine.registers.sp, 0)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x345)
        self.assertEqual(self.machine.registers.sp, 1)

    def test_call_ret(self) -> None:
        self.machine.registers.pc = 0x202  # small hack because the test harness behaves slightly different then the original machine
        call = self.isa.decode(0x200, 0x2456)
        self.isa.execute(self.machine, call)
        self.assertEqual(self.machine.registers.pc, 0x456)
        self.assertEqual(self.machine.registers.sp, 1)
        ret = self.isa.decode(0x456, 0x00EE)
        self.isa.execute(self.machine, ret)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.sp, 0)

    def test_skip_and_se_instructions_reject_invalid_operands(self) -> None:
        """Verify SKNP and SE reject invalid operand counts and register indices."""
        test_cases = (
            (
                "SKNP operand count",
                "SKNP",
                (),
                "SKNP requires exactly one operand"
            ),
            (
                "SE operand count",
                "SE",
                (
                    AssemblerOperand(AssemblerOperandType.REGISTER, 1),
                ),
                "SE requires exactly two operands"
            ),
            (
                "SE first register out of range",
                "SE",
                (
                    AssemblerOperand(AssemblerOperandType.REGISTER, 0x10),
                    AssemblerOperand(AssemblerOperandType.REGISTER, 2)
                ),
                "Register must be in the range V0 to VF"
            )
        )
        for description, name, operands, expected_message in test_cases:
            with self.subTest(description=description):
                with self.assertRaisesRegex(ValueError, expected_message):
                    self.isa.create_assembler_instruction(name, operands)

    def test_se_byte(self) -> None:
        self.machine.registers.pc = 0x202  # small hack because the test harness behaves slightly different then the original machine
        self.machine.registers.write_register(1, 0x42)
        instruction = self.isa.decode(0x200, 0x3142)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x204)
        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(1, 0x43)
        instruction = self.isa.decode(0x200, 0x3142)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)

    def test_sne_byte(self) -> None:
        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(1, 0x42)
        instruction = self.isa.decode(0x200, 0x4142)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(1, 0x43)
        instruction = self.isa.decode(0x200, 0x4142)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x204)

    def test_se_register(self) -> None:
        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(1, 0x42)
        self.machine.registers.write_register(2, 0x42)
        instruction = self.isa.decode(0x200, 0x5120)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x204)
        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(1, 0x43)
        self.machine.registers.write_register(2, 0x42)
        instruction = self.isa.decode(0x200, 0x5120)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)

    def test_ld_byte(self) -> None:
        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(1, 0x42)
        self.assertEqual(self.machine.registers.read_register(1), 0x42)
        instruction = self.isa.decode(0x200, 0x61BD)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.read_register(1), 0xBD)

    def test_add_byte(self) -> None:
        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(5, 0xFE)
        self.assertEqual(self.machine.registers.read_register(5), 0xFE)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x7505)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.read_register(5), 0x03)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)

    def test_ld_register(self) -> None:
        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(3, 0x55)
        self.machine.registers.write_register(7, 0xAA)
        self.assertEqual(self.machine.registers.read_register(3), 0x55)
        self.assertEqual(self.machine.registers.read_register(7), 0xAA)
        instruction = self.isa.decode(0x200, 0x8370)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.read_register(3), 0xAA)
        self.assertEqual(self.machine.registers.read_register(7), 0xAA)

    def test_add_rejects_incorrect_operand_count(self) -> None:
        """Verify ADD requires exactly two operands."""
        with self.assertRaisesRegex(ValueError, "ADD requires exactly two operands"):
            self.isa.create_assembler_instruction("ADD", ())

    def test_add_rejects_out_of_range_operands(self) -> None:
        """Verify ADD rejects register indices and immediate values outside their ranges."""
        test_cases = (
            (
                "immediate form register index",
                (
                    AssemblerOperand(AssemblerOperandType.REGISTER, 0x10),
                    AssemblerOperand(AssemblerOperandType.VALUE, 0x23)
                ),
                "Register must be in the range V0 to VF"
            ),
            (
                "immediate value",
                (
                    AssemblerOperand(AssemblerOperandType.REGISTER, 0x1),
                    AssemblerOperand(AssemblerOperandType.VALUE, 0x100)
                ),
                "ADD immediate value must be in the range"
            ),
            (
                "register form first index",
                (
                    AssemblerOperand(AssemblerOperandType.REGISTER, 0x10),
                    AssemblerOperand(AssemblerOperandType.REGISTER, 0x2)
                ),
                "Register must be in the range V0 to VF"
            ),
            (
                "register form second index",
                (
                    AssemblerOperand(AssemblerOperandType.REGISTER, 0x1),
                    AssemblerOperand(AssemblerOperandType.REGISTER, 0x10)
                ),
                "Register must be in the range V0 to VF"
            )
        )
        for description, operands, expected_message in test_cases:
            with self.subTest(description=description):
                with self.assertRaisesRegex(ValueError, expected_message):
                    self.isa.create_assembler_instruction("ADD", operands)

    def test_register_operations_reject_invalid_operands(self) -> None:
        """Verify register operations reject invalid operand counts, types and indices."""
        test_cases = (
            (
                "incorrect operand count",
                (),
                "OR requires exactly two operands"
            ),
            (
                "invalid first operand type",
                (
                    AssemblerOperand(AssemblerOperandType.VALUE, 1),
                    AssemblerOperand(AssemblerOperandType.REGISTER, 2)
                ),
                "OR requires register operands"
            ),
            (
                "first register out of range",
                (
                    AssemblerOperand(AssemblerOperandType.REGISTER, 0x10),
                    AssemblerOperand(AssemblerOperandType.REGISTER, 2)
                ),
                "Register must be in the range V0 to VF"
            ),
            (
                "second register out of range",
                (
                    AssemblerOperand(AssemblerOperandType.REGISTER, 1),
                    AssemblerOperand(AssemblerOperandType.REGISTER, 0x10)
                ),
                "Register must be in the range V0 to VF"
            )
        )
        for description, operands, expected_message in test_cases:
            with self.subTest(description=description):
                with self.assertRaisesRegex(ValueError, expected_message):
                    self.isa.create_assembler_instruction("OR", operands)

    def test_or(self) -> None:
        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(3, 0x55)
        self.machine.registers.write_register(7, 0xAA)
        self.assertEqual(self.machine.registers.read_register(3), 0x55)
        self.assertEqual(self.machine.registers.read_register(7), 0xAA)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x8371)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.read_register(3), 0xFF)
        self.assertEqual(self.machine.registers.read_register(7), 0xAA)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)

    def test_and(self) -> None:
        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(3, 0x55)
        self.machine.registers.write_register(7, 0xAA)
        self.assertEqual(self.machine.registers.read_register(3), 0x55)
        self.assertEqual(self.machine.registers.read_register(7), 0xAA)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x8372)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.read_register(3), 0x00)
        self.assertEqual(self.machine.registers.read_register(7), 0xAA)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)


    def test_xor(self) -> None:
        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(3, 0x55)
        self.machine.registers.write_register(7, 0xAA)
        self.assertEqual(self.machine.registers.read_register(3), 0x55)
        self.assertEqual(self.machine.registers.read_register(7), 0xAA)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x8373)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.read_register(3), 0xFF)
        self.assertEqual(self.machine.registers.read_register(7), 0xAA)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)

    def test_add_register(self) -> None:
        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(3, 0x10)
        self.machine.registers.write_register(7, 0x20)
        self.machine.registers.write_register(15, 0x01)
        self.assertEqual(self.machine.registers.read_register(3), 0x10)
        self.assertEqual(self.machine.registers.read_register(7), 0x20)
        self.assertEqual(self.machine.registers.read_register(15), 0x01)
        instruction = self.isa.decode(0x200, 0x8374)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.read_register(3), 0x30)
        self.assertEqual(self.machine.registers.read_register(7), 0x20)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)

        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(3, 0xFF)
        self.machine.registers.write_register(7, 0x01)
        self.machine.registers.write_register(15, 0x00)
        self.assertEqual(self.machine.registers.read_register(3), 0xFF)
        self.assertEqual(self.machine.registers.read_register(7), 0x01)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x8374)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.read_register(3), 0x00)
        self.assertEqual(self.machine.registers.read_register(7), 0x01)
        self.assertEqual(self.machine.registers.read_register(15), 0x01)

        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(3, 0xFE)
        self.machine.registers.write_register(7, 0x03)
        self.machine.registers.write_register(15, 0x00)
        self.assertEqual(self.machine.registers.read_register(3), 0xFE)
        self.assertEqual(self.machine.registers.read_register(7), 0x03)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x8374)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.read_register(3), 0x01)
        self.assertEqual(self.machine.registers.read_register(7), 0x03)
        self.assertEqual(self.machine.registers.read_register(15), 0x01)

    def test_sub_register(self) -> None:
        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(3, 0x50)
        self.machine.registers.write_register(7, 0x20)
        self.machine.registers.write_register(15, 0x00)
        self.assertEqual(self.machine.registers.read_register(3), 0x50)
        self.assertEqual(self.machine.registers.read_register(7), 0x20)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x8375)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.read_register(3), 0x30)
        self.assertEqual(self.machine.registers.read_register(7), 0x20)
        self.assertEqual(self.machine.registers.read_register(15), 0x01)

        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(3, 0x20)
        self.machine.registers.write_register(7, 0x50)
        self.machine.registers.write_register(15, 0x01)
        self.assertEqual(self.machine.registers.read_register(3), 0x20)
        self.assertEqual(self.machine.registers.read_register(7), 0x50)
        self.assertEqual(self.machine.registers.read_register(15), 0x01)
        instruction = self.isa.decode(0x200, 0x8375)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.read_register(3), 0xD0)
        self.assertEqual(self.machine.registers.read_register(7), 0x50)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)

        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(3, 0x50)
        self.machine.registers.write_register(7, 0x50)
        self.machine.registers.write_register(15, 0x00)
        self.assertEqual(self.machine.registers.read_register(3), 0x50)
        self.assertEqual(self.machine.registers.read_register(7), 0x50)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x8375)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.read_register(3), 0x00)
        self.assertEqual(self.machine.registers.read_register(7), 0x50)
        self.assertEqual(self.machine.registers.read_register(15), 0x01)

    def test_shr(self) -> None:
        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(1, 0x02)
        self.machine.registers.write_register(2, 0x55)
        self.machine.registers.write_register(15, 0x01)
        self.assertEqual(self.machine.registers.read_register(1), 0x02)
        self.assertEqual(self.machine.registers.read_register(2), 0x55)
        self.assertEqual(self.machine.registers.read_register(15), 0x01)
        instruction = self.isa.decode(0x200, 0x8126)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.read_register(1), 0x01)
        self.assertEqual(self.machine.registers.read_register(2), 0x55)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)

        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(1, 0x03)
        self.machine.registers.write_register(2, 0x55)
        self.machine.registers.write_register(15, 0x00)
        self.assertEqual(self.machine.registers.read_register(1), 0x03)
        self.assertEqual(self.machine.registers.read_register(2), 0x55)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x8126)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.read_register(1), 0x01)
        self.assertEqual(self.machine.registers.read_register(2), 0x55)
        self.assertEqual(self.machine.registers.read_register(15), 0x01)

        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(1, 0x80)
        self.machine.registers.write_register(2, 0x55)
        self.machine.registers.write_register(15, 0x01)
        self.assertEqual(self.machine.registers.read_register(1), 0x80)
        self.assertEqual(self.machine.registers.read_register(2), 0x55)
        self.assertEqual(self.machine.registers.read_register(15), 0x01)
        instruction = self.isa.decode(0x200, 0x8126)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.read_register(1), 0x40)
        self.assertEqual(self.machine.registers.read_register(2), 0x55)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)

    def test_subn(self) -> None:
        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(1, 0x20)
        self.machine.registers.write_register(2, 0x50)
        self.machine.registers.write_register(15, 0x00)
        self.assertEqual(self.machine.registers.read_register(1), 0x20)
        self.assertEqual(self.machine.registers.read_register(2), 0x50)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x8127)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.read_register(1), 0x30)
        self.assertEqual(self.machine.registers.read_register(2), 0x50)
        self.assertEqual(self.machine.registers.read_register(15), 0x01)

        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(1, 0x50)
        self.machine.registers.write_register(2, 0x20)
        self.machine.registers.write_register(15, 0x01)
        self.assertEqual(self.machine.registers.read_register(1), 0x50)
        self.assertEqual(self.machine.registers.read_register(2), 0x20)
        self.assertEqual(self.machine.registers.read_register(15), 0x01)
        instruction = self.isa.decode(0x200, 0x8127)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.read_register(1), 0xD0)
        self.assertEqual(self.machine.registers.read_register(2), 0x20)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)

        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(1, 0x55)
        self.machine.registers.write_register(2, 0x55)
        self.machine.registers.write_register(15, 0x00)
        self.assertEqual(self.machine.registers.read_register(1), 0x55)
        self.assertEqual(self.machine.registers.read_register(2), 0x55)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x8127)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.read_register(1), 0x00)
        self.assertEqual(self.machine.registers.read_register(2), 0x55)
        self.assertEqual(self.machine.registers.read_register(15), 0x01)

    def test_shl(self) -> None:
        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(1, 0x40)
        self.machine.registers.write_register(2, 0x55)
        self.machine.registers.write_register(15, 0x01)
        self.assertEqual(self.machine.registers.read_register(1), 0x40)
        self.assertEqual(self.machine.registers.read_register(2), 0x55)
        self.assertEqual(self.machine.registers.read_register(15), 0x01)
        instruction = self.isa.decode(0x200, 0x812E)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.read_register(1), 0x80)
        self.assertEqual(self.machine.registers.read_register(2), 0x55)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)

        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(1, 0x80)
        self.machine.registers.write_register(2, 0x55)
        self.machine.registers.write_register(15, 0x00)
        self.assertEqual(self.machine.registers.read_register(1), 0x80)
        self.assertEqual(self.machine.registers.read_register(2), 0x55)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x812E)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.read_register(1), 0x00)
        self.assertEqual(self.machine.registers.read_register(2), 0x55)
        self.assertEqual(self.machine.registers.read_register(15), 0x01)

        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(1, 0xC1)
        self.machine.registers.write_register(2, 0x55)
        self.machine.registers.write_register(15, 0x00)
        self.assertEqual(self.machine.registers.read_register(1), 0xC1)
        self.assertEqual(self.machine.registers.read_register(2), 0x55)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)
        instruction = self.isa.decode(0x200, 0x812E)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.read_register(1), 0x82)
        self.assertEqual(self.machine.registers.read_register(2), 0x55)
        self.assertEqual(self.machine.registers.read_register(15), 0x01)

    def test_sne_register(self) -> None:
        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(1, 0x42)
        self.machine.registers.write_register(2, 0x43)
        instruction = self.isa.decode(0x200, 0x9120)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x204)

        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(1, 0x42)
        self.machine.registers.write_register(2, 0x42)
        instruction = self.isa.decode(0x200, 0x9120)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)

    def test_sne_rejects_invalid_operand_count_and_register(self) -> None:
        """Verify SNE rejects incorrect operand counts and invalid registers."""
        test_cases = (
            (
                "incorrect operand count",
                (),
                "SNE requires exactly two operands"
            ),
            (
                "first register out of range",
                (
                    AssemblerOperand(AssemblerOperandType.REGISTER, 0x10),
                    AssemblerOperand(AssemblerOperandType.REGISTER, 2)
                ),
                "Register must be in the range V0 to VF"
            )
        )
        for description, operands, expected_message in test_cases:
            with self.subTest(description=description):
                with self.assertRaisesRegex(ValueError, expected_message):
                    self.isa.create_assembler_instruction("SNE", operands)


    def test_drw_rejects_invalid_operands(self) -> None:
        """Verify DRW rejects invalid operand counts, types and register indices."""
        test_cases = (
            (
                "incorrect operand count",
                (),
                "DRW requires exactly three operands"
            ),
            (
                "first operand type",
                (
                    AssemblerOperand(AssemblerOperandType.VALUE, 1),
                    AssemblerOperand(AssemblerOperandType.REGISTER, 2),
                    AssemblerOperand(AssemblerOperandType.VALUE, 3)
                ),
                "DRW requires a register as the first operand"
            ),
            (
                "second operand type",
                (
                    AssemblerOperand(AssemblerOperandType.REGISTER, 1),
                    AssemblerOperand(AssemblerOperandType.VALUE, 2),
                    AssemblerOperand(AssemblerOperandType.VALUE, 3)
                ),
                "DRW requires a register as the second operand"
            ),
            (
                "first register out of range",
                (
                    AssemblerOperand(AssemblerOperandType.REGISTER, 0x10),
                    AssemblerOperand(AssemblerOperandType.REGISTER, 2),
                    AssemblerOperand(AssemblerOperandType.VALUE, 3)
                ),
                "Register must be in the range V0 to VF"
            ),
            (
                "second register out of range",
                (
                    AssemblerOperand(AssemblerOperandType.REGISTER, 1),
                    AssemblerOperand(AssemblerOperandType.REGISTER, 0x10),
                    AssemblerOperand(AssemblerOperandType.VALUE, 3)
                ),
                "Register must be in the range V0 to VF"
            )
        )
        for description, operands, expected_message in test_cases:
            with self.subTest(description=description):
                with self.assertRaisesRegex(ValueError, expected_message):
                    self.isa.create_assembler_instruction("DRW", operands)

    def test_ld_i(self) -> None:
        self.machine.registers.pc = 0x202
        self.assertEqual(self.machine.registers.i, 0x000)
        self.machine.registers.write_register(1, 0x00)
        self.machine.registers.write_register(2, 0x00)
        self.machine.registers.write_register(3, 0x00)
        self.machine.registers.write_register(4, 0x00)
        self.machine.registers.write_register(5, 0x00)
        self.machine.registers.write_register(6, 0x00)
        self.machine.registers.write_register(7, 0x00)
        self.machine.registers.write_register(8, 0x00)
        self.machine.registers.write_register(9, 0x00)
        self.machine.registers.write_register(10, 0x00)
        self.machine.registers.write_register(11, 0x00)
        self.machine.registers.write_register(12, 0x00)
        self.machine.registers.write_register(13, 0x00)
        self.machine.registers.write_register(14, 0x00)
        self.machine.registers.write_register(15, 0x00)
        instruction = self.isa.decode(0x200, 0xA456)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers.i, 0x456)
        self.assertEqual(self.machine.registers.read_register(1), 0x00)
        self.assertEqual(self.machine.registers.read_register(2), 0x00)
        self.assertEqual(self.machine.registers.read_register(3), 0x00)
        self.assertEqual(self.machine.registers.read_register(4), 0x00)
        self.assertEqual(self.machine.registers.read_register(5), 0x00)
        self.assertEqual(self.machine.registers.read_register(6), 0x00)
        self.assertEqual(self.machine.registers.read_register(7), 0x00)
        self.assertEqual(self.machine.registers.read_register(8), 0x00)
        self.assertEqual(self.machine.registers.read_register(9), 0x00)
        self.assertEqual(self.machine.registers.read_register(10), 0x00)
        self.assertEqual(self.machine.registers.read_register(11), 0x00)
        self.assertEqual(self.machine.registers.read_register(12), 0x00)
        self.assertEqual(self.machine.registers.read_register(13), 0x00)
        self.assertEqual(self.machine.registers.read_register(14), 0x00)
        self.assertEqual(self.machine.registers.read_register(15), 0x00)

    def test_jp_v0(self) -> None :
        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(0, 0x10)
        self.machine.registers.write_register(1, 0x43)
        instruction = self.isa.decode(0x200, 0xB456)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x466)

        self.machine.registers.pc = 0x202
        self.machine.registers.write_register(0, 0x00)
        self.machine.registers.write_register(1, 0x43)
        instruction = self.isa.decode(0x200, 0xB456)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x456)

    def test_execute_rnd_vx_nn_zero_mask(self) -> None:
        self.machine.registers[0x3] = 0xAB
        instruction = self.isa.decode(0x200, 0xC300)
        result = self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers[0x3], 0x00)
        self.assertEqual(self.machine.registers.pc, 0x200)
        self.assertEqual(result.display_changed, False)

    def test_execute_rnd_vx_nn_full_mask(self) -> None:
        self.machine.registers[0x3] = 0x00
        instruction = self.isa.decode(0x200, 0xC3FF)
        result = self.isa.execute(self.machine, instruction)
        self.assertGreaterEqual(self.machine.registers[0x3], 0x00)
        self.assertLessEqual(self.machine.registers[0x3], 0xFF)
        self.assertEqual(self.machine.registers.pc, 0x200)
        self.assertEqual(result.display_changed, False)

    def test_execute_rnd_vx_nn_masks_random_value(self) -> None:
        instruction = self.isa.decode(0x200, 0xC30F)
        for _ in range(100):
            self.machine.registers[0x3] = 0x00
            self.isa.execute(self.machine, instruction)
            self.assertLessEqual(self.machine.registers[0x3], 0x0F)

    def test_execute_drw_vx_vy_n(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.registers[0x3] = 2
        self.machine.registers[0x4] = 3
        self.machine.memory.write_byte(0x300, 0xA0)
        instruction = self.isa.decode(0x200, 0xD341)
        result = self.isa.execute(self.machine, instruction)
        self.assertTrue(result.display_changed)
        self.assertEqual(self.machine.registers[0xF], 0)
        self.assertTrue(self.machine.framebuffer.get_pixel(2, 3))
        self.assertTrue(self.machine.framebuffer.get_pixel(4, 3))
        self.assertFalse(self.machine.framebuffer.get_pixel(3, 3))

    def test_execute_drw_multiple_rows(self) -> None:
        self.machine.registers.i = 0x350
        self.machine.registers[0x3] = 1
        self.machine.registers[0x4] = 2
        self.machine.memory.write_byte(0x350, 0x80)
        self.machine.memory.write_byte(0x351, 0x40)
        self.machine.memory.write_byte(0x352, 0x20)
        instruction = self.isa.decode(0x200, 0xD343)
        result = self.isa.execute(self.machine, instruction)
        self.assertTrue(result.display_changed)
        self.assertEqual(self.machine.registers[0xF], 0)
        self.assertTrue(self.machine.framebuffer.get_pixel(1, 2))
        self.assertTrue(self.machine.framebuffer.get_pixel(2, 3))
        self.assertTrue(self.machine.framebuffer.get_pixel(3, 4))

    def test_execute_drw_collision(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.registers[0x3] = 2
        self.machine.registers[0x4] = 3
        self.machine.memory.write_byte(0x300, 0xA0)
        instruction = self.isa.decode(0x200, 0xD341)
        first_result = self.isa.execute(self.machine, instruction)
        self.assertTrue(first_result.display_changed)
        self.assertEqual(self.machine.registers[0xF], 0)
        self.assertTrue(self.machine.framebuffer.get_pixel(2, 3))
        self.assertTrue(self.machine.framebuffer.get_pixel(4, 3))
        second_result = self.isa.execute(self.machine, instruction)
        self.assertTrue(second_result.display_changed)
        self.assertEqual(self.machine.registers[0xF], 1)
        self.assertFalse(self.machine.framebuffer.get_pixel(2, 3))
        self.assertFalse(self.machine.framebuffer.get_pixel(4, 3))

    def test_execute_drw_no_collision(self) -> None:
        self.machine.registers[0xF] = 1
        self.machine.registers.i = 0x300
        self.machine.registers[0x3] = 0
        self.machine.registers[0x4] = 0
        self.machine.memory.write_byte(0x300, 0x80)
        instruction = self.isa.decode(0x200, 0xD341)
        result = self.isa.execute(self.machine, instruction)
        self.assertTrue(result.display_changed)
        self.assertEqual(self.machine.registers[0xF], 0)

    def test_execute_skp_vx_key_pressed(self) -> None:
        self.machine.registers.pc = 0x200
        self.machine.registers[0x3] = 0xA
        self.machine.keyboard.press(0xA)
        instruction = self.isa.decode(0x200, 0xE39E)
        result = self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertFalse(result.display_changed)

    def test_execute_skp_vx_key_not_pressed(self) -> None:
        self.machine.registers.pc = 0x200
        self.machine.registers[0x3] = 0xA
        instruction = self.isa.decode(0x200, 0xE39E)
        result = self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x200)
        self.assertFalse(result.display_changed)

    def test_execute_skp_vx_uses_vx(self) -> None:
        self.machine.registers.pc = 0x200
        self.machine.registers[0x3] = 0xA
        self.machine.registers[0x4] = 0xB
        self.machine.keyboard.press(0xB)
        instruction = self.isa.decode(0x200, 0xE39E)
        result = self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x200)
        self.assertFalse(result.display_changed)

    def test_execute_sknp_vx_key_pressed(self) -> None:
        self.machine.registers.pc = 0x200
        self.machine.registers[0x3] = 0xA
        self.machine.keyboard.press(0xA)
        instruction = self.isa.decode(0x200, 0xE3A1)
        result = self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x200)
        self.assertFalse(result.display_changed)

    def test_execute_sknp_vx_key_not_pressed(self) -> None:
        self.machine.registers.pc = 0x200
        self.machine.registers[0x3] = 0xA
        instruction = self.isa.decode(0x200, 0xE3A1)
        result = self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertFalse(result.display_changed)

    def test_execute_sknp_vx_uses_vx(self) -> None:
        self.machine.registers.pc = 0x200
        self.machine.registers[0x3] = 0xA
        self.machine.registers[0x4] = 0xB
        self.machine.keyboard.press(0xB)
        instruction = self.isa.decode(0x200, 0xE3A1)
        result = self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertFalse(result.display_changed)

    def test_execute_ld_vx_dt(self) -> None:
        self.machine.timers.delay_timer = 0x7B
        self.machine.registers[0x3] = 0x00
        self.machine.registers.pc = 0x200
        instruction = self.isa.decode(0x200, 0xF307)
        result = self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers[0x3], 0x7B)
        self.assertEqual(self.machine.timers.delay_timer, 0x7B)
        self.assertEqual(self.machine.registers.pc, 0x200)
        self.assertFalse(result.display_changed)

    def test_execute_ld_vx_dt_preserves_vf(self) -> None:
        self.machine.timers.delay_timer = 0x42
        self.machine.registers[0xF] = 0xAB
        instruction = self.isa.decode(0x200, 0xF507)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers[0x5], 0x42)
        self.assertEqual(self.machine.registers[0xF], 0xAB)

    def test_execute_ld_vx_k_no_key_pressed(self) -> None:
        self.machine.registers.pc = 0x202
        self.machine.registers[0x3] = 0xAB
        instruction = self.isa.decode(0x200, 0xF30A)
        result = self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x200)
        self.assertEqual(self.machine.registers[0x3], 0xAB)
        self.assertFalse(result.display_changed)

    def test_execute_ld_vx_k_key_pressed(self) -> None:
        self.machine.registers.pc = 0x202
        self.machine.registers[0x3] = 0xAB
        self.machine.keyboard.press(0x7)
        instruction = self.isa.decode(0x200, 0xF30A)
        result = self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers[0x3], 0x07)
        self.assertFalse(result.display_changed)

    def test_execute_ld_vx_k_uses_first_pressed_key(self) -> None:
        self.machine.registers.pc = 0x202
        self.machine.keyboard.press(0xA)
        self.machine.keyboard.press(0x3)
        instruction = self.isa.decode(0x200, 0xF50A)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x202)
        self.assertEqual(self.machine.registers[0x5], 0x03)

    def test_execute_ld_dt_vx(self) -> None:
        self.machine.registers.pc = 0x200
        self.machine.registers[0x3] = 0x7B
        self.machine.timers.delay_timer = 0x00
        instruction = self.isa.decode(0x200, 0xF315)
        result = self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.timers.delay_timer, 0x7B)
        self.assertEqual(self.machine.registers[0x3], 0x7B)
        self.assertEqual(self.machine.registers.pc, 0x200)
        self.assertFalse(result.display_changed)

    def test_execute_ld_dt_vx_zero(self) -> None:
        self.machine.registers[0x3] = 0x00
        self.machine.timers.delay_timer = 0xFF
        instruction = self.isa.decode(0x200, 0xF315)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.timers.delay_timer, 0x00)
        self.assertEqual(self.machine.registers[0x3], 0x00)

    def test_execute_ld_dt_vx_maximum(self) -> None:
        self.machine.registers[0x3] = 0xFF
        self.machine.timers.delay_timer = 0x00
        instruction = self.isa.decode(0x200, 0xF315)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.timers.delay_timer, 0xFF)
        self.assertEqual(self.machine.registers[0x3], 0xFF)

    def test_execute_ld_dt_vx_preserves_vf(self) -> None:
        self.machine.registers[0xF] = 0xAB
        self.machine.registers[0x3] = 0x42
        instruction = self.isa.decode(0x200, 0xF315)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers[0xF], 0xAB)
        self.assertEqual(self.machine.timers.delay_timer, 0x42)

    def test_execute_ld_st_vx(self) -> None:
        self.machine.registers.pc = 0x200
        self.machine.registers[0x3] = 0x7B
        self.machine.timers.delay_timer = 0x00
        instruction = self.isa.decode(0x200, 0xF318)
        result = self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.timers.sound_timer, 0x7B)
        self.assertEqual(self.machine.registers[0x3], 0x7B)
        self.assertEqual(self.machine.registers.pc, 0x200)
        self.assertFalse(result.display_changed)

    def test_execute_ld_st_vx_zero(self) -> None:
        self.machine.registers[0x3] = 0x00
        self.machine.timers.delay_timer = 0xFF
        instruction = self.isa.decode(0x200, 0xF318)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.timers.sound_timer, 0x00)
        self.assertEqual(self.machine.registers[0x3], 0x00)

    def test_execute_ld_st_vx_maximum(self) -> None:
        self.machine.registers[0x3] = 0xFF
        self.machine.timers.delay_timer = 0x00
        instruction = self.isa.decode(0x200, 0xF318)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.timers.sound_timer, 0xFF)
        self.assertEqual(self.machine.registers[0x3], 0xFF)

    def test_execute_ld_st_vx_preserves_vf(self) -> None:
        self.machine.registers[0xF] = 0xAB
        self.machine.registers[0x3] = 0x42
        instruction = self.isa.decode(0x200, 0xF318)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers[0xF], 0xAB)
        self.assertEqual(self.machine.timers.sound_timer, 0x42)

    def test_execute_add_i_vx(self) -> None:
        self.machine.registers.pc = 0x200
        self.machine.registers.i = 0x300
        self.machine.registers[0x3] = 0x42
        self.machine.registers[0xF] = 0xAB
        instruction = self.isa.decode(0x200, 0xF31E)
        result = self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.i, 0x342)
        self.assertEqual(self.machine.registers[0x3], 0x42)
        self.assertEqual(self.machine.registers[0xF], 0xAB)
        self.assertEqual(self.machine.registers.pc, 0x200)
        self.assertFalse(result.display_changed)

    def test_execute_add_i_vx_zero(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.registers[0x3] = 0x00
        instruction = self.isa.decode(0x200, 0xF31E)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.i, 0x300)

    def test_execute_add_i_vx_maximum_value(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.registers[0x3] = 0xFF
        instruction = self.isa.decode(0x200, 0xF31E)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.i, 0x3FF)

    def test_execute_add_i_vx_crosses_address_range(self) -> None:
        self.machine.registers.i = 0xFFF
        self.machine.registers[0x3] = 0x01
        instruction = self.isa.decode(0x200, 0xF31E)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.i, 0x000)

    def test_execute_ld_f_vx(self) -> None:
        self.machine.registers[0x3] = 0x0A

        instruction = self.isa.decode(0x200, 0xF329)
        result = self.isa.execute(self.machine, instruction)

        self.assertEqual(self.machine.registers.i, FONT_START + 0x0A * FONT_CHARACTER_SIZE)
        self.assertFalse(result.display_changed)

    def test_execute_ld_f_vx_uses_low_nibble(self) -> None:
        self.machine.registers[0x3] = 0xFA

        instruction = self.isa.decode(0x200, 0xF329)
        self.isa.execute(self.machine, instruction)

        self.assertEqual(self.machine.registers.i, FONT_START + 0x0A * FONT_CHARACTER_SIZE)

    def test_execute_ld_b_vx(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.registers[0x3] = 234

        instruction = self.isa.decode(0x200, 0xF333)
        result = self.isa.execute(self.machine, instruction)

        self.assertEqual(self.machine.memory.read_byte(0x300), 2)
        self.assertEqual(self.machine.memory.read_byte(0x301), 3)
        self.assertEqual(self.machine.memory.read_byte(0x302), 4)
        self.assertEqual(result.memory_range, (0x300, 0x302))

    def test_execute_ld_b_vx_zero(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.registers[0x3] = 0

        instruction = self.isa.decode(0x200, 0xF333)
        self.isa.execute(self.machine, instruction)

        self.assertEqual(self.machine.memory.read_byte(0x300), 0)
        self.assertEqual(self.machine.memory.read_byte(0x301), 0)
        self.assertEqual(self.machine.memory.read_byte(0x302), 0)

    def test_execute_ld_b_vx_maximum(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.registers[0x3] = 255

        instruction = self.isa.decode(0x200, 0xF333)
        self.isa.execute(self.machine, instruction)

        self.assertEqual(self.machine.memory.read_byte(0x300), 2)
        self.assertEqual(self.machine.memory.read_byte(0x301), 5)
        self.assertEqual(self.machine.memory.read_byte(0x302), 5)

    def test_execute_ld_i_vx(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.registers[0] = 0x10
        self.machine.registers[1] = 0x20
        self.machine.registers[2] = 0x30
        self.machine.registers[3] = 0x40

        instruction = self.isa.decode(0x200, 0xF355)
        result = self.isa.execute(self.machine, instruction)

        self.assertEqual(self.machine.memory.read_byte(0x300), 0x10)
        self.assertEqual(self.machine.memory.read_byte(0x301), 0x20)
        self.assertEqual(self.machine.memory.read_byte(0x302), 0x30)
        self.assertEqual(self.machine.memory.read_byte(0x303), 0x40)
        self.assertEqual(result.memory_range, (0x300, 0x303))

    def test_execute_ld_i_vx_preserves_i(self) -> None:
        self.machine.registers.i = 0x350
        self.machine.registers[0x2] = 0xAA

        instruction = self.isa.decode(0x200, 0xF255)
        self.isa.execute(self.machine, instruction)

        self.assertEqual(self.machine.registers.i, 0x350)

    def test_execute_ld_vx_i(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.memory.write_byte(0x300, 0x10)
        self.machine.memory.write_byte(0x301, 0x20)
        self.machine.memory.write_byte(0x302, 0x30)
        self.machine.memory.write_byte(0x303, 0x40)

        instruction = self.isa.decode(0x200, 0xF365)
        result = self.isa.execute(self.machine, instruction)

        self.assertEqual(self.machine.registers[0], 0x10)
        self.assertEqual(self.machine.registers[1], 0x20)
        self.assertEqual(self.machine.registers[2], 0x30)
        self.assertEqual(self.machine.registers[3], 0x40)
        self.assertEqual(self.machine.registers.i, 0x300)
        self.assertFalse(result.display_changed)

    def test_execute_ld_vx_i_does_not_modify_registers_above_vx(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.memory.write_byte(0x300, 0x12)
        self.machine.memory.write_byte(0x301, 0x34)

        self.machine.registers[0x2] = 0xAA
        self.machine.registers[0x3] = 0xBB

        instruction = self.isa.decode(0x200, 0xF165)
        self.isa.execute(self.machine, instruction)

        self.assertEqual(self.machine.registers[0], 0x12)
        self.assertEqual(self.machine.registers[1], 0x34)
        self.assertEqual(self.machine.registers[2], 0xAA)
        self.assertEqual(self.machine.registers[3], 0xBB)


    def test_encode_ld_byte(self) -> None:
        instruction = AssemblerInstruction( id=InstructionId.LD_BYTE, x=3, nn=0x42)
        self.assertEqual( self.isa.encode(instruction), 0x6342)


    def test_encode_add_register(self) -> None:
        instruction = AssemblerInstruction( id=InstructionId.ADD_REGISTER, x=3, y=4)
        self.assertEqual( self.isa.encode(instruction), 0x8344)


    def test_encode_drw(self) -> None:
        instruction = AssemblerInstruction( id=InstructionId.DRW, x=3, y=4, n=5)
        self.assertEqual( self.isa.encode(instruction), 0xD345)


    def test_encode_sys(self) -> None:
        instruction = AssemblerInstruction( id=InstructionId.SYS, nnn=0x234)
        self.assertEqual( self.isa.encode(instruction), 0x0234)


    def test_encode_cls(self) -> None:
        instruction = AssemblerInstruction( id=InstructionId.CLS)
        self.assertEqual( self.isa.encode(instruction), 0x00E0)


    def test_encode_ret(self) -> None:
        instruction = AssemblerInstruction( id=InstructionId.RET)
        self.assertEqual( self.isa.encode(instruction), 0x00EE)


    def test_encode_rejects_missing_operand(self) -> None:
        instruction = AssemblerInstruction( id=InstructionId.LD_BYTE, x=3)
        with self.assertRaises(ValueError):
            self.isa.encode(instruction)


    def test_encode_rejects_register_out_of_range(self) -> None:
        instruction = AssemblerInstruction( id=InstructionId.LD_BYTE, x=16, nn=0)
        with self.assertRaises(ValueError):
            self.isa.encode(instruction)


    def test_encode_rejects_byte_out_of_range(self) -> None:
        instruction = AssemblerInstruction( id=InstructionId.LD_BYTE, x=0, nn=256)
        with self.assertRaises(ValueError):
            self.isa.encode(instruction)


    def test_encode_rejects_address_out_of_range(self) -> None:
        instruction = AssemblerInstruction( id=InstructionId.JP, nnn=0x1000)
        with self.assertRaises(ValueError):
            self.isa.encode(instruction)

    def test_encode_rejects_unknown_instruction(self) -> None:
        """Verify encoding an unknown instruction raises ValueError."""
        instruction = AssemblerInstruction(id=InstructionId.UNKNOWN)
        with self.assertRaisesRegex(ValueError, "Cannot encode an unknown instruction"):
            self.isa.encode(instruction)

    def test_encode_add_byte(self) -> None:
        """Verify ADD Vx, byte encoding."""
        instruction = AssemblerInstruction(id=InstructionId.ADD_BYTE, x=3, nn=0x42)
        self.assertEqual(self.isa.encode(instruction), 0x7342)


    def test_analyze_se_register_nonzero_nibble(self) -> None:
        """Verify SE with a nonzero low nibble terminates control-flow analysis."""
        instruction = Instruction(
            address=0x200, opcode=0x5121, id=InstructionId.SE_REGISTER,
            x=1, y=2, n=1, nn=0x21, nnn=0x121
        )
        analysis = self.isa.analyze(instruction)
        self.assertEqual(analysis.control_flow.name, "TERMINATE")
        self.assertEqual(analysis.targets, ())


    def test_analyze_sys_terminates(self) -> None:
        """Verify SYS instructions terminate control flow analysis."""
        instruction = self.isa.decode(0x200, 0x0123)
        analysis = self.isa.analyze(instruction)
        self.assertEqual(analysis.control_flow.name, "TERMINATE")
        self.assertEqual(analysis.targets, ())


    def test_execute_sys_is_not_implemented(self) -> None:
        """Verify executing SYS raises NotImplementedError."""
        instruction = self.isa.decode(0x200, 0x0123)
        with self.assertRaisesRegex(NotImplementedError, "Opcode 0123 is not implemented"):
            self.isa.execute(self.machine, instruction)


    def test_execute_se_register_nonzero_nibble_is_not_implemented(self) -> None:
        """Verify SE with a nonzero low nibble raises NotImplementedError."""
        instruction = Instruction(
            address=0x200, opcode=0x5121, id=InstructionId.SE_REGISTER,
            x=1, y=2, n=1, nn=0x21, nnn=0x121
        )
        with self.assertRaisesRegex( NotImplementedError, "Opcode 5121 is not implemented"):
            self.isa.execute(self.machine, instruction)


    def test_assembler_operand_register(self) -> None:
        operand = self.isa.assembler_operand("V3")
        self.assertIsNotNone(operand)
        assert operand is not None
        self.assertEqual(operand.type, AssemblerOperandType.REGISTER)
        self.assertEqual(operand.value, 3)

    def test_assembler_operand_rejects_invalid_register_names(self) -> None:
        """Verify invalid register names are not resolved as assembler operands."""
        for name in ("VX", "VG", "V10", "V"):
            with self.subTest(name=name):
                self.assertIsNone(self.isa.assembler_operand(name))

    def test_jp_v0_rejects_nonzero_register(self) -> None:
        """Verify JP V0, address rejects a register other than V0."""
        operands = (
            AssemblerOperand(AssemblerOperandType.REGISTER, 1),
            AssemblerOperand(AssemblerOperandType.ADDRESS, 0x234)
        )
        with self.assertRaisesRegex(ValueError, "requires V0 as the first operand"):
            self.isa.create_assembler_instruction("JP", operands)


    def test_jp_v0_rejects_non_address_second_operand(self) -> None:
        """Verify JP V0, nnn requires an address as its second operand."""
        operands = (
            AssemblerOperand(AssemblerOperandType.REGISTER, 0),
            AssemblerOperand(AssemblerOperandType.VALUE, 0x23)
        )
        with self.assertRaisesRegex( ValueError, "requires an address as the second operand"):
            self.isa.create_assembler_instruction("JP", operands)

    def test_jp_v0_rejects_address_above_range(self) -> None:
        """Verify JP V0, nnn rejects an address above the 12-bit range."""
        operands = (
            AssemblerOperand(AssemblerOperandType.REGISTER, 0),
            AssemblerOperand(AssemblerOperandType.ADDRESS, 0x1000)
        )
        with self.assertRaisesRegex(ValueError, "JP address must be in the range"):
            self.isa.create_assembler_instruction("JP", operands)

    def test_encode_rejects_unsupported_instruction_id(self) -> None:
        """Verify encoding rejects an instruction ID not in the enum."""
        instruction = AssemblerInstruction(id=cast(InstructionId, 254))
        with self.assertRaisesRegex(ValueError, "Unsupported instruction ID: 254"):
            self.isa.encode(instruction)

    def test_instruction_references_reject_unknown_instruction(self) -> None:
        """Verify resource analysis rejects instructions without a handler."""
        instruction = AssemblerInstruction(id=InstructionId.UNKNOWN)
        with self.assertRaisesRegex(ValueError, "Unsupported instruction ID"):
            self.isa.instruction_references(instruction)

    def test_decode_id_rejects_negative_opcode(self) -> None:
        """Verify the decoder's outer fallback for a negative opcode."""
        self.assertIs(self.isa._decode_id(-0x1000), InstructionId.UNKNOWN)

    def test_assembler_operand_rejects_non_hex_register(self) -> None:
        """Verify a register name with a non-hexadecimal digit is rejected."""
        self.assertIsNone(self.isa.assembler_operand("VG"))

    def test_format_sys_as_data_directive(self) -> None:
        """Verify SYS instructions are formatted as data directives."""
        instruction = self.isa.decode(0x200, 0x0234)
        self.assertEqual(self.isa.format(instruction), "DW #0234")

    def test_format_se_register_with_nonzero_nibble(self) -> None:
        """Format a nonstandard SE-register opcode as data."""
        instruction = Instruction(
            address=0x200,
            opcode=0x5121,
            id=InstructionId.SE_REGISTER,
            x=1,
            y=2,
            n=1,
            nn=0x21,
            nnn=0x121
        )
        self.assertEqual(self.isa.format(instruction), "DATA 5121")

    def test_format_register_and_special_instructions(self) -> None:
        """Verify formatting of register operations and special instructions."""
        test_cases = (
            (0x8120, "LD V1, V2"),
            (0x8121, "OR V1, V2"),
            (0x8122, "AND V1, V2"),
            (0x8123, "XOR V1, V2"),
            (0x8124, "ADD V1, V2"),
            (0x8125, "SUB V1, V2"),
            (0x8126, "SHR V1"),
            (0x8127, "SUBN V1, V2"),
            (0x812E, "SHL V1"),
            (0xA123, "LD I, 123"),
            (0xB123, "JP V0, 123"),
            (0xC123, "RND V1, 23"),
            (0xD123, "DRW V1, V2, 3"),
            (0xE09E, "SKP V0"),
            (0xE0A1, "SKNP V0"),
            (0xF007, "LD V0, DT"),
            (0xF00A, "LD V0, K"),
            (0xF015, "LD DT, V0"),
            (0xF018, "LD ST, V0"),
            (0xF01E, "ADD I, V0"),
            (0xF029, "LD F, V0"),
            (0xF033, "LD B, V0"),
            (0xF055, "LD [I], V0"),
            (0xF065, "LD V0, [I]")
        )
        for opcode, expected in test_cases:
            with self.subTest(opcode=f"{opcode:04X}"):
                instruction = self.isa.decode(0x200, opcode)
                self.assertEqual(self.isa.format(instruction), expected)

    ###########################################################################
    # instruction references tests
    ###########################################################################
    def test_instruction_references(self) -> None:
        test_cases = [
            (
                AssemblerInstruction( id=InstructionId.LD_BYTE, x=3),
                ( ("V3", ReferenceAccess.WRITE),)
            ),
            (
                AssemblerInstruction( id=InstructionId.ADD_BYTE, x=3),
                ( ("V3", ReferenceAccess.READ_WRITE),)
            ),
            (
                AssemblerInstruction( id=InstructionId.LD_REGISTER, x=3, y=7),
                ( ("V3", ReferenceAccess.WRITE), ("V7", ReferenceAccess.READ))
            ),
            (
                AssemblerInstruction( id=InstructionId.ADD_REGISTER, x=3, y=7),
                ( ("V3", ReferenceAccess.READ_WRITE), ("V7", ReferenceAccess.READ), ("VF", ReferenceAccess.WRITE))
            ),
            (
                AssemblerInstruction( id=InstructionId.SHR, x=3, y=7),
                ( ("V3", ReferenceAccess.READ_WRITE), ("VF", ReferenceAccess.WRITE))
            ),
            (
                AssemblerInstruction( id=InstructionId.LD_I, nnn=0x456),
                ( ("I", ReferenceAccess.WRITE),)
            ),
            (
                AssemblerInstruction( id=InstructionId.JP_V0, nnn=0x456),
                ( ("V0", ReferenceAccess.READ),)
            ),
            (
                AssemblerInstruction( id=InstructionId.DRW, x=3, y=7, n=5),
                ( ("V3", ReferenceAccess.READ), ("V7", ReferenceAccess.READ), ("I", ReferenceAccess.READ), ("VF", ReferenceAccess.WRITE))
            ),
            (
                AssemblerInstruction( id=InstructionId.LD_VX_DT, x=3),
                ( ("V3", ReferenceAccess.WRITE), ("DT", ReferenceAccess.READ))
            ),
            (
                AssemblerInstruction( id=InstructionId.LD_VX_K, x=3),
                ( ("V3", ReferenceAccess.WRITE), ("KEY", ReferenceAccess.READ))
            ),
            (
                AssemblerInstruction( id=InstructionId.LD_DT_VX, x=3),
                ( ("DT", ReferenceAccess.WRITE), ("V3", ReferenceAccess.READ))
            ),
            (
                AssemblerInstruction( id=InstructionId.LD_ST_VX, x=3),
                ( ("ST", ReferenceAccess.WRITE), ("V3", ReferenceAccess.READ))
            ),
            (
                AssemblerInstruction( id=InstructionId.ADD_I_VX, x=3),
                ( ("I", ReferenceAccess.READ_WRITE), ("V3", ReferenceAccess.READ))
            ),
            (
                AssemblerInstruction( id=InstructionId.LD_F_VX, x=3),
                ( ("FONT_REGISTER", ReferenceAccess.WRITE), ("V3", ReferenceAccess.READ), ("I", ReferenceAccess.WRITE))),
            (
                AssemblerInstruction( id=InstructionId.LD_B_VX, x=3),
                ( ("BCD_REGISTER", ReferenceAccess.WRITE), ("V3", ReferenceAccess.READ), ("I", ReferenceAccess.READ))
            ),
            (
                AssemblerInstruction( id=InstructionId.LD_I_VX, x=3),
                ( ("I", ReferenceAccess.READ), ("V0", ReferenceAccess.READ), ("V1", ReferenceAccess.READ), ("V2", ReferenceAccess.READ), ("V3", ReferenceAccess.READ))
            ),
            (
                AssemblerInstruction( id=InstructionId.LD_VX_I, x=3),
                ( ("I", ReferenceAccess.READ), ("V0", ReferenceAccess.WRITE), ("V1", ReferenceAccess.WRITE), ("V2", ReferenceAccess.WRITE), ("V3", ReferenceAccess.WRITE))
            ),
            (
                AssemblerInstruction(id=InstructionId.SE_BYTE, x=3),
                (("V3", ReferenceAccess.READ),)
            ),
            (
                AssemblerInstruction(id=InstructionId.SE_REGISTER, x=3, y=7),
                (("V3", ReferenceAccess.READ), ("V7", ReferenceAccess.READ))
            ),
            (
                AssemblerInstruction(id=InstructionId.OR, x=3, y=7),
                (("V3", ReferenceAccess.READ_WRITE), ("V7", ReferenceAccess.READ))
            ),
            (
                AssemblerInstruction(id=InstructionId.LD_I_VX),
                (("I", ReferenceAccess.READ),)
            ),
            (
                AssemblerInstruction(id=InstructionId.LD_VX_I),
                (("I", ReferenceAccess.READ),)
            )
        ]

        for instruction, expected in test_cases:
            with self.subTest(instruction=instruction.id):
                references = self.isa.instruction_references(instruction)
                actual = tuple(
                    (reference.resource, reference.access)
                    for reference in references
                )
                self.assertEqual(actual, expected)


    def test_assembler_instruction_size(self) -> None:
        self.assertEqual( self.isa.assembler_instruction_size("CLS", 0), INSTRUCTION_SIZE)

    def test_assembler_operand_signatures(self) -> None:
        """Verify operand signatures for address, skip and comparison instructions."""
        test_cases = (
            (
                "SYS",
                1,
                ((AssemblerOperandType.ADDRESS,),)
            ),
            (
                "JP",
                2,
                ((AssemblerOperandType.REGISTER, AssemblerOperandType.ADDRESS),)
            ),
            (
                "SE",
                2,
                (
                    (AssemblerOperandType.REGISTER, AssemblerOperandType.VALUE),
                    (AssemblerOperandType.REGISTER, AssemblerOperandType.REGISTER)
                )
            ),
            (
                "SKP",
                1,
                ((AssemblerOperandType.REGISTER,),)
            ),
            (
                "UNKNOWN",
                0,
                ()
            )
        )
        for mnemonic, operand_count, expected in test_cases:
            with self.subTest(mnemonic=mnemonic, operand_count=operand_count):
                self.assertEqual( self.isa.assembler_operand_signatures(mnemonic, operand_count), expected)

if __name__ == "__main__":
    unittest.main(verbosity=2)


