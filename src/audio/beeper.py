"""
@file beeper.py

@brief CHIP-8 audio output.
"""

from __future__ import annotations

from PyQt6.QtMultimedia import QAudioDevice, QAudioFormat, QAudioSink, QMediaDevices

from audio.squarewavegenerator import SquareWaveGenerator
from controller.emulatorconfiguration import EmulatorConfiguration
from emulator.constants import BEEPER_SAMPLE_RATE


class Beeper:
    """
    @brief CHIP-8 audio output.

    @details
    Generates a continuous square wave while enabled.
    """
    def __init__(self) -> None:
        """
        @brief Construct the beeper.
        """
        format = QAudioFormat()
        format.setSampleRate(BEEPER_SAMPLE_RATE)
        format.setChannelCount(1)
        format.setSampleFormat(QAudioFormat.SampleFormat.Int16)
        self._configuration = EmulatorConfiguration()       # store the configuration object
        device: QAudioDevice = QMediaDevices.defaultAudioOutput()
        self._generator = SquareWaveGenerator()
        self._audio = QAudioSink(device, format)
        self._playing = False
        self.configuration = self._configuration            # configure ourselfes using the setter
#        self._audio.setVolume(self._configuration.sound_volume / 100.0)


    def set_volume(self, volume: int) -> None:
        """
        @brief Set the output volume.

        @param volume
            Volume in percent [0..100].
        """
        volume = max(0, min(100, volume))
        self.configuration.sound_volume = volume
        self._audio.setVolume(volume / 100.0)


    def enable(self, enabled: bool) -> None:
        if self.configuration.sound_enabled == enabled:
            return
        self.configuration.sound_enabled = enabled
        if not enabled:
            self.stop()


    def start(self) -> None:
        """
        @brief Start the CHIP-8 beep.
        """
        if not self.configuration.sound_enabled or self._playing:
            return
        self._generator.start()
        self._audio.start(self._generator)
        self._playing = True


    def stop(self) -> None:
        """
        @brief Stop the CHIP-8 beep.
        """
        if not self._playing:
            return
        self._audio.reset()
#        self._generator.stop()
        self._playing = False


    def close(self) -> None:
        """
        @brief Release audio resources.
        """
        self.stop()


    @property
    def is_playing(self) -> bool:
        """
        @brief Return whether the beeper is currently active.
        """
        return self._playing

    @property
    def enabled(self) -> bool:
        return self.configuration.sound_enabled

    @property
    def volume(self) -> int:
        return self.configuration.sound_volumeY

    @property
    def configuration(self) -> EmulatorConfiguration:
        """
        @brief Return the current audio configuration.
        """
        return self._configuration


    @configuration.setter
    def configuration(self, configuration: EmulatorConfiguration) -> None:
        """
        @brief Apply a new audio configuration.
        """
        self._configuration = configuration
        self._audio.setVolume( configuration.sound_volume / 100.0)
        if not configuration.sound_enabled:
            self.stop()

