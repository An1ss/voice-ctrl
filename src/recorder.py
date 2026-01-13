"""Audio recording module using sounddevice library."""

import sounddevice as sd
import numpy as np
import wave
import threading
import time
from pathlib import Path
from datetime import datetime
from .notifier import Notifier
from .audio_feedback import AudioFeedback


class AudioRecorder:
    """Records audio from microphone with toggle start/stop behavior."""

    def __init__(self, sample_rate=16000, channels=1, max_duration=240, audio_feedback_enabled=True):
        """Initialize the audio recorder.

        Args:
            sample_rate: Sample rate in Hz (default 16000 for Whisper compatibility)
            channels: Number of audio channels (1 for mono, 2 for stereo)
            max_duration: Maximum recording duration in seconds (default 240)
            audio_feedback_enabled: Whether to play beeps on start/stop (default True)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.max_duration = max_duration
        self.is_recording = False
        self.audio_data = []
        self.recording_thread = None
        self.start_time = None
        self.notifier = Notifier()
        self.audio_feedback = AudioFeedback(enabled=audio_feedback_enabled)
        self.on_auto_stop_callback = None  # Callback for auto-stop events

    def start_recording(self):
        """Start audio recording in a separate thread."""
        if self.is_recording:
            print("Already recording!")
            return

        self.is_recording = True
        self.audio_data = []
        self.start_time = time.time()

        # Play start beep
        self.audio_feedback.play_start_beep()

        # Start recording in a separate thread to avoid blocking
        self.recording_thread = threading.Thread(target=self._record)
        self.recording_thread.start()

        print(f"Recording started... (max {self.max_duration}s)")

    def stop_recording(self):
        """Stop audio recording and save to WAV file."""
        if not self.is_recording:
            print("Not currently recording!")
            return None

        self.is_recording = False

        # Wait for recording thread to finish
        if self.recording_thread:
            self.recording_thread.join()

        # Play stop beep
        self.audio_feedback.play_stop_beep()

        duration = time.time() - self.start_time
        print(f"Recording stopped. Duration: {duration:.2f}s")

        # Save to temporary WAV file
        return self._save_to_wav()

    def toggle_recording(self):
        """Toggle between start and stop recording."""
        if self.is_recording:
            return self.stop_recording()
        else:
            self.start_recording()
            return None

    def set_auto_stop_callback(self, callback):
        """Set callback function to be called when recording auto-stops.

        Args:
            callback: Function that takes audio_file path as argument
        """
        self.on_auto_stop_callback = callback

    def _handle_auto_stop(self):
        """Handle auto-stop by performing same actions as manual stop."""
        # Wait for recording thread to finish
        if self.recording_thread:
            self.recording_thread.join()

        # Play stop beep
        self.audio_feedback.play_stop_beep()

        duration = time.time() - self.start_time
        print(f"Recording auto-stopped. Duration: {duration:.2f}s")

        # Save to WAV file
        audio_file = self._save_to_wav()

        # Notify user that auto-stop occurred
        if audio_file:
            self.notifier.notify_error(
                "Recording Auto-Stopped",
                f"Maximum duration ({self.max_duration}s) reached. Transcribing..."
            )

        # Invoke callback to trigger transcription
        if self.on_auto_stop_callback and audio_file:
            self.on_auto_stop_callback(audio_file)

    def _record(self):
        """Internal method to record audio (runs in separate thread)."""
        def callback(indata, frames, time_info, status):
            """Callback function called by sounddevice for each audio block."""
            if status:
                print(f"Recording status: {status}")
            self.audio_data.append(indata.copy())

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=callback
            ):
                # Record until stopped or max duration reached
                elapsed = 0
                while self.is_recording and elapsed < self.max_duration:
                    time.sleep(0.1)
                    elapsed = time.time() - self.start_time

                # Auto-stop if max duration reached
                if elapsed >= self.max_duration and self.is_recording:
                    print(f"Maximum duration ({self.max_duration}s) reached. Auto-stopping...")
                    self.is_recording = False
                    # Trigger auto-stop processing in a separate thread
                    threading.Thread(target=self._handle_auto_stop, daemon=True).start()

        except Exception as e:
            print(f"Error during recording: {e}")
            self.is_recording = False

    def _save_to_wav(self):
        """Save recorded audio data to WAV file in /tmp/ directory.

        Returns:
            Path to the saved WAV file, or None if no data recorded
        """
        if not self.audio_data:
            print("No audio data to save!")
            self.notifier.notify_no_audio()
            return None

        # Concatenate all audio chunks
        audio_array = np.concatenate(self.audio_data, axis=0)

        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = Path(f"/tmp/voice_recording_{timestamp}.wav")

        # Save as WAV file
        try:
            with wave.open(str(filepath), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(self.sample_rate)
                # Convert float32 to int16
                audio_int16 = (audio_array * 32767).astype(np.int16)
                wf.writeframes(audio_int16.tobytes())

            print(f"Audio saved to: {filepath}")
            return str(filepath)

        except Exception as e:
            print(f"Error saving audio file: {e}")
            return None
