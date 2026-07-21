"""
@file test_beeper.py

@brief Tests for the CHIP-8 beeper interface.
"""

import unittest
from unittest.mock import MagicMock, patch

from audio.beeper import Beeper
from controller.diagnostic import DiagnosticSource
from controller.diagnostics import Diagnostics
from controller.emulatorconfiguration import EmulatorConfiguration


class TestBeeper(unittest.TestCase):
    """
    @brief Test Beeper.
    """

    def create_beeper(self) -> Beeper:
        diagnostics = Diagnostics()
        return Beeper( diagnostics.reporter(DiagnosticSource.UNIT_TEST))


    def test_initial_state(self) -> None:
        beeper = self.create_beeper()
        self.assertFalse(beeper.is_playing)
        self.assertTrue(beeper.enabled)
        self.assertEqual( beeper.volume, 100)


    @patch("audio.beeper.AudioDevice")
    def test_start(self, audio_device: MagicMock) -> None:
        beeper = self.create_beeper()
        beeper.start()
        self.assertTrue(beeper.is_playing)
        audio_device.return_value.start.assert_called_once()


    @patch("audio.beeper.AudioDevice")
    def test_start_when_disabled(self, audio_device: MagicMock) -> None:
        beeper = self.create_beeper()
        configuration = EmulatorConfiguration( sound_enabled=False)
        beeper.configuration = configuration
        beeper.start()
        self.assertFalse(beeper.is_playing)
        audio_device.return_value.start.assert_not_called()


    @patch("audio.beeper.AudioDevice")
    def test_stop(self, audio_device: MagicMock) -> None:
        beeper = self.create_beeper()
        beeper.start()
        beeper.stop()
        self.assertFalse(beeper.is_playing)
        audio_device.return_value.stop.assert_called_once()


    @patch("audio.beeper.AudioDevice")
    def test_configuration_update(self, audio_device: MagicMock) -> None:
        beeper = self.create_beeper()
        configuration = EmulatorConfiguration( sound_volume=25, beeper_frequency=880)
        beeper.configuration = configuration
        self.assertEqual( beeper.volume, 25)
        audio_device.return_value.apply_configuration.assert_called_with( configuration)


    @patch("audio.beeper.AudioDevice")
    def test_configuration_disable_stops_beeper( self, audio_device: MagicMock) -> None:
        beeper = self.create_beeper()
        beeper.start()
        configuration = EmulatorConfiguration( sound_enabled=False)
        beeper.configuration = configuration
        self.assertFalse( beeper.is_playing)
        audio_device.return_value.stop.assert_called()


    @patch("audio.beeper.AudioDevice")
    def test_enumerate_audio_devices( self, audio_device: MagicMock) -> None:
        audio_device.return_value.enumerate_audio_devices.return_value = [ "default", "USB Audio" ]
        beeper = self.create_beeper()
        devices = beeper.enumerate_audio_devices()
        self.assertEqual( devices, [ "default", "USB Audio" ])


    @patch("audio.beeper.AudioDevice")
    def test_shutdown( self, audio_device: MagicMock) -> None:
        beeper = self.create_beeper()
        beeper.shutdown()
        audio_device.return_value.shutdown.assert_called_once()
