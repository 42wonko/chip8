"""Unit tests for the Super-CHIP Modern instruction set architecture."""

import unittest
from unittest.mock import MagicMock

from assembler.operand import AssemblerOperand, AssemblerOperandType
from chip8.isa.instructionid import InstructionId
from chip8.isa.superchipmodernisa import SuperChipModernInstructionSetArchitecture
from emulator.chip8framebuffer import (
    SUPERCHIP_DISPLAY_HEIGHT,
    SUPERCHIP_DISPLAY_WIDTH,
    Chip8Framebuffer,
)
from emulator.constants import (
    DISPLAY_HEIGHT,
    DISPLAY_WIDTH,
    SUPERCHIP_FONT_CHARACTER_SIZE,
    SUPERCHIP_FONT_START,
)


class TestSuperChipModernInstructionSetArchitecture(unittest.TestCase):
    def setUp(self) -> None:
        self.machine = MagicMock()
        self.machine.framebuffer = Chip8Framebuffer(MagicMock(), MagicMock())
        self.isa = SuperChipModernInstructionSetArchitecture()

    def test_supports_superchip11_scroll_opcodes(self) -> None:
        for opcode, instruction_id in (
            (0x00C3, InstructionId.SCROLL_DOWN),
            (0x00FB, InstructionId.SCROLL_RIGHT),
            (0x00FC, InstructionId.SCROLL_LEFT),
        ):
            with self.subTest(opcode=f"{opcode:04X}"):
                self.assertIs(self.isa.decode(0x200, opcode).id, instruction_id)

    def test_shift_right_uses_vy_and_writes_vx(self) -> None:
        self.machine.registers.__getitem__.side_effect = lambda index: {1: 0x03, 2: 0x06, 15: 0}[index]
        self.machine.registers.write_register = MagicMock()
        instruction = self.isa.decode(0x200, 0x8126)
        self.isa.execute(self.machine, instruction)
        self.machine.registers.write_register.assert_any_call(15, 0)
        self.machine.registers.write_register.assert_any_call(1, 3)

    def test_shift_left_uses_vy_and_writes_vx(self) -> None:
        self.machine.registers.__getitem__.side_effect = lambda index: {1: 0x03, 2: 0x81, 15: 0}[index]
        self.machine.registers.write_register = MagicMock()
        instruction = self.isa.decode(0x200, 0x812E)
        self.isa.execute(self.machine, instruction)
        self.machine.registers.write_register.assert_any_call(15, 1)
        self.machine.registers.write_register.assert_any_call(1, 0x102)

    def test_shift_right_writes_flag_after_vx_when_x_is_vf(self) -> None:
        self.machine.registers.__getitem__.side_effect = lambda index: {2: 0x02}[index]
        self.machine.registers.write_register = MagicMock()
        instruction = self.isa.decode(0x200, 0x8F26)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(
            self.machine.registers.write_register.call_args_list,
            [unittest.mock.call(15, 1), unittest.mock.call(15, 0)]
        )

    def test_shift_left_writes_flag_after_vx_when_x_is_vf(self) -> None:
        self.machine.registers.__getitem__.side_effect = lambda index: {2: 0x81}[index]
        self.machine.registers.write_register = MagicMock()
        instruction = self.isa.decode(0x200, 0x8F2E)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(
            self.machine.registers.write_register.call_args_list,
            [unittest.mock.call(15, 0x102), unittest.mock.call(15, 1)]
        )

    def test_shift_right_preserves_flag_when_destination_is_vf(self) -> None:
        register_values = [0] * 16
        register_values[2] = 0x02
        self.machine.registers.__getitem__.side_effect = lambda index: register_values[index]
        self.machine.registers.write_register.side_effect = ( lambda index, value: register_values.__setitem__(index, value & 0xFF))
        instruction = self.isa.decode(0x200, 0x8F26)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(register_values[15], 0)

    def test_shift_left_preserves_flag_when_destination_is_vf(self) -> None:
        register_values = [0] * 16
        register_values[2] = 0x81
        self.machine.registers.__getitem__.side_effect = lambda index: register_values[index]
        self.machine.registers.write_register.side_effect = ( lambda index, value: register_values.__setitem__(index, value & 0xFF))
        instruction = self.isa.decode(0x200, 0x8F2E)
        self.isa.execute(self.machine, instruction)
        self.assertEqual(register_values[15], 1)

    def test_fx55_and_fx65_transfer_registers_without_incrementing_i(self) -> None:
        register_values = [0] * 16
        register_values[:3] = [0x12, 0x34, 0x56]
        self.machine.registers.i = 0x300
        self.machine.registers.__getitem__.side_effect = lambda index: register_values[index]
        self.machine.registers.write_register.side_effect = ( lambda index, value: register_values.__setitem__(index, value))
        memory_values: dict[int, int] = {}
        self.machine.memory.write_byte.side_effect = ( lambda address, value: memory_values.__setitem__(address, value))
        self.machine.memory.read_byte.side_effect = lambda address: memory_values[address]
        store = self.isa.decode(0x200, 0xF255)
        load = self.isa.decode(0x202, 0xF265)
        self.isa.execute(self.machine, store)
        self.assertEqual(memory_values, {0x300: 0x12, 0x301: 0x34, 0x302: 0x56})
        self.assertEqual(self.machine.registers.i, 0x300)
        register_values[:3] = [0, 0, 0]
        self.isa.execute(self.machine, load)
        self.assertEqual(register_values[:3], [0x12, 0x34, 0x56])
        self.assertEqual(self.machine.registers.i, 0x300)

    def test_fx55_stores_all_sixteen_registers_without_incrementing_i(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.registers.__getitem__.side_effect = ( lambda index: 0x10 + index)
        result = self.isa.execute( self.machine, self.isa.decode(0x200, 0xFF55),)
        self.assertEqual(
            self.machine.memory.write_byte.call_args_list,
            [
                unittest.mock.call(0x300 + register, 0x10 + register)
                for register in range(16)
            ]
        )
        self.assertEqual(self.machine.registers.i, 0x300)
        self.assertEqual(result.memory_range, (0x300, 0x30F))

    def test_fx65_loads_all_sixteen_registers_without_incrementing_i(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.registers.write_register = MagicMock()
        self.machine.memory.read_byte.side_effect = ( lambda address: 0xA0 + address - 0x300)
        self.isa.execute( self.machine, self.isa.decode(0x200, 0xFF65),)
        self.assertEqual(
            self.machine.memory.read_byte.call_args_list,
            [
                unittest.mock.call(0x300 + register)
                for register in range(16)
            ]
        )
        self.assertEqual(
            self.machine.registers.write_register.call_args_list,
            [
                unittest.mock.call(register, 0xA0 + register)
                for register in range(16)
            ]
        )
        self.assertEqual(self.machine.registers.i, 0x300)

    def test_fx65_does_not_report_a_memory_write_range(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.registers.write_register = MagicMock()
        self.machine.memory.read_byte.side_effect = ( lambda address: 0xA0 + address - 0x300)
        result = self.isa.execute( self.machine, self.isa.decode(0x200, 0xFF65),)
        self.assertIsNone(result.memory_range)
        self.machine.memory.write_byte.assert_not_called()
        self.assertEqual(self.machine.registers.i, 0x300)

    def test_drw_16_draws_sixteen_pixels_per_row_in_low_resolution(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.registers.__getitem__.side_effect = lambda index: {1: 4, 2: 5, 15: 0}[index]
        self.machine.registers.write_register = MagicMock()
        self.machine.memory.read_byte.side_effect = lambda address: {0x300: 0x00, 0x301: 0x80}.get(address, 0)
        self.machine.framebuffer.set_resolution(DISPLAY_WIDTH, DISPLAY_HEIGHT)
        result = self.isa.execute(self.machine, self.isa.decode(0x200, 0xD120))
        self.assertTrue(self.machine.framebuffer.get_pixel(12, 5))
        self.assertTrue(result.display_changed)

    def test_drw_16_draws_sixteen_pixels_per_row_in_high_resolution(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.registers.__getitem__.side_effect = lambda index: {1: 4, 2: 5, 15: 0}[index]
        self.machine.registers.write_register = MagicMock()
        self.machine.memory.read_byte.side_effect = lambda address: {0x300: 0x00, 0x301: 0x80}.get(address, 0)
        self.machine.framebuffer.set_resolution(SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        result = self.isa.execute(self.machine, self.isa.decode(0x200, 0xD120))
        self.assertTrue(self.machine.framebuffer.get_pixel(12, 5))
        self.assertTrue(result.display_changed)

    def test_drw_16_sets_vf_when_a_pixel_collides(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.registers.__getitem__.side_effect = lambda index: {1: 4, 2: 5, 15: 0}[index]
        self.machine.registers.write_register = MagicMock()
        self.machine.memory.read_byte.side_effect = lambda address: {0x300: 0x80, 0x301: 0x00}.get(address, 0)
        framebuffer = self.machine.framebuffer
        framebuffer.set_pixel(4, 5, True)
        result = self.isa.execute(self.machine, self.isa.decode(0x200, 0xD120))
        self.assertFalse(framebuffer.get_pixel(4, 5))
        self.machine.registers.write_register.assert_any_call(15, 1)
        self.assertTrue(result.display_changed)

    def test_large_font_instruction_is_available_in_modern_profile(self) -> None:
        self.machine.registers.__getitem__.side_effect = lambda index: {3: 0x2A}[index]
        self.isa.execute(self.machine, self.isa.decode(0x200, 0xF330))
        self.assertEqual( self.machine.registers.i, SUPERCHIP_FONT_START + 0xA * SUPERCHIP_FONT_CHARACTER_SIZE)

    def test_large_font_instruction_selects_glyph_f(self) -> None:
        self.machine.registers.__getitem__.side_effect = lambda index: {3: 0xFF}[index]
        self.isa.execute( self.machine, self.isa.decode(0x200, 0xF330))
        self.assertEqual( self.machine.registers.i, SUPERCHIP_FONT_START + 0xF * SUPERCHIP_FONT_CHARACTER_SIZE)

    def test_user_flag_opcodes_support_vf_in_modern_profile(self) -> None:
        self.assertIs(self.isa.decode(0x200, 0xFF75).id, InstructionId.LD_R_VX)
        self.assertIs(self.isa.decode(0x200, 0xFF85).id, InstructionId.LD_VX_R)

    def test_user_flag_save_and_restore_support_vf(self) -> None:
        self.machine.user_flags = bytearray(16)
        self.machine.registers.__getitem__.side_effect = lambda index: index * 7
        self.machine.registers.write_register = MagicMock()
        self.isa.execute(self.machine, self.isa.decode(0x200, 0xFF75))
        self.assertEqual(self.machine.user_flags[15], 105)
        self.machine.user_flags[15] = 0xA5
        self.isa.execute(self.machine, self.isa.decode(0x202, 0xFF85))
        self.machine.registers.write_register.assert_any_call(15, 0xA5)

    def test_resolution_switches_clear_display(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_pixel(1, 1, True)
        self.isa.execute(self.machine, self.isa.decode(0x200, 0x00FF))
        self.assertEqual((framebuffer.width, framebuffer.height), (SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT))
        self.assertFalse(framebuffer.get_pixel(1, 1))
        framebuffer.set_pixel(1, 1, True)
        self.isa.execute(self.machine, self.isa.decode(0x202, 0x00FE))
        self.assertEqual((framebuffer.width, framebuffer.height), (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.assertFalse(framebuffer.get_pixel(1, 1))
    def test_low_resolution_scroll_down_uses_one_pixel_in_modern_profile(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_pixel(10, 10, True)
        instruction = self.isa.decode(0x200, 0x00C1)
        self.isa.execute(self.machine, instruction)
        self.assertTrue(framebuffer.get_pixel(10, 11))
        self.assertFalse(framebuffer.get_pixel(10, 10))

    def test_low_resolution_horizontal_scroll_uses_four_pixels_in_modern_profile(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_pixel(10, 10, True)
        self.isa.execute(self.machine, self.isa.decode(0x200, 0x00FB))
        self.assertTrue(framebuffer.get_pixel(14, 10))
        self.assertFalse(framebuffer.get_pixel(10, 10))
        self.isa.execute(self.machine, self.isa.decode(0x202, 0x00FC))
        self.assertTrue(framebuffer.get_pixel(10, 10))
        self.assertFalse(framebuffer.get_pixel(14, 10))

    def test_low_resolution_scrolling_clips_edges_without_wrapping(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_pixel(10, DISPLAY_HEIGHT - 1, True)
        framebuffer.set_pixel(DISPLAY_WIDTH - 1, 12, True)
        framebuffer.set_pixel(0, 20, True)
        self.isa.execute(self.machine, self.isa.decode(0x200, 0x00C1))
        self.assertFalse(framebuffer.get_pixel(10, 0))
        self.assertFalse(framebuffer.get_pixel(10, DISPLAY_HEIGHT - 1))
        self.isa.execute(self.machine, self.isa.decode(0x202, 0x00FB))
        self.assertFalse(framebuffer.get_pixel(0, 12))
        self.assertFalse(framebuffer.get_pixel(DISPLAY_WIDTH - 1, 12))
        self.assertTrue(framebuffer.get_pixel(4, 21))
        self.isa.execute(self.machine, self.isa.decode(0x204, 0x00FC))
        self.assertFalse(framebuffer.get_pixel(DISPLAY_WIDTH - 1, 21))
        self.assertTrue(framebuffer.get_pixel(0, 21))

    def test_drw_16_sets_vf_to_zero_when_no_pixel_collides(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.registers.__getitem__.side_effect = lambda index: {1: 4, 2: 5, 15: 0}[index]
        self.machine.registers.write_register = MagicMock()
        self.machine.memory.read_byte.side_effect = lambda address: {0x300: 0x80, 0x301: 0x00}.get(address, 0)
        framebuffer = self.machine.framebuffer
        result = self.isa.execute(self.machine, self.isa.decode(0x200, 0xD120))
        self.assertTrue(framebuffer.get_pixel(4, 5))
        self.machine.registers.write_register.assert_any_call(15, 0)
        self.assertTrue(result.display_changed)

    def test_drw_16_wraps_sprite_at_right_display_edge(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.registers.__getitem__.side_effect = ( lambda index: {1: DISPLAY_WIDTH - 1, 2: 5, 15: 0}[index])
        self.machine.registers.write_register = MagicMock()
        self.machine.memory.read_byte.side_effect = ( lambda address: {0x300: 0xC0, 0x301: 0x00}.get(address, 0))
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution(DISPLAY_WIDTH, DISPLAY_HEIGHT)
        result = self.isa.execute(self.machine, self.isa.decode(0x200, 0xD120))
        self.assertTrue(framebuffer.get_pixel(DISPLAY_WIDTH - 1, 5))
        self.assertTrue(framebuffer.get_pixel(0, 5))
        self.machine.registers.write_register.assert_any_call(15, 0)
        self.assertTrue(result.display_changed)

    def test_drw_16_wraps_sprite_at_bottom_display_edge(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.registers.__getitem__.side_effect = ( lambda index: {1: 5, 2: DISPLAY_HEIGHT - 1, 15: 0}[index])
        self.machine.registers.write_register = MagicMock()
        self.machine.memory.read_byte.side_effect = (
            lambda address: {
                0x300: 0x80,
                0x301: 0x00,
                0x302: 0x80,
                0x303: 0x00,
            }.get(address, 0)
        )
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution(DISPLAY_WIDTH, DISPLAY_HEIGHT)
        result = self.isa.execute(self.machine, self.isa.decode(0x200, 0xD120))
        self.assertTrue(framebuffer.get_pixel(5, DISPLAY_HEIGHT - 1))
        self.assertTrue(framebuffer.get_pixel(5, 0))
        self.machine.registers.write_register.assert_any_call(15, 0)
        self.assertTrue(result.display_changed)

    def test_drw_16_detects_collision_in_high_resolution(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.registers.__getitem__.side_effect = ( lambda index: {1: 4, 2: 5, 15: 0}[index])
        self.machine.registers.write_register = MagicMock()
        self.machine.memory.read_byte.side_effect = ( lambda address: {0x300: 0x80, 0x301: 0x00}.get(address, 0))
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution( SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        framebuffer.set_pixel(4, 5, True)
        result = self.isa.execute( self.machine, self.isa.decode(0x200, 0xD120))
        self.assertFalse(framebuffer.get_pixel(4, 5))
        self.machine.registers.write_register.assert_any_call(15, 1)
        self.assertTrue(result.display_changed)

    def test_drw_16_reports_boolean_collision_for_multiple_colliding_rows(self) -> None:
        self.machine.registers.i = 0x300
        self.machine.registers.__getitem__.side_effect = lambda index: {1: 4, 2: 5, 15: 0}[index]
        self.machine.registers.write_register = MagicMock()
        self.machine.memory.read_byte.side_effect = lambda address: {
            0x300: 0x80,
            0x301: 0x00,
            0x302: 0x80,
            0x303: 0x00,
        }.get(address, 0)
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution(SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        framebuffer.set_pixel(4, 5, True)
        framebuffer.set_pixel(4, 6, True)
        result = self.isa.execute(self.machine, self.isa.decode(0x200, 0xD120))
        self.assertFalse(framebuffer.get_pixel(4, 5))
        self.assertFalse(framebuffer.get_pixel(4, 6))
        self.machine.registers.write_register.assert_any_call(15, 1)
        self.assertTrue(result.display_changed)

    def test_high_resolution_horizontal_scroll_moves_four_pixels_without_wrapping(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution( SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        framebuffer.set_pixel(10, 10, True)
        framebuffer.set_pixel(SUPERCHIP_DISPLAY_WIDTH - 1, 12, True)
        result = self.isa.execute( self.machine, self.isa.decode(0x200, 0x00FB))
        self.assertTrue(framebuffer.get_pixel(14, 10))
        self.assertFalse(framebuffer.get_pixel(10, 10))
        self.assertFalse(framebuffer.get_pixel(0, 12))
        self.assertFalse(framebuffer.get_pixel(SUPERCHIP_DISPLAY_WIDTH - 1, 12))
        self.assertTrue(result.display_changed)

    def test_high_resolution_scroll_down_clips_bottom_edge_without_wrapping(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution( SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        framebuffer.set_pixel(10, SUPERCHIP_DISPLAY_HEIGHT - 1, True)
        framebuffer.set_pixel(20, 10, True)
        result = self.isa.execute( self.machine, self.isa.decode(0x200, 0x00C1))
        self.assertFalse( framebuffer.get_pixel(10, SUPERCHIP_DISPLAY_HEIGHT - 1))
        self.assertTrue(framebuffer.get_pixel(20, 11))
        self.assertFalse(framebuffer.get_pixel(20, 10))
        self.assertTrue(result.display_changed)

    def test_user_flag_transfer_rejects_register_outside_vf(self) -> None:
        operands = (
            AssemblerOperand(AssemblerOperandType.USER_FLAGS_REGISTER, 0),
            AssemblerOperand(AssemblerOperandType.REGISTER, 16)
        )
        with self.assertRaisesRegex(ValueError, "Register must be in the range V0 to VF\\."):
            self.isa.create_assembler_instruction("LD", operands)

