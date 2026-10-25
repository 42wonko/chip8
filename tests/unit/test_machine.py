"""
@file test_machine.py
@brief Test for the CHIP-8 machine.
"""
import unittest
from unittest.mock import patch

from chip8.isa.superchip10isa import SuperChip10InstructionSetArchitecture
from controller.diagnostic import DiagnosticSource
from controller.diagnostics import Diagnostics
from controller.logging import LogManager
from emulator.chip8machine import Chip8Machine
from emulator.constants import PROGRAM_START
from emulator.stepresult import StepResult
from tests.helpers import create_machine, write_opcode


class TestChip8Machine(unittest.TestCase):
    def test_fetch_instruction(self) -> None:
        machine = create_machine()
        machine.memory.write_byte( 0x200, 0x6A)
        machine.memory.write_byte( 0x201, 0x05)
        instruction = machine.fetch_instruction()
        self.assertEqual(instruction.address, 0x200)
        self.assertEqual(instruction.opcode, 0x6A05)
        self.assertEqual(machine.registers.pc, 0x202)

    def test_machine_uses_isa_for_execution(self) -> None:
        machine = create_machine()
        write_opcode(machine, 0x6001)
        machine.execute_cycle()
        self.assertEqual(machine.registers[0], 0x01)

    def test_peek_instruction_does_not_advance_program_counter(self) -> None:
        machine = create_machine()
        write_opcode(machine, 0x6A05)
        initial_pc = machine.registers.pc
        instruction = machine.peek_instruction()
        self.assertEqual(instruction.address, initial_pc)
        self.assertEqual(instruction.opcode, 0x6A05)
        self.assertEqual(machine.registers.pc, initial_pc)

    def test_peek_instruction_does_not_modify_memory(self) -> None:
        machine = create_machine()
        write_opcode(machine, 0x6A05)
        initial_bytes = ( machine.memory.read_byte(0x200), machine.memory.read_byte(0x201))
        machine.peek_instruction()
        self.assertEqual(
            (
                machine.memory.read_byte(0x200),
                machine.memory.read_byte(0x201)
            ),
            initial_bytes
        )

    def test_load_rom_resets_registers_and_loads_program(self) -> None:
        machine = create_machine()
        machine.registers[0] = 0xAB
        machine.registers.pc = 0x300
        machine.load_rom(bytes([0x6A, 0x05]))
        self.assertEqual(machine.registers[0], 0)
        self.assertEqual(machine.registers.pc, 0x200)
        self.assertEqual(machine.memory.read_byte(0x200), 0x6A)
        self.assertEqual(machine.memory.read_byte(0x201), 0x05)

    def test_reset_clears_cycle_counter(self) -> None:
        machine = create_machine()
        write_opcode(machine, 0x6001)
        machine.execute_cycle()
        self.assertEqual(machine.cycle_counter(), 1)
        machine.reset()
        self.assertEqual(machine.cycle_counter(), 0)

    def test_execute_cycle_traces_registers_before_and_after_execution(self) -> None:
        machine = create_machine()
        write_opcode(machine, 0x6001)
        with unittest.mock.patch.object(machine._trace_reporter, "trace") as trace:
            machine.execute_cycle()
        trace.assert_called_once()
        record = trace.call_args.args[0]
        self.assertEqual(record.cycle, 0)
        self.assertEqual(record.registers_before[0], 0)
        self.assertEqual(record.registers_after[0], 1)
        self.assertEqual(machine.cycle_counter(), 1)

    def test_execute_cycle_does_not_advance_after_termination(self) -> None:
        machine = create_machine()
        write_opcode(machine, 0x00FD)
        machine.set_isa(SuperChip10InstructionSetArchitecture())
        result = machine.execute_cycle()
        self.assertTrue(result.terminated)
        pc_after_exit = machine.registers.pc
        cycles_after_exit = machine.cycle_counter()
        result = machine.execute_cycle()
        self.assertTrue(result.terminated)
        self.assertEqual(machine.registers.pc, pc_after_exit)
        self.assertEqual(machine.cycle_counter(), cycles_after_exit)

    def test_execute_cycle_translates_unsupported_instruction_error(self) -> None:
        machine = create_machine()
        write_opcode(machine, 0xFFFF)
        with unittest.mock.patch.object( machine.isa, "execute", side_effect=ValueError("unsupported instruction")):
            with self.assertRaisesRegex( NotImplementedError, "Opcode FFFF is not implemented.") as context:
                machine.execute_cycle()
        self.assertIsInstance(context.exception.__cause__, ValueError)

    def test_reset_allows_execution_after_termination(self) -> None:
        machine = create_machine()
        machine.set_isa(SuperChip10InstructionSetArchitecture())
        write_opcode(machine, 0x00FD)
        result = machine.execute_cycle()
        self.assertTrue(result.terminated)
        machine.reset()
        write_opcode(machine, 0x6001)
        result = machine.execute_cycle()
        self.assertFalse(result.terminated)
        self.assertEqual(machine.registers[0], 1)
        self.assertEqual(machine.cycle_counter(), 1)

    def test_execute_cycle_traces_instruction_metadata(self) -> None:
        machine = create_machine()
        write_opcode(machine, 0x6A05)
        with unittest.mock.patch.object(machine._trace_reporter, "trace") as trace:
            machine.execute_cycle()
        trace.assert_called_once()
        record = trace.call_args.args[0]
        self.assertEqual(record.instruction.address, 0x200)
        self.assertEqual(record.instruction.opcode, 0x6A05)

    def test_execute_cycle_traces_display_and_memory_changes(self) -> None:
        machine = create_machine()
        write_opcode(machine, 0x6001)
        result = StepResult( display_changed=True, memory_range=(0x300, 0x30F))
        with patch.object(machine.isa, "execute", return_value=result):
            with patch.object(machine._trace_reporter, "trace") as trace:
                machine.execute_cycle()
        record = trace.call_args.args[0]
        self.assertTrue(record.display_changed)
        self.assertEqual(record.memory_range, (0x300, 0x30F))

    def test_tick_timers_advances_delay_and_sound_timers(self) -> None:
        machine = create_machine()
        machine.timers.delay_timer = 2
        machine.timers.sound_timer = 3
        machine.tick_timers()
        self.assertEqual(machine.timers.delay_timer, 1)
        self.assertEqual(machine.timers.sound_timer, 2)

    def test_execute_cycle_does_not_trace_or_count_unsupported_instruction(self) -> None:
        machine = create_machine()
        write_opcode(machine, 0xFFFF)
        with unittest.mock.patch.object(
            machine.isa,
            "execute",
            side_effect=ValueError("unsupported instruction")
        ):
            with unittest.mock.patch.object(machine._trace_reporter, "trace") as trace:
                with self.assertRaises(NotImplementedError):
                    machine.execute_cycle()
        self.assertEqual(machine.cycle_counter(), 0)
        trace.assert_not_called()

    def test_execute_cycle_traces_timer_values_before_and_after(self) -> None:
        machine = create_machine()
        machine.timers.delay_timer = 2
        machine.timers.sound_timer = 3
        machine.registers[0] = 7
        write_opcode(machine, 0xF015)
        with unittest.mock.patch.object(machine._trace_reporter, "trace") as trace:
            machine.execute_cycle()
        trace.assert_called_once()
        record = trace.call_args.args[0]
        self.assertEqual(record.delay_timer_before, 2)
        self.assertEqual(record.delay_timer_after, 7)
        self.assertEqual(record.sound_timer_before, 3)
        self.assertEqual(record.sound_timer_after, 3)

    def test_reset_clears_user_flags(self) -> None:
        machine = create_machine()
        machine.user_flags[:] = bytes(range(len(machine.user_flags)))
        machine.reset()
        self.assertEqual( machine.user_flags, bytearray(len(machine.user_flags)))

    def test_reset_restores_fontset_in_memory(self) -> None:
        from emulator.constants import FONT_START, FONTSET
        machine = create_machine()
        machine.memory.write_byte(FONT_START, FONTSET[0] ^ 0xFF)
        machine.reset()
        for offset, byte in enumerate(FONTSET):
            with self.subTest(offset=offset):
                self.assertEqual( machine.memory.read_byte(FONT_START + offset), byte)

    def test_reset_clears_stack(self) -> None:
        machine = create_machine()
        machine.stack.push(0x234)
        machine.reset()
        self.assertEqual(machine.stack.size(), 0)

    def test_reset_clears_timers(self) -> None:
        machine = create_machine()
        machine.timers.delay_timer = 42
        machine.timers.sound_timer = 17
        machine.reset()
        self.assertEqual(machine.timers.delay_timer, 0)
        self.assertEqual(machine.timers.sound_timer, 0)

    def test_load_rom_clears_user_flags(self) -> None:
        machine = create_machine()
        machine.user_flags[:] = bytes(range(len(machine.user_flags)))
        machine.load_rom(bytes([0x60, 0x01]))
        self.assertEqual( machine.user_flags, bytearray(len(machine.user_flags)))

    def test_load_rom_clears_previous_rom_contents(self) -> None:
        machine = create_machine()
        machine.load_rom(bytes([0x60, 0x01, 0x61, 0x02]))
        machine.load_rom(bytes([0x60, 0x03]))
        self.assertEqual(machine.memory.read_byte(0x200), 0x60)
        self.assertEqual(machine.memory.read_byte(0x201), 0x03)
        self.assertEqual(machine.memory.read_byte(0x202), 0x00)
        self.assertEqual(machine.memory.read_byte(0x203), 0x00)

    def test_execute_cycle_increments_cycle_counter_once(self) -> None:
        machine = create_machine()
        write_opcode(machine, 0x6001)
        machine.memory.write_byte(0x202, 0x61)
        machine.memory.write_byte(0x203, 0x02)
        self.assertEqual(machine.cycle_counter(), 0)
        machine.execute_cycle()
        self.assertEqual(machine.cycle_counter(), 1)
        machine.execute_cycle()
        self.assertEqual(machine.cycle_counter(), 2)

    def test_fetch_instruction_advances_program_counter_by_two(self) -> None:
        machine = create_machine()
        write_opcode(machine, 0x6A05)
        initial_pc = machine.registers.pc
        instruction = machine.fetch_instruction()
        self.assertEqual(instruction.opcode, 0x6A05)
        self.assertEqual(instruction.address, initial_pc)
        self.assertEqual(machine.registers.pc, initial_pc + 2)

    def test_fetch_instruction_advances_program_counter_before_decode_error(self) -> None:
        machine = create_machine()
        write_opcode(machine, 0xFFFF)
        initial_pc = machine.registers.pc
        with unittest.mock.patch.object( machine.isa, "decode", side_effect=ValueError("invalid opcode")):
            with self.assertRaisesRegex(ValueError, "invalid opcode"):
                machine.fetch_instruction()
        self.assertEqual(machine.registers.pc, initial_pc + 2)

    def test_peek_instruction_does_not_advance_program_counter_on_decode_error(self) -> None:
        machine = create_machine()
        write_opcode(machine, 0xFFFF)
        initial_pc = machine.registers.pc
        with unittest.mock.patch.object( machine.isa, "decode", side_effect=ValueError("invalid opcode")):
            with self.assertRaisesRegex(ValueError, "invalid opcode"):
                machine.peek_instruction()
        self.assertEqual(machine.registers.pc, initial_pc)

    def test_execute_cycle_does_not_trace_or_count_unexpected_exception(self) -> None:
        machine = create_machine()
        write_opcode(machine, 0x6001)
        with unittest.mock.patch.object(
            machine.isa,
            "execute",
            side_effect=RuntimeError("execution failed")
        ), unittest.mock.patch.object(machine._trace_reporter, "trace") as trace:
            with self.assertRaisesRegex(RuntimeError, "execution failed"):
                machine.execute_cycle()
        self.assertEqual(machine.cycle_counter(), 0)
        trace.assert_not_called()

    def test_execute_cycle_traces_consecutive_cycle_numbers(self) -> None:
        machine = create_machine()
        write_opcode(machine, 0x6001)
        machine.memory.write_byte(0x202, 0x61)
        machine.memory.write_byte(0x203, 0x02)
        with unittest.mock.patch.object(machine._trace_reporter, "trace") as trace:
            machine.execute_cycle()
            machine.execute_cycle()
        self.assertEqual(trace.call_count, 2)
        self.assertEqual(trace.call_args_list[0].args[0].cycle, 0)
        self.assertEqual(trace.call_args_list[1].args[0].cycle, 1)
        self.assertEqual(machine.cycle_counter(), 2)

    def test_execute_cycle_marks_machine_terminated(self) -> None:
        machine = create_machine()
        write_opcode(machine, 0x6001)
        with unittest.mock.patch.object(
            machine.isa,
            "execute",
            return_value=StepResult(terminated=True)
        ), unittest.mock.patch.object(machine._trace_reporter, "trace") as trace:
            result = machine.execute_cycle()
        self.assertTrue(result.terminated)
        self.assertTrue(machine.execute_cycle().terminated)
        self.assertEqual(machine.cycle_counter(), 1)
        trace.assert_called_once()

    def test_execute_cycle_traces_timer_snapshot_before_instruction(self) -> None:
        machine = create_machine()
        machine.timers.delay_timer = 5
        machine.timers.sound_timer = 7
        machine.registers[0] = 3
        write_opcode(machine, 0xF015)
        with unittest.mock.patch.object(machine._trace_reporter, "trace") as trace:
            machine.execute_cycle()
        record = trace.call_args.args[0]
        self.assertEqual(record.delay_timer_before, 5)
        self.assertEqual(record.delay_timer_after, 3)
        self.assertEqual(record.sound_timer_before, 7)
        self.assertEqual(record.sound_timer_after, 7)

    def test_execute_cycle_traces_independent_register_snapshots(self) -> None:
        machine = create_machine()
        write_opcode(machine, 0x6001)
        with unittest.mock.patch.object(machine._trace_reporter, "trace") as trace:
            machine.execute_cycle()
        record = trace.call_args.args[0]
        self.assertEqual(record.registers_before[0], 0)
        self.assertEqual(record.registers_after[0], 1)
        machine.registers[0] = 0xFF
        self.assertEqual(record.registers_before[0], 0)
        self.assertEqual(record.registers_after[0], 1)

    def test_execute_cycle_traces_memory_range(self) -> None:
        machine = create_machine()
        with unittest.mock.patch.object(
            machine.isa,
            "execute",
            return_value=StepResult(memory_range=(0x300, 0x30F))
        ), unittest.mock.patch.object(machine._trace_reporter, "trace") as trace:
            machine.execute_cycle()
        trace.assert_called_once()
        record = trace.call_args.args[0]
        self.assertEqual(record.memory_range, (0x300, 0x30F))

    def test_execute_cycle_traces_display_changed_flag(self) -> None:
        machine = create_machine()
        write_opcode(machine, 0x6001)
        with unittest.mock.patch.object(
            machine.isa,
            "execute",
            return_value=StepResult(display_changed=True)
        ), unittest.mock.patch.object(machine._trace_reporter, "trace") as trace:
            machine.execute_cycle()
        trace.assert_called_once()
        record = trace.call_args.args[0]
        self.assertTrue(record.display_changed)

    def test_execute_cycle_traces_sound_timer_change(self) -> None:
        machine = create_machine()
        machine.timers.sound_timer = 4
        machine.registers[0] = 9
        write_opcode(machine, 0xF018)
        with unittest.mock.patch.object(machine._trace_reporter, "trace") as trace:
            machine.execute_cycle()
        trace.assert_called_once()
        record = trace.call_args.args[0]
        self.assertEqual(record.sound_timer_before, 4)
        self.assertEqual(record.sound_timer_after, 9)
        self.assertEqual(record.delay_timer_before, 0)
        self.assertEqual(record.delay_timer_after, 0)

    def test_execute_cycle_traces_instruction_at_non_default_address(self) -> None:
        machine = create_machine()
        machine.registers.pc = 0x300
        machine.memory.write_byte(0x300, 0x6A)
        machine.memory.write_byte(0x301, 0x05)
        with unittest.mock.patch.object(machine._trace_reporter, "trace") as trace:
            machine.execute_cycle()
        trace.assert_called_once()
        record = trace.call_args.args[0]
        self.assertEqual(record.instruction.address, 0x300)
        self.assertEqual(record.instruction.opcode, 0x6A05)
        self.assertEqual(machine.registers.pc, 0x302)

    def test_set_isa_changes_instruction_execution(self) -> None:
        machine = create_machine()
        machine.set_isa(SuperChip10InstructionSetArchitecture())
        write_opcode(machine, 0x00FD)
        result = machine.execute_cycle()
        self.assertTrue(result.terminated)
        self.assertEqual(machine.cycle_counter(), 1)

    def test_reset_initializes_configured_isa(self) -> None:
        machine = create_machine()
        with unittest.mock.patch.object(
            machine.isa,
            "initialize_machine"
        ) as initialize_machine:
            machine.reset()
        initialize_machine.assert_called_once_with(machine)

    def test_reset_without_configured_isa(self) -> None:
        log_manager = LogManager()
        diagnostics = Diagnostics()
        machine = Chip8Machine(
            diagnostics.reporter(DiagnosticSource.UNIT_TEST),
            log_manager.application_logger(DiagnosticSource.UNIT_TEST),
            log_manager.execution_trace_reporter()
        )
        machine.registers.pc = 0x300
        machine.reset()
        self.assertEqual(machine.registers.pc, PROGRAM_START)
        self.assertEqual(machine.cycle_counter(), 0)

    def test_load_rom_resets_index_register(self) -> None:
        machine = create_machine()
        machine.registers.i = 0x345
        machine.load_rom(bytes([0x60, 0x01]))
        self.assertEqual(machine.registers.i, 0)

    def test_load_rom_resets_keyboard_state(self) -> None:
        machine = create_machine()
        machine.keyboard.press(5)
        self.assertTrue(machine.keyboard.is_pressed(5))
        machine.load_rom(bytes([0x60, 0x01]))
        self.assertFalse(machine.keyboard.is_pressed(5))

    def test_load_rom_resets_stack_pointer(self) -> None:
        machine = create_machine()
        machine.stack.push(0x234)
        machine.load_rom(bytes([0x60, 0x01]))
        self.assertEqual(machine.registers.sp, 0)

    def test_load_empty_rom_sets_program_counter(self) -> None:
        machine = create_machine()
        machine.registers.pc = 0x300
        machine.load_rom(b"")
        self.assertEqual(machine.registers.pc, PROGRAM_START)
        self.assertEqual(machine.cycle_counter(), 0)

    def test_load_rom_allows_execution_after_termination(self) -> None:
        machine = create_machine()
        machine.set_isa(SuperChip10InstructionSetArchitecture())
        write_opcode(machine, 0x00FD)
        result = machine.execute_cycle()
        self.assertTrue(result.terminated)
        machine.load_rom(bytes([0x60, 0x01]))
        result = machine.execute_cycle()
        self.assertFalse(result.terminated)
        self.assertEqual(machine.registers[0], 1)
        self.assertEqual(machine.cycle_counter(), 1)

    def test_load_rom_clears_framebuffer(self) -> None:
        machine = create_machine()
        machine.framebuffer.set_pixel(1, 1, True)
        machine.load_rom(bytes([0x60, 0x01]))
        self.assertFalse(machine.framebuffer.get_pixel(1, 1))

    def test_load_rom_clears_previous_display_resolution(self) -> None:
        machine = create_machine()
        machine.set_isa(SuperChip10InstructionSetArchitecture())
        write_opcode(machine, 0x00FF)
        machine.execute_cycle()
        machine.load_rom(bytes([0x60, 0x01]))
        self.assertEqual(machine.framebuffer.width, 64)
        self.assertEqual(machine.framebuffer.height, 32)

    def test_load_rom_rejects_oversized_rom(self) -> None:
        machine = create_machine()
        rom = bytes(machine.memory.size() - PROGRAM_START + 1)
        with self.assertRaises(ValueError):
            machine.load_rom(rom)

    def test_load_rom_accepts_rom_filling_available_memory(self) -> None:
        machine = create_machine()
        rom_size = machine.memory.size() - PROGRAM_START
        rom = bytes(rom_size)
        machine.load_rom(rom)
        self.assertEqual(machine.registers.pc, PROGRAM_START)
        self.assertEqual( machine.memory.read_byte(machine.memory.size() - 1), 0)

    def test_load_rom_overwrites_entire_previous_rom(self) -> None:
        machine = create_machine()
        machine.load_rom(bytes([0x60, 0x01, 0x61, 0x02]))
        machine.load_rom(bytes([0x62, 0x03, 0x63, 0x04]))
        self.assertEqual(machine.memory.read_byte(PROGRAM_START), 0x62)
        self.assertEqual(machine.memory.read_byte(PROGRAM_START + 1), 0x03)
        self.assertEqual(machine.memory.read_byte(PROGRAM_START + 2), 0x63)
        self.assertEqual(machine.memory.read_byte(PROGRAM_START + 3), 0x04)

    def test_load_rom_resets_delay_and_sound_timers(self) -> None:
        machine = create_machine()
        machine.load_rom(bytes([0x60, 0x05, 0x61, 0x07]))
        write_opcode(machine, 0xF015)
        machine.execute_cycle()
        write_opcode(machine, 0xF018)
        machine.execute_cycle()
        machine.load_rom(bytes([0x62, 0x02]))
        self.assertEqual(machine.timers.delay_timer, 0)
        self.assertEqual(machine.timers.sound_timer, 0)

    def test_load_rom_does_not_execute_first_instruction(self) -> None:
        machine = create_machine()
        machine.load_rom(bytes([0x60, 0x01]))
        self.assertEqual(machine.registers[0], 0)
        self.assertEqual(machine.registers.pc, PROGRAM_START)
        self.assertEqual(machine.cycle_counter(), 0)
        self.assertEqual(machine.memory.read_byte(PROGRAM_START), 0x60)
        self.assertEqual(machine.memory.read_byte(PROGRAM_START + 1), 0x01)

    def test_load_rom_positions_program_counter_before_first_instruction(self) -> None:
        machine = create_machine()
        machine.load_rom(bytes([0x60, 0x01]))
        self.assertEqual(machine.registers.pc, PROGRAM_START)
        self.assertEqual(machine.cycle_counter(), 0)

    def test_execute_cycle_advances_program_counter_by_two(self) -> None:
        machine = create_machine()
        machine.load_rom(bytes([0x60, 0x01]))
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, PROGRAM_START + 2)
        self.assertEqual(machine.cycle_counter(), 1)

    def test_execute_cycle_executes_only_one_instruction(self) -> None:
        machine = create_machine()
        machine.load_rom(bytes([0x60, 0x01, 0x61, 0x02]))
        machine.execute_cycle()
        self.assertEqual(machine.registers[0], 1)
        self.assertEqual(machine.registers[1], 0)
        self.assertEqual(machine.registers.pc, PROGRAM_START + 2)
        self.assertEqual(machine.cycle_counter(), 1)
        machine.execute_cycle()
        self.assertEqual(machine.registers[0], 1)
        self.assertEqual(machine.registers[1], 2)
        self.assertEqual(machine.registers.pc, PROGRAM_START + 4)
        self.assertEqual(machine.cycle_counter(), 2)


    def test_isa_raises_when_not_configured(self) -> None:
        machine = create_machine()
        with patch.object(machine, "_isa", None):
            with self.assertRaisesRegex(
                RuntimeError,
                "Instruction set architecture has not been configured\\."
            ):
                _ = machine.isa


if __name__ == "__main__":
    unittest.main(verbosity=2)

