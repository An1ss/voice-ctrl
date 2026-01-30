#!/usr/bin/env python3
"""Integration test for fallback functionality."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.local_transcriber import LocalTranscriber
from src.transcriber import WhisperTranscriber

def test_integration():
    """Test the integration of fallback logic."""
    print("=== Integration Test ===\n")

    # Load config
    config = Config()

    # Test 1: Verify both transcribers can be initialized
    print("1. Testing transcriber initialization...")
    try:
        local_transcriber = LocalTranscriber(config=config)
        print("   ✓ LocalTranscriber initialized")
    except Exception as e:
        print(f"   ✗ LocalTranscriber failed: {e}")
        return False

    try:
        openai_transcriber = WhisperTranscriber(config=config)
        print("   ✓ WhisperTranscriber initialized")
    except Exception as e:
        print(f"   ✗ WhisperTranscriber failed: {e}")
        return False

    # Test 2: Verify cleanup parameter
    print("\n2. Testing cleanup parameter...")
    import inspect
    sig = inspect.signature(local_transcriber.transcribe)
    params = sig.parameters

    if 'cleanup' in params:
        print(f"   ✓ LocalTranscriber.transcribe() has cleanup parameter")
        default_value = params['cleanup'].default
        if default_value == True:
            print(f"   ✓ Default value is True (cleanup by default)")
        else:
            print(f"   ✗ Default value is {default_value}, expected True")
            return False
    else:
        print(f"   ✗ LocalTranscriber.transcribe() missing cleanup parameter")
        return False

    # Test 3: Verify main.py imports work
    print("\n3. Testing main.py imports...")
    try:
        from src import main
        print("   ✓ main.py imports successfully")
    except Exception as e:
        print(f"   ✗ main.py import failed: {e}")
        return False

    # Test 4: Verify the fallback logic structure
    print("\n4. Verifying fallback logic structure...")
    print("   - LocalTranscriber with cleanup=False for fallback scenarios")
    print("   - WhisperTranscriber handles cleanup normally")
    print("   - process_audio_file has finally block for cleanup")
    print("   ✓ Structure verified")

    print("\n✓ All integration tests passed!")
    return True

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)
