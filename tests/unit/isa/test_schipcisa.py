"""Tests for the HP48 SCHIPC compatibility profile."""

import unittest
from unittest.mock import MagicMock

from assembler.operand import AssemblerOperand, AssemblerOperandType
from chip8.isa.instructionid import InstructionId
from chip8.isa.isa import ControlFlow
from chip8.isa.schipcisa import SCHIPCInstructionSetArchitecture
from emulator.chip8framebuffer import (
    SUPERCHIP_DISPLAY_HEIGHT,
    SUPERCHIP_DISPLAY_WIDTH,
    Chip8Framebuffer,
)
from emulator.constants import (
    DISPLAY_WIDTH,
    SUPERCHIP_FONT_CHARACTER_SIZE,
    SUPERCHIP_FONT_START,
)


class TestSCHIPCInstructionSetArchitecture(unittest.TestCase):
    def setUp(self) -> None:
        self.machine = MagicMock()
        self.machine.framebuffer = Chip8Framebuffer(MagicMock(), MagicMock())
        self.machine.registers.__getitem__.side_effect = lambda index: self._registers[index]
        self.machine.registers.__setitem__.side_effect = lambda index, value: self._registers.__setitem__(index, value)
        self.machine.registers.write_register.side_effect = lambda index, value: self._registers.__setitem__(index, value & 0xFF)
        self._registers = [0] * 16
        self.machine.registers.pc = 0x200
        self.machine.registers.i = 0
        self.isa = SCHIPCInstructionSetArchitecture()

    def test_rejects_zero_distance_scroll_opcode(self) -> None:
        self.assertIs(self.isa.decode(0x200, 0x00C0).id, InstructionId.UNKNOWN)
        self.assertIs(self.isa.decode(0x200, 0x00C1).id, InstructionId.SCROLL_DOWN)

    def test_assembler_rejects_zero_distance_scroll(self) -> None:
        with self.assertRaises(ValueError):
            self.isa.create_assembler_instruction( "SCD", (AssemblerOperand(AssemblerOperandType.VALUE, 0),))

    def test_assembler_accepts_maximum_scroll_distance(self) -> None:
        instruction = self.isa.create_assembler_instruction(
            "SCD", (AssemblerOperand(AssemblerOperandType.VALUE, 15),)
        )
        self.assertIs(instruction.id, InstructionId.SCROLL_DOWN)
        self.assertEqual(self.isa.encode(instruction), 0x00CF)

    def test_assembler_rejects_scroll_distance_above_maximum(self) -> None:
        with self.assertRaises(ValueError):
            self.isa.create_assembler_instruction( "SCD",
                (AssemblerOperand(AssemblerOperandType.VALUE, 16),)
            )

    def test_assembler_rejects_negative_scroll_distance(self) -> None:
        with self.assertRaises(ValueError):
            self.isa.create_assembler_instruction( "SCD", (AssemblerOperand(AssemblerOperandType.VALUE, -1),))

    def test_assembler_rejects_register_operand_for_scroll_down(self) -> None:
        with self.assertRaises(ValueError):
            self.isa.create_assembler_instruction( "SCD", (AssemblerOperand(AssemblerOperandType.REGISTER, 1),))

    def test_schipc_jump_uses_nnn_plus_v0(self) -> None:
        self.machine.registers[0] = 3
        instruction = self.isa.decode(0x200, 0xB234)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x237)

    def test_schipc_jump_does_not_truncate_offset_result_to_12_bits(self) -> None:
        self.machine.registers[0] = 0xFF
        instruction = self.isa.decode(0x200, 0xBFFF)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(self.machine.registers.pc, 0x10FE)

    def test_schipc_jump_assembler_encodes_bnnn(self) -> None:
        instruction = self.isa.create_assembler_instruction(
            "JP",
            (
                AssemblerOperand(AssemblerOperandType.REGISTER, 0),
                AssemblerOperand(AssemblerOperandType.ADDRESS, 0x234),
            ),
        )
        self.assertEqual(self.isa.encode(instruction), 0xB234)

    def test_schipc_jump_formats_as_v0_plus_12_bit_address(self) -> None:
        instruction = self.isa.decode(0x200, 0xB234)
        self.assertEqual(self.isa.format(instruction), "JP V0, 234")

    def test_schipc_jump_references_v0(self) -> None:
        instruction = self.isa.create_assembler_instruction(
            "JP",
            (
                AssemblerOperand(AssemblerOperandType.REGISTER, 0),
                AssemblerOperand(AssemblerOperandType.ADDRESS, 0x234),
            ),
        )
        references = self.isa.instruction_references(instruction)
        self.assertEqual(len(references), 1)
        self.assertEqual(references[0].resource, "V0")
        self.assertEqual(references[0].access.value, "read")

    def test_schipc_jump_assembler_rejects_non_v0_register(self) -> None:
        with self.assertRaises(ValueError):
            self.isa.create_assembler_instruction(
                "JP", (
                    AssemblerOperand(AssemblerOperandType.REGISTER, 1),
                    AssemblerOperand(AssemblerOperandType.ADDRESS, 0x234),
                )
            )

    def test_schipc_jump_assembler_rejects_wrong_first_operand_type(self) -> None:
        with self.assertRaisesRegex( ValueError, "Super-CHIP JP requires a register as the first operand"):
            self.isa.create_assembler_instruction(
                "JP",
                (
                    AssemblerOperand(AssemblerOperandType.VALUE, 0),
                    AssemblerOperand(AssemblerOperandType.ADDRESS, 0x234)
                )
            )

    def test_schipc_jump_assembler_rejects_address_above_12_bits(self) -> None:
        with self.assertRaises(ValueError):
            self.isa.create_assembler_instruction(
                "JP", (
                    AssemblerOperand(AssemblerOperandType.REGISTER, 0),
                    AssemblerOperand(AssemblerOperandType.ADDRESS, 0x1000),
                )
            )

    def test_low_resolution_scroll_uses_half_distance(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_pixel(3, 1, True)
        self.isa.execute(self.machine, self.isa.decode(0x200, 0x00C2))
        self.assertTrue(framebuffer.get_pixel(3, 2))
        self.assertFalse(framebuffer.get_pixel(3, 1))

    def test_high_resolution_scroll_down_clips_at_bottom_edge(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution( SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        framebuffer.set_pixel(3, SUPERCHIP_DISPLAY_HEIGHT - 4, True)
        framebuffer.set_pixel(5, SUPERCHIP_DISPLAY_HEIGHT - 1, True)
        result = self.isa.execute( self.machine, self.isa.decode(0x200, 0x00C3))
        self.assertTrue( framebuffer.get_pixel(3, SUPERCHIP_DISPLAY_HEIGHT - 1))
        self.assertFalse( framebuffer.get_pixel(5, SUPERCHIP_DISPLAY_HEIGHT - 1))
        self.assertTrue(result.display_changed)

    def test_high_resolution_scroll_down_uses_exact_distance(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution(SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        framebuffer.set_pixel(3, 1, True)
        result = self.isa.execute(self.machine, self.isa.decode(0x200, 0x00C2))
        self.assertTrue(framebuffer.get_pixel(3, 3))
        self.assertFalse(framebuffer.get_pixel(3, 1))
        self.assertTrue(result.display_changed)

    def test_register_store_increments_i_by_x(self) -> None:
        self.machine.registers.i = 0x300
        self._registers[2] = 0x77
        result = self.isa.execute( self.machine, self.isa.decode(0x200, 0xF255))
        self.assertEqual(self.machine.registers.i, 0x302)
        self.machine.memory.write_byte.assert_any_call(0x300, 0)
        self.machine.memory.write_byte.assert_any_call(0x301, 0)
        self.machine.memory.write_byte.assert_any_call(0x302, 0x77)
        self.assertEqual(result.memory_range, (0x300, 0x302))

    def test_register_load_increments_i_by_x(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.memory.read_byte.side_effect = lambda address: {
            0x300: 0x11,
            0x301: 0x22,
            0x302: 0x33,
        }[address]
        self.isa.execute(self.machine, self.isa.decode(0x200, 0xF265))
        self.assertEqual(self._registers[:3], [0x11, 0x22, 0x33])
        self.assertEqual(self.machine.registers.i, 0x302)

    def test_large_font_instruction_uses_low_nibble(self) -> None:
        self.machine.registers[3] = 0xFA
        self.isa.execute( self.machine, self.isa.decode(0x200, 0xF330))
        self.assertEqual( self.machine.registers.i, SUPERCHIP_FONT_START + 0xA * SUPERCHIP_FONT_CHARACTER_SIZE)

    def test_low_resolution_draw_uses_eight_by_sixteen_sprite(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.memory.write_byte(0x300, 0x80)
        self.machine.memory.write_byte(0x301, 0x40)
        self.machine.registers[1] = 4
        self.machine.registers[2] = 5
        instruction = self.isa.decode(0x200, 0xD120)
        self.isa.execute(self.machine, instruction)
        self.assertTrue(self.machine.framebuffer.get_pixel(4, 5))
        self.assertTrue(self.machine.framebuffer.get_pixel(5, 6))
        self.assertFalse(self.machine.framebuffer.get_pixel(12, 5))
        for y in range(5, 7):
            for x in range(4, 6):
                self.assertTrue(self.machine.framebuffer.get_pixel(x, y))

    def test_low_resolution_draw_detects_collision(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_pixel(4, 5, True)
        framebuffer.set_pixel(4, 6, True)
        self.machine.registers.i = 0x300
        self.machine.registers[1] = 4
        self.machine.registers[2] = 5
        self.machine.memory.read_byte.side_effect = ( lambda address: 0x80 if address in (0x300, 0x301) else 0)
        self.isa.execute( self.machine, self.isa.decode(0x200, 0xD120))
        self.assertFalse(framebuffer.get_pixel(4, 5))
        self.assertFalse(framebuffer.get_pixel(4, 6))
        self.assertEqual(self._registers[0xF], 1)

    def test_resolution_switch_preserves_existing_pixels(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution(SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        framebuffer.set_pixel(10, 10, True)
        result = self.isa.execute(self.machine, self.isa.decode(0x200, 0x00FE))
        self.assertEqual(framebuffer.width, DISPLAY_WIDTH)
        self.assertTrue(framebuffer.get_pixel(10, 10))
        self.assertTrue(result.display_changed)
        result = self.isa.execute(self.machine, self.isa.decode(0x202, 0x00FF))
        self.assertEqual(framebuffer.width, SUPERCHIP_DISPLAY_WIDTH)
        self.assertTrue(framebuffer.get_pixel(10, 10))
        self.assertTrue(result.display_changed)

    def test_high_resolution_draw_uses_boolean_collision_flag(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution(SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        framebuffer.set_pixel(4, 5, True)
        framebuffer.set_pixel(4, 6, True)
        self.machine.registers.i = 0x300
        self.machine.registers[1] = 4
        self.machine.registers[2] = 5
        self.machine.memory.read_byte.side_effect = lambda address: ( 0x80 if address in (0x300, 0x302) else 0)
        result = self.isa.execute(self.machine, self.isa.decode(0x200, 0xD120))
        self.assertEqual(self._registers[0xF], 1)
        self.assertFalse(framebuffer.get_pixel(4, 5))
        self.assertFalse(framebuffer.get_pixel(4, 6))
        self.assertTrue(result.display_changed)

    def test_high_resolution_draw_reports_multiple_collisions_as_one(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution(SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        framebuffer.set_pixel(4, 5, True)
        framebuffer.set_pixel(5, 5, True)
        self.machine.registers.i = 0x300
        self.machine.registers[1] = 4
        self.machine.registers[2] = 5
        self.machine.memory.read_byte.side_effect = ( lambda address: 0xC0 if address == 0x300 else 0)
        self.isa.execute(self.machine, self.isa.decode(0x200, 0xD120))
        self.assertFalse(framebuffer.get_pixel(4, 5))
        self.assertFalse(framebuffer.get_pixel(5, 5))
        self.assertEqual(self._registers[0xF], 1)

    def test_high_resolution_draw_does_not_count_clipped_rows_as_collisions(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution(SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        self.machine.registers.i = 0x300
        self.machine.registers[1] = 4
        self.machine.registers[2] = SUPERCHIP_DISPLAY_HEIGHT - 4
        self.machine.memory.read_byte.return_value = 0
        self.isa.execute(self.machine, self.isa.decode(0x200, 0xD120))
        self.assertEqual(self._registers[0xF], 0)

    def test_high_resolution_draw_wraps_at_bottom_edge(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution( SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        self.machine.registers.i = 0x300
        self.machine.registers[1] = 4
        self.machine.registers[2] = SUPERCHIP_DISPLAY_HEIGHT - 1
        self.machine.memory.read_byte.side_effect = ( lambda address: 0x80 if address in (0x300, 0x302) else 0)
        self.isa.execute( self.machine, self.isa.decode(0x200, 0xD120))
        self.assertTrue(framebuffer.get_pixel(4, SUPERCHIP_DISPLAY_HEIGHT - 1))
        self.assertTrue(framebuffer.get_pixel(4, 0))
        self.assertEqual(self._registers[0xF], 0)

    def test_high_resolution_draw_wraps_at_right_edge(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution( SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        self.machine.registers.i = 0x300
        self.machine.registers[1] = SUPERCHIP_DISPLAY_WIDTH - 1
        self.machine.registers[2] = 10
        self.machine.memory.read_byte.side_effect = ( lambda address: 0xC0 if address == 0x300 else 0)
        self.isa.execute( self.machine, self.isa.decode(0x200, 0xD120))
        self.assertTrue( framebuffer.get_pixel(SUPERCHIP_DISPLAY_WIDTH - 1, 10))
        self.assertTrue(framebuffer.get_pixel(0, 10))
        self.assertEqual(self._registers[0xF], 0)

    def test_high_resolution_draw_detects_collision_after_right_edge_wrap(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution( SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        framebuffer.set_pixel(0, 10, True)
        self.machine.registers.i = 0x300
        self.machine.registers[1] = SUPERCHIP_DISPLAY_WIDTH - 1
        self.machine.registers[2] = 10
        self.machine.memory.read_byte.side_effect = ( lambda address: 0xC0 if address == 0x300 else 0)
        self.isa.execute( self.machine, self.isa.decode(0x200, 0xD120))
        self.assertTrue( framebuffer.get_pixel(SUPERCHIP_DISPLAY_WIDTH - 1, 10))
        self.assertFalse(framebuffer.get_pixel(0, 10))
        self.assertEqual(self._registers[0xF], 1)

    def test_high_resolution_draw_detects_collision_after_bottom_edge_wrap(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution(SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        framebuffer.set_pixel(4, 0, True)
        self.machine.registers.i = 0x300
        self.machine.registers[1] = 4
        self.machine.registers[2] = SUPERCHIP_DISPLAY_HEIGHT - 1
        self.machine.memory.read_byte.side_effect = ( lambda address: 0x80 if address in (0x300, 0x302) else 0)
        self.isa.execute(self.machine, self.isa.decode(0x200, 0xD120))
        self.assertTrue(framebuffer.get_pixel(4, SUPERCHIP_DISPLAY_HEIGHT - 1))
        self.assertFalse(framebuffer.get_pixel(4, 0))
        self.assertEqual(self._registers[0xF], 1)

    def test_high_resolution_draw_renders_second_byte_of_sprite_row(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution(SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        self.machine.registers.i = 0x300
        self.machine.registers[1] = 4
        self.machine.registers[2] = 5
        self.machine.memory.read_byte.side_effect = ( lambda address: 0x01 if address == 0x301 else 0)
        self.isa.execute(self.machine, self.isa.decode(0x200, 0xD120))
        self.assertTrue(framebuffer.get_pixel(19, 5))
        self.assertFalse(framebuffer.get_pixel(4, 5))
        self.assertEqual(self._registers[0xF], 0)

    def test_user_flags_remain_limited_to_v0_through_v7(self) -> None:
        self.assertIs(self.isa.decode(0x200, 0xF775).id, InstructionId.LD_R_VX)
        self.assertIs(self.isa.decode(0x200, 0xF875).id, InstructionId.UNKNOWN)
        self.assertIs(self.isa.decode(0x200, 0xF885).id, InstructionId.UNKNOWN)

    def test_user_flags_save_and_restore_v0_through_v7(self) -> None:
        original_values = [0x10 + register for register in range(8)]
        self.machine.user_flags = bytearray(8)
        self._registers[:8] = original_values
        self.isa.execute(self.machine, self.isa.decode(0x200, 0xF775))
        self.assertEqual(list(self.machine.user_flags), original_values)
        self._registers[:8] = [0] * 8
        self.isa.execute(self.machine, self.isa.decode(0x202, 0xF785))
        self.assertEqual(self._registers[:8], original_values)

    def test_low_resolution_scroll_down_odd_distance_uses_integer_division( self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_pixel(3, 1, True)
        self.isa.execute(self.machine, self.isa.decode(0x200, 0x00C3))
        self.assertTrue(framebuffer.get_pixel(3, 2))
        self.assertFalse(framebuffer.get_pixel(3, 1))

    def test_low_resolution_scroll_down_one_row_moves_zero_pixels( self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_pixel(3, 1, True)
        self.isa.execute(self.machine, self.isa.decode(0x200, 0x00C1))
        self.assertTrue(framebuffer.get_pixel(3, 1))
        self.assertFalse(framebuffer.get_pixel(3, 2))

    def test_low_resolution_scroll_right_clips_pixels_at_right_edge( self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_pixel(DISPLAY_WIDTH - 1, 1, True)
        self.isa.execute(self.machine, self.isa.decode(0x200, 0x00FB))
        self.assertFalse(framebuffer.get_pixel(DISPLAY_WIDTH - 1, 1))
        self.assertFalse(framebuffer.get_pixel(0, 1))

    def test_high_resolution_scroll_right_moves_four_pixels(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution( SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        framebuffer.set_pixel(3, 1, True)
        self.isa.execute(self.machine, self.isa.decode(0x200, 0x00FB))
        self.assertTrue(framebuffer.get_pixel(7, 1))
        self.assertFalse(framebuffer.get_pixel(3, 1))

    def test_high_resolution_scroll_left_clips_pixels_at_left_edge( self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution( SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        framebuffer.set_pixel(3, 1, True)
        self.isa.execute(self.machine, self.isa.decode(0x200, 0x00FC))
        self.assertFalse(framebuffer.get_pixel(3, 1))
        self.assertFalse(framebuffer.get_pixel(SUPERCHIP_DISPLAY_WIDTH - 1, 1))

    def test_high_resolution_scroll_left_moves_four_pixels(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution(SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        framebuffer.set_pixel(7, 1, True)
        result = self.isa.execute(self.machine, self.isa.decode(0x200, 0x00FC))
        self.assertTrue(framebuffer.get_pixel(3, 1))
        self.assertFalse(framebuffer.get_pixel(7, 1))
        self.assertTrue(result.display_changed)

    def test_low_resolution_scroll_right_moves_two_pixels(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_pixel(3, 1, True)
        self.isa.execute(self.machine, self.isa.decode(0x200, 0x00FB))
        self.assertTrue(framebuffer.get_pixel(5, 1))
        self.assertFalse(framebuffer.get_pixel(3, 1))

    def test_high_resolution_scroll_right_clips_pixels_at_right_edge(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution(SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        framebuffer.set_pixel(SUPERCHIP_DISPLAY_WIDTH - 2, 1, True)
        self.isa.execute(self.machine, self.isa.decode(0x200, 0x00FB))
        self.assertFalse(framebuffer.get_pixel(SUPERCHIP_DISPLAY_WIDTH - 2, 1))
        self.assertFalse(framebuffer.get_pixel(2, 1))

    def test_low_resolution_scroll_left_clips_pixels_at_left_edge(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_pixel(1, 1, True)
        self.isa.execute(self.machine, self.isa.decode(0x200, 0x00FC))
        self.assertFalse(framebuffer.get_pixel(0, 1))
        self.assertFalse(framebuffer.get_pixel(framebuffer.width - 1, 1))

    def test_low_resolution_scroll_left_moves_two_pixels(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_pixel(6, 1, True)
        self.isa.execute(self.machine, self.isa.decode(0x200, 0x00FC))
        self.assertTrue(framebuffer.get_pixel(4, 1))
        self.assertFalse(framebuffer.get_pixel(6, 1))

    def test_shift_right_uses_vx_not_vy(self) -> None:
        self._registers[1] = 0x03
        self._registers[2] = 0x80
        self.isa.execute(self.machine, self.isa.decode(0x200, 0x8126))
        self.assertEqual(self._registers[1], 0x01)
        self.assertEqual(self._registers[2], 0x80)
        self.assertEqual(self._registers[0xF], 1)

    def test_shift_left_uses_vx_not_vy(self) -> None:
        self._registers[1] = 0x81
        self._registers[2] = 0x03
        self.isa.execute(self.machine, self.isa.decode(0x200, 0x812E))
        self.assertEqual(self._registers[1], 0x02)
        self.assertEqual(self._registers[2], 0x03)
        self.assertEqual(self._registers[0xF], 1)

    def test_register_store_stops_at_memory_boundary(self) -> None:
        self.machine.registers.i = 0xFFF
        self._registers[0] = 0x12
        self._registers[1] = 0x34
        def write_byte(address: int, value: int) -> None:
            if address >= 0x1000:
                raise IndexError("Memory address out of range")
        self.machine.memory.write_byte.side_effect = write_byte
        with self.assertRaises(IndexError):
            self.isa.execute(self.machine, self.isa.decode(0x200, 0xF155))
        self.machine.memory.write_byte.assert_any_call(0xFFF, 0x12)
        self.machine.memory.write_byte.assert_any_call(0x1000, 0x34)
        self.assertEqual(self.machine.memory.write_byte.call_count, 2)
        self.assertEqual(self.machine.registers.i, 0xFFF)

    def test_register_load_stops_at_memory_boundary(self) -> None:
        self.machine.registers.i = 0xFFF
        self.machine.memory.read_byte.side_effect = lambda address: (
            0x12 if address == 0xFFF else (_ for _ in ()).throw( IndexError("Memory address out of range")))
        with self.assertRaises(IndexError):
            self.isa.execute(self.machine, self.isa.decode(0x200, 0xF165))
        self.assertEqual(self._registers[0], 0x12)
        self.assertEqual(self._registers[1], 0)
        self.assertEqual(self.machine.registers.i, 0xFFF)


    def test_register_store_transfers_all_sixteen_registers(self) -> None:
        self.machine.registers.i = 0x300
        self._registers[:] = [0x10 + register for register in range(16)]
        result = self.isa.execute( self.machine, self.isa.decode(0x200, 0xFF55))
        actual_writes = [ call.args for call in self.machine.memory.write_byte.call_args_list ]
        expected_writes = [ (0x300 + register, 0x10 + register) for register in range(16) ]
        self.assertEqual(actual_writes, expected_writes)
        self.assertEqual(self.machine.registers.i, 0x30F)
        self.assertEqual(result.memory_range, (0x300, 0x30F))


    def test_register_load_transfers_all_sixteen_registers(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.memory.read_byte.side_effect = ( lambda address: 0xA0 + address - 0x300)
        self.isa.execute( self.machine, self.isa.decode(0x200, 0xFF65))
        self.assertEqual( self._registers, [0xA0 + register for register in range(16)])
        self.assertEqual(self.machine.registers.i, 0x30F)
        actual_reads = [ call.args for call in self.machine.memory.read_byte.call_args_list ]
        expected_reads = [ (0x300 + register) for register in range(16) ]
        self.assertEqual(actual_reads, [(address,) for address in expected_reads])

    def test_exit_is_terminal_control_flow(self) -> None:
        instruction = self.isa.decode(0x200, 0x00FD)
        analysis = self.isa.analyze(instruction)
        self.assertIs(analysis.control_flow, ControlFlow.TERMINATE)
        self.assertEqual(analysis.targets, ())
        self.assertTrue(analysis.is_code)

    def test_schipc_jump_analysis_has_no_static_target(self) -> None:
        instruction = self.isa.decode(0x240, 0xB234)
        analysis = self.isa.analyze(instruction)
        self.assertIs(analysis.control_flow, ControlFlow.BRANCH)
        self.assertEqual(analysis.targets, ())
        self.assertTrue(analysis.is_code)

