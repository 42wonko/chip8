"""
@file beeper.py

@brief CHIP-8 audio output.
"""

from __future__ import annotations

from PyQt6.QtMultimedia import QAudioDevice, QAudioFormat, QAudioSink, QMediaDevices
from audio.squarewavegenerator import SquareWaveGenerator
from emulator.constants import  BEEPER_SAMPLE_RATE


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
        device: QAudioDevice = QMediaDevices.defaultAudioOutput()
        self._generator = SquareWaveGenerator()
        self._audio = QAudioSink(device, format)
        self._playing = False
        self._enabled = True
        self._volume = 100
        self._audio.setVolume(self._volume / 100.0)


    def set_volume(self, volume: int) -> None:
        """
        @brief Set the output volume.

        @param volume
            Volume in percent [0..100].
        """
        volume = max(0, min(100, volume))
        self._volume = volume
        self._audio.setVolume(volume / 100.0)


    def enable(self, enabled: bool) -> None:
        if self._enabled == enabled:
            return
        self._enabled = enabled
        if not enabled:
            self.stop()


    def start(self) -> None:
        """
        @brief Start the CHIP-8 beep.
        """
        if not self._enabled or self._playing:
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
        return self._enabled

    @property
    def volume(self) -> int:
        return self._volume
