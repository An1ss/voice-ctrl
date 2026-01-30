#!/usr/bin/env python3
"""Test local STT functionality."""

import sys
from pathlib import Path
import tempfile
import wave
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.local_transcriber import LocalTranscriber

def create_test_audio():
    """Create a simple test audio file (1 second of silence)."""
    # Create a temporary WAV file with 1 second of silence
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    sample_rate = 16000
    duration = 1  # 1 second

    # Generate silence
    audio_data = np.zeros(sample_rate * duration, dtype=np.int16)

    # Write WAV file
    with wave.open(temp_file.name, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())

    return temp_file.name

def test_local_transcriber_initialization():
    """Test that LocalTranscriber can be initialized."""
    print("=== Testing LocalTranscriber Initialization ===\n")

    config = Config()
    transcriber = LocalTranscriber(config=config)

    print(f"✓ LocalTranscriber initialized")
    print(f"  Engine: {transcriber.engine}")
    print(f"  Model path: '{transcriber.model_path}'")
    print(f"  Model ID: '{transcriber.model_id}'")
    print(f"  Model loaded: {transcriber.model is not None}")

    return transcriber

def test_model_loading():
    """Test that faster-whisper model can be loaded."""
    print("\n=== Testing Model Loading ===\n")

    config = Config()
    transcriber = LocalTranscriber(config=config)

    print("Attempting to load model (this will download the base model if not cached)...")
    print("This may take a few minutes on first run...")

    success = transcriber._load_model()

    if success:
        print(f"✓ Model loaded successfully")
        print(f"  Model object: {type(transcriber.model)}")
    else:
        print(f"✗ Model loading failed")
        return False

    return True

def test_transcription_with_silence():
    """Test transcription with a silent audio file."""
    print("\n=== Testing Transcription (Silent Audio) ===\n")

    config = Config()
    transcriber = LocalTranscriber(config=config)

    # Create test audio file
    print("Creating test audio file (1 second of silence)...")
    audio_file = create_test_audio()
    print(f"Test audio: {audio_file}")

    # Test transcription
    print("Transcribing...")
    result = transcriber.transcribe(audio_file)

    if result is None:
        print("✓ Transcription returned None (expected for silence)")
    elif result == "":
        print("✓ Transcription returned empty string (expected for silence)")
    else:
        print(f"Note: Transcription returned: '{result}'")

    print("\n✓ Transcription function executed without errors")

if __name__ == "__main__":
    print("Local STT Test Suite")
    print("=" * 50)

    # Test 1: Initialization
    test_local_transcriber_initialization()

    # Test 2: Model loading
    model_loaded = test_model_loading()

    # Test 3: Transcription (only if model loaded successfully)
    if model_loaded:
        test_transcription_with_silence()
    else:
        print("\n⊘ Skipping transcription test - model loading failed")

    print("\n" + "=" * 50)
    print("Test suite complete!")
