"""
@file stepresult.py

@brief Result object returned after executing a single CHIP-8 instruction.

@details
This module defines the @ref StepResult data class, which communicates
which parts of the machine state changed during the execution of a single
instruction.

The controller uses this information to update only those GUI components
that are affected by the executed instruction, avoiding unnecessary
refreshes while keeping the debugger view synchronized with the emulator.

The class intentionally contains only change information. The actual
machine state remains stored inside the emulator and is queried directly
by the controller when updating the user interface.

@author
Michael Dlubatz

@copyright
MIT License
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class StepResult:
    """
    @brief Result of executing a single CHIP-8 instruction.

    @details
    The result describes which parts of the emulator state changed during
    instruction execution so the controller can efficiently update the GUI.
    """

    display_changed: bool = False
    memory_range: tuple[int, int] | None = None
