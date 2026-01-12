"""Audio recording module using sounddevice library."""

import sounddevice as sd
import numpy as np
import wave
import threading
import time
from pathlib import Path
from datetime import datetime


class AudioRecorder:
    """Records audio from microphone with toggle start/stop behavior."""

    def __init__(self, sample_rate=16000, channels=1, max_duration=240):
        """Initialize the audio recorder.

        Args:
            sample_rate: Sample rate in Hz (default 16000 for Whisper compatibility)
            channels: Number of audio channels (1 for mono, 2 for stereo)
            max_duration: Maximum recording duration in seconds (default 240)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.max_duration = max_duration
        self.is_recording = False
        self.audio_data = []
        self.recording_thread = None
        self.start_time = None

    def start_recording(self):
        """Start audio recording in a separate thread."""
        if self.is_recording:
            print("Already recording!")
            return

        self.is_recording = True
        self.audio_data = []
        self.start_time = time.time()

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
                if elapsed >= self.max_duration:
                    print(f"Maximum duration ({self.max_duration}s) reached. Auto-stopping...")
                    self.is_recording = False

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
