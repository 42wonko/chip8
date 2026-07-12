"""
@file emulatorconfiguration.py

@brief Emulator runtime configuration.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class EmulatorConfiguration:
    """
    @brief Emulator runtime configuration.
    """

    sound_enabled: bool = True
    sound_volume: int = 100
    disable_display_updates: bool = False
    enable_debugging: bool = False
    enable_debug_trace: bool = False
    enable_chip8_program_trace: bool = False

