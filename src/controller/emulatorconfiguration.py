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
    realtime_updates: bool = True
    runtime_trace: bool = False
