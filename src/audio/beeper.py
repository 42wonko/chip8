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


    def start(self) -> None:
        """
        @brief Start the CHIP-8 beep.
        """
        if self._playing:
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

