#!/usr/bin/env python3
"""Test script to verify transcription functionality."""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.transcriber import WhisperTranscriber
from src.local_transcriber import LocalTranscriber
from src.recorder import AudioRecorder

def test_local_transcription():
    """Test local transcription with faster-whisper."""
    print("\n=== Testing Local Transcription (faster-whisper) ===")

    # Create a test config with local provider
    config = Config()

    # Temporarily set to local mode
    original_provider = config.get_stt_provider()
    config.config['stt_provider'] = 'local'

    try:
        transcriber = LocalTranscriber(config=config)

        # Test that the transcriber was initialized
        print(f"✓ LocalTranscriber initialized")
        print(f"  Engine: {transcriber.engine}")
        print(f"  Model path: {transcriber.model_path}")
        print(f"  Model ID: {transcriber.model_id}")

        # Test with a recording (user manual test)
        print("\n--- Manual Test ---")
        print("This test will record 5 seconds of audio and transcribe it using faster-whisper.")
        print("Press Enter to start recording, then speak clearly for 5 seconds...")
        input()

        recorder = AudioRecorder(max_duration=5, audio_feedback_enabled=True)
        print("Recording started - speak now...")
        audio_file = recorder.toggle_recording()
        time.sleep(5.5)  # Wait for recording to complete
        audio_file = recorder.toggle_recording()

        if audio_file:
            print(f"Recording saved to: {audio_file}")
            print("Transcribing with faster-whisper...")
            result = transcriber.transcribe(audio_file)

            if result:
                print(f"✓ Transcription successful: {result}")
            else:
                print("✗ Transcription returned None")
        else:
            print("✗ Recording failed - no audio file")

    finally:
        # Restore original provider
        config.config['stt_provider'] = original_provider

def test_openai_transcription():
    """Test OpenAI transcription path."""
    print("\n=== Testing OpenAI Transcription ===")

    config = Config()

    # Check if API key is configured
    api_key = config.get_api_key()
    if not api_key or not api_key.strip():
        print("⊘ Skipping OpenAI test - no API key configured")
        return

    try:
        transcriber = WhisperTranscriber(config=config)

        print(f"✓ WhisperTranscriber initialized")
        print(f"  API key configured: {'Yes' if transcriber.api_key else 'No'}")

        print("\nNote: OpenAI transcription test requires manual verification")
        print("Set stt_provider to 'openai' in config and test via the application")

    except Exception as e:
        print(f"✗ Error initializing WhisperTranscriber: {e}")

def test_config_switching():
    """Test that config correctly switches between providers."""
    print("\n=== Testing Provider Switching ===")

    config = Config()
    current_provider = config.get_stt_provider()

    print(f"Current provider: {current_provider}")

    if current_provider == "openai":
        print("✓ Default is OpenAI - existing functionality preserved")
    elif current_provider == "local":
        print("✓ Configured for local STT")
    else:
        print(f"✗ Unexpected provider: {current_provider}")

if __name__ == "__main__":
    print("VoiceControl Transcription Test Suite")
    print("=" * 50)

    test_config_switching()
    test_local_transcription()
    test_openai_transcription()

    print("\n" + "=" * 50)
    print("Test suite complete!")
