"""
@file chip8machine.py

@brief CHIP-8 virtual machine.

@details
Owns all hardware components of the CHIP-8 virtual machine.

The machine provides a single point of access to the virtual hardware.
Instruction execution will be added in a later milestone.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

from chip8.isa.instruction import Instruction
from chip8.isa.instructionid import InstructionId
from chip8.isa.isa import InstructionSetArchitecture
from controller.applicationlogreporter import ApplicationLogReporter
from controller.diagnostics import DiagnosticReporter
from controller.executiontracereporter import ExecutionTraceReporter
from emulator.chip8framebuffer import Chip8Framebuffer
from emulator.chip8keyboard import Chip8Keyboard
from emulator.chip8memory import Chip8Memory
from emulator.chip8registers import Chip8Registers
from emulator.chip8stack import Chip8Stack
from emulator.chip8timers import Chip8Timers
from emulator.constants import FONT_START, FONTSET, PROGRAM_START
from emulator.stepresult import StepResult
from emulator.tracerecord import TraceRecord


class Chip8Machine:
    """
    @brief CHIP-8 virtual machine.
    """
    def __init__(self, diagnostics: DiagnosticReporter, logger: ApplicationLogReporter, tracer: ExecutionTraceReporter) -> None:

        """
        @brief Construct the virtual machine.
        @detai All members are private to prevent other classes from accidentally
        replacing any of the hardware components. By decorating them with @property
        we can still use them, though.
        """
        self._diagnostics           = diagnostics           # only needed to create the reporters for the subsystems
        self._logger                = logger                # only needed to create the reporters for the subsystems
        self._trace_reporter        = tracer
        self._cycles                = 0
        self._memory                = Chip8Memory(self._diagnostics, self._logger)
        self._registers             = Chip8Registers(self._diagnostics, self._logger)
        self._stack                 = Chip8Stack(self._diagnostics, self._logger, self._registers)
        self._timers                = Chip8Timers(self._diagnostics, self._logger)
        self._keyboard              = Chip8Keyboard(self._diagnostics, self._logger, self._trace_reporter, cycle_provider=self.cycle_counter)
        self._framebuffer           = Chip8Framebuffer(self._diagnostics, self._logger)
        self._isa: InstructionSetArchitecture | None = None
        self.reset()

    ###########################################################################
    # Hardware access
    ###########################################################################
    @property
    def memory(self) -> Chip8Memory:
        """
        @brief Return the main memory.
        """
        return self._memory


    @property
    def registers(self) -> Chip8Registers:
        """
        @brief Return the CPU registers.
        """
        return self._registers


    @property
    def stack(self) -> Chip8Stack:
        """
        @brief Return the call stack.
        """
        return self._stack


    @property
    def timers(self) -> Chip8Timers:
        """
        @brief Return the timer registers.
        """
        return self._timers


    @property
    def keyboard(self) -> Chip8Keyboard:
        """
        @brief Return the hexadecimal keypad.
        """
        return self._keyboard


    @property
    def framebuffer(self) -> Chip8Framebuffer:
        """
        @brief Return the framebuffer.
        """
        return self._framebuffer


    def cycle_counter(self) -> int:
        """
        @brief returns the current cycle count. Needed for execution tracing in Keybord.
        """
        return self._cycles


    def set_isa(self, isa: InstructionSetArchitecture) -> None:
        """
        @brief Set the instruction set architecture.

        @param isa
            Instruction set architecture used to decode and execute instructions.
        """
        self._isa = isa


    @property
    def isa(self) -> InstructionSetArchitecture:
        """
        @brief Return the instruction set architecture.
        """
        if self._isa is None:
            raise RuntimeError("Instruction set architecture has not been configured.")
        return self._isa

    ###########################################################################
    # Machine control
    ###########################################################################
    def reset(self) -> None:
        """
        @brief Reset the complete virtual machine.
        """
        self._logger.info("Resetting virtual machine.")
        self._memory.reset()
        self._registers.reset()
        self._stack.reset()
        self._timers.reset()
        self._keyboard.reset()
        self._framebuffer.reset()
        for offset, byte in enumerate(FONTSET):                 # init the builtin font
            self._memory.write_byte(FONT_START + offset, byte)
        self._cycles = 0


    def load_rom(self, data: bytes) -> None:
        """
        @brief Load a ROM image.

        @param data
            ROM contents.
        """
        self._logger.info(f"Loading ROM ({len(data)} bytes) into memory.")
        self.reset()
        self._memory.load_rom(data)
        self._registers.pc = PROGRAM_START


    def tick_timers(self) -> None:
        """
        @brief Advance the hardware timers.
        """
        self._timers.tick()


    def fetch_instruction(self) -> Instruction:
        """
        @brief Fetch and decode the next instruction.
        """
        address = self._registers.pc
        msb = self._memory.read_byte(address)
        lsb = self._memory.read_byte(address + 1)
        opcode = (msb << 8) | lsb
        self._registers.pc += 2
        return self.isa.decode( address, opcode)


    def peek_instruction(self) -> Instruction:
        address = self._registers.pc
        msb = self._memory.read_byte(address)
        lsb = self._memory.read_byte(address + 1)
        opcode = (msb << 8) | lsb
        return self.isa.decode( address, opcode)

    def execute_cycle(self) -> StepResult:
        """
        @brief Execute one instruction.
        """
        result = StepResult()
        registers_before = self._registers.copy()
        delay_timer_before = self._timers.delay_timer
        sound_timer_before = self._timers.sound_timer

        instruction = self.fetch_instruction()

        try:
            result = self.isa.execute(instruction)
        except ValueError as error:
            raise NotImplementedError( f"Opcode {instruction.opcode:04X} is not implemented.") from error
        if instruction.id == InstructionId.JP_V0:
            result.bnnn_target = (instruction.address, self.registers.pc)

        registers_after = self._registers.copy()
        delay_timer_after = self._timers.delay_timer
        sound_timer_after = self._timers.sound_timer

        ptrace_rec = TraceRecord(
                cycle=self._cycles,
                instruction=instruction,

                registers_before=registers_before,
                registers_after=registers_after,

                delay_timer_before=delay_timer_before,
                delay_timer_after=delay_timer_after,

                sound_timer_before=sound_timer_before,
                sound_timer_after=sound_timer_after,

                memory_range=result.memory_range,
                display_changed=result.display_changed
                )
        self._trace_reporter.trace(ptrace_rec)
        self._cycles += 1
        return result

