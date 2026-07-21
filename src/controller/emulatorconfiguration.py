"""
@file emulatorconfiguration.py

@brief Emulator runtime configuration.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, auto  # we need the IntEnum for comparisons
from emulator.constants import DEFAULT_BEEPER_FREQUENCY


class TraceLevel(IntEnum):
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
    sound_enabled: bool                 = True
    sound_volume: int                   = 100
    beeper_frequency: int               = DEFAULT_BEEPER_FREQUENCY
    audio_output_device: str            = "default"
    available_audio_devices: list[str]  = field(default_factory=list)

    ###########################################################################
    # Display
    ###########################################################################
    disable_display_updates: bool       = False

    ###########################################################################
    # Application Logging
    ###########################################################################
    logging_enabled: bool               = False
    logging_enabled_info: bool          = False
    logging_enabled_warning: bool       = False
    logging_enabled_error: bool         = False
    log_filename: str                   = ""
    function_trace_enabled: bool        = False

    ###########################################################################
    # CHIP-8 Execution Trace
    ###########################################################################
    execution_trace_enabled: bool       = False
    trace_filename: str                 = ""
    trace_level: TraceLevel             = TraceLevel.BASIC
