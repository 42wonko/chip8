"""
@file emulatorconfiguration.py

@brief Emulator runtime configuration.
"""
from __future__ import annotations
from PyQt6.QtCore import QSettings          # TBD: think about this. Do I want Qt depedencies here?
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

    def read_settings(self, settings: QSettings) -> None:
        """
        @brief Read the emulator configuration from persistent storage.

        @param settings
            QSettings instance.
        """
        self.sound_enabled = settings.value( "audio/sound_enabled", self.sound_enabled, bool)
        self.sound_volume = settings.value( "audio/volume", self.sound_volume, int)
        self.beeper_frequency = settings.value( "audio/frequency", self.beeper_frequency, int)
        self.audio_output_device = settings.value( "audio/output_device", self.audio_output_device, str)
        self.logging_enabled = settings.value( "logging/enabled", self.logging_enabled, bool)
        self.logging_enabled_info = settings.value( "logging/info", self.logging_enabled_info, bool)
        self.logging_enabled_warning = settings.value( "logging/warning", self.logging_enabled_warning, bool)
        self.disable_display_updates = settings.value( "display/disable_updates", self.disable_display_updates, bool)

    def write_settings(self, settings: QSettings) -> None:
        """
        @brief Write the emulator configuration to persistent storage.

        @param settings
            QSettings instance.
        """
        settings.setValue( "audio/sound_enabled", self.sound_enabled)
        settings.setValue( "audio/volume", self.sound_volume)
        settings.setValue( "audio/frequency", self.beeper_frequency)
        settings.setValue( "audio/output_device", self.audio_output_device)
        settings.setValue( "logging/enabled", self.logging_enabled)
        settings.setValue( "logging/info", self.logging_enabled_info)
        settings.setValue( "logging/warning", self.logging_enabled_warning)
        settings.setValue( "display/disable_updates", self.disable_display_updates)
        settings.sync()
