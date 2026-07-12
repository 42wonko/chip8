"""
@file squarewavegenerator.py

@brief Continuous square-wave PCM generator.
"""

from __future__ import annotations

from PyQt6 import sip
from PyQt6.QtCore import QIODevice, QObject

from emulator.constants import BEEPER_AMPLITUDE, BEEPER_FREQUENCY, BEEPER_SAMPLE_RATE


class SquareWaveGenerator(QIODevice):
    """
    @brief Continuous square-wave audio generator.

    @details
    Generates an endless signed 16-bit PCM mono square wave.
    The generator behaves like a random-access file so that
    QAudioSink may seek within the stream.
    """

    _BYTES_PER_SAMPLE = 2          # signed 16-bit PCM
    _CHANNEL_COUNT = 1
    _BYTES_PER_FRAME = _BYTES_PER_SAMPLE * _CHANNEL_COUNT

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._period = max( 1, round(BEEPER_SAMPLE_RATE / BEEPER_FREQUENCY),)   # Samples per waveform period.
        self._position = 0                                                      # Current byte position within the virtual stream.


    def start(self) -> None:
        """
        @brief Begin audio generation.
        """
        self._position = 0
        self.open(QIODevice.OpenModeFlag.ReadOnly)


    def stop(self) -> None:
        """
        @brief Stop audio generation.
        """
        self.close()


    ###########################################################################
    # QIODevice interface
    ###########################################################################

    def readData(self, maxlen: int) -> bytes:
        """
        @brief Produce PCM samples.

        @param maxlen
            Number of bytes requested.

        @return
            Signed 16-bit little-endian PCM data.
        """
        maxlen &= ~(self._BYTES_PER_FRAME - 1)        # Always generate complete samples.
        data = bytearray(maxlen)
        position = self._position
        for index in range(0, maxlen, self._BYTES_PER_FRAME):
            sample = position // self._BYTES_PER_SAMPLE
            phase = sample % self._period
            if phase < self._period // 2:
                value = BEEPER_AMPLITUDE
            else:
                value = -BEEPER_AMPLITUDE
            data[index:index + 2] = value.to_bytes( 2, byteorder="little", signed=True)
            position += self._BYTES_PER_FRAME
        self._position = position
        return bytes(data)


    def writeData(self, data: sip.Buffer) -> int:
        """
        @brief Writing is unsupported.
        """
        return 0


    ###########################################################################
    # Random-access interface
    ###########################################################################
    def pos(self) -> int:
        """
        @brief Return the current byte position.
        """
        return self._position


    def seek(self, position: int) -> bool:
        """
        @brief Seek to a new byte position.
        """
        if position < 0:
            return False

        self._position = position
        return True


    def size(self) -> int:
        """
        @brief Return the size of the virtual audio stream.

        @details
        The stream is effectively endless. Return a very large size so
        that the audio backend may seek freely.
        """
        return 0x7FFFFFFFFFFFFFFF


    def bytesAvailable(self) -> int:
        """
        @brief Report that audio data is always available.
        """
        return self._BYTES_PER_FRAME * 4096 + super().bytesAvailable()

