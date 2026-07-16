from __future__ import annotations

from dataclasses import dataclass

from emulator.instruction import Instruction


@dataclass(slots=True, frozen = True)
class TraceRecord:
    """
    @brief Describes one executed instruction.

    The CHIP-8 machine constructs a TraceRecord before and
    immediately after executing an instruction. Formatting
    is performed by the ExecutionTraceReporter.
    """
    pc_before: int
    pc_after: int
    instruction: Instruction

