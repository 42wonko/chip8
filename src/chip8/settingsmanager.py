"""
###############################################################################
# CHIP-8 Emulator
#
# Settings manager
###############################################################################
"""

from __future__ import annotations

from PyQt6.QtCore import QSettings

from controller.emulatorconfiguration import EmulatorConfiguration


class SettingsManager:
    """
    @brief Persistent application settings.

    @details
    Encapsulates access to QSettings.

    The manager itself does not know individual configuration values.
    Reading and writing of configuration members is delegated to
    EmulatorConfiguration.
    """

    ORGANIZATION = "emulators"
    APPLICATION = "CHIP8"

    def __init__(self) -> None:
        """
        @brief Construct the settings manager.
        """
        self._settings = QSettings( self.ORGANIZATION, self.APPLICATION)


    def load_configuration( self, configuration: EmulatorConfiguration) -> None:
        """
        @brief Load emulator configuration.

        @param configuration
            Configuration object to populate.
        """
        configuration.read_settings(self._settings)


    def save_configuration( self, configuration: EmulatorConfiguration) -> None:
        """
        @brief Save emulator configuration.

        @param configuration
            Configuration object to save.
        """
        configuration.write_settings(self._settings)


    def settings(self) -> QSettings:
        """
        @brief Return the underlying QSettings object.

        @return
            Persistent application settings.
        """
        return self._settings

