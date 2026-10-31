
"""
@file test_configdialog.py

@brief Tests for the application configuration dialog.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PyQt6.QtWidgets import QApplication, QDialog

from controller.emulatorconfiguration import (
    EmulationMode,
    EmulatorConfiguration,
    TraceLevel,
)
from gui.configdialog import (
    ConfigDialog,
    index_to_trace_level,
    trace_level_to_index,
)


class TestConfigDialog(unittest.TestCase):
    """Tests for ConfigDialog."""

    @classmethod
    def setUpClass(cls) -> None:
        """Create the Qt application required by the dialog tests."""
        cls._application = QApplication.instance()
        if cls._application is None:
            cls._application = QApplication([])

    def setUp(self) -> None:
        self.dialog = ConfigDialog()

    def test_initialization_updates_audio_labels(self) -> None:
        """The labels should reflect the initial slider values."""
        self.assertEqual( self.dialog.soundVolumeLabel.text(), f"{self.dialog.soundVolumeSlider.value()} %")
        self.assertEqual( self.dialog.soundFrequencyLabel.text(), f"{self.dialog.soundFrequencySlider.value()} Hz")

    def test_sound_enabled_property(self) -> None:
        """The sound-enabled property should access the audio group box."""
        self.dialog.sound_enabled = False
        self.assertFalse(self.dialog.sound_enabled)
        self.dialog.sound_enabled = True
        self.assertTrue(self.dialog.sound_enabled)

    def test_sound_volume_property(self) -> None:
        """The sound-volume property should access the volume slider."""
        self.dialog.sound_volume = 65
        self.assertEqual(self.dialog.sound_volume, 65)
        self.assertEqual(self.dialog.soundVolumeLabel.text(), "65 %")

    def test_sound_frequency_property(self) -> None:
        """The sound-frequency property should access the frequency slider."""
        self.dialog.sound_frequency = 880
        self.assertEqual(self.dialog.sound_frequency, 880)
        self.assertEqual(self.dialog.soundFrequencyLabel.text(), "880 Hz")

    def test_volume_slider_updates_label(self) -> None:
        """Changing the volume slider should update its label."""
        self.dialog.soundVolumeSlider.setValue(40)
        self.assertEqual(self.dialog.soundVolumeLabel.text(), "40 %")

    def test_frequency_slider_updates_label(self) -> None:
        """Changing the frequency slider should update its label."""
        self.dialog.soundFrequencySlider.setValue(1000)
        self.assertEqual(self.dialog.soundFrequencyLabel.text(), "1000 Hz")

    def test_test_sound_emits_current_configuration(self) -> None:
        """The test-sound button should emit the current configuration."""
        emitted: list[EmulatorConfiguration] = []
        self.dialog.test_sound_requested.connect(emitted.append)
        self.dialog.sound_volume = 35
        self.dialog.sound_frequency = 900
        self.dialog.playTestSoundPushButton.click()
        self.assertEqual(len(emitted), 1)
        self.assertEqual(emitted[0].sound_volume, 35)
        self.assertEqual(emitted[0].beeper_frequency, 900)

    def test_configuration_getter(self) -> None:
        """The configuration property should collect all dialog settings."""
        self.dialog.sound_enabled = False
        self.dialog.sound_volume = 70
        self.dialog.sound_frequency = 1200
        self.dialog.audioDeviceComboBox.addItems(["Device A", "Device B"])
        self.dialog.audioDeviceComboBox.setCurrentText("Device B")
        self.dialog.super11RadioButton.setChecked(True)
        self.dialog.disableDisplayUpdatesCheckBox.setChecked(True)
        self.dialog.applicationLoggingGroupBox.setChecked(True)
        self.dialog.logInformationCheckBox.setChecked(False)
        self.dialog.logWarningsCheckBox.setChecked(True)
        self.dialog.logErrorsCheckBox.setChecked(False)
        self.dialog.logFilenameLineEdit.setText("application.log")
        self.dialog.enableFunctionTraceCheckBox.setChecked(True)
        self.dialog.executionTraceGroupBox.setChecked(True)
        self.dialog.traceFilenameLineEdit.setText("execution.trace")
        self.dialog.traceLevelComboBox.setCurrentIndex(2)
        configuration = self.dialog.configuration
        self.assertFalse(configuration.sound_enabled)
        self.assertEqual(configuration.sound_volume, 70)
        self.assertEqual(configuration.beeper_frequency, 1200)
        self.assertEqual(configuration.audio_output_device, "Device B")
        self.assertEqual( configuration.available_audio_devices, ["Device A", "Device B"])
        self.assertEqual( configuration.emulation_mode, EmulationMode.SUPERCHIP_11)
        self.assertTrue(configuration.disable_display_updates)
        self.assertTrue(configuration.logging_enabled)
        self.assertFalse(configuration.logging_enabled_info)
        self.assertTrue(configuration.logging_enabled_warning)
        self.assertFalse(configuration.logging_enabled_error)
        self.assertEqual(configuration.log_filename, "application.log")
        self.assertTrue(configuration.function_trace_enabled)
        self.assertTrue(configuration.execution_trace_enabled)
        self.assertEqual(configuration.trace_filename, "execution.trace")
        self.assertEqual(configuration.trace_level, TraceLevel.FULL)

    def test_configuration_setter(self) -> None:
        """The configuration setter should initialize all dialog settings."""
        configuration = EmulatorConfiguration(
            sound_enabled=False,
            sound_volume=65,
            beeper_frequency=1500,
            audio_output_device="Device B",
            available_audio_devices=["Device A", "Device B"],
            emulation_mode=EmulationMode.SCHIPC,
            disable_display_updates=True,
            logging_enabled=True,
            logging_enabled_info=False,
            logging_enabled_warning=True,
            logging_enabled_error=False,
            log_filename="application.log",
            function_trace_enabled=True,
            execution_trace_enabled=True,
            trace_filename="execution.trace",
            trace_level=TraceLevel.CHANGES
        )
        self.dialog.configuration = configuration
        self.assertFalse(self.dialog.sound_enabled)
        self.assertEqual(self.dialog.sound_volume, 65)
        self.assertEqual(self.dialog.sound_frequency, 1500)
        self.assertEqual( self.dialog.audioDeviceComboBox.currentText(), "Device B")
        self.assertEqual(
            [
                self.dialog.audioDeviceComboBox.itemText(index)
                for index in range(self.dialog.audioDeviceComboBox.count())
            ],
            ["Device A", "Device B"]
        )
        self.assertTrue(self.dialog.superCRadioButton.isChecked())
        self.assertTrue(self.dialog.disableDisplayUpdatesCheckBox.isChecked())
        self.assertTrue(self.dialog.applicationLoggingGroupBox.isChecked())
        self.assertFalse(self.dialog.logInformationCheckBox.isChecked())
        self.assertTrue(self.dialog.logWarningsCheckBox.isChecked())
        self.assertFalse(self.dialog.logErrorsCheckBox.isChecked())
        self.assertEqual( self.dialog.logFilenameLineEdit.text(), "application.log")
        self.assertTrue(self.dialog.enableFunctionTraceCheckBox.isChecked())
        self.assertTrue(self.dialog.executionTraceGroupBox.isChecked())
        self.assertEqual( self.dialog.traceFilenameLineEdit.text(), "execution.trace")
        self.assertEqual(self.dialog.traceLevelComboBox.currentIndex(), 1)

    def test_configuration_setter_keeps_device_when_not_found(self) -> None:
        """An unavailable configured device should not select another device."""
        self.dialog.audioDeviceComboBox.addItems(["Device A", "Device B"])
        self.dialog.audioDeviceComboBox.setCurrentText("Device B")
        configuration = EmulatorConfiguration( audio_output_device="Unavailable", available_audio_devices=["Device A", "Device B"])
        self.dialog.configuration = configuration
        self.assertEqual( self.dialog.audioDeviceComboBox.currentText(), "Device A")

    def test_configuration_setter_selects_each_emulation_mode(self) -> None:
        """Each emulation mode should select its corresponding radio button."""
        radio_buttons = {
            EmulationMode.CLASSIC: self.dialog.classicRadioButton,
            EmulationMode.SUPERCHIP_10: self.dialog.super10RadioButton,
            EmulationMode.SUPERCHIP_11: self.dialog.super11RadioButton,
            EmulationMode.SUPERCHIP_MODERN: self.dialog.superModernRadioButton,
            EmulationMode.SCHIPC: self.dialog.superCRadioButton
        }
        for mode, radio_button in radio_buttons.items():
            with self.subTest(mode=mode):
                self.dialog.configuration = EmulatorConfiguration( emulation_mode=mode)
                self.assertTrue(radio_button.isChecked())

    def test_selected_emulation_mode_defaults_to_classic(self) -> None:
        """Classic should be returned when no other profile is selected."""
        self.assertEqual( self.dialog._selected_emulation_mode(), EmulationMode.CLASSIC)

    def test_selected_emulation_mode(self) -> None:
        """The selected radio button should determine the emulation mode."""
        cases = (
            (self.dialog.super10RadioButton, EmulationMode.SUPERCHIP_10),
            (self.dialog.super11RadioButton, EmulationMode.SUPERCHIP_11),
            (self.dialog.superModernRadioButton, EmulationMode.SUPERCHIP_MODERN),
            (self.dialog.superCRadioButton, EmulationMode.SCHIPC)
        )
        for radio_button, expected_mode in cases:
            with self.subTest(mode=expected_mode):
                radio_button.setChecked(True)
                self.assertEqual( self.dialog._selected_emulation_mode(), expected_mode)

    def test_browse_log_file_accepts_selected_file(self) -> None:
        """Accepting the log-file dialog should update the filename."""
        with patch("gui.configdialog.QFileDialog") as dialog_type:
            file_dialog = dialog_type.return_value
            file_dialog.exec.return_value = 1
            file_dialog.selectedFiles.return_value = ["/tmp/application.log"]
            self.dialog._browse_log_file()
        self.assertEqual( self.dialog.logFilenameLineEdit.text(), "/tmp/application.log")
        file_dialog.setWindowTitle.assert_called_once_with( "Application Log File")
        file_dialog.selectFile.assert_not_called()

    def test_browse_log_file_uses_existing_filename(self) -> None:
        """The current log filename should be selected in the file dialog."""
        self.dialog.logFilenameLineEdit.setText("existing.log")
        with patch("gui.configdialog.QFileDialog") as dialog_type:
            file_dialog = dialog_type.return_value
            file_dialog.exec.return_value = 0
            self.dialog._browse_log_file()
        file_dialog.selectFile.assert_called_once_with("existing.log")
        self.assertEqual( self.dialog.logFilenameLineEdit.text(), "existing.log")

    def test_browse_log_file_cancelled(self) -> None:
        """Cancelling the log-file dialog should leave the filename unchanged."""
        self.dialog.logFilenameLineEdit.setText("existing.log")
        with patch("gui.configdialog.QFileDialog") as dialog_type:
            dialog_type.return_value.exec.return_value = 0
            self.dialog._browse_log_file()
        self.assertEqual( self.dialog.logFilenameLineEdit.text(), "existing.log")

    def test_browse_log_file_without_selected_files(self) -> None:
        """An accepted dialog without a selected file should do nothing."""
        with patch("gui.configdialog.QFileDialog") as dialog_type:
            file_dialog = dialog_type.return_value
            file_dialog.exec.return_value = 1
            file_dialog.selectedFiles.return_value = []
            self.dialog._browse_log_file()
        self.assertEqual(self.dialog.logFilenameLineEdit.text(), "")

    def test_browse_trace_file_accepts_selected_file(self) -> None:
        """Accepting the trace-file dialog should update the filename."""
        with patch("gui.configdialog.QFileDialog") as dialog_type:
            file_dialog = dialog_type.return_value
            file_dialog.exec.return_value = 1
            file_dialog.selectedFiles.return_value = ["/tmp/execution.trace"]
            self.dialog._browse_trace_file()
        self.assertEqual( self.dialog.traceFilenameLineEdit.text(), "/tmp/execution.trace")
        file_dialog.setWindowTitle.assert_called_once_with( "Execution Trace File")

    def test_browse_trace_file_uses_existing_filename(self) -> None:
        """The current trace filename should be selected in the file dialog."""
        self.dialog.traceFilenameLineEdit.setText("existing.trace")
        with patch("gui.configdialog.QFileDialog") as dialog_type:
            file_dialog = dialog_type.return_value
            file_dialog.exec.return_value = 0
            self.dialog._browse_trace_file()
        file_dialog.selectFile.assert_called_once_with("existing.trace")
        self.assertEqual( self.dialog.traceFilenameLineEdit.text(), "existing.trace")

    def test_browse_trace_file_cancelled(self) -> None:
        """Cancelling the trace-file dialog should leave the filename unchanged."""
        self.dialog.traceFilenameLineEdit.setText("existing.trace")
        with patch("gui.configdialog.QFileDialog") as dialog_type:
            dialog_type.return_value.exec.return_value = 0
            self.dialog._browse_trace_file()
        self.assertEqual( self.dialog.traceFilenameLineEdit.text(), "existing.trace")

    def test_browse_trace_file_without_selected_files(self) -> None:
        """An accepted dialog without a selected file should do nothing."""
        with patch("gui.configdialog.QFileDialog") as dialog_type:
            file_dialog = dialog_type.return_value
            file_dialog.exec.return_value = 1
            file_dialog.selectedFiles.return_value = []
            self.dialog._browse_trace_file()
        self.assertEqual(self.dialog.traceFilenameLineEdit.text(), "")

    def test_accept_without_logging_enabled(self) -> None:
        """Accepting should not require a log filename when logging is disabled."""
        self.dialog.applicationLoggingGroupBox.setChecked(False)
        self.dialog.executionTraceGroupBox.setChecked(False)
        self.dialog.accept()
        self.assertEqual(self.dialog.result(), QDialog.DialogCode.Accepted)

    def test_accept_rejects_empty_log_filename(self) -> None:
        """Enabled application logging requires a filename."""
        self.dialog.applicationLoggingGroupBox.setChecked(True)
        self.dialog.logFilenameLineEdit.clear()
        with patch("gui.configdialog.QMessageBox.warning") as warning:
            self.dialog.accept()
        warning.assert_called_once()
        self.assertNotEqual( self.dialog.result(), QDialog.DialogCode.Accepted)

    def test_accept_rejects_missing_log_directory(self) -> None:
        """The log-file parent directory must exist."""
        self.dialog.applicationLoggingGroupBox.setChecked(True)
        self.dialog.logFilenameLineEdit.setText( "/directory_that_does_not_exist/application.log")
        with patch("gui.configdialog.QMessageBox.warning") as warning:
            self.dialog.accept()
        warning.assert_called_once()
        self.assertNotEqual( self.dialog.result(), QDialog.DialogCode.Accepted)

    def test_accept_rejects_empty_trace_filename(self) -> None:
        """Enabled execution tracing requires a filename."""
        self.dialog.executionTraceGroupBox.setChecked(True)
        self.dialog.traceFilenameLineEdit.clear()
        with patch("gui.configdialog.QMessageBox.warning") as warning:
            self.dialog.accept()
        warning.assert_called_once()
        self.assertNotEqual( self.dialog.result(), QDialog.DialogCode.Accepted)

    def test_accept_rejects_missing_trace_directory(self) -> None:
        """The trace-file parent directory must exist."""
        self.dialog.executionTraceGroupBox.setChecked(True)
        self.dialog.traceFilenameLineEdit.setText( "/directory_that_does_not_exist/execution.trace")
        with patch("gui.configdialog.QMessageBox.warning") as warning:
            self.dialog.accept()
        warning.assert_called_once()
        self.assertNotEqual( self.dialog.result(), QDialog.DialogCode.Accepted)

    def test_accept_with_valid_log_and_trace_filenames(self) -> None:
        """Valid enabled logging and tracing settings should be accepted."""
        with tempfile.TemporaryDirectory() as directory:
            self.dialog.applicationLoggingGroupBox.setChecked(True)
            self.dialog.logFilenameLineEdit.setText( str(Path(directory) / "application.log"))
            self.dialog.executionTraceGroupBox.setChecked(True)
            self.dialog.traceFilenameLineEdit.setText( str(Path(directory) / "execution.trace"))
            self.dialog.accept()
        self.assertEqual(self.dialog.result(), QDialog.DialogCode.Accepted)


class TestTraceLevelConversions(unittest.TestCase):
    """Tests for trace-level conversion helpers."""

    def test_trace_level_to_index(self) -> None:
        """Each trace level should map to its corresponding combo index."""
        expected = ( (TraceLevel.BASIC, 0), (TraceLevel.CHANGES, 1), (TraceLevel.FULL, 2))
        for level, index in expected:
            with self.subTest(level=level):
                self.assertEqual(trace_level_to_index(level), index)

    def test_index_to_trace_level(self) -> None:
        """Each combo index should map to its corresponding trace level."""
        expected = ( (0, TraceLevel.BASIC), (1, TraceLevel.CHANGES), (2, TraceLevel.FULL))
        for index, level in expected:
            with self.subTest(index=index):
                self.assertEqual(index_to_trace_level(index), level)

