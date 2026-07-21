"""
@file configdialog.py

@brief Application configuration dialog.
"""

from __future__ import annotations

from pathlib import Path
from typing import cast

from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox, QWidget
from PyQt6.QtCore import pyqtSignal

from controller.emulatorconfiguration import EmulatorConfiguration, TraceLevel


def trace_level_to_index(level: TraceLevel) -> int:
    """
    @brief Convert a TraceLevel to a combo box index.
    """
    return {
        TraceLevel.BASIC: 0,
        TraceLevel.CHANGES: 1,
        TraceLevel.FULL: 2,
    }[level]


def index_to_trace_level(index: int) -> TraceLevel:
    """
    @brief Convert a combo box index to a TraceLevel.
    """
    return (
        TraceLevel.BASIC,
        TraceLevel.CHANGES,
        TraceLevel.FULL,
    )[index]


class ConfigDialog(QDialog):
    """
    @brief Application configuration dialog.
    """

    testSoundRequested = pyqtSignal(EmulatorConfiguration)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        ui_file = ( Path(__file__).resolve().parent / "ui" / "configdialog.ui")
        uic.loadUi(ui_file, self)
        self.soundVolumeSlider.valueChanged.connect(self._update_volume_label)
        self._update_volume_label( self.soundVolumeSlider.value())
        self.browseLogFilePushButton.clicked.connect(self._browse_log_file)
        self.browseTraceFilePushButton.clicked.connect(self._browse_trace_file)
        self.playTestSoundPushButton.clicked.connect(self._test_sound)


    @property
    def sound_enabled(self) -> bool:
        """
        @brief Return whether sound is enabled.
        """
        return cast(bool, self.enableAudioGroupBox.isChecked())


    @sound_enabled.setter
    def sound_enabled(self, enabled: bool) -> None:
        self.enableAudioGroupBox.setChecked(enabled)


    @property
    def sound_volume(self) -> int:
        """
        @brief Return the sound volume in percent.
        """
        return cast(int, self.soundVolumeSlider.value())


    @sound_volume.setter
    def sound_volume(self, volume: int) -> None:
        self.soundVolumeSlider.setValue(volume)


    @property
    def configuration(self) -> EmulatorConfiguration:
        """
        @brief Return the current dialog settings.
        """
        return EmulatorConfiguration(
            sound_enabled=self.enableAudioGroupBox.isChecked(),
            sound_volume=self.soundVolumeSlider.value(),
            audio_output_device=self.audioDeviceComboBox.currentText(),
            available_audio_devices=[ self.audioDeviceComboBox.itemText(i) for i in range(self.audioDeviceComboBox.count()) ],
            disable_display_updates=self.disableDisplayUpdatesCheckBox.isChecked(),

            logging_enabled=self.applicationLoggingGroupBox.isChecked(),
            logging_enabled_info=self.logInformationCheckBox.isChecked(),
            logging_enabled_warning=self.logWarningsCheckBox.isChecked(),
            logging_enabled_error=self.logErrorsCheckBox.isChecked(),
            log_filename=self.logFilenameLineEdit.text(),
            function_trace_enabled=self.enableFunctionTraceCheckBox.isChecked(),
            execution_trace_enabled=self.executionTraceGroupBox.isChecked(),
            trace_filename=self.traceFilenameLineEdit.text(),
            trace_level=index_to_trace_level(self.traceLevelComboBox.currentIndex())
        )


    @configuration.setter
    def configuration( self, configuration: EmulatorConfiguration) -> None:
        """
        @brief Initialize the dialog.
        """
        self.enableAudioGroupBox.setChecked( configuration.sound_enabled)
        self.soundVolumeSlider.setValue( configuration.sound_volume)
        self.audioDeviceComboBox.clear()
        self.audioDeviceComboBox.addItems(configuration.available_audio_devices)
        index = self.audioDeviceComboBox.findText( configuration.audio_output_device)
        if index >= 0:
            self.audioDeviceComboBox.setCurrentIndex(index)

        self.disableDisplayUpdatesCheckBox.setChecked( configuration.disable_display_updates)
        self.applicationLoggingGroupBox.setChecked(configuration.logging_enabled)
        self.logInformationCheckBox.setChecked(configuration.logging_enabled_info)
        self.logWarningsCheckBox.setChecked(configuration.logging_enabled_warning)
        self.logErrorsCheckBox.setChecked(configuration.logging_enabled_error)
        self.logFilenameLineEdit.setText(configuration.log_filename)
        self.enableFunctionTraceCheckBox.setChecked(configuration.function_trace_enabled)
        self.executionTraceGroupBox.setChecked(configuration.execution_trace_enabled)
        self.traceFilenameLineEdit.setText(configuration.trace_filename)
        self.traceLevelComboBox.setCurrentIndex( trace_level_to_index(configuration.trace_level))


    def _test_sound(self) -> None:
        """
        @brief Request a sound test through the controller.
        """
        self.testSoundRequested.emit(self.configuration)


    def _update_volume_label(self, value: int) -> None:
        """
        @brief Update the volume label.
        """
        self.soundVolumeLabel.setText(f"{value} %")


    def _browse_log_file(self) -> None:
        """
        @brief Select the application log file.
        """
        dialog = QFileDialog(self)

        dialog.setWindowTitle("Application Log File")
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setNameFilter("Log files (*.log);;All files (*)")
        dialog.setOption(QFileDialog.Option.DontConfirmOverwrite, True)

        if self.logFilenameLineEdit.text():
            dialog.selectFile(self.logFilenameLineEdit.text())

        if dialog.exec():
            filenames = dialog.selectedFiles()
            if filenames:
                self.logFilenameLineEdit.setText(filenames[0])


    def _browse_trace_file(self) -> None:
        """
        @brief Select the execution trace file.
        """
        dialog = QFileDialog(self)

        dialog.setWindowTitle("Execution Trace File")
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setNameFilter("Trace files (*.trace);;Text files (*.txt);;All files (*)")
        dialog.setOption(QFileDialog.Option.DontConfirmOverwrite, True)

        if self.traceFilenameLineEdit.text():
            dialog.selectFile(self.traceFilenameLineEdit.text())

        if dialog.exec():
            filenames = dialog.selectedFiles()
            if filenames:
                self.traceFilenameLineEdit.setText(filenames[0])


    def accept(self) -> None:
        """
        @brief Validate the configuration before closing the dialog.
        """

        #
        # Application logging
        #

        if self.applicationLoggingGroupBox.isChecked():
            filename = self.logFilenameLineEdit.text().strip()
            if not filename:
                QMessageBox.warning( self, "Logging", "Application logging is enabled, but no log filename has been specified.")
                return
            parent = Path(filename).parent

            if not parent.exists():
                QMessageBox.warning( self, "Logging", "The directory for the log file does not exist.")
                return

        #
        # Execution trace
        #

        if self.executionTraceGroupBox.isChecked():
            filename = self.traceFilenameLineEdit.text().strip()
            if not filename:
                QMessageBox.warning( self, "Execution Trace", "Execution tracing is enabled, but no trace filename has been specified.")
                return
            parent = Path(filename).parent
            if not parent.exists():
                QMessageBox.warning( self, "Execution Trace", "The directory for the trace file does not exist.")
                return
        super().accept()
