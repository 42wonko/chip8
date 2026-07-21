"""
@file beeper.py

@brief CHIP-8 audio output interface.

@details
High-level CHIP-8 beeper interface. The Beeper owns the audio
configuration and delegates low-level audio generation to AudioDevice.
"""

from __future__ import annotations

from PyQt6.QtCore import QTimer

from audio.audiodevice import AudioDevice
from controller.diagnostics import DiagnosticReporter
from controller.emulatorconfiguration import EmulatorConfiguration


class Beeper:
    """
    @brief CHIP-8 audio output.

    @details
    Provides the public sound interface used by the controller.
    """

    def __init__(self, diagnostics: DiagnosticReporter) -> None:
        """
        @brief Construct the beeper.
        """
        self._diagnostics = diagnostics
        self._configuration = EmulatorConfiguration()
        self._audio_device = AudioDevice(diagnostics)
        self._playing = False
        self.configuration = self._configuration
        self._test_timer = QTimer()
        self._test_timer.setSingleShot(True)
        self._test_timer.timeout.connect(self.stop)

    def start(self) -> None:
        """
        @brief Start the CHIP-8 beep.
        """
        if self._playing:
            return
        if not self.configuration.sound_enabled:
            return
        self._playing = True
        self._audio_device.start()


    def stop(self) -> None:
        """
        @brief Stop the CHIP-8 beep.
        """
        if not self._playing:
            return
        self._playing = False
        self._audio_device.stop()


    def test(self, configuration: EmulatorConfiguration | None = None) -> None:
        """
        @brief Play a test sound.

        @param configuration
            Optional temporary configuration.
        """
        if configuration is not None:
            self.configuration = configuration
            self.start()
            self._test_timer.start(500)


    def set_volume(self, volume: int) -> None:
        """
        @brief Set the output volume.

        @param volume
            Volume in percent [0..100].
        """
        volume = max(0, min(100, volume))
        self._configuration.sound_volume = volume
        self._audio_device.set_volume(volume)


    def shutdown(self) -> None:
        """
        @brief Release audio resources.
        """
        self._playing = False
        self._audio_device.shutdown()


    def enumerate_audio_devices(self) -> list[str]:
        """
        @brief Return available audio output device names.
        """
        return self._audio_device.enumerate_audio_devices()


    @property
    def is_playing(self) -> bool:
        """
        @brief Return whether the beeper is active.
        """
        return self._playing


    @property
    def enabled(self) -> bool:
        """
        @brief Return whether sound output is enabled.
        """
        return self.configuration.sound_enabled


    @property
    def volume(self) -> int:
        """
        @brief Return configured volume.
        """
        return self.configuration.sound_volume


    @property
    def configuration(self) -> EmulatorConfiguration:
        """
        @brief Return current audio configuration.
        """
        return self._configuration


    @configuration.setter
    def configuration(self, configuration: EmulatorConfiguration) -> None:
        """
        @brief Apply a new audio configuration.
        """
        self._configuration = configuration
        self._audio_device.apply_configuration(configuration)

        if not configuration.sound_enabled:
            self.stop()

