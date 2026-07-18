from __future__ import annotations

from dataclasses import dataclass

from emulator.chip8registers import Chip8Registers
from emulator.instruction import Instruction


@dataclass(slots=True, frozen = True)
class TraceRecord:
    """
    @brief Describes one executed instruction.

    The CHIP-8 machine constructs a TraceRecord before and
    immediately after executing an instruction. Formatting
    is performed by the ExecutionTraceReporter.
    """

    cycle: int
    instruction: Instruction

    registers_before: Chip8Registers
    registers_after: Chip8Registers

    delay_timer_before: int
    delay_timer_after: int

    sound_timer_before: int
    sound_timer_after: int

    memory_range: tuple[int, int] | None = None

    display_changed: bool = False
