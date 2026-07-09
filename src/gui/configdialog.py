"""
@file configdialog.py

@brief Application configuration dialog.
"""

from __future__ import annotations
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtWidgets import QDialog
from controller.emulatorconfiguration import EmulatorConfiguration


class ConfigDialog(QDialog):
    """
    @brief Application configuration dialog.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        ui_file = ( Path(__file__).resolve().parent / "ui" / "configdialog.ui")
        uic.loadUi(ui_file, self)
        self.soundVolumeSlider.valueChanged.connect(self._update_volume_label)
        self._update_volume_label( self.soundVolumeSlider.value())


    @property
    def sound_enabled(self) -> bool:
        """
        @brief Return whether sound is enabled.
        """
        return self.enableSoundCheckBox.isChecked()


    @sound_enabled.setter
    def sound_enabled(self, enabled: bool) -> None:
        self.enableSoundCheckBox.setChecked(enabled)


    @property
    def sound_volume(self) -> int:
        """
        @brief Return the sound volume in percent.
        """
        return self.soundVolumeSlider.value()


    @sound_volume.setter
    def sound_volume(self, volume: int) -> None:
        self.soundVolumeSlider.setValue(volume)


    @property
    def configuration(self) -> EmulatorConfiguration:
        """
        @brief Return the current dialog settings.
        """
        return EmulatorConfiguration(
            sound_enabled=self.enableSoundCheckBox.isChecked(),
            sound_volume=self.soundVolumeSlider.value(),
            runtime_trace=self.rtTraceCheckBox.isChecked(),
        )


    @configuration.setter
    def configuration( self, configuration: EmulatorConfiguration) -> None:
        """
        @brief Initialize the dialog.
        """
        self.enableSoundCheckBox.setChecked(configuration.sound_enabled)
        self.soundVolumeSlider.setValue(configuration.sound_volume)
        self.rtTraceCheckBox.setChecked(configuration.runtime_trace)

    def _update_volume_label(self, value: int) -> None:
        """
        @brief Update the volume label.
        """
        self.soundVolumeLabel.setText(f"{value} %")
