
import unittest
from unittest.mock import MagicMock, patch

from chip8.settingsmanager import SettingsManager


class TestSettingsManager(unittest.TestCase):
    @patch("chip8.settingsmanager.QSettings")
    def test_constructor_creates_qsettings( self, qsettings_class: MagicMock) -> None:
        settings = MagicMock()
        qsettings_class.return_value = settings
        manager = SettingsManager()
        qsettings_class.assert_called_once_with( SettingsManager.ORGANIZATION, SettingsManager.APPLICATION)
        self.assertIs(manager.settings(), settings)

    @patch("chip8.settingsmanager.QSettings")
    def test_load_configuration_delegates_to_configuration( self, qsettings_class: MagicMock) -> None:
        manager = SettingsManager()
        configuration = MagicMock()
        manager.load_configuration(configuration)
        configuration.read_settings.assert_called_once_with( qsettings_class.return_value)

    @patch("chip8.settingsmanager.QSettings")
    def test_save_configuration_delegates_to_configuration( self, qsettings_class: MagicMock) -> None:
        manager = SettingsManager()
        configuration = MagicMock()
        manager.save_configuration(configuration)
        configuration.write_settings.assert_called_once_with( qsettings_class.return_value)

    @patch("chip8.settingsmanager.QSettings")
    def test_settings_returns_underlying_settings_object( self, qsettings_class: MagicMock) -> None:
        manager = SettingsManager()
        self.assertIs(manager.settings(), qsettings_class.return_value)

