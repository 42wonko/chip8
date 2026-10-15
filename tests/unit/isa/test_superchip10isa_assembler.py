"""Assembler interface tests for the Super-CHIP 1.0 ISA."""

import unittest

from assembler.operand import AssemblerOperand, AssemblerOperandType
from chip8.isa.classicisa import ClassicInstructionSetArchitecture
from chip8.isa.instructionid import InstructionId
from chip8.isa.reference import InstructionReference, ReferenceAccess
from chip8.isa.superchip10isa import SuperChip10InstructionSetArchitecture
from emulator.constants import INSTRUCTION_SIZE


class TestSuperChip10AssemblerInterface(unittest.TestCase):
    def setUp(self) -> None:
        self.isa = SuperChip10InstructionSetArchitecture()

    def test_additional_mnemonics_are_discoverable(self) -> None:
        self.assertTrue({"LOW", "HIGH", "EXIT"}.issubset(self.isa.assembler_mnemonics()))

    def test_zero_operand_instructions_construct_and_encode(self) -> None:
        cases = (("LOW", InstructionId.LOW_RES, 0x00FE),
                 ("HIGH", InstructionId.HIGH_RES, 0x00FF),
                 ("EXIT", InstructionId.EXIT, 0x00FD))
        for mnemonic, instruction_id, opcode in cases:
            with self.subTest(mnemonic=mnemonic):
                instruction = self.isa.create_assembler_instruction(mnemonic.lower(), ())
                self.assertIs(instruction.id, instruction_id)
                self.assertEqual(self.isa.encode(instruction), opcode)
                self.assertEqual(self.isa.instruction_references(instruction), ())

    def test_zero_operand_signatures_and_sizes(self) -> None:
        for mnemonic in ("LOW", "HIGH", "EXIT"):
            with self.subTest(mnemonic=mnemonic):
                self.assertEqual(self.isa.assembler_operand_signatures(mnemonic, 0), ((),))
                self.assertEqual(self.isa.assembler_operand_signatures(mnemonic, 1), ())
                self.assertEqual(self.isa.assembler_instruction_size(mnemonic, 0), INSTRUCTION_SIZE)
                self.assertEqual(self.isa.assembler_instruction_size(mnemonic, 1), 0)

    def test_zero_operand_instructions_reject_operands(self) -> None:
        operand = AssemblerOperand(type=AssemblerOperandType.VALUE, value=1)
        for mnemonic in ("LOW", "HIGH", "EXIT"):
            with self.subTest(mnemonic=mnemonic):
                with self.assertRaises(ValueError):
                    self.isa.create_assembler_instruction(mnemonic, (operand,))

    def test_classic_instruction_encoding_is_preserved(self) -> None:
        classic = ClassicInstructionSetArchitecture()
        classic_cls = classic.create_assembler_instruction("CLS", ())
        superchip_cls = self.isa.create_assembler_instruction("CLS", ())
        self.assertEqual(classic.encode(classic_cls), 0x00E0)
        self.assertEqual(self.isa.encode(superchip_cls), 0x00E0)


    def test_superchip_register_offset_jump_constructs_and_encodes(self) -> None:
        cases = ((0, 0x34, 0xB034), (2, 0x34, 0xB234), (15, 0xFF, 0xBFFF))
        for register, offset, opcode in cases:
            with self.subTest(register=register, offset=offset):
                instruction = self.isa.create_assembler_instruction(
                    "JP",
                    (
                        AssemblerOperand(AssemblerOperandType.REGISTER, register),
                        AssemblerOperand(AssemblerOperandType.VALUE, offset),
                    ),
                )
                self.assertIs(instruction.id, InstructionId.JP_V0)
                self.assertEqual((instruction.x, instruction.nn), (register, offset))
                self.assertEqual(self.isa.encode(instruction), opcode)
                self.assertEqual(
                    self.isa.instruction_references(instruction),
                    (InstructionReference(resource=f"V{register:X}", access=ReferenceAccess.READ),),
                )

    def test_superchip_register_offset_jump_signature_and_size(self) -> None:
        self.assertEqual(
            self.isa.assembler_operand_signatures("JP", 2),
            ((AssemblerOperandType.REGISTER, AssemblerOperandType.VALUE),),
        )
        self.assertEqual(self.isa.assembler_instruction_size("JP", 2), INSTRUCTION_SIZE)

    def test_superchip_register_offset_jump_rejects_invalid_operands(self) -> None:
        invalid_operands = (
            (
                AssemblerOperand(AssemblerOperandType.VALUE, 1),
                AssemblerOperand(AssemblerOperandType.VALUE, 2),
            ),
            (
                AssemblerOperand(AssemblerOperandType.REGISTER, 1),
                AssemblerOperand(AssemblerOperandType.ADDRESS, 0x234),
            ),
            (
                AssemblerOperand(AssemblerOperandType.REGISTER, 1),
                AssemblerOperand(AssemblerOperandType.VALUE, 0x100),
            ),
            (
                AssemblerOperand(AssemblerOperandType.REGISTER, 16),
                AssemblerOperand(AssemblerOperandType.VALUE, 1),
            ),
        )
        for operands in invalid_operands:
            with self.subTest(operands=operands):
                with self.assertRaises(ValueError):
                    self.isa.create_assembler_instruction("JP", operands)

    def test_superchip_special_loads_construct_and_encode(self) -> None:
        cases = (
            ("HF", "V3", InstructionId.LD_HF_VX, 0xF330),
            ("R", "V7", InstructionId.LD_R_VX, 0xF775),
            ("V7", "R", InstructionId.LD_VX_R, 0xF785),
        )
        for destination, source, instruction_id, opcode in cases:
            with self.subTest(destination=destination, source=source):
                operands = tuple(
                    operand for operand in (
                        self.isa.assembler_operand(destination),
                        self.isa.assembler_operand(source),
                    ) if operand is not None
                )
                instruction = self.isa.create_assembler_instruction("LD", operands)
                self.assertIs(instruction.id, instruction_id)
                self.assertEqual(self.isa.encode(instruction), opcode)
                self.assertEqual(len(self.isa.instruction_references(instruction)), 1)

    def test_superchip_special_load_signatures_and_sizes(self) -> None:
        expected = (
            (AssemblerOperandType.HIGH_FONT_REGISTER, AssemblerOperandType.REGISTER),
            (AssemblerOperandType.USER_FLAGS_REGISTER, AssemblerOperandType.REGISTER),
            (AssemblerOperandType.REGISTER, AssemblerOperandType.USER_FLAGS_REGISTER),
        )
        signatures = self.isa.assembler_operand_signatures("LD", 2)
        for signature in expected:
            self.assertIn(signature, signatures)
        self.assertEqual(self.isa.assembler_instruction_size("LD", 2), INSTRUCTION_SIZE)

    def test_superchip_user_flags_reject_registers_above_v7(self) -> None:
        for mnemonic, operands in (
            ("LD", (AssemblerOperand(AssemblerOperandType.USER_FLAGS_REGISTER, 0), AssemblerOperand(AssemblerOperandType.REGISTER, 8))),
            ("LD", (AssemblerOperand(AssemblerOperandType.REGISTER, 8), AssemblerOperand(AssemblerOperandType.USER_FLAGS_REGISTER, 0))),
        ):
            with self.subTest(operands=operands):
                with self.assertRaises(ValueError):
                    self.isa.create_assembler_instruction(mnemonic, operands)

    def test_classic_font_load_remains_distinct_from_high_font_load(self) -> None:
        register = AssemblerOperand(AssemblerOperandType.REGISTER, 3)
        classic_font = self.isa.create_assembler_instruction(
            "LD", (AssemblerOperand(AssemblerOperandType.FONT_REGISTER, 0), register)
        )
        high_font = self.isa.create_assembler_instruction(
            "LD", (AssemblerOperand(AssemblerOperandType.HIGH_FONT_REGISTER, 0), register)
        )
        self.assertIs(classic_font.id, InstructionId.LD_F_VX)
        self.assertEqual(self.isa.encode(classic_font), 0xF329)
        self.assertIs(high_font.id, InstructionId.LD_HF_VX)
        self.assertEqual(self.isa.encode(high_font), 0xF330)

    def test_draw_zero_height_assembles_as_superchip_16x16_draw(self) -> None:
        instruction = self.isa.create_assembler_instruction(
            "DRW",
            (
                AssemblerOperand(AssemblerOperandType.REGISTER, 1),
                AssemblerOperand(AssemblerOperandType.REGISTER, 2),
                AssemblerOperand(AssemblerOperandType.VALUE, 0),
            ),
        )

        self.assertIs(instruction.id, InstructionId.DRW_16)
        self.assertEqual(self.isa.encode(instruction), 0xD120)
        self.assertEqual(
            self.isa.instruction_references(instruction),
            (
                InstructionReference(resource="V1", access=ReferenceAccess.READ),
                InstructionReference(resource="V2", access=ReferenceAccess.READ),
                InstructionReference(resource="I", access=ReferenceAccess.READ),
                InstructionReference(resource="VF", access=ReferenceAccess.WRITE),
            ),
        )

    def test_draw_nonzero_height_remains_classic_draw(self) -> None:
        instruction = self.isa.create_assembler_instruction(
            "DRW",
            (
                AssemblerOperand(AssemblerOperandType.REGISTER, 1),
                AssemblerOperand(AssemblerOperandType.REGISTER, 2),
                AssemblerOperand(AssemblerOperandType.VALUE, 5),
            ),
        )

        self.assertIs(instruction.id, InstructionId.DRW)
        self.assertEqual(self.isa.encode(instruction), 0xD125)

    def test_classic_jump_encoding_remains_unchanged(self) -> None:
        instruction = self.isa.create_assembler_instruction(
            "JP", (AssemblerOperand(AssemblerOperandType.ADDRESS, 0x234),)
        )
        self.assertEqual(self.isa.encode(instruction), 0x1234)


if __name__ == "__main__":
    unittest.main(verbosity=2)
