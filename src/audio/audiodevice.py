# audio/audiodevice.py

"""
@file audiodevice.py

@brief Sound device abstraction for CHIP-8 audio output.

@details
Provides a backend-neutral audio device implementation using sounddevice.
The device owns the OutputStream, callback generation, oscillator state,
phase accumulator, and audio device handling.

The stream is continuous. The callback outputs either silence or a square
wave depending on the current enabled state.
"""

from __future__ import annotations

import threading

import numpy as np
import sounddevice as sd

from controller.diagnostics import DiagnosticReporter
from controller.emulatorconfiguration import EmulatorConfiguration
from emulator.constants import BEEPER_AMPLITUDE, DEFAULT_BEEPER_FREQUENCY, BEEPER_SAMPLE_RATE


class AudioDevice:
    """
    @brief Low-level audio output device.

    @details
    Owns the sounddevice OutputStream and generates the CHIP-8 square wave.
    """

    def __init__(self, diagnostics: DiagnosticReporter) -> None:
        """
        @brief Construct the audio device.
        """
        self._diagnostics = diagnostics
        self._stream: sd.OutputStream | None = None
        self._lock = threading.Lock()
        self._enabled = False
        self._phase = 0.0
        self._frequency = DEFAULT_BEEPER_FREQUENCY
        self._volume = 1.0
        self._audio_output_device = "default"


    ###########################################################################
    # Configuration
    ###########################################################################
    def apply_configuration( self, configuration: EmulatorConfiguration) -> None:
        """
        @brief Apply audio configuration.

        @details
        The stream is restarted only when the selected output device changes.
        """
        with self._lock:
            self._volume = max( 0.0, min(1.0, configuration.sound_volume / 100.0))
            if not configuration.sound_enabled:
                self._enabled = False
            if configuration.audio_output_device == self._audio_output_device:
                return
            self._audio_output_device = configuration.audio_output_device
            self._restart_stream_locked()


    ###########################################################################
    # Stream handling
    ###########################################################################
    def _create_stream_locked(self) -> None:
        """
        @brief Create and start the audio stream.
        """
        if self._stream is not None:
            return
        device: str | None = None
        if self._audio_output_device != "default":
            device = self._audio_output_device

        try:
            self._stream = sd.OutputStream( device=device, samplerate=BEEPER_SAMPLE_RATE, channels=2, dtype="float32", callback=self._callback)
            self._stream.start()

        except sd.PortAudioError as e:
            self._diagnostics.error( f"Unable to open audio device '{self._audio_output_device}': {e}")
            if device is None:
                return
            self._audio_output_device = "default"
            try:
                self._stream = sd.OutputStream( samplerate=BEEPER_SAMPLE_RATE, channels=2, dtype="float32", callback=self._callback)
                self._stream.start()
            except sd.PortAudioError as e2:
                self._stream = None
                self._diagnostics.error( f"Unable to open default audio device: {e2}")


    def _restart_stream_locked(self) -> None:
        """
        @brief Restart the stream after a device change.
        """
        self._close_stream_locked()
        self._create_stream_locked()


    def _close_stream_locked(self) -> None:
        """
        @brief Close the current audio stream.
        """
        if self._stream is None:
            return
        try:
            self._stream.stop()
            self._stream.close()
        except Exception as exc:
            self._diagnostics.error( f"Unable to close audio device: {exc}")
        finally:
            self._stream = None


    ###########################################################################
    # Public control
    ###########################################################################
    def start(self) -> None:
        """
        @brief Enable tone generation.
        """
        with self._lock:
            self._enabled = True
            self._create_stream_locked()


    def stop(self) -> None:
        """
        @brief Disable tone generation.
        """
        with self._lock:
            self._enabled = False


    def test(self) -> None:
        """
        @brief Generate a short test tone.

        @details
        This method only enables the generator. The caller controls the
        duration of the test.
        """
        self.start()


    def set_volume(self, volume: int) -> None:
        """
        @brief Set software output volume.

        @param volume
            Volume in percent [0..100].
        """
        with self._lock:
            self._volume = max(0.0, min(1.0, volume / 100.0))


    def shutdown(self) -> None:
        """
        @brief Release audio resources.
        """
        with self._lock:
            self._enabled = False
            self._close_stream_locked()


    ###########################################################################
    # Device enumeration
    ###########################################################################
    def enumerate_audio_devices(self) -> list[str]:
        """
        @brief Return available output device names.
        """
        devices: list[str] = ["default"]


        try:
            for device in sd.query_devices():
                if device["max_output_channels"] > 0:
                    devices.append(device["name"])
        except Exception as e:
            self._diagnostics.error( f"Unable to enumerate audio devices: {e}")
        return devices


    ###########################################################################
    # Audio callback
    ###########################################################################
    def _callback( self, outdata: np.ndarray, frames: int, time, status) -> None:
        """
        @brief Generate audio samples.

        @details
        Called from the sounddevice audio thread.
        """
        if status:
            self._diagnostics.warning( f"Audio callback status: {status}")

        if not self._enabled:
            outdata.fill(0)
            return

        phase_increment = ( self._frequency / BEEPER_SAMPLE_RATE)
        phases = ( self._phase + np.arange(frames) * phase_increment)
        phases %= 1.0
        wave = np.where( phases < 0.5, 1.0, -1.0)
        amplitude = ( BEEPER_AMPLITUDE / 32768.0)
        samples = ( wave * amplitude * self._volume).astype(np.float32)

        outdata[:, 0] = samples
        outdata[:, 1] = samples

        self._phase = ( self._phase + frames * phase_increment) % 1.0
