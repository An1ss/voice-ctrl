"""Audio feedback module for playing beep sounds."""

import sounddevice as sd
import numpy as np
import threading


class AudioFeedback:
    """Plays audio feedback beeps for recording events."""

    def __init__(self, enabled=True, sample_rate=44100):
        """Initialize the audio feedback system.

        Args:
            enabled: Whether audio feedback is enabled
            sample_rate: Sample rate for audio playback (default 44100 Hz)
        """
        self.enabled = enabled
        self.sample_rate = sample_rate

    def _generate_beep(self, frequency, duration, volume=0.3):
        """Generate a simple sine wave beep.

        Args:
            frequency: Frequency in Hz (e.g., 800 for high beep, 400 for low beep)
            duration: Duration in seconds
            volume: Volume level (0.0 to 1.0, default 0.3 for non-intrusive)

        Returns:
            numpy array containing the audio samples
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        # Generate sine wave
        note = np.sin(frequency * 2 * np.pi * t)
        # Apply envelope to avoid clicks (fade in/out)
        envelope = np.ones_like(note)
        fade_samples = int(0.01 * self.sample_rate)  # 10ms fade
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        # Apply volume and envelope
        audio = note * envelope * volume
        return audio

    def _play_sound(self, audio_data):
        """Play audio data through the default output device.

        Args:
            audio_data: numpy array containing audio samples
        """
        try:
            sd.play(audio_data, self.sample_rate)
            # Don't wait for playback to complete (non-blocking)
        except Exception as e:
            # Fail silently - audio feedback is non-critical
            pass

    def play_start_beep(self):
        """Play a beep sound when recording starts (higher pitch)."""
        if not self.enabled:
            return

        def _play_async():
            # Higher frequency beep for "start" (800 Hz)
            beep = self._generate_beep(frequency=800, duration=0.1)
            self._play_sound(beep)

        # Play in separate thread to avoid blocking
        thread = threading.Thread(target=_play_async, daemon=True)
        thread.start()

    def play_stop_beep(self):
        """Play a beep sound when recording stops (lower pitch)."""
        if not self.enabled:
            return

        def _play_async():
            # Lower frequency beep for "stop" (400 Hz)
            beep = self._generate_beep(frequency=400, duration=0.15)
            self._play_sound(beep)

        # Play in separate thread to avoid blocking
        thread = threading.Thread(target=_play_async, daemon=True)
        thread.start()

    def set_enabled(self, enabled):
        """Enable or disable audio feedback.

        Args:
            enabled: True to enable, False to disable
        """
        self.enabled = enabled
