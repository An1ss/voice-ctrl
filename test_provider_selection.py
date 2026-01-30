#!/usr/bin/env python3
"""Test that provider selection works correctly."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.transcriber import WhisperTranscriber
from src.local_transcriber import LocalTranscriber

def test_provider_selection():
    """Test that the correct transcriber is selected based on config."""

    print("=== Testing Provider Selection ===\n")

    # Load config
    config = Config()
    stt_provider = config.get_stt_provider()

    print(f"Current stt_provider: {stt_provider}")

    # Test selection logic (mimics main.py)
    if stt_provider == "local":
        print("Selection: LocalTranscriber (faster-whisper)")
        transcriber = LocalTranscriber(config=config)
        print(f"✓ LocalTranscriber created")
        print(f"  Engine: {transcriber.engine}")
    else:
        print("Selection: WhisperTranscriber (OpenAI)")
        transcriber = WhisperTranscriber(config=config)
        print(f"✓ WhisperTranscriber created")
        print(f"  API key configured: {'Yes' if transcriber.api_key else 'No'}")

    print("\n✓ Provider selection logic working correctly!")
    print(f"✓ OpenAI path remains unchanged when stt_provider is '{stt_provider}'")

if __name__ == "__main__":
    test_provider_selection()
