#!/usr/bin/env python3
"""Test script for model scanner functionality."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.model_scanner import ModelScanner
from src.config import Config

def test_scanner():
    """Test the model scanner."""
    print("Testing ModelScanner...")
    print()

    # Initialize scanner
    config = Config()
    scanner = ModelScanner(log_path=config.log_path)

    # Test scanning a specific directory (faster-whisper cache)
    test_path = Path.home() / ".cache" / "huggingface" / "hub"
    if test_path.exists():
        print(f"Scanning: {test_path}")
        models = scanner.scan_folder_sync(test_path)
        print(f"Found {len(models)} models:")
        for model in models:
            print(f"  - {model['name']}")
            print(f"    Path: {model['path']}")
        print()
    else:
        print(f"Test path does not exist: {test_path}")
        print()

    # Test default paths scan (in background)
    print("Scanning default paths (background)...")

    def on_complete(models):
        print(f"\nDefault scan complete! Found {len(models)} models:")
        for i, model in enumerate(models, 1):
            print(f"{i}. {model['name']}")
            print(f"   {model['path']}")
        print()

    thread = scanner.scan_default_paths(callback=on_complete)
    thread.join()  # Wait for completion

    print("Test complete!")

if __name__ == "__main__":
    test_scanner()
