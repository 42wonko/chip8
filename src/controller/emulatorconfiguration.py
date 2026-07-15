"""
@file emulatorconfiguration.py

@brief Emulator runtime configuration.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto


class TraceLevel(Enum):
    """
    @brief Amount of information written to the CHIP-8 execution trace.
    """
    BASIC   = auto()
    CHANGES = auto()
    FULL    = auto()


@dataclass(slots=True)
class EmulatorConfiguration:
    """
    @brief Emulator runtime configuration.
    """
    ###########################################################################
    # Audio
    ###########################################################################
    sound_enabled: bool             = True
    sound_volume: int               = 100

    ###########################################################################
    # Display
    ###########################################################################
    disable_display_updates: bool   = False

    ###########################################################################
    # Application Logging
    ###########################################################################
    logging_enabled: bool           = False
    log_filename: str               = ""
    function_trace_enabled: bool    = False

    ###########################################################################
    # CHIP-8 Execution Trace
    ###########################################################################
    execution_trace_enabled: bool   = False
    trace_filename: str             = ""
    trace_level: TraceLevel         = TraceLevel.BASIC
