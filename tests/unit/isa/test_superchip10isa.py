"""Unit tests for the Super-CHIP 1.0 instruction set architecture."""

import unittest

from chip8.isa.instructionid import InstructionId
from chip8.isa.isa import ControlFlow
from chip8.isa.superchip10isa import SuperChip10InstructionSetArchitecture
from emulator.constants import (
    SUPERCHIP_FONT_CHARACTER_SIZE,
    SUPERCHIP_FONT_START,
    SUPERCHIP_FONTSET,
)
from tests.helpers import create_machine


class TestSuperChip10InstructionSetArchitecture(unittest.TestCase):
    def setUp(self) -> None:
        self.machine = create_machine()
        self.isa = SuperChip10InstructionSetArchitecture()
        self.machine.set_isa(self.isa)

    def test_inherits_classic_instruction_decoding(self) -> None:
        self.assertIs(self.isa.decode(0x200, 0x6123).id, InstructionId.LD_BYTE)

    def test_decodes_superchip_instructions(self) -> None:
        cases = (
            (0x00FE, InstructionId.LOW_RES),
            (0x00FF, InstructionId.HIGH_RES),
            (0xD120, InstructionId.DRW_16),
            (0xF130, InstructionId.LD_HF_VX),
            (0xF175, InstructionId.LD_R_VX),
            (0xF185, InstructionId.LD_VX_R),
        )
        for opcode, expected in cases:
            with self.subTest(opcode=f"{opcode:04X}"):
                self.assertIs(self.isa.decode(0x200, opcode).id, expected)

    def test_rejects_opcodes_reserved_for_later_superchip_profiles(self) -> None:
        for opcode in (0x00C0, 0x00C1, 0x00CF, 0x00FB, 0x00FC):
            with self.subTest(opcode=f"{opcode:04X}"):
                self.assertIs(self.isa.decode(0x200, opcode).id, InstructionId.UNKNOWN)

    def test_preserves_classic_sys_instruction_decoding(self) -> None:
        self.assertIs(self.isa.decode(0x200, 0x0123).id, InstructionId.SYS)

    def test_formats_reserved_opcode_as_unknown_without_raising(self) -> None:
        instruction = self.isa.decode(0x200, 0x00FB)

        self.assertIs(instruction.id, InstructionId.UNKNOWN)
        self.assertEqual(self.isa.format(instruction), "UNKNOWN 00FB")

    def test_exit_instruction_terminates_execution(self) -> None:
        instruction = self.isa.decode(0x200, 0x00FD)

        result = self.isa.execute(self.machine, instruction)

        self.assertIs(instruction.id, InstructionId.EXIT)
        self.assertTrue(result.terminated)
        self.assertEqual(self.isa.format(instruction), "EXIT")

    def test_exit_instruction_terminates_static_analysis(self) -> None:
        instruction = self.isa.decode(0x200, 0x00FD)

        analysis = self.isa.analyze(instruction)

        self.assertEqual(analysis.control_flow.value, "terminate")
        self.assertEqual(analysis.targets, ())

    def test_non_branch_superchip_instructions_analyze_as_fallthrough(self) -> None:
        cases = (
            (0x00FE, InstructionId.LOW_RES),
            (0x00FF, InstructionId.HIGH_RES),
            (0xD120, InstructionId.DRW_16),
            (0xF130, InstructionId.LD_HF_VX),
            (0xF175, InstructionId.LD_R_VX),
            (0xF185, InstructionId.LD_VX_R),
        )
        for opcode, expected_id in cases:
            with self.subTest(opcode=f"{opcode:04X}"):
                instruction = self.isa.decode(0x240, opcode)
                analysis = self.isa.analyze(instruction)

                self.assertIs(instruction.id, expected_id)
                self.assertIs(analysis.control_flow, ControlFlow.NEXT)
                self.assertEqual(analysis.targets, (0x242,))
                self.assertTrue(analysis.is_code)

    def test_bxnn_analysis_does_not_claim_a_static_target(self) -> None:
        instruction = self.isa.decode(0x240, 0xB234)

        analysis = self.isa.analyze(instruction)

        self.assertIs(analysis.control_flow, ControlFlow.BRANCH)
        self.assertEqual(analysis.targets, ())
        self.assertTrue(analysis.is_code)

    def test_exit_instruction_prevents_further_machine_execution_until_reset(self) -> None:
        self.machine.registers.pc = 0x200
        self.machine.memory.write_byte(0x200, 0x00)
        self.machine.memory.write_byte(0x201, 0xFD)
        self.machine.memory.write_byte(0x202, 0x61)
        self.machine.memory.write_byte(0x203, 0x7B)

        exit_result = self.machine.execute_cycle()
        pc_after_exit = self.machine.registers.pc
        cycles_after_exit = self.machine.cycle_counter()
        halted_result = self.machine.execute_cycle()

        self.assertTrue(exit_result.terminated)
        self.assertTrue(halted_result.terminated)
        self.assertEqual(self.machine.registers.pc, pc_after_exit)
        self.assertEqual(self.machine.registers[1], 0)
        self.assertEqual(self.machine.cycle_counter(), cycles_after_exit)

        self.machine.reset()
        self.machine.registers.pc = 0x200
        self.machine.memory.write_byte(0x200, 0x61)
        self.machine.memory.write_byte(0x201, 0x7B)
        self.assertFalse(self.machine.execute_cycle().terminated)
        self.assertEqual(self.machine.registers[1], 0x7B)

    def test_bxnn_jumps_to_xnn_plus_vx(self) -> None:
        self.machine.registers[2] = 0x10
        instruction = self.isa.decode(0x200, 0xB234)

        result = self.isa.execute(self.machine, instruction)

        self.assertEqual(self.machine.registers.pc, 0x44)
        self.assertIsNone(result.bnnn_target)

    def test_bxnn_formats_register_and_byte_operand(self) -> None:
        instruction = self.isa.decode(0x200, 0xB234)

        self.assertEqual(self.isa.format(instruction), "JP V2, 34")

    def test_user_flags_only_support_v0_through_v7(self) -> None:
        self.assertIs(self.isa.decode(0x200, 0xF775).id, InstructionId.LD_R_VX)
        self.assertIs(self.isa.decode(0x200, 0xF875).id, InstructionId.UNKNOWN)
        self.assertIs(self.isa.decode(0x200, 0xF885).id, InstructionId.UNKNOWN)

    def test_high_resolution_instruction_changes_mode_without_clearing_pixels(self) -> None:
        self.machine.framebuffer.set_pixel(3, 4, True)
        result = self.isa.execute(self.machine, self.isa.decode(0x200, 0x00FF))
        self.assertEqual((self.machine.framebuffer.width, self.machine.framebuffer.height), (128, 64))
        self.assertTrue(self.machine.framebuffer.get_pixel(3, 4))
        self.assertTrue(result.display_changed)

    def test_low_resolution_instruction_restores_classic_mode(self) -> None:
        self.machine.framebuffer.set_resolution(128, 64)
        result = self.isa.execute(self.machine, self.isa.decode(0x200, 0x00FE))
        self.assertEqual((self.machine.framebuffer.width, self.machine.framebuffer.height), (64, 32))
        self.assertTrue(result.display_changed)

    def test_large_font_instruction_sets_index_register(self) -> None:
        self.machine.registers[3] = 0x2A
        self.isa.execute(self.machine, self.isa.decode(0x200, 0xF330))
        self.assertEqual(self.machine.registers.i, SUPERCHIP_FONT_START + 0xA * SUPERCHIP_FONT_CHARACTER_SIZE)

    def test_store_registers_increments_index_by_x(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.registers[0] = 0x12
        self.machine.registers[1] = 0x34
        self.machine.registers[2] = 0x56

        result = self.isa.execute(self.machine, self.isa.decode(0x200, 0xF255))

        self.assertEqual([self.machine.memory.read_byte(0x300 + offset) for offset in range(3)], [0x12, 0x34, 0x56])
        self.assertEqual(self.machine.registers.i, 0x302)
        self.assertEqual(result.memory_range, (0x300, 0x302))

    def test_load_registers_increments_index_by_x(self) -> None:
        self.machine.registers.i = 0x300
        for offset, value in enumerate((0x12, 0x34, 0x56)):
            self.machine.memory.write_byte(0x300 + offset, value)

        self.isa.execute(self.machine, self.isa.decode(0x200, 0xF265))

        self.assertEqual([self.machine.registers[index] for index in range(3)], [0x12, 0x34, 0x56])
        self.assertEqual(self.machine.registers.i, 0x302)

    def test_user_flags_save_and_restore(self) -> None:
        for index in range(8):
            self.machine.registers[index] = index * 17
        self.isa.execute(self.machine, self.isa.decode(0x200, 0xF775))
        for index in range(8):
            self.machine.registers[index] = 0
        self.isa.execute(self.machine, self.isa.decode(0x200, 0xF785))
        self.assertEqual([self.machine.registers[i] for i in range(8)], [i * 17 for i in range(8)])

    def test_draw_16x16_sprite_in_high_resolution(self) -> None:
        self.machine.framebuffer.set_resolution(128, 64)
        self.machine.registers[1] = 10
        self.machine.registers[2] = 12
        self.machine.registers.i = 0x300
        self.machine.memory.write_byte(0x300, 0x80)
        self.machine.memory.write_byte(0x301, 0x01)
        result = self.isa.execute(self.machine, self.isa.decode(0x200, 0xD120))
        self.assertTrue(self.machine.framebuffer.get_pixel(10, 12))
        self.assertTrue(self.machine.framebuffer.get_pixel(25, 12))
        self.assertEqual(self.machine.registers[0xF], 0)
        self.assertTrue(result.display_changed)

    def test_draw_16_opcode_uses_8x16_sprite_in_low_resolution(self) -> None:
        self.machine.registers[1] = 5
        self.machine.registers[2] = 6
        self.machine.registers.i = 0x300
        self.machine.memory.write_byte(0x300, 0x80)
        self.isa.execute(self.machine, self.isa.decode(0x200, 0xD120))
        self.assertTrue(self.machine.framebuffer.get_pixel(5, 6))
        self.assertFalse(self.machine.framebuffer.get_pixel(20, 6))

    def test_draw_16_opcode_reports_collision_and_erases_existing_pixel(self) -> None:
        self.machine.registers[1] = 7
        self.machine.registers[2] = 9
        self.machine.registers.i = 0x300
        self.machine.memory.write_byte(0x300, 0x80)
        self.machine.framebuffer.set_pixel(7, 9, True)

        result = self.isa.execute(self.machine, self.isa.decode(0x200, 0xD120))

        self.assertFalse(self.machine.framebuffer.get_pixel(7, 9))
        self.assertEqual(self.machine.registers[0xF], 1)
        self.assertTrue(result.display_changed)

    def test_draw_16x16_sprite_wraps_at_high_resolution_boundaries(self) -> None:
        self.machine.framebuffer.set_resolution(128, 64)
        self.machine.registers[1] = 127
        self.machine.registers[2] = 63
        self.machine.registers.i = 0x300
        # The first and last pixels of row zero are set; row one is empty.
        self.machine.memory.write_byte(0x300, 0x80)
        self.machine.memory.write_byte(0x301, 0x01)
        self.machine.memory.write_byte(0x302, 0x00)
        self.machine.memory.write_byte(0x303, 0x00)

        self.isa.execute(self.machine, self.isa.decode(0x200, 0xD120))

        self.assertTrue(self.machine.framebuffer.get_pixel(127, 63))
        self.assertTrue(self.machine.framebuffer.get_pixel(14, 63))
        self.assertEqual(self.machine.registers[0xF], 0)

    def test_draw_8x16_sprite_wraps_at_low_resolution_boundaries(self) -> None:
        self.machine.registers[1] = 63
        self.machine.registers[2] = 31
        self.machine.registers.i = 0x300
        self.machine.memory.write_byte(0x300, 0x81)
        self.machine.memory.write_byte(0x301, 0x80)

        self.isa.execute(self.machine, self.isa.decode(0x200, 0xD120))

        self.assertTrue(self.machine.framebuffer.get_pixel(63, 31))
        self.assertTrue(self.machine.framebuffer.get_pixel(6, 31))
        self.assertTrue(self.machine.framebuffer.get_pixel(63, 0))
        self.assertEqual(self.machine.registers[0xF], 0)

    def test_large_font_is_initialized_exactly_in_machine_memory(self) -> None:
        actual = [
            self.machine.memory.read_byte(SUPERCHIP_FONT_START + offset)
            for offset in range(len(SUPERCHIP_FONTSET))
        ]
        self.assertEqual(actual, SUPERCHIP_FONTSET)


if __name__ == "__main__":
    unittest.main(verbosity=2)
