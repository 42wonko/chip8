"""
@file test_audiodevice.py

@brief Tests for the sounddevice audio backend.
"""

import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from audio.audiodevice import AudioDevice
from controller.diagnostic import DiagnosticSource
from controller.diagnostics import Diagnostics
from controller.emulatorconfiguration import EmulatorConfiguration
from emulator.constants import DEFAULT_BEEPER_FREQUENCY


class FakeStream:
    """
    @brief Fake sounddevice output stream.
    """
    def __init__(self) -> None:
        self.started = False
        self.stopped = False
        self.closed = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True

    def close(self) -> None:
        self.closed = True


class TestAudioDevice(unittest.TestCase):
    """
    @brief Test AudioDevice.
    """

    def create_audio_device(self) -> AudioDevice:
        diagnostics = Diagnostics()
        return AudioDevice( diagnostics.reporter(DiagnosticSource.UNIT_TEST))


    def test_initial_configuration(self) -> None:
        device = self.create_audio_device()
        self.assertEqual( device._frequency, DEFAULT_BEEPER_FREQUENCY)
        self.assertEqual( device._volume, 1.0)
        self.assertEqual( device._audio_output_device, "default")


    @patch("audio.audiodevice.sd.query_devices")
    def test_enumerate_devices(self, query_devices: MagicMock) -> None:
        query_devices.return_value = [
            { "name": "Output Device", "max_output_channels": 2 },
            { "name": "Input Device", "max_output_channels": 0 }
        ]
        device = self.create_audio_device()
        devices = device.enumerate_audio_devices()
        self.assertEqual( devices, [ "default", "Output Device" ])


    @patch("audio.audiodevice.sd.OutputStream")
    def test_start_creates_stream( self, output_stream: MagicMock) -> None:
        stream = FakeStream()
        output_stream.return_value = stream
        device = self.create_audio_device()
        device.start()
        output_stream.assert_called_once()
        self.assertTrue(stream.started)


    @patch("audio.audiodevice.sd.OutputStream")
    def test_start_does_not_create_second_stream( self, output_stream: MagicMock) -> None:
        output_stream.return_value = FakeStream()
        device = self.create_audio_device()
        device.start()
        device.start()
        output_stream.assert_called_once()


    @patch("audio.audiodevice.sd.OutputStream")
    def test_stop_keeps_stream_open( self, output_stream: MagicMock) -> None:
        stream = FakeStream()
        output_stream.return_value = stream
        device = self.create_audio_device()
        device.start()
        device.stop()
        self.assertFalse(stream.stopped)
        self.assertFalse(stream.closed)


    @patch("audio.audiodevice.sd.OutputStream")
    def test_shutdown_closes_stream( self, output_stream: MagicMock) -> None:
        stream = FakeStream()
        output_stream.return_value = stream
        device = self.create_audio_device()
        device.start()
        device.shutdown()
        self.assertTrue(stream.stopped)
        self.assertTrue(stream.closed)


    @patch("audio.audiodevice.sd.OutputStream")
    def test_volume_change_does_not_restart_stream( self, output_stream: MagicMock) -> None:
        output_stream.return_value = FakeStream()
        device = self.create_audio_device()
        device.start()
        device.set_volume(50)
        output_stream.assert_called_once()
        self.assertEqual(device._volume, 0.5)


    @patch("audio.audiodevice.sd.OutputStream")
    def test_device_change_restarts_stream( self, output_stream: MagicMock) -> None:
        output_stream.return_value = FakeStream()
        device = self.create_audio_device()
        device.start()
        configuration = EmulatorConfiguration( audio_output_device="USB Audio")
        device.apply_configuration(configuration)
        self.assertEqual( output_stream.call_count, 2)


    def test_callback_generates_output(self) -> None:
        device = self.create_audio_device()
        device._enabled = True
        output = np.zeros( (100, 2), dtype=np.float32)
        device._callback( output, 100, None, None)
        self.assertTrue( np.any(output != 0))
        self.assertEqual( output.shape, (100, 2))


    def test_callback_generates_silence_when_disabled(self) -> None:
        device = self.create_audio_device()
        output = np.ones( (100, 2), dtype=np.float32)
        device._callback( output, 100, None, None)
        self.assertTrue( np.all(output == 0))
