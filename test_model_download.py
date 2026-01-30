#!/usr/bin/env python3
"""Test model download functionality."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.local_transcriber import LocalTranscriber

def test_model_download():
    """Test downloading a model using LocalTranscriber."""
    print("=" * 60)
    print("Testing Model Download Functionality")
    print("=" * 60)

    # Test 1: Create config with model_id
    print("\n1. Creating config with model_id 'tiny'...")
    temp_config = Config()
    temp_config.settings['local_model_id'] = 'tiny'
    temp_config.settings['local_model_path'] = ""
    print(f"   Config created: model_id='tiny', model_path=''")

    # Test 2: Create LocalTranscriber with the config
    print("\n2. Creating LocalTranscriber with config...")
    try:
        transcriber = LocalTranscriber(config=temp_config)
        print("   ✓ LocalTranscriber created successfully")
    except Exception as e:
        print(f"   ✗ Failed to create LocalTranscriber: {e}")
        return False

    # Test 3: Load the model (this should trigger download if not cached)
    print("\n3. Loading model (will download if not cached)...")
    print("   This may take a few minutes for first download...")
    try:
        result = transcriber._load_model()
        if result:
            print("   ✓ Model loaded successfully!")
            print(f"   Model instance: {transcriber.model}")
        else:
            print("   ✗ Model loading failed")
            return False
    except Exception as e:
        print(f"   ✗ Exception during model loading: {e}")
        return False

    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_model_download()
    sys.exit(0 if success else 1)
